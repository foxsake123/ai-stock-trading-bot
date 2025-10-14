"""Tests for communication protocol utilities."""

from datetime import datetime, timezone

from communication.protocols import AgentMessage


def test_agent_message_to_dict_serializes_payload():
    payload = {"insight": "buy", "confidence": 0.87}
    message = AgentMessage(
        agent_id="agent-123",
        agent_type="analysis",
        timestamp=datetime(2024, 1, 1, 12, 30, tzinfo=timezone.utc),
        ticker="AAPL",
        message_type="analysis",
        payload=payload,
        priority=5,
    )

    serialized = message.to_dict()

    assert serialized["payload"] == payload
    assert serialized["timestamp"] == "2024-01-01T12:30:00+00:00"
