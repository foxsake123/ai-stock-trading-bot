#!/usr/bin/env python3
"""
Portfolio CSV Updater
Creates daily CSV tracking files matching ChatGPT-Micro-Cap format
Tracks individual positions and daily performance for both bots
"""

import csv
import alpaca_trade_api as tradeapi
from datetime import datetime
from pathlib import Path
import pandas as pd

# Alpaca API Configuration
DEE_BOT_CONFIG = {
    'API_KEY': 'PK6FZK4DAQVTD7DYVH78',
    'SECRET_KEY': 'JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt',
    'BASE_URL': 'https://paper-api.alpaca.markets'
}

SHORGAN_BOT_CONFIG = {
    'API_KEY': 'PKJRLSB2MFEJUSK6UK2E',
    'SECRET_KEY': 'QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic',
    'BASE_URL': 'https://paper-api.alpaca.markets'
}

# Output paths
OUTPUT_DIR = Path("scripts-and-data/daily-csv")
DEE_CSV = OUTPUT_DIR / "dee_bot_portfolio_history.csv"
SHORGAN_CSV = OUTPUT_DIR / "shorgan_bot_portfolio_history.csv"
COMBINED_CSV = OUTPUT_DIR / "combined_portfolio_history.csv"

def get_portfolio_data(api, bot_name):
    """Fetch current portfolio data from Alpaca"""
    try:
        account = api.get_account()
        positions = api.list_positions()

        today = datetime.now().strftime('%Y-%m-%d')
        cash_balance = float(account.cash)
        total_equity = float(account.portfolio_value)

        portfolio_rows = []

        # Add individual position rows
        for position in positions:
            row = {
                'Date': today,
                'Ticker': position.symbol,
                'Shares': float(position.qty),
                'Buy Price': float(position.avg_entry_price),
                'Cost Basis': float(position.cost_basis),
                'Stop Loss': '',  # To be added if available
                'Current Price': float(position.current_price),
                'Total Value': float(position.market_value),
                'PnL': float(position.unrealized_pl),
                'Action': 'HOLD',
                'Cash Balance': '',
                'Total Equity': '',
                'Bot': bot_name,
                'Side': position.side
            }
            portfolio_rows.append(row)

        # Add TOTAL row
        total_pnl = sum(float(p.unrealized_pl) for p in positions)
        total_row = {
            'Date': today,
            'Ticker': 'TOTAL',
            'Shares': '',
            'Buy Price': '',
            'Cost Basis': '',
            'Stop Loss': '',
            'Current Price': '',
            'Total Value': total_equity - cash_balance,
            'PnL': total_pnl,
            'Action': '',
            'Cash Balance': cash_balance,
            'Total Equity': total_equity,
            'Bot': bot_name,
            'Side': ''
        }
        portfolio_rows.append(total_row)

        return portfolio_rows

    except Exception as e:
        print(f"Error fetching {bot_name} portfolio data: {e}")
        return []

def update_csv_file(csv_path, new_rows):
    """Update CSV file with new daily data"""
    # Check if file exists
    file_exists = csv_path.exists()

    # Read existing data if file exists
    existing_data = []
    if file_exists:
        try:
            df = pd.read_csv(csv_path)
            existing_data = df.to_dict('records')
        except Exception as e:
            print(f"Warning: Could not read existing CSV: {e}")

    # Append new rows
    all_rows = existing_data + new_rows

    # Write updated data
    if all_rows:
        df = pd.DataFrame(all_rows)
        df.to_csv(csv_path, index=False)
        return True

    return False

def create_combined_portfolio():
    """Create combined portfolio CSV with both bots"""
    dee_api = tradeapi.REST(
        DEE_BOT_CONFIG['API_KEY'],
        DEE_BOT_CONFIG['SECRET_KEY'],
        DEE_BOT_CONFIG['BASE_URL'],
        api_version='v2'
    )

    shorgan_api = tradeapi.REST(
        SHORGAN_BOT_CONFIG['API_KEY'],
        SHORGAN_BOT_CONFIG['SECRET_KEY'],
        SHORGAN_BOT_CONFIG['BASE_URL'],
        api_version='v2'
    )

    # Fetch data for both bots
    dee_rows = get_portfolio_data(dee_api, 'DEE-BOT')
    shorgan_rows = get_portfolio_data(shorgan_api, 'SHORGAN-BOT')

    # Update individual CSV files
    if dee_rows:
        update_csv_file(DEE_CSV, dee_rows)
        print(f"[OK] Updated DEE-BOT CSV: {DEE_CSV}")

    if shorgan_rows:
        update_csv_file(SHORGAN_CSV, shorgan_rows)
        print(f"[OK] Updated SHORGAN-BOT CSV: {SHORGAN_CSV}")

    # Create combined CSV
    combined_rows = dee_rows + shorgan_rows
    if combined_rows:
        update_csv_file(COMBINED_CSV, combined_rows)
        print(f"[OK] Updated Combined CSV: {COMBINED_CSV}")

        # Calculate and display summary
        dee_total = [r for r in dee_rows if r['Ticker'] == 'TOTAL'][0]
        shorgan_total = [r for r in shorgan_rows if r['Ticker'] == 'TOTAL'][0]

        print("\n" + "="*60)
        print("PORTFOLIO UPDATE SUMMARY")
        print("="*60)
        print(f"Date: {dee_total['Date']}")
        print(f"\nDEE-BOT:")
        print(f"  Total Equity: ${dee_total['Total Equity']:,.2f}")
        print(f"  Cash Balance: ${dee_total['Cash Balance']:,.2f}")
        print(f"  Unrealized P&L: ${dee_total['PnL']:,.2f}")
        print(f"  Positions: {len(dee_rows) - 1}")

        print(f"\nSHORGAN-BOT:")
        print(f"  Total Equity: ${shorgan_total['Total Equity']:,.2f}")
        print(f"  Cash Balance: ${shorgan_total['Cash Balance']:,.2f}")
        print(f"  Unrealized P&L: ${shorgan_total['PnL']:,.2f}")
        print(f"  Positions: {len(shorgan_rows) - 1}")

        combined_equity = dee_total['Total Equity'] + shorgan_total['Total Equity']
        combined_pnl = dee_total['PnL'] + shorgan_total['PnL']
        combined_return = ((combined_equity - 200000) / 200000) * 100

        print(f"\nCOMBINED:")
        print(f"  Total Equity: ${combined_equity:,.2f}")
        print(f"  Total P&L: ${combined_pnl:,.2f}")
        print(f"  Total Return: {combined_return:+.2f}%")
        print("="*60)

    return combined_rows

def main():
    """Main execution"""
    print("[STATUS] Updating Portfolio CSV Files...")
    print(f"Output Directory: {OUTPUT_DIR}")

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Create/update portfolio CSVs
    combined_data = create_combined_portfolio()

    if combined_data:
        print("\n[SUCCESS] Portfolio CSV update complete!")
        print("\nGenerate performance graph with:")
        print("  python generate_performance_graph.py")
    else:
        print("\n[ERROR] No portfolio data to update")

if __name__ == "__main__":
    main()