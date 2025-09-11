"""
Risk Manager Agent
Oversees portfolio risk and has veto power over trades
"""

from .base_agent import BaseAgent
from datetime import datetime
from typing import Dict, Any, List, Optional
import numpy as np
import logging

class RiskManagerAgent(BaseAgent):
    """
    Risk management agent with veto authority over trading decisions
    """
    
    def __init__(self):
        super().__init__(
            agent_id="risk_manager_001",
            agent_type="risk_manager"
        )
        
        # Risk limits
        self.max_position_size = 0.05  # 5% max per position
        self.max_portfolio_risk = 0.15  # 15% max portfolio risk
        self.max_correlation = 0.7  # Max correlation between positions
        self.max_daily_loss = 0.02  # 2% max daily loss
        self.max_volatility = 0.5  # 50% annualized volatility max
        self.min_liquidity_ratio = 100000  # Min $100k daily volume
        
        # Risk scoring weights
        self.risk_weights = {
            "volatility": 0.25,
            "liquidity": 0.20,
            "correlation": 0.15,
            "concentration": 0.15,
            "fundamental": 0.15,
            "technical": 0.10
        }
        
    def analyze(self, ticker: str, market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Perform comprehensive risk analysis
        
        Args:
            ticker: Stock symbol
            market_data: Current market data
            portfolio_data: Current portfolio positions
            
        Returns:
            Risk analysis and recommendation (can veto trades)
        """
        try:
            portfolio_data = kwargs.get('portfolio_data', {})
            agent_reports = kwargs.get('agent_reports', [])
            
            # Calculate individual position risk
            position_risk = self._calculate_position_risk(ticker, market_data)
            
            # Assess portfolio-level risk
            portfolio_risk = self._assess_portfolio_risk(portfolio_data, ticker, market_data)
            
            # Check risk limits
            limit_violations = self._check_risk_limits(
                position_risk, 
                portfolio_risk, 
                market_data
            )
            
            # Analyze agent consensus risk
            consensus_risk = self._analyze_consensus_risk(agent_reports)
            
            # Calculate overall risk score
            risk_score = self._calculate_risk_score(
                position_risk, 
                portfolio_risk, 
                consensus_risk,
                limit_violations
            )
            
            # Determine if veto is needed
            veto_decision = self._make_veto_decision(risk_score, limit_violations)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                risk_score, 
                veto_decision, 
                limit_violations
            )
            
            # Risk metrics for position sizing
            risk_metrics = self._calculate_risk_metrics(
                position_risk, 
                portfolio_risk, 
                market_data
            )
            
            analysis_result = {
                "recommendation": recommendation,
                "analysis": {
                    "risk_score": risk_score,
                    "position_risk": position_risk,
                    "portfolio_risk": portfolio_risk,
                    "consensus_risk": consensus_risk,
                    "limit_violations": limit_violations,
                    "veto_decision": veto_decision,
                    "risk_metrics": risk_metrics,
                    "key_factors": self._identify_key_factors(
                        risk_score, 
                        limit_violations, 
                        veto_decision
                    )
                },
                "risk_assessment": risk_metrics,
                "confidence": self._calculate_confidence(risk_score, veto_decision)
            }
            
            self.log_analysis(ticker, analysis_result)
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Risk analysis failed for {ticker}: {str(e)}")
            return self._generate_error_result(f"Analysis error: {str(e)}")
    
    def _calculate_position_risk(self, ticker: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk metrics for individual position"""
        
        # Volatility risk
        volatility = market_data.get('volatility', 0.3)
        volatility_risk = min(1.0, volatility / self.max_volatility)
        
        # Liquidity risk
        volume = market_data.get('volume', 0)
        avg_volume = market_data.get('avg_volume', 1)
        liquidity_score = min(1.0, volume / self.min_liquidity_ratio)
        liquidity_risk = 1.0 - liquidity_score
        
        # Price risk (distance from support)
        current_price = market_data.get('price', 0)
        support_level = market_data.get('support_level', current_price * 0.95)
        price_risk = (current_price - support_level) / current_price
        
        # Beta risk (market correlation)
        beta = market_data.get('beta', 1.0)
        beta_risk = min(1.0, abs(beta - 1.0))
        
        # Calculate Value at Risk (VaR)
        position_size = market_data.get('proposed_position_size', 10000)
        var_95 = self._calculate_var(position_size, volatility, 0.95)
        
        return {
            "volatility_risk": volatility_risk,
            "liquidity_risk": liquidity_risk,
            "price_risk": price_risk,
            "beta_risk": beta_risk,
            "var_95": var_95,
            "volatility": volatility,
            "beta": beta,
            "overall_risk": (volatility_risk * 0.4 + liquidity_risk * 0.3 + 
                           price_risk * 0.2 + beta_risk * 0.1)
        }
    
    def _assess_portfolio_risk(self, portfolio_data: Dict[str, Any], 
                              ticker: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess portfolio-level risk impact"""
        
        current_positions = portfolio_data.get('positions', [])
        portfolio_value = portfolio_data.get('total_value', 100000)
        
        # Concentration risk
        proposed_size = market_data.get('proposed_position_size', 0)
        concentration = proposed_size / portfolio_value
        concentration_risk = concentration / self.max_position_size
        
        # Correlation risk
        correlations = []
        for position in current_positions:
            correlation = self._calculate_correlation(ticker, position.get('ticker', ''))
            correlations.append(correlation)
        
        max_correlation = max(correlations) if correlations else 0
        correlation_risk = max_correlation / self.max_correlation
        
        # Sector concentration
        sector = market_data.get('sector', 'unknown')
        sector_exposure = sum(p.get('value', 0) for p in current_positions 
                            if p.get('sector') == sector)
        sector_concentration = (sector_exposure + proposed_size) / portfolio_value
        
        # Portfolio volatility impact
        current_volatility = portfolio_data.get('portfolio_volatility', 0.15)
        new_volatility = self._calculate_new_portfolio_volatility(
            current_volatility, 
            market_data.get('volatility', 0.3),
            concentration
        )
        volatility_increase = (new_volatility - current_volatility) / current_volatility
        
        # Max drawdown risk
        historical_drawdown = portfolio_data.get('max_drawdown', 0.1)
        expected_drawdown = self._estimate_drawdown(new_volatility)
        
        return {
            "concentration_risk": concentration_risk,
            "correlation_risk": correlation_risk,
            "sector_concentration": sector_concentration,
            "volatility_increase": volatility_increase,
            "expected_drawdown": expected_drawdown,
            "position_count": len(current_positions) + 1,
            "overall_risk": (concentration_risk * 0.3 + correlation_risk * 0.3 +
                           sector_concentration * 0.2 + volatility_increase * 0.2)
        }
    
    def _check_risk_limits(self, position_risk: Dict[str, Any], 
                          portfolio_risk: Dict[str, Any],
                          market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for risk limit violations"""
        violations = []
        
        # Position size limit
        if portfolio_risk['concentration_risk'] > 1.0:
            violations.append({
                "type": "position_size",
                "severity": "CRITICAL",
                "message": f"Position size exceeds {self.max_position_size*100}% limit"
            })
        
        # Correlation limit
        if portfolio_risk['correlation_risk'] > 1.0:
            violations.append({
                "type": "correlation",
                "severity": "HIGH",
                "message": f"Correlation exceeds {self.max_correlation} limit"
            })
        
        # Volatility limit
        if position_risk['volatility'] > self.max_volatility:
            violations.append({
                "type": "volatility",
                "severity": "HIGH",
                "message": f"Volatility {position_risk['volatility']:.1%} exceeds limit"
            })
        
        # Liquidity limit
        if market_data.get('volume', 0) < self.min_liquidity_ratio:
            violations.append({
                "type": "liquidity",
                "severity": "MEDIUM",
                "message": "Insufficient liquidity"
            })
        
        # Sector concentration
        if portfolio_risk['sector_concentration'] > 0.3:
            violations.append({
                "type": "sector_concentration",
                "severity": "MEDIUM",
                "message": "Excessive sector concentration"
            })
        
        return violations
    
    def _analyze_consensus_risk(self, agent_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze risk from agent consensus"""
        
        if not agent_reports:
            return {"consensus_quality": 0.5, "disagreement": 0.5, "confidence_avg": 0.5}
        
        # Extract recommendations
        recommendations = [r.get('recommendation', {}).get('action', 'HOLD') 
                         for r in agent_reports]
        confidences = [r.get('confidence', 0.5) for r in agent_reports]
        
        # Calculate disagreement
        buy_count = recommendations.count('BUY')
        sell_count = recommendations.count('SELL')
        hold_count = recommendations.count('HOLD')
        
        total = len(recommendations)
        if total > 0:
            disagreement = 1.0 - max(buy_count, sell_count, hold_count) / total
        else:
            disagreement = 0.5
        
        # Average confidence
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        
        # Consensus quality (lower disagreement + higher confidence = better)
        consensus_quality = (1 - disagreement) * avg_confidence
        
        return {
            "consensus_quality": consensus_quality,
            "disagreement": disagreement,
            "confidence_avg": avg_confidence,
            "buy_votes": buy_count,
            "sell_votes": sell_count,
            "hold_votes": hold_count
        }
    
    def _calculate_risk_score(self, position_risk: Dict[str, Any], 
                             portfolio_risk: Dict[str, Any],
                             consensus_risk: Dict[str, Any],
                             violations: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score (0=low risk, 1=extreme risk)"""
        
        # Base risk scores
        position_score = position_risk['overall_risk']
        portfolio_score = portfolio_risk['overall_risk']
        consensus_score = 1.0 - consensus_risk['consensus_quality']
        
        # Violation penalty
        violation_penalty = 0.0
        for violation in violations:
            if violation['severity'] == 'CRITICAL':
                violation_penalty += 0.3
            elif violation['severity'] == 'HIGH':
                violation_penalty += 0.2
            else:
                violation_penalty += 0.1
        
        # Weighted combination
        risk_score = (
            position_score * 0.3 +
            portfolio_score * 0.3 +
            consensus_score * 0.2 +
            min(1.0, violation_penalty) * 0.2
        )
        
        return min(1.0, risk_score)
    
    def _make_veto_decision(self, risk_score: float, 
                           violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Determine if trade should be vetoed"""
        
        # Check for critical violations
        has_critical = any(v['severity'] == 'CRITICAL' for v in violations)
        
        # Veto conditions
        if has_critical:
            return {
                "veto": True,
                "reason": "Critical risk limit violation",
                "override_possible": False
            }
        elif risk_score > 0.8:
            return {
                "veto": True,
                "reason": "Excessive overall risk",
                "override_possible": True
            }
        elif len(violations) >= 3:
            return {
                "veto": True,
                "reason": "Multiple risk violations",
                "override_possible": True
            }
        else:
            return {
                "veto": False,
                "reason": None,
                "override_possible": False
            }
    
    def _generate_recommendation(self, risk_score: float, 
                                veto_decision: Dict[str, Any],
                                violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate risk management recommendation"""
        
        if veto_decision['veto']:
            action = "HOLD"  # Veto = no trade
            confidence = 1.0  # High confidence in veto
            timeframe = "immediate"
            reasoning = f"VETO: {veto_decision['reason']}"
        elif risk_score > 0.6:
            action = "HOLD"
            confidence = 0.8
            timeframe = "short"
            reasoning = f"High risk score: {risk_score:.2f}"
        elif risk_score < 0.3:
            action = "PROCEED"  # Risk manager approves
            confidence = 0.7
            timeframe = "medium"
            reasoning = "Risk within acceptable limits"
        else:
            action = "HOLD"
            confidence = 0.5
            timeframe = "medium"
            reasoning = "Moderate risk profile"
        
        # Add violation warnings
        if violations and not veto_decision['veto']:
            reasoning += f" | Warnings: {len(violations)} risk factors"
        
        return {
            "action": action,
            "confidence": confidence,
            "timeframe": timeframe,
            "reasoning": reasoning
        }
    
    def _calculate_risk_metrics(self, position_risk: Dict[str, Any], 
                               portfolio_risk: Dict[str, Any],
                               market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed risk metrics for position sizing"""
        
        risk_score = (position_risk['overall_risk'] + portfolio_risk['overall_risk']) / 2
        
        # Determine risk level
        if risk_score > 0.7:
            risk_level = "CRITICAL"
        elif risk_score > 0.5:
            risk_level = "HIGH"
        elif risk_score > 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Calculate position size based on risk
        if risk_level == "CRITICAL":
            position_size = 0.0  # No position
        elif risk_level == "HIGH":
            position_size = 0.01  # 1% max
        elif risk_level == "MEDIUM":
            position_size = 0.02  # 2%
        else:
            position_size = 0.03  # 3%
        
        # Adjust for volatility
        volatility = position_risk['volatility']
        volatility_adj = min(1.0, 0.02 / volatility)  # Target 2% volatility
        position_size = position_size * volatility_adj
        
        # Calculate stop loss based on volatility
        stop_loss_multiplier = 2.0 if risk_level == "LOW" else 1.5
        stop_loss_pct = min(0.1, volatility * stop_loss_multiplier)
        
        current_price = market_data.get('price', 100)
        
        return {
            "risk_level": risk_level,
            "stop_loss": current_price * (1 - stop_loss_pct),
            "take_profit": current_price * (1 + stop_loss_pct * 2),
            "position_size_pct": position_size,
            "volatility": volatility,
            "var_95": position_risk.get('var_95', 0),
            "max_loss": position_size * stop_loss_pct
        }
    
    def _calculate_var(self, position_size: float, volatility: float, 
                      confidence: float) -> float:
        """Calculate Value at Risk"""
        # Using parametric VaR
        z_score = norm.ppf(confidence)
        daily_volatility = volatility / np.sqrt(252)
        var = position_size * z_score * daily_volatility
        return var
    
    def _calculate_correlation(self, ticker1: str, ticker2: str) -> float:
        """Estimate correlation between two stocks"""
        # Simplified - in production would use historical data
        if ticker1 == ticker2:
            return 1.0
        # Assume moderate correlation for same sector
        return 0.5  # Placeholder
    
    def _calculate_new_portfolio_volatility(self, current_vol: float, 
                                           new_vol: float, weight: float) -> float:
        """Estimate new portfolio volatility after adding position"""
        # Simplified calculation
        return np.sqrt((1-weight)**2 * current_vol**2 + weight**2 * new_vol**2 + 
                      2 * weight * (1-weight) * current_vol * new_vol * 0.5)
    
    def _estimate_drawdown(self, volatility: float) -> float:
        """Estimate expected maximum drawdown"""
        # Rule of thumb: max drawdown ≈ 2-3x annualized volatility
        return min(0.5, volatility * 2.5)
    
    def _identify_key_factors(self, risk_score: float, violations: List[Dict[str, Any]], 
                             veto: Dict[str, Any]) -> List[str]:
        """Identify key risk factors"""
        factors = []
        
        if veto['veto']:
            factors.append(f"VETOED: {veto['reason']}")
        
        if risk_score > 0.7:
            factors.append(f"Extreme risk score: {risk_score:.2f}")
        elif risk_score > 0.5:
            factors.append(f"High risk score: {risk_score:.2f}")
        
        for violation in violations[:3]:
            factors.append(f"{violation['type']}: {violation['message']}")
        
        return factors
    
    def _calculate_confidence(self, risk_score: float, veto: Dict[str, Any]) -> float:
        """Calculate confidence in risk assessment"""
        if veto['veto']:
            return 0.95  # Very confident in veto decisions
        
        # Higher risk = higher confidence in risk assessment
        return min(0.95, 0.5 + risk_score * 0.5)
    
    def _generate_error_result(self, error_msg: str) -> Dict[str, Any]:
        """Generate error result"""
        return {
            "recommendation": {"action": "HOLD", "confidence": 1.0, "timeframe": "immediate"},
            "analysis": {"error": error_msg},
            "risk_assessment": {"risk_level": "CRITICAL"},
            "confidence": 1.0
        }