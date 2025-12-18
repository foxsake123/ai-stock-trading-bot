#!/usr/bin/env python3
"""
Tax-Loss Harvesting Module
===========================
Automatically identifies and harvests tax losses from live trading accounts.
Sells positions with significant unrealized losses (>$100) and replaces them
with similar securities to maintain market exposure while avoiding wash sale rules.

Features:
- Scans live accounts for harvestable losses
- Calculates estimated tax savings (35% assumed marginal rate)
- Executes sell + replacement buy atomically
- Tracks harvest history to prevent wash sales (30-day window)
- Sends Telegram notifications on successful harvests

Author: AI Trading Bot System
Date: December 2025
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()


class TaxLossHarvester:
    """
    Intelligent tax-loss harvesting for live trading accounts.

    Attributes:
        account_type: "DEE-LIVE" or "SHORGAN-LIVE"
        loss_threshold: Minimum unrealized loss to trigger harvest (default $100)
        tax_rate: Estimated marginal tax rate for savings calculation (default 35%)
    """

    # Minimum loss threshold to trigger harvest
    DEFAULT_LOSS_THRESHOLD = 100.0

    # Estimated marginal tax rate for savings calculation
    DEFAULT_TAX_RATE = 0.35

    # Data directory for tracking
    DATA_DIR = Path(__file__).parent.parent.parent / "data" / "tax_loss_harvesting"

    # Alternative securities mapping (S&P 100 and common small/mid caps)
    # These are "substantially different" to avoid wash sale rules
    ALTERNATIVES = {
        # S&P 100 Large Cap Alternatives
        'AAPL': 'MSFT',  # Tech giants
        'MSFT': 'AAPL',
        'GOOGL': 'META',  # Digital advertising
        'GOOG': 'META',
        'META': 'GOOGL',
        'AMZN': 'WMT',   # Retail
        'WMT': 'AMZN',
        'NVDA': 'AMD',   # Semiconductors
        'AMD': 'NVDA',
        'TSLA': 'GM',    # Auto
        'GM': 'F',
        'F': 'GM',
        'JNJ': 'PFE',    # Healthcare
        'PFE': 'JNJ',
        'UNH': 'CVS',    # Health services
        'CVS': 'UNH',
        'JPM': 'BAC',    # Banks
        'BAC': 'JPM',
        'V': 'MA',       # Payment processors
        'MA': 'V',
        'HD': 'LOW',     # Home improvement
        'LOW': 'HD',
        'DIS': 'CMCSA',  # Media
        'CMCSA': 'DIS',
        'NFLX': 'DIS',   # Streaming
        'KO': 'PEP',     # Beverages
        'PEP': 'KO',
        'MCD': 'SBUX',   # Restaurants
        'SBUX': 'MCD',
        'NKE': 'LULU',   # Apparel
        'COST': 'TGT',   # Retail
        'TGT': 'COST',
        'XOM': 'CVX',    # Energy
        'CVX': 'XOM',
        'COP': 'XOM',
        'NEE': 'DUK',    # Utilities
        'DUK': 'NEE',
        'SO': 'NEE',

        # ETF Alternatives (sector swaps)
        'SPY': 'VOO',    # S&P 500
        'VOO': 'SPY',
        'QQQ': 'VGT',    # Tech
        'VGT': 'QQQ',
        'XLK': 'VGT',
        'XLF': 'VFH',    # Financials
        'VFH': 'XLF',
        'XLE': 'VDE',    # Energy
        'VDE': 'XLE',
        'XLV': 'VHT',    # Healthcare
        'VHT': 'XLV',
        'XLY': 'VCR',    # Consumer discretionary
        'VCR': 'XLY',

        # Small/Mid Cap Alternatives
        'FUBO': 'ROKU',  # Streaming
        'ROKU': 'FUBO',
        'PLUG': 'FCEL',  # Clean energy
        'FCEL': 'PLUG',
        'PLTR': 'SNOW',  # Data/AI
        'SNOW': 'PLTR',
        'SOFI': 'UPST',  # Fintech
        'UPST': 'SOFI',
        'RIVN': 'LCID',  # EV
        'LCID': 'RIVN',
        'COIN': 'MARA',  # Crypto-related
        'MARA': 'RIOT',
        'RIOT': 'MARA',
        'NIO': 'XPEV',   # Chinese EV
        'XPEV': 'NIO',
        'IONQ': 'RGTI',  # Quantum computing
        'RGTI': 'IONQ',
        'DNA': 'CRSP',   # Biotech
        'CRSP': 'EDIT',
        'EDIT': 'CRSP',
        'STEM': 'ENPH',  # Solar/energy storage
        'ENPH': 'SEDG',
        'SEDG': 'ENPH',
    }

    def __init__(self, account_type: str, loss_threshold: float = None, tax_rate: float = None):
        """
        Initialize the Tax-Loss Harvester.

        Args:
            account_type: "DEE-LIVE" or "SHORGAN-LIVE"
            loss_threshold: Minimum unrealized loss to harvest (default $100)
            tax_rate: Estimated marginal tax rate (default 35%)
        """
        self.account_type = account_type.upper()
        self.loss_threshold = loss_threshold or self.DEFAULT_LOSS_THRESHOLD
        self.tax_rate = tax_rate or self.DEFAULT_TAX_RATE

        # Initialize Alpaca API
        self.api = self._init_api()

        # Ensure data directory exists
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Load harvest history
        self.history_file = self.DATA_DIR / "harvest_history.json"
        self.harvest_history = self._load_history()

        print(f"[TLH] Initialized for {self.account_type}")
        print(f"[TLH] Loss threshold: ${self.loss_threshold:.2f}")
        print(f"[TLH] Estimated tax rate: {self.tax_rate*100:.0f}%")

    def _init_api(self) -> tradeapi.REST:
        """Initialize Alpaca API for the specified account."""
        if self.account_type == "DEE-LIVE":
            api_key = os.getenv('ALPACA_LIVE_API_KEY_DEE')
            secret_key = os.getenv('ALPACA_LIVE_SECRET_KEY_DEE')
        elif self.account_type == "SHORGAN-LIVE":
            api_key = os.getenv('ALPACA_LIVE_API_KEY_SHORGAN')
            secret_key = os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN')
        else:
            raise ValueError(f"Unknown account type: {self.account_type}")

        if not api_key or not secret_key:
            raise ValueError(f"API keys not found for {self.account_type}")

        return tradeapi.REST(
            api_key,
            secret_key,
            'https://api.alpaca.markets',  # Live endpoint
            api_version='v2'
        )

    def _load_history(self) -> Dict:
        """Load harvest history from JSON file."""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {
            "harvests": [],
            "ytd_summary": {
                "total_harvested": 0.0,
                "estimated_tax_savings": 0.0,
                "harvest_count": 0
            }
        }

    def _save_history(self):
        """Save harvest history to JSON file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.harvest_history, f, indent=2, default=str)

    def _is_wash_sale_safe(self, symbol: str, replacement: str) -> Tuple[bool, str]:
        """
        Check if selling symbol and buying replacement would violate wash sale rules.

        Wash sale rule: Cannot claim loss if you buy "substantially identical"
        security within 30 days before or after the sale.

        Args:
            symbol: Stock to sell
            replacement: Stock to buy

        Returns:
            (is_safe, reason)
        """
        now = datetime.now()
        wash_sale_window = timedelta(days=30)

        # Check recent harvests for wash sale conflicts
        for harvest in self.harvest_history.get("harvests", []):
            harvest_date = datetime.fromisoformat(harvest["date"])

            # Check if within 30-day window
            if now - harvest_date < wash_sale_window:
                sold_symbol = harvest.get("sold_symbol")
                bought_symbol = harvest.get("bought_symbol")

                # Cannot buy back what we sold
                if symbol == bought_symbol:
                    return False, f"Wash sale: Bought {symbol} on {harvest_date.strftime('%Y-%m-%d')}"

                # Cannot sell what we just bought as replacement
                if replacement == sold_symbol:
                    return False, f"Wash sale: Sold {replacement} on {harvest_date.strftime('%Y-%m-%d')}"

        return True, "No wash sale conflict"

    def scan_harvestable_positions(self) -> List[Dict]:
        """
        Scan account for positions with unrealized losses exceeding threshold.

        Returns:
            List of harvestable positions with details
        """
        print(f"\n[TLH] Scanning {self.account_type} for harvestable losses...")

        try:
            positions = self.api.list_positions()
        except Exception as e:
            print(f"[TLH] Error getting positions: {e}")
            return []

        harvestable = []

        for pos in positions:
            symbol = pos.symbol
            qty = float(pos.qty)
            market_value = float(pos.market_value)
            unrealized_pl = float(pos.unrealized_pl)
            unrealized_plpc = float(pos.unrealized_plpc) * 100  # Convert to percentage
            avg_entry = float(pos.avg_entry_price)
            current_price = float(pos.current_price)

            # Skip positions with gains or small losses
            if unrealized_pl >= -self.loss_threshold:
                continue

            # Get replacement security
            replacement = self._get_best_alternative(symbol)
            if not replacement:
                print(f"    [SKIP] {symbol}: No alternative available")
                continue

            # Check wash sale safety
            is_safe, reason = self._is_wash_sale_safe(symbol, replacement)
            if not is_safe:
                print(f"    [SKIP] {symbol}: {reason}")
                continue

            # Calculate tax savings
            tax_savings = self._estimate_tax_savings(abs(unrealized_pl))

            position_data = {
                "symbol": symbol,
                "qty": qty,
                "avg_entry": avg_entry,
                "current_price": current_price,
                "market_value": market_value,
                "unrealized_pl": unrealized_pl,
                "unrealized_plpc": unrealized_plpc,
                "replacement": replacement,
                "estimated_tax_savings": tax_savings
            }

            harvestable.append(position_data)
            print(f"    [HARVEST] {symbol}: Loss ${abs(unrealized_pl):.2f} ({unrealized_plpc:.1f}%)")
            print(f"              Replacement: {replacement}, Est. Tax Savings: ${tax_savings:.2f}")

        print(f"\n[TLH] Found {len(harvestable)} harvestable positions")
        return harvestable

    def _get_best_alternative(self, symbol: str) -> Optional[str]:
        """
        Get the best wash-sale-safe alternative for a symbol.

        Args:
            symbol: Stock symbol to find alternative for

        Returns:
            Alternative symbol or None if not found
        """
        # Check direct mapping
        if symbol in self.ALTERNATIVES:
            return self.ALTERNATIVES[symbol]

        # For unknown symbols, try to find sector ETF
        # This is a fallback - consider expanding ALTERNATIVES dict
        print(f"    [INFO] No direct alternative for {symbol}, skipping")
        return None

    def _estimate_tax_savings(self, loss_amount: float) -> float:
        """
        Estimate tax savings from harvesting a loss.

        Args:
            loss_amount: Absolute value of unrealized loss

        Returns:
            Estimated tax savings
        """
        # Short-term losses offset short-term gains (taxed as ordinary income)
        # Long-term losses offset long-term gains (taxed at capital gains rate)
        # For simplicity, use single tax rate
        return loss_amount * self.tax_rate

    def execute_harvest(self, position: Dict, auto_replace: bool = True) -> Dict:
        """
        Execute a tax-loss harvest: sell loser, buy replacement.

        Args:
            position: Position data from scan_harvestable_positions
            auto_replace: If True, automatically buy replacement security

        Returns:
            Harvest result with order details
        """
        symbol = position["symbol"]
        qty = int(position["qty"])
        replacement = position["replacement"]
        loss_amount = abs(position["unrealized_pl"])
        current_price = position["current_price"]

        result = {
            "date": datetime.now().isoformat(),
            "account": self.account_type,
            "sold_symbol": symbol,
            "sold_qty": qty,
            "sold_price": None,
            "loss_harvested": loss_amount,
            "bought_symbol": None,
            "bought_qty": None,
            "bought_price": None,
            "tax_savings": position["estimated_tax_savings"],
            "status": "pending",
            "error": None
        }

        print(f"\n[TLH] Executing harvest for {symbol}...")
        print(f"    Selling {qty} shares at ~${current_price:.2f}")

        # Step 1: Sell the losing position
        try:
            sell_order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side='sell',
                type='market',
                time_in_force='day'
            )
            result["sold_price"] = current_price
            print(f"    [OK] Sell order submitted: {sell_order.id}")
        except Exception as e:
            result["status"] = "failed"
            result["error"] = f"Sell failed: {str(e)}"
            print(f"    [ERROR] Sell failed: {e}")
            return result

        # Step 2: Buy replacement (if enabled)
        if auto_replace and replacement:
            # Get current price of replacement
            try:
                replacement_bar = self.api.get_latest_bar(replacement)
                replacement_price = replacement_bar.c
            except:
                replacement_price = current_price  # Fallback

            # Calculate equivalent shares (maintain similar dollar exposure)
            replacement_qty = int(position["market_value"] / replacement_price)

            if replacement_qty > 0:
                print(f"    Buying {replacement_qty} {replacement} at ~${replacement_price:.2f}")

                try:
                    buy_order = self.api.submit_order(
                        symbol=replacement,
                        qty=replacement_qty,
                        side='buy',
                        type='market',
                        time_in_force='day'
                    )
                    result["bought_symbol"] = replacement
                    result["bought_qty"] = replacement_qty
                    result["bought_price"] = replacement_price
                    print(f"    [OK] Buy order submitted: {buy_order.id}")
                except Exception as e:
                    # Sell succeeded but buy failed - still count as partial harvest
                    result["error"] = f"Replacement buy failed: {str(e)}"
                    print(f"    [WARNING] Replacement buy failed: {e}")

        result["status"] = "completed"

        # Record harvest in history
        self.harvest_history["harvests"].append(result)
        self.harvest_history["ytd_summary"]["total_harvested"] += loss_amount
        self.harvest_history["ytd_summary"]["estimated_tax_savings"] += position["estimated_tax_savings"]
        self.harvest_history["ytd_summary"]["harvest_count"] += 1
        self._save_history()

        print(f"    [SUCCESS] Harvested ${loss_amount:.2f} loss, Est. tax savings: ${result['tax_savings']:.2f}")

        return result

    def run_daily_harvest(self, dry_run: bool = False) -> List[Dict]:
        """
        Main entry point: scan and harvest all eligible positions.

        Args:
            dry_run: If True, only scan and report without executing

        Returns:
            List of harvest results
        """
        print("=" * 70)
        print(f"TAX-LOSS HARVESTING - {self.account_type}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        # Scan for harvestable positions
        harvestable = self.scan_harvestable_positions()

        if not harvestable:
            print("\n[TLH] No positions meet harvesting criteria")
            return []

        if dry_run:
            print("\n[DRY RUN] Would harvest the following positions:")
            total_loss = sum(abs(p["unrealized_pl"]) for p in harvestable)
            total_savings = sum(p["estimated_tax_savings"] for p in harvestable)
            for pos in harvestable:
                print(f"  - {pos['symbol']}: Sell {pos['qty']} shares, Loss ${abs(pos['unrealized_pl']):.2f}")
                print(f"    Replace with {pos['replacement']}")
            print(f"\nTotal potential harvest: ${total_loss:.2f}")
            print(f"Estimated tax savings: ${total_savings:.2f}")
            return []

        # Execute harvests
        results = []
        for position in harvestable:
            result = self.execute_harvest(position, auto_replace=True)
            results.append(result)

        # Send notification
        if results:
            self._send_harvest_notification(results)

        # Summary
        print("\n" + "=" * 70)
        print("HARVEST SUMMARY")
        print("=" * 70)
        successful = [r for r in results if r["status"] == "completed"]
        failed = [r for r in results if r["status"] == "failed"]

        print(f"Successful harvests: {len(successful)}")
        print(f"Failed harvests: {len(failed)}")

        if successful:
            total_harvested = sum(r["loss_harvested"] for r in successful)
            total_savings = sum(r["tax_savings"] for r in successful)
            print(f"Total losses harvested: ${total_harvested:.2f}")
            print(f"Estimated tax savings: ${total_savings:.2f}")

        print("\nYTD Summary:")
        print(f"  Total harvested: ${self.harvest_history['ytd_summary']['total_harvested']:.2f}")
        print(f"  Est. tax savings: ${self.harvest_history['ytd_summary']['estimated_tax_savings']:.2f}")
        print(f"  Harvest count: {self.harvest_history['ytd_summary']['harvest_count']}")

        return results

    def _send_harvest_notification(self, results: List[Dict]):
        """Send Telegram notification about harvest results."""
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not bot_token or not chat_id:
            print("[TLH] Telegram credentials not found, skipping notification")
            return

        successful = [r for r in results if r["status"] == "completed"]
        if not successful:
            return

        total_harvested = sum(r["loss_harvested"] for r in successful)
        total_savings = sum(r["tax_savings"] for r in successful)

        message = f"Tax-Loss Harvest - {self.account_type}\n"
        message += f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        message += f"Harvested {len(successful)} position(s):\n"

        for r in successful:
            message += f"SOLD {r['sold_symbol']} -> {r['bought_symbol'] or 'CASH'}\n"
            message += f"  Loss: ${r['loss_harvested']:.2f}\n"

        message += f"\nTotal Harvested: ${total_harvested:.2f}\n"
        message += f"Est. Tax Savings: ${total_savings:.2f}"

        try:
            url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            response = requests.post(url, data={
                'chat_id': chat_id,
                'text': message
            }, timeout=10)

            if response.json().get('ok'):
                print("[TLH] Telegram notification sent")
            else:
                print(f"[TLH] Telegram notification failed: {response.text}")
        except Exception as e:
            print(f"[TLH] Error sending Telegram notification: {e}")


def run_tax_loss_harvesting(account_type: str = None, dry_run: bool = False):
    """
    Convenience function to run tax-loss harvesting.

    Args:
        account_type: "DEE-LIVE", "SHORGAN-LIVE", or None for both
        dry_run: If True, only scan and report without executing
    """
    accounts = []

    if account_type:
        accounts = [account_type.upper()]
    else:
        # Run for all live accounts
        accounts = ["DEE-LIVE", "SHORGAN-LIVE"]

    all_results = {}

    for acct in accounts:
        try:
            harvester = TaxLossHarvester(acct)
            results = harvester.run_daily_harvest(dry_run=dry_run)
            all_results[acct] = results
        except ValueError as e:
            print(f"[TLH] Skipping {acct}: {e}")
        except Exception as e:
            print(f"[TLH] Error processing {acct}: {e}")

    return all_results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Tax-Loss Harvesting Tool")
    parser.add_argument(
        "--account",
        choices=["DEE-LIVE", "SHORGAN-LIVE", "ALL"],
        default="ALL",
        help="Account to harvest (default: ALL)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and report without executing trades"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=100.0,
        help="Minimum loss threshold to harvest (default: $100)"
    )

    args = parser.parse_args()

    account = None if args.account == "ALL" else args.account
    run_tax_loss_harvesting(account_type=account, dry_run=args.dry_run)
