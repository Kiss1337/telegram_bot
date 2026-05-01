import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")

logging.basicConfig(level=logging.INFO)

client = genai.Client(api_key=GEMINI_KEY)

user_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я AI ассистент.\n\n"
        "Напиши мне что-нибудь!\n"
        "/clear — очистить историю."
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text("🗑️ История очищена!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({"role": "user", "parts": [{"text": user_text}]})

    await update.message.chat.send_action("typing")

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_histories[user_id]
    )

    reply = response.text
    user_histories[user_id].append({"role": "model", "parts": [{"text": reply}]})

    await update.message.reply_text(reply)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен!")
    app.run_polling()
