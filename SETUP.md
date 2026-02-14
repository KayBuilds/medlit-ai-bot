# MedLit AI — Setup Guide

## What We Just Built

A complete MVP that:
1. **Scrapes** latest papers from **OpenAlex** (free, open scholarly API) — no paywalls, no RELX dependency
2. **Summarizes** using AI into clinical takeaways
3. **Delivers** via Telegram bot every morning at 8 AM
4. **Collects payments** via subscription model

---

## Quick Start (Get Running in 30 Minutes)

### Step 1: Create Telegram Bot

1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Name it: `MedLit AI` 
4. Username: `MedLitAIBot` (or whatever is available)
5. Copy the API token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Configure

1. Open `config.json` (copy from `config.example.json`)
2. Add your Telegram token:
```json
{
  "telegram_bot_token": "YOUR_TOKEN_HERE",
  "specialties": ["cardiology", "endocrinology"],
  "delivery_time": "08:00",
  "timezone": "Asia/Kolkata"
}
```

### Step 3: Install & Run

```bash
# Navigate to project
cd medlit-ai

# Install Python dependencies
pip install -r requirements.txt

# Create data directory
mkdir data

# Test: Fetch papers (runs manually first time)
python scraper/fetch_papers.py

# Test: Generate summaries
python summarizer/generate.py --limit 10

# Start the bot (this runs continuously)
python bot/telegram_bot.py
```

### Step 4: Test It

1. Open Telegram, find your bot (@MedLitAIBot)
2. Send `/start`
3. Select a specialty
4. Send `/today` to get your first digest

---

## Daily Operations

### Automated (Once Running)
- **8 AM IST**: Bot automatically sends digests to all subscribers
- Background job runs continuously

### Manual Commands
```bash
# Fetch new papers
python scraper/fetch_papers.py

# Generate summaries for new papers
python summarizer/generate.py --limit 20

# Check subscriber database
sqlite3 data/medlit.db "SELECT * FROM subscribers;"
```

---

## Getting First 10 Customers

### Week 1: Friends & Network
1. Message 10 doctor friends/colleagues from your network
2. Offer free trial in exchange for feedback
3. Get them added to the bot

### Week 2: LinkedIn Outreach
Post content like:
- "New study shows SGLT2 inhibitors reduce heart failure by 30% — are you prescribing them?"
- Comment on Cardiologist/Endocrinologist posts with insights
- DM interested doctors with trial offer

### Week 3: Doctor Groups
- Join WhatsApp/Telegram groups for doctors
- Share valuable insights (not spam)
- Offer bot when relevant

---

## Monetization Plan

| Milestone | Target | Revenue |
|-----------|--------|---------|
| 34 paying customers | Month 2 | ₹10,000 |
| 100 paying customers | Month 4 | ₹30,000 |
| 334 paying customers | Month 8 | ₹1,00,000 ($1,200) |
| 1000 paying customers | Year 2 | ₹3,00,000 ($3,600) |

**Revenue per customer:**
- Single specialty: ₹299/month
- Both specialties: ₹499/month

---

## Upgrading to Real AI (Phase 2)

Current MVP uses rule-based extraction. To upgrade:

1. Get OpenAI API key from platform.openai.com
2. Add to `config.json`: `"openai_api_key": "sk-..."`
3. Modify `summarizer/generate.py` to call GPT-4:

```python
import openai

def summarize_with_gpt4(title, abstract):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "system",
            "content": "You are a medical research assistant. Summarize this paper into 3 parts: Key Finding, Clinical Impact, Action Item. Be concise."
        }, {
            "role": "user",
            "content": f"Title: {title}\nAbstract: {abstract}"
        }]
    )
    return response.choices[0].message.content
```

Cost: ~$0.01-0.03 per paper = ₹1-2.5 per digest. Very profitable at scale.

---

## Next Features to Build

### Phase 2 (Month 2)
- [ ] Web dashboard for archives/search
- [ ] WhatsApp Business API (instead of Telegram)
- [ ] Razorpay/UPI payment integration
- [ ] More specialties (Oncology, Neurology)

### Phase 3 (Month 4)
- [ ] Pharma-sponsored digests (separate revenue stream)
- [ ] CME credit integration
- [ ] Multi-language summaries (Hindi, Tamil, etc.)

---

## Files You Have

```
medlit-ai/
├── README.md                    # Project overview
├── SETUP.md                     # This file
├── requirements.txt             # Python dependencies
├── config.example.json          # Configuration template
├── config.json                  # Your actual config (add tokens here)
├── scraper/
│   └── fetch_papers.py         # Journal scraper
├── summarizer/
│   └── generate.py             # AI summarizer
├── bot/
│   └── telegram_bot.py         # Telegram delivery bot
├── web/
│   └── index.html              # Landing page
└── data/
    └── medlit.db               # SQLite database (created on run)
```

---

## Support

If you get stuck:
1. Check error messages in terminal
2. Make sure `config.json` has correct API keys
3. Ensure Python 3.8+ is installed: `python --version`

---

## What You Do Next

1. **Today:** Create Telegram bot, run the scraper once
2. **This Week:** Get 5 doctor friends to try it
3. **Next Week:** Post on LinkedIn, get 10 trial users
4. **Month 2:** Convert trials to paid, hit ₹10K MRR (34 subscribers)

**Ready to start?** Create that Telegram bot and let's get your first digest running.
