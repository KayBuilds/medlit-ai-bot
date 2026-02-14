from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import sqlite3
from datetime import datetime, timedelta

TOKEN = "8233772963:AAHHu9X00Y22A75eVjXOs7m0Aw23g3aCin8"
DB_PATH = "data/medlit.db"

# Setup database
conn = sqlite3.connect(DB_PATH)
conn.execute('CREATE TABLE IF NOT EXISTS subscribers (user_id INTEGER PRIMARY KEY, name TEXT, specialty TEXT, status TEXT, trial_ends TEXT)')
conn.commit()
conn.close()

SAMPLE = '''🫀 SAMPLE: Cardiology Digest

1️⃣ SGLT2 Inhibitors in Heart Failure
📰 Indian Heart Journal
📝 34% reduction in hospitalization
💡 Impact: HIGH | ✅ Consider for all HF
🔗 https://doi.org/10.1016/j.ihj.2025.01.001

2️⃣ Triple Therapy in AF + Diabetes
📝 42% MACE reduction
💡 Impact: HIGH | ✅ Add GLP-1RA

3️⃣ Early Rhythm Control in AF
📝 24% CV death reduction at 5 years
💡 Impact: MODERATE | ✅ Refer early

You get 3-5 like this DAILY at 8 AM'''

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🫀 View Sample", callback_data="sample")],
        [InlineKeyboardButton("✅ START 7-DAY FREE TRIAL", callback_data="trial")]
    ]
    await update.message.reply_text(
        "🩺 Welcome to MedLit AI!\n\nDaily medical research summaries with full-text links.\n\nPricing: ₹299/month\n🎁 First 7 days FREE\n\nTap below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    
    if query.data == "sample":
        await context.bot.send_message(chat_id=user.id, text=SAMPLE)
    
    elif query.data == "trial":
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        trial_end = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        conn.execute('INSERT OR REPLACE INTO subscribers VALUES (?,?,?,?,?)', 
            (user.id, user.full_name, "cardio", "trial", trial_end))
        conn.commit()
        conn.close()
        
        await context.bot.send_message(
            chat_id=user.id,
            text=f'''✅ TRIAL ACTIVATED!

📅 Your 7-day free trial starts NOW
⏰ First digest: Tomorrow 8:00 AM IST

You will receive 3-5 medical papers daily with:
• Key findings
• Clinical impact  
• Action items
• Full-text links

Trial ends: {trial_end}

Use /today to see a sample now!'''
        )

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(SAMPLE)

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("today", today))
app.add_handler(CallbackQueryHandler(button))

print("✅ Bot ready! https://t.me/medicnews_bot")
app.run_polling()
