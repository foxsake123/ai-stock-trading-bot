"""
Check if Tuesday trades are ready and automation is set up
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
import requests

def check_status():
    print("="*60)
    print("TUESDAY TRADING STATUS CHECK")
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    status_good = True

    # 1. Check if trades file exists
    print("\n1. Checking for Tuesday trades file...")
    trades_file = Path("TODAYS_TRADES_2025-09-30.md")
    if trades_file.exists():
        print(f"   [OK] Found: {trades_file.name}")

        # Count trades in file
        with open(trades_file, 'r') as f:
            content = f.read()
            dee_trades = content.count("DEE-BOT")
            shorgan_trades = content.count("SHORGAN-BOT")
            print(f"   [OK] DEE-BOT trades ready: {dee_trades}")
            print(f"   [OK] SHORGAN-BOT trades ready: {shorgan_trades}")
    else:
        print("   [FAIL] No trades file found!")
        print("   Run: python scripts-and-data/automation/complete_weekly_workflow.py")
        status_good = False

    # 2. Check Windows Task Scheduler
    print("\n2. Checking Windows Task Scheduler...")
    try:
        result = subprocess.run(
            ['schtasks', '/query', '/fo', 'list'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if 'AI Trading Bot' in result.stdout:
            tasks = result.stdout.count('AI Trading Bot')
            print(f"   [OK] Found {tasks} scheduled tasks")

            if 'Tuesday Execution' in result.stdout:
                print("   [OK] Tuesday specific task found")
            else:
                print("   [INFO] No Tuesday-specific task (using daily tasks)")
        else:
            print("   [WARNING] No automated tasks found")
            print("   To automate: Run setup_tuesday_automation.bat as Administrator")
    except:
        print("   [WARNING] Could not check scheduled tasks")

    # 3. Check execution script
    print("\n3. Checking execution script...")
    exec_script = Path("scripts-and-data/automation/execute_daily_trades.py")
    if exec_script.exists():
        print(f"   [OK] Execution script ready: {exec_script.name}")
    else:
        print("   [FAIL] Execution script missing!")
        status_good = False

    # 4. Check Alpaca connection
    print("\n4. Checking broker connections...")
    try:
        import alpaca_trade_api as tradeapi

        # Test DEE connection
        dee_api = tradeapi.REST(
            'PK6FZK4DAQVTD7DYVH78',
            'JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt',
            'https://paper-api.alpaca.markets'
        )
        account = dee_api.get_account()
        print(f"   [OK] DEE-BOT connected: ${float(account.portfolio_value):,.2f}")

        # Test SHORGAN connection
        shorgan_api = tradeapi.REST(
            'PKJRLSB2MFEJUSK6UK2E',
            'QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic',
            'https://paper-api.alpaca.markets'
        )
        account = shorgan_api.get_account()
        print(f"   [OK] SHORGAN-BOT connected: ${float(account.portfolio_value):,.2f}")

    except Exception as e:
        print(f"   [FAIL] Broker connection error: {e}")
        status_good = False

    # 5. Check key positions to monitor
    print("\n5. Key positions to monitor Tuesday:")
    print("   - FBIO: Check FDA decision from Monday")
    print("   - BBAI: Monitor for Wednesday earnings")
    print("   - RGTI: +117% gain (trailing stop $25)")
    print("   - SAVA: +50% gain (CEO buying)")
    print("   - Cover all short positions")

    # Summary
    print("\n" + "="*60)
    if status_good:
        print("STATUS: READY FOR TUESDAY TRADING")
        print("="*60)
        print("\nOPTION 1 - Fully Automated (if scheduled):")
        print("   No action needed - trades execute at 9:30 AM")
        print("\nOPTION 2 - Manual Trigger (if not scheduled):")
        print("   At 9:30 AM run: python scripts-and-data/automation/execute_daily_trades.py")
    else:
        print("STATUS: ISSUES NEED ATTENTION")
        print("="*60)
        print("\nFix the issues above before market open")

    # Send Telegram alert
    try:
        telegram_token = "8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c"
        chat_id = "7870288896"

        if status_good:
            message = "✅ TUESDAY READY\n\nSystem checked and ready for trading.\nTrades will execute at 9:30 AM."
        else:
            message = "⚠️ TUESDAY NEEDS ATTENTION\n\nIssues detected. Check system before market open."

        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        requests.post(url, data={'chat_id': chat_id, 'text': message})
        print("\nTelegram alert sent!")

    except:
        print("\nCould not send Telegram alert")

if __name__ == "__main__":
    check_status()