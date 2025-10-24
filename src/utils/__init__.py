"""
Utility modules for the AI Trading Bot

Provides essential utilities for:
- Market hours and trading day validation
- Structured logging with rotation
- Configuration loading and management
- Date/time utilities and holding period calculations
"""

# Market Hours utilities
from .market_hours import (
    MarketHours,
    is_market_open,
    is_market_day,
    get_market_status,
    should_run_pipeline,
    get_market_schedule,
    is_trading_hours,
    get_next_market_open,
    is_market_open_today,
)

# Logging utilities
from .logger import (
    setup_logging,
    get_logger,
    log_performance,
    log_trade,
    TradeLogger,
    PerformanceLogger,
    read_trade_log,
    read_performance_log,
)

# Configuration utilities
from .config_loader import (
    ConfigLoader,
    get_config_loader,
    load_config,
    validate_config,
    get_secret,
    load_env_file,
)

# Date utilities
from .date_utils import (
    # Timezone conversion
    to_market_timezone,
    to_utc,
    is_same_trading_day,

    # Trading day calculations
    get_trading_days,
    get_next_n_trading_days,
    get_previous_n_trading_days,

    # Holding period calculations
    calculate_holding_period,
    calculate_holding_period_detailed,

    # Date ranges
    get_date_range,
    get_quarter_dates,

    # Convenience functions
    is_today_a_trading_day,
    days_until_next_trading_day,
    format_trading_date,
    parse_trading_date,

    # Constants
    MARKET_TIMEZONE,
    UTC_TIMEZONE,
)

__all__ = [
    # Market Hours
    'MarketHours',
    'is_market_open',
    'is_market_day',
    'get_market_status',
    'should_run_pipeline',
    'get_market_schedule',
    'is_trading_hours',
    'get_next_market_open',
    'is_market_open_today',

    # Logging
    'setup_logging',
    'get_logger',
    'log_performance',
    'log_trade',
    'TradeLogger',
    'PerformanceLogger',
    'read_trade_log',
    'read_performance_log',

    # Configuration
    'ConfigLoader',
    'get_config_loader',
    'load_config',
    'validate_config',
    'get_secret',
    'load_env_file',

    # Date Utilities
    'to_market_timezone',
    'to_utc',
    'is_same_trading_day',
    'get_trading_days',
    'get_next_n_trading_days',
    'get_previous_n_trading_days',
    'calculate_holding_period',
    'calculate_holding_period_detailed',
    'get_date_range',
    'get_quarter_dates',
    'is_today_a_trading_day',
    'days_until_next_trading_day',
    'format_trading_date',
    'parse_trading_date',
    'MARKET_TIMEZONE',
    'UTC_TIMEZONE',
]

__version__ = '2.0.0'
