import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

#!/usr/bin/env python3
"""
Daily Portfolio Performance Tracker
Archives performance metrics and reports to index folder
"""

import json
import csv
import os
import shutil
from datetime import datetime, timedelta
import pandas as pd
import alpaca_trade_api as tradeapi
from pathlib import Path

# Configuration
API_KEY = os.getenv('ALPACA_API_KEY_SHORGAN')
API_SECRET = os.getenv('ALPACA_SECRET_KEY_SHORGAN')
BASE_URL = 'https://paper-api.alpaca.markets'

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

def get_portfolio_performance():
    """Get current portfolio performance metrics"""
    try:
        account = api.get_account()
        positions = api.list_positions()

        # Calculate metrics
        total_value = float(account.portfolio_value)
        buying_power = float(account.buying_power)
        day_pl = float(account.equity) - float(account.last_equity)
        day_pl_pct = (day_pl / float(account.last_equity)) * 100 if float(account.last_equity) > 0 else 0

        # Position details
        position_data = []
        for position in positions:
            pos_data = {
                'symbol': position.symbol,
                'qty': int(position.qty),
                'market_value': float(position.market_value),
                'cost_basis': float(position.cost_basis),
                'unrealized_pl': float(position.unrealized_pl),
                'unrealized_plpc': float(position.unrealized_plpc) * 100,
                'current_price': float(position.current_price),
                'avg_entry_price': float(position.avg_entry_price)
            }
            position_data.append(pos_data)

        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'portfolio_value': total_value,
            'buying_power': buying_power,
            'day_pl': day_pl,
            'day_pl_pct': day_pl_pct,
            'position_count': len(positions),
            'positions': position_data
        }
    except Exception as e:
        print(f"Error getting portfolio performance: {e}")
        return None

def save_performance_to_csv(performance_data):
    """Save performance data to CSV in index folder"""
    date_str = performance_data['date']

    # Create performance CSV path
    perf_dir = PROJECT_ROOT / 'docs' / 'index' / 'portfolio-performance'
    perf_dir.mkdir(parents=True, exist_ok=True)

    csv_file = perf_dir / f'performance_{date_str}.csv'

    # Write main metrics
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Date', performance_data['date']])
        writer.writerow(['Time', performance_data['time']])
        writer.writerow(['Portfolio Value', f"${performance_data['portfolio_value']:,.2f}"])
        writer.writerow(['Buying Power', f"${performance_data['buying_power']:,.2f}"])
        writer.writerow(['Day P&L', f"${performance_data['day_pl']:,.2f}"])
        writer.writerow(['Day P&L %', f"{performance_data['day_pl_pct']:.2f}%"])
        writer.writerow(['Position Count', performance_data['position_count']])
        writer.writerow([])  # Empty row

        # Write position details
        if performance_data['positions']:
            writer.writerow(['Symbol', 'Quantity', 'Market Value', 'Cost Basis', 'Unrealized P&L', 'P&L %', 'Current Price', 'Avg Entry'])
            for pos in performance_data['positions']:
                writer.writerow([
                    pos['symbol'],
                    pos['qty'],
                    f"${pos['market_value']:,.2f}",
                    f"${pos['cost_basis']:,.2f}",
                    f"${pos['unrealized_pl']:,.2f}",
                    f"{pos['unrealized_plpc']:.2f}%",
                    f"${pos['current_price']:.2f}",
                    f"${pos['avg_entry_price']:.2f}"
                ])

    print(f"Performance CSV saved to: {csv_file}")
    return csv_file

def archive_daily_reports():
    """Archive all daily reports to index folder"""
    date_str = datetime.now().strftime('%Y-%m-%d')

    # Reports to archive
    report_paths = [
        {
            'source': Path('../../scripts-and-data/automation/legacy/02_data/research/reports/pre_market_daily'),
            'dest': Path('../../docs/index/reports-md/pre-market'),
            'pattern': f'*{date_str}*.json'
        },
        {
            'source': Path('../../docs/reports/premarket'),
            'dest': Path('../../docs/index/reports-md/pre-market'),
            'pattern': f'*{date_str}*.txt'
        },
        {
            'source': Path('../../scripts-and-data/data/reports/post-market'),
            'dest': Path('../../docs/index/reports-md/post-market'),
            'pattern': f'*{date_str}*.txt'
        }
    ]

    archived_count = 0

    for report in report_paths:
        if report['source'].exists():
            files = list(report['source'].glob(report['pattern']))
            for file in files:
                dest_dir = report['dest'] / date_str
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_file = dest_dir / file.name

                try:
                    shutil.copy2(file, dest_file)
                    print(f"Archived: {file.name} to {dest_file}")
                    archived_count += 1
                except Exception as e:
                    print(f"Error archiving {file.name}: {e}")

    return archived_count

def update_performance_history():
    """Update the master performance history file"""
    history_file = Path('../../docs/index/portfolio-performance/performance_history.csv')

    # Get current performance
    performance = get_portfolio_performance()
    if not performance:
        print("Could not get performance data")
        return

    # Read existing history or create new
    if history_file.exists():
        df = pd.read_csv(history_file)
    else:
        df = pd.DataFrame(columns=['date', 'portfolio_value', 'day_pl', 'day_pl_pct', 'position_count'])

    # Add today's data if not already present
    today = performance['date']
    if today not in df['date'].values:
        new_row = {
            'date': today,
            'portfolio_value': performance['portfolio_value'],
            'day_pl': performance['day_pl'],
            'day_pl_pct': performance['day_pl_pct'],
            'position_count': performance['position_count']
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # Save updated history
        df.to_csv(history_file, index=False)
        print(f"Updated performance history: {history_file}")
    else:
        print(f"Performance for {today} already recorded")

def create_daily_summary_md():
    """Create markdown summary of daily performance"""
    performance = get_portfolio_performance()
    if not performance:
        return

    date_str = performance['date']
    summary_dir = Path('../../docs/index/reports-md/daily-summary')
    summary_dir.mkdir(parents=True, exist_ok=True)

    summary_file = summary_dir / f'summary_{date_str}.md'

    with open(summary_file, 'w') as f:
        f.write(f"# Daily Performance Summary - {date_str}\n\n")
        f.write(f"Generated at: {performance['time']}\n\n")

        f.write("## Portfolio Metrics\n\n")
        f.write(f"- **Portfolio Value**: ${performance['portfolio_value']:,.2f}\n")
        f.write(f"- **Buying Power**: ${performance['buying_power']:,.2f}\n")
        f.write(f"- **Day P&L**: ${performance['day_pl']:,.2f} ({performance['day_pl_pct']:.2f}%)\n")
        f.write(f"- **Active Positions**: {performance['position_count']}\n\n")

        if performance['positions']:
            f.write("## Position Details\n\n")
            f.write("| Symbol | Qty | Market Value | Unrealized P&L | P&L % |\n")
            f.write("|--------|-----|--------------|----------------|-------|\n")

            for pos in sorted(performance['positions'], key=lambda x: x['unrealized_plpc'], reverse=True):
                f.write(f"| {pos['symbol']} | {pos['qty']} | ${pos['market_value']:,.2f} | ")
                f.write(f"${pos['unrealized_pl']:,.2f} | {pos['unrealized_plpc']:.2f}% |\n")

    print(f"Daily summary saved to: {summary_file}")
    return summary_file

def main():
    """Main execution"""
    print("=" * 60)
    print("DAILY PERFORMANCE TRACKER")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Get and save current performance
    print("\n1. Capturing current performance...")
    performance = get_portfolio_performance()
    if performance:
        save_performance_to_csv(performance)
        create_daily_summary_md()

    # 2. Update performance history
    print("\n2. Updating performance history...")
    update_performance_history()

    # 3. Archive daily reports
    print("\n3. Archiving daily reports...")
    archived = archive_daily_reports()
    print(f"Archived {archived} reports")

    print("\n" + "=" * 60)
    print("DAILY PERFORMANCE TRACKING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()