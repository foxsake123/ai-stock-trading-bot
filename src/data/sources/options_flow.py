"""
Options Flow Analyzer - Unusual Options Activity Detector
Wraps existing options_flow_tracker.py from data_sources/
"""

import logging
from datetime import datetime
from typing import List
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from data_sources.options_flow_tracker import OptionsFlowTracker
from src.data.alternative_data_aggregator import AlternativeDataSignal, SignalType

logger = logging.getLogger(__name__)


class OptionsFlowAnalyzer:
    """
    Adapter to convert options flow data to AlternativeDataSignal format
    """

    def __init__(self):
        """Initialize options flow analyzer"""
        try:
            self.tracker = OptionsFlowTracker()
        except Exception as e:
            logger.warning(f"OptionsFlowTracker not available: {e}")
            self.tracker = None

    def get_signals(self, ticker: str) -> List[AlternativeDataSignal]:
        """
        Get options flow signals for a ticker

        Args:
            ticker: Stock ticker symbol

        Returns:
            List of AlternativeDataSignal objects
        """
        if not self.tracker:
            logger.warning(f"Options flow tracker not available for {ticker}")
            return []

        try:
            # Get options chain data
            options_data = self.tracker.get_options_chain(ticker)

            if not options_data or options_data.empty:
                logger.info(f"No options data found for {ticker}")
                return []

            # Analyze unusual activity
            unusual_activity = self._analyze_unusual_activity(ticker, options_data)

            if not unusual_activity:
                logger.info(f"No unusual options activity for {ticker}")
                return []

            # Convert to AlternativeDataSignal
            signals = []
            for activity in unusual_activity:
                signal = self._create_options_signal(ticker, activity)
                if signal:
                    signals.append(signal)

            logger.info(f"Generated {len(signals)} options signals for {ticker}")
            return signals

        except Exception as e:
            logger.error(f"Error fetching options signals for {ticker}: {e}")
            return []

    def _analyze_unusual_activity(self, ticker: str, options_df) -> List[dict]:
        """
        Analyze options data for unusual activity

        Args:
            ticker: Stock ticker symbol
            options_df: DataFrame with options chain data

        Returns:
            List of unusual activity dictionaries
        """
        unusual_activities = []

        try:
            # Calculate volume to open interest ratio
            options_df['vol_oi_ratio'] = options_df['volume'] / options_df['openInterest'].replace(0, 1)

            # Calculate premium (volume * last price * 100)
            options_df['premium'] = options_df['volume'] * options_df['lastPrice'] * 100

            # Define unusual thresholds
            vol_oi_threshold = 0.25  # Volume > 25% of OI
            premium_threshold = 50000  # $50K+ premium

            # Find unusual activity
            unusual = options_df[
                (options_df['vol_oi_ratio'] > vol_oi_threshold) &
                (options_df['premium'] > premium_threshold)
            ]

            for _, row in unusual.head(5).iterrows():  # Top 5 unusual activities
                activity = {
                    'type': row.get('type', 'UNKNOWN'),
                    'strike': row.get('strike', 0),
                    'expiry': row.get('expiry', ''),
                    'volume': row.get('volume', 0),
                    'openInterest': row.get('openInterest', 0),
                    'premium': row['premium'],
                    'impliedVolatility': row.get('impliedVolatility', 0),
                    'vol_oi_ratio': row['vol_oi_ratio']
                }
                unusual_activities.append(activity)

        except Exception as e:
            logger.error(f"Error analyzing unusual activity for {ticker}: {e}")

        return unusual_activities

    def _create_options_signal(self, ticker: str, activity: dict) -> AlternativeDataSignal:
        """
        Create AlternativeDataSignal from options activity

        Args:
            ticker: Stock ticker symbol
            activity: Dictionary with options activity data

        Returns:
            AlternativeDataSignal object
        """
        option_type = activity.get('type', '').upper()
        premium = activity.get('premium', 0)
        vol_oi_ratio = activity.get('vol_oi_ratio', 0)

        # Determine signal type based on option type
        if option_type == 'CALL':
            signal_type = SignalType.BULLISH
        elif option_type == 'PUT':
            signal_type = SignalType.BEARISH
        else:
            signal_type = SignalType.NEUTRAL

        # Strength based on premium size
        if premium > 500000:
            strength = 95.0
        elif premium > 250000:
            strength = 85.0
        elif premium > 100000:
            strength = 75.0
        else:
            strength = 65.0

        # Confidence based on volume/OI ratio
        if vol_oi_ratio > 1.0:
            confidence = 90.0
        elif vol_oi_ratio > 0.5:
            confidence = 75.0
        elif vol_oi_ratio > 0.25:
            confidence = 60.0
        else:
            confidence = 50.0

        return AlternativeDataSignal(
            ticker=ticker,
            source='options',
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            timestamp=datetime.now(),
            metadata={
                'option_type': option_type,
                'strike': activity.get('strike', 0),
                'expiry': activity.get('expiry', ''),
                'volume': activity.get('volume', 0),
                'openInterest': activity.get('openInterest', 0),
                'premium': premium,
                'impliedVolatility': activity.get('impliedVolatility', 0),
                'vol_oi_ratio': vol_oi_ratio
            }
        )

    def get_put_call_ratio(self, ticker: str) -> float:
        """
        Calculate put/call ratio for a ticker

        Args:
            ticker: Stock ticker symbol

        Returns:
            Put/call ratio (higher = more bearish)
        """
        if not self.tracker:
            return 0.0

        try:
            options_data = self.tracker.get_options_chain(ticker)

            if not options_data or options_data.empty:
                return 0.0

            call_volume = options_data[options_data['type'] == 'CALL']['volume'].sum()
            put_volume = options_data[options_data['type'] == 'PUT']['volume'].sum()

            if call_volume == 0:
                return 999.0 if put_volume > 0 else 0.0

            return put_volume / call_volume

        except Exception as e:
            logger.error(f"Error calculating put/call ratio for {ticker}: {e}")
            return 0.0

    def get_summary(self, ticker: str) -> dict:
        """
        Get summary of options flow activity

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with summary statistics
        """
        signals = self.get_signals(ticker)

        if not signals:
            return {
                'ticker': ticker,
                'unusual_activity_count': 0,
                'net_signal': 'NEUTRAL',
                'avg_confidence': 0.0,
                'put_call_ratio': 0.0
            }

        call_count = sum(1 for s in signals if s.signal_type == SignalType.BULLISH)
        put_count = sum(1 for s in signals if s.signal_type == SignalType.BEARISH)

        if call_count > put_count:
            net_signal = 'BULLISH'
        elif put_count > call_count:
            net_signal = 'BEARISH'
        else:
            net_signal = 'NEUTRAL'

        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        put_call_ratio = self.get_put_call_ratio(ticker)

        return {
            'ticker': ticker,
            'unusual_activity_count': len(signals),
            'call_count': call_count,
            'put_count': put_count,
            'net_signal': net_signal,
            'avg_confidence': avg_confidence,
            'put_call_ratio': put_call_ratio
        }
