import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from stream import start_stream, stop_stream, stream_status
from utils import extract_info
from keep_alive import keep_alive

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID"))

current_stream = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    await update.message.reply_text(
        "✅ Please send the following info in this format:\n\n"
        "Stream Key: <your_key>\n"
        "Title: <stream_title>\n"
        "Source: <video/file/YouTube playlist link>\n"
        "Loop: yes/no"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return

    message = update.message.text
    info = extract_info(message)

    # Check for missing fields
    missing = []
    if not info.get("stream_key"):
        missing.append("Stream Key")
    if not info.get("title"):
        missing.append("Title")
    if not info.get("source"):
        missing.append("Source")
    if "loop" not in info:
        missing.append("Loop (yes/no)")

    if missing:
        await update.message.reply_text(f"⚠️ Missing fields: {', '.join(missing)}.\nPlease send again in the correct format.")
        return

    # If everything is valid
    await update.message.reply_text("✅ Starting Stream...")
    current_stream["status"] = True

    try:
        await start_stream(
            info["stream_key"],
            info["source"],
            info["title"],
            info["loop"]
        )
    except Exception as e:
        current_stream["status"] = False
        await update.message.reply_text(f"❌ Stream failed to start: {str(e)}")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return

    await stop_stream()
    current_stream["status"] = False
    await update.message.reply_text("🛑 Stream stopped.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return

    if current_stream.get("status"):
        await update.message.reply_text("📡 Stream is currently running.")
    else:
        await update.message.reply_text("🔴 No active stream.")

if __name__ == "__main__":
    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot is running...")
    app.run_polling()
