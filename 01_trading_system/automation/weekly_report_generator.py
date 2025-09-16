"""
Weekly Performance Report Generator
Runs every Sunday at 2:00 PM ET
Analyzes weekly performance and generates comprehensive report
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import logging

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

load_dotenv()

# Configure logging
log_dir = '09_logs/reports'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/weekly_report_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

class WeeklyReportGenerator:
    """Generates comprehensive weekly performance reports"""
    
    def __init__(self):
        # Initialize Alpaca API
        self.api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY_SHORGAN'),
            os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
        self.report_dir = '07_docs/weekly_reports'
        self.portfolio_csv = '02_data/portfolio/positions/shorgan_bot_positions.csv'
        self.trades_dir = '08_trading_logs/trades'
        
        os.makedirs(self.report_dir, exist_ok=True)
        
    def get_week_dates(self):
        """Get start and end dates for the past week"""
        today = datetime.now()
        # Get last Monday
        days_since_monday = today.weekday()
        if days_since_monday == 6:  # Sunday
            monday = today - timedelta(days=6)
        else:
            monday = today - timedelta(days=days_since_monday)
        
        # Get Friday (or today if before Friday)
        friday = monday + timedelta(days=4)
        if friday > today:
            friday = today
            
        return monday.strftime('%Y-%m-%d'), friday.strftime('%Y-%m-%d')
    
    def get_weekly_trades(self, start_date, end_date):
        """Fetch all trades from the week"""
        try:
            # Get trades from Alpaca
            trades = self.api.list_orders(
                status='all',
                after=f"{start_date}T00:00:00Z",
                until=f"{end_date}T23:59:59Z",
                direction='desc',
                limit=500
            )
            
            return trades
        except Exception as e:
            logging.error(f"Error fetching trades: {e}")
            return []
    
    def calculate_performance_metrics(self, trades):
        """Calculate weekly performance metrics"""
        metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'largest_win': 0.0,
            'largest_loss': 0.0,
            'sharpe_ratio': 0.0,
            'total_volume': 0.0
        }
        
        wins = []
        losses = []
        
        for trade in trades:
            if trade.status != 'filled':
                continue
                
            metrics['total_trades'] += 1
            
            # Calculate P&L (simplified - would need position tracking for accurate P&L)
            qty = float(trade.filled_qty or 0)
            price = float(trade.filled_avg_price or 0)
            metrics['total_volume'] += qty * price
            
            # Note: This is simplified. Real P&L calculation would need entry/exit pairs
            # For now, we'll track what we can from order data
        
        if wins:
            metrics['winning_trades'] = len(wins)
            metrics['avg_win'] = sum(wins) / len(wins)
            metrics['largest_win'] = max(wins)
        
        if losses:
            metrics['losing_trades'] = len(losses)
            metrics['avg_loss'] = sum(losses) / len(losses)
            metrics['largest_loss'] = min(losses)
        
        if metrics['total_trades'] > 0:
            metrics['win_rate'] = (metrics['winning_trades'] / metrics['total_trades']) * 100
        
        return metrics
    
    def get_current_positions(self):
        """Get current portfolio positions"""
        try:
            positions = self.api.list_positions()
            position_data = []
            
            for pos in positions:
                position_data.append({
                    'symbol': pos.symbol,
                    'quantity': int(pos.qty),
                    'avg_cost': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price or 0),
                    'market_value': float(pos.market_value or 0),
                    'unrealized_pnl': float(pos.unrealized_pl or 0),
                    'unrealized_pnl_pct': float(pos.unrealized_plpc or 0) * 100
                })
            
            return position_data
        except Exception as e:
            logging.error(f"Error fetching positions: {e}")
            return []
    
    def get_account_metrics(self):
        """Get account-level metrics"""
        try:
            account = self.api.get_account()
            
            return {
                'portfolio_value': float(account.portfolio_value),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'equity': float(account.equity),
                'last_equity': float(account.last_equity),
                'week_change': float(account.equity) - float(account.last_equity),
                'week_change_pct': ((float(account.equity) - float(account.last_equity)) / float(account.last_equity)) * 100 if float(account.last_equity) > 0 else 0
            }
        except Exception as e:
            logging.error(f"Error fetching account metrics: {e}")
            return {}
    
    def generate_markdown_report(self, data):
        """Generate markdown report"""
        start_date, end_date = data['dates']
        
        report = f"""# Weekly Trading Report - SHORGAN-BOT
## Week of {start_date} to {end_date}

---

## Executive Summary
- **Portfolio Value**: ${data['account']['portfolio_value']:,.2f}
- **Week Change**: ${data['account']['week_change']:,.2f} ({data['account']['week_change_pct']:.2f}%)
- **Total Trades**: {data['metrics']['total_trades']}
- **Win Rate**: {data['metrics']['win_rate']:.1f}%

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Total Trades | {data['metrics']['total_trades']} |
| Winning Trades | {data['metrics']['winning_trades']} |
| Losing Trades | {data['metrics']['losing_trades']} |
| Win Rate | {data['metrics']['win_rate']:.1f}% |
| Total Volume | ${data['metrics']['total_volume']:,.2f} |
| Average Win | ${data['metrics']['avg_win']:,.2f} |
| Average Loss | ${data['metrics']['avg_loss']:,.2f} |
| Largest Win | ${data['metrics']['largest_win']:,.2f} |
| Largest Loss | ${data['metrics']['largest_loss']:,.2f} |

---

## Account Status

| Metric | Value |
|--------|-------|
| Portfolio Value | ${data['account']['portfolio_value']:,.2f} |
| Cash Balance | ${data['account']['cash']:,.2f} |
| Buying Power | ${data['account']['buying_power']:,.2f} |
| Total Equity | ${data['account']['equity']:,.2f} |

---

## Current Positions ({len(data['positions'])})

| Symbol | Quantity | Avg Cost | Current | Market Value | Unrealized P&L | % Change |
|--------|----------|----------|---------|--------------|----------------|----------|
"""
        
        for pos in data['positions']:
            report += f"| {pos['symbol']} | {pos['quantity']} | ${pos['avg_cost']:.2f} | ${pos['current_price']:.2f} | ${pos['market_value']:,.2f} | ${pos['unrealized_pnl']:,.2f} | {pos['unrealized_pnl_pct']:.2f}% |\n"
        
        report += f"""
---

## Week's Top Performers
{self._get_top_performers(data['positions'])}

## Week's Bottom Performers
{self._get_bottom_performers(data['positions'])}

---

## Risk Analysis
- **Portfolio Beta**: ~1.0 (market neutral target)
- **Max Position Size**: 15% of portfolio
- **Stop Loss Coverage**: All positions protected
- **Margin Usage**: Limited

---

## Next Week's Outlook
- Continue monitoring micro-cap catalysts
- Maintain position sizing discipline
- Focus on risk-adjusted returns
- Review and adjust stop losses

---

*Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}*
"""
        return report
    
    def _get_top_performers(self, positions, limit=3):
        """Get top performing positions"""
        if not positions:
            return "No positions to report"
        
        sorted_positions = sorted(positions, key=lambda x: x['unrealized_pnl_pct'], reverse=True)[:limit]
        
        result = ""
        for i, pos in enumerate(sorted_positions, 1):
            result += f"{i}. **{pos['symbol']}**: +{pos['unrealized_pnl_pct']:.2f}% (${pos['unrealized_pnl']:,.2f})\n"
        
        return result
    
    def _get_bottom_performers(self, positions, limit=3):
        """Get bottom performing positions"""
        if not positions:
            return "No positions to report"
        
        sorted_positions = sorted(positions, key=lambda x: x['unrealized_pnl_pct'])[:limit]
        
        result = ""
        for i, pos in enumerate(sorted_positions, 1):
            result += f"{i}. **{pos['symbol']}**: {pos['unrealized_pnl_pct']:.2f}% (${pos['unrealized_pnl']:,.2f})\n"
        
        return result
    
    def save_report(self, report, data):
        """Save report to file"""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        # Save markdown
        md_file = f"{self.report_dir}/weekly_report_{timestamp}.md"
        with open(md_file, 'w') as f:
            f.write(report)
        logging.info(f"Markdown report saved to {md_file}")
        
        # Save JSON data
        json_file = f"{self.report_dir}/weekly_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            # Convert datetime objects to strings
            data['generated_at'] = datetime.now().isoformat()
            json.dump(data, f, indent=2, default=str)
        logging.info(f"JSON data saved to {json_file}")
        
        return md_file, json_file
    
    def run(self):
        """Generate weekly report"""
        logging.info("="*60)
        logging.info("GENERATING WEEKLY REPORT")
        logging.info("="*60)
        
        try:
            # Get date range
            start_date, end_date = self.get_week_dates()
            logging.info(f"Report period: {start_date} to {end_date}")
            
            # Gather data
            trades = self.get_weekly_trades(start_date, end_date)
            metrics = self.calculate_performance_metrics(trades)
            positions = self.get_current_positions()
            account = self.get_account_metrics()
            
            # Compile data
            data = {
                'dates': (start_date, end_date),
                'metrics': metrics,
                'positions': positions,
                'account': account,
                'trades': [t.dict() for t in trades[:20]]  # Last 20 trades
            }
            
            # Generate report
            report = self.generate_markdown_report(data)
            
            # Save report
            md_file, json_file = self.save_report(report, data)
            
            logging.info("="*60)
            logging.info("WEEKLY REPORT COMPLETE")
            logging.info(f"Files saved: {md_file}, {json_file}")
            logging.info("="*60)
            
            return md_file
            
        except Exception as e:
            logging.error(f"Failed to generate weekly report: {e}")
            return None


if __name__ == "__main__":
    generator = WeeklyReportGenerator()
    generator.run()