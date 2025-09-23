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

# Add path for logging
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Alpaca API Configuration
DEE_BOT_CONFIG = {
    'API_KEY': 'PK6FZK4DAQVTD7DYVH78',
    'SECRET_KEY': 'JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt',
    'BASE_URL': 'https://paper-api.alpaca.markets'
}

SHORGAN_BOT_CONFIG = {
    'API_KEY': 'PKJRLSB2MFEJUSK6UK2E',
    'SECRET_KEY': 'QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic',
    'BASE_URL': 'https://paper-api.alpaca.markets'
}

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

        with open(file_path, 'r') as f:
            content = f.read()

        dee_trades = {'sell': [], 'buy': []}
        shorgan_trades = {'sell': [], 'buy': [], 'short': []}

        # Find DEE-BOT section
        dee_section_match = re.search(r'## DEE-BOT.*?(?=^## [A-Z]|^---|\Z)', content, re.DOTALL | re.MULTILINE)
        if dee_section_match:
            dee_content = dee_section_match.group(0)

            # Parse DEE-BOT sell orders
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

            # Parse DEE-BOT buy orders
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

        # Find SHORGAN-BOT section
        shorgan_section_match = re.search(r'## SHORGAN-BOT.*?(?=^## [A-Z]|^---|\Z)', content, re.DOTALL | re.MULTILINE)
        if shorgan_section_match:
            shorgan_content = shorgan_section_match.group(0)

            # Parse SHORGAN-BOT buy orders
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

            # Parse SHORT SELL orders
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

    def execute_trade(self, api, trade_info, side):
        """Execute a single trade"""
        try:
            symbol = trade_info['symbol']
            shares = trade_info['shares']
            limit_price = trade_info.get('limit_price')

            if shares <= 0:
                print(f"[SKIP] {symbol}: Invalid share count ({shares})")
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

    def execute_all_trades(self):
        """Execute all trades from today's file"""
        print("=" * 80)
        print(f"DAILY TRADE EXECUTION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # Find and parse trades file
        trades_file = self.find_todays_trades_file()
        if not trades_file:
            print("[ERROR] No trades file found for today")
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

        # Execute DEE-BOT trades
        if dee_trades['sell'] or dee_trades['buy']:
            print("-" * 40)
            print("DEE-BOT TRADES")
            print("-" * 40)

            # Execute sells first
            for trade in dee_trades['sell']:
                self.execute_trade(self.dee_api, trade, 'sell')
                time.sleep(1)  # Rate limiting

            # Execute buys
            for trade in dee_trades['buy']:
                self.execute_trade(self.dee_api, trade, 'buy')
                time.sleep(1)

        # Execute SHORGAN-BOT trades
        if shorgan_trades['buy'] or shorgan_trades['short']:
            print("-" * 40)
            print("SHORGAN-BOT TRADES")
            print("-" * 40)

            # Execute buys
            for trade in shorgan_trades['buy']:
                self.execute_trade(self.shorgan_api, trade, 'buy')
                time.sleep(1)

            # Execute shorts
            for trade in shorgan_trades['short']:
                self.execute_trade(self.shorgan_api, trade, 'sell')  # Short = sell
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