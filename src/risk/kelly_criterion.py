"""
Kelly Criterion Position Sizing
Calculates optimal position sizes based on edge and risk/reward
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class PositionSizeRecommendation:
    """Position sizing recommendation"""
    ticker: str
    kelly_pct: float  # Full Kelly percentage
    fractional_kelly_pct: float  # Conservative Kelly (25-50% of full)
    recommended_pct: float  # Final recommendation after limits
    recommended_shares: int  # Number of shares to buy
    recommended_dollar_amount: float  # Dollar amount to invest

    # Inputs
    win_probability: float
    avg_win: float
    avg_loss: float
    confidence: float
    volatility: float
    current_price: float
    portfolio_value: float

    # Limits applied
    max_position_limit: float
    max_portfolio_exposure: float
    volatility_adjustment: float

    # Reasoning
    reasoning: str


@dataclass
class KellyParameters:
    """Parameters for Kelly calculation"""
    win_rate: float  # Historical win rate (0-1)
    avg_win_pct: float  # Average win as percentage (e.g., 0.15 for 15%)
    avg_loss_pct: float  # Average loss as percentage (e.g., 0.08 for 8%)
    confidence: float = 0.7  # Confidence in the setup (0-1)
    volatility: float = 0.3  # Stock volatility (annualized std dev)

    def __post_init__(self):
        """Validate parameters"""
        if not (0 <= self.win_rate <= 1):
            raise ValueError(f"win_rate must be between 0 and 1, got {self.win_rate}")
        if self.avg_win_pct <= 0:
            raise ValueError(f"avg_win_pct must be positive, got {self.avg_win_pct}")
        if self.avg_loss_pct <= 0:
            raise ValueError(f"avg_loss_pct must be positive, got {self.avg_loss_pct}")
        if not (0 <= self.confidence <= 1):
            raise ValueError(f"confidence must be between 0 and 1, got {self.confidence}")
        if self.volatility < 0:
            raise ValueError(f"volatility must be non-negative, got {self.volatility}")


class KellyPositionSizer:
    """Calculate optimal position sizes using Kelly Criterion"""

    def __init__(
        self,
        max_position_pct: float = 0.10,  # Max 10% per position
        max_portfolio_exposure: float = 0.60,  # Max 60% total exposure
        kelly_fraction: float = 0.25,  # Use 25% of Kelly (conservative)
        min_position_pct: float = 0.01,  # Minimum 1% position
        volatility_scaling: bool = True,  # Scale by volatility
        confidence_scaling: bool = True  # Scale by confidence
    ):
        """
        Initialize Kelly position sizer

        Args:
            max_position_pct: Maximum position size as % of portfolio
            max_portfolio_exposure: Maximum total portfolio exposure
            kelly_fraction: Fraction of Kelly to use (0.25 = 25% of Kelly)
            min_position_pct: Minimum position size
            volatility_scaling: Whether to scale by volatility
            confidence_scaling: Whether to scale by confidence
        """
        self.max_position_pct = max_position_pct
        self.max_portfolio_exposure = max_portfolio_exposure
        self.kelly_fraction = kelly_fraction
        self.min_position_pct = min_position_pct
        self.volatility_scaling = volatility_scaling
        self.confidence_scaling = confidence_scaling

        logger.info(
            f"Initialized KellyPositionSizer: max_position={max_position_pct:.1%}, "
            f"max_exposure={max_portfolio_exposure:.1%}, kelly_fraction={kelly_fraction:.1%}"
        )

    def calculate_kelly_pct(
        self,
        win_rate: float,
        avg_win_pct: float,
        avg_loss_pct: float
    ) -> float:
        """
        Calculate Kelly percentage

        Kelly% = (Win% × AvgWin - Loss% × AvgLoss) / AvgWin

        Args:
            win_rate: Historical win rate (0-1)
            avg_win_pct: Average win as percentage
            avg_loss_pct: Average loss as percentage

        Returns:
            Kelly percentage (can be negative if no edge)
        """
        loss_rate = 1 - win_rate

        kelly = (win_rate * avg_win_pct - loss_rate * avg_loss_pct) / avg_win_pct

        logger.debug(
            f"Kelly calculation: win_rate={win_rate:.2%}, avg_win={avg_win_pct:.2%}, "
            f"avg_loss={avg_loss_pct:.2%}, kelly={kelly:.2%}"
        )

        return kelly

    def calculate_volatility_adjustment(self, volatility: float) -> float:
        """
        Calculate volatility adjustment factor

        Higher volatility = smaller position
        Adjustment = 1 / (1 + volatility)

        Args:
            volatility: Annualized volatility (e.g., 0.3 for 30%)

        Returns:
            Adjustment factor (0-1)
        """
        if not self.volatility_scaling:
            return 1.0

        # Scale down by volatility
        adjustment = 1 / (1 + volatility)

        logger.debug(f"Volatility adjustment: vol={volatility:.2%}, adjustment={adjustment:.2%}")

        return adjustment

    def calculate_confidence_adjustment(self, confidence: float) -> float:
        """
        Calculate confidence adjustment factor

        Lower confidence = smaller position

        Args:
            confidence: Confidence in setup (0-1)

        Returns:
            Adjustment factor (0-1)
        """
        if not self.confidence_scaling:
            return 1.0

        # Use confidence directly as scaling factor
        adjustment = confidence

        logger.debug(f"Confidence adjustment: confidence={confidence:.2%}, adjustment={adjustment:.2%}")

        return adjustment

    def calculate_position_size(
        self,
        ticker: str,
        params: KellyParameters,
        current_price: float,
        portfolio_value: float,
        current_exposure_pct: float = 0.0
    ) -> PositionSizeRecommendation:
        """
        Calculate recommended position size

        Args:
            ticker: Stock ticker
            params: Kelly parameters
            current_price: Current stock price
            portfolio_value: Total portfolio value
            current_exposure_pct: Current portfolio exposure (0-1)

        Returns:
            PositionSizeRecommendation
        """
        # Calculate full Kelly
        kelly_pct = self.calculate_kelly_pct(
            params.win_rate,
            params.avg_win_pct,
            params.avg_loss_pct
        )

        # If Kelly is negative or zero, no edge exists
        if kelly_pct <= 0:
            return self._create_no_position_recommendation(
                ticker, kelly_pct, params, current_price, portfolio_value,
                "No positive edge detected (Kelly ≤ 0)"
            )

        # Apply Kelly fraction (conservative approach)
        fractional_kelly = kelly_pct * self.kelly_fraction

        # Apply volatility adjustment
        vol_adjustment = self.calculate_volatility_adjustment(params.volatility)

        # Apply confidence adjustment
        conf_adjustment = self.calculate_confidence_adjustment(params.confidence)

        # Calculate adjusted position size
        adjusted_pct = fractional_kelly * vol_adjustment * conf_adjustment

        # Apply maximum position limit
        recommended_pct = min(adjusted_pct, self.max_position_pct)

        # Check if we would exceed max portfolio exposure
        if current_exposure_pct + recommended_pct > self.max_portfolio_exposure:
            available_exposure = self.max_portfolio_exposure - current_exposure_pct
            if available_exposure <= 0:
                return self._create_no_position_recommendation(
                    ticker, kelly_pct, params, current_price, portfolio_value,
                    f"Portfolio exposure limit reached ({current_exposure_pct:.1%} / {self.max_portfolio_exposure:.1%})"
                )
            recommended_pct = available_exposure

        # Check minimum position size
        if recommended_pct < self.min_position_pct:
            return self._create_no_position_recommendation(
                ticker, kelly_pct, params, current_price, portfolio_value,
                f"Position size below minimum ({recommended_pct:.2%} < {self.min_position_pct:.2%})"
            )

        # Calculate dollar amount and shares
        dollar_amount = portfolio_value * recommended_pct
        shares = int(dollar_amount / current_price)
        actual_dollar_amount = shares * current_price
        actual_pct = actual_dollar_amount / portfolio_value

        # Generate reasoning
        reasoning = self._generate_reasoning(
            kelly_pct, fractional_kelly, vol_adjustment, conf_adjustment,
            adjusted_pct, recommended_pct, params
        )

        return PositionSizeRecommendation(
            ticker=ticker,
            kelly_pct=kelly_pct,
            fractional_kelly_pct=fractional_kelly,
            recommended_pct=actual_pct,
            recommended_shares=shares,
            recommended_dollar_amount=actual_dollar_amount,
            win_probability=params.win_rate,
            avg_win=params.avg_win_pct,
            avg_loss=params.avg_loss_pct,
            confidence=params.confidence,
            volatility=params.volatility,
            current_price=current_price,
            portfolio_value=portfolio_value,
            max_position_limit=self.max_position_pct,
            max_portfolio_exposure=self.max_portfolio_exposure,
            volatility_adjustment=vol_adjustment,
            reasoning=reasoning
        )

    def _create_no_position_recommendation(
        self,
        ticker: str,
        kelly_pct: float,
        params: KellyParameters,
        current_price: float,
        portfolio_value: float,
        reason: str
    ) -> PositionSizeRecommendation:
        """Create recommendation for no position"""
        return PositionSizeRecommendation(
            ticker=ticker,
            kelly_pct=kelly_pct,
            fractional_kelly_pct=0.0,
            recommended_pct=0.0,
            recommended_shares=0,
            recommended_dollar_amount=0.0,
            win_probability=params.win_rate,
            avg_win=params.avg_win_pct,
            avg_loss=params.avg_loss_pct,
            confidence=params.confidence,
            volatility=params.volatility,
            current_price=current_price,
            portfolio_value=portfolio_value,
            max_position_limit=self.max_position_pct,
            max_portfolio_exposure=self.max_portfolio_exposure,
            volatility_adjustment=1.0,
            reasoning=f"No position recommended: {reason}"
        )

    def _generate_reasoning(
        self,
        kelly_pct: float,
        fractional_kelly: float,
        vol_adjustment: float,
        conf_adjustment: float,
        adjusted_pct: float,
        recommended_pct: float,
        params: KellyParameters
    ) -> str:
        """Generate detailed reasoning for position size"""
        reasoning_parts = []

        # Kelly calculation
        reasoning_parts.append(
            f"Full Kelly: {kelly_pct:.2%} (Win rate: {params.win_rate:.1%}, "
            f"Avg win: {params.avg_win_pct:.1%}, Avg loss: {params.avg_loss_pct:.1%})"
        )

        # Kelly fraction
        reasoning_parts.append(
            f"Fractional Kelly ({self.kelly_fraction:.0%}): {fractional_kelly:.2%}"
        )

        # Adjustments
        if self.volatility_scaling:
            reasoning_parts.append(
                f"Volatility adjustment: ×{vol_adjustment:.2f} (volatility: {params.volatility:.1%})"
            )

        if self.confidence_scaling:
            reasoning_parts.append(
                f"Confidence adjustment: ×{conf_adjustment:.2f} (confidence: {params.confidence:.1%})"
            )

        # Adjusted size
        reasoning_parts.append(f"Adjusted size: {adjusted_pct:.2%}")

        # Limits
        if recommended_pct < adjusted_pct:
            reasoning_parts.append(
                f"Limited to {recommended_pct:.2%} (max position: {self.max_position_pct:.1%})"
            )

        return " | ".join(reasoning_parts)

    def calculate_batch_sizes(
        self,
        opportunities: List[Dict],
        portfolio_value: float,
        current_exposure_pct: float = 0.0
    ) -> List[PositionSizeRecommendation]:
        """
        Calculate position sizes for multiple opportunities

        Accounts for portfolio exposure limits across all positions

        Args:
            opportunities: List of dicts with keys:
                - ticker: str
                - params: KellyParameters
                - current_price: float
            portfolio_value: Total portfolio value
            current_exposure_pct: Current portfolio exposure

        Returns:
            List of PositionSizeRecommendation sorted by recommended size
        """
        recommendations = []
        running_exposure = current_exposure_pct

        # Sort by Kelly percentage (descending) to prioritize best opportunities
        opportunities_sorted = sorted(
            opportunities,
            key=lambda x: self.calculate_kelly_pct(
                x['params'].win_rate,
                x['params'].avg_win_pct,
                x['params'].avg_loss_pct
            ),
            reverse=True
        )

        for opp in opportunities_sorted:
            rec = self.calculate_position_size(
                ticker=opp['ticker'],
                params=opp['params'],
                current_price=opp['current_price'],
                portfolio_value=portfolio_value,
                current_exposure_pct=running_exposure
            )

            recommendations.append(rec)
            running_exposure += rec.recommended_pct

            logger.info(
                f"{rec.ticker}: Recommended {rec.recommended_pct:.2%} "
                f"({rec.recommended_shares} shares @ ${rec.current_price:.2f})"
            )

        return recommendations

    def generate_report(
        self,
        recommendations: List[PositionSizeRecommendation]
    ) -> str:
        """
        Generate markdown report of position sizing recommendations

        Args:
            recommendations: List of position size recommendations

        Returns:
            Markdown formatted report
        """
        report = "# Position Sizing Recommendations (Kelly Criterion)\n\n"

        # Summary
        total_recommended = sum(r.recommended_pct for r in recommendations)
        total_dollar = sum(r.recommended_dollar_amount for r in recommendations)
        num_positions = sum(1 for r in recommendations if r.recommended_shares > 0)

        report += f"**Total Positions**: {num_positions}\n"
        report += f"**Total Exposure**: {total_recommended:.2%}\n"
        report += f"**Total Investment**: ${total_dollar:,.2f}\n\n"

        # Individual positions
        report += "## Recommended Positions\n\n"

        for rec in recommendations:
            if rec.recommended_shares == 0:
                continue

            report += f"### {rec.ticker}\n\n"
            report += f"- **Shares**: {rec.recommended_shares}\n"
            report += f"- **Price**: ${rec.current_price:.2f}\n"
            report += f"- **Investment**: ${rec.recommended_dollar_amount:,.2f}\n"
            report += f"- **Position Size**: {rec.recommended_pct:.2%} of portfolio\n"
            report += f"- **Full Kelly**: {rec.kelly_pct:.2%}\n"
            report += f"- **Fractional Kelly**: {rec.fractional_kelly_pct:.2%}\n\n"

            report += f"**Parameters**:\n"
            report += f"- Win Probability: {rec.win_probability:.1%}\n"
            report += f"- Avg Win: {rec.avg_win:.1%}\n"
            report += f"- Avg Loss: {rec.avg_loss:.1%}\n"
            report += f"- Confidence: {rec.confidence:.1%}\n"
            report += f"- Volatility: {rec.volatility:.1%}\n\n"

            report += f"**Reasoning**: {rec.reasoning}\n\n"

        # Rejected positions
        rejected = [r for r in recommendations if r.recommended_shares == 0]
        if rejected:
            report += "## Rejected Positions\n\n"
            for rec in rejected:
                report += f"- **{rec.ticker}**: {rec.reasoning}\n"

        return report


def calculate_historical_kelly_params(
    trades: List[Dict],
    lookback_trades: int = 30
) -> KellyParameters:
    """
    Calculate Kelly parameters from historical trade data

    Args:
        trades: List of trade dicts with keys:
            - return_pct: float
            - win: bool
        lookback_trades: Number of recent trades to analyze

    Returns:
        KellyParameters calculated from historical performance
    """
    if not trades:
        raise ValueError("No trades provided")

    # Use most recent trades
    recent_trades = trades[-lookback_trades:] if len(trades) > lookback_trades else trades

    # Separate wins and losses
    wins = [t['return_pct'] for t in recent_trades if t['win']]
    losses = [abs(t['return_pct']) for t in recent_trades if not t['win']]

    if not wins:
        raise ValueError("No winning trades found")
    if not losses:
        raise ValueError("No losing trades found")

    # Calculate statistics
    win_rate = len(wins) / len(recent_trades)
    avg_win = np.mean(wins)
    avg_loss = np.mean(losses)

    # Calculate volatility
    returns = [t['return_pct'] for t in recent_trades]
    volatility = np.std(returns) * np.sqrt(252)  # Annualized

    # Default confidence based on sample size
    confidence = min(0.9, len(recent_trades) / 100)  # Max 90% confidence

    return KellyParameters(
        win_rate=win_rate,
        avg_win_pct=avg_win,
        avg_loss_pct=avg_loss,
        confidence=confidence,
        volatility=volatility
    )
