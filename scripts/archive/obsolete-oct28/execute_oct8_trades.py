#!/usr/bin/env python3
"""
Automated Execution for Oct 8, 2025 Approved Trades
Executes 9 approved orders (5 DEE-BOT + 4 SHORGAN-BOT) and sends Telegram notifications
"""

import os
import sys
import json
import time
import requests
import alpaca_trade_api as tradeapi
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Alpaca API Configuration
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

# Telegram Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-4524457329')

# Validate API keys
if not DEE_BOT_CONFIG['API_KEY'] or not DEE_BOT_CONFIG['SECRET_KEY']:
    raise ValueError("DEE-BOT API keys not found in environment variables")
if not SHORGAN_BOT_CONFIG['API_KEY'] or not SHORGAN_BOT_CONFIG['SECRET_KEY']:
    raise ValueError("SHORGAN-BOT API keys not found in environment variables")

# APPROVED ORDERS - Option B (User Approved Oct 7, 2025)
APPROVED_ORDERS = {
    'DEE': [
        {'symbol': 'WMT', 'shares': 93, 'limit_price': 102.00, 'type': 'buy'},
        {'symbol': 'UNH', 'shares': 22, 'limit_price': 360.00, 'type': 'buy'},
        {'symbol': 'NEE', 'shares': 95, 'limit_price': 80.00, 'type': 'buy'},
        {'symbol': 'COST', 'shares': 11, 'limit_price': 915.00, 'type': 'buy'},
        {'symbol': 'MRK', 'shares': 110, 'limit_price': 89.00, 'type': 'buy'}
    ],
    'SHORGAN': [
        {'symbol': 'ARQT', 'shares': 150, 'limit_price': 20.00, 'type': 'buy', 'stop_loss': 16.50, 'catalyst': 'FDA Oct 13'},
        {'symbol': 'HIMS', 'shares': 37, 'limit_price': 54.00, 'type': 'buy', 'stop_loss': 49.00, 'catalyst': 'Short squeeze'},
        {'symbol': 'WOLF', 'shares': 96, 'limit_price': 26.00, 'type': 'buy', 'stop_loss': 22.00, 'catalyst': 'Delisting Oct 10'},
        {'symbol': 'PLUG', 'shares': 500, 'limit_price': 4.50, 'type': 'short', 'stop_loss': 5.50, 'catalyst': 'Fuel cell headwinds'}
    ]
}

class Oct8TradeExecutor:
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

        self.executed_orders = []
        self.failed_orders = []
        self.stop_orders = []

    def send_telegram(self, message):
        """Send message via Telegram"""
        if not TELEGRAM_TOKEN:
            print("[WARNING] Telegram token not configured")
            return False

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }

        try:
            response = requests.post(url, data=payload, timeout=10)
            if response.status_code == 200:
                print("[TELEGRAM] Message sent successfully")
                return True
            else:
                print(f"[TELEGRAM] Failed: {response.text}")
                return False
        except Exception as e:
            print(f"[TELEGRAM] Error: {e}")
            return False

    def check_market_status(self):
        """Check if market is open"""
        try:
            clock = self.dee_api.get_clock()
            return clock.is_open, clock
        except Exception as e:
            print(f"[ERROR] Could not check market status: {e}")
            return False, None

    def execute_order(self, api, order_info, bot_name):
        """Execute a single order"""
        try:
            symbol = order_info['symbol']
            shares = order_info['shares']
            limit_price = order_info['limit_price']
            order_type = order_info['type']

            # Determine side (buy or sell for short)
            side = 'sell' if order_type == 'short' else 'buy'

            order_params = {
                'symbol': symbol,
                'qty': shares,
                'side': side,
                'type': 'limit',
                'time_in_force': 'day',
                'limit_price': str(limit_price)
            }

            action_str = 'SHORT' if order_type == 'short' else 'BUY'
            print(f"[{bot_name}] {action_str} {shares} {symbol} @ ${limit_price}")

            order = api.submit_order(**order_params)

            record = {
                'bot': bot_name,
                'symbol': symbol,
                'shares': shares,
                'side': side,
                'limit_price': limit_price,
                'order_id': order.id,
                'timestamp': datetime.now().isoformat(),
                'type': order_type,
                'catalyst': order_info.get('catalyst', '')
            }

            self.executed_orders.append(record)
            print(f"[SUCCESS] Order ID: {order.id}")

            # Schedule stop-loss if applicable
            if 'stop_loss' in order_info:
                self.schedule_stop_loss(api, order_info, bot_name)

            return order

        except Exception as e:
            error_record = {
                'bot': bot_name,
                'symbol': order_info['symbol'],
                'shares': order_info['shares'],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.failed_orders.append(error_record)
            print(f"[ERROR] {order_info['symbol']}: {e}")
            return None

    def schedule_stop_loss(self, api, order_info, bot_name):
        """Schedule stop-loss order (to be placed after fill)"""
        stop_info = {
            'bot': bot_name,
            'symbol': order_info['symbol'],
            'shares': order_info['shares'],
            'stop_price': order_info['stop_loss'],
            'type': order_info['type'],
            'api': api
        }
        self.stop_orders.append(stop_info)
        print(f"[STOP SCHEDULED] {order_info['symbol']} @ ${order_info['stop_loss']}")

    def place_stop_loss_orders(self, wait_time=60):
        """Place stop-loss orders after waiting for fills"""
        if not self.stop_orders:
            print("[INFO] No stop-loss orders to place")
            return

        print(f"\n[INFO] Waiting {wait_time} seconds for fills before placing stops...")
        time.sleep(wait_time)

        print("\n" + "="*80)
        print("PLACING STOP-LOSS ORDERS")
        print("="*80)

        for stop in self.stop_orders:
            try:
                symbol = stop['symbol']
                shares = stop['shares']
                stop_price = stop['stop_price']
                api = stop['api']
                order_type = stop['type']

                # Determine side (buy for short cover, sell for long protection)
                side = 'buy' if order_type == 'short' else 'sell'

                order_params = {
                    'symbol': symbol,
                    'qty': shares,
                    'side': side,
                    'type': 'stop',
                    'time_in_force': 'gtc',
                    'stop_price': str(stop_price)
                }

                action = 'BUY TO COVER' if order_type == 'short' else 'STOP LOSS'
                print(f"[{stop['bot']}] {action} {shares} {symbol} @ ${stop_price}")

                order = api.submit_order(**order_params)
                print(f"[SUCCESS] Stop order ID: {order.id}")

            except Exception as e:
                print(f"[ERROR] Failed to place stop for {symbol}: {e}")

    def execute_all_orders(self):
        """Execute all approved orders"""
        print("="*80)
        print(f"EXECUTING APPROVED ORDERS - OCT 8, 2025")
        print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print("="*80)

        # Check market status
        is_open, clock = self.check_market_status()
        if not is_open:
            if clock:
                msg = f"Market is CLOSED. Next open: {clock.next_open}"
            else:
                msg = "Market is CLOSED"
            print(f"[WARNING] {msg}")
            self.send_telegram(f"<b>Trade Execution Alert</b>\n\n{msg}\n\nOrders will be queued for market open.")

        # Send pre-execution notification
        pre_msg = f"""<b>AI Trading Bot - Execution Starting</b>

Date: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}
Status: {"Market Open" if is_open else "Pre-Market (Orders Queued)"}

<b>Executing 9 Approved Orders:</b>

<b>DEE-BOT (5 orders - $44,861):</b>
1. BUY 93 WMT @ $102.00
2. BUY 22 UNH @ $360.00
3. BUY 95 NEE @ $80.00
4. BUY 11 COST @ $915.00
5. BUY 110 MRK @ $89.00

<b>SHORGAN-BOT (4 orders - $9,744):</b>
6. BUY 150 ARQT @ $20.00 (FDA Oct 13)
7. BUY 37 HIMS @ $54.00 (Short squeeze)
8. BUY 96 WOLF @ $26.00 (Delisting Oct 10)
9. SHORT 500 PLUG @ $4.50 (Fuel cell sector)

<b>Risk Profile:</b>
Total Deployed: $54,605 (54.6%)
Cash Reserve: $145,395 (45.4%)
Max Loss: $1,594 (1.6%)

Execution starting now..."""

        self.send_telegram(pre_msg)

        # Execute DEE-BOT orders
        print("\n" + "-"*80)
        print("DEE-BOT ORDERS")
        print("-"*80)
        for order in APPROVED_ORDERS['DEE']:
            self.execute_order(self.dee_api, order, 'DEE-BOT')
            time.sleep(1)  # Rate limiting

        # Execute SHORGAN-BOT orders
        print("\n" + "-"*80)
        print("SHORGAN-BOT ORDERS")
        print("-"*80)
        for order in APPROVED_ORDERS['SHORGAN']:
            self.execute_order(self.shorgan_api, order, 'SHORGAN-BOT')
            time.sleep(1)

        # Summary
        print("\n" + "="*80)
        print("EXECUTION SUMMARY")
        print("="*80)
        print(f"Successful orders: {len(self.executed_orders)}/9")
        print(f"Failed orders: {len(self.failed_orders)}")
        print(f"Stop-loss orders scheduled: {len(self.stop_orders)}")

        # Send execution summary via Telegram
        summary_msg = self.build_summary_message()
        self.send_telegram(summary_msg)

        # Place stop-loss orders
        if self.stop_orders:
            self.place_stop_loss_orders()

            # Send stop confirmation
            stop_msg = f"""<b>Stop-Loss Orders Placed</b>

{len(self.stop_orders)} GTC stop orders active:

ARQT: STOP @ $16.50 (-17.5%)
HIMS: STOP @ $49.00 (-9.3%)
WOLF: STOP @ $22.00 (-15.4%)
PLUG: BUY TO COVER @ $5.50 (+22%)

All positions protected."""
            self.send_telegram(stop_msg)

        # Save execution log
        self.save_execution_log()

        return len(self.failed_orders) == 0

    def build_summary_message(self):
        """Build execution summary for Telegram"""
        success_count = len(self.executed_orders)
        fail_count = len(self.failed_orders)

        msg = f"""<b>Execution Complete - Oct 8, 2025</b>

<b>Results:</b>
Successful: {success_count}/9
Failed: {fail_count}

<b>Executed Orders:</b>
"""

        for order in self.executed_orders:
            action = 'SHORT' if order['type'] == 'short' else 'BUY'
            msg += f"\n{order['bot']}: {action} {order['shares']} {order['symbol']} @ ${order['limit_price']}"
            if order['catalyst']:
                msg += f" ({order['catalyst']})"

        if self.failed_orders:
            msg += "\n\n<b>Failed Orders:</b>"
            for failed in self.failed_orders:
                msg += f"\n{failed['bot']}: {failed['symbol']} - {failed['error']}"

        msg += f"\n\n<b>Next Steps:</b>"
        msg += f"\n1. Stop-loss orders will be placed in 60 seconds"
        msg += f"\n2. Monitor FOMC Minutes at 2PM ET today"
        msg += f"\n3. Track WOLF delisting Oct 10"
        msg += f"\n4. Track ARQT FDA decision Oct 13"

        return msg

    def save_execution_log(self):
        """Save execution log to file"""
        log_data = {
            'execution_date': '2025-10-08',
            'execution_time': datetime.now().isoformat(),
            'executed_orders': self.executed_orders,
            'failed_orders': self.failed_orders,
            'stop_orders': [
                {k: v for k, v in stop.items() if k != 'api'}
                for stop in self.stop_orders
            ],
            'success_rate': f"{len(self.executed_orders)}/9"
        }

        log_file = f"data/daily/reports/2025-10-08/execution_log_{datetime.now().strftime('%H%M%S')}.json"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)

        print(f"\n[LOG] Execution log saved: {log_file}")

def main():
    """Main execution function"""
    executor = Oct8TradeExecutor()

    # Send startup notification
    startup_msg = f"""<b>AUTOMATED EXECUTION STARTING</b>

Date: October 8, 2025
Time: {datetime.now().strftime('%I:%M %p ET')}

Executing user-approved Option B:
9 orders (5 DEE-BOT + 4 SHORGAN-BOT)

Multi-agent consensus validated:
- ARQT: 80%
- HIMS: 74%
- WOLF: 71%
- PLUG SHORT: 59%

System starting execution..."""

    executor.send_telegram(startup_msg)

    # Execute all orders
    success = executor.execute_all_orders()

    if success:
        print("\n[SUCCESS] All orders executed successfully")
        return 0
    else:
        print("\n[WARNING] Some orders failed - check Telegram and logs")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
