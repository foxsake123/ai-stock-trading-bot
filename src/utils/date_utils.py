"""
Date and Time Utilities
Provides trading day calculations, timezone conversions, and holding period analysis
"""

import pytz
from datetime import datetime, date, timedelta
from typing import List, Optional, Union
import logging
from .market_hours import MarketHours

logger = logging.getLogger(__name__)


# ============================================================================
# TIMEZONE UTILITIES
# ============================================================================

# Market timezone (Eastern Time)
MARKET_TIMEZONE = pytz.timezone('America/New_York')
UTC_TIMEZONE = pytz.UTC


def to_market_timezone(dt: Union[datetime, str, None] = None) -> datetime:
    """
    Convert datetime to market timezone (America/New_York)

    Args:
        dt: Datetime object, ISO string, or None (uses current time)

    Returns:
        datetime: Datetime in ET timezone

    Examples:
        >>> to_market_timezone()  # Current time in ET
        >>> to_market_timezone("2025-10-15 14:30:00")
        >>> to_market_timezone(datetime.utcnow())
    """
    if dt is None:
        dt = datetime.now(pytz.UTC)

    # If string, parse it
    if isinstance(dt, str):
        # Try ISO format first
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            # Try common format
            dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')

    # If naive datetime, assume UTC
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)

    # Convert to market timezone
    return dt.astimezone(MARKET_TIMEZONE)


def to_utc(dt: Union[datetime, str]) -> datetime:
    """
    Convert datetime to UTC timezone

    Args:
        dt: Datetime object or ISO string

    Returns:
        datetime: Datetime in UTC timezone
    """
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)

    if dt.tzinfo is None:
        # Assume it's already in market timezone
        dt = MARKET_TIMEZONE.localize(dt)

    return dt.astimezone(pytz.UTC)


def is_same_trading_day(dt1: datetime, dt2: datetime) -> bool:
    """
    Check if two datetimes are on the same trading day

    Args:
        dt1: First datetime
        dt2: Second datetime

    Returns:
        bool: True if same trading day in ET timezone
    """
    et1 = to_market_timezone(dt1)
    et2 = to_market_timezone(dt2)

    return et1.date() == et2.date()


# ============================================================================
# TRADING DAY CALCULATIONS
# ============================================================================

def get_trading_days(
    start_date: Union[datetime, date, str],
    end_date: Union[datetime, date, str],
    include_today: bool = True
) -> List[date]:
    """
    Get list of trading days between two dates

    Excludes weekends and market holidays. Uses market_hours.py for holiday data.

    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive if include_today=True)
        include_today: Whether to include end_date if it's a trading day

    Returns:
        List[date]: List of trading days

    Examples:
        >>> get_trading_days('2025-10-01', '2025-10-31')
        [date(2025, 10, 1), date(2025, 10, 2), ..., date(2025, 10, 31)]

        >>> get_trading_days(datetime(2025, 10, 1), datetime(2025, 10, 15))
        # Returns 11 trading days (excludes 2 weekends)
    """
    # Convert to date objects
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date.split()[0]).date()
    elif isinstance(start_date, datetime):
        start_date = start_date.date()

    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date.split()[0]).date()
    elif isinstance(end_date, datetime):
        end_date = end_date.date()

    # Initialize market hours checker
    mh = MarketHours()

    # Build list of trading days
    trading_days = []
    current_date = start_date

    while current_date <= end_date:
        # Convert to datetime for market_hours check
        dt = datetime.combine(current_date, datetime.min.time())
        dt = MARKET_TIMEZONE.localize(dt)

        # Check if it's a market day
        if mh.is_market_day(dt):
            trading_days.append(current_date)

        current_date += timedelta(days=1)

    # Handle include_today flag
    if not include_today and trading_days and trading_days[-1] == end_date:
        trading_days.pop()

    logger.debug(f"Found {len(trading_days)} trading days between {start_date} and {end_date}")

    return trading_days


def get_next_n_trading_days(n: int, start_date: Optional[datetime] = None) -> List[date]:
    """
    Get the next N trading days from a given date

    Args:
        n: Number of trading days to get
        start_date: Starting date (default: today)

    Returns:
        List[date]: List of next N trading days

    Example:
        >>> get_next_n_trading_days(5)
        # Returns next 5 trading days starting from today
    """
    if start_date is None:
        start_date = datetime.now(MARKET_TIMEZONE)

    mh = MarketHours()
    trading_days = []
    current_date = start_date.date() if isinstance(start_date, datetime) else start_date

    # Search up to 3x the needed days (accounts for weekends/holidays)
    max_days = n * 3
    days_checked = 0

    while len(trading_days) < n and days_checked < max_days:
        dt = datetime.combine(current_date, datetime.min.time())
        dt = MARKET_TIMEZONE.localize(dt)

        if mh.is_market_day(dt):
            trading_days.append(current_date)

        current_date += timedelta(days=1)
        days_checked += 1

    if len(trading_days) < n:
        logger.warning(f"Only found {len(trading_days)} trading days out of {n} requested")

    return trading_days[:n]


def get_previous_n_trading_days(n: int, end_date: Optional[datetime] = None) -> List[date]:
    """
    Get the previous N trading days before a given date

    Args:
        n: Number of trading days to get
        end_date: Ending date (default: today)

    Returns:
        List[date]: List of previous N trading days (most recent first)

    Example:
        >>> get_previous_n_trading_days(5)
        # Returns last 5 trading days (most recent first)
    """
    if end_date is None:
        end_date = datetime.now(MARKET_TIMEZONE)

    mh = MarketHours()
    trading_days = []
    current_date = end_date.date() if isinstance(end_date, datetime) else end_date

    # Search up to 3x the needed days
    max_days = n * 3
    days_checked = 0

    while len(trading_days) < n and days_checked < max_days:
        dt = datetime.combine(current_date, datetime.min.time())
        dt = MARKET_TIMEZONE.localize(dt)

        if mh.is_market_day(dt):
            trading_days.append(current_date)

        current_date -= timedelta(days=1)
        days_checked += 1

    if len(trading_days) < n:
        logger.warning(f"Only found {len(trading_days)} trading days out of {n} requested")

    return trading_days[:n]


# ============================================================================
# HOLDING PERIOD CALCULATIONS
# ============================================================================

def calculate_holding_period(
    entry_date: Union[datetime, date, str],
    exit_date: Union[datetime, date, str],
    unit: str = 'days'
) -> int:
    """
    Calculate holding period between entry and exit dates

    Counts only trading days (excludes weekends and holidays).

    Args:
        entry_date: Entry date/time
        exit_date: Exit date/time
        unit: Return unit ('days', 'calendar_days', 'weeks')

    Returns:
        int: Number of trading days held

    Examples:
        >>> calculate_holding_period('2025-10-01', '2025-10-15')
        11  # Trading days

        >>> calculate_holding_period('2025-10-01', '2025-10-15', unit='calendar_days')
        14  # Calendar days

        >>> calculate_holding_period(
        ...     datetime(2025, 10, 1, 9, 30),
        ...     datetime(2025, 10, 1, 15, 30)
        ... )
        0  # Same day (intraday trade)
    """
    # Convert to date objects
    if isinstance(entry_date, str):
        entry_date = datetime.fromisoformat(entry_date.split()[0]).date()
    elif isinstance(entry_date, datetime):
        entry_date = entry_date.date()

    if isinstance(exit_date, str):
        exit_date = datetime.fromisoformat(exit_date.split()[0]).date()
    elif isinstance(exit_date, datetime):
        exit_date = exit_date.date()

    # Calendar days calculation
    if unit == 'calendar_days':
        return (exit_date - entry_date).days

    # Trading days calculation
    if unit == 'days':
        if entry_date == exit_date:
            return 0  # Intraday trade

        # Get trading days between (exclusive of entry, inclusive of exit)
        trading_days = get_trading_days(
            entry_date + timedelta(days=1),
            exit_date,
            include_today=True
        )

        return len(trading_days)

    # Weeks calculation (approximate: trading_days / 5)
    if unit == 'weeks':
        trading_days = calculate_holding_period(entry_date, exit_date, unit='days')
        return trading_days // 5

    raise ValueError(f"Invalid unit: {unit}. Use 'days', 'calendar_days', or 'weeks'")


def calculate_holding_period_detailed(
    entry_date: Union[datetime, date, str],
    exit_date: Union[datetime, date, str]
) -> dict:
    """
    Calculate detailed holding period metrics

    Args:
        entry_date: Entry date/time
        exit_date: Exit date/time

    Returns:
        dict: Detailed holding metrics

    Example:
        >>> calculate_holding_period_detailed('2025-10-01', '2025-10-15')
        {
            'trading_days': 11,
            'calendar_days': 14,
            'weeks': 2,
            'business_days': 10,
            'weekend_days': 4,
            'holidays': 0,
            'is_intraday': False
        }
    """
    # Convert to datetime for consistency
    if isinstance(entry_date, str):
        entry_dt = datetime.fromisoformat(entry_date)
    elif isinstance(entry_date, date) and not isinstance(entry_date, datetime):
        entry_dt = datetime.combine(entry_date, datetime.min.time())
    else:
        entry_dt = entry_date

    if isinstance(exit_date, str):
        exit_dt = datetime.fromisoformat(exit_date)
    elif isinstance(exit_date, date) and not isinstance(exit_date, datetime):
        exit_dt = datetime.combine(exit_date, datetime.min.time())
    else:
        exit_dt = exit_date

    entry_date_only = entry_dt.date()
    exit_date_only = exit_dt.date()

    # Calendar days
    calendar_days = (exit_date_only - entry_date_only).days

    # Trading days
    trading_days = calculate_holding_period(entry_date_only, exit_date_only, unit='days')

    # Count weekends and holidays
    mh = MarketHours()
    weekend_days = 0
    holidays = 0

    current_date = entry_date_only
    while current_date <= exit_date_only:
        dt = datetime.combine(current_date, datetime.min.time())
        dt = MARKET_TIMEZONE.localize(dt)

        # Check if weekend
        if current_date.weekday() >= 5:
            weekend_days += 1
        # Check if holiday (weekday but not market day)
        elif not mh.is_market_day(dt):
            holidays += 1

        current_date += timedelta(days=1)

    # Business days (weekdays, including holidays)
    business_days = calendar_days - weekend_days

    return {
        'trading_days': trading_days,
        'calendar_days': calendar_days,
        'weeks': calendar_days // 7,
        'business_days': business_days,
        'weekend_days': weekend_days,
        'holidays': holidays,
        'is_intraday': entry_date_only == exit_date_only,
        'entry_date': entry_date_only.isoformat(),
        'exit_date': exit_date_only.isoformat(),
    }


# ============================================================================
# DATE RANGE UTILITIES
# ============================================================================

def get_date_range(
    period: str,
    end_date: Optional[datetime] = None
) -> tuple[date, date]:
    """
    Get date range for common periods (1D, 1W, 1M, 3M, 6M, 1Y, YTD)

    Args:
        period: Period string ('1D', '1W', '1M', '3M', '6M', '1Y', 'YTD')
        end_date: End date (default: today)

    Returns:
        tuple: (start_date, end_date)

    Examples:
        >>> get_date_range('1M')
        (date(2025, 9, 15), date(2025, 10, 15))

        >>> get_date_range('YTD')
        (date(2025, 1, 1), date(2025, 10, 15))
    """
    if end_date is None:
        end_date = datetime.now(MARKET_TIMEZONE)

    end = end_date.date() if isinstance(end_date, datetime) else end_date

    period_map = {
        '1D': timedelta(days=1),
        '1W': timedelta(weeks=1),
        '2W': timedelta(weeks=2),
        '1M': timedelta(days=30),
        '3M': timedelta(days=90),
        '6M': timedelta(days=180),
        '1Y': timedelta(days=365),
        '2Y': timedelta(days=730),
    }

    if period == 'YTD':
        # Year to date
        start = date(end.year, 1, 1)
    elif period == 'MTD':
        # Month to date
        start = date(end.year, end.month, 1)
    elif period in period_map:
        start = end - period_map[period]
    else:
        raise ValueError(f"Invalid period: {period}. Use 1D, 1W, 1M, 3M, 6M, 1Y, YTD, or MTD")

    return start, end


def get_quarter_dates(year: int, quarter: int) -> tuple[date, date]:
    """
    Get start and end dates for a fiscal quarter

    Args:
        year: Year (e.g., 2025)
        quarter: Quarter number (1, 2, 3, or 4)

    Returns:
        tuple: (start_date, end_date) of quarter

    Example:
        >>> get_quarter_dates(2025, 3)
        (date(2025, 7, 1), date(2025, 9, 30))
    """
    if quarter not in [1, 2, 3, 4]:
        raise ValueError(f"Quarter must be 1, 2, 3, or 4 (got {quarter})")

    quarter_months = {
        1: (1, 3),
        2: (4, 6),
        3: (7, 9),
        4: (10, 12),
    }

    start_month, end_month = quarter_months[quarter]

    start_date = date(year, start_month, 1)

    # End date is last day of end_month
    if end_month == 12:
        end_date = date(year, 12, 31)
    else:
        # First day of next month - 1 day
        end_date = date(year, end_month + 1, 1) - timedelta(days=1)

    return start_date, end_date


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def is_today_a_trading_day() -> bool:
    """Check if today is a trading day"""
    mh = MarketHours()
    return mh.is_market_day()


def days_until_next_trading_day() -> int:
    """Get number of calendar days until next trading day"""
    today = datetime.now(MARKET_TIMEZONE).date()
    next_trading = get_next_n_trading_days(1, today)

    if next_trading:
        return (next_trading[0] - today).days
    return 0


def format_trading_date(dt: Union[datetime, date]) -> str:
    """
    Format date for trading logs (YYYY-MM-DD)

    Args:
        dt: Date or datetime to format

    Returns:
        str: Formatted date string
    """
    if isinstance(dt, datetime):
        dt = dt.date()

    return dt.strftime('%Y-%m-%d')


def parse_trading_date(date_str: str) -> date:
    """
    Parse trading date string (YYYY-MM-DD)

    Args:
        date_str: Date string in YYYY-MM-DD format

    Returns:
        date: Parsed date object
    """
    return datetime.strptime(date_str, '%Y-%m-%d').date()


# Example usage
if __name__ == '__main__':
    # Timezone conversion
    now_et = to_market_timezone()
    print(f"Current time in ET: {now_et}")

    # Trading days
    days = get_trading_days('2025-10-01', '2025-10-15')
    print(f"Trading days in Oct 1-15: {len(days)}")

    # Next 5 trading days
    next_5 = get_next_n_trading_days(5)
    print(f"Next 5 trading days: {next_5}")

    # Holding period
    holding = calculate_holding_period('2025-10-01', '2025-10-15')
    print(f"Holding period (Oct 1-15): {holding} trading days")

    # Detailed holding period
    detailed = calculate_holding_period_detailed('2025-10-01', '2025-10-15')
    print(f"Detailed holding: {detailed}")

    # Date ranges
    start, end = get_date_range('1M')
    print(f"Last month: {start} to {end}")

    # Quarter dates
    q3_start, q3_end = get_quarter_dates(2025, 3)
    print(f"Q3 2025: {q3_start} to {q3_end}")
