"""
Options Flow Analyzer - Main Analysis Engine

Analyzes options flow data to generate trading signals based on:
- Put/Call ratio deviations
- Flow imbalance (calls vs puts in dollar terms)
- Large trader positioning
- Net delta and gamma exposure
- Unusual volume and open interest changes

Generates bullish/bearish signals and daily summary reports.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import statistics

from src.data.loaders.options_data_fetcher import (
    OptionsDataFetcher,
    OptionsContract,
    OptionsFlow,
    OptionType,
    TradeType
)

logger = logging.getLogger(__name__)


class FlowSignal(str):
    """Flow signal enumeration"""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    VERY_BULLISH = "VERY_BULLISH"
    VERY_BEARISH = "VERY_BEARISH"


@dataclass
class PutCallMetrics:
    """Put/Call ratio metrics"""
    ticker: str
    timestamp: datetime

    # Volume metrics
    call_volume: int
    put_volume: int
    volume_ratio: float  # put_volume / call_volume

    # Dollar flow metrics
    call_premium: float
    put_premium: float
    premium_ratio: float  # put_premium / call_premium

    # Open interest metrics
    call_oi: int
    put_oi: int
    oi_ratio: float  # put_oi / call_oi

    # Historical context
    avg_volume_ratio: float = 1.0  # 30-day average
    volume_ratio_deviation: float = 0.0  # Std deviations from average

    def __post_init__(self):
        """Calculate ratios"""
        self.volume_ratio = self.put_volume / self.call_volume if self.call_volume > 0 else 0
        self.premium_ratio = self.put_premium / self.call_premium if self.call_premium > 0 else 0
        self.oi_ratio = self.put_oi / self.call_oi if self.call_oi > 0 else 0


@dataclass
class FlowImbalance:
    """Flow imbalance metrics"""
    ticker: str
    timestamp: datetime

    # Call flow
    call_buys_premium: float
    call_sells_premium: float
    net_call_premium: float  # buys - sells

    # Put flow
    put_buys_premium: float
    put_sells_premium: float
    net_put_premium: float  # buys - sells

    # Net imbalance
    total_imbalance: float  # net_call - net_put (positive = bullish)
    imbalance_ratio: float  # total_imbalance / total_premium

    # Trade counts
    call_buy_count: int = 0
    call_sell_count: int = 0
    put_buy_count: int = 0
    put_sell_count: int = 0

    def __post_init__(self):
        """Calculate derived metrics"""
        self.net_call_premium = self.call_buys_premium - self.call_sells_premium
        self.net_put_premium = self.put_buys_premium - self.put_sells_premium
        self.total_imbalance = self.net_call_premium - self.net_put_premium

        total_premium = (
            self.call_buys_premium + self.call_sells_premium +
            self.put_buys_premium + self.put_sells_premium
        )
        self.imbalance_ratio = self.total_imbalance / total_premium if total_premium > 0 else 0


@dataclass
class DeltaGammaExposure:
    """Net delta and gamma exposure"""
    ticker: str
    timestamp: datetime

    # Delta exposure
    call_delta: float
    put_delta: float
    net_delta: float  # call_delta + put_delta

    # Gamma exposure
    call_gamma: float
    put_gamma: float
    net_gamma: float  # call_gamma + put_gamma

    # Notional exposure (delta * spot * shares)
    spot_price: float
    delta_notional: float  # net_delta * spot * 100

    def __post_init__(self):
        """Calculate net exposure"""
        self.net_delta = self.call_delta + self.put_delta
        self.net_gamma = self.call_gamma + self.put_gamma
        self.delta_notional = self.net_delta * self.spot_price * 100


@dataclass
class OptionsFlowSignal:
    """Complete options flow signal"""
    ticker: str
    timestamp: datetime

    # Overall signal
    signal: FlowSignal
    confidence: float  # 0-1

    # Component signals
    put_call_signal: FlowSignal
    flow_imbalance_signal: FlowSignal
    delta_exposure_signal: FlowSignal
    unusual_activity_signal: FlowSignal

    # Supporting metrics
    put_call_metrics: PutCallMetrics
    flow_imbalance: FlowImbalance
    delta_gamma: DeltaGammaExposure

    # Large trades
    large_trades_count: int
    sweep_orders_count: int
    unusual_strikes: List[float] = field(default_factory=list)

    # Reasoning
    reasoning: str = ""

    def __post_init__(self):
        """Generate reasoning"""
        if not self.reasoning:
            self.reasoning = self._generate_reasoning()

    def _generate_reasoning(self) -> str:
        """Generate human-readable reasoning"""
        reasons = []

        # Put/Call ratio
        if self.put_call_metrics.volume_ratio_deviation > 2:
            reasons.append(
                f"Put/Call ratio {self.put_call_metrics.volume_ratio:.2f} is "
                f"{self.put_call_metrics.volume_ratio_deviation:.1f} std devs above average "
                f"(bearish)"
            )
        elif self.put_call_metrics.volume_ratio_deviation < -2:
            reasons.append(
                f"Put/Call ratio {self.put_call_metrics.volume_ratio:.2f} is unusually low "
                f"(bullish)"
            )

        # Flow imbalance
        if abs(self.flow_imbalance.imbalance_ratio) > 0.3:
            direction = "bullish" if self.flow_imbalance.imbalance_ratio > 0 else "bearish"
            reasons.append(
                f"Strong {direction} flow imbalance: "
                f"${self.flow_imbalance.total_imbalance:,.0f} net {direction}"
            )

        # Delta exposure
        if abs(self.delta_gamma.net_delta) > 1000:
            direction = "bullish" if self.delta_gamma.net_delta > 0 else "bearish"
            reasons.append(
                f"Large {direction} delta exposure: {self.delta_gamma.net_delta:,.0f} "
                f"(${self.delta_gamma.delta_notional:,.0f} notional)"
            )

        # Large trades
        if self.large_trades_count > 0:
            reasons.append(f"{self.large_trades_count} large trades (>$100k premium)")

        # Sweeps
        if self.sweep_orders_count > 0:
            reasons.append(f"{self.sweep_orders_count} sweep orders (urgent flow)")

        return " | ".join(reasons) if reasons else "No significant flow detected"


class OptionsFlowAnalyzer:
    """
    Main options flow analysis engine

    Analyzes options activity to generate trading signals based on:
    - Put/Call ratios
    - Flow imbalance
    - Large trader positioning
    - Delta/gamma exposure
    """

    def __init__(
        self,
        data_fetcher: OptionsDataFetcher,
        lookback_days: int = 30,
        large_trade_threshold: float = 100000,  # $100k
        unusual_volume_multiplier: float = 3.0,  # 3x average
        flow_imbalance_threshold: float = 0.2  # 20% imbalance
    ):
        """
        Initialize options flow analyzer

        Args:
            data_fetcher: OptionsDataFetcher instance
            lookback_days: Days of historical data for averages
            large_trade_threshold: Minimum premium for "large" trade
            unusual_volume_multiplier: Multiple of average for "unusual"
            flow_imbalance_threshold: Threshold for significant imbalance
        """
        self.data_fetcher = data_fetcher
        self.lookback_days = lookback_days
        self.large_trade_threshold = large_trade_threshold
        self.unusual_volume_multiplier = unusual_volume_multiplier
        self.flow_imbalance_threshold = flow_imbalance_threshold

        # Historical data cache
        self.historical_ratios: Dict[str, List[float]] = defaultdict(list)

        logger.info(
            f"OptionsFlowAnalyzer initialized "
            f"(lookback={lookback_days}d, large_trade=${large_trade_threshold:,.0f})"
        )

    async def analyze_ticker(
        self,
        ticker: str,
        minutes_back: int = 60
    ) -> OptionsFlowSignal:
        """
        Analyze options flow for ticker

        Args:
            ticker: Stock ticker symbol
            minutes_back: How many minutes of flow to analyze

        Returns:
            OptionsFlowSignal with complete analysis
        """
        logger.info(f"Analyzing options flow for {ticker}")

        # Fetch options chain
        chain = await self.data_fetcher.fetch_options_chain(ticker)

        # Fetch recent flow
        flows = await self.data_fetcher.fetch_options_flow(ticker, minutes_back)

        # Get spot price
        spot_price = await self.data_fetcher.get_spot_price(ticker)

        # Calculate metrics
        put_call = self._calculate_put_call_metrics(ticker, chain, flows)
        imbalance = self._calculate_flow_imbalance(ticker, flows)
        delta_gamma = self._calculate_delta_gamma_exposure(ticker, chain, spot_price)

        # Detect unusual activity
        large_trades = [f for f in flows if f.is_large_trade]
        sweeps = [f for f in flows if f.is_sweep]
        unusual_strikes = self._detect_unusual_strikes(chain, flows)

        # Generate component signals
        put_call_signal = self._evaluate_put_call_signal(put_call)
        imbalance_signal = self._evaluate_imbalance_signal(imbalance)
        delta_signal = self._evaluate_delta_signal(delta_gamma)
        unusual_signal = self._evaluate_unusual_activity(
            large_trades, sweeps, unusual_strikes
        )

        # Combine signals
        overall_signal, confidence = self._combine_signals(
            put_call_signal,
            imbalance_signal,
            delta_signal,
            unusual_signal
        )

        # Create signal
        signal = OptionsFlowSignal(
            ticker=ticker,
            timestamp=datetime.now(),
            signal=overall_signal,
            confidence=confidence,
            put_call_signal=put_call_signal,
            flow_imbalance_signal=imbalance_signal,
            delta_exposure_signal=delta_signal,
            unusual_activity_signal=unusual_signal,
            put_call_metrics=put_call,
            flow_imbalance=imbalance,
            delta_gamma=delta_gamma,
            large_trades_count=len(large_trades),
            sweep_orders_count=len(sweeps),
            unusual_strikes=unusual_strikes
        )

        logger.info(
            f"{ticker} signal: {signal.signal} "
            f"(confidence={signal.confidence:.2f})"
        )

        return signal

    def _calculate_put_call_metrics(
        self,
        ticker: str,
        chain: List[OptionsContract],
        flows: List[OptionsFlow]
    ) -> PutCallMetrics:
        """Calculate put/call ratio metrics"""
        # Aggregate from chain
        call_volume = sum(c.volume for c in chain if c.option_type == OptionType.CALL)
        put_volume = sum(c.volume for c in chain if c.option_type == OptionType.PUT)

        call_oi = sum(c.open_interest for c in chain if c.option_type == OptionType.CALL)
        put_oi = sum(c.open_interest for c in chain if c.option_type == OptionType.PUT)

        # Aggregate from flows
        call_premium = sum(
            f.premium for f in flows
            if f.contract.option_type == OptionType.CALL
        )
        put_premium = sum(
            f.premium for f in flows
            if f.contract.option_type == OptionType.PUT
        )

        # Calculate current ratio
        volume_ratio = put_volume / call_volume if call_volume > 0 else 0

        # Get historical average
        if ticker in self.historical_ratios and len(self.historical_ratios[ticker]) > 0:
            avg_ratio = statistics.mean(self.historical_ratios[ticker])
            std_ratio = statistics.stdev(self.historical_ratios[ticker]) if len(self.historical_ratios[ticker]) > 1 else 0
            deviation = (volume_ratio - avg_ratio) / std_ratio if std_ratio > 0 else 0
        else:
            avg_ratio = 1.0
            deviation = 0.0

        # Update historical
        self.historical_ratios[ticker].append(volume_ratio)
        if len(self.historical_ratios[ticker]) > self.lookback_days:
            self.historical_ratios[ticker].pop(0)

        return PutCallMetrics(
            ticker=ticker,
            timestamp=datetime.now(),
            call_volume=call_volume,
            put_volume=put_volume,
            volume_ratio=volume_ratio,
            call_premium=call_premium,
            put_premium=put_premium,
            premium_ratio=0,  # Calculated in __post_init__
            call_oi=call_oi,
            put_oi=put_oi,
            oi_ratio=0,  # Calculated in __post_init__
            avg_volume_ratio=avg_ratio,
            volume_ratio_deviation=deviation
        )

    def _calculate_flow_imbalance(
        self,
        ticker: str,
        flows: List[OptionsFlow]
    ) -> FlowImbalance:
        """Calculate flow imbalance (buys vs sells)"""
        call_buys = sum(
            f.premium for f in flows
            if f.contract.option_type == OptionType.CALL and f.side == "BUY"
        )
        call_sells = sum(
            f.premium for f in flows
            if f.contract.option_type == OptionType.CALL and f.side == "SELL"
        )

        put_buys = sum(
            f.premium for f in flows
            if f.contract.option_type == OptionType.PUT and f.side == "BUY"
        )
        put_sells = sum(
            f.premium for f in flows
            if f.contract.option_type == OptionType.PUT and f.side == "SELL"
        )

        # Count trades
        call_buy_count = len([
            f for f in flows
            if f.contract.option_type == OptionType.CALL and f.side == "BUY"
        ])
        call_sell_count = len([
            f for f in flows
            if f.contract.option_type == OptionType.CALL and f.side == "SELL"
        ])
        put_buy_count = len([
            f for f in flows
            if f.contract.option_type == OptionType.PUT and f.side == "BUY"
        ])
        put_sell_count = len([
            f for f in flows
            if f.contract.option_type == OptionType.PUT and f.side == "SELL"
        ])

        return FlowImbalance(
            ticker=ticker,
            timestamp=datetime.now(),
            call_buys_premium=call_buys,
            call_sells_premium=call_sells,
            net_call_premium=0,  # Calculated in __post_init__
            put_buys_premium=put_buys,
            put_sells_premium=put_sells,
            net_put_premium=0,  # Calculated in __post_init__
            total_imbalance=0,  # Calculated in __post_init__
            imbalance_ratio=0,  # Calculated in __post_init__
            call_buy_count=call_buy_count,
            call_sell_count=call_sell_count,
            put_buy_count=put_buy_count,
            put_sell_count=put_sell_count
        )

    def _calculate_delta_gamma_exposure(
        self,
        ticker: str,
        chain: List[OptionsContract],
        spot_price: float
    ) -> DeltaGammaExposure:
        """Calculate net delta and gamma exposure"""
        call_delta = sum(
            (c.delta or 0) * c.open_interest
            for c in chain
            if c.option_type == OptionType.CALL
        )

        put_delta = sum(
            (c.delta or 0) * c.open_interest
            for c in chain
            if c.option_type == OptionType.PUT
        )

        call_gamma = sum(
            (c.gamma or 0) * c.open_interest
            for c in chain
            if c.option_type == OptionType.CALL
        )

        put_gamma = sum(
            (c.gamma or 0) * c.open_interest
            for c in chain
            if c.option_type == OptionType.PUT
        )

        return DeltaGammaExposure(
            ticker=ticker,
            timestamp=datetime.now(),
            call_delta=call_delta,
            put_delta=put_delta,
            net_delta=0,  # Calculated in __post_init__
            call_gamma=call_gamma,
            put_gamma=put_gamma,
            net_gamma=0,  # Calculated in __post_init__
            spot_price=spot_price,
            delta_notional=0  # Calculated in __post_init__
        )

    def _detect_unusual_strikes(
        self,
        chain: List[OptionsContract],
        flows: List[OptionsFlow]
    ) -> List[float]:
        """Detect strikes with unusual activity"""
        unusual = []

        # Group flows by strike
        strike_activity = defaultdict(lambda: {'volume': 0, 'premium': 0})

        for flow in flows:
            strike = flow.contract.strike
            strike_activity[strike]['volume'] += flow.size
            strike_activity[strike]['premium'] += flow.premium

        # Find strikes with >3x normal volume
        for strike, activity in strike_activity.items():
            # Find corresponding contract in chain
            contracts = [c for c in chain if c.strike == strike]
            if not contracts:
                continue

            avg_volume = statistics.mean([c.volume for c in contracts])

            if activity['volume'] > avg_volume * self.unusual_volume_multiplier:
                unusual.append(strike)

        return sorted(unusual)

    def _evaluate_put_call_signal(self, metrics: PutCallMetrics) -> FlowSignal:
        """Evaluate put/call ratio signal"""
        # High deviation = bearish (more puts than normal)
        # Low deviation = bullish (fewer puts than normal)

        if metrics.volume_ratio_deviation > 2:
            return FlowSignal.BEARISH
        elif metrics.volume_ratio_deviation > 1:
            return FlowSignal.NEUTRAL
        elif metrics.volume_ratio_deviation < -2:
            return FlowSignal.BULLISH
        elif metrics.volume_ratio_deviation < -1:
            return FlowSignal.NEUTRAL
        else:
            return FlowSignal.NEUTRAL

    def _evaluate_imbalance_signal(self, imbalance: FlowImbalance) -> FlowSignal:
        """Evaluate flow imbalance signal"""
        ratio = imbalance.imbalance_ratio

        if ratio > 0.4:
            return FlowSignal.VERY_BULLISH
        elif ratio > 0.2:
            return FlowSignal.BULLISH
        elif ratio < -0.4:
            return FlowSignal.VERY_BEARISH
        elif ratio < -0.2:
            return FlowSignal.BEARISH
        else:
            return FlowSignal.NEUTRAL

    def _evaluate_delta_signal(self, delta_gamma: DeltaGammaExposure) -> FlowSignal:
        """Evaluate delta exposure signal"""
        # Positive delta = bullish, negative delta = bearish

        if delta_gamma.net_delta > 5000:
            return FlowSignal.VERY_BULLISH
        elif delta_gamma.net_delta > 1000:
            return FlowSignal.BULLISH
        elif delta_gamma.net_delta < -5000:
            return FlowSignal.VERY_BEARISH
        elif delta_gamma.net_delta < -1000:
            return FlowSignal.BEARISH
        else:
            return FlowSignal.NEUTRAL

    def _evaluate_unusual_activity(
        self,
        large_trades: List[OptionsFlow],
        sweeps: List[OptionsFlow],
        unusual_strikes: List[float]
    ) -> FlowSignal:
        """Evaluate unusual activity signal"""
        # Count bullish vs bearish large trades
        bullish_count = len([t for t in large_trades if t.sentiment == "BULLISH"])
        bearish_count = len([t for t in large_trades if t.sentiment == "BEARISH"])

        # Sweeps are more important (urgent)
        bullish_sweeps = len([s for s in sweeps if s.sentiment == "BULLISH"])
        bearish_sweeps = len([s for s in sweeps if s.sentiment == "BEARISH"])

        # Weight sweeps 2x
        total_bullish = bullish_count + (bullish_sweeps * 2)
        total_bearish = bearish_count + (bearish_sweeps * 2)

        if total_bullish > total_bearish * 2:
            return FlowSignal.BULLISH
        elif total_bearish > total_bullish * 2:
            return FlowSignal.BEARISH
        else:
            return FlowSignal.NEUTRAL

    def _combine_signals(
        self,
        put_call: FlowSignal,
        imbalance: FlowSignal,
        delta: FlowSignal,
        unusual: FlowSignal
    ) -> Tuple[FlowSignal, float]:
        """
        Combine component signals into overall signal

        Returns:
            Tuple of (overall signal, confidence)
        """
        # Score each signal
        signal_scores = {
            FlowSignal.VERY_BULLISH: 2,
            FlowSignal.BULLISH: 1,
            FlowSignal.NEUTRAL: 0,
            FlowSignal.BEARISH: -1,
            FlowSignal.VERY_BEARISH: -2
        }

        # Weighted combination
        weights = {
            'put_call': 0.2,
            'imbalance': 0.4,
            'delta': 0.3,
            'unusual': 0.1
        }

        combined_score = (
            signal_scores[put_call] * weights['put_call'] +
            signal_scores[imbalance] * weights['imbalance'] +
            signal_scores[delta] * weights['delta'] +
            signal_scores[unusual] * weights['unusual']
        )

        # Map score to signal
        if combined_score >= 1.5:
            signal = FlowSignal.VERY_BULLISH
        elif combined_score >= 0.5:
            signal = FlowSignal.BULLISH
        elif combined_score <= -1.5:
            signal = FlowSignal.VERY_BEARISH
        elif combined_score <= -0.5:
            signal = FlowSignal.BEARISH
        else:
            signal = FlowSignal.NEUTRAL

        # Calculate confidence (0-1)
        confidence = min(abs(combined_score) / 2.0, 1.0)

        return signal, confidence

    async def generate_daily_summary(
        self,
        tickers: List[str],
        minutes_back: int = 390  # Full trading day
    ) -> str:
        """
        Generate daily options flow summary report

        Args:
            tickers: List of tickers to analyze
            minutes_back: How many minutes to analyze

        Returns:
            Markdown-formatted summary report
        """
        logger.info(f"Generating daily summary for {len(tickers)} tickers")

        signals = []
        for ticker in tickers:
            try:
                signal = await self.analyze_ticker(ticker, minutes_back)
                signals.append(signal)
            except Exception as e:
                logger.error(f"Error analyzing {ticker}: {e}")

        # Sort by confidence
        signals.sort(key=lambda s: s.confidence, reverse=True)

        # Generate report
        report = [
            "# Options Flow Daily Summary",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Period**: Last {minutes_back} minutes",
            "",
            "## Strong Signals (Confidence > 0.7)",
            ""
        ]

        strong_signals = [s for s in signals if s.confidence > 0.7]
        if strong_signals:
            for signal in strong_signals:
                report.append(f"### {signal.ticker} - {signal.signal} ({signal.confidence:.1%} confidence)")
                report.append(f"**Reasoning**: {signal.reasoning}")
                report.append(f"- Put/Call Ratio: {signal.put_call_metrics.volume_ratio:.2f}")
                report.append(f"- Flow Imbalance: ${signal.flow_imbalance.total_imbalance:,.0f}")
                report.append(f"- Net Delta: {signal.delta_gamma.net_delta:,.0f}")
                report.append(f"- Large Trades: {signal.large_trades_count}")
                report.append(f"- Sweep Orders: {signal.sweep_orders_count}")
                report.append("")
        else:
            report.append("*No strong signals detected*")
            report.append("")

        # Summary statistics
        report.append("## Summary Statistics")
        report.append("")
        report.append(f"- Total Tickers Analyzed: {len(tickers)}")
        report.append(f"- Bullish Signals: {len([s for s in signals if 'BULLISH' in s.signal])}")
        report.append(f"- Bearish Signals: {len([s for s in signals if 'BEARISH' in s.signal])}")
        report.append(f"- Neutral Signals: {len([s for s in signals if s.signal == FlowSignal.NEUTRAL])}")
        report.append(f"- Average Confidence: {statistics.mean([s.confidence for s in signals]):.1%}")
        report.append("")

        # Top movers
        report.append("## All Signals")
        report.append("")
        report.append("| Ticker | Signal | Confidence | P/C Ratio | Flow Imbalance | Large Trades |")
        report.append("|--------|--------|------------|-----------|----------------|--------------|")

        for signal in signals:
            report.append(
                f"| {signal.ticker} | {signal.signal} | {signal.confidence:.1%} | "
                f"{signal.put_call_metrics.volume_ratio:.2f} | "
                f"${signal.flow_imbalance.total_imbalance:,.0f} | "
                f"{signal.large_trades_count} |"
            )

        return "\n".join(report)
