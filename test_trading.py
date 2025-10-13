import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_SECRET_KEY'),
    os.getenv('ALPACA_BASE_URL'),
    api_version='v2'
)

try:
    acc = api.get_account()
    print(f'Account: {acc.status}')
    print(f'Cash: ${float(acc.cash):,.2f}')
    print(f'Trading Blocked: {acc.trading_blocked}')
    print()

    if acc.trading_blocked:
        print('[FAIL] Trading is blocked')
        exit(1)

    print('Testing order submission...')
    order = api.submit_order(
        symbol='SPY',
        qty=1,
        side='buy',
        type='limit',
        time_in_force='day',
        limit_price=1.00
    )
    print(f'[OK] Test order submitted: {order.id}')
    api.cancel_order(order.id)
    print('[OK] Test order cancelled')
    print()
    print('[SUCCESS] Trading permissions verified!')

except Exception as e:
    print(f'[FAIL] {e}')
    exit(1)
