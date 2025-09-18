"""
Create master trade log CSV from JSON trade logs
"""

import json
import pandas as pd
from datetime import datetime

# Read JSON trade logs
shorgan_trades = []
dee_trades = []

try:
    with open('../09_logs/trading/SHORGAN_BOT_TRADE_LOG_COMPLETE.json', 'r') as f:
        shorgan_data = json.load(f)
        if isinstance(shorgan_data, list):
            shorgan_trades = shorgan_data
        elif 'executed_positions' in shorgan_data:
            # Extract trades from executed_positions
            for pos in shorgan_data['executed_positions']:
                trade = {
                    'date': shorgan_data.get('session_date', ''),
                    'symbol': pos.get('symbol', ''),
                    'action': 'BUY' if pos.get('direction') == 'LONG' else 'SELL',
                    'quantity': pos.get('quantity', 0),
                    'price': pos.get('entry_price', 0),
                    'order_id': pos.get('order_id', ''),
                    'catalyst': pos.get('catalyst', ''),
                    'stop_loss': pos.get('stop_loss', 0),
                    'take_profit': pos.get('take_profit', 0)
                }
                shorgan_trades.append(trade)
        elif 'trades' in shorgan_data:
            shorgan_trades = shorgan_data['trades']
except Exception as e:
    print(f"Error loading SHORGAN trades: {e}")

try:
    with open('../09_logs/trading/DEE_BOT_TRADE_LOG_COMPLETE.json', 'r') as f:
        dee_data = json.load(f)
        if isinstance(dee_data, list):
            dee_trades = dee_data
        elif 'trades' in dee_data:
            dee_trades = dee_data['trades']
except Exception as e:
    print(f"Error loading DEE trades: {e}")

# Add bot identifier
for trade in shorgan_trades:
    trade['bot'] = 'SHORGAN'

for trade in dee_trades:
    trade['bot'] = 'DEE'

# Combine all trades
all_trades = shorgan_trades + dee_trades

# Convert to DataFrame
if all_trades:
    df = pd.DataFrame(all_trades)

    # Standardize columns
    if 'date' not in df.columns and 'timestamp' in df.columns:
        df['date'] = df['timestamp']

    # Sort by date
    if 'date' in df.columns:
        df = df.sort_values('date', ascending=False)

    # Save to CSV
    df.to_csv('../trade-logs/all-trades.csv', index=False)

    print("="*60)
    print("MASTER TRADE LOG CREATED")
    print("="*60)
    print(f"Total Trades: {len(df)}")
    print(f"SHORGAN Trades: {len(shorgan_trades)}")
    print(f"DEE Trades: {len(dee_trades)}")
    print()

    if 'symbol' in df.columns:
        print("Trade Summary by Symbol:")
        print(df.groupby('symbol').size().sort_values(ascending=False).head(10))

    print()
    print("Saved to: trade-logs/all-trades.csv")
else:
    print("No trades found to process")

# Also create a simplified trade history
trade_history = []

# Manual entry of recent trades from positions
recent_trades = [
    {'date': '2025-09-16', 'bot': 'DEE', 'symbol': 'PG', 'action': 'BUY', 'quantity': 39, 'price': 155.20},
    {'date': '2025-09-16', 'bot': 'DEE', 'symbol': 'JNJ', 'action': 'BUY', 'quantity': 37, 'price': 162.45},
    {'date': '2025-09-16', 'bot': 'DEE', 'symbol': 'KO', 'action': 'BUY', 'quantity': 104, 'price': 58.90},
    {'date': '2025-09-17', 'bot': 'SHORGAN', 'symbol': 'CBRL', 'action': 'BUY', 'quantity': 81, 'price': 51.00},
    {'date': '2025-09-12', 'bot': 'SHORGAN', 'symbol': 'RGTI', 'action': 'BUY', 'quantity': 130, 'price': 15.35},
    {'date': '2025-09-10', 'bot': 'SHORGAN', 'symbol': 'ORCL', 'action': 'BUY', 'quantity': 42, 'price': 239.04},
]

# Save simplified history
if recent_trades:
    simple_df = pd.DataFrame(recent_trades)
    simple_df.to_csv('../trade-logs/recent-trades.csv', index=False)
    print()
    print("Recent trades saved to: trade-logs/recent-trades.csv")