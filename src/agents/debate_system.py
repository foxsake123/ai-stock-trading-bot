"""
Bull/Bear Debate System
Structured debate mechanism where bull and bear agents argue for/against trades
A judge agent evaluates the arguments and adjusts confidence scores
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Argument:
    """Represents a single argument in the debate"""
    position: str  # BULL or BEAR
    point: str  # The argument being made
    evidence: List[str]  # Supporting evidence
    strength: float  # Strength score (0-1)
    rebuttal_to: Optional[str] = None  # Which argument this rebuts


@dataclass
class DebateResult:
    """Result of a bull/bear debate"""
    ticker: str
    bull_score: float
    bear_score: float
    winner: str  # BULL, BEAR, or TIE
    confidence_adjustment: float  # -0.10 to +0.10
    bull_arguments: List[Argument]
    bear_arguments: List[Argument]
    judge_reasoning: str
    debate_summary: str


class DebateSystem:
    """Manages bull vs bear debates for trade validation"""

    def __init__(self, bull_agent=None, bear_agent=None):
        """
        Initialize debate system

        Args:
            bull_agent: Bull researcher agent
            bear_agent: Bear researcher agent
        """
        self.bull_agent = bull_agent
        self.bear_agent = bear_agent

        # Debate parameters
        self.max_rounds = 3
        self.min_confidence_for_debate = 0.55  # Only debate borderline trades
        self.max_confidence_for_debate = 0.75

    def should_debate(self, initial_confidence: float) -> bool:
        """
        Determine if a trade should go through debate

        Args:
            initial_confidence: Initial consensus confidence

        Returns:
            True if confidence is in debate range
        """
        return (self.min_confidence_for_debate <= initial_confidence
                <= self.max_confidence_for_debate)

    def conduct_debate(
        self,
        ticker: str,
        initial_recommendation: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> DebateResult:
        """
        Conduct full debate between bull and bear agents

        Args:
            ticker: Stock ticker
            initial_recommendation: Initial trade recommendation
            market_data: Current market data

        Returns:
            DebateResult with winner and confidence adjustment
        """
        logger.info(f"Starting debate for {ticker}")

        # Collect arguments from both sides
        bull_arguments = self._gather_bull_arguments(
            ticker, initial_recommendation, market_data
        )
        bear_arguments = self._gather_bear_arguments(
            ticker, initial_recommendation, market_data
        )

        # Conduct rounds of rebuttals
        for round_num in range(self.max_rounds):
            logger.debug(f"Debate round {round_num + 1}")

            # Bear rebuts bull arguments
            bear_rebuttals = self._generate_rebuttals(
                bear_arguments, bull_arguments, "BEAR"
            )
            bear_arguments.extend(bear_rebuttals)

            # Bull rebuts bear arguments
            bull_rebuttals = self._generate_rebuttals(
                bull_arguments, bear_arguments, "BULL"
            )
            bull_arguments.extend(bull_rebuttals)

        # Judge evaluates all arguments
        bull_score, bear_score = self._judge_arguments(
            bull_arguments, bear_arguments
        )

        # Determine winner and confidence adjustment
        winner, confidence_adjustment = self._determine_winner(
            bull_score, bear_score, initial_recommendation
        )

        # Generate reasoning and summary
        judge_reasoning = self._generate_judge_reasoning(
            bull_score, bear_score, bull_arguments, bear_arguments
        )
        debate_summary = self._generate_debate_summary(
            ticker, winner, confidence_adjustment, bull_score, bear_score
        )

        return DebateResult(
            ticker=ticker,
            bull_score=bull_score,
            bear_score=bear_score,
            winner=winner,
            confidence_adjustment=confidence_adjustment,
            bull_arguments=bull_arguments,
            bear_arguments=bear_arguments,
            judge_reasoning=judge_reasoning,
            debate_summary=debate_summary
        )

    def _gather_bull_arguments(
        self,
        ticker: str,
        recommendation: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> List[Argument]:
        """Gather initial bull arguments"""
        arguments = []

        # Extract bullish factors from recommendation
        analysis = recommendation.get('analysis', {})

        # Technical bullish arguments
        if analysis.get('technical_score', 0) > 0.6:
            arguments.append(Argument(
                position="BULL",
                point="Strong technical setup",
                evidence=[
                    f"Technical score: {analysis.get('technical_score', 0):.2f}",
                    "Price above key support levels"
                ],
                strength=0.7
            ))

        # Fundamental bullish arguments
        if analysis.get('fundamental_score', 0) > 0.6:
            arguments.append(Argument(
                position="BULL",
                point="Solid fundamentals",
                evidence=[
                    f"Fundamental score: {analysis.get('fundamental_score', 0):.2f}",
                    "Strong balance sheet and earnings"
                ],
                strength=0.8
            ))

        # Sentiment bullish arguments
        if analysis.get('sentiment_score', 0) > 0.6:
            arguments.append(Argument(
                position="BULL",
                point="Positive sentiment",
                evidence=[
                    f"Sentiment score: {analysis.get('sentiment_score', 0):.2f}",
                    "Market optimism"
                ],
                strength=0.6
            ))

        # Default argument if none found
        if not arguments:
            arguments.append(Argument(
                position="BULL",
                point="Positive risk/reward",
                evidence=["Favorable entry price"],
                strength=0.5
            ))

        return arguments

    def _gather_bear_arguments(
        self,
        ticker: str,
        recommendation: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> List[Argument]:
        """Gather initial bear arguments"""
        arguments = []

        analysis = recommendation.get('analysis', {})
        risk_assessment = recommendation.get('risk_assessment', {})

        # Risk-based bear arguments
        risk_level = risk_assessment.get('risk_level', 'MEDIUM')
        if risk_level in ['HIGH', 'EXTREME']:
            arguments.append(Argument(
                position="BEAR",
                point=f"{risk_level} risk level",
                evidence=[
                    f"Risk assessment: {risk_level}",
                    "Significant downside potential"
                ],
                strength=0.8
            ))

        # Valuation bear arguments
        if analysis.get('valuation_score', 0) < 0.4:
            arguments.append(Argument(
                position="BEAR",
                point="Overvalued",
                evidence=[
                    f"Valuation score: {analysis.get('valuation_score', 0):.2f}",
                    "Price above fair value"
                ],
                strength=0.7
            ))

        # Technical bear arguments
        if analysis.get('technical_score', 0) < 0.4:
            arguments.append(Argument(
                position="BEAR",
                point="Weak technical setup",
                evidence=[
                    f"Technical score: {analysis.get('technical_score', 0):.2f}",
                    "Price below key resistance"
                ],
                strength=0.6
            ))

        # Default bear argument
        if not arguments:
            arguments.append(Argument(
                position="BEAR",
                point="Market uncertainty",
                evidence=["General market volatility"],
                strength=0.5
            ))

        return arguments

    def _generate_rebuttals(
        self,
        own_arguments: List[Argument],
        opponent_arguments: List[Argument],
        position: str
    ) -> List[Argument]:
        """Generate rebuttals to opponent's arguments"""
        rebuttals = []

        # Rebut strongest opponent arguments
        sorted_opponent = sorted(
            opponent_arguments,
            key=lambda a: a.strength,
            reverse=True
        )

        for arg in sorted_opponent[:2]:  # Rebut top 2 arguments
            rebuttal = self._create_rebuttal(arg, position)
            if rebuttal:
                rebuttals.append(rebuttal)

        return rebuttals

    def _create_rebuttal(self, argument: Argument, position: str) -> Optional[Argument]:
        """Create a rebuttal to a specific argument"""

        if position == "BULL":
            # Bull rebuts bear arguments
            if "risk" in argument.point.lower():
                return Argument(
                    position="BULL",
                    point="Risk is manageable with stops",
                    evidence=["Stop loss protection in place", "Position sizing accounts for risk"],
                    strength=0.6,
                    rebuttal_to=argument.point
                )
            elif "overvalued" in argument.point.lower():
                return Argument(
                    position="BULL",
                    point="Growth justifies valuation",
                    evidence=["Strong growth prospects", "Premium warranted"],
                    strength=0.5,
                    rebuttal_to=argument.point
                )

        else:  # BEAR
            # Bear rebuts bull arguments
            if "technical" in argument.point.lower():
                return Argument(
                    position="BEAR",
                    point="Technicals can reverse quickly",
                    evidence=["Overbought conditions", "Divergences present"],
                    strength=0.5,
                    rebuttal_to=argument.point
                )
            elif "fundamental" in argument.point.lower():
                return Argument(
                    position="BEAR",
                    point="Fundamentals already priced in",
                    evidence=["Market efficiency", "No new catalysts"],
                    strength=0.6,
                    rebuttal_to=argument.point
                )

        return None

    def _judge_arguments(
        self,
        bull_arguments: List[Argument],
        bear_arguments: List[Argument]
    ) -> Tuple[float, float]:
        """
        Judge evaluates all arguments and assigns scores

        Returns:
            (bull_score, bear_score) both 0-1
        """
        # Calculate bull score
        bull_score = 0.0
        for arg in bull_arguments:
            bull_score += arg.strength
            # Bonus for rebuttals
            if arg.rebuttal_to:
                bull_score += 0.1

        # Calculate bear score
        bear_score = 0.0
        for arg in bear_arguments:
            bear_score += arg.strength
            # Bonus for rebuttals
            if arg.rebuttal_to:
                bear_score += 0.1

        # Normalize scores
        total = bull_score + bear_score
        if total > 0:
            bull_score = bull_score / total
            bear_score = bear_score / total
        else:
            bull_score = 0.5
            bear_score = 0.5

        return bull_score, bear_score

    def _determine_winner(
        self,
        bull_score: float,
        bear_score: float,
        initial_recommendation: Dict[str, Any]
    ) -> Tuple[str, float]:
        """
        Determine debate winner and confidence adjustment

        Returns:
            (winner, confidence_adjustment)
        """
        score_diff = abs(bull_score - bear_score)

        # Determine winner
        if bull_score > bear_score + 0.1:  # Clear bull win
            winner = "BULL"
        elif bear_score > bull_score + 0.1:  # Clear bear win
            winner = "BEAR"
        else:
            winner = "TIE"

        # Calculate confidence adjustment (-0.10 to +0.10)
        action = initial_recommendation.get('recommendation', {}).get('action', 'HOLD')

        if winner == "BULL":
            if action in ["BUY", "LONG"]:
                # Bull wins and we're buying - increase confidence
                confidence_adjustment = min(0.10, score_diff * 0.20)
            else:
                # Bull wins but we're not buying - decrease confidence
                confidence_adjustment = -min(0.10, score_diff * 0.20)

        elif winner == "BEAR":
            if action in ["SELL", "SHORT", "HOLD"]:
                # Bear wins and we're not buying - increase confidence
                confidence_adjustment = min(0.10, score_diff * 0.20)
            else:
                # Bear wins but we're buying - decrease confidence
                confidence_adjustment = -min(0.10, score_diff * 0.20)

        else:  # TIE
            # Tie - slight decrease in confidence (uncertainty)
            confidence_adjustment = -0.03

        return winner, confidence_adjustment

    def _generate_judge_reasoning(
        self,
        bull_score: float,
        bear_score: float,
        bull_arguments: List[Argument],
        bear_arguments: List[Argument]
    ) -> str:
        """Generate judge's reasoning"""
        reasoning = []

        reasoning.append(f"Bull score: {bull_score:.2f}, Bear score: {bear_score:.2f}")

        # Strongest bull argument
        if bull_arguments:
            strongest_bull = max(bull_arguments, key=lambda a: a.strength)
            reasoning.append(f"Strongest bull case: {strongest_bull.point}")

        # Strongest bear argument
        if bear_arguments:
            strongest_bear = max(bear_arguments, key=lambda a: a.strength)
            reasoning.append(f"Strongest bear case: {strongest_bear.point}")

        # Conclusion
        if bull_score > bear_score:
            reasoning.append("Bull case is more compelling")
        elif bear_score > bull_score:
            reasoning.append("Bear case is more compelling")
        else:
            reasoning.append("Arguments are evenly balanced")

        return ". ".join(reasoning)

    def _generate_debate_summary(
        self,
        ticker: str,
        winner: str,
        confidence_adjustment: float,
        bull_score: float,
        bear_score: float
    ) -> str:
        """Generate human-readable debate summary"""
        summary = f"Debate for {ticker}: "

        if winner == "BULL":
            summary += f"Bull wins ({bull_score:.0%} vs {bear_score:.0%}). "
        elif winner == "BEAR":
            summary += f"Bear wins ({bear_score:.0%} vs {bull_score:.0%}). "
        else:
            summary += f"Tie ({bull_score:.0%} vs {bear_score:.0%}). "

        summary += f"Confidence adjusted by {confidence_adjustment:+.1%}"

        return summary


def debate_trade(
    ticker: str,
    recommendation: Dict[str, Any],
    market_data: Dict[str, Any],
    bull_agent=None,
    bear_agent=None
) -> DebateResult:
    """
    Convenience function to debate a trade

    Args:
        ticker: Stock ticker
        recommendation: Trade recommendation
        market_data: Market data
        bull_agent: Optional bull agent
        bear_agent: Optional bear agent

    Returns:
        DebateResult
    """
    debate = DebateSystem(bull_agent, bear_agent)
    return debate.conduct_debate(ticker, recommendation, market_data)
