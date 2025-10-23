"""
Debate-Enhanced Coordinator
Integrates bull/bear debate system with existing agent coordination
Replaces simple weighted voting with structured debates
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.agents.debate_orchestrator import (
    DebateOrchestrator,
    DebatePosition,
    DebateConclusion
)
from src.agents.bull_analyst import BullAnalyst
from src.agents.bear_analyst import BearAnalyst
from src.agents.neutral_moderator import NeutralModerator

logger = logging.getLogger(__name__)


class DebateCoordinator:
    """
    Enhanced Coordinator that uses bull/bear debates instead of weighted voting

    Integration with existing system:
    - Receives analysis requests from coordinator
    - Conducts structured 3-round debates
    - Returns DebateConclusion as decision
    - Stores debate history for analysis
    - Compatible with both SHORGAN-BOT and DEE-BOT strategies
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout_seconds: int = 30,
        enable_debates: bool = True
    ):
        """
        Initialize Debate Coordinator

        Args:
            api_key: Anthropic API key (optional, uses env var if not provided)
            timeout_seconds: Maximum debate duration
            enable_debates: Enable debate mode (if False, falls back to simple consensus)
        """
        self.enable_debates = enable_debates

        if self.enable_debates:
            # Initialize debate components
            self.bull_analyst = BullAnalyst(api_key=api_key)
            self.bear_analyst = BearAnalyst(api_key=api_key)
            self.moderator = NeutralModerator(api_key=api_key)

            self.orchestrator = DebateOrchestrator(
                bull_analyst=self.bull_analyst,
                bear_analyst=self.bear_analyst,
                neutral_moderator=self.moderator,
                timeout_seconds=timeout_seconds
            )

            logger.info(f"DebateCoordinator initialized with debates enabled ({timeout_seconds}s timeout)")
        else:
            logger.info("DebateCoordinator initialized with debates disabled (fallback mode)")

    async def make_decision_with_debate(
        self,
        ticker: str,
        agent_analyses: Dict[str, Any],
        market_data: Dict[str, Any],
        fundamental_data: Optional[Dict] = None,
        technical_data: Optional[Dict] = None,
        alternative_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make trading decision using debate system

        Args:
            ticker: Stock ticker symbol
            agent_analyses: Analyses from traditional agents
            market_data: Current market data
            fundamental_data: Fundamental analysis data
            technical_data: Technical analysis data
            alternative_data: Alternative data signals

        Returns:
            Decision dictionary compatible with existing coordinator format
        """
        if not self.enable_debates:
            return self._fallback_decision(ticker, agent_analyses)

        try:
            # Conduct debate
            conclusion = await self.orchestrator.conduct_debate(
                ticker=ticker,
                market_data=market_data,
                fundamental_data=fundamental_data or self._extract_fundamental_data(agent_analyses),
                technical_data=technical_data or self._extract_technical_data(agent_analyses),
                alternative_data=alternative_data
            )

            # Convert debate conclusion to coordinator decision format
            decision = self._convert_debate_to_decision(ticker, conclusion, agent_analyses)

            logger.info(f"Debate decision for {ticker}: {conclusion.final_position.value} ({conclusion.confidence:.1f}% confidence)")

            return decision

        except Exception as e:
            logger.error(f"Error in debate for {ticker}: {e}")
            return self._fallback_decision(ticker, agent_analyses)

    def _convert_debate_to_decision(
        self,
        ticker: str,
        conclusion: DebateConclusion,
        agent_analyses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert DebateConclusion to coordinator decision format

        Args:
            ticker: Stock ticker
            conclusion: Debate conclusion
            agent_analyses: Original agent analyses

        Returns:
            Decision dict compatible with existing system
        """
        # Map DebatePosition to action
        if conclusion.final_position == DebatePosition.LONG:
            action = "BUY"
        elif conclusion.final_position == DebatePosition.SHORT:
            action = "SELL"
        else:  # NEUTRAL
            action = "HOLD"

        decision = {
            "ticker": ticker,
            "action": action,
            "confidence": conclusion.confidence / 100.0,  # Convert to 0-1 range
            "debate_conclusion": {
                "final_position": conclusion.final_position.value,
                "bull_score": conclusion.bull_score,
                "bear_score": conclusion.bear_score,
                "key_arguments": conclusion.key_arguments,
                "risk_factors": conclusion.risk_factors,
                "debate_summary": conclusion.debate_summary
            },
            "agent_analyses": agent_analyses,  # Preserve original analyses
            "timestamp": datetime.now().isoformat(),
            "decision_method": "debate"
        }

        return decision

    def _extract_fundamental_data(self, agent_analyses: Dict[str, Any]) -> Dict:
        """Extract fundamental data from agent analyses"""
        fundamental_data = {}

        for agent_id, analysis in agent_analyses.items():
            if 'fundamental' in agent_id.lower() and isinstance(analysis, dict):
                fundamental_data.update({
                    'pe_ratio': analysis.get('pe_ratio'),
                    'peg_ratio': analysis.get('peg_ratio'),
                    'revenue_growth': analysis.get('revenue_growth'),
                    'profit_margin': analysis.get('profit_margin'),
                    'debt_to_equity': analysis.get('debt_to_equity'),
                    'roe': analysis.get('roe')
                })

        return {k: v for k, v in fundamental_data.items() if v is not None}

    def _extract_technical_data(self, agent_analyses: Dict[str, Any]) -> Dict:
        """Extract technical data from agent analyses"""
        technical_data = {}

        for agent_id, analysis in agent_analyses.items():
            if 'technical' in agent_id.lower() and isinstance(analysis, dict):
                technical_data.update({
                    'rsi': analysis.get('rsi'),
                    'macd': analysis.get('macd'),
                    'trend': analysis.get('trend'),
                    'support': analysis.get('support'),
                    'resistance': analysis.get('resistance'),
                    'volume_trend': analysis.get('volume_trend')
                })

        return {k: v for k, v in technical_data.items() if v is not None}

    def _fallback_decision(self, ticker: str, agent_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback to simple consensus when debates disabled or error occurs

        Uses weighted voting based on agent confidence scores
        """
        logger.info(f"Using fallback consensus for {ticker}")

        # Calculate weighted average confidence
        buy_votes = 0
        sell_votes = 0
        hold_votes = 0
        total_confidence = 0.0
        count = 0

        for agent_id, analysis in agent_analyses.items():
            if not isinstance(analysis, dict):
                continue

            action = analysis.get('action', 'HOLD')
            confidence = analysis.get('confidence', 0.5)

            if action == 'BUY':
                buy_votes += confidence
            elif action == 'SELL':
                sell_votes += confidence
            else:
                hold_votes += confidence

            total_confidence += confidence
            count += 1

        # Determine final action
        if buy_votes > sell_votes and buy_votes > hold_votes:
            final_action = 'BUY'
            final_confidence = buy_votes / count if count > 0 else 0.5
        elif sell_votes > buy_votes and sell_votes > hold_votes:
            final_action = 'SELL'
            final_confidence = sell_votes / count if count > 0 else 0.5
        else:
            final_action = 'HOLD'
            final_confidence = hold_votes / count if count > 0 else 0.5

        return {
            "ticker": ticker,
            "action": final_action,
            "confidence": final_confidence,
            "agent_analyses": agent_analyses,
            "timestamp": datetime.now().isoformat(),
            "decision_method": "weighted_voting"
        }

    async def make_batch_decisions(
        self,
        tickers: List[str],
        market_data_by_ticker: Dict[str, Dict],
        agent_analyses_by_ticker: Dict[str, Dict[str, Any]],
        max_concurrent: int = 3
    ) -> Dict[str, Dict[str, Any]]:
        """
        Make decisions for multiple tickers using debates

        Args:
            tickers: List of tickers to analyze
            market_data_by_ticker: Market data for each ticker
            agent_analyses_by_ticker: Agent analyses for each ticker
            max_concurrent: Maximum concurrent debates

        Returns:
            Dictionary mapping ticker to decision
        """
        logger.info(f"Making batch decisions for {len(tickers)} tickers")

        async def decide_ticker(ticker: str):
            return ticker, await self.make_decision_with_debate(
                ticker=ticker,
                agent_analyses=agent_analyses_by_ticker.get(ticker, {}),
                market_data=market_data_by_ticker.get(ticker, {})
            )

        # Control concurrency
        semaphore = asyncio.Semaphore(max_concurrent)

        async def decide_with_semaphore(ticker: str):
            async with semaphore:
                return await decide_ticker(ticker)

        results = await asyncio.gather(*[decide_with_semaphore(t) for t in tickers])

        return {ticker: decision for ticker, decision in results}

    def get_debate_history(self, ticker: str) -> List:
        """Get debate history for a ticker"""
        if not self.enable_debates:
            return []
        return self.orchestrator.get_debate_history(ticker)

    def get_latest_debate(self, ticker: str):
        """Get most recent debate for a ticker"""
        if not self.enable_debates:
            return None
        return self.orchestrator.get_latest_debate(ticker)

    def generate_debate_report(self, ticker: str) -> Optional[str]:
        """Generate formatted debate report for a ticker"""
        if not self.enable_debates:
            return None

        latest_debate = self.get_latest_debate(ticker)
        if not latest_debate:
            return None

        return self.orchestrator.generate_debate_report(latest_debate)

    def get_performance_stats(self) -> Dict:
        """Get debate performance statistics"""
        if not self.enable_debates:
            return {"debates_enabled": False}

        stats = self.orchestrator.get_performance_stats()
        stats["debates_enabled"] = True
        return stats


# Example integration with existing coordinator

async def enhance_coordinator_with_debates(
    coordinator,
    ticker: str,
    market_data: Dict[str, Any],
    supplemental_data: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Example function showing how to integrate debate system with existing coordinator

    Args:
        coordinator: Existing Coordinator instance
        ticker: Stock ticker
        market_data: Market data
        supplemental_data: Supplemental data from various sources

    Returns:
        Decision from debate system
    """
    # Get traditional agent analyses
    agent_analyses = coordinator.request_analysis(ticker, market_data, supplemental_data)

    # Create debate coordinator
    debate_coordinator = DebateCoordinator()

    # Make decision with debates
    decision = await debate_coordinator.make_decision_with_debate(
        ticker=ticker,
        agent_analyses=agent_analyses,
        market_data=market_data
    )

    return decision


# Example usage for SHORGAN-BOT and DEE-BOT

async def example_usage():
    """Example showing how to use debate system with trading bots"""

    # Initialize debate coordinator
    debate_coordinator = DebateCoordinator(
        timeout_seconds=30,
        enable_debates=True
    )

    # Example data
    ticker = "AAPL"
    market_data = {"price": 150.00, "volume": 1000000}
    agent_analyses = {
        "fundamental": {"action": "BUY", "confidence": 0.75},
        "technical": {"action": "HOLD", "confidence": 0.60},
        "sentiment": {"action": "BUY", "confidence": 0.70}
    }

    # Make decision with debate
    decision = await debate_coordinator.make_decision_with_debate(
        ticker=ticker,
        agent_analyses=agent_analyses,
        market_data=market_data
    )

    print(f"Decision: {decision['action']}")
    print(f"Confidence: {decision['confidence']:.2%}")
    print(f"Bull Score: {decision['debate_conclusion']['bull_score']:.1f}")
    print(f"Bear Score: {decision['debate_conclusion']['bear_score']:.1f}")
    print(f"\nKey Arguments:")
    for arg in decision['debate_conclusion']['key_arguments']:
        print(f"- {arg}")

    # Generate debate report
    report = debate_coordinator.generate_debate_report(ticker)
    if report:
        print("\n" + report)


if __name__ == '__main__':
    asyncio.run(example_usage())
