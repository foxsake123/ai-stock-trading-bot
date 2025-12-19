"""
Daily Claude Research Generator (Market Days Only)
===================================================
Runs every evening at 6 PM ET to generate next-day trading research.
Only executes if tomorrow is a trading day.

Schedule: Daily at 6:00 PM ET (automated via Task Scheduler)
Output: PDF + Markdown reports for both bots

Author: AI Trading Bot System
Date: September 30, 2025
"""

import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import requests
from dotenv import load_dotenv

# Change to project root directory (important for Task Scheduler)
PROJECT_ROOT = Path(__file__).parent.parent.parent
os.chdir(PROJECT_ROOT)

# Load environment variables from project root
load_dotenv(PROJECT_ROOT / ".env")

sys.path.append(str(Path(__file__).parent))

from claude_research_generator import ClaudeResearchGenerator


def is_market_day(date):
    """
    Check if a given date is a trading day (Mon-Fri, excluding holidays)

    Args:
        date: datetime object to check

    Returns:
        bool: True if market is open
    """
    # Check if weekend (Sat=5, Sun=6)
    if date.weekday() >= 5:
        return False

    # US Market Holidays 2025 (approximate - update annually)
    holidays_2025 = [
        datetime(2025, 1, 1),   # New Year's Day
        datetime(2025, 1, 20),  # MLK Day
        datetime(2025, 2, 17),  # Presidents Day
        datetime(2025, 4, 18),  # Good Friday
        datetime(2025, 5, 26),  # Memorial Day
        datetime(2025, 6, 19),  # Juneteenth
        datetime(2025, 7, 4),   # Independence Day
        datetime(2025, 9, 1),   # Labor Day
        datetime(2025, 11, 27), # Thanksgiving
        datetime(2025, 12, 25), # Christmas
    ]

    # Check if date matches any holiday
    for holiday in holidays_2025:
        if date.date() == holiday.date():
            return False

    return True


def get_next_market_day():
    """Get the next trading day from tomorrow"""
    tomorrow = datetime.now() + timedelta(days=1)

    # Check up to 7 days ahead
    for i in range(7):
        check_date = tomorrow + timedelta(days=i)
        if is_market_day(check_date):
            return check_date

    return None


def should_generate_report(force=False):
    """
    Determine if we should generate a report tonight

    Args:
        force: If True, bypass all time checks and generate report immediately

    Returns:
        tuple: (should_run: bool, next_trading_day: datetime, reason: str)
    """
    if force:
        tomorrow = datetime.now() + timedelta(days=1)
        return True, tomorrow, "FORCED GENERATION (--force flag)"

    et_tz = pytz.timezone('America/New_York')
    now_et = datetime.now(et_tz)

    # Get next trading day
    next_day = get_next_market_day()

    if not next_day:
        return False, None, "No trading day found in next 7 days"

    # Check if it's before market close (don't run during trading hours)
    if now_et.hour < 16:
        return False, next_day, f"Too early (before 4 PM ET), will run at 6 PM for {next_day.strftime('%Y-%m-%d')}"

    # Check if tomorrow is a trading day
    tomorrow = datetime.now() + timedelta(days=1)
    if is_market_day(tomorrow):
        return True, tomorrow, f"Tomorrow is a trading day: {tomorrow.strftime('%A, %B %d, %Y')}"

    return False, next_day, f"Tomorrow is {tomorrow.strftime('%A')} (not a trading day), next market day is {next_day.strftime('%A, %B %d')}"


def send_telegram_notification(pdf_paths):
    """
    Send research PDFs to Telegram

    Args:
        pdf_paths: dict with 'dee_bot' and 'shorgan_bot' PDF paths

    Returns:
        bool: True if both sent successfully
    """
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("[-] Warning: Telegram credentials not found, skipping notification")
        return False

    url = f'https://api.telegram.org/bot{bot_token}/sendDocument'
    success_count = 0

    for bot_name, pdf_path in pdf_paths.items():
        if not pdf_path or not os.path.exists(pdf_path):
            print(f"[-] PDF not found for {bot_name}: {pdf_path}")
            continue

        try:
            caption = f"{bot_name.replace('_', '-').upper()} Research - {datetime.now().strftime('%b %d, %Y')}"
            with open(pdf_path, 'rb') as f:
                response = requests.post(
                    url,
                    data={'chat_id': chat_id, 'caption': caption},
                    files={'document': f},
                    timeout=30
                )

            if response.json().get('ok'):
                print(f"[+] {bot_name.replace('_', '-').upper()} research sent to Telegram")
                success_count += 1
            else:
                print(f"[-] Failed to send {bot_name}: {response.text}")

        except Exception as e:
            print(f"[-] Error sending {bot_name} to Telegram: {e}")

    return success_count == len(pdf_paths)


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate daily Claude research for tomorrow\'s trading')
    parser.add_argument('--force', action='store_true',
                       help='Force generation regardless of time/date (bypass all checks)')
    args = parser.parse_args()

    print("="*70)
    print("DAILY CLAUDE RESEARCH AUTOMATION")
    print("="*70)
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    if args.force:
        print("[FORCE MODE] Bypassing all time/date checks")
    print()

    # Check if we should run
    should_run, next_trading_day, reason = should_generate_report(force=args.force)

    print(f"[*] {reason}")

    if not should_run:
        print(f"\n[!] Skipping report generation")
        print(f"[!] Next scheduled run: Tomorrow at 6:00 PM ET")
        print(f"[!] To force generation now, use: python {sys.argv[0]} --force")
        return

    print(f"\n[+] Generating research for: {next_trading_day.strftime('%A, %B %d, %Y')}")
    print(f"[+] Reports will plan trades for tomorrow's market open")
    print()

    # Initialize generator
    generator = ClaudeResearchGenerator()

    # Calculate week number (example: week 1 = first week of trading)
    # You can adjust this based on your experiment start date
    start_date = datetime(2025, 9, 1)  # Adjust to your experiment start
    days_elapsed = (datetime.now() - start_date).days
    week_number = (days_elapsed // 7) + 1

    # Generate reports for all configured accounts
    # DEE-BOT-LIVE only included if API keys are configured
    bots = ["DEE-BOT", "SHORGAN-BOT", "SHORGAN-BOT-LIVE"]
    if os.getenv("ALPACA_LIVE_API_KEY_DEE") and os.getenv("ALPACA_LIVE_SECRET_KEY_DEE"):
        bots.insert(1, "DEE-BOT-LIVE")  # Add after DEE-BOT
    else:
        print("[INFO] Skipping DEE-BOT-LIVE - no API keys configured")
    report_paths = []
    pdf_paths = {}

    for bot_name in bots:
        try:
            print(f"\n{'-'*70}")
            print(f"GENERATING {bot_name} RESEARCH REPORT")
            print(f"{'-'*70}")

            report, portfolio_data = generator.generate_research_report(
                bot_name=bot_name,
                week_number=week_number,
                include_market_data=True
            )

            md_path, pdf_path = generator.save_report(
                report=report,
                bot_name=bot_name,
                portfolio_data=portfolio_data,
                export_pdf=True
            )
            report_paths.append(md_path)

            # Store PDF path for Telegram notification
            bot_key = bot_name.lower().replace('-', '_')
            if pdf_path:
                pdf_paths[bot_key] = pdf_path

            print(f"\n[+] {bot_name} report complete!")
            print(f"    Markdown: {md_path}")
            if pdf_path:
                print(f"    PDF: {pdf_path}")

            # Add 2-minute delay between bots to avoid Anthropic API rate limit (30K tokens/min)
            if bot_name != bots[-1]:  # Don't delay after last bot
                print(f"\n[*] Waiting 120 seconds before next bot (API rate limit protection)...")
                time.sleep(120)

        except Exception as e:
            print(f"\n[-] Error generating {bot_name} report: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Combine all bot reports into single claude_research.md file
    if len(report_paths) >= 2:
        try:
            print(f"\n{'-'*70}")
            print(f"COMBINING REPORTS INTO SINGLE FILE")
            print(f"{'-'*70}")

            # FIX: Use absolute path to avoid CWD dependency
            # Determine target directory (tomorrow's date)
            tomorrow = datetime.now() + timedelta(days=1)
            date_str = tomorrow.strftime("%Y-%m-%d")
            # Go up two levels: scripts/automation -> scripts -> project_root
            project_root = Path(__file__).parent.parent.parent
            combined_dir = project_root / "reports" / "premarket" / date_str
            combined_path = combined_dir / "claude_research.md"

            # Read both reports
            combined_content = ""
            for md_path in report_paths:
                with open(md_path, 'r', encoding='utf-8') as f:
                    combined_content += f.read() + "\n"

            # Write combined report
            with open(combined_path, 'w', encoding='utf-8') as f:
                f.write(combined_content)

            print(f"[+] Combined report saved: {combined_path}")
            print(f"    This file combines DEE-BOT, SHORGAN-BOT Paper, and SHORGAN-BOT Live research")
            print(f"    Individual bot files preserved for debugging")

        except Exception as e:
            print(f"[-] Error combining reports: {e}")

    # Send Telegram notifications
    if pdf_paths:
        print(f"\n{'-'*70}")
        print(f"SENDING TELEGRAM NOTIFICATIONS")
        print(f"{'-'*70}")
        telegram_success = send_telegram_notification(pdf_paths)
        if telegram_success:
            print(f"[+] All research reports sent to Telegram successfully")
        else:
            print(f"[!] Some Telegram notifications may have failed (check logs above)")

    print(f"\n{'='*70}")
    print(f"[+] DAILY RESEARCH GENERATION COMPLETE")
    print(f"[+] Review reports before tomorrow's market open (9:30 AM ET)")
    if pdf_paths:
        print(f"[+] Research PDFs sent to Telegram")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
