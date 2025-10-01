#!/usr/bin/env python3
"""Cancel OPEN limit order"""
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

load_dotenv()

# Initialize SHORGAN client
shorgan_client = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY_SHORGAN'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    paper=True
)

print("\n" + "="*70)
print("CANCELING OPEN LIMIT ORDER")
print("="*70)

# Order ID from earlier check
order_id = "dbdaac7a-49c7-471b-96cf-048ae0ab20a2"

try:
    # Get order details before canceling
    order = shorgan_client.get_order_by_id(order_id)
    print(f"\nOrder Details:")
    print(f"  Symbol: {order.symbol}")
    print(f"  Quantity: {order.qty}")
    print(f"  Limit Price: ${order.limit_price}")
    print(f"  Status: {order.status}")

    # Cancel the order
    shorgan_client.cancel_order_by_id(order_id)
    print(f"\n[+] Order {order_id} canceled successfully")

    # Verify cancellation
    updated_order = shorgan_client.get_order_by_id(order_id)
    print(f"[+] New Status: {updated_order.status}")

except Exception as e:
    print(f"\n[-] Error canceling order: {e}")

print("\n" + "="*70)

# Show remaining active orders
print("\nRemaining Active SHORGAN-BOT Orders:")
try:
    active_orders = [o for o in shorgan_client.get_orders() if str(o.submitted_at).startswith('2025-10-01')]
    if active_orders:
        for order in active_orders:
            limit_price = float(order.limit_price) if order.limit_price else 0.0
            print(f"  * {order.symbol:6} {str(order.side):10} {order.qty:6} @ ${limit_price:6.2f} - {order.status}")
    else:
        print(f"  No active orders from today")
except Exception as e:
    print(f"  Error: {e}")

print("="*70 + "\n")
