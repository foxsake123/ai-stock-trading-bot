#!/usr/bin/env python3
"""
Send Telegram notification about tomorrow's automated trading plan
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
    """Send tomorrow's execution plan notification"""

    message = f"""<b>AI TRADING BOT - AUTOMATED EXECUTION SCHEDULED</b>

<b>Execution Date:</b> October 8, 2025
<b>Execution Time:</b> Market Open (9:30 AM ET)
<b>Status:</b> READY FOR AUTOMATED EXECUTION

<b>User Approved Option B (Oct 7, 10:50 PM ET)</b>

<b>=== EXECUTION PLAN (9 TOTAL ORDERS) ===</b>

<b>DEE-BOT (5 orders - $44,861):</b>
1. BUY 93 WMT @ $102.00 LIMIT (DAY)
2. BUY 22 UNH @ $360.00 LIMIT (DAY)
3. BUY 95 NEE @ $80.00 LIMIT (DAY)
4. BUY 11 COST @ $915.00 LIMIT (DAY)
5. BUY 110 MRK @ $89.00 LIMIT (DAY)

<b>SHORGAN-BOT (4 orders - $9,744):</b>
6. BUY 150 ARQT @ $20.00 LIMIT (DAY)
   Stop: $16.50 | FDA Decision Oct 13
   Multi-Agent Score: 80%

7. BUY 37 HIMS @ $54.00 LIMIT (DAY)
   Stop: $49.00 | Active Short Squeeze
   Multi-Agent Score: 74%

8. BUY 96 WOLF @ $26.00 LIMIT (DAY)
   Stop: $22.00 | Delisting Catalyst Oct 10
   Multi-Agent Score: 71%

9. SELL SHORT 500 PLUG @ $4.50 LIMIT (DAY)
   Stop: $5.50 (BUY TO COVER)
   Multi-Agent Score: 59%

<b>=== RISK PROFILE ===</b>
Total Capital Deployed: $54,605 (54.6%)
Cash Reserve: $145,395 (45.4%)
Max Loss (All Stops Hit): $1,594 (1.6%)
Max Gain (All Targets): $2,960 (3.0%)
Risk/Reward Ratio: 1:1.9 (asymmetric)

<b>=== AUTOMATED WORKFLOW ===</b>
1. Pre-Market (6:30-9:30 AM):
   - Script will place all 9 limit orders
   - Orders queued for market open

2. Market Open (9:30-10:00 AM):
   - Orders execute as market opens
   - Real-time Telegram notifications
   - Stop-loss orders placed after fills

3. Afternoon (2:00 PM ET):
   - FOMC Minutes release (HIGH VOLATILITY)
   - Monitor all positions closely

<b>=== CATALYST MONITORING ===</b>
Oct 8 (Tuesday): FOMC Minutes 2PM ET
Oct 10 (Thursday): WOLF Delisting Event
Oct 13 (Monday): ARQT FDA Decision

<b>=== EXECUTION METHOD ===</b>
Script: execute_oct8_trades.py
Batch File: EXECUTE_OCT8_TRADES.bat
Status: Automated, no manual intervention required

<b>=== NOTIFICATION SCHEDULE ===</b>
You will receive Telegram alerts for:
- Execution start confirmation
- Each order status (success/fail)
- Stop-loss placement confirmation
- Final execution summary

<b>System Ready. Execution will begin automatically at market open.</b>

To run manually at any time:
scripts\windows\EXECUTE_OCT8_TRADES.bat

Document Reference:
docs/reports/post-market/FINAL_APPROVED_ORDERS_OCT8_2025.md
"""

    print("="*80)
    print("SENDING TOMORROW'S EXECUTION PLAN TO TELEGRAM")
    print("="*80)
    print()

    success = send_telegram(message)

    if success:
        print("\n[SUCCESS] Plan notification sent via Telegram")
        print("You will receive automated updates tomorrow during execution")
    else:
        print("\n[ERROR] Failed to send notification")
        print("Please check your Telegram configuration in .env file")

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
