"""
Alternative Data Aggregator - Multi-Source Intelligence System
Integrates: Twitter/X, Reddit, SEC Filings, Options Flow, Dark Pools, and more
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSource(Enum):
    """Available alternative data sources"""
    TWITTER = "twitter"
    REDDIT = "reddit"
    SEC_EDGAR = "sec_edgar"
    UNUSUAL_WHALES = "unusual_whales"
    DARK_POOL = "dark_pool"
    CONGRESS_TRADES = "congress_trades"
    INSIDER_TRADING = "insider_trading"
    OPTIONS_FLOW = "options_flow"
    STOCKTWITS = "stocktwits"
    GOOGLE_TRENDS = "google_trends"
    NEWS_SENTIMENT = "news_sentiment"
    SOCIAL_VOLUME = "social_volume"
    SHORT_INTEREST = "short_interest"
    BENZINGA = "benzinga"
    SEEKING_ALPHA = "seeking_alpha"

@dataclass
class AlternativeDataSignal:
    """Standardized signal from alternative data sources"""
    source: DataSource
    symbol: str
    timestamp: datetime
    signal_type: str  # bullish, bearish, neutral, unusual_activity
    strength: float  # 0-100
    data: Dict[str, Any]
    confidence: float  # 0-1

class TwitterSentimentAnalyzer:
    """Analyze Twitter/X sentiment and volume"""

    def __init__(self):
        self.base_url = "https://api.twitter.com/2"
        # Note: You'll need to add your Twitter API credentials
        self.bearer_token = None
        self.influential_accounts = [
            "DeItaone",  # Breaking news
            "FirstSquawk",  # Market news
            "LiveSquawk",  # Real-time news
            "zerohedge",  # Market commentary
            "unusual_whales",  # Options flow
            "CheddarFlow",  # Options flow
            "TradeWithAlerts",  # Trade alerts
            "Mr_Derivatives",  # Options expert
            "jimcramer",  # Inverse indicator
            "Carl_Icahn",  # Activist investor
            "chamath",  # VC investor
            "elonmusk",  # Market mover
        ]

    async def analyze_symbol(self, symbol: str) -> Dict[str, Any]:
        """Analyze Twitter sentiment for a symbol"""
        try:
            # Search for recent tweets
            tweets = await self._search_tweets(f"${symbol}")

            # Analyze sentiment
            sentiment_score = self._calculate_sentiment(tweets)

            # Check volume spike
            volume_spike = self._detect_volume_spike(tweets)

            # Check influential mentions
            influential_mentions = self._check_influential_mentions(tweets)

            return {
                "symbol": symbol,
                "sentiment_score": sentiment_score,
                "tweet_volume": len(tweets),
                "volume_spike": volume_spike,
                "influential_mentions": influential_mentions,
                "top_tweets": tweets[:5] if tweets else []
            }

        except Exception as e:
            logger.error(f"Twitter analysis error for {symbol}: {e}")
            return {}

    async def _search_tweets(self, query: str) -> List[Dict]:
        """Search Twitter for relevant tweets"""
        # Placeholder - implement Twitter API v2 search
        return []

    def _calculate_sentiment(self, tweets: List[Dict]) -> float:
        """Calculate aggregate sentiment from tweets"""
        if not tweets:
            return 50.0  # Neutral

        # Simple sentiment keywords (extend with ML model)
        bullish_words = ['bullish', 'moon', 'rocket', 'buy', 'long', 'calls', 'breakout', 'squeeze']
        bearish_words = ['bearish', 'puts', 'short', 'sell', 'dump', 'crash', 'overvalued']

        bullish_count = 0
        bearish_count = 0

        for tweet in tweets:
            text = tweet.get('text', '').lower()
            bullish_count += sum(1 for word in bullish_words if word in text)
            bearish_count += sum(1 for word in bearish_words if word in text)

        if bullish_count + bearish_count == 0:
            return 50.0

        sentiment = (bullish_count / (bullish_count + bearish_count)) * 100
        return sentiment

    def _detect_volume_spike(self, tweets: List[Dict]) -> bool:
        """Detect if there's unusual Twitter volume"""
        # Compare to rolling average
        return len(tweets) > 100  # Simplified threshold

    def _check_influential_mentions(self, tweets: List[Dict]) -> List[str]:
        """Check if influential accounts mentioned the symbol"""
        mentions = []
        for tweet in tweets:
            author = tweet.get('author_username', '')
            if author in self.influential_accounts:
                mentions.append(author)
        return mentions

class RedditWSBScraper:
    """Scrape and analyze WallStreetBets sentiment"""

    def __init__(self):
        self.subreddits = [
            "wallstreetbets",
            "stocks",
            "options",
            "investing",
            "pennystocks",
            "Shortsqueeze",
            "SPACs",
            "thetagang"
        ]
        self.base_url = "https://www.reddit.com"

    async def analyze_symbol(self, symbol: str) -> Dict[str, Any]:
        """Analyze Reddit sentiment for a symbol"""
        try:
            mentions = []

            for subreddit in self.subreddits:
                # Get hot posts
                hot_posts = await self._get_subreddit_posts(subreddit, 'hot')
                # Get new posts
                new_posts = await self._get_subreddit_posts(subreddit, 'new')

                # Find mentions
                for post in hot_posts + new_posts:
                    if symbol.upper() in post.get('title', '').upper() or \
                       symbol.upper() in post.get('text', '').upper():
                        mentions.append({
                            'subreddit': subreddit,
                            'title': post.get('title'),
                            'score': post.get('score', 0),
                            'comments': post.get('num_comments', 0),
                            'url': post.get('url')
                        })

            # Calculate metrics
            total_score = sum(m['score'] for m in mentions)
            total_comments = sum(m['comments'] for m in mentions)

            # Detect if it's trending
            is_trending = len(mentions) > 5 or total_score > 1000

            return {
                "symbol": symbol,
                "mention_count": len(mentions),
                "total_score": total_score,
                "total_comments": total_comments,
                "is_trending": is_trending,
                "top_mentions": sorted(mentions, key=lambda x: x['score'], reverse=True)[:5],
                "sentiment": self._calculate_reddit_sentiment(mentions)
            }

        except Exception as e:
            logger.error(f"Reddit analysis error for {symbol}: {e}")
            return {}

    async def _get_subreddit_posts(self, subreddit: str, sort: str) -> List[Dict]:
        """Get posts from a subreddit"""
        # Placeholder - implement Reddit API or scraping
        return []

    def _calculate_reddit_sentiment(self, mentions: List[Dict]) -> str:
        """Calculate overall Reddit sentiment"""
        if not mentions:
            return "neutral"

        # High engagement typically means bullish on Reddit
        avg_score = sum(m['score'] for m in mentions) / len(mentions)

        if avg_score > 500:
            return "very_bullish"
        elif avg_score > 100:
            return "bullish"
        elif avg_score < 0:
            return "bearish"
        else:
            return "neutral"

class UnusualOptionsFlowTracker:
    """Track unusual options activity"""

    def __init__(self):
        self.flow_threshold = 100000  # $100K minimum
        self.unusual_ratio = 3  # 3x normal volume

    async def get_unusual_flow(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get unusual options flow data"""
        try:
            flows = []

            # Sources to check:
            # 1. Unusual Whales API
            # 2. FlowAlgo
            # 3. Cheddar Flow
            # 4. Market Chameleon

            # Placeholder for API implementation
            sample_flow = {
                "symbol": symbol or "SPY",
                "timestamp": datetime.now(),
                "option_type": "CALL",
                "strike": 575,
                "expiry": "2025-10-04",
                "premium": 250000,
                "volume": 5000,
                "open_interest": 10000,
                "volume_oi_ratio": 0.5,
                "sentiment": "BULLISH",
                "is_sweep": True,
                "is_unusual": True
            }

            flows.append(sample_flow)

            return flows

        except Exception as e:
            logger.error(f"Options flow error: {e}")
            return []

    def analyze_flow_sentiment(self, flows: List[Dict]) -> Dict[str, Any]:
        """Analyze overall options flow sentiment"""
        if not flows:
            return {"sentiment": "neutral", "confidence": 0}

        call_premium = sum(f['premium'] for f in flows if f['option_type'] == 'CALL')
        put_premium = sum(f['premium'] for f in flows if f['option_type'] == 'PUT')

        if call_premium + put_premium == 0:
            return {"sentiment": "neutral", "confidence": 0}

        call_ratio = call_premium / (call_premium + put_premium)

        if call_ratio > 0.7:
            sentiment = "bullish"
        elif call_ratio < 0.3:
            sentiment = "bearish"
        else:
            sentiment = "neutral"

        confidence = abs(call_ratio - 0.5) * 2  # 0 to 1 scale

        return {
            "sentiment": sentiment,
            "call_ratio": call_ratio,
            "confidence": confidence,
            "total_premium": call_premium + put_premium
        }

class SECInsiderTracker:
    """Track SEC Form 4 insider trading"""

    def __init__(self):
        self.edgar_url = "https://www.sec.gov/edgar/search-and-access"
        self.significant_threshold = 100000  # $100K minimum

    async def get_insider_trades(self, symbol: str) -> List[Dict]:
        """Get recent insider trades for a symbol"""
        try:
            trades = []

            # Would implement SEC EDGAR API here
            # For now, return sample data
            sample_trade = {
                "symbol": symbol,
                "insider_name": "CEO John Smith",
                "transaction_type": "Buy",
                "shares": 10000,
                "price": 50.00,
                "value": 500000,
                "date": datetime.now() - timedelta(days=1),
                "ownership_change": "+5%",
                "remaining_shares": 200000
            }

            trades.append(sample_trade)

            return trades

        except Exception as e:
            logger.error(f"SEC insider tracking error: {e}")
            return []

    def analyze_insider_sentiment(self, trades: List[Dict]) -> Dict[str, Any]:
        """Analyze insider trading patterns"""
        if not trades:
            return {"sentiment": "neutral", "confidence": 0}

        recent_trades = [t for t in trades if t['date'] > datetime.now() - timedelta(days=30)]

        buy_value = sum(t['value'] for t in recent_trades if t['transaction_type'] == 'Buy')
        sell_value = sum(t['value'] for t in recent_trades if t['transaction_type'] == 'Sell')

        if buy_value > sell_value * 2:
            sentiment = "bullish"
        elif sell_value > buy_value * 2:
            sentiment = "bearish"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "buy_value": buy_value,
            "sell_value": sell_value,
            "net_buying": buy_value - sell_value,
            "trade_count": len(recent_trades)
        }

class DarkPoolMonitor:
    """Monitor dark pool activity"""

    def __init__(self):
        self.threshold_pct = 40  # Alert if >40% dark pool

    async def get_dark_pool_data(self, symbol: str) -> Dict[str, Any]:
        """Get dark pool trading data"""
        try:
            # Would integrate with:
            # - FINRA ADF data
            # - NYSE TRF data
            # - Dark pool aggregators

            # Sample data
            data = {
                "symbol": symbol,
                "dark_pool_volume": 5000000,
                "total_volume": 10000000,
                "dark_pool_percent": 50,
                "large_blocks": [
                    {"size": 100000, "price": 50.00, "time": "10:30"},
                    {"size": 250000, "price": 50.25, "time": "14:15"}
                ],
                "net_sentiment": "accumulation",  # or "distribution"
                "is_unusual": True
            }

            return data

        except Exception as e:
            logger.error(f"Dark pool monitor error: {e}")
            return {}

class CongressionalTradeTracker:
    """Track congressional trading disclosures"""

    def __init__(self):
        self.sources = [
            "quiverquant.com",
            "capitoltrades.com",
            "smartinsider.com"
        ]

    async def get_congress_trades(self) -> List[Dict]:
        """Get recent congressional trades"""
        try:
            trades = []

            # Would scrape/API from sources
            # Sample data
            sample_trade = {
                "politician": "Senator Jane Doe",
                "symbol": "NVDA",
                "transaction_type": "Buy",
                "amount_range": "$100,000 - $250,000",
                "date_disclosed": datetime.now() - timedelta(days=2),
                "date_traded": datetime.now() - timedelta(days=30),
                "committee": "Technology",
                "party": "D"
            }

            trades.append(sample_trade)

            return trades

        except Exception as e:
            logger.error(f"Congressional tracking error: {e}")
            return []

class SocialVolumeAnalyzer:
    """Analyze social media volume spikes"""

    def __init__(self):
        self.sources = [
            "twitter",
            "reddit",
            "stocktwits",
            "discord",
            "telegram"
        ]
        self.baseline_window = 30  # days

    async def detect_volume_spike(self, symbol: str) -> Dict[str, Any]:
        """Detect social volume spikes across platforms"""
        try:
            current_volume = await self._get_current_volume(symbol)
            baseline = await self._get_baseline_volume(symbol)

            spike_ratio = current_volume / baseline if baseline > 0 else 0

            return {
                "symbol": symbol,
                "current_volume": current_volume,
                "baseline_volume": baseline,
                "spike_ratio": spike_ratio,
                "is_spiking": spike_ratio > 3,
                "percentile": min(99, spike_ratio * 20),  # 0-99 percentile
                "trending_platforms": self._get_trending_platforms(symbol)
            }

        except Exception as e:
            logger.error(f"Social volume error: {e}")
            return {}

    async def _get_current_volume(self, symbol: str) -> int:
        """Get current 24h social volume"""
        # Placeholder
        return 1000

    async def _get_baseline_volume(self, symbol: str) -> int:
        """Get baseline average volume"""
        # Placeholder
        return 300

    def _get_trending_platforms(self, symbol: str) -> List[str]:
        """Get platforms where symbol is trending"""
        # Placeholder
        return ["twitter", "reddit"]

class GoogleTrendsAnalyzer:
    """Analyze Google Trends data"""

    def __init__(self):
        self.categories = {
            "finance": 7,
            "business": 12
        }

    async def get_trend_data(self, symbol: str) -> Dict[str, Any]:
        """Get Google Trends data for symbol"""
        try:
            # Would use pytrends library
            # from pytrends.request import TrendReq

            # Sample data
            data = {
                "symbol": symbol,
                "interest_over_time": 75,  # 0-100
                "trend_direction": "rising",
                "related_queries": [
                    f"{symbol} stock price",
                    f"{symbol} earnings",
                    f"buy {symbol} stock"
                ],
                "regional_interest": {
                    "United States": 100,
                    "Canada": 45,
                    "United Kingdom": 30
                }
            }

            return data

        except Exception as e:
            logger.error(f"Google Trends error: {e}")
            return {}

class AlternativeDataAggregator:
    """Main aggregator for all alternative data sources"""

    def __init__(self):
        self.twitter = TwitterSentimentAnalyzer()
        self.reddit = RedditWSBScraper()
        self.options = UnusualOptionsFlowTracker()
        self.sec = SECInsiderTracker()
        self.dark_pool = DarkPoolMonitor()
        self.congress = CongressionalTradeTracker()
        self.social_volume = SocialVolumeAnalyzer()
        self.google_trends = GoogleTrendsAnalyzer()

        # Weights for combining signals
        self.weights = {
            DataSource.TWITTER: 0.15,
            DataSource.REDDIT: 0.10,
            DataSource.OPTIONS_FLOW: 0.20,
            DataSource.INSIDER_TRADING: 0.15,
            DataSource.DARK_POOL: 0.15,
            DataSource.CONGRESS_TRADES: 0.10,
            DataSource.SOCIAL_VOLUME: 0.10,
            DataSource.GOOGLE_TRENDS: 0.05
        }

    async def analyze_symbol(self, symbol: str) -> Dict[str, Any]:
        """Comprehensive analysis across all data sources"""
        logger.info(f"Starting comprehensive analysis for {symbol}")

        # Gather all data concurrently
        tasks = [
            self.twitter.analyze_symbol(symbol),
            self.reddit.analyze_symbol(symbol),
            self.options.get_unusual_flow(symbol),
            self.sec.get_insider_trades(symbol),
            self.dark_pool.get_dark_pool_data(symbol),
            self.social_volume.detect_volume_spike(symbol),
            self.google_trends.get_trend_data(symbol)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        twitter_data = results[0] if not isinstance(results[0], Exception) else {}
        reddit_data = results[1] if not isinstance(results[1], Exception) else {}
        options_data = results[2] if not isinstance(results[2], Exception) else []
        insider_data = results[3] if not isinstance(results[3], Exception) else []
        dark_pool_data = results[4] if not isinstance(results[4], Exception) else {}
        social_volume_data = results[5] if not isinstance(results[5], Exception) else {}
        google_trends_data = results[6] if not isinstance(results[6], Exception) else {}

        # Calculate composite score
        composite_score = self._calculate_composite_score({
            'twitter': twitter_data,
            'reddit': reddit_data,
            'options': options_data,
            'insider': insider_data,
            'dark_pool': dark_pool_data,
            'social_volume': social_volume_data,
            'google_trends': google_trends_data
        })

        # Detect unusual activity
        unusual_flags = self._detect_unusual_activity({
            'twitter': twitter_data,
            'reddit': reddit_data,
            'options': options_data,
            'insider': insider_data,
            'dark_pool': dark_pool_data,
            'social_volume': social_volume_data
        })

        # Generate trading signals
        signals = self._generate_trading_signals(
            symbol, composite_score, unusual_flags
        )

        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "composite_score": composite_score,
            "signals": signals,
            "unusual_activity": unusual_flags,
            "data_sources": {
                "twitter": twitter_data,
                "reddit": reddit_data,
                "options_flow": self.options.analyze_flow_sentiment(options_data),
                "insider_trading": self.sec.analyze_insider_sentiment(insider_data),
                "dark_pool": dark_pool_data,
                "social_volume": social_volume_data,
                "google_trends": google_trends_data
            },
            "recommendation": self._generate_recommendation(composite_score, unusual_flags)
        }

    def _calculate_composite_score(self, data: Dict) -> float:
        """Calculate weighted composite sentiment score (0-100)"""
        score = 50  # Start neutral

        # Twitter sentiment
        if data.get('twitter', {}).get('sentiment_score'):
            score += self.weights[DataSource.TWITTER] * (data['twitter']['sentiment_score'] - 50)

        # Reddit sentiment
        if data.get('reddit', {}).get('sentiment') == 'bullish':
            score += self.weights[DataSource.REDDIT] * 30
        elif data.get('reddit', {}).get('sentiment') == 'very_bullish':
            score += self.weights[DataSource.REDDIT] * 50
        elif data.get('reddit', {}).get('sentiment') == 'bearish':
            score -= self.weights[DataSource.REDDIT] * 30

        # Options flow
        if data.get('options'):
            flow_sentiment = self.options.analyze_flow_sentiment(data['options'])
            if flow_sentiment['sentiment'] == 'bullish':
                score += self.weights[DataSource.OPTIONS_FLOW] * 40 * flow_sentiment['confidence']
            elif flow_sentiment['sentiment'] == 'bearish':
                score -= self.weights[DataSource.OPTIONS_FLOW] * 40 * flow_sentiment['confidence']

        # Insider trading
        if data.get('insider'):
            insider_sentiment = self.sec.analyze_insider_sentiment(data['insider'])
            if insider_sentiment['sentiment'] == 'bullish':
                score += self.weights[DataSource.INSIDER_TRADING] * 35
            elif insider_sentiment['sentiment'] == 'bearish':
                score -= self.weights[DataSource.INSIDER_TRADING] * 35

        # Dark pool
        if data.get('dark_pool', {}).get('net_sentiment') == 'accumulation':
            score += self.weights[DataSource.DARK_POOL] * 30
        elif data.get('dark_pool', {}).get('net_sentiment') == 'distribution':
            score -= self.weights[DataSource.DARK_POOL] * 30

        # Social volume spike
        if data.get('social_volume', {}).get('is_spiking'):
            score += self.weights[DataSource.SOCIAL_VOLUME] * 20

        # Google trends
        if data.get('google_trends', {}).get('trend_direction') == 'rising':
            score += self.weights[DataSource.GOOGLE_TRENDS] * 15

        return max(0, min(100, score))

    def _detect_unusual_activity(self, data: Dict) -> List[str]:
        """Detect unusual activity flags"""
        flags = []

        # Twitter volume spike
        if data.get('twitter', {}).get('volume_spike'):
            flags.append("twitter_volume_spike")

        # Reddit trending
        if data.get('reddit', {}).get('is_trending'):
            flags.append("reddit_trending")

        # Unusual options flow
        if any(f.get('is_unusual') for f in data.get('options', [])):
            flags.append("unusual_options_flow")

        # Large insider buying
        if data.get('insider'):
            insider_sentiment = self.sec.analyze_insider_sentiment(data['insider'])
            if insider_sentiment.get('net_buying', 0) > 1000000:
                flags.append("large_insider_buying")

        # High dark pool activity
        if data.get('dark_pool', {}).get('dark_pool_percent', 0) > 40:
            flags.append("high_dark_pool_activity")

        # Social volume spike
        if data.get('social_volume', {}).get('spike_ratio', 0) > 5:
            flags.append("extreme_social_spike")

        return flags

    def _generate_trading_signals(self, symbol: str, score: float, flags: List[str]) -> List[Dict]:
        """Generate actionable trading signals"""
        signals = []

        # Strong bullish signal
        if score > 75:
            signals.append({
                "type": "STRONG_BUY",
                "confidence": (score - 75) / 25,
                "reason": "Multiple bullish indicators aligned"
            })

        # Moderate bullish
        elif score > 60:
            signals.append({
                "type": "BUY",
                "confidence": (score - 60) / 15,
                "reason": "Positive sentiment across data sources"
            })

        # Strong bearish
        elif score < 25:
            signals.append({
                "type": "STRONG_SELL",
                "confidence": (25 - score) / 25,
                "reason": "Multiple bearish indicators"
            })

        # Moderate bearish
        elif score < 40:
            signals.append({
                "type": "SELL",
                "confidence": (40 - score) / 15,
                "reason": "Negative sentiment detected"
            })

        # Check for specific flag-based signals
        if "unusual_options_flow" in flags and "twitter_volume_spike" in flags:
            signals.append({
                "type": "MOMENTUM_ALERT",
                "confidence": 0.8,
                "reason": "Options flow + social spike combo"
            })

        if "large_insider_buying" in flags:
            signals.append({
                "type": "INSIDER_ACCUMULATION",
                "confidence": 0.7,
                "reason": "Significant insider buying detected"
            })

        if "extreme_social_spike" in flags and "reddit_trending" in flags:
            signals.append({
                "type": "MEME_STOCK_ALERT",
                "confidence": 0.6,
                "reason": "Potential meme stock momentum"
            })

        return signals

    def _generate_recommendation(self, score: float, flags: List[str]) -> str:
        """Generate human-readable recommendation"""
        if score > 75:
            action = "STRONG BUY"
        elif score > 60:
            action = "BUY"
        elif score > 40:
            action = "HOLD"
        elif score > 25:
            action = "SELL"
        else:
            action = "STRONG SELL"

        if flags:
            return f"{action} - Unusual Activity Detected: {', '.join(flags)}"
        else:
            return f"{action} - Sentiment Score: {score:.1f}/100"

    async def get_market_movers(self) -> Dict[str, List[Dict]]:
        """Get top movers across all alternative data sources"""
        logger.info("Scanning for market movers across alternative data")

        movers = {
            "trending_social": [],
            "unusual_options": [],
            "insider_buying": [],
            "congress_trades": [],
            "dark_pool_accumulation": []
        }

        # Get trending on social
        # This would scan top mentioned symbols

        # Get unusual options flow
        options_flow = await self.options.get_unusual_flow()
        movers['unusual_options'] = options_flow[:10]

        # Get recent congressional trades
        congress = await self.congress.get_congress_trades()
        movers['congress_trades'] = congress[:10]

        return movers

    async def continuous_monitor(self, symbols: List[str], callback=None):
        """Continuously monitor symbols for signals"""
        logger.info(f"Starting continuous monitoring for {len(symbols)} symbols")

        while True:
            for symbol in symbols:
                try:
                    analysis = await self.analyze_symbol(symbol)

                    # Check for actionable signals
                    if analysis['signals']:
                        logger.info(f"Signals detected for {symbol}: {analysis['signals']}")
                        if callback:
                            await callback(symbol, analysis)

                except Exception as e:
                    logger.error(f"Error monitoring {symbol}: {e}")

            # Wait before next scan
            await asyncio.sleep(300)  # 5 minutes

class RealTimeAlertSystem:
    """Real-time alert system for critical events"""

    def __init__(self, telegram_token: str, chat_id: str):
        self.telegram_token = telegram_token
        self.chat_id = chat_id
        self.aggregator = AlternativeDataAggregator()

    async def send_alert(self, message: str, priority: str = "MEDIUM"):
        """Send alert via Telegram"""
        import requests

        # Add emoji based on priority
        emoji_map = {
            "HIGH": "🚨",
            "MEDIUM": "⚠️",
            "LOW": "ℹ️",
            "CRITICAL": "🔴"
        }

        emoji = emoji_map.get(priority, "📌")
        formatted_message = f"{emoji} {message}"

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        data = {
            'chat_id': self.chat_id,
            'text': formatted_message,
            'parse_mode': 'HTML'
        }

        try:
            response = requests.post(url, data=data)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False

    async def monitor_and_alert(self, symbols: List[str]):
        """Monitor symbols and send alerts on significant events"""

        async def alert_callback(symbol: str, analysis: Dict):
            """Callback for sending alerts"""

            # Check for high-priority signals
            for signal in analysis['signals']:
                if signal['confidence'] > 0.7:
                    message = f"<b>{symbol}</b>\n"
                    message += f"Signal: {signal['type']}\n"
                    message += f"Confidence: {signal['confidence']:.1%}\n"
                    message += f"Reason: {signal['reason']}\n"
                    message += f"Score: {analysis['composite_score']:.1f}/100"

                    priority = "HIGH" if signal['confidence'] > 0.8 else "MEDIUM"
                    await self.send_alert(message, priority)

            # Check for unusual activity
            if len(analysis['unusual_activity']) >= 3:
                message = f"<b>{symbol} - Multiple Unusual Activities</b>\n"
                message += "\n".join(f"• {flag}" for flag in analysis['unusual_activity'])
                await self.send_alert(message, "HIGH")

        await self.aggregator.continuous_monitor(symbols, alert_callback)

# Example usage
async def main():
    """Example usage of the alternative data system"""

    # Initialize aggregator
    aggregator = AlternativeDataAggregator()

    # Analyze a single symbol
    analysis = await aggregator.analyze_symbol("TSLA")
    print(json.dumps(analysis, indent=2, default=str))

    # Get market movers
    movers = await aggregator.get_market_movers()
    print("Market Movers:", movers)

    # Set up real-time alerts
    alert_system = RealTimeAlertSystem(
        telegram_token="YOUR_TOKEN",
        chat_id="YOUR_CHAT_ID"
    )

    # Monitor key symbols
    watchlist = ["AAPL", "TSLA", "SPY", "NVDA", "BBAI", "SOUN"]
    await alert_system.monitor_and_alert(watchlist)

if __name__ == "__main__":
    asyncio.run(main())