from alpaca.trading.client import TradingClient
import os
from dotenv import load_dotenv

load_dotenv()

# DEE-BOT
dee_client = TradingClient(os.getenv('ALPACA_API_KEY_DEE'), os.getenv('ALPACA_SECRET_KEY_DEE'), paper=True)
dee_acc = dee_client.get_account()
print("="*60)
print("DEE-BOT ACCOUNT")
print("="*60)
print(f"Cash: ${float(dee_acc.cash):,.2f}")
print(f"Portfolio Value: ${float(dee_acc.portfolio_value):,.2f}")
print(f"Buying Power: ${float(dee_acc.buying_power):,.2f}")
print(f"Equity: ${float(dee_acc.equity):,.2f}")

# SHORGAN-BOT
shorgan_client = TradingClient(os.getenv('ALPACA_API_KEY_SHORGAN'), os.getenv('ALPACA_SECRET_KEY_SHORGAN'), paper=True)
shorgan_acc = shorgan_client.get_account()
print("\n" + "="*60)
print("SHORGAN-BOT ACCOUNT")
print("="*60)
print(f"Cash: ${float(shorgan_acc.cash):,.2f}")
print(f"Portfolio Value: ${float(shorgan_acc.portfolio_value):,.2f}")
print(f"Buying Power: ${float(shorgan_acc.buying_power):,.2f}")
print(f"Equity: ${float(shorgan_acc.equity):,.2f}")

print("\n" + "="*60)
print("COMBINED TOTAL")
print("="*60)
print(f"Total Portfolio Value: ${float(dee_acc.portfolio_value) + float(shorgan_acc.portfolio_value):,.2f}")