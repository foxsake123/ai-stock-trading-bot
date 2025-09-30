from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
import os

load_dotenv()

# DEE-BOT
dee = TradingClient(os.getenv('ALPACA_API_KEY_DEE'), os.getenv('ALPACA_SECRET_KEY_DEE'), paper=True)
print("="*60)
print("DEE-BOT OPEN ORDERS")
print("="*60)
orders = dee.get_orders()
if orders:
    for order in orders:
        print(f"{order.symbol}: {order.side} {order.qty} @ ${order.limit_price} - Status: {order.status}")
else:
    print("No open orders")

# SHORGAN
shorgan = TradingClient(os.getenv('ALPACA_API_KEY_SHORGAN'), os.getenv('ALPACA_SECRET_KEY_SHORGAN'), paper=True)
print("\n" + "="*60)
print("SHORGAN-BOT OPEN ORDERS")
print("="*60)
orders = shorgan.get_orders()
if orders:
    for order in orders:
        print(f"{order.symbol}: {order.side} {order.qty} @ ${order.limit_price} - Status: {order.status}")
else:
    print("No open orders")