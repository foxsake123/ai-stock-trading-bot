#!/usr/bin/env python3
"""
Update Performance History with Daily Portfolio Values
========================================================
Fetches historical daily close values from Alpaca for both bots
and updates the performance_history.json file.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

# File paths
PERFORMANCE_JSON = "data/daily/performance/performance_history.json"

# Initialize API clients
dee_api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY_DEE'),
    os.getenv('ALPACA_SECRET_KEY_DEE'),
    'https://paper-api.alpaca.markets',
    api_version='v2'
)

shorgan_api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY_SHORGAN'),
    os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    'https://paper-api.alpaca.markets',
    api_version='v2'
)

def fetch_portfolio_history(api, bot_name):
    """Fetch portfolio history from Alpaca"""
    print(f"Fetching {bot_name} portfolio history...")

    # Get 1 month of daily data
    history = api.get_portfolio_history(period='1M', timeframe='1D')

    # Convert to dictionary by date
    data_by_date = {}
    for i, ts in enumerate(history.timestamp):
        dt = datetime.fromtimestamp(ts)
        date_str = dt.strftime('%Y-%m-%d')
        equity = history.equity[i]

        # Skip zero values (before account was active)
        if equity > 0:
            data_by_date[date_str] = equity

    print(f"  Found {len(data_by_date)} days with data")
    return data_by_date

def update_performance_json(dee_data, shorgan_data):
    """Update or create performance_history.json"""

    # Load existing data if it exists
    try:
        with open(PERFORMANCE_JSON, 'r') as f:
            performance_data = json.load(f)
            existing_records = {r['date']: r for r in performance_data.get('daily_records', [])}
    except FileNotFoundError:
        performance_data = {
            "start_date": "2025-09-08",
            "daily_records": []
        }
        existing_records = {}

    # Get all unique dates from both bots
    all_dates = sorted(set(list(dee_data.keys()) + list(shorgan_data.keys())))

    print(f"\nProcessing {len(all_dates)} dates...")

    # Create records for each date
    new_records = []
    for date_str in all_dates:
        # Use existing record if available, otherwise create new one
        if date_str in existing_records:
            record = existing_records[date_str]
            # Update values if they're from Alpaca
            if date_str in dee_data:
                record['dee_bot']['value'] = dee_data[date_str]
            if date_str in shorgan_data:
                record['shorgan_bot']['value'] = shorgan_data[date_str]
        else:
            # Create new record
            dee_value = dee_data.get(date_str, 100000.0)
            shorgan_value = shorgan_data.get(date_str, 100000.0)

            record = {
                "date": date_str,
                "timestamp": f"{date_str}T16:00:00",
                "dee_bot": {
                    "value": dee_value,
                    "daily_pnl": 0,
                    "total_return": ((dee_value - 100000) / 100000) * 100
                },
                "shorgan_bot": {
                    "value": shorgan_value,
                    "daily_pnl": 0,
                    "total_return": ((shorgan_value - 100000) / 100000) * 100
                },
                "combined": {
                    "total_value": dee_value + shorgan_value,
                    "total_daily_pnl": 0,
                    "total_return": ((dee_value + shorgan_value - 200000) / 200000) * 100,
                    "total_positions": 0,
                    "total_orders_today": 0
                }
            }

        new_records.append(record)

    # Update the performance data
    performance_data['daily_records'] = new_records

    # Save to file
    with open(PERFORMANCE_JSON, 'w') as f:
        json.dump(performance_data, f, indent=2)

    print(f"\n[SUCCESS] Updated {PERFORMANCE_JSON} with {len(new_records)} records")

    # Show summary
    print(f"\nDate range: {all_dates[0]} to {all_dates[-1]}")

    # Find first and last dates with actual data for each bot
    dee_dates = sorted(dee_data.keys())
    shorgan_dates = sorted(shorgan_data.keys())

    if dee_dates:
        print(f"DEE-BOT: ${dee_data[dee_dates[0]]:,.2f} → ${dee_data[dee_dates[-1]]:,.2f} ({dee_dates[0]} to {dee_dates[-1]})")

    if shorgan_dates:
        print(f"SHORGAN-BOT: ${shorgan_data[shorgan_dates[0]]:,.2f} → ${shorgan_data[shorgan_dates[-1]]:,.2f} ({shorgan_dates[0]} to {shorgan_dates[-1]})")

    return len(new_records)

def main():
    print("="*70)
    print("UPDATING PERFORMANCE HISTORY WITH DAILY PORTFOLIO VALUES")
    print("="*70)

    # Fetch data from both bots
    dee_data = fetch_portfolio_history(dee_api, "DEE-BOT")
    shorgan_data = fetch_portfolio_history(shorgan_api, "SHORGAN-BOT")

    # Update JSON file
    count = update_performance_json(dee_data, shorgan_data)

    print("\n" + "="*70)
    print(f"COMPLETE - {count} daily records saved")
    print("="*70)
    print("\nNext step: Run 'python generate_performance_graph.py' to see the updated chart!")

if __name__ == "__main__":
    main()
