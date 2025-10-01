#!/usr/bin/env python3
"""
DEE-BOT Position Updater
Updates current prices and P&L for DEE-BOT positions
Fixes the stale price issue in dee-bot-positions.csv
"""

import yfinance as yf
import pandas as pd
import csv
from datetime import datetime
from pathlib import Path

# File paths
CSV_FILE = Path("scripts-and-data/daily-csv/dee-bot-positions.csv")

def get_current_price(symbol):
    """Get current stock price using yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Try multiple price fields
        price = (info.get('regularMarketPrice') or
                info.get('currentPrice') or
                info.get('previousClose') or
                info.get('bid') or
                info.get('ask'))

        if price:
            return float(price)

        # Fallback to historical data
        hist = ticker.history(period="1d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])

        return None

    except Exception as e:
        print(f"Error getting price for {symbol}: {e}")
        return None

def update_positions():
    """Update DEE-BOT positions with current prices and P&L"""

    if not CSV_FILE.exists():
        print(f"Error: {CSV_FILE} not found")
        return

    print("="*60)
    print("DEE-BOT POSITION UPDATER")
    print("="*60)
    print()

    # Read current positions
    df = pd.read_csv(CSV_FILE)

    if df.empty:
        print("No positions found in DEE-BOT CSV")
        return

    print("Updating positions:")
    print("-"*60)

    updated_rows = []

    for _, row in df.iterrows():
        symbol = row['symbol']
        quantity = int(row['quantity'])
        avg_price = float(row['avg_price'])

        print(f"Updating {symbol}... ", end="")

        # Get current price
        current_price = get_current_price(symbol)

        if current_price is None:
            print(f"FAILED - Using avg price ${avg_price:.2f}")
            current_price = avg_price
        else:
            print(f"${current_price:.2f}")

        # Calculate P&L
        position_value = quantity * current_price
        cost_basis = quantity * avg_price
        pnl = position_value - cost_basis
        pnl_pct = (pnl / cost_basis) * 100 if cost_basis > 0 else 0

        # Update row
        updated_row = {
            'symbol': symbol,
            'quantity': quantity,
            'avg_price': avg_price,
            'current_price': current_price,
            'pnl': round(pnl, 2),
            'pnl_pct': f"{pnl_pct:.2f}%",
            'side': row['side'],
            'date_acquired': row['date_acquired']
        }

        updated_rows.append(updated_row)

        # Show update
        print(f"  {symbol}: {quantity} @ ${avg_price:.2f} -> ${current_price:.2f} | P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)")

    # Write updated data
    print()
    print("Writing updated positions...")

    with open(CSV_FILE, 'w', newline='') as f:
        fieldnames = ['symbol', 'quantity', 'avg_price', 'current_price', 'pnl', 'pnl_pct', 'side', 'date_acquired']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"✅ Updated {len(updated_rows)} positions in {CSV_FILE}")

    # Summary
    total_pnl = sum(row['pnl'] for row in updated_rows)
    total_value = sum(row['quantity'] * row['current_price'] for row in updated_rows)

    print()
    print("SUMMARY:")
    print("-"*30)
    print(f"Positions: {len(updated_rows)}")
    print(f"Total Value: ${total_value:,.2f}")
    print(f"Total P&L: ${total_pnl:+,.2f}")
    print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

def check_logging_issues():
    """Diagnose DEE-BOT logging problems"""

    print("\nDEE-BOT LOGGING DIAGNOSIS:")
    print("-"*40)

    issues = []

    # Check if CSV exists
    if not CSV_FILE.exists():
        issues.append(f"❌ Position file missing: {CSV_FILE}")

    # Check CSV content
    try:
        df = pd.read_csv(CSV_FILE)

        if df.empty:
            issues.append("❌ No positions in CSV file")
        else:
            # Check for stale prices
            stale_count = 0
            for _, row in df.iterrows():
                if float(row['current_price']) == float(row['avg_price']):
                    stale_count += 1

            if stale_count > 0:
                issues.append(f"❌ {stale_count} positions have stale prices")

            # Check for zero P&L
            zero_pnl = df[df['pnl'] == 0.0]
            if len(zero_pnl) > 0:
                issues.append(f"❌ {len(zero_pnl)} positions showing zero P&L")

    except Exception as e:
        issues.append(f"❌ Error reading CSV: {e}")

    # Check for update scripts
    update_scripts = [
        "scripts-and-data/automation/update-dee-bot-positions.py",
        "scripts-and-data/automation/execute-dee-bot.py",
        "01_trading_system/execute_dee_bot_trades.py"
    ]

    for script in update_scripts:
        if not Path(script).exists():
            issues.append(f"❌ Missing script: {script}")

    if not issues:
        print("✅ No issues found")
    else:
        print("Issues found:")
        for issue in issues:
            print(f"  {issue}")

    print()
    print("RECOMMENDATIONS:")
    print("1. Run this script daily to update prices")
    print("2. Set up automated price updates")
    print("3. Check Alpaca API connectivity")
    print("4. Verify trade execution logging")

if __name__ == "__main__":
    check_logging_issues()
    print()
    update_positions()