"""
Keep Computer Awake During Trading Hours
Prevents Windows from sleeping during market hours to ensure automation runs.

Usage:
    python scripts/automation/keep_awake.py

Run this at system startup or as a scheduled task at 6:00 AM.
"""

import ctypes
import time
import datetime
import sys
import os

# Windows API constants
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

def prevent_sleep():
    """Prevent Windows from sleeping"""
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED
    )
    print("[AWAKE] Sleep prevention ENABLED")

def allow_sleep():
    """Allow Windows to sleep again"""
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    print("[AWAKE] Sleep prevention DISABLED")

def is_trading_day():
    """Check if today is a trading day (Mon-Fri, not a holiday)"""
    today = datetime.date.today()

    # Weekend check
    if today.weekday() >= 5:  # Saturday=5, Sunday=6
        return False

    # US Market holidays 2025 (update annually)
    holidays_2025 = [
        datetime.date(2025, 1, 1),   # New Year's Day
        datetime.date(2025, 1, 20),  # MLK Day
        datetime.date(2025, 2, 17),  # Presidents Day
        datetime.date(2025, 4, 18),  # Good Friday
        datetime.date(2025, 5, 26),  # Memorial Day
        datetime.date(2025, 6, 19),  # Juneteenth
        datetime.date(2025, 7, 4),   # Independence Day
        datetime.date(2025, 9, 1),   # Labor Day
        datetime.date(2025, 11, 27), # Thanksgiving
        datetime.date(2025, 12, 25), # Christmas
    ]

    if today in holidays_2025:
        return False

    return True

def is_saturday():
    """Check if today is Saturday (weekend research day)"""
    return datetime.date.today().weekday() == 5

def get_awake_hours():
    """Get the hours to stay awake based on day type"""
    if is_saturday():
        # Saturday: Stay awake 11:00 AM - 1:00 PM for weekend research
        return (11, 0), (13, 0)
    elif is_trading_day():
        # Weekday: Stay awake 8:00 AM - 5:00 PM for trading
        return (8, 0), (17, 0)
    else:
        return None, None

def is_within_awake_hours():
    """Check if current time is within awake hours"""
    start, end = get_awake_hours()
    if start is None:
        return False

    now = datetime.datetime.now()
    start_time = now.replace(hour=start[0], minute=start[1], second=0)
    end_time = now.replace(hour=end[0], minute=end[1], second=0)

    return start_time <= now <= end_time

def main():
    """Main loop - keep computer awake during trading hours"""
    print("=" * 60)
    print("KEEP AWAKE SERVICE - AI Trading Bot")
    print("=" * 60)
    print(f"Started: {datetime.datetime.now()}")
    print(f"Trading day: {is_trading_day()}")
    print(f"Saturday: {is_saturday()}")

    start, end = get_awake_hours()
    if start:
        print(f"Awake hours: {start[0]:02d}:{start[1]:02d} - {end[0]:02d}:{end[1]:02d}")
    else:
        print("No awake hours today (weekend/holiday)")
        print("Exiting...")
        return

    print("-" * 60)

    awake = False

    try:
        while True:
            now = datetime.datetime.now()
            should_be_awake = is_within_awake_hours()

            if should_be_awake and not awake:
                prevent_sleep()
                awake = True
                print(f"[{now.strftime('%H:%M:%S')}] Entered awake period")

            elif not should_be_awake and awake:
                allow_sleep()
                awake = False
                print(f"[{now.strftime('%H:%M:%S')}] Exited awake period")

            # Check if we're past end time
            _, end = get_awake_hours()
            end_time = now.replace(hour=end[0], minute=end[1], second=0)
            if now > end_time and not awake:
                print(f"[{now.strftime('%H:%M:%S')}] Past awake hours, exiting")
                break

            # Sleep for 5 minutes between checks
            time.sleep(300)

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] User cancelled")
    finally:
        allow_sleep()
        print("Keep-awake service stopped")

if __name__ == "__main__":
    main()
