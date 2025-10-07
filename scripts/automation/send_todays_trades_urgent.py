#!/usr/bin/env python3
"""
Send urgent notification of today's approved trades (Oct 7, 2025)
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-4524457329')

def send_telegram(message):
    """Send message via Telegram"""
    if not TELEGRAM_TOKEN:
        print("[ERROR] Telegram token not configured")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            print("[SUCCESS] Telegram notification sent")
            return True
        else:
            print(f"[ERROR] Telegram failed: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Telegram error: {e}")
        return False

def main():
    """Send today's trades URGENTLY"""

    message = f"""<b>URGENT - TODAY'S TRADES (OCT 7, 2025)</b>

<b>Market Opens: 9:30 AM ET (SOON!)</b>
<b>User Approved: Option B (9 orders)</b>

<b>=== EXECUTE THESE ORDERS TODAY ===</b>

<b>DEE-BOT (5 orders - $44,861):</b>
1. BUY 93 WMT @ $102.00 LIMIT (DAY)
2. BUY 22 UNH @ $360.00 LIMIT (DAY)
3. BUY 95 NEE @ $80.00 LIMIT (DAY)
4. BUY 11 COST @ $915.00 LIMIT (DAY)
5. BUY 110 MRK @ $89.00 LIMIT (DAY)

<b>SHORGAN-BOT (4 orders - $9,744):</b>
6. BUY 150 ARQT @ $20.00 LIMIT (DAY)
   Stop: $16.50 (GTC) - FDA Oct 13

7. BUY 37 HIMS @ $54.00 LIMIT (DAY)
   Stop: $49.00 (GTC) - Short Squeeze

8. BUY 96 WOLF @ $26.00 LIMIT (DAY)
   Stop: $22.00 (GTC) - Delisting Oct 10

9. SELL SHORT 500 PLUG @ $4.50 LIMIT (DAY)
   Stop: $5.50 (BUY TO COVER) GTC

<b>=== STOP-LOSS ORDERS (Place after fills) ===</b>
ARQT: STOP 150 @ $16.50 (GTC)
HIMS: STOP 37 @ $49.00 (GTC)
WOLF: STOP 96 @ $22.00 (GTC)
PLUG: STOP (BUY) 500 @ $5.50 (GTC)

<b>=== RISK PROFILE ===</b>
Total Deployed: $54,605 (54.6%)
Cash Reserve: $145,395 (45.4%)
Max Loss: $1,594 (1.6%)
Max Gain: $2,960 (3.0%)
Risk/Reward: 1:1.9

<b>=== MULTI-AGENT SCORES ===</b>
ARQT: 80% (TOP PICK - FDA catalyst)
HIMS: 74% (Active squeeze)
WOLF: 71% (Delisting Oct 10)
PLUG: 59% (SHORT - fuel cell sector)

<b>=== ACTION REQUIRED ===</b>
1. Place all 9 limit orders NOW
2. Set 4 GTC stop-loss orders after fills
3. Monitor FOMC Minutes at 2 PM ET (HIGH VOLATILITY)

<b>=== CATALYST MONITORING ===</b>
Today (Oct 7): Market open execution
Oct 7 (2 PM): FOMC Minutes release
Oct 10: WOLF delisting
Oct 13: ARQT FDA decision

<b>Orders ready for execution!</b>

Reference: FINAL_APPROVED_ORDERS_OCT8_2025.md
(Note: File name has wrong date - these are for TODAY Oct 7)
"""

    print("="*80)
    print("SENDING URGENT TRADES NOTIFICATION FOR TODAY (OCT 7, 2025)")
    print("="*80)
    print()

    success = send_telegram(message)

    if success:
        print("\n[SUCCESS] Today's trades sent via Telegram")
        print("Market opens at 9:30 AM ET - orders should be placed NOW")
    else:
        print("\n[ERROR] Failed to send notification")
        print("Please check your Telegram configuration")

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
