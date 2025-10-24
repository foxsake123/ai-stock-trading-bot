"""
Market Hours Utility
Determines if the market is open and provides market schedule information
"""

import pytz
from datetime import datetime, time
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class MarketHours:
    """Utility for checking market hours and schedule"""

    # US market holidays 2025 (update annually)
    MARKET_HOLIDAYS_2025 = [
        "2025-01-01",  # New Year's Day
        "2025-01-20",  # Martin Luther King Jr. Day
        "2025-02-17",  # Presidents' Day
        "2025-04-18",  # Good Friday
        "2025-05-26",  # Memorial Day
        "2025-07-03",  # Independence Day (observed)
        "2025-09-01",  # Labor Day
        "2025-11-27",  # Thanksgiving
        "2025-12-25",  # Christmas
    ]

    # Market hours (ET)
    PRE_MARKET_START = time(4, 0)      # 4:00 AM ET
    MARKET_OPEN = time(9, 30)          # 9:30 AM ET
    MARKET_CLOSE = time(16, 0)         # 4:00 PM ET
    AFTER_HOURS_END = time(20, 0)      # 8:00 PM ET

    # Early close days (1:00 PM ET close)
    EARLY_CLOSE_DAYS_2025 = [
        "2025-07-03",  # Day before Independence Day
        "2025-11-28",  # Day after Thanksgiving
        "2025-12-24",  # Christmas Eve
    ]
    EARLY_CLOSE_TIME = time(13, 0)     # 1:00 PM ET

    def __init__(self):
        """Initialize market hours checker"""
        self.et_tz = pytz.timezone('America/New_York')

    def get_current_time_et(self) -> datetime:
        """
        Get current time in ET timezone

        Returns:
            datetime: Current time in ET
        """
        return datetime.now(self.et_tz)

    def is_market_day(self, dt: Optional[datetime] = None) -> bool:
        """
        Check if given date is a market day (weekday and not a holiday)

        Args:
            dt: Date to check (default: current date)

        Returns:
            bool: True if market is open this day
        """
        if dt is None:
            dt = self.get_current_time_et()

        # Check if weekend
        if dt.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False

        # Check if holiday
        date_str = dt.strftime('%Y-%m-%d')
        if date_str in self.MARKET_HOLIDAYS_2025:
            return False

        return True

    def is_early_close_day(self, dt: Optional[datetime] = None) -> bool:
        """
        Check if given date is an early close day

        Args:
            dt: Date to check (default: current date)

        Returns:
            bool: True if market closes early (1 PM ET)
        """
        if dt is None:
            dt = self.get_current_time_et()

        date_str = dt.strftime('%Y-%m-%d')
        return date_str in self.EARLY_CLOSE_DAYS_2025

    def get_market_close_time(self, dt: Optional[datetime] = None) -> time:
        """
        Get market close time for given date

        Args:
            dt: Date to check (default: current date)

        Returns:
            time: Market close time (4:00 PM or 1:00 PM ET)
        """
        if self.is_early_close_day(dt):
            return self.EARLY_CLOSE_TIME
        return self.MARKET_CLOSE

    def is_market_open(self, dt: Optional[datetime] = None) -> bool:
        """
        Check if market is currently open for regular trading

        Args:
            dt: Time to check (default: current time)

        Returns:
            bool: True if market is open
        """
        if dt is None:
            dt = self.get_current_time_et()

        # Check if it's a market day
        if not self.is_market_day(dt):
            return False

        # Check if within market hours
        current_time = dt.time()
        close_time = self.get_market_close_time(dt)

        return self.MARKET_OPEN <= current_time < close_time

    def is_pre_market(self, dt: Optional[datetime] = None) -> bool:
        """
        Check if currently in pre-market hours (4:00 AM - 9:30 AM ET)

        Args:
            dt: Time to check (default: current time)

        Returns:
            bool: True if in pre-market hours
        """
        if dt is None:
            dt = self.get_current_time_et()

        if not self.is_market_day(dt):
            return False

        current_time = dt.time()
        return self.PRE_MARKET_START <= current_time < self.MARKET_OPEN

    def is_after_hours(self, dt: Optional[datetime] = None) -> bool:
        """
        Check if currently in after-hours trading (4:00 PM - 8:00 PM ET)

        Args:
            dt: Time to check (default: current time)

        Returns:
            bool: True if in after-hours
        """
        if dt is None:
            dt = self.get_current_time_et()

        if not self.is_market_day(dt):
            return False

        current_time = dt.time()
        close_time = self.get_market_close_time(dt)

        return close_time <= current_time < self.AFTER_HOURS_END

    def get_market_status(self, dt: Optional[datetime] = None) -> Dict:
        """
        Get comprehensive market status information

        Args:
            dt: Time to check (default: current time)

        Returns:
            Dict with market status details
        """
        if dt is None:
            dt = self.get_current_time_et()

        is_mkt_day = self.is_market_day(dt)
        is_open = self.is_market_open(dt)
        is_pre = self.is_pre_market(dt)
        is_after = self.is_after_hours(dt)
        is_early = self.is_early_close_day(dt)

        # Determine status
        if not is_mkt_day:
            status = "CLOSED - Market Holiday/Weekend"
        elif is_pre:
            status = "PRE-MARKET"
        elif is_open:
            status = "OPEN"
        elif is_after:
            status = "AFTER-HOURS"
        else:
            status = "CLOSED"

        return {
            'current_time_et': dt.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'status': status,
            'is_market_day': is_mkt_day,
            'is_market_open': is_open,
            'is_pre_market': is_pre,
            'is_after_hours': is_after,
            'is_early_close': is_early,
            'market_open_time': self.MARKET_OPEN.strftime('%H:%M'),
            'market_close_time': self.get_market_close_time(dt).strftime('%H:%M'),
            'pre_market_start': self.PRE_MARKET_START.strftime('%H:%M'),
            'after_hours_end': self.AFTER_HOURS_END.strftime('%H:%M'),
        }

    def should_run_daily_pipeline(self, dt: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        Determine if daily pipeline should run

        Args:
            dt: Time to check (default: current time)

        Returns:
            Tuple[bool, str]: (should_run, reason)
        """
        if dt is None:
            dt = self.get_current_time_et()

        # Must be a market day
        if not self.is_market_day(dt):
            return False, "Not a market day (weekend or holiday)"

        # Pipeline should run before market open (typically 6:00 AM)
        current_time = dt.time()

        # If it's after market close, too late for today
        if current_time >= self.MARKET_CLOSE:
            return False, "Market already closed for the day"

        # If before pre-market, too early
        if current_time < time(6, 0):
            return False, "Too early (pipeline runs at 6:00 AM ET)"

        # Ideal time: 6:00 AM - 9:00 AM
        if time(6, 0) <= current_time < time(9, 0):
            return True, "Optimal pipeline execution window (6:00-9:00 AM ET)"

        # Between 9:00 AM and market open
        if time(9, 0) <= current_time < self.MARKET_OPEN:
            return True, "Late but acceptable (before market open)"

        # Market is already open
        if self.is_market_open(dt):
            return False, "Market already open (run pipeline before 9:30 AM)"

        return False, "Outside pipeline execution window"

    def time_until_market_open(self, dt: Optional[datetime] = None) -> Optional[int]:
        """
        Calculate minutes until market opens

        Args:
            dt: Time to check (default: current time)

        Returns:
            int: Minutes until market open, or None if not a market day
        """
        if dt is None:
            dt = self.get_current_time_et()

        if not self.is_market_day(dt):
            return None

        if self.is_market_open(dt):
            return 0  # Already open

        # Calculate time until 9:30 AM
        market_open_today = dt.replace(
            hour=self.MARKET_OPEN.hour,
            minute=self.MARKET_OPEN.minute,
            second=0,
            microsecond=0
        )

        diff = market_open_today - dt
        return int(diff.total_seconds() / 60)

    def log_market_status(self):
        """Log current market status"""
        status = self.get_market_status()
        logger.info("=" * 60)
        logger.info("MARKET STATUS")
        logger.info("=" * 60)
        for key, value in status.items():
            logger.info(f"{key}: {value}")
        logger.info("=" * 60)


# Convenience functions
def is_market_open() -> bool:
    """Check if market is currently open"""
    return MarketHours().is_market_open()


def is_market_day() -> bool:
    """Check if today is a market day"""
    return MarketHours().is_market_day()


def get_market_status() -> Dict:
    """Get current market status"""
    return MarketHours().get_market_status()


def should_run_pipeline() -> Tuple[bool, str]:
    """Check if daily pipeline should run now"""
    return MarketHours().should_run_daily_pipeline()


def get_market_schedule(dt: Optional[datetime] = None) -> Dict:
    """
    Get market schedule for a given date

    Args:
        dt: Date to check (default: today)

    Returns:
        Dict with market schedule times
    """
    mh = MarketHours()
    if dt is None:
        dt = mh.get_current_time_et()

    return {
        'date': dt.strftime('%Y-%m-%d'),
        'is_market_day': mh.is_market_day(dt),
        'is_early_close': mh.is_early_close_day(dt),
        'pre_market_start': mh.PRE_MARKET_START.strftime('%H:%M'),
        'market_open': mh.MARKET_OPEN.strftime('%H:%M'),
        'market_close': mh.get_market_close_time(dt).strftime('%H:%M'),
        'after_hours_end': mh.AFTER_HOURS_END.strftime('%H:%M'),
    }


def is_trading_hours(dt: Optional[datetime] = None) -> bool:
    """
    Check if currently in regular trading hours (9:30 AM - 4:00 PM ET)

    Args:
        dt: Time to check (default: current time)

    Returns:
        bool: True if in regular trading hours
    """
    return MarketHours().is_market_open(dt)


def get_next_market_open(dt: Optional[datetime] = None) -> datetime:
    """
    Get the next market open datetime

    Args:
        dt: Starting datetime (default: current time)

    Returns:
        datetime: Next market open time in ET
    """
    mh = MarketHours()
    if dt is None:
        dt = mh.get_current_time_et()

    # Start with current date
    check_date = dt

    # If market is already open today, return today's open
    if mh.is_market_open(check_date):
        return check_date.replace(
            hour=mh.MARKET_OPEN.hour,
            minute=mh.MARKET_OPEN.minute,
            second=0,
            microsecond=0
        )

    # If before market open today and it's a market day, return today's open
    if mh.is_market_day(check_date) and check_date.time() < mh.MARKET_OPEN:
        return check_date.replace(
            hour=mh.MARKET_OPEN.hour,
            minute=mh.MARKET_OPEN.minute,
            second=0,
            microsecond=0
        )

    # Otherwise, find next market day
    from datetime import timedelta
    max_days_ahead = 10  # Safety limit

    for days_ahead in range(1, max_days_ahead):
        next_date = check_date + timedelta(days=days_ahead)

        if mh.is_market_day(next_date):
            return next_date.replace(
                hour=mh.MARKET_OPEN.hour,
                minute=mh.MARKET_OPEN.minute,
                second=0,
                microsecond=0
            )

    # Fallback: return next Monday at market open
    days_until_monday = (7 - check_date.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7

    next_monday = check_date + timedelta(days=days_until_monday)
    return next_monday.replace(
        hour=mh.MARKET_OPEN.hour,
        minute=mh.MARKET_OPEN.minute,
        second=0,
        microsecond=0
    )


def is_market_open_today() -> bool:
    """
    Check if US market is open today (not necessarily right now)

    Returns:
        bool: True if market is open sometime today
    """
    return MarketHours().is_market_day()
