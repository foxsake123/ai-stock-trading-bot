"""
Update Trade Outcomes from Alpaca
Fetches filled orders and updates ML training data with actual outcomes.

Run daily after market close to update P&L on closed positions.

Usage:
    python scripts/ml/update_outcomes.py
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderStatus, QueryOrderStatus

load_dotenv()

# Import data collector
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.ml.data_collector import MLDataCollector

def get_filled_orders(api: TradingClient, days: int = 7) -> list:
    """Get filled orders from last N days"""
    try:
        request = GetOrdersRequest(
            status=QueryOrderStatus.CLOSED,
            after=(datetime.now() - timedelta(days=days)).isoformat()
        )
        orders = api.get_orders(filter=request)
        return [o for o in orders if o.status == OrderStatus.FILLED]
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return []

def get_current_positions(api: TradingClient) -> dict:
    """Get current positions with cost basis"""
    try:
        positions = api.get_all_positions()
        return {p.symbol: {
            "qty": float(p.qty),
            "avg_entry": float(p.avg_entry_price),
            "current_price": float(p.current_price),
            "unrealized_pnl": float(p.unrealized_pl),
            "unrealized_pnl_pct": float(p.unrealized_plpc) * 100
        } for p in positions}
    except Exception as e:
        print(f"Error fetching positions: {e}")
        return {}

def update_outcomes_from_alpaca():
    """Update ML training data with outcomes from Alpaca"""
    collector = MLDataCollector()

    # Load API clients
    accounts = []

    # DEE-BOT Paper
    if os.getenv('ALPACA_API_KEY_DEE'):
        accounts.append(("DEE-BOT", TradingClient(
            os.getenv('ALPACA_API_KEY_DEE'),
            os.getenv('ALPACA_SECRET_KEY_DEE'),
            paper=True
        )))

    # SHORGAN Paper
    if os.getenv('ALPACA_API_KEY_SHORGAN'):
        accounts.append(("SHORGAN-Paper", TradingClient(
            os.getenv('ALPACA_API_KEY_SHORGAN'),
            os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
            paper=True
        )))

    # SHORGAN Live
    if os.getenv('ALPACA_API_KEY_SHORGAN_LIVE'):
        accounts.append(("SHORGAN-Live", TradingClient(
            os.getenv('ALPACA_API_KEY_SHORGAN_LIVE'),
            os.getenv('ALPACA_SECRET_KEY_SHORGAN_LIVE'),
            paper=False
        )))

    print("=" * 60)
    print("ML OUTCOME UPDATE")
    print("=" * 60)

    # Load existing trade records
    trades_file = collector.trades_file
    with open(trades_file, 'r') as f:
        data = json.load(f)

    pending_records = [r for r in data["records"] if r["outcome"]["filled"] is None]
    print(f"Pending trades to update: {len(pending_records)}")

    updates = 0

    for account_name, api in accounts:
        print(f"\n--- {account_name} ---")

        # Get filled orders
        filled_orders = get_filled_orders(api, days=14)
        print(f"Filled orders (14d): {len(filled_orders)}")

        # Get current positions
        positions = get_current_positions(api)
        print(f"Current positions: {len(positions)}")

        # Match orders to pending records
        for order in filled_orders:
            symbol = order.symbol
            fill_date = order.filled_at.strftime('%Y-%m-%d') if order.filled_at else None
            fill_price = float(order.filled_avg_price) if order.filled_avg_price else None

            # Find matching pending record
            for record in pending_records:
                if record["symbol"] == symbol and record["outcome"]["filled"] is None:
                    # Update fill info
                    record["outcome"]["filled"] = True
                    record["outcome"]["fill_price"] = fill_price

                    # Check if position is closed (not in current positions)
                    if symbol not in positions:
                        # Position closed - try to find exit price from orders
                        # For now, mark as needing manual update
                        record["outcome"]["status"] = "closed_needs_exit_price"
                    else:
                        # Position still open - update unrealized P&L
                        pos = positions[symbol]
                        record["outcome"]["current_price"] = pos["current_price"]
                        record["outcome"]["unrealized_pnl_pct"] = pos["unrealized_pnl_pct"]
                        record["outcome"]["status"] = "open"

                    updates += 1
                    print(f"  Updated: {symbol} filled @ ${fill_price}")
                    break

    # Save updates
    if updates > 0:
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(trades_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nSaved {updates} updates")

    # Print statistics
    print("\n" + "=" * 60)
    stats = collector.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    update_outcomes_from_alpaca()
