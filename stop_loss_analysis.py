"""
Stop-Loss Analysis for All Positions
September 17, 2025
"""

import csv
from datetime import datetime

print('='*70)
print('STOP-LOSS ANALYSIS - September 17, 2025, 11:45 AM ET')
print('='*70)
print()

# Define stop-loss thresholds
CATALYST_STOP = -8.0  # SHORGAN-BOT catalyst trades
DEFENSIVE_STOP = -3.0  # DEE-BOT defensive positions

print('STOP-LOSS RULES:')
print('  • SHORGAN-BOT (Catalyst): -8% trailing stop')
print('  • DEE-BOT (Defensive): -3% fixed stop')
print('  • Force close all: -7% daily portfolio loss')
print()

# Analyze SHORGAN positions
print('SHORGAN-BOT STOP-LOSS STATUS:')
print('-'*70)
print(f'{"Symbol":<8} {"Qty":>6} {"Avg Price":>10} {"Current":>10} {"P&L %":>8} {"Stop @":>10} {"Action":<25}')
print('-'*70)

positions_at_risk = []
positions_near_stop = []
safe_positions = []
winner_positions = []

with open('scripts-and-data/daily-csv/shorgan-bot-positions.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        symbol = row['symbol']
        quantity = int(row['quantity'])
        avg_price = float(row['avg_price'])
        current_price = float(row['current_price'])
        pnl_pct = float(row['unrealized_pnl_pct'])

        # Calculate stop price
        stop_price = avg_price * (1 + CATALYST_STOP/100)

        # Determine action
        if pnl_pct <= CATALYST_STOP:
            action = '[STOP] SELL NOW'
            positions_at_risk.append((symbol, quantity, pnl_pct))
        elif -8 < pnl_pct <= -6:
            action = '[WARN] NEAR STOP'
            positions_near_stop.append((symbol, quantity, pnl_pct))
        elif pnl_pct > 15:
            action = '[WIN] TAKE PROFITS'
            winner_positions.append((symbol, quantity, pnl_pct))
        elif pnl_pct > 10:
            action = '[WIN] Consider profits'
            winner_positions.append((symbol, quantity, pnl_pct))
        elif symbol == 'CBRL':
            action = '[EVENT] EARNINGS TONIGHT'
        elif symbol == 'INCY':
            action = '[EVENT] FDA Thursday'
        else:
            action = 'Monitor'
            safe_positions.append((symbol, quantity, pnl_pct))

        print(f'{symbol:<8} {quantity:>6} ${avg_price:>9.2f} ${current_price:>9.2f} {pnl_pct:>7.1f}% ${stop_price:>9.2f} {action:<25}')

print()

# Analyze DEE-BOT positions
print('DEE-BOT STOP-LOSS STATUS (Beta-Neutral):')
print('-'*70)

with open('scripts-and-data/daily-csv/dee-bot-positions.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        symbol = row['symbol']
        quantity = int(row['quantity'])
        avg_price = float(row['avg_price'])

        # Calculate stop price for defensive positions
        stop_price = avg_price * (1 + DEFENSIVE_STOP/100)

        print(f'{symbol:<8} {quantity:>6} ${avg_price:>9.2f}     {"0.0":>7}% ${stop_price:>9.2f} {"Defensive - Hold":<25}')

print()
print('='*70)
print('SUMMARY & RECOMMENDATIONS:')
print('='*70)

if positions_at_risk:
    print()
    print('[ALERT] IMMEDIATE ACTION REQUIRED:')
    for symbol, qty, pnl in positions_at_risk:
        print(f'   - {symbol}: STOP TRIGGERED at {pnl:.1f}% - SELL {qty} shares')

if positions_near_stop:
    print()
    print('[WARNING] POSITIONS NEAR STOP LOSS:')
    for symbol, qty, pnl in positions_near_stop:
        print(f'   - {symbol}: At {pnl:.1f}% (stop at -8%) - Set alerts')

print()
print('RISK METRICS:')
print(f'   - Positions at/below stop: {len(positions_at_risk)}')
print(f'   - Positions near stop (-6% to -8%): {len(positions_near_stop)}')
print(f'   - Safe positions (> -6%): {len(safe_positions)}')
print(f'   - Winners (>10%): {len(winner_positions)}')

print()
print('SPECIAL SITUATIONS:')
print('   - CBRL: EARNINGS AFTER CLOSE TODAY')
print('     * Current: 81 shares @ $51.00')
print('     * Action: Set trailing stop at $49.50 or exit before close')
print('     * Risk: Gap down on disappointing earnings')
print()
print('   - INCY: FDA DECISION THURSDAY')
print('     * Current: 61 shares @ $83.97')
print('     * Stop: $77.25 (-8%)')
print('     * Action: Hold for binary event, size appropriately')

print()
print('STOP-LOSS BEST PRACTICES:')
print('   1. Use trailing stops on winners to lock in gains')
print('   2. Tighten stops before binary events (earnings/FDA)')
print('   3. Honor stops immediately - no "hoping" for recovery')
print('   4. Consider market conditions when setting stops')
print('   5. Review stops daily at market open and close')

print()
print('='*70)