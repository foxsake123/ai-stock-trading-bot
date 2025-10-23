"""Communication protocol definitions for agent messaging."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass
class AgentMessage:
    """Standardized payload for inter-agent communication."""

    agent_id: str
    agent_type: str
    timestamp: datetime
    ticker: str
    message_type: str
    payload: Dict[str, Any]
    priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the message into a dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data
