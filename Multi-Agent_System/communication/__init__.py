"""
Communication module for AI Trading Bot
Handles inter-agent messaging and coordination
"""

from .coordinator import Coordinator
from .message_bus import MessageBus
from .protocols import AgentMessage, TradingDecision

__all__ = ['Coordinator', 'MessageBus', 'AgentMessage', 'TradingDecision']