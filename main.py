import os
import logging
from telegram import Update, ForceReply
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)
from stream import start_stream, stop_stream
from utils import extract_info
from keep_alive import keep_alive

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
ASK_STREAM_KEY, ASK_TITLE, ASK_SOURCE, ASK_LOOP = range(4)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    if str(user.id) != os.getenv("OWNER_ID"):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return ConversationHandler.END

    await update.message.reply_text("🎬 Please enter your YouTube Stream Key:")
    return ASK_STREAM_KEY

# Ask for title
async def ask_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["stream_key"] = update.message.text.strip()
    await update.message.reply_text("📝 Please enter a custom livestream title:")
    return ASK_TITLE

# Ask for video source
async def ask_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["title"] = update.message.text.strip()
    await update.message.reply_text(
        "📤 Now send a video file or a YouTube/Google Drive/OneDrive link:"
    )
    return ASK_SOURCE

# Ask for loop preference
async def ask_loop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    source = await extract_info(update)
    if not source:
        await update.message.reply_text("⚠️ Invalid input. Try again.")
        return ASK_SOURCE

    context.user_data["source"] = source
    await update.message.reply_text("🔁 Do you want to loop the video? (yes/no)")
    return ASK_LOOP

# Start stream
async def begin_stream(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    loop_input = update.message.text.strip().lower()
    loop = loop_input == "yes"

    await update.message.reply_text("🚀 Starting livestream...")
    await start_stream(
        context.user_data["stream_key"],
        context.user_data["title"],
        context.user_data["source"],
        loop,
    )
    await update.message.reply_text("✅ Livestream started!")
    return ConversationHandler.END

# Stop stream
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if str(user.id) != os.getenv("OWNER_ID"):
        await update.message.reply_text("❌ You are not authorized to stop the stream.")
        return

    await stop_stream()
    await update.message.reply_text("🛑 Livestream stopped!")

# Status command (optional - placeholder)
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Status command not implemented.")

# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END

# Main function
def main():
    keep_alive()
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_STREAM_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_title)],
            ASK_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_source)],
            ASK_SOURCE: [MessageHandler(filters.ALL, ask_loop)],
            ASK_LOOP: [MessageHandler(filters.TEXT & ~filters.COMMAND, begin_stream)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status))

    app.run_polling()

if __name__ == "__main__":
    main()
