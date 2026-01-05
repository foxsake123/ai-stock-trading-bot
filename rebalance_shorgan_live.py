#!/usr/bin/env python
"""Rebalance SHORGAN Live: Close worst positions, buy top ideas."""

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import os
from dotenv import load_dotenv
import time

load_dotenv()

client = TradingClient(
    os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'),
    os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'),
    paper=False
)

print("="*60)
print("SHORGAN LIVE REBALANCING")
print("="*60)

# Check account
account = client.get_account()
print(f"\nAccount Value: ${float(account.equity):,.2f}")
print(f"Cash: ${float(account.cash):,.2f}")
print(f"Buying Power: ${float(account.buying_power):,.2f}")

# STEP 1: Close worst positions
print("\n" + "="*60)
print("STEP 1: CLOSING WORST POSITIONS")
print("="*60)

sells = [
    # (symbol, qty, reason)
    ("PRTA", 29, "Worst performer, no catalyst"),
    ("DNLI", 17, "Underperforming, cut losses"),
    ("VKTX", 12, "Trimming loser"),
    ("NKE", 3, "Cover short position (BUY to close)"),
]

for symbol, qty, reason in sells:
    try:
        # Check if position exists
        try:
            position = client.get_open_position(symbol)
            current_qty = int(float(position.qty))
            print(f"\n[{symbol}] Current position: {current_qty} shares")
        except:
            print(f"\n[{symbol}] No position found, skipping")
            continue

        # Determine side based on current position
        if current_qty > 0:
            # Long position - sell to close
            side = OrderSide.SELL
            order_qty = min(abs(qty), abs(current_qty))
        else:
            # Short position - buy to cover
            side = OrderSide.BUY
            order_qty = min(abs(qty), abs(current_qty))

        print(f"[{symbol}] {side.value.upper()} {order_qty} shares - {reason}")

        order_request = MarketOrderRequest(
            symbol=symbol,
            qty=order_qty,
            side=side,
            time_in_force=TimeInForce.DAY
        )
        order = client.submit_order(order_request)
        print(f"[{symbol}] SUCCESS - Order ID: {order.id}")
        time.sleep(1)

    except Exception as e:
        print(f"[{symbol}] ERROR: {e}")

# Wait for sells to settle
print("\n[*] Waiting 5 seconds for orders to fill...")
time.sleep(5)

# Check updated cash
account = client.get_account()
print(f"\nUpdated Cash: ${float(account.cash):,.2f}")
print(f"Updated Buying Power: ${float(account.buying_power):,.2f}")

# STEP 2: Buy top ideas (only if we have cash)
print("\n" + "="*60)
print("STEP 2: BUYING TOP IDEAS FROM RESEARCH")
print("="*60)

buys = [
    # (symbol, qty, limit_price, reason)
    ("HIMS", 5, 34.50, "Telehealth growth, earnings catalyst"),
    ("MRNA", 6, 31.00, "Biotech rebound, oversold"),
]

# Refresh account
account = client.get_account()
cash = float(account.cash)

if cash > 100:
    for symbol, qty, limit_price, reason in buys:
        try:
            cost = qty * limit_price
            if cost > cash:
                print(f"\n[{symbol}] SKIP - Not enough cash (need ${cost:.2f}, have ${cash:.2f})")
                continue

            print(f"\n[{symbol}] BUY {qty} shares @ ${limit_price} limit - {reason}")

            order_request = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
                limit_price=limit_price
            )
            order = client.submit_order(order_request)
            print(f"[{symbol}] SUCCESS - Order ID: {order.id}")
            cash -= cost
            time.sleep(1)

        except Exception as e:
            print(f"[{symbol}] ERROR: {e}")
else:
    print(f"\n[!] Not enough cash for buys (${cash:.2f})")

# Final summary
print("\n" + "="*60)
print("REBALANCING COMPLETE")
print("="*60)
account = client.get_account()
positions = client.get_all_positions()
print(f"Account Value: ${float(account.equity):,.2f}")
print(f"Cash: ${float(account.cash):,.2f}")
print(f"Position Count: {len(positions)}")
