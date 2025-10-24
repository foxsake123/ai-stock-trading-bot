# AI Trading Bot - Utilities Documentation
**Version**: 2.0.0
**Last Updated**: October 23, 2025

## Overview

The `src/utils/` module provides essential utility functions for the AI trading bot, including:
- **Market hours validation** - Trading day checks, market schedules
- **Structured logging** - Performance tracking, trade logging
- **Configuration management** - YAML loading, secrets management
- **Date/time utilities** - Holding period calculations, timezone conversions

---

## Table of Contents

1. [Market Hours Utilities](#1-market-hours-utilities)
2. [Logging Utilities](#2-logging-utilities)
3. [Configuration Utilities](#3-configuration-utilities)
4. [Date Utilities](#4-date-utilities)
5. [Quick Reference](#5-quick-reference)
6. [Usage Examples](#6-usage-examples)

---

## 1. Market Hours Utilities

**Module**: `src/utils/market_hours.py`

### Overview
Determines if the US stock market is open, provides market schedules, and handles market holidays.

### Key Functions

#### `is_market_open()` → bool
Check if the market is currently open for regular trading (9:30 AM - 4:00 PM ET).

```python
from src.utils import is_market_open

if is_market_open():
    print("Market is OPEN - place trades")
else:
    print("Market is CLOSED")
```

#### `is_market_day()` → bool
Check if today is a trading day (excludes weekends and holidays).

```python
from src.utils import is_market_day

if is_market_day():
    print("Today is a trading day")
else:
    print("Market closed today (weekend or holiday)")
```

#### `get_market_status()` → Dict
Get comprehensive market status with all details.

```python
from src.utils import get_market_status

status = get_market_status()
print(status)
# {
#     'current_time_et': '2025-10-23 14:30:00 EDT',
#     'status': 'OPEN',
#     'is_market_day': True,
#     'is_market_open': True,
#     'is_pre_market': False,
#     'is_after_hours': False,
#     'is_early_close': False,
#     'market_open_time': '09:30',
#     'market_close_time': '16:00',
#     'pre_market_start': '04:00',
#     'after_hours_end': '20:00'
# }
```

#### `get_market_schedule(date)` → Dict
Get market schedule for a specific date.

```python
from src.utils import get_market_schedule
from datetime import datetime

schedule = get_market_schedule(datetime(2025, 10, 23))
print(schedule)
# {
#     'date': '2025-10-23',
#     'is_market_day': True,
#     'is_early_close': False,
#     'pre_market_start': '04:00',
#     'market_open': '09:30',
#     'market_close': '16:00',
#     'after_hours_end': '20:00'
# }
```

#### `get_next_market_open(date)` → datetime
Get the next market open time from a given date.

```python
from src.utils import get_next_market_open

next_open = get_next_market_open()
print(f"Next market open: {next_open}")
# Next market open: 2025-10-24 09:30:00 EDT
```

#### `should_run_pipeline()` → (bool, str)
Determine if the daily pipeline should run now.

```python
from src.utils import should_run_pipeline

should_run, reason = should_run_pipeline()
print(f"Should run: {should_run} - {reason}")
# Should run: True - Optimal pipeline execution window (6:00-9:00 AM ET)
```

### Market Holidays 2025
- January 1 (New Year's Day)
- January 20 (MLK Jr. Day)
- February 17 (Presidents' Day)
- April 18 (Good Friday)
- May 26 (Memorial Day)
- July 3 (Independence Day, observed)
- September 1 (Labor Day)
- November 27 (Thanksgiving)
- December 25 (Christmas)

### Early Close Days 2025 (1:00 PM ET)
- July 3 (Day before Independence Day)
- November 28 (Day after Thanksgiving)
- December 24 (Christmas Eve)

---

## 2. Logging Utilities

**Module**: `src/utils/logger.py`

### Overview
Provides structured logging with rotation, performance tracking, and trade logging.

### Setup Logging

#### `setup_logging(level, log_to_file, log_to_console, rotation, ...)`
Configure the logging system with rotation and multiple outputs.

```python
from src.utils import setup_logging

# Basic setup (defaults to INFO level)
logger = setup_logging()

# Custom setup
logger = setup_logging(
    level='DEBUG',
    log_to_file=True,
    log_to_console=True,
    rotation='daily',       # Options: 'daily', 'size', 'none'
    max_bytes=10*1024*1024, # 10MB for size rotation
    backup_count=30,        # Keep 30 backup files
    detailed_format=True,   # Include file:line info
    json_format=False       # Use JSON format
)
```

### Get Logger

#### `get_logger(name, level)` → Logger
Get a named logger instance.

```python
from src.utils import get_logger

logger = get_logger(__name__)
logger.info("Application started")
logger.warning("Low disk space")
logger.error("Failed to connect to API")
```

### Performance Logging

#### `log_performance(operation, logger, level, include_result)`
Context manager to log execution time of operations.

```python
from src.utils import log_performance, get_logger

logger = get_logger(__name__)

# Basic timing
with log_performance('data_fetch', logger=logger):
    data = fetch_market_data()

# With result logging
with log_performance('calculation', include_result=True) as perf:
    result = expensive_calculation()
    perf['result'] = result

# Output: [PERF] data_fetch completed in 2.345s
```

**Performance logs** are saved to `logs/performance/performance_YYYYMMDD.jsonl`:
```json
{
  "operation": "data_fetch",
  "start_time": "2025-10-23T14:30:00",
  "end_time": "2025-10-23T14:30:02",
  "elapsed_seconds": 2.345,
  "result": "success"
}
```

### Trade Logging

#### `log_trade(action, ticker, quantity, price, strategy, ...)`
Log a trade execution with structured data.

```python
from src.utils import log_trade

log_trade(
    action='BUY',
    ticker='AAPL',
    quantity=100,
    price=175.50,
    strategy='momentum',
    order_id='ABC123',
    status='FILLED',
    notes='Breakout entry'
)

# Output: [TRADE] BUY 100 AAPL @ $175.50 ($17,550.00) | momentum | FILLED | Order: ABC123
```

**Trade logs** are saved to `logs/trades/trades_YYYYMMDD.jsonl`:
```json
{
  "timestamp": "2025-10-23T09:35:00",
  "action": "BUY",
  "ticker": "AAPL",
  "quantity": 100,
  "price": 175.50,
  "total_value": 17550.00,
  "strategy": "momentum",
  "order_id": "ABC123",
  "status": "FILLED",
  "notes": "Breakout entry"
}
```

### Specialized Loggers

#### `TradeLogger` - Dedicated trade logger

```python
from src.utils import TradeLogger

trade_logger = TradeLogger()

# Order submitted
trade_logger.log_order_submitted(
    ticker='TSLA',
    action='BUY',
    quantity=50,
    price=250.00,
    strategy='momentum'
)

# Order filled
trade_logger.log_order_filled(
    ticker='TSLA',
    action='BUY',
    quantity=50,
    fill_price=250.50,
    order_id='XYZ789',
    strategy='momentum'
)

# Order rejected
trade_logger.log_order_rejected(
    ticker='TSLA',
    action='BUY',
    quantity=50,
    price=250.00,
    reason='Insufficient funds',
    strategy='momentum'
)
```

#### `PerformanceLogger` - Performance metrics logger

```python
from src.utils import PerformanceLogger

perf_logger = PerformanceLogger()

# Log single metric
perf_logger.log_metric(
    'api_latency_ms',
    value=245.5,
    tags={'endpoint': 'prices', 'source': 'alpaca'}
)

# Log portfolio metrics
perf_logger.log_portfolio_metrics(
    portfolio_value=100000.0,
    daily_pnl=2500.0,
    positions_count=12,
    cash=25000.0,
    total_return_pct=25.5
)

# Output: [PORTFOLIO] Value: $100,000.00 | P&L: $+2,500.00 (+2.50%) | Positions: 12 | Cash: $25,000.00
```

### Reading Logs

#### `read_trade_log(date)` → List[Dict]
Read trades from structured log file.

```python
from src.utils import read_trade_log

# Today's trades
trades = read_trade_log()

# Specific date
trades = read_trade_log('20251023')

for trade in trades:
    print(f"{trade['action']} {trade['quantity']} {trade['ticker']} @ ${trade['price']}")
```

#### `read_performance_log(date)` → List[Dict]
Read performance metrics from log file.

```python
from src.utils import read_performance_log

metrics = read_performance_log('20251023')

for metric in metrics:
    if metric.get('operation'):
        print(f"{metric['operation']}: {metric['elapsed_seconds']:.3f}s")
```

### Log Directories

All logs are organized in `logs/`:
```
logs/
├── app/              # Application logs (daily rotation)
│   ├── app_20251023.log
│   └── app_20251022.log
├── trades/           # Trade execution logs (JSONL)
│   ├── trades_20251023.jsonl
│   └── trades_20251022.jsonl
├── errors/           # Error logs (daily rotation)
│   ├── errors_20251023.log
│   └── errors_20251022.log
└── performance/      # Performance metrics (JSONL)
    ├── performance_20251023.jsonl
    └── performance_20251022.jsonl
```

---

## 3. Configuration Utilities

**Module**: `src/utils/config_loader.py`

### Overview
Loads YAML configurations, manages secrets, and provides nested config access.

### Load Configuration

#### `load_config(config_name, config_dir)` → Dict
Load a YAML configuration file.

```python
from src.utils import load_config

# Load main config
config = load_config('config')
print(config['environment'])  # 'production'

# Load data sources config
data_sources = load_config('data_sources')
print(data_sources['financial_datasets']['enabled'])  # True

# Load alerts config
alerts = load_config('alerts')
print(alerts['channels']['telegram']['enabled'])  # True
```

### ConfigLoader Class

#### Advanced usage with ConfigLoader class

```python
from src.utils import ConfigLoader

loader = ConfigLoader(config_dir='configs/')

# Load with caching
config = loader.load_config('config', use_cache=True)

# Access nested values with dot notation
value = loader.get_nested(config, 'trading.bots.dee_bot.enabled', default=False)
print(value)  # True

# Validate required keys
required = ['environment', 'trading.mode', 'feature_flags']
is_valid, missing = loader.validate_config(config, required)

if not is_valid:
    print(f"Missing required keys: {missing}")
```

### Environment Variable Substitution

Config files support `${VAR:default}` syntax for environment variables:

**config.yaml**:
```yaml
database:
  host: ${DB_HOST:localhost}
  port: ${DB_PORT:5432}
  password: ${DB_PASSWORD:secret}
```

**Usage**:
```python
from src.utils import load_config

# Loads with environment variable substitution
config = load_config('config')

# DB_HOST env var is used if set, otherwise 'localhost'
print(config['database']['host'])
```

### Secret Management

#### `get_secret(key, default, required)` → str
Retrieve API keys and secrets from environment variables.

```python
from src.utils import get_secret

# Optional secret with default
api_key = get_secret('ANTHROPIC_API_KEY', default=None)

# Required secret (raises error if missing)
api_key = get_secret('ANTHROPIC_API_KEY', required=True)

# With default value
slack_webhook = get_secret('SLACK_WEBHOOK', default='https://hooks.slack.com/default')
```

#### `load_env_file(env_file)` → None
Load environment variables from `.env` file.

```python
from src.utils import load_env_file
from pathlib import Path

# Load from default location (configs/.env)
load_env_file()

# Load from custom location
load_env_file(Path('config/production.env'))
```

**.env file format**:
```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-xxxxx
ALPACA_API_KEY=PKxxxxx
ALPACA_SECRET_KEY=xxxxx

# Database
DB_HOST=localhost
DB_PORT=5432
DB_PASSWORD="my secure password"

# Notifications
TELEGRAM_BOT_TOKEN=123456:ABCdefg
TELEGRAM_CHAT_ID=-1001234567890
```

### Configuration Validation

```python
from src.utils import validate_config, load_config

config = load_config('config')

# Validate required keys (supports dot notation)
required_keys = [
    'environment',
    'trading.mode',
    'trading.bots.dee_bot.enabled',
    'trading.bots.shorgan_bot.enabled',
    'feature_flags.multi_agent_system'
]

is_valid, missing_keys = validate_config(config, required_keys)

if not is_valid:
    print(f"Configuration validation failed!")
    print(f"Missing keys: {missing_keys}")
else:
    print("Configuration is valid ✅")
```

---

## 4. Date Utilities

**Module**: `src/utils/date_utils.py`

### Overview
Provides trading day calculations, timezone conversions, and holding period analysis.

### Timezone Conversion

#### `to_market_timezone(dt)` → datetime
Convert datetime to market timezone (America/New_York).

```python
from src.utils import to_market_timezone
from datetime import datetime

# Current time in ET
now_et = to_market_timezone()
print(now_et)  # 2025-10-23 14:30:00 EDT

# Convert UTC to ET
utc_time = datetime.utcnow()
et_time = to_market_timezone(utc_time)

# Parse string and convert to ET
et_time = to_market_timezone("2025-10-23 14:30:00")
```

#### `to_utc(dt)` → datetime
Convert datetime to UTC timezone.

```python
from src.utils import to_utc
from datetime import datetime

# Convert ET to UTC
et_time = datetime(2025, 10, 23, 14, 30)
utc_time = to_utc(et_time)
```

#### `is_same_trading_day(dt1, dt2)` → bool
Check if two datetimes are on the same trading day.

```python
from src.utils import is_same_trading_day
from datetime import datetime

dt1 = datetime(2025, 10, 23, 9, 30)   # Market open
dt2 = datetime(2025, 10, 23, 16, 0)   # Market close

if is_same_trading_day(dt1, dt2):
    print("Same trading day")  # True
```

### Trading Day Calculations

#### `get_trading_days(start_date, end_date, include_today)` → List[date]
Get list of trading days between two dates (excludes weekends and holidays).

```python
from src.utils import get_trading_days

# Get trading days in October 2025
days = get_trading_days('2025-10-01', '2025-10-31')
print(f"Trading days in October: {len(days)}")  # 23 days

# Exclude end date
days = get_trading_days('2025-10-01', '2025-10-31', include_today=False)
print(f"Trading days: {len(days)}")  # 22 days
```

#### `get_next_n_trading_days(n, start_date)` → List[date]
Get the next N trading days from a given date.

```python
from src.utils import get_next_n_trading_days

# Next 5 trading days
next_5 = get_next_n_trading_days(5)
print(next_5)
# [date(2025, 10, 24), date(2025, 10, 25), date(2025, 10, 28), ...]

# Next 10 trading days from specific date
next_10 = get_next_n_trading_days(10, start_date='2025-10-23')
```

#### `get_previous_n_trading_days(n, end_date)` → List[date]
Get the previous N trading days before a given date.

```python
from src.utils import get_previous_n_trading_days

# Last 5 trading days
last_5 = get_previous_n_trading_days(5)
print(last_5)  # Most recent first
```

### Holding Period Calculations

#### `calculate_holding_period(entry_date, exit_date, unit)` → int
Calculate holding period between entry and exit dates.

```python
from src.utils import calculate_holding_period

# Trading days held
days = calculate_holding_period('2025-10-01', '2025-10-15')
print(f"Held for {days} trading days")  # 11 trading days

# Calendar days
cal_days = calculate_holding_period('2025-10-01', '2025-10-15', unit='calendar_days')
print(f"Held for {cal_days} calendar days")  # 14 calendar days

# Weeks
weeks = calculate_holding_period('2025-10-01', '2025-10-31', unit='weeks')
print(f"Held for {weeks} weeks")  # 4 weeks

# Intraday trade (same day)
days = calculate_holding_period('2025-10-15', '2025-10-15')
print(days)  # 0 (intraday)
```

#### `calculate_holding_period_detailed(entry_date, exit_date)` → Dict
Calculate detailed holding period metrics.

```python
from src.utils import calculate_holding_period_detailed

detailed = calculate_holding_period_detailed('2025-10-01', '2025-10-15')
print(detailed)
# {
#     'trading_days': 11,
#     'calendar_days': 14,
#     'weeks': 2,
#     'business_days': 10,
#     'weekend_days': 4,
#     'holidays': 0,
#     'is_intraday': False,
#     'entry_date': '2025-10-01',
#     'exit_date': '2025-10-15'
# }
```

### Date Range Utilities

#### `get_date_range(period, end_date)` → (date, date)
Get date range for common periods.

```python
from src.utils import get_date_range

# Last month
start, end = get_date_range('1M')

# Last 3 months
start, end = get_date_range('3M')

# Year to date
start, end = get_date_range('YTD')

# Month to date
start, end = get_date_range('MTD')

# Supported periods: '1D', '1W', '2W', '1M', '3M', '6M', '1Y', '2Y', 'YTD', 'MTD'
```

#### `get_quarter_dates(year, quarter)` → (date, date)
Get start and end dates for a fiscal quarter.

```python
from src.utils import get_quarter_dates

# Q3 2025 (July 1 - September 30)
start, end = get_quarter_dates(2025, 3)
print(f"Q3 2025: {start} to {end}")
# Q3 2025: 2025-07-01 to 2025-09-30
```

### Convenience Functions

#### `is_today_a_trading_day()` → bool
```python
from src.utils import is_today_a_trading_day

if is_today_a_trading_day():
    print("Market is open today")
```

#### `days_until_next_trading_day()` → int
```python
from src.utils import days_until_next_trading_day

days = days_until_next_trading_day()
print(f"Next trading day in {days} days")
```

#### `format_trading_date(dt)` → str
```python
from src.utils import format_trading_date
from datetime import datetime

date_str = format_trading_date(datetime.now())
print(date_str)  # "2025-10-23"
```

#### `parse_trading_date(date_str)` → date
```python
from src.utils import parse_trading_date

dt = parse_trading_date("2025-10-23")
print(dt)  # date(2025, 10, 23)
```

---

## 5. Quick Reference

### Common Imports

```python
# Market hours
from src.utils import is_market_open, is_market_day, get_market_status

# Logging
from src.utils import setup_logging, get_logger, log_performance, log_trade

# Configuration
from src.utils import load_config, get_secret, validate_config

# Date utilities
from src.utils import (
    to_market_timezone,
    get_trading_days,
    calculate_holding_period,
    get_date_range
)
```

### One-Liner Examples

```python
# Check if market is open right now
if is_market_open(): execute_trades()

# Get logger
logger = get_logger(__name__)

# Load config
config = load_config('config')

# Get API key
api_key = get_secret('ANTHROPIC_API_KEY', required=True)

# Get last 30 trading days
from src.utils import get_previous_n_trading_days
last_30_days = get_previous_n_trading_days(30)

# Calculate holding period
from src.utils import calculate_holding_period
days_held = calculate_holding_period('2025-10-01', '2025-10-15')

# Time an operation
from src.utils import log_performance, get_logger
logger = get_logger(__name__)
with log_performance('data_fetch', logger=logger):
    data = fetch_data()
```

---

## 6. Usage Examples

### Example 1: Daily Pipeline with Full Logging

```python
from src.utils import (
    setup_logging,
    get_logger,
    log_performance,
    is_market_day,
    should_run_pipeline,
    load_config
)

# Setup logging
setup_logging(
    level='INFO',
    log_to_file=True,
    log_to_console=True,
    rotation='daily',
    backup_count=30
)

logger = get_logger(__name__)

# Load configuration
config = load_config('config')

# Check if pipeline should run
should_run, reason = should_run_pipeline()

if not should_run:
    logger.info(f"Pipeline skipped: {reason}")
    exit(0)

logger.info("Starting daily pipeline...")

# Execute with performance tracking
with log_performance('daily_pipeline', logger=logger):
    # Phase 1: Data fetch
    with log_performance('data_fetch', logger=logger):
        data = fetch_market_data()

    # Phase 2: Analysis
    with log_performance('analysis', logger=logger):
        recommendations = analyze_data(data)

    # Phase 3: Validation
    with log_performance('validation', logger=logger):
        approved = validate_recommendations(recommendations)

logger.info(f"Pipeline complete: {len(approved)} trades approved")
```

### Example 2: Trade Execution with Logging

```python
from src.utils import TradeLogger, get_logger

logger = get_logger(__name__)
trade_logger = TradeLogger()

def execute_trade(ticker, action, quantity, price, strategy):
    """Execute a trade with comprehensive logging"""

    logger.info(f"Submitting {action} order for {quantity} {ticker}")

    # Log order submission
    trade_logger.log_order_submitted(
        ticker=ticker,
        action=action,
        quantity=quantity,
        price=price,
        strategy=strategy
    )

    try:
        # Submit order to broker
        order = submit_order(ticker, action, quantity, price)

        # Wait for fill
        fill = wait_for_fill(order.id)

        # Log successful fill
        trade_logger.log_order_filled(
            ticker=ticker,
            action=action,
            quantity=fill.quantity,
            fill_price=fill.price,
            order_id=order.id,
            strategy=strategy
        )

        logger.info(f"✅ Order filled: {quantity} {ticker} @ ${fill.price}")
        return fill

    except OrderRejected as e:
        # Log rejection
        trade_logger.log_order_rejected(
            ticker=ticker,
            action=action,
            quantity=quantity,
            price=price,
            reason=str(e),
            strategy=strategy
        )

        logger.error(f"❌ Order rejected: {e}")
        raise

# Execute trades
execute_trade('AAPL', 'BUY', 100, 175.50, 'momentum')
execute_trade('TSLA', 'SELL', 50, 250.00, 'mean_reversion')
```

### Example 3: Configuration Management

```python
from src.utils import load_config, get_secret, validate_config, load_env_file
from pathlib import Path

# Load environment variables
load_env_file(Path('configs/.env'))

# Load configurations
config = load_config('config')
data_sources = load_config('data_sources')
alerts = load_config('alerts')

# Validate configuration
required_keys = [
    'environment',
    'trading.mode',
    'trading.bots.dee_bot.enabled',
    'trading.bots.shorgan_bot.enabled',
]

is_valid, missing = validate_config(config, required_keys)

if not is_valid:
    raise ValueError(f"Invalid configuration. Missing: {missing}")

# Get secrets
anthropic_key = get_secret('ANTHROPIC_API_KEY', required=True)
alpaca_key = get_secret('ALPACA_API_KEY', required=True)
alpaca_secret = get_secret('ALPACA_SECRET_KEY', required=True)

# Get nested configuration values
from src.utils import ConfigLoader

loader = ConfigLoader()

dee_bot_enabled = loader.get_nested(config, 'trading.bots.dee_bot.enabled', default=False)
multi_agent = loader.get_nested(config, 'feature_flags.multi_agent_system', default=False)

if dee_bot_enabled and multi_agent:
    print("✅ DEE-BOT with multi-agent system enabled")
```

### Example 4: Holding Period Analysis

```python
from src.utils import (
    calculate_holding_period,
    calculate_holding_period_detailed,
    get_trading_days,
    to_market_timezone
)
from datetime import datetime

# Calculate simple holding period
entry = '2025-10-01'
exit = '2025-10-15'

days_held = calculate_holding_period(entry, exit)
print(f"Position held for {days_held} trading days")  # 11 days

# Detailed analysis
detailed = calculate_holding_period_detailed(entry, exit)
print(f"""
Holding Period Analysis:
- Trading days: {detailed['trading_days']}
- Calendar days: {detailed['calendar_days']}
- Weekends: {detailed['weekend_days']}
- Holidays: {detailed['holidays']}
- Intraday: {detailed['is_intraday']}
""")

# Get all trading days in holding period
trading_days = get_trading_days(entry, exit)
print(f"Traded on {len(trading_days)} days:")
for day in trading_days:
    print(f"  - {day}")

# Calculate average holding period for portfolio
positions = [
    {'entry': '2025-10-01', 'exit': '2025-10-10'},
    {'entry': '2025-10-05', 'exit': '2025-10-20'},
    {'entry': '2025-10-10', 'exit': '2025-10-15'},
]

holding_periods = [
    calculate_holding_period(p['entry'], p['exit'])
    for p in positions
]

avg_holding = sum(holding_periods) / len(holding_periods)
print(f"Average holding period: {avg_holding:.1f} days")
```

### Example 5: Market Hours Validation

```python
from src.utils import (
    is_market_open,
    is_market_day,
    get_market_status,
    get_next_market_open,
    to_market_timezone
)
from datetime import datetime

# Check current market status
status = get_market_status()

print(f"""
Current Market Status:
Time: {status['current_time_et']}
Status: {status['status']}
Market Day: {status['is_market_day']}
Market Open: {status['is_market_open']}
Pre-Market: {status['is_pre_market']}
After-Hours: {status['is_after_hours']}
Early Close: {status['is_early_close']}

Schedule:
Pre-Market: {status['pre_market_start']}
Market Open: {status['market_open_time']}
Market Close: {status['market_close_time']}
After-Hours End: {status['after_hours_end']}
""")

# Conditional execution based on market status
if is_market_open():
    print("✅ EXECUTING TRADES")
    execute_daily_trades()
elif status['is_pre_market']:
    print("⏳ PRE-MARKET - Preparing for market open")
    prepare_orders()
elif status['is_after_hours']:
    print("📊 AFTER-HOURS - Analyzing performance")
    analyze_daily_performance()
else:
    print("❌ MARKET CLOSED")
    next_open = get_next_market_open()
    print(f"Next market open: {next_open}")
```

---

## Summary

The `src/utils/` module provides a comprehensive set of utilities for:

✅ **Market hours validation** - Know when to trade, when to wait
✅ **Structured logging** - Track performance, trades, and errors
✅ **Configuration management** - Load configs, manage secrets
✅ **Date/time utilities** - Calculate holding periods, trading days

All utilities are production-ready with:
- Comprehensive error handling
- Detailed logging
- Environment variable support
- Type hints for IDE support
- Extensive documentation

For questions or issues, see the main [README.md](../README.md) or file an issue on GitHub.

---

**Last Updated**: October 23, 2025
**Version**: 2.0.0
