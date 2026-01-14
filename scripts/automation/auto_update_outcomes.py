#!/usr/bin/env python3
"""
Automated ML Outcome Update
===========================
Updates trade outcomes from Alpaca order history.
Run daily at 5:00 PM to capture closed positions.

Author: AI Trading Bot System
Date: January 13, 2026
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus

# Import health monitor
from scripts.core.health_monitor import get_health_monitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutcomeUpdater:
    """Updates ML training data with actual trade outcomes."""

    def __init__(self):
        self.data_file = PROJECT_ROOT / "data" / "ml_training" / "trade_outcomes.json"
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize Alpaca clients
        self.clients = {}

        # DEE-BOT Paper
        if os.getenv('ALPACA_API_KEY_DEE'):
            self.clients['DEE-BOT'] = TradingClient(
                os.getenv('ALPACA_API_KEY_DEE'),
                os.getenv('ALPACA_SECRET_KEY_DEE'),
                paper=True
            )

        # SHORGAN-BOT Paper
        if os.getenv('ALPACA_API_KEY_SHORGAN'):
            self.clients['SHORGAN-BOT'] = TradingClient(
                os.getenv('ALPACA_API_KEY_SHORGAN'),
                os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
                paper=True
            )

        # SHORGAN-BOT Live
        if os.getenv('ALPACA_API_KEY_SHORGAN_LIVE'):
            self.clients['SHORGAN-BOT-LIVE'] = TradingClient(
                os.getenv('ALPACA_API_KEY_SHORGAN_LIVE'),
                os.getenv('ALPACA_SECRET_KEY_SHORGAN_LIVE'),
                paper=False
            )

    def load_outcomes(self) -> List[Dict]:
        """Load existing outcome data."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load outcomes: {e}")
        return []

    def save_outcomes(self, data: List[Dict]):
        """Save outcome data."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(data)} outcome records")
        except Exception as e:
            logger.error(f"Failed to save outcomes: {e}")

    def get_filled_orders(
        self,
        client: TradingClient,
        lookback_days: int = 7
    ) -> List[Dict]:
        """Get filled orders from Alpaca."""
        try:
            request = GetOrdersRequest(
                status=QueryOrderStatus.ALL,
                limit=200
            )
            orders = client.get_orders(filter=request)

            cutoff = datetime.now() - timedelta(days=lookback_days)
            filled = []

            for order in orders:
                if order.filled_at and order.filled_at.replace(tzinfo=None) >= cutoff:
                    filled.append({
                        'order_id': str(order.id),
                        'symbol': order.symbol,
                        'side': order.side.value,
                        'qty': float(order.filled_qty or 0),
                        'filled_price': float(order.filled_avg_price) if order.filled_avg_price else None,
                        'filled_at': order.filled_at.isoformat()
                    })

            return filled
        except Exception as e:
            logger.error(f"Failed to get orders: {e}")
            return []

    def match_and_update(
        self,
        outcomes: List[Dict],
        filled_orders: List[Dict],
        bot_name: str
    ) -> int:
        """Match filled orders to outcome records and update."""
        updated_count = 0

        for outcome in outcomes:
            # Skip if already has outcome data
            if outcome.get('fill_price') and outcome.get('exit_price'):
                continue

            # Skip if different bot
            if outcome.get('bot') != bot_name:
                continue

            symbol = outcome.get('symbol')
            action = outcome.get('action', '').lower()

            # Find matching fill
            for order in filled_orders:
                if order['symbol'] != symbol:
                    continue

                # Match buy recommendation to buy order
                if action in ['buy', 'long'] and order['side'] == 'buy':
                    if not outcome.get('fill_price'):
                        outcome['fill_price'] = order['filled_price']
                        outcome['fill_date'] = order['filled_at']
                        outcome['fill_qty'] = order['qty']
                        updated_count += 1
                        logger.info(f"Updated fill for {symbol}: ${order['filled_price']}")

                # Match sell recommendation to sell order
                elif action in ['sell', 'exit', 'trim'] and order['side'] == 'sell':
                    if not outcome.get('exit_price'):
                        outcome['exit_price'] = order['filled_price']
                        outcome['exit_date'] = order['filled_at']
                        updated_count += 1
                        logger.info(f"Updated exit for {symbol}: ${order['filled_price']}")

            # Calculate P&L if both prices available
            if outcome.get('fill_price') and outcome.get('exit_price'):
                entry = outcome['fill_price']
                exit_price = outcome['exit_price']
                qty = outcome.get('fill_qty', outcome.get('shares', 0))

                if action in ['buy', 'long']:
                    pnl = (exit_price - entry) * qty
                    pnl_pct = (exit_price - entry) / entry * 100
                else:  # Short
                    pnl = (entry - exit_price) * qty
                    pnl_pct = (entry - exit_price) / entry * 100

                outcome['realized_pnl'] = round(pnl, 2)
                outcome['realized_pnl_pct'] = round(pnl_pct, 2)
                outcome['win'] = pnl > 0
                outcome['outcome_status'] = 'complete'

        return updated_count

    def update_all(self) -> Dict:
        """Update outcomes for all accounts."""
        outcomes = self.load_outcomes()
        initial_count = len(outcomes)

        results = {
            'initial_records': initial_count,
            'updates_by_bot': {},
            'total_updated': 0
        }

        for bot_name, client in self.clients.items():
            logger.info(f"Processing {bot_name}...")

            filled_orders = self.get_filled_orders(client)
            logger.info(f"  Found {len(filled_orders)} filled orders")

            updated = self.match_and_update(outcomes, filled_orders, bot_name)
            results['updates_by_bot'][bot_name] = updated
            results['total_updated'] += updated

            logger.info(f"  Updated {updated} records")

        # Save updated outcomes
        self.save_outcomes(outcomes)

        # Calculate completion stats
        complete = len([o for o in outcomes if o.get('outcome_status') == 'complete'])
        pending = len(outcomes) - complete

        results['complete_outcomes'] = complete
        results['pending_outcomes'] = pending
        results['completion_rate'] = complete / len(outcomes) if outcomes else 0

        return results


def main():
    """Main entry point."""
    print("=" * 60)
    print("AUTOMATED ML OUTCOME UPDATE")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Get health monitor
    monitor = get_health_monitor()

    try:
        with monitor.track_task("ml_outcome_update") as tracker:
            updater = OutcomeUpdater()
            results = updater.update_all()

            tracker.add_detail("total_updated", results['total_updated'])
            tracker.add_detail("completion_rate", results['completion_rate'])

            print("\n" + "=" * 60)
            print("RESULTS")
            print("=" * 60)
            print(f"Initial Records: {results['initial_records']}")
            print(f"Total Updated: {results['total_updated']}")
            print(f"Complete: {results['complete_outcomes']}")
            print(f"Pending: {results['pending_outcomes']}")
            print(f"Completion Rate: {results['completion_rate']:.1%}")

            print("\nUpdates by Bot:")
            for bot, count in results['updates_by_bot'].items():
                print(f"  {bot}: {count}")

            print("=" * 60)

    except Exception as e:
        logger.error(f"Outcome update failed: {e}")
        raise


if __name__ == "__main__":
    main()
