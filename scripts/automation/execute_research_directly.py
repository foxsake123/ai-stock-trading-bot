"""
Direct Research Execution (Emergency Bypass)
=============================================
Executes external research recommendations directly without multi-agent validation.

USE ONLY WHEN: Multi-agent system is unavailable due to API issues.

WARNING: This bypasses risk management validation. Use with caution.

Author: AI Trading Bot System
Date: October 15, 2025
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.automation.report_parser import ExternalReportParser
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class DirectResearchExecutor:
    """Execute external research without agent validation"""

    def __init__(self):
        self.dee_api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY_DEE'),
            os.getenv('ALPACA_SECRET_KEY_DEE'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )

        self.shorgan_api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY_SHORGAN'),
            os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )

        self.parser = ExternalReportParser()
        self.executed = []
        self.failed = []

    def execute_recommendation(self, rec, api, bot_name):
        """Execute a single recommendation"""
        try:
            print(f"\n[{bot_name}] Executing {rec.ticker} {rec.action}...")

            # Get current price
            bars = api.get_latest_bar(rec.ticker)
            current_price = bars.c

            # Calculate shares if not specified
            if not rec.shares:
                account = api.get_account()
                portfolio_value = float(account.portfolio_value)
                position_pct = rec.position_size_pct or 5.0
                position_value = portfolio_value * (position_pct / 100)
                rec.shares = int(position_value / current_price)

            if rec.shares <= 0:
                print(f"  [SKIP] Invalid share count: {rec.shares}")
                return False

            # Determine order parameters
            side = 'sell' if rec.action == 'SHORT' else 'buy'
            limit_price = rec.entry_price if rec.entry_price else current_price * 1.005

            # Place order
            order = api.submit_order(
                symbol=rec.ticker,
                qty=rec.shares,
                side=side,
                type='limit',
                time_in_force='day',
                limit_price=str(round(limit_price, 2))
            )

            print(f"  [OK] Order placed: {rec.shares} shares @ ${limit_price:.2f}")
            print(f"       Order ID: {order.id}")
            print(f"       Source: {rec.source.upper()}")
            print(f"       Catalyst: {rec.catalyst[:50] if rec.catalyst else 'N/A'}")

            self.executed.append({
                'bot': bot_name,
                'ticker': rec.ticker,
                'action': rec.action,
                'shares': rec.shares,
                'limit_price': limit_price,
                'order_id': order.id,
                'source': rec.source,
                'catalyst': rec.catalyst
            })

            return True

        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.failed.append({
                'bot': bot_name,
                'ticker': rec.ticker,
                'error': str(e)
            })
            return False

    def run(self, date_str=None):
        """Execute all recommendations from external research"""
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')

        print("="*70)
        print("DIRECT RESEARCH EXECUTION (EMERGENCY BYPASS)")
        print("WARNING: Multi-agent validation SKIPPED")
        print("="*70)
        print(f"Date: {date_str}")
        print()

        # Find research files
        research_dir = Path(f"reports/premarket/{date_str}")
        claude_path = research_dir / "claude_research.md"
        chatgpt_path = research_dir / "chatgpt_research.md"

        if not claude_path.exists() and not chatgpt_path.exists():
            print(f"[ERROR] No research files found for {date_str}")
            return

        # Parse recommendations
        print("Parsing external research...")
        dee_recs = self.parser.get_recommendations_for_bot("DEE-BOT", claude_path, chatgpt_path)
        shorgan_recs = self.parser.get_recommendations_for_bot("SHORGAN-BOT", claude_path, chatgpt_path)

        print(f"  DEE-BOT: {len(dee_recs)} recommendations")
        print(f"  SHORGAN: {len(shorgan_recs)} recommendations")
        print()

        # Confirm execution
        print("="*70)
        print("CONFIRMATION REQUIRED")
        print("="*70)
        print(f"About to execute {len(dee_recs) + len(shorgan_recs)} trades WITHOUT agent validation.")
        print("This bypasses risk management checks.")
        print()
        response = input("Type 'EXECUTE' to proceed: ")

        if response != 'EXECUTE':
            print("\n[ABORTED] Execution canceled by user.")
            return

        print("\n" + "="*70)
        print("EXECUTING TRADES")
        print("="*70)

        # Execute DEE-BOT (limit to top 5 by position size)
        if dee_recs:
            print("\n[DEE-BOT] Executing trades...")
            dee_recs_sorted = sorted(dee_recs, key=lambda x: x.position_size_pct or 0, reverse=True)[:5]
            for rec in dee_recs_sorted:
                self.execute_recommendation(rec, self.dee_api, "DEE-BOT")

        # Execute SHORGAN-BOT (limit to top 5 by conviction)
        if shorgan_recs:
            print("\n[SHORGAN-BOT] Executing trades...")
            shorgan_recs_sorted = sorted(shorgan_recs,
                key=lambda x: 3 if x.conviction == 'HIGH' else 2 if x.conviction == 'MEDIUM' else 1,
                reverse=True)[:5]
            for rec in shorgan_recs_sorted:
                self.execute_recommendation(rec, self.shorgan_api, "SHORGAN-BOT")

        # Summary
        print("\n" + "="*70)
        print("EXECUTION SUMMARY")
        print("="*70)
        print(f"Executed: {len(self.executed)}")
        print(f"Failed: {len(self.failed)}")

        if self.executed:
            print("\nSuccessful Orders:")
            for trade in self.executed:
                print(f"  [{trade['bot']}] {trade['ticker']} {trade['action']} "
                      f"{trade['shares']} @ ${trade['limit_price']:.2f} ({trade['source']})")

        if self.failed:
            print("\nFailed Orders:")
            for trade in self.failed:
                print(f"  [{trade['bot']}] {trade['ticker']}: {trade['error'][:60]}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Date (YYYY-MM-DD)")
    args = parser.parse_args()

    executor = DirectResearchExecutor()
    executor.run(args.date)
