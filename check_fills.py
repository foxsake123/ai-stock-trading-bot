"""Check today's order fills across all accounts"""
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
load_dotenv()

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus

def check_account(name, api_key, secret_key, paper=True):
    print('=' * 60)
    print(f'{name} ORDER STATUS')
    print('=' * 60)

    client = TradingClient(api_key, secret_key, paper=paper)

    # Get recent orders
    request = GetOrdersRequest(status=QueryOrderStatus.ALL, after=datetime.now() - timedelta(days=1))
    orders = client.get_orders(filter=request)

    if not orders:
        print("No orders in last 24 hours")
    else:
        for o in orders:
            fill_price = f"${o.filled_avg_price}" if o.filled_avg_price else 'N/A'
            print(f"{o.side.name:4} {o.symbol:6} | Qty: {o.qty:>5} | Status: {o.status.name:12} | Fill: {fill_price}")

    acct = client.get_account()
    print(f"\nPortfolio Value: ${float(acct.portfolio_value):,.2f}")
    print(f"Cash: ${float(acct.cash):,.2f}")
    print()

# Check all accounts
check_account("DEE-BOT",
              os.getenv('ALPACA_API_KEY_DEE'),
              os.getenv('ALPACA_SECRET_KEY_DEE'),
              paper=True)

check_account("SHORGAN LIVE",
              os.getenv('ALPACA_API_KEY_SHORGAN_LIVE'),
              os.getenv('ALPACA_SECRET_KEY_SHORGAN_LIVE'),
              paper=False)

check_account("SHORGAN PAPER",
              os.getenv('ALPACA_API_KEY_SHORGAN'),
              os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
              paper=True)
