"""
Insider Trading Monitor - Adapter for Alternative Data Aggregator
Wraps existing insider_monitor.py from data_sources/
"""

import logging
from datetime import datetime
from typing import List
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from data_sources.insider_monitor import InsiderMonitor, get_insider_signals
from src.data.alternative_data_aggregator import AlternativeDataSignal, SignalType

logger = logging.getLogger(__name__)


class InsiderMonitorAdapter:
    """
    Adapter to convert insider trading data to AlternativeDataSignal format
    """

    def __init__(self, api_client=None):
        """
        Initialize insider monitor

        Args:
            api_client: Financial Datasets API client
        """
        self.api_client = api_client
        if api_client:
            self.monitor = InsiderMonitor(api_client)
        else:
            self.monitor = None
            logger.warning("Insider monitor initialized without API client")

    def get_signals(self, ticker: str, days: int = 30) -> List[AlternativeDataSignal]:
        """
        Get insider trading signals for a ticker

        Args:
            ticker: Stock ticker symbol
            days: Number of days to look back

        Returns:
            List of AlternativeDataSignal objects
        """
        if not self.monitor:
            logger.warning(f"Insider monitor not available for {ticker}")
            return []

        try:
            # Fetch insider transactions
            transactions = self.monitor.fetch_recent_transactions(ticker, days=days)

            if not transactions:
                logger.info(f"No insider transactions found for {ticker}")
                return []

            signals = []

            for txn in transactions:
                # Convert insider signal to AlternativeDataSignal
                if txn.signal == 'BULLISH':
                    signal_type = SignalType.BULLISH
                    # Strength based on transaction value (capped at 100)
                    strength = min(100, (txn.value / 500000) * 50 + 50)
                elif txn.signal == 'BEARISH':
                    signal_type = SignalType.BEARISH
                    strength = min(100, (txn.value / 1000000) * 50 + 50)
                else:  # NEUTRAL
                    signal_type = SignalType.NEUTRAL
                    strength = 50.0

                # Confidence based on insider position and value
                is_c_suite = any(title in txn.title.upper()
                                for title in ['CEO', 'CFO', 'PRESIDENT', 'CHAIRMAN', 'COO'])

                if is_c_suite and txn.value >= 500000:
                    confidence = 90.0
                elif is_c_suite or txn.value >= 500000:
                    confidence = 75.0
                elif txn.value >= 250000:
                    confidence = 60.0
                else:
                    confidence = 50.0

                signal = AlternativeDataSignal(
                    ticker=ticker,
                    source='insider',
                    signal_type=signal_type,
                    strength=strength,
                    confidence=confidence,
                    timestamp=txn.filing_date,
                    metadata={
                        'insider_name': txn.insider_name,
                        'title': txn.title,
                        'transaction_type': txn.transaction_type,
                        'shares': txn.shares,
                        'price': txn.price,
                        'value': txn.value,
                        'filing_date': txn.filing_date.isoformat(),
                        'transaction_date': txn.transaction_date.isoformat()
                    }
                )

                signals.append(signal)

            logger.info(f"Generated {len(signals)} insider signals for {ticker}")
            return signals

        except Exception as e:
            logger.error(f"Error fetching insider signals for {ticker}: {e}")
            return []

    def get_summary(self, ticker: str, days: int = 30) -> dict:
        """
        Get summary of insider activity

        Args:
            ticker: Stock ticker symbol
            days: Number of days to look back

        Returns:
            Dictionary with summary statistics
        """
        signals = self.get_signals(ticker, days)

        if not signals:
            return {
                'ticker': ticker,
                'total_signals': 0,
                'bullish_count': 0,
                'bearish_count': 0,
                'net_signal': 'NEUTRAL',
                'avg_confidence': 0.0
            }

        bullish_count = sum(1 for s in signals if s.signal_type == SignalType.BULLISH)
        bearish_count = sum(1 for s in signals if s.signal_type == SignalType.BEARISH)

        if bullish_count > bearish_count:
            net_signal = 'BULLISH'
        elif bearish_count > bullish_count:
            net_signal = 'BEARISH'
        else:
            net_signal = 'NEUTRAL'

        avg_confidence = sum(s.confidence for s in signals) / len(signals)

        return {
            'ticker': ticker,
            'total_signals': len(signals),
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'net_signal': net_signal,
            'avg_confidence': avg_confidence
        }
