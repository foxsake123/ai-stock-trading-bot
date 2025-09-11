"""
Catalyst Detection System for Shorgan-Bot
Identifies and analyzes short-term catalysts for trading opportunities
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import yfinance as yf
from bs4 import BeautifulSoup
import re

class CatalystDetector:
    """
    Detects and analyzes various types of catalysts for short-term trading
    """
    
    def __init__(self):
        self.logger = logging.getLogger("catalyst.detector")
        
        # Catalyst scoring weights
        self.catalyst_weights = {
            "earnings_beat": 0.9,
            "fda_approval": 0.95,
            "major_contract": 0.85,
            "analyst_upgrade": 0.7,
            "insider_buying": 0.6,
            "technical_breakout": 0.65,
            "short_squeeze": 0.8,
            "merger_acquisition": 0.9,
            "product_launch": 0.75,
            "partnership": 0.7
        }
        
        # Time decay factors (how quickly catalyst impact fades)
        self.time_decay_rates = {
            "earnings_beat": 0.2,      # Fades quickly (5 days)
            "fda_approval": 0.1,        # Lasts longer (10 days)
            "major_contract": 0.15,     # Medium duration (7 days)
            "analyst_upgrade": 0.25,    # Fades fast (4 days)
            "insider_buying": 0.1,      # Long-lasting signal
            "technical_breakout": 0.3,  # Very short-term (3 days)
            "short_squeeze": 0.4,       # Extremely short (2-3 days)
            "merger_acquisition": 0.05, # Very long-lasting
            "product_launch": 0.2,      # Medium fade
            "partnership": 0.15         # Medium duration
        }
    
    def detect_catalysts(self, ticker: str) -> Dict[str, Any]:
        """
        Detect all potential catalysts for a given ticker
        
        Args:
            ticker: Stock symbol to analyze
            
        Returns:
            Dict containing detected catalysts and analysis
        """
        catalysts = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "detected_catalysts": [],
            "total_score": 0.0,
            "recommendation": "HOLD",
            "urgency": "LOW"
        }
        
        # Run all catalyst detection methods
        catalysts_found = []
        
        # Check earnings catalysts
        earnings_catalyst = self._check_earnings_catalyst(ticker)
        if earnings_catalyst:
            catalysts_found.append(earnings_catalyst)
        
        # Check news catalysts
        news_catalysts = self._check_news_catalysts(ticker)
        catalysts_found.extend(news_catalysts)
        
        # Check technical catalysts
        technical_catalyst = self._check_technical_catalyst(ticker)
        if technical_catalyst:
            catalysts_found.append(technical_catalyst)
        
        # Check insider activity
        insider_catalyst = self._check_insider_activity(ticker)
        if insider_catalyst:
            catalysts_found.append(insider_catalyst)
        
        # Check short interest for squeeze potential
        squeeze_catalyst = self._check_short_squeeze_potential(ticker)
        if squeeze_catalyst:
            catalysts_found.append(squeeze_catalyst)
        
        # Calculate combined score and recommendation
        if catalysts_found:
            catalysts["detected_catalysts"] = catalysts_found
            catalysts["total_score"] = self._calculate_combined_score(catalysts_found)
            catalysts["recommendation"] = self._generate_recommendation(catalysts["total_score"])
            catalysts["urgency"] = self._calculate_urgency(catalysts_found)
        
        return catalysts
    
    def _check_earnings_catalyst(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Check for earnings-related catalysts
        
        Returns:
            Catalyst dict if found, None otherwise
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Check earnings dates
            earnings_dates = stock.earnings_dates
            if earnings_dates is not None and not earnings_dates.empty:
                # Get next earnings date
                future_dates = earnings_dates[earnings_dates.index > datetime.now()]
                if not future_dates.empty:
                    next_earnings = future_dates.index[0]
                    days_until = (next_earnings - datetime.now()).days
                    
                    if days_until <= 30:  # Within our 30-day timeframe
                        return {
                            "type": "earnings_announcement",
                            "date": next_earnings.isoformat(),
                            "days_until": days_until,
                            "strength": self._calculate_earnings_strength(days_until),
                            "description": f"Earnings announcement in {days_until} days"
                        }
            
            # Check for recent earnings beat
            earnings_history = stock.earnings_history
            if earnings_history is not None and not earnings_history.empty:
                latest = earnings_history.iloc[-1]
                if 'epsActual' in latest and 'epsEstimate' in latest:
                    beat_pct = (latest['epsActual'] - latest['epsEstimate']) / abs(latest['epsEstimate']) if latest['epsEstimate'] != 0 else 0
                    
                    if beat_pct > 0.1:  # 10% earnings beat
                        return {
                            "type": "earnings_beat",
                            "strength": min(1.0, beat_pct * 2),
                            "beat_percentage": beat_pct,
                            "description": f"Recent earnings beat by {beat_pct:.1%}"
                        }
            
        except Exception as e:
            self.logger.warning(f"Error checking earnings catalyst for {ticker}: {str(e)}")
        
        return None
    
    def _check_news_catalysts(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Check for news-based catalysts
        
        Returns:
            List of news catalysts found
        """
        catalysts = []
        
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if news:
                for article in news[:10]:  # Check last 10 news items
                    catalyst_type = self._classify_news_catalyst(article)
                    if catalyst_type:
                        # Calculate age of news
                        pub_time = datetime.fromtimestamp(article.get('providerPublishTime', 0))
                        age_hours = (datetime.now() - pub_time).total_seconds() / 3600
                        
                        if age_hours < 72:  # Within 3 days
                            catalysts.append({
                                "type": catalyst_type,
                                "title": article.get('title', ''),
                                "publisher": article.get('publisher', ''),
                                "age_hours": age_hours,
                                "strength": self._calculate_news_strength(catalyst_type, age_hours),
                                "link": article.get('link', ''),
                                "description": article.get('title', '')[:100]
                            })
            
        except Exception as e:
            self.logger.warning(f"Error checking news catalysts for {ticker}: {str(e)}")
        
        return catalysts
    
    def _check_technical_catalyst(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Check for technical breakout catalysts
        
        Returns:
            Technical catalyst if found
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="30d")
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            
            # Check for breakout above 20-day high
            high_20d = hist['High'].rolling(20).max().iloc[-1] if len(hist) >= 20 else 0
            
            if high_20d > 0 and current_price > high_20d * 1.02:  # 2% above 20-day high
                breakout_strength = (current_price - high_20d) / high_20d
                
                # Check volume confirmation
                avg_volume = hist['Volume'].mean()
                current_volume = hist['Volume'].iloc[-1]
                volume_surge = current_volume / avg_volume if avg_volume > 0 else 1
                
                if volume_surge > 1.5:  # Volume confirmation
                    return {
                        "type": "technical_breakout",
                        "breakout_level": high_20d,
                        "current_price": current_price,
                        "breakout_percentage": breakout_strength,
                        "volume_surge": volume_surge,
                        "strength": min(1.0, breakout_strength * 10 * (volume_surge / 2)),
                        "description": f"Technical breakout above ${high_20d:.2f} with {volume_surge:.1f}x volume"
                    }
            
            # Check for momentum surge
            if len(hist) >= 5:
                momentum_5d = (current_price - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]
                
                if momentum_5d > 0.15:  # 15% gain in 5 days
                    return {
                        "type": "momentum_surge",
                        "momentum_5d": momentum_5d,
                        "strength": min(1.0, momentum_5d * 3),
                        "description": f"Strong momentum: {momentum_5d:.1%} gain in 5 days"
                    }
            
        except Exception as e:
            self.logger.warning(f"Error checking technical catalyst for {ticker}: {str(e)}")
        
        return None
    
    def _check_insider_activity(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Check for insider buying activity
        
        Returns:
            Insider catalyst if significant activity found
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Check insider transactions
            insider_transactions = stock.insider_transactions
            if insider_transactions is not None and not insider_transactions.empty:
                # Filter for recent purchases
                recent_purchases = insider_transactions[
                    insider_transactions['Transaction'].str.contains('Buy', case=False, na=False)
                ]
                
                if not recent_purchases.empty:
                    total_value = recent_purchases['Value'].sum() if 'Value' in recent_purchases.columns else 0
                    
                    if total_value > 100000:  # Significant insider buying
                        return {
                            "type": "insider_buying",
                            "total_value": total_value,
                            "transaction_count": len(recent_purchases),
                            "strength": min(1.0, total_value / 1000000),  # Scale by millions
                            "description": f"Insider buying: ${total_value:,.0f} across {len(recent_purchases)} transactions"
                        }
            
        except Exception as e:
            self.logger.warning(f"Error checking insider activity for {ticker}: {str(e)}")
        
        return None
    
    def _check_short_squeeze_potential(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Check for short squeeze potential
        
        Returns:
            Short squeeze catalyst if conditions are met
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get short interest data
            short_pct = info.get('shortPercentOfFloat', 0)
            short_ratio = info.get('shortRatio', 0)
            
            if short_pct > 0.20:  # More than 20% short interest
                # Check for recent price momentum
                hist = stock.history(period="5d")
                if not hist.empty:
                    momentum = (hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]
                    
                    if momentum > 0.10:  # 10% gain with high short interest
                        squeeze_score = short_pct * (1 + momentum) * 2
                        
                        return {
                            "type": "short_squeeze",
                            "short_percent": short_pct,
                            "short_ratio": short_ratio,
                            "recent_momentum": momentum,
                            "strength": min(1.0, squeeze_score),
                            "description": f"Short squeeze potential: {short_pct:.1%} short with {momentum:.1%} momentum"
                        }
            
        except Exception as e:
            self.logger.warning(f"Error checking short squeeze for {ticker}: {str(e)}")
        
        return None
    
    def _classify_news_catalyst(self, article: Dict[str, Any]) -> Optional[str]:
        """
        Classify news article as a potential catalyst type
        
        Returns:
            Catalyst type or None
        """
        title = article.get('title', '').lower()
        
        # Catalyst keywords mapping
        catalyst_patterns = {
            "fda_approval": ["fda", "approval", "approved", "clearance"],
            "major_contract": ["contract", "deal", "agreement", "awarded", "wins"],
            "analyst_upgrade": ["upgrade", "raises", "target", "buy rating", "outperform"],
            "merger_acquisition": ["merger", "acquisition", "acquire", "buyout", "takeover"],
            "product_launch": ["launch", "release", "unveil", "introduce", "debut"],
            "partnership": ["partnership", "collaboration", "joint venture", "alliance"]
        }
        
        for catalyst_type, keywords in catalyst_patterns.items():
            if any(keyword in title for keyword in keywords):
                return catalyst_type
        
        return None
    
    def _calculate_earnings_strength(self, days_until: int) -> float:
        """
        Calculate strength of earnings catalyst based on timing
        
        Args:
            days_until: Days until earnings
            
        Returns:
            Strength score between 0 and 1
        """
        if days_until <= 2:
            return 1.0  # Maximum strength right before earnings
        elif days_until <= 7:
            return 0.8
        elif days_until <= 14:
            return 0.6
        elif days_until <= 30:
            return 0.4
        else:
            return 0.2
    
    def _calculate_news_strength(self, catalyst_type: str, age_hours: float) -> float:
        """
        Calculate news catalyst strength based on type and age
        
        Args:
            catalyst_type: Type of news catalyst
            age_hours: Age of news in hours
            
        Returns:
            Strength score between 0 and 1
        """
        base_weight = self.catalyst_weights.get(catalyst_type, 0.5)
        decay_rate = self.time_decay_rates.get(catalyst_type, 0.2)
        
        # Calculate time decay
        decay_factor = max(0.3, 1.0 - (age_hours / 24) * decay_rate)
        
        return base_weight * decay_factor
    
    def _calculate_combined_score(self, catalysts: List[Dict[str, Any]]) -> float:
        """
        Calculate combined score from multiple catalysts
        
        Args:
            catalysts: List of detected catalysts
            
        Returns:
            Combined score between 0 and 1
        """
        if not catalysts:
            return 0.0
        
        # Weight recent catalysts more heavily
        total_score = 0.0
        for catalyst in catalysts:
            strength = catalyst.get('strength', 0.5)
            total_score += strength
        
        # Apply multiplier for multiple catalysts (synergy effect)
        if len(catalysts) > 1:
            multiplier = 1 + (len(catalysts) - 1) * 0.2  # 20% bonus per additional catalyst
            total_score *= multiplier
        
        return min(1.0, total_score)
    
    def _generate_recommendation(self, score: float) -> str:
        """
        Generate trading recommendation based on catalyst score
        
        Args:
            score: Combined catalyst score
            
        Returns:
            Trading recommendation
        """
        if score >= 0.8:
            return "STRONG_BUY"
        elif score >= 0.6:
            return "BUY"
        elif score >= 0.4:
            return "WATCH"
        elif score >= 0.2:
            return "HOLD"
        else:
            return "AVOID"
    
    def _calculate_urgency(self, catalysts: List[Dict[str, Any]]) -> str:
        """
        Calculate urgency level based on catalyst timing
        
        Args:
            catalysts: List of detected catalysts
            
        Returns:
            Urgency level (IMMEDIATE, HIGH, MEDIUM, LOW)
        """
        if not catalysts:
            return "LOW"
        
        # Check for immediate catalysts
        for catalyst in catalysts:
            if catalyst.get('type') in ['technical_breakout', 'short_squeeze']:
                return "IMMEDIATE"
            
            if catalyst.get('type') == 'earnings_announcement':
                days_until = catalyst.get('days_until', 30)
                if days_until <= 2:
                    return "IMMEDIATE"
                elif days_until <= 7:
                    return "HIGH"
            
            age_hours = catalyst.get('age_hours', 72)
            if age_hours < 6:
                return "HIGH"
        
        return "MEDIUM"