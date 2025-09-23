import os
from alpaca.trading.client import TradingClient

# SHORGAN-BOT credentials from environment or hardcoded
api_key = os.getenv('ALPACA_API_KEY_PAPER', 'PKJRLSB2MFEJUSK6UK2E')
secret_key = os.getenv('ALPACA_SECRET_KEY_PAPER', 'eTSRAfs9AobCJyqGkycrHFLdD2sAOp8DpqOGVvvr')

client = TradingClient(api_key, secret_key, paper=True)

# Check KSS position
positions = client.get_all_positions()
kss_positions = [p for p in positions if p.symbol == 'KSS']

if kss_positions:
    kss = kss_positions[0]
    current_price = float(kss.current_price)
    avg_price = float(kss.avg_entry_price)
    shares = int(kss.qty)
    pnl = float(kss.unrealized_pl)

    print(f"KSS Position Summary:")
    print(f"  Shares: {shares}")
    print(f"  Avg Entry: ${avg_price:.2f}")
    print(f"  Current Price: ${current_price:.2f}")
    print(f"  P&L: ${pnl:.2f}")
    print(f"  Stop Loss Level: $15.18")
    print(f"  Distance to Stop: ${current_price - 15.18:.2f}")

    if current_price <= 15.18:
        print("\n⚠️ WARNING: KSS has hit or passed stop loss level!")
        print("Action Required: SELL immediately at market open")
    else:
        print(f"\n✓ KSS is ${current_price - 15.18:.2f} above stop loss")
else:
    print("No KSS position found - may have already been stopped out")