"""
Logging Utility
Provides structured logging with rotation, performance tracking, and trade logging
"""

import logging
import logging.handlers
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
from contextlib import contextmanager
import sys

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DETAILED_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
JSON_LOG_FORMAT = '%(message)s'  # We'll format as JSON ourselves

# Default log directories
DEFAULT_LOG_DIR = Path('logs')
APP_LOG_DIR = DEFAULT_LOG_DIR / 'app'
TRADE_LOG_DIR = DEFAULT_LOG_DIR / 'trades'
ERROR_LOG_DIR = DEFAULT_LOG_DIR / 'errors'
PERFORMANCE_LOG_DIR = DEFAULT_LOG_DIR / 'performance'


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(
    level: str = 'INFO',
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_dir: Optional[Path] = None,
    rotation: str = 'daily',  # 'daily', 'size', 'none'
    max_bytes: int = 10 * 1024 * 1024,  # 10MB for size rotation
    backup_count: int = 30,
    detailed_format: bool = False,
    json_format: bool = False,
) -> logging.Logger:
    """
    Configure logging with rotation and multiple outputs

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Enable file logging
        log_to_console: Enable console logging
        log_dir: Directory for log files (default: logs/app/)
        rotation: Rotation strategy ('daily', 'size', 'none')
        max_bytes: Max file size for size rotation
        backup_count: Number of backup files to keep
        detailed_format: Use detailed log format with file:line info
        json_format: Output logs in JSON format

    Returns:
        logging.Logger: Configured root logger
    """
    # Determine log level
    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)

    # Create log directory
    if log_dir is None:
        log_dir = APP_LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    # Determine log format
    if json_format:
        log_format = JSON_LOG_FORMAT
    elif detailed_format:
        log_format = DETAILED_LOG_FORMAT
    else:
        log_format = DEFAULT_LOG_FORMAT

    # Create formatter
    formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Remove existing handlers
    logger.handlers = []

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_to_file:
        log_filename = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"

        if rotation == 'daily':
            # Daily rotation at midnight
            file_handler = logging.handlers.TimedRotatingFileHandler(
                log_filename,
                when='midnight',
                interval=1,
                backupCount=backup_count,
                encoding='utf-8',
            )
        elif rotation == 'size':
            # Size-based rotation
            file_handler = logging.handlers.RotatingFileHandler(
                log_filename,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8',
            )
        else:
            # No rotation
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')

        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Error file handler (always log errors separately)
    if log_to_file:
        ERROR_LOG_DIR.mkdir(parents=True, exist_ok=True)
        error_log = ERROR_LOG_DIR / f"errors_{datetime.now().strftime('%Y%m%d')}.log"

        error_handler = logging.handlers.TimedRotatingFileHandler(
            error_log,
            when='midnight',
            interval=1,
            backupCount=backup_count,
            encoding='utf-8',
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

    logger.info("Logging configured successfully")
    logger.debug(f"Log level: {level}")
    logger.debug(f"Log directory: {log_dir}")
    logger.debug(f"Rotation: {rotation}")

    return logger


# ============================================================================
# LOGGER FACTORY
# ============================================================================

def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with the specified name

    Args:
        name: Logger name (typically __name__)
        level: Optional logging level override

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)

    if level is not None:
        logger.setLevel(LOG_LEVELS.get(level.upper(), logging.INFO))

    return logger


# ============================================================================
# PERFORMANCE LOGGING
# ============================================================================

@contextmanager
def log_performance(
    operation: str,
    logger: Optional[logging.Logger] = None,
    level: str = 'INFO',
    include_result: bool = False,
):
    """
    Context manager to log execution time of an operation

    Args:
        operation: Name of the operation being timed
        logger: Logger instance (default: root logger)
        level: Log level for timing message
        include_result: Whether to include operation result in log

    Usage:
        with log_performance('data_fetch'):
            result = fetch_data()

        # With result logging
        with log_performance('calculation', include_result=True) as perf:
            result = expensive_calculation()
            perf['result'] = result
    """
    if logger is None:
        logger = logging.getLogger()

    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)

    start_time = time.time()
    perf_data = {
        'operation': operation,
        'start_time': datetime.now().isoformat(),
    }

    try:
        yield perf_data
    finally:
        end_time = time.time()
        elapsed = end_time - start_time

        perf_data['end_time'] = datetime.now().isoformat()
        perf_data['elapsed_seconds'] = round(elapsed, 3)

        # Build log message
        message = f"[PERF] {operation} completed in {elapsed:.3f}s"

        if include_result and 'result' in perf_data:
            message += f" | Result: {perf_data['result']}"

        logger.log(log_level, message)

        # Also log to performance log file
        _log_performance_metric(perf_data)


def _log_performance_metric(perf_data: Dict):
    """Log performance metric to dedicated performance log"""
    PERFORMANCE_LOG_DIR.mkdir(parents=True, exist_ok=True)
    perf_log = PERFORMANCE_LOG_DIR / f"performance_{datetime.now().strftime('%Y%m%d')}.jsonl"

    try:
        with open(perf_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(perf_data) + '\n')
    except Exception:
        pass  # Don't fail if performance logging fails


# ============================================================================
# TRADE LOGGING
# ============================================================================

def log_trade(
    action: str,
    ticker: str,
    quantity: int,
    price: float,
    strategy: str,
    total_value: Optional[float] = None,
    order_id: Optional[str] = None,
    status: str = 'PENDING',
    notes: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
    **kwargs,
):
    """
    Log a trade execution with structured data

    Args:
        action: Trade action (BUY, SELL, SHORT, COVER)
        ticker: Stock ticker
        quantity: Number of shares
        price: Execution price
        strategy: Trading strategy name
        total_value: Total value of trade
        order_id: Broker order ID
        status: Order status (PENDING, FILLED, REJECTED, CANCELLED)
        notes: Additional notes
        logger: Logger instance
        **kwargs: Additional metadata to log
    """
    if logger is None:
        logger = logging.getLogger('trades')

    # Calculate total value if not provided
    if total_value is None:
        total_value = quantity * price

    # Build trade data
    trade_data = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'ticker': ticker,
        'quantity': quantity,
        'price': round(price, 2),
        'total_value': round(total_value, 2),
        'strategy': strategy,
        'order_id': order_id,
        'status': status,
        'notes': notes,
    }

    # Add any additional metadata
    trade_data.update(kwargs)

    # Log to console/file
    message = (
        f"[TRADE] {action} {quantity} {ticker} @ ${price:.2f} "
        f"(${total_value:,.2f}) | {strategy} | {status}"
    )

    if order_id:
        message += f" | Order: {order_id}"

    if notes:
        message += f" | {notes}"

    logger.info(message)

    # Log to structured trade log
    _log_trade_structured(trade_data)


def _log_trade_structured(trade_data: Dict):
    """Log trade to dedicated structured trade log"""
    TRADE_LOG_DIR.mkdir(parents=True, exist_ok=True)
    trade_log = TRADE_LOG_DIR / f"trades_{datetime.now().strftime('%Y%m%d')}.jsonl"

    try:
        with open(trade_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(trade_data) + '\n')
    except Exception:
        pass  # Don't fail if trade logging fails


# ============================================================================
# SPECIALIZED LOGGERS
# ============================================================================

class TradeLogger:
    """Specialized logger for trade execution"""

    def __init__(self, logger_name: str = 'trades'):
        self.logger = get_logger(logger_name)
        TRADE_LOG_DIR.mkdir(parents=True, exist_ok=True)

    def log_order_submitted(self, ticker: str, action: str, quantity: int,
                           price: float, strategy: str, **kwargs):
        """Log order submission"""
        log_trade(
            action=action,
            ticker=ticker,
            quantity=quantity,
            price=price,
            strategy=strategy,
            status='SUBMITTED',
            logger=self.logger,
            **kwargs
        )

    def log_order_filled(self, ticker: str, action: str, quantity: int,
                        fill_price: float, order_id: str, strategy: str, **kwargs):
        """Log order fill"""
        log_trade(
            action=action,
            ticker=ticker,
            quantity=quantity,
            price=fill_price,
            strategy=strategy,
            order_id=order_id,
            status='FILLED',
            logger=self.logger,
            **kwargs
        )

    def log_order_rejected(self, ticker: str, action: str, quantity: int,
                          price: float, reason: str, strategy: str, **kwargs):
        """Log order rejection"""
        log_trade(
            action=action,
            ticker=ticker,
            quantity=quantity,
            price=price,
            strategy=strategy,
            status='REJECTED',
            notes=f"Rejection reason: {reason}",
            logger=self.logger,
            **kwargs
        )


class PerformanceLogger:
    """Specialized logger for performance metrics"""

    def __init__(self):
        self.logger = get_logger('performance')
        PERFORMANCE_LOG_DIR.mkdir(parents=True, exist_ok=True)

    def log_metric(self, metric_name: str, value: Any, tags: Optional[Dict] = None):
        """Log a performance metric"""
        metric_data = {
            'timestamp': datetime.now().isoformat(),
            'metric': metric_name,
            'value': value,
        }

        if tags:
            metric_data['tags'] = tags

        self.logger.info(f"[METRIC] {metric_name}: {value}")
        _log_performance_metric(metric_data)

    def log_portfolio_metrics(self, portfolio_value: float, daily_pnl: float,
                             positions_count: int, cash: float, **kwargs):
        """Log portfolio metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_value': round(portfolio_value, 2),
            'daily_pnl': round(daily_pnl, 2),
            'daily_pnl_pct': round((daily_pnl / portfolio_value * 100), 2) if portfolio_value > 0 else 0,
            'positions_count': positions_count,
            'cash': round(cash, 2),
        }
        metrics.update(kwargs)

        self.logger.info(
            f"[PORTFOLIO] Value: ${portfolio_value:,.2f} | "
            f"P&L: ${daily_pnl:+,.2f} ({metrics['daily_pnl_pct']:+.2f}%) | "
            f"Positions: {positions_count} | Cash: ${cash:,.2f}"
        )

        _log_performance_metric(metrics)


# ============================================================================
# LOG ANALYSIS UTILITIES
# ============================================================================

def read_trade_log(date: Optional[str] = None) -> list:
    """
    Read trades from log file

    Args:
        date: Date string in YYYYMMDD format (default: today)

    Returns:
        list: List of trade dictionaries
    """
    if date is None:
        date = datetime.now().strftime('%Y%m%d')

    trade_log = TRADE_LOG_DIR / f"trades_{date}.jsonl"

    if not trade_log.exists():
        return []

    trades = []
    with open(trade_log, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                trades.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue

    return trades


def read_performance_log(date: Optional[str] = None) -> list:
    """
    Read performance metrics from log file

    Args:
        date: Date string in YYYYMMDD format (default: today)

    Returns:
        list: List of performance metric dictionaries
    """
    if date is None:
        date = datetime.now().strftime('%Y%m%d')

    perf_log = PERFORMANCE_LOG_DIR / f"performance_{date}.jsonl"

    if not perf_log.exists():
        return []

    metrics = []
    with open(perf_log, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                metrics.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue

    return metrics


# ============================================================================
# INITIALIZATION
# ============================================================================

# Create log directories
for log_dir in [DEFAULT_LOG_DIR, APP_LOG_DIR, TRADE_LOG_DIR, ERROR_LOG_DIR, PERFORMANCE_LOG_DIR]:
    log_dir.mkdir(parents=True, exist_ok=True)


# Example usage
if __name__ == '__main__':
    # Setup logging
    setup_logging(level='DEBUG', detailed_format=True)

    logger = get_logger(__name__)

    logger.info("This is an info message")
    logger.warning("This is a warning")
    logger.error("This is an error")

    # Performance logging
    with log_performance('test_operation', logger=logger):
        time.sleep(0.5)

    # Trade logging
    log_trade(
        action='BUY',
        ticker='AAPL',
        quantity=100,
        price=175.50,
        strategy='momentum',
        order_id='ABC123',
        status='FILLED'
    )

    # Specialized loggers
    trade_logger = TradeLogger()
    trade_logger.log_order_filled(
        ticker='TSLA',
        action='SELL',
        quantity=50,
        fill_price=250.00,
        order_id='XYZ789',
        strategy='mean_reversion'
    )

    perf_logger = PerformanceLogger()
    perf_logger.log_portfolio_metrics(
        portfolio_value=100000.0,
        daily_pnl=2500.0,
        positions_count=12,
        cash=25000.0
    )
