#!/usr/bin/env python3
"""
Manual Trade Execution Script - November 10, 2025
Executes trades from Nov 7 research recommendations
Executed at: 2:33 PM ET (late execution, using 3-day-old research)
"""

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

print("=" * 80)
print("MANUAL TRADE EXECUTION - November 10, 2025")
print("Based on Nov 7 Research (3 days old)")
print("=" * 80)
print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
print()

# Initialize clients
dee_client = TradingClient(
    os.getenv('ALPACA_API_KEY_DEE'),
    os.getenv('ALPACA_SECRET_KEY_DEE'),
    paper=True
)

shorgan_paper_client = TradingClient(
    os.getenv('ALPACA_API_KEY_SHORGAN'),
    os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    paper=True
)

shorgan_live_client = TradingClient(
    os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'),
    os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'),
    paper=False
)

# ============================================================================
# DEE-BOT TRADES (Paper Account)
# From TRADE_DECISIONS_2025-11-07.md
# ============================================================================

print("=" * 80)
print("DEE-BOT TRADES (Paper Account - $100K)")
print("=" * 80)
print()

dee_trades = [
    {
        'action': 'SELL',
        'symbol': 'MRK',
        'shares': 85,
        'limit_price': 86.25,
        'rationale': 'Continue position reduction from 15.8% to 10% target'
    },
    {
        'action': 'BUY',
        'symbol': 'JNJ',
        'shares': 52,
        'limit_price': 153.50,
        'stop_loss': 141.75,
        'rationale': 'Premier healthcare defensive at 15x P/E with 3.1% yield'
    },
    {
        'action': 'BUY',
        'symbol': 'NEE',
        'shares': 83,
        'limit_price': 72.25,
        'stop_loss': 66.50,
        'rationale': 'Renewable leader fills utilities gap, 3.2% yield, 8% growth'
    },
    {
        'action': 'BUY',
        'symbol': 'MSFT',
        'shares': 17,
        'limit_price': 416.00,
        'stop_loss': 385.00,
        'rationale': 'Quality technology anchor, increases beta toward 1.0 target'
    }
]

dee_orders_placed = []
dee_errors = []

for trade in dee_trades:
    try:
        print(f"[{trade['action']}] {trade['symbol']}: {trade['shares']} shares @ ${trade['limit_price']}")
        print(f"   Rationale: {trade['rationale']}")

        # Use market orders for immediate execution (late in day)
        order_data = MarketOrderRequest(
            symbol=trade['symbol'],
            qty=trade['shares'],
            side=OrderSide.BUY if trade['action'] == 'BUY' else OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )

        order = dee_client.submit_order(order_data)
        dee_orders_placed.append({
            'symbol': trade['symbol'],
            'action': trade['action'],
            'shares': trade['shares'],
            'order_id': order.id,
            'status': order.status
        })
        print(f"   [OK] Market order submitted: ID {order.id}")

        if 'stop_loss' in trade:
            print(f"   Stop Loss: ${trade['stop_loss']} (will place after fill)")
        print()

    except Exception as e:
        dee_errors.append({
            'symbol': trade['symbol'],
            'error': str(e)
        })
        print(f"   [ERROR] {str(e)}")
        print()

# ============================================================================
# SHORGAN-BOT PAPER TRADES ($100K Account)
# From TRADE_DECISIONS_2025-11-07.md - Catalyst trades
# ============================================================================

print("=" * 80)
print("SHORGAN-BOT PAPER TRADES ($100K Account)")
print("=" * 80)
print()

shorgan_paper_trades = [
    {
        'action': 'SELL',  # Exit short position
        'symbol': 'FUBO',
        'shares': 1000,
        'limit_price': 3.82,
        'rationale': 'EXIT DEAD MONEY - High cash burn, no near catalyst'
    },
    {
        'action': 'SELL',  # Exit position
        'symbol': 'UNH',
        'shares': 42,
        'limit_price': 322.00,
        'rationale': 'No near catalyst, redeploy capital'
    },
    {
        'action': 'BUY',
        'symbol': 'ARWR',
        'shares': 150,
        'limit_price': 40.20,
        'stop_loss': 36.50,
        'rationale': 'Earnings Nov 7 AMC + partnership potential'
    },
    {
        'action': 'BUY',
        'symbol': 'RGTI',
        'shares': 225,
        'limit_price': 35.20,
        'stop_loss': 31.00,
        'rationale': 'Quantum momentum, gov contracts Nov 14'
    },
    {
        'action': 'BUY',
        'symbol': 'ARQQ',
        'shares': 175,
        'limit_price': 28.80,
        'stop_loss': 25.50,
        'rationale': 'FDA PDUFA Nov 22, high probability approval'
    },
    {
        'action': 'BUY',
        'symbol': 'MDGL',
        'shares': 125,
        'limit_price': 68.50,
        'stop_loss': 62.00,
        'rationale': 'Phase 3 NASH data Nov 15, extreme short interest'
    },
    {
        'action': 'BUY',
        'symbol': 'QSI',
        'shares': 300,
        'limit_price': 19.20,
        'stop_loss': 17.00,
        'rationale': 'Quantum laggard, government summit Nov 14'
    }
]

shorgan_paper_orders_placed = []
shorgan_paper_errors = []

for trade in shorgan_paper_trades:
    try:
        print(f"[{trade['action']}] {trade['symbol']}: {trade['shares']} shares @ ${trade['limit_price']}")
        print(f"   Rationale: {trade['rationale']}")

        # Use market orders for immediate execution
        order_data = MarketOrderRequest(
            symbol=trade['symbol'],
            qty=trade['shares'],
            side=OrderSide.BUY if trade['action'] == 'BUY' else OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )

        order = shorgan_paper_client.submit_order(order_data)
        shorgan_paper_orders_placed.append({
            'symbol': trade['symbol'],
            'action': trade['action'],
            'shares': trade['shares'],
            'order_id': order.id,
            'status': order.status
        })
        print(f"   [OK] Market order submitted: ID {order.id}")

        if 'stop_loss' in trade:
            print(f"   Stop Loss: ${trade['stop_loss']} (will place after fill)")
        print()

    except Exception as e:
        shorgan_paper_errors.append({
            'symbol': trade['symbol'],
            'error': str(e)
        })
        print(f"   [ERROR] {str(e)}")
        print()

# ============================================================================
# SHORGAN-BOT LIVE TRADES ($2K Account)
# From TRADE_DECISIONS_2025-11-07.md - Small-cap catalysts
# ============================================================================

print("=" * 80)
print("SHORGAN-BOT LIVE TRADES ($2K Account)")
print("=" * 80)
print()

shorgan_live_trades = [
    {
        'action': 'SELL',
        'symbol': 'FUBO',
        'shares': 9,
        'limit_price': 4.05,
        'rationale': 'Partial trim at profit (keep 18 shares for Nov 18 catalyst)'
    },
    {
        'action': 'BUY',
        'symbol': 'NERV',
        'shares': 10,
        'limit_price': 8.40,
        'stop_loss': 7.15,
        'rationale': 'Phase 3 depression data Nov 7 AM (URGENT!)'
    },
    {
        'action': 'BUY',
        'symbol': 'STEM',
        'shares': 15,
        'limit_price': 6.65,
        'stop_loss': 5.65,
        'rationale': 'Utility contract announcement Nov 8'
    },
    {
        'action': 'BUY',
        'symbol': 'LCID',
        'shares': 20,
        'limit_price': 3.90,
        'stop_loss': 3.35,
        'rationale': 'Q4 deliveries Nov 13, Gravity SUV catalyst'
    }
]

shorgan_live_orders_placed = []
shorgan_live_errors = []

for trade in shorgan_live_trades:
    try:
        print(f"[{trade['action']}] {trade['symbol']}: {trade['shares']} shares @ ${trade['limit_price']}")
        print(f"   Rationale: {trade['rationale']}")

        # Use market orders for immediate execution
        order_data = MarketOrderRequest(
            symbol=trade['symbol'],
            qty=trade['shares'],
            side=OrderSide.BUY if trade['action'] == 'BUY' else OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )

        order = shorgan_live_client.submit_order(order_data)
        shorgan_live_orders_placed.append({
            'symbol': trade['symbol'],
            'action': trade['action'],
            'shares': trade['shares'],
            'order_id': order.id,
            'status': order.status
        })
        print(f"   [OK] Market order submitted: ID {order.id}")

        if 'stop_loss' in trade:
            print(f"   Stop Loss: ${trade['stop_loss']} (will place after fill)")
        print()

    except Exception as e:
        shorgan_live_errors.append({
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
print(f"SHORGAN-BOT PAPER: {len(shorgan_paper_orders_placed)} orders placed, {len(shorgan_paper_errors)} errors")
for order in shorgan_paper_orders_placed:
    print(f"  - {order['action']} {order['symbol']}: {order['shares']} shares (Order ID: {order['order_id']})")

if shorgan_paper_errors:
    print("\nSHORGAN-BOT PAPER Errors:")
    for error in shorgan_paper_errors:
        print(f"  - {error['symbol']}: {error['error']}")

print()
print(f"SHORGAN-BOT LIVE: {len(shorgan_live_orders_placed)} orders placed, {len(shorgan_live_errors)} errors")
for order in shorgan_live_orders_placed:
    print(f"  - {order['action']} {order['symbol']}: {order['shares']} shares (Order ID: {order['order_id']})")

if shorgan_live_errors:
    print("\nSHORGAN-BOT LIVE Errors:")
    for error in shorgan_live_errors:
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
print("⚠️  WARNING: Trades executed from 3-day-old research (Nov 7)")
print("   Prices and catalysts may have changed significantly")
print("   Some catalysts (NERV Nov 7 AM) may have already occurred")
print("=" * 80)
