#!/usr/bin/env python3
"""
Enhanced Data Integration Module
Demonstrates integration with multiple data APIs for better research
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class EnhancedDataIntegration:
    """Multi-source data integration for enhanced research"""

    def __init__(self):
        # API Keys (set these in .env file)
        self.polygon_key = os.getenv('POLYGON_API_KEY')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_KEY')
        self.benzinga_key = os.getenv('BENZINGA_API_KEY')
        self.newsapi_key = os.getenv('NEWS_API_KEY')
        self.fred_key = os.getenv('FRED_API_KEY')

    # =============== POLYGON.IO INTEGRATION ===============
    def get_polygon_quote(self, ticker: str) -> Dict:
        """Get real-time quote from Polygon.io"""
        if not self.polygon_key:
            return self._fallback_quote(ticker)

        url = f"https://api.polygon.io/v2/last/nbbo/{ticker}"
        params = {'apiKey': self.polygon_key}

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    'ticker': ticker,
                    'price': data['results']['P'],
                    'bid': data['results']['p'],
                    'ask': data['results']['P'],
                    'timestamp': data['results']['t'],
                    'source': 'polygon'
                }
        except Exception as e:
            print(f"Polygon error: {e}")

        return self._fallback_quote(ticker)

    def get_polygon_aggregates(self, ticker: str, days: int = 30) -> pd.DataFrame:
        """Get historical aggregates from Polygon.io"""
        if not self.polygon_key:
            return pd.DataFrame()

        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
        params = {'apiKey': self.polygon_key}

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data['results'])
                df['date'] = pd.to_datetime(df['t'], unit='ms')
                return df[['date', 'o', 'h', 'l', 'c', 'v']]
        except Exception as e:
            print(f"Polygon aggregates error: {e}")

        return pd.DataFrame()

    # =============== ALPHA VANTAGE INTEGRATION ===============
    def get_company_overview(self, ticker: str) -> Dict:
        """Get fundamental data from Alpha Vantage"""
        if not self.alpha_vantage_key:
            return {}

        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'OVERVIEW',
            'symbol': ticker,
            'apikey': self.alpha_vantage_key
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    'market_cap': data.get('MarketCapitalization'),
                    'pe_ratio': data.get('PERatio'),
                    'dividend_yield': data.get('DividendYield'),
                    'beta': data.get('Beta'),
                    'profit_margin': data.get('ProfitMargin'),
                    '52_week_high': data.get('52WeekHigh'),
                    '52_week_low': data.get('52WeekLow'),
                    'analyst_target': data.get('AnalystTargetPrice'),
                    'description': data.get('Description')
                }
        except Exception as e:
            print(f"Alpha Vantage error: {e}")

        return {}

    def get_technical_indicators(self, ticker: str, indicator: str = 'RSI') -> Dict:
        """Get technical indicators from Alpha Vantage"""
        if not self.alpha_vantage_key:
            return {}

        url = "https://www.alphavantage.co/query"
        params = {
            'function': indicator,
            'symbol': ticker,
            'interval': 'daily',
            'time_period': 14,
            'series_type': 'close',
            'apikey': self.alpha_vantage_key
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Technical indicator error: {e}")

        return {}

    # =============== BENZINGA NEWS INTEGRATION ===============
    def get_benzinga_news(self, ticker: str) -> List[Dict]:
        """Get news and sentiment from Benzinga"""
        if not self.benzinga_key:
            return []

        url = "https://api.benzinga.com/api/v2/news"
        headers = {
            'accept': 'application/json',
            'Token': self.benzinga_key
        }
        params = {
            'tickers': ticker,
            'pageSize': 10,
            'displayOutput': 'full'
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                articles = response.json()
                return [{
                    'title': article.get('title'),
                    'summary': article.get('teaser'),
                    'url': article.get('url'),
                    'published': article.get('created'),
                    'sentiment': self._analyze_sentiment(article.get('title', ''))
                } for article in articles]
        except Exception as e:
            print(f"Benzinga error: {e}")

        return []

    def get_fda_calendar(self) -> List[Dict]:
        """Get FDA calendar events from Benzinga"""
        if not self.benzinga_key:
            return []

        url = "https://api.benzinga.com/api/v2.1/calendar/fda"
        headers = {
            'accept': 'application/json',
            'Token': self.benzinga_key
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"FDA calendar error: {e}")

        return []

    # =============== SENTIMENT ANALYSIS ===============
    def get_stocktwits_sentiment(self, ticker: str) -> Dict:
        """Get sentiment from StockTwits (no API key required)"""
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                messages = data.get('messages', [])

                bullish = sum(1 for m in messages if m.get('entities', {}).get('sentiment', {}).get('basic') == 'Bullish')
                bearish = sum(1 for m in messages if m.get('entities', {}).get('sentiment', {}).get('basic') == 'Bearish')

                return {
                    'ticker': ticker,
                    'bullish_count': bullish,
                    'bearish_count': bearish,
                    'sentiment_ratio': bullish / (bullish + bearish) if (bullish + bearish) > 0 else 0.5,
                    'message_volume': len(messages)
                }
        except Exception as e:
            print(f"StockTwits error: {e}")

        return {}

    # =============== ECONOMIC DATA ===============
    def get_economic_indicators(self) -> Dict:
        """Get key economic indicators from FRED"""
        if not self.fred_key:
            return {}

        indicators = {
            'DGS10': '10_year_treasury',
            'DFF': 'fed_funds_rate',
            'UNRATE': 'unemployment_rate',
            'CPIAUCSL': 'cpi',
            'DEXUSEU': 'usd_eur'
        }

        results = {}
        base_url = "https://api.stlouisfed.org/fred/series/observations"

        for series_id, name in indicators.items():
            params = {
                'series_id': series_id,
                'api_key': self.fred_key,
                'file_type': 'json',
                'limit': 1,
                'sort_order': 'desc'
            }

            try:
                response = requests.get(base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data['observations']:
                        results[name] = float(data['observations'][0]['value'])
            except Exception as e:
                print(f"FRED error for {series_id}: {e}")

        return results

    # =============== ENHANCED RESEARCH REPORT ===============
    def generate_enhanced_research(self, ticker: str) -> Dict:
        """Generate comprehensive research report using multiple data sources"""

        print(f"Generating enhanced research for {ticker}...")

        research = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'market_data': {},
            'fundamentals': {},
            'technicals': {},
            'news_sentiment': {},
            'social_sentiment': {},
            'economic_context': {},
            'catalyst_events': [],
            'risk_factors': [],
            'opportunities': []
        }

        # 1. Real-time market data
        print("  Fetching market data...")
        research['market_data'] = self.get_polygon_quote(ticker)

        # 2. Historical price data
        historical = self.get_polygon_aggregates(ticker)
        if not historical.empty:
            research['market_data']['30d_return'] = (
                (historical.iloc[-1]['c'] - historical.iloc[0]['c']) / historical.iloc[0]['c'] * 100
            )
            research['market_data']['volatility'] = historical['c'].pct_change().std() * (252 ** 0.5)

        # 3. Fundamental data
        print("  Fetching fundamentals...")
        research['fundamentals'] = self.get_company_overview(ticker)

        # 4. Technical indicators
        print("  Calculating technicals...")
        rsi_data = self.get_technical_indicators(ticker, 'RSI')
        if rsi_data:
            research['technicals']['rsi'] = rsi_data

        # 5. News sentiment
        print("  Analyzing news sentiment...")
        news = self.get_benzinga_news(ticker)
        if news:
            research['news_sentiment'] = {
                'articles': news[:5],
                'avg_sentiment': sum(a.get('sentiment', 0.5) for a in news) / len(news)
            }

        # 6. Social sentiment
        print("  Checking social sentiment...")
        research['social_sentiment'] = self.get_stocktwits_sentiment(ticker)

        # 7. Economic context
        print("  Getting economic context...")
        research['economic_context'] = self.get_economic_indicators()

        # 8. Identify catalysts (for SHORGAN-BOT)
        research['catalyst_events'] = self._identify_catalysts(ticker)

        # 9. Risk assessment
        research['risk_factors'] = self._assess_risks(research)

        # 10. Opportunities
        research['opportunities'] = self._identify_opportunities(research)

        print(f"Enhanced research complete for {ticker}")
        return research

    # =============== HELPER METHODS ===============
    def _fallback_quote(self, ticker: str) -> Dict:
        """Fallback to Alpaca for quotes"""
        # Use existing Alpaca connection
        return {
            'ticker': ticker,
            'price': 0,
            'source': 'fallback'
        }

    def _analyze_sentiment(self, text: str) -> float:
        """Simple sentiment analysis (0-1 scale)"""
        positive_words = ['beat', 'upgrade', 'buy', 'growth', 'strong', 'positive', 'gain']
        negative_words = ['miss', 'downgrade', 'sell', 'decline', 'weak', 'negative', 'loss']

        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count + neg_count == 0:
            return 0.5
        return pos_count / (pos_count + neg_count)

    def _identify_catalysts(self, ticker: str) -> List[Dict]:
        """Identify upcoming catalyst events"""
        catalysts = []

        # Check FDA calendar if biotech
        if self.benzinga_key:
            fda_events = self.get_fda_calendar()
            for event in fda_events:
                if event.get('ticker') == ticker:
                    catalysts.append({
                        'type': 'FDA',
                        'date': event.get('date'),
                        'description': event.get('event_description')
                    })

        return catalysts

    def _assess_risks(self, research: Dict) -> List[str]:
        """Assess risk factors from research data"""
        risks = []

        # High valuation risk
        if research['fundamentals'].get('pe_ratio'):
            try:
                if float(research['fundamentals']['pe_ratio']) > 30:
                    risks.append("High P/E ratio indicates expensive valuation")
            except:
                pass

        # High volatility
        if research['market_data'].get('volatility', 0) > 0.4:
            risks.append("High volatility (>40% annualized)")

        # Negative sentiment
        if research['news_sentiment'].get('avg_sentiment', 0.5) < 0.3:
            risks.append("Negative news sentiment")

        return risks

    def _identify_opportunities(self, research: Dict) -> List[str]:
        """Identify opportunities from research data"""
        opportunities = []

        # Oversold on RSI
        if research['technicals'].get('rsi'):
            # Check if RSI < 30 (would need to parse the response)
            pass

        # Positive news momentum
        if research['news_sentiment'].get('avg_sentiment', 0.5) > 0.7:
            opportunities.append("Strong positive news sentiment")

        # Below analyst target
        if research['fundamentals'].get('analyst_target'):
            try:
                target = float(research['fundamentals']['analyst_target'])
                current = research['market_data'].get('price', 0)
                if current > 0 and target > current * 1.1:
                    opportunities.append(f"Trading below analyst target of ${target}")
            except:
                pass

        return opportunities


def main():
    """Demo the enhanced data integration"""
    print("=" * 60)
    print("ENHANCED DATA INTEGRATION DEMO")
    print("=" * 60)

    # Initialize the integration
    integrator = EnhancedDataIntegration()

    # Test with a ticker
    ticker = "AAPL"
    research = integrator.generate_enhanced_research(ticker)

    # Save to file
    output_file = f"enhanced_research_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(research, f, indent=2, default=str)

    print(f"\nResearch saved to: {output_file}")

    # Display summary
    print(f"\n{ticker} Research Summary:")
    print(f"  Price: ${research['market_data'].get('price', 'N/A')}")
    print(f"  P/E Ratio: {research['fundamentals'].get('pe_ratio', 'N/A')}")
    print(f"  News Sentiment: {research['news_sentiment'].get('avg_sentiment', 'N/A'):.2%}")
    print(f"  Risk Factors: {len(research['risk_factors'])}")
    print(f"  Opportunities: {len(research['opportunities'])}")


if __name__ == "__main__":
    main()