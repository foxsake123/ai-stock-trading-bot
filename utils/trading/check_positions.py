from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
import os

load_dotenv()

# DEE-BOT
dee = TradingClient(os.getenv('ALPACA_API_KEY_DEE'), os.getenv('ALPACA_SECRET_KEY_DEE'), paper=True)
positions = dee.get_all_positions()
print("="*60)
print("DEE-BOT POSITIONS")
print("="*60)
for p in positions:
    print(f"{p.symbol}: {p.qty} shares @ ${float(p.current_price):.2f} = ${float(p.market_value):.2f}")

# SHORGAN-BOT
shorgan = TradingClient(os.getenv('ALPACA_API_KEY_SHORGAN'), os.getenv('ALPACA_SECRET_KEY_SHORGAN'), paper=True)
positions = shorgan.get_all_positions()
print("\n" + "="*60)
print("SHORGAN-BOT POSITIONS")
print("="*60)
for p in positions:
    side = "SHORT" if p.side == "short" else "LONG"
    print(f"{p.symbol}: {p.qty} shares ({side}) @ ${float(p.current_price):.2f} = ${float(p.market_value):.2f}")