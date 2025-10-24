#!/usr/bin/env python3
"""Test DEE-BOT Alpaca API connection with existing keys"""

from alpaca.trading.client import TradingClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test DEE-BOT keys (existing in .env)
api_key_dee = os.getenv('ALPACA_API_KEY_DEE')
secret_key_dee = os.getenv('ALPACA_SECRET_KEY_DEE')

# Test SHORGAN-BOT keys (existing in .env)
api_key_shorgan = os.getenv('ALPACA_API_KEY_SHORGAN')
secret_key_shorgan = os.getenv('ALPACA_SECRET_KEY_SHORGAN')

print("=" * 80)
print("TESTING ALPACA API CONNECTIONS - BOTH BOTS".center(80))
print("=" * 80)

# Test DEE-BOT
print("\n[1/2] Testing DEE-BOT Alpaca API...")
print(f"      API Key: {api_key_dee}")
try:
    client_dee = TradingClient(api_key_dee, secret_key_dee, paper=True)
    account_dee = client_dee.get_account()
    print('      [SUCCESS] DEE-BOT Alpaca API connection working')
    print(f'      Account: {account_dee.account_number}')
    print(f'      Equity: ${float(account_dee.equity):,.2f}')
    print(f'      Cash: ${float(account_dee.cash):,.2f}')
except Exception as e:
    print(f'      [ERROR] DEE-BOT API failed: {e}')
    print('\nTroubleshooting:')
    print('1. Verify DEE-BOT API keys at: https://app.alpaca.markets/paper/dashboard/overview')
    print('2. Make sure you are using PAPER trading keys')
    print('3. Regenerate keys if needed')

# Test SHORGAN-BOT
print("\n[2/2] Testing SHORGAN-BOT Alpaca API...")
print(f"      API Key: {api_key_shorgan}")
try:
    client_shorgan = TradingClient(api_key_shorgan, secret_key_shorgan, paper=True)
    account_shorgan = client_shorgan.get_account()
    print('      [SUCCESS] SHORGAN-BOT Alpaca API connection working')
    print(f'      Account: {account_shorgan.account_number}')
    print(f'      Equity: ${float(account_shorgan.equity):,.2f}')
    print(f'      Cash: ${float(account_shorgan.cash):,.2f}')
except Exception as e:
    print(f'      [ERROR] SHORGAN-BOT API failed: {e}')
    print('\nTroubleshooting:')
    print('1. Verify SHORGAN-BOT API keys at: https://app.alpaca.markets/paper/dashboard/overview')
    print('2. Make sure you are using PAPER trading keys')
    print('3. Regenerate keys if needed')

print("\n" + "=" * 80)
