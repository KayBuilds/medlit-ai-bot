from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8453120303:AAElOAgxz8dtBRM6b95OgFsa-LVEnYCo_tA"

SAMPLE_TEXT = """🫀 SAMPLE Cardiology Digest

1️⃣ SGLT2 Inhibitors in Heart Failure
📰 Indian Heart Journal

📝 Key Finding:
34% reduction in hospitalization with dapagliflozin

💡 Impact: HIGH
✅ Action: Consider for all HF patients

2️⃣ Triple Therapy in AF + Diabetes
42% MACE reduction with triple therapy

3️⃣ Early Rhythm Control in AF
24% CV death reduction at 5 years

You get 3-5 like this daily at 8 AM"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! Click below to see sample:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("See Sample", callback_data="sample")],
            [InlineKeyboardButton("Start Trial", callback_data="subscribe")]
        ])
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "sample":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=SAMPLE_TEXT
        )
    elif query.data == "subscribe":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Trial activated! You'll get digests at 8 AM."
        )

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

print("Bot running...")
app.run_polling()
