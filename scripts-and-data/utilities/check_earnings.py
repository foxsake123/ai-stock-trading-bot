"""
Check CBRL earnings reaction and other critical positions
September 17, 2025, 4:21 PM ET
"""

import yfinance as yf
from datetime import datetime

print('='*60)
print('CRITICAL POSITION UPDATES - September 17, 2025, 4:21 PM ET')
print('='*60)
print()

# Check CBRL earnings
print('[1] CBRL EARNINGS CHECK:')
print('-'*60)
try:
    cbrl = yf.Ticker('CBRL')
    info = cbrl.info

    current_price = info.get('regularMarketPrice', info.get('currentPrice', 51.00))
    prev_close = info.get('previousClose', 51.00)
    volume = info.get('volume', 0)

    change = current_price - prev_close
    change_pct = (change / prev_close) * 100 if prev_close > 0 else 0

    print(f'Previous Close: ${prev_close:.2f}')
    print(f'Current Price: ${current_price:.2f}')
    print(f'Change: ${change:+.2f} ({change_pct:+.2f}%)')

    # Our position
    shares = 81
    entry_price = 51.00
    position_value = shares * current_price
    pnl = (current_price - entry_price) * shares

    print(f'\nOur Position: {shares} shares @ ${entry_price:.2f}')
    print(f'Current Value: ${position_value:,.2f}')
    print(f'P&L: ${pnl:+.2f}')

    # Action
    if change_pct > 3:
        print('\nACTION: EARNINGS BEAT - Set trailing stop at', f'${current_price * 0.97:.2f}')
    elif change_pct < -3:
        print('\nACTION: EARNINGS MISS - EXIT IMMEDIATELY')
    else:
        print('\nACTION: NEUTRAL - Monitor closely, tight stop at', f'${current_price * 0.98:.2f}')

except Exception as e:
    print(f'Yahoo Finance error - check manually')
    print('Maintain stop at $46.92')

print()

# Check KSS (near stop loss)
print('[2] KSS STOP-LOSS CHECK:')
print('-'*60)
try:
    kss = yf.Ticker('KSS')
    info = kss.info

    current_price = info.get('regularMarketPrice', info.get('currentPrice', 15.28))

    shares = 90
    entry_price = 16.50
    stop_price = 15.18  # -8% stop

    pnl_pct = ((current_price - entry_price) / entry_price) * 100

    print(f'Position: {shares} shares @ ${entry_price:.2f}')
    print(f'Current Price: ${current_price:.2f} ({pnl_pct:+.2f}%)')
    print(f'Stop Loss: ${stop_price:.2f}')

    if current_price <= stop_price:
        print('\nACTION: STOP TRIGGERED - SELL NOW')
    elif current_price <= stop_price * 1.02:
        print('\nACTION: VERY CLOSE TO STOP - Consider exiting')
    else:
        print('\nACTION: Monitor closely')

except Exception as e:
    print(f'Error checking KSS - monitor manually')

print()

# Check big winners
print('[3] PROFIT-TAKING CANDIDATES:')
print('-'*60)

winners = [
    ('RGTI', 130, 15.35, 18.84, 22.7),
    ('ORCL', 42, 239.04, 291.43, 21.9),
    ('DAKT', 743, 20.97, 23.87, 13.8),
    ('TSLA', 2, 349.12, 395.50, 13.3),
    ('BTBT', 570, 2.66, 2.95, 10.9)
]

print('Symbol | Shares |  Entry  | Current |  Gain  | Action')
print('-'*60)
for symbol, shares, entry, last_price, gain_pct in winners:
    if gain_pct > 20:
        action = 'TAKE 50% PROFITS'
    elif gain_pct > 15:
        action = 'Consider profits'
    else:
        action = 'Trailing stop'

    print(f'{symbol:6} | {shares:6} | ${entry:7.2f} | ${last_price:7.2f} | {gain_pct:+5.1f}% | {action}')

print()
print('='*60)
print('SUMMARY ACTIONS:')
print('1. Check CBRL after-hours reaction')
print('2. Monitor KSS closely (near stop)')
print('3. Take partial profits on RGTI and ORCL (>20%)')
print('4. Prepare for 4:30 PM automated report')
print('5. Plan INCY FDA strategy for Thursday')
print('='*60)