import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from stream import start_stream, stop_stream, get_stream_status
from utils import extract_info
from keep_alive import keep_alive

# Replace with your actual token and owner ID
BOT_TOKEN = os.getenv("BOT_TOKEN", "8363849977:AAF00Fv0TkNoPG-F9ORpk2DloAVe3e2x94k")
OWNER_ID = int(os.getenv("OWNER_ID", "5326642169"))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Access denied.")
        return

    await update.message.reply_text("Please send stream key.")
    context.user_data['step'] = 'stream_key'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    text = update.message.text

    step = context.user_data.get('step')

    if step == 'stream_key':
        context.user_data['stream_key'] = text
        await update.message.reply_text("Enter stream title:")
        context.user_data['step'] = 'title'
    elif step == 'title':
        context.user_data['title'] = text
        await update.message.reply_text("Send video URL, YouTube playlist, or file link:")
        context.user_data['step'] = 'video'
    elif step == 'video':
        context.user_data['video_url'] = text
        await update.message.reply_text("Loop video? (yes/no)")
        context.user_data['step'] = 'loop'
    elif step == 'loop':
        loop = text.lower() == 'yes'
        await update.message.reply_text("Starting stream...")
        info = extract_info(
            context.user_data['video_url'],
            context.user_data['stream_key'],
            context.user_data['title'],
            loop
        )
        start_stream(info)
        await update.message.reply_text("✅ Stream started!")
        context.user_data.clear()

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    stop_stream()
    await update.message.reply_text("⛔ Stream stopped.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    status = get_stream_status()
    await update.message.reply_text(f"📊 Stream status: {status}")

if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
