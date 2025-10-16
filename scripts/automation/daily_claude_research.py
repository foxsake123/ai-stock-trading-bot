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
from datetime import datetime, timedelta
from pathlib import Path
import pytz

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

    # Generate reports for both bots
    bots = ["DEE-BOT", "SHORGAN-BOT"]

    for bot_name in bots:
        try:
            print(f"\n{'-'*70}")
            print(f"GENERATING {bot_name} RESEARCH REPORT")
            print(f"{'-'*70}")

            report = generator.generate_research_report(
                bot_name=bot_name,
                week_number=week_number,
                include_market_data=True
            )

            md_path, pdf_path = generator.save_report(report, bot_name, export_pdf=True)

            print(f"\n[+] {bot_name} report complete!")
            print(f"    Markdown: {md_path}")
            if pdf_path:
                print(f"    PDF: {pdf_path}")

        except Exception as e:
            print(f"\n[-] Error generating {bot_name} report: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"\n{'='*70}")
    print(f"[+] DAILY RESEARCH GENERATION COMPLETE")
    print(f"[+] Review reports before tomorrow's market open (9:30 AM ET)")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
