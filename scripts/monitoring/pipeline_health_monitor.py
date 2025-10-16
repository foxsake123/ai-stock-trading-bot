"""
Pipeline Health Monitor
Checks each automation stage and sends alerts on failures
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineHealthMonitor:
    """Monitor automation pipeline health and send alerts"""

    def __init__(self):
        self.email_from = os.getenv('GMAIL_ADDRESS')
        self.email_to = os.getenv('ALERT_EMAIL', self.email_from)
        self.email_password = os.getenv('GMAIL_APP_PASSWORD')

    def send_alert(self, title: str, message: str, severity: str = "WARNING"):
        """Send alert email"""
        if not self.email_from or not self.email_password:
            logger.warning("Email credentials not configured, printing alert instead")
            print(f"\n{'='*60}")
            print(f"[{severity}] {title}")
            print(f"{message}")
            print(f"{'='*60}\n")
            return

        # Create email
        msg = MIMEMultipart()
        msg['From'] = self.email_from
        msg['To'] = self.email_to
        msg['Subject'] = f"[AI Trading Bot - {severity}] {title}"

        body = f"""
AI Trading Bot Alert

Severity: {severity}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}

{message}

---
This is an automated alert from your AI trading bot pipeline monitor.
"""

        msg.attach(MIMEText(body, 'plain'))

        # Send email
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(msg)
                logger.info(f"Alert sent: {title}")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            # Fallback to console
            print(f"\n[{severity}] {title}\n{message}\n")

    def check_evening_research(self, date_str: str = None):
        """Check if evening research files exist (daily structure)"""
        if date_str is None:
            # Check for tomorrow's date
            tomorrow = datetime.now() + timedelta(days=1)
            date_str = tomorrow.strftime('%Y-%m-%d')

        # Check combined research file (created by daily_claude_research.py)
        claude_file = project_root / f"reports/premarket/{date_str}/claude_research.md"

        # ChatGPT research is manual, saved in same directory
        chatgpt_file = project_root / f"reports/premarket/{date_str}/chatgpt_research.md"

        issues = []

        # Check Claude research
        if not claude_file.exists():
            issues.append({
                'severity': 'CRITICAL',
                'title': '[CRITICAL] MISSING CLAUDE RESEARCH',
                'message': f"""
Expected file not found: {claude_file}

This means the evening research script did not run successfully.

Immediate Actions:
1. Run manually: python scripts/automation/daily_claude_research.py --force
2. Check Task Scheduler: schtasks /query /tn "AI Trading - Evening Research" /v
3. Check script logs for errors

Without Claude research, tomorrow's trade generation will fail.
"""
            })

        # Check ChatGPT research (warning only, since it's manual)
        if not chatgpt_file.exists():
            issues.append({
                'severity': 'WARNING',
                'title': '[WARNING] MISSING CHATGPT RESEARCH',
                'message': f"""
Expected file not found: {chatgpt_file}

This is a manual step - you need to:
1. Review Claude research: {claude_file}
2. Submit same questions to ChatGPT Deep Research
3. Save response to: {chatgpt_file}

Without ChatGPT research, you'll only have Claude's perspective.
"""
            })

        # Send alerts
        for issue in issues:
            self.send_alert(
                title=issue['title'],
                message=issue['message'],
                severity=issue['severity']
            )

        if not issues:
            logger.info(f"[OK] Research files exist for {date_str}")

        return len(issues) == 0

    def check_trade_generation(self, date_str: str = None):
        """Check if trades were generated and approved"""
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')

        trades_file = project_root / f"docs/TODAYS_TRADES_{date_str}.md"

        if not trades_file.exists():
            self.send_alert(
                title='[CRITICAL] TRADE GENERATION FAILED',
                message=f"""
Expected file not found: {trades_file}

This means generate_todays_trades_v2.py did not run successfully.

Immediate Actions:
1. Check if research files exist (need both Claude + ChatGPT)
2. Run manually: python scripts/automation/generate_todays_trades_v2.py
3. Check logs for errors (likely data API failures)

Without this file, trade execution at 9:30 AM will fail.
""",
                severity='CRITICAL'
            )
            return False

        # Parse file for approval stats
        with open(trades_file) as f:
            content = f.read()

        # Extract approval stats (looking for pattern like "5 approved / 10 rejected")
        import re
        match = re.search(r'(\d+) approved / (\d+) rejected', content)

        if match:
            approved = int(match.group(1))
            rejected = int(match.group(2))
            total = approved + rejected
            approval_rate = (approved / total * 100) if total > 0 else 0

            if approved == 0:
                self.send_alert(
                    title='[WARNING] ZERO TRADES APPROVED',
                    message=f"""
Trade generation completed but ALL {total} recommendations were rejected.

Approval Rate: 0% ({approved} approved / {rejected} rejected)

Possible Causes:
1. Data API failures (check for 429 errors)
2. All recommendations had low confidence (<55%)
3. Risk Manager vetoed all trades
4. Negative cash balance triggering rejections

Actions:
1. Check TODAYS_TRADES file for rejection reasons: {trades_file}
2. Verify Financial Datasets API is working
3. Check portfolio cash balances (need positive cash)
4. Consider lowering confidence threshold temporarily

No trades will execute at market open unless manually approved.
""",
                    severity='WARNING'
                )
            elif approval_rate < 20:
                self.send_alert(
                    title=f'[WARNING] LOW APPROVAL RATE: {approval_rate:.0f}%',
                    message=f"""
Trade generation completed with low approval rate.

Stats: {approved} approved / {rejected} rejected ({approval_rate:.0f}% approval rate)

This is below the expected 30-50% approval rate.

Review the trades file to understand why: {trades_file}
""",
                    severity='WARNING'
                )
            else:
                logger.info(f"[OK] {approved} trades approved ({approval_rate:.0f}% approval rate)")

        return True

    def check_execution_status(self, date_str: str = None):
        """Check if trades were executed"""
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')

        # Check for execution logs
        log_dir = project_root / f"reports/execution/{date_str}"

        if not log_dir.exists():
            self.send_alert(
                title='[WARNING] NO EXECUTION LOGS FOUND',
                message=f"""
Expected execution logs not found: {log_dir}

This means execute_daily_trades.py may not have run.

Actions:
1. Check if TODAYS_TRADES file has approved trades
2. Run manually: python scripts/automation/execute_daily_trades.py
3. Check Task Scheduler: schtasks /query /tn "AI Trading - Trade Execution" /v
""",
                severity='WARNING'
            )
            return False

        logger.info(f"[OK] Execution logs found for {date_str}")
        return True

    def run_daily_health_check(self):
        """Run comprehensive daily health check"""
        logger.info("="*60)
        logger.info("Starting Daily Pipeline Health Check")
        logger.info("="*60)

        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')

        # Check 1: Evening research (for tomorrow)
        logger.info(f"\n[1/3] Checking evening research for {tomorrow}...")
        research_ok = self.check_evening_research(tomorrow)

        # Check 2: Trade generation (for today)
        logger.info(f"\n[2/3] Checking trade generation for {today}...")
        trades_ok = self.check_trade_generation(today)

        # Check 3: Execution status (for today)
        logger.info(f"\n[3/3] Checking execution status for {today}...")
        execution_ok = self.check_execution_status(today)

        # Summary
        logger.info("\n" + "="*60)
        logger.info("Health Check Summary")
        logger.info("="*60)
        logger.info(f"Evening Research: {'[OK] OK' if research_ok else '[ERROR] FAILED'}")
        logger.info(f"Trade Generation: {'[OK] OK' if trades_ok else '[ERROR] FAILED'}")
        logger.info(f"Trade Execution: {'[OK] OK' if execution_ok else '[ERROR] FAILED'}")

        if research_ok and trades_ok and execution_ok:
            logger.info("\n[OK] ALL SYSTEMS OPERATIONAL")
        else:
            logger.warning("\n[WARNING] ISSUES DETECTED - Check alerts")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='AI Trading Bot Pipeline Health Monitor')
    parser.add_argument('--check', choices=['research', 'trades', 'execution', 'all'],
                       default='all', help='Which check to run')
    parser.add_argument('--date', help='Date to check (YYYY-MM-DD format)')

    args = parser.parse_args()

    monitor = PipelineHealthMonitor()

    if args.check == 'research':
        monitor.check_evening_research(args.date)
    elif args.check == 'trades':
        monitor.check_trade_generation(args.date)
    elif args.check == 'execution':
        monitor.check_execution_status(args.date)
    else:
        monitor.run_daily_health_check()


if __name__ == '__main__':
    main()
