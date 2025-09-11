#!/usr/bin/env python3
"""
Automated Research Report Generator
Inspired by ChatGPT Micro-Cap Experiment
Generates daily research reports using Financial Datasets API and trading data
"""

import asyncio
import csv
import json
import logging
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dataclasses import dataclass, asdict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project paths
import sys
sys.path.insert(0, str(Path(__file__).parent))

from dee_bot.data.financial_datasets_api import FinancialDatasetsAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/research_reports.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TradeLog:
    """Trade log entry matching ChatGPT experiment format"""
    date: str
    ticker: str
    shares_bought: Optional[int] = None
    buy_price: Optional[float] = None
    cost_basis: Optional[float] = None
    pnl: Optional[float] = None
    reason: Optional[str] = None
    shares_sold: Optional[int] = None
    sell_price: Optional[float] = None
    
    def to_csv_row(self) -> list:
        """Convert to CSV row format"""
        return [
            self.date,
            self.ticker,
            self.shares_bought or '',
            self.buy_price or '',
            self.cost_basis or '',
            self.pnl or '',
            self.reason or '',
            self.shares_sold or '',
            self.sell_price or ''
        ]

@dataclass
class PortfolioPosition:
    """Current portfolio position"""
    ticker: str
    shares: int
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    pnl_percent: float
    weight: float  # Portfolio weight percentage

class ResearchReportGenerator:
    """Generates automated research reports with Financial Datasets API"""
    
    def __init__(self, portfolio_value: float = 1000000.0):
        self.portfolio_value = portfolio_value
        self.fd_api = FinancialDatasetsAPI()
        self.reports_dir = Path("data/research_reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Trade log file paths
        self.trade_log_path = Path("data/trade_log.csv")
        self.portfolio_path = Path("data/portfolio_positions.csv")
        
        # Initialize trade log if it doesn't exist
        self._initialize_trade_log()
    
    def _initialize_trade_log(self):
        """Initialize trade log CSV with headers"""
        if not self.trade_log_path.exists():
            self.trade_log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.trade_log_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Date', 'Ticker', 'Shares Bought', 'Buy Price', 
                    'Cost Basis', 'PnL', 'Reason', 'Shares Sold', 'Sell Price'
                ])
            logger.info(f"Initialized trade log at {self.trade_log_path}")
    
    def log_trade(self, trade: TradeLog):
        """Log a trade to CSV file"""
        with open(self.trade_log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(trade.to_csv_row())
        logger.info(f"Logged trade: {trade.ticker} - {trade.reason}")
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get market overview using available tickers"""
        overview = {
            "timestamp": datetime.now().isoformat(),
            "major_indices": {},
            "sector_performance": {},
            "top_movers": {"gainers": [], "losers": []}
        }
        
        async with self.fd_api as api:
            # Get major indices
            indices = ["SPY", "QQQ", "DIA", "IWM", "VTI"]
            for index in indices:
                snapshot = await api.get_price_snapshot(index)
                if snapshot:
                    overview["major_indices"][index] = {
                        "price": snapshot.price,
                        "change": snapshot.change,
                        "change_percent": snapshot.change_percent,
                        "volume": snapshot.volume
                    }
            
            # Get sector ETFs
            sectors = {
                "Technology": "XLK",
                "Healthcare": "XLV", 
                "Financial": "XLF",
                "Energy": "XLE",
                "Consumer": "XLY",
                "Industrial": "XLI"
            }
            
            for sector_name, etf in sectors.items():
                snapshot = await api.get_price_snapshot(etf)
                if snapshot:
                    overview["sector_performance"][sector_name] = {
                        "etf": etf,
                        "change_percent": snapshot.change_percent
                    }
        
        return overview
    
    async def analyze_portfolio_positions(self, positions: List[str]) -> List[PortfolioPosition]:
        """Analyze current portfolio positions"""
        portfolio_positions = []
        total_value = 0
        
        async with self.fd_api as api:
            for ticker in positions:
                snapshot = await api.get_price_snapshot(ticker)
                if snapshot:
                    # For demo, assume equal weight positions
                    shares = 100  # Placeholder
                    avg_cost = snapshot.price * 0.95  # Assume 5% profit for demo
                    market_value = shares * snapshot.price
                    unrealized_pnl = market_value - (shares * avg_cost)
                    
                    position = PortfolioPosition(
                        ticker=ticker,
                        shares=shares,
                        avg_cost=avg_cost,
                        current_price=snapshot.price,
                        market_value=market_value,
                        unrealized_pnl=unrealized_pnl,
                        pnl_percent=(unrealized_pnl / (shares * avg_cost)) * 100,
                        weight=0  # Calculate after total
                    )
                    portfolio_positions.append(position)
                    total_value += market_value
        
        # Calculate portfolio weights
        for position in portfolio_positions:
            position.weight = (position.market_value / total_value) * 100
        
        return portfolio_positions
    
    async def generate_daily_report(self, watchlist: List[str]) -> Dict[str, Any]:
        """Generate comprehensive daily research report"""
        logger.info("Generating daily research report...")
        
        report = {
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "report_time": datetime.now().strftime("%H:%M:%S"),
            "market_overview": await self.get_market_overview(),
            "watchlist_analysis": {},
            "recommendations": [],
            "risk_alerts": []
        }
        
        # Analyze watchlist stocks
        async with self.fd_api as api:
            for ticker in watchlist:
                snapshot = await api.get_price_snapshot(ticker)
                if snapshot:
                    analysis = {
                        "price": snapshot.price,
                        "change": snapshot.change,
                        "change_percent": snapshot.change_percent,
                        "volume": snapshot.volume,
                        "market_cap": snapshot.market_cap,
                        "signal": self._calculate_signal(snapshot)
                    }
                    report["watchlist_analysis"][ticker] = analysis
                    
                    # Generate recommendations
                    if analysis["signal"] == "BUY":
                        report["recommendations"].append({
                            "ticker": ticker,
                            "action": "BUY",
                            "reason": f"Positive momentum: {snapshot.change_percent:.2f}%",
                            "target_allocation": 5.0  # 5% position
                        })
                    elif analysis["signal"] == "SELL" and snapshot.change_percent < -5:
                        report["risk_alerts"].append({
                            "ticker": ticker,
                            "alert": "Sharp decline",
                            "change": snapshot.change_percent,
                            "action": "Review stop-loss"
                        })
        
        # Save report
        report_path = self.reports_dir / f"daily_report_{report['report_date']}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Daily report saved to {report_path}")
        return report
    
    def _calculate_signal(self, snapshot) -> str:
        """Calculate buy/sell signal based on snapshot data"""
        if snapshot.change_percent > 2:
            return "BUY"
        elif snapshot.change_percent < -2:
            return "SELL"
        else:
            return "HOLD"
    
    def generate_performance_graph(self, 
                                 start_date: Optional[date] = None,
                                 end_date: Optional[date] = None):
        """Generate performance graph similar to ChatGPT experiment"""
        if not self.trade_log_path.exists():
            logger.warning("No trade log found for graph generation")
            return
        
        # Read trade log
        df = pd.read_csv(self.trade_log_path)
        if df.empty:
            logger.warning("Trade log is empty")
            return
        
        # Convert date column
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Calculate cumulative portfolio value
        df['Portfolio_Value'] = self.portfolio_value  # Starting value
        
        # Apply PnL changes
        if 'PnL' in df.columns:
            df['PnL'].fillna(0, inplace=True)
            df['Cumulative_PnL'] = df['PnL'].cumsum()
            df['Portfolio_Value'] = self.portfolio_value + df['Cumulative_PnL']
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot portfolio value
        ax.plot(df['Date'], df['Portfolio_Value'], 
                label='Portfolio Value', color='blue', linewidth=2)
        
        # Add markers for trades
        buy_trades = df[df['Shares Bought'].notna()]
        sell_trades = df[df['Shares Sold'].notna()]
        
        if not buy_trades.empty:
            ax.scatter(buy_trades['Date'], buy_trades['Portfolio_Value'], 
                      color='green', marker='^', s=100, label='Buy', zorder=5)
        
        if not sell_trades.empty:
            ax.scatter(sell_trades['Date'], sell_trades['Portfolio_Value'], 
                      color='red', marker='v', s=100, label='Sell', zorder=5)
        
        # Calculate and annotate max drawdown
        rolling_max = df['Portfolio_Value'].expanding().max()
        drawdown = (df['Portfolio_Value'] - rolling_max) / rolling_max * 100
        max_drawdown = drawdown.min()
        max_dd_idx = drawdown.idxmin()
        
        if pd.notna(max_dd_idx):
            ax.annotate(f'Max Drawdown: {max_drawdown:.1f}%',
                       xy=(df.loc[max_dd_idx, 'Date'], df.loc[max_dd_idx, 'Portfolio_Value']),
                       xytext=(10, -30), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        # Format the plot
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax.set_title('Trading Performance Report', fontsize=14, fontweight='bold')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.xticks(rotation=45)
        
        # Add performance metrics
        total_return = ((df['Portfolio_Value'].iloc[-1] - self.portfolio_value) / 
                       self.portfolio_value * 100)
        
        metrics_text = f'Total Return: {total_return:.2f}%\n'
        metrics_text += f'Max Drawdown: {max_drawdown:.2f}%\n'
        metrics_text += f'Current Value: ${df["Portfolio_Value"].iloc[-1]:,.2f}'
        
        ax.text(0.02, 0.98, metrics_text, transform=ax.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        # Save the graph
        graph_path = self.reports_dir / f"performance_graph_{datetime.now().strftime('%Y%m%d')}.png"
        plt.savefig(graph_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Performance graph saved to {graph_path}")
        return graph_path
    
    async def generate_weekly_summary(self) -> Dict[str, Any]:
        """Generate weekly performance summary"""
        logger.info("Generating weekly summary report...")
        
        # Read trade log for the week
        df = pd.read_csv(self.trade_log_path)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Filter last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        week_df = df[df['Date'] >= week_ago]
        
        summary = {
            "week_ending": datetime.now().strftime("%Y-%m-%d"),
            "total_trades": len(week_df),
            "unique_tickers": week_df['Ticker'].nunique(),
            "total_pnl": week_df['PnL'].sum() if 'PnL' in week_df.columns else 0,
            "winning_trades": len(week_df[week_df['PnL'] > 0]) if 'PnL' in week_df.columns else 0,
            "losing_trades": len(week_df[week_df['PnL'] < 0]) if 'PnL' in week_df.columns else 0,
            "top_performers": [],
            "worst_performers": []
        }
        
        # Get top and worst performers
        if 'PnL' in week_df.columns and not week_df.empty:
            ticker_pnl = week_df.groupby('Ticker')['PnL'].sum().sort_values(ascending=False)
            
            summary["top_performers"] = [
                {"ticker": ticker, "pnl": pnl} 
                for ticker, pnl in ticker_pnl.head(3).items()
            ]
            
            summary["worst_performers"] = [
                {"ticker": ticker, "pnl": pnl} 
                for ticker, pnl in ticker_pnl.tail(3).items()
            ]
        
        # Calculate win rate
        if summary["total_trades"] > 0:
            summary["win_rate"] = (summary["winning_trades"] / summary["total_trades"]) * 100
        else:
            summary["win_rate"] = 0
        
        # Save summary
        summary_path = self.reports_dir / f"weekly_summary_{summary['week_ending']}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Weekly summary saved to {summary_path}")
        return summary

async def main():
    """Main function to run research report generation"""
    generator = ResearchReportGenerator()
    
    # Example watchlist
    watchlist = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"]
    
    # Generate daily report
    daily_report = await generator.generate_daily_report(watchlist)
    print(f"Generated daily report for {daily_report['report_date']}")
    
    # Log some example trades
    generator.log_trade(TradeLog(
        date=datetime.now().strftime("%Y-%m-%d"),
        ticker="AAPL",
        shares_bought=100,
        buy_price=233.20,
        cost_basis=23320.00,
        reason="Technical breakout"
    ))
    
    # Generate performance graph
    generator.generate_performance_graph()
    
    # Generate weekly summary
    weekly_summary = await generator.generate_weekly_summary()
    print(f"Generated weekly summary with {weekly_summary['total_trades']} trades")

if __name__ == "__main__":
    asyncio.run(main())