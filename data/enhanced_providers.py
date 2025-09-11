"""
Enhanced Data Providers with API Integration
Handles optional dependencies gracefully
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import asyncio
import aiohttp
from dotenv import load_dotenv
import yfinance as yf

# Optional imports
try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False

try:
    from newsapi import NewsApiClient
    NEWSAPI_AVAILABLE = True
except ImportError:
    NEWSAPI_AVAILABLE = False

try:
    from polygon import RESTClient as PolygonClient
    POLYGON_AVAILABLE = True
except ImportError:
    POLYGON_AVAILABLE = False

try:
    from fredapi import Fred
    FRED_AVAILABLE = True
except ImportError:
    FRED_AVAILABLE = False

# Load environment variables
load_dotenv()

logger = logging.getLogger("enhanced_providers")

class EnhancedDataHub:
    """
    Enhanced data hub with actual API implementations
    """
    
    def __init__(self):
        self.market_provider = EnhancedMarketProvider()
        self.news_provider = EnhancedNewsProvider()
        self.sentiment_provider = EnhancedSentimentProvider()
        
    async def get_market_data(self, ticker: str) -> Dict[str, Any]:
        """Get market data with source tracking"""
        return await self.market_provider.get_quote(ticker)
    
    async def get_news(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get news from available sources"""
        return await self.news_provider.get_news(ticker, limit)
    
    async def get_social_sentiment(self, ticker: str) -> Dict[str, Any]:
        """Get social sentiment data"""
        return await self.sentiment_provider.get_sentiment(ticker)
    
    async def get_options_flow(self, ticker: str) -> Dict[str, Any]:
        """Get options flow data"""
        # Placeholder for options data
        return {
            'ticker': ticker,
            'put_call_ratio': 0.85,
            'unusual_activity': [],
            'source': 'yfinance'
        }
    
    async def get_economic_indicators(self) -> Dict[str, Any]:
        """Get economic indicators"""
        indicators = {}
        
        if FRED_AVAILABLE and os.getenv('FRED_API_KEY'):
            try:
                fred = Fred(api_key=os.getenv('FRED_API_KEY'))
                # Get key indicators
                indicators['gdp'] = fred.get_series_latest_release('GDP')
                indicators['unemployment'] = fred.get_series_latest_release('UNRATE')
                indicators['inflation'] = fred.get_series_latest_release('CPIAUCSL')
            except Exception as e:
                logger.warning(f"FRED API error: {e}")
        
        # Fallback values
        if not indicators:
            indicators = {
                'gdp': 'N/A',
                'unemployment': 'N/A',
                'inflation': 'N/A',
                'source': 'unavailable'
            }
        
        return indicators

class EnhancedMarketProvider:
    """
    Market data provider with multiple source fallback
    """
    
    def __init__(self):
        self.polygon_key = os.getenv('POLYGON_API_KEY')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.iex_token = os.getenv('IEX_CLOUD_TOKEN')
        
    async def get_quote(self, ticker: str) -> Dict[str, Any]:
        """Get real-time quote with fallback"""
        
        # Try Polygon first
        if POLYGON_AVAILABLE and self.polygon_key:
            try:
                client = PolygonClient(self.polygon_key)
                quote = client.get_last_quote(ticker)
                if quote:
                    return {
                        'ticker': ticker,
                        'price': float(quote.ask_price or quote.bid_price or 0),
                        'volume': 0,  # Would need trades endpoint for volume
                        'bid': float(quote.bid_price or 0),
                        'ask': float(quote.ask_price or 0),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'polygon'
                    }
            except Exception as e:
                logger.warning(f"Polygon error for {ticker}: {e}")
        
        # Try Alpha Vantage
        if self.alpha_vantage_key and self.alpha_vantage_key != 'your_alpha_vantage_api_key_here':
            try:
                url = f"https://www.alphavantage.co/query"
                params = {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': ticker,
                    'apikey': self.alpha_vantage_key
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        data = await response.json()
                        if 'Global Quote' in data:
                            quote = data['Global Quote']
                            return {
                                'ticker': ticker,
                                'price': float(quote.get('05. price', 0)),
                                'volume': int(quote.get('06. volume', 0)),
                                'open': float(quote.get('02. open', 0)),
                                'high': float(quote.get('03. high', 0)),
                                'low': float(quote.get('04. low', 0)),
                                'previous_close': float(quote.get('08. previous close', 0)),
                                'change': float(quote.get('09. change', 0)),
                                'change_percent': quote.get('10. change percent', '0%'),
                                'timestamp': quote.get('07. latest trading day', ''),
                                'source': 'alpha_vantage'
                            }
            except Exception as e:
                logger.warning(f"Alpha Vantage error for {ticker}: {e}")
        
        # Fallback to yfinance
        try:
            stock = yf.Ticker(ticker)
            # Add small delay to avoid rate limiting
            import time
            time.sleep(0.5)
            info = stock.info
            hist = stock.history(period="1d", interval="1m")
            
            current_price = info.get('regularMarketPrice', 0)
            if current_price == 0 and not hist.empty:
                current_price = hist['Close'].iloc[-1]
            
            return {
                'ticker': ticker,
                'price': current_price,
                'volume': info.get('regularMarketVolume', 0),
                'open': info.get('regularMarketOpen', 0),
                'high': info.get('regularMarketDayHigh', 0),
                'low': info.get('regularMarketDayLow', 0),
                'previous_close': info.get('regularMarketPreviousClose', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'timestamp': datetime.now().isoformat(),
                'source': 'yfinance'
            }
        except Exception as e:
            logger.error(f"All market data sources failed for {ticker}: {e}")
            return {
                'ticker': ticker,
                'price': 0,
                'error': str(e),
                'source': 'none'
            }

class EnhancedNewsProvider:
    """
    News provider with multiple sources
    """
    
    def __init__(self):
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
        self.finnhub_key = os.getenv('FINNHUB_API_KEY')
        
    async def get_news(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get news from available sources"""
        all_news = []
        
        # Try NewsAPI
        if NEWSAPI_AVAILABLE and self.newsapi_key:
            try:
                newsapi = NewsApiClient(api_key=self.newsapi_key)
                # Get news for the ticker
                articles = newsapi.get_everything(
                    q=ticker,
                    language='en',
                    sort_by='publishedAt',
                    page_size=limit
                )
                
                if articles.get('articles'):
                    for article in articles['articles']:
                        all_news.append({
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'url': article.get('url', ''),
                            'source': article.get('source', {}).get('name', 'NewsAPI'),
                            'published_date': article.get('publishedAt', ''),
                            'sentiment': None  # Would need NLP analysis
                        })
            except Exception as e:
                logger.warning(f"NewsAPI error for {ticker}: {e}")
        
        # Try Finnhub
        if self.finnhub_key:
            try:
                url = f"https://finnhub.io/api/v1/company-news"
                today = datetime.now().strftime('%Y-%m-%d')
                week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                
                params = {
                    'symbol': ticker,
                    'from': week_ago,
                    'to': today,
                    'token': self.finnhub_key
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        articles = await response.json()
                        for article in articles[:limit]:
                            all_news.append({
                                'title': article.get('headline', ''),
                                'description': article.get('summary', ''),
                                'url': article.get('url', ''),
                                'source': article.get('source', 'Finnhub'),
                                'published_date': datetime.fromtimestamp(article.get('datetime', 0)).isoformat(),
                                'sentiment': None
                            })
            except Exception as e:
                logger.warning(f"Finnhub error for {ticker}: {e}")
        
        # Fallback to yfinance news
        if not all_news:
            try:
                stock = yf.Ticker(ticker)
                news = stock.news
                if news:
                    for article in news[:limit]:
                        all_news.append({
                            'title': article.get('title', ''),
                            'description': '',
                            'url': article.get('link', ''),
                            'source': article.get('publisher', 'Yahoo Finance'),
                            'published_date': datetime.fromtimestamp(article.get('providerPublishTime', 0)).isoformat(),
                            'sentiment': None
                        })
            except Exception as e:
                logger.warning(f"yfinance news error for {ticker}: {e}")
        
        return all_news[:limit]

class EnhancedSentimentProvider:
    """
    Social sentiment provider
    """
    
    def __init__(self):
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        self.reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.twitter_bearer = os.getenv('TWITTER_BEARER_TOKEN')
        
    async def get_sentiment(self, ticker: str) -> Dict[str, Any]:
        """Get social sentiment data"""
        sentiment_data = {
            'ticker': ticker,
            'overall_score': 0.5,  # Neutral
            'sources': []
        }
        
        # Reddit sentiment
        if PRAW_AVAILABLE and self.reddit_client_id and self.reddit_client_id != 'your_reddit_client_id_here':
            try:
                reddit = praw.Reddit(
                    client_id=self.reddit_client_id,
                    client_secret=self.reddit_secret,
                    user_agent='TradingBot/1.0'
                )
                
                # Search wallstreetbets for the ticker
                wsb = reddit.subreddit('wallstreetbets')
                mentions = 0
                sentiment_sum = 0
                
                for submission in wsb.search(ticker, limit=10, time_filter='day'):
                    mentions += 1
                    # Simple sentiment based on score
                    if submission.score > 100:
                        sentiment_sum += 0.7
                    elif submission.score > 50:
                        sentiment_sum += 0.6
                    else:
                        sentiment_sum += 0.5
                
                if mentions > 0:
                    reddit_score = sentiment_sum / mentions
                    sentiment_data['reddit_score'] = reddit_score
                    sentiment_data['reddit_mentions'] = mentions
                    sentiment_data['sources'].append('reddit')
            except Exception as e:
                logger.warning(f"Reddit API error for {ticker}: {e}")
        
        # Twitter sentiment (placeholder - Twitter API v2 requires more setup)
        if self.twitter_bearer:
            sentiment_data['twitter_score'] = 0.5  # Placeholder
            sentiment_data['sources'].append('twitter_placeholder')
        
        # Calculate overall sentiment
        scores = []
        if 'reddit_score' in sentiment_data:
            scores.append(sentiment_data['reddit_score'])
        if 'twitter_score' in sentiment_data:
            scores.append(sentiment_data['twitter_score'])
        
        if scores:
            sentiment_data['overall_score'] = sum(scores) / len(scores)
        
        return sentiment_data