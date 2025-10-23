"""
Social Sentiment Analyzer - Reddit WSB and Social Media
Wraps existing reddit_wsb_scanner.py and provides sentiment analysis
"""

import logging
from datetime import datetime
from typing import List, Dict
import sys
from pathlib import Path
import re

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.alternative_data_aggregator import AlternativeDataSignal, SignalType

logger = logging.getLogger(__name__)


class SocialSentimentAnalyzer:
    """
    Analyze social media sentiment from Reddit and other sources
    """

    def __init__(self):
        """Initialize social sentiment analyzer"""
        # Try to import reddit scanner
        try:
            from data_sources.reddit_wsb_scanner import RedditWSBScanner
            self.reddit_scanner = RedditWSBScanner()
        except ImportError as e:
            logger.warning(f"RedditWSBScanner not available: {e}")
            self.reddit_scanner = None

        # Sentiment keywords for analysis
        self.bullish_keywords = [
            'moon', 'squeeze', 'rocket', 'bull', 'calls', 'tendies', 'diamond hands',
            'buy', 'long', 'breakout', 'gainz', 'printing', 'uppies', 'green',
            'to the moon', 'lfg', 'bullish', 'accumulate', 'oversold'
        ]

        self.bearish_keywords = [
            'puts', 'bear', 'short', 'dump', 'crash', 'sell', 'worthless',
            'bag holder', 'bagholder', 'rip', 'guh', 'loss porn', 'red',
            'drill', 'tank', 'bearish', 'overvalued', 'overbought'
        ]

    def get_signals(self, ticker: str) -> List[AlternativeDataSignal]:
        """
        Get social sentiment signals for a ticker

        Args:
            ticker: Stock ticker symbol

        Returns:
            List of AlternativeDataSignal objects
        """
        # For now, return simulated sentiment based on simple analysis
        # In production, this would integrate with Reddit API via PRAW
        try:
            sentiment_data = self._analyze_ticker_sentiment(ticker)

            if not sentiment_data:
                logger.info(f"No social sentiment data for {ticker}")
                return []

            # Convert to AlternativeDataSignal
            signal = self._create_sentiment_signal(ticker, sentiment_data)

            return [signal] if signal else []

        except Exception as e:
            logger.error(f"Error fetching social signals for {ticker}: {e}")
            return []

    def _analyze_ticker_sentiment(self, ticker: str) -> Dict:
        """
        Analyze sentiment for a ticker (mock implementation)

        In production, this would:
        1. Fetch recent posts/comments from Reddit via PRAW
        2. Analyze text for bullish/bearish keywords
        3. Count mentions and sentiment scores
        4. Detect volume spikes

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with sentiment analysis
        """
        # Mock implementation - returns neutral sentiment with low confidence
        # In production, integrate with Reddit API
        logger.info(f"Social sentiment analysis for {ticker} (mock mode)")

        return {
            'ticker': ticker,
            'mention_count': 0,
            'bullish_mentions': 0,
            'bearish_mentions': 0,
            'neutral_mentions': 0,
            'sentiment_score': 0.0,  # -1 to +1
            'volume_spike': False,
            'top_posts': []
        }

    def _create_sentiment_signal(self, ticker: str, sentiment_data: Dict) -> AlternativeDataSignal:
        """
        Create AlternativeDataSignal from sentiment data

        Args:
            ticker: Stock ticker symbol
            sentiment_data: Dictionary with sentiment analysis

        Returns:
            AlternativeDataSignal object
        """
        mention_count = sentiment_data.get('mention_count', 0)

        # If no mentions, return neutral with low confidence
        if mention_count == 0:
            return AlternativeDataSignal(
                ticker=ticker,
                source='social',
                signal_type=SignalType.NEUTRAL,
                strength=50.0,
                confidence=20.0,  # Low confidence for no data
                timestamp=datetime.now(),
                metadata={
                    'mention_count': 0,
                    'sentiment_score': 0.0,
                    'source': 'reddit_wsb',
                    'note': 'No social media mentions found'
                }
            )

        sentiment_score = sentiment_data.get('sentiment_score', 0.0)  # -1 to +1

        # Determine signal type based on sentiment score
        if sentiment_score > 0.2:
            signal_type = SignalType.BULLISH
            # Strength scales with sentiment (50-100)
            strength = min(100, 50 + (sentiment_score * 50))
        elif sentiment_score < -0.2:
            signal_type = SignalType.BEARISH
            strength = min(100, 50 + (abs(sentiment_score) * 50))
        else:
            signal_type = SignalType.NEUTRAL
            strength = 50.0

        # Confidence based on mention count and volume spike
        if mention_count > 100:
            base_confidence = 75.0
        elif mention_count > 50:
            base_confidence = 65.0
        elif mention_count > 20:
            base_confidence = 55.0
        else:
            base_confidence = 45.0

        # Boost confidence if volume spike detected
        if sentiment_data.get('volume_spike', False):
            base_confidence = min(100, base_confidence + 15)

        return AlternativeDataSignal(
            ticker=ticker,
            source='social',
            signal_type=signal_type,
            strength=strength,
            confidence=base_confidence,
            timestamp=datetime.now(),
            metadata={
                'mention_count': mention_count,
                'bullish_mentions': sentiment_data.get('bullish_mentions', 0),
                'bearish_mentions': sentiment_data.get('bearish_mentions', 0),
                'sentiment_score': sentiment_score,
                'volume_spike': sentiment_data.get('volume_spike', False),
                'source': 'reddit_wsb'
            }
        )

    def analyze_text_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text using keyword matching

        Args:
            text: Text to analyze

        Returns:
            Sentiment score from -1 (bearish) to +1 (bullish)
        """
        text_lower = text.lower()

        bullish_count = sum(1 for keyword in self.bullish_keywords
                           if keyword in text_lower)
        bearish_count = sum(1 for keyword in self.bearish_keywords
                           if keyword in text_lower)

        total = bullish_count + bearish_count

        if total == 0:
            return 0.0

        # Calculate sentiment score
        score = (bullish_count - bearish_count) / total

        return score

    def get_summary(self, ticker: str) -> dict:
        """
        Get summary of social sentiment

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with summary statistics
        """
        signals = self.get_signals(ticker)

        if not signals:
            return {
                'ticker': ticker,
                'signal': 'NEUTRAL',
                'mentions': 0,
                'confidence': 0.0
            }

        signal = signals[0]  # Only one signal per ticker

        return {
            'ticker': ticker,
            'signal': signal.signal_type.value,
            'mentions': signal.metadata.get('mention_count', 0),
            'sentiment_score': signal.metadata.get('sentiment_score', 0.0),
            'confidence': signal.confidence
        }


class RedditAPIWrapper:
    """
    Wrapper for Reddit API using PRAW
    To enable: pip install praw and add Reddit API credentials
    """

    def __init__(self, client_id=None, client_secret=None, user_agent=None):
        """
        Initialize Reddit API wrapper

        Args:
            client_id: Reddit app client ID
            client_secret: Reddit app client secret
            user_agent: User agent string
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent or "TradingBot/1.0"
        self.reddit = None

        if client_id and client_secret:
            try:
                import praw
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=self.user_agent
                )
                logger.info("Reddit API initialized successfully")
            except ImportError:
                logger.warning("PRAW not installed. Install with: pip install praw")
            except Exception as e:
                logger.error(f"Failed to initialize Reddit API: {e}")

    def search_ticker_mentions(self, ticker: str, subreddit: str = 'wallstreetbets',
                               limit: int = 100, time_filter: str = 'day') -> List[dict]:
        """
        Search for ticker mentions in subreddit

        Args:
            ticker: Stock ticker symbol
            subreddit: Subreddit name
            limit: Maximum number of posts to fetch
            time_filter: Time filter ('hour', 'day', 'week', 'month', 'year', 'all')

        Returns:
            List of post dictionaries with title, score, num_comments, etc.
        """
        if not self.reddit:
            logger.warning("Reddit API not initialized")
            return []

        try:
            posts = []
            subreddit_obj = self.reddit.subreddit(subreddit)

            # Search for ticker mentions
            for submission in subreddit_obj.search(f"${ticker}", time_filter=time_filter, limit=limit):
                posts.append({
                    'title': submission.title,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'created_utc': datetime.fromtimestamp(submission.created_utc),
                    'url': submission.url,
                    'selftext': submission.selftext[:500]  # First 500 chars
                })

            logger.info(f"Found {len(posts)} mentions of {ticker} in r/{subreddit}")
            return posts

        except Exception as e:
            logger.error(f"Error searching Reddit for {ticker}: {e}")
            return []
