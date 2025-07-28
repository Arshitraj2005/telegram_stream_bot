

import os
import logging
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from stream import start_stream, stop_stream, stream_status
from utils import extract_info
from keep_alive import keep_alive

BOT_TOKEN = "8363849977:AAF00Fv0TkNoPG-F9ORpk2DloAVe3e2x94k"
OWNER_ID = 5326642169

# Conversation states
SOURCE, TITLE, LOOP, STREAM_KEY = range(4)

user_data = {}
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Unauthorized user.")
        return ConversationHandler.END
    await update.message.reply_text("Send video file, video URL, YouTube playlist URL, or OneDrive URL:")
    return SOURCE

async def handle_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    source = update.message.text or update.message.video.file_id
    user_data["source"] = source
    await update.message.reply_text("Enter stream title:")
    return TITLE

async def handle_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["title"] = update.message.text
    await update.message.reply_text("Do you want the video to loop? (yes/no):")
    return LOOP

async def handle_loop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["loop"] = update.message.text.strip().lower() == "yes"
    await update.message.reply_text("Send your YouTube Stream Key:")
    return STREAM_KEY

async def handle_stream_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["stream_key"] = update.message.text
    await update.message.reply_text("Starting stream...")
    source, title, loop, stream_key = user_data.values()
    input_file = await extract_info(source, context.bot)  # URL or Telegram video
    start_stream(input_file, stream_key, title, loop)
    await update.message.reply_text("✅ Stream started.")
    return ConversationHandler.END

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Unauthorized.")
    stop_stream()
    await update.message.reply_text("🛑 Stream stopped.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = stream_status()
    await update.message.reply_text(f"📡 Stream status: {status}")

app = ApplicationBuilder().token(BOT_TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SOURCE: [MessageHandler(filters.ALL, handle_source)],
        TITLE: [MessageHandler(filters.TEXT, handle_title)],
        LOOP: [MessageHandler(filters.TEXT, handle_loop)],
        STREAM_KEY: [MessageHandler(filters.TEXT, handle_stream_key)]
    },
    fallbacks=[]
)

app.add_handler(conv)
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("status", status))

keep_alive()
app.run_polling()



