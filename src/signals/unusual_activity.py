"""
Unusual Options Activity Detector

Identifies unusual options patterns:
- Large block trades (>$100k premium)
- Unusual volume (>3x average daily volume)
- Sweep orders (multi-exchange aggressive orders)
- Multi-leg strategies (spreads, straddles, butterflies)
- Unusual open interest changes
- Smart money indicators

These patterns often precede significant price moves.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import statistics

from src.data.options_data_fetcher import (
    OptionsContract,
    OptionsFlow,
    OptionType,
    TradeType
)

logger = logging.getLogger(__name__)


class ActivityLevel(str):
    """Unusual activity level"""
    EXTREME = "EXTREME"  # >10x normal
    VERY_HIGH = "VERY_HIGH"  # 5-10x normal
    HIGH = "HIGH"  # 3-5x normal
    ELEVATED = "ELEVATED"  # 2-3x normal
    NORMAL = "NORMAL"  # <2x normal


class StrategyType(str):
    """Multi-leg strategy types"""
    CALL_SPREAD = "CALL_SPREAD"  # Bullish/bearish call spread
    PUT_SPREAD = "PUT_SPREAD"  # Bullish/bearish put spread
    STRADDLE = "STRADDLE"  # Long/short straddle
    STRANGLE = "STRANGLE"  # Long/short strangle
    BUTTERFLY = "BUTTERFLY"  # Butterfly spread
    IRON_CONDOR = "IRON_CONDOR"  # Iron condor
    CALENDAR_SPREAD = "CALENDAR_SPREAD"  # Time spread
    DIAGONAL_SPREAD = "DIAGONAL_SPREAD"  # Diagonal spread
    COLLAR = "COLLAR"  # Protective collar
    RATIO_SPREAD = "RATIO_SPREAD"  # Ratio spread


@dataclass
class UnusualTrade:
    """Represents an unusual options trade"""
    flow: OptionsFlow

    # Unusual characteristics
    is_block_trade: bool = False  # >$100k premium
    is_sweep: bool = False  # Multi-exchange sweep
    is_unusual_volume: bool = False  # >3x average
    is_unusual_strike: bool = False  # Strike far from spot
    is_large_oi_change: bool = False  # Large OI delta

    # Context
    volume_multiple: float = 1.0  # Multiple of average volume
    oi_change: int = 0  # Change in open interest
    distance_from_spot_pct: float = 0.0  # % away from spot

    # Smart money indicators
    is_institutional: bool = False  # Likely institutional
    conviction_score: float = 0.0  # 0-1 conviction score

    # Reasoning
    reasoning: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Calculate derived fields"""
        if not self.reasoning:
            self._generate_reasoning()

    def _generate_reasoning(self):
        """Generate reasoning for why this is unusual"""
        if self.is_block_trade:
            self.reasoning.append(
                f"Large block trade: ${self.flow.premium:,.0f} premium"
            )

        if self.is_sweep:
            self.reasoning.append("Multi-exchange sweep order (urgent)")

        if self.is_unusual_volume:
            self.reasoning.append(
                f"Unusual volume: {self.volume_multiple:.1f}x average"
            )

        if self.is_unusual_strike:
            self.reasoning.append(
                f"Unusual strike: {abs(self.distance_from_spot_pct):.1%} "
                f"{'OTM' if self.distance_from_spot_pct > 0 else 'ITM'}"
            )

        if self.is_large_oi_change:
            self.reasoning.append(
                f"Large OI change: {self.oi_change:+,} contracts"
            )


@dataclass
class MultiLegStrategy:
    """Detected multi-leg options strategy"""
    ticker: str
    strategy_type: StrategyType
    timestamp: datetime

    # Legs
    legs: List[OptionsFlow]

    # Strategy details
    net_premium: float  # Total premium (positive = debit, negative = credit)
    net_delta: float  # Net delta exposure
    max_profit: Optional[float] = None
    max_loss: Optional[float] = None
    breakeven: Optional[float] = None

    # Sentiment
    sentiment: str = "NEUTRAL"  # BULLISH, BEARISH, NEUTRAL
    confidence: float = 0.0  # 0-1

    # Reasoning
    reasoning: str = ""

    def __post_init__(self):
        """Determine sentiment and generate reasoning"""
        if not self.sentiment or self.sentiment == "NEUTRAL":
            self._determine_sentiment()

        if not self.reasoning:
            self._generate_reasoning()

    def _determine_sentiment(self):
        """Determine bullish/bearish sentiment from strategy"""
        if self.strategy_type in [StrategyType.CALL_SPREAD]:
            # Debit call spread = bullish, credit call spread = bearish
            self.sentiment = "BULLISH" if self.net_premium > 0 else "BEARISH"
        elif self.strategy_type in [StrategyType.PUT_SPREAD]:
            # Debit put spread = bearish, credit put spread = bullish
            self.sentiment = "BEARISH" if self.net_premium > 0 else "BULLISH"
        elif self.strategy_type in [StrategyType.STRADDLE, StrategyType.STRANGLE]:
            # Long straddle/strangle = expecting volatility
            self.sentiment = "VOLATILE" if self.net_premium > 0 else "NEUTRAL"
        else:
            self.sentiment = "NEUTRAL"

    def _generate_reasoning(self):
        """Generate human-readable reasoning"""
        self.reasoning = (
            f"{self.strategy_type} detected with {len(self.legs)} legs. "
            f"Net premium: ${abs(self.net_premium):,.0f} "
            f"({'debit' if self.net_premium > 0 else 'credit'}). "
            f"Net delta: {self.net_delta:,.0f}. "
            f"Sentiment: {self.sentiment}"
        )


class UnusualActivityDetector:
    """
    Detects unusual options activity patterns

    Features:
    - Large block trade detection (>$100k)
    - Unusual volume detection (>3x average)
    - Sweep order identification
    - Multi-leg strategy detection
    - Open interest change monitoring
    - Smart money indicators
    """

    def __init__(
        self,
        block_trade_threshold: float = 100000,  # $100k
        unusual_volume_multiplier: float = 3.0,  # 3x average
        unusual_strike_threshold: float = 0.05,  # 5% OTM/ITM
        large_oi_change_threshold: int = 500  # 500 contracts
    ):
        """
        Initialize unusual activity detector

        Args:
            block_trade_threshold: Minimum premium for block trade
            unusual_volume_multiplier: Multiple of average for unusual
            unusual_strike_threshold: % distance from spot for unusual
            large_oi_change_threshold: Minimum OI change for unusual
        """
        self.block_threshold = block_trade_threshold
        self.volume_multiplier = unusual_volume_multiplier
        self.strike_threshold = unusual_strike_threshold
        self.oi_threshold = large_oi_change_threshold

        # Historical data
        self.historical_volumes: Dict[str, Dict[float, List[int]]] = defaultdict(
            lambda: defaultdict(list)
        )
        self.previous_oi: Dict[str, Dict[float, int]] = defaultdict(dict)

        logger.info(
            f"UnusualActivityDetector initialized "
            f"(block=${block_trade_threshold:,.0f}, volume={unusual_volume_multiplier}x)"
        )

    def detect_unusual_trades(
        self,
        ticker: str,
        flows: List[OptionsFlow],
        chain: List[OptionsContract],
        spot_price: float
    ) -> List[UnusualTrade]:
        """
        Detect unusual trades from flow data

        Args:
            ticker: Stock ticker
            flows: Recent options flow
            chain: Current options chain
            spot_price: Current stock price

        Returns:
            List of UnusualTrade objects
        """
        unusual_trades = []

        for flow in flows:
            unusual = UnusualTrade(flow=flow)

            # Check block trade
            if flow.premium >= self.block_threshold:
                unusual.is_block_trade = True

            # Check sweep
            if flow.is_sweep or flow.trade_type == TradeType.SWEEP:
                unusual.is_sweep = True

            # Check unusual volume
            avg_volume = self._get_average_volume(
                ticker, flow.contract.strike, flow.contract.option_type
            )
            if avg_volume > 0:
                unusual.volume_multiple = flow.size / avg_volume
                if unusual.volume_multiple >= self.volume_multiplier:
                    unusual.is_unusual_volume = True

            # Check unusual strike
            if spot_price > 0:
                distance_pct = (flow.contract.strike - spot_price) / spot_price
                unusual.distance_from_spot_pct = distance_pct

                if abs(distance_pct) >= self.strike_threshold:
                    unusual.is_unusual_strike = True

            # Check OI change
            oi_change = self._get_oi_change(ticker, flow.contract)
            unusual.oi_change = oi_change
            if abs(oi_change) >= self.oi_threshold:
                unusual.is_large_oi_change = True

            # Calculate conviction score
            unusual.conviction_score = self._calculate_conviction_score(unusual)

            # Check if institutional
            unusual.is_institutional = self._is_likely_institutional(unusual)

            # Add if truly unusual
            if any([
                unusual.is_block_trade,
                unusual.is_sweep,
                unusual.is_unusual_volume,
                unusual.is_unusual_strike,
                unusual.is_large_oi_change
            ]):
                unusual_trades.append(unusual)

        logger.info(f"Detected {len(unusual_trades)} unusual trades for {ticker}")
        return unusual_trades

    def detect_multi_leg_strategies(
        self,
        ticker: str,
        flows: List[OptionsFlow],
        time_window_seconds: int = 60
    ) -> List[MultiLegStrategy]:
        """
        Detect multi-leg options strategies from flow

        Args:
            ticker: Stock ticker
            flows: Recent options flow
            time_window_seconds: Time window to group legs

        Returns:
            List of MultiLegStrategy objects
        """
        strategies = []

        # Group flows by time window
        time_groups = self._group_by_time(flows, time_window_seconds)

        for group in time_groups:
            # Detect vertical spreads (same exp, different strikes)
            spreads = self._detect_vertical_spreads(ticker, group)
            strategies.extend(spreads)

            # Detect straddles/strangles (same exp, same strike or different)
            volatility_plays = self._detect_volatility_plays(ticker, group)
            strategies.extend(volatility_plays)

            # Detect calendar spreads (different exp, same strike)
            calendar_spreads = self._detect_calendar_spreads(ticker, group)
            strategies.extend(calendar_spreads)

        logger.info(f"Detected {len(strategies)} multi-leg strategies for {ticker}")
        return strategies

    def get_activity_level(
        self,
        ticker: str,
        flows: List[OptionsFlow],
        chain: List[OptionsContract]
    ) -> ActivityLevel:
        """
        Get overall unusual activity level for ticker

        Args:
            ticker: Stock ticker
            flows: Recent options flow
            chain: Current options chain

        Returns:
            ActivityLevel enum
        """
        # Calculate total volume
        total_volume = sum(f.size for f in flows)

        # Get historical average
        all_strikes = set([f.contract.strike for f in flows])
        avg_volumes = []

        for strike in all_strikes:
            for opt_type in [OptionType.CALL, OptionType.PUT]:
                avg_vol = self._get_average_volume(ticker, strike, opt_type)
                if avg_vol > 0:
                    avg_volumes.append(avg_vol)

        if not avg_volumes:
            return ActivityLevel.NORMAL

        avg_total = sum(avg_volumes)

        if avg_total == 0:
            return ActivityLevel.NORMAL

        # Calculate multiple
        multiple = total_volume / avg_total

        # Classify
        if multiple >= 10:
            return ActivityLevel.EXTREME
        elif multiple >= 5:
            return ActivityLevel.VERY_HIGH
        elif multiple >= 3:
            return ActivityLevel.HIGH
        elif multiple >= 2:
            return ActivityLevel.ELEVATED
        else:
            return ActivityLevel.NORMAL

    def _get_average_volume(
        self,
        ticker: str,
        strike: float,
        option_type: OptionType
    ) -> float:
        """Get historical average volume for strike"""
        key = f"{strike}_{option_type.value}"

        if ticker in self.historical_volumes and key in self.historical_volumes[ticker]:
            volumes = self.historical_volumes[ticker][key]
            if volumes:
                return statistics.mean(volumes)

        return 0.0

    def update_historical_volume(
        self,
        ticker: str,
        contract: OptionsContract
    ):
        """Update historical volume data"""
        key = f"{contract.strike}_{contract.option_type.value}"
        self.historical_volumes[ticker][key].append(contract.volume)

        # Keep last 30 days
        if len(self.historical_volumes[ticker][key]) > 30:
            self.historical_volumes[ticker][key].pop(0)

    def _get_oi_change(self, ticker: str, contract: OptionsContract) -> int:
        """Calculate change in open interest"""
        key = f"{contract.strike}_{contract.option_type.value}_{contract.expiration}"

        previous = self.previous_oi[ticker].get(key, contract.open_interest)
        change = contract.open_interest - previous

        # Update previous
        self.previous_oi[ticker][key] = contract.open_interest

        return change

    def _calculate_conviction_score(self, unusual: UnusualTrade) -> float:
        """Calculate conviction score (0-1) for unusual trade"""
        score = 0.0

        # Block trade adds conviction
        if unusual.is_block_trade:
            score += 0.3

        # Sweep adds high conviction (urgent order)
        if unusual.is_sweep:
            score += 0.4

        # Unusual volume adds conviction
        if unusual.is_unusual_volume:
            score += min(unusual.volume_multiple / 10.0, 0.3)

        # Large OI change adds conviction
        if unusual.is_large_oi_change:
            score += 0.2

        return min(score, 1.0)

    def _is_likely_institutional(self, unusual: UnusualTrade) -> bool:
        """Determine if trade is likely institutional"""
        # Large block trades are usually institutional
        if unusual.flow.premium >= 500000:  # $500k+
            return True

        # Sweeps are often institutional
        if unusual.is_sweep:
            return True

        # Large size + unusual strike combo
        if unusual.is_unusual_volume and unusual.is_unusual_strike:
            return True

        return False

    def _group_by_time(
        self,
        flows: List[OptionsFlow],
        window_seconds: int
    ) -> List[List[OptionsFlow]]:
        """Group flows by time window"""
        if not flows:
            return []

        # Sort by timestamp
        sorted_flows = sorted(flows, key=lambda f: f.timestamp)

        groups = []
        current_group = [sorted_flows[0]]

        for flow in sorted_flows[1:]:
            time_diff = (flow.timestamp - current_group[0].timestamp).total_seconds()

            if time_diff <= window_seconds:
                current_group.append(flow)
            else:
                groups.append(current_group)
                current_group = [flow]

        if current_group:
            groups.append(current_group)

        return groups

    def _detect_vertical_spreads(
        self,
        ticker: str,
        flows: List[OptionsFlow]
    ) -> List[MultiLegStrategy]:
        """Detect vertical spreads (call/put spreads)"""
        strategies = []

        # Group by option type and expiration
        by_type_exp = defaultdict(list)

        for flow in flows:
            key = f"{flow.contract.option_type.value}_{flow.contract.expiration}"
            by_type_exp[key].append(flow)

        # Look for pairs with different strikes
        for key, group in by_type_exp.items():
            if len(group) >= 2:
                # Sort by strike
                group.sort(key=lambda f: f.contract.strike)

                # Check for spread (buy low strike, sell high strike or vice versa)
                for i in range(len(group) - 1):
                    flow1 = group[i]
                    flow2 = group[i + 1]

                    # Check if opposite sides
                    if flow1.side != flow2.side:
                        opt_type = flow1.contract.option_type
                        strategy_type = (
                            StrategyType.CALL_SPREAD if opt_type == OptionType.CALL
                            else StrategyType.PUT_SPREAD
                        )

                        net_premium = (
                            flow1.premium if flow1.side == "BUY" else -flow1.premium
                        ) + (
                            flow2.premium if flow2.side == "BUY" else -flow2.premium
                        )

                        net_delta = (
                            (flow1.contract.delta or 0) * flow1.size +
                            (flow2.contract.delta or 0) * flow2.size
                        )

                        strategies.append(MultiLegStrategy(
                            ticker=ticker,
                            strategy_type=strategy_type,
                            timestamp=flow1.timestamp,
                            legs=[flow1, flow2],
                            net_premium=net_premium,
                            net_delta=net_delta
                        ))

        return strategies

    def _detect_volatility_plays(
        self,
        ticker: str,
        flows: List[OptionsFlow]
    ) -> List[MultiLegStrategy]:
        """Detect straddles and strangles"""
        strategies = []

        # Group by expiration
        by_exp = defaultdict(list)

        for flow in flows:
            by_exp[flow.contract.expiration].append(flow)

        for exp, group in by_exp.items():
            # Look for call + put combinations
            calls = [f for f in group if f.contract.option_type == OptionType.CALL]
            puts = [f for f in group if f.contract.option_type == OptionType.PUT]

            if calls and puts:
                # Check for straddle (same strike)
                for call in calls:
                    for put in puts:
                        if call.contract.strike == put.contract.strike:
                            # Same strike = straddle
                            if call.side == put.side:  # Both buy or both sell
                                net_premium = call.premium + put.premium
                                if call.side == "SELL":
                                    net_premium = -net_premium

                                strategies.append(MultiLegStrategy(
                                    ticker=ticker,
                                    strategy_type=StrategyType.STRADDLE,
                                    timestamp=call.timestamp,
                                    legs=[call, put],
                                    net_premium=net_premium,
                                    net_delta=0  # Straddles are delta-neutral
                                ))

                        elif abs(call.contract.strike - put.contract.strike) <= 5:
                            # Close strikes = strangle
                            if call.side == put.side:
                                net_premium = call.premium + put.premium
                                if call.side == "SELL":
                                    net_premium = -net_premium

                                strategies.append(MultiLegStrategy(
                                    ticker=ticker,
                                    strategy_type=StrategyType.STRANGLE,
                                    timestamp=call.timestamp,
                                    legs=[call, put],
                                    net_premium=net_premium,
                                    net_delta=0  # Strangles are delta-neutral
                                ))

        return strategies

    def _detect_calendar_spreads(
        self,
        ticker: str,
        flows: List[OptionsFlow]
    ) -> List[MultiLegStrategy]:
        """Detect calendar spreads (different expirations, same strike)"""
        strategies = []

        # Group by option type and strike
        by_type_strike = defaultdict(list)

        for flow in flows:
            key = f"{flow.contract.option_type.value}_{flow.contract.strike}"
            by_type_strike[key].append(flow)

        # Look for different expirations
        for key, group in by_type_strike.items():
            if len(group) >= 2:
                # Sort by expiration
                group.sort(key=lambda f: f.contract.expiration)

                # Check for calendar spread
                for i in range(len(group) - 1):
                    flow1 = group[i]
                    flow2 = group[i + 1]

                    if flow1.side != flow2.side:
                        net_premium = (
                            flow1.premium if flow1.side == "BUY" else -flow1.premium
                        ) + (
                            flow2.premium if flow2.side == "BUY" else -flow2.premium
                        )

                        strategies.append(MultiLegStrategy(
                            ticker=ticker,
                            strategy_type=StrategyType.CALENDAR_SPREAD,
                            timestamp=flow1.timestamp,
                            legs=[flow1, flow2],
                            net_premium=net_premium,
                            net_delta=0  # Simplified
                        ))

        return strategies
