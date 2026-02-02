#!/usr/bin/env python3
"""
Daily Trade Execution System
Automatically executes trades from TODAYS_TRADES markdown file

Enhanced with:
- Retry logic with exponential backoff
- Order fill verification
- Circuit breaker for API resilience
"""

import os
import re
import sys
import json
import time
import logging
import alpaca_trade_api as tradeapi
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Change to project root directory (important for Task Scheduler)
PROJECT_ROOT = Path(__file__).parent.parent.parent
os.chdir(PROJECT_ROOT)

# Load environment variables from project root
load_dotenv(PROJECT_ROOT / ".env")

# Add path for logging
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import regulatory compliance checker
try:
    from scripts.automation.regulatory_compliance import RegulatoryComplianceChecker, check_trade_compliance, TradeRecord
    COMPLIANCE_AVAILABLE = True
except ImportError:
    COMPLIANCE_AVAILABLE = False
    print("[WARNING] Regulatory compliance module not available")

# Import tax-loss harvesting module
try:
    from scripts.automation.tax_loss_harvester import TaxLossHarvester
    TLH_AVAILABLE = True
except ImportError:
    TLH_AVAILABLE = False
    print("[WARNING] Tax-loss harvesting module not available")

# Import core utilities for retry logic, order verification, and circuit breaker
try:
    from scripts.core import (
        retry_with_backoff,
        alpaca_circuit,
        CircuitBreakerOpenError,
        OrderVerifier,
        FillStatus
    )
    CORE_UTILS_AVAILABLE = True
except ImportError:
    CORE_UTILS_AVAILABLE = False
    print("[WARNING] Core utilities not available - running without retry/verification")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Alpaca API Configuration (from environment variables)
DEE_BOT_CONFIG = {
    'API_KEY': os.getenv('ALPACA_API_KEY_DEE'),
    'SECRET_KEY': os.getenv('ALPACA_SECRET_KEY_DEE'),
    'BASE_URL': 'https://paper-api.alpaca.markets'  # Keep DEE on paper
}

# SHORGAN-BOT PAPER CONFIGURATION
SHORGAN_PAPER_CONFIG = {
    'API_KEY': os.getenv('ALPACA_API_KEY_SHORGAN'),  # PAPER KEYS
    'SECRET_KEY': os.getenv('ALPACA_SECRET_KEY_SHORGAN'),  # PAPER KEYS
    'BASE_URL': 'https://paper-api.alpaca.markets'  # PAPER TRADING
}

# ⚠️ SHORGAN-BOT LIVE TRADING CONFIGURATION ⚠️
SHORGAN_LIVE_CONFIG = {
    'API_KEY': os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'),  # LIVE KEYS
    'SECRET_KEY': os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'),  # LIVE KEYS
    'BASE_URL': 'https://api.alpaca.markets'  # LIVE TRADING - REAL MONEY
}

# SHORGAN-BOT LIVE TRADING SETTINGS (User requested: Aggressive)
SHORGAN_LIVE_TRADING = True  # Set to False to disable live trading
SHORGAN_CAPITAL = 3000.0  # Live account capital ($3K invested)
SHORGAN_MAX_POSITION_SIZE = 290.0  # $300 max per position (10% of capital)
SHORGAN_MIN_POSITION_SIZE = 90.0  # $90 minimum position size (3%)
SHORGAN_CASH_BUFFER = 0.0  # No cash buffer (aggressive mode)
SHORGAN_MAX_POSITIONS = 10  # Max 10 concurrent positions
SHORGAN_MAX_DAILY_LOSS = 300.0  # Stop trading if lose $300 in one day (10%)
SHORGAN_MAX_TRADES_PER_DAY = 5  # Execute top 5 highest-confidence trades only
SHORGAN_ALLOW_SHORTS = False  # DISABLED - Cash account (no margin approval)
SHORGAN_ALLOW_OPTIONS = True  # Enable options trading (if approved)

# ⚠️ DEE-BOT LIVE TRADING CONFIGURATION ⚠️
DEE_BOT_LIVE_CONFIG = {
    'API_KEY': os.getenv('ALPACA_LIVE_API_KEY_DEE'),  # LIVE KEYS
    'SECRET_KEY': os.getenv('ALPACA_LIVE_SECRET_KEY_DEE'),  # LIVE KEYS
    'BASE_URL': 'https://api.alpaca.markets'  # LIVE TRADING - REAL MONEY
}

# DEE-BOT LIVE TRADING SETTINGS ($10K S&P 100 Account)
DEE_LIVE_TRADING = False  # DISABLED until user creates account and provides API keys
DEE_CAPITAL = 10000.0  # Live account capital ($10K invested)

# Safety Settings (Issue #4 and #7 fixes)
REQUIRE_LIVE_CONFIRMATION = os.getenv('REQUIRE_LIVE_CONFIRMATION', 'true').lower() == 'true'  # Require confirmation for live trades
MAX_RETRY_ATTEMPTS = 3  # Maximum retry attempts per trade (Issue #7 fix)
DEE_MAX_POSITION_SIZE = 1000.0  # $1,000 max per position (10% of capital)
DEE_MIN_POSITION_SIZE = 400.0  # $400 minimum position size (4%)
DEE_CASH_BUFFER = 500.0  # Keep $500 buffer for emergencies
DEE_MAX_POSITIONS = 12  # Max 12 concurrent positions
DEE_MAX_DAILY_LOSS = 500.0  # Stop trading if lose $500 in one day (5%)
DEE_MAX_TRADES_PER_DAY = 5  # Execute top 5 highest-confidence trades only
DEE_STOP_LOSS_PCT = 0.08  # 8% hard stop loss on all positions

@dataclass
class LiveAccountSettings:
    """Configuration for a live trading account, used to avoid duplicating
    daily-loss-limit, position-count, and position-size checks."""
    name: str
    enabled: bool
    capital: float
    max_position_size: float
    min_position_size: float
    max_positions: int
    max_daily_loss: float
    max_trades_per_day: int
    stop_loss_pct: float = 0.18

SHORGAN_LIVE_SETTINGS = LiveAccountSettings(
    name="SHORGAN-BOT",
    enabled=SHORGAN_LIVE_TRADING,
    capital=SHORGAN_CAPITAL,
    max_position_size=SHORGAN_MAX_POSITION_SIZE,
    min_position_size=SHORGAN_MIN_POSITION_SIZE,
    max_positions=SHORGAN_MAX_POSITIONS,
    max_daily_loss=SHORGAN_MAX_DAILY_LOSS,
    max_trades_per_day=SHORGAN_MAX_TRADES_PER_DAY,
    stop_loss_pct=0.18,
)

DEE_LIVE_SETTINGS = LiveAccountSettings(
    name="DEE-BOT",
    enabled=DEE_LIVE_TRADING,
    capital=DEE_CAPITAL,
    max_position_size=DEE_MAX_POSITION_SIZE,
    min_position_size=DEE_MIN_POSITION_SIZE,
    max_positions=DEE_MAX_POSITIONS,
    max_daily_loss=DEE_MAX_DAILY_LOSS,
    max_trades_per_day=DEE_MAX_TRADES_PER_DAY,
    stop_loss_pct=DEE_STOP_LOSS_PCT,
)


# Validate API keys are loaded
if not DEE_BOT_CONFIG['API_KEY'] or not DEE_BOT_CONFIG['SECRET_KEY']:
    raise ValueError("DEE-BOT API keys not found in environment variables. Check your .env file.")
if not SHORGAN_PAPER_CONFIG['API_KEY'] or not SHORGAN_PAPER_CONFIG['SECRET_KEY']:
    raise ValueError("SHORGAN-BOT Paper API keys not found in environment variables. Check your .env file.")
if not SHORGAN_LIVE_CONFIG['API_KEY'] or not SHORGAN_LIVE_CONFIG['SECRET_KEY']:
    print("[WARNING] SHORGAN-BOT Live API keys not found - live trading disabled")

class DailyTradeExecutor:
    def __init__(self):
        # DEE-BOT Paper API
        self.dee_api = tradeapi.REST(
            DEE_BOT_CONFIG['API_KEY'],
            DEE_BOT_CONFIG['SECRET_KEY'],
            DEE_BOT_CONFIG['BASE_URL'],
            api_version='v2'
        )

        # DEE-BOT Live API (only if enabled and keys available)
        self.dee_live_api = None
        if DEE_LIVE_TRADING and DEE_BOT_LIVE_CONFIG['API_KEY'] and DEE_BOT_LIVE_CONFIG['SECRET_KEY']:
            self.dee_live_api = tradeapi.REST(
                DEE_BOT_LIVE_CONFIG['API_KEY'],
                DEE_BOT_LIVE_CONFIG['SECRET_KEY'],
                DEE_BOT_LIVE_CONFIG['BASE_URL'],
                api_version='v2'
            )
            print("[LIVE] DEE-BOT Live API initialized")

        # SHORGAN-BOT Paper API
        self.shorgan_paper_api = tradeapi.REST(
            SHORGAN_PAPER_CONFIG['API_KEY'],
            SHORGAN_PAPER_CONFIG['SECRET_KEY'],
            SHORGAN_PAPER_CONFIG['BASE_URL'],
            api_version='v2'
        )
        print("[PAPER] SHORGAN-BOT Paper API initialized")

        # SHORGAN-BOT Live API
        self.shorgan_live_api = None
        if SHORGAN_LIVE_TRADING and SHORGAN_LIVE_CONFIG['API_KEY'] and SHORGAN_LIVE_CONFIG['SECRET_KEY']:
            self.shorgan_live_api = tradeapi.REST(
                SHORGAN_LIVE_CONFIG['API_KEY'],
                SHORGAN_LIVE_CONFIG['SECRET_KEY'],
                SHORGAN_LIVE_CONFIG['BASE_URL'],
                api_version='v2'
            )
            print("[LIVE] SHORGAN-BOT Live API initialized")

        self.executed_trades = []
        self.failed_trades = []

        # DEE-BOT is LONG-ONLY - no shorting allowed
        self.dee_bot_long_only = True

        # Extended hours trading configuration
        self.enable_extended_hours = True  # Allow pre-market and after-hours trading

        # Initialize tracking for live accounts
        self.shorgan_starting_equity = None
        self.dee_starting_equity = None
        self.dee_live_trades_today = 0
        self._init_live_tracking(self.shorgan_live_api, SHORGAN_LIVE_SETTINGS)
        self._init_live_tracking(self.dee_live_api, DEE_LIVE_SETTINGS)
        if not DEE_LIVE_TRADING:
            print(f"[INFO] DEE-BOT Live trading is DISABLED (enable with DEE_LIVE_TRADING=True)")

    def _init_live_tracking(self, api, settings):
        """Initialize daily performance tracking for a live account."""
        if not settings.enabled or not api:
            return
        try:
            account = api.get_account()
            starting_equity = float(account.last_equity)
            # Store on self using the settings name as key
            if "SHORGAN" in settings.name:
                self.shorgan_starting_equity = starting_equity
            else:
                self.dee_starting_equity = starting_equity
            print(f"\n[LIVE] {settings.name} LIVE TRADING ACTIVE")
            print(f"Starting Equity: ${starting_equity:,.2f}")
            print(f"Daily Loss Limit: ${settings.max_daily_loss:.2f}")
            print(f"Max Trades Today: {settings.max_trades_per_day}")
            if settings.stop_loss_pct < 0.18:
                print(f"Stop Loss: {settings.stop_loss_pct*100:.0f}%")
        except Exception as e:
            print(f"[ERROR] Could not get {settings.name} starting equity: {e}")

    def is_extended_hours(self, api=None):
        """
        Check if current time is in extended hours (pre-market or after-hours).
        Pre-market: 4:00 AM - 9:30 AM ET
        After-hours: 4:00 PM - 8:00 PM ET
        """
        try:
            # Use the API to get accurate market clock
            clock = (api or self.dee_api).get_clock()

            if clock.is_open:
                return False  # Regular market hours

            # Get current Eastern time
            from datetime import timezone
            import pytz
            eastern = pytz.timezone('US/Eastern')
            now_et = datetime.now(eastern)
            current_hour = now_et.hour
            current_minute = now_et.minute
            current_time = current_hour + current_minute / 60.0

            # Pre-market: 4:00 AM - 9:30 AM ET
            if 4.0 <= current_time < 9.5:
                return True

            # After-hours: 4:00 PM - 8:00 PM ET
            if 16.0 <= current_time < 20.0:
                return True

            return False
        except Exception as e:
            print(f"[WARNING] Could not determine extended hours status: {e}")
            # Fallback: check time manually
            try:
                import pytz
                eastern = pytz.timezone('US/Eastern')
                now_et = datetime.now(eastern)
                current_hour = now_et.hour
                current_minute = now_et.minute
                current_time = current_hour + current_minute / 60.0

                if 4.0 <= current_time < 9.5 or 16.0 <= current_time < 20.0:
                    return True
            except:
                pass
            return False

    def _confirm_live_trades(self, bot_name, trades_count, total_value):
        """
        Prompt user to confirm live trades (Issue #4 fix).
        Can be bypassed with REQUIRE_LIVE_CONFIRMATION=false in .env
        """
        if not REQUIRE_LIVE_CONFIRMATION:
            print(f"[INFO] Live confirmation bypassed (REQUIRE_LIVE_CONFIRMATION=false)")
            return True

        print("\n" + "=" * 60)
        print(f"[LIVE TRADE CONFIRMATION REQUIRED] - {bot_name}")
        print("=" * 60)
        print(f"About to execute {trades_count} LIVE trades")
        print(f"Estimated value: ${total_value:,.2f}")
        print(f"\nThis will trade REAL MONEY on your live account!")
        print("=" * 60)

        try:
            response = input("\nType 'YES' to confirm, anything else to cancel: ").strip()
            if response == 'YES':
                print("[CONFIRMED] Proceeding with live trades...")
                return True
            else:
                print("[CANCELLED] Live trades cancelled by user")
                self._send_telegram_alert(f"{bot_name} live trades CANCELLED by user confirmation", is_critical=False)
                return False
        except EOFError:
            # Running in non-interactive mode (e.g., Task Scheduler)
            print("[INFO] Non-interactive mode - bypassing confirmation")
            return True

    def _check_daily_loss_limit(self, api, settings, starting_equity):
        """Circuit breaker: Stop trading if daily loss exceeds limit.
        Returns True if trading can continue, False if loss limit hit."""
        if not settings.enabled or not api or starting_equity is None:
            return True

        try:
            account = api.get_account()
            current_equity = float(account.equity)
            daily_pnl = current_equity - starting_equity

            if daily_pnl < -settings.max_daily_loss:
                print(f"\n[CIRCUIT BREAKER] TRIGGERED - {settings.name}")
                print(f"Daily Loss: ${-daily_pnl:.2f}")
                print(f"Loss Limit: ${settings.max_daily_loss:.2f}")
                print(f"[ALERT] STOPPING ALL {settings.name} TRADING FOR TODAY")
                return False

            print(f"[OK] {settings.name} Daily P&L: ${daily_pnl:+.2f} (Limit: -${settings.max_daily_loss:.2f})")
            return True
        except Exception as e:
            print(f"[ERROR] Could not check {settings.name} daily loss limit: {e}")
            return False  # Err on side of caution

    def _check_position_count_limit(self, api, settings):
        """Don't exceed max concurrent positions. Returns True if within limit."""
        if not settings.enabled or not api:
            return True

        try:
            positions = api.list_positions()
            position_count = len(positions)

            if position_count >= settings.max_positions:
                print(f"\n[WARNING] {settings.name} position limit reached: {position_count}/{settings.max_positions}")
                print(f"Cannot open new positions until existing ones close")
                return False

            print(f"[OK] {settings.name} Position Count: {position_count}/{settings.max_positions}")
            return True
        except Exception as e:
            print(f"[ERROR] Could not check {settings.name} position count: {e}")
            return False

    def _calculate_position_size(self, price, shares_recommended, settings):
        """Calculate safe position size for a live account.
        Returns 0 if position is too small, otherwise the adjusted share count."""
        if not settings.enabled:
            return shares_recommended  # Use recommended size for paper

        max_shares = int(settings.max_position_size / price)

        if max_shares * price < settings.min_position_size:
            print(f"[SKIP] {settings.name} position too small: ${max_shares * price:.2f} < ${settings.min_position_size}")
            return 0

        final_shares = min(shares_recommended, max_shares)
        position_value = final_shares * price
        print(f"[INFO] {settings.name} Position: {final_shares} shares @ ${price:.2f} = ${position_value:.2f}")
        return final_shares

    # Backward-compatible wrappers that delegate to the unified methods
    def check_shorgan_daily_loss_limit(self):
        return self._check_daily_loss_limit(self.shorgan_live_api, SHORGAN_LIVE_SETTINGS, self.shorgan_starting_equity)

    def check_shorgan_position_count_limit(self):
        return self._check_position_count_limit(self.shorgan_live_api, SHORGAN_LIVE_SETTINGS)

    def calculate_shorgan_position_size(self, price, shares_recommended):
        return self._calculate_position_size(price, shares_recommended, SHORGAN_LIVE_SETTINGS)

    def check_dee_live_daily_loss_limit(self):
        return self._check_daily_loss_limit(self.dee_live_api, DEE_LIVE_SETTINGS, self.dee_starting_equity)

    def check_dee_live_position_count_limit(self):
        return self._check_position_count_limit(self.dee_live_api, DEE_LIVE_SETTINGS)

    def calculate_dee_live_position_size(self, price, shares_recommended):
        return self._calculate_position_size(price, shares_recommended, DEE_LIVE_SETTINGS)

    def _run_tax_loss_harvesting(self):
        """Run tax-loss harvesting for all live accounts before regular trades."""
        print("\n" + "=" * 70)
        print("TAX-LOSS HARVESTING SCAN")
        print("=" * 70)

        # Harvest from SHORGAN Live (always active)
        if SHORGAN_LIVE_TRADING:
            try:
                print("\n[TLH] Scanning SHORGAN-BOT Live...")
                shorgan_tlh = TaxLossHarvester("SHORGAN-LIVE")
                shorgan_results = shorgan_tlh.run_daily_harvest(dry_run=False)
                if shorgan_results:
                    print(f"[TLH] SHORGAN: {len(shorgan_results)} positions harvested")
            except Exception as e:
                print(f"[TLH] SHORGAN harvest error: {e}")

        # Harvest from DEE Live (if enabled)
        if DEE_LIVE_TRADING and self.dee_live_api:
            try:
                print("\n[TLH] Scanning DEE-BOT Live...")
                dee_tlh = TaxLossHarvester("DEE-LIVE")
                dee_results = dee_tlh.run_daily_harvest(dry_run=False)
                if dee_results:
                    print(f"[TLH] DEE: {len(dee_results)} positions harvested")
            except Exception as e:
                print(f"[TLH] DEE harvest error: {e}")

        print("\n[TLH] Tax-loss harvesting complete")
        print("=" * 70 + "\n")

    def _validate_research_freshness(self, file_path, trades_file_date):
        """
        Issue #9 fix: Validate that research is fresh enough for execution.
        Warns if trades are from stale research (older than 1 trading day).
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            if trades_file_date != today:
                days_old = (datetime.now() - datetime.strptime(trades_file_date, '%Y-%m-%d')).days
                if days_old >= 1:
                    warning_msg = f"STALE RESEARCH: Trades file is {days_old} day(s) old! Catalyst dates may have passed."
                    print(f"[WARNING] {warning_msg}")
                    self._send_telegram_alert(warning_msg, is_critical=False)

                    # For live accounts, block execution of stale research
                    if 'LIVE' in str(file_path).upper():
                        print("[BLOCKED] Live account trades blocked - research too stale")
                        return False
            return True
        except Exception as e:
            print(f"[WARNING] Could not validate research freshness: {e}")
            return True  # Allow execution if we can't validate

    def find_todays_trades_file(self, file_type="main"):
        """Find today's trades file

        Args:
            file_type: "main" (DEE Paper + SHORGAN Paper), "dee_live", or "shorgan_live"
        """
        today = datetime.now().strftime('%Y-%m-%d')

        # Determine file suffix based on type
        if file_type == "dee_live":
            suffix = "_DEE_LIVE"
        elif file_type == "shorgan_live":
            suffix = "_SHORGAN_LIVE"
        else:
            suffix = ""

        # Check multiple possible locations
        possible_paths = [
            f'docs/TODAYS_TRADES_{today}{suffix}.md',
            f'TODAYS_TRADES_{today}{suffix}.md'
        ]

        # Also check legacy paths for main file
        if file_type == "main":
            possible_paths.extend([
                f'docs/ORDERS_FOR_{today}.md',
                f'ORDERS_FOR_{today}.md'
            ])

        for path in possible_paths:
            full_path = Path(path)
            if full_path.exists():
                return full_path

        # If today's file doesn't exist, look for most recent (main file only)
        if file_type == "main":
            docs_dir = Path('docs')
            if docs_dir.exists():
                trade_files = list(docs_dir.glob('TODAYS_TRADES_*.md')) + list(docs_dir.glob('ORDERS_FOR_*.md'))
                # Exclude live-specific files when looking for main
                trade_files = [f for f in trade_files if '_DEE_LIVE' not in f.name and '_SHORGAN_LIVE' not in f.name]
                if trade_files:
                    # Get most recent file
                    latest_file = max(trade_files, key=lambda x: x.stat().st_mtime)
                    print(f"[WARNING] Using most recent trades file: {latest_file}")
                    return latest_file

        return None

    @staticmethod
    def _parse_dollar_value(text):
        """Parse a dollar value string like '$123.45' into a float, or None."""
        cleaned = text.replace('$', '').replace(',', '')
        if cleaned.replace('.', '').isdigit():
            return float(cleaned)
        return None

    @staticmethod
    def _is_table_data_row(row):
        """Return True if a markdown table row contains data (not header/separator)."""
        return '|' in row and not row.strip().startswith('|--') and '-----' not in row

    def _parse_table_rows(self, section_content, header_pattern, min_columns):
        """
        Extract rows from a legacy markdown table section.

        Args:
            section_content: The markdown text to search within
            header_pattern: Regex pattern for the table header (e.g. '### SELL ORDERS')
            min_columns: Minimum number of columns a row must have

        Returns:
            List of lists, where each inner list is the parsed column values
        """
        table_match = re.search(
            rf'{header_pattern}.*?\n\|.*?\n\|(.*?)(?=\n### |\n## |\Z)',
            section_content, re.DOTALL
        )
        if not table_match:
            return []

        rows = []
        for row in table_match.group(1).strip().split('\n'):
            if self._is_table_data_row(row):
                parts = [p.strip() for p in row.split('|') if p.strip()]
                if len(parts) >= min_columns:
                    rows.append(parts)
        return rows

    def _build_sell_trade(self, parts):
        """Build a sell trade dict from parsed table columns."""
        return {
            'symbol': parts[0],
            'shares': int(parts[1]) if parts[1].isdigit() else 0,
            'limit_price': self._parse_dollar_value(parts[2]),
            'rationale': parts[3] if len(parts) > 3 else ''
        }

    def _build_buy_trade(self, parts):
        """Build a buy trade dict from parsed table columns."""
        return {
            'symbol': parts[0],
            'shares': int(parts[1]) if parts[1].isdigit() else 0,
            'limit_price': self._parse_dollar_value(parts[2]),
            'stop_loss': self._parse_dollar_value(parts[3]) if len(parts) > 3 else None,
            'rationale': parts[4] if len(parts) > 4 else ''
        }

    def parse_trades_file(self, file_path):
        """Parse trades from markdown file"""
        if not file_path or not file_path.exists():
            print(f"[ERROR] Trades file not found: {file_path}")
            return {}, {}

        print(f"[INFO] Parsing trades from: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        dee_trades = {'sell': [], 'buy': []}
        shorgan_trades = {'sell': [], 'buy': [], 'short': []}

        # Find DEE-BOT section (with or without emoji)
        dee_section_match = re.search(r'## (?:🛡️ )?DEE-BOT.*?(?=^## (?:🚀 )?SHORGAN|^## \[|^---|\Z)', content, re.DOTALL | re.MULTILINE)
        if dee_section_match:
            dee_content = dee_section_match.group(0)

            # Parse individual trade entries (#### format)
            trade_pattern = r'####\s+\d+\.\s+(BUY|SELL|HOLD|TRIM)\s+(\w+).*?- \*\*Shares\*\*:\s*(\d+).*?- \*\*Price\*\*:\s*\$?([\d.]+)'
            for match in re.finditer(trade_pattern, dee_content, re.DOTALL):
                action, symbol, shares, price = match.groups()
                if action in ['SELL', 'TRIM']:
                    dee_trades['sell'].append({
                        'symbol': symbol,
                        'shares': int(shares),
                        'limit_price': float(price),
                        'rationale': action
                    })
                elif action == 'BUY':
                    dee_trades['buy'].append({
                        'symbol': symbol,
                        'shares': int(shares),
                        'limit_price': float(price),
                        'stop_loss': None,
                        'rationale': 'DEE-BOT buy'
                    })

            # Also check for table format (legacy)
            for parts in self._parse_table_rows(dee_content, '### SELL ORDERS', min_columns=3):
                dee_trades['sell'].append(self._build_sell_trade(parts))
            for parts in self._parse_table_rows(dee_content, '### BUY ORDERS', min_columns=4):
                dee_trades['buy'].append(self._build_buy_trade(parts))

        # Find SHORGAN-BOT section (with or without emoji)
        shorgan_section_match = re.search(r'## (?:🚀 )?SHORGAN-BOT.*?(?=^## 📋|^## \[|^---|\Z)', content, re.DOTALL | re.MULTILINE)
        if shorgan_section_match:
            shorgan_content = shorgan_section_match.group(0)

            # Parse individual trade entries (#### format)
            trade_pattern = r'####\s+\d+\.\s+(BUY|SHORT|SELL)\s+(\w+).*?- \*\*Shares\*\*:\s*(\d+).*?- \*\*Price\*\*:\s*\$?([\d.]+)'
            for match in re.finditer(trade_pattern, shorgan_content, re.DOTALL):
                action, symbol, shares, price = match.groups()
                if action == 'SHORT':
                    shorgan_trades['short'].append({
                        'symbol': symbol,
                        'shares': int(shares),
                        'limit_price': float(price),
                        'rationale': 'Short position'
                    })
                elif action == 'BUY':
                    shorgan_trades['buy'].append({
                        'symbol': symbol,
                        'shares': int(shares),
                        'limit_price': float(price),
                        'stop_loss': None,
                        'rationale': 'SHORGAN-BOT buy'
                    })
                elif action == 'SELL':
                    shorgan_trades['sell'].append({
                        'symbol': symbol,
                        'shares': int(shares),
                        'limit_price': float(price),
                        'rationale': 'SHORGAN-BOT sell'
                    })

            # Also check for table format (legacy)
            for parts in self._parse_table_rows(shorgan_content, '### SELL ORDERS', min_columns=3):
                shorgan_trades['sell'].append(self._build_sell_trade(parts))
            for parts in self._parse_table_rows(shorgan_content, '### BUY ORDERS', min_columns=4):
                shorgan_trades['buy'].append(self._build_buy_trade(parts))
            for parts in self._parse_table_rows(shorgan_content, '### SHORT SELL', min_columns=4):
                shorgan_trades['short'].append(self._build_buy_trade(parts))

        return dee_trades, shorgan_trades

    def validate_trade(self, api, symbol, shares, side, limit_price=None):
        """Validate trade before execution"""
        try:
            account = api.get_account()
            buying_power = float(account.buying_power)

            # Check if we're using margin (especially for DEE-BOT)
            cash_available = float(account.cash)
            is_dee_bot = (api == self.dee_api)

            validation_errors = []

            # 1. Check market hours (allow extended hours limit orders, block market orders)
            clock = api.get_clock()
            if not clock.is_open:
                # Check if we're in extended hours (pre-market or after-hours)
                in_extended_hours = self.is_extended_hours(api)

                # If no limit price specified, this would be a market order - block it
                if limit_price is None:
                    validation_errors.append(f"Market is closed (market orders not allowed in extended hours)")
                    return False, validation_errors
                elif in_extended_hours and self.enable_extended_hours:
                    # In pre-market or after-hours - limit orders OK
                    print(f"[INFO] Extended hours trading - placing limit order")
                else:
                    # Market is fully closed (outside extended hours)
                    print(f"[INFO] Placing limit order for next trading session")

            # 2. Validate SELL orders
            if side == 'sell':
                try:
                    position = api.get_position(symbol)
                    current_qty = float(position.qty)

                    if current_qty <= 0:
                        validation_errors.append(f"No long position to sell (current: {current_qty})")
                        return False, validation_errors

                    if shares > current_qty:
                        validation_errors.append(f"Trying to sell {shares} but only have {current_qty}")
                        # Adjust to sell only what we have
                        print(f"[ADJUST] Reducing sell qty from {shares} to {int(current_qty)}")
                        shares = int(current_qty)

                except Exception as e:
                    validation_errors.append(f"No position exists to sell")
                    return False, validation_errors

            # 3. Validate BUY orders
            if side == 'buy':
                # Get current price for validation
                try:
                    bars = api.get_latest_bar(symbol)
                    current_price = bars.c  # Close price
                except:
                    current_price = limit_price if limit_price else 100  # Conservative estimate

                required_capital = shares * current_price

                # Check buying power
                if required_capital > buying_power:
                    validation_errors.append(f"Insufficient buying power: need ${required_capital:.2f}, have ${buying_power:.2f}")
                    return False, validation_errors

                # DEE-BOT specific: Prevent margin usage
                if is_dee_bot and cash_available < required_capital:
                    validation_errors.append(f"DEE-BOT would use margin: cash ${cash_available:.2f}, need ${required_capital:.2f}")
                    # Calculate max shares we can buy with cash only
                    max_shares = int(cash_available / current_price)
                    if max_shares > 0:
                        print(f"[ADJUST] DEE-BOT: Reducing buy from {shares} to {max_shares} shares (cash-only)")
                        shares = max_shares
                    else:
                        return False, validation_errors

                # Check position concentration (max 10% for SHORGAN, 8% for DEE)
                # For SHORGAN Live, use invested capital ($3K) not current equity
                is_shorgan_live = (api == self.shorgan_live_api and SHORGAN_LIVE_TRADING)
                if is_shorgan_live:
                    portfolio_value = SHORGAN_CAPITAL  # Use invested capital, not equity
                else:
                    portfolio_value = float(account.portfolio_value)
                max_position_pct = 0.08 if is_dee_bot else 0.10
                max_position_value = portfolio_value * max_position_pct

                if required_capital > max_position_value:
                    validation_errors.append(f"Position too large: ${required_capital:.2f} exceeds {max_position_pct*100}% limit (${max_position_value:.2f})")
                    # Adjust shares to fit within limit
                    max_shares = int(max_position_value / current_price)
                    if max_shares > 0:
                        print(f"[ADJUST] Reducing position from {shares} to {max_shares} shares (position limit)")
                        shares = max_shares
                    else:
                        return False, validation_errors

            # 4. Check for existing opposite orders
            try:
                orders = api.list_orders(status='open', symbols=[symbol])
                for order in orders:
                    if order.side != side:
                        validation_errors.append(f"Conflicting {order.side} order already exists")
                        return False, validation_errors
            except:
                pass  # Continue if we can't check orders

            if validation_errors:
                return False, validation_errors

            # Return validated (possibly adjusted) share count
            return True, shares

        except Exception as e:
            return False, [f"Validation error: {str(e)}"]

    def execute_trade(self, api, trade_info, side):
        """Execute a single trade with pre-validation"""
        try:
            symbol = trade_info['symbol']
            shares = trade_info['shares']
            limit_price = trade_info.get('limit_price')

            if shares <= 0:
                print(f"[SKIP] {symbol}: Invalid share count ({shares})")
                return None

            # SHORGAN-BOT LIVE ACCOUNT: Adjust position size BEFORE validation
            if api == self.shorgan_live_api and SHORGAN_LIVE_TRADING and limit_price:
                original_shares = shares
                shares = self.calculate_shorgan_position_size(limit_price, shares)
                if shares == 0:
                    print(f"[SKIP] {symbol}: Position too small for $3K account")
                    return None
                if shares != original_shares:
                    print(f"[ADJUST] SHORGAN-BOT Live: {original_shares} -> {shares} shares (${shares * limit_price:.2f})")
                    trade_info['shares'] = shares  # Update trade info

            # PRE-EXECUTION VALIDATION
            is_valid, result = self.validate_trade(api, symbol, shares, side, limit_price)

            if not is_valid:
                print(f"[VALIDATION FAILED] {symbol}: {', '.join(result)}")
                self.failed_trades.append({
                    'symbol': symbol,
                    'shares': shares,
                    'side': side,
                    'error': f"Validation failed: {', '.join(result)}",
                    'timestamp': datetime.now().isoformat()
                })
                return None

            # If validation returned adjusted share count, use it
            if isinstance(result, int):
                original_shares = shares
                shares = result
                if shares != original_shares:
                    print(f"[ADJUSTED] {symbol}: Changed from {original_shares} to {shares} shares")

            # DEE-BOT LONG-ONLY ENFORCEMENT
            if api == self.dee_api and self.dee_bot_long_only and side == 'sell':
                # Only allow sells if we have an existing long position to close
                try:
                    position = api.get_position(symbol)
                    if float(position.qty) < 0:  # This is a short position
                        print(f"[BLOCKED] {symbol}: DEE-BOT cannot sell short (LONG-ONLY strategy)")
                        self.failed_trades.append({
                            'symbol': symbol,
                            'shares': shares,
                            'side': side,
                            'error': 'DEE-BOT is LONG-ONLY - shorting not allowed',
                            'timestamp': datetime.now().isoformat()
                        })
                        return None
                except:
                    # No position exists - this would create a short
                    if side == 'sell':
                        print(f"[BLOCKED] {symbol}: DEE-BOT cannot initiate short positions (LONG-ONLY)")
                        self.failed_trades.append({
                            'symbol': symbol,
                            'shares': shares,
                            'side': side,
                            'error': 'DEE-BOT is LONG-ONLY - cannot initiate shorts',
                            'timestamp': datetime.now().isoformat()
                        })
                        return None

            # REGULATORY COMPLIANCE CHECK
            if COMPLIANCE_AVAILABLE:
                # Determine account info for compliance check
                account_name = "DEE-BOT" if api == self.dee_api else "SHORGAN-LIVE"
                try:
                    account = api.get_account()
                    account_value = float(account.portfolio_value)
                    is_margin = account.account_type == 'margin'
                except:
                    account_value = SHORGAN_CAPITAL if api == self.shorgan_live_api else 100000
                    is_margin = False

                is_compliant, compliance_msg = check_trade_compliance(
                    symbol=symbol,
                    action=side.upper(),
                    account=account_name,
                    account_value=account_value,
                    is_margin=is_margin
                )

                if not is_compliant:
                    print(f"[COMPLIANCE BLOCK] {symbol}: {compliance_msg}")
                    self.failed_trades.append({
                        'symbol': symbol,
                        'shares': shares,
                        'side': side,
                        'error': f"Regulatory compliance: {compliance_msg}",
                        'timestamp': datetime.now().isoformat()
                    })
                    return None

                if "WARNING" in compliance_msg:
                    print(f"[COMPLIANCE WARNING] {symbol}: {compliance_msg}")

            # Determine order type
            order_type = 'limit' if limit_price else 'market'

            # Check if we're in extended hours
            in_extended_hours = self.is_extended_hours(api)

            order_params = {
                'symbol': symbol,
                'qty': shares,
                'side': side,
                'type': order_type,
                'time_in_force': 'day'
            }

            if order_type == 'limit':
                order_params['limit_price'] = str(limit_price)

            # Enable extended hours trading if applicable
            if in_extended_hours and self.enable_extended_hours and order_type == 'limit':
                order_params['extended_hours'] = True
                session_type = "PRE-MARKET" if datetime.now().hour < 12 else "AFTER-HOURS"
                print(f"[{session_type}] {side.upper()} {shares} {symbol} @ ${limit_price}")
            else:
                print(f"[EXECUTING] {side.upper()} {shares} {symbol} @ {f'${limit_price}' if limit_price else 'market'}")

            # Check circuit breaker before submitting (if available)
            if CORE_UTILS_AVAILABLE and alpaca_circuit.state == "OPEN":
                raise Exception(f"Alpaca circuit breaker OPEN - too many recent failures")

            # Submit order with retry logic (if available)
            if CORE_UTILS_AVAILABLE:
                @retry_with_backoff(max_attempts=3, initial_delay=1.0, backoff_factor=2.0)
                def submit_with_retry():
                    return api.submit_order(**order_params)
                order = submit_with_retry()
            else:
                order = api.submit_order(**order_params)

            # Record success in circuit breaker
            if CORE_UTILS_AVAILABLE:
                alpaca_circuit.record_success()

            # Determine bot name for stop-loss and logging
            bot_name = "DEE-BOT" if api == self.dee_api else "SHORGAN-BOT"

            # Verify order fill (if available and market order)
            fill_status = None
            fill_price = None
            if CORE_UTILS_AVAILABLE and order_type == 'market':
                try:
                    verifier = OrderVerifier(api, max_wait_seconds=30)
                    result = verifier.verify_order(order.id)
                    fill_status = result.status.value
                    fill_price = result.filled_price
                    if result.status == FillStatus.FILLED:
                        logger.info(f"[VERIFIED] {symbol} filled @ ${fill_price}")
                    elif result.status == FillStatus.PARTIAL:
                        logger.warning(f"[PARTIAL] {symbol} partially filled: {result.filled_qty}/{shares}")
                except Exception as e:
                    logger.warning(f"[VERIFY ERROR] Could not verify {symbol}: {e}")

            trade_record = {
                'symbol': symbol,
                'shares': shares,
                'side': side,
                'order_type': order_type,
                'limit_price': limit_price,
                'order_id': order.id,
                'timestamp': datetime.now().isoformat(),
                'status': fill_status or 'submitted',
                'fill_price': fill_price,
                'extended_hours': order_params.get('extended_hours', False),
                'rationale': trade_info.get('rationale', ''),
                'bot': bot_name
            }

            self.executed_trades.append(trade_record)
            print(f"[SUCCESS] Order ID: {order.id}" + (f" - Filled @ ${fill_price}" if fill_price else ""))

            # Record trade for regulatory compliance tracking
            if COMPLIANCE_AVAILABLE:
                try:
                    compliance_checker = RegulatoryComplianceChecker()
                    account_name = "DEE-BOT" if api == self.dee_api else "SHORGAN-LIVE"
                    compliance_checker.record_trade(TradeRecord(
                        symbol=symbol,
                        action=side.upper(),
                        qty=shares,
                        price=limit_price or 0,
                        timestamp=datetime.now(),
                        account=account_name,
                        order_id=order.id
                    ))
                except Exception as e:
                    print(f"[WARNING] Failed to record trade for compliance: {e}")

            return order

        except Exception as e:
            # Record failure in circuit breaker
            if CORE_UTILS_AVAILABLE:
                try:
                    alpaca_circuit.record_failure(e)
                except Exception:
                    pass  # Don't let circuit breaker errors mask the real error

            error_record = {
                'symbol': trade_info['symbol'],
                'shares': trade_info['shares'],
                'side': side,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.failed_trades.append(error_record)
            logger.error(f"[ERROR] Failed to {side} {trade_info['symbol']}: {e}")
            return None

    def _send_telegram_alert(self, message, is_critical=False):
        """Send Telegram alert for important events (Issue #6 fix)"""
        try:
            import requests
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
            if not bot_token or not chat_id:
                return False

            prefix = "[CRITICAL] " if is_critical else "[ALERT] "
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            response = requests.post(url, data={
                "chat_id": chat_id,
                "text": prefix + message,
                "parse_mode": "HTML"
            }, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"[WARNING] Failed to send Telegram alert: {e}")
            return False

    def place_stop_loss_order(self, api, symbol, shares, entry_price, bot_name="DEE-BOT", stop_loss_pct=None):
        """
        Place a GTC stop-loss order after a BUY fills.
        Stop-loss percentages:
        - DEE-BOT: 11% (defensive S&P 100 strategy)
        - SHORGAN: 18% (aggressive catalyst plays)
        """
        try:
            if stop_loss_pct:
                stop_pct = stop_loss_pct
            elif bot_name == "DEE-BOT" or bot_name == "DEE-BOT-LIVE":
                stop_pct = 0.11  # 11% stop for defensive portfolio
            else:
                stop_pct = 0.18  # 18% stop for aggressive catalyst plays

            stop_price = round(entry_price * (1 - stop_pct), 2)
            print(f"    [STOP-LOSS] Placing GTC stop for {symbol}: {shares} shares @ ${stop_price:.2f} ({stop_pct*100:.0f}% below entry)")

            stop_order = api.submit_order(
                symbol=symbol,
                qty=shares,
                side='sell',
                type='stop',
                stop_price=stop_price,
                time_in_force='gtc'
            )
            print(f"    [STOP-LOSS] SUCCESS: Order {stop_order.id} placed for {symbol}")
            return stop_order
        except Exception as e:
            error_msg = f"STOP LOSS FAILED: {bot_name} - {symbol} ({shares} shares @ ${entry_price:.2f})\nError: {str(e)}"
            print(f"    [STOP-LOSS] WARNING: Failed to place stop for {symbol}: {e}")
            # Send Telegram alert for stop loss failure (Issue #6 fix)
            self._send_telegram_alert(error_msg, is_critical=True)
            return None

    def place_stop_losses_for_executed_buys(self, api, bot_name="DEE-BOT", stop_loss_pct=None):
        """
        Place stop-loss orders for all successfully executed BUY orders in this session.
        Called after all trades are executed.
        """
        buy_trades = [t for t in self.executed_trades if t.get('side') == 'buy' and t.get('bot') == bot_name]

        if not buy_trades:
            print(f"\n[STOP-LOSS] No BUY orders executed for {bot_name} - skipping stop placement")
            return

        print(f"\n{'='*60}")
        print(f"PLACING STOP-LOSS ORDERS FOR {bot_name}")
        print(f"{'='*60}")

        stops_placed = 0
        for trade in buy_trades:
            symbol = trade.get('symbol')
            shares = trade.get('shares')
            # Use limit_price as entry estimate (actual fill may differ slightly)
            entry_price = trade.get('limit_price') or trade.get('fill_price', 0)

            if entry_price > 0 and shares > 0:
                result = self.place_stop_loss_order(api, symbol, shares, entry_price, bot_name, stop_loss_pct)
                if result:
                    stops_placed += 1
                time.sleep(0.5)  # Rate limiting

        print(f"\n[STOP-LOSS] Placed {stops_placed}/{len(buy_trades)} stop-loss orders for {bot_name}")

    def check_market_status(self):
        """Check if market is open or in extended hours"""
        try:
            clock = self.dee_api.get_clock()
            if clock.is_open:
                print("[INFO] Market is OPEN - Regular trading hours")
                return 'open'
            else:
                # Check if we're in extended hours
                if self.is_extended_hours():
                    import pytz
                    eastern = pytz.timezone('US/Eastern')
                    now_et = datetime.now(eastern)
                    if now_et.hour < 12:
                        print("[INFO] Market is in PRE-MARKET session (4:00 AM - 9:30 AM ET)")
                        print("[INFO] Extended hours trading ENABLED - limit orders only")
                    else:
                        print("[INFO] Market is in AFTER-HOURS session (4:00 PM - 8:00 PM ET)")
                        print("[INFO] Extended hours trading ENABLED - limit orders only")
                    return 'extended'
                else:
                    next_open = clock.next_open
                    print(f"[INFO] Market is CLOSED. Opens at {next_open}")
                    return 'closed'
        except Exception as e:
            print(f"[WARNING] Could not check market status: {e}")
            return 'unknown'  # Proceed anyway

    def execute_all_trades(self, max_retries=2):
        """Execute all trades from today's file with retry logic"""
        print("=" * 80)
        print(f"DAILY TRADE EXECUTION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # Find and parse trades file
        trades_file = self.find_todays_trades_file()
        if not trades_file:
            print("[WARNING] No trades file found for today, attempting to generate...")
            # Try to generate trades file automatically
            try:
                from generate_todays_trades import AutomatedTradeGenerator
                generator = AutomatedTradeGenerator()
                trades_file = generator.run()
                if not trades_file:
                    print("[ERROR] Could not generate trades file")
                    return False
            except Exception as e:
                print(f"[ERROR] Failed to generate trades: {e}")
                return False

        dee_trades, shorgan_trades = self.parse_trades_file(trades_file)

        # Check market status
        self.check_market_status()

        # Run tax-loss harvesting BEFORE regular trades (for live accounts)
        if TLH_AVAILABLE:
            self._run_tax_loss_harvesting()

        total_trades = (len(dee_trades['sell']) + len(dee_trades['buy']) +
                       len(shorgan_trades['sell']) + len(shorgan_trades['buy']) +
                       len(shorgan_trades['short']))

        if total_trades == 0:
            print("[INFO] No trades found in file")
            return True

        print(f"[INFO] Found {total_trades} total trades to execute")
        print()

        # Track trades for retry
        retry_queue = []

        # Execute DEE-BOT trades
        if dee_trades['sell'] or dee_trades['buy']:
            print("-" * 40)
            print("DEE-BOT TRADES")
            print("-" * 40)

            # Execute sells first
            for trade in dee_trades['sell']:
                result = self.execute_trade(self.dee_api, trade, 'sell')
                if result is None:
                    retry_queue.append(('dee', trade, 'sell'))
                time.sleep(1)  # Rate limiting

            # Execute buys
            for trade in dee_trades['buy']:
                result = self.execute_trade(self.dee_api, trade, 'buy')
                if result is None:
                    retry_queue.append(('dee', trade, 'buy'))
                time.sleep(1)

        # Execute DEE-BOT LIVE trades (if enabled)
        if DEE_LIVE_TRADING and self.dee_live_api:
            # Find and parse DEE Live file
            dee_live_file = self.find_todays_trades_file(file_type="dee_live")
            if dee_live_file:
                # Issue #9 fix: Validate research freshness for live trades
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', str(dee_live_file))
                file_date = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
                if not self._validate_research_freshness(dee_live_file, file_date):
                    print("[SKIPPED] DEE Live trades skipped - stale research")
                else:
                    dee_live_trades, _ = self.parse_trades_file(dee_live_file)

                    if dee_live_trades['sell'] or dee_live_trades['buy']:
                        print("-" * 40)
                        print("DEE-BOT LIVE TRADES (REAL MONEY)")
                        print("-" * 40)

                        # Calculate total trade value for confirmation
                        total_trades = len(dee_live_trades['sell']) + len(dee_live_trades['buy'])
                        total_value = sum(t.get('shares', 0) * t.get('limit_price', 0) for t in dee_live_trades['buy'])

                        # Require confirmation for live trades (Issue #4 fix)
                        if not self._confirm_live_trades("DEE-BOT", total_trades, total_value):
                            print("[SKIPPED] DEE Live trades skipped - user declined confirmation")
                        # Check circuit breakers before executing
                        elif not self.check_dee_live_daily_loss_limit():
                            print("[CIRCUIT BREAKER] Skipping all DEE Live trades due to daily loss limit")
                        elif not self.check_dee_live_position_count_limit():
                            print("[POSITION LIMIT] Skipping new DEE Live buy trades")
                            # Still execute sells
                            for trade in dee_live_trades['sell']:
                                result = self.execute_trade(self.dee_live_api, trade, 'sell')
                                if result is None:
                                    retry_queue.append(('dee_live', trade, 'sell'))
                                time.sleep(1)
                        else:
                            # Execute sells first
                            for trade in dee_live_trades['sell']:
                                result = self.execute_trade(self.dee_live_api, trade, 'sell')
                                if result is None:
                                    retry_queue.append(('dee_live', trade, 'sell'))
                                time.sleep(1)

                            # Execute buys with position sizing
                            trades_executed = 0
                            for trade in dee_live_trades['buy']:
                                if trades_executed >= DEE_MAX_TRADES_PER_DAY:
                                    print(f"[LIMIT] Reached max trades per day ({DEE_MAX_TRADES_PER_DAY})")
                                    break

                                # Re-check circuit breaker BEFORE each trade (Issue #5 fix)
                                if not self.check_dee_live_daily_loss_limit():
                                    print("[CIRCUIT BREAKER] Stopping DEE Live - daily loss limit hit during execution")
                                    break

                                # Re-check position limit BEFORE each trade (Issue #3 fix)
                                if not self.check_dee_live_position_count_limit():
                                    print("[POSITION LIMIT] Stopping DEE Live - max positions reached during execution")
                                    break

                                # Apply position sizing
                                price = trade.get('limit_price', 50.0)
                                original_shares = trade.get('shares', 10)
                                adjusted_shares = self.calculate_dee_live_position_size(price, original_shares)

                                if adjusted_shares > 0:
                                    trade['shares'] = adjusted_shares
                                    result = self.execute_trade(self.dee_live_api, trade, 'buy')
                                    if result is None:
                                        retry_queue.append(('dee_live', trade, 'buy'))
                                    else:
                                        trades_executed += 1
                                time.sleep(1)
            else:
                print("[INFO] No DEE-BOT Live trades file found")

        # Execute SHORGAN-BOT PAPER trades
        if shorgan_trades['sell'] or shorgan_trades['buy'] or shorgan_trades['short']:
            print("-" * 40)
            print("SHORGAN-BOT PAPER TRADES")
            print("-" * 40)

            # Execute sells first
            for trade in shorgan_trades['sell']:
                result = self.execute_trade(self.shorgan_paper_api, trade, 'sell')
                if result is None:
                    retry_queue.append(('shorgan_paper', trade, 'sell'))
                time.sleep(1)

            # Execute buys
            for trade in shorgan_trades['buy']:
                result = self.execute_trade(self.shorgan_paper_api, trade, 'buy')
                if result is None:
                    retry_queue.append(('shorgan_paper', trade, 'buy'))
                time.sleep(1)

            # Execute shorts (Paper account can short)
            for trade in shorgan_trades['short']:
                result = self.execute_trade(self.shorgan_paper_api, trade, 'sell')  # Short = sell
                if result is None:
                    retry_queue.append(('shorgan_paper', trade, 'sell'))
                time.sleep(1)

        # Execute SHORGAN-BOT LIVE trades (if enabled)
        if SHORGAN_LIVE_TRADING and self.shorgan_live_api:
            # Find and parse SHORGAN Live file
            shorgan_live_file = self.find_todays_trades_file(file_type="shorgan_live")
            if shorgan_live_file:
                # Issue #9 fix: Validate research freshness for live trades
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', str(shorgan_live_file))
                file_date = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
                if not self._validate_research_freshness(shorgan_live_file, file_date):
                    print("[SKIPPED] SHORGAN Live trades skipped - stale research")
                else:
                    _, shorgan_live_trades = self.parse_trades_file(shorgan_live_file)

                    if shorgan_live_trades['sell'] or shorgan_live_trades['buy']:
                        print("-" * 40)
                        print("SHORGAN-BOT LIVE TRADES (REAL MONEY)")
                        print("-" * 40)

                        # Calculate total trade value for confirmation
                        total_trades = len(shorgan_live_trades['sell']) + len(shorgan_live_trades['buy'])
                        total_value = sum(t.get('shares', 0) * t.get('limit_price', 0) for t in shorgan_live_trades['buy'])

                        # Require confirmation for live trades (Issue #4 fix)
                        if not self._confirm_live_trades("SHORGAN-BOT", total_trades, total_value):
                            print("[SKIPPED] SHORGAN Live trades skipped - user declined confirmation")
                        # Check circuit breakers before executing
                        elif not self.check_shorgan_daily_loss_limit():
                            print("[CIRCUIT BREAKER] Skipping all SHORGAN Live trades due to daily loss limit")
                        elif not self.check_shorgan_position_count_limit():
                            print("[POSITION LIMIT] Skipping new SHORGAN Live buy trades")
                            # Still execute sells
                            for trade in shorgan_live_trades['sell']:
                                result = self.execute_trade(self.shorgan_live_api, trade, 'sell')
                                if result is None:
                                    retry_queue.append(('shorgan_live', trade, 'sell'))
                                time.sleep(1)
                        else:
                            # Execute sells first
                            for trade in shorgan_live_trades['sell']:
                                result = self.execute_trade(self.shorgan_live_api, trade, 'sell')
                                if result is None:
                                    retry_queue.append(('shorgan_live', trade, 'sell'))
                                time.sleep(1)

                            # Execute buys with position sizing
                            trades_executed = 0
                            for trade in shorgan_live_trades['buy']:
                                if trades_executed >= SHORGAN_MAX_TRADES_PER_DAY:
                                    print(f"[LIMIT] Reached max trades per day ({SHORGAN_MAX_TRADES_PER_DAY})")
                                    break

                                # Re-check circuit breaker BEFORE each trade (Issue #5 fix)
                                if not self.check_shorgan_daily_loss_limit():
                                    print("[CIRCUIT BREAKER] Stopping - daily loss limit hit during execution")
                                    break

                                # Re-check position limit BEFORE each trade (Issue #3 fix)
                                if not self.check_shorgan_position_count_limit():
                                    print("[POSITION LIMIT] Stopping - max positions reached during execution")
                                    break

                                result = self.execute_trade(self.shorgan_live_api, trade, 'buy')
                                if result is None:
                                    retry_queue.append(('shorgan_live', trade, 'buy'))
                                else:
                                    trades_executed += 1
                                time.sleep(1)
            else:
                print("[INFO] No SHORGAN-BOT Live trades file found")

        # Retry failed trades if any (Issue #7 fix - limit total retries)
        retry_attempts = {}  # Track retry attempts per symbol
        if retry_queue and max_retries > 0:
            print()
            print("-" * 40)
            print(f"RETRYING {len(retry_queue)} FAILED TRADES (max {MAX_RETRY_ATTEMPTS} attempts each)")
            print("-" * 40)
            time.sleep(5)  # Wait before retry

            for bot_type, trade, side in retry_queue:
                symbol = trade['symbol']
                retry_key = f"{symbol}_{side}"

                # Check if we've exceeded max retries for this symbol (Issue #7 fix)
                if retry_key not in retry_attempts:
                    retry_attempts[retry_key] = 0
                retry_attempts[retry_key] += 1

                if retry_attempts[retry_key] > MAX_RETRY_ATTEMPTS:
                    print(f"[MAX RETRIES] {symbol} - exceeded {MAX_RETRY_ATTEMPTS} attempts, giving up")
                    continue

                print(f"\n[RETRY {retry_attempts[retry_key]}/{MAX_RETRY_ATTEMPTS}] {side.upper()} {trade['shares']} {trade['symbol']}")
                if bot_type == 'dee':
                    api = self.dee_api
                elif bot_type == 'dee_live':
                    api = self.dee_live_api
                elif bot_type == 'shorgan_paper':
                    api = self.shorgan_paper_api
                elif bot_type == 'shorgan_live':
                    api = self.shorgan_live_api
                else:
                    api = self.shorgan_paper_api  # Default to paper

                # Re-validate and retry with adjusted parameters
                result = self.execute_trade(api, trade, side)
                if result:
                    print(f"[RETRY SUCCESS] {trade['symbol']}")
                    # Remove from failed trades if it succeeded on retry
                    self.failed_trades = [
                        f for f in self.failed_trades
                        if f['symbol'] != trade['symbol'] or f['side'] != side
                    ]
                else:
                    print(f"[RETRY FAILED] {trade['symbol']} - attempt {retry_attempts[retry_key]}/{MAX_RETRY_ATTEMPTS}")
                time.sleep(1)

        # Summary
        print()
        print("=" * 80)
        print("EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Successful trades: {len(self.executed_trades)}")
        print(f"Failed trades: {len(self.failed_trades)}")

        if self.executed_trades:
            print("\nExecuted Trades:")
            for trade in self.executed_trades:
                price_str = f" @ ${trade['limit_price']}" if trade['limit_price'] else ""
                print(f"  {trade['side'].upper()} {trade['shares']} {trade['symbol']}{price_str} - {trade['order_id']}")

        if self.failed_trades:
            print("\nFailed Trades:")
            for trade in self.failed_trades:
                print(f"  {trade['side'].upper()} {trade['shares']} {trade['symbol']} - {trade['error']}")

        # Place stop-loss orders for all executed BUY orders
        print("\n" + "=" * 80)
        print("AUTOMATIC STOP-LOSS PLACEMENT")
        print("=" * 80)
        self.place_stop_losses_for_executed_buys(self.dee_api, "DEE-BOT")
        if DEE_LIVE_TRADING and self.dee_live_api:
            self.place_stop_losses_for_executed_buys(self.dee_live_api, "DEE-BOT-LIVE", stop_loss_pct=DEE_STOP_LOSS_PCT)
        self.place_stop_losses_for_executed_buys(self.shorgan_paper_api, "SHORGAN-BOT")
        if SHORGAN_LIVE_TRADING and self.shorgan_live_api:
            self.place_stop_losses_for_executed_buys(self.shorgan_live_api, "SHORGAN-BOT-LIVE")

        # Save execution log
        log_data = {
            'execution_time': datetime.now().isoformat(),
            'trades_file': str(trades_file),
            'executed_trades': self.executed_trades,
            'failed_trades': self.failed_trades
        }

        log_file = f"scripts-and-data/trade-logs/daily_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)

        print(f"\nExecution log saved to: {log_file}")

        return len(self.failed_trades) == 0

def sync_positions_before_trading():
    """Sync position files from Alpaca before trading to prevent mismatches"""
    try:
        from scripts.portfolio.sync_positions import sync_positions
        print("[SYNC] Syncing positions from Alpaca before trading...")
        positions_count, orders_count = sync_positions()
        print(f"[SYNC] Synced {positions_count} positions, {orders_count} open orders")
        return True
    except Exception as e:
        print(f"[SYNC] Warning: Position sync failed: {e}")
        return False

def main():
    # ALWAYS sync positions before trading to prevent mismatch errors
    sync_positions_before_trading()
    
    executor = DailyTradeExecutor()
    success = executor.execute_all_trades()

    # Send compliance summary to Telegram
    try:
        from scripts.automation.regulatory_compliance import send_compliance_summary_telegram

        # Get account values
        accounts_data = []

        # DEE-BOT (Paper - over $25K, unrestricted)
        try:
            dee_account = executor.dee_api.get_account()
            accounts_data.append({
                'name': 'DEE-BOT',
                'value': float(dee_account.portfolio_value),
                'is_margin': False
            })
        except Exception as e:
            print(f"[WARNING] Could not get DEE-BOT account: {e}")

        # SHORGAN-LIVE (Real money - under $25K, restricted)
        if SHORGAN_LIVE_TRADING and executor.shorgan_live_api:
            try:
                shorgan_account = executor.shorgan_live_api.get_account()
                accounts_data.append({
                    'name': 'SHORGAN-LIVE',
                    'value': float(shorgan_account.portfolio_value),
                    'is_margin': True
                })
            except Exception as e:
                print(f"[WARNING] Could not get SHORGAN-LIVE account: {e}")

        if accounts_data:
            send_compliance_summary_telegram(accounts_data)

    except Exception as e:
        print(f"[WARNING] Compliance summary failed: {e}")

    if success:
        print("\n[SUCCESS] All trades executed successfully")
        return 0
    else:
        print("\n[WARNING] Some trades failed - check logs")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)