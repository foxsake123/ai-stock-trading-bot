"""
Google Trends Monitoring Module
Tracks search interest for stock tickers to detect retail sentiment shifts
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import time

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    logging.warning("pytrends not installed. Run: pip install pytrends")

logger = logging.getLogger(__name__)

@dataclass
class TrendsData:
    """Data class for Google Trends metrics"""
    ticker: str
    current_interest: int  # 0-100 scale
    avg_7d: float
    avg_30d: float
    change_pct_7d: float
    change_pct_30d: float
    signal: str  # SPIKE, ELEVATED, NORMAL, LOW
    timestamp: datetime

class TrendsMonitor:
    """Monitor Google search interest for stock tickers"""

    def __init__(self):
        """Initialize Google Trends monitor"""
        if not PYTRENDS_AVAILABLE:
            raise ImportError("pytrends library not installed. Install with: pip install pytrends")

        self.pytrends = TrendReq(hl='en-US', tz=360)
        self.rate_limit_delay = 2  # seconds between requests

    def fetch_trends_data(
        self,
        ticker: str,
        timeframe: str = 'today 1-m'  # Last 30 days
    ) -> Optional[TrendsData]:
        """
        Fetch Google Trends data for a ticker

        Args:
            ticker: Stock ticker symbol
            timeframe: Google Trends timeframe (default: last 30 days)

        Returns:
            TrendsData object or None if error
        """
        try:
            # Add company name for better results
            search_terms = [ticker, f"{ticker} stock"]

            self.pytrends.build_payload(
                kw_list=[ticker],
                cat=0,  # All categories
                timeframe=timeframe,
                geo='US'
            )

            # Get interest over time
            interest_df = self.pytrends.interest_over_time()

            if interest_df.empty or ticker not in interest_df.columns:
                logger.warning(f"No trends data for {ticker}")
                return None

            # Calculate metrics
            series = interest_df[ticker]
            current_interest = int(series.iloc[-1])
            avg_7d = float(series.iloc[-7:].mean())
            avg_30d = float(series.mean())

            change_pct_7d = ((current_interest / avg_7d) - 1) * 100 if avg_7d > 0 else 0
            change_pct_30d = ((current_interest / avg_30d) - 1) * 100 if avg_30d > 0 else 0

            # Determine signal
            signal = self._determine_signal(current_interest, avg_7d, avg_30d)

            return TrendsData(
                ticker=ticker,
                current_interest=current_interest,
                avg_7d=avg_7d,
                avg_30d=avg_30d,
                change_pct_7d=change_pct_7d,
                change_pct_30d=change_pct_30d,
                signal=signal,
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error fetching trends for {ticker}: {e}")
            return None

    def _determine_signal(
        self,
        current: int,
        avg_7d: float,
        avg_30d: float
    ) -> str:
        """
        Determine interest signal

        Args:
            current: Current interest level (0-100)
            avg_7d: 7-day average
            avg_30d: 30-day average

        Returns:
            Signal: SPIKE, ELEVATED, NORMAL, or LOW
        """
        if current >= avg_7d * 2.0:  # 2x spike
            return 'SPIKE'
        elif current >= avg_7d * 1.5:  # 50% above average
            return 'ELEVATED'
        elif current >= avg_7d * 0.5:  # Normal range
            return 'NORMAL'
        else:
            return 'LOW'

    def batch_fetch(
        self,
        tickers: List[str],
        timeframe: str = 'today 1-m'
    ) -> Dict[str, TrendsData]:
        """
        Fetch trends data for multiple tickers

        Args:
            tickers: List of ticker symbols
            timeframe: Google Trends timeframe

        Returns:
            Dictionary mapping ticker to TrendsData
        """
        results = {}

        for i, ticker in enumerate(tickers):
            try:
                data = self.fetch_trends_data(ticker, timeframe)
                if data:
                    results[ticker] = data

                # Rate limiting to avoid Google blocking
                if i < len(tickers) - 1:
                    time.sleep(self.rate_limit_delay)

            except Exception as e:
                logger.error(f"Error fetching trends for {ticker}: {e}")
                continue

        return results

    def get_related_queries(self, ticker: str) -> Dict[str, List]:
        """
        Get related and rising search queries

        Args:
            ticker: Stock ticker

        Returns:
            Dictionary with 'top' and 'rising' queries
        """
        try:
            self.pytrends.build_payload(
                kw_list=[ticker],
                timeframe='today 1-m',
                geo='US'
            )

            related_queries = self.pytrends.related_queries()

            if ticker in related_queries:
                return {
                    'top': related_queries[ticker].get('top', []),
                    'rising': related_queries[ticker].get('rising', [])
                }

            return {'top': [], 'rising': []}

        except Exception as e:
            logger.error(f"Error fetching related queries for {ticker}: {e}")
            return {'top': [], 'rising': []}

    def generate_summary_report(
        self,
        trends_data: Dict[str, TrendsData]
    ) -> str:
        """
        Generate markdown summary of trends data

        Args:
            trends_data: Dictionary of ticker -> TrendsData

        Returns:
            Markdown formatted report
        """
        if not trends_data:
            return "**Google Trends data unavailable**\n"

        report = "## Google Trends Sentiment\n\n"
        report += "*Retail investor interest levels (0-100 scale)*\n\n"
        report += "| Ticker | Current | 7d Avg | 30d Avg | Change (7d) | Signal |\n"
        report += "|--------|---------|--------|---------|-------------|--------|\n"

        # Sort by signal priority (SPIKE first)
        signal_priority = {'SPIKE': 0, 'ELEVATED': 1, 'NORMAL': 2, 'LOW': 3}
        sorted_data = sorted(
            trends_data.items(),
            key=lambda x: signal_priority.get(x[1].signal, 4)
        )

        for ticker, data in sorted_data:
            signal_indicator = {
                'SPIKE': '[FIRE]',
                'ELEVATED': '[CHART]',
                'NORMAL': '[MINUS]',
                'LOW': '[DOWN]'
            }.get(data.signal, '[?]')

            change_str = f"+{data.change_pct_7d:.0f}%" if data.change_pct_7d > 0 else f"{data.change_pct_7d:.0f}%"

            report += f"| **{ticker}** | {data.current_interest} | "
            report += f"{data.avg_7d:.1f} | {data.avg_30d:.1f} | "
            report += f"{change_str} | {signal_indicator} {data.signal} |\n"

        # Add interpretation
        spike_count = sum(1 for d in trends_data.values() if d.signal == 'SPIKE')
        elevated_count = sum(1 for d in trends_data.values() if d.signal == 'ELEVATED')

        report += "\n**Interpretation:**\n"
        if spike_count > 0:
            report += f"- [FIRE] {spike_count} ticker(s) showing **significant retail interest spike** (2x+ above average)\n"
        if elevated_count > 0:
            report += f"- [CHART] {elevated_count} ticker(s) with **elevated interest** (50%+ above average)\n"

        report += "\n*Note: Spikes often precede increased volatility. Consider for short-term momentum plays.*\n\n"

        return report


def get_trends_signals(tickers: List[str]) -> Dict:
    """
    Convenience function to get Google Trends signals

    Args:
        tickers: List of stock tickers

    Returns:
        Dictionary with trends data and formatted report
    """
    try:
        monitor = TrendsMonitor()
        trends_data = monitor.batch_fetch(tickers)
        report = monitor.generate_summary_report(trends_data)

        return {
            'trends_data': trends_data,
            'report': report,
            'summary': {
                'total_tickers': len(trends_data),
                'spike_signals': sum(1 for d in trends_data.values() if d.signal == 'SPIKE'),
                'elevated_signals': sum(1 for d in trends_data.values() if d.signal == 'ELEVATED'),
                'avg_interest': sum(d.current_interest for d in trends_data.values()) / len(trends_data) if trends_data else 0
            }
        }
    except Exception as e:
        logger.error(f"Error in get_trends_signals: {e}")
        return {
            'trends_data': {},
            'report': "**Google Trends data temporarily unavailable**\n",
            'summary': {'total_tickers': 0, 'spike_signals': 0, 'elevated_signals': 0, 'avg_interest': 0}
        }
