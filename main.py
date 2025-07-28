import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

from stream import start_stream, stop_stream, get_stream_status
from utils import extract_info
from keep_alive import keep_alive

# Telegram Bot Token and Owner ID from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# States for conversation
WAITING_FOR_SOURCE, WAITING_FOR_TITLE, WAITING_FOR_LOOP, WAITING_FOR_KEY = range(4)

user_data = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ You are not authorized to use this bot.")
        return
    await update.message.reply_text("🎬 Send me your video URL / file / YouTube playlist / OneDrive link.")
    return WAITING_FOR_SOURCE

# Get source
async def get_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    source = update.message.text or update.message.video or update.message.document
    user_data["source"] = source
    await update.message.reply_text("📝 Enter your livestream title:")
    return WAITING_FOR_TITLE

# Get title
async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["title"] = update.message.text
    await update.message.reply_text("🔁 Do you want to loop the video? (yes/no)")
    return WAITING_FOR_LOOP

# Get loop choice
async def get_loop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["loop"] = update.message.text.lower() in ["yes", "y"]
    await update.message.reply_text("🔑 Send your YouTube Stream Key:")
    return WAITING_FOR_KEY

# Get stream key and start stream
async def get_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["key"] = update.message.text
    await update.message.reply_text("🚀 Starting livestream...")
    await start_stream(user_data)
    return ConversationHandler.END

# Stop command
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await stop_stream()
    await update.message.reply_text("🛑 Livestream stopped.")

# Status command
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    status = get_stream_status()
    await update.message.reply_text(f"📡 Livestream status: {status}")

# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Livestream setup cancelled.")
    return ConversationHandler.END

# Start the app
if __name__ == "__main__":
    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_FOR_SOURCE: [MessageHandler(filters.ALL, get_source)],
            WAITING_FOR_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
            WAITING_FOR_LOOP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_loop)],
            WAITING_FOR_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_key)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status))

    app.run_polling()
