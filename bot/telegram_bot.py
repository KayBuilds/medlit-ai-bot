#!/usr/bin/env python3
"""
MedLit AI - Telegram Bot with Working Samples
Fixed version - sends samples properly
"""

import json
import sqlite3
import asyncio
import logging
from datetime import datetime, timedelta, time
from typing import Dict, List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DB_PATH = "data/medlit.db"

# Single comprehensive sample per specialty
SAMPLE_CARDIO = """🫀 *SAMPLE: Cardiology Digest*

*1️⃣ SGLT2 Inhibitors in Heart Failure*
📰 Indian Heart Journal • 👤 Cardiologists

📝 *Key Finding:*
Analysis of 1,200 HF patients showed 34% reduction in hospitalization with dapagliflozin vs standard care.

💡 *Impact:* 🔴 High - Practice-changing
✅ *Action:* Consider SGLT2i for all HF patients

───────────────────

*2️⃣ Triple Therapy in AF + Diabetes*
📰 European Heart Journal • 👤 Cardiologists

📝 *Key Finding:*  
Triple therapy (GLP-1RA + SGLT2i + Metformin) reduces MACE by 42% vs dual therapy in T2DM with AF.

💡 *Impact:* 🔴 High - Significant stroke reduction
✅ *Action:* Consider adding GLP-1RA for T2DM+AF patients

───────────────────

*3️⃣ Early Rhythm Control in AF*
📰 Circulation • 👤 EP Specialists

📝 *Key Finding:*
Early rhythm control (within 12 months) reduced CV death by 24% vs rate control at 5 years.

💡 *Impact:* 🟡 Moderate - Reinforces early intervention
✅ *Action:* Refer new-onset AF patients early for rhythm control

───────────────────

*You would receive 3-5 digests like this daily at 8 AM*"""

SAMPLE_ENDO = """🍬 *SAMPLE: Endocrinology Digest*

*1️⃣ Time-Restricted Eating vs Calorie Counting*
📰 Diabetes Care • 👤 Endocrinologists

📝 *Key Finding:*
8-hour eating window achieved same HbA1c reduction (-1.2%) with 40% better adherence than calorie counting.

💡 *Impact:* 🟡 Moderate - Viable alternative
✅ *Action:* Offer TRE to patients who struggle with calorie tracking

───────────────────

*2️⃣ CGM vs HbA1c in Type 1 Diabetes*
📰 JCEM • 👤 Endocrinologists

📝 *Key Finding:*
CGM identified 7.4x more hypoglycemic episodes than HbA1c. 42% were nocturnal and asymptomatic.

💡 *Impact:* 🔴 High - CGM superiority established
✅ *Action:* Advocate CGM for all T1DM patients

───────────────────

*3️⃣ Tirzepatide vs Semaglutide for Obesity*
📰 NEJM • 👤 Endocrinologists

📝 *Key Finding:*
Tirzepatide 15mg achieved 22.8% weight loss vs 16.5% with semaglutide. 64% achieved >20% weight loss.

💡 *Impact:* 🔴 High - New benchmark for weight loss
✅ *Action:* Prioritize tirzepatide if cost permits

───────────────────

*You would receive 3-5 digests like this daily at 8 AM*"""


class MedLitBot:
    def __init__(self):
        self.config = self._load_config()
        self.token = self.config.get("telegram_bot_token", "")
    
    def _load_config(self) -> Dict:
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except:
            return {}
    
    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                name TEXT,
                specialty TEXT,
                subscription_status TEXT DEFAULT 'trial',
                trial_ends TEXT,
                subscription_ends TEXT,
                joined_at TEXT,
                last_delivery TEXT
            )
        ''')
        conn.commit()
        conn.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show welcome with sample buttons"""
    user = update.effective_user
    
    welcome_text = f"""🩺 *Welcome to MedLit AI, Dr. {user.first_name}!*

I deliver daily AI-summarized medical research to your phone.

*What you get:*
• 3-5 papers every morning at 8 AM IST
• Key findings + clinical impact + action items
• Cardiology & Endocrinology specialties

*Pricing:* ₹299/month (one) or ₹499/month (both)
🎁 *First 7 days FREE*

👇 *Tap below to see sample digests:*"""
    
    keyboard = [
        [InlineKeyboardButton("🫀 View Cardiology Samples", callback_data="view_cardio")],
        [InlineKeyboardButton("🍬 View Endocrinology Samples", callback_data="view_endo")],
        [InlineKeyboardButton("✅ Start Free Trial", callback_data="show_pricing")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def show_samples(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show sample digest - sends as new message"""
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    
    if query.data == "view_cardio":
        sample_text = SAMPLE_CARDIO
        title = "🫀 Cardiology Samples"
    elif query.data == "view_endo":
        sample_text = SAMPLE_ENDO
        title = "🍬 Endocrinology Samples"
    else:
        return
    
    # Send sample as new message (don't edit)
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"*{title}*\n\n{sample_text}",
        parse_mode="Markdown"
    )
    
    # Send CTA after sample
    keyboard = [
        [InlineKeyboardButton("✅ Start 7-Day Free Trial", callback_data="show_pricing")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")],
    ]
    await context.bot.send_message(
        chat_id=chat_id,
        text="*Ready to receive digests like this daily?*\n\nStart your free trial - no credit card required!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def show_pricing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pricing options"""
    query = update.callback_query
    await query.answer()
    
    pricing_text = """💳 *Choose Your Plan*

*🫀 Cardiology - ₹299/month*
• Daily cardiology digests
• Heart failure & arrhythmias
• 3-5 papers daily

*🍬 Endocrinology - ₹299/month*
• Daily endocrinology digests
• Diabetes & metabolic disorders
• 3-5 papers daily

*🫀🍬 Both - ₹499/month (Save ₹99)*
• All features included
• Priority support

🎁 *7 days FREE trial*"""
    
    keyboard = [
        [InlineKeyboardButton("🫀 Cardiology (₹299)", callback_data="sub_cardiology")],
        [InlineKeyboardButton("🍬 Endocrinology (₹299)", callback_data="sub_endocrinology")],
        [InlineKeyboardButton("🫀🍬 Both (₹499)", callback_data="sub_both")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")],
    ]
    
    # Edit original message
    try:
        await query.edit_message_text(
            pricing_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    except:
        # If edit fails, send new message
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=pricing_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Go back to main menu"""
    query = update.callback_query
    await query.answer()
    
    # Send fresh start message
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="👇 *Main Menu*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🫀 View Cardiology Samples", callback_data="view_cardio")],
            [InlineKeyboardButton("🍬 View Endocrinology Samples", callback_data="view_endo")],
            [InlineKeyboardButton("✅ Start Free Trial", callback_data="show_pricing")],
        ]),
        parse_mode="Markdown"
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button clicks"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    data = query.data
    
    if data == "view_cardio" or data == "view_endo":
        await show_samples(update, context)
        return
    
    if data == "show_pricing":
        await show_pricing(update, context)
        return
    
    if data == "back_to_start":
        await back_to_start(update, context)
        return
    
    if data.startswith("sub_"):
        specialty = data.replace("sub_", "")
        
        # Save subscriber
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        trial_ends = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        cursor.execute('''
            INSERT OR REPLACE INTO subscribers 
            (user_id, username, name, specialty, subscription_status, trial_ends, joined_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user.id,
            user.username,
            user.full_name,
            specialty,
            "trial",
            trial_ends,
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
        
        spec_name = {
            "cardiology": "🫀 Cardiology",
            "endocrinology": "🍬 Endocrinology", 
            "both": "🫀🍬 Both Specialties"
        }.get(specialty, specialty)
        
        success_text = f"""✅ *Trial Activated!*

Selected: {spec_name}
Trial ends: {trial_ends}

*What's next:*
• First digest tomorrow at 8:00 AM IST
• 3-5 papers daily
• Reply with questions anytime

*Questions?* Just message me!"""
        
        try:
            await query.edit_message_text(
                success_text,
                parse_mode="Markdown"
            )
        except:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=success_text,
                parse_mode="Markdown"
            )


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send today's digest"""
    user = update.effective_user
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT specialty FROM subscribers WHERE user_id = ?",
        (user.id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        await update.message.reply_text(
            "❌ Not subscribed. Use /start to begin your trial!"
        )
        return
    
    specialty = row[0]
    sample = SAMPLE_CARDIO if specialty == "cardiology" else SAMPLE_ENDO
    
    await update.message.reply_text(
        f"📚 *Today's Sample Digest:*\n\n{sample}",
        parse_mode="Markdown"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check subscription status"""
    user = update.effective_user
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT specialty, subscription_status, trial_ends FROM subscribers WHERE user_id = ?",
        (user.id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        await update.message.reply_text("❌ Not subscribed. Use /start to begin.")
        return
    
    specialty, status, trial_ends = row
    
    await update.message.reply_text(
        f"""📊 *Your Subscription*

Specialty: {specialty.title()}
Status: {status.upper()}
Trial ends: {trial_ends}

Use /today to get your latest digest.""",
        parse_mode="Markdown"
    )


def main():
    import os
    os.makedirs("data", exist_ok=True)
    
    bot = MedLitBot()
    
    if not bot.token:
        print("Error: telegram_bot_token not set in config.json")
        return
    
    bot._init_db()
    
    application = Application.builder().token(bot.token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("today", today))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Schedule daily digest
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_daily(
            lambda ctx: asyncio.create_task(send_daily_digests(ctx)),
            time=time(hour=2, minute=30)
        )
    
    print("✅ MedLit Bot is running with working samples!")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


async def send_daily_digests(context):
    """Send daily digests"""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('''
        SELECT user_id, specialty FROM subscribers
        WHERE subscription_status = 'active' 
           OR (subscription_status = 'trial' AND trial_ends >= ?)
    ''', (today,))
    
    subscribers = cursor.fetchall()
    conn.close()
    
    for user_id, specialty in subscribers:
        try:
            sample = SAMPLE_CARDIO if specialty == "cardiology" else SAMPLE_ENDO
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🩺 *MedLit Daily Digest - {datetime.now().strftime('%B %d, %Y')}*\n\n{sample[:1500]}...",
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")


if __name__ == "__main__":
    main()
