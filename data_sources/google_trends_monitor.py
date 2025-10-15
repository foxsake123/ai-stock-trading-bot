"""
Google Trends Monitoring Module
Tracks retail investor interest and search momentum using Google Trends data
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import time

logger = logging.getLogger(__name__)

@dataclass
class TrendData:
    """Data class for Google Trends data"""
    keyword: str
    ticker: str
    current_interest: int  # 0-100 scale
    avg_interest_7d: float
    avg_interest_30d: float
    peak_interest: int
    peak_date: datetime
    trend_direction: str  # RISING, FALLING, STABLE
    momentum_score: float  # -1.0 to 1.0
    is_breakout: bool  # True if current > 2x average
    related_queries: List[str]
    signal: str  # BULLISH, BEARISH, NEUTRAL


@dataclass
class ComparisonData:
    """Data class for comparing multiple tickers"""
    tickers: List[str]
    winner: str  # Ticker with highest interest
    interest_scores: Dict[str, int]
    relative_strength: Dict[str, float]  # Normalized scores


class GoogleTrendsMonitor:
    """Monitor and analyze Google Trends data for trading signals"""

    def __init__(self, pytrends_client=None):
        """
        Initialize with pytrends client

        Args:
            pytrends_client: Configured pytrends TrendReq object
                If None, will be created on first use
        """
        self._pytrends = pytrends_client
        self.request_delay = 2  # seconds between requests
        self.last_request_time = 0

        # Signal thresholds
        self.breakout_threshold = 2.0  # 2x average = breakout
        self.rising_threshold = 0.20  # 20% increase = rising
        self.falling_threshold = -0.20  # 20% decrease = falling

    @property
    def pytrends(self):
        """Lazy load pytrends client"""
        if self._pytrends is None:
            try:
                from pytrends.request import TrendReq
                self._pytrends = TrendReq(hl='en-US', tz=360)
                logger.info("Initialized pytrends client")
            except ImportError:
                logger.error("pytrends not installed. Run: pip install pytrends")
                raise
        return self._pytrends

    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def get_interest_over_time(
        self,
        keyword: str,
        timeframe: str = 'today 3-m'
    ) -> Optional[Dict]:
        """
        Get Google Trends interest over time for a keyword

        Args:
            keyword: Search term (usually ticker symbol)
            timeframe: Google Trends timeframe
                'now 1-H' = past hour
                'now 4-H' = past 4 hours
                'now 1-d' = past day
                'today 1-m' = past month
                'today 3-m' = past 3 months (default)

        Returns:
            Dictionary with interest data or None on error
        """
        try:
            self._rate_limit()

            # Build payload
            self.pytrends.build_payload(
                kw_list=[keyword],
                timeframe=timeframe,
                geo='US'
            )

            # Get interest over time
            df = self.pytrends.interest_over_time()

            if df.empty or keyword not in df.columns:
                logger.warning(f"No trends data for {keyword}")
                return None

            # Extract time series
            interest_series = df[keyword].values.tolist()
            dates = df.index.tolist()

            return {
                'keyword': keyword,
                'dates': dates,
                'interest': interest_series,
                'current': interest_series[-1] if interest_series else 0,
                'max': max(interest_series) if interest_series else 0,
                'avg': sum(interest_series) / len(interest_series) if interest_series else 0
            }

        except Exception as e:
            logger.error(f"Error fetching trends for {keyword}: {e}")
            return None

    def get_related_queries(self, keyword: str) -> List[str]:
        """
        Get related rising queries for a keyword

        Args:
            keyword: Search term

        Returns:
            List of related query strings
        """
        try:
            self._rate_limit()

            # Must call build_payload first
            self.pytrends.build_payload(
                kw_list=[keyword],
                timeframe='today 3-m',
                geo='US'
            )

            # Get related queries
            related = self.pytrends.related_queries()

            if keyword not in related:
                return []

            # Extract top rising queries
            rising = related[keyword].get('rising')
            if rising is None or rising.empty:
                return []

            # Return top 5 query strings
            return rising.head(5)['query'].tolist()

        except Exception as e:
            logger.error(f"Error fetching related queries for {keyword}: {e}")
            return []

    def analyze_ticker(
        self,
        ticker: str,
        company_name: Optional[str] = None
    ) -> Optional[TrendData]:
        """
        Analyze Google Trends data for a ticker

        Args:
            ticker: Stock ticker symbol
            company_name: Company name (optional, for better results)

        Returns:
            TrendData object with analysis
        """
        try:
            # Use both ticker and company name if available
            keywords = [ticker]
            if company_name:
                keywords.append(company_name)

            # Get trends for primary keyword (ticker)
            data = self.get_interest_over_time(ticker, timeframe='today 3-m')
            if not data:
                return self._default_trend_data(ticker)

            # Calculate metrics
            current = data['current']
            interest_series = data['interest']

            # Calculate averages
            avg_7d = self._calculate_recent_avg(interest_series, days=7)
            avg_30d = self._calculate_recent_avg(interest_series, days=30)

            # Find peak
            peak_value = data['max']
            peak_idx = interest_series.index(peak_value)
            peak_date = data['dates'][peak_idx]

            # Determine trend direction
            trend_direction = self._determine_trend(current, avg_7d, avg_30d)

            # Calculate momentum score
            momentum = self._calculate_momentum(current, avg_7d, avg_30d)

            # Check for breakout
            is_breakout = current >= (avg_30d * self.breakout_threshold)

            # Get related queries
            related = self.get_related_queries(ticker)

            # Determine signal
            signal = self._determine_signal(
                trend_direction,
                momentum,
                is_breakout,
                current,
                avg_30d
            )

            return TrendData(
                keyword=ticker,
                ticker=ticker,
                current_interest=current,
                avg_interest_7d=avg_7d,
                avg_interest_30d=avg_30d,
                peak_interest=peak_value,
                peak_date=peak_date,
                trend_direction=trend_direction,
                momentum_score=momentum,
                is_breakout=is_breakout,
                related_queries=related,
                signal=signal
            )

        except Exception as e:
            logger.error(f"Error analyzing trends for {ticker}: {e}")
            return self._default_trend_data(ticker)

    def compare_tickers(
        self,
        tickers: List[str],
        timeframe: str = 'today 1-m'
    ) -> Optional[ComparisonData]:
        """
        Compare Google Trends interest across multiple tickers

        Args:
            tickers: List of ticker symbols (max 5)
            timeframe: Timeframe for comparison

        Returns:
            ComparisonData with relative interest scores
        """
        try:
            if len(tickers) > 5:
                logger.warning("Google Trends limits to 5 keywords, using first 5")
                tickers = tickers[:5]

            self._rate_limit()

            # Build payload with multiple keywords
            self.pytrends.build_payload(
                kw_list=tickers,
                timeframe=timeframe,
                geo='US'
            )

            # Get interest over time
            df = self.pytrends.interest_over_time()

            if df.empty:
                return None

            # Calculate current interest scores
            interest_scores = {}
            for ticker in tickers:
                if ticker in df.columns:
                    interest_scores[ticker] = int(df[ticker].iloc[-1])
                else:
                    interest_scores[ticker] = 0

            # Find winner
            winner = max(interest_scores, key=interest_scores.get)

            # Calculate relative strength (normalized 0-1)
            max_interest = max(interest_scores.values()) if interest_scores else 1
            relative_strength = {
                ticker: score / max_interest if max_interest > 0 else 0
                for ticker, score in interest_scores.items()
            }

            return ComparisonData(
                tickers=tickers,
                winner=winner,
                interest_scores=interest_scores,
                relative_strength=relative_strength
            )

        except Exception as e:
            logger.error(f"Error comparing tickers: {e}")
            return None

    def _calculate_recent_avg(self, series: List[int], days: int) -> float:
        """Calculate average of most recent N data points"""
        if not series:
            return 0.0

        # Assuming daily data points
        recent = series[-days:] if len(series) >= days else series
        return sum(recent) / len(recent) if recent else 0.0

    def _determine_trend(
        self,
        current: int,
        avg_7d: float,
        avg_30d: float
    ) -> str:
        """Determine trend direction"""
        # Compare current to 7-day average
        if avg_7d == 0:
            return 'STABLE'

        change = (current - avg_7d) / avg_7d

        if change >= self.rising_threshold:
            return 'RISING'
        elif change <= self.falling_threshold:
            return 'FALLING'
        else:
            return 'STABLE'

    def _calculate_momentum(
        self,
        current: int,
        avg_7d: float,
        avg_30d: float
    ) -> float:
        """
        Calculate momentum score (-1.0 to 1.0)

        Positive momentum = current > recent averages
        Negative momentum = current < recent averages
        """
        if avg_30d == 0:
            return 0.0

        # Compare to 30-day average
        long_term_change = (current - avg_30d) / avg_30d

        # Compare 7-day to 30-day (acceleration)
        if avg_30d != 0:
            acceleration = (avg_7d - avg_30d) / avg_30d
        else:
            acceleration = 0.0

        # Weighted combination
        momentum = (long_term_change * 0.6) + (acceleration * 0.4)

        # Clamp to [-1, 1]
        return max(-1.0, min(1.0, momentum))

    def _determine_signal(
        self,
        trend: str,
        momentum: float,
        is_breakout: bool,
        current: int,
        avg_30d: float
    ) -> str:
        """Determine trading signal from trends data"""

        # Breakout with rising trend = strong bullish
        if is_breakout and trend == 'RISING':
            return 'BULLISH'

        # Rising trend with positive momentum
        if trend == 'RISING' and momentum > 0.3:
            return 'BULLISH'

        # Falling trend with negative momentum
        if trend == 'FALLING' and momentum < -0.3:
            return 'BEARISH'

        # Very low interest (< 10 consistently) = bearish
        if current < 10 and avg_30d < 10:
            return 'BEARISH'

        return 'NEUTRAL'

    def _default_trend_data(self, ticker: str) -> TrendData:
        """Return default/neutral trend data when no data available"""
        return TrendData(
            keyword=ticker,
            ticker=ticker,
            current_interest=0,
            avg_interest_7d=0.0,
            avg_interest_30d=0.0,
            peak_interest=0,
            peak_date=datetime.now(),
            trend_direction='STABLE',
            momentum_score=0.0,
            is_breakout=False,
            related_queries=[],
            signal='NEUTRAL'
        )

    def generate_report(
        self,
        ticker_data: Dict[str, TrendData]
    ) -> str:
        """
        Generate markdown report from trends data

        Args:
            ticker_data: Dictionary mapping ticker to TrendData

        Returns:
            Markdown formatted report
        """
        if not ticker_data:
            return "**No Google Trends data available.**\n"

        report = "## Google Trends Analysis\n\n"

        # Filter for significant signals only
        significant = {
            t: data for t, data in ticker_data.items()
            if data.signal in ['BULLISH', 'BEARISH'] or data.is_breakout
        }

        if not significant:
            report += "**No significant trend signals detected.**\n\n"
        else:
            report += "| Ticker | Interest | Trend | Momentum | Signal | Notes |\n"
            report += "|--------|----------|-------|----------|--------|-------|\n"

            for ticker, data in significant.items():
                # Format signal with icon
                signal_icon = "[BUY]" if data.signal == "BULLISH" else "[SELL]" if data.signal == "BEARISH" else "[HOLD]"

                # Create notes
                notes = []
                if data.is_breakout:
                    notes.append("BREAKOUT")
                if abs(data.momentum_score) > 0.5:
                    notes.append(f"{abs(data.momentum_score):.0%} momentum")
                if data.related_queries:
                    notes.append(f"{len(data.related_queries)} related")

                notes_str = ", ".join(notes) if notes else "-"

                report += f"| {ticker} | {data.current_interest}/100 | "
                report += f"{data.trend_direction} | {data.momentum_score:+.2f} | "
                report += f"{signal_icon} {data.signal} | {notes_str} |\n"

        # Add summary statistics
        total = len(ticker_data)
        bullish = sum(1 for d in ticker_data.values() if d.signal == 'BULLISH')
        bearish = sum(1 for d in ticker_data.values() if d.signal == 'BEARISH')
        breakouts = sum(1 for d in ticker_data.values() if d.is_breakout)

        report += f"\n**Summary**: {total} tickers analyzed, "
        report += f"{bullish} bullish, {bearish} bearish, {breakouts} breakouts\n"

        return report


def get_trends_signals(
    tickers: List[str],
    pytrends_client=None
) -> Dict:
    """
    Convenience function to get Google Trends signals for tickers

    Args:
        tickers: List of stock tickers
        pytrends_client: Optional pytrends client

    Returns:
        Dictionary with trend data and formatted report
    """
    monitor = GoogleTrendsMonitor(pytrends_client)
    ticker_data = {}

    for ticker in tickers:
        trend_data = monitor.analyze_ticker(ticker)
        if trend_data:
            ticker_data[ticker] = trend_data

    report = monitor.generate_report(ticker_data)

    return {
        'trends': ticker_data,
        'report': report,
        'summary': {
            'total_analyzed': len(ticker_data),
            'bullish_signals': sum(1 for d in ticker_data.values() if d.signal == 'BULLISH'),
            'bearish_signals': sum(1 for d in ticker_data.values() if d.signal == 'BEARISH'),
            'breakouts': sum(1 for d in ticker_data.values() if d.is_breakout)
        }
    }
