"""
Shorgan-Bot Catalyst Trading Agent
Specialized agent focused on catalyst-driven short-term trading in micro-cap to mid-cap stocks
"""

from .base_agent import BaseAgent
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import requests
import pandas as pd
import numpy as np
import logging
import sys
import os

# Import data sources
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'automation'))

# Tiingo API (primary price data source)
try:
    from tiingo_integration import TiingoAPI
    TIINGO_AVAILABLE = True
except ImportError:
    TIINGO_AVAILABLE = False

# Financial Datasets API (fundamentals, not prices)
try:
    from financial_datasets_integration import FinancialDatasetsAPI
    FD_API_AVAILABLE = True
except ImportError:
    FD_API_AVAILABLE = False

class ShorganCatalystAgent(BaseAgent):
    """
    Shorgan-Bot specialized catalyst trading agent
    
    Strategy Focus:
    - Micro-cap to mid-cap stocks (<$20B market cap)
    - 1-30 day catalyst-driven events
    - Maximum return optimization
    - Short-term momentum and technical breakouts
    """
    
    def __init__(self):
        super().__init__(
            agent_id="shorgan_catalyst_001",
            agent_type="catalyst_trader"
        )
        
        # Initialize Tiingo API (primary for prices)
        if TIINGO_AVAILABLE:
            self.tiingo_api = TiingoAPI()
        else:
            self.tiingo_api = None
            self.logger.warning("Tiingo API not available")
        
        # Initialize Financial Datasets API (for fundamentals)
        if FD_API_AVAILABLE:
            self.fd_api = FinancialDatasetsAPI()
        else:
            self.fd_api = None
        
        # Strategy parameters
        self.max_market_cap = 20_000_000_000  # $20B max market cap
        self.min_volume = 100_000  # Minimum daily volume
        self.max_position_risk = 0.05  # 5% max position risk
        self.timeframe_days = 30  # Maximum holding period
        
        # Catalyst categories to focus on
        self.catalyst_types = [
            "earnings_surprise",
            "contract_announcement",
            "fda_approval",
            "merger_acquisition",
            "insider_buying",
            "analyst_upgrade",
            "breakthrough_news",
            "technical_breakout"
        ]
        
    def analyze(self, ticker: str, market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Analyze stock for catalyst-driven trading opportunity
        
        Args:
            ticker: Stock symbol to analyze
            market_data: Current market data
            **kwargs: Additional parameters (catalyst_data, news_data, etc.)
            
        Returns:
            Analysis results with recommendation
        """
        try:
            # Validate market data
            if not self.validate_market_data(market_data):
                return self._generate_error_result("Invalid market data")
            
            # Check market cap filter
            if not self._check_market_cap_filter(market_data):
                return self._generate_skip_result("Market cap exceeds limit")
            
            # Perform catalyst analysis
            catalyst_score = self._analyze_catalysts(ticker, kwargs.get('catalyst_data', {}))
            
            # Technical analysis for entry timing
            technical_score = self._technical_analysis(ticker, market_data)
            
            # Risk assessment
            risk_metrics = self._calculate_risk(ticker, market_data)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                catalyst_score, 
                technical_score, 
                risk_metrics
            )
            
            # Create analysis result
            analysis_result = {
                "recommendation": recommendation,
                "analysis": {
                    "catalyst_score": catalyst_score,
                    "technical_score": technical_score,
                    "market_cap": market_data.get('market_cap', 0),
                    "volume_score": self._volume_score(market_data.get('volume', 0)),
                    "key_factors": self._identify_key_factors(catalyst_score, technical_score)
                },
                "risk_assessment": risk_metrics,
                "confidence": self._calculate_confidence(catalyst_score, technical_score, risk_metrics)
            }
            
            self.log_analysis(ticker, analysis_result)
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Analysis failed for {ticker}: {str(e)}")
            return self._generate_error_result(f"Analysis error: {str(e)}")
    
    def _check_market_cap_filter(self, market_data: Dict[str, Any]) -> bool:
        """Check if stock meets market cap criteria"""
        market_cap = market_data.get('market_cap', float('inf'))
        return market_cap <= self.max_market_cap
    
    def _analyze_catalysts(self, ticker: str, catalyst_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze catalyst potential for the stock
        
        Returns:
            Dict with catalyst analysis and scoring
        """
        catalyst_score = {
            "total_score": 0.0,
            "detected_catalysts": [],
            "catalyst_strength": "NONE"
        }
        
        # Check for recent news catalysts
        recent_news = catalyst_data.get('news', [])
        for news_item in recent_news:
            catalyst_type = self._classify_news_catalyst(news_item)
            if catalyst_type:
                strength = self._score_catalyst_strength(news_item, catalyst_type)
                catalyst_score["detected_catalysts"].append({
                    "type": catalyst_type,
                    "strength": strength,
                    "headline": news_item.get('title', ''),
                    "date": news_item.get('date', '')
                })
                catalyst_score["total_score"] += strength
        
        # Check for upcoming events
        upcoming_events = catalyst_data.get('events', [])
        for event in upcoming_events:
            if self._is_relevant_event(event):
                event_score = self._score_upcoming_event(event)
                catalyst_score["total_score"] += event_score
                catalyst_score["detected_catalysts"].append({
                    "type": "upcoming_event",
                    "strength": event_score,
                    "event": event.get('type', ''),
                    "date": event.get('date', '')
                })
        
        # Determine overall catalyst strength
        if catalyst_score["total_score"] >= 0.8:
            catalyst_score["catalyst_strength"] = "VERY_HIGH"
        elif catalyst_score["total_score"] >= 0.6:
            catalyst_score["catalyst_strength"] = "HIGH"
        elif catalyst_score["total_score"] >= 0.4:
            catalyst_score["catalyst_strength"] = "MEDIUM"
        elif catalyst_score["total_score"] >= 0.2:
            catalyst_score["catalyst_strength"] = "LOW"
        
        return catalyst_score
    
    def _technical_analysis(self, ticker: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform technical analysis for entry timing
        
        Returns:
            Technical analysis scores and indicators
        """
        try:
            # Get recent price data from Tiingo API
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            hist = pd.DataFrame()
            
            if self.tiingo_api:
                hist = self.tiingo_api.get_historical_prices(ticker, interval='day', start_date=start_date, end_date=end_date)
                # Tiingo integration already returns capitalized columns
            
            if hist.empty:
                return {"score": 0.0, "indicators": {}, "error": "No price data from Tiingo API"}
            
            current_price = market_data.get('price', hist['Close'].iloc[-1])
            
            # Calculate technical indicators
            sma_20 = hist['Close'].rolling(20).mean().iloc[-1] if len(hist) >= 20 else current_price
            volume_avg = hist['Volume'].mean()
            current_volume = market_data.get('volume', hist['Volume'].iloc[-1])
            
            # Price momentum (5-day vs 20-day)
            price_5d_avg = hist['Close'].tail(5).mean()
            momentum_score = (price_5d_avg - sma_20) / sma_20 if sma_20 > 0 else 0
            
            # Volume surge detection
            volume_surge = (current_volume - volume_avg) / volume_avg if volume_avg > 0 else 0
            
            # Breakout detection
            high_20d = hist['High'].rolling(20).max().iloc[-1] if len(hist) >= 20 else current_price
            breakout_score = (current_price - high_20d) / high_20d if high_20d > 0 else 0
            
            # Overall technical score
            technical_score = (
                max(0, momentum_score) * 0.4 +  # Positive momentum
                min(1, max(0, volume_surge)) * 0.3 +  # Volume surge
                max(0, breakout_score) * 0.3  # Breakout potential
            )
            
            return {
                "score": min(1.0, technical_score),
                "indicators": {
                    "momentum_score": momentum_score,
                    "volume_surge": volume_surge,
                    "breakout_score": breakout_score,
                    "current_price": current_price,
                    "sma_20": sma_20,
                    "volume_ratio": current_volume / volume_avg if volume_avg > 0 else 0
                }
            }
            
        except Exception as e:
            self.logger.warning(f"Technical analysis failed for {ticker}: {str(e)}")
            return {"score": 0.0, "indicators": {}, "error": str(e)}
    
    def _calculate_risk(self, ticker: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate risk metrics for the position
        
        Returns:
            Risk assessment with stop-loss and position sizing
        """
        current_price = market_data.get('price', 0)
        volume = market_data.get('volume', 0)
        
        # Calculate volatility-based risk
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="30d")
            if not hist.empty:
                returns = hist['Close'].pct_change().dropna()
                volatility = returns.std() * (252 ** 0.5)  # Annualized volatility
            else:
                volatility = 0.3  # Default assumption
        except:
            volatility = 0.3
        
        # Risk level determination
        if volatility > 0.6:
            risk_level = "HIGH"
            stop_loss_pct = 0.08  # 8% stop loss for high volatility
        elif volatility > 0.4:
            risk_level = "MEDIUM"
            stop_loss_pct = 0.06  # 6% stop loss for medium volatility
        else:
            risk_level = "LOW"
            stop_loss_pct = 0.04  # 4% stop loss for low volatility
        
        # Calculate stop loss and take profit levels
        stop_loss_price = current_price * (1 - stop_loss_pct)
        take_profit_price = current_price * (1 + (stop_loss_pct * 2))  # 2:1 risk/reward
        
        return {
            "risk_level": risk_level,
            "volatility": volatility,
            "stop_loss": stop_loss_price,
            "take_profit": take_profit_price,
            "stop_loss_pct": stop_loss_pct,
            "position_size_pct": min(self.max_position_risk, 0.05 / volatility)  # Volatility-adjusted sizing
        }
    
    def _generate_recommendation(self, catalyst_score: Dict, technical_score: Dict, risk_metrics: Dict) -> Dict[str, Any]:
        """
        Generate trading recommendation based on all analysis
        
        Returns:
            Trading recommendation with action, confidence, and timeframe
        """
        # Calculate combined score
        catalyst_weight = 0.6  # Catalyst analysis is primary
        technical_weight = 0.4  # Technical analysis is secondary
        
        combined_score = (
            catalyst_score["total_score"] * catalyst_weight +
            technical_score["score"] * technical_weight
        )
        
        # Determine action based on combined score and risk
        if combined_score >= 0.7 and risk_metrics["risk_level"] != "HIGH":
            action = "BUY"
            confidence = min(0.95, combined_score)
            timeframe = "short"  # 1-7 days for high-confidence catalyst plays
        elif combined_score >= 0.5:
            action = "BUY"
            confidence = combined_score
            timeframe = "medium"  # 7-30 days for moderate catalyst plays
        elif combined_score <= 0.3:
            action = "SELL" if combined_score < 0.2 else "HOLD"
            confidence = 1 - combined_score
            timeframe = "short"
        else:
            action = "HOLD"
            confidence = 0.5
            timeframe = "medium"
        
        return {
            "action": action,
            "confidence": confidence,
            "timeframe": timeframe,
            "combined_score": combined_score,
            "reasoning": self._generate_reasoning(catalyst_score, technical_score, risk_metrics, action)
        }
    
    def _generate_reasoning(self, catalyst_score: Dict, technical_score: Dict, risk_metrics: Dict, action: str) -> str:
        """Generate human-readable reasoning for the recommendation"""
        reasoning_parts = []
        
        # Catalyst reasoning
        if catalyst_score["catalyst_strength"] in ["VERY_HIGH", "HIGH"]:
            reasoning_parts.append(f"Strong catalyst detected ({catalyst_score['catalyst_strength']})")
        elif catalyst_score["total_score"] > 0.3:
            reasoning_parts.append(f"Moderate catalyst potential")
        else:
            reasoning_parts.append("Limited catalyst activity")
        
        # Technical reasoning
        if technical_score["score"] > 0.6:
            reasoning_parts.append("favorable technical setup")
        elif technical_score["score"] > 0.3:
            reasoning_parts.append("neutral technical indicators")
        else:
            reasoning_parts.append("weak technical setup")
        
        # Risk reasoning
        reasoning_parts.append(f"{risk_metrics['risk_level'].lower()} risk profile")
        
        return f"{action} recommendation based on: " + ", ".join(reasoning_parts)
    
    def _classify_news_catalyst(self, news_item: Dict[str, Any]) -> Optional[str]:
        """Classify news item as potential catalyst"""
        title = news_item.get('title', '').lower()
        content = news_item.get('content', '').lower()
        text = f"{title} {content}"
        
        # Keyword matching for catalyst classification
        catalyst_keywords = {
            "earnings_surprise": ["earnings", "beat", "surprise", "revenue"],
            "contract_announcement": ["contract", "deal", "agreement", "partnership"],
            "fda_approval": ["fda", "approval", "clinical", "trial", "drug"],
            "merger_acquisition": ["merger", "acquisition", "buyout", "takeover"],
            "insider_buying": ["insider", "buying", "director", "ceo"],
            "analyst_upgrade": ["upgrade", "price target", "analyst", "recommendation"],
            "breakthrough_news": ["breakthrough", "innovation", "patent", "technology"]
        }
        
        for catalyst_type, keywords in catalyst_keywords.items():
            if any(keyword in text for keyword in keywords):
                return catalyst_type
        
        return None
    
    def _score_catalyst_strength(self, news_item: Dict, catalyst_type: str) -> float:
        """Score the strength of a detected catalyst"""
        base_scores = {
            "earnings_surprise": 0.8,
            "contract_announcement": 0.7,
            "fda_approval": 0.9,
            "merger_acquisition": 0.9,
            "insider_buying": 0.5,
            "analyst_upgrade": 0.6,
            "breakthrough_news": 0.7
        }
        
        # Adjust score based on recency (news within 24 hours gets full score)
        hours_old = self._calculate_news_age_hours(news_item.get('date', ''))
        recency_multiplier = max(0.3, 1.0 - (hours_old / 168))  # Decay over 1 week
        
        return base_scores.get(catalyst_type, 0.5) * recency_multiplier
    
    def _calculate_news_age_hours(self, news_date: str) -> float:
        """Calculate how many hours old the news is"""
        try:
            if not news_date:
                return 48.0  # Default to 48 hours if no date
            
            news_time = datetime.fromisoformat(news_date.replace('Z', '+00:00'))
            age = datetime.now() - news_time.replace(tzinfo=None)
            return age.total_seconds() / 3600
        except:
            return 48.0
    
    def _is_relevant_event(self, event: Dict[str, Any]) -> bool:
        """Check if upcoming event is relevant for catalyst trading"""
        event_type = event.get('type', '').lower()
        relevant_events = ['earnings', 'fda', 'conference', 'presentation', 'announcement']
        return any(relevant in event_type for relevant in relevant_events)
    
    def _score_upcoming_event(self, event: Dict[str, Any]) -> float:
        """Score upcoming events for catalyst potential"""
        event_type = event.get('type', '').lower()
        
        # Days until event
        try:
            event_date = datetime.fromisoformat(event.get('date', ''))
            days_until = (event_date - datetime.now()).days
        except:
            days_until = 30
        
        # Score based on event type and timing
        base_scores = {
            'earnings': 0.8,
            'fda': 0.9,
            'conference': 0.4,
            'presentation': 0.3,
            'announcement': 0.6
        }
        
        event_score = base_scores.get(event_type, 0.3)
        
        # Optimal timing is 1-7 days out
        if 1 <= days_until <= 7:
            timing_multiplier = 1.0
        elif days_until <= 14:
            timing_multiplier = 0.8
        elif days_until <= 30:
            timing_multiplier = 0.6
        else:
            timing_multiplier = 0.3
        
        return event_score * timing_multiplier
    
    def _volume_score(self, current_volume: float) -> float:
        """Score volume relative to minimum threshold"""
        if current_volume >= self.min_volume:
            return min(1.0, current_volume / (self.min_volume * 3))
        else:
            return current_volume / self.min_volume
    
    def _identify_key_factors(self, catalyst_score: Dict, technical_score: Dict) -> List[str]:
        """Identify key factors driving the recommendation"""
        factors = []
        
        if catalyst_score["total_score"] > 0.6:
            factors.append(f"Strong catalyst: {catalyst_score['catalyst_strength']}")
        
        if technical_score["score"] > 0.6:
            factors.append("Favorable technical setup")
        
        if len(catalyst_score["detected_catalysts"]) > 0:
            factors.append(f"{len(catalyst_score['detected_catalysts'])} catalysts detected")
        
        # Add specific technical factors
        indicators = technical_score.get("indicators", {})
        if indicators.get("volume_surge", 0) > 0.5:
            factors.append("Volume surge detected")
        if indicators.get("breakout_score", 0) > 0.1:
            factors.append("Technical breakout potential")
        
        return factors
    
    def _calculate_confidence(self, catalyst_score: Dict, technical_score: Dict, risk_metrics: Dict) -> float:
        """Calculate overall confidence in the recommendation"""
        # Base confidence from scores
        base_confidence = (catalyst_score["total_score"] * 0.6 + technical_score["score"] * 0.4)
        
        # Adjust for risk
        risk_adjustment = {
            "LOW": 1.0,
            "MEDIUM": 0.9,
            "HIGH": 0.7
        }.get(risk_metrics["risk_level"], 0.8)
        
        # Adjust for number of catalysts (more catalysts = higher confidence)
        catalyst_count_bonus = min(0.2, len(catalyst_score.get("detected_catalysts", [])) * 0.05)
        
        final_confidence = min(0.95, (base_confidence * risk_adjustment) + catalyst_count_bonus)
        return max(0.05, final_confidence)  # Minimum 5% confidence
    
    def _generate_error_result(self, error_msg: str) -> Dict[str, Any]:
        """Generate error result structure"""
        return {
            "recommendation": {"action": "HOLD", "confidence": 0.0, "timeframe": "medium"},
            "analysis": {"error": error_msg},
            "risk_assessment": {"risk_level": "HIGH"},
            "confidence": 0.0
        }
    
    def _generate_skip_result(self, reason: str) -> Dict[str, Any]:
        """Generate skip result for filtered stocks"""
        return {
            "recommendation": {"action": "SKIP", "confidence": 0.0, "timeframe": "N/A"},
            "analysis": {"skip_reason": reason},
            "risk_assessment": {"risk_level": "N/A"},
            "confidence": 0.0
        }