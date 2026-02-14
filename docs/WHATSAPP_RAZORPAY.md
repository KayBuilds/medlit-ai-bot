# WhatsApp & Razorpay Setup Guide

## 📱 WhatsApp Business Setup

### Option 1: WhatsApp Business App (FREE - Start Here)

**Best for:** Getting started immediately, small volume (<100 customers)

1. **Download WhatsApp Business**
   - Android: Play Store → "WhatsApp Business"
   - iOS: App Store → "WhatsApp Business"

2. **Set Up Business Profile**
   ```
   Business Name: MedLit AI
   Category: Healthcare/Medical
   Description: Daily AI-summarized medical research for doctors
   Email: kashif@medlit.ai
   Website: https://medlit.ai (after deployment)
   ```

3. **Create Click-to-Chat Link**
   - Get your WhatsApp Business number (e.g., +91-98765-43210)
   - Link: `https://wa.me/919876543210?text=START`
   - Update this in:
     - `web/index.html`
     - `web/samples.html`
     - Landing page CTA buttons

4. **Set Up Quick Replies**
   ```
   /start - Welcome message
   /price - Pricing information
   /samples - Link to sample digests
   /pay - Payment instructions
   ```

5. **QR Code for Marketing**
   - Generate at: https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=https://wa.me/919876543210?text=START
   - Print on cards, add to LinkedIn, share in doctor groups

---

### Option 2: WhatsApp Business API (For Scale)

**Best for:** >100 customers, automation, scheduling

**Cost:** ~$0.005-0.05 per message

1. **Choose Provider:**
   - **360dialog** (https://360dialog.com) - India-friendly
   - **MessageBird** (https://messagebird.com)
   - **Twilio** (https://twilio.com)

2. **360dialog Setup (Recommended for India):**
   ```bash
   # Sign up at 360dialog.com
   # Cost: ~$30/month + message fees
   # Get API key
   ```

3. **API Integration:**
   ```python
   import requests
   
   API_KEY = "your_360dialog_api_key"
   PHONE_NUMBER = "919876543210"
   
   def send_whatsapp_message(to_number, message):
       url = f"https://waba.360dialog.io/v1/messages"
       headers = {
           "D360-API-KEY": API_KEY,
           "Content-Type": "application/json"
       }
       payload = {
           "messaging_product": "whatsapp",
           "to": to_number,
           "type": "text",
           "text": {"body": message}
       }
       response = requests.post(url, json=payload, headers=headers)
       return response.json()
   ```

4. **Webhook for Incoming Messages:**
   - Set up webhook URL in 360dialog dashboard
   - Handle incoming messages (START, PAY, etc.)

---

## 💳 Razorpay Payment Setup

### Step 1: Create Account

1. Go to https://razorpay.com
2. Sign up with business details
3. Complete KYC (takes 1-2 days)
4. Get API Keys from Dashboard → Settings → API Keys
   - Key ID: `rzp_test_...` (test) or `rzp_live_...` (production)
   - Key Secret: `...`

### Step 2: Create Payment Links

**Method A: Dashboard (Manual)**

1. Login: https://dashboard.razorpay.com/app/payment-links
2. Click "+ Create Payment Link"
3. Create 3 links:

```
Link 1: Cardiology Monthly
- Amount: ₹299
- Description: "MedLit AI - Cardiology (Monthly Subscription)"
- Customer Details: Optional
- Save as template: Yes

Link 2: Endocrinology Monthly
- Amount: ₹299
- Description: "MedLit AI - Endocrinology (Monthly Subscription)"

Link 3: Both Specialties Monthly
- Amount: ₹499
- Description: "MedLit AI - Both Specialties (Monthly Subscription)"
```

4. Copy short URLs (e.g., `razorpay.me/@medlit-cardio`)
5. Add to your bot responses and landing page

**Method B: API (Automated)**

```python
import razorpay

client = razorpay.Client(auth=("rzp_live_YOUR_KEY_ID", "YOUR_KEY_SECRET"))

def create_payment_link(specialty, customer_email):
    pricing = {
        "cardiology": {"amount": 29900, "description": "MedLit AI - Cardiology"},
        "endocrinology": {"amount": 29900, "description": "MedLit AI - Endocrinology"},
        "both": {"amount": 49900, "description": "MedLit AI - Both Specialties"}
    }
    
    plan = pricing[specialty]
    
    payment_link = client.payment_link.create({
        "amount": plan["amount"],
        "currency": "INR",
        "description": plan["description"],
        "customer": {"email": customer_email},
        "notify": {"email": True},
        "reminder_enable": True,
        "notes": {"specialty": specialty}
    })
    
    return payment_link["short_url"]

# Usage
url = create_payment_link("cardiology", "doctor@hospital.com")
print(url)  # e.g., https://razorpay.me/@medlit-ai/abc123
```

### Step 3: Payment Webhook

Set up webhook to auto-activate subscriptions:

1. Dashboard → Settings → Webhooks → Add New
2. URL: `https://yourdomain.com/webhook/razorpay`
3. Secret: Generate a random string
4. Events: `payment_link.paid`, `payment.captured`

```python
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhook/razorpay', methods=['POST'])
def razorpay_webhook():
    webhook_secret = "your_webhook_secret"
    
    # Verify signature
    signature = request.headers.get('X-Razorpay-Signature')
    body = request.get_data()
    
    expected = hmac.new(
        webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if signature != expected:
        return "Invalid signature", 400
    
    data = request.json
    
    # Handle payment success
    if data['event'] == 'payment_link.paid':
        customer_email = data['payload']['payment']['entity']['email']
        specialty = data['payload']['payment_link']['entity']['notes']['specialty']
        
        # Activate subscription in database
        activate_subscription(customer_email, specialty)
        
        # Send welcome message
        send_whatsapp_message(customer_phone, "Payment received! Your subscription is active.")
    
    return "OK", 200
```

---

## 🔗 Integration Checklist

### Update These Files:

1. **config.json**
```json
{
  "telegram_bot_token": "8453120303:AAElOAgxz8dtBRM6b95OgFsa-LVEnYCo_tA",
  "whatsapp_api_key": "your_360dialog_key",
  "admin_phone": "+919876543210",
  "admin_email": "kashif@medlit.ai",
  "razorpay_key_id": "rzp_live_...",
  "razorpay_key_secret": "...",
  "razorpay_webhook_secret": "..."
}
```

2. **web/index.html**
   - Update WhatsApp link: `https://wa.me/91YOURNUMBER?text=START`
   - Update Telegram link: `https://t.me/MedJournal_bot`

3. **web/samples.html**
   - Same updates as above

4. **bot/telegram_bot.py**
   - Add Razorpay payment links in responses

---

## 📊 Test Flow

1. **Customer Journey:**
   - Doctor visits landing page → sees samples
   - Clicks WhatsApp link → sends "START"
   - You reply with specialty options
   - They choose → you send payment link
   - They pay → webhook activates subscription
   - They receive first digest at 8 AM

2. **Test Payments:**
   - Use Razorpay test mode first
   - Test card: `5267 3181 8797 5449`
   - Any future date, any CVV

---

## 💰 Revenue Calculation

With Razorpay:
- Transaction fee: 2% + GST (≈2.36%)
- On ₹299: Fee = ₹7.05, You get = ₹291.95
- On ₹499: Fee = ₹11.78, You get = ₹487.22

**To hit ₹10K/month net:**
- Need ₹10,280 in sales
- At ₹299: 35 customers
- At ₹499: 21 customers

---

## 🚀 Quick Start (Next 30 Minutes)

1. ✅ Set up WhatsApp Business App (5 min)
2. ✅ Create Razorpay account (5 min)
3. ✅ Create 3 payment links (5 min)
4. ✅ Update landing page with links (5 min)
5. ✅ Deploy to Netlify (10 min)
6. ✅ Test complete flow (5 min)

**You're live and ready to take payments!**
