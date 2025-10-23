"""
Google Trends Analyzer - Adapter for Alternative Data Aggregator
Wraps existing trends_monitor.py from data_sources/
"""

import logging
from datetime import datetime
from typing import List
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from data_sources.trends_monitor import TrendsMonitor, get_trends_signals
from src.data.alternative_data_aggregator import AlternativeDataSignal, SignalType

logger = logging.getLogger(__name__)


class TrendsAnalyzer:
    """
    Adapter to convert Google Trends data to AlternativeDataSignal format
    """

    def __init__(self):
        """Initialize Google Trends analyzer"""
        try:
            self.monitor = TrendsMonitor()
        except ImportError as e:
            logger.warning(f"TrendsMonitor not available: {e}")
            self.monitor = None

    def get_signals(self, ticker: str, timeframe: str = 'today 1-m') -> List[AlternativeDataSignal]:
        """
        Get Google Trends signals for a ticker

        Args:
            ticker: Stock ticker symbol
            timeframe: Google Trends timeframe (default: last 30 days)

        Returns:
            List of AlternativeDataSignal objects
        """
        if not self.monitor:
            logger.warning(f"Trends monitor not available for {ticker}")
            return []

        try:
            # Fetch trends data
            trends_data = self.monitor.fetch_trends_data(ticker, timeframe=timeframe)

            if not trends_data:
                logger.info(f"No trends data found for {ticker}")
                return []

            # Convert to AlternativeDataSignal
            # Map trends signal to sentiment
            if trends_data.signal == 'SPIKE':
                signal_type = SignalType.BULLISH
                strength = 85.0  # High strength for spikes
                confidence = 75.0  # Moderate confidence (trends are noisy)
            elif trends_data.signal == 'ELEVATED':
                signal_type = SignalType.BULLISH
                strength = 65.0
                confidence = 60.0
            elif trends_data.signal == 'LOW':
                signal_type = SignalType.BEARISH
                strength = 60.0
                confidence = 50.0
            else:  # NORMAL
                signal_type = SignalType.NEUTRAL
                strength = 50.0
                confidence = 50.0

            # Adjust confidence based on magnitude of change
            if abs(trends_data.change_pct_7d) > 100:
                confidence = min(100, confidence + 15)
            elif abs(trends_data.change_pct_7d) > 50:
                confidence = min(100, confidence + 10)

            signal = AlternativeDataSignal(
                ticker=ticker,
                source='trends',
                signal_type=signal_type,
                strength=strength,
                confidence=confidence,
                timestamp=trends_data.timestamp,
                metadata={
                    'current_interest': trends_data.current_interest,
                    'avg_7d': trends_data.avg_7d,
                    'avg_30d': trends_data.avg_30d,
                    'change_pct_7d': trends_data.change_pct_7d,
                    'change_pct_30d': trends_data.change_pct_30d,
                    'signal': trends_data.signal,
                    'timeframe': timeframe
                }
            )

            logger.info(f"Generated trends signal for {ticker}: {trends_data.signal}")
            return [signal]

        except Exception as e:
            logger.error(f"Error fetching trends signals for {ticker}: {e}")
            return []

    def get_batch_signals(self, tickers: List[str], timeframe: str = 'today 1-m') -> dict:
        """
        Get trends signals for multiple tickers

        Args:
            tickers: List of stock ticker symbols
            timeframe: Google Trends timeframe

        Returns:
            Dictionary mapping ticker to list of signals
        """
        if not self.monitor:
            return {ticker: [] for ticker in tickers}

        results = {}

        try:
            # Use batch fetch for efficiency
            trends_dict = self.monitor.batch_fetch(tickers, timeframe=timeframe)

            for ticker in tickers:
                if ticker in trends_dict:
                    results[ticker] = self.get_signals(ticker, timeframe)
                else:
                    results[ticker] = []

        except Exception as e:
            logger.error(f"Error in batch trends fetch: {e}")
            results = {ticker: [] for ticker in tickers}

        return results

    def get_summary(self, ticker: str, timeframe: str = 'today 1-m') -> dict:
        """
        Get summary of trends activity

        Args:
            ticker: Stock ticker symbol
            timeframe: Google Trends timeframe

        Returns:
            Dictionary with summary statistics
        """
        signals = self.get_signals(ticker, timeframe)

        if not signals:
            return {
                'ticker': ticker,
                'signal': 'NEUTRAL',
                'interest_level': 0,
                'confidence': 0.0
            }

        signal = signals[0]  # Only one signal per ticker

        return {
            'ticker': ticker,
            'signal': signal.signal_type.value,
            'interest_level': signal.metadata.get('current_interest', 0),
            'confidence': signal.confidence,
            'change_7d': signal.metadata.get('change_pct_7d', 0.0)
        }
