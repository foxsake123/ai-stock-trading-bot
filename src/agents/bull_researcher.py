"""
Bull Researcher Agent
Focuses on identifying positive catalysts and growth opportunities
"""

from .base_agent import BaseAgent
from datetime import datetime
from typing import Dict, Any, List
import logging

class BullResearcherAgent(BaseAgent):
    """
    Specialized in finding bullish opportunities and positive catalysts
    """
    
    def __init__(self):
        super().__init__(
            agent_id="bull_researcher_001",
            agent_type="bull_researcher"
        )
        
        # Bull case factors and weights
        self.bullish_factors = {
            "revenue_growth": 0.9,
            "market_expansion": 0.8,
            "product_innovation": 0.85,
            "competitive_advantage": 0.9,
            "insider_buying": 0.7,
            "institutional_accumulation": 0.8,
            "technical_breakout": 0.7,
            "sector_leadership": 0.75,
            "earnings_momentum": 0.85,
            "margin_expansion": 0.8
        }
        
    def analyze(self, ticker: str, market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Perform bullish analysis on the stock
        
        Args:
            ticker: Stock symbol
            market_data: Current market data
            
        Returns:
            Bullish analysis and recommendation
        """
        try:
            # Extract all available data
            fundamental_data = kwargs.get('fundamental_data', {})
            technical_data = kwargs.get('technical_data', {})
            news_data = kwargs.get('news_data', [])
            
            # Identify growth catalysts
            growth_catalysts = self._identify_growth_catalysts(
                fundamental_data, news_data
            )
            
            # Analyze competitive positioning
            competitive_strength = self._analyze_competitive_position(
                fundamental_data, market_data
            )
            
            # Identify momentum factors
            momentum_factors = self._identify_momentum_factors(
                technical_data, market_data
            )
            
            # Calculate bull case score
            bull_score = self._calculate_bull_score(
                growth_catalysts, 
                competitive_strength, 
                momentum_factors
            )
            
            # Generate bullish thesis
            bull_thesis = self._generate_bull_thesis(
                growth_catalysts, 
                competitive_strength, 
                momentum_factors
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(bull_score, bull_thesis)
            
            # Risk assessment (from bull perspective)
            risk_assessment = self._assess_bullish_risk(bull_score, momentum_factors)
            
            analysis_result = {
                "recommendation": recommendation,
                "analysis": {
                    "bull_score": bull_score,
                    "growth_catalysts": growth_catalysts,
                    "competitive_strength": competitive_strength,
                    "momentum_factors": momentum_factors,
                    "bull_thesis": bull_thesis,
                    "key_factors": self._identify_key_factors(
                        growth_catalysts, momentum_factors
                    )
                },
                "risk_assessment": risk_assessment,
                "confidence": self._calculate_confidence(bull_score, len(growth_catalysts))
            }
            
            self.log_analysis(ticker, analysis_result)
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Bull analysis failed for {ticker}: {str(e)}")
            return self._generate_error_result(f"Analysis error: {str(e)}")
    
    def _identify_growth_catalysts(self, fundamental_data: Dict[str, Any], 
                                  news_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify positive growth catalysts"""
        catalysts = []
        
        # Revenue growth catalyst
        revenue_growth = fundamental_data.get('revenue_growth', 0)
        if revenue_growth > 0.15:
            catalysts.append({
                "type": "revenue_growth",
                "strength": min(1.0, revenue_growth / 0.3),
                "description": f"Strong revenue growth: {revenue_growth*100:.1f}%"
            })
        
        # Earnings momentum
        earnings_growth = fundamental_data.get('earnings_growth', 0)
        if earnings_growth > 0.1:
            catalysts.append({
                "type": "earnings_momentum",
                "strength": min(1.0, earnings_growth / 0.2),
                "description": f"Earnings momentum: {earnings_growth*100:.1f}%"
            })
        
        # Market expansion opportunities
        if fundamental_data.get('international_revenue_pct', 0) < 0.3:
            catalysts.append({
                "type": "market_expansion",
                "strength": 0.7,
                "description": "International expansion opportunity"
            })
        
        # Product innovation from news
        for news in news_data[:5]:
            if any(word in news.get('title', '').lower() 
                   for word in ['innovation', 'breakthrough', 'patent', 'launch']):
                catalysts.append({
                    "type": "product_innovation",
                    "strength": 0.8,
                    "description": "Product innovation catalyst"
                })
                break
        
        # Margin expansion
        if fundamental_data.get('gross_margin_trend', 0) > 0:
            catalysts.append({
                "type": "margin_expansion",
                "strength": 0.75,
                "description": "Expanding profit margins"
            })
        
        return catalysts
    
    def _analyze_competitive_position(self, fundamental_data: Dict[str, Any], 
                                     market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze company's competitive positioning"""
        strengths = []
        score = 0.5  # Neutral starting point
        
        # Market share analysis
        market_cap = market_data.get('market_cap', 0)
        sector_avg_cap = fundamental_data.get('sector_avg_market_cap', market_cap)
        
        if market_cap > sector_avg_cap * 1.5:
            strengths.append("Market leader")
            score += 0.2
        
        # Profitability advantage
        roe = fundamental_data.get('return_on_equity', 0)
        if roe > 0.15:
            strengths.append("High ROE")
            score += 0.15
        
        # Growth advantage
        if fundamental_data.get('revenue_growth', 0) > fundamental_data.get('sector_avg_growth', 0):
            strengths.append("Above-sector growth")
            score += 0.15
        
        # Financial strength
        if fundamental_data.get('debt_to_equity', 1) < 0.5:
            strengths.append("Strong balance sheet")
            score += 0.1
        
        return {
            "score": min(1.0, score),
            "strengths": strengths,
            "moat_rating": self._calculate_moat_rating(score, strengths)
        }
    
    def _identify_momentum_factors(self, technical_data: Dict[str, Any], 
                                  market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify positive momentum factors"""
        factors = []
        momentum_score = 0.0
        
        # Price momentum
        price_change_30d = technical_data.get('price_change_30d', 0)
        if price_change_30d > 0.1:
            factors.append("Strong price momentum")
            momentum_score += 0.3
        
        # Volume surge
        if technical_data.get('volume_ratio', 1) > 1.5:
            factors.append("Increasing volume")
            momentum_score += 0.2
        
        # Technical breakout
        if technical_data.get('above_resistance', False):
            factors.append("Technical breakout")
            momentum_score += 0.25
        
        # Moving average alignment
        if technical_data.get('ma_alignment', '') == 'bullish':
            factors.append("Bullish MA alignment")
            momentum_score += 0.25
        
        return {
            "factors": factors,
            "score": min(1.0, momentum_score),
            "trend": "bullish" if momentum_score > 0.5 else "neutral"
        }
    
    def _calculate_bull_score(self, catalysts: List[Dict[str, Any]], 
                             competitive: Dict[str, Any], 
                             momentum: Dict[str, Any]) -> float:
        """Calculate overall bull case score"""
        # Catalyst contribution
        catalyst_score = sum(c['strength'] for c in catalysts) / max(1, len(catalysts))
        catalyst_score = min(1.0, catalyst_score * 1.2)  # Boost for multiple catalysts
        
        # Weighted combination
        bull_score = (
            catalyst_score * 0.4 +
            competitive['score'] * 0.35 +
            momentum['score'] * 0.25
        )
        
        return min(1.0, bull_score)
    
    def _generate_bull_thesis(self, catalysts: List[Dict[str, Any]], 
                            competitive: Dict[str, Any], 
                            momentum: Dict[str, Any]) -> str:
        """Generate comprehensive bull thesis"""
        thesis_points = []
        
        # Top catalysts
        if catalysts:
            top_catalyst = max(catalysts, key=lambda x: x['strength'])
            thesis_points.append(top_catalyst['description'])
        
        # Competitive advantages
        if competitive['strengths']:
            thesis_points.append(f"{competitive['strengths'][0]} position")
        
        # Momentum confirmation
        if momentum['score'] > 0.5:
            thesis_points.append("Positive momentum confirmation")
        
        # Moat rating
        if competitive['moat_rating'] in ['wide', 'medium']:
            thesis_points.append(f"{competitive['moat_rating'].title()} moat")
        
        return " | ".join(thesis_points) if thesis_points else "Limited bull case"
    
    def _generate_recommendation(self, bull_score: float, bull_thesis: str) -> Dict[str, Any]:
        """Generate trading recommendation from bull perspective"""
        
        if bull_score > 0.7:
            action = "BUY"
            confidence = min(0.9, bull_score)
            timeframe = "medium"  # Bull cases typically play out over time
        elif bull_score > 0.5:
            action = "BUY"
            confidence = bull_score * 0.8
            timeframe = "long"
        else:
            action = "HOLD"
            confidence = 0.5
            timeframe = "medium"
        
        reasoning = f"Bull case: {bull_thesis}"
        
        return {
            "action": action,
            "confidence": confidence,
            "timeframe": timeframe,
            "reasoning": reasoning
        }
    
    def _assess_bullish_risk(self, bull_score: float, momentum: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk from bullish perspective"""
        
        # Bulls accept more risk for growth
        if bull_score > 0.7:
            risk_level = "MEDIUM"  # Acceptable risk for strong bull case
            position_size = 0.04
        elif bull_score > 0.5:
            risk_level = "MEDIUM"
            position_size = 0.03
        else:
            risk_level = "HIGH"
            position_size = 0.01
        
        # Bulls use wider stops to ride volatility
        stop_loss_pct = 0.08 if momentum['score'] > 0.5 else 0.06
        
        return {
            "risk_level": risk_level,
            "stop_loss": 100 * (1 - stop_loss_pct),
            "take_profit": 100 * (1 + stop_loss_pct * 3),  # 3:1 reward/risk
            "position_size_pct": position_size,
            "volatility": 0.03
        }
    
    def _identify_key_factors(self, catalysts: List[Dict[str, Any]], 
                             momentum: Dict[str, Any]) -> List[str]:
        """Identify key bullish factors"""
        factors = []
        
        # Top 2 catalysts
        for catalyst in sorted(catalysts, key=lambda x: x['strength'], reverse=True)[:2]:
            factors.append(catalyst['description'])
        
        # Momentum factors
        for factor in momentum['factors'][:2]:
            factors.append(factor)
        
        if len(catalysts) >= 3:
            factors.append(f"{len(catalysts)} growth catalysts identified")
        
        return factors
    
    def _calculate_confidence(self, bull_score: float, catalyst_count: int) -> float:
        """Calculate confidence in bull case"""
        # More catalysts = higher confidence
        catalyst_confidence = min(1.0, catalyst_count / 3)
        
        # Strong bull score = higher confidence
        score_confidence = bull_score
        
        return min(0.95, score_confidence * 0.7 + catalyst_confidence * 0.3)
    
    def _calculate_moat_rating(self, score: float, strengths: List[str]) -> str:
        """Calculate economic moat rating"""
        if score > 0.8 and len(strengths) >= 3:
            return "wide"
        elif score > 0.6 and len(strengths) >= 2:
            return "medium"
        elif score > 0.4:
            return "narrow"
        else:
            return "none"
    
    def _generate_error_result(self, error_msg: str) -> Dict[str, Any]:
        """Generate error result"""
        return {
            "recommendation": {"action": "HOLD", "confidence": 0.0, "timeframe": "medium"},
            "analysis": {"error": error_msg},
            "risk_assessment": {"risk_level": "HIGH"},
            "confidence": 0.0
        }