#!/usr/bin/env python3
"""
Enhanced Portfolio Tracking System
Based on ChatGPT Micro-Cap Experiment structure with improvements
"""

import pandas as pd
import numpy as np
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass, asdict
import sys
sys.path.append('.')

from automated_trade_executor import ExecutionResult
from dee_bot.data.financial_datasets_api import FinancialDatasetsAPI

@dataclass
class Position:
    """Portfolio position data"""
    ticker: str
    shares: int
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float
    entry_date: datetime
    sector: str = "Unknown"
    
@dataclass
class Trade:
    """Individual trade record"""
    timestamp: datetime
    ticker: str
    action: str  # BUY/SELL
    shares: int
    price: float
    total_value: float
    commission: float
    bot_name: str
    reason: str
    confidence: float

@dataclass
class PortfolioSnapshot:
    """Daily portfolio snapshot"""
    date: datetime
    total_value: float
    cash: float
    positions_value: float
    daily_pnl: float
    total_pnl: float
    positions: List[Position]
    benchmark_value: float  # SPY comparison

class PortfolioTracker:
    """Enhanced portfolio tracking and reporting system"""
    
    def __init__(self, initial_value: float = 100000.0):
        """Initialize portfolio tracker
        
        Args:
            initial_value: Starting portfolio value
        """
        self.initial_value = initial_value
        self.fd_api = FinancialDatasetsAPI()
        
        # Data directories
        self.trade_logs_dir = Path("Portfolio Data/Trade Logs")
        self.positions_dir = Path("Portfolio Data/Position Tracking")
        self.metrics_dir = Path("Portfolio Data/Performance Metrics")
        self.reports_dir = Path("Trading Reports")
        
        # Create directories
        for dir_path in [self.trade_logs_dir, self.positions_dir, self.metrics_dir, self.reports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize data files
        self.trade_log_file = self.trade_logs_dir / "trade_history.csv"
        self.portfolio_file = self.positions_dir / "portfolio_history.json"
        self.performance_file = self.metrics_dir / "performance_metrics.json"
        
        # Load existing data
        self.trades = self._load_trades()
        self.portfolio_history = self._load_portfolio_history()
        
    def _load_trades(self) -> List[Trade]:
        """Load trade history from CSV"""
        trades = []
        if self.trade_log_file.exists():
            df = pd.read_csv(self.trade_log_file)
            for _, row in df.iterrows():
                trades.append(Trade(
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    ticker=row['ticker'],
                    action=row['action'],
                    shares=int(row['shares']),
                    price=float(row['price']),
                    total_value=float(row['total_value']),
                    commission=float(row['commission']),
                    bot_name=row['bot_name'],
                    reason=row['reason'],
                    confidence=float(row['confidence'])
                ))
        return trades
    
    def _load_portfolio_history(self) -> List[PortfolioSnapshot]:
        """Load portfolio history"""
        history = []
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r') as f:
                data = json.load(f)
                for entry in data:
                    positions = [Position(**pos) for pos in entry['positions']]
                    history.append(PortfolioSnapshot(
                        date=datetime.fromisoformat(entry['date']),
                        total_value=entry['total_value'],
                        cash=entry['cash'],
                        positions_value=entry['positions_value'],
                        daily_pnl=entry['daily_pnl'],
                        total_pnl=entry['total_pnl'],
                        positions=positions,
                        benchmark_value=entry['benchmark_value']
                    ))
        return history
    
    def record_trade(self, trade: Trade):
        """Record a new trade"""
        self.trades.append(trade)
        
        # Save to CSV (ChatGPT experiment style)
        trade_data = {
            'timestamp': trade.timestamp.isoformat(),
            'ticker': trade.ticker,
            'action': trade.action,
            'shares': trade.shares,
            'price': trade.price,
            'total_value': trade.total_value,
            'commission': trade.commission,
            'bot_name': trade.bot_name,
            'reason': trade.reason,
            'confidence': trade.confidence
        }
        
        # Write header if file doesn't exist
        file_exists = self.trade_log_file.exists()
        with open(self.trade_log_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=trade_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(trade_data)
    
    def update_portfolio_snapshot(self, positions: List[Position], cash: float):
        """Update daily portfolio snapshot"""
        
        # Calculate values
        positions_value = sum(pos.market_value for pos in positions)
        total_value = positions_value + cash
        
        # Calculate daily P&L
        daily_pnl = 0.0
        if self.portfolio_history:
            yesterday_value = self.portfolio_history[-1].total_value
            daily_pnl = total_value - yesterday_value
        
        # Calculate total P&L
        total_pnl = total_value - self.initial_value
        
        # Get benchmark (SPY) value
        benchmark_value = self._get_benchmark_value()
        
        # Create snapshot
        snapshot = PortfolioSnapshot(
            date=datetime.now(),
            total_value=total_value,
            cash=cash,
            positions_value=positions_value,
            daily_pnl=daily_pnl,
            total_pnl=total_pnl,
            positions=positions,
            benchmark_value=benchmark_value
        )
        
        self.portfolio_history.append(snapshot)
        
        # Save to file
        self._save_portfolio_history()
        
        return snapshot
    
    def _get_benchmark_value(self) -> float:
        """Get S&P 500 (SPY) value for comparison"""
        try:
            spy = yf.Ticker("SPY")
            return spy.history(period="1d")['Close'].iloc[-1]
        except:
            return 0.0
    
    def _save_portfolio_history(self):
        """Save portfolio history to JSON"""
        data = []
        for snapshot in self.portfolio_history:
            positions_data = [asdict(pos) for pos in snapshot.positions]
            # Convert datetime objects to strings
            for pos_data in positions_data:
                if isinstance(pos_data['entry_date'], datetime):
                    pos_data['entry_date'] = pos_data['entry_date'].isoformat()
            
            data.append({
                'date': snapshot.date.isoformat(),
                'total_value': snapshot.total_value,
                'cash': snapshot.cash,
                'positions_value': snapshot.positions_value,
                'daily_pnl': snapshot.daily_pnl,
                'total_pnl': snapshot.total_pnl,
                'positions': positions_data,
                'benchmark_value': snapshot.benchmark_value
            })
        
        with open(self.portfolio_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_performance_metrics(self) -> Dict:
        """Calculate key performance metrics"""
        if len(self.portfolio_history) < 2:
            return {"error": "Insufficient data for metrics calculation"}
        
        # Get daily returns
        values = [snap.total_value for snap in self.portfolio_history]
        returns = np.diff(values) / values[:-1]
        
        # Get benchmark returns (SPY)
        benchmark_values = [snap.benchmark_value for snap in self.portfolio_history]
        benchmark_returns = np.diff(benchmark_values) / benchmark_values[:-1] if benchmark_values[0] > 0 else [0] * len(returns)
        
        # Calculate metrics
        total_return = (values[-1] - values[0]) / values[0] * 100
        
        # Annualized return
        days = (self.portfolio_history[-1].date - self.portfolio_history[0].date).days
        annualized_return = ((values[-1] / values[0]) ** (365 / max(days, 1)) - 1) * 100 if days > 0 else 0
        
        # Volatility (annualized)
        volatility = np.std(returns) * np.sqrt(252) * 100 if len(returns) > 1 else 0
        
        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        sharpe_ratio = (annualized_return/100 - risk_free_rate) / (volatility/100) if volatility > 0 else 0
        
        # Maximum drawdown
        peak = values[0]
        max_drawdown = 0
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
        max_drawdown *= 100
        
        # Win rate
        winning_trades = sum(1 for trade in self.trades if trade.action == "SELL" and trade.total_value > 0)
        total_trades = len([trade for trade in self.trades if trade.action == "SELL"])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Beta (vs SPY)
        if len(returns) > 1 and len(benchmark_returns) == len(returns):
            covariance = np.cov(returns, benchmark_returns)[0, 1]
            benchmark_variance = np.var(benchmark_returns)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
        else:
            beta = 1.0
        
        metrics = {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'beta': beta,
            'total_trades': len(self.trades),
            'current_value': values[-1],
            'benchmark_return': (benchmark_values[-1] - benchmark_values[0]) / benchmark_values[0] * 100 if benchmark_values[0] > 0 else 0,
            'last_updated': datetime.now().isoformat()
        }
        
        # Save metrics
        with open(self.performance_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return metrics
    
    def generate_performance_chart(self, save_path: Optional[Path] = None) -> Path:
        """Generate performance chart comparing to benchmark"""
        if len(self.portfolio_history) < 2:
            print("Insufficient data for chart generation")
            return None
        
        # Prepare data
        dates = [snap.date for snap in self.portfolio_history]
        values = [snap.total_value for snap in self.portfolio_history]
        benchmark_values = [snap.benchmark_value for snap in self.portfolio_history]
        
        # Normalize to starting value for comparison
        portfolio_normalized = [(v / values[0] - 1) * 100 for v in values]
        benchmark_normalized = [(v / benchmark_values[0] - 1) * 100 for v in benchmark_values] if benchmark_values[0] > 0 else [0] * len(values)
        
        # Create chart
        plt.style.use('seaborn-v0_8')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Performance comparison
        ax1.plot(dates, portfolio_normalized, label='Portfolio', linewidth=2, color='#2E86AB')
        ax1.plot(dates, benchmark_normalized, label='S&P 500 (SPY)', linewidth=2, color='#A23B72')
        ax1.set_title('Portfolio vs S&P 500 Performance', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Returns (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Daily P&L
        daily_pnl = [snap.daily_pnl for snap in self.portfolio_history[1:]]  # Skip first day
        colors = ['green' if pnl >= 0 else 'red' for pnl in daily_pnl]
        ax2.bar(dates[1:], daily_pnl, color=colors, alpha=0.7)
        ax2.set_title('Daily P&L', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Daily P&L ($)')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        
        # Save chart
        if save_path is None:
            save_path = self.reports_dir / "Performance Charts" / f"performance_{datetime.now().strftime('%Y%m%d')}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def generate_daily_report(self) -> str:
        """Generate daily performance report"""
        if not self.portfolio_history:
            return "No portfolio data available"
        
        latest = self.portfolio_history[-1]
        metrics = self.calculate_performance_metrics()
        
        # Generate chart
        chart_path = self.generate_performance_chart()
        
        # Create report
        report = f"""# Daily Portfolio Report - {latest.date.strftime('%Y-%m-%d')}

## Portfolio Summary
- **Total Value**: ${latest.total_value:,.2f}
- **Daily P&L**: ${latest.daily_pnl:+,.2f} ({latest.daily_pnl/latest.total_value*100:+.2f}%)
- **Total P&L**: ${latest.total_pnl:+,.2f} ({metrics['total_return']:+.2f}%)
- **Cash Position**: ${latest.cash:,.2f}
- **Invested**: ${latest.positions_value:,.2f}

## Performance Metrics
- **Total Return**: {metrics['total_return']:+.2f}%
- **Annualized Return**: {metrics['annualized_return']:+.2f}%
- **Sharpe Ratio**: {metrics['sharpe_ratio']:.2f}
- **Max Drawdown**: {metrics['max_drawdown']:.2f}%
- **Win Rate**: {metrics['win_rate']:.1f}%
- **Beta vs S&P 500**: {metrics['beta']:.2f}

## Current Positions ({len(latest.positions)} holdings)
"""
        
        # Add positions
        for pos in sorted(latest.positions, key=lambda x: x.market_value, reverse=True):
            pnl_pct = (pos.unrealized_pnl / (pos.shares * pos.avg_cost)) * 100 if pos.shares * pos.avg_cost > 0 else 0
            weight = pos.market_value / latest.total_value * 100
            report += f"""
### {pos.ticker} ({pos.sector})
- **Shares**: {pos.shares:,}
- **Avg Cost**: ${pos.avg_cost:.2f}
- **Current**: ${pos.current_price:.2f}
- **Market Value**: ${pos.market_value:,.2f} ({weight:.1f}% of portfolio)
- **Unrealized P&L**: ${pos.unrealized_pnl:+,.2f} ({pnl_pct:+.2f}%)
- **Entry Date**: {pos.entry_date.strftime('%Y-%m-%d')}
"""
        
        # Add recent trades
        recent_trades = [t for t in self.trades if t.timestamp.date() == latest.date.date()]
        if recent_trades:
            report += f"\n## Today's Trades ({len(recent_trades)})\n"
            for trade in recent_trades:
                report += f"""
- **{trade.action}** {trade.shares} {trade.ticker} @ ${trade.price:.2f}
  - Bot: {trade.bot_name} | Confidence: {trade.confidence:.0%}
  - Reason: {trade.reason}
"""
        
        report += f"\n## Benchmark Comparison\n"
        report += f"- **Portfolio**: {metrics['total_return']:+.2f}%\n"
        report += f"- **S&P 500**: {metrics['benchmark_return']:+.2f}%\n"
        report += f"- **Alpha**: {metrics['total_return'] - metrics['benchmark_return']:+.2f}%\n"
        
        # Save report
        report_path = self.reports_dir / "Daily Research" / f"daily_report_{latest.date.strftime('%Y%m%d')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"Daily report saved to: {report_path}")
        return report

def test_portfolio_tracker():
    """Test the portfolio tracker"""
    tracker = PortfolioTracker()
    
    # Test trade recording
    test_trade = Trade(
        timestamp=datetime.now(),
        ticker="AAPL",
        action="BUY",
        shares=100,
        price=235.50,
        total_value=23550.00,
        commission=0.00,
        bot_name="dee-bot",
        reason="Technical breakout",
        confidence=0.75
    )
    
    tracker.record_trade(test_trade)
    
    # Test position tracking
    test_positions = [
        Position(
            ticker="AAPL",
            shares=100,
            avg_cost=235.50,
            current_price=238.00,
            market_value=23800.00,
            unrealized_pnl=250.00,
            realized_pnl=0.00,
            entry_date=datetime.now(),
            sector="Technology"
        )
    ]
    
    snapshot = tracker.update_portfolio_snapshot(test_positions, 76450.00)
    
    # Generate reports
    metrics = tracker.calculate_performance_metrics()
    print(f"Performance Metrics: {json.dumps(metrics, indent=2)}")
    
    report = tracker.generate_daily_report()
    print("Daily report generated successfully")

if __name__ == "__main__":
    test_portfolio_tracker()