#!/usr/bin/env python
"""Assess SHORGAN Live positions and identify worst performers."""

from alpaca.trading.client import TradingClient
import os
from dotenv import load_dotenv
load_dotenv()

client = TradingClient(
    os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'),
    os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'),
    paper=False
)
account = client.get_account()
positions = client.get_all_positions()

print('='*60)
print('SHORGAN-BOT LIVE ACCOUNT ASSESSMENT')
print('='*60)
print(f'Account Value: ${float(account.equity):,.2f}')
print(f'Cash: ${float(account.cash):,.2f}')
print(f'Buying Power: ${float(account.buying_power):,.2f}')
print(f'Position Count: {len(positions)} (Limit: 10)')
print()
print('POSITIONS RANKED BY P&L:')
print('-'*60)

# Sort by P&L
sorted_positions = sorted(positions, key=lambda p: float(p.unrealized_pl))

for i, p in enumerate(sorted_positions):
    pnl = float(p.unrealized_pl)
    pnl_pct = float(p.unrealized_plpc) * 100
    market_value = float(p.market_value)
    qty = float(p.qty)
    side = 'LONG' if qty > 0 else 'SHORT'
    print(f'{i+1:2}. {p.symbol:6} | {side:5} | {abs(int(qty)):4} shares | MV: ${abs(market_value):>8,.2f} | P&L: ${pnl:>+8.2f} ({pnl_pct:>+6.1f}%)')

print()
print('WORST 5 (candidates to close):')
for p in sorted_positions[:5]:
    pnl = float(p.unrealized_pl)
    print(f'  {p.symbol}: ${pnl:+.2f}')

print()
print('BEST 5 (keep):')
for p in sorted_positions[-5:]:
    pnl = float(p.unrealized_pl)
    print(f'  {p.symbol}: ${pnl:+.2f}')
