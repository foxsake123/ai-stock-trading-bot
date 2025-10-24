"""
Portfolio Rebalancing Execution Script
October 16, 2025
"""

import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

load_dotenv()

# Initialize API clients
api_dee = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY_DEE'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_DEE'),
    paper=True
)

api_shorgan = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY_SHORGAN'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    paper=True
)

print("="*80)
print("PORTFOLIO REBALANCING - OCTOBER 16, 2025")
print("="*80)

# Cancel all pending orders first
print("\n[1/3] Canceling pending orders...")
try:
    api_dee.cancel_orders()
    print("  [OK] DEE-BOT: All orders canceled")
except Exception as e:
    print(f"  [WARN] DEE-BOT cancel error: {e}")

try:
    api_shorgan.cancel_orders()
    print("  [OK] SHORGAN-BOT: All orders canceled")
except Exception as e:
    print(f"  [WARN] SHORGAN-BOT cancel error: {e}")

# DEE-BOT Rebalancing (Trim to get positive cash)
print("\n[2/3] DEE-BOT: Trimming overweight positions...")
print("Goal: Eliminate negative cash balance (-$77,575)\n")

dee_sells = [
    ("AAPL", 50),
    ("JPM", 36),
    ("MRK", 120),
    ("MSFT", 17),
    ("ABBV", 37),
    ("VZ", 184),
    ("UNH", 22),
    ("PG", 50),
    ("KO", 98),
    ("COST", 2),
    ("LMT", 3),
]

dee_total_raised = 0
dee_filled = 0

for symbol, qty in dee_sells:
    try:
        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )

        submitted = api_dee.submit_order(order)
        print(f"  [OK] Sell {qty:4} {symbol:6} -> Order ID: {submitted.id}")
        dee_filled += 1

    except Exception as e:
        print(f"  [ERR] Sell {qty:4} {symbol:6} -> ERROR: {str(e)[:60]}")

print(f"\nDEE-BOT Summary: {dee_filled}/{len(dee_sells)} orders submitted")

# SHORGAN-BOT Rebalancing
print("\n[3/3] SHORGAN-BOT: Taking profits & cutting losers...")
print("Goal: Lock in gains, stop bleeding on losers\n")

shorgan_sells = [
    # Take 50% profits
    ("RGTI", 33, "50% profit take (+218% gain)"),
    ("ORCL", 11, "50% profit take (+33% gain)"),
    ("RXRX", 294, "50% profit take (+34% gain)"),
    ("BTBT", 285, "50% profit take (+45% gain)"),
    ("SAVA", 100, "50% profit take (+114% gain)"),

    # Cut losers 100%
    ("GPK", 142, "Cut loser (-18%)"),
    ("CIVI", 76, "Cut loser (-17%)"),
    ("SRRK", 193, "Cut loser (-9%)"),
    ("RIVN", 714, "Cut loser (-9%)"),
    ("DAKT", 743, "Cut loser (-6%)"),
    ("EMBC", 68, "Cut loser (-8%)"),
]

shorgan_filled = 0

for item in shorgan_sells:
    if len(item) == 3:
        symbol, qty, reason = item
    else:
        symbol, qty = item
        reason = "Rebalance"

    try:
        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )

        submitted = api_shorgan.submit_order(order)
        print(f"  [OK] Sell {qty:4} {symbol:6} -> {reason}")
        shorgan_filled += 1

    except Exception as e:
        print(f"  [ERR] Sell {qty:4} {symbol:6} -> ERROR: {str(e)[:60]}")

print(f"\nSHORGAN-BOT Summary: {shorgan_filled}/{len(shorgan_sells)} orders submitted")

print("\n" + "="*80)
print("REBALANCING EXECUTION COMPLETE")
print("="*80)
print("\nNext Steps:")
print("1. Monitor fills over next 5-10 minutes")
print("2. Run: python scripts/performance/get_portfolio_status.py")
print("3. Verify DEE-BOT cash is positive")
print("4. Review final allocation vs targets")
print("\nExpected Results:")
print("- DEE-BOT cash: -$77,575 → +$5,619 (positive!)")
print("- SHORGAN-BOT: Profits locked, losers cut")
print("- Combined portfolio: Healthier, more balanced")
print("="*80)
