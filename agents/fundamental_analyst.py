"""
Fundamental Analyst Agent
Analyzes company financials, earnings, and valuation metrics
"""

from .base_agent import BaseAgent
from datetime import datetime
from typing import Dict, Any, List, Optional
import yfinance as yf
import logging

class FundamentalAnalystAgent(BaseAgent):
    """
    Analyzes fundamental financial metrics and company health
    """
    
    def __init__(self):
        super().__init__(
            agent_id="fundamental_analyst_001",
            agent_type="fundamental_analyst"
        )
        
        # Valuation thresholds
        self.pe_ratio_max = 30  # Maximum P/E for value consideration
        self.peg_ratio_max = 2.0  # Maximum PEG ratio
        self.debt_to_equity_max = 2.0  # Maximum debt/equity ratio
        self.current_ratio_min = 1.0  # Minimum current ratio
        
    def analyze(self, ticker: str, market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Perform fundamental analysis on the stock
        
        Args:
            ticker: Stock symbol
            market_data: Current market data
            
        Returns:
            Fundamental analysis and recommendation
        """
        try:
            # Get stock info
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract key metrics
            metrics = self._extract_financial_metrics(info)
            
            # Analyze valuation
            valuation_score = self._analyze_valuation(metrics)
            
            # Analyze financial health
            health_score = self._analyze_financial_health(metrics)
            
            # Analyze growth prospects
            growth_score = self._analyze_growth(metrics)
            
            # Calculate overall fundamental score
            fundamental_score = self._calculate_fundamental_score(
                valuation_score, health_score, growth_score
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(fundamental_score, metrics)
            
            # Risk assessment
            risk_assessment = self._assess_fundamental_risk(metrics)
            
            analysis_result = {
                "recommendation": recommendation,
                "analysis": {
                    "fundamental_score": fundamental_score,
                    "valuation_score": valuation_score,
                    "health_score": health_score,
                    "growth_score": growth_score,
                    "key_metrics": metrics,
                    "key_factors": self._identify_key_factors(metrics, fundamental_score)
                },
                "risk_assessment": risk_assessment,
                "confidence": self._calculate_confidence(fundamental_score, metrics)
            }
            
            self.log_analysis(ticker, analysis_result)
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Fundamental analysis failed for {ticker}: {str(e)}")
            return self._generate_error_result(f"Analysis error: {str(e)}")
    
    def _extract_financial_metrics(self, info: Dict[str, Any]) -> Dict[str, float]:
        """Extract key financial metrics from stock info"""
        return {
            "pe_ratio": info.get('trailingPE', 0),
            "forward_pe": info.get('forwardPE', 0),
            "peg_ratio": info.get('pegRatio', 0),
            "price_to_book": info.get('priceToBook', 0),
            "debt_to_equity": info.get('debtToEquity', 0),
            "current_ratio": info.get('currentRatio', 1),
            "quick_ratio": info.get('quickRatio', 1),
            "gross_margin": info.get('grossMargins', 0),
            "operating_margin": info.get('operatingMargins', 0),
            "profit_margin": info.get('profitMargins', 0),
            "return_on_equity": info.get('returnOnEquity', 0),
            "return_on_assets": info.get('returnOnAssets', 0),
            "revenue_growth": info.get('revenueGrowth', 0),
            "earnings_growth": info.get('earningsGrowth', 0),
            "free_cash_flow": info.get('freeCashflow', 0),
            "market_cap": info.get('marketCap', 0),
            "enterprise_value": info.get('enterpriseValue', 0),
            "beta": info.get('beta', 1)
        }
    
    def _analyze_valuation(self, metrics: Dict[str, float]) -> float:
        """
        Analyze valuation metrics
        
        Returns:
            Valuation score (0-1, higher is better value)
        """
        score = 0.0
        weight_sum = 0.0
        
        # P/E Ratio analysis
        pe = metrics.get('pe_ratio', 0)
        if 0 < pe < self.pe_ratio_max:
            pe_score = 1.0 - (pe / self.pe_ratio_max)
            score += pe_score * 0.3
            weight_sum += 0.3
        elif pe > 0:
            weight_sum += 0.3
            
        # PEG Ratio analysis
        peg = metrics.get('peg_ratio', 0)
        if 0 < peg < self.peg_ratio_max:
            peg_score = 1.0 - (peg / self.peg_ratio_max)
            score += peg_score * 0.25
            weight_sum += 0.25
        elif peg > 0:
            weight_sum += 0.25
            
        # Price to Book analysis
        pb = metrics.get('price_to_book', 0)
        if 0 < pb < 3:
            pb_score = 1.0 - (pb / 3)
            score += pb_score * 0.2
            weight_sum += 0.2
        elif pb > 0:
            weight_sum += 0.2
            
        # Forward P/E vs Trailing P/E
        forward_pe = metrics.get('forward_pe', 0)
        if forward_pe > 0 and pe > 0 and forward_pe < pe:
            improvement_score = min(1.0, (pe - forward_pe) / pe)
            score += improvement_score * 0.25
            weight_sum += 0.25
        elif forward_pe > 0:
            weight_sum += 0.25
            
        return score / weight_sum if weight_sum > 0 else 0.5
    
    def _analyze_financial_health(self, metrics: Dict[str, float]) -> float:
        """
        Analyze financial health metrics
        
        Returns:
            Health score (0-1, higher is healthier)
        """
        score = 0.0
        weight_sum = 0.0
        
        # Debt to Equity analysis
        de = metrics.get('debt_to_equity', 0)
        if de >= 0:
            if de < self.debt_to_equity_max:
                de_score = 1.0 - (de / self.debt_to_equity_max)
            else:
                de_score = 0
            score += de_score * 0.3
            weight_sum += 0.3
            
        # Current Ratio analysis
        current = metrics.get('current_ratio', 0)
        if current > 0:
            current_score = min(1.0, current / 2.0)
            score += current_score * 0.25
            weight_sum += 0.25
            
        # Profit Margin analysis
        margin = metrics.get('profit_margin', 0)
        if margin > 0:
            margin_score = min(1.0, margin / 0.2)  # 20% profit margin = perfect score
            score += margin_score * 0.25
            weight_sum += 0.25
            
        # Return on Equity analysis
        roe = metrics.get('return_on_equity', 0)
        if roe > 0:
            roe_score = min(1.0, roe / 0.15)  # 15% ROE = perfect score
            score += roe_score * 0.2
            weight_sum += 0.2
            
        return score / weight_sum if weight_sum > 0 else 0.5
    
    def _analyze_growth(self, metrics: Dict[str, float]) -> float:
        """
        Analyze growth prospects
        
        Returns:
            Growth score (0-1, higher is better growth)
        """
        score = 0.0
        weight_sum = 0.0
        
        # Revenue Growth analysis
        rev_growth = metrics.get('revenue_growth', 0)
        if rev_growth != 0:
            rev_score = min(1.0, max(0, (rev_growth + 0.1) / 0.3))  # 20% growth = high score
            score += rev_score * 0.4
            weight_sum += 0.4
            
        # Earnings Growth analysis
        earn_growth = metrics.get('earnings_growth', 0)
        if earn_growth != 0:
            earn_score = min(1.0, max(0, (earn_growth + 0.1) / 0.3))
            score += earn_score * 0.4
            weight_sum += 0.4
            
        # Free Cash Flow analysis
        fcf = metrics.get('free_cash_flow', 0)
        if fcf > 0:
            score += 0.2
            weight_sum += 0.2
            
        return score / weight_sum if weight_sum > 0 else 0.5
    
    def _calculate_fundamental_score(self, valuation: float, health: float, growth: float) -> float:
        """Calculate overall fundamental score"""
        # Weighted average of components
        return (valuation * 0.35 + health * 0.35 + growth * 0.3)
    
    def _generate_recommendation(self, fundamental_score: float, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Generate trading recommendation based on fundamental analysis"""
        
        # Determine action based on score
        if fundamental_score >= 0.7:
            action = "BUY"
            confidence = min(0.95, fundamental_score)
            timeframe = "long"  # Fundamental plays are typically longer-term
        elif fundamental_score >= 0.5:
            action = "HOLD"
            confidence = 0.5
            timeframe = "medium"
        else:
            action = "SELL"
            confidence = 1.0 - fundamental_score
            timeframe = "medium"
            
        # Generate reasoning
        reasoning = self._generate_reasoning(fundamental_score, metrics)
        
        return {
            "action": action,
            "confidence": confidence,
            "timeframe": timeframe,
            "reasoning": reasoning
        }
    
    def _assess_fundamental_risk(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Assess risk based on fundamental metrics"""
        
        # Calculate risk factors
        debt_risk = min(1.0, metrics.get('debt_to_equity', 0) / 3.0)
        valuation_risk = min(1.0, metrics.get('pe_ratio', 30) / 50)
        beta_risk = min(1.0, abs(metrics.get('beta', 1) - 1))
        
        overall_risk = (debt_risk * 0.4 + valuation_risk * 0.3 + beta_risk * 0.3)
        
        if overall_risk > 0.7:
            risk_level = "HIGH"
        elif overall_risk > 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
            
        # Calculate position sizing based on risk
        position_size = max(0.01, min(0.05, 0.05 * (1 - overall_risk)))
        
        # Set stop loss based on volatility (beta proxy)
        beta = metrics.get('beta', 1)
        stop_loss_pct = min(0.15, 0.05 * beta)
        
        current_price = metrics.get('current_price', 100)
        
        return {
            "risk_level": risk_level,
            "stop_loss": current_price * (1 - stop_loss_pct),
            "take_profit": current_price * (1 + stop_loss_pct * 2),
            "position_size_pct": position_size,
            "volatility": beta
        }
    
    def _identify_key_factors(self, metrics: Dict[str, float], score: float) -> List[str]:
        """Identify key fundamental factors"""
        factors = []
        
        # Valuation factors
        if metrics.get('pe_ratio', 30) < 20:
            factors.append(f"Attractive P/E ratio: {metrics['pe_ratio']:.1f}")
        
        # Growth factors
        if metrics.get('revenue_growth', 0) > 0.15:
            factors.append(f"Strong revenue growth: {metrics['revenue_growth']*100:.1f}%")
        
        # Health factors
        if metrics.get('current_ratio', 0) > 2:
            factors.append(f"Strong liquidity: {metrics['current_ratio']:.1f} current ratio")
        
        if metrics.get('debt_to_equity', 1) < 0.5:
            factors.append("Low debt levels")
            
        # Profitability factors
        if metrics.get('return_on_equity', 0) > 0.15:
            factors.append(f"High ROE: {metrics['return_on_equity']*100:.1f}%")
            
        if score > 0.7:
            factors.append("Strong fundamental score")
            
        return factors
    
    def _calculate_confidence(self, fundamental_score: float, metrics: Dict[str, float]) -> float:
        """Calculate confidence in fundamental analysis"""
        base_confidence = fundamental_score
        
        # Adjust for data quality
        data_points = sum(1 for v in metrics.values() if v != 0)
        data_quality = data_points / len(metrics)
        
        return min(0.95, base_confidence * (0.5 + 0.5 * data_quality))
    
    def _generate_reasoning(self, score: float, metrics: Dict[str, float]) -> str:
        """Generate reasoning for recommendation"""
        reasons = []
        
        if score > 0.7:
            reasons.append("Strong fundamentals")
        elif score > 0.5:
            reasons.append("Moderate fundamentals")
        else:
            reasons.append("Weak fundamentals")
            
        # Add specific metric callouts
        if metrics.get('pe_ratio', 30) < 15:
            reasons.append("undervalued")
        if metrics.get('revenue_growth', 0) > 0.2:
            reasons.append("high growth")
        if metrics.get('debt_to_equity', 1) < 0.3:
            reasons.append("low debt")
            
        return ", ".join(reasons)
    
    def _generate_error_result(self, error_msg: str) -> Dict[str, Any]:
        """Generate error result"""
        return {
            "recommendation": {"action": "HOLD", "confidence": 0.0, "timeframe": "medium"},
            "analysis": {"error": error_msg},
            "risk_assessment": {"risk_level": "HIGH"},
            "confidence": 0.0
        }