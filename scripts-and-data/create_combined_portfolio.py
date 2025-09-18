"""
Create combined portfolio view from SHORGAN and DEE bot positions
"""

import pandas as pd
import csv
from datetime import datetime

# Read both position files
shorgan_df = pd.read_csv('daily-csv/shorgan-bot-positions.csv')
dee_df = pd.read_csv('daily-csv/dee-bot-positions.csv')

# Add bot column
shorgan_df['bot'] = 'SHORGAN'
dee_df['bot'] = 'DEE'

# Combine
combined_df = pd.concat([shorgan_df, dee_df], ignore_index=True)

# Calculate total values
combined_df['market_value'] = combined_df['quantity'] * combined_df['current_price']

# Sort by P&L descending
combined_df = combined_df.sort_values('pnl', ascending=False)

# Save combined view
combined_df.to_csv('../portfolio-holdings/current/combined-portfolio.csv', index=False)

# Calculate summary stats
total_value = combined_df['market_value'].sum()
total_pnl = combined_df['pnl'].sum()
total_positions = len(combined_df)

# Get cash balances (from CLAUDE.md)
shorgan_cash = 37896.67
dee_cash = 50956.16
total_cash = shorgan_cash + dee_cash

# Total portfolio value
total_portfolio = total_value + total_cash

print("="*60)
print("COMBINED PORTFOLIO CREATED")
print("="*60)
print(f"Total Positions: {total_positions}")
print(f"Market Value: ${total_value:,.2f}")
print(f"Cash Balance: ${total_cash:,.2f}")
print(f"Total Portfolio: ${total_portfolio:,.2f}")
print(f"Total P&L: ${total_pnl:+,.2f}")
print()
print("Top Winners:")
print(combined_df[['symbol', 'bot', 'pnl', 'pnl_pct']].head(5).to_string(index=False))
print()
print("Saved to: portfolio-holdings/current/combined-portfolio.csv")