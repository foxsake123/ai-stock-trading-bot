"""
Fix stop orders for KSS and INCY
"""

import alpaca_trade_api as tradeapi
import time

# SHORGAN-BOT credentials
API_KEY = 'PKJRLSB2MFEJUSK6UK2E'
SECRET_KEY = 'QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic'
BASE_URL = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

# Cancel existing stop orders for KSS and INCY
orders = api.list_orders(status='open')
for order in orders:
    if order.symbol in ['KSS', 'INCY'] and order.order_type in ['stop', 'stop_limit']:
        try:
            api.cancel_order(order.id)
            print(f"Cancelled stop order for {order.symbol}")
            time.sleep(0.5)
        except:
            pass

# Wait for orders to clear
time.sleep(2)

# Set new stop orders
stops = {
    'KSS': {'qty': 90, 'stop': 15.18},
    'INCY': {'qty': 61, 'stop': 77.25}
}

for symbol, params in stops.items():
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=params['qty'],
            side='sell',
            type='stop',
            stop_price=params['stop'],
            time_in_force='gtc'
        )
        print(f"[STOP SET] {symbol}: {params['qty']} shares @ ${params['stop']:.2f}")
    except Exception as e:
        print(f"[ERROR] {symbol}: {e}")

print("\nAll stop orders updated successfully!")