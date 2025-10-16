"""
Alternative Data Consolidator
Combines multiple alternative data sources into unified signals
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConsolidatedSignal:
    """Consolidated alternative data signal"""
    ticker: str
    timestamp: datetime

    # Component scores (0-1 scale)
    insider_score: float
    trends_score: float
    options_score: float

    # Weighted composite
    composite_score: float
    composite_signal: str  # BULLISH, BEARISH, NEUTRAL

    # Confidence and strength
    confidence: float  # How confident in the signal (0-1)
    strength: str  # STRONG, MODERATE, WEAK

    # Contributing factors
    bullish_factors: List[str]
    bearish_factors: List[str]

    # Detailed breakdown
    breakdown: Dict[str, Any]


@dataclass
class DataSourceStatus:
    """Status of alternative data sources"""
    insider_available: bool
    trends_available: bool
    options_available: bool
    sources_active: int
    sources_total: int


class AlternativeDataConsolidator:
    """Consolidates multiple alternative data sources into unified signals"""

    def __init__(
        self,
        insider_monitor=None,
        trends_monitor=None,
        options_analyzer=None,
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize alternative data consolidator

        Args:
            insider_monitor: InsiderMonitor instance
            trends_monitor: GoogleTrendsMonitor instance
            options_analyzer: OptionsFlowAnalyzer instance (optional)
            weights: Custom source weights (default: equal weighting)
        """
        self.insider_monitor = insider_monitor
        self.trends_monitor = trends_monitor
        self.options_analyzer = options_analyzer

        # Default weights (can be adjusted based on historical accuracy)
        self.weights = weights or {
            'insider': 0.40,  # Insider trading most predictive
            'trends': 0.30,   # Retail sentiment moderate
            'options': 0.30   # Options flow moderate
        }

        # Normalize weights to sum to 1.0
        total = sum(self.weights.values())
        self.weights = {k: v/total for k, v in self.weights.items()}

        # Signal thresholds
        self.bullish_threshold = 0.60
        self.bearish_threshold = 0.40
        self.strong_threshold = 0.75
        self.weak_threshold = 0.55

    def get_source_status(self) -> DataSourceStatus:
        """
        Get status of all data sources

        Returns:
            DataSourceStatus with availability info
        """
        insider_available = self.insider_monitor is not None
        trends_available = self.trends_monitor is not None
        options_available = self.options_analyzer is not None

        sources_active = sum([
            insider_available,
            trends_available,
            options_available
        ])

        return DataSourceStatus(
            insider_available=insider_available,
            trends_available=trends_available,
            options_available=options_available,
            sources_active=sources_active,
            sources_total=3
        )

    def consolidate_signal(
        self,
        ticker: str,
        insider_data: Optional[Dict[str, Any]] = None,
        trends_data: Optional[Dict[str, Any]] = None,
        options_data: Optional[Dict[str, Any]] = None
    ) -> ConsolidatedSignal:
        """
        Consolidate signals from multiple sources

        Args:
            ticker: Stock ticker
            insider_data: Insider trading data (from InsiderMonitor)
            trends_data: Google Trends data (from GoogleTrendsMonitor)
            options_data: Options flow data (from OptionsFlowAnalyzer)

        Returns:
            ConsolidatedSignal with unified score and signal
        """
        # Calculate individual scores
        insider_score = self._calculate_insider_score(insider_data)
        trends_score = self._calculate_trends_score(trends_data)
        options_score = self._calculate_options_score(options_data)

        # Calculate weighted composite
        composite_score = (
            insider_score * self.weights['insider'] +
            trends_score * self.weights['trends'] +
            options_score * self.weights['options']
        )

        # Determine signal
        composite_signal = self._determine_signal(composite_score)

        # Calculate confidence (based on source agreement)
        confidence = self._calculate_confidence(
            insider_score, trends_score, options_score
        )

        # Determine strength
        strength = self._determine_strength(composite_score, confidence)

        # Identify contributing factors
        bullish_factors, bearish_factors = self._identify_factors(
            insider_data, trends_data, options_data
        )

        # Create detailed breakdown
        breakdown = {
            'insider': {
                'score': insider_score,
                'weight': self.weights['insider'],
                'contribution': insider_score * self.weights['insider'],
                'available': insider_data is not None
            },
            'trends': {
                'score': trends_score,
                'weight': self.weights['trends'],
                'contribution': trends_score * self.weights['trends'],
                'available': trends_data is not None
            },
            'options': {
                'score': options_score,
                'weight': self.weights['options'],
                'contribution': options_score * self.weights['options'],
                'available': options_data is not None
            }
        }

        return ConsolidatedSignal(
            ticker=ticker,
            timestamp=datetime.now(),
            insider_score=insider_score,
            trends_score=trends_score,
            options_score=options_score,
            composite_score=composite_score,
            composite_signal=composite_signal,
            confidence=confidence,
            strength=strength,
            bullish_factors=bullish_factors,
            bearish_factors=bearish_factors,
            breakdown=breakdown
        )

    def _calculate_insider_score(
        self,
        insider_data: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate score from insider trading data

        Returns:
            Score from 0 (bearish) to 1 (bullish), 0.5 = neutral
        """
        if not insider_data:
            return 0.5  # Neutral if no data

        # Extract transactions
        transactions = insider_data.get('transactions', [])
        if not transactions:
            return 0.5

        # Calculate net signal
        buy_value = sum(
            t.get('value', 0) for t in transactions
            if t.get('transaction_type') == 'BUY'
        )
        sell_value = sum(
            t.get('value', 0) for t in transactions
            if t.get('transaction_type') == 'SELL'
        )

        net_value = buy_value - sell_value

        # Normalize to 0-1 scale
        # Strong buy: $2M+ net = 1.0
        # Strong sell: -$2M+ net = 0.0
        # Neutral: $0 net = 0.5
        threshold = 2_000_000

        if net_value > 0:
            # Bullish: 0.5 to 1.0
            score = 0.5 + (0.5 * min(net_value / threshold, 1.0))
        elif net_value < 0:
            # Bearish: 0.0 to 0.5
            score = 0.5 - (0.5 * min(abs(net_value) / threshold, 1.0))
        else:
            score = 0.5

        return score

    def _calculate_trends_score(
        self,
        trends_data: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate score from Google Trends data

        Returns:
            Score from 0 (bearish) to 1 (bullish), 0.5 = neutral
        """
        if not trends_data:
            return 0.5  # Neutral if no data

        # Extract key metrics
        signal = trends_data.get('signal', 'NEUTRAL')
        momentum = trends_data.get('momentum_score', 0.0)
        is_breakout = trends_data.get('is_breakout', False)
        current_interest = trends_data.get('current_interest', 50)

        # Base score from signal
        if signal == 'BULLISH':
            base_score = 0.65
        elif signal == 'BEARISH':
            base_score = 0.35
        else:
            base_score = 0.5

        # Adjust for momentum (-1.0 to 1.0)
        momentum_adjustment = momentum * 0.15  # Max ±0.15

        # Boost for breakout
        breakout_boost = 0.10 if is_breakout else 0.0

        # Penalize very low interest
        interest_penalty = -0.10 if current_interest < 10 else 0.0

        score = base_score + momentum_adjustment + breakout_boost + interest_penalty

        # Clamp to 0-1
        return max(0.0, min(1.0, score))

    def _calculate_options_score(
        self,
        options_data: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate score from options flow data

        Returns:
            Score from 0 (bearish) to 1 (bullish), 0.5 = neutral
        """
        if not options_data:
            return 0.5  # Neutral if no data

        # Extract key metrics
        signal = options_data.get('signal', 'NEUTRAL')
        sentiment = options_data.get('sentiment', 0.0)  # -1 to 1
        put_call_ratio = options_data.get('put_call_ratio', 1.0)

        # Base score from signal
        if signal == 'BULLISH':
            base_score = 0.65
        elif signal == 'BEARISH':
            base_score = 0.35
        else:
            base_score = 0.5

        # Adjust for sentiment
        sentiment_adjustment = sentiment * 0.15  # Max ±0.15

        # Adjust for put/call ratio
        # Low P/C (< 0.7) = bullish, High P/C (> 1.3) = bearish
        if put_call_ratio < 0.7:
            pc_adjustment = 0.10  # Bullish
        elif put_call_ratio > 1.3:
            pc_adjustment = -0.10  # Bearish
        else:
            pc_adjustment = 0.0  # Neutral

        score = base_score + sentiment_adjustment + pc_adjustment

        # Clamp to 0-1
        return max(0.0, min(1.0, score))

    def _determine_signal(self, composite_score: float) -> str:
        """
        Determine signal from composite score

        Args:
            composite_score: Composite score (0-1)

        Returns:
            Signal: BULLISH, BEARISH, or NEUTRAL
        """
        if composite_score >= self.bullish_threshold:
            return 'BULLISH'
        elif composite_score <= self.bearish_threshold:
            return 'BEARISH'
        else:
            return 'NEUTRAL'

    def _calculate_confidence(
        self,
        insider_score: float,
        trends_score: float,
        options_score: float
    ) -> float:
        """
        Calculate confidence based on source agreement

        Args:
            insider_score: Insider score (0-1)
            trends_score: Trends score (0-1)
            options_score: Options score (0-1)

        Returns:
            Confidence (0-1), high when sources agree
        """
        scores = [insider_score, trends_score, options_score]

        # Calculate standard deviation (low = high agreement)
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5

        # Convert std dev to confidence
        # Low std dev (0.0) = high confidence (1.0)
        # High std dev (0.5) = low confidence (0.0)
        max_std_dev = 0.5
        confidence = 1.0 - (std_dev / max_std_dev)

        return max(0.0, min(1.0, confidence))

    def _determine_strength(self, composite_score: float, confidence: float) -> str:
        """
        Determine signal strength

        Args:
            composite_score: Composite score (0-1)
            confidence: Confidence level (0-1)

        Returns:
            Strength: STRONG, MODERATE, or WEAK
        """
        # Distance from neutral (0.5)
        distance = abs(composite_score - 0.5)

        # Combine score distance with confidence
        strength_metric = distance * 2 * confidence  # Scale to 0-1

        if strength_metric >= 0.75:
            return 'STRONG'
        elif strength_metric >= 0.55:
            return 'MODERATE'
        else:
            return 'WEAK'

    def _identify_factors(
        self,
        insider_data: Optional[Dict[str, Any]],
        trends_data: Optional[Dict[str, Any]],
        options_data: Optional[Dict[str, Any]]
    ) -> Tuple[List[str], List[str]]:
        """
        Identify bullish and bearish contributing factors

        Returns:
            (bullish_factors, bearish_factors)
        """
        bullish_factors = []
        bearish_factors = []

        # Insider factors
        if insider_data:
            transactions = insider_data.get('transactions', [])
            buy_count = sum(1 for t in transactions if t.get('transaction_type') == 'BUY')
            sell_count = sum(1 for t in transactions if t.get('transaction_type') == 'SELL')

            if buy_count > sell_count:
                bullish_factors.append(f"Insider buying ({buy_count} buys vs {sell_count} sells)")
            elif sell_count > buy_count:
                bearish_factors.append(f"Insider selling ({sell_count} sells vs {buy_count} buys)")

        # Trends factors
        if trends_data:
            if trends_data.get('is_breakout'):
                bullish_factors.append("Search interest breakout")

            momentum = trends_data.get('momentum_score', 0.0)
            if momentum > 0.3:
                bullish_factors.append(f"Rising search momentum ({momentum:+.0%})")
            elif momentum < -0.3:
                bearish_factors.append(f"Falling search momentum ({momentum:+.0%})")

            interest = trends_data.get('current_interest', 50)
            if interest < 10:
                bearish_factors.append("Very low retail interest")

        # Options factors
        if options_data:
            signal = options_data.get('signal')
            if signal == 'BULLISH':
                bullish_factors.append("Bullish options flow")
            elif signal == 'BEARISH':
                bearish_factors.append("Bearish options flow")

            put_call = options_data.get('put_call_ratio', 1.0)
            if put_call < 0.7:
                bullish_factors.append(f"Low put/call ratio ({put_call:.2f})")
            elif put_call > 1.3:
                bearish_factors.append(f"High put/call ratio ({put_call:.2f})")

        return bullish_factors, bearish_factors

    def generate_report(
        self,
        signals: List[ConsolidatedSignal],
        include_neutral: bool = False
    ) -> str:
        """
        Generate markdown report of consolidated signals

        Args:
            signals: List of ConsolidatedSignal objects
            include_neutral: Include neutral signals in report

        Returns:
            Markdown formatted report
        """
        if not signals:
            return "**No alternative data signals available**\n"

        # Filter signals
        if not include_neutral:
            signals = [s for s in signals if s.composite_signal != 'NEUTRAL']

        if not signals:
            return "**No significant alternative data signals**\n"

        report = "## Alternative Data Consolidated Signals\n\n"

        # Table header
        report += "| Ticker | Signal | Strength | Score | Confidence | Key Factors |\n"
        report += "|--------|--------|----------|-------|------------|-------------|\n"

        # Sort by composite score (best signals first)
        sorted_signals = sorted(
            signals,
            key=lambda s: abs(s.composite_score - 0.5),
            reverse=True
        )

        for signal in sorted_signals:
            # Format signal with indicator
            if signal.composite_signal == 'BULLISH':
                signal_display = "[BUY] BULLISH"
            elif signal.composite_signal == 'BEARISH':
                signal_display = "[SELL] BEARISH"
            else:
                signal_display = "[HOLD] NEUTRAL"

            # Format score
            score_display = f"{signal.composite_score:.2f}"

            # Format confidence
            conf_display = f"{signal.confidence:.0%}"

            # Key factors (top 2)
            if signal.composite_signal == 'BULLISH':
                factors = signal.bullish_factors[:2]
            elif signal.composite_signal == 'BEARISH':
                factors = signal.bearish_factors[:2]
            else:
                factors = []

            factors_display = ", ".join(factors) if factors else "-"

            report += f"| {signal.ticker} | {signal_display} | {signal.strength} | "
            report += f"{score_display} | {conf_display} | {factors_display} |\n"

        # Summary
        bullish = sum(1 for s in signals if s.composite_signal == 'BULLISH')
        bearish = sum(1 for s in signals if s.composite_signal == 'BEARISH')
        neutral = sum(1 for s in signals if s.composite_signal == 'NEUTRAL')

        report += f"\n**Summary**: {len(signals)} tickers analyzed, "
        report += f"{bullish} bullish, {bearish} bearish"
        if include_neutral:
            report += f", {neutral} neutral"
        report += "\n"

        return report


def consolidate_alternative_data(
    tickers: List[str],
    insider_monitor=None,
    trends_monitor=None,
    options_analyzer=None,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Convenience function to consolidate alternative data for multiple tickers

    Args:
        tickers: List of stock tickers
        insider_monitor: InsiderMonitor instance
        trends_monitor: GoogleTrendsMonitor instance
        options_analyzer: OptionsFlowAnalyzer instance (optional)
        weights: Custom source weights

    Returns:
        Dict with 'signals', 'report', and 'summary' keys
    """
    consolidator = AlternativeDataConsolidator(
        insider_monitor,
        trends_monitor,
        options_analyzer,
        weights
    )

    signals = []

    for ticker in tickers:
        try:
            # Fetch data from each source
            insider_data = None
            if insider_monitor:
                try:
                    transactions = insider_monitor.fetch_recent_transactions(ticker, days=30)
                    if transactions:
                        insider_data = {'transactions': [t.__dict__ for t in transactions]}
                except Exception as e:
                    logger.warning(f"Error fetching insider data for {ticker}: {e}")

            trends_data = None
            if trends_monitor:
                try:
                    trend = trends_monitor.analyze_ticker(ticker)
                    if trend:
                        trends_data = {
                            'signal': trend.signal,
                            'momentum_score': trend.momentum_score,
                            'is_breakout': trend.is_breakout,
                            'current_interest': trend.current_interest
                        }
                except Exception as e:
                    logger.warning(f"Error fetching trends data for {ticker}: {e}")

            options_data = None
            if options_analyzer:
                try:
                    options_data = options_analyzer.analyze(ticker)
                except Exception as e:
                    logger.warning(f"Error fetching options data for {ticker}: {e}")

            # Consolidate signal
            signal = consolidator.consolidate_signal(
                ticker,
                insider_data,
                trends_data,
                options_data
            )
            signals.append(signal)

        except Exception as e:
            logger.error(f"Error consolidating data for {ticker}: {e}")

    # Generate report
    report = consolidator.generate_report(signals, include_neutral=False)

    # Summary
    summary = {
        'total_analyzed': len(signals),
        'bullish_signals': sum(1 for s in signals if s.composite_signal == 'BULLISH'),
        'bearish_signals': sum(1 for s in signals if s.composite_signal == 'BEARISH'),
        'neutral_signals': sum(1 for s in signals if s.composite_signal == 'NEUTRAL'),
        'strong_signals': sum(1 for s in signals if s.strength == 'STRONG'),
        'source_status': consolidator.get_source_status().__dict__
    }

    return {
        'signals': signals,
        'report': report,
        'summary': summary
    }
