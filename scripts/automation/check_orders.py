"""
Check open orders and positions in SHORGAN-BOT account
"""

import alpaca_trade_api as tradeapi

# SHORGAN-BOT credentials
API_KEY = 'PKJRLSB2MFEJUSK6UK2E'
SECRET_KEY = 'QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic'
BASE_URL = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

# Check open orders
orders = api.list_orders(status='open')
print("="*60)
print("OPEN ORDERS")
print("="*60)
if orders:
    for order in orders:
        print(f"{order.symbol}: {order.side} {order.qty} @ {order.order_type}")
else:
    print("No open orders")

# Check recently filled orders
filled = api.list_orders(status='filled', limit=10)
print("\n" + "="*60)
print("RECENT FILLED ORDERS")
print("="*60)
if filled:
    for order in filled[:5]:
        print(f"{order.symbol}: {order.side} {order.qty} @ {order.filled_avg_price or 'market'} - {order.filled_at}")
else:
    print("No recent filled orders")

# Check positions with detailed info
print("\n" + "="*60)
print("DETAILED POSITION INFO")
print("="*60)
positions = api.list_positions()
for pos in positions:
    if pos.symbol in ['CBRL', 'RGTI', 'ORCL', 'INCY', 'KSS']:
        print(f"\n{pos.symbol}:")
        print(f"  Qty: {pos.qty}")
        print(f"  Qty Available: {pos.qty_available if hasattr(pos, 'qty_available') else 'N/A'}")
        print(f"  Market Value: ${float(pos.market_value):.2f}")
        print(f"  Avg Entry: ${float(pos.avg_entry_price):.2f}")
        print(f"  Unrealized P&L: ${float(pos.unrealized_pl):.2f}")

# Check if positions are available to trade
print("\n" + "="*60)
print("CHECKING POSITION AVAILABILITY")
print("="*60)

# Get CBRL position specifically
try:
    cbrl_pos = api.get_position('CBRL')
    print(f"CBRL position found: {cbrl_pos.qty} shares")
    print(f"  Can sell: {cbrl_pos.qty_available if hasattr(cbrl_pos, 'qty_available') else cbrl_pos.qty}")
except:
    print("CBRL position not found")

try:
    rgti_pos = api.get_position('RGTI')
    print(f"RGTI position found: {rgti_pos.qty} shares")
    print(f"  Can sell: {rgti_pos.qty_available if hasattr(rgti_pos, 'qty_available') else rgti_pos.qty}")
except:
    print("RGTI position not found")

try:
    orcl_pos = api.get_position('ORCL')
    print(f"ORCL position found: {orcl_pos.qty} shares")
    print(f"  Can sell: {orcl_pos.qty_available if hasattr(orcl_pos, 'qty_available') else orcl_pos.qty}")
except:
    print("ORCL position not found")