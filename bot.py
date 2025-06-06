import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import random

load_dotenv()  # Зчитує змінні із .env

TOKEN = os.getenv("BOT_TOKEN")

used_words = []
last_letter = ''
all_words = set()

def load_words():
    global all_words
    with open("words.txt", "r", encoding="utf-8") as f:
        # Якщо слова через пробіли, розділяємо по пробілах
        text = f.read()
        words = text.split()
        all_words = set(word.strip().capitalize() for word in words if word.strip())

def find_word(start_letter):
    for word in all_words:
        if word.startswith(start_letter.upper()) and word not in used_words:
            return word
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global used_words, last_letter
    used_words = []
    last_letter = ''
    await update.message.reply_text(
        "Гра почалася! Напиши перше слово."
    )

async def skip_turn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global used_words, last_letter
    if not last_letter:
        await update.message.reply_text("Ще не почали гру, напиши перше слово.")
        return
    bot_word = find_word(last_letter)
    if bot_word:
        used_words.append(bot_word)
        last_letter = bot_word[-1]
        await update.message.reply_text(f"Я пропускаю хід і кажу: {bot_word}. Тепер на: {last_letter.upper()}")
    else:
        await update.message.reply_text("Я більше не знаю слів. Ти виграв!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global used_words, last_letter
    word = update.message.text.strip().capitalize()

    if word in used_words:
        await update.message.reply_text("Це слово вже було!")
        return

    if last_letter and not word.startswith(last_letter.upper()):
        await update.message.reply_text(f"Треба слово на літеру: {last_letter.upper()}")
        return

    if word not in all_words:
        await update.message.reply_text("Не знаю такого слова.")
        return

    used_words.append(word)
    last_letter = word[-1]

    bot_word = find_word(last_letter)
    if bot_word:
        used_words.append(bot_word)
        last_letter = bot_word[-1]
        # Додаємо кнопку "Пропустити хід"
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Пропустити хід", callback_data="skip")]]
        )
        await update.message.reply_text(
            f"Моє слово: {bot_word}. Тепер на: {last_letter.upper()}",
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text("Я більше не знаю слів. Ти виграв!")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "skip":
        await skip_turn(update, context)

def main():
    load_words()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()

