"""
Check current positions and pre-market status
September 17, 2025
"""

import alpaca_trade_api as tradeapi
from datetime import datetime

# Alpaca API
api = tradeapi.REST(
    'PK6FZK4DAQVTD7DYVH78',
    'iXfKe0M7chQ5aYNy9bz4YARnGtiufJFq8nMqJlfa',
    'https://paper-api.alpaca.markets'
)

# Get account info
account = api.get_account()

print('='*60)
print('POSITION CHECK - September 17, 2025, 11:42 AM ET')
print('='*60)
print()
print(f'Portfolio Value: ${float(account.portfolio_value):,.2f}')
print(f'Buying Power: ${float(account.buying_power):,.2f}')
print(f'Cash: ${float(account.cash):,.2f}')
print()

# Critical alerts
print('🔴 CRITICAL ALERTS:')
print('  • CBRL: EARNINGS AFTER CLOSE TODAY (81 shares @ $51.00)')
print('  • INCY: FDA DECISION THURSDAY (61 shares @ $83.97)')
print()

# Get positions
positions = api.list_positions()

print('CURRENT POSITIONS:')
print('-'*60)

critical_positions = ['CBRL', 'INCY']
total_unrealized_pnl = 0
position_count = 0

for position in positions:
    symbol = position.symbol
    qty = int(position.qty)
    avg_price = float(position.avg_entry_price)
    current_price = float(position.current_price)
    unrealized_pnl = float(position.unrealized_pl)
    unrealized_pnl_pct = float(position.unrealized_plpc) * 100
    market_value = float(position.market_value)

    total_unrealized_pnl += unrealized_pnl
    position_count += 1

    # Status indicators
    if symbol in critical_positions:
        status = '🎯 CATALYST'
    elif unrealized_pnl_pct > 10:
        status = '✅ WINNER'
    elif unrealized_pnl_pct < -5:
        status = '⚠️  WATCH'
    else:
        status = '   OK'

    print(f'{status:12} | {symbol:6} | Shares: {qty:4} | Avg: ${avg_price:7.2f} | Now: ${current_price:7.2f} | P&L: ${unrealized_pnl:+8.2f} ({unrealized_pnl_pct:+6.2f}%)')

    # Alert for critical positions
    if symbol == 'CBRL':
        print(f'              --> ACTION NEEDED: Earnings tonight - Consider taking profits or setting tight stop')
    elif symbol == 'INCY':
        print(f'              --> Monitor closely - Binary FDA event Thursday')

    # Stop loss warnings
    if unrealized_pnl_pct < -6:
        print(f'              --> ⚠️  STOP LOSS WARNING: Currently at {unrealized_pnl_pct:.1f}% (stop at -8%)')

print('-'*60)
print(f'SUMMARY: {position_count} positions | Total P&L: ${total_unrealized_pnl:+,.2f}')
print()

# Get recent orders
print('RECENT EXECUTIONS:')
print('-'*60)
orders = api.list_orders(status='filled', limit=5)
for order in orders:
    filled_time = order.filled_at[:19] if order.filled_at else 'N/A'
    print(f'{filled_time} | {order.side.upper():4} {int(order.qty):4} {order.symbol:6} @ ${float(order.filled_avg_price or 0):7.2f}')

print('='*60)
print()
print('RECOMMENDATIONS:')
print('1. CBRL: Set trailing stop or take partial profits before earnings')
print('2. INCY: Hold for FDA but consider position size')
print('3. Winners (>10%): Consider taking partial profits')
print('4. Losers (<-6%): Review stop losses')
print('='*60)