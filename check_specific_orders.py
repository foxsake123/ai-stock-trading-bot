#!/usr/bin/env python3
"""Check specific order IDs"""
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

load_dotenv()

print("\n" + "="*70)
print("CHECKING SPECIFIC ORDERS BY ID")
print("="*70)

# Initialize clients
dee_client = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY_DEE'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_DEE'),
    paper=True
)

shorgan_client = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY_SHORGAN'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    paper=True
)

# Order IDs from recent execution
orders_to_check = [
    ('DEE', 'fdf8fef2-8f95-49d4-af39-24713280e0b2', 'CL'),
    ('SHORGAN', 'fce099b6-72b0-42c3-bc01-6bc8bd8e7758', 'GKOS'),
    ('SHORGAN', '5ad5a8b9-f990-4a63-9d41-ffc9405586fb', 'SNDX'),
    ('SHORGAN', 'dbdaac7a-49c7-471b-96cf-048ae0ab20a2', 'OPEN'),
    ('SHORGAN', '2517db9a-8936-4964-b012-90f76c06feed', 'FUBO'),
]

for bot, order_id, symbol in orders_to_check:
    client = dee_client if bot == 'DEE' else shorgan_client
    try:
        order = client.get_order_by_id(order_id)
        limit_price = float(order.limit_price) if order.limit_price else 0.0
        print(f"{bot:8} | {symbol:6} | {order.qty:6} @ ${limit_price:6.2f} | {order.status}")
    except Exception as e:
        print(f"{bot:8} | {symbol:6} | ERROR: {e}")

print("\n" + "="*70)
