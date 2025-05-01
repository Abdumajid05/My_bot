import os
from flask import Flask, request
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    CommandHandler,
    filters,
)
from utils import generate_gpt_reply

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [KeyboardButton("📌 Yordam"), KeyboardButton("💡 Savol berish")],
    ]
    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(
        "🤖 Salom! Men ChatGPT yordamchi botman. Har qanday savolni bemalol yozishingiz mumkin!",
        reply_markup=markup
    )

# Xabar javob berish
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply = generate_gpt_reply(user_message)
    await update.message.reply_text(reply)

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# Flask route
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put(update)
    return "OK", 200

# Webhook o‘rnatish
@app.before_first_request
def init_webhook():
    telegram_app.bot.set_webhook(url=WEBHOOK_URL)

if __name__ == "__main__":
    telegram_app.initialize()
    app.run(host="0.0.0.0", port=5000)
