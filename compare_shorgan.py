from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
import os

load_dotenv()

print('=' * 60)
print('SHORGAN PAPER ($100K)')
print('=' * 60)
paper = TradingClient(os.getenv('ALPACA_API_KEY_SHORGAN'), os.getenv('ALPACA_SECRET_KEY_SHORGAN'), paper=True)
acct = paper.get_account()
print(f'Portfolio Value: ${float(acct.portfolio_value):,.2f}')
print(f'Cash: ${float(acct.cash):,.2f} ({float(acct.cash)/float(acct.portfolio_value)*100:.1f}%)')
positions = paper.get_all_positions()
print(f'Positions: {len(positions)}')
print()
print('Top 10 Positions by Value:')
pos_list = [(p.symbol, float(p.market_value), float(p.unrealized_pl), float(p.unrealized_plpc)*100, float(p.qty)) for p in positions]
pos_list.sort(key=lambda x: abs(x[1]), reverse=True)
for sym, val, pnl, pnl_pct, qty in pos_list[:10]:
    side = 'LONG' if qty > 0 else 'SHORT'
    print(f'  {sym:6} {side:5} ${abs(val):>8,.0f} | P&L: ${pnl:>+8,.0f} ({pnl_pct:>+6.1f}%)')

# Count winners/losers
winners = sum(1 for p in pos_list if p[2] > 0)
losers = sum(1 for p in pos_list if p[2] < 0)
total_pnl = sum(p[2] for p in pos_list)
print(f'\nWin/Loss: {winners}W / {losers}L')
print(f'Total Unrealized P&L: ${total_pnl:+,.2f}')

print()
print('=' * 60)
print('SHORGAN LIVE ($3K)')
print('=' * 60)
live = TradingClient(os.getenv('ALPACA_API_KEY_SHORGAN_LIVE'), os.getenv('ALPACA_SECRET_KEY_SHORGAN_LIVE'), paper=False)
acct = live.get_account()
print(f'Portfolio Value: ${float(acct.portfolio_value):,.2f}')
print(f'Cash: ${float(acct.cash):,.2f} ({float(acct.cash)/float(acct.portfolio_value)*100:.1f}%)')
positions = live.get_all_positions()
print(f'Positions: {len(positions)}')
print()
print('All Positions:')
pos_list = [(p.symbol, float(p.market_value), float(p.unrealized_pl), float(p.unrealized_plpc)*100, float(p.qty)) for p in positions]
pos_list.sort(key=lambda x: abs(x[1]), reverse=True)
for sym, val, pnl, pnl_pct, qty in pos_list:
    side = 'LONG' if qty > 0 else 'SHORT'
    print(f'  {sym:6} {side:5} ${abs(val):>8,.0f} | P&L: ${pnl:>+8,.0f} ({pnl_pct:>+6.1f}%)')

# Count winners/losers
winners = sum(1 for p in pos_list if p[2] > 0)
losers = sum(1 for p in pos_list if p[2] < 0)
total_pnl = sum(p[2] for p in pos_list)
print(f'\nWin/Loss: {winners}W / {losers}L')
print(f'Total Unrealized P&L: ${total_pnl:+,.2f}')

# Check overlap
paper_symbols = {p.symbol for p in paper.get_all_positions()}
live_symbols = {p.symbol for p in live.get_all_positions()}
overlap = paper_symbols & live_symbols
print()
print('=' * 60)
print('OVERLAP ANALYSIS')
print('=' * 60)
print(f'Paper positions: {len(paper_symbols)}')
print(f'Live positions: {len(live_symbols)}')
print(f'Overlapping: {len(overlap)} ({", ".join(sorted(overlap)) if overlap else "NONE"})')
print(f'Paper only: {len(paper_symbols - live_symbols)}')
print(f'Live only: {len(live_symbols - paper_symbols)}')
