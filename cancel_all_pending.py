#!/usr/bin/env python3
"""Cancel all remaining pending orders"""
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

load_dotenv()

# Initialize clients
shorgan_client = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY_SHORGAN'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    paper=True
)

dee_client = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY_DEE'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_DEE'),
    paper=True
)

print("\n" + "="*70)
print("CANCELING ALL REMAINING PENDING ORDERS")
print("="*70)

canceled_count = 0
error_count = 0

# Cancel SHORGAN orders
print("\nSHORGAN-BOT:")
shorgan_orders = [o for o in shorgan_client.get_orders() if str(o.submitted_at).startswith('2025-10-01')]
for order in shorgan_orders:
    try:
        print(f"  Canceling {order.symbol}: {order.qty} @ ${order.limit_price}... ", end='')
        shorgan_client.cancel_order_by_id(order.id)
        print(f"[+] CANCELED")
        canceled_count += 1
    except Exception as e:
        print(f"[-] ERROR: {e}")
        error_count += 1

# Cancel DEE orders
print("\nDEE-BOT:")
dee_orders = [o for o in dee_client.get_orders() if str(o.submitted_at).startswith('2025-10-01')]
for order in dee_orders:
    try:
        print(f"  Canceling {order.symbol}: {order.qty} @ ${order.limit_price}... ", end='')
        dee_client.cancel_order_by_id(order.id)
        print(f"[+] CANCELED")
        canceled_count += 1
    except Exception as e:
        print(f"[-] ERROR: {e}")
        error_count += 1

print("\n" + "="*70)
print(f"CANCELLATION SUMMARY")
print("="*70)
print(f"Successfully Canceled: {canceled_count}")
print(f"Errors: {error_count}")
print("="*70 + "\n")
