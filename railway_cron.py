#!/usr/bin/env python3
"""
Railway Cron Job Entry Point
============================
Unified entry point for all scheduled trading tasks on Railway.

Usage:
    python railway_cron.py <task>

Tasks:
    research    - Generate research reports (runs Saturday 12 PM ET)
    trades      - Generate trade recommendations (runs weekdays 8:30 AM ET)
    execute     - Execute approved trades (runs weekdays 9:30 AM ET)
    performance - Update performance graph (runs weekdays 4:30 PM ET)

Environment Variables Required:
    - ANTHROPIC_API_KEY
    - ALPACA_API_KEY_DEE / ALPACA_SECRET_KEY_DEE
    - ALPACA_API_KEY_SHORGAN / ALPACA_SECRET_KEY_SHORGAN
    - ALPACA_LIVE_API_KEY_SHORGAN / ALPACA_LIVE_SECRET_KEY_SHORGAN
    - TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID
    - FINANCIAL_DATASETS_API_KEY
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Set up paths
PROJECT_ROOT = Path(__file__).parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


def send_telegram_message(message: str):
    """Send notification to Telegram."""
    import requests

    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("[WARNING] Telegram credentials not configured")
        return

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=10)
        print(f"[OK] Telegram notification sent")
    except Exception as e:
        print(f"[ERROR] Telegram failed: {e}")


def run_research():
    """Generate research reports for all bots."""
    print("=" * 60)
    print(f"[RAILWAY] Running Research Generation - {datetime.now()}")
    print("=" * 60)

    send_telegram_message("🚀 *Railway Cron* - Starting research generation...")

    try:
        # Import and run the research generator
        from scripts.automation.daily_claude_research import main as research_main
        research_main()
        send_telegram_message("✅ *Railway Cron* - Research generation complete!")
        return 0
    except Exception as e:
        error_msg = f"❌ *Railway Cron* - Research failed: {str(e)[:200]}"
        print(f"[ERROR] {e}")
        send_telegram_message(error_msg)
        return 1


def run_trades():
    """Generate trade recommendations from research."""
    print("=" * 60)
    print(f"[RAILWAY] Running Trade Generation - {datetime.now()}")
    print("=" * 60)

    send_telegram_message("📊 *Railway Cron* - Starting trade generation...")

    try:
        # Import and run the trade generator
        from scripts.automation.generate_todays_trades_v2 import main as trades_main
        trades_main()
        send_telegram_message("✅ *Railway Cron* - Trade generation complete!")
        return 0
    except Exception as e:
        error_msg = f"❌ *Railway Cron* - Trade generation failed: {str(e)[:200]}"
        print(f"[ERROR] {e}")
        send_telegram_message(error_msg)
        return 1


def run_execute():
    """Execute approved trades."""
    print("=" * 60)
    print(f"[RAILWAY] Running Trade Execution - {datetime.now()}")
    print("=" * 60)

    send_telegram_message("💰 *Railway Cron* - Starting trade execution...")

    try:
        # Import and run the trade executor
        from scripts.automation.execute_daily_trades import main as execute_main
        execute_main()
        send_telegram_message("✅ *Railway Cron* - Trade execution complete!")
        return 0
    except Exception as e:
        error_msg = f"❌ *Railway Cron* - Execution failed: {str(e)[:200]}"
        print(f"[ERROR] {e}")
        send_telegram_message(error_msg)
        return 1


def run_performance():
    """Update performance graph."""
    print("=" * 60)
    print(f"[RAILWAY] Running Performance Update - {datetime.now()}")
    print("=" * 60)

    send_telegram_message("📈 *Railway Cron* - Updating performance graph...")

    try:
        # Import and run the performance generator
        from scripts.performance.generate_performance_graph import main as perf_main
        perf_main()
        send_telegram_message("✅ *Railway Cron* - Performance update complete!")
        return 0
    except Exception as e:
        error_msg = f"❌ *Railway Cron* - Performance update failed: {str(e)[:200]}"
        print(f"[ERROR] {e}")
        send_telegram_message(error_msg)
        return 1


def main():
    """Main entry point - dispatch based on task argument."""
    if len(sys.argv) < 2:
        # Check for RAILWAY_TASK environment variable
        task = os.getenv('RAILWAY_TASK', '').lower()
        if not task:
            print("Usage: python railway_cron.py <task>")
            print("Tasks: research, trades, execute, performance")
            print("Or set RAILWAY_TASK environment variable")
            return 1
    else:
        task = sys.argv[1].lower()

    print(f"[RAILWAY] Task: {task}")
    print(f"[RAILWAY] Time: {datetime.now()}")
    print(f"[RAILWAY] Working Dir: {os.getcwd()}")

    tasks = {
        'research': run_research,
        'trades': run_trades,
        'execute': run_execute,
        'performance': run_performance,
    }

    if task not in tasks:
        print(f"[ERROR] Unknown task: {task}")
        print(f"Available tasks: {', '.join(tasks.keys())}")
        return 1

    return tasks[task]()


if __name__ == "__main__":
    sys.exit(main())
