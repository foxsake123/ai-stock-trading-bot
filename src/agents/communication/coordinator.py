"""Coordinator for managing agent interactions."""

import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Deque, Dict, List, Optional

logger = logging.getLogger(__name__)


class DecisionAction(Enum):
    """Available actions for coordinator decisions."""

    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"


@dataclass
class DecisionRecord:
    """Represents a coordinator decision with supporting metadata."""

    ticker: str
    action: DecisionAction
    confidence: float
    analyses: Dict[str, Any]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the decision for external consumers."""

        return {
            "ticker": self.ticker,
            "action": self.action.value,
            "confidence": self.confidence,
            "analyses": self.analyses,
            "timestamp": self.timestamp.isoformat(),
        }


class Coordinator:
    """Coordinates agent interactions and trading decisions."""

    def __init__(self, message_bus, history_limit: int = 50):
        self.message_bus = message_bus
        self.agents: Dict[str, Any] = {}
        self._decision_history: Dict[str, Deque[DecisionRecord]] = {}
        self._history_limit = history_limit

    def register_agent(self, agent_id: str, agent) -> None:
        """Register an agent with the coordinator."""

        self.agents[agent_id] = agent
        logger.info("Registered agent: %s", agent_id)

    def request_analysis(
        self,
        ticker: str,
        market_data: Dict[str, Any],
        supplemental_data: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Request analysis from all registered agents."""

        supplemental_data = supplemental_data or {}
        results: Dict[str, Any] = {}
        risk_agents: List[str] = []

        for agent_id, agent in self.agents.items():
            if getattr(agent, "agent_type", "") == "risk_manager":
                risk_agents.append(agent_id)
                continue

            try:
                kwargs = self._build_agent_context(agent_id, agent, supplemental_data)
                result = agent.analyze(ticker, market_data, **kwargs)
                results[agent_id] = result
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.error("Error getting analysis from %s: %s", agent_id, exc)

        for agent_id in risk_agents:
            agent = self.agents[agent_id]
            try:
                kwargs = self._build_agent_context(agent_id, agent, supplemental_data)
                kwargs.setdefault("agent_reports", list(results.values()))
                result = agent.analyze(ticker, market_data, **kwargs)
                results[agent_id] = result
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.error("Error getting analysis from %s: %s", agent_id, exc)

        return results

    def make_decision(self, ticker: str, analyses: Dict[str, Any]) -> DecisionRecord:
        """Make trading decision based on agent analyses."""

        scores: List[float] = []
        for analysis in analyses.values():
            confidence = analysis.get("confidence") if isinstance(analysis, dict) else None
            if isinstance(confidence, (int, float)):
                scores.append(float(confidence))

        avg_confidence = sum(scores) / len(scores) if scores else 0.0
        action = DecisionAction.BUY if avg_confidence > 0.6 else DecisionAction.HOLD

        decision = DecisionRecord(
            ticker=ticker,
            action=action,
            confidence=avg_confidence,
            analyses=analyses,
            timestamp=datetime.now(timezone.utc),
        )

        history = self._decision_history.setdefault(
            ticker, deque(maxlen=self._history_limit)
        )
        history.appendleft(decision)

        return decision

    def get_decision_history(
        self, ticker: str, limit: Optional[int] = None
    ) -> List[DecisionRecord]:
        """Return the most recent decisions for a ticker."""

        history = list(self._decision_history.get(ticker, []))
        if limit is not None:
            return history[:limit]
        return history

    def _build_agent_context(
        self,
        agent_id: str,
        agent: Any,
        supplemental_data: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Resolve supplemental context for an agent."""

        context: Dict[str, Any] = {}
        if supplemental_data:
            context = (
                supplemental_data.get(agent_id)
                or supplemental_data.get(getattr(agent, "agent_type", ""))
                or {}
            )
        return dict(context)