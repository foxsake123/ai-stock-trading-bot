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

# Alpaca API Configuration (from environment variables)
DEE_BOT_CONFIG = {
    'API_KEY': os.getenv('ALPACA_API_KEY_DEE'),
    'SECRET_KEY': os.getenv('ALPACA_SECRET_KEY_DEE'),
    'BASE_URL': 'https://paper-api.alpaca.markets'
}

SHORGAN_BOT_CONFIG = {
    'API_KEY': os.getenv('ALPACA_API_KEY_SHORGAN'),
    'SECRET_KEY': os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    'BASE_URL': 'https://paper-api.alpaca.markets'
}

# Validate API keys are loaded
if not DEE_BOT_CONFIG['API_KEY'] or not DEE_BOT_CONFIG['SECRET_KEY']:
    raise ValueError("DEE-BOT API keys not found in environment variables. Check your .env file.")
if not SHORGAN_BOT_CONFIG['API_KEY'] or not SHORGAN_BOT_CONFIG['SECRET_KEY']:
    raise ValueError("SHORGAN-BOT API keys not found in environment variables. Check your .env file.")

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

            # 1. Check market hours
            clock = api.get_clock()
            if not clock.is_open:
                validation_errors.append(f"Market is closed")
                return False, validation_errors

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

            # Determine order type
            order_type = 'limit' if limit_price else 'market'

            order_params = {
                'symbol': symbol,
                'qty': shares,
                'side': side,
                'type': order_type,
                'time_in_force': 'day'
            }

            if order_type == 'limit':
                order_params['limit_price'] = str(limit_price)

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
                'rationale': trade_info.get('rationale', '')
            }

            self.executed_trades.append(trade_record)
            print(f"[SUCCESS] Order ID: {order.id}")
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
        """Check if market is open"""
        try:
            clock = self.dee_api.get_clock()
            if clock.is_open:
                print("[INFO] Market is OPEN")
                return True
            else:
                next_open = clock.next_open
                print(f"[INFO] Market is CLOSED. Opens at {next_open}")
                return False
        except Exception as e:
            print(f"[WARNING] Could not check market status: {e}")
            return True  # Proceed anyway

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

            # Execute shorts
            for trade in shorgan_trades['short']:
                result = self.execute_trade(self.shorgan_api, trade, 'sell')  # Short = sell
                if result is None:
                    retry_queue.append(('shorgan', trade, 'sell'))
                time.sleep(1)

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