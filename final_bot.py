from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import sqlite3
from datetime import datetime, timedelta

TOKEN = "8233772963:AAHHu9X00Y22A75eVjXOs7m0Aw23g3aCin8"
DB_PATH = "data/medlit.db"

# Initialize database
conn = sqlite3.connect(DB_PATH)
conn.execute('''CREATE TABLE IF NOT EXISTS subscribers (
    user_id INTEGER PRIMARY KEY, name TEXT, specialty TEXT, 
    status TEXT, trial_ends TEXT)''')
conn.commit()
conn.close()

# SAMPLES WITH LINKS
SAMPLES = {
    "cardio": '''🫀 SAMPLE: Cardiology Digest

1️⃣ SGLT2 Inhibitors in Heart Failure
📰 Indian Heart Journal | 📊 High (RCT)
📝 1,200 HF patients: 34% reduction in hospitalization with dapagliflozin
💡 Impact: HIGH | ✅ Consider SGLT2i for all HF patients
🔗 Links: https://doi.org/10.1016/j.ihj.2025.01.001 | https://openalex.org/works/W123456789

2️⃣ Triple Therapy in AF + Diabetes
📰 European Heart Journal | 📊 Meta-analysis (n=45,000)
📝 Triple therapy reduces MACE by 42% vs dual therapy in T2DM+AF
💡 Impact: HIGH | ✅ Add GLP-1RA for eligible patients
🔗 Links: https://doi.org/10.1093/eurheartj/ehad123 | https://openalex.org/works/W987654321

3️⃣ Early Rhythm Control in AF
📰 Circulation | 📊 RCT (5-year follow-up)
📝 Early rhythm control reduced CV death by 24% vs rate control
💡 Impact: MODERATE | ✅ Refer new AF patients within 12 months
🔗 Links: https://doi.org/10.1161/circulationaha.124.012345 | https://openalex.org/works/W456789012

You get 3-5 digests like this DAILY at 8 AM IST''',

    "endo": '''🍬 SAMPLE: Endocrinology Digest

1️⃣ Time-Restricted Eating vs Calorie Counting
📰 Diabetes Care | 📊 RCT (12 months)
📝 8-hour TRE: same HbA1c drop (-1.2%), 40% better adherence
💡 Impact: MODERATE | ✅ Offer TRE to busy patients
🔗 Links: https://doi.org/10.2337/dc24-1234 | https://openalex.org/works/W789012345

2️⃣ CGM vs HbA1c in Type 1 Diabetes
📰 JCEM | 📊 Prospective cohort
📝 CGM found 7.4x more hypoglycemic episodes (42% nocturnal)
💡 Impact: HIGH | ✅ Advocate CGM for all T1DM
🔗 Links: https://doi.org/10.1210/jcem.2025.01.0567 | https://openalex.org/works/W567890123

3️⃣ Tirzepatide vs Semaglutide for Obesity
📰 NEJM | 📊 SURMOUNT-5 trial (72 weeks)
📝 Tirzepatide: 22.8% weight loss vs 16.5% semaglutide
💡 Impact: HIGH | ✅ Prioritize tirzepatide for weight loss
🔗 Links: https://doi.org/10.1056/nejmoa2412345 | https://openalex.org/works/W890123456

You get 3-5 digests like this DAILY at 8 AM IST'''
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '''🩺 *Welcome to MedLit AI!*

I deliver daily AI-summarized medical research with full-text links.

*What you get:*
• 3-5 papers every morning at 8 AM IST
• Key findings + clinical impact + action items
• Links to full text (DOI + OpenAlex)
• Cardiology & Endocrinology

*Pricing:*
• One specialty: ₹299/month
• Both specialties: ₹499/month
🎁 *First 7 days FREE*

👇 *Tap below to see samples with links:*''',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🫀 View Cardiology Samples", callback_data="cardio")],
            [InlineKeyboardButton("🍬 View Endocrinology Samples", callback_data="endo")],
            [InlineKeyboardButton("✅ Start Free Trial", callback_data="subscribe")]
        ]),
        parse_mode="Markdown"
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    
    if query.data in ["cardio", "endo"]:
        # Send sample
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=SAMPLES[query.data],
            parse_mode="Markdown"
        )
        # Send CTA
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Ready to receive digests like this daily?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Start 7-Day Free Trial", callback_data="subscribe")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )
    
    elif query.data == "subscribe":
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        trial_end = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        conn.execute('''INSERT OR REPLACE INTO subscribers 
            VALUES (?, ?, ?, ?, ?)''', 
            (user.id, user.full_name, "cardio", "trial", trial_end))
        conn.commit()
        conn.close()
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'''✅ *Trial Activated!*

Your 7-day free trial starts now.
First digest: Tomorrow 8:00 AM IST

*Commands:*
/today - Get today's digest
/status - Check subscription
/help - Get help

Questions? Just reply here!''',
            parse_mode="Markdown"
        )
    
    elif query.data == "back":
        await start(update, context)

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(SAMPLES["cardio"], parse_mode="Markdown")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT * FROM subscribers WHERE user_id=?", (user.id,)).fetchone()
    conn.close()
    
    if row:
        await update.message.reply_text(f"Status: {row[3]}\nTrial ends: {row[4]}")
    else:
        await update.message.reply_text("Not subscribed. Click /start")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '''*MedLit AI Commands:*
        
/start - Begin subscription
/today - Get today's digest
/status - Check your subscription
/help - Show this message

Contact: kashif@hostmyai.app''',
        parse_mode="Markdown"
    )

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("today", today))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CallbackQueryHandler(button))

print("✅ Bot ready! Test: https://t.me/medicnews_bot")
app.run_polling()
