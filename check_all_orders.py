#!/usr/bin/env python3
"""Check ALL orders including closed ones"""
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import QueryOrderStatus

load_dotenv()

print("\n" + "="*70)
print("ALL ORDERS (INCLUDING PENDING/FILLED/CANCELED)")
print("="*70)

# SHORGAN-BOT
print("\nSHORGAN-BOT Orders:")
shorgan_client = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY_SHORGAN'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    paper=True
)

try:
    # Get ALL orders (no status filter to get everything)
    all_orders = shorgan_client.get_orders()
    today_orders = [o for o in all_orders if str(o.submitted_at).startswith('2025-10-01')]

    print(f"  Total orders today: {len(today_orders)}")
    for order in sorted(today_orders, key=lambda x: x.submitted_at, reverse=True)[:15]:
        limit_price = float(order.limit_price) if order.limit_price else 0.0
        print(f"  * {order.symbol:6} {str(order.side):10} {order.qty:6} @ ${limit_price:8.2f} - {order.status}")
except Exception as e:
    print(f"  Error: {e}")

# DEE-BOT
print("\nDEE-BOT Orders:")
dee_client = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY_DEE'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_DEE'),
    paper=True
)

try:
    all_orders = dee_client.get_orders()
    today_orders = [o for o in all_orders if str(o.submitted_at).startswith('2025-10-01')]

    print(f"  Total orders today: {len(today_orders)}")
    for order in sorted(today_orders, key=lambda x: x.submitted_at, reverse=True)[:15]:
        limit_price = float(order.limit_price) if order.limit_price else 0.0
        print(f"  * {order.symbol:6} {str(order.side):10} {order.qty:6} @ ${limit_price:8.2f} - {order.status}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*70)
