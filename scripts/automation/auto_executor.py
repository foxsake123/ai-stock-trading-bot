"""
Automated Trade Execution Pipeline
===================================
Executes validated trades from consensus system and confirms fills.

Flow:
1. Load execution plan (from consensus validator)
2. Submit orders to Alpaca
3. Monitor for fills
4. Send Telegram notifications
5. Update portfolio tracking

Author: AI Trading Bot System
Date: September 30, 2025
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import requests

sys.path.append(str(Path(__file__).parent.parent.parent))

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv

load_dotenv()


class AutoExecutor:
    """Automated trade executor with fill confirmation"""

    def __init__(self, bot_name: str):
        """
        Initialize executor

        Args:
            bot_name: "DEE-BOT" or "SHORGAN-BOT"
        """
        self.bot_name = bot_name

        # Initialize Alpaca client
        if bot_name == "DEE-BOT":
            self.client = TradingClient(
                api_key=os.getenv("ALPACA_API_KEY_DEE"),
                secret_key=os.getenv("ALPACA_SECRET_KEY_DEE"),
                paper=True
            )
        else:
            self.client = TradingClient(
                api_key=os.getenv("ALPACA_API_KEY_SHORGAN"),
                secret_key=os.getenv("ALPACA_SECRET_KEY_SHORGAN"),
                paper=True
            )

        # Telegram configuration
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send_telegram(self, message: str):
        """Send Telegram notification"""
        if not self.telegram_token or not self.telegram_chat_id:
            print("[!] Telegram not configured, skipping notification")
            return

        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                print("[+] Telegram notification sent")
            else:
                print(f"[-] Telegram failed: {response.status_code}")
        except Exception as e:
            print(f"[-] Telegram error: {e}")

    def execute_trade(self, trade: Dict) -> Dict:
        """
        Execute a single trade

        Args:
            trade: Trade dictionary from execution plan

        Returns:
            Dict with execution results
        """
        print(f"\n[*] Executing: {trade['action'].upper()} {trade['shares']} {trade['ticker']} @ ${trade['limit_price']}")

        try:
            # Determine order side
            side = OrderSide.BUY if trade['action'] == 'buy' else OrderSide.SELL

            # Determine time in force
            tif_map = {
                'DAY': TimeInForce.DAY,
                'GTC': TimeInForce.GTC,
                'IOC': TimeInForce.IOC,
                'FOK': TimeInForce.FOK
            }
            time_in_force = tif_map.get(trade.get('time_in_force', 'DAY'), TimeInForce.DAY)

            # Create limit order request
            order_request = LimitOrderRequest(
                symbol=trade['ticker'],
                qty=trade['shares'],
                side=side,
                time_in_force=time_in_force,
                limit_price=trade['limit_price']
            )

            # Submit order
            order = self.client.submit_order(order_request)

            print(f"[+] Order submitted: {order.id}")
            print(f"    Status: {order.status}")
            print(f"    Symbol: {order.symbol}")
            print(f"    Qty: {order.qty}")
            print(f"    Side: {order.side}")
            print(f"    Limit Price: ${order.limit_price}")

            return {
                'success': True,
                'order_id': str(order.id),
                'status': str(order.status),
                'symbol': order.symbol,
                'qty': float(order.qty),
                'filled_qty': float(order.filled_qty) if order.filled_qty else 0,
                'limit_price': float(order.limit_price) if order.limit_price else 0,
                'submitted_at': str(order.submitted_at),
                'trade': trade
            }

        except Exception as e:
            print(f"[-] Execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'trade': trade
            }

    def monitor_fills(self, order_ids: List[str], timeout_minutes: int = 30) -> Dict:
        """
        Monitor orders for fills

        Args:
            order_ids: List of order IDs to monitor
            timeout_minutes: How long to wait for fills

        Returns:
            Dict with fill status for each order
        """
        print(f"\n[*] Monitoring {len(order_ids)} orders for fills (timeout: {timeout_minutes}min)")

        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        fill_status = {}

        while time.time() - start_time < timeout_seconds:
            all_filled = True

            for order_id in order_ids:
                if order_id in fill_status and fill_status[order_id]['filled']:
                    continue

                try:
                    order = self.client.get_order_by_id(order_id)
                    status = str(order.status)

                    if status == 'filled':
                        fill_status[order_id] = {
                            'filled': True,
                            'symbol': order.symbol,
                            'filled_qty': float(order.filled_qty),
                            'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else 0,
                            'filled_at': str(order.filled_at) if order.filled_at else None
                        }
                        print(f"[+] FILLED: {order.symbol} - {order.filled_qty} @ ${order.filled_avg_price}")
                    elif status in ['canceled', 'expired', 'rejected']:
                        fill_status[order_id] = {
                            'filled': False,
                            'symbol': order.symbol,
                            'status': status,
                            'reason': 'Order ' + status
                        }
                        print(f"[-] {status.upper()}: {order.symbol}")
                    else:
                        all_filled = False
                        fill_status[order_id] = {
                            'filled': False,
                            'symbol': order.symbol,
                            'status': status,
                            'reason': 'Pending'
                        }

                except Exception as e:
                    print(f"[-] Error checking order {order_id}: {e}")
                    all_filled = False

            if all_filled:
                print(f"\n[+] All orders filled!")
                break

            time.sleep(10)  # Check every 10 seconds

        # Check for any unfilled orders
        unfilled = [oid for oid, status in fill_status.items() if not status.get('filled')]
        if unfilled:
            print(f"\n[!] {len(unfilled)} orders not filled within timeout")

        return fill_status

    def execute_plan(self, execution_plan_path: Path) -> Dict:
        """
        Execute all trades from an execution plan

        Args:
            execution_plan_path: Path to execution plan JSON

        Returns:
            Dict with execution summary
        """
        print(f"\n{'='*70}")
        print(f"AUTO EXECUTION PIPELINE - {self.bot_name}")
        print(f"{'='*70}")
        print(f"Plan: {execution_plan_path.name}")
        print()

        # Load execution plan
        with open(execution_plan_path, 'r', encoding='utf-8') as f:
            plan = json.load(f)

        trades = plan.get('approved_trades', [])

        if not trades:
            print("[!] No approved trades in execution plan")
            return {
                'bot': self.bot_name,
                'total_trades': 0,
                'executed': 0,
                'filled': 0,
                'failed': 0
            }

        print(f"[*] Found {len(trades)} approved trades to execute")

        # Execute all trades
        executed = []
        failed = []

        for trade in trades:
            result = self.execute_trade(trade)

            if result['success']:
                executed.append(result)
            else:
                failed.append(result)

            time.sleep(1)  # Rate limiting

        # Monitor fills
        order_ids = [r['order_id'] for r in executed]
        fill_status = self.monitor_fills(order_ids, timeout_minutes=30) if order_ids else {}

        # Count fills
        filled_count = sum(1 for status in fill_status.values() if status.get('filled'))

        # Generate summary
        summary = {
            'bot': self.bot_name,
            'execution_plan': str(execution_plan_path),
            'timestamp': datetime.now().isoformat(),
            'total_trades': len(trades),
            'executed': len(executed),
            'filled': filled_count,
            'failed': len(failed),
            'executed_orders': executed,
            'failed_orders': failed,
            'fill_status': fill_status
        }

        # Print summary
        print(f"\n{'='*70}")
        print(f"EXECUTION SUMMARY")
        print(f"{'='*70}")
        print(f"Total Trades: {summary['total_trades']}")
        print(f"Executed: {summary['executed']}")
        print(f"Filled: {summary['filled']}")
        print(f"Failed: {summary['failed']}")
        print(f"Fill Rate: {summary['filled']/summary['total_trades']*100:.1f}%")
        print(f"{'='*70}\n")

        # Send Telegram notification
        telegram_msg = f"""
*{self.bot_name} Trade Execution Complete*

📊 *Summary:*
• Total Trades: {summary['total_trades']}
• Executed: {summary['executed']}
• Filled: {summary['filled']} ({summary['filled']/summary['total_trades']*100:.1f}%)
• Failed: {summary['failed']}

⏰ {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}
"""
        self.send_telegram(telegram_msg)

        # Save execution summary
        output_dir = Path("scripts-and-data/data/execution-results")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        bot_slug = self.bot_name.lower().replace("-", "_")
        result_file = output_dir / f"execution_result_{bot_slug}_{timestamp}.json"

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        print(f"[+] Execution results saved: {result_file}")

        return summary


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Execute validated trades automatically")
    parser.add_argument(
        "--bot",
        choices=["dee", "shorgan", "both"],
        default="both",
        help="Which bot to execute"
    )
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Date of execution plan (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without placing orders"
    )

    args = parser.parse_args()

    if args.dry_run:
        print("[!] DRY RUN MODE - No orders will be placed\n")

    # Determine which bots to process
    bots = []
    if args.bot == "both":
        bots = ["DEE-BOT", "SHORGAN-BOT"]
    elif args.bot == "dee":
        bots = ["DEE-BOT"]
    else:
        bots = ["SHORGAN-BOT"]

    # Process each bot
    for bot_name in bots:
        # Find execution plan
        bot_slug = bot_name.lower().replace("-", "_")
        plan_dir = Path("scripts-and-data/data/execution-plans")
        plan_file = plan_dir / f"execution_plan_{bot_slug}_{args.date}.json"

        if not plan_file.exists():
            print(f"\n[!] Execution plan not found: {plan_file}")
            continue

        # Execute trades
        executor = AutoExecutor(bot_name)

        if args.dry_run:
            print(f"\n[DRY RUN] Would execute: {plan_file}")
            with open(plan_file, 'r') as f:
                plan = json.load(f)
            print(f"[DRY RUN] Approved trades: {len(plan.get('approved_trades', []))}")
        else:
            summary = executor.execute_plan(plan_file)


if __name__ == "__main__":
    main()
