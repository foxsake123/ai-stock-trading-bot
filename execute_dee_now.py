import os
from datetime import datetime
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

load_dotenv()

api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_SECRET_KEY'),
    os.getenv('ALPACA_BASE_URL'),
    api_version='v2'
)

print("=" * 80)
print("EXECUTING DEE-BOT ORDERS - OCTOBER 14, 2025")
print("=" * 80)
print()

orders = [
    {'symbol': 'ED', 'qty': 100, 'limit': 100.81},
    {'symbol': 'WMT', 'qty': 45, 'limit': 160.00},
    {'symbol': 'COST', 'qty': 5, 'limit': 915.00}
]

results = {'successful': [], 'failed': []}

for order in orders:
    try:
        print(f"Submitting: BUY {order['qty']} {order['symbol']} @ ${order['limit']:.2f}...")

        submitted = api.submit_order(
            symbol=order['symbol'],
            qty=order['qty'],
            side='buy',
            type='limit',
            time_in_force='day',
            limit_price=order['limit']
        )

        print(f"[OK] {order['symbol']} submitted: {submitted.id}")
        results['successful'].append((order['symbol'], order['qty'], order['limit'], submitted.id))

    except Exception as e:
        print(f"[FAILED] {order['symbol']}: {e}")
        results['failed'].append((order['symbol'], order['qty'], order['limit'], str(e)))

print()
print("=" * 80)
print("EXECUTION SUMMARY")
print("=" * 80)
print(f"Successful: {len(results['successful'])}/3")
print(f"Failed: {len(results['failed'])}/3")
print()

if results['successful']:
    print("EXECUTED:")
    for symbol, qty, limit, order_id in results['successful']:
        print(f"  [OK] BUY {qty} {symbol} @ ${limit:.2f} (ID: {order_id})")

if results['failed']:
    print()
    print("FAILED:")
    for symbol, qty, limit, error in results['failed']:
        print(f"  [FAIL] {symbol}: {error}")

print()
print("Next: Monitor fills in Alpaca dashboard")
