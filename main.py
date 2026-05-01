import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8758967434:AAF0TgSw27aR2PKIebv__GBf-7zT_9f_b1A")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Это бот-предложка.\n\n"
        "Напиши своё предложение — новость, идею для рубрики или тему для поста!"
    )

async def handle_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    await update.message.reply_text("✅ Спасибо за предложение! Мы рассмотрим его и скоро ответим. 🙏")
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
