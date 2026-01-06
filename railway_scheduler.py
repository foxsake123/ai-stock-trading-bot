#!/usr/bin/env python3
"""
Railway Always-On Scheduler
============================
Runs continuously on Railway and executes tasks at scheduled times.
This replaces the need for Railway's cron feature.

Schedule (ET):
- Saturday 12:00 PM: Research generation
- Mon-Fri 8:30 AM: Trade generation
- Mon-Fri 9:30 AM: Trade execution
- Mon-Fri 4:30 PM: Performance graph
"""

import os
import sys
import time
import schedule
from datetime import datetime
from pathlib import Path

# Set up paths
PROJECT_ROOT = Path(__file__).parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import pytz

ET = pytz.timezone('America/New_York')


def get_et_time():
    """Get current time in ET."""
    return datetime.now(ET)


def send_telegram(message: str):
    """Send notification to Telegram."""
    import requests
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if bot_token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)
        except:
            pass


def run_research():
    """Run research generation."""
    print(f"[{get_et_time()}] Starting research generation...")
    send_telegram("🔬 *Railway* - Starting research generation...")
    try:
        from scripts.automation.daily_claude_research import main as research_main
        research_main()
        send_telegram("✅ *Railway* - Research complete!")
        print(f"[{get_et_time()}] Research complete!")
    except Exception as e:
        send_telegram(f"❌ *Railway* - Research failed: {str(e)[:100]}")
        print(f"[{get_et_time()}] Research failed: {e}")


def run_trades():
    """Run trade generation."""
    print(f"[{get_et_time()}] Starting trade generation...")
    send_telegram("📊 *Railway* - Starting trade generation...")
    try:
        from scripts.automation.generate_todays_trades_v2 import main as trades_main
        trades_main()
        send_telegram("✅ *Railway* - Trades generated!")
        print(f"[{get_et_time()}] Trades generated!")
    except Exception as e:
        send_telegram(f"❌ *Railway* - Trade generation failed: {str(e)[:100]}")
        print(f"[{get_et_time()}] Trade generation failed: {e}")


def run_execute():
    """Run trade execution."""
    print(f"[{get_et_time()}] Starting trade execution...")
    send_telegram("💰 *Railway* - Starting trade execution...")
    try:
        from scripts.automation.execute_daily_trades import main as execute_main
        execute_main()
        send_telegram("✅ *Railway* - Trades executed!")
        print(f"[{get_et_time()}] Trades executed!")
    except Exception as e:
        send_telegram(f"❌ *Railway* - Execution failed: {str(e)[:100]}")
        print(f"[{get_et_time()}] Execution failed: {e}")


def run_performance():
    """Run performance graph update."""
    print(f"[{get_et_time()}] Starting performance update...")
    send_telegram("📈 *Railway* - Updating performance...")
    try:
        from scripts.performance.generate_performance_graph import main as perf_main
        perf_main()
        send_telegram("✅ *Railway* - Performance updated!")
        print(f"[{get_et_time()}] Performance updated!")
    except Exception as e:
        send_telegram(f"❌ *Railway* - Performance failed: {str(e)[:100]}")
        print(f"[{get_et_time()}] Performance failed: {e}")


def heartbeat():
    """Send hourly heartbeat to confirm service is running."""
    now = get_et_time()
    if now.hour == 9 and now.minute < 5:  # Only at 9 AM ET
        send_telegram(f"💓 *Railway Scheduler* - Running ({now.strftime('%Y-%m-%d %H:%M ET')})")


def main():
    """Main scheduler loop."""
    print("=" * 60)
    print("Railway Scheduler Starting")
    print(f"Current time (ET): {get_et_time()}")
    print("=" * 60)

    send_telegram("🚀 *Railway Scheduler* - Service started!")

    # Schedule tasks (ET times)
    # Research: Saturday 12:00 PM
    schedule.every().saturday.at("12:00").do(run_research)

    # Trades: Mon-Fri 8:30 AM
    schedule.every().monday.at("08:30").do(run_trades)
    schedule.every().tuesday.at("08:30").do(run_trades)
    schedule.every().wednesday.at("08:30").do(run_trades)
    schedule.every().thursday.at("08:30").do(run_trades)
    schedule.every().friday.at("08:30").do(run_trades)

    # Execute: Mon-Fri 9:30 AM
    schedule.every().monday.at("09:30").do(run_execute)
    schedule.every().tuesday.at("09:30").do(run_execute)
    schedule.every().wednesday.at("09:30").do(run_execute)
    schedule.every().thursday.at("09:30").do(run_execute)
    schedule.every().friday.at("09:30").do(run_execute)

    # Performance: Mon-Fri 4:30 PM
    schedule.every().monday.at("16:30").do(run_performance)
    schedule.every().tuesday.at("16:30").do(run_performance)
    schedule.every().wednesday.at("16:30").do(run_performance)
    schedule.every().thursday.at("16:30").do(run_performance)
    schedule.every().friday.at("16:30").do(run_performance)

    # Heartbeat every hour
    schedule.every().hour.do(heartbeat)

    print("\nScheduled tasks:")
    print("- Research: Saturday 12:00 PM ET")
    print("- Trades: Mon-Fri 8:30 AM ET")
    print("- Execute: Mon-Fri 9:30 AM ET")
    print("- Performance: Mon-Fri 4:30 PM ET")
    print("\nWaiting for scheduled times...")

    # Run forever
    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 seconds


if __name__ == "__main__":
    main()
