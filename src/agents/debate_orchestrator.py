"""
Debate Orchestrator - Structured Bull/Bear Debate System
Orchestrates 3-round debates between bull and bear analysts with neutral moderation
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DebatePosition(Enum):
    """Final debate position"""
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


class DebateRound(Enum):
    """Debate round types"""
    OPENING = "opening"
    REBUTTAL = "rebuttal"
    CLOSING = "closing"


@dataclass
class DebateArgument:
    """Single argument in a debate"""
    round_type: DebateRound
    side: str  # 'bull' or 'bear'
    argument: str  # 100-200 words
    data_citations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DebateConclusion:
    """Final conclusion from debate"""
    ticker: str
    final_position: DebatePosition
    confidence: float  # 0-100
    bull_score: float  # 0-100
    bear_score: float  # 0-100
    key_arguments: List[str]
    risk_factors: List[str]
    debate_summary: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DebateHistory:
    """Complete debate history for a ticker"""
    ticker: str
    opening_arguments: Dict[str, DebateArgument]  # {'bull': arg, 'bear': arg}
    rebuttals: Dict[str, DebateArgument]
    closing_arguments: Dict[str, DebateArgument]
    conclusion: DebateConclusion
    duration_seconds: float
    timestamp: datetime = field(default_factory=datetime.now)


class DebateOrchestrator:
    """
    Orchestrates structured bull/bear debates between agents

    Debate Structure:
    - Round 1: Opening Arguments (bull and bear present initial cases)
    - Round 2: Rebuttals (each side responds to opponent's arguments)
    - Round 3: Closing Arguments (final statements and key points)
    - Moderation: Neutral moderator evaluates and reaches conclusion
    """

    def __init__(
        self,
        bull_analyst,
        bear_analyst,
        neutral_moderator,
        timeout_seconds: int = 30
    ):
        """
        Initialize debate orchestrator

        Args:
            bull_analyst: BullAnalyst instance
            bear_analyst: BearAnalyst instance
            neutral_moderator: NeutralModerator instance
            timeout_seconds: Maximum debate duration (default: 30s)
        """
        self.bull_analyst = bull_analyst
        self.bear_analyst = bear_analyst
        self.moderator = neutral_moderator
        self.timeout_seconds = timeout_seconds
        self.debate_history: Dict[str, List[DebateHistory]] = {}

        logger.info(f"DebateOrchestrator initialized with {timeout_seconds}s timeout")

    async def conduct_debate(
        self,
        ticker: str,
        market_data: Dict,
        fundamental_data: Dict,
        technical_data: Dict,
        alternative_data: Dict = None
    ) -> DebateConclusion:
        """
        Conduct full 3-round debate for a ticker

        Args:
            ticker: Stock ticker symbol
            market_data: Current market data
            fundamental_data: Fundamental analysis data
            technical_data: Technical analysis data
            alternative_data: Alternative data signals (optional)

        Returns:
            DebateConclusion with final position and confidence
        """
        start_time = datetime.now()
        logger.info(f"Starting debate for {ticker}")

        try:
            # Run debate with timeout
            debate_result = await asyncio.wait_for(
                self._run_debate_rounds(
                    ticker,
                    market_data,
                    fundamental_data,
                    technical_data,
                    alternative_data
                ),
                timeout=self.timeout_seconds
            )

            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Debate for {ticker} completed in {duration:.2f}s")

            # Store in history
            self._store_debate_history(debate_result, duration)

            return debate_result.conclusion

        except asyncio.TimeoutError:
            logger.error(f"Debate for {ticker} exceeded {self.timeout_seconds}s timeout")
            return self._create_timeout_conclusion(ticker)
        except Exception as e:
            logger.error(f"Error in debate for {ticker}: {e}")
            return self._create_error_conclusion(ticker, str(e))

    async def _run_debate_rounds(
        self,
        ticker: str,
        market_data: Dict,
        fundamental_data: Dict,
        technical_data: Dict,
        alternative_data: Dict = None
    ) -> DebateHistory:
        """
        Run all three debate rounds

        Returns:
            Complete DebateHistory object
        """
        # Prepare debate context
        debate_context = {
            'ticker': ticker,
            'market_data': market_data,
            'fundamental_data': fundamental_data,
            'technical_data': technical_data,
            'alternative_data': alternative_data or {}
        }

        # Round 1: Opening Arguments (parallel)
        logger.info(f"{ticker}: Round 1 - Opening Arguments")
        opening_bull, opening_bear = await asyncio.gather(
            self.bull_analyst.generate_opening_argument(debate_context),
            self.bear_analyst.generate_opening_argument(debate_context)
        )

        opening_arguments = {
            'bull': opening_bull,
            'bear': opening_bear
        }

        # Round 2: Rebuttals (sequential - each responds to opponent)
        logger.info(f"{ticker}: Round 2 - Rebuttals")
        rebuttal_bull = await self.bull_analyst.generate_rebuttal(
            debate_context,
            opponent_argument=opening_bear
        )
        rebuttal_bear = await self.bear_analyst.generate_rebuttal(
            debate_context,
            opponent_argument=opening_bull
        )

        rebuttals = {
            'bull': rebuttal_bull,
            'bear': rebuttal_bear
        }

        # Round 3: Closing Arguments (parallel)
        logger.info(f"{ticker}: Round 3 - Closing Arguments")
        closing_bull, closing_bear = await asyncio.gather(
            self.bull_analyst.generate_closing_argument(
                debate_context,
                previous_arguments=[opening_bull, rebuttal_bull],
                opponent_arguments=[opening_bear, rebuttal_bear]
            ),
            self.bear_analyst.generate_closing_argument(
                debate_context,
                previous_arguments=[opening_bear, rebuttal_bear],
                opponent_arguments=[opening_bull, rebuttal_bull]
            )
        )

        closing_arguments = {
            'bull': closing_bull,
            'bear': closing_bear
        }

        # Moderation: Evaluate debate and reach conclusion
        logger.info(f"{ticker}: Moderator evaluating debate")
        conclusion = await self.moderator.evaluate_debate(
            ticker=ticker,
            opening_arguments=opening_arguments,
            rebuttals=rebuttals,
            closing_arguments=closing_arguments,
            market_data=market_data,
            fundamental_data=fundamental_data,
            technical_data=technical_data,
            alternative_data=alternative_data
        )

        # Create debate history
        debate_history = DebateHistory(
            ticker=ticker,
            opening_arguments=opening_arguments,
            rebuttals=rebuttals,
            closing_arguments=closing_arguments,
            conclusion=conclusion,
            duration_seconds=0  # Will be set by caller
        )

        return debate_history

    def _store_debate_history(self, debate: DebateHistory, duration: float):
        """Store debate history for later analysis"""
        debate.duration_seconds = duration

        if debate.ticker not in self.debate_history:
            self.debate_history[debate.ticker] = []

        self.debate_history[debate.ticker].append(debate)
        logger.info(f"Stored debate history for {debate.ticker} ({len(self.debate_history[debate.ticker])} total debates)")

    def _create_timeout_conclusion(self, ticker: str) -> DebateConclusion:
        """Create conclusion when debate times out"""
        return DebateConclusion(
            ticker=ticker,
            final_position=DebatePosition.NEUTRAL,
            confidence=0.0,
            bull_score=50.0,
            bear_score=50.0,
            key_arguments=["Debate timed out - no conclusion reached"],
            risk_factors=["Insufficient time for analysis"],
            debate_summary=f"Debate for {ticker} exceeded time limit"
        )

    def _create_error_conclusion(self, ticker: str, error: str) -> DebateConclusion:
        """Create conclusion when debate encounters error"""
        return DebateConclusion(
            ticker=ticker,
            final_position=DebatePosition.NEUTRAL,
            confidence=0.0,
            bull_score=50.0,
            bear_score=50.0,
            key_arguments=[f"Debate error: {error}"],
            risk_factors=["Unable to complete analysis"],
            debate_summary=f"Debate for {ticker} encountered error: {error}"
        )

    def get_debate_history(self, ticker: str) -> List[DebateHistory]:
        """Get all debate history for a ticker"""
        return self.debate_history.get(ticker, [])

    def get_latest_debate(self, ticker: str) -> Optional[DebateHistory]:
        """Get most recent debate for a ticker"""
        history = self.get_debate_history(ticker)
        return history[-1] if history else None

    def generate_debate_report(self, debate: DebateHistory) -> str:
        """
        Generate formatted report showing both sides of the debate

        Args:
            debate: DebateHistory object

        Returns:
            Formatted markdown report
        """
        report = f"# Debate Report: {debate.ticker}\n\n"
        report += f"**Date**: {debate.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"**Duration**: {debate.duration_seconds:.2f}s\n\n"

        report += "---\n\n"

        # Round 1: Opening Arguments
        report += "## Round 1: Opening Arguments\n\n"

        report += "### 🐂 Bull Case\n\n"
        bull_opening = debate.opening_arguments['bull']
        report += f"{bull_opening.argument}\n\n"
        if bull_opening.data_citations:
            report += "**Data Citations**:\n"
            for citation in bull_opening.data_citations:
                report += f"- {citation}\n"
        report += "\n"

        report += "### 🐻 Bear Case\n\n"
        bear_opening = debate.opening_arguments['bear']
        report += f"{bear_opening.argument}\n\n"
        if bear_opening.data_citations:
            report += "**Data Citations**:\n"
            for citation in bear_opening.data_citations:
                report += f"- {citation}\n"
        report += "\n"

        report += "---\n\n"

        # Round 2: Rebuttals
        report += "## Round 2: Rebuttals\n\n"

        report += "### 🐂 Bull Rebuttal\n\n"
        bull_rebuttal = debate.rebuttals['bull']
        report += f"{bull_rebuttal.argument}\n\n"
        if bull_rebuttal.data_citations:
            report += "**Data Citations**:\n"
            for citation in bull_rebuttal.data_citations:
                report += f"- {citation}\n"
        report += "\n"

        report += "### 🐻 Bear Rebuttal\n\n"
        bear_rebuttal = debate.rebuttals['bear']
        report += f"{bear_rebuttal.argument}\n\n"
        if bear_rebuttal.data_citations:
            report += "**Data Citations**:\n"
            for citation in bear_rebuttal.data_citations:
                report += f"- {citation}\n"
        report += "\n"

        report += "---\n\n"

        # Round 3: Closing Arguments
        report += "## Round 3: Closing Arguments\n\n"

        report += "### 🐂 Bull Closing\n\n"
        bull_closing = debate.closing_arguments['bull']
        report += f"{bull_closing.argument}\n\n"
        if bull_closing.data_citations:
            report += "**Data Citations**:\n"
            for citation in bull_closing.data_citations:
                report += f"- {citation}\n"
        report += "\n"

        report += "### 🐻 Bear Closing\n\n"
        bear_closing = debate.closing_arguments['bear']
        report += f"{bear_closing.argument}\n\n"
        if bear_closing.data_citations:
            report += "**Data Citations**:\n"
            for citation in bear_closing.data_citations:
                report += f"- {citation}\n"
        report += "\n"

        report += "---\n\n"

        # Final Conclusion
        report += "## Final Conclusion\n\n"
        conclusion = debate.conclusion

        report += f"**Position**: {conclusion.final_position.value}\n"
        report += f"**Confidence**: {conclusion.confidence:.1f}%\n"
        report += f"**Bull Score**: {conclusion.bull_score:.1f}%\n"
        report += f"**Bear Score**: {conclusion.bear_score:.1f}%\n\n"

        report += f"**Summary**: {conclusion.debate_summary}\n\n"

        report += "### Key Arguments\n\n"
        for arg in conclusion.key_arguments:
            report += f"- {arg}\n"
        report += "\n"

        report += "### Risk Factors\n\n"
        for risk in conclusion.risk_factors:
            report += f"- {risk}\n"
        report += "\n"

        report += "---\n\n"
        report += f"*Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return report

    async def conduct_batch_debates(
        self,
        tickers: List[str],
        market_data: Dict[str, Dict],
        fundamental_data: Dict[str, Dict],
        technical_data: Dict[str, Dict],
        alternative_data: Dict[str, Dict] = None,
        max_concurrent: int = 3
    ) -> Dict[str, DebateConclusion]:
        """
        Conduct debates for multiple tickers with concurrency control

        Args:
            tickers: List of ticker symbols
            market_data: Market data by ticker
            fundamental_data: Fundamental data by ticker
            technical_data: Technical data by ticker
            alternative_data: Alternative data by ticker (optional)
            max_concurrent: Maximum concurrent debates (default: 3)

        Returns:
            Dictionary mapping ticker to DebateConclusion
        """
        logger.info(f"Starting batch debates for {len(tickers)} tickers (max {max_concurrent} concurrent)")

        semaphore = asyncio.Semaphore(max_concurrent)

        async def debate_with_semaphore(ticker: str):
            async with semaphore:
                return ticker, await self.conduct_debate(
                    ticker=ticker,
                    market_data=market_data.get(ticker, {}),
                    fundamental_data=fundamental_data.get(ticker, {}),
                    technical_data=technical_data.get(ticker, {}),
                    alternative_data=alternative_data.get(ticker) if alternative_data else None
                )

        results = await asyncio.gather(*[debate_with_semaphore(t) for t in tickers])

        return {ticker: conclusion for ticker, conclusion in results}

    def get_performance_stats(self) -> Dict:
        """
        Get performance statistics across all debates

        Returns:
            Dictionary with statistics
        """
        all_debates = [d for debates in self.debate_history.values() for d in debates]

        if not all_debates:
            return {
                'total_debates': 0,
                'avg_duration': 0.0,
                'position_distribution': {},
                'avg_confidence': 0.0
            }

        position_counts = {}
        total_confidence = 0.0
        total_duration = 0.0

        for debate in all_debates:
            pos = debate.conclusion.final_position.value
            position_counts[pos] = position_counts.get(pos, 0) + 1
            total_confidence += debate.conclusion.confidence
            total_duration += debate.duration_seconds

        return {
            'total_debates': len(all_debates),
            'avg_duration': total_duration / len(all_debates),
            'position_distribution': position_counts,
            'avg_confidence': total_confidence / len(all_debates),
            'tickers_analyzed': len(self.debate_history)
        }
