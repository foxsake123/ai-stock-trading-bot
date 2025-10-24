#!/usr/bin/env python3
"""Test Alpaca API connection"""

from alpaca.trading.client import TradingClient

# Test the API keys
api_key = 'CKFO1ITKSVL7H902VBS2'
secret_key = 'RF2ytLXhWqOB01s77fvIWFwI0NH6bY3DAFwLKq1c'

try:
    client = TradingClient(api_key, secret_key, paper=True)
    account = client.get_account()
    print('SUCCESS: Alpaca API connection working')
    print(f'Account: {account.account_number}')
    print(f'Equity: ${float(account.equity):,.2f}')
    print(f'Cash: ${float(account.cash):,.2f}')
except Exception as e:
    print(f'ERROR: {e}')
    print('\nTroubleshooting:')
    print('1. Verify your API keys at: https://app.alpaca.markets/paper/dashboard/overview')
    print('2. Make sure you are using PAPER trading keys')
    print('3. Regenerate keys if needed')
