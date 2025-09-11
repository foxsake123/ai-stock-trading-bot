"""
Central coordinator for agent consensus and decision making
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from collections import defaultdict
import numpy as np

from .protocols import (
    AgentMessage, AgentReport, TradingDecision, 
    TradingAction, RiskLevel, TimeFrame, Recommendation, RiskAssessment
)
from .message_bus import MessageBus

class Coordinator:
    """
    Central coordinator that aggregates agent reports and makes final trading decisions
    """
    
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.agents: Dict[str, Any] = {}  # Registered agents
        self.pending_analyses: Dict[str, List[AgentReport]] = defaultdict(list)
        self.decision_history: List[TradingDecision] = []
        self.logger = logging.getLogger("coordinator")
        
        # Configuration
        self.consensus_threshold = 0.6  # 60% agreement needed
        self.min_agents_for_decision = 3  # Minimum agents needed
        self.risk_veto_enabled = True  # Risk manager can veto
        
        # Agent weights for voting
        self.agent_weights = {
            "fundamental_analyst": 1.0,
            "technical_analyst": 1.0,
            "news_analyst": 0.8,
            "sentiment_analyst": 0.8,
            "bull_researcher": 0.9,
            "bear_researcher": 0.9,
            "risk_manager": 1.2,  # Higher weight for risk manager
            "catalyst_trader": 1.0,
            "options_trader": 0.8
        }
        
        # Subscribe to all messages
        self.message_bus.subscribe('all', self._handle_message)
        
    def register_agent(self, agent_id: str, agent_instance: Any):
        """Register an agent with the coordinator"""
        self.agents[agent_id] = agent_instance
        self.logger.info(f"Registered agent: {agent_id}")
        
    async def _handle_message(self, message: AgentMessage):
        """Handle incoming messages from agents"""
        if message.message_type == "analysis":
            await self._process_analysis(message)
        elif message.message_type == "veto":
            await self._process_veto(message)
        elif message.message_type == "alert":
            await self._process_alert(message)
            
    async def _process_analysis(self, message: AgentMessage):
        """Process analysis report from an agent"""
        try:
            # Extract report from message payload
            report_data = message.payload
            
            # Create AgentReport from payload
            report = self._create_report_from_payload(message, report_data)
            
            # Add to pending analyses for this ticker
            self.pending_analyses[message.ticker].append(report)
            
            # Check if we have enough reports to make a decision
            if len(self.pending_analyses[message.ticker]) >= self.min_agents_for_decision:
                await self._attempt_decision(message.ticker)
                
        except Exception as e:
            self.logger.error(f"Error processing analysis: {e}")
            
    def _create_report_from_payload(self, message: AgentMessage, payload: Dict) -> AgentReport:
        """Create AgentReport from message payload"""
        rec_data = payload.get("recommendation", {})
        risk_data = payload.get("risk_assessment", {})
        
        recommendation = Recommendation(
            action=TradingAction(rec_data.get("action", "HOLD")),
            confidence=rec_data.get("confidence", 0.0),
            timeframe=TimeFrame(rec_data.get("timeframe", "medium")),
            reasoning=rec_data.get("reasoning", "")
        )
        
        risk_assessment = RiskAssessment(
            risk_level=RiskLevel(risk_data.get("risk_level", "MEDIUM")),
            stop_loss=risk_data.get("stop_loss", 0.0),
            take_profit=risk_data.get("take_profit", 0.0),
            position_size_pct=risk_data.get("position_size_pct", 0.01),
            volatility=risk_data.get("volatility", 0.0)
        )
        
        return AgentReport(
            agent_id=message.agent_id,
            agent_type=message.agent_type,
            timestamp=message.timestamp,
            ticker=message.ticker,
            recommendation=recommendation,
            analysis=payload.get("analysis", {}),
            risk_assessment=risk_assessment,
            confidence=payload.get("confidence", 0.0)
        )
        
    async def _attempt_decision(self, ticker: str):
        """Attempt to make a trading decision based on collected reports"""
        reports = self.pending_analyses[ticker]
        
        # Calculate weighted consensus
        consensus = self._calculate_consensus(reports)
        
        # Check for risk manager veto
        if self.risk_veto_enabled:
            risk_veto = self._check_risk_veto(reports)
            if risk_veto:
                self.logger.warning(f"Risk manager vetoed trade for {ticker}")
                consensus["action"] = TradingAction.HOLD
                consensus["risk_override"] = True
                
        # Create trading decision
        decision = self._create_trading_decision(ticker, reports, consensus)
        
        # Store decision
        self.decision_history.append(decision)
        
        # Clear pending analyses for this ticker
        self.pending_analyses[ticker] = []
        
        # Publish decision
        await self._publish_decision(decision)
        
        self.logger.info(f"Trading decision made for {ticker}: {decision.action.value}")
        
    def _calculate_consensus(self, reports: List[AgentReport]) -> Dict[str, Any]:
        """
        Calculate weighted consensus from agent reports
        
        Returns:
            Consensus decision with confidence
        """
        action_votes = defaultdict(float)
        total_weight = 0
        confidence_scores = []
        stop_losses = []
        take_profits = []
        position_sizes = []
        
        for report in reports:
            weight = self.agent_weights.get(report.agent_type, 1.0)
            
            # Weight the vote by agent weight and confidence
            vote_weight = weight * report.confidence
            action_votes[report.recommendation.action] += vote_weight
            total_weight += vote_weight
            
            # Collect metrics
            confidence_scores.append(report.confidence)
            stop_losses.append(report.risk_assessment.stop_loss)
            take_profits.append(report.risk_assessment.take_profit)
            position_sizes.append(report.risk_assessment.position_size_pct)
            
        # Determine winning action
        if total_weight > 0:
            normalized_votes = {
                action: votes/total_weight 
                for action, votes in action_votes.items()
            }
            winning_action = max(normalized_votes, key=normalized_votes.get)
            consensus_strength = normalized_votes[winning_action]
        else:
            winning_action = TradingAction.HOLD
            consensus_strength = 0.0
            
        # Calculate aggregate metrics
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        avg_stop_loss = np.mean([sl for sl in stop_losses if sl > 0]) if stop_losses else 0.0
        avg_take_profit = np.mean([tp for tp in take_profits if tp > 0]) if take_profits else 0.0
        avg_position_size = np.mean(position_sizes) if position_sizes else 0.01
        
        # Adjust position size based on consensus strength
        adjusted_position_size = avg_position_size * min(1.0, consensus_strength / self.consensus_threshold)
        
        return {
            "action": winning_action,
            "consensus_strength": consensus_strength,
            "confidence": avg_confidence * consensus_strength,
            "stop_loss": avg_stop_loss,
            "take_profit": avg_take_profit,
            "position_size": adjusted_position_size,
            "risk_override": False
        }
        
    def _check_risk_veto(self, reports: List[AgentReport]) -> bool:
        """
        Check if risk manager has vetoed the trade
        
        Returns:
            True if trade should be vetoed
        """
        for report in reports:
            if report.agent_type == "risk_manager":
                # Veto if risk is critical or action is explicit hold/sell with high confidence
                if (report.risk_assessment.risk_level == RiskLevel.CRITICAL or
                    (report.recommendation.action in [TradingAction.HOLD, TradingAction.SELL] and
                     report.confidence > 0.8)):
                    return True
        return False
        
    def _create_trading_decision(self, ticker: str, reports: List[AgentReport], 
                                consensus: Dict[str, Any]) -> TradingDecision:
        """Create final trading decision from consensus"""
        
        # Determine timeframe (use most common)
        timeframes = [r.recommendation.timeframe for r in reports]
        timeframe_counts = defaultdict(int)
        for tf in timeframes:
            timeframe_counts[tf] += 1
        winning_timeframe = max(timeframe_counts, key=timeframe_counts.get) if timeframes else TimeFrame.MEDIUM
        
        # Get contributing agents
        contributing_agents = [r.agent_id for r in reports]
        
        # Generate reasoning
        reasoning = self._generate_decision_reasoning(reports, consensus)
        
        return TradingDecision(
            timestamp=datetime.now(),
            ticker=ticker,
            action=consensus["action"],
            confidence=consensus["confidence"],
            position_size=consensus["position_size"],
            stop_loss=consensus["stop_loss"],
            take_profit=consensus["take_profit"],
            timeframe=winning_timeframe,
            contributing_agents=contributing_agents,
            risk_override=consensus.get("risk_override", False),
            reasoning=reasoning
        )
        
    def _generate_decision_reasoning(self, reports: List[AgentReport], 
                                    consensus: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for the decision"""
        reasons = []
        
        # Consensus strength
        strength_pct = consensus["consensus_strength"] * 100
        reasons.append(f"{strength_pct:.0f}% agent consensus")
        
        # Key factors from top agents
        top_reports = sorted(reports, key=lambda r: r.confidence, reverse=True)[:3]
        for report in top_reports:
            if report.recommendation.reasoning:
                reasons.append(f"{report.agent_type}: {report.recommendation.reasoning[:50]}")
                
        # Risk override note
        if consensus.get("risk_override"):
            reasons.append("Risk manager override applied")
            
        return " | ".join(reasons)
        
    async def _publish_decision(self, decision: TradingDecision):
        """Publish trading decision to message bus"""
        message = AgentMessage(
            agent_id="coordinator",
            agent_type="coordinator",
            timestamp=decision.timestamp,
            ticker=decision.ticker,
            message_type="decision",
            payload=decision.to_dict(),
            priority=2  # High priority
        )
        
        await self.message_bus.publish(message)
        
    async def _process_veto(self, message: AgentMessage):
        """Process veto message from risk manager"""
        ticker = message.ticker
        
        # Clear any pending analyses for this ticker
        if ticker in self.pending_analyses:
            self.pending_analyses[ticker] = []
            self.logger.warning(f"Risk veto received for {ticker}, clearing pending analyses")
            
        # Publish veto notification
        veto_decision = TradingDecision(
            timestamp=datetime.now(),
            ticker=ticker,
            action=TradingAction.HOLD,
            confidence=1.0,
            position_size=0.0,
            stop_loss=0.0,
            take_profit=0.0,
            timeframe=TimeFrame.SHORT,
            contributing_agents=[message.agent_id],
            risk_override=True,
            reasoning=f"Vetoed by {message.agent_id}: {message.payload.get('reason', 'Risk threshold exceeded')}"
        )
        
        await self._publish_decision(veto_decision)
        
    async def _process_alert(self, message: AgentMessage):
        """Process alert message from agents"""
        self.logger.warning(f"Alert from {message.agent_id}: {message.payload.get('alert', 'Unknown alert')}")
        
        # Forward critical alerts
        if message.priority >= 2:
            alert_message = AgentMessage(
                agent_id="coordinator",
                agent_type="coordinator",
                timestamp=datetime.now(),
                ticker=message.ticker,
                message_type="alert_forward",
                payload=message.payload,
                priority=message.priority
            )
            await self.message_bus.publish(alert_message)
            
    async def request_analysis(self, ticker: str, market_data: Dict[str, Any], 
                              catalyst_data: Optional[Dict[str, Any]] = None):
        """
        Request analysis from all registered agents
        
        Args:
            ticker: Stock symbol to analyze
            market_data: Current market data
            catalyst_data: Optional catalyst information
        """
        self.logger.info(f"Requesting analysis for {ticker}")
        
        # Clear any existing pending analyses
        self.pending_analyses[ticker] = []
        
        # Request analysis from each agent
        tasks = []
        for agent_id, agent in self.agents.items():
            if hasattr(agent, 'analyze'):
                task = asyncio.create_task(
                    self._request_agent_analysis(agent, ticker, market_data, catalyst_data)
                )
                tasks.append(task)
                
        # Wait for all agents to respond (with timeout)
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout waiting for agent analyses for {ticker}")
            
    async def _request_agent_analysis(self, agent: Any, ticker: str, 
                                     market_data: Dict[str, Any],
                                     catalyst_data: Optional[Dict[str, Any]]):
        """Request analysis from a single agent"""
        try:
            # Call agent's analyze method
            result = agent.analyze(ticker, market_data, catalyst_data=catalyst_data)
            
            # Publish result to message bus
            message = AgentMessage(
                agent_id=agent.agent_id,
                agent_type=agent.agent_type,
                timestamp=datetime.now(),
                ticker=ticker,
                message_type="analysis",
                payload=result,
                priority=1
            )
            
            await self.message_bus.publish(message)
            
        except Exception as e:
            self.logger.error(f"Error getting analysis from {agent.agent_id}: {e}")
            
    def get_decision_history(self, ticker: Optional[str] = None, 
                           limit: int = 10) -> List[TradingDecision]:
        """Get recent trading decisions"""
        decisions = self.decision_history
        
        if ticker:
            decisions = [d for d in decisions if d.ticker == ticker]
            
        return decisions[-limit:]
    
    def get_coordinator_stats(self) -> Dict[str, Any]:
        """Get coordinator statistics"""
        action_counts = defaultdict(int)
        ticker_counts = defaultdict(int)
        
        for decision in self.decision_history:
            action_counts[decision.action.value] += 1
            ticker_counts[decision.ticker] += 1
            
        return {
            "total_decisions": len(self.decision_history),
            "registered_agents": len(self.agents),
            "pending_analyses": sum(len(analyses) for analyses in self.pending_analyses.values()),
            "action_distribution": dict(action_counts),
            "ticker_distribution": dict(ticker_counts),
            "consensus_threshold": self.consensus_threshold,
            "min_agents_required": self.min_agents_for_decision
        }