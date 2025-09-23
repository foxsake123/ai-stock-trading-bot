"""
Fix DEE-BOT position tracking with current prices
"""

import yfinance as yf
import csv
from datetime import datetime

print("="*60)
print("FIXING DEE-BOT POSITION TRACKING")
print("="*60)

# Current positions
positions = [
    {'symbol': 'PG', 'quantity': 39, 'avg_price': 155.20},
    {'symbol': 'JNJ', 'quantity': 37, 'avg_price': 162.45},
    {'symbol': 'KO', 'quantity': 104, 'avg_price': 58.90}
]

updated_rows = []

print("Updating positions:")
print("-" * 40)

for pos in positions:
    symbol = pos['symbol']
    quantity = pos['quantity']
    avg_price = pos['avg_price']

    try:
        # Get current price
        ticker = yf.Ticker(symbol)
        current_price = ticker.history(period="1d")['Close'].iloc[-1]

        # Calculate P&L
        pnl = (current_price - avg_price) * quantity
        pnl_pct = (pnl / (quantity * avg_price)) * 100

        updated_row = {
            'symbol': symbol,
            'quantity': quantity,
            'avg_price': avg_price,
            'current_price': round(current_price, 2),
            'pnl': round(pnl, 2),
            'pnl_pct': f"{pnl_pct:.2f}%",
            'side': 'long',
            'date_acquired': '2025-09-16'
        }

        updated_rows.append(updated_row)

        print(f"{symbol}: ${avg_price:.2f} -> ${current_price:.2f} | P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)")

    except Exception as e:
        print(f"Error updating {symbol}: {e}")

# Write to CSV
csv_file = "scripts-and-data/daily-csv/dee-bot-positions.csv"

with open(csv_file, 'w', newline='') as f:
    fieldnames = ['symbol', 'quantity', 'avg_price', 'current_price', 'pnl', 'pnl_pct', 'side', 'date_acquired']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(updated_rows)

# Summary
total_pnl = sum(row['pnl'] for row in updated_rows)
total_value = sum(row['quantity'] * row['current_price'] for row in updated_rows)

print()
print("SUMMARY:")
print(f"Total Value: ${total_value:,.2f}")
print(f"Total P&L: ${total_pnl:+,.2f}")
print(f"Positions Updated: {len(updated_rows)}")
print(f"File: {csv_file}")
print("="*60)

print()
print("LOGGING ISSUE DIAGNOSIS:")
print("-" * 40)
print("ROOT CAUSE: DEE-BOT not updating prices automatically")
print("FIXES NEEDED:")
print("1. Add daily price update to automation")
print("2. Fix Alpaca API connection in DEE-BOT scripts")
print("3. Create scheduled task for position updates")
print("4. Add real-time P&L tracking")
print()
print("RECOMMENDATION: Run this script daily until automation is fixed")