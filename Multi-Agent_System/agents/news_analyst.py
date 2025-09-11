"""
News Analyst Agent
Monitors and analyzes real-time news for market-moving events
"""

from .base_agent import BaseAgent
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
import re

class NewsAnalystAgent(BaseAgent):
    """
    Analyzes news sentiment and impact on stock prices
    """
    
    def __init__(self):
        super().__init__(
            agent_id="news_analyst_001",
            agent_type="news_analyst"
        )
        
        # News impact keywords and weights
        self.positive_keywords = {
            "breakthrough": 0.9, "record": 0.8, "beat": 0.8, "upgrade": 0.8,
            "approval": 0.9, "contract": 0.7, "partnership": 0.7, "expansion": 0.7,
            "profit": 0.7, "growth": 0.6, "innovation": 0.6, "success": 0.6,
            "strong": 0.5, "positive": 0.5, "gain": 0.5, "surge": 0.7,
            "acquisition": 0.6, "merger": 0.6, "deal": 0.6, "wins": 0.7
        }
        
        self.negative_keywords = {
            "lawsuit": -0.8, "recall": -0.9, "bankruptcy": -1.0, "fraud": -1.0,
            "investigation": -0.7, "downgrade": -0.8, "loss": -0.7, "decline": -0.6,
            "cut": -0.6, "layoff": -0.7, "warning": -0.6, "miss": -0.7,
            "failure": -0.8, "scandal": -0.9, "violation": -0.7, "concern": -0.5,
            "weak": -0.5, "negative": -0.5, "fall": -0.5, "crash": -0.8
        }
        
        # News source credibility weights
        self.source_weights = {
            "reuters": 1.0, "bloomberg": 1.0, "wsj": 0.95, "cnbc": 0.9,
            "marketwatch": 0.85, "seekingalpha": 0.7, "yahoo": 0.7,
            "twitter": 0.5, "reddit": 0.4, "unknown": 0.3
        }
        
    def analyze(self, ticker: str, market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Analyze news impact for the stock
        
        Args:
            ticker: Stock symbol
            market_data: Current market data
            news_data: Recent news articles
            
        Returns:
            News analysis and recommendation
        """
        try:
            news_data = kwargs.get('news_data', [])
            
            if not news_data:
                return self._generate_no_news_result()
            
            # Analyze each news item
            news_analyses = []
            for news_item in news_data:
                analysis = self._analyze_news_item(news_item, ticker)
                news_analyses.append(analysis)
            
            # Calculate aggregate sentiment
            aggregate_sentiment = self._calculate_aggregate_sentiment(news_analyses)
            
            # Identify key news events
            key_events = self._identify_key_events(news_analyses)
            
            # Assess news velocity (frequency and recency)
            news_velocity = self._calculate_news_velocity(news_analyses)
            
            # Generate news score
            news_score = self._calculate_news_score(
                aggregate_sentiment, 
                news_velocity, 
                key_events
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(news_score, key_events, aggregate_sentiment)
            
            # Risk assessment
            risk_assessment = self._assess_news_risk(news_score, key_events)
            
            analysis_result = {
                "recommendation": recommendation,
                "analysis": {
                    "news_score": news_score,
                    "sentiment": aggregate_sentiment,
                    "news_velocity": news_velocity,
                    "key_events": key_events,
                    "total_articles": len(news_analyses),
                    "recent_headlines": self._get_recent_headlines(news_analyses),
                    "key_factors": self._identify_key_factors(news_score, key_events, aggregate_sentiment)
                },
                "risk_assessment": risk_assessment,
                "confidence": self._calculate_confidence(news_score, len(news_analyses))
            }
            
            self.log_analysis(ticker, analysis_result)
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"News analysis failed for {ticker}: {str(e)}")
            return self._generate_error_result(f"Analysis error: {str(e)}")
    
    def _analyze_news_item(self, news_item: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """Analyze individual news item"""
        title = news_item.get('title', '').lower()
        content = news_item.get('content', '').lower()
        source = news_item.get('source', 'unknown').lower()
        published_date = news_item.get('published_date', datetime.now().isoformat())
        
        # Combine title and content for analysis
        full_text = f"{title} {content}"
        
        # Calculate sentiment score
        sentiment_score = self._calculate_sentiment(full_text)
        
        # Check if ticker is mentioned
        ticker_mentioned = ticker.lower() in full_text
        relevance = 1.0 if ticker_mentioned else 0.3
        
        # Identify news type
        news_type = self._classify_news_type(full_text)
        
        # Calculate recency weight
        recency_weight = self._calculate_recency_weight(published_date)
        
        # Get source credibility
        source_weight = self.source_weights.get(source, 0.3)
        
        # Calculate weighted impact
        impact_score = sentiment_score * relevance * recency_weight * source_weight
        
        return {
            "title": news_item.get('title', ''),
            "source": source,
            "published_date": published_date,
            "sentiment_score": sentiment_score,
            "impact_score": impact_score,
            "relevance": relevance,
            "news_type": news_type,
            "ticker_mentioned": ticker_mentioned
        }
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score from text"""
        sentiment_score = 0.0
        word_count = 0
        
        # Check for positive keywords
        for keyword, weight in self.positive_keywords.items():
            count = text.count(keyword)
            if count > 0:
                sentiment_score += weight * count
                word_count += count
        
        # Check for negative keywords
        for keyword, weight in self.negative_keywords.items():
            count = text.count(keyword)
            if count > 0:
                sentiment_score += weight * count  # weight is already negative
                word_count += count
        
        # Normalize by word count
        if word_count > 0:
            sentiment_score = sentiment_score / word_count
        
        # Clamp to [-1, 1]
        return max(-1.0, min(1.0, sentiment_score))
    
    def _classify_news_type(self, text: str) -> str:
        """Classify the type of news"""
        if any(word in text for word in ['earnings', 'revenue', 'profit', 'eps']):
            return "earnings"
        elif any(word in text for word in ['merger', 'acquisition', 'buyout', 'takeover']):
            return "merger_acquisition"
        elif any(word in text for word in ['fda', 'approval', 'clinical', 'trial']):
            return "regulatory"
        elif any(word in text for word in ['contract', 'deal', 'partnership', 'agreement']):
            return "business_deal"
        elif any(word in text for word in ['lawsuit', 'investigation', 'fraud', 'scandal']):
            return "legal"
        elif any(word in text for word in ['upgrade', 'downgrade', 'analyst', 'rating']):
            return "analyst_rating"
        elif any(word in text for word in ['innovation', 'product', 'launch', 'technology']):
            return "product_news"
        else:
            return "general"
    
    def _calculate_recency_weight(self, published_date: str) -> float:
        """Calculate weight based on news recency"""
        try:
            news_time = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
            age_hours = (datetime.now() - news_time.replace(tzinfo=None)).total_seconds() / 3600
            
            if age_hours < 1:
                return 1.0  # Breaking news
            elif age_hours < 6:
                return 0.9
            elif age_hours < 24:
                return 0.7
            elif age_hours < 48:
                return 0.5
            elif age_hours < 72:
                return 0.3
            else:
                return 0.1
        except:
            return 0.5  # Default weight
    
    def _calculate_aggregate_sentiment(self, news_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate aggregate sentiment from all news"""
        if not news_analyses:
            return {"overall": 0.0, "positive": 0, "negative": 0, "neutral": 0}
        
        sentiments = [item['sentiment_score'] for item in news_analyses]
        impacts = [item['impact_score'] for item in news_analyses]
        
        # Weighted average by impact
        total_impact = sum(abs(i) for i in impacts)
        if total_impact > 0:
            weighted_sentiment = sum(s * abs(i) for s, i in zip(sentiments, impacts)) / total_impact
        else:
            weighted_sentiment = sum(sentiments) / len(sentiments)
        
        # Count sentiment types
        positive_count = sum(1 for s in sentiments if s > 0.1)
        negative_count = sum(1 for s in sentiments if s < -0.1)
        neutral_count = len(sentiments) - positive_count - negative_count
        
        return {
            "overall": weighted_sentiment,
            "positive": positive_count,
            "negative": negative_count,
            "neutral": neutral_count,
            "strength": abs(weighted_sentiment)
        }
    
    def _identify_key_events(self, news_analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify the most impactful news events"""
        # Sort by absolute impact score
        sorted_news = sorted(news_analyses, key=lambda x: abs(x['impact_score']), reverse=True)
        
        key_events = []
        for news in sorted_news[:5]:  # Top 5 events
            if abs(news['impact_score']) > 0.3:  # Significant impact threshold
                key_events.append({
                    "headline": news['title'],
                    "type": news['news_type'],
                    "impact": news['impact_score'],
                    "sentiment": news['sentiment_score'],
                    "source": news['source']
                })
        
        return key_events
    
    def _calculate_news_velocity(self, news_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate news velocity (frequency and recency)"""
        if not news_analyses:
            return {"velocity": 0.0, "recent_count": 0, "trend": "stable"}
        
        # Count recent news (last 24 hours)
        recent_count = 0
        very_recent_count = 0
        
        for news in news_analyses:
            try:
                news_time = datetime.fromisoformat(news['published_date'].replace('Z', '+00:00'))
                age_hours = (datetime.now() - news_time.replace(tzinfo=None)).total_seconds() / 3600
                
                if age_hours < 24:
                    recent_count += 1
                    if age_hours < 6:
                        very_recent_count += 1
            except:
                continue
        
        # Calculate velocity score
        velocity = (recent_count * 0.5 + very_recent_count * 1.0) / max(1, len(news_analyses))
        
        # Determine trend
        if velocity > 0.5:
            trend = "accelerating"
        elif velocity > 0.2:
            trend = "active"
        else:
            trend = "stable"
        
        return {
            "velocity": velocity,
            "recent_count": recent_count,
            "very_recent_count": very_recent_count,
            "trend": trend
        }
    
    def _calculate_news_score(self, sentiment: Dict[str, Any], velocity: Dict[str, Any], 
                             key_events: List[Dict[str, Any]]) -> float:
        """Calculate overall news score"""
        # Base score from sentiment
        sentiment_score = (sentiment['overall'] + 1) / 2  # Convert [-1,1] to [0,1]
        
        # Adjust for velocity
        velocity_adjustment = velocity['velocity'] * 0.2
        
        # Adjust for key events
        if key_events:
            max_impact = max(abs(event['impact']) for event in key_events)
            event_adjustment = max_impact * 0.3
        else:
            event_adjustment = 0
        
        # Combine scores
        news_score = min(1.0, max(0.0, sentiment_score + velocity_adjustment + event_adjustment))
        
        return news_score
    
    def _generate_recommendation(self, news_score: float, key_events: List[Dict[str, Any]], 
                                sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading recommendation based on news analysis"""
        
        # Check for major events
        major_positive = any(event['impact'] > 0.6 for event in key_events)
        major_negative = any(event['impact'] < -0.6 for event in key_events)
        
        if major_positive and news_score > 0.6:
            action = "BUY"
            confidence = min(0.9, news_score)
            timeframe = "short"  # News impact is typically short-term
        elif major_negative and news_score < 0.4:
            action = "SELL"
            confidence = min(0.9, 1 - news_score)
            timeframe = "short"
        elif news_score > 0.65:
            action = "BUY"
            confidence = news_score * 0.8
            timeframe = "short"
        elif news_score < 0.35:
            action = "SELL"
            confidence = (1 - news_score) * 0.8
            timeframe = "short"
        else:
            action = "HOLD"
            confidence = 0.5
            timeframe = "medium"
        
        reasoning = self._generate_reasoning(news_score, sentiment, key_events)
        
        return {
            "action": action,
            "confidence": confidence,
            "timeframe": timeframe,
            "reasoning": reasoning
        }
    
    def _assess_news_risk(self, news_score: float, key_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess risk based on news"""
        
        # Check for high-impact negative news
        has_major_negative = any(event['impact'] < -0.5 for event in key_events)
        has_legal_issues = any(event['type'] == 'legal' for event in key_events)
        
        if has_major_negative or has_legal_issues:
            risk_level = "HIGH"
            position_size = 0.01
        elif abs(news_score - 0.5) < 0.2:  # Mixed signals
            risk_level = "MEDIUM"
            position_size = 0.02
        else:
            risk_level = "LOW"
            position_size = 0.03
        
        # News-driven trades need tighter stops
        stop_loss_pct = 0.03 if risk_level == "LOW" else 0.05
        
        return {
            "risk_level": risk_level,
            "stop_loss": 100 * (1 - stop_loss_pct),  # Placeholder price
            "take_profit": 100 * (1 + stop_loss_pct * 2),
            "position_size_pct": position_size,
            "volatility": 0.02  # News-driven volatility estimate
        }
    
    def _get_recent_headlines(self, news_analyses: List[Dict[str, Any]]) -> List[str]:
        """Get list of recent headlines"""
        sorted_news = sorted(news_analyses, 
                           key=lambda x: x.get('published_date', ''), 
                           reverse=True)
        return [news['title'] for news in sorted_news[:5]]
    
    def _identify_key_factors(self, news_score: float, key_events: List[Dict[str, Any]], 
                             sentiment: Dict[str, Any]) -> List[str]:
        """Identify key news factors"""
        factors = []
        
        if news_score > 0.7:
            factors.append("Strong positive news flow")
        elif news_score < 0.3:
            factors.append("Negative news sentiment")
        
        if sentiment['strength'] > 0.5:
            factors.append(f"High sentiment strength ({sentiment['strength']:.2f})")
        
        for event in key_events[:2]:
            if abs(event['impact']) > 0.5:
                factors.append(f"{event['type'].replace('_', ' ').title()}: {event['headline'][:30]}...")
        
        if sentiment['positive'] > sentiment['negative'] * 2:
            factors.append(f"{sentiment['positive']} positive articles")
        elif sentiment['negative'] > sentiment['positive'] * 2:
            factors.append(f"{sentiment['negative']} negative articles")
        
        return factors
    
    def _calculate_confidence(self, news_score: float, article_count: int) -> float:
        """Calculate confidence in news analysis"""
        # More articles = higher confidence
        article_confidence = min(1.0, article_count / 10)
        
        # Extreme scores = higher confidence
        score_confidence = abs(news_score - 0.5) * 2
        
        return min(0.95, (article_confidence * 0.4 + score_confidence * 0.6))
    
    def _generate_reasoning(self, score: float, sentiment: Dict[str, Any], 
                           key_events: List[Dict[str, Any]]) -> str:
        """Generate reasoning for recommendation"""
        reasons = []
        
        if score > 0.65:
            reasons.append("Positive news momentum")
        elif score < 0.35:
            reasons.append("Negative news pressure")
        else:
            reasons.append("Mixed news signals")
        
        if key_events:
            top_event = key_events[0]
            reasons.append(f"{top_event['type'].replace('_', ' ')}")
        
        if sentiment['overall'] > 0.3:
            reasons.append(f"{sentiment['positive']} positive headlines")
        elif sentiment['overall'] < -0.3:
            reasons.append(f"{sentiment['negative']} negative headlines")
        
        return ", ".join(reasons)
    
    def _generate_no_news_result(self) -> Dict[str, Any]:
        """Generate result when no news is available"""
        return {
            "recommendation": {"action": "HOLD", "confidence": 0.0, "timeframe": "medium"},
            "analysis": {"message": "No recent news available"},
            "risk_assessment": {"risk_level": "MEDIUM"},
            "confidence": 0.0
        }
    
    def _generate_error_result(self, error_msg: str) -> Dict[str, Any]:
        """Generate error result"""
        return {
            "recommendation": {"action": "HOLD", "confidence": 0.0, "timeframe": "medium"},
            "analysis": {"error": error_msg},
            "risk_assessment": {"risk_level": "HIGH"},
            "confidence": 0.0
        }