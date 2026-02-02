from alpaca.trading.client import TradingClient
import os
from dotenv import load_dotenv

load_dotenv()

# SHORGAN Live
client = TradingClient(
    os.getenv('ALPACA_API_KEY_SHORGAN_LIVE'),
    os.getenv('ALPACA_SECRET_KEY_SHORGAN_LIVE'),
    paper=False
)

account = client.get_account()
positions = client.get_all_positions()

print('SHORGAN-BOT LIVE Performance')
print('=' * 50)
print(f'Portfolio Value: ${float(account.portfolio_value):,.2f}')
print(f'Cash: ${float(account.cash):,.2f}')
print(f'Total Deposits: $3,000.00')
print(f'P&L: ${float(account.portfolio_value) - 3000:,.2f}')
print(f'Return: {((float(account.portfolio_value) - 3000) / 3000) * 100:.2f}%')
print()
print(f'Open Positions: {len(positions)}')
print()
print('Current Holdings:')
print('-' * 50)
for pos in sorted(positions, key=lambda x: float(x.unrealized_plpc), reverse=True):
    pnl = float(pos.unrealized_pl)
    pct = float(pos.unrealized_plpc) * 100
    print(f'{pos.symbol:6} | {int(pos.qty):4} sh | ${float(pos.market_value):8,.2f} | ${pnl:+8,.2f} ({pct:+6.2f}%)')

print()
print('Stop Loss Orders:')
print('-' * 50)
orders = client.get_orders(status='open')
stop_orders = [o for o in orders if o.stop_price]
print(f'Total: {len(stop_orders)}')
for order in stop_orders:
    print(f'{order.symbol:6} | {order.side:4} {order.qty} @ stop ${order.stop_price}')
