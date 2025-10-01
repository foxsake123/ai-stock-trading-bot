#!/usr/bin/env python3
"""Quick check of today's orders"""
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from datetime import datetime

load_dotenv()

print("\n" + "="*70)
print("CHECKING TODAY'S ORDERS")
print("="*70)

# Check SHORGAN-BOT
print("\nSHORGAN-BOT Orders:")
shorgan_client = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY_SHORGAN'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    paper=True
)

try:
    shorgan_orders = list(shorgan_client.get_orders())
    today_orders = [o for o in shorgan_orders if str(o.submitted_at).startswith('2025-10-01')]
    print(f"  Total orders today: {len(today_orders)}")
    for order in today_orders[:10]:
        print(f"  * {order.symbol:6} {str(order.side):4} {order.qty:6} @ ${order.limit_price:8} - {order.status}")
except Exception as e:
    print(f"  Error: {e}")

# Check DEE-BOT
print("\nDEE-BOT Orders:")
dee_client = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY_DEE'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_DEE'),
    paper=True
)

try:
    dee_orders = list(dee_client.get_orders())
    today_orders = [o for o in dee_orders if str(o.submitted_at).startswith('2025-10-01')]
    print(f"  Total orders today: {len(today_orders)}")
    for order in today_orders[:10]:
        print(f"  * {order.symbol:6} {str(order.side):4} {order.qty:6} @ ${order.limit_price:8} - {order.status}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*70)
