#!/usr/bin/env python3
"""
Financial Datasets API Integration
Premium data source with MCP support for comprehensive market analysis
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
from dotenv import load_dotenv
import asyncio
import aiohttp

load_dotenv()

class FinancialDatasetsAPI:
    """
    Integration with Financial Datasets API
    Provides high-quality financial data for both DEE-BOT and SHORGAN-BOT strategies
    """

    def __init__(self):
        self.api_key = os.getenv('FINANCIAL_DATASETS_API_KEY')
        if not self.api_key:
            print("Warning: FINANCIAL_DATASETS_API_KEY not set in .env")

        self.base_url = "https://api.financialdatasets.ai"
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

    # =============== PRICE DATA ===============
    def get_historical_prices(self, ticker: str, interval: str = 'day',
                            start_date: str = None, end_date: str = None,
                            limit: int = 1000) -> pd.DataFrame:
        """
        Get historical price data

        Args:
            ticker: Stock symbol
            interval: 'minute', 'day', 'week', 'month', 'year'
            start_date: YYYY-MM-DD format
            end_date: YYYY-MM-DD format
            limit: Max records (default 1000, max 5000)
        """
        endpoint = f"{self.base_url}/v1/prices/historical"

        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        params = {
            'ticker': ticker.upper(),
            'interval': interval,
            'start': start_date,
            'end': end_date,
            'limit': limit
        }

        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data['prices'])
                df['datetime'] = pd.to_datetime(df['time'])
                df = df.set_index('datetime')
                return df[['open', 'high', 'low', 'close', 'volume']]
            else:
                print(f"Error fetching prices: {response.status_code}")
                return pd.DataFrame()
        except Exception as e:
            print(f"Error: {e}")
            return pd.DataFrame()

    def get_snapshot_price(self, ticker: str) -> Dict:
        """Get current/snapshot price data"""
        endpoint = f"{self.base_url}/v1/prices/snapshot"
        params = {'ticker': ticker.upper()}

        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    'ticker': ticker,
                    'price': data.get('price'),
                    'change': data.get('change'),
                    'change_percent': data.get('change_percent'),
                    'volume': data.get('volume'),
                    'market_cap': data.get('market_cap'),
                    'timestamp': data.get('timestamp')
                }
        except Exception as e:
            print(f"Snapshot error: {e}")
        return {}

    # =============== FUNDAMENTAL DATA ===============
    def get_financial_statements(self, ticker: str, statement_type: str = 'income',
                                period: str = 'quarterly', limit: int = 4) -> List[Dict]:
        """
        Get financial statements

        Args:
            ticker: Stock symbol
            statement_type: 'income', 'balance', 'cashflow'
            period: 'quarterly' or 'annual'
            limit: Number of periods
        """
        endpoint = f"{self.base_url}/v1/financials/statements"
        params = {
            'ticker': ticker.upper(),
            'type': statement_type,
            'period': period,
            'limit': limit
        }

        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json().get('statements', [])
        except Exception as e:
            print(f"Financial statements error: {e}")
        return []

    def get_financial_metrics(self, ticker: str) -> Dict:
        """Get key financial metrics and ratios"""
        endpoint = f"{self.base_url}/v1/financials/metrics"
        params = {'ticker': ticker.upper()}

        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    'pe_ratio': data.get('pe_ratio'),
                    'peg_ratio': data.get('peg_ratio'),
                    'price_to_book': data.get('pb_ratio'),
                    'price_to_sales': data.get('ps_ratio'),
                    'ev_to_ebitda': data.get('ev_ebitda'),
                    'roi': data.get('return_on_investment'),
                    'roe': data.get('return_on_equity'),
                    'roa': data.get('return_on_assets'),
                    'debt_to_equity': data.get('debt_equity'),
                    'current_ratio': data.get('current_ratio'),
                    'quick_ratio': data.get('quick_ratio'),
                    'gross_margin': data.get('gross_margin'),
                    'operating_margin': data.get('operating_margin'),
                    'net_margin': data.get('net_margin'),
                    'dividend_yield': data.get('dividend_yield'),
                    'beta': data.get('beta')
                }
        except Exception as e:
            print(f"Metrics error: {e}")
        return {}

    # =============== EARNINGS & ESTIMATES ===============
    def get_earnings(self, ticker: str, limit: int = 8) -> List[Dict]:
        """Get earnings history and surprises"""
        endpoint = f"{self.base_url}/v1/earnings/history"
        params = {
            'ticker': ticker.upper(),
            'limit': limit
        }

        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            if response.status_code == 200:
                earnings = response.json().get('earnings', [])
                return [{
                    'date': e.get('date'),
                    'reported_eps': e.get('reported_eps'),
                    'estimated_eps': e.get('estimated_eps'),
                    'surprise': e.get('surprise'),
                    'surprise_percent': e.get('surprise_percent')
                } for e in earnings]
        except Exception as e:
            print(f"Earnings error: {e}")
        return []

    def get_analyst_estimates(self, ticker: str) -> Dict:
        """Get analyst consensus estimates"""
        endpoint = f"{self.base_url}/v1/estimates/consensus"
        params = {'ticker': ticker.upper()}

        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    'current_quarter_estimate': data.get('current_quarter_eps'),
                    'next_quarter_estimate': data.get('next_quarter_eps'),
                    'current_year_estimate': data.get('current_year_eps'),
                    'next_year_estimate': data.get('next_year_eps'),
                    'revenue_estimate': data.get('revenue_estimate'),
                    'price_target': data.get('price_target'),
                    'strong_buy': data.get('strong_buy'),
                    'buy': data.get('buy'),
                    'hold': data.get('hold'),
                    'sell': data.get('sell'),
                    'strong_sell': data.get('strong_sell')
                }
        except Exception as e:
            print(f"Estimates error: {e}")
        return {}

    # =============== NEWS & SENTIMENT ===============
    def get_news(self, ticker: str = None, limit: int = 10) -> List[Dict]:
        """Get latest news articles"""
        endpoint = f"{self.base_url}/v1/news/articles"
        params = {'limit': limit}
        if ticker:
            params['ticker'] = ticker.upper()

        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            if response.status_code == 200:
                articles = response.json().get('articles', [])
                return [{
                    'title': a.get('title'),
                    'summary': a.get('summary'),
                    'url': a.get('url'),
                    'source': a.get('source'),
                    'published': a.get('published_at'),
                    'tickers': a.get('tickers', []),
                    'sentiment': a.get('sentiment_score')
                } for a in articles]
        except Exception as e:
            print(f"News error: {e}")
        return []

    # =============== INSIDER & INSTITUTIONAL ===============
    def get_insider_trades(self, ticker: str, limit: int = 20) -> List[Dict]:
        """Get insider trading activity"""
        endpoint = f"{self.base_url}/v1/insider/trades"
        params = {
            'ticker': ticker.upper(),
            'limit': limit
        }

        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            if response.status_code == 200:
                trades = response.json().get('trades', [])
                return [{
                    'filing_date': t.get('filing_date'),
                    'trade_date': t.get('trade_date'),
                    'insider_name': t.get('insider_name'),
                    'title': t.get('title'),
                    'transaction': t.get('transaction_type'),
                    'shares': t.get('shares'),
                    'price': t.get('price'),
                    'value': t.get('value'),
                    'shares_owned': t.get('shares_owned_after')
                } for t in trades]
        except Exception as e:
            print(f"Insider trades error: {e}")
        return []

    def get_institutional_ownership(self, ticker: str) -> Dict:
        """Get institutional ownership data"""
        endpoint = f"{self.base_url}/v1/institutional/ownership"
        params = {'ticker': ticker.upper()}

        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    'institutional_percent': data.get('institutional_ownership_percent'),
                    'number_of_institutions': data.get('number_of_institutions'),
                    'shares_held': data.get('total_shares_held'),
                    'value_held': data.get('total_value_held'),
                    'top_holders': data.get('top_holders', [])
                }
        except Exception as e:
            print(f"Institutional ownership error: {e}")
        return {}

    # =============== SEC FILINGS ===============
    def get_sec_filings(self, ticker: str, filing_type: str = None, limit: int = 10) -> List[Dict]:
        """Get recent SEC filings"""
        endpoint = f"{self.base_url}/v1/sec/filings"
        params = {
            'ticker': ticker.upper(),
            'limit': limit
        }
        if filing_type:
            params['type'] = filing_type  # e.g., '10-K', '10-Q', '8-K'

        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            if response.status_code == 200:
                filings = response.json().get('filings', [])
                return [{
                    'filing_date': f.get('filing_date'),
                    'type': f.get('form_type'),
                    'title': f.get('title'),
                    'url': f.get('url'),
                    'size': f.get('size')
                } for f in filings]
        except Exception as e:
            print(f"SEC filings error: {e}")
        return []

    # =============== COMPREHENSIVE RESEARCH ===============
    async def get_comprehensive_research_async(self, ticker: str) -> Dict:
        """
        Async method to fetch all data in parallel for faster research
        """
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_async(session, 'prices/snapshot', {'ticker': ticker}),
                self._fetch_async(session, 'financials/metrics', {'ticker': ticker}),
                self._fetch_async(session, 'earnings/history', {'ticker': ticker, 'limit': 4}),
                self._fetch_async(session, 'estimates/consensus', {'ticker': ticker}),
                self._fetch_async(session, 'news/articles', {'ticker': ticker, 'limit': 5}),
                self._fetch_async(session, 'insider/trades', {'ticker': ticker, 'limit': 5}),
                self._fetch_async(session, 'institutional/ownership', {'ticker': ticker})
            ]

            results = await asyncio.gather(*tasks)

            return {
                'ticker': ticker,
                'timestamp': datetime.now().isoformat(),
                'snapshot': results[0],
                'metrics': results[1],
                'earnings': results[2],
                'estimates': results[3],
                'news': results[4],
                'insider_trades': results[5],
                'institutional': results[6]
            }

    async def _fetch_async(self, session: aiohttp.ClientSession, endpoint: str, params: Dict) -> Dict:
        """Helper for async fetching"""
        url = f"{self.base_url}/v1/{endpoint}"
        headers = {'X-API-KEY': self.api_key}

        try:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"Async fetch error for {endpoint}: {e}")
        return {}

    def generate_comprehensive_research(self, ticker: str) -> Dict:
        """
        Generate comprehensive research report using all available data
        Perfect for both DEE-BOT and SHORGAN-BOT strategies
        """
        print(f"Generating comprehensive research for {ticker} using Financial Datasets...")

        research = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'data_source': 'Financial Datasets API',
            'price_analysis': {},
            'fundamental_analysis': {},
            'earnings_analysis': {},
            'analyst_sentiment': {},
            'news_sentiment': {},
            'insider_activity': {},
            'institutional_activity': {},
            'technical_signals': {},
            'dee_bot_signals': {},      # For defensive strategy
            'shorgan_bot_signals': {},   # For catalyst strategy
            'risk_assessment': [],
            'opportunities': []
        }

        # 1. Price Analysis
        print("  Fetching price data...")
        snapshot = self.get_snapshot_price(ticker)
        research['price_analysis'] = snapshot

        historical = self.get_historical_prices(ticker, interval='day', limit=252)
        if not historical.empty:
            research['price_analysis']['52_week_high'] = historical['high'].max()
            research['price_analysis']['52_week_low'] = historical['low'].min()
            research['price_analysis']['ytd_return'] = (
                (historical['close'].iloc[-1] - historical['close'].iloc[0]) /
                historical['close'].iloc[0] * 100
            )
            research['price_analysis']['volatility'] = historical['close'].pct_change().std() * (252 ** 0.5)

        # 2. Fundamental Analysis
        print("  Analyzing fundamentals...")
        metrics = self.get_financial_metrics(ticker)
        research['fundamental_analysis'] = metrics

        # 3. Earnings Analysis
        print("  Reviewing earnings...")
        earnings = self.get_earnings(ticker)
        if earnings:
            research['earnings_analysis'] = {
                'recent_earnings': earnings[:4],
                'avg_surprise': sum(e.get('surprise_percent', 0) for e in earnings[:4]) / 4,
                'beat_rate': sum(1 for e in earnings[:4] if e.get('surprise_percent', 0) > 0) / 4
            }

        # 4. Analyst Estimates
        print("  Getting analyst consensus...")
        estimates = self.get_analyst_estimates(ticker)
        research['analyst_sentiment'] = estimates

        # 5. News Sentiment
        print("  Analyzing news...")
        news = self.get_news(ticker, limit=10)
        if news:
            research['news_sentiment'] = {
                'recent_articles': news[:5],
                'article_count': len(news),
                'avg_sentiment': sum(a.get('sentiment', 0.5) for a in news) / len(news) if news else 0.5
            }

        # 6. Insider Trading
        print("  Checking insider activity...")
        insider_trades = self.get_insider_trades(ticker)
        if insider_trades:
            recent_buys = sum(1 for t in insider_trades[:10]
                            if 'buy' in t.get('transaction', '').lower())
            recent_sells = sum(1 for t in insider_trades[:10]
                             if 'sell' in t.get('transaction', '').lower())

            research['insider_activity'] = {
                'recent_trades': insider_trades[:5],
                'buy_sell_ratio': recent_buys / (recent_sells + 1),
                'net_sentiment': 'bullish' if recent_buys > recent_sells else 'bearish'
            }

        # 7. Institutional Ownership
        print("  Analyzing institutional holdings...")
        institutional = self.get_institutional_ownership(ticker)
        research['institutional_activity'] = institutional

        # 8. DEE-BOT Signals (Defensive Strategy)
        research['dee_bot_signals'] = self._calculate_dee_bot_signals(research)

        # 9. SHORGAN-BOT Signals (Catalyst Strategy)
        research['shorgan_bot_signals'] = self._calculate_shorgan_bot_signals(research)

        # 10. Risk Assessment
        research['risk_assessment'] = self._assess_risks(research)

        # 11. Opportunities
        research['opportunities'] = self._identify_opportunities(research)

        print(f"Research complete for {ticker}")
        return research

    def _calculate_dee_bot_signals(self, research: Dict) -> Dict:
        """Calculate signals for DEE-BOT defensive strategy"""
        signals = {
            'quality_score': 0,
            'dividend_safety': 0,
            'valuation_score': 0,
            'stability_score': 0,
            'recommendation': 'HOLD'
        }

        metrics = research.get('fundamental_analysis', {})

        # Quality metrics
        if metrics.get('roe', 0) > 15:
            signals['quality_score'] += 25
        if metrics.get('current_ratio', 0) > 1.5:
            signals['quality_score'] += 25
        if metrics.get('debt_to_equity', 100) < 50:
            signals['quality_score'] += 25
        if metrics.get('gross_margin', 0) > 30:
            signals['quality_score'] += 25

        # Dividend safety
        if metrics.get('dividend_yield', 0) > 2 and metrics.get('dividend_yield', 0) < 6:
            signals['dividend_safety'] = 80

        # Valuation
        pe = metrics.get('pe_ratio', 999)
        if 10 < pe < 25:
            signals['valuation_score'] = 75
        elif pe < 10:
            signals['valuation_score'] = 90

        # Stability (low volatility preferred)
        volatility = research.get('price_analysis', {}).get('volatility', 1)
        if volatility < 0.2:
            signals['stability_score'] = 90
        elif volatility < 0.3:
            signals['stability_score'] = 70
        elif volatility < 0.4:
            signals['stability_score'] = 50

        # Overall recommendation
        total_score = (signals['quality_score'] + signals['dividend_safety'] +
                      signals['valuation_score'] + signals['stability_score']) / 4

        if total_score > 70:
            signals['recommendation'] = 'BUY'
        elif total_score > 50:
            signals['recommendation'] = 'HOLD'
        else:
            signals['recommendation'] = 'AVOID'

        return signals

    def _calculate_shorgan_bot_signals(self, research: Dict) -> Dict:
        """Calculate signals for SHORGAN-BOT catalyst strategy"""
        signals = {
            'catalyst_score': 0,
            'momentum_score': 0,
            'sentiment_score': 0,
            'insider_score': 0,
            'recommendation': 'WAIT'
        }

        # Catalyst detection (earnings surprises)
        earnings = research.get('earnings_analysis', {})
        if earnings.get('avg_surprise', 0) > 5:
            signals['catalyst_score'] = 80
        elif earnings.get('beat_rate', 0) >= 0.75:
            signals['catalyst_score'] = 60

        # Price momentum
        price_data = research.get('price_analysis', {})
        if price_data.get('change_percent', 0) > 5:
            signals['momentum_score'] = 70

        # News sentiment
        news = research.get('news_sentiment', {})
        if news.get('avg_sentiment', 0.5) > 0.7:
            signals['sentiment_score'] = 80
        elif news.get('avg_sentiment', 0.5) > 0.6:
            signals['sentiment_score'] = 60

        # Insider activity
        insider = research.get('insider_activity', {})
        if insider.get('buy_sell_ratio', 0) > 2:
            signals['insider_score'] = 90
        elif insider.get('buy_sell_ratio', 0) > 1:
            signals['insider_score'] = 60

        # Overall recommendation
        total_score = (signals['catalyst_score'] + signals['momentum_score'] +
                      signals['sentiment_score'] + signals['insider_score']) / 4

        if total_score > 70:
            signals['recommendation'] = 'BUY'
        elif total_score > 50:
            signals['recommendation'] = 'WATCH'
        else:
            signals['recommendation'] = 'WAIT'

        return signals

    def _assess_risks(self, research: Dict) -> List[str]:
        """Identify risk factors"""
        risks = []

        metrics = research.get('fundamental_analysis', {})
        if metrics.get('debt_to_equity', 0) > 100:
            risks.append("High debt levels (D/E > 100)")

        if metrics.get('pe_ratio', 0) > 35:
            risks.append("Expensive valuation (P/E > 35)")

        volatility = research.get('price_analysis', {}).get('volatility', 0)
        if volatility > 0.5:
            risks.append(f"High volatility ({volatility:.1%} annualized)")

        insider = research.get('insider_activity', {})
        if insider.get('net_sentiment') == 'bearish':
            risks.append("Net insider selling activity")

        return risks

    def _identify_opportunities(self, research: Dict) -> List[str]:
        """Identify opportunities"""
        opportunities = []

        # Earnings beats
        earnings = research.get('earnings_analysis', {})
        if earnings.get('beat_rate', 0) >= 0.75:
            opportunities.append(f"Strong earnings beat rate ({earnings['beat_rate']:.0%})")

        # Undervalued
        metrics = research.get('fundamental_analysis', {})
        if metrics.get('pe_ratio', 999) < 15 and metrics.get('peg_ratio', 999) < 1:
            opportunities.append("Potentially undervalued (low P/E and PEG)")

        # Insider buying
        insider = research.get('insider_activity', {})
        if insider.get('buy_sell_ratio', 0) > 2:
            opportunities.append("Strong insider buying activity")

        # Analyst upgrades
        estimates = research.get('analyst_sentiment', {})
        if estimates.get('strong_buy', 0) + estimates.get('buy', 0) > estimates.get('sell', 0) + estimates.get('strong_sell', 0):
            opportunities.append("Positive analyst sentiment")

        return opportunities


def main():
    """Demo the Financial Datasets integration"""
    print("=" * 60)
    print("FINANCIAL DATASETS API INTEGRATION")
    print("=" * 60)

    # Initialize
    fd = FinancialDatasetsAPI()

    # Test with a ticker
    ticker = "AAPL"

    # Generate comprehensive research
    research = fd.generate_comprehensive_research(ticker)

    # Save to file
    output_file = f"fd_research_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(research, f, indent=2, default=str)

    print(f"\nResearch saved to: {output_file}")

    # Display summary
    print(f"\n{ticker} Research Summary:")
    print(f"  Price: ${research['price_analysis'].get('price', 'N/A')}")
    print(f"  Change: {research['price_analysis'].get('change_percent', 'N/A'):.2f}%")
    print(f"  P/E Ratio: {research['fundamental_analysis'].get('pe_ratio', 'N/A')}")
    print(f"  DEE-BOT Signal: {research['dee_bot_signals']['recommendation']}")
    print(f"  SHORGAN-BOT Signal: {research['shorgan_bot_signals']['recommendation']}")
    print(f"  Risks: {len(research['risk_assessment'])}")
    print(f"  Opportunities: {len(research['opportunities'])}")

    # Run async example
    print("\n" + "=" * 60)
    print("Testing async data fetching...")

    async def run_async():
        result = await fd.get_comprehensive_research_async(ticker)
        print(f"Fetched {len(result)} data categories asynchronously")
        return result

    # asyncio.run(run_async())


if __name__ == "__main__":
    main()