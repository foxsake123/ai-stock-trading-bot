"""
Bear Researcher Agent
Identifies risks, vulnerabilities, and potential downside
"""

from .base_agent import BaseAgent
from datetime import datetime
from typing import Dict, Any, List
import logging

class BearResearcherAgent(BaseAgent):
    """
    Specialized in identifying risks and bearish signals
    """
    
    def __init__(self):
        super().__init__(
            agent_id="bear_researcher_001",
            agent_type="bear_researcher"
        )
        
        # Bear case factors and weights
        self.bearish_factors = {
            "declining_revenue": 0.9,
            "margin_compression": 0.85,
            "increasing_debt": 0.8,
            "market_saturation": 0.75,
            "regulatory_risk": 0.85,
            "competitive_threats": 0.8,
            "insider_selling": 0.7,
            "technical_breakdown": 0.75,
            "valuation_concern": 0.8,
            "macro_headwinds": 0.7
        }
        
    def analyze(self, ticker: str, market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Perform bearish analysis on the stock
        
        Args:
            ticker: Stock symbol
            market_data: Current market data
            
        Returns:
            Bearish analysis and recommendation
        """
        try:
            # Extract all available data
            fundamental_data = kwargs.get('fundamental_data', {})
            technical_data = kwargs.get('technical_data', {})
            news_data = kwargs.get('news_data', [])
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(
                fundamental_data, news_data, market_data
            )
            
            # Analyze valuation concerns
            valuation_risks = self._analyze_valuation_risks(
                fundamental_data, market_data
            )
            
            # Identify technical weakness
            technical_weakness = self._identify_technical_weakness(
                technical_data, market_data
            )
            
            # Analyze competitive threats
            competitive_threats = self._analyze_competitive_threats(
                fundamental_data, news_data
            )
            
            # Calculate bear case score
            bear_score = self._calculate_bear_score(
                risk_factors, 
                valuation_risks, 
                technical_weakness,
                competitive_threats
            )
            
            # Generate bear thesis
            bear_thesis = self._generate_bear_thesis(
                risk_factors, 
                valuation_risks, 
                technical_weakness
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(bear_score, bear_thesis)
            
            # Risk assessment (conservative approach)
            risk_assessment = self._assess_bearish_risk(bear_score, risk_factors)
            
            analysis_result = {
                "recommendation": recommendation,
                "analysis": {
                    "bear_score": bear_score,
                    "risk_factors": risk_factors,
                    "valuation_risks": valuation_risks,
                    "technical_weakness": technical_weakness,
                    "competitive_threats": competitive_threats,
                    "bear_thesis": bear_thesis,
                    "key_factors": self._identify_key_factors(
                        risk_factors, valuation_risks
                    )
                },
                "risk_assessment": risk_assessment,
                "confidence": self._calculate_confidence(bear_score, len(risk_factors))
            }
            
            self.log_analysis(ticker, analysis_result)
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Bear analysis failed for {ticker}: {str(e)}")
            return self._generate_error_result(f"Analysis error: {str(e)}")
    
    def _identify_risk_factors(self, fundamental_data: Dict[str, Any], 
                              news_data: List[Dict[str, Any]],
                              market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify key risk factors"""
        risks = []
        
        # Revenue decline risk
        revenue_growth = fundamental_data.get('revenue_growth', 0)
        if revenue_growth < 0:
            risks.append({
                "type": "declining_revenue",
                "severity": min(1.0, abs(revenue_growth) / 0.2),
                "description": f"Revenue declining: {revenue_growth*100:.1f}%"
            })
        
        # Margin compression
        margin_trend = fundamental_data.get('margin_trend', 0)
        if margin_trend < 0:
            risks.append({
                "type": "margin_compression",
                "severity": 0.8,
                "description": "Profit margins compressing"
            })
        
        # High debt levels
        debt_to_equity = fundamental_data.get('debt_to_equity', 0)
        if debt_to_equity > 2:
            risks.append({
                "type": "increasing_debt",
                "severity": min(1.0, debt_to_equity / 4),
                "description": f"High debt burden: {debt_to_equity:.1f}x equity"
            })
        
        # Cash burn
        free_cash_flow = fundamental_data.get('free_cash_flow', 0)
        if free_cash_flow < 0:
            risks.append({
                "type": "cash_burn",
                "severity": 0.9,
                "description": "Negative free cash flow"
            })
        
        # Regulatory risks from news
        for news in news_data[:5]:
            if any(word in news.get('title', '').lower() 
                   for word in ['investigation', 'regulatory', 'lawsuit', 'probe']):
                risks.append({
                    "type": "regulatory_risk",
                    "severity": 0.85,
                    "description": "Regulatory/legal concerns"
                })
                break
        
        # Insider selling
        if fundamental_data.get('insider_selling_ratio', 0) > 2:
            risks.append({
                "type": "insider_selling",
                "severity": 0.7,
                "description": "Heavy insider selling"
            })
        
        return risks
    
    def _analyze_valuation_risks(self, fundamental_data: Dict[str, Any], 
                                market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze valuation-related risks"""
        concerns = []
        risk_score = 0.0
        
        # P/E ratio concerns
        pe_ratio = fundamental_data.get('pe_ratio', 0)
        sector_avg_pe = fundamental_data.get('sector_avg_pe', 20)
        
        if pe_ratio > sector_avg_pe * 1.5:
            concerns.append("Overvalued vs sector")
            risk_score += 0.3
        
        if pe_ratio > 40:
            concerns.append("Extreme valuation")
            risk_score += 0.4
        
        # PEG ratio concerns
        peg_ratio = fundamental_data.get('peg_ratio', 0)
        if peg_ratio > 2:
            concerns.append("Growth not justifying valuation")
            risk_score += 0.3
        
        # Price to sales concerns
        ps_ratio = fundamental_data.get('price_to_sales', 0)
        if ps_ratio > 10:
            concerns.append("Excessive P/S ratio")
            risk_score += 0.2
        
        return {
            "score": min(1.0, risk_score),
            "concerns": concerns,
            "overvaluation_level": self._calculate_overvaluation(pe_ratio, peg_ratio)
        }
    
    def _identify_technical_weakness(self, technical_data: Dict[str, Any], 
                                    market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify technical weakness signals"""
        weaknesses = []
        weakness_score = 0.0
        
        # Price below moving averages
        if technical_data.get('below_ma200', False):
            weaknesses.append("Below 200-day MA")
            weakness_score += 0.3
        
        if technical_data.get('death_cross', False):
            weaknesses.append("Death cross pattern")
            weakness_score += 0.4
        
        # Downtrend
        price_change_30d = technical_data.get('price_change_30d', 0)
        if price_change_30d < -0.1:
            weaknesses.append("Strong downtrend")
            weakness_score += 0.3
        
        # Support breakdown
        if technical_data.get('below_support', False):
            weaknesses.append("Support level broken")
            weakness_score += 0.25
        
        # Declining volume
        if technical_data.get('volume_trend', 0) < 0:
            weaknesses.append("Declining volume")
            weakness_score += 0.15
        
        return {
            "weaknesses": weaknesses,
            "score": min(1.0, weakness_score),
            "trend": "bearish" if weakness_score > 0.5 else "neutral"
        }
    
    def _analyze_competitive_threats(self, fundamental_data: Dict[str, Any], 
                                    news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze competitive threats"""
        threats = []
        threat_level = 0.0
        
        # Market share loss
        if fundamental_data.get('market_share_trend', 0) < 0:
            threats.append("Losing market share")
            threat_level += 0.4
        
        # New competition from news
        for news in news_data[:5]:
            if any(word in news.get('title', '').lower() 
                   for word in ['competitor', 'rival', 'disruption', 'threat']):
                threats.append("Competitive pressure")
                threat_level += 0.3
                break
        
        # Industry headwinds
        if fundamental_data.get('industry_growth', 0) < 0:
            threats.append("Industry headwinds")
            threat_level += 0.3
        
        return {
            "threats": threats,
            "threat_level": min(1.0, threat_level)
        }
    
    def _calculate_bear_score(self, risks: List[Dict[str, Any]], 
                             valuation: Dict[str, Any], 
                             technical: Dict[str, Any],
                             competitive: Dict[str, Any]) -> float:
        """Calculate overall bear case score"""
        # Risk factor contribution
        risk_score = sum(r['severity'] for r in risks) / max(1, len(risks))
        risk_score = min(1.0, risk_score * 1.2)  # Boost for multiple risks
        
        # Weighted combination
        bear_score = (
            risk_score * 0.35 +
            valuation['score'] * 0.25 +
            technical['score'] * 0.25 +
            competitive['threat_level'] * 0.15
        )
        
        return min(1.0, bear_score)
    
    def _generate_bear_thesis(self, risks: List[Dict[str, Any]], 
                            valuation: Dict[str, Any], 
                            technical: Dict[str, Any]) -> str:
        """Generate comprehensive bear thesis"""
        thesis_points = []
        
        # Top risk
        if risks:
            top_risk = max(risks, key=lambda x: x['severity'])
            thesis_points.append(top_risk['description'])
        
        # Valuation concerns
        if valuation['concerns']:
            thesis_points.append(valuation['concerns'][0])
        
        # Technical weakness
        if technical['weaknesses']:
            thesis_points.append(technical['weaknesses'][0])
        
        # Overall assessment
        if len(risks) >= 3:
            thesis_points.append(f"{len(risks)} major risk factors")
        
        return " | ".join(thesis_points) if thesis_points else "Limited bear case"
    
    def _generate_recommendation(self, bear_score: float, bear_thesis: str) -> Dict[str, Any]:
        """Generate trading recommendation from bear perspective"""
        
        if bear_score > 0.7:
            action = "SELL"
            confidence = min(0.9, bear_score)
            timeframe = "short"  # Bears often focus on near-term risks
        elif bear_score > 0.5:
            action = "SELL"
            confidence = bear_score * 0.8
            timeframe = "medium"
        else:
            action = "HOLD"
            confidence = 0.5
            timeframe = "medium"
        
        reasoning = f"Bear case: {bear_thesis}"
        
        return {
            "action": action,
            "confidence": confidence,
            "timeframe": timeframe,
            "reasoning": reasoning
        }
    
    def _assess_bearish_risk(self, bear_score: float, risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess risk from bearish perspective (conservative)"""
        
        # Bears are risk-averse
        if bear_score > 0.6 or len(risks) >= 3:
            risk_level = "HIGH"
            position_size = 0.0  # No position recommended
        elif bear_score > 0.4:
            risk_level = "MEDIUM"
            position_size = 0.01  # Very small if any
        else:
            risk_level = "LOW"
            position_size = 0.02
        
        # Bears use tight stops
        stop_loss_pct = 0.03  # 3% max loss
        
        return {
            "risk_level": risk_level,
            "stop_loss": 100 * (1 - stop_loss_pct),
            "take_profit": 100 * (1 + stop_loss_pct * 2),
            "position_size_pct": position_size,
            "volatility": 0.05  # Assume higher volatility in bear scenarios
        }
    
    def _identify_key_factors(self, risks: List[Dict[str, Any]], 
                             valuation: Dict[str, Any]) -> List[str]:
        """Identify key bearish factors"""
        factors = []
        
        # Top 2 risks
        for risk in sorted(risks, key=lambda x: x['severity'], reverse=True)[:2]:
            factors.append(risk['description'])
        
        # Valuation concerns
        for concern in valuation['concerns'][:2]:
            factors.append(concern)
        
        if len(risks) >= 4:
            factors.append(f"{len(risks)} major risks identified")
        
        return factors
    
    def _calculate_confidence(self, bear_score: float, risk_count: int) -> float:
        """Calculate confidence in bear case"""
        # More risks = higher confidence in bear case
        risk_confidence = min(1.0, risk_count / 3)
        
        # Strong bear score = higher confidence
        score_confidence = bear_score
        
        return min(0.95, score_confidence * 0.7 + risk_confidence * 0.3)
    
    def _calculate_overvaluation(self, pe_ratio: float, peg_ratio: float) -> str:
        """Calculate overvaluation level"""
        if pe_ratio > 50 or peg_ratio > 3:
            return "extreme"
        elif pe_ratio > 30 or peg_ratio > 2:
            return "high"
        elif pe_ratio > 20 or peg_ratio > 1.5:
            return "moderate"
        else:
            return "fair"
    
    def _generate_error_result(self, error_msg: str) -> Dict[str, Any]:
        """Generate error result"""
        return {
            "recommendation": {"action": "HOLD", "confidence": 0.0, "timeframe": "medium"},
            "analysis": {"error": error_msg},
            "risk_assessment": {"risk_level": "HIGH"},
            "confidence": 0.0
        }