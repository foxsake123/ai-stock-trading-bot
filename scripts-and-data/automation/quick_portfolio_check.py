"""
Quick Portfolio Check
Shows current positions for both SHORGAN-BOT and DEE-BOT
Can be run anytime during market hours for a quick status check
"""

import pandas as pd
from datetime import datetime
import os

def load_current_positions():
    """Load the current position files"""

    # File paths
    shorgan_file = 'scripts-and-data/daily-csv/shorgan-bot-positions.csv'
    dee_file = 'scripts-and-data/daily-csv/dee-bot-positions.csv'

    # Load SHORGAN-BOT
    shorgan_positions = None
    if os.path.exists(shorgan_file):
        shorgan_positions = pd.read_csv(shorgan_file)

    # Load DEE-BOT
    dee_positions = None
    if os.path.exists(dee_file):
        dee_positions = pd.read_csv(dee_file)

    return shorgan_positions, dee_positions

def display_portfolio_summary():
    """Display a quick summary of both portfolios"""

    print("="*70)
    print(f"PORTFOLIO QUICK CHECK - {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    print("="*70)

    # Load positions
    shorgan_df, dee_df = load_current_positions()

    # SHORGAN-BOT Summary
    if shorgan_df is not None and not shorgan_df.empty:
        print("\n🚀 SHORGAN-BOT POSITIONS:")
        print("-"*50)

        total_value = shorgan_df['market_value'].sum()
        total_pnl = shorgan_df['unrealized_pnl'].sum()
        total_cost = shorgan_df['cost_basis'].sum()

        print(f"Total Positions: {len(shorgan_df)}")
        print(f"Total Value: ${total_value:,.2f}")
        print(f"Total Cost: ${total_cost:,.2f}")
        print(f"Unrealized P&L: ${total_pnl:+,.2f} ({(total_pnl/total_cost)*100:+.2f}%)")

        # Show each position
        print("\nPositions:")
        print(f"{'Symbol':<8} {'Shares':<8} {'Entry':<10} {'Current':<10} {'P&L':<12} {'%':<8}")
        print("-"*70)

        for _, row in shorgan_df.iterrows():
            symbol = row['symbol']
            qty = int(row['quantity'])
            entry = row['avg_price']
            current = row['current_price']
            pnl = row['unrealized_pnl']
            pnl_pct = row['unrealized_pnl_pct']

            # Color coding for console (optional)
            pnl_display = f"${pnl:+,.0f}"
            pct_display = f"{pnl_pct:+.1f}%"

            print(f"{symbol:<8} {qty:<8} ${entry:<9.2f} ${current:<9.2f} {pnl_display:<12} {pct_display:<8}")

        # Highlight key positions
        print("\n📌 KEY POSITIONS:")

        # Best performers
        best = shorgan_df.nlargest(3, 'unrealized_pnl_pct')
        print("Top Gainers:")
        for _, row in best.iterrows():
            print(f"  ✅ {row['symbol']}: {row['unrealized_pnl_pct']:+.2f}% (${row['unrealized_pnl']:+,.2f})")

        # Worst performers
        worst = shorgan_df.nsmallest(3, 'unrealized_pnl_pct')
        print("\nWorst Performers:")
        for _, row in worst.iterrows():
            print(f"  ⚠️ {row['symbol']}: {row['unrealized_pnl_pct']:+.2f}% (${row['unrealized_pnl']:+,.2f})")

        # Special alerts
        print("\n🔔 ALERTS:")

        # Check for CBRL (earnings)
        if 'CBRL' in shorgan_df['symbol'].values:
            cbrl = shorgan_df[shorgan_df['symbol'] == 'CBRL'].iloc[0]
            print(f"  🎯 CBRL: Earnings today! {cbrl['quantity']} shares @ ${cbrl['avg_price']:.2f}")

        # Check for INCY (FDA)
        if 'INCY' in shorgan_df['symbol'].values:
            incy = shorgan_df[shorgan_df['symbol'] == 'INCY'].iloc[0]
            print(f"  🎯 INCY: FDA decision Sept 19! {incy['quantity']} shares @ ${incy['avg_price']:.2f}")

        # Check for stops
        stops_near = shorgan_df[shorgan_df['unrealized_pnl_pct'] < -7]
        if not stops_near.empty:
            for _, row in stops_near.iterrows():
                print(f"  🛑 {row['symbol']}: Near stop loss! {row['unrealized_pnl_pct']:+.2f}%")

    # DEE-BOT Summary
    if dee_df is not None and not dee_df.empty:
        print("\n\n🛡️ DEE-BOT POSITIONS:")
        print("-"*50)

        print(f"Total Positions: {len(dee_df)}")

        print("\nPositions:")
        for _, row in dee_df.iterrows():
            symbol = row['symbol']
            qty = row['quantity']
            price = row['avg_price']
            print(f"  {symbol}: {qty} shares @ ${price:.2f}")

    print("\n" + "="*70)

    # Cash calculation estimate
    print("\n💰 ESTIMATED CASH AVAILABLE:")
    total_portfolio = 205338.41  # From last known total
    if shorgan_df is not None:
        positions_value = shorgan_df['market_value'].sum()
        if dee_df is not None and 'market_value' in dee_df.columns:
            positions_value += dee_df['market_value'].sum()
        elif dee_df is not None:
            # Estimate DEE-BOT value
            positions_value += 18189.05  # Last known DEE-BOT value

        cash = total_portfolio - positions_value
        print(f"Estimated Cash: ${cash:,.2f}")

    print("\n" + "="*70)
    print("Quick check complete!")

def main():
    """Run the quick portfolio check"""
    display_portfolio_summary()

    # Option to save to file
    save = input("\nSave this summary to file? (y/n): ").lower()
    if save == 'y':
        filename = f"scripts-and-data/daily-snapshots/quick-check-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Redirect output to file
        import sys
        original_stdout = sys.stdout
        with open(filename, 'w') as f:
            sys.stdout = f
            display_portfolio_summary()
            sys.stdout = original_stdout

        print(f"\n✅ Summary saved to: {filename}")

if __name__ == "__main__":
    main()