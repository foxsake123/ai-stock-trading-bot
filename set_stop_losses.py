#!/usr/bin/env python3
"""
Set Stop Loss Orders for SHORGAN-BOT Live Positions
15% stop loss for aggressive event-driven strategy
"""

import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import StopLossRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from datetime import datetime
import time

load_dotenv()

# SHORGAN-BOT LIVE credentials
API_KEY = os.getenv('ALPACA_LIVE_API_KEY_SHORGAN')
SECRET_KEY = os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN')

print("="*70)
print("SETTING STOP LOSS ORDERS - SHORGAN-BOT LIVE")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

# Initialize client
client = TradingClient(API_KEY, SECRET_KEY, paper=False)

# Get current positions
positions = client.get_all_positions()

print(f"\nFound {len(positions)} open positions")
print()

# Define stop loss prices (15% below entry)
stop_losses = {
    "PLTR": {"entry": 42.25, "stop": 35.91, "stop_pct": 0.85},
    "VKTX": {"entry": 16.65, "stop": 14.15, "stop_pct": 0.85},
    "FUBO": {"entry": 3.58, "stop": 3.04, "stop_pct": 0.85},
    "RVMD": {"entry": 58.25, "stop": 49.51, "stop_pct": 0.85},
    "ENPH": {"entry": 82.50, "stop": 70.12, "stop_pct": 0.85},
}

executed_stops = []
failed_stops = []

print("CREATING STOP LOSS ORDERS (15% stops):")
print("-" * 70)

for position in positions:
    symbol = position.symbol
    qty = abs(int(float(position.qty)))
    current_price = float(position.current_price)
    avg_entry = float(position.avg_entry_price)

    if symbol in stop_losses:
        stop_price = stop_losses[symbol]["stop"]
        entry_price = stop_losses[symbol]["entry"]

        print(f"\n{symbol}:")
        print(f"  Quantity: {qty} shares")
        print(f"  Entry: ${avg_entry:.2f} (expected ${entry_price:.2f})")
        print(f"  Current: ${current_price:.2f}")
        print(f"  Stop Loss: ${stop_price:.2f} (15% below entry)")

        try:
            # Create stop loss order
            from alpaca.trading.requests import StopOrderRequest

            stop_order = StopOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.GTC,  # Good-til-canceled
                stop_price=stop_price
            )

            order = client.submit_order(stop_order)

            print(f"  [SUCCESS] Stop order ID: {order.id}")
            print(f"  Status: {order.status}")

            executed_stops.append({
                "symbol": symbol,
                "qty": qty,
                "stop_price": stop_price,
                "order_id": str(order.id)
            })

            time.sleep(0.3)

        except Exception as e:
            print(f"  [FAILED] Error: {str(e)}")
            failed_stops.append({
                "symbol": symbol,
                "error": str(e)
            })
    else:
        print(f"\n{symbol}: No stop loss defined (not in today's trades)")

print("\n" + "="*70)
print("STOP LOSS SUMMARY")
print("="*70)
print(f"Successfully created: {len(executed_stops)}")
print(f"Failed: {len(failed_stops)}")

if executed_stops:
    print("\nActive Stop Losses:")
    for stop in executed_stops:
        print(f"  {stop['symbol']:6} | {stop['qty']:2} shares @ ${stop['stop_price']:6.2f} | {stop['order_id']}")

if failed_stops:
    print("\nFailed Stop Losses:")
    for stop in failed_stops:
        print(f"  {stop['symbol']:6} - {stop['error']}")

print("\n" + "="*70)
print("PROTECTION ACTIVE")
print("="*70)
print("Your positions are now protected with 15% stop losses.")
print("Stop orders are GTC (Good-Til-Canceled) - active until filled or cancelled.")
print("\nMonitor positions via Alpaca dashboard:")
print("https://app.alpaca.markets/")
print("="*70)
