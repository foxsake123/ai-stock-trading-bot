from alpaca.trading.client import TradingClient
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing API Keys...")
print()

# Test DEE-BOT
try:
    dee = TradingClient(os.getenv('ALPACA_API_KEY_DEE'), os.getenv('ALPACA_SECRET_KEY_DEE'), paper=True)
    acct = dee.get_account()
    print(f"[OK] DEE-BOT: ${float(acct.portfolio_value):,.2f}")
except Exception as e:
    print(f"[FAIL] DEE-BOT: {e}")

# Test SHORGAN Paper
try:
    shorgan_paper = TradingClient(os.getenv('ALPACA_API_KEY_SHORGAN'), os.getenv('ALPACA_SECRET_KEY_SHORGAN'), paper=True)
    acct = shorgan_paper.get_account()
    print(f"[OK] SHORGAN-BOT Paper: ${float(acct.portfolio_value):,.2f}")
except Exception as e:
    print(f"[FAIL] SHORGAN-BOT Paper: {e}")

# Test SHORGAN Live
try:
    shorgan_live = TradingClient(os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'), os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'), paper=False)
    acct = shorgan_live.get_account()
    print(f"[OK] SHORGAN-BOT Live: ${float(acct.portfolio_value):,.2f}")
except Exception as e:
    print(f"[FAIL] SHORGAN-BOT Live: {e}")
