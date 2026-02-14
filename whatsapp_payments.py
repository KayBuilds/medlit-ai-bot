#!/usr/bin/env python3
"""
MedLit AI - WhatsApp Handler
Simple click-to-chat and basic automation using WhatsApp Business API
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List

DB_PATH = "data/medlit.db"

# WhatsApp Business API configuration
# For production, use: https://business.whatsapp.com/products/business-platform
WHATSAPP_CONFIG = {
    "phone_number": "+91XXXXXXXXXX",  # Your WhatsApp Business number
    "api_token": "",  # From Meta Business Platform
    "webhook_url": ""  # Your webhook endpoint
}

class WhatsAppHandler:
    """Handle WhatsApp interactions"""
    
    def __init__(self):
        self.config = self._load_config()
        self.phone = self.config.get("admin_phone", "+91XXXXXXXXXX")
    
    def _load_config(self) -> Dict:
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except:
            return {}
    
    def get_click_to_chat_link(self, message: str = None) -> str:
        """Generate WhatsApp click-to-chat link"""
        # Remove + and spaces from phone
        clean_phone = self.phone.replace("+", "").replace(" ", "")
        
        if message:
            import urllib.parse
            encoded_msg = urllib.parse.quote(message)
            return f"https://wa.me/{clean_phone}?text={encoded_msg}"
        else:
            return f"https://wa.me/{clean_phone}"
    
    def generate_qr_code_url(self, size: int = 300) -> str:
        """Generate QR code URL for WhatsApp"""
        link = self.get_click_to_chat_link("START")
        return f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={link}"
    
    def get_welcome_message(self) -> str:
        """Welcome message for WhatsApp users"""
        return """🩺 *Welcome to MedLit AI!*

I deliver daily medical research summaries straight to your WhatsApp.

*Available Specialties:*
🫀 Cardiology — Heart failure, arrhythmias, interventions
🍬 Endocrinology — Diabetes, thyroid, metabolic disorders

*Pricing:*
• One specialty: ₹299/month
• Both: ₹499/month
• First 7 days FREE

Reply with your specialty:
1️⃣ Cardiology
2️⃣ Endocrinology  
3️⃣ Both

Or visit: https://medlit.ai/samples"""
    
    def get_sample_digest_cardio(self) -> str:
        """Sample digest for Cardiology"""
        return """🫀 *MedLit Sample — Cardiology*

*SGLT2 Inhibitors in Heart Failure*
📰 Indian Heart Journal
👤 Cardiologists | 📊 High (RCT)

📝 *Key Finding:*
Analysis of 1,200 HF patients showed 34% reduction in hospitalization with dapagliflozin vs standard care.

💡 *Impact:* 🔴 High
✅ *Action:* Consider SGLT2i for all HF patients regardless of EF

—

Get 3-5 digests like this daily at 8 AM.

*Subscribe:* ₹299/month (7 days free)
Reply PAY to get payment link."""
    
    def get_sample_digest_endo(self) -> str:
        """Sample digest for Endocrinology"""
        return """🍬 *MedLit Sample — Endocrinology*

*CGM vs HbA1c in Type 1 Diabetes*
📰 JCEM
👤 Endocrinologists | 📊 High (Prospective)

📝 *Key Finding:*
CGM identified 7.4x more hypoglycemic episodes than HbA1c. 42% were nocturnal and asymptomatic.

💡 *Impact:* 🔴 High
✅ *Action:* Advocate CGM for all T1DM patients

—

Get 3-5 digests like this daily at 8 AM.

*Subscribe:* ₹299/month (7 days free)
Reply PAY to get payment link."""


class RazorpayIntegration:
    """Generate Razorpay payment links"""
    
    PRICING = {
        "cardiology": {"amount": 29900, "description": "MedLit AI - Cardiology (Monthly)"},
        "endocrinology": {"amount": 29900, "description": "MedLit AI - Endocrinology (Monthly)"},
        "both": {"amount": 49900, "description": "MedLit AI - Both Specialties (Monthly)"}
    }
    
    def __init__(self):
        self.config = self._load_config()
        self.key_id = self.config.get("razorpay_key_id", "")
        self.key_secret = self.config.get("razorpay_key_secret", "")
    
    def _load_config(self) -> Dict:
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except:
            return {}
    
    def generate_payment_link(self, specialty: str, customer_email: str = None, 
                             customer_phone: str = None, customer_name: str = None) -> Dict:
        """
        Generate Razorpay payment link
        
        For actual implementation, use Razorpay Python SDK:
        pip install razorpay
        
        Then:
        import razorpay
        client = razorpay.Client(auth=(key_id, key_secret))
        link = client.payment_link.create({...})
        """
        
        if specialty not in self.PRICING:
            return {"error": "Invalid specialty"}
        
        plan = self.PRICING[specialty]
        
        # This is the payload for Razorpay API
        payment_data = {
            "amount": plan["amount"],  # in paise (₹299 = 29900)
            "currency": "INR",
            "accept_partial": False,
            "description": plan["description"],
            "customer": {
                "name": customer_name or "Doctor",
                "email": customer_email or "doctor@hospital.com",
                "contact": customer_phone or "+919999999999"
            },
            "notify": {
                "sms": True,
                "email": True
            },
            "reminder_enable": True,
            "notes": {
                "specialty": specialty,
                "plan": "monthly"
            },
            "callback_url": "https://medlit.ai/payment-success",
            "callback_method": "get"
        }
        
        # For now, return instructions
        return {
            "status": "manual_setup_required",
            "payment_data": payment_data,
            "instructions": """
To create payment link:

1. Login to https://dashboard.razorpay.com
2. Go to Payment Links → + Create New
3. Set amount: ₹{amount}/month
4. Description: {description}
5. Add customer details
6. Copy the short URL
7. Share with customer

Or use Razorpay API:
```python
import razorpay
client = razorpay.Client(auth=("YOUR_KEY_ID", "YOUR_KEY_SECRET"))
link = client.payment_link.create({payment_data})
short_url = link['short_url']
```
            """.format(amount=plan["amount"]//100, description=plan["description"])
        }
    
    def get_quick_links(self) -> Dict:
        """Get manual payment links (create these in Razorpay dashboard)"""
        return {
            "cardiology": {
                "amount": "₹299/month",
                "setup_instructions": """
1. Go to https://dashboard.razorpay.com/app/payment-links
2. Click 'Create Payment Link'
3. Amount: 29900 (paise)
4. Description: 'MedLit AI - Cardiology Monthly'
5. Save and copy the link
"""
            },
            "endocrinology": {
                "amount": "₹299/month",
                "setup_instructions": """
1. Go to https://dashboard.razorpay.com/app/payment-links  
2. Click 'Create Payment Link'
3. Amount: 29900 (paise)
4. Description: 'MedLit AI - Endocrinology Monthly'
5. Save and copy the link
"""
            },
            "both": {
                "amount": "₹499/month",
                "setup_instructions": """
1. Go to https://dashboard.razorpay.com/app/payment-links
2. Click 'Create Payment Link'
3. Amount: 49900 (paise)
4. Description: 'MedLit AI - Both Specialties Monthly'
5. Save and copy the link
"""
            }
        }


def main():
    """Demo usage"""
    print("=" * 60)
    print("MedLit AI - WhatsApp & Payment Setup")
    print("=" * 60)
    
    # WhatsApp
    print("\nWHATSAPP Click-to-Chat Links:")
    print("-" * 60)
    wa = WhatsAppHandler()
    print(f"General: {wa.get_click_to_chat_link()}")
    print(f"With message: {wa.get_click_to_chat_link('START')}")
    print(f"\nQR Code URL: {wa.generate_qr_code_url()}")
    
    # Razorpay
    print("\nRAZORPAY Payment Setup:")
    print("-" * 60)
    rz = RazorpayIntegration()
    links = rz.get_quick_links()
    
    for specialty, info in links.items():
        print(f"\n{specialty.upper()}:")
        print(f"  Price: {info['amount']}")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("1. Set up WhatsApp Business: https://business.whatsapp.com")
    print("2. Create Razorpay account: https://razorpay.com")
    print("3. Generate payment links in dashboard")
    print("4. Update config.json with your details")
    print("=" * 60)


if __name__ == "__main__":
    main()
