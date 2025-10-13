"""
Wash Sale Prevention System
Checks for wash sale risks before executing trades
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import alpaca_trade_api as tradeapi

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dotenv import load_dotenv
load_dotenv()


class WashSaleChecker:
    """Check for wash sale risks in trading"""

    WASH_SALE_DAYS = 30  # IRS wash sale period

    def __init__(self, account_type='dee'):
        """Initialize wash sale checker

        Args:
            account_type: 'dee' or 'shorgan'
        """
        self.account_type = account_type.lower()

        # Initialize Alpaca API
        if self.account_type == 'dee':
            api_key = os.getenv('ALPACA_API_KEY')
            api_secret = os.getenv('ALPACA_SECRET_KEY')
        else:
            api_key = os.getenv('ALPACA_API_KEY_SHORGAN')
            api_secret = os.getenv('ALPACA_SECRET_KEY_SHORGAN')

        base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')

        self.api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

    def get_position_history(self, ticker: str, days: int = 30) -> List[Dict]:
        """Get position history for a ticker

        Args:
            ticker: Stock symbol
            days: Number of days to look back

        Returns:
            List of positions and trades
        """
        # Get current position
        try:
            position = self.api.get_position(ticker)
            has_position = True
        except:
            has_position = False
            position = None

        # Get recent orders - Alpaca requires RFC3339 format
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        try:
            # Format date as RFC3339 (YYYY-MM-DDTHH:MM:SSZ)
            after_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            orders = self.api.list_orders(
                status='all',
                limit=500,
                after=after_date
            )
            # Filter by ticker since symbols parameter may not work
            orders = [o for o in orders if o.symbol == ticker]
        except Exception as e:
            print(f"Error fetching orders: {e}")
            orders = []

        # Get filled orders only
        filled_orders = [
            {
                'ticker': o.symbol,
                'side': o.side,
                'qty': float(o.filled_qty) if o.filled_qty else 0,
                'price': float(o.filled_avg_price) if o.filled_avg_price else 0,
                'date': o.filled_at,
                'status': o.status
            }
            for o in orders
            if o.status == 'filled' and o.filled_qty
        ]

        return {
            'has_position': has_position,
            'position': position,
            'recent_orders': filled_orders
        }

    def check_wash_sale_risk(self, ticker: str, action: str, quantity: int = 0) -> Dict:
        """Check if a trade would trigger a wash sale

        Args:
            ticker: Stock symbol
            action: 'buy' or 'sell'
            quantity: Number of shares (optional)

        Returns:
            Dictionary with wash sale risk information
        """
        history = self.get_position_history(ticker, self.WASH_SALE_DAYS)

        result = {
            'ticker': ticker,
            'action': action,
            'blocked': False,
            'reason': None,
            'has_current_position': history['has_position'],
            'recent_trades': len(history['recent_orders']),
            'last_trade_date': None,
            'days_since_last_trade': None,
            'clear_date': None,
            'alternatives': []
        }

        # Check if we have recent trades
        if not history['recent_orders']:
            result['reason'] = "No recent trades - safe to trade"
            return result

        # Get most recent trade
        recent_orders = sorted(history['recent_orders'], key=lambda x: x['date'], reverse=True)
        last_trade = recent_orders[0]

        last_trade_date = last_trade['date']
        days_since = (datetime.now(last_trade_date.tzinfo) - last_trade_date).days

        result['last_trade_date'] = last_trade_date.strftime('%Y-%m-%d')
        result['days_since_last_trade'] = days_since
        result['clear_date'] = (last_trade_date + timedelta(days=self.WASH_SALE_DAYS + 1)).strftime('%Y-%m-%d')

        # Check for wash sale risk
        if days_since < self.WASH_SALE_DAYS:
            # Within wash sale window

            # If we're trying to buy and we recently bought, that's OK
            if action.lower() == 'buy' and last_trade['side'] == 'buy':
                result['blocked'] = True
                result['reason'] = f"Wash sale risk: Bought {ticker} {days_since} days ago. Cannot buy again until {result['clear_date']}."

            # If we're trying to buy after a recent sell, check if it was at a loss
            elif action.lower() == 'buy' and last_trade['side'] == 'sell':
                # Get the purchase before the sell to check if it was a loss
                buy_orders = [o for o in recent_orders if o['side'] == 'buy']
                if buy_orders:
                    original_buy = buy_orders[0]
                    if last_trade['price'] < original_buy['price']:
                        # Sold at a loss - wash sale applies
                        result['blocked'] = True
                        result['reason'] = f"Wash sale risk: Sold {ticker} at loss {days_since} days ago. Cannot rebuy until {result['clear_date']}."

            # If we currently have a position and recently traded, flag it
            elif history['has_position']:
                result['blocked'] = True
                result['reason'] = f"Wash sale risk: Active position in {ticker} from {days_since} days ago. Wait until {result['clear_date']}."

        else:
            result['reason'] = f"Safe to trade: Last trade was {days_since} days ago (>30 days)"

        # Add alternatives if blocked
        if result['blocked']:
            result['alternatives'] = self.suggest_alternatives(ticker)

        return result

    def check_multiple_tickers(self, trades: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Check multiple trades for wash sale risks

        Args:
            trades: List of trade dicts with 'ticker', 'action', 'quantity'

        Returns:
            Tuple of (safe_trades, blocked_trades)
        """
        safe_trades = []
        blocked_trades = []

        for trade in trades:
            ticker = trade.get('ticker')
            action = trade.get('action', 'buy')
            quantity = trade.get('quantity', trade.get('shares', 0))

            result = self.check_wash_sale_risk(ticker, action, quantity)

            if result['blocked']:
                blocked_trades.append({
                    **trade,
                    'wash_sale_info': result
                })
            else:
                safe_trades.append(trade)

        return safe_trades, blocked_trades

    def suggest_alternatives(self, ticker: str) -> List[str]:
        """Suggest alternative securities that won't trigger wash sales

        Args:
            ticker: Blocked ticker symbol

        Returns:
            List of alternative tickers
        """
        # Alternative securities mapping
        ALTERNATIVES = {
            # Biotech/Pharma
            'ARQT': ['KRYS', 'DNLI', 'DERM', 'LEGN'],
            'KRYS': ['ARQT', 'DNLI', 'VRTX'],

            # Telehealth
            'HIMS': ['TDOC', 'AMWL', 'ONEM', 'DOCS'],
            'TDOC': ['HIMS', 'AMWL', 'ONEM'],

            # Semiconductors
            'WOLF': ['ON', 'MPWR', 'QRVO', 'SWKS'],
            'ON': ['WOLF', 'MPWR', 'MXL'],
            'MPWR': ['WOLF', 'ON', 'POWI'],

            # Energy/Oil
            'PLUG': ['BE', 'FCEL', 'BLDP', 'CLNE'],
            'RIG': ['VAL', 'NE', 'DO', 'PTEN'],

            # Large Cap Tech (ETF alternatives)
            'AAPL': ['QQQ', 'XLK', 'VGT'],
            'MSFT': ['QQQ', 'XLK', 'VGT'],
            'GOOGL': ['QQQ', 'XLK', 'VGT'],

            # Defensive/Healthcare
            'UNH': ['XLV', 'VHT', 'CVS', 'CI'],
            'JNJ': ['XLV', 'PFE', 'ABT', 'BMY'],

            # Utilities
            'NEE': ['XLU', 'DUK', 'SO', 'D'],
            'DUK': ['XLU', 'NEE', 'SO', 'D'],

            # Retail
            'WMT': ['TGT', 'COST', 'XRT'],
            'COST': ['WMT', 'TGT', 'XRT'],
            'TGT': ['WMT', 'COST', 'XRT'],
        }

        # Get alternatives or suggest sector ETF
        alternatives = ALTERNATIVES.get(ticker, [])

        # If no alternatives, suggest checking similar sector ETFs
        if not alternatives:
            alternatives = ['Check similar sector ETFs']

        return alternatives

    def generate_report(self, trades: List[Dict]) -> str:
        """Generate a wash sale report for proposed trades

        Args:
            trades: List of proposed trades

        Returns:
            Formatted report string
        """
        safe, blocked = self.check_multiple_tickers(trades)

        report = []
        report.append("=" * 80)
        report.append(f"WASH SALE RISK ANALYSIS - {self.account_type.upper()}-BOT")
        report.append("=" * 80)
        report.append("")
        report.append(f"Total Trades Analyzed: {len(trades)}")
        report.append(f"Safe to Execute: {len(safe)} [OK]")
        report.append(f"Blocked (Wash Sale Risk): {len(blocked)} [BLOCKED]")
        report.append("")

        if safe:
            report.append("-" * 80)
            report.append("SAFE TRADES (No Wash Sale Risk)")
            report.append("-" * 80)
            for trade in safe:
                report.append(f"[OK] {trade['action'].upper()} {trade.get('quantity', trade.get('shares', 0))} {trade['ticker']}")
            report.append("")

        if blocked:
            report.append("-" * 80)
            report.append("BLOCKED TRADES (Wash Sale Risk)")
            report.append("-" * 80)
            for trade in blocked:
                info = trade['wash_sale_info']
                report.append(f"[BLOCKED] {trade['action'].upper()} {trade.get('quantity', trade.get('shares', 0))} {trade['ticker']}")
                report.append(f"   Reason: {info['reason']}")
                report.append(f"   Last Trade: {info['last_trade_date']} ({info['days_since_last_trade']} days ago)")
                report.append(f"   Clear Date: {info['clear_date']}")
                if info['alternatives']:
                    report.append(f"   Alternatives: {', '.join(info['alternatives'])}")
                report.append("")

        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Test wash sale checker"""
    import argparse

    parser = argparse.ArgumentParser(description='Check for wash sale risks')
    parser.add_argument('--account', choices=['dee', 'shorgan'], default='shorgan',
                      help='Account to check (dee or shorgan)')
    parser.add_argument('--ticker', type=str, help='Ticker to check')
    parser.add_argument('--action', choices=['buy', 'sell'], default='buy',
                      help='Action to check')

    args = parser.parse_args()

    checker = WashSaleChecker(args.account)

    if args.ticker:
        # Check single ticker
        result = checker.check_wash_sale_risk(args.ticker, args.action)

        print("=" * 80)
        print(f"WASH SALE CHECK: {args.ticker}")
        print("=" * 80)
        print(f"Account: {args.account.upper()}-BOT")
        print(f"Action: {args.action.upper()}")
        print(f"Blocked: {'YES [BLOCKED]' if result['blocked'] else 'NO [OK]'}")
        print(f"Reason: {result['reason']}")

        if result['last_trade_date']:
            print(f"Last Trade: {result['last_trade_date']} ({result['days_since_last_trade']} days ago)")
            print(f"Clear Date: {result['clear_date']}")

        if result['alternatives']:
            print(f"Alternatives: {', '.join(result['alternatives'])}")

        print("=" * 80)

    else:
        # Check today's failed trades
        print("Checking today's failed SHORGAN-BOT trades...")

        test_trades = [
            {'ticker': 'ARQT', 'action': 'buy', 'shares': 150},
            {'ticker': 'HIMS', 'action': 'buy', 'shares': 37},
            {'ticker': 'WOLF', 'action': 'buy', 'shares': 96},
            {'ticker': 'PLUG', 'action': 'sell', 'shares': 500},
        ]

        report = checker.generate_report(test_trades)
        print(report)


if __name__ == '__main__':
    main()
