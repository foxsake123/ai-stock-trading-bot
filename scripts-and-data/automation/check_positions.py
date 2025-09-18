"""
Check current positions in SHORGAN-BOT account
"""

import alpaca_trade_api as tradeapi

# SHORGAN-BOT credentials
API_KEY = 'PKJRLSB2MFEJUSK6UK2E'
SECRET_KEY = 'QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic'
BASE_URL = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

# Get positions
positions = api.list_positions()

print("="*60)
print("SHORGAN-BOT ACTUAL POSITIONS")
print("="*60)

if not positions:
    print("No positions found in account")
else:
    for position in positions:
        qty = float(position.qty)
        symbol = position.symbol
        market_value = float(position.market_value)
        avg_entry = float(position.avg_entry_price)
        current = float(position.current_price) if hasattr(position, 'current_price') else 0
        pl = float(position.unrealized_pl)
        pl_pct = float(position.unrealized_plpc) * 100

        print(f"{symbol:6} {int(qty):5} shares @ ${avg_entry:7.2f} | Value: ${market_value:10.2f} | P&L: ${pl:+8.2f} ({pl_pct:+.1f}%)")

# Check account info
account = api.get_account()
print("\n" + "="*60)
print("ACCOUNT SUMMARY")
print("="*60)
print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
print(f"Cash: ${float(account.cash):,.2f}")
print(f"Buying Power: ${float(account.buying_power):,.2f}")