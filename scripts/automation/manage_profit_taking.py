"""
Automated Profit-Taking Manager
================================
Monitors open positions and automatically takes profits at predefined levels.

Strategy:
- Level 1: Sell 50% of position at +20% gain
- Level 2: Sell additional 25% at +30% gain
- Let final 25% run with trailing stop

Author: AI Trading Bot System
Date: October 29, 2025
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import requests

# Load environment variables
load_dotenv()

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))


class ProfitTakingManager:
    """Manages automated profit taking for open positions"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "daily" / "profit_taking"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load profit-taking history
        self.history_file = self.data_dir / "profit_taking_history.json"
        self.history = self._load_history()

        # Initialize Alpaca clients (with error handling)
        try:
            dee_api_key = os.getenv("ALPACA_PAPER_API_KEY_DEE") or os.getenv("ALPACA_PAPER_API_KEY")
            dee_secret = os.getenv("ALPACA_PAPER_SECRET_KEY_DEE") or os.getenv("ALPACA_PAPER_SECRET_KEY")
            if dee_api_key and dee_secret:
                self.dee_trading = TradingClient(
                    api_key=dee_api_key,
                    secret_key=dee_secret,
                    paper=True
                )
            else:
                print("[WARNING] DEE-BOT credentials not found, skipping")
                self.dee_trading = None
        except Exception as e:
            print(f"[WARNING] Could not initialize DEE-BOT client: {e}")
            self.dee_trading = None

        try:
            shorgan_paper_key = os.getenv("ALPACA_PAPER_API_KEY_SHORGAN")
            shorgan_paper_secret = os.getenv("ALPACA_PAPER_SECRET_KEY_SHORGAN")
            if shorgan_paper_key and shorgan_paper_secret:
                self.shorgan_trading = TradingClient(
                    api_key=shorgan_paper_key,
                    secret_key=shorgan_paper_secret,
                    paper=True
                )
            else:
                print("[WARNING] SHORGAN-BOT Paper credentials not found, skipping")
                self.shorgan_trading = None
        except Exception as e:
            print(f"[WARNING] Could not initialize SHORGAN-BOT Paper client: {e}")
            self.shorgan_trading = None

        try:
            shorgan_live_key = os.getenv("ALPACA_LIVE_API_KEY_SHORGAN")
            shorgan_live_secret = os.getenv("ALPACA_LIVE_SECRET_KEY_SHORGAN")
            if shorgan_live_key and shorgan_live_secret:
                self.shorgan_live_trading = TradingClient(
                    api_key=shorgan_live_key,
                    secret_key=shorgan_live_secret,
                    paper=False
                )
            else:
                print("[WARNING] SHORGAN-BOT Live credentials not found, skipping")
                self.shorgan_live_trading = None
        except Exception as e:
            print(f"[WARNING] Could not initialize SHORGAN-BOT Live client: {e}")
            self.shorgan_live_trading = None

        # Telegram config
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

    def _load_history(self) -> Dict:
        """Load profit-taking history from disk"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_history(self):
        """Save profit-taking history to disk"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def _send_telegram(self, message: str):
        """Send notification to Telegram"""
        if not self.telegram_token or not self.telegram_chat_id:
            print("[WARNING] Telegram credentials not configured")
            return

        try:
            url = f'https://api.telegram.org/bot{self.telegram_token}/sendMessage'
            response = requests.post(
                url,
                data={'chat_id': self.telegram_chat_id, 'text': message},
                timeout=10
            )
            if response.json().get('ok'):
                print(f"[+] Telegram notification sent")
            else:
                print(f"[-] Telegram error: {response.text}")
        except Exception as e:
            print(f"[-] Telegram send failed: {e}")

    def check_profit_targets(self, bot_name: str, client: TradingClient):
        """Check all positions for profit-taking opportunities"""
        print(f"\n{'='*80}")
        print(f"PROFIT-TAKING CHECK: {bot_name}")
        print(f"{'='*80}\n")

        try:
            # Get all open positions
            positions = client.get_all_positions()

            if not positions:
                print(f"[*] {bot_name}: No open positions")
                return

            print(f"[*] {bot_name}: Checking {len(positions)} position(s)...")

            actions_taken = []

            for pos in positions:
                symbol = pos.symbol
                shares = int(pos.qty)
                entry_price = float(pos.avg_entry_price)
                current_price = float(pos.current_price)
                market_value = float(pos.market_value)
                unrealized_pl = float(pos.unrealized_pl)
                unrealized_pl_pct = float(pos.unrealized_plpc) * 100

                print(f"\n  [{symbol}] {shares} shares @ ${entry_price:.2f}")
                print(f"    Current: ${current_price:.2f} | P&L: ${unrealized_pl:+.2f} ({unrealized_pl_pct:+.2f}%)")

                # Get profit-taking history for this symbol
                pos_key = f"{bot_name}:{symbol}"
                if pos_key not in self.history:
                    self.history[pos_key] = {
                        'entry_price': entry_price,
                        'entry_shares': shares,
                        'level1_taken': False,
                        'level2_taken': False,
                        'actions': []
                    }

                pos_history = self.history[pos_key]

                # Level 1: 50% off at +20%
                if unrealized_pl_pct >= 20.0 and not pos_history['level1_taken']:
                    shares_to_sell = max(1, shares // 2)
                    action = self._execute_profit_take(
                        client, bot_name, symbol, shares_to_sell,
                        current_price, entry_price, "Level 1 (+20%)"
                    )
                    if action:
                        pos_history['level1_taken'] = True
                        pos_history['actions'].append(action)
                        actions_taken.append(action)
                        print(f"    [PROFIT] Level 1: Sold {shares_to_sell} shares @ ${current_price:.2f}")

                # Level 2: 25% more at +30%
                elif unrealized_pl_pct >= 30.0 and pos_history['level1_taken'] and not pos_history['level2_taken']:
                    # Sell 1/3 of remaining shares (which is ~25% of original)
                    shares_to_sell = max(1, shares // 3)
                    action = self._execute_profit_take(
                        client, bot_name, symbol, shares_to_sell,
                        current_price, entry_price, "Level 2 (+30%)"
                    )
                    if action:
                        pos_history['level2_taken'] = True
                        pos_history['actions'].append(action)
                        actions_taken.append(action)
                        print(f"    [PROFIT] Level 2: Sold {shares_to_sell} shares @ ${current_price:.2f}")

                else:
                    if pos_history['level1_taken'] and pos_history['level2_taken']:
                        print(f"    [HOLD] Letting final 25% run (both levels taken)")
                    elif pos_history['level1_taken']:
                        print(f"    [HOLD] Waiting for +30% for Level 2")
                    else:
                        print(f"    [HOLD] Waiting for +20% for Level 1")

            # Save updated history
            self._save_history()

            # Send Telegram summary if actions taken
            if actions_taken:
                summary = f"🎯 PROFIT-TAKING: {bot_name}\n\n"
                for action in actions_taken:
                    summary += f"✓ {action['symbol']}: {action['level']}\n"
                    summary += f"  Sold {action['shares']} @ ${action['price']:.2f}\n"
                    summary += f"  Profit: ${action['profit']:.2f} ({action['profit_pct']:.1f}%)\n\n"
                self._send_telegram(summary)
                print(f"\n[SUCCESS] {len(actions_taken)} profit-taking action(s) executed")
            else:
                print(f"\n[*] No profit-taking actions needed")

        except Exception as e:
            print(f"[ERROR] Profit-taking check failed for {bot_name}: {e}")
            import traceback
            traceback.print_exc()

    def _execute_profit_take(self, client: TradingClient, bot_name: str, symbol: str,
                            shares: int, current_price: float, entry_price: float,
                            level: str) -> Dict:
        """Execute a profit-taking sell order"""
        try:
            # Create market sell order
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=shares,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )

            order = client.submit_order(order_data)

            # Calculate profit
            profit_per_share = current_price - entry_price
            total_profit = profit_per_share * shares
            profit_pct = (profit_per_share / entry_price) * 100

            action = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'shares': shares,
                'price': current_price,
                'entry_price': entry_price,
                'profit': total_profit,
                'profit_pct': profit_pct,
                'level': level,
                'order_id': order.id
            }

            return action

        except Exception as e:
            print(f"    [ERROR] Failed to execute profit-take for {symbol}: {e}")
            return None

    def run(self):
        """Run profit-taking checks for all accounts"""
        print(f"\n{'='*80}")
        print(f"AUTOMATED PROFIT-TAKING MANAGER")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")

        # Check DEE-BOT Paper
        if self.dee_trading:
            self.check_profit_targets("DEE-BOT", self.dee_trading)

        # Check SHORGAN-BOT Paper
        if self.shorgan_trading:
            self.check_profit_targets("SHORGAN-BOT-PAPER", self.shorgan_trading)

        # Check SHORGAN-BOT Live
        if self.shorgan_live_trading:
            self.check_profit_targets("SHORGAN-BOT-LIVE", self.shorgan_live_trading)

        print(f"\n{'='*80}")
        print("PROFIT-TAKING CHECK COMPLETE")
        print(f"{'='*80}\n")


def main():
    """Main execution"""
    manager = ProfitTakingManager()
    manager.run()


if __name__ == "__main__":
    main()
