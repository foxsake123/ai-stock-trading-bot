#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Execute Tuesday September 23, 2025 Trading Plan
Processes trades for both DEE-BOT and SHORGAN-BOT
"""
import os
import sys
os.environ['PYTHONIOENCODING'] = 'utf-8'
import json
import time
from datetime import datetime
import alpaca_trade_api as tradeapi

# API Configuration
API_KEY = 'PKJRLSB2MFEJUSK6UK2E'
API_SECRET = 'QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic'
BASE_URL = 'https://paper-api.alpaca.markets'

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

def execute_dee_bot_trades():
    """Execute DEE-BOT trades (Beta-Neutral S&P 100)"""
    print("\n" + "="*60)
    print("EXECUTING DEE-BOT TRADES")
    print("="*60)

    # SELL ORDERS
    sell_orders = [
        {'symbol': 'PG', 'qty': 33, 'limit': 153},
        {'symbol': 'CVX', 'qty': 31, 'limit': 156},
        {'symbol': 'AAPL', 'qty': 5, 'limit': 256},
        {'symbol': 'NVDA', 'qty': 15, 'limit': 182.50}
    ]

    for order in sell_orders:
        try:
            api.submit_order(
                symbol=order['symbol'],
                qty=order['qty'],
                side='sell',
                type='limit',
                time_in_force='day',
                limit_price=order['limit']
            )
            print(f"[SUCCESS] SELL {order['qty']} {order['symbol']} @ ${order['limit']}")
            time.sleep(0.5)
        except Exception as e:
            print(f"[FAILED] Failed to sell {order['symbol']}: {e}")

    # BUY ORDERS
    buy_orders = [
        {'symbol': 'UNH', 'qty': 14, 'limit': 342, 'stop': 300},
        {'symbol': 'NEE', 'qty': 53, 'limit': 71.50, 'stop': 63},
        {'symbol': 'AMZN', 'qty': 21, 'limit': 228, 'stop': 200}
    ]

    for order in buy_orders:
        try:
            # Place buy order
            api.submit_order(
                symbol=order['symbol'],
                qty=order['qty'],
                side='buy',
                type='limit',
                time_in_force='day',
                limit_price=order['limit']
            )
            print(f"[SUCCESS] BUY {order['qty']} {order['symbol']} @ ${order['limit']}")
            time.sleep(0.5)
        except Exception as e:
            print(f"[FAILED] Failed to buy {order['symbol']}: {e}")

def execute_shorgan_bot_trades():
    """Execute SHORGAN-BOT trades (Catalyst Trading)"""
    print("\n" + "="*60)
    print("EXECUTING SHORGAN-BOT TRADES")
    print("="*60)

    # BUY ORDERS
    buy_orders = [
        {'symbol': 'SRRK', 'qty': 100, 'limit': 34.50, 'stop': 27.00, 'note': 'FDA catalyst TODAY'},
        {'symbol': 'FBIO', 'qty': 700, 'limit': 4.10, 'stop': 3.00, 'note': 'Sept 30 FDA'},
        {'symbol': 'RIVN', 'qty': 200, 'limit': 15.50, 'stop': 13.00, 'note': 'Q3 deliveries'},
        {'symbol': 'KSS', 'qty': 150, 'limit': 17.00, 'stop': 15.00, 'note': 'Retail turnaround'}
    ]

    for order in buy_orders:
        try:
            api.submit_order(
                symbol=order['symbol'],
                qty=order['qty'],
                side='buy',
                type='limit',
                time_in_force='day',
                limit_price=order['limit']
            )
            print(f"[SUCCESS] BUY {order['qty']} {order['symbol']} @ ${order['limit']} ({order['note']})")
            time.sleep(0.5)
        except Exception as e:
            print(f"[FAILED] Failed to buy {order['symbol']}: {e}")

    # SHORT SELL ORDER
    try:
        api.submit_order(
            symbol='IONQ',
            qty=50,
            side='sell',
            type='limit',
            time_in_force='day',
            limit_price=69.00
        )
        print(f"[SUCCESS] SHORT 50 IONQ @ $69.00 (overhyped quantum)")
    except Exception as e:
        print(f"[FAILED] Failed to short IONQ: {e}")

def check_positions():
    """Check current positions for both bots"""
    print("\n" + "="*60)
    print("CURRENT POSITIONS CHECK")
    print("="*60)

    try:
        positions = api.list_positions()
        total_value = 0
        for position in positions:
            value = float(position.market_value)
            total_value += value
            pl = float(position.unrealized_pl)
            pl_pct = float(position.unrealized_plpc) * 100
            current_price = float(position.current_price)
            print(f"{position.symbol}: {position.qty} shares @ ${current_price:.2f} | P&L: ${pl:.2f} ({pl_pct:.1f}%)")

        print(f"\nTotal Position Value: ${total_value:,.2f}")

        # Check account
        account = api.get_account()
        print(f"Account Value: ${float(account.portfolio_value):,.2f}")
        print(f"Buying Power: ${float(account.buying_power):,.2f}")

    except Exception as e:
        print(f"Error checking positions: {e}")

def main():
    """Main execution"""
    print(f"\n{'='*60}")
    print(f"TUESDAY SEPTEMBER 23, 2025 TRADE EXECUTION")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    # Check market status
    try:
        clock = api.get_clock()
        if not clock.is_open:
            print("\n[WARNING] MARKET IS CLOSED - Orders will be queued for next open")
        else:
            print(f"[OPEN] Market is OPEN until {clock.next_close.strftime('%I:%M %p')}")
    except Exception as e:
        print(f"Could not check market status: {e}")

    # Execute trades
    execute_dee_bot_trades()
    execute_shorgan_bot_trades()

    # Check positions
    check_positions()

    print(f"\n{'='*60}")
    print("EXECUTION COMPLETE - Monitor positions throughout the day")
    print("SPECIAL FOCUS: SRRK FDA decision today!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()