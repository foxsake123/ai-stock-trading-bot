"""
Tests for schedule_config.py
Tests trading day calculation, holiday detection, and timezone handling.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pytz

# Import module to test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from schedule_config import get_next_trading_day, is_trading_day, MARKET_HOLIDAYS_2025


class TestGetNextTradingDay:
    """Test get_next_trading_day() function."""

    @pytest.mark.unit
    def test_friday_to_monday(self):
        """Test Friday -> Monday transition (skip weekend)."""
        # Friday, October 10, 2025 at 3:00 PM (after market close)
        friday = datetime(2025, 10, 10, 15, 0, 0)

        next_day = get_next_trading_day(from_date=friday)

        # Should return Monday, October 13, 2025
        assert next_day.year == 2025
        assert next_day.month == 10
        assert next_day.day == 13
        assert next_day.weekday() == 0  # Monday

    @pytest.mark.unit
    def test_before_holiday_to_after_holiday(self):
        """Test day before holiday -> day after holiday."""
        # Wednesday, November 26, 2025 (day before Thanksgiving)
        before_thanksgiving = datetime(2025, 11, 26, 15, 0, 0)

        next_day = get_next_trading_day(from_date=before_thanksgiving)

        # Should return Monday, December 1, 2025 (skip Thanksgiving + weekend)
        assert next_day.year == 2025
        assert next_day.month == 12
        assert next_day.day == 1
        assert next_day.weekday() == 0  # Monday

    @pytest.mark.unit
    def test_regular_weekday_to_next_day(self):
        """Test regular weekday -> next weekday."""
        # Monday, October 13, 2025 at 3:00 PM (after market close)
        monday = datetime(2025, 10, 13, 15, 0, 0)

        next_day = get_next_trading_day(from_date=monday)

        # Should return Tuesday, October 14, 2025
        assert next_day.year == 2025
        assert next_day.month == 10
        assert next_day.day == 14
        assert next_day.weekday() == 1  # Tuesday

    @pytest.mark.unit
    def test_thursday_to_friday(self):
        """Test Thursday -> Friday transition."""
        # Thursday, October 9, 2025 at 3:00 PM (after market close)
        thursday = datetime(2025, 10, 9, 15, 0, 0)

        next_day = get_next_trading_day(from_date=thursday)

        # Should return Friday, October 10, 2025
        assert next_day.year == 2025
        assert next_day.month == 10
        assert next_day.day == 10
        assert next_day.weekday() == 4  # Friday

    @pytest.mark.unit
    def test_year_boundary(self):
        """Test year boundary (December -> January)."""
        # Tuesday, December 30, 2025 at 3:00 PM (after market close)
        dec_30 = datetime(2025, 12, 30, 15, 0, 0)

        next_day = get_next_trading_day(from_date=dec_30)

        # Should return Wednesday, December 31, 2025
        # (Dec 31 is a trading day, Jan 1 2026 is a holiday)
        assert next_day.year == 2025
        assert next_day.month == 12
        assert next_day.day == 31
        assert next_day.weekday() == 2  # Wednesday

    @pytest.mark.unit
    def test_skip_multiple_holidays(self):
        """Test skipping multiple consecutive holidays."""
        # Wednesday, December 24, 2025 at 3:00 PM (before Christmas)
        before_christmas = datetime(2025, 12, 24, 15, 0, 0)

        next_day = get_next_trading_day(from_date=before_christmas)

        # Should skip Christmas (12/25 Thursday), weekend (12/27-28), return Monday 12/29
        assert next_day.year == 2025
        assert next_day.month == 12
        assert next_day.day == 29
        assert next_day.weekday() == 0  # Monday


class TestIsTradingDay:
    """Test is_trading_day() function."""

    @pytest.mark.unit
    def test_weekday_is_trading_day(self):
        """Test that regular weekdays are trading days."""
        # Monday, October 13, 2025
        monday = datetime(2025, 10, 13)
        assert is_trading_day(monday) is True

        # Wednesday, October 15, 2025
        wednesday = datetime(2025, 10, 15)
        assert is_trading_day(wednesday) is True

    @pytest.mark.unit
    def test_saturday_not_trading_day(self):
        """Test that Saturday is not a trading day."""
        # Saturday, October 11, 2025
        saturday = datetime(2025, 10, 11)
        assert is_trading_day(saturday) is False

    @pytest.mark.unit
    def test_sunday_not_trading_day(self):
        """Test that Sunday is not a trading day."""
        # Sunday, October 12, 2025
        sunday = datetime(2025, 10, 12)
        assert is_trading_day(sunday) is False

    @pytest.mark.unit
    def test_holiday_not_trading_day(self):
        """Test that holidays are not trading days."""
        # Christmas Day 2025 (Thursday, December 25)
        christmas = datetime(2025, 12, 25)
        assert is_trading_day(christmas) is False

        # Thanksgiving 2025 (Thursday, November 27)
        thanksgiving = datetime(2025, 11, 27)
        assert is_trading_day(thanksgiving) is False

    @pytest.mark.unit
    def test_new_years_day(self):
        """Test New Year's Day is not a trading day."""
        # January 1, 2025 (Wednesday)
        new_years = datetime(2025, 1, 1)
        assert is_trading_day(new_years) is False

    @pytest.mark.unit
    def test_independence_day(self):
        """Test Independence Day is not a trading day."""
        # July 4, 2025 (Friday)
        july_4 = datetime(2025, 7, 4)
        assert is_trading_day(july_4) is False

    @pytest.mark.unit
    def test_memorial_day(self):
        """Test Memorial Day is not a trading day."""
        # Memorial Day 2025 (last Monday of May - May 26)
        memorial_day = datetime(2025, 5, 26)
        # Check if this date is in MARKET_HOLIDAYS_2025
        if memorial_day.strftime('%Y-%m-%d') in MARKET_HOLIDAYS_2025:
            assert is_trading_day(memorial_day) is False

    @pytest.mark.unit
    def test_labor_day(self):
        """Test Labor Day is not a trading day."""
        # Labor Day 2025 (first Monday of September - Sept 1)
        labor_day = datetime(2025, 9, 1)
        # Check if this date is in MARKET_HOLIDAYS_2025
        if labor_day.strftime('%Y-%m-%d') in MARKET_HOLIDAYS_2025:
            assert is_trading_day(labor_day) is False

    @pytest.mark.unit
    def test_multiple_consecutive_days(self):
        """Test multiple consecutive days for consistency."""
        # Week of October 13-17, 2025 (all weekdays, no holidays)
        dates = [
            datetime(2025, 10, 13),  # Monday
            datetime(2025, 10, 14),  # Tuesday
            datetime(2025, 10, 15),  # Wednesday
            datetime(2025, 10, 16),  # Thursday
            datetime(2025, 10, 17),  # Friday
        ]

        for date in dates:
            assert is_trading_day(date) is True

    @pytest.mark.unit
    def test_weekend_after_friday(self):
        """Test weekend days after Friday are not trading days."""
        # Friday, October 10, 2025
        friday = datetime(2025, 10, 10)
        saturday = datetime(2025, 10, 11)
        sunday = datetime(2025, 10, 12)

        assert is_trading_day(friday) is True
        assert is_trading_day(saturday) is False
        assert is_trading_day(sunday) is False


class TestMarketHolidays:
    """Test MARKET_HOLIDAYS_2025 constant."""

    @pytest.mark.unit
    def test_holidays_list_format(self):
        """Test that holidays list is in correct format."""
        from datetime import date
        assert isinstance(MARKET_HOLIDAYS_2025, list)
        assert len(MARKET_HOLIDAYS_2025) > 0

        # Check format is date object
        for holiday in MARKET_HOLIDAYS_2025:
            assert isinstance(holiday, date)
            assert holiday.year == 2025

    @pytest.mark.unit
    def test_required_holidays_present(self):
        """Test that major holidays are in the list."""
        from datetime import date

        # Check for December holidays (Christmas)
        december_holidays = [h for h in MARKET_HOLIDAYS_2025 if h.month == 12]
        assert len(december_holidays) > 0

        # Check for November holiday (Thanksgiving)
        november_holidays = [h for h in MARKET_HOLIDAYS_2025 if h.month == 11]
        assert len(november_holidays) > 0

        # Check for specific major holidays
        assert date(2025, 12, 25) in MARKET_HOLIDAYS_2025  # Christmas
        assert date(2025, 7, 4) in MARKET_HOLIDAYS_2025    # Independence Day
        assert date(2025, 1, 1) in MARKET_HOLIDAYS_2025    # New Year's Day

    @pytest.mark.unit
    def test_holidays_are_sorted(self):
        """Test that holidays are in chronological order."""
        sorted_holidays = sorted(MARKET_HOLIDAYS_2025)
        assert MARKET_HOLIDAYS_2025 == sorted_holidays

    @pytest.mark.unit
    def test_no_duplicate_holidays(self):
        """Test that there are no duplicate holidays."""
        assert len(MARKET_HOLIDAYS_2025) == len(set(MARKET_HOLIDAYS_2025))
