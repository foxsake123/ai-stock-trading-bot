"""Backfill missing performance data from Alpaca portfolio history"""
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetPortfolioHistoryRequest

def get_portfolio_history(api_key, secret_key, paper=True, start_date=None):
    """Get daily portfolio history from Alpaca"""
    client = TradingClient(api_key, secret_key, paper=paper)

    request = GetPortfolioHistoryRequest(
        period="3M",  # Last 3 months
        timeframe="1D"  # Daily
    )

    history = client.get_portfolio_history(request)

    # Convert to list of {date, value} records
    records = []
    for i, timestamp in enumerate(history.timestamp):
        dt = datetime.fromtimestamp(timestamp)
        records.append({
            'date': dt.strftime('%Y-%m-%d'),
            'value': history.equity[i]
        })

    return records

def backfill_performance_history():
    """Backfill missing dates in performance history"""

    # Load existing history
    history_file = 'data/daily/performance/performance_history.json'
    with open(history_file, 'r') as f:
        data = json.load(f)

    existing_dates = {r['date'] for r in data['daily_records']}
    print(f"Existing records: {len(existing_dates)}")
    print(f"Date range: {min(existing_dates)} to {max(existing_dates)}")

    # Get DEE-BOT history
    print("\nFetching DEE-BOT portfolio history...")
    dee_history = get_portfolio_history(
        os.getenv('ALPACA_API_KEY_DEE'),
        os.getenv('ALPACA_SECRET_KEY_DEE'),
        paper=True
    )
    print(f"  Got {len(dee_history)} records")

    # Get SHORGAN Paper history
    print("Fetching SHORGAN Paper portfolio history...")
    shorgan_history = get_portfolio_history(
        os.getenv('ALPACA_API_KEY_SHORGAN'),
        os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
        paper=True
    )
    print(f"  Got {len(shorgan_history)} records")

    # Get SHORGAN Live history
    print("Fetching SHORGAN Live portfolio history...")
    try:
        live_history = get_portfolio_history(
            os.getenv('ALPACA_API_KEY_SHORGAN_LIVE'),
            os.getenv('ALPACA_SECRET_KEY_SHORGAN_LIVE'),
            paper=False
        )
        print(f"  Got {len(live_history)} records")
    except Exception as e:
        print(f"  Error: {e}")
        live_history = []

    # Create lookup dicts
    dee_by_date = {r['date']: r['value'] for r in dee_history}
    shorgan_by_date = {r['date']: r['value'] for r in shorgan_history}
    live_by_date = {r['date']: r['value'] for r in live_history}

    # Find all unique dates
    all_dates = set(dee_by_date.keys()) | set(shorgan_by_date.keys())
    new_dates = all_dates - existing_dates

    print(f"\nNew dates to add: {len(new_dates)}")

    # Add missing records
    added = 0
    for date in sorted(new_dates):
        dee_val = dee_by_date.get(date, 0)
        shorgan_val = shorgan_by_date.get(date, 0)
        live_val = live_by_date.get(date, 0)

        if dee_val > 0 and shorgan_val > 0:
            record = {
                "date": date,
                "timestamp": f"{date}T16:00:00",
                "dee_bot": {
                    "value": dee_val,
                    "daily_pnl": 0,
                    "total_return": ((dee_val / 100000) - 1) * 100
                },
                "shorgan_bot": {
                    "value": shorgan_val,
                    "daily_pnl": 0,
                    "total_return": ((shorgan_val / 100000) - 1) * 100
                },
                "shorgan_live": {
                    "value": live_val if live_val > 0 else 0,
                    "daily_pnl": 0,
                    "total_return": ((live_val / 3000) - 1) * 100 if live_val > 0 else 0
                },
                "combined": {
                    "total_value": dee_val + shorgan_val + live_val,
                    "total_daily_pnl": 0,
                    "total_return": (((dee_val + shorgan_val) / 200000) - 1) * 100,
                    "total_positions": 0,
                    "total_orders_today": 0
                }
            }
            data['daily_records'].append(record)
            added += 1
            print(f"  Added {date}: DEE=${dee_val:,.2f}, SHORGAN=${shorgan_val:,.2f}")

    # Sort by date
    data['daily_records'].sort(key=lambda x: x['date'])

    # Save updated history
    with open(history_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\nBackfill complete!")
    print(f"  Added {added} new records")
    print(f"  Total records: {len(data['daily_records'])}")
    print(f"  Date range: {data['daily_records'][0]['date']} to {data['daily_records'][-1]['date']}")

if __name__ == "__main__":
    backfill_performance_history()
