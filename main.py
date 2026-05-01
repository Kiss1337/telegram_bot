import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
import anthropic

BOT_TOKEN = "8758967434:AAF0TgSw27aR2PKIebv__GBf-7zT_9f_b1A"
ANTHROPIC_API_KEY = "ВАШ_КЛЮЧ_ANTHROPIC"
ADMIN_ID = 0

SYSTEM_PROMPT = """Ты — помощник бота-предложки для Telegram канала.
Пользователи присылают тебе свои предложения: новости, идеи рубрик, темы для постов.
Твоя задача:
- Поблагодарить пользователя за предложение
- Кратко прокомментировать идею
- Сообщить что предложение передано администратору на рассмотрение
Отвечай дружелюбно, по-русски, коротко (2-3 предложения)."""

logging.basicConfig(level=logging.INFO)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Напиши своё предложение — новость, идею для рубрики или тему для поста!")

async def handle_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    await update.message.reply_text("⏳ Обрабатываю твоё предложение...")
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": text}]
        )
        ai_reply = response.content[0].text
    except Exception:
        ai_reply = "Спасибо за предложение! Оно передано администратору. 🙏"
    await update.message.reply_text(ai_reply)
    username = f"@{user.username}" if user.username else f"ID: {user.id}"
    admin_text = f"📬 *Новое предложение*\n\n👤 От: {user.full_name} ({username})\n\n💬 *Текст:*\n{text}"
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Принять", callback_data=f"accept_{user.id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user.id}"),
    ]])
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown", reply_markup=keyboard)
    except Exception:
        pass

async def handle_admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ Только для администратора", show_alert=True)
        return
    action, user_id = query.data.split("_", 1)
    if action == "accept":
        result_text = "✅ *Принято*"
        user_msg = "🎉 Ваше предложение было *принято* администратором!"
    else:
        result_text = "❌ *Отклонено*"
        user_msg = "Ваше предложение рассмотрено, но на этот раз не подошло. Присылайте новые идеи! 💪"
    await query.edit_message_text(text=f"{query.message.text}\n\n{result_text}", parse_mode="Markdown")
    try:
        await context.bot.send_message(chat_id=int(user_id), text=user_msg, parse_mode="Markdown")
    except Exception:
        pass

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_admin_decision))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_suggestion))
    print("✅ Бот запущен!")
    app.run_polling()
      
