import os
import logging
from telegram import Update, ForceReply
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from stream import start_stream, stop_stream
from utils import extract_info
from keep_alive import keep_alive

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
OWNER_ID = 5326642169  # Replace with your actual Telegram user ID
TOKEN = "8363849977:AAF00Fv0TkNoPG-F9ORpk2DloAVe3e2x94k"  # Your bot token

# Conversation states
ASK_TITLE, ASK_SOURCE, ASK_LOOP, ASK_STREAM_KEY = range(4)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return ConversationHandler.END

    await update.message.reply_text("🎬 Send me the stream title:")
    return ASK_TITLE

async def title_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["title"] = update.message.text
    await update.message.reply_text("📁 Now send a video file, video URL, YouTube playlist link, or OneDrive link:")
    return ASK_SOURCE

async def source_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.video or update.message.document
    if file:
        file_path = await extract_info(update, context, file)
    else:
        url = update.message.text
        file_path = await extract_info(update, context, url)

    if not file_path:
        await update.message.reply_text("❌ Could not process the file or link. Try again.")
        return ConversationHandler.END

    context.user_data["source"] = file_path
    await update.message.reply_text("🔁 Do you want the video to loop? (yes/no):")
    return ASK_LOOP

async def loop_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    context.user_data["loop"] = text in ["yes", "y"]
    await update.message.reply_text("🔑 Now send me your YouTube stream key:")
    return ASK_STREAM_KEY

async def stream_key_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["stream_key"] = update.message.text
    await update.message.reply_text("🚀 Starting stream...")

    title = context.user_data["title"]
    source = context.user_data["source"]
    loop = context.user_data["loop"]
    stream_key = context.user_data["stream_key"]

    success = start_stream(source, stream_key, title, loop)
    if success:
        await update.message.reply_text("✅ Stream started successfully!")
    else:
        await update.message.reply_text("❌ Failed to start stream.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized to stop the stream.")
        return

    result = stop_stream()
    await update.message.reply_text(result)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(stream_status())

# Main function
def main():
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, title_received)],
            ASK_SOURCE: [MessageHandler(filters.ALL & ~filters.COMMAND, source_received)],
            ASK_LOOP: [MessageHandler(filters.TEXT & ~filters.COMMAND, loop_received)],
            ASK_STREAM_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, stream_key_received)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
