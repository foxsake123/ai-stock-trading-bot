#!/usr/bin/env python3
"""
Resubmit SHORGAN-BOT Live Trades at Current Market Prices
APPS and PAYO orders were canceled - prices dropped since research
"""

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("RESUBMITTING SHORGAN-BOT LIVE TRADES")
print("=" * 80)
print()

shorgan = TradingClient(
    os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'),
    os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'),
    paper=False
)

print("CURRENT MARKET PRICES:")
print("  APPS: $6.36 (was $8.45 in research - DOWN 24.7%!)")
print("  PAYO: $5.24 (was $7.23 in research - DOWN 27.5%!)")
print()
print("NOTE: Both stocks dropped significantly, likely due to earnings")
print("      or market reaction. Recalculating position sizes...")
print()

# Recalculate shares at current prices (same $100 target per position)
apps_shares = int(100 / 6.36)  # ~15 shares
payo_shares = int(100 / 5.24)  # ~19 shares

print("ADJUSTED POSITION SIZES:")
print(f"  APPS: {apps_shares} shares @ market (~${apps_shares * 6.36:.2f})")
print(f"  PAYO: {payo_shares} shares @ market (~${payo_shares * 5.24:.2f})")
print()

response = input("These stocks dropped 25-28%. Still want to buy? (yes/no): ")

if response.lower() != 'yes':
    print()
    print("Orders CANCELED by user. Wise decision to reassess after big drops.")
    print()
    print("RECOMMENDATION:")
    print("  - Wait to see why they dropped (check news/earnings)")
    print("  - If earnings already reported, assess if thesis still intact")
    print("  - If pre-earnings drop, may be better entry point")
    print("  - Consider waiting for stabilization")
    exit(0)

print()
print("Submitting market orders...")
print()

try:
    # APPS order
    apps_order = MarketOrderRequest(
        symbol='APPS',
        qty=apps_shares,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )
    apps_result = shorgan.submit_order(apps_order)
    print(f"[OK] APPS order submitted: {apps_result.id}")
    print(f"     {apps_shares} shares at market price")
    print()

except Exception as e:
    print(f"[ERROR] APPS order failed: {e}")
    print()

try:
    # PAYO order
    payo_order = MarketOrderRequest(
        symbol='PAYO',
        qty=payo_shares,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )
    payo_result = shorgan.submit_order(payo_order)
    print(f"[OK] PAYO order submitted: {payo_result.id}")
    print(f"     {payo_shares} shares at market price")
    print()

except Exception as e:
    print(f"[ERROR] PAYO order failed: {e}")
    print()

print("=" * 80)
print("NOTE: After 25-28% drops, stop losses need to be tighter!")
print("Recommended new stops (8% from entry):")
print(f"  APPS: ${6.36 * 0.92:.2f} stop")
print(f"  PAYO: ${5.24 * 0.92:.2f} stop")
print("=" * 80)
