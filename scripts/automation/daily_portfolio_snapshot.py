"""
Daily Portfolio Snapshot Generator
Pulls current positions from Alpaca and saves to dated CSV files
Run this daily at market close to track portfolio history
"""

import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Alpaca API Configuration
API_KEY = 'PK6FZK4DAQVTD7DYVH78'
API_SECRET = 'OJPdMDllGBYhiWLVpLcRLEFjmof8s6NHKKrKC2C9'
BASE_URL = 'https://paper-api.alpaca.markets'

# Initialize API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

def get_current_positions():
    """Fetch all current positions from Alpaca"""
    try:
        positions = api.list_positions()

        # Convert to list of dictionaries
        position_data = []
        for pos in positions:
            position_data.append({
                'symbol': pos.symbol,
                'quantity': int(pos.qty),
                'avg_price': float(pos.avg_entry_price),
                'current_price': float(pos.current_price),
                'market_value': float(pos.market_value),
                'cost_basis': float(pos.cost_basis),
                'unrealized_pnl': float(pos.unrealized_pl),
                'unrealized_pnl_pct': float(pos.unrealized_plpc) * 100,
                'change_today': float(pos.change_today) if hasattr(pos, 'change_today') else 0,
                'change_today_pct': float(pos.change_today_percent) if hasattr(pos, 'change_today_percent') else 0,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

        return position_data
    except Exception as e:
        print(f"Error fetching positions: {e}")
        return []

def categorize_positions(positions):
    """Categorize positions into SHORGAN-BOT and DEE-BOT"""

    # DEE-BOT stocks (defensive S&P 100)
    dee_bot_symbols = ['PG', 'JNJ', 'KO', 'WMT', 'HD', 'MCD', 'PEP', 'CVX', 'XOM', 'LLY',
                       'UNH', 'V', 'MA', 'COST', 'CL', 'KMB', 'MRK', 'PFE', 'ABT', 'TMO']

    shorgan_positions = []
    dee_positions = []

    for pos in positions:
        if pos['symbol'] in dee_bot_symbols:
            dee_positions.append(pos)
        else:
            shorgan_positions.append(pos)

    return shorgan_positions, dee_positions

def save_daily_snapshot(shorgan_positions, dee_positions):
    """Save positions to daily snapshot files"""

    # Create date-stamped directory
    today = datetime.now().strftime('%Y-%m-%d')
    snapshot_dir = f'scripts-and-data/daily-snapshots/{today}'
    os.makedirs(snapshot_dir, exist_ok=True)

    # Save SHORGAN-BOT positions
    if shorgan_positions:
        shorgan_df = pd.DataFrame(shorgan_positions)
        shorgan_file = f'{snapshot_dir}/shorgan-bot-snapshot-{today}.csv'
        shorgan_df.to_csv(shorgan_file, index=False)
        print(f"✅ SHORGAN-BOT snapshot saved: {shorgan_file}")
        print(f"   {len(shorgan_positions)} positions, Total value: ${shorgan_df['market_value'].sum():,.2f}")
    else:
        print("⚠️ No SHORGAN-BOT positions found")

    # Save DEE-BOT positions
    if dee_positions:
        dee_df = pd.DataFrame(dee_positions)
        dee_file = f'{snapshot_dir}/dee-bot-snapshot-{today}.csv'
        dee_df.to_csv(dee_file, index=False)
        print(f"✅ DEE-BOT snapshot saved: {dee_file}")
        print(f"   {len(dee_positions)} positions, Total value: ${dee_df['market_value'].sum():,.2f}")
    else:
        print("⚠️ No DEE-BOT positions found")

    # Also update the main position files
    update_main_position_files(shorgan_positions, dee_positions)

    return snapshot_dir

def update_main_position_files(shorgan_positions, dee_positions):
    """Update the main position tracking files"""

    # Update SHORGAN-BOT main file
    if shorgan_positions:
        shorgan_df = pd.DataFrame(shorgan_positions)
        shorgan_df.to_csv('scripts-and-data/daily-csv/shorgan-bot-positions.csv', index=False)
        print("✅ Updated main SHORGAN-BOT position file")

    # Update DEE-BOT main file
    if dee_positions:
        dee_df = pd.DataFrame(dee_positions)
        # Format DEE-BOT specific columns
        dee_df['pnl'] = dee_df['unrealized_pnl']
        dee_df['pnl_pct'] = dee_df['unrealized_pnl_pct'].apply(lambda x: f"{x:.2f}%")
        dee_df['side'] = 'long'
        dee_df['date_acquired'] = datetime.now().strftime('%Y-%m-%d')

        # Select columns for DEE-BOT format
        dee_columns = ['symbol', 'quantity', 'avg_price', 'current_price', 'pnl', 'pnl_pct', 'side', 'date_acquired']
        dee_output = dee_df[dee_columns]
        dee_output.to_csv('scripts-and-data/daily-csv/dee-bot-positions.csv', index=False)
        print("✅ Updated main DEE-BOT position file")

def generate_summary_report(shorgan_positions, dee_positions):
    """Generate a summary report of both portfolios"""

    today = datetime.now().strftime('%Y-%m-%d %I:%M %p ET')

    print("\n" + "="*60)
    print(f"DAILY PORTFOLIO SNAPSHOT - {today}")
    print("="*60)

    # Account summary
    try:
        account = api.get_account()
        print(f"\n📊 ACCOUNT OVERVIEW:")
        print(f"Total Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"Total Buying Power: ${float(account.buying_power):,.2f}")
        print(f"Total Cash: ${float(account.cash):,.2f}")
    except:
        pass

    # SHORGAN-BOT Summary
    if shorgan_positions:
        shorgan_df = pd.DataFrame(shorgan_positions)
        total_value = shorgan_df['market_value'].sum()
        total_pnl = shorgan_df['unrealized_pnl'].sum()

        print(f"\n🚀 SHORGAN-BOT (Catalyst Strategy):")
        print(f"Positions: {len(shorgan_positions)}")
        print(f"Total Value: ${total_value:,.2f}")
        print(f"Unrealized P&L: ${total_pnl:+,.2f}")

        # Top performers
        top_gainers = shorgan_df.nlargest(3, 'unrealized_pnl_pct')
        print("\nTop Gainers:")
        for _, row in top_gainers.iterrows():
            print(f"  {row['symbol']}: {row['unrealized_pnl_pct']:+.2f}% (${row['unrealized_pnl']:+,.2f})")

        # Worst performers
        worst = shorgan_df.nsmallest(3, 'unrealized_pnl_pct')
        print("\nWorst Performers:")
        for _, row in worst.iterrows():
            print(f"  {row['symbol']}: {row['unrealized_pnl_pct']:+.2f}% (${row['unrealized_pnl']:+,.2f})")

    # DEE-BOT Summary
    if dee_positions:
        dee_df = pd.DataFrame(dee_positions)
        total_value = dee_df['market_value'].sum()
        total_pnl = dee_df['unrealized_pnl'].sum()

        print(f"\n🛡️ DEE-BOT (Beta-Neutral Strategy):")
        print(f"Positions: {len(dee_positions)}")
        print(f"Total Value: ${total_value:,.2f}")
        print(f"Unrealized P&L: ${total_pnl:+,.2f}")

        print("\nPositions:")
        for _, row in dee_df.iterrows():
            print(f"  {row['symbol']}: {row['quantity']} shares @ ${row['avg_price']:.2f}")

    print("\n" + "="*60)

    # Save summary to file
    summary_file = f'scripts-and-data/daily-snapshots/summary-{datetime.now().strftime("%Y-%m-%d")}.txt'
    os.makedirs(os.path.dirname(summary_file), exist_ok=True)

    with open(summary_file, 'w') as f:
        f.write(f"Portfolio Snapshot - {today}\n")
        f.write("="*60 + "\n\n")

        if shorgan_positions:
            f.write(f"SHORGAN-BOT: {len(shorgan_positions)} positions, ${shorgan_df['market_value'].sum():,.2f}\n")
            f.write(f"P&L: ${shorgan_df['unrealized_pnl'].sum():+,.2f}\n\n")

        if dee_positions:
            f.write(f"DEE-BOT: {len(dee_positions)} positions, ${dee_df['market_value'].sum():,.2f}\n")
            f.write(f"P&L: ${dee_df['unrealized_pnl'].sum():+,.2f}\n")

    print(f"✅ Summary saved to: {summary_file}")

def main():
    print("="*60)
    print("GENERATING DAILY PORTFOLIO SNAPSHOT")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print("="*60)

    # Fetch current positions
    print("\n📡 Fetching positions from Alpaca...")
    all_positions = get_current_positions()

    if not all_positions:
        print("❌ No positions found or API error")
        return

    # Categorize positions
    print("📂 Categorizing positions...")
    shorgan_positions, dee_positions = categorize_positions(all_positions)

    # Save snapshots
    print("\n💾 Saving daily snapshots...")
    snapshot_dir = save_daily_snapshot(shorgan_positions, dee_positions)

    # Generate summary
    generate_summary_report(shorgan_positions, dee_positions)

    print(f"\n✅ Daily snapshot complete!")
    print(f"📁 Files saved in: {snapshot_dir}")
    print("="*60)

if __name__ == "__main__":
    main()