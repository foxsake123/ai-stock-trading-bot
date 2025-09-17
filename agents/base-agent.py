"""
Base Agent Class for AI Trading System
Abstract base class defining the interface for all trading agents
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import logging

class BaseAgent(ABC):
    """Abstract base class for all trading agents"""
    
    def __init__(self, agent_id: str, agent_type: str):
        """
        Initialize base agent
        
        Args:
            agent_id: Unique identifier for this agent instance
            agent_type: Type of agent (e.g., 'catalyst_trader', 'risk_manager')
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.timestamp = datetime.now()
        self.logger = logging.getLogger(f"agent.{agent_id}")
        
    @abstractmethod
    def analyze(self, ticker: str, market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Analyze a stock and generate trading recommendation
        
        Args:
            ticker: Stock symbol to analyze
            market_data: Current market data for the stock
            **kwargs: Additional analysis parameters
            
        Returns:
            Dict containing analysis results and recommendation
        """
        pass
    
    def generate_report(self, ticker: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate standardized agent report
        
        Args:
            ticker: Stock symbol analyzed
            analysis: Analysis results from analyze() method
            
        Returns:
            Standardized report format
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker,
            "recommendation": analysis.get("recommendation", {}),
            "analysis": analysis.get("analysis", {}),
            "risk_assessment": analysis.get("risk_assessment", {}),
            "confidence": analysis.get("confidence", 0.0)
        }
    
    def validate_market_data(self, market_data: Dict[str, Any]) -> bool:
        """
        Validate required market data is present
        
        Args:
            market_data: Market data dictionary to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        required_fields = ['price', 'volume', 'market_cap']
        return all(field in market_data for field in required_fields)
    
    def log_analysis(self, ticker: str, result: Dict[str, Any]) -> None:
        """
        Log analysis results
        
        Args:
            ticker: Stock symbol
            result: Analysis result to log
        """
        self.logger.info(f"Analysis complete for {ticker}: {result.get('recommendation', {}).get('action', 'UNKNOWN')}")
    
    def get_agent_info(self) -> Dict[str, str]:
        """
        Get basic agent information
        
        Returns:
            Dict with agent metadata
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "created_at": self.timestamp.isoformat()
        }