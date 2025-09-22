import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from communication.coordinator import Coordinator, DecisionAction


class DummyAgent:
    """Simple agent used for coordinator tests."""

    def __init__(self, agent_id: str, agent_type: str, response: Dict[str, Any]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self._response = response
        self.calls: List[Dict[str, Any]] = []

    def analyze(self, ticker: str, market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        self.calls.append({
            "ticker": ticker,
            "market_data": market_data,
            "kwargs": kwargs,
        })
        return dict(self._response)


class DummyRiskAgent:
    """Risk manager stub that records received reports."""

    def __init__(self, response: Dict[str, Any]):
        self.agent_id = "risk_manager_001"
        self.agent_type = "risk_manager"
        self._response = response
        self.received_reports: Optional[List[Dict[str, Any]]] = None
        self.received_kwargs: Optional[Dict[str, Any]] = None

    def analyze(self, ticker: str, market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        self.received_kwargs = kwargs
        self.received_reports = kwargs.get("agent_reports")
        return dict(self._response)


@pytest.fixture
def coordinator() -> Coordinator:
    return Coordinator(message_bus=None, history_limit=5)


def test_register_agent_is_synchronous(coordinator: Coordinator) -> None:
    agent = DummyAgent("agent-1", "test_agent", {"confidence": 0.5})

    coordinator.register_agent(agent.agent_id, agent)

    assert coordinator.agents[agent.agent_id] is agent


def test_request_analysis_invokes_agents_with_context(coordinator: Coordinator) -> None:
    market_data = {"price": 100.0}
    analysis_response = {"confidence": 0.7}

    fundamental_agent = DummyAgent("fundamental_analyst_001", "fundamental_analyst", analysis_response)
    risk_agent = DummyRiskAgent({"confidence": 0.4})

    coordinator.register_agent(fundamental_agent.agent_id, fundamental_agent)
    coordinator.register_agent(risk_agent.agent_id, risk_agent)

    supplemental_data = {
        fundamental_agent.agent_type: {"fundamental_data": {"pe_ratio": 20}},
        risk_agent.agent_type: {"portfolio_data": {"positions": []}},
    }

    results = coordinator.request_analysis("AAPL", market_data, supplemental_data=supplemental_data)

    assert fundamental_agent.calls, "Fundamental agent should be invoked"
    assert fundamental_agent.calls[0]["kwargs"]["fundamental_data"]["pe_ratio"] == 20

    assert risk_agent.received_reports is not None
    assert len(risk_agent.received_reports) == 1
    assert risk_agent.received_reports[0]["confidence"] == analysis_response["confidence"]
    assert risk_agent.received_kwargs is not None
    assert "portfolio_data" in risk_agent.received_kwargs

    assert results[fundamental_agent.agent_id]["confidence"] == analysis_response["confidence"]
    assert results[risk_agent.agent_id]["confidence"] == 0.4


def test_make_decision_tracks_history(coordinator: Coordinator) -> None:
    agent_id = "fundamental_analyst_001"
    coordinator.agents[agent_id] = DummyAgent(agent_id, "fundamental_analyst", {"confidence": 0.8})

    first_decision = coordinator.make_decision("AAPL", {
        agent_id: {"confidence": 0.8}
    })
    second_decision = coordinator.make_decision("AAPL", {
        agent_id: {"confidence": 0.3}
    })

    history = coordinator.get_decision_history("AAPL")

    assert history[0] == second_decision
    assert history[1] == first_decision
    assert history[0].action == DecisionAction.HOLD
    assert history[0].confidence == pytest.approx(0.3)
    assert history[0].to_dict()["action"] == DecisionAction.HOLD.value

    limited_history = coordinator.get_decision_history("AAPL", limit=1)
    assert limited_history == [second_decision]
