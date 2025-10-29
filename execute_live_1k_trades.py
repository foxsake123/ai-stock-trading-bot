#!/usr/bin/env python3
"""
Execute SHORGAN-BOT Live Trades - $1K Account
Manual execution for Oct 28, 2025
"""

import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from datetime import datetime
import time

load_dotenv()

# SHORGAN-BOT LIVE credentials
API_KEY = os.getenv('ALPACA_LIVE_API_KEY_SHORGAN')
SECRET_KEY = os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN')

print("="*70)
print("SHORGAN-BOT LIVE TRADING - $1K ACCOUNT")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

# Initialize client
client = TradingClient(API_KEY, SECRET_KEY, paper=False)

# Get account info
account = client.get_account()
print(f"\nAccount Status: {account.status}")
print(f"Buying Power: ${float(account.buying_power):,.2f}")
print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
print()

# Define trades (calculated for $1K account)
trades = [
    {"symbol": "PLTR", "shares": 2, "price": 42.25, "catalyst": "Earnings Nov 5"},
    {"symbol": "VKTX", "shares": 6, "price": 16.65, "catalyst": "Data Oct 30"},
    {"symbol": "FUBO", "shares": 27, "price": 3.58, "catalyst": "Earnings Nov 1"},
    {"symbol": "RVMD", "shares": 1, "price": 58.25, "catalyst": "Phase 3 Nov 5"},
    {"symbol": "ENPH", "shares": 1, "price": 82.50, "catalyst": "Earnings Oct 29"},
]

executed = []
failed = []

print("EXECUTING 5 LIVE TRADES:")
print("-" * 70)

for i, trade in enumerate(trades, 1):
    symbol = trade['symbol']
    shares = trade['shares']
    limit_price = trade['price']
    catalyst = trade['catalyst']

    print(f"\n[{i}/5] {symbol}: BUY {shares} shares @ ${limit_price:.2f}")
    print(f"      Catalyst: {catalyst}")
    print(f"      Position Value: ${shares * limit_price:.2f}")

    try:
        # Use limit order at current price
        order_data = LimitOrderRequest(
            symbol=symbol,
            qty=shares,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
            limit_price=limit_price
        )

        order = client.submit_order(order_data)

        print(f"      [SUCCESS] Order ID: {order.id}")
        print(f"      Status: {order.status}")

        executed.append({
            "symbol": symbol,
            "shares": shares,
            "price": limit_price,
            "order_id": str(order.id),
            "catalyst": catalyst
        })

        # Small delay between orders
        time.sleep(0.5)

    except Exception as e:
        print(f"      [FAILED] Error: {str(e)}")
        failed.append({
            "symbol": symbol,
            "shares": shares,
            "error": str(e)
        })

print("\n" + "="*70)
print("EXECUTION SUMMARY")
print("="*70)
print(f"Successful: {len(executed)}")
print(f"Failed: {len(failed)}")

if executed:
    print("\nExecuted Trades:")
    total_value = 0
    for t in executed:
        value = t['shares'] * t['price']
        total_value += value
        print(f"  {t['symbol']:6} | {t['shares']:2} shares @ ${t['price']:6.2f} = ${value:6.2f} | {t['order_id']}")
    print(f"\nTotal Deployed: ${total_value:.2f}")

if failed:
    print("\nFailed Trades:")
    for t in failed:
        print(f"  {t['symbol']:6} | {t['shares']:2} shares - {t['error']}")

print("\n" + "="*70)
print("NEXT STEPS:")
print("="*70)
print("1. Check Alpaca dashboard for order fills")
print("2. Place stop loss orders for filled positions:")
for t in executed:
    stop_price = t['price'] * 0.85  # 15% stop loss
    print(f"   {t['symbol']}: Stop @ ${stop_price:.2f} (15% below entry)")
print("="*70)
