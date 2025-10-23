"""
AI Trading Bot - Agents Module
Multi-agent trading system with specialized agents
"""

from .base_agent import BaseAgent
from .shorgan_catalyst_agent import ShorganCatalystAgent

__all__ = ['BaseAgent', 'ShorganCatalystAgent']