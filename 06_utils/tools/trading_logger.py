#!/usr/bin/env python3
"""
Unified Trading Logger System
Provides comprehensive logging for both dee-bot and shorgan-bot
Inspired by ChatGPT Micro-Cap Experiment logging patterns
"""

import csv
import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import pandas as pd

class TradeAction(Enum):
    """Trade action types"""
    BUY = "BUY"
    SELL = "SELL"
    SHORT = "SHORT"
    COVER = "COVER"
    DIVIDEND = "DIVIDEND"
    
class TradeReason(Enum):
    """Reasons for trades"""
    SIGNAL_BUY = "SIGNAL BUY"
    SIGNAL_SELL = "SIGNAL SELL"
    STOP_LOSS = "STOPLOSS TRIGGERED"
    TAKE_PROFIT = "TAKE PROFIT"
    REBALANCE = "PORTFOLIO REBALANCE"
    MANUAL = "MANUAL TRADE"
    AI_RECOMMENDATION = "AI RECOMMENDATION"
    TECHNICAL = "TECHNICAL INDICATOR"
    FUNDAMENTAL = "FUNDAMENTAL ANALYSIS"
    RISK_MANAGEMENT = "RISK MANAGEMENT"

@dataclass
class Trade:
    """Complete trade record"""
    timestamp: datetime
    bot_name: str  # dee-bot or shorgan-bot
    ticker: str
    action: TradeAction
    shares: int
    price: float
    commission: float = 0.0
    reason: TradeReason = TradeReason.MANUAL
    notes: str = ""
    
    # Calculated fields
    total_value: float = field(init=False)
    net_value: float = field(init=False)
    
    def __post_init__(self):
        self.total_value = self.shares * self.price
        self.net_value = self.total_value + self.commission if self.action == TradeAction.BUY else self.total_value - self.commission

@dataclass
class Position:
    """Current position tracking"""
    ticker: str
    shares: int
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float = 0.0
    first_purchase: Optional[datetime] = None
    last_update: Optional[datetime] = None

@dataclass
class DailyPerformance:
    """Daily performance metrics"""
    date: date
    starting_value: float
    ending_value: float
    daily_pnl: float
    daily_return: float
    trades_count: int
    commission_paid: float
    winning_trades: int
    losing_trades: int

class TradingLogger:
    """Comprehensive trading logger for both bots"""
    
    def __init__(self, bot_name: str, base_dir: Path = Path("data")):
        self.bot_name = bot_name
        self.base_dir = base_dir / bot_name
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.trade_log_file = self.base_dir / "trade_log.csv"
        self.position_file = self.base_dir / "positions.json"
        self.performance_file = self.base_dir / "daily_performance.csv"
        self.audit_log_file = self.base_dir / "audit_log.txt"
        
        # Initialize files
        self._initialize_files()
        
        # Setup Python logger
        self.logger = self._setup_logger()
        
        # Load current positions
        self.positions = self._load_positions()
    
    def _initialize_files(self):
        """Initialize log files with headers if they don't exist"""
        
        # Trade log CSV
        if not self.trade_log_file.exists():
            with open(self.trade_log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Timestamp', 'Bot', 'Ticker', 'Action', 'Shares', 
                    'Price', 'Total Value', 'Commission', 'Net Value',
                    'Reason', 'Notes'
                ])
        
        # Daily performance CSV
        if not self.performance_file.exists():
            with open(self.performance_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Date', 'Starting Value', 'Ending Value', 'Daily P&L',
                    'Daily Return %', 'Trades Count', 'Commission Paid',
                    'Winning Trades', 'Losing Trades'
                ])
        
        # Positions JSON
        if not self.position_file.exists():
            with open(self.position_file, 'w') as f:
                json.dump({}, f)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup Python logging"""
        logger = logging.getLogger(f"{self.bot_name}_trading")
        logger.setLevel(logging.DEBUG)
        
        # File handler for detailed logs
        fh = logging.FileHandler(self.base_dir / f"{self.bot_name}_trading.log")
        fh.setLevel(logging.DEBUG)
        
        # Console handler for important messages
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _load_positions(self) -> Dict[str, Position]:
        """Load current positions from file"""
        positions = {}
        
        if self.position_file.exists():
            with open(self.position_file, 'r') as f:
                data = json.load(f)
                for ticker, pos_data in data.items():
                    positions[ticker] = Position(**pos_data)
        
        return positions
    
    def _save_positions(self):
        """Save current positions to file"""
        data = {}
        for ticker, position in self.positions.items():
            pos_dict = asdict(position)
            # Convert datetime objects to strings
            if pos_dict['first_purchase']:
                pos_dict['first_purchase'] = pos_dict['first_purchase'].isoformat()
            if pos_dict['last_update']:
                pos_dict['last_update'] = pos_dict['last_update'].isoformat()
            data[ticker] = pos_dict
        
        with open(self.position_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def log_trade(self, trade: Trade) -> bool:
        """Log a trade to all relevant files"""
        try:
            # Log to CSV
            with open(self.trade_log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    trade.timestamp.isoformat(),
                    trade.bot_name,
                    trade.ticker,
                    trade.action.value,
                    trade.shares,
                    trade.price,
                    trade.total_value,
                    trade.commission,
                    trade.net_value,
                    trade.reason.value,
                    trade.notes
                ])
            
            # Update positions
            self._update_position(trade)
            
            # Log to Python logger
            self.logger.info(
                f"Trade executed: {trade.action.value} {trade.shares} shares of "
                f"{trade.ticker} at ${trade.price:.2f} - Reason: {trade.reason.value}"
            )
            
            # Audit log
            with open(self.audit_log_file, 'a') as f:
                f.write(f"{datetime.now()}: {trade.bot_name} - {trade.action.value} "
                       f"{trade.shares} {trade.ticker} @ ${trade.price:.2f}\n")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging trade: {e}")
            return False
    
    def _update_position(self, trade: Trade):
        """Update position based on trade"""
        ticker = trade.ticker
        
        if trade.action == TradeAction.BUY:
            if ticker in self.positions:
                # Update existing position
                pos = self.positions[ticker]
                total_shares = pos.shares + trade.shares
                total_cost = (pos.shares * pos.avg_cost) + trade.net_value
                pos.shares = total_shares
                pos.avg_cost = total_cost / total_shares if total_shares > 0 else 0
                pos.last_update = trade.timestamp
            else:
                # New position
                self.positions[ticker] = Position(
                    ticker=ticker,
                    shares=trade.shares,
                    avg_cost=trade.price,
                    current_price=trade.price,
                    market_value=trade.total_value,
                    unrealized_pnl=0,
                    first_purchase=trade.timestamp,
                    last_update=trade.timestamp
                )
        
        elif trade.action == TradeAction.SELL:
            if ticker in self.positions:
                pos = self.positions[ticker]
                
                # Calculate realized P&L
                realized = (trade.price - pos.avg_cost) * trade.shares
                pos.realized_pnl += realized
                
                # Update shares
                pos.shares -= trade.shares
                
                if pos.shares <= 0:
                    # Position closed
                    del self.positions[ticker]
                    self.logger.info(f"Position closed: {ticker} - Realized P&L: ${realized:.2f}")
                else:
                    pos.last_update = trade.timestamp
        
        self._save_positions()
    
    def update_market_prices(self, prices: Dict[str, float]):
        """Update current market prices and unrealized P&L"""
        for ticker, price in prices.items():
            if ticker in self.positions:
                pos = self.positions[ticker]
                pos.current_price = price
                pos.market_value = pos.shares * price
                pos.unrealized_pnl = (price - pos.avg_cost) * pos.shares
                pos.last_update = datetime.now()
        
        self._save_positions()
    
    def log_daily_performance(self, performance: DailyPerformance):
        """Log daily performance metrics"""
        with open(self.performance_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                performance.date.isoformat(),
                performance.starting_value,
                performance.ending_value,
                performance.daily_pnl,
                performance.daily_return,
                performance.trades_count,
                performance.commission_paid,
                performance.winning_trades,
                performance.losing_trades
            ])
        
        self.logger.info(
            f"Daily Performance: P&L: ${performance.daily_pnl:.2f} "
            f"({performance.daily_return:.2%}) - Trades: {performance.trades_count}"
        )
    
    def get_position_summary(self) -> Dict[str, Any]:
        """Get current position summary"""
        total_value = sum(pos.market_value for pos in self.positions.values())
        total_unrealized = sum(pos.unrealized_pnl for pos in self.positions.values())
        total_realized = sum(pos.realized_pnl for pos in self.positions.values())
        
        return {
            "positions_count": len(self.positions),
            "total_market_value": total_value,
            "total_unrealized_pnl": total_unrealized,
            "total_realized_pnl": total_realized,
            "total_pnl": total_unrealized + total_realized,
            "positions": {
                ticker: {
                    "shares": pos.shares,
                    "avg_cost": pos.avg_cost,
                    "current_price": pos.current_price,
                    "market_value": pos.market_value,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "pnl_percent": (pos.unrealized_pnl / (pos.shares * pos.avg_cost) * 100) if pos.shares > 0 else 0
                }
                for ticker, pos in self.positions.items()
            }
        }
    
    def generate_trade_report(self, start_date: Optional[date] = None, 
                            end_date: Optional[date] = None) -> pd.DataFrame:
        """Generate trade report for specified period"""
        df = pd.read_csv(self.trade_log_file)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        if start_date:
            df = df[df['Timestamp'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['Timestamp'] <= pd.to_datetime(end_date)]
        
        return df
    
    def calculate_metrics(self) -> Dict[str, float]:
        """Calculate performance metrics"""
        df = pd.read_csv(self.trade_log_file)
        
        if df.empty:
            return {}
        
        # Calculate metrics
        total_trades = len(df)
        buy_trades = len(df[df['Action'] == 'BUY'])
        sell_trades = len(df[df['Action'] == 'SELL'])
        
        # Read performance data
        perf_df = pd.read_csv(self.performance_file)
        if not perf_df.empty:
            total_pnl = perf_df['Daily P&L'].sum()
            avg_daily_return = perf_df['Daily Return %'].mean()
            win_rate = (perf_df['Winning Trades'].sum() / 
                       (perf_df['Winning Trades'].sum() + perf_df['Losing Trades'].sum()) * 100
                       if (perf_df['Winning Trades'].sum() + perf_df['Losing Trades'].sum()) > 0 else 0)
        else:
            total_pnl = 0
            avg_daily_return = 0
            win_rate = 0
        
        return {
            "total_trades": total_trades,
            "buy_trades": buy_trades,
            "sell_trades": sell_trades,
            "total_pnl": total_pnl,
            "avg_daily_return": avg_daily_return,
            "win_rate": win_rate,
            "total_commission": df['Commission'].sum() if 'Commission' in df.columns else 0
        }

# Example usage
def example_usage():
    """Example of how to use the trading logger"""
    
    # Initialize loggers for both bots
    dee_logger = TradingLogger("dee-bot")
    shorgan_logger = TradingLogger("shorgan-bot")
    
    # Log a trade
    trade = Trade(
        timestamp=datetime.now(),
        bot_name="dee-bot",
        ticker="AAPL",
        action=TradeAction.BUY,
        shares=100,
        price=233.50,
        commission=1.00,
        reason=TradeReason.AI_RECOMMENDATION,
        notes="Strong technical breakout signal"
    )
    
    dee_logger.log_trade(trade)
    
    # Update market prices
    dee_logger.update_market_prices({"AAPL": 235.00})
    
    # Get position summary
    summary = dee_logger.get_position_summary()
    print(f"Position Summary: {json.dumps(summary, indent=2)}")
    
    # Log daily performance
    performance = DailyPerformance(
        date=date.today(),
        starting_value=100000,
        ending_value=100500,
        daily_pnl=500,
        daily_return=0.005,
        trades_count=5,
        commission_paid=5.00,
        winning_trades=3,
        losing_trades=2
    )
    
    dee_logger.log_daily_performance(performance)
    
    # Get metrics
    metrics = dee_logger.calculate_metrics()
    print(f"Performance Metrics: {json.dumps(metrics, indent=2)}")

if __name__ == "__main__":
    example_usage()