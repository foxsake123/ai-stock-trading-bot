"""
Sentiment Analyst Agent
Analyzes social media sentiment and retail investor behavior
"""

from .base_agent import BaseAgent
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
import re

class SentimentAnalystAgent(BaseAgent):
    """
    Analyzes social sentiment from various sources
    """
    
    def __init__(self):
        super().__init__(
            agent_id="sentiment_analyst_001",
            agent_type="sentiment_analyst"
        )
        
        # Sentiment thresholds
        self.bullish_threshold = 0.6
        self.bearish_threshold = 0.4
        
        # Social media platform weights
        self.platform_weights = {
            "twitter": 0.8,
            "reddit": 0.9,  # WSB has high impact
            "stocktwits": 0.7,
            "youtube": 0.5,
            "discord": 0.6
        }
        
        # Emoji sentiment mapping
        self.emoji_sentiment = {
            "🚀": 1.0, "🌙": 0.9, "💎": 0.8, "🙌": 0.7, "📈": 0.8,
            "🐂": 0.9, "💰": 0.7, "🔥": 0.6, "⬆️": 0.7, "💪": 0.6,
            "📉": -0.8, "🐻": -0.9, "💔": -0.7, "😱": -0.6, "⬇️": -0.7,
            "🚨": -0.5, "⚠️": -0.4, "😭": -0.6, "🤡": -0.5, "💩": -0.8
        }
        
    def analyze(self, ticker: str, market_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Analyze social sentiment for the stock
        
        Args:
            ticker: Stock symbol
            market_data: Current market data
            social_data: Social media data
            
        Returns:
            Sentiment analysis and recommendation
        """
        try:
            social_data = kwargs.get('social_data', {})
            
            # Analyze mentions volume
            mention_analysis = self._analyze_mention_volume(social_data, ticker)
            
            # Analyze sentiment from posts
            sentiment_scores = self._analyze_post_sentiment(social_data)
            
            # Analyze influencer activity
            influencer_impact = self._analyze_influencer_activity(social_data)
            
            # Analyze options flow sentiment
            options_sentiment = self._analyze_options_sentiment(kwargs.get('options_data', {}))
            
            # Calculate retail interest score
            retail_interest = self._calculate_retail_interest(
                mention_analysis, 
                sentiment_scores, 
                influencer_impact
            )
            
            # Generate overall sentiment score
            sentiment_score = self._calculate_sentiment_score(
                sentiment_scores, 
                mention_analysis, 
                influencer_impact,
                options_sentiment
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                sentiment_score, 
                retail_interest, 
                mention_analysis
            )
            
            # Risk assessment
            risk_assessment = self._assess_sentiment_risk(
                sentiment_score, 
                mention_analysis, 
                retail_interest
            )
            
            analysis_result = {
                "recommendation": recommendation,
                "analysis": {
                    "sentiment_score": sentiment_score,
                    "mention_volume": mention_analysis,
                    "sentiment_breakdown": sentiment_scores,
                    "influencer_impact": influencer_impact,
                    "retail_interest": retail_interest,
                    "options_sentiment": options_sentiment,
                    "key_factors": self._identify_key_factors(
                        sentiment_score, 
                        mention_analysis, 
                        retail_interest
                    )
                },
                "risk_assessment": risk_assessment,
                "confidence": self._calculate_confidence(sentiment_score, mention_analysis)
            }
            
            self.log_analysis(ticker, analysis_result)
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed for {ticker}: {str(e)}")
            return self._generate_error_result(f"Analysis error: {str(e)}")
    
    def _analyze_mention_volume(self, social_data: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """Analyze social media mention volume and trends"""
        mentions_by_platform = {}
        total_mentions = 0
        
        for platform, data in social_data.items():
            if isinstance(data, list):
                platform_mentions = len([post for post in data 
                                       if ticker.lower() in str(post).lower()])
                mentions_by_platform[platform] = platform_mentions
                total_mentions += platform_mentions
        
        # Calculate mention velocity (trending or not)
        recent_mentions = social_data.get('recent_mentions', 0)
        historical_avg = social_data.get('historical_avg_mentions', 1)
        
        if historical_avg > 0:
            mention_velocity = recent_mentions / historical_avg
        else:
            mention_velocity = 1.0
        
        # Determine if it's trending
        is_trending = mention_velocity > 2.0
        is_viral = mention_velocity > 5.0
        
        return {
            "total_mentions": total_mentions,
            "by_platform": mentions_by_platform,
            "mention_velocity": mention_velocity,
            "is_trending": is_trending,
            "is_viral": is_viral,
            "trend_strength": min(1.0, mention_velocity / 10)
        }
    
    def _analyze_post_sentiment(self, social_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment from social media posts"""
        platform_sentiments = {}
        all_sentiments = []
        
        for platform, posts in social_data.items():
            if isinstance(posts, list):
                platform_weight = self.platform_weights.get(platform, 0.5)
                sentiments = []
                
                for post in posts:
                    sentiment = self._calculate_post_sentiment(post)
                    sentiments.append(sentiment)
                    all_sentiments.append(sentiment * platform_weight)
                
                if sentiments:
                    platform_sentiments[platform] = sum(sentiments) / len(sentiments)
        
        # Calculate overall sentiment
        if all_sentiments:
            overall_sentiment = sum(all_sentiments) / len(all_sentiments)
            bullish_pct = len([s for s in all_sentiments if s > 0.2]) / len(all_sentiments)
            bearish_pct = len([s for s in all_sentiments if s < -0.2]) / len(all_sentiments)
        else:
            overall_sentiment = 0.0
            bullish_pct = 0.0
            bearish_pct = 0.0
        
        return {
            "overall": overall_sentiment,
            "by_platform": platform_sentiments,
            "bullish_percentage": bullish_pct,
            "bearish_percentage": bearish_pct,
            "neutral_percentage": 1.0 - bullish_pct - bearish_pct
        }
    
    def _calculate_post_sentiment(self, post: Any) -> float:
        """Calculate sentiment for individual post"""
        if isinstance(post, dict):
            text = post.get('text', '').lower()
            likes = post.get('likes', 0)
            shares = post.get('shares', 0)
        else:
            text = str(post).lower()
            likes = 0
            shares = 0
        
        # Text sentiment
        sentiment = 0.0
        
        # Bullish keywords
        bullish_words = ['buy', 'calls', 'moon', 'squeeze', 'breakout', 'bullish', 
                        'long', 'yolo', 'diamond hands', 'hodl', 'pump']
        for word in bullish_words:
            if word in text:
                sentiment += 0.3
        
        # Bearish keywords
        bearish_words = ['sell', 'puts', 'short', 'dump', 'crash', 'bearish',
                        'overvalued', 'bubble', 'dead', 'trash']
        for word in bearish_words:
            if word in text:
                sentiment -= 0.3
        
        # Emoji sentiment
        for emoji, score in self.emoji_sentiment.items():
            if emoji in text:
                sentiment += score * 0.5
        
        # Engagement multiplier
        engagement_factor = 1.0 + min(0.5, (likes + shares * 2) / 1000)
        sentiment = sentiment * engagement_factor
        
        # Clamp to [-1, 1]
        return max(-1.0, min(1.0, sentiment))
    
    def _analyze_influencer_activity(self, social_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze activity from influential accounts"""
        influencer_posts = social_data.get('influencer_posts', [])
        
        if not influencer_posts:
            return {
                "active": False,
                "sentiment": 0.0,
                "impact": 0.0
            }
        
        total_sentiment = 0.0
        total_reach = 0
        
        for post in influencer_posts:
            followers = post.get('followers', 0)
            sentiment = self._calculate_post_sentiment(post)
            
            # Weight by follower count
            total_sentiment += sentiment * followers
            total_reach += followers
        
        if total_reach > 0:
            weighted_sentiment = total_sentiment / total_reach
        else:
            weighted_sentiment = 0.0
        
        # Calculate impact based on reach
        impact = min(1.0, total_reach / 1000000)  # 1M followers = max impact
        
        return {
            "active": True,
            "sentiment": weighted_sentiment,
            "impact": impact,
            "total_reach": total_reach,
            "post_count": len(influencer_posts)
        }
    
    def _analyze_options_sentiment(self, options_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment from options flow"""
        if not options_data:
            return {
                "put_call_ratio": 1.0,
                "sentiment": "neutral",
                "unusual_activity": False
            }
        
        call_volume = options_data.get('call_volume', 0)
        put_volume = options_data.get('put_volume', 0)
        
        if call_volume + put_volume == 0:
            put_call_ratio = 1.0
        else:
            put_call_ratio = put_volume / (call_volume + 0.001)
        
        # Determine sentiment from put/call ratio
        if put_call_ratio < 0.7:
            sentiment = "bullish"
            sentiment_score = 0.7
        elif put_call_ratio > 1.3:
            sentiment = "bearish"
            sentiment_score = -0.7
        else:
            sentiment = "neutral"
            sentiment_score = 0.0
        
        # Check for unusual activity
        avg_volume = options_data.get('avg_options_volume', 1)
        current_volume = call_volume + put_volume
        unusual_activity = current_volume > avg_volume * 2
        
        return {
            "put_call_ratio": put_call_ratio,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "unusual_activity": unusual_activity,
            "call_volume": call_volume,
            "put_volume": put_volume
        }
    
    def _calculate_retail_interest(self, mentions: Dict[str, Any], 
                                  sentiment: Dict[str, Any], 
                                  influencer: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall retail interest level"""
        # Base score from mentions
        mention_score = mentions['trend_strength']
        
        # Adjust for sentiment strength
        sentiment_strength = abs(sentiment['overall'])
        
        # Add influencer impact
        influencer_boost = influencer['impact'] * 0.3
        
        # Calculate interest level
        interest_score = min(1.0, mention_score + sentiment_strength * 0.3 + influencer_boost)
        
        # Determine interest category
        if interest_score > 0.8:
            interest_level = "extreme"
        elif interest_score > 0.6:
            interest_level = "high"
        elif interest_score > 0.4:
            interest_level = "moderate"
        elif interest_score > 0.2:
            interest_level = "low"
        else:
            interest_level = "minimal"
        
        return {
            "score": interest_score,
            "level": interest_level,
            "is_meme_stock": mentions['is_viral'] and sentiment['overall'] > 0.5,
            "retail_dominated": interest_score > 0.7
        }
    
    def _calculate_sentiment_score(self, sentiment: Dict[str, Any], 
                                  mentions: Dict[str, Any], 
                                  influencer: Dict[str, Any],
                                  options: Dict[str, Any]) -> float:
        """Calculate overall sentiment score"""
        # Weighted combination of factors
        social_sentiment = sentiment['overall'] * 0.4
        mention_momentum = (mentions['trend_strength'] - 0.5) * 0.2
        influencer_impact = influencer['sentiment'] * influencer['impact'] * 0.2
        options_sentiment = options.get('sentiment_score', 0) * 0.2
        
        # Combine and normalize to [0, 1]
        raw_score = social_sentiment + mention_momentum + influencer_impact + options_sentiment
        sentiment_score = (raw_score + 1) / 2
        
        return max(0.0, min(1.0, sentiment_score))
    
    def _generate_recommendation(self, sentiment_score: float, 
                                retail_interest: Dict[str, Any], 
                                mentions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading recommendation based on sentiment"""
        
        # Check for extreme conditions
        if retail_interest['is_meme_stock']:
            # Meme stock dynamics - high risk, high reward
            if sentiment_score > 0.7:
                action = "BUY"
                confidence = 0.6  # Lower confidence due to volatility
                timeframe = "intraday"  # Very short-term
            else:
                action = "HOLD"
                confidence = 0.3
                timeframe = "intraday"
        elif sentiment_score > self.bullish_threshold and mentions['is_trending']:
            action = "BUY"
            confidence = min(0.8, sentiment_score)
            timeframe = "short"
        elif sentiment_score < self.bearish_threshold:
            action = "SELL"
            confidence = min(0.8, 1 - sentiment_score)
            timeframe = "short"
        else:
            action = "HOLD"
            confidence = 0.5
            timeframe = "medium"
        
        reasoning = self._generate_reasoning(sentiment_score, retail_interest, mentions)
        
        return {
            "action": action,
            "confidence": confidence,
            "timeframe": timeframe,
            "reasoning": reasoning
        }
    
    def _assess_sentiment_risk(self, sentiment_score: float, 
                              mentions: Dict[str, Any], 
                              retail_interest: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk based on sentiment analysis"""
        
        # High retail interest = higher risk
        if retail_interest['is_meme_stock']:
            risk_level = "HIGH"
            volatility = 0.1  # 10% expected volatility
            position_size = 0.005  # Very small position
        elif retail_interest['retail_dominated']:
            risk_level = "MEDIUM"
            volatility = 0.05
            position_size = 0.01
        else:
            risk_level = "LOW"
            volatility = 0.03
            position_size = 0.02
        
        # Sentiment-driven trades need tight stops
        stop_loss_pct = 0.03 if risk_level == "LOW" else 0.05
        
        return {
            "risk_level": risk_level,
            "stop_loss": 100 * (1 - stop_loss_pct),
            "take_profit": 100 * (1 + stop_loss_pct * 2),
            "position_size_pct": position_size,
            "volatility": volatility
        }
    
    def _identify_key_factors(self, sentiment_score: float, 
                             mentions: Dict[str, Any], 
                             retail_interest: Dict[str, Any]) -> List[str]:
        """Identify key sentiment factors"""
        factors = []
        
        if sentiment_score > 0.7:
            factors.append("Strong bullish sentiment")
        elif sentiment_score < 0.3:
            factors.append("Strong bearish sentiment")
        
        if mentions['is_viral']:
            factors.append("Viral social media activity")
        elif mentions['is_trending']:
            factors.append("Trending on social media")
        
        if retail_interest['is_meme_stock']:
            factors.append("Meme stock characteristics")
        elif retail_interest['retail_dominated']:
            factors.append("High retail interest")
        
        factors.append(f"Mention velocity: {mentions['mention_velocity']:.1f}x normal")
        
        return factors
    
    def _calculate_confidence(self, sentiment_score: float, 
                             mentions: Dict[str, Any]) -> float:
        """Calculate confidence in sentiment analysis"""
        # Base confidence from sentiment strength
        sentiment_confidence = abs(sentiment_score - 0.5) * 2
        
        # Adjust for data volume
        volume_confidence = min(1.0, mentions['total_mentions'] / 100)
        
        # Combine
        return min(0.9, sentiment_confidence * 0.6 + volume_confidence * 0.4)
    
    def _generate_reasoning(self, score: float, retail: Dict[str, Any], 
                           mentions: Dict[str, Any]) -> str:
        """Generate reasoning for recommendation"""
        reasons = []
        
        if score > 0.65:
            reasons.append("Bullish social sentiment")
        elif score < 0.35:
            reasons.append("Bearish social sentiment")
        else:
            reasons.append("Neutral sentiment")
        
        if retail['is_meme_stock']:
            reasons.append("meme stock dynamics")
        elif mentions['is_trending']:
            reasons.append("trending ticker")
        
        reasons.append(f"{retail['level']} retail interest")
        
        return ", ".join(reasons)
    
    def _generate_error_result(self, error_msg: str) -> Dict[str, Any]:
        """Generate error result"""
        return {
            "recommendation": {"action": "HOLD", "confidence": 0.0, "timeframe": "medium"},
            "analysis": {"error": error_msg},
            "risk_assessment": {"risk_level": "HIGH"},
            "confidence": 0.0
        }