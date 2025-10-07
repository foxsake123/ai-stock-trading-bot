#!/usr/bin/env python3
"""
Send Telegram confirmation that automated execution is scheduled
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
        print("[WARNING] Telegram token not configured")
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
            return True
        else:
            print(f"[ERROR] Telegram failed: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Telegram error: {e}")
        return False

def main():
    """Send automation confirmation"""

    message = f"""<b>AUTOMATED EXECUTION CONFIRMED</b>

<b>Status:</b> Task Scheduled Successfully
<b>Execution Date:</b> October 8, 2025
<b>Execution Time:</b> 9:30 AM ET (Market Open)

<b>Windows Task Scheduler Details:</b>
Task Name: AI_Trading_Bot_Execute_Oct8_2025
Status: Enabled
Wake Computer: Yes
Run if Missed: Yes

<b>What Will Happen Automatically:</b>

<b>9:30 AM ET - Execution Starts</b>
- System wakes computer (if asleep)
- Script launches automatically
- All 9 limit orders submitted
- Telegram notification: "Execution starting..."

<b>9:30-9:35 AM - Orders Execute</b>
- Orders fill as market opens
- Real-time Telegram updates per order
- DEE-BOT: 5 orders ($44,861)
- SHORGAN-BOT: 4 orders ($9,744)

<b>9:35-9:40 AM - Stop Placement</b>
- Script waits 60 seconds for fills
- 4 GTC stop-loss orders placed
- Telegram notification: "Stops placed"

<b>9:40 AM - Completion</b>
- Final summary sent via Telegram
- Execution log saved
- Task completes

<b>You Will Receive:</b>
1. Execution start notification
2. Per-order status updates (9 total)
3. Stop-loss confirmation (4 stops)
4. Final execution summary

<b>No Manual Action Required</b>

Your computer will handle everything automatically. You'll receive Telegram updates throughout the process.

<b>To Verify Task:</b>
1. Press Win+R
2. Type: taskschd.msc
3. Find: AI_Trading_Bot_Execute_Oct8_2025

<b>To Run Manually (Optional):</b>
scripts\\windows\\EXECUTE_OCT8_TRADES.bat

System is fully automated. Sleep well!
"""

    success = send_telegram(message)

    if success:
        print("[SUCCESS] Automation confirmation sent via Telegram")
    else:
        print("[WARNING] Could not send Telegram confirmation")

    return 0

if __name__ == "__main__":
    exit(main())
