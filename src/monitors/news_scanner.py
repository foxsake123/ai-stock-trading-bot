"""
News Scanner - Real-Time Breaking News Monitoring
Scans Financial Datasets API and other sources for breaking news
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    """Represents a single news item"""
    ticker: str
    headline: str
    summary: str
    published_time: datetime
    source: str
    url: Optional[str] = None
    sentiment: Optional[str] = None  # POSITIVE, NEGATIVE, NEUTRAL
    sentiment_score: float = 0.0  # -1.0 to 1.0
    relevance_score: float = 0.0  # 0.0 to 1.0
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class NewsScanner:
    """
    Real-time news scanner using Financial Datasets API

    Features:
    - Scans for breaking news in real-time
    - Sentiment analysis of headlines
    - Relevance scoring
    - Deduplication
    - Rate limiting
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_minutes: int = 5,
        max_retries: int = 3
    ):
        """
        Initialize News Scanner

        Args:
            api_key: Financial Datasets API key (uses env var if not provided)
            cache_minutes: How long to cache news items
            max_retries: Maximum API retry attempts
        """
        self.api_key = api_key or os.getenv('FINANCIAL_DATASETS_API_KEY')
        if not self.api_key:
            logger.warning("FINANCIAL_DATASETS_API_KEY not found - news scanning will be limited")

        self.cache_minutes = cache_minutes
        self.max_retries = max_retries

        self.news_cache: Dict[str, List[NewsItem]] = {}  # ticker -> news items
        self.cache_timestamps: Dict[str, datetime] = {}  # ticker -> last update
        self.seen_headlines: set = set()  # For deduplication

        self.api_base_url = "https://api.financialdatasets.ai"

        logger.info("NewsScanner initialized")

    async def scan_recent_news(
        self,
        tickers: List[str],
        minutes_back: int = 60
    ) -> List[Dict]:
        """
        Scan recent news for multiple tickers

        Args:
            tickers: List of ticker symbols
            minutes_back: How many minutes back to look

        Returns:
            List of news items as dictionaries
        """
        all_news = []

        for ticker in tickers:
            try:
                news_items = await self._fetch_ticker_news(ticker, minutes_back)
                all_news.extend([self._news_item_to_dict(item) for item in news_items])
            except Exception as e:
                logger.error(f"Error scanning news for {ticker}: {e}")

        return all_news

    async def _fetch_ticker_news(
        self,
        ticker: str,
        minutes_back: int
    ) -> List[NewsItem]:
        """Fetch news for a single ticker"""
        ticker = ticker.upper()

        # Check cache first
        if self._is_cache_valid(ticker):
            logger.debug(f"Using cached news for {ticker}")
            return self.news_cache[ticker]

        # Fetch from API
        news_items = await self._fetch_from_api(ticker, minutes_back)

        # Update cache
        self.news_cache[ticker] = news_items
        self.cache_timestamps[ticker] = datetime.now()

        return news_items

    def _is_cache_valid(self, ticker: str) -> bool:
        """Check if cache is still valid for ticker"""
        if ticker not in self.cache_timestamps:
            return False

        age = (datetime.now() - self.cache_timestamps[ticker]).total_seconds() / 60
        return age < self.cache_minutes

    async def _fetch_from_api(
        self,
        ticker: str,
        minutes_back: int
    ) -> List[NewsItem]:
        """Fetch news from Financial Datasets API"""
        if not self.api_key:
            logger.warning(f"No API key - using mock data for {ticker}")
            return self._get_mock_news(ticker)

        news_items = []

        try:
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=minutes_back)

            # Build API request
            url = f"{self.api_base_url}/news"
            params = {
                'ticker': ticker,
                'from': start_time.isoformat(),
                'to': end_time.isoformat(),
                'limit': 50
            }

            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }

            # Make request with retries
            for attempt in range(self.max_retries):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                            if response.status == 200:
                                data = await response.json()
                                news_items = self._parse_api_response(ticker, data)
                                break
                            elif response.status == 429:  # Rate limit
                                wait_time = 2 ** attempt
                                logger.warning(f"Rate limited, waiting {wait_time}s...")
                                await asyncio.sleep(wait_time)
                            else:
                                logger.error(f"API error {response.status}: {await response.text()}")
                                break

                except asyncio.TimeoutError:
                    logger.warning(f"Timeout fetching news for {ticker} (attempt {attempt + 1})")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Error in API request: {e}")
                    break

        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {e}")

        return news_items

    def _parse_api_response(self, ticker: str, data: Dict) -> List[NewsItem]:
        """Parse API response into NewsItem objects"""
        news_items = []

        articles = data.get('news', []) or data.get('articles', []) or data.get('data', [])

        for article in articles:
            try:
                # Extract fields (API structure may vary)
                headline = article.get('headline') or article.get('title') or ''
                summary = article.get('summary') or article.get('description') or ''

                # Skip if we've seen this headline
                headline_key = f"{ticker}:{headline[:100]}"
                if headline_key in self.seen_headlines:
                    continue
                self.seen_headlines.add(headline_key)

                # Parse published time
                pub_time_str = article.get('published_at') or article.get('publishedAt') or article.get('date')
                if pub_time_str:
                    try:
                        published_time = datetime.fromisoformat(pub_time_str.replace('Z', '+00:00'))
                    except:
                        published_time = datetime.now()
                else:
                    published_time = datetime.now()

                # Sentiment
                sentiment_data = article.get('sentiment', {})
                if isinstance(sentiment_data, dict):
                    sentiment_score = sentiment_data.get('score', 0.0)
                    sentiment_label = sentiment_data.get('label', 'NEUTRAL')
                else:
                    sentiment_score = 0.0
                    sentiment_label = 'NEUTRAL'

                # Create news item
                news_item = NewsItem(
                    ticker=ticker,
                    headline=headline,
                    summary=summary,
                    published_time=published_time,
                    source=article.get('source', {}).get('name', 'Unknown') if isinstance(article.get('source'), dict) else article.get('source', 'Unknown'),
                    url=article.get('url') or article.get('link'),
                    sentiment=sentiment_label,
                    sentiment_score=sentiment_score,
                    relevance_score=article.get('relevance_score', 0.5),
                    metadata=article
                )

                news_items.append(news_item)

            except Exception as e:
                logger.error(f"Error parsing article: {e}")

        logger.info(f"Fetched {len(news_items)} news items for {ticker}")
        return news_items

    def _get_mock_news(self, ticker: str) -> List[NewsItem]:
        """Generate mock news for testing"""
        now = datetime.now()

        mock_items = [
            NewsItem(
                ticker=ticker,
                headline=f"{ticker} announces Q4 earnings beat",
                summary=f"{ticker} reports earnings of $2.50 vs $2.30 expected",
                published_time=now - timedelta(minutes=30),
                source="MockNews",
                sentiment="POSITIVE",
                sentiment_score=0.65,
                relevance_score=0.9
            ),
            NewsItem(
                ticker=ticker,
                headline=f"Analyst upgrades {ticker} to Buy",
                summary=f"Major analyst upgrades {ticker} citing strong fundamentals",
                published_time=now - timedelta(minutes=45),
                source="MockNews",
                sentiment="POSITIVE",
                sentiment_score=0.55,
                relevance_score=0.7
            )
        ]

        return mock_items

    def _news_item_to_dict(self, item: NewsItem) -> Dict:
        """Convert NewsItem to dictionary"""
        return {
            'ticker': item.ticker,
            'headline': item.headline,
            'summary': item.summary,
            'published_time': item.published_time,
            'source': item.source,
            'url': item.url,
            'sentiment': item.sentiment,
            'sentiment_score': item.sentiment_score,
            'relevance_score': item.relevance_score,
            'metadata': item.metadata
        }

    async def get_breaking_news(
        self,
        tickers: List[str],
        minutes_back: int = 15,
        min_relevance: float = 0.7
    ) -> List[Dict]:
        """
        Get only breaking/high-relevance news

        Args:
            tickers: List of tickers to scan
            minutes_back: How recent (default: 15 min)
            min_relevance: Minimum relevance score (0-1)

        Returns:
            List of high-relevance news items
        """
        all_news = await self.scan_recent_news(tickers, minutes_back)

        # Filter for high relevance and strong sentiment
        breaking = [
            news for news in all_news
            if news.get('relevance_score', 0) >= min_relevance or
               abs(news.get('sentiment_score', 0)) >= 0.6
        ]

        return breaking

    async def get_sentiment_changes(
        self,
        ticker: str,
        hours_back: int = 24
    ) -> Dict:
        """
        Analyze sentiment changes over time

        Args:
            ticker: Ticker symbol
            hours_back: How far back to analyze

        Returns:
            Dictionary with sentiment statistics
        """
        news_items = await self._fetch_ticker_news(ticker, hours_back * 60)

        if not news_items:
            return {
                'ticker': ticker,
                'avg_sentiment': 0.0,
                'sentiment_trend': 'NEUTRAL',
                'article_count': 0
            }

        # Calculate average sentiment
        sentiments = [item.sentiment_score for item in news_items]
        avg_sentiment = sum(sentiments) / len(sentiments)

        # Determine trend (compare first half vs second half)
        mid_point = len(sentiments) // 2
        if mid_point > 0:
            first_half_avg = sum(sentiments[:mid_point]) / mid_point
            second_half_avg = sum(sentiments[mid_point:]) / (len(sentiments) - mid_point)

            if second_half_avg > first_half_avg + 0.1:
                trend = 'IMPROVING'
            elif second_half_avg < first_half_avg - 0.1:
                trend = 'DECLINING'
            else:
                trend = 'STABLE'
        else:
            trend = 'INSUFFICIENT_DATA'

        return {
            'ticker': ticker,
            'avg_sentiment': avg_sentiment,
            'sentiment_trend': trend,
            'article_count': len(news_items),
            'recent_articles': [
                {
                    'headline': item.headline,
                    'sentiment': item.sentiment,
                    'sentiment_score': item.sentiment_score,
                    'published_time': item.published_time.isoformat()
                }
                for item in news_items[:5]  # Most recent 5
            ]
        }

    def clear_cache(self, ticker: Optional[str] = None) -> None:
        """Clear news cache"""
        if ticker:
            ticker = ticker.upper()
            self.news_cache.pop(ticker, None)
            self.cache_timestamps.pop(ticker, None)
            logger.info(f"Cleared news cache for {ticker}")
        else:
            self.news_cache.clear()
            self.cache_timestamps.clear()
            self.seen_headlines.clear()
            logger.info("Cleared all news cache")

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_items = sum(len(items) for items in self.news_cache.values())

        return {
            'cached_tickers': len(self.news_cache),
            'total_cached_items': total_items,
            'unique_headlines': len(self.seen_headlines)
        }
