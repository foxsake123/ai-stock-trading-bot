"""
Alternative Data Aggregator - Production-Ready Multi-Source Intelligence System
Consolidates signals from insider trading, options flow, social sentiment, and Google Trends
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
from collections import defaultdict
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Signal types"""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


@dataclass
class AlternativeDataSignal:
    """Standardized signal from alternative data sources"""
    ticker: str
    source: str  # 'insider', 'options', 'social', 'trends', 'other'
    signal_type: SignalType
    strength: float  # 0-100 scale
    confidence: float  # 0-100 scale
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'ticker': self.ticker,
            'source': self.source,
            'signal_type': self.signal_type.value,
            'strength': self.strength,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


class SignalCache:
    """1-hour cache for alternative data signals"""

    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Tuple[List[AlternativeDataSignal], datetime]] = {}
        self.ttl_seconds = ttl_seconds

    def get(self, ticker: str) -> Optional[List[AlternativeDataSignal]]:
        """Get cached signals if not expired"""
        if ticker in self.cache:
            signals, timestamp = self.cache[ticker]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl_seconds):
                logger.info(f"Cache HIT for {ticker} (age: {(datetime.now() - timestamp).seconds}s)")
                return signals
            else:
                logger.info(f"Cache EXPIRED for {ticker}")
                del self.cache[ticker]
        return None

    def set(self, ticker: str, signals: List[AlternativeDataSignal]):
        """Cache signals for ticker"""
        self.cache[ticker] = (signals, datetime.now())
        logger.info(f"Cached {len(signals)} signals for {ticker}")

    def clear(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("Cache cleared")


class AlternativeDataAggregator:
    """
    Production-ready aggregator for alternative data sources
    Fetches data asynchronously and generates composite scores
    """

    # Signal weights (must sum to 1.0)
    SIGNAL_WEIGHTS = {
        'insider': 0.25,
        'options': 0.25,
        'social': 0.20,
        'trends': 0.15,
        'other': 0.15
    }

    def __init__(self, api_client=None):
        """
        Initialize aggregator

        Args:
            api_client: Financial Datasets API client (optional)
        """
        self.api_client = api_client
        self.cache = SignalCache(ttl_seconds=3600)  # 1-hour cache

        # Import source modules with fallback handling
        self._init_sources()

    def _init_sources(self):
        """Initialize data source modules"""
        try:
            from src.data.sources.insider_monitor import InsiderMonitorAdapter
            self.insider_monitor = InsiderMonitorAdapter(self.api_client)
        except ImportError:
            logger.warning("InsiderMonitorAdapter not available")
            self.insider_monitor = None

        try:
            from src.data.sources.trends_analyzer import TrendsAnalyzer
            self.trends_analyzer = TrendsAnalyzer()
        except ImportError:
            logger.warning("TrendsAnalyzer not available")
            self.trends_analyzer = None

        try:
            from src.data.sources.social_sentiment import SocialSentimentAnalyzer
            self.social_analyzer = SocialSentimentAnalyzer()
        except ImportError:
            logger.warning("SocialSentimentAnalyzer not available")
            self.social_analyzer = None

        try:
            from src.data.sources.options_flow import OptionsFlowAnalyzer
            self.options_analyzer = OptionsFlowAnalyzer()
        except ImportError:
            logger.warning("OptionsFlowAnalyzer not available")
            self.options_analyzer = None

    async def fetch_all_signals(self, tickers: List[str]) -> Dict[str, List[AlternativeDataSignal]]:
        """
        Fetch signals from all sources asynchronously

        Args:
            tickers: List of stock tickers

        Returns:
            Dictionary mapping ticker to list of signals
        """
        all_signals = {}

        for ticker in tickers:
            # Check cache first
            cached_signals = self.cache.get(ticker)
            if cached_signals is not None:
                all_signals[ticker] = cached_signals
                continue

            # Fetch from all sources concurrently
            tasks = []

            if self.insider_monitor:
                tasks.append(self._fetch_insider_signals(ticker))
            if self.options_analyzer:
                tasks.append(self._fetch_options_signals(ticker))
            if self.social_analyzer:
                tasks.append(self._fetch_social_signals(ticker))
            if self.trends_analyzer:
                tasks.append(self._fetch_trends_signals(ticker))

            # Wait for all sources to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Combine signals
            ticker_signals = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error fetching signal for {ticker}: {result}")
                    continue
                if result:
                    ticker_signals.extend(result)

            # Cache the results
            if ticker_signals:
                self.cache.set(ticker, ticker_signals)
                all_signals[ticker] = ticker_signals
            else:
                # Store empty list to avoid repeated failed fetches
                self.cache.set(ticker, [])
                all_signals[ticker] = []

        return all_signals

    async def _fetch_insider_signals(self, ticker: str) -> List[AlternativeDataSignal]:
        """Fetch insider trading signals"""
        try:
            result = await asyncio.to_thread(
                self.insider_monitor.get_signals, ticker
            )
            return result if result else []
        except Exception as e:
            logger.error(f"Insider signal error for {ticker}: {e}")
            return []

    async def _fetch_options_signals(self, ticker: str) -> List[AlternativeDataSignal]:
        """Fetch options flow signals"""
        try:
            result = await asyncio.to_thread(
                self.options_analyzer.get_signals, ticker
            )
            return result if result else []
        except Exception as e:
            logger.error(f"Options signal error for {ticker}: {e}")
            return []

    async def _fetch_social_signals(self, ticker: str) -> List[AlternativeDataSignal]:
        """Fetch social sentiment signals"""
        try:
            result = await asyncio.to_thread(
                self.social_analyzer.get_signals, ticker
            )
            return result if result else []
        except Exception as e:
            logger.error(f"Social signal error for {ticker}: {e}")
            return []

    async def _fetch_trends_signals(self, ticker: str) -> List[AlternativeDataSignal]:
        """Fetch Google Trends signals"""
        try:
            result = await asyncio.to_thread(
                self.trends_analyzer.get_signals, ticker
            )
            return result if result else []
        except Exception as e:
            logger.error(f"Trends signal error for {ticker}: {e}")
            return []

    def calculate_composite_score(self, signals: List[AlternativeDataSignal]) -> Dict:
        """
        Calculate weighted composite score from all signals

        Args:
            signals: List of AlternativeDataSignal objects

        Returns:
            Dictionary with composite score and breakdown
        """
        if not signals:
            return {
                'composite_score': 0.0,
                'signal_type': SignalType.NEUTRAL.value,
                'confidence': 0.0,
                'breakdown': {},
                'signal_count': 0
            }

        # Group signals by source
        by_source = defaultdict(list)
        for signal in signals:
            by_source[signal.source].append(signal)

        # Calculate weighted average for each source
        source_scores = {}
        total_weight_used = 0.0

        for source, source_signals in by_source.items():
            # Calculate source average (weighted by confidence)
            total_strength = 0.0
            total_conf = 0.0

            for sig in source_signals:
                # Convert signal type to numeric score (-100 to +100)
                if sig.signal_type == SignalType.BULLISH:
                    score = sig.strength
                elif sig.signal_type == SignalType.BEARISH:
                    score = -sig.strength
                else:  # NEUTRAL
                    score = 0.0

                # Weight by confidence
                total_strength += score * (sig.confidence / 100.0)
                total_conf += sig.confidence / 100.0

            # Average strength for this source
            if total_conf > 0:
                avg_strength = total_strength / total_conf
                avg_confidence = total_conf / len(source_signals) * 100.0
            else:
                avg_strength = 0.0
                avg_confidence = 0.0

            source_scores[source] = {
                'strength': avg_strength,
                'confidence': avg_confidence,
                'signal_count': len(source_signals),
                'weight': self.SIGNAL_WEIGHTS.get(source, 0.0)
            }

            total_weight_used += self.SIGNAL_WEIGHTS.get(source, 0.0)

        # Calculate composite score (weighted average)
        composite_strength = 0.0
        composite_confidence = 0.0

        for source, scores in source_scores.items():
            weight = scores['weight']
            if total_weight_used > 0:
                normalized_weight = weight / total_weight_used
            else:
                normalized_weight = 0.0

            composite_strength += scores['strength'] * normalized_weight
            composite_confidence += scores['confidence'] * normalized_weight

        # Determine overall signal type
        if composite_strength > 10:
            signal_type = SignalType.BULLISH.value
        elif composite_strength < -10:
            signal_type = SignalType.BEARISH.value
        else:
            signal_type = SignalType.NEUTRAL.value

        return {
            'composite_score': composite_strength,  # -100 to +100
            'signal_type': signal_type,
            'confidence': composite_confidence,
            'breakdown': source_scores,
            'signal_count': len(signals)
        }

    def generate_summary_table(self, ticker_signals: Dict[str, List[AlternativeDataSignal]]) -> pd.DataFrame:
        """
        Generate summary table of composite scores

        Args:
            ticker_signals: Dictionary mapping ticker to signals

        Returns:
            Pandas DataFrame with summary
        """
        rows = []

        for ticker, signals in ticker_signals.items():
            composite = self.calculate_composite_score(signals)

            # Count signals by source
            source_counts = defaultdict(int)
            for sig in signals:
                source_counts[sig.source] += 1

            row = {
                'Ticker': ticker,
                'Composite Score': f"{composite['composite_score']:.1f}",
                'Signal': composite['signal_type'],
                'Confidence': f"{composite['confidence']:.1f}%",
                'Total Signals': composite['signal_count'],
                'Insider': source_counts.get('insider', 0),
                'Options': source_counts.get('options', 0),
                'Social': source_counts.get('social', 0),
                'Trends': source_counts.get('trends', 0)
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        # Sort by composite score (descending)
        if not df.empty:
            df['_sort_score'] = df['Composite Score'].astype(float)
            df = df.sort_values('_sort_score', ascending=False)
            df = df.drop('_sort_score', axis=1)

        return df

    def generate_markdown_report(self, ticker_signals: Dict[str, List[AlternativeDataSignal]]) -> str:
        """
        Generate markdown formatted report

        Args:
            ticker_signals: Dictionary mapping ticker to signals

        Returns:
            Markdown formatted string
        """
        report = "## Alternative Data Signals\n\n"
        report += f"*Analysis as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"

        if not ticker_signals:
            report += "**No alternative data signals available.**\n"
            return report

        # Generate summary table
        df = self.generate_summary_table(ticker_signals)

        if df.empty:
            report += "**No signals generated.**\n"
            return report

        # Add table
        report += "### Composite Scores\n\n"
        report += df.to_markdown(index=False)
        report += "\n\n"

        # Add detailed breakdown for each ticker
        report += "### Detailed Breakdown\n\n"

        for ticker, signals in sorted(ticker_signals.items()):
            if not signals:
                continue

            composite = self.calculate_composite_score(signals)

            report += f"#### {ticker}\n\n"
            report += f"**Composite Score**: {composite['composite_score']:.1f} ({composite['signal_type']})\n"
            report += f"**Confidence**: {composite['confidence']:.1f}%\n\n"

            # Breakdown by source
            if composite['breakdown']:
                report += "| Source | Strength | Confidence | Signals | Weight |\n"
                report += "|--------|----------|------------|---------|--------|\n"

                for source, scores in composite['breakdown'].items():
                    report += f"| {source.title()} | {scores['strength']:.1f} | "
                    report += f"{scores['confidence']:.1f}% | {scores['signal_count']} | "
                    report += f"{scores['weight']:.0%} |\n"

                report += "\n"

        # Add interpretation
        report += "### Interpretation\n\n"
        report += "- **Composite Score**: Range from -100 (very bearish) to +100 (very bullish)\n"
        report += "- **Signal Weights**: Insider (25%), Options (25%), Social (20%), Trends (15%), Other (15%)\n"
        report += "- **Confidence**: Higher values indicate stronger conviction across sources\n\n"

        return report

    async def analyze_tickers(self, tickers: List[str]) -> Dict:
        """
        Main entry point: Analyze tickers and return complete results

        Args:
            tickers: List of stock tickers

        Returns:
            Dictionary with signals, composite scores, and report
        """
        logger.info(f"Analyzing {len(tickers)} tickers: {tickers}")

        # Fetch all signals asynchronously
        ticker_signals = await self.fetch_all_signals(tickers)

        # Generate composite scores
        composite_scores = {}
        for ticker, signals in ticker_signals.items():
            composite_scores[ticker] = self.calculate_composite_score(signals)

        # Generate summary table
        summary_df = self.generate_summary_table(ticker_signals)

        # Generate markdown report
        report = self.generate_markdown_report(ticker_signals)

        return {
            'signals': ticker_signals,
            'composite_scores': composite_scores,
            'summary_table': summary_df,
            'report': report,
            'timestamp': datetime.now().isoformat()
        }


def analyze_tickers_sync(tickers: List[str], api_client=None) -> Dict:
    """
    Synchronous wrapper for analyze_tickers

    Args:
        tickers: List of stock tickers
        api_client: Financial Datasets API client (optional)

    Returns:
        Dictionary with analysis results
    """
    aggregator = AlternativeDataAggregator(api_client=api_client)
    return asyncio.run(aggregator.analyze_tickers(tickers))
