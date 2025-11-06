#!/usr/bin/env python3
"""
Manual Trade Execution Script
Executes trades from research reports for DEE-BOT and SHORGAN-BOT Live
Date: November 5, 2025 11:00 AM ET
"""

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

print("=" * 80)
print("MANUAL TRADE EXECUTION - November 5, 2025")
print("=" * 80)
print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
print()

# Initialize clients
dee_client = TradingClient(
    os.getenv('ALPACA_API_KEY_DEE'),
    os.getenv('ALPACA_SECRET_KEY_DEE'),
    paper=True
)

shorgan_live_client = TradingClient(
    os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'),
    os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'),
    paper=False
)

# ============================================================================
# DEE-BOT TRADES (Paper Account)
# ============================================================================

print("=" * 80)
print("DEE-BOT TRADES (Paper Account - $100K)")
print("=" * 80)
print()

dee_trades = [
    # SELL ORDER
    {
        'action': 'SELL',
        'symbol': 'MRK',
        'shares': 185,
        'limit_price': 84.25,
        'rationale': 'Reduce concentration risk from 30.8% to 15.4%'
    },
    # BUY ORDERS
    {
        'action': 'BUY',
        'symbol': 'JNJ',
        'shares': 52,
        'limit_price': 152.00,
        'stop_loss': 142.00,
        'rationale': 'Premier healthcare defensive at discount valuation, 3.2% yield'
    },
    {
        'action': 'BUY',
        'symbol': 'PG',
        'shares': 27,
        'limit_price': 147.50,
        'stop_loss': 136.00,
        'rationale': 'Build consumer staples position to 4.5% for defensive stability'
    },
    {
        'action': 'BUY',
        'symbol': 'NEE',
        'shares': 33,
        'limit_price': 75.00,
        'stop_loss': 69.00,
        'rationale': 'Initiate utility position for defensive allocation, 3.8% yield'
    },
    {
        'action': 'BUY',
        'symbol': 'BRK.B',
        'shares': 3,
        'limit_price': 428.00,
        'stop_loss': 400.00,
        'rationale': 'Buffett defensive conglomerate near book value'
    }
]

dee_orders_placed = []
dee_errors = []

for trade in dee_trades:
    try:
        print(f"[{trade['action']}] {trade['symbol']}: {trade['shares']} shares @ ${trade['limit_price']}")
        print(f"   Rationale: {trade['rationale']}")

        order_data = LimitOrderRequest(
            symbol=trade['symbol'],
            qty=trade['shares'],
            side=OrderSide.BUY if trade['action'] == 'BUY' else OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
            limit_price=trade['limit_price']
        )

        order = dee_client.submit_order(order_data)
        dee_orders_placed.append({
            'symbol': trade['symbol'],
            'action': trade['action'],
            'shares': trade['shares'],
            'order_id': order.id,
            'status': order.status
        })
        print(f"   [OK] Order submitted: ID {order.id}")

        if 'stop_loss' in trade:
            print(f"   Stop Loss: ${trade['stop_loss']}")
        print()

    except Exception as e:
        dee_errors.append({
            'symbol': trade['symbol'],
            'error': str(e)
        })
        print(f"   [ERROR] {str(e)}")
        print()

# ============================================================================
# SHORGAN-BOT LIVE TRADES ($2K Account)
# ============================================================================

print("=" * 80)
print("SHORGAN-BOT LIVE TRADES ($2K Account)")
print("=" * 80)
print()

shorgan_trades = [
    {
        'action': 'BUY',
        'symbol': 'APPS',
        'shares': 12,
        'limit_price': 8.50,
        'stop_loss': 7.23,
        'rationale': 'Earnings tonight + mobile growth inflection'
    },
    {
        'action': 'BUY',
        'symbol': 'PAYO',
        'shares': 14,
        'limit_price': 7.30,
        'stop_loss': 6.20,
        'rationale': 'Fintech earnings + cross-border payment growth'
    }
]

shorgan_orders_placed = []
shorgan_errors = []

for trade in shorgan_trades:
    try:
        print(f"[{trade['action']}] {trade['symbol']}: {trade['shares']} shares @ ${trade['limit_price']}")
        print(f"   Rationale: {trade['rationale']}")

        order_data = LimitOrderRequest(
            symbol=trade['symbol'],
            qty=trade['shares'],
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
            limit_price=trade['limit_price']
        )

        order = shorgan_live_client.submit_order(order_data)
        shorgan_orders_placed.append({
            'symbol': trade['symbol'],
            'action': trade['action'],
            'shares': trade['shares'],
            'order_id': order.id,
            'status': order.status
        })
        print(f"   [OK] Order submitted: ID {order.id}")
        print(f"   Stop Loss: ${trade['stop_loss']}")
        print()

    except Exception as e:
        shorgan_errors.append({
            'symbol': trade['symbol'],
            'error': str(e)
        })
        print(f"   [ERROR] {str(e)}")
        print()

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 80)
print("EXECUTION SUMMARY")
print("=" * 80)
print()

print(f"DEE-BOT: {len(dee_orders_placed)} orders placed, {len(dee_errors)} errors")
for order in dee_orders_placed:
    print(f"  - {order['action']} {order['symbol']}: {order['shares']} shares (Order ID: {order['order_id']})")

if dee_errors:
    print("\nDEE-BOT Errors:")
    for error in dee_errors:
        print(f"  - {error['symbol']}: {error['error']}")

print()
print(f"SHORGAN-BOT LIVE: {len(shorgan_orders_placed)} orders placed, {len(shorgan_errors)} errors")
for order in shorgan_orders_placed:
    print(f"  - {order['action']} {order['symbol']}: {order['shares']} shares (Order ID: {order['order_id']})")

if shorgan_errors:
    print("\nSHORGAN-BOT LIVE Errors:")
    for error in shorgan_errors:
        print(f"  - {error['symbol']}: {error['error']}")

print()
print("=" * 80)
print("NEXT STEPS:")
print("=" * 80)
print("1. Monitor order fills throughout the day")
print("2. Place GTC stop loss orders once positions fill")
print("3. Check portfolio status at market close (4:00 PM ET)")
print("4. Review Telegram for any alerts")
print()
print("Trades executed from research dated: 2025-11-05")
print("=" * 80)
