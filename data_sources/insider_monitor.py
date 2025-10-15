"""
Insider Transaction Monitoring Module
Fetches and analyzes SEC Form 4 filings for insider trading signals
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class InsiderTransaction:
    """Data class for insider transaction"""
    ticker: str
    insider_name: str
    title: str  # CEO, CFO, Director, etc.
    transaction_type: str  # BUY or SELL
    shares: int
    price: float
    value: float
    filing_date: datetime
    transaction_date: datetime
    signal: str  # BULLISH, BEARISH, NEUTRAL

class InsiderMonitor:
    """Monitor and analyze insider transactions"""

    def __init__(self, api_client):
        """
        Initialize with Financial Datasets API client

        Args:
            api_client: Configured Financial Datasets API client
        """
        self.api = api_client
        self.significance_threshold = 500_000  # $500K
        self.c_suite_titles = ['CEO', 'CFO', 'President', 'Chairman', 'COO']

    def fetch_recent_transactions(
        self,
        ticker: str,
        days: int = 30
    ) -> List[InsiderTransaction]:
        """
        Fetch recent insider transactions for a ticker

        Args:
            ticker: Stock ticker symbol
            days: Number of days to look back

        Returns:
            List of InsiderTransaction objects
        """
        try:
            # Fetch Form 4 filings from Financial Datasets API
            filings = self.api.get_filings(
                ticker=ticker,
                filing_type='4',
                limit=50
            )

            cutoff_date = datetime.now() - timedelta(days=days)
            transactions = []

            for filing in filings:
                # Parse filing data
                filing_date = datetime.fromisoformat(filing['filing_date'])

                if filing_date < cutoff_date:
                    continue

                # Extract transaction details
                transaction = self._parse_filing(ticker, filing)
                if transaction:
                    transactions.append(transaction)

            logger.info(f"Found {len(transactions)} insider transactions for {ticker}")
            return transactions

        except Exception as e:
            logger.error(f"Error fetching insider transactions for {ticker}: {e}")
            return []

    def _parse_filing(self, ticker: str, filing: dict) -> Optional[InsiderTransaction]:
        """Parse Form 4 filing into InsiderTransaction object"""
        try:
            # Extract relevant fields
            shares = filing.get('shares_traded', 0)
            price = filing.get('price_per_share', 0)
            value = shares * price

            transaction_type = filing.get('transaction_type', '').upper()
            if transaction_type not in ['BUY', 'SELL', 'PURCHASE', 'SALE']:
                return None

            # Normalize transaction type
            if transaction_type in ['PURCHASE', 'BUY']:
                transaction_type = 'BUY'
            elif transaction_type in ['SALE', 'SELL']:
                transaction_type = 'SELL'

            return InsiderTransaction(
                ticker=ticker,
                insider_name=filing.get('reporting_owner', 'Unknown'),
                title=filing.get('title', 'Unknown'),
                transaction_type=transaction_type,
                shares=shares,
                price=price,
                value=value,
                filing_date=datetime.fromisoformat(filing['filing_date']),
                transaction_date=datetime.fromisoformat(filing.get('transaction_date', filing['filing_date'])),
                signal=self._determine_signal(transaction_type, value, filing.get('title', ''))
            )

        except Exception as e:
            logger.error(f"Error parsing filing: {e}")
            return None

    def _determine_signal(self, transaction_type: str, value: float, title: str) -> str:
        """
        Determine trading signal from insider transaction

        Args:
            transaction_type: BUY or SELL
            value: Transaction value in dollars
            title: Insider's title/position

        Returns:
            Signal: BULLISH, BEARISH, or NEUTRAL
        """
        # Large transactions by C-suite are more significant
        is_c_suite = any(t.lower() in title.lower() for t in self.c_suite_titles)
        is_significant = value >= self.significance_threshold

        if transaction_type == 'BUY':
            if is_c_suite and is_significant:
                return 'BULLISH'
            elif is_significant:
                return 'BULLISH'
            else:
                return 'NEUTRAL'

        elif transaction_type == 'SELL':
            if is_c_suite and value >= self.significance_threshold * 2:  # 2x threshold for sells
                return 'BEARISH'
            elif value >= self.significance_threshold * 3:  # 3x threshold for non-C-suite
                return 'BEARISH'
            else:
                return 'NEUTRAL'  # Routine selling is common

        return 'NEUTRAL'

    def get_significant_transactions(
        self,
        tickers: List[str],
        days: int = 30
    ) -> Dict[str, List[InsiderTransaction]]:
        """
        Get significant insider transactions for multiple tickers

        Args:
            tickers: List of ticker symbols
            days: Number of days to look back

        Returns:
            Dictionary mapping ticker to list of significant transactions
        """
        results = {}

        for ticker in tickers:
            transactions = self.fetch_recent_transactions(ticker, days)

            # Filter for significant transactions only
            significant = [
                t for t in transactions
                if t.signal in ['BULLISH', 'BEARISH']
            ]

            if significant:
                results[ticker] = significant

        return results

    def generate_summary_report(
        self,
        transactions: Dict[str, List[InsiderTransaction]]
    ) -> str:
        """
        Generate markdown summary of insider transactions

        Args:
            transactions: Dictionary of ticker -> transactions

        Returns:
            Markdown formatted report
        """
        if not transactions:
            return "**No significant insider transactions detected.**\n"

        report = "## Insider Transaction Signals\n\n"

        for ticker, trans_list in transactions.items():
            report += f"### {ticker}\n\n"
            report += "| Date | Insider | Title | Type | Shares | Value | Signal |\n"
            report += "|------|---------|-------|------|--------|-------|--------|\n"

            for t in trans_list:
                signal_emoji = "[BUY]" if t.signal == "BULLISH" else "[SELL]" if t.signal == "BEARISH" else "[HOLD]"
                report += f"| {t.filing_date.strftime('%m/%d')} | "
                report += f"{t.insider_name[:20]} | {t.title[:15]} | "
                report += f"**{t.transaction_type}** | {t.shares:,} | "
                report += f"${t.value:,.0f} | {signal_emoji} {t.signal} |\n"

            # Summary for ticker
            bullish_count = sum(1 for t in trans_list if t.signal == 'BULLISH')
            bearish_count = sum(1 for t in trans_list if t.signal == 'BEARISH')
            net_value = sum(t.value if t.transaction_type == 'BUY' else -t.value for t in trans_list)

            report += f"\n**Net Signal:** "
            if bullish_count > bearish_count:
                report += f"[BUY] **BULLISH** ({bullish_count} buys vs {bearish_count} sells, "
            elif bearish_count > bullish_count:
                report += f"[SELL] **BEARISH** ({bearish_count} sells vs {bullish_count} buys, "
            else:
                report += f"[HOLD] **MIXED** ({bullish_count} buys, {bearish_count} sells, "

            report += f"Net: ${net_value:,.0f})\n\n"

        return report


def get_insider_signals(tickers: List[str], api_client, days: int = 30) -> Dict:
    """
    Convenience function to get insider signals for tickers

    Args:
        tickers: List of stock tickers
        api_client: Financial Datasets API client
        days: Days to look back

    Returns:
        Dictionary with transactions and formatted report
    """
    monitor = InsiderMonitor(api_client)
    transactions = monitor.get_significant_transactions(tickers, days)
    report = monitor.generate_summary_report(transactions)

    return {
        'transactions': transactions,
        'report': report,
        'summary': {
            'total_tickers': len(transactions),
            'total_transactions': sum(len(t) for t in transactions.values()),
            'bullish_signals': sum(
                1 for t_list in transactions.values()
                for t in t_list if t.signal == 'BULLISH'
            ),
            'bearish_signals': sum(
                1 for t_list in transactions.values()
                for t in t_list if t.signal == 'BEARISH'
            )
        }
    }
