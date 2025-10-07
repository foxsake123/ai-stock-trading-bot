#!/usr/bin/env python3
"""
Send Telegram instructions for completing the automated setup
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
    """Send setup instructions"""

    message = f"""<b>FINAL STEP: ENABLE AUTOMATED EXECUTION</b>

All files are ready! Complete automation requires ONE quick step (needs Administrator privileges):

<b>OPTION 1: One-Click Setup (Recommended)</b>

1. Navigate to:
   C:\\Users\\shorg\\ai-stock-trading-bot\\scripts\\windows

2. Right-click on:
   SETUP_AUTOMATED_EXECUTION.bat

3. Select:
   "Run as administrator"

4. Click "Yes" when Windows asks for permission

That's it! You'll receive a confirmation message when done.

<b>OPTION 2: Manual Setup (Alternative)</b>

1. Press Win+R
2. Type: taskschd.msc
3. Press Enter
4. Click "Import Task..." (right sidebar)
5. Browse to: C:\\Users\\shorg\\ai-stock-trading-bot\\scripts\\windows\\Oct8_Execution_Task.xml
6. Click Open, then OK

<b>OPTION 3: Run Manually Tomorrow</b>

Don't schedule it - just run this when you wake up:
C:\\Users\\shorg\\ai-stock-trading-bot\\scripts\\windows\\EXECUTE_OCT8_TRADES.bat

The script will execute all orders and send Telegram updates.

<b>What Happens After Setup:</b>

Tomorrow at 9:30 AM ET, your computer will:
1. Wake up (if asleep)
2. Execute all 9 approved orders
3. Place 4 stop-loss orders
4. Send you Telegram notifications throughout

<b>Current Status:</b>
- Execution script: READY
- Telegram notifications: ENABLED
- Scheduled task file: CREATED
- Final step: Needs Administrator permission

<b>Choose your option and you're all set!</b>

I recommend Option 1 (Run as administrator) - takes 5 seconds.
"""

    success = send_telegram(message)

    if success:
        print("\n" + "="*80)
        print("SETUP INSTRUCTIONS SENT VIA TELEGRAM")
        print("="*80)
        print()
        print("All automation files are ready!")
        print()
        print("NEXT STEP (Choose one):")
        print()
        print("OPTION 1 - One-Click Setup (Recommended):")
        print("  1. Right-click: scripts\\windows\\SETUP_AUTOMATED_EXECUTION.bat")
        print("  2. Select: 'Run as administrator'")
        print("  3. Click 'Yes' when prompted")
        print()
        print("OPTION 2 - Manual Task Scheduler:")
        print("  1. Press Win+R, type: taskschd.msc")
        print("  2. Import Task: scripts\\windows\\Oct8_Execution_Task.xml")
        print()
        print("OPTION 3 - Run Manually Tomorrow:")
        print("  Just double-click: scripts\\windows\\EXECUTE_OCT8_TRADES.bat")
        print()
        print("Check Telegram for detailed instructions!")
        print("="*80)
    else:
        print("[WARNING] Could not send Telegram instructions")
        print("Please run scripts\\windows\\SETUP_AUTOMATED_EXECUTION.bat as Administrator")

    return 0

if __name__ == "__main__":
    exit(main())
