from alpaca.trading.client import TradingClient
import os
from dotenv import load_dotenv

load_dotenv()

dee = TradingClient(os.getenv('ALPACA_API_KEY_DEE'), os.getenv('ALPACA_SECRET_KEY_DEE'), paper=True)
shorgan_paper = TradingClient(os.getenv('ALPACA_API_KEY_SHORGAN'), os.getenv('ALPACA_SECRET_KEY_SHORGAN'), paper=True)
shorgan_live = TradingClient(os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'), os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'), paper=False)

dee_acct = dee.get_account()
shorgan_p_acct = shorgan_paper.get_account()
shorgan_l_acct = shorgan_live.get_account()

print(f"DEE-BOT (Paper): ${float(dee_acct.portfolio_value):,.2f}")
print(f"SHORGAN-BOT (Paper): ${float(shorgan_p_acct.portfolio_value):,.2f}")
print(f"SHORGAN-BOT (Live): ${float(shorgan_l_acct.portfolio_value):,.2f}")
print(f"\nCombined: ${float(dee_acct.portfolio_value) + float(shorgan_p_acct.portfolio_value) + float(shorgan_l_acct.portfolio_value):,.2f}")
