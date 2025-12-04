#!/usr/bin/env python3
"""
Daily Trade Execution System
Automatically executes trades from TODAYS_TRADES markdown file
"""

import os
import re
import sys
import json
import time
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add path for logging
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import regulatory compliance checker
try:
    from scripts.automation.regulatory_compliance import RegulatoryComplianceChecker, check_trade_compliance, TradeRecord
    COMPLIANCE_AVAILABLE = True
except ImportError:
    COMPLIANCE_AVAILABLE = False
    print("[WARNING] Regulatory compliance module not available")

# Alpaca API Configuration (from environment variables)
DEE_BOT_CONFIG = {
    'API_KEY': os.getenv('ALPACA_API_KEY_DEE'),
    'SECRET_KEY': os.getenv('ALPACA_SECRET_KEY_DEE'),
    'BASE_URL': 'https://paper-api.alpaca.markets'  # Keep DEE on paper
}

# ⚠️ SHORGAN-BOT LIVE TRADING CONFIGURATION ⚠️
SHORGAN_BOT_CONFIG = {
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

# Validate API keys are loaded
if not DEE_BOT_CONFIG['API_KEY'] or not DEE_BOT_CONFIG['SECRET_KEY']:
    raise ValueError("DEE-BOT API keys not found in environment variables. Check your .env file.")
if not SHORGAN_BOT_CONFIG['API_KEY'] or not SHORGAN_BOT_CONFIG['SECRET_KEY']:
    raise ValueError("SHORGAN-BOT LIVE API keys not found in environment variables. Check your .env file.")

class DailyTradeExecutor:
    def __init__(self):
        self.dee_api = tradeapi.REST(
            DEE_BOT_CONFIG['API_KEY'],
            DEE_BOT_CONFIG['SECRET_KEY'],
            DEE_BOT_CONFIG['BASE_URL'],
            api_version='v2'
        )

        self.shorgan_api = tradeapi.REST(
            SHORGAN_BOT_CONFIG['API_KEY'],
            SHORGAN_BOT_CONFIG['SECRET_KEY'],
            SHORGAN_BOT_CONFIG['BASE_URL'],
            api_version='v2'
        )

        self.executed_trades = []
        self.failed_trades = []

        # DEE-BOT is LONG-ONLY - no shorting allowed
        self.dee_bot_long_only = True

        # Extended hours trading configuration
        self.enable_extended_hours = True  # Allow pre-market and after-hours trading

        # Initialize SHORGAN tracking
        self._init_shorgan_tracking()

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

    def _init_shorgan_tracking(self):
        """Initialize SHORGAN daily performance tracking"""
        # Track SHORGAN daily performance for circuit breaker
        self.shorgan_starting_equity = None
        if SHORGAN_LIVE_TRADING:
            try:
                account = self.shorgan_api.get_account()
                self.shorgan_starting_equity = float(account.last_equity)
                print(f"\n[LIVE] SHORGAN-BOT LIVE TRADING ACTIVE")
                print(f"Starting Equity: ${self.shorgan_starting_equity:,.2f}")
                print(f"Daily Loss Limit: ${SHORGAN_MAX_DAILY_LOSS:.2f}")
                print(f"Max Trades Today: {SHORGAN_MAX_TRADES_PER_DAY}")
            except Exception as e:
                print(f"[ERROR] Could not get SHORGAN starting equity: {e}")

    def check_shorgan_daily_loss_limit(self):
        """Circuit breaker: Stop trading if daily loss exceeds limit"""
        if not SHORGAN_LIVE_TRADING or self.shorgan_starting_equity is None:
            return True

        try:
            account = self.shorgan_api.get_account()
            current_equity = float(account.equity)
            daily_pnl = current_equity - self.shorgan_starting_equity

            if daily_pnl < -SHORGAN_MAX_DAILY_LOSS:
                print(f"\n[CIRCUIT BREAKER] TRIGGERED - SHORGAN-BOT")
                print(f"Daily Loss: ${-daily_pnl:.2f}")
                print(f"Loss Limit: ${SHORGAN_MAX_DAILY_LOSS:.2f}")
                print(f"[ALERT] STOPPING ALL SHORGAN TRADING FOR TODAY")
                return False

            print(f"[OK] Daily P&L Check: ${daily_pnl:+.2f} (Limit: -${SHORGAN_MAX_DAILY_LOSS:.2f})")
            return True
        except Exception as e:
            print(f"[ERROR] Could not check daily loss limit: {e}")
            return False  # Err on side of caution

    def check_shorgan_position_count_limit(self):
        """Don't exceed max concurrent positions"""
        if not SHORGAN_LIVE_TRADING:
            return True

        try:
            positions = self.shorgan_api.list_positions()
            position_count = len(positions)

            if position_count >= SHORGAN_MAX_POSITIONS:
                print(f"\n[WARNING] Position limit reached: {position_count}/{SHORGAN_MAX_POSITIONS}")
                print(f"Cannot open new positions until existing ones close")
                return False

            print(f"[OK] Position Count: {position_count}/{SHORGAN_MAX_POSITIONS}")
            return True
        except Exception as e:
            print(f"[ERROR] Could not check position count: {e}")
            return False

    def calculate_shorgan_position_size(self, price, shares_recommended):
        """Calculate safe position size for $3,000 live account"""
        if not SHORGAN_LIVE_TRADING:
            return shares_recommended  # Use recommended size for paper

        # Calculate affordable shares based on position size limit
        max_shares = int(SHORGAN_MAX_POSITION_SIZE / price)

        # Don't buy if position would be too small
        if max_shares * price < SHORGAN_MIN_POSITION_SIZE:
            print(f"[SKIP] Position too small: ${max_shares * price:.2f} < ${SHORGAN_MIN_POSITION_SIZE}")
            return 0

        # Use the smaller of recommended or max affordable
        final_shares = min(shares_recommended, max_shares)
        position_value = final_shares * price

        print(f"[INFO] Position Size: {final_shares} shares @ ${price:.2f} = ${position_value:.2f}")
        return final_shares

    def find_todays_trades_file(self):
        """Find today's trades file"""
        today = datetime.now().strftime('%Y-%m-%d')

        # Check multiple possible locations
        possible_paths = [
            f'docs/TODAYS_TRADES_{today}.md',
            f'docs/ORDERS_FOR_{today}.md',
            f'TODAYS_TRADES_{today}.md',
            f'ORDERS_FOR_{today}.md'
        ]

        for path in possible_paths:
            full_path = Path(path)
            if full_path.exists():
                return full_path

        # If today's file doesn't exist, look for most recent
        docs_dir = Path('docs')
        if docs_dir.exists():
            trade_files = list(docs_dir.glob('TODAYS_TRADES_*.md')) + list(docs_dir.glob('ORDERS_FOR_*.md'))
            if trade_files:
                # Get most recent file
                latest_file = max(trade_files, key=lambda x: x.stat().st_mtime)
                print(f"[WARNING] Using most recent trades file: {latest_file}")
                return latest_file

        return None

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
            sell_table_match = re.search(r'### SELL ORDERS.*?\n\|.*?\n\|(.*?)(?=\n### |\n## |\Z)', dee_content, re.DOTALL)
            if sell_table_match:
                sell_rows = sell_table_match.group(1).strip().split('\n')
                for row in sell_rows:
                    if '|' in row and not row.strip().startswith('|--') and not '-----' in row:
                        parts = [p.strip() for p in row.split('|') if p.strip()]
                        if len(parts) >= 3:
                            dee_trades['sell'].append({
                                'symbol': parts[0],
                                'shares': int(parts[1]) if parts[1].isdigit() else 0,
                                'limit_price': float(parts[2].replace('$', '')) if parts[2].replace('$', '').replace('.', '').isdigit() else None,
                                'rationale': parts[3] if len(parts) > 3 else ''
                            })

            buy_table_match = re.search(r'### BUY ORDERS.*?\n\|.*?\n\|(.*?)(?=\n### |\n## |\Z)', dee_content, re.DOTALL)
            if buy_table_match:
                buy_rows = buy_table_match.group(1).strip().split('\n')
                for row in buy_rows:
                    if '|' in row and not row.strip().startswith('|--') and not '-----' in row:
                        parts = [p.strip() for p in row.split('|') if p.strip()]
                        if len(parts) >= 4:
                            dee_trades['buy'].append({
                                'symbol': parts[0],
                                'shares': int(parts[1]) if parts[1].isdigit() else 0,
                                'limit_price': float(parts[2].replace('$', '')) if parts[2].replace('$', '').replace('.', '').isdigit() else None,
                                'stop_loss': float(parts[3].replace('$', '')) if parts[3].replace('$', '').replace('.', '').isdigit() else None,
                                'rationale': parts[4] if len(parts) > 4 else ''
                            })

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
            sell_table_match = re.search(r'### SELL ORDERS.*?\n\|.*?\n\|(.*?)(?=\n### |\n## |\Z)', shorgan_content, re.DOTALL)
            if sell_table_match:
                sell_rows = sell_table_match.group(1).strip().split('\n')
                for row in sell_rows:
                    if '|' in row and not row.strip().startswith('|--') and not '-----' in row:
                        parts = [p.strip() for p in row.split('|') if p.strip()]
                        if len(parts) >= 3:
                            shorgan_trades['sell'].append({
                                'symbol': parts[0],
                                'shares': int(parts[1]) if parts[1].isdigit() else 0,
                                'limit_price': float(parts[2].replace('$', '')) if parts[2].replace('$', '').replace('.', '').isdigit() else None,
                                'rationale': parts[3] if len(parts) > 3 else ''
                            })

            buy_table_match = re.search(r'### BUY ORDERS.*?\n\|.*?\n\|(.*?)(?=\n### |\n## |\Z)', shorgan_content, re.DOTALL)
            if buy_table_match:
                buy_rows = buy_table_match.group(1).strip().split('\n')
                for row in buy_rows:
                    if '|' in row and not row.strip().startswith('|--') and not '-----' in row:
                        parts = [p.strip() for p in row.split('|') if p.strip()]
                        if len(parts) >= 4:
                            shorgan_trades['buy'].append({
                                'symbol': parts[0],
                                'shares': int(parts[1]) if parts[1].isdigit() else 0,
                                'limit_price': float(parts[2].replace('$', '')) if parts[2].replace('$', '').replace('.', '').isdigit() else None,
                                'stop_loss': float(parts[3].replace('$', '')) if parts[3].replace('$', '').replace('.', '').isdigit() else None,
                                'rationale': parts[4] if len(parts) > 4 else ''
                            })

            short_table_match = re.search(r'### SHORT SELL.*?\n\|.*?\n\|(.*?)(?=\n### |\n## |\Z)', shorgan_content, re.DOTALL)
            if short_table_match:
                short_rows = short_table_match.group(1).strip().split('\n')
                for row in short_rows:
                    if '|' in row and not row.strip().startswith('|--') and not '-----' in row:
                        parts = [p.strip() for p in row.split('|') if p.strip()]
                        if len(parts) >= 4:
                            shorgan_trades['short'].append({
                                'symbol': parts[0],
                                'shares': int(parts[1]) if parts[1].isdigit() else 0,
                                'limit_price': float(parts[2].replace('$', '')) if parts[2].replace('$', '').replace('.', '').isdigit() else None,
                                'stop_loss': float(parts[3].replace('$', '')) if parts[3].replace('$', '').replace('.', '').isdigit() else None,
                                'rationale': parts[4] if len(parts) > 4 else ''
                            })

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
                is_shorgan_live = (api == self.shorgan_api and SHORGAN_LIVE_TRADING)
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
            if api == self.shorgan_api and SHORGAN_LIVE_TRADING and limit_price:
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
                    account_value = SHORGAN_CAPITAL if api == self.shorgan_api else 100000
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

            order = api.submit_order(**order_params)

            trade_record = {
                'symbol': symbol,
                'shares': shares,
                'side': side,
                'order_type': order_type,
                'limit_price': limit_price,
                'order_id': order.id,
                'timestamp': datetime.now().isoformat(),
                'status': 'submitted',
                'extended_hours': order_params.get('extended_hours', False),
                'rationale': trade_info.get('rationale', '')
            }

            self.executed_trades.append(trade_record)
            print(f"[SUCCESS] Order ID: {order.id}")

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
            error_record = {
                'symbol': trade_info['symbol'],
                'shares': trade_info['shares'],
                'side': side,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.failed_trades.append(error_record)
            print(f"[ERROR] Failed to {side} {trade_info['symbol']}: {e}")
            return None

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

        # Execute SHORGAN-BOT trades
        if shorgan_trades['sell'] or shorgan_trades['buy'] or shorgan_trades['short']:
            print("-" * 40)
            print("SHORGAN-BOT TRADES")
            print("-" * 40)

            # Execute sells first
            for trade in shorgan_trades['sell']:
                result = self.execute_trade(self.shorgan_api, trade, 'sell')
                if result is None:
                    retry_queue.append(('shorgan', trade, 'sell'))
                time.sleep(1)

            # Execute buys
            for trade in shorgan_trades['buy']:
                result = self.execute_trade(self.shorgan_api, trade, 'buy')
                if result is None:
                    retry_queue.append(('shorgan', trade, 'buy'))
                time.sleep(1)

            # Execute shorts (if enabled)
            if SHORGAN_ALLOW_SHORTS:
                for trade in shorgan_trades['short']:
                    result = self.execute_trade(self.shorgan_api, trade, 'sell')  # Short = sell
                    if result is None:
                        retry_queue.append(('shorgan', trade, 'sell'))
                    time.sleep(1)
            elif shorgan_trades['short']:
                print(f"\n[WARNING] SKIPPING {len(shorgan_trades['short'])} SHORT TRADES (Shorting disabled - cash account)")
                for trade in shorgan_trades['short']:
                    print(f"   [SKIP] SHORT {trade['shares']} {trade['symbol']} @ ${trade.get('price', 'N/A')}")
                    self.failed_trades.append({
                        'symbol': trade['symbol'],
                        'side': 'short',
                        'shares': trade['shares'],
                        'error': 'Shorting disabled - cash account (no margin)',
                        'bot': 'SHORGAN-BOT'
                    })

        # Retry failed trades if any
        if retry_queue and max_retries > 0:
            print()
            print("-" * 40)
            print(f"RETRYING {len(retry_queue)} FAILED TRADES")
            print("-" * 40)
            time.sleep(5)  # Wait before retry

            for bot_type, trade, side in retry_queue:
                print(f"\n[RETRY] {side.upper()} {trade['shares']} {trade['symbol']}")
                api = self.dee_api if bot_type == 'dee' else self.shorgan_api

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
                    print(f"[RETRY FAILED] {trade['symbol']} - will not retry again")
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

def main():
    executor = DailyTradeExecutor()
    success = executor.execute_all_trades()

    if success:
        print("\n[SUCCESS] All trades executed successfully")
        return 0
    else:
        print("\n[WARNING] Some trades failed - check logs")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)