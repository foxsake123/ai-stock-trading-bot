#!/usr/bin/env python3
"""
SHORGAN-BOT Paper Trade Execution
Executes trades from TODAYS_TRADES file to the SHORGAN Paper account ($100K)
"""

import os
import re
import sys
import json
import time
import alpaca_trade_api as tradeapi
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SHORGAN Paper API Configuration
SHORGAN_PAPER_CONFIG = {
    'API_KEY': os.getenv('ALPACA_API_KEY_SHORGAN'),
    'SECRET_KEY': os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    'BASE_URL': 'https://paper-api.alpaca.markets'
}

# Paper account settings
SHORGAN_PAPER_CAPITAL = 100000.0
SHORGAN_MAX_POSITION_PCT = 0.10  # 10% max position
SHORGAN_ALLOW_SHORTS = True  # Paper can short

# Validate API keys
if not SHORGAN_PAPER_CONFIG['API_KEY'] or not SHORGAN_PAPER_CONFIG['SECRET_KEY']:
    raise ValueError("SHORGAN Paper API keys not found. Check ALPACA_API_KEY_SHORGAN in .env")


class ShorganPaperExecutor:
    def __init__(self):
        self.api = tradeapi.REST(
            SHORGAN_PAPER_CONFIG['API_KEY'],
            SHORGAN_PAPER_CONFIG['SECRET_KEY'],
            SHORGAN_PAPER_CONFIG['BASE_URL'],
            api_version='v2'
        )
        self.executed_trades = []
        self.failed_trades = []

    def get_account_info(self):
        """Get account information"""
        account = self.api.get_account()
        return {
            'equity': float(account.equity),
            'cash': float(account.cash),
            'buying_power': float(account.buying_power),
            'portfolio_value': float(account.portfolio_value)
        }

    def get_positions(self):
        """Get current positions"""
        positions = self.api.list_positions()
        return {p.symbol: {'qty': int(p.qty), 'market_value': float(p.market_value)} for p in positions}

    def find_trades_file(self):
        """Find today's trades file"""
        today = datetime.now().strftime('%Y-%m-%d')

        # Try today's date first
        paths = [
            f'docs/TODAYS_TRADES_{today}.md',
            f'TODAYS_TRADES_{today}.md'
        ]

        for path in paths:
            if Path(path).exists():
                return Path(path)

        # Find most recent (excluding _LIVE files)
        docs_dir = Path('docs')
        if docs_dir.exists():
            trade_files = [f for f in docs_dir.glob('TODAYS_TRADES_*.md')
                          if '_LIVE' not in f.name]
            if trade_files:
                latest = max(trade_files, key=lambda x: x.stat().st_mtime)
                print(f"[INFO] Using most recent file: {latest}")
                return latest

        return None

    def parse_shorgan_trades(self, file_path):
        """Parse SHORGAN-BOT trades from markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        trades = {'sell': [], 'buy': [], 'short': []}

        # Find SHORGAN-BOT section
        shorgan_match = re.search(
            r'## (?:🚀 )?SHORGAN-BOT TRADES.*?(?=^## (?:📋|🤖)|^---|\Z)',
            content, re.DOTALL | re.MULTILINE
        )

        if not shorgan_match:
            print("[WARNING] No SHORGAN-BOT section found")
            return trades

        shorgan_content = shorgan_match.group(0)

        # Parse SELL orders table
        sell_section = re.search(r'### SELL ORDERS.*?(?=### BUY|### 📋|\Z)', shorgan_content, re.DOTALL)
        if sell_section:
            sell_rows = re.findall(r'\|\s*(\w+)\s*\|\s*(\d+)\s*\|\s*\$?([\d.]+)', sell_section.group(0))
            for symbol, shares, price in sell_rows:
                if symbol.upper() not in ['SYMBOL', 'NO']:
                    trades['sell'].append({
                        'symbol': symbol.upper(),
                        'shares': int(shares),
                        'price': float(price)
                    })

        # Parse BUY orders table
        buy_section = re.search(r'### BUY ORDERS.*?(?=### 📋|### REJECTED|\Z)', shorgan_content, re.DOTALL)
        if buy_section:
            buy_rows = re.findall(r'\|\s*(\w+)\s*\|\s*(\d+)\s*\|\s*\$?([\d.]+)\s*\|\s*\$?([\d.]+)', buy_section.group(0))
            for symbol, shares, price, stop_loss in buy_rows:
                if symbol.upper() not in ['SYMBOL', 'NO']:
                    trades['buy'].append({
                        'symbol': symbol.upper(),
                        'shares': int(shares),
                        'price': float(price),
                        'stop_loss': float(stop_loss) if stop_loss else None
                    })

        return trades

    def execute_trade(self, trade, side):
        """Execute a single trade"""
        symbol = trade['symbol']
        shares = trade['shares']
        price = trade.get('price')

        try:
            # Get current positions
            positions = self.get_positions()

            # Validation for sells
            if side == 'sell':
                if symbol not in positions:
                    print(f"[SKIP] {symbol}: No position to sell")
                    return None
                current_qty = positions[symbol]['qty']
                if current_qty < shares:
                    print(f"[ADJUST] {symbol}: Reducing sell from {shares} to {current_qty} shares")
                    shares = current_qty

            # Get account info for buys
            if side == 'buy':
                account = self.get_account_info()
                required = shares * price
                if required > account['buying_power']:
                    max_shares = int(account['buying_power'] / price)
                    if max_shares < 1:
                        print(f"[SKIP] {symbol}: Insufficient buying power (${account['buying_power']:.2f})")
                        return None
                    print(f"[ADJUST] {symbol}: Reducing buy from {shares} to {max_shares} shares")
                    shares = max_shares

            # Submit order
            print(f"[EXECUTING] {side.upper()} {shares} {symbol} @ ${price}")

            order = self.api.submit_order(
                symbol=symbol,
                qty=shares,
                side=side,
                type='limit',
                time_in_force='day',
                limit_price=price
            )

            print(f"[SUCCESS] Order ID: {order.id}")
            self.executed_trades.append({
                'symbol': symbol,
                'side': side,
                'shares': shares,
                'price': price,
                'order_id': order.id
            })
            return order

        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] {symbol}: {error_msg}")
            self.failed_trades.append({
                'symbol': symbol,
                'side': side,
                'shares': shares,
                'error': error_msg
            })
            return None

    def run(self):
        """Execute all SHORGAN Paper trades"""
        print("=" * 70)
        print("SHORGAN-BOT PAPER TRADE EXECUTION")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        # Get account info
        account = self.get_account_info()
        print(f"\n[ACCOUNT] Equity: ${account['equity']:,.2f}")
        print(f"[ACCOUNT] Cash: ${account['cash']:,.2f}")
        print(f"[ACCOUNT] Buying Power: ${account['buying_power']:,.2f}")

        # Find trades file
        trades_file = self.find_trades_file()
        if not trades_file:
            print("[ERROR] No trades file found")
            return

        print(f"\n[INFO] Using: {trades_file}")

        # Parse trades
        trades = self.parse_shorgan_trades(trades_file)
        total = len(trades['sell']) + len(trades['buy']) + len(trades['short'])
        print(f"[INFO] Found {total} trades (Sells: {len(trades['sell'])}, Buys: {len(trades['buy'])})")

        if total == 0:
            print("[INFO] No trades to execute")
            return

        # Execute sells first
        print("\n" + "-" * 40)
        print("SELL ORDERS")
        print("-" * 40)
        for trade in trades['sell']:
            self.execute_trade(trade, 'sell')
            time.sleep(0.5)

        # Execute buys
        print("\n" + "-" * 40)
        print("BUY ORDERS")
        print("-" * 40)
        for trade in trades['buy']:
            self.execute_trade(trade, 'buy')
            time.sleep(0.5)

        # Summary
        print("\n" + "=" * 70)
        print("EXECUTION SUMMARY")
        print("=" * 70)
        print(f"Successful: {len(self.executed_trades)}")
        print(f"Failed/Skipped: {len(self.failed_trades)}")

        if self.executed_trades:
            print("\nExecuted Trades:")
            for t in self.executed_trades:
                print(f"  {t['side'].upper()} {t['shares']} {t['symbol']} @ ${t['price']} - {t['order_id']}")

        if self.failed_trades:
            print("\nFailed/Skipped Trades:")
            for t in self.failed_trades:
                print(f"  {t['side'].upper()} {t['shares']} {t['symbol']} - {t['error']}")

        # Save log
        log_dir = Path('scripts-and-data/trade-logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"shorgan_paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(log_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'account': 'SHORGAN-PAPER',
                'executed': self.executed_trades,
                'failed': self.failed_trades
            }, f, indent=2)

        print(f"\n[LOG] Saved to: {log_file}")


if __name__ == '__main__':
    executor = ShorganPaperExecutor()
    executor.run()
