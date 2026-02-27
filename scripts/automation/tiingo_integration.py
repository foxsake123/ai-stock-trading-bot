#!/usr/bin/env python3
"""
Tiingo API Integration - Full Suite
- EOD prices (daily bars)
- IEX real-time quotes
- Financial news with sentiment
- Fundamentals (P/E, margins, etc)
- Crypto prices
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class TiingoAPI:
    """
    Full Tiingo API Integration
    
    Free tier: 500 symbols/month, 1000 req/day
    Paid ($30/mo): 100k req/day, 30yr history, fundamentals
    """

    def __init__(self):
        self.api_key = os.getenv('TIINGO_API_KEY')
        if not self.api_key:
            print("Warning: TIINGO_API_KEY not set in .env")
        
        self.base_url = "https://api.tiingo.com"
        self.headers = {
            'Authorization': f'Token {self.api_key}',
            'Content-Type': 'application/json'
        }

    # =========================================================================
    # EOD PRICES (Daily bars)
    # =========================================================================
    
    def get_historical_prices(self, ticker: str, interval: str = 'day',
                              start_date: str = None, end_date: str = None,
                              limit: int = 1000) -> pd.DataFrame:
        """
        Get historical EOD price data
        
        Args:
            ticker: Stock symbol
            interval: 'day' (free tier only supports daily)
            start_date: YYYY-MM-DD format
            end_date: YYYY-MM-DD format
        
        Returns:
            DataFrame with OHLCV data (capitalized columns)
        """
        if not self.api_key:
            return pd.DataFrame()
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        endpoint = f"{self.base_url}/tiingo/daily/{ticker.upper()}/prices"
        params = {'startDate': start_date, 'endDate': end_date}

        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list):
                    df = pd.DataFrame(data)
                    if 'date' in df.columns:
                        df['datetime'] = pd.to_datetime(df['date'])
                        df = df.set_index('datetime')
                        df = df.rename(columns={
                            'open': 'Open', 'high': 'High', 'low': 'Low',
                            'close': 'Close', 'volume': 'Volume',
                            'adjOpen': 'Adj_Open', 'adjHigh': 'Adj_High',
                            'adjLow': 'Adj_Low', 'adjClose': 'Adj_Close',
                            'adjVolume': 'Adj_Volume'
                        })
                        return df
            return pd.DataFrame()
        except Exception as e:
            print(f"Tiingo EOD error for {ticker}: {e}")
            return pd.DataFrame()

    # =========================================================================
    # IEX REAL-TIME QUOTES
    # =========================================================================
    
    def get_realtime_quote(self, ticker: str) -> Dict:
        """
        Get real-time IEX quote (during market hours)
        
        Returns:
            Dict with bid, ask, last, volume, timestamp
        """
        if not self.api_key:
            return {}
        
        endpoint = f"{self.base_url}/iex/{ticker.upper()}"
        
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    quote = data[0]
                    return {
                        'ticker': ticker.upper(),
                        'last': quote.get('last'),
                        'bid': quote.get('bidPrice'),
                        'ask': quote.get('askPrice'),
                        'bid_size': quote.get('bidSize'),
                        'ask_size': quote.get('askSize'),
                        'volume': quote.get('volume'),
                        'timestamp': quote.get('timestamp'),
                        'source': 'iex_realtime'
                    }
            return {}
        except Exception as e:
            print(f"Tiingo IEX error for {ticker}: {e}")
            return {}

    def get_realtime_quotes_bulk(self, tickers: List[str]) -> List[Dict]:
        """Get real-time quotes for multiple tickers"""
        if not self.api_key or not tickers:
            return []
        
        ticker_str = ','.join([t.upper() for t in tickers])
        endpoint = f"{self.base_url}/iex/"
        params = {'tickers': ticker_str}
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                results = []
                for quote in data:
                    results.append({
                        'ticker': quote.get('ticker'),
                        'last': quote.get('last'),
                        'bid': quote.get('bidPrice'),
                        'ask': quote.get('askPrice'),
                        'volume': quote.get('volume'),
                        'timestamp': quote.get('timestamp'),
                        'source': 'iex_realtime'
                    })
                return results
            return []
        except Exception as e:
            print(f"Tiingo IEX bulk error: {e}")
            return []

    def get_intraday_prices(self, ticker: str, resample: str = '5min',
                            start_date: str = None) -> pd.DataFrame:
        """
        Get intraday price bars (paid tier)
        
        Args:
            ticker: Stock symbol
            resample: '1min', '5min', '15min', '30min', '1hour'
            start_date: YYYY-MM-DD (defaults to today)
        """
        if not self.api_key:
            return pd.DataFrame()
        
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        endpoint = f"{self.base_url}/iex/{ticker.upper()}/prices"
        params = {
            'startDate': start_date,
            'resampleFreq': resample
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data:
                    df = pd.DataFrame(data)
                    if 'date' in df.columns:
                        df['datetime'] = pd.to_datetime(df['date'])
                        df = df.set_index('datetime')
                        df = df.rename(columns={
                            'open': 'Open', 'high': 'High', 'low': 'Low',
                            'close': 'Close', 'volume': 'Volume'
                        })
                        return df
            return pd.DataFrame()
        except Exception as e:
            print(f"Tiingo intraday error for {ticker}: {e}")
            return pd.DataFrame()

    # =========================================================================
    # NEWS API
    # =========================================================================
    
    def get_news(self, tickers: List[str] = None, tags: List[str] = None,
                 source: str = None, limit: int = 20,
                 start_date: str = None) -> List[Dict]:
        """
        Get financial news with ticker tags
        
        Args:
            tickers: Filter by stock symbols
            tags: Filter by topic tags (e.g., 'earnings', 'merger')
            source: Filter by source (e.g., 'bloomberg')
            limit: Max articles (default 20, max 100)
            start_date: YYYY-MM-DD
        
        Returns:
            List of news articles with sentiment indicators
        """
        if not self.api_key:
            return []
        
        endpoint = f"{self.base_url}/tiingo/news"
        params = {'limit': min(limit, 100)}
        
        if tickers:
            params['tickers'] = ','.join([t.upper() for t in tickers])
        if tags:
            params['tags'] = ','.join(tags)
        if source:
            params['source'] = source
        if start_date:
            params['startDate'] = start_date
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            if response.status_code == 200:
                articles = response.json()
                results = []
                for article in articles:
                    results.append({
                        'id': article.get('id'),
                        'title': article.get('title'),
                        'description': article.get('description'),
                        'url': article.get('url'),
                        'source': article.get('source'),
                        'published': article.get('publishedDate'),
                        'tickers': article.get('tickers', []),
                        'tags': article.get('tags', []),
                        'crawled': article.get('crawlDate')
                    })
                return results
            return []
        except Exception as e:
            print(f"Tiingo news error: {e}")
            return []

    def get_news_sentiment(self, ticker: str, limit: int = 10) -> Dict:
        """
        Get news for ticker and analyze sentiment
        
        Returns:
            Dict with articles and overall sentiment score
        """
        articles = self.get_news(tickers=[ticker], limit=limit)
        
        if not articles:
            return {'ticker': ticker, 'articles': [], 'sentiment': 'neutral', 'score': 0.5}
        
        # Simple sentiment heuristics based on tags
        bullish_tags = {'earnings-beat', 'upgrade', 'buyback', 'dividend', 'growth'}
        bearish_tags = {'earnings-miss', 'downgrade', 'layoffs', 'lawsuit', 'debt'}
        
        bull_count = 0
        bear_count = 0
        
        for article in articles:
            tags = set(t.lower() for t in article.get('tags', []))
            title_lower = article.get('title', '').lower()
            
            # Check tags
            if tags & bullish_tags:
                bull_count += 1
            if tags & bearish_tags:
                bear_count += 1
            
            # Simple title keywords
            if any(w in title_lower for w in ['surge', 'jump', 'beat', 'record', 'soar']):
                bull_count += 0.5
            if any(w in title_lower for w in ['fall', 'drop', 'miss', 'cut', 'warning']):
                bear_count += 0.5
        
        total = bull_count + bear_count
        if total > 0:
            score = bull_count / total
        else:
            score = 0.5
        
        sentiment = 'bullish' if score > 0.6 else 'bearish' if score < 0.4 else 'neutral'
        
        return {
            'ticker': ticker,
            'articles': articles[:5],  # Top 5
            'article_count': len(articles),
            'sentiment': sentiment,
            'score': round(score, 2),
            'bull_signals': bull_count,
            'bear_signals': bear_count
        }

    # =========================================================================
    # FUNDAMENTALS
    # =========================================================================
    
    def get_fundamentals_meta(self, ticker: str) -> Dict:
        """
        Get fundamental metrics (P/E, margins, etc)
        Requires paid tier for full data
        """
        if not self.api_key:
            return {}
        
        endpoint = f"{self.base_url}/tiingo/fundamentals/{ticker.upper()}/meta"
        
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Tiingo fundamentals error for {ticker}: {e}")
            return {}

    def get_fundamentals_daily(self, ticker: str, start_date: str = None) -> List[Dict]:
        """
        Get daily fundamental metrics
        """
        if not self.api_key:
            return []
        
        endpoint = f"{self.base_url}/tiingo/fundamentals/{ticker.upper()}/daily"
        params = {}
        if start_date:
            params['startDate'] = start_date
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=15)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Tiingo fundamentals daily error for {ticker}: {e}")
            return []

    def get_fundamentals_statements(self, ticker: str, statement_type: str = 'overview',
                                     start_date: str = None) -> List[Dict]:
        """
        Get financial statements
        
        Args:
            ticker: Stock symbol
            statement_type: 'overview', 'income', 'balance', 'cashflow'
            start_date: YYYY-MM-DD
        """
        if not self.api_key:
            return []
        
        endpoint = f"{self.base_url}/tiingo/fundamentals/{ticker.upper()}/statements"
        params = {'type': statement_type}
        if start_date:
            params['startDate'] = start_date
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=15)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Tiingo statements error for {ticker}: {e}")
            return []

    # =========================================================================
    # CRYPTO
    # =========================================================================
    
    def get_crypto_quote(self, ticker: str, base_currency: str = 'usd') -> Dict:
        """
        Get crypto price quote
        
        Args:
            ticker: Crypto symbol (btc, eth, etc)
            base_currency: Quote currency (usd, eur, btc)
        """
        if not self.api_key:
            return {}
        
        pair = f"{ticker.lower()}{base_currency.lower()}"
        endpoint = f"{self.base_url}/tiingo/crypto/prices"
        params = {'tickers': pair}
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    quote = data[0]
                    price_data = quote.get('priceData', [{}])[0] if quote.get('priceData') else {}
                    return {
                        'ticker': ticker.upper(),
                        'pair': pair.upper(),
                        'price': price_data.get('close'),
                        'open': price_data.get('open'),
                        'high': price_data.get('high'),
                        'low': price_data.get('low'),
                        'volume': price_data.get('volume'),
                        'timestamp': price_data.get('date'),
                        'source': 'tiingo_crypto'
                    }
            return {}
        except Exception as e:
            print(f"Tiingo crypto error for {ticker}: {e}")
            return {}

    def get_crypto_prices_historical(self, ticker: str, base_currency: str = 'usd',
                                      resample: str = '1day', 
                                      start_date: str = None) -> pd.DataFrame:
        """
        Get historical crypto prices
        
        Args:
            ticker: Crypto symbol
            base_currency: Quote currency
            resample: '1min', '5min', '1hour', '1day'
        """
        if not self.api_key:
            return pd.DataFrame()
        
        pair = f"{ticker.lower()}{base_currency.lower()}"
        endpoint = f"{self.base_url}/tiingo/crypto/prices"
        params = {
            'tickers': pair,
            'resampleFreq': resample
        }
        if start_date:
            params['startDate'] = start_date
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0 and data[0].get('priceData'):
                    df = pd.DataFrame(data[0]['priceData'])
                    if 'date' in df.columns:
                        df['datetime'] = pd.to_datetime(df['date'])
                        df = df.set_index('datetime')
                        df = df.rename(columns={
                            'open': 'Open', 'high': 'High', 'low': 'Low',
                            'close': 'Close', 'volume': 'Volume'
                        })
                        return df
            return pd.DataFrame()
        except Exception as e:
            print(f"Tiingo crypto historical error for {ticker}: {e}")
            return pd.DataFrame()

    # =========================================================================
    # METADATA
    # =========================================================================
    
    def get_ticker_metadata(self, ticker: str) -> Dict:
        """Get ticker metadata (name, exchange, description)"""
        if not self.api_key:
            return {}
        
        endpoint = f"{self.base_url}/tiingo/daily/{ticker.upper()}"
        
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Tiingo metadata error for {ticker}: {e}")
            return {}

    def get_supported_tickers(self) -> pd.DataFrame:
        """Get list of all supported tickers"""
        if not self.api_key:
            return pd.DataFrame()
        
        endpoint = f"{self.base_url}/tiingo/daily"
        
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=60)
            if response.status_code == 200:
                return pd.DataFrame(response.json())
            return pd.DataFrame()
        except Exception as e:
            print(f"Tiingo tickers list error: {e}")
            return pd.DataFrame()


# =========================================================================
# CONVENIENCE FUNCTIONS
# =========================================================================

def get_tiingo_prices(ticker: str, days: int = 90) -> pd.DataFrame:
    """Quick helper for EOD prices"""
    api = TiingoAPI()
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    return api.get_historical_prices(ticker, start_date=start_date)


def get_tiingo_quote(ticker: str) -> Dict:
    """Quick helper for real-time quote"""
    api = TiingoAPI()
    return api.get_realtime_quote(ticker)


def get_tiingo_news(tickers: List[str], limit: int = 20) -> List[Dict]:
    """Quick helper for news"""
    api = TiingoAPI()
    return api.get_news(tickers=tickers, limit=limit)


# =========================================================================
# TEST
# =========================================================================

if __name__ == "__main__":
    api = TiingoAPI()
    print("="*60)
    print("TIINGO API FULL TEST")
    print("="*60)
    
    # EOD prices
    print("\n[1] EOD Prices (AAPL)...")
    df = api.get_historical_prices("AAPL", start_date="2026-02-01")
    if not df.empty:
        print(f"    [OK] Got {len(df)} daily bars")
    else:
        print("    [FAIL] No data")
    
    # Real-time quote
    print("\n[2] Real-time Quote (NVDA)...")
    quote = api.get_realtime_quote("NVDA")
    if quote:
        print(f"    [OK] Last: ${quote.get('last')}, Bid: ${quote.get('bid')}, Ask: ${quote.get('ask')}")
    else:
        print("    [FAIL] No quote (may be outside market hours)")
    
    # Bulk quotes
    print("\n[3] Bulk Quotes (SPY, QQQ, AAPL)...")
    quotes = api.get_realtime_quotes_bulk(['SPY', 'QQQ', 'AAPL'])
    print(f"    [OK] Got {len(quotes)} quotes")
    
    # News
    print("\n[4] News (NVDA)...")
    news = api.get_news(tickers=['NVDA'], limit=5)
    if news:
        print(f"    [OK] Got {len(news)} articles")
        print(f"    Latest: {news[0].get('title')[:60]}...")
    else:
        print("    [FAIL] No news")
    
    # News sentiment
    print("\n[5] News Sentiment (TSLA)...")
    sentiment = api.get_news_sentiment("TSLA")
    print(f"    [OK] Sentiment: {sentiment.get('sentiment')} ({sentiment.get('score')})")
    
    # Fundamentals
    print("\n[6] Fundamentals Meta (AAPL)...")
    fundamentals = api.get_fundamentals_meta("AAPL")
    if fundamentals:
        print(f"    [OK] Got fundamentals data")
    else:
        print("    [FAIL] No fundamentals (may need paid tier)")
    
    # Crypto
    print("\n[7] Crypto Quote (BTC)...")
    crypto = api.get_crypto_quote("btc")
    if crypto and crypto.get('price'):
        print(f"    [OK] BTC: ${crypto.get('price'):,.2f}")
    else:
        print("    [FAIL] No crypto data")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
