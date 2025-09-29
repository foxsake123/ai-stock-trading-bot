"""
Quick System Health Check
Run this for instant status of the trading bot
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import json

def check_status():
    """Quick status check of all systems"""

    print("=" * 60)
    print(f"AI TRADING BOT - QUICK STATUS CHECK")
    print(f"{datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
    print("=" * 60)

    status = {'ok': 0, 'warn': 0, 'fail': 0}

    # Check today's trades
    today = datetime.now().strftime('%Y-%m-%d')
    trades_file = Path(f'docs/TODAYS_TRADES_{today}.md')

    if trades_file.exists():
        print(f"[OK] Today's trades file exists")
        status['ok'] += 1

        with open(trades_file, 'r') as f:
            content = f.read()
            trades = content.count('|') // 10  # Rough estimate
            print(f"     Found approximately {trades} trades")
    else:
        print(f"[WARN] No trades file for today (will auto-generate)")
        status['warn'] += 1

    # Check critical scripts
    critical_files = [
        'scripts-and-data/automation/execute_daily_trades.py',
        'scripts-and-data/automation/generate_todays_trades.py',
        'scripts-and-data/automation/automated_chatgpt_fetcher.py',
        'communication/coordinator.py'
    ]

    all_exist = True
    for file in critical_files:
        if not Path(file).exists():
            print(f"[FAIL] Missing: {file}")
            status['fail'] += 1
            all_exist = False

    if all_exist:
        print(f"[OK] All critical files present")
        status['ok'] += 1

    # Check position files
    dee_csv = Path('scripts-and-data/daily-csv/dee-bot-positions.csv')
    shorgan_csv = Path('scripts-and-data/daily-csv/shorgan-bot-positions.csv')

    if dee_csv.exists() and shorgan_csv.exists():
        print(f"[OK] Position tracking files exist")
        status['ok'] += 1
    else:
        print(f"[FAIL] Position files missing")
        status['fail'] += 1

    # Check for recent execution logs
    log_dir = Path('scripts-and-data/trade-logs')
    if log_dir.exists():
        logs = list(log_dir.glob('*.json'))
        if logs:
            latest = max(logs, key=lambda p: p.stat().st_mtime)

            # Read latest log
            try:
                with open(latest, 'r') as f:
                    data = json.load(f)

                executed = len(data.get('executed_trades', []))
                failed = len(data.get('failed_trades', []))
                total = executed + failed

                if total > 0:
                    success_rate = (executed / total) * 100
                    print(f"[INFO] Last execution: {executed}/{total} trades ({success_rate:.0f}% success)")

                    if success_rate >= 80:
                        status['ok'] += 1
                    elif success_rate >= 50:
                        status['warn'] += 1
                    else:
                        status['fail'] += 1
            except:
                pass

    # Check API config
    api_keys_file = Path('config/api_keys.yaml')
    if api_keys_file.exists():
        print(f"[OK] API configuration found")
        status['ok'] += 1
    else:
        # Check environment variables
        if os.getenv('APCA_API_KEY_ID'):
            print(f"[OK] API keys in environment")
            status['ok'] += 1
        else:
            print(f"[WARN] API configuration needs setup")
            status['warn'] += 1

    # Summary
    print("\n" + "=" * 60)
    total_checks = status['ok'] + status['warn'] + status['fail']

    if status['fail'] == 0 and status['warn'] <= 1:
        print("SYSTEM STATUS: READY FOR TRADING")
        print("All systems operational. Ready for 9:30 AM execution.")
    elif status['fail'] == 0:
        print("SYSTEM STATUS: READY (with warnings)")
        print("System can trade but check warnings above.")
    else:
        print("SYSTEM STATUS: NEEDS ATTENTION")
        print("Critical issues found. Fix before trading.")

    print(f"\nChecks: {status['ok']} OK, {status['warn']} WARN, {status['fail']} FAIL")
    print("=" * 60)

    # Quick tips
    if status['warn'] > 0 or status['fail'] > 0:
        print("\nQuick Fixes:")

        if not trades_file.exists():
            print("- Generate trades: python scripts-and-data/automation/generate_todays_trades.py")

        if status['fail'] > 0:
            print("- Run full test: python scripts-and-data/automation/test_full_pipeline.py")
            print("- Install deps: pip install -r requirements.txt")

    return status['fail'] == 0

if __name__ == "__main__":
    import sys
    success = check_status()

    # Next steps
    print("\nNext Steps:")
    print("1. Run dashboard: python scripts-and-data/automation/system_dashboard.py")
    print("2. Check schedule: schtasks /query /tn \"AI Trading Bot*\"")
    print("3. Monitor execution at 9:30 AM")

    sys.exit(0 if success else 1)