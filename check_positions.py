from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
import os

load_dotenv()

# SHORGAN Live account
client = TradingClient(
    os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'),
    os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'),
    paper=False
)

# Get all positions
positions = client.get_all_positions()
print(f'Open Positions: {len(positions)}')
for pos in positions:
    pnl = float(pos.unrealized_pl)
    pnl_pct = float(pos.unrealized_plpc) * 100
    print(f'  {pos.symbol}: {pos.qty} shares @ ${pos.avg_entry_price} | P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)')

# Get today's orders
orders = client.get_orders()
print(f'\nTotal Orders Today: {len(orders)}')
filled = [o for o in orders if o.status == 'filled']
pending = [o for o in orders if o.status in ['new', 'pending_new', 'accepted']]
print(f'  Filled: {len(filled)}')
print(f'  Pending: {len(pending)}')

if pending:
    print('\nPending Orders:')
    for o in pending:
        print(f'  {o.symbol}: {o.side} {o.qty} shares @ ${o.limit_price}')

# Get account info
account = client.get_account()
print(f'\nAccount Value: ${float(account.portfolio_value):.2f}')
print(f'Cash: ${float(account.cash):.2f}')
print(f'Buying Power: ${float(account.buying_power):.2f}')
