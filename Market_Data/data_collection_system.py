#!/usr/bin/env python3
"""
Enhanced Data Collection System for Trading Bot
Collects market data, news, sentiment, and trading performance
Similar to ChatGPT Micro-Cap Experiment but enhanced
"""

import pandas as pd
import numpy as np
import json
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import aiohttp
from dataclasses import dataclass, asdict
import logging
import sys
sys.path.append('.')

from dee_bot.data.financial_datasets_api import FinancialDatasetsAPI
from portfolio_tracker import PortfolioTracker, Trade, Position

logger = logging.getLogger(__name__)

@dataclass 
class MarketDataPoint:
    """Single market data point"""
    timestamp: datetime
    ticker: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: float

@dataclass
class NewsItem:
    """News article data"""
    timestamp: datetime
    title: str
    summary: str
    url: str
    source: str
    sentiment_score: float
    tickers_mentioned: List[str]

@dataclass
class SentimentData:
    """Market sentiment data"""
    timestamp: datetime
    ticker: str
    social_sentiment: float  # -1 to 1
    news_sentiment: float
    options_put_call_ratio: float
    fear_greed_index: float

class DataCollectionSystem:
    """Comprehensive data collection and storage system"""
    
    def __init__(self):
        """Initialize data collection system"""
        self.fd_api = FinancialDatasetsAPI()
        
        # Data directories
        self.market_data_dir = Path("Portfolio Data/Market Data")
        self.news_data_dir = Path("Portfolio Data/News Data")
        self.sentiment_data_dir = Path("Portfolio Data/Sentiment Data")
        
        # Create directories
        for dir_path in [self.market_data_dir, self.news_data_dir, self.sentiment_data_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Universe of stocks to track
        self.universe = {
            "mega_cap": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"],
            "large_cap": ["JPM", "JNJ", "PG", "UNH", "HD", "DIS", "VZ"],
            "mid_cap": ["COIN", "SQ", "ROKU", "TWLO", "ZM", "SHOP"],
            "small_cap": ["PLTR", "BB", "AMC", "GME", "WISH", "CLOV"],
            "etfs": ["SPY", "QQQ", "IWM", "VTI", "SQQQ", "TQQQ"]
        }
        
        # All tickers as flat list
        self.all_tickers = []
        for category in self.universe.values():
            self.all_tickers.extend(category)
    
    async def collect_market_data(self, tickers: Optional[List[str]] = None, period: str = "1d") -> Dict[str, List[MarketDataPoint]]:
        """Collect market data for tickers
        
        Args:
            tickers: List of tickers to collect (default: all)
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            Dictionary of ticker -> list of data points
        """
        if tickers is None:
            tickers = self.all_tickers
        
        market_data = {}
        
        for ticker in tickers:
            try:
                # Try Financial Datasets API first
                data_points = await self._collect_fd_data(ticker, period)
                if not data_points:
                    # Fallback to yfinance
                    data_points = await self._collect_yfinance_data(ticker, period)
                
                market_data[ticker] = data_points
                logger.info(f"Collected {len(data_points)} data points for {ticker}")
                
            except Exception as e:
                logger.error(f"Failed to collect data for {ticker}: {e}")
                market_data[ticker] = []
        
        # Save to files
        await self._save_market_data(market_data)
        
        return market_data
    
    async def _collect_fd_data(self, ticker: str, period: str) -> List[MarketDataPoint]:
        """Collect data from Financial Datasets API"""
        try:
            # Get price snapshot
            snapshot = await self.fd_api.get_price_snapshot(ticker)
            if not snapshot:
                return []
            
            # Convert snapshot to data point
            data_point = MarketDataPoint(
                timestamp=datetime.now(),
                ticker=ticker,
                open=snapshot.get('open', 0),
                high=snapshot.get('high', 0),
                low=snapshot.get('low', 0),
                close=snapshot.get('price', 0),
                volume=snapshot.get('volume', 0),
                adj_close=snapshot.get('price', 0)
            )
            
            return [data_point]
            
        except Exception as e:
            logger.warning(f"FD API failed for {ticker}: {e}")
            return []
    
    async def _collect_yfinance_data(self, ticker: str, period: str) -> List[MarketDataPoint]:
        """Collect data from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                return []
            
            data_points = []
            for date, row in hist.iterrows():
                data_points.append(MarketDataPoint(
                    timestamp=date.to_pydatetime(),
                    ticker=ticker,
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume']),
                    adj_close=float(row['Close'])
                ))
            
            return data_points
            
        except Exception as e:
            logger.warning(f"yfinance failed for {ticker}: {e}")
            return []
    
    async def _save_market_data(self, market_data: Dict[str, List[MarketDataPoint]]):
        """Save market data to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for ticker, data_points in market_data.items():
            if not data_points:
                continue
            
            # Save as CSV (ChatGPT experiment style)
            df_data = []
            for point in data_points:
                df_data.append(asdict(point))
            
            df = pd.DataFrame(df_data)
            
            # Save individual ticker file
            ticker_file = self.market_data_dir / f"{ticker}_{timestamp}.csv"
            df.to_csv(ticker_file, index=False)
            
            # Append to master file
            master_file = self.market_data_dir / f"market_data_{datetime.now().strftime('%Y%m%d')}.csv"
            if master_file.exists():
                df.to_csv(master_file, mode='a', header=False, index=False)
            else:
                df.to_csv(master_file, index=False)
    
    async def collect_news_data(self, tickers: Optional[List[str]] = None) -> List[NewsItem]:
        """Collect news data for tickers"""
        if tickers is None:
            tickers = self.all_tickers[:10]  # Limit to avoid API limits
        
        news_items = []
        
        for ticker in tickers:
            try:
                # Use Financial Datasets API for news
                company_info = await self.fd_api.get_company_financials(ticker)
                if company_info:
                    # Mock news item (replace with actual news API)
                    news_item = NewsItem(
                        timestamp=datetime.now(),
                        title=f"Market Update for {ticker}",
                        summary=f"Latest market analysis for {company_info.get('name', ticker)}",
                        url="",
                        source="Financial Datasets",
                        sentiment_score=0.0,
                        tickers_mentioned=[ticker]
                    )
                    news_items.append(news_item)
                
            except Exception as e:
                logger.error(f"Failed to collect news for {ticker}: {e}")
        
        # Save news data
        await self._save_news_data(news_items)
        
        return news_items
    
    async def _save_news_data(self, news_items: List[NewsItem]):
        """Save news data to files"""
        if not news_items:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d')
        news_file = self.news_data_dir / f"news_{timestamp}.json"
        
        # Convert to JSON-serializable format
        news_data = []
        for item in news_items:
            item_dict = asdict(item)
            item_dict['timestamp'] = item.timestamp.isoformat()
            news_data.append(item_dict)
        
        # Load existing data
        existing_data = []
        if news_file.exists():
            with open(news_file, 'r') as f:
                existing_data = json.load(f)
        
        # Append new data
        existing_data.extend(news_data)
        
        # Save combined data
        with open(news_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
    
    async def collect_sentiment_data(self, tickers: Optional[List[str]] = None) -> List[SentimentData]:
        """Collect sentiment data for tickers"""
        if tickers is None:
            tickers = self.all_tickers[:5]  # Limit for demo
        
        sentiment_data = []
        
        for ticker in tickers:
            try:
                # Mock sentiment data (replace with actual sentiment APIs)
                sentiment = SentimentData(
                    timestamp=datetime.now(),
                    ticker=ticker,
                    social_sentiment=np.random.uniform(-0.5, 0.5),  # Random for demo
                    news_sentiment=np.random.uniform(-0.3, 0.7),
                    options_put_call_ratio=np.random.uniform(0.5, 1.5),
                    fear_greed_index=np.random.uniform(20, 80)
                )
                sentiment_data.append(sentiment)
                
            except Exception as e:
                logger.error(f"Failed to collect sentiment for {ticker}: {e}")
        
        # Save sentiment data
        await self._save_sentiment_data(sentiment_data)
        
        return sentiment_data
    
    async def _save_sentiment_data(self, sentiment_data: List[SentimentData]):
        """Save sentiment data to files"""
        if not sentiment_data:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d')
        sentiment_file = self.sentiment_data_dir / f"sentiment_{timestamp}.json"
        
        # Convert to JSON-serializable format
        data = []
        for item in sentiment_data:
            item_dict = asdict(item)
            item_dict['timestamp'] = item.timestamp.isoformat()
            data.append(item_dict)
        
        # Load existing data
        existing_data = []
        if sentiment_file.exists():
            with open(sentiment_file, 'r') as f:
                existing_data = json.load(f)
        
        # Append new data
        existing_data.extend(data)
        
        # Save combined data
        with open(sentiment_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
    
    def create_daily_summary(self) -> Dict:
        """Create daily summary of all collected data"""
        today = datetime.now().strftime('%Y%m%d')
        
        summary = {
            'date': today,
            'timestamp': datetime.now().isoformat(),
            'market_data': {},
            'news_count': 0,
            'sentiment_summary': {},
            'data_quality': {}
        }
        
        # Check market data files
        market_files = list(self.market_data_dir.glob(f"*_{today}*.csv"))
        summary['market_data']['files_collected'] = len(market_files)
        summary['market_data']['tickers_covered'] = []
        
        for file in market_files:
            if file.stem.startswith('market_data_'):
                continue
            ticker = file.stem.split('_')[0]
            summary['market_data']['tickers_covered'].append(ticker)
        
        # Check news data
        news_file = self.news_data_dir / f"news_{today}.json"
        if news_file.exists():
            with open(news_file, 'r') as f:
                news_data = json.load(f)
                summary['news_count'] = len(news_data)
        
        # Check sentiment data
        sentiment_file = self.sentiment_data_dir / f"sentiment_{today}.json"
        if sentiment_file.exists():
            with open(sentiment_file, 'r') as f:
                sentiment_data = json.load(f)
                if sentiment_data:
                    avg_sentiment = np.mean([item['social_sentiment'] for item in sentiment_data])
                    summary['sentiment_summary']['average_social_sentiment'] = avg_sentiment
                    summary['sentiment_summary']['tickers_analyzed'] = len(sentiment_data)
        
        # Data quality assessment
        summary['data_quality']['market_data_completeness'] = len(summary['market_data']['tickers_covered']) / len(self.all_tickers) * 100
        summary['data_quality']['news_availability'] = 'Yes' if summary['news_count'] > 0 else 'No'
        summary['data_quality']['sentiment_coverage'] = 'Yes' if summary['sentiment_summary'] else 'No'
        
        # Save summary
        summary_file = Path("Portfolio Data") / f"daily_summary_{today}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    async def run_daily_collection(self):
        """Run complete daily data collection"""
        logger.info("Starting daily data collection...")
        
        # Collect market data
        logger.info("Collecting market data...")
        market_data = await self.collect_market_data(period="1d")
        
        # Collect news data
        logger.info("Collecting news data...")
        news_data = await self.collect_news_data()
        
        # Collect sentiment data
        logger.info("Collecting sentiment data...")
        sentiment_data = await self.collect_sentiment_data()
        
        # Create summary
        logger.info("Creating daily summary...")
        summary = self.create_daily_summary()
        
        logger.info(f"Data collection complete. Summary: {json.dumps(summary, indent=2)}")
        
        return {
            'market_data': market_data,
            'news_data': news_data,
            'sentiment_data': sentiment_data,
            'summary': summary
        }

class TradingDataLogger:
    """Logs trading data in ChatGPT Micro-Cap Experiment style"""
    
    def __init__(self):
        """Initialize trading data logger"""
        self.portfolio_tracker = PortfolioTracker()
        self.trade_log_file = Path("Portfolio Data/Trade Logs/chatgpt_trade_log.csv")
        self.trade_log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_trade_execution(self, signal_data: Dict, execution_result: Any):
        """Log trade execution in ChatGPT experiment format"""
        
        # Create trade record
        trade = Trade(
            timestamp=datetime.now(),
            ticker=signal_data.get('ticker', ''),
            action=signal_data.get('action', ''),
            shares=signal_data.get('shares', 0),
            price=execution_result.executed_price if execution_result and execution_result.executed_price else signal_data.get('limit_price', 0),
            total_value=0,  # Calculate below
            commission=0.0,  # Alpaca commission-free
            bot_name=signal_data.get('bot_name', ''),
            reason=signal_data.get('reason', ''),
            confidence=signal_data.get('confidence', 0)
        )
        
        trade.total_value = trade.shares * trade.price
        
        # Record in portfolio tracker
        self.portfolio_tracker.record_trade(trade)
        
        logger.info(f"Logged trade: {trade.action} {trade.shares} {trade.ticker} @ ${trade.price:.2f}")
    
    def update_portfolio_positions(self, alpaca_positions: List):
        """Update portfolio positions from Alpaca"""
        positions = []
        
        for pos in alpaca_positions:
            position = Position(
                ticker=pos['symbol'],
                shares=pos['qty'],
                avg_cost=pos['avg_cost'],
                current_price=pos.get('current_price', pos['avg_cost']),
                market_value=pos['market_value'],
                unrealized_pnl=pos['unrealized_pl'],
                realized_pnl=0.0,  # Would need to track separately
                entry_date=datetime.now(),  # Would need actual entry date
                sector="Unknown"  # Would need to lookup
            )
            positions.append(position)
        
        # Update portfolio snapshot
        cash = 100000 - sum(pos.market_value for pos in positions)  # Simplified
        self.portfolio_tracker.update_portfolio_snapshot(positions, cash)

async def test_data_collection():
    """Test the data collection system"""
    collector = DataCollectionSystem()
    
    # Test with a few tickers
    test_tickers = ["AAPL", "MSFT", "TSLA"]
    
    print("Testing data collection...")
    results = await collector.run_daily_collection()
    
    print(f"\nCollection Results:")
    print(f"Market data collected for: {len(results['market_data'])} tickers")
    print(f"News items collected: {len(results['news_data'])}")
    print(f"Sentiment data points: {len(results['sentiment_data'])}")
    
    print(f"\nDaily Summary:")
    print(json.dumps(results['summary'], indent=2))

if __name__ == "__main__":
    # Test the system
    asyncio.run(test_data_collection())