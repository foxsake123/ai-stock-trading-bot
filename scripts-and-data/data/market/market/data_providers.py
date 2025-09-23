"""
Comprehensive Data Provider Module
Integrates multiple data sources for the AI Trading Bot
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import yfinance as yf
from dotenv import load_dotenv
import logging
from functools import lru_cache
import asyncio
import aiohttp
from alpaca_trade_api import REST
import praw  # Reddit API
import tweepy  # Twitter API

# Load environment variables
load_dotenv()

logger = logging.getLogger("data_providers")

class DataProviderHub:
    """
    Central hub for all data providers
    Manages API keys, rate limiting, and caching
    """
    
    def __init__(self):
        # Initialize API keys from environment
        self.api_keys = {
            'polygon': os.getenv('POLYGON_API_KEY'),
            'alpha_vantage': os.getenv('ALPHA_VANTAGE_API_KEY'),
            'newsapi': os.getenv('NEWSAPI_KEY'),
            'finnhub': os.getenv('FINNHUB_API_KEY'),
            'fred': os.getenv('FRED_API_KEY'),
            'twitter': os.getenv('TWITTER_BEARER_TOKEN'),
            'reddit_client': os.getenv('REDDIT_CLIENT_ID'),
            'reddit_secret': os.getenv('REDDIT_CLIENT_SECRET'),
            'alpaca_key': os.getenv('ALPACA_API_KEY'),
            'alpaca_secret': os.getenv('ALPACA_SECRET_KEY'),
            'iex_cloud': os.getenv('IEX_CLOUD_TOKEN'),
            'quandl': os.getenv('QUANDL_API_KEY')
        }
        
        # Initialize providers
        self.providers = {}
        self._initialize_providers()
        
        # Cache settings
        self.cache_ttl = {
            'market_data': 60,      # 1 minute
            'fundamental': 3600,    # 1 hour
            'news': 300,           # 5 minutes
            'social': 180,         # 3 minutes
            'economic': 86400      # 1 day
        }
        
    def _initialize_providers(self):
        """Initialize all data provider instances"""
        self.providers['market'] = MarketDataProvider(self.api_keys)
        self.providers['fundamental'] = FundamentalDataProvider(self.api_keys)
        self.providers['news'] = NewsDataProvider(self.api_keys)
        self.providers['social'] = SocialSentimentProvider(self.api_keys)
        self.providers['options'] = OptionsDataProvider(self.api_keys)
        self.providers['alternative'] = AlternativeDataProvider(self.api_keys)
        self.providers['economic'] = EconomicDataProvider(self.api_keys)
        
    async def get_comprehensive_data(self, ticker: str) -> Dict[str, Any]:
        """
        Get all available data for a ticker
        
        Returns:
            Comprehensive data package for analysis
        """
        tasks = [
            self.providers['market'].get_real_time_quote(ticker),
            self.providers['fundamental'].get_fundamentals(ticker),
            self.providers['news'].get_news(ticker),
            self.providers['social'].get_sentiment(ticker),
            self.providers['options'].get_options_flow(ticker),
            self.providers['alternative'].get_alternative_data(ticker)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'market_data': results[0] if not isinstance(results[0], Exception) else {},
            'fundamentals': results[1] if not isinstance(results[1], Exception) else {},
            'news': results[2] if not isinstance(results[2], Exception) else [],
            'social_sentiment': results[3] if not isinstance(results[3], Exception) else {},
            'options_flow': results[4] if not isinstance(results[4], Exception) else {},
            'alternative_data': results[5] if not isinstance(results[5], Exception) else {}
        }

class MarketDataProvider:
    """
    Real-time and historical market data from multiple sources
    Priority: Polygon.io > Alpha Vantage > IEX Cloud > yfinance
    """
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.polygon_base = "https://api.polygon.io"
        self.alpha_vantage_base = "https://www.alphavantage.co/query"
        self.iex_base = "https://cloud.iexapis.com/stable"
        
    async def get_real_time_quote(self, ticker: str) -> Dict[str, Any]:
        """Get real-time quote with fallback sources"""
        
        # Try Polygon.io first (best real-time data)
        if self.api_keys.get('polygon'):
            try:
                return await self._get_polygon_quote(ticker)
            except Exception as e:
                logger.warning(f"Polygon failed for {ticker}: {e}")
        
        # Fallback to Alpha Vantage
        if self.api_keys.get('alpha_vantage'):
            try:
                return await self._get_alpha_vantage_quote(ticker)
            except Exception as e:
                logger.warning(f"Alpha Vantage failed for {ticker}: {e}")
        
        # Fallback to IEX Cloud
        if self.api_keys.get('iex_cloud'):
            try:
                return await self._get_iex_quote(ticker)
            except Exception as e:
                logger.warning(f"IEX failed for {ticker}: {e}")
        
        # Final fallback to yfinance
        return self._get_yfinance_quote(ticker)
    
    async def _get_polygon_quote(self, ticker: str) -> Dict[str, Any]:
        """Get quote from Polygon.io"""
        url = f"{self.polygon_base}/v2/last/nbbo/{ticker}"
        params = {'apiKey': self.api_keys['polygon']}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                if data['status'] == 'OK':
                    result = data['results']
                    return {
                        'source': 'polygon',
                        'price': result['P'],
                        'bid': result['p'],
                        'ask': result['P'],
                        'volume': result['s'],
                        'timestamp': result['t'],
                        'real_time': True
                    }
                raise Exception(f"Polygon API error: {data}")
    
    async def _get_alpha_vantage_quote(self, ticker: str) -> Dict[str, Any]:
        """Get quote from Alpha Vantage"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': ticker,
            'apikey': self.api_keys['alpha_vantage']
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.alpha_vantage_base, params=params) as response:
                data = await response.json()
                
                if 'Global Quote' in data:
                    quote = data['Global Quote']
                    return {
                        'source': 'alpha_vantage',
                        'price': float(quote['05. price']),
                        'open': float(quote['02. open']),
                        'high': float(quote['03. high']),
                        'low': float(quote['04. low']),
                        'volume': int(quote['06. volume']),
                        'change': float(quote['09. change']),
                        'change_pct': quote['10. change percent'],
                        'real_time': False  # 15-min delay
                    }
                raise Exception(f"Alpha Vantage API error: {data}")
    
    async def _get_iex_quote(self, ticker: str) -> Dict[str, Any]:
        """Get quote from IEX Cloud"""
        url = f"{self.iex_base}/stock/{ticker}/quote"
        params = {'token': self.api_keys['iex_cloud']}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                return {
                    'source': 'iex',
                    'price': data['latestPrice'],
                    'open': data['open'],
                    'high': data['high'],
                    'low': data['low'],
                    'volume': data['volume'],
                    'market_cap': data['marketCap'],
                    'pe_ratio': data['peRatio'],
                    'real_time': data['isUSMarketOpen']
                }
    
    def _get_yfinance_quote(self, ticker: str) -> Dict[str, Any]:
        """Fallback to yfinance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'source': 'yfinance',
                'price': info.get('regularMarketPrice', 0),
                'volume': info.get('regularMarketVolume', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'real_time': False
            }
        except Exception as e:
            logger.error(f"yfinance failed for {ticker}: {e}")
            return {}
    
    async def get_historical_data(self, ticker: str, period: str = '1mo') -> pd.DataFrame:
        """Get historical price data"""
        # Polygon.io has the best historical data
        if self.api_keys.get('polygon'):
            try:
                return await self._get_polygon_historical(ticker, period)
            except Exception as e:
                logger.warning(f"Polygon historical failed: {e}")
        
        # Fallback to yfinance
        stock = yf.Ticker(ticker)
        return stock.history(period=period)
    
    async def _get_polygon_historical(self, ticker: str, period: str) -> pd.DataFrame:
        """Get historical data from Polygon"""
        # Convert period to date range
        end_date = datetime.now()
        period_map = {
            '1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365
        }
        days = period_map.get(period, 30)
        start_date = end_date - timedelta(days=days)
        
        url = f"{self.polygon_base}/v2/aggs/ticker/{ticker}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
        params = {'apiKey': self.api_keys['polygon']}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                if data['status'] == 'OK':
                    df = pd.DataFrame(data['results'])
                    df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
                    df.set_index('timestamp', inplace=True)
                    df.rename(columns={'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'}, inplace=True)
                    return df
                raise Exception(f"Polygon historical error: {data}")

class FundamentalDataProvider:
    """
    Fundamental data from multiple sources
    """
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        
    async def get_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive fundamental data"""
        fundamentals = {}
        
        # Get data from multiple sources
        tasks = []
        
        if self.api_keys.get('polygon'):
            tasks.append(self._get_polygon_fundamentals(ticker))
        
        if self.api_keys.get('alpha_vantage'):
            tasks.append(self._get_alpha_vantage_fundamentals(ticker))
        
        # Always include yfinance
        tasks.append(self._get_yfinance_fundamentals(ticker))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Merge results
        for result in results:
            if not isinstance(result, Exception):
                fundamentals.update(result)
        
        return fundamentals
    
    async def _get_polygon_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """Get fundamentals from Polygon"""
        url = f"{self.polygon_base}/v2/reference/financials/{ticker}"
        params = {'apiKey': self.api_keys['polygon'], 'limit': 1}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                if data['status'] == 'OK' and data['results']:
                    financials = data['results'][0]
                    return {
                        'revenue': financials.get('revenues', 0),
                        'earnings': financials.get('net_income', 0),
                        'assets': financials.get('assets', 0),
                        'liabilities': financials.get('liabilities', 0),
                        'source': 'polygon'
                    }
        return {}
    
    async def _get_alpha_vantage_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """Get fundamentals from Alpha Vantage"""
        params = {
            'function': 'OVERVIEW',
            'symbol': ticker,
            'apikey': self.api_keys['alpha_vantage']
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.alphavantage.co/query", params=params) as response:
                data = await response.json()
                
                if 'Symbol' in data:
                    return {
                        'market_cap': float(data.get('MarketCapitalization', 0)),
                        'pe_ratio': float(data.get('PERatio', 0)),
                        'peg_ratio': float(data.get('PEGRatio', 0)),
                        'dividend_yield': float(data.get('DividendYield', 0)),
                        'profit_margin': float(data.get('ProfitMargin', 0)),
                        'roe': float(data.get('ReturnOnEquityTTM', 0)),
                        'revenue_ttm': float(data.get('RevenueTTM', 0)),
                        'source_fundamental': 'alpha_vantage'
                    }
        return {}
    
    async def _get_yfinance_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """Get fundamentals from yfinance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'trailing_pe': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'price_to_book': info.get('priceToBook', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'gross_margins': info.get('grossMargins', 0),
                'operating_margins': info.get('operatingMargins', 0),
                'source_yfinance': 'yfinance'
            }
        except:
            return {}

class NewsDataProvider:
    """
    News data from multiple sources
    """
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.newsapi_base = "https://newsapi.org/v2"
        self.finnhub_base = "https://finnhub.io/api/v1"
        
    async def get_news(self, ticker: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get news from multiple sources"""
        all_news = []
        
        # Get news from different providers
        tasks = []
        
        if self.api_keys.get('newsapi'):
            tasks.append(self._get_newsapi_news(ticker, limit))
        
        if self.api_keys.get('finnhub'):
            tasks.append(self._get_finnhub_news(ticker, limit))
        
        if self.api_keys.get('polygon'):
            tasks.append(self._get_polygon_news(ticker, limit))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine and deduplicate news
        for result in results:
            if not isinstance(result, Exception):
                all_news.extend(result)
        
        # Sort by date and limit
        all_news.sort(key=lambda x: x.get('published_date', ''), reverse=True)
        
        return all_news[:limit]
    
    async def _get_newsapi_news(self, ticker: str, limit: int) -> List[Dict[str, Any]]:
        """Get news from NewsAPI"""
        url = f"{self.newsapi_base}/everything"
        params = {
            'q': ticker,
            'apiKey': self.api_keys['newsapi'],
            'sortBy': 'publishedAt',
            'pageSize': limit,
            'language': 'en'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                if data['status'] == 'ok':
                    return [{
                        'title': article['title'],
                        'description': article['description'],
                        'url': article['url'],
                        'source': article['source']['name'],
                        'published_date': article['publishedAt'],
                        'sentiment': None,  # Would need NLP analysis
                        'provider': 'newsapi'
                    } for article in data['articles']]
        return []
    
    async def _get_finnhub_news(self, ticker: str, limit: int) -> List[Dict[str, Any]]:
        """Get news from Finnhub"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        url = f"{self.finnhub_base}/company-news"
        params = {
            'symbol': ticker,
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'token': self.api_keys['finnhub']
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                return [{
                    'title': article['headline'],
                    'description': article['summary'],
                    'url': article['url'],
                    'source': article['source'],
                    'published_date': datetime.fromtimestamp(article['datetime']).isoformat(),
                    'sentiment': self._classify_sentiment(article['summary']),
                    'provider': 'finnhub'
                } for article in data[:limit]]
    
    async def _get_polygon_news(self, ticker: str, limit: int) -> List[Dict[str, Any]]:
        """Get news from Polygon"""
        url = f"https://api.polygon.io/v2/reference/news"
        params = {
            'ticker': ticker,
            'limit': limit,
            'apiKey': self.api_keys['polygon']
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                if data['status'] == 'OK':
                    return [{
                        'title': article['title'],
                        'description': article['description'],
                        'url': article['article_url'],
                        'source': article['publisher']['name'],
                        'published_date': article['published_utc'],
                        'sentiment': None,
                        'provider': 'polygon'
                    } for article in data.get('results', [])]
        return []
    
    def _classify_sentiment(self, text: str) -> str:
        """Simple sentiment classification"""
        positive_words = ['beat', 'exceed', 'upgrade', 'positive', 'growth', 'surge']
        negative_words = ['miss', 'downgrade', 'negative', 'decline', 'fall', 'concern']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

class SocialSentimentProvider:
    """
    Social media sentiment from Reddit, Twitter, StockTwits
    """
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self._init_reddit()
        self._init_twitter()
        
    def _init_reddit(self):
        """Initialize Reddit API"""
        if self.api_keys.get('reddit_client') and self.api_keys.get('reddit_secret'):
            self.reddit = praw.Reddit(
                client_id=self.api_keys['reddit_client'],
                client_secret=self.api_keys['reddit_secret'],
                user_agent='TradingBot/1.0'
            )
        else:
            self.reddit = None
            
    def _init_twitter(self):
        """Initialize Twitter API"""
        if self.api_keys.get('twitter'):
            self.twitter = tweepy.Client(bearer_token=self.api_keys['twitter'])
        else:
            self.twitter = None
    
    async def get_sentiment(self, ticker: str) -> Dict[str, Any]:
        """Get social sentiment from multiple platforms"""
        sentiment_data = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'platforms': {}
        }
        
        # Get Reddit sentiment
        if self.reddit:
            sentiment_data['platforms']['reddit'] = await self._get_reddit_sentiment(ticker)
        
        # Get Twitter sentiment
        if self.twitter:
            sentiment_data['platforms']['twitter'] = await self._get_twitter_sentiment(ticker)
        
        # Calculate aggregate sentiment
        sentiment_data['aggregate'] = self._calculate_aggregate_sentiment(sentiment_data['platforms'])
        
        return sentiment_data
    
    async def _get_reddit_sentiment(self, ticker: str) -> Dict[str, Any]:
        """Get sentiment from Reddit (WSB, stocks, investing)"""
        subreddits = ['wallstreetbets', 'stocks', 'investing', 'StockMarket']
        posts = []
        
        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                for post in subreddit.search(ticker, limit=10, time_filter='day'):
                    posts.append({
                        'title': post.title,
                        'score': post.score,
                        'comments': post.num_comments,
                        'created': datetime.fromtimestamp(post.created_utc).isoformat()
                    })
            except Exception as e:
                logger.warning(f"Reddit error for {subreddit_name}: {e}")
        
        # Analyze sentiment
        bullish = sum(1 for p in posts if any(word in p['title'].lower() 
                     for word in ['moon', 'call', 'bull', 'buy', 'long']))
        bearish = sum(1 for p in posts if any(word in p['title'].lower() 
                     for word in ['put', 'bear', 'sell', 'short']))
        
        return {
            'posts': len(posts),
            'bullish': bullish,
            'bearish': bearish,
            'sentiment_score': (bullish - bearish) / max(1, len(posts)),
            'top_posts': posts[:5]
        }
    
    async def _get_twitter_sentiment(self, ticker: str) -> Dict[str, Any]:
        """Get sentiment from Twitter"""
        try:
            # Search for recent tweets
            query = f"${ticker} -is:retweet lang:en"
            tweets = self.twitter.search_recent_tweets(
                query=query,
                max_results=100,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            if tweets.data:
                bullish = 0
                bearish = 0
                total_engagement = 0
                
                for tweet in tweets.data:
                    text = tweet.text.lower()
                    metrics = tweet.public_metrics
                    engagement = metrics['like_count'] + metrics['retweet_count']
                    
                    if any(word in text for word in ['bull', 'buy', 'long', 'call', 'moon']):
                        bullish += 1 + (engagement / 100)
                    elif any(word in text for word in ['bear', 'sell', 'short', 'put']):
                        bearish += 1 + (engagement / 100)
                    
                    total_engagement += engagement
                
                return {
                    'tweets': len(tweets.data),
                    'bullish': bullish,
                    'bearish': bearish,
                    'sentiment_score': (bullish - bearish) / max(1, len(tweets.data)),
                    'total_engagement': total_engagement
                }
        except Exception as e:
            logger.warning(f"Twitter error: {e}")
            
        return {}
    
    def _calculate_aggregate_sentiment(self, platforms: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate aggregate sentiment across platforms"""
        total_bullish = 0
        total_bearish = 0
        total_posts = 0
        
        for platform, data in platforms.items():
            if data:
                total_bullish += data.get('bullish', 0)
                total_bearish += data.get('bearish', 0)
                total_posts += data.get('posts', 0) or data.get('tweets', 0)
        
        if total_posts > 0:
            sentiment_score = (total_bullish - total_bearish) / total_posts
        else:
            sentiment_score = 0
        
        return {
            'total_bullish': total_bullish,
            'total_bearish': total_bearish,
            'total_posts': total_posts,
            'sentiment_score': sentiment_score,
            'sentiment_label': 'bullish' if sentiment_score > 0.2 else 'bearish' if sentiment_score < -0.2 else 'neutral'
        }

class OptionsDataProvider:
    """
    Options flow and unusual activity data
    """
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        
    async def get_options_flow(self, ticker: str) -> Dict[str, Any]:
        """Get options flow data"""
        options_data = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat()
        }
        
        # Get options chain from yfinance as baseline
        try:
            stock = yf.Ticker(ticker)
            expirations = stock.options[:3]  # Next 3 expirations
            
            total_call_volume = 0
            total_put_volume = 0
            total_call_oi = 0
            total_put_oi = 0
            
            for exp in expirations:
                opt = stock.option_chain(exp)
                total_call_volume += opt.calls['volume'].sum()
                total_put_volume += opt.puts['volume'].sum()
                total_call_oi += opt.calls['openInterest'].sum()
                total_put_oi += opt.puts['openInterest'].sum()
            
            put_call_ratio = total_put_volume / max(1, total_call_volume)
            
            options_data.update({
                'call_volume': total_call_volume,
                'put_volume': total_put_volume,
                'put_call_ratio': put_call_ratio,
                'call_oi': total_call_oi,
                'put_oi': total_put_oi,
                'sentiment': 'bullish' if put_call_ratio < 0.7 else 'bearish' if put_call_ratio > 1.3 else 'neutral'
            })
            
        except Exception as e:
            logger.warning(f"Options data error for {ticker}: {e}")
            
        return options_data

class AlternativeDataProvider:
    """
    Alternative data sources (satellite, web traffic, app downloads, etc.)
    """
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        
    async def get_alternative_data(self, ticker: str) -> Dict[str, Any]:
        """Get alternative data signals"""
        alt_data = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat()
        }
        
        # This would integrate with providers like:
        # - Quandl for alternative datasets
        # - SimilarWeb for web traffic
        # - App Annie for app metrics
        # - Satellite data providers
        
        # Placeholder for now
        alt_data['signals'] = {
            'web_traffic_trend': 'increasing',
            'app_downloads_trend': 'stable',
            'satellite_activity': 'normal'
        }
        
        return alt_data

class EconomicDataProvider:
    """
    Economic indicators from FRED and other sources
    """
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.fred_base = "https://api.stlouisfed.org/fred"
        
    async def get_economic_indicators(self) -> Dict[str, Any]:
        """Get key economic indicators"""
        indicators = {}
        
        if self.api_keys.get('fred'):
            # Get key indicators
            series_ids = {
                'DGS10': '10_year_treasury',
                'DFF': 'fed_funds_rate',
                'UNRATE': 'unemployment_rate',
                'CPIAUCSL': 'cpi',
                'DEXUSEU': 'usd_eur',
                'VIXCLS': 'vix'
            }
            
            for series_id, name in series_ids.items():
                try:
                    value = await self._get_fred_series(series_id)
                    indicators[name] = value
                except Exception as e:
                    logger.warning(f"FRED error for {series_id}: {e}")
        
        return indicators
    
    async def _get_fred_series(self, series_id: str) -> float:
        """Get single FRED series value"""
        url = f"{self.fred_base}/series/observations"
        params = {
            'series_id': series_id,
            'api_key': self.api_keys['fred'],
            'file_type': 'json',
            'limit': 1,
            'sort_order': 'desc'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                if 'observations' in data and data['observations']:
                    return float(data['observations'][0]['value'])
        
        return 0.0