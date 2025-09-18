import pandas as pd
from datetime import datetime

# Load SHORGAN-BOT positions
shorgan_df = pd.read_csv('scripts-and-data/daily-csv/shorgan-bot-positions.csv')

print('='*60)
print('SHORGAN-BOT HOLDINGS - September 18, 2025')
print('='*60)
print(f'Total Positions: {len(shorgan_df)}')
print(f'Total Value: ${shorgan_df["market_value"].sum():,.2f}')
print(f'Total P&L: ${shorgan_df["unrealized_pnl"].sum():+,.2f}')
print()

# List all positions
print('Current Positions:')
print('-'*60)
for _, row in shorgan_df.iterrows():
    symbol = row['symbol']
    qty = int(row['quantity'])
    entry = row['avg_price']
    current = row['current_price']
    pnl_pct = row['unrealized_pnl_pct']

    status = ''
    if symbol == 'CBRL':
        status = ' <- EXIT TODAY (earnings miss)'
    elif symbol == 'RGTI':
        status = ' <- SELL 50% TODAY'
    elif symbol == 'ORCL':
        status = ' <- SELL 50% TODAY'
    elif symbol == 'INCY':
        status = ' <- FDA Thursday'
    elif symbol == 'KSS':
        status = ' <- WATCH STOP'

    print(f'{symbol:6} {qty:4} shares @ ${entry:7.2f} | Current: ${current:7.2f} | {pnl_pct:+6.1f}%{status}')

print()
print('Actions for Sept 18 at 9:30 AM:')
print('1. EXIT CBRL - 81 shares (earnings miss)')
print('2. SELL RGTI - 65 shares (take profits)')
print('3. SELL ORCL - 21 shares (take profits)')
print('4. WATCH KSS - stop at $15.18')