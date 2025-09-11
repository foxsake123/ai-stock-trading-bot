"""
Message protocols and data structures for agent communication
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

class TradingAction(Enum):
    """Trading action types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    SKIP = "SKIP"

class RiskLevel(Enum):
    """Risk level classifications"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class TimeFrame(Enum):
    """Trading timeframes"""
    INTRADAY = "intraday"
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"

@dataclass
class AgentMessage:
    """Standard message format for inter-agent communication"""
    agent_id: str
    agent_type: str
    timestamp: datetime
    ticker: str
    message_type: str  # 'analysis', 'recommendation', 'alert', 'veto'
    payload: Dict[str, Any]
    priority: int = 0  # 0=low, 1=normal, 2=high, 3=critical
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "timestamp": self.timestamp.isoformat(),
            "ticker": self.ticker,
            "message_type": self.message_type,
            "payload": self.payload,
            "priority": self.priority
        }

@dataclass
class Recommendation:
    """Trading recommendation structure"""
    action: TradingAction
    confidence: float
    timeframe: TimeFrame
    reasoning: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.value,
            "confidence": self.confidence,
            "timeframe": self.timeframe.value,
            "reasoning": self.reasoning
        }

@dataclass
class RiskAssessment:
    """Risk assessment structure"""
    risk_level: RiskLevel
    stop_loss: float
    take_profit: float
    position_size_pct: float
    volatility: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_level": self.risk_level.value,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "position_size_pct": self.position_size_pct,
            "volatility": self.volatility
        }

@dataclass
class AgentReport:
    """Standardized agent analysis report"""
    agent_id: str
    agent_type: str
    timestamp: datetime
    ticker: str
    recommendation: Recommendation
    analysis: Dict[str, Any]
    risk_assessment: RiskAssessment
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "timestamp": self.timestamp.isoformat(),
            "ticker": self.ticker,
            "recommendation": self.recommendation.to_dict(),
            "analysis": self.analysis,
            "risk_assessment": self.risk_assessment.to_dict(),
            "confidence": self.confidence
        }

@dataclass
class TradingDecision:
    """Final aggregated trading decision"""
    timestamp: datetime
    ticker: str
    action: TradingAction
    confidence: float
    position_size: float
    stop_loss: float
    take_profit: float
    timeframe: TimeFrame
    contributing_agents: List[str]
    risk_override: bool = False
    reasoning: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "ticker": self.ticker,
            "action": self.action.value,
            "confidence": self.confidence,
            "position_size": self.position_size,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "timeframe": self.timeframe.value,
            "contributing_agents": self.contributing_agents,
            "risk_override": self.risk_override,
            "reasoning": self.reasoning
        }