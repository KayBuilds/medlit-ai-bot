from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import sqlite3
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8233772963:AAHHu9X00Y22A75eVjXOs7m0Aw23g3aCin8"
DB_PATH = "data/medlit.db"

conn = sqlite3.connect(DB_PATH)
conn.execute('CREATE TABLE IF NOT EXISTS subscribers (user_id INTEGER PRIMARY KEY, name TEXT, specialty TEXT, status TEXT, trial_ends TEXT)')
conn.commit()
conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
logger.info(f"Start command from user {update.effective_user.id}")

keyboard = [[InlineKeyboardButton("✅ CLICK HERE TO START TRIAL", callback_data="start_trial")]]

await update.message.reply_text(
"🩺 MedLit AI\n\nClick the button below to start your 7-day FREE trial:",
reply_markup=InlineKeyboardMarkup(keyboard)
)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
logger.info(f"Button clicked by user {query.from_user.id}, data={query.data}")

await query.answer("Processing...")

if query.data == "start_trial":
user = query.from_user
trial_end = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

try:
conn = sqlite3.connect(DB_PATH)
conn.execute('INSERT OR REPLACE INTO subscribers VALUES (?,?,?,?,?)',
(user.id, user.full_name, "cardio", "trial", trial_end))
conn.commit()
conn.close()
logger.info(f"Trial activated for user {user.id}")

await context.bot.send_message(
chat_id=user.id,
text=f"✅ SUCCESS! Your 7-day trial is active.\n\nFirst digest: Tomorrow 8 AM\nTrial ends: {trial_end}"
)
except Exception as e:
logger.error(f"Error: {e}")
await context.bot.send_message(chat_id=user.id, text="Error. Please try /start again")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_click))

print("Bot running with DEBUG logging...")
app.run_polling()
