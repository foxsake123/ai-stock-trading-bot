"""
Coordinator for managing agent interactions
"""

import asyncio
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class Coordinator:
    """Coordinates agent interactions and decisions"""

    def __init__(self, message_bus):
        self.message_bus = message_bus
        self.agents = {}

    async def register_agent(self, agent_id: str, agent):
        """Register an agent with the coordinator"""
        self.agents[agent_id] = agent
        logger.info(f"Registered agent: {agent_id}")

    async def request_analysis(self, ticker: str):
        """Request analysis from all agents"""
        results = {}
        for agent_id, agent in self.agents.items():
            try:
                result = await agent.analyze(ticker)
                results[agent_id] = result
            except Exception as e:
                logger.error(f"Error getting analysis from {agent_id}: {e}")
        return results

    async def make_decision(self, analyses: Dict[str, Any]):
        """Make trading decision based on agent analyses"""
        # Simple consensus logic
        scores = []
        for agent_id, analysis in analyses.items():
            if 'confidence' in analysis:
                scores.append(analysis['confidence'])

        if scores:
            avg_confidence = sum(scores) / len(scores)
            return {
                'action': 'BUY' if avg_confidence > 0.6 else 'HOLD',
                'confidence': avg_confidence
            }
        return {'action': 'HOLD', 'confidence': 0}