"""
Daily Trading Automation
Handles all daily automated tasks
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, time
import schedule
import time as time_module
import requests

class DailyTradingAutomation:
    """Automates daily trading tasks"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.automation_dir = Path(__file__).parent

        # Telegram configuration
        self.telegram_token = "8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c"
        self.telegram_chat_id = "7870288896"

        # Trading hours (ET)
        self.market_open = time(9, 30)
        self.market_close = time(16, 0)
        self.post_market = time(16, 30)

    def send_telegram_alert(self, message: str):
        """Send alert via Telegram"""
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        data = {
            'chat_id': self.telegram_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        try:
            requests.post(url, data=data)
        except:
            pass

    def pre_market_check(self):
        """9:00 AM - Pre-market preparation"""
        print(f"\n{'='*50}")
        print(f"PRE-MARKET CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")

        tasks_completed = []

        # Check for today's trades file
        today_str = datetime.now().strftime("%Y-%m-%d")
        trades_file = self.project_root / f"TODAYS_TRADES_{today_str}.md"

        if trades_file.exists():
            tasks_completed.append("✅ Today's trades file found")
            print(f"✅ Trades file ready: {trades_file.name}")
        else:
            print("❌ No trades file for today - run weekly workflow first")
            self.send_telegram_alert(
                "⚠️ <b>Pre-Market Alert</b>\n"
                "No trades file found for today.\n"
                "Run weekly workflow to generate trades."
            )
            return

        # Check account status
        try:
            result = subprocess.run(
                ["python", "scripts-and-data/automation/check_account_status.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                tasks_completed.append("✅ Account status checked")
                print("✅ Account status verified")
        except:
            print("⚠️ Could not check account status")

        # Update positions
        try:
            result = subprocess.run(
                ["python", "scripts-and-data/automation/update_all_bot_positions.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                tasks_completed.append("✅ Positions updated")
                print("✅ Positions updated")
        except:
            print("⚠️ Could not update positions")

        # Send pre-market summary
        summary = f"""<b>🔔 Pre-Market Ready</b>
Time: {datetime.now().strftime('%I:%M %p')}

<b>Checklist:</b>
{chr(10).join(tasks_completed)}

<b>Market Open:</b> 9:30 AM
<b>Trades:</b> Check TODAYS_TRADES file

Ready for automated execution!"""

        self.send_telegram_alert(summary)
        print("\n✅ Pre-market check complete")

    def market_open_execution(self):
        """9:30 AM - Execute trades at market open"""
        print(f"\n{'='*50}")
        print(f"MARKET OPEN EXECUTION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")

        # Execute daily trades
        try:
            result = subprocess.run(
                ["python", "scripts-and-data/automation/execute_daily_trades.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            if result.returncode == 0:
                print("✅ Trades executed successfully")
                self.send_telegram_alert(
                    "✅ <b>Market Open</b>\n"
                    "Trades executed successfully.\n"
                    "Check positions for confirmation."
                )
            else:
                print(f"❌ Trade execution failed: {result.stderr}")
                self.send_telegram_alert(
                    "❌ <b>Trade Execution Failed</b>\n"
                    "Manual intervention required."
                )

        except Exception as e:
            print(f"❌ Execution error: {e}")
            self.send_telegram_alert(f"❌ Execution error: {str(e)[:100]}")

    def midday_check(self):
        """12:00 PM - Midday position check"""
        print(f"\n{'='*50}")
        print(f"MIDDAY CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")

        # Update positions
        try:
            subprocess.run(
                ["python", "scripts-and-data/automation/update_all_bot_positions.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            print("✅ Midday positions updated")

        except:
            print("⚠️ Could not update positions")

    def market_close_tasks(self):
        """4:00 PM - Market close tasks"""
        print(f"\n{'='*50}")
        print(f"MARKET CLOSE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")

        tasks_completed = []

        # Update final positions
        try:
            subprocess.run(
                ["python", "scripts-and-data/automation/update_all_bot_positions.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            tasks_completed.append("✅ Final positions updated")
            print("✅ Positions updated")
        except:
            print("⚠️ Could not update positions")

        # Take daily snapshot
        try:
            subprocess.run(
                ["python", "scripts-and-data/automation/daily_portfolio_snapshot.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            tasks_completed.append("✅ Portfolio snapshot saved")
            print("✅ Daily snapshot saved")
        except:
            print("⚠️ Could not save snapshot")

        print("\n✅ Market close tasks complete")

    def post_market_report(self):
        """4:30 PM - Generate and send post-market report"""
        print(f"\n{'='*50}")
        print(f"POST-MARKET REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")

        try:
            result = subprocess.run(
                ["python", "scripts-and-data/automation/generate-post-market-report.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("✅ Post-market report sent")
                self.send_telegram_alert(
                    "📊 <b>Post-Market Report Sent</b>\n"
                    "Check Telegram for full report."
                )
            else:
                print("❌ Report generation failed")

        except Exception as e:
            print(f"❌ Report error: {e}")

    def run_scheduled_tasks(self):
        """Run tasks on schedule"""
        print("="*70)
        print("DAILY AUTOMATION SCHEDULER")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        # Schedule daily tasks
        schedule.every().day.at("09:00").do(self.pre_market_check)
        schedule.every().day.at("09:30").do(self.market_open_execution)
        schedule.every().day.at("12:00").do(self.midday_check)
        schedule.every().day.at("16:00").do(self.market_close_tasks)
        schedule.every().day.at("16:30").do(self.post_market_report)

        print("\nScheduled Tasks:")
        print("- 9:00 AM: Pre-market check")
        print("- 9:30 AM: Execute trades")
        print("- 12:00 PM: Midday check")
        print("- 4:00 PM: Market close tasks")
        print("- 4:30 PM: Post-market report")
        print("\nScheduler running... (Ctrl+C to stop)")

        while True:
            schedule.run_pending()
            time_module.sleep(60)  # Check every minute

    def run_now(self, task: str = None):
        """Run specific task immediately"""
        task_map = {
            'pre-market': self.pre_market_check,
            'execute': self.market_open_execution,
            'midday': self.midday_check,
            'close': self.market_close_tasks,
            'report': self.post_market_report
        }

        if task and task in task_map:
            task_map[task]()
        else:
            print("Available tasks: pre-market, execute, midday, close, report")
            print("Or run without arguments for scheduled mode")

def main():
    """Main execution"""
    automation = DailyTradingAutomation()

    if len(sys.argv) > 1:
        # Run specific task
        task = sys.argv[1]
        automation.run_now(task)
    else:
        # Run scheduled mode
        automation.run_scheduled_tasks()

if __name__ == "__main__":
    main()