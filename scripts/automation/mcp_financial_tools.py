#!/usr/bin/env python3
"""
MCP Financial Data Tools for Claude Research Generation
========================================================
Provides real-time stock data access via Anthropic's tool calling (MCP-like interface)

These tools allow Claude to fetch accurate, real-time financial data during research generation,
eliminating stale price issues.

Author: AI Trading Bot System
Date: November 17, 2025
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import our existing Financial Datasets integration
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from financial_datasets_integration import FinancialDatasetsAPI

# Also import Alpaca for real-time quotes
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import (
    StockLatestQuoteRequest,
    StockBarsRequest,
    StockLatestTradeRequest
)
from alpaca.data.timeframe import TimeFrame

load_dotenv()


class FinancialDataToolsProvider:
    """
    Provides financial data tools for Claude via MCP/Tool Calling
    Combines Alpaca (real-time quotes) and Financial Datasets (fundamentals)
    """

    def __init__(self):
        """Initialize data providers"""
        self.fd_api = FinancialDatasetsAPI()

        # Alpaca for real-time market data (fastest, most reliable)
        self.alpaca_data = StockHistoricalDataClient(
            api_key=os.getenv("ALPACA_API_KEY_DEE"),
            secret_key=os.getenv("ALPACA_SECRET_KEY_DEE")
        )

        # Cache to avoid duplicate API calls
        self.price_cache = {}
        self.metrics_cache = {}
        self.cache_timestamp = None

    def get_tool_definitions(self) -> List[Dict]:
        """
        Return tool definitions for Claude API
        These define what tools Claude can call during research generation
        """
        return [
            {
                "name": "get_current_price",
                "description": "Get real-time stock price, bid/ask, volume, and daily change. Use this for ANY stock you want to analyze or recommend. Returns current market data as of the last trade.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Stock ticker symbol (e.g., AAPL, TSLA, PLUG)"
                        }
                    },
                    "required": ["ticker"]
                }
            },
            {
                "name": "get_price_history",
                "description": "Get historical price data for technical analysis. Returns OHLCV data, 52-week high/low, moving averages, and volatility metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days of history (default 30, max 365)",
                            "default": 30
                        }
                    },
                    "required": ["ticker"]
                }
            },
            {
                "name": "get_fundamental_metrics",
                "description": "Get key fundamental metrics: revenue, earnings, profit margins, ROE, ROA, debt ratios, growth rates. Essential for fundamental analysis.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        }
                    },
                    "required": ["ticker"]
                }
            },
            {
                "name": "get_valuation_multiples",
                "description": "Get comprehensive valuation multiples: P/E ratio, P/B ratio, P/S ratio, EV/EBITDA, Dividend Yield, Market Cap, Enterprise Value. Critical for determining if a stock is overvalued or undervalued.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        }
                    },
                    "required": ["ticker"]
                }
            },
            {
                "name": "get_multiple_prices",
                "description": "Get real-time prices for multiple stocks at once. More efficient than calling get_current_price multiple times. Use when comparing several stocks.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "tickers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of ticker symbols (e.g., ['AAPL', 'MSFT', 'GOOGL'])"
                        }
                    },
                    "required": ["tickers"]
                }
            },
            {
                "name": "get_earnings_history",
                "description": "Get earnings history showing EPS beats/misses, revenue growth, and earnings trends. Useful for catalyst analysis.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        },
                        "quarters": {
                            "type": "integer",
                            "description": "Number of quarters to retrieve (default 4, max 8)",
                            "default": 4
                        }
                    },
                    "required": ["ticker"]
                }
            },
            {
                "name": "get_news_sentiment",
                "description": "Get recent news articles and sentiment analysis for a stock. Helps identify catalysts and market perception.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of articles to retrieve (default 5, max 20)",
                            "default": 5
                        }
                    },
                    "required": ["ticker"]
                }
            }
        ]

    def execute_tool(self, tool_name: str, tool_input: Dict) -> Dict:
        """
        Execute a tool call from Claude

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters from Claude

        Returns:
            Tool result as a dictionary
        """
        try:
            # Route to appropriate handler
            if tool_name == "get_current_price":
                return self._get_current_price(tool_input["ticker"])
            elif tool_name == "get_price_history":
                days = tool_input.get("days", 30)
                return self._get_price_history(tool_input["ticker"], days)
            elif tool_name == "get_fundamental_metrics":
                return self._get_fundamental_metrics(tool_input["ticker"])
            elif tool_name == "get_valuation_multiples":
                return self._get_valuation_multiples(tool_input["ticker"])
            elif tool_name == "get_multiple_prices":
                return self._get_multiple_prices(tool_input["tickers"])
            elif tool_name == "get_earnings_history":
                quarters = tool_input.get("quarters", 4)
                return self._get_earnings_history(tool_input["ticker"], quarters)
            elif tool_name == "get_news_sentiment":
                limit = tool_input.get("limit", 5)
                return self._get_news_sentiment(tool_input["ticker"], limit)
            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

    # ==================== TOOL IMPLEMENTATIONS ====================

    def _get_current_price(self, ticker: str) -> Dict:
        """Get real-time price from Alpaca"""
        ticker = ticker.upper()

        # Check cache (valid for 60 seconds)
        cache_key = f"price_{ticker}"
        if cache_key in self.price_cache:
            cached_time, cached_data = self.price_cache[cache_key]
            if (datetime.now() - cached_time).seconds < 60:
                return cached_data

        try:
            # Get latest quote
            quote_req = StockLatestQuoteRequest(symbol_or_symbols=[ticker])
            quotes = self.alpaca_data.get_stock_latest_quote(quote_req)

            # Get latest trade
            trade_req = StockLatestTradeRequest(symbol_or_symbols=[ticker])
            trades = self.alpaca_data.get_stock_latest_trade(trade_req)

            if ticker in quotes and ticker in trades:
                q = quotes[ticker]
                t = trades[ticker]

                # Get daily bars for change calculation
                end_date = datetime.now()
                start_date = end_date - timedelta(days=2)
                bars_req = StockBarsRequest(
                    symbol_or_symbols=[ticker],
                    timeframe=TimeFrame.Day,
                    start=start_date,
                    end=end_date
                )
                bars = self.alpaca_data.get_stock_bars(bars_req)

                # Calculate daily change
                prev_close = None
                current_price = float(t.price)

                if ticker in bars and len(bars[ticker]) > 1:
                    prev_close = float(bars[ticker][-2].close)
                elif ticker in bars and len(bars[ticker]) == 1:
                    prev_close = float(bars[ticker][0].open)

                change = (current_price - prev_close) if prev_close else 0
                change_pct = (change / prev_close * 100) if prev_close else 0

                result = {
                    "ticker": ticker,
                    "price": round(current_price, 2),
                    "bid": round(float(q.bid_price), 2),
                    "ask": round(float(q.ask_price), 2),
                    "bid_size": int(q.bid_size),
                    "ask_size": int(q.ask_size),
                    "last_trade_time": str(t.timestamp),
                    "volume": int(t.size),
                    "spread": round(float(q.ask_price - q.bid_price), 3),
                    "daily_change": round(change, 2),
                    "daily_change_pct": round(change_pct, 2),
                    "previous_close": round(prev_close, 2) if prev_close else None,
                    "data_source": "Alpaca (real-time)",
                    "timestamp": datetime.now().isoformat()
                }

                # Cache result
                self.price_cache[cache_key] = (datetime.now(), result)
                return result

            return {"error": f"No data available for {ticker}"}

        except Exception as e:
            return {"error": f"Failed to fetch price for {ticker}: {str(e)}"}

    def _get_multiple_prices(self, tickers: List[str]) -> Dict:
        """Get prices for multiple tickers efficiently"""
        tickers = [t.upper() for t in tickers]
        results = {}

        try:
            # Batch request for quotes
            quote_req = StockLatestQuoteRequest(symbol_or_symbols=tickers)
            quotes = self.alpaca_data.get_stock_latest_quote(quote_req)

            # Batch request for trades
            trade_req = StockLatestTradeRequest(symbol_or_symbols=tickers)
            trades = self.alpaca_data.get_stock_latest_trade(trade_req)

            for ticker in tickers:
                if ticker in quotes and ticker in trades:
                    q = quotes[ticker]
                    t = trades[ticker]

                    results[ticker] = {
                        "price": round(float(t.price), 2),
                        "bid": round(float(q.bid_price), 2),
                        "ask": round(float(q.ask_price), 2),
                        "spread": round(float(q.ask_price - q.bid_price), 3),
                        "timestamp": str(t.timestamp)
                    }
                else:
                    results[ticker] = {"error": "No data available"}

            return {
                "prices": results,
                "count": len(results),
                "data_source": "Alpaca (real-time)",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"Batch price fetch failed: {str(e)}"}

    def _get_price_history(self, ticker: str, days: int = 30) -> Dict:
        """Get historical price data for technical analysis"""
        ticker = ticker.upper()
        days = min(days, 365)  # Cap at 1 year

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            bars_req = StockBarsRequest(
                symbol_or_symbols=[ticker],
                timeframe=TimeFrame.Day,
                start=start_date,
                end=end_date
            )
            bars = self.alpaca_data.get_stock_bars(bars_req)

            if ticker not in bars or len(bars[ticker]) == 0:
                return {"error": f"No historical data for {ticker}"}

            ticker_bars = bars[ticker]
            closes = [float(b.close) for b in ticker_bars]
            highs = [float(b.high) for b in ticker_bars]
            lows = [float(b.low) for b in ticker_bars]
            volumes = [int(b.volume) for b in ticker_bars]

            # Calculate metrics
            current_price = closes[-1]
            period_high = max(highs)
            period_low = min(lows)
            avg_volume = sum(volumes) / len(volumes)

            # Simple moving averages
            sma_20 = sum(closes[-20:]) / min(20, len(closes)) if len(closes) >= 20 else None
            sma_50 = sum(closes[-50:]) / min(50, len(closes)) if len(closes) >= 50 else None

            # Volatility (standard deviation of returns)
            returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
            volatility = (sum([(r - sum(returns)/len(returns))**2 for r in returns]) / len(returns)) ** 0.5
            annualized_volatility = volatility * (252 ** 0.5)

            return {
                "ticker": ticker,
                "period_days": len(ticker_bars),
                "current_price": round(current_price, 2),
                "period_high": round(period_high, 2),
                "period_low": round(period_low, 2),
                "period_return_pct": round((current_price - closes[0]) / closes[0] * 100, 2),
                "avg_daily_volume": int(avg_volume),
                "sma_20": round(sma_20, 2) if sma_20 else None,
                "sma_50": round(sma_50, 2) if sma_50 else None,
                "volatility_annualized": round(annualized_volatility, 3),
                "data_source": "Alpaca",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"Historical data fetch failed for {ticker}: {str(e)}"}

    def _get_fundamental_metrics(self, ticker: str) -> Dict:
        """Get fundamental metrics from Financial Datasets"""
        ticker = ticker.upper()

        # Check cache (valid for 1 hour)
        cache_key = f"metrics_{ticker}"
        if cache_key in self.metrics_cache:
            cached_time, cached_data = self.metrics_cache[cache_key]
            if (datetime.now() - cached_time).seconds < 3600:
                return cached_data

        try:
            metrics = self.fd_api.get_financial_metrics(ticker)

            if not metrics:
                return {"error": f"No fundamental data available for {ticker}"}

            result = {
                "ticker": ticker,
                "revenue": metrics.get("revenue"),
                "net_income": metrics.get("net_income"),
                "eps": metrics.get("eps"),
                "ebitda": metrics.get("ebitda"),
                "gross_margin_pct": round(metrics.get("gross_margin", 0), 2),
                "operating_margin_pct": round(metrics.get("operating_margin", 0), 2),
                "net_margin_pct": round(metrics.get("net_margin", 0), 2),
                "roe_pct": round(metrics.get("roe", 0), 2),
                "roa_pct": round(metrics.get("roa", 0), 2),
                "debt_to_equity_pct": round(metrics.get("debt_to_equity", 0), 2),
                "current_ratio": round(metrics.get("current_ratio", 0), 2),
                "total_assets": metrics.get("total_assets"),
                "total_equity": metrics.get("total_equity"),
                "total_debt": metrics.get("total_debt"),
                "cash": metrics.get("cash"),
                "shares_outstanding": metrics.get("shares_outstanding"),
                "book_value_per_share": metrics.get("book_value_per_share"),
                "data_source": "Financial Datasets",
                "timestamp": datetime.now().isoformat()
            }

            # Cache result
            self.metrics_cache[cache_key] = (datetime.now(), result)
            return result

        except Exception as e:
            return {"error": f"Fundamentals fetch failed for {ticker}: {str(e)}"}

    def _get_valuation_multiples(self, ticker: str) -> Dict:
        """Get valuation multiples (P/E, P/B, P/S, EV/EBITDA, etc.)"""
        ticker = ticker.upper()

        # Check cache (valid for 1 hour)
        cache_key = f"valuation_{ticker}"
        if cache_key in self.metrics_cache:
            cached_time, cached_data = self.metrics_cache[cache_key]
            if (datetime.now() - cached_time).seconds < 3600:
                return cached_data

        try:
            # Get current price from Alpaca first
            price_data = self._get_current_price(ticker)
            current_price = price_data.get("price") if price_data and "price" in price_data else None

            if not current_price:
                return {"error": f"Could not fetch current price for {ticker}"}

            # Get valuation multiples from Financial Datasets API
            valuation = self.fd_api.get_valuation_multiples(ticker, current_price=current_price)

            if not valuation or "error" in valuation:
                return {"error": f"No valuation data available for {ticker}"}

            # Cache result
            self.metrics_cache[cache_key] = (datetime.now(), valuation)
            return valuation

        except Exception as e:
            return {"error": f"Valuation multiples fetch failed for {ticker}: {str(e)}"}

    def _get_earnings_history(self, ticker: str, quarters: int = 4) -> Dict:
        """Get earnings history from Financial Datasets"""
        ticker = ticker.upper()
        quarters = min(quarters, 8)

        try:
            earnings = self.fd_api.get_earnings(ticker, limit=quarters)

            if not earnings:
                return {"error": f"No earnings data available for {ticker}"}

            return {
                "ticker": ticker,
                "quarters": len(earnings),
                "earnings_history": earnings,
                "avg_surprise_pct": sum(e.get("surprise_percent", 0) for e in earnings) / len(earnings),
                "beat_rate": sum(1 for e in earnings if e.get("surprise_percent", 0) > 0) / len(earnings),
                "data_source": "Financial Datasets",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"Earnings fetch failed for {ticker}: {str(e)}"}

    def _get_news_sentiment(self, ticker: str, limit: int = 5) -> Dict:
        """Get news and sentiment from Financial Datasets"""
        ticker = ticker.upper()
        limit = min(limit, 20)

        try:
            news = self.fd_api.get_news(ticker, limit=limit)

            if not news:
                return {"error": f"No news available for {ticker}"}

            # Calculate average sentiment
            sentiments = [a.get("sentiment", 0.5) for a in news if "sentiment" in a]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.5

            return {
                "ticker": ticker,
                "article_count": len(news),
                "recent_articles": news[:limit],
                "avg_sentiment": round(avg_sentiment, 3),
                "sentiment_rating": "bullish" if avg_sentiment > 0.6 else "bearish" if avg_sentiment < 0.4 else "neutral",
                "data_source": "Financial Datasets",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"News fetch failed for {ticker}: {str(e)}"}


def main():
    """Test the MCP tools"""
    print("="*60)
    print("TESTING MCP FINANCIAL DATA TOOLS")
    print("="*60)

    provider = FinancialDataToolsProvider()

    # Test get_current_price
    print("\n1. Testing get_current_price('AAPL')...")
    result = provider.execute_tool("get_current_price", {"ticker": "AAPL"})
    print(json.dumps(result, indent=2))

    # Test get_multiple_prices
    print("\n2. Testing get_multiple_prices(['TSLA', 'NVDA', 'PLUG'])...")
    result = provider.execute_tool("get_multiple_prices", {"tickers": ["TSLA", "NVDA", "PLUG"]})
    print(json.dumps(result, indent=2))

    # Test get_price_history
    print("\n3. Testing get_price_history('MSFT', 30)...")
    result = provider.execute_tool("get_price_history", {"ticker": "MSFT", "days": 30})
    print(json.dumps(result, indent=2))

    # Test get_fundamental_metrics
    print("\n4. Testing get_fundamental_metrics('GOOGL')...")
    result = provider.execute_tool("get_fundamental_metrics", {"ticker": "GOOGL"})
    print(json.dumps(result, indent=2))

    print("\n" + "="*60)
    print("All tool definitions:")
    print("="*60)
    for tool in provider.get_tool_definitions():
        print(f"\n{tool['name']}:")
        print(f"  {tool['description']}")


if __name__ == "__main__":
    main()
