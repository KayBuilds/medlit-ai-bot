import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from datetime import datetime, timedelta

TOKEN = os.environ.get("BOT_TOKEN", "8233772963:AAHHu9X00Y22A75eVjXOs7m0Aw23g3aCin8")

SAMPLE = """Welcome to MedLit AI!

Daily medical research summaries."""

async def start(update, context):
    keyboard = [[InlineKeyboardButton("START TRIAL", callback_data="trial")]]
    await update.message.reply_text("MedLit AI - Click to start trial", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "trial":
        await context.bot.send_message(chat_id=query.from_user.id, text="TRIAL ACTIVATED!")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
