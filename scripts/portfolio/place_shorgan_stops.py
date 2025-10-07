#!/usr/bin/env python3
"""
Place Stop-Loss Orders for SHORGAN-BOT Oct 7 Positions
ARQT, HIMS, WOLF - GTC stop-loss orders
"""

import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

shorgan_api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY_SHORGAN'),
    os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    'https://paper-api.alpaca.markets',
    api_version='v2'
)

def place_stop_loss(symbol, qty, stop_price):
    """Place a GTC stop-loss order"""
    try:
        print(f"\n[PLACING STOP] {symbol}: STOP {qty} @ ${stop_price} (GTC)")

        order = shorgan_api.submit_order(
            symbol=symbol,
            qty=qty,
            side='sell',
            type='stop',
            time_in_force='gtc',
            stop_price=str(stop_price)
        )

        print(f"  [SUCCESS] Stop order placed: {order.id}")
        print(f"  Status: {order.status}")
        return True

    except Exception as e:
        print(f"  [ERROR] Failed to place stop: {e}")
        return False

def main():
    """Place all stop-loss orders"""
    print("="*80)
    print("SHORGAN-BOT STOP-LOSS ORDER PLACEMENT")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print("="*80)

    # Check current positions first
    print("\nVerifying positions...")
    try:
        positions = shorgan_api.list_positions()
        position_dict = {p.symbol: int(float(p.qty)) for p in positions}

        print(f"\nCurrent long positions:")
        for symbol in ['ARQT', 'HIMS', 'WOLF']:
            qty = position_dict.get(symbol, 0)
            if qty > 0:
                print(f"  {symbol}: {qty} shares")
            else:
                print(f"  {symbol}: NO POSITION")
    except Exception as e:
        print(f"[ERROR] Could not fetch positions: {e}")
        return

    # Define stop-loss orders
    stops = [
        ('ARQT', 150, 16.50),  # FDA Oct 13 - protect downside
        ('HIMS', 37, 49.00),   # Short squeeze - protect gains
        ('WOLF', 96, 22.00)    # Delisting Oct 10 - protect downside
    ]

    print("\n" + "="*80)
    print("PLACING STOP-LOSS ORDERS")
    print("="*80)

    success_count = 0

    for symbol, qty, stop_price in stops:
        current_qty = position_dict.get(symbol, 0)

        if current_qty < qty:
            print(f"\n[WARNING] {symbol}: Position size {current_qty} < order qty {qty}")
            print(f"  Adjusting stop order to {current_qty} shares")
            qty = current_qty

        if qty > 0:
            if place_stop_loss(symbol, qty, stop_price):
                success_count += 1
        else:
            print(f"\n[SKIP] {symbol}: No position to protect")

    # Summary
    print("\n" + "="*80)
    print("STOP-LOSS PLACEMENT SUMMARY")
    print("="*80)
    print(f"\nSuccessfully placed: {success_count}/3 stop orders")

    # List all open orders
    print("\n[VERIFICATION] Checking open orders...")
    orders = shorgan_api.list_orders(status='open')

    if orders:
        print(f"\nOpen stop orders: {len(orders)}")
        for order in orders:
            print(f"  {order.symbol}: {order.side.upper()} {order.qty} @ ${order.stop_price} ({order.type}, {order.time_in_force})")
    else:
        print("\nNo open orders found")

    print("\n" + "="*80)
    print("STOP-LOSS PROTECTION ACTIVE")
    print("="*80)

if __name__ == "__main__":
    main()
