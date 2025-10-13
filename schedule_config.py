"""
Trading Schedule Configuration
Handles timezone, trading days, and market holidays
"""

from datetime import datetime, timedelta, date
from typing import Optional
import pytz

# US/Eastern timezone for market hours
ET = pytz.timezone('US/Eastern')

# Market holidays for 2025 (NYSE/NASDAQ)
MARKET_HOLIDAYS_2025 = [
    date(2025, 1, 1),   # New Year's Day
    date(2025, 1, 20),  # Martin Luther King Jr. Day
    date(2025, 2, 17),  # Presidents' Day
    date(2025, 4, 18),  # Good Friday
    date(2025, 5, 26),  # Memorial Day
    date(2025, 6, 19),  # Juneteenth
    date(2025, 7, 4),   # Independence Day
    date(2025, 9, 1),   # Labor Day
    date(2025, 11, 27), # Thanksgiving
    date(2025, 12, 25), # Christmas
]

# Trading schedule configuration
TRADING_SCHEDULE = {
    'report_generation_time': '18:00',  # 6:00 PM ET
    'market_open': '09:30',             # 9:30 AM ET
    'market_close': '16:00',            # 4:00 PM ET
    'trading_days': [0, 1, 2, 3, 4],   # Monday=0 through Friday=4
    'excluded_dates': MARKET_HOLIDAYS_2025,
    'timezone': 'US/Eastern'
}


def is_trading_day(check_date: date) -> bool:
    """
    Check if a given date is a trading day

    Args:
        check_date: Date to check

    Returns:
        True if the date is a trading day, False otherwise

    Example:
        >>> is_trading_day(date(2025, 10, 14))  # Monday
        True
        >>> is_trading_day(date(2025, 10, 18))  # Saturday
        False
        >>> is_trading_day(date(2025, 12, 25))  # Christmas
        False
    """
    # Check if weekend (Saturday=5, Sunday=6)
    if check_date.weekday() >= 5:
        return False

    # Check if market holiday
    if check_date in MARKET_HOLIDAYS_2025:
        return False

    return True


def get_next_trading_day(from_date: Optional[datetime] = None) -> date:
    """
    Calculate the next trading day from a given date (or now)

    Skips weekends and market holidays. If from_date is a trading day
    and it's before market close, returns the same day. Otherwise,
    returns the next valid trading day.

    Args:
        from_date: Starting date/datetime (defaults to now in ET)

    Returns:
        Next trading day as a date object

    Example:
        >>> get_next_trading_day()  # Returns next trading day from now
        date(2025, 10, 14)
    """
    # Default to current time in ET
    if from_date is None:
        from_date = datetime.now(ET)

    # If datetime, convert to date for checking
    if isinstance(from_date, datetime):
        check_date = from_date.date()
    else:
        check_date = from_date

    # Check if today is a trading day and we're before market close
    if isinstance(from_date, datetime):
        market_close = datetime.strptime(TRADING_SCHEDULE['market_close'], '%H:%M').time()
        if is_trading_day(check_date) and from_date.time() < market_close:
            return check_date

    # Start checking from tomorrow
    check_date = check_date + timedelta(days=1)

    # Keep checking until we find a trading day
    while not is_trading_day(check_date):
        check_date = check_date + timedelta(days=1)

        # Safety check: don't loop forever (max 30 days ahead)
        if check_date > (datetime.now(ET).date() + timedelta(days=30)):
            raise ValueError("No trading day found within 30 days")

    return check_date


def get_previous_trading_day(from_date: Optional[datetime] = None) -> date:
    """
    Calculate the previous trading day from a given date (or now)

    Args:
        from_date: Starting date/datetime (defaults to now in ET)

    Returns:
        Previous trading day as a date object
    """
    # Default to current time in ET
    if from_date is None:
        from_date = datetime.now(ET)

    # If datetime, convert to date for checking
    if isinstance(from_date, datetime):
        check_date = from_date.date()
    else:
        check_date = from_date

    # Start checking from yesterday
    check_date = check_date - timedelta(days=1)

    # Keep checking until we find a trading day
    while not is_trading_day(check_date):
        check_date = check_date - timedelta(days=1)

        # Safety check: don't loop forever (max 30 days back)
        if check_date < (datetime.now(ET).date() - timedelta(days=30)):
            raise ValueError("No trading day found within 30 days back")

    return check_date


def get_current_time_et() -> datetime:
    """
    Get current time in US/Eastern timezone

    Returns:
        Current datetime in ET
    """
    return datetime.now(ET)


def is_market_open(check_time: Optional[datetime] = None) -> bool:
    """
    Check if the market is currently open

    Args:
        check_time: Time to check (defaults to now in ET)

    Returns:
        True if market is open, False otherwise
    """
    if check_time is None:
        check_time = datetime.now(ET)

    # Check if trading day
    if not is_trading_day(check_time.date()):
        return False

    # Check if within market hours
    market_open = datetime.strptime(TRADING_SCHEDULE['market_open'], '%H:%M').time()
    market_close = datetime.strptime(TRADING_SCHEDULE['market_close'], '%H:%M').time()

    current_time = check_time.time()

    return market_open <= current_time <= market_close


# Test functions when run directly
if __name__ == '__main__':
    print("=" * 80)
    print("TRADING SCHEDULE CONFIGURATION TEST")
    print("=" * 80)
    print()

    # Get current time in ET
    now_et = get_current_time_et()
    print(f"Current Time (ET): {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Today's Date: {now_et.date()}")
    print()

    # Check if today is a trading day
    today_is_trading = is_trading_day(now_et.date())
    print(f"Is Today a Trading Day? {today_is_trading}")
    print()

    # Get next trading day
    next_trading = get_next_trading_day()
    print(f"Next Trading Day: {next_trading}")
    print()

    # Get previous trading day
    prev_trading = get_previous_trading_day()
    print(f"Previous Trading Day: {prev_trading}")
    print()

    # Check if market is currently open
    market_open_now = is_market_open()
    print(f"Is Market Open Now? {market_open_now}")
    print()

    # Display market holidays
    print("Market Holidays (2025):")
    print("-" * 80)
    for holiday in MARKET_HOLIDAYS_2025:
        day_name = holiday.strftime('%A')
        print(f"  {holiday.strftime('%Y-%m-%d')} ({day_name})")
    print()

    # Display trading schedule
    print("Trading Schedule:")
    print("-" * 80)
    print(f"  Report Generation: {TRADING_SCHEDULE['report_generation_time']} ET")
    print(f"  Market Open: {TRADING_SCHEDULE['market_open']} ET")
    print(f"  Market Close: {TRADING_SCHEDULE['market_close']} ET")
    print(f"  Trading Days: Monday-Friday")
    print(f"  Timezone: {TRADING_SCHEDULE['timezone']}")
    print()

    # Test specific dates
    print("Test Specific Dates:")
    print("-" * 80)
    test_dates = [
        date(2025, 10, 14),  # Monday
        date(2025, 10, 18),  # Saturday
        date(2025, 10, 19),  # Sunday
        date(2025, 12, 25),  # Christmas
        date(2025, 1, 1),    # New Year's
        date(2025, 7, 4),    # Independence Day
    ]

    for test_date in test_dates:
        is_trading = is_trading_day(test_date)
        day_name = test_date.strftime('%A')
        status = "TRADING DAY" if is_trading else "NON-TRADING"
        print(f"  {test_date} ({day_name}): {status}")

    print()
    print("=" * 80)
