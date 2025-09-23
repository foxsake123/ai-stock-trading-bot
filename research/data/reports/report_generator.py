#!/usr/bin/env python3
"""
Comprehensive Report Generation System
Generates daily, weekly, and monthly reports in Markdown and PDF formats
Based on ChatGPT Micro-Cap Experiment but enhanced
"""

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys
sys.path.append('.')

from portfolio_tracker import PortfolioTracker
from data_collection_system import DataCollectionSystem
from dee_bot.data.financial_datasets_api import FinancialDatasetsAPI

# Try to import PDF generation (optional)
try:
    import weasyprint
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("PDF generation not available. Install weasyprint for PDF support.")

class ReportGenerator:
    """Generates comprehensive trading reports"""
    
    def __init__(self):
        """Initialize report generator"""
        self.portfolio_tracker = PortfolioTracker()
        self.data_collector = DataCollectionSystem()
        self.fd_api = FinancialDatasetsAPI()
        
        # Report directories
        self.daily_reports_dir = Path("Trading Reports/Daily Research")
        self.weekly_reports_dir = Path("Trading Reports/Weekly Summaries")
        self.monthly_reports_dir = Path("Trading Reports/Monthly Reviews")
        self.charts_dir = Path("Trading Reports/Performance Charts")
        
        # Create directories
        for dir_path in [self.daily_reports_dir, self.weekly_reports_dir, 
                        self.monthly_reports_dir, self.charts_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def generate_daily_report(self, date: Optional[datetime] = None) -> Path:
        """Generate comprehensive daily trading report
        
        Args:
            date: Date for report (default: today)
            
        Returns:
            Path to generated report file
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime('%Y%m%d')
        report_file = self.daily_reports_dir / f"daily_report_{date_str}.md"
        
        # Generate performance chart
        chart_path = self.portfolio_tracker.generate_performance_chart(
            self.charts_dir / f"daily_performance_{date_str}.png"
        )
        
        # Get portfolio data
        if self.portfolio_tracker.portfolio_history:
            latest_portfolio = self.portfolio_tracker.portfolio_history[-1]
            metrics = self.portfolio_tracker.calculate_performance_metrics()
        else:
            latest_portfolio = None
            metrics = {}
        
        # Get market data summary
        data_summary = self.data_collector.create_daily_summary()
        
        # Generate report content
        report_content = self._generate_daily_content(date, latest_portfolio, metrics, data_summary, chart_path)
        
        # Save report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Generate PDF if available
        if PDF_AVAILABLE:
            self._generate_pdf_report(report_file, report_content)
        
        print(f"Daily report generated: {report_file}")
        return report_file
    
    def _generate_daily_content(self, date: datetime, portfolio, metrics: Dict, 
                               data_summary: Dict, chart_path: Optional[Path]) -> str:
        """Generate daily report content"""
        
        date_formatted = date.strftime('%B %d, %Y')
        
        report = f"""# 📊 Daily Trading Report - {date_formatted}

*Generated at {datetime.now().strftime('%I:%M %p ET')}*

---

## 🎯 Executive Summary

"""
        
        if portfolio:
            daily_return = (portfolio.daily_pnl / portfolio.total_value) * 100 if portfolio.total_value > 0 else 0
            report += f"""
**Portfolio Performance:**
- Total Value: ${portfolio.total_value:,.2f}
- Daily P&L: ${portfolio.daily_pnl:+,.2f} ({daily_return:+.2f}%)
- Total Return: {metrics.get('total_return', 0):+.2f}%
- Cash Position: ${portfolio.cash:,.2f}

**Key Metrics:**
- Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}
- Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%
- Win Rate: {metrics.get('win_rate', 0):.1f}%
- Active Positions: {len(portfolio.positions)}
"""
        else:
            report += "\n*No portfolio data available yet*\n"
        
        # Market Overview
        report += f"""
---

## 🌍 Market Overview

**Data Collection Status:**
- Market Data Coverage: {data_summary.get('data_quality', {}).get('market_data_completeness', 0):.1f}%
- News Articles: {data_summary.get('news_count', 0)}
- Sentiment Analysis: {data_summary.get('data_quality', {}).get('sentiment_coverage', 'No')}

"""
        
        # Add performance chart
        if chart_path and chart_path.exists():
            report += f"""
---

## 📈 Performance Chart

![Portfolio Performance]({chart_path.name})

*Portfolio performance vs S&P 500 benchmark*

"""
        
        # Current Positions
        if portfolio and portfolio.positions:
            report += """
---

## 📋 Current Positions

| Ticker | Shares | Avg Cost | Current | Market Value | Unrealized P&L | Weight |
|--------|--------|----------|---------|--------------|----------------|--------|
"""
            
            for pos in sorted(portfolio.positions, key=lambda x: x.market_value, reverse=True):
                weight = (pos.market_value / portfolio.total_value) * 100 if portfolio.total_value > 0 else 0
                pnl_pct = (pos.unrealized_pnl / (pos.shares * pos.avg_cost)) * 100 if pos.shares * pos.avg_cost > 0 else 0
                
                report += f"| {pos.ticker} | {pos.shares:,} | ${pos.avg_cost:.2f} | ${pos.current_price:.2f} | "
                report += f"${pos.market_value:,.2f} | ${pos.unrealized_pnl:+,.2f} ({pnl_pct:+.1f}%) | {weight:.1f}% |\n"
        
        # Today's Trades
        if portfolio:
            today_trades = [t for t in self.portfolio_tracker.trades 
                          if t.timestamp.date() == date.date()]
            
            if today_trades:
                report += f"""
---

## 💰 Today's Trading Activity ({len(today_trades)} trades)

"""
                for trade in today_trades:
                    profit_loss = "N/A"
                    if trade.action == "SELL":
                        # Would need to calculate actual P&L
                        profit_loss = f"${trade.total_value:,.2f}"
                    
                    report += f"""
### {trade.action} {trade.ticker}
- **Shares**: {trade.shares:,}
- **Price**: ${trade.price:.2f}
- **Total Value**: ${trade.total_value:,.2f}
- **Bot**: {trade.bot_name}
- **Confidence**: {trade.confidence:.0%}
- **Reason**: {trade.reason}
- **Time**: {trade.timestamp.strftime('%I:%M %p')}
"""
            else:
                report += "\n---\n\n## 💰 Today's Trading Activity\n\n*No trades executed today*\n"
        
        # Market Analysis
        report += """
---

## 🔍 Market Analysis

### Technical Indicators
*Analysis from dee-bot and shorgan-bot agents*

"""
        
        # Add AI-generated market commentary (would integrate with actual agent output)
        report += """
### Key Market Themes
- Market showing mixed signals with moderate volatility
- Technology sector leading performance 
- Monitoring for breakout patterns in key positions
- Risk management remains priority

### Upcoming Catalysts
- Earnings announcements this week
- Federal Reserve policy updates
- Economic data releases
- Geopolitical developments

"""
        
        # Risk Assessment
        report += """
---

## ⚠️ Risk Assessment

"""
        
        if portfolio:
            # Calculate portfolio concentration
            if portfolio.positions:
                top_position_weight = max(pos.market_value for pos in portfolio.positions) / portfolio.total_value * 100
                
                report += f"""
**Portfolio Risk Metrics:**
- Largest Position: {top_position_weight:.1f}% of portfolio
- Number of Positions: {len(portfolio.positions)}
- Cash Allocation: {(portfolio.cash/portfolio.total_value)*100:.1f}%
- Beta vs S&P 500: {metrics.get('beta', 1.0):.2f}

**Risk Alerts:**
"""
                
                if top_position_weight > 20:
                    report += "- ⚠️ High concentration risk - largest position >20%\n"
                if len(portfolio.positions) < 5:
                    report += "- ⚠️ Low diversification - fewer than 5 positions\n"
                if portfolio.cash / portfolio.total_value < 0.05:
                    report += "- ⚠️ Low cash reserves - less than 5%\n"
                
                if not any(["⚠️" in line for line in report.split('\n')[-3:]]):
                    report += "- ✅ No significant risk alerts\n"
        
        # Action Items
        report += """
---

## 🎯 Action Items

### Next Trading Session
- [ ] Review overnight news and pre-market movers
- [ ] Check earnings calendar for position holdings
- [ ] Monitor key technical levels for breakouts
- [ ] Review stop-loss orders and risk limits

### Weekly Tasks
- [ ] Rebalance portfolio if needed
- [ ] Review agent performance and accuracy
- [ ] Update watchlist based on new opportunities
- [ ] Assess risk metrics and position sizing

---

## 📞 Support & Contact

For questions about this report or trading system:
- System Status: `python check_trading_status.py`
- Generate New Report: `python report_generator.py --daily`
- Emergency Stop: Set `EXECUTION_MODE=paper` in .env

---

*This report is generated by an AI-driven trading system. All recommendations should be validated with personal due diligence. Past performance does not guarantee future results.*

**Disclaimer**: This software is for educational purposes only. Trading involves significant risk of loss.

"""
        
        return report
    
    def generate_weekly_report(self, week_ending: Optional[datetime] = None) -> Path:
        """Generate weekly summary report"""
        if week_ending is None:
            week_ending = datetime.now()
        
        # Get start of week (Monday)
        days_since_monday = week_ending.weekday()
        week_start = week_ending - timedelta(days=days_since_monday)
        
        date_str = week_ending.strftime('%Y%m%d')
        report_file = self.weekly_reports_dir / f"weekly_summary_{date_str}.md"
        
        # Get weekly performance data
        weekly_trades = [t for t in self.portfolio_tracker.trades 
                        if week_start.date() <= t.timestamp.date() <= week_ending.date()]
        
        # Generate weekly chart
        weekly_chart = self.charts_dir / f"weekly_performance_{date_str}.png"
        self._generate_weekly_chart(weekly_chart, week_start, week_ending)
        
        report_content = f"""# 📅 Weekly Trading Summary - Week of {week_start.strftime('%B %d')} - {week_ending.strftime('%B %d, %Y')}

## 📊 Weekly Performance Summary

### Trading Activity
- **Total Trades**: {len(weekly_trades)}
- **Buy Orders**: {sum(1 for t in weekly_trades if t.action == 'BUY')}
- **Sell Orders**: {sum(1 for t in weekly_trades if t.action == 'SELL')}

### Performance vs Benchmark
![Weekly Performance]({weekly_chart.name})

### Key Metrics
"""
        
        if self.portfolio_tracker.portfolio_history:
            metrics = self.portfolio_tracker.calculate_performance_metrics()
            report_content += f"""
- **Weekly Return**: TBD%
- **Sharpe Ratio**: {metrics.get('sharpe_ratio', 0):.2f}
- **Win Rate**: {metrics.get('win_rate', 0):.1f}%
- **Max Drawdown**: {metrics.get('max_drawdown', 0):.2f}%
"""
        
        # Weekly trades summary
        if weekly_trades:
            report_content += "\n## 💰 Weekly Trades\n\n"
            
            by_bot = {}
            for trade in weekly_trades:
                if trade.bot_name not in by_bot:
                    by_bot[trade.bot_name] = []
                by_bot[trade.bot_name].append(trade)
            
            for bot_name, bot_trades in by_bot.items():
                report_content += f"\n### {bot_name} ({len(bot_trades)} trades)\n"
                for trade in bot_trades:
                    report_content += f"- {trade.timestamp.strftime('%m/%d')}: {trade.action} {trade.shares} {trade.ticker} @ ${trade.price:.2f}\n"
        
        report_content += f"""

## 🎯 Week Ahead

### Watchlist Updates
- Monitor current positions for continuation patterns
- Review earnings calendar for upcoming weeks
- Assess sector rotation opportunities

### Risk Management
- Rebalance positions if concentration exceeds limits  
- Update stop-loss levels based on volatility
- Review correlation between positions

---

*Generated on {datetime.now().strftime('%Y-%m-%d at %I:%M %p ET')}*
"""
        
        # Save report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"Weekly report generated: {report_file}")
        return report_file
    
    def generate_monthly_report(self, month_ending: Optional[datetime] = None) -> Path:
        """Generate monthly deep dive report"""
        if month_ending is None:
            month_ending = datetime.now()
        
        # Get first day of month
        month_start = month_ending.replace(day=1)
        
        date_str = month_ending.strftime('%Y%m')
        report_file = self.monthly_reports_dir / f"monthly_review_{date_str}.md"
        
        # Get monthly data
        monthly_trades = [t for t in self.portfolio_tracker.trades 
                         if month_start.date() <= t.timestamp.date() <= month_ending.date()]
        
        report_content = f"""# 📈 Monthly Trading Review - {month_ending.strftime('%B %Y')}

## 🎯 Executive Summary

### Performance Highlights
"""
        
        if self.portfolio_tracker.portfolio_history:
            metrics = self.portfolio_tracker.calculate_performance_metrics()
            report_content += f"""
- **Total Return**: {metrics.get('total_return', 0):+.2f}%
- **Benchmark Return**: {metrics.get('benchmark_return', 0):+.2f}%
- **Alpha Generated**: {metrics.get('total_return', 0) - metrics.get('benchmark_return', 0):+.2f}%
- **Sharpe Ratio**: {metrics.get('sharpe_ratio', 0):.2f}
- **Maximum Drawdown**: {metrics.get('max_drawdown', 0):.2f}%
"""
        
        report_content += f"""

### Trading Statistics
- **Total Trades**: {len(monthly_trades)}
- **Win Rate**: {len([t for t in monthly_trades if t.action == 'SELL']) and 'TBD' or 'N/A'}
- **Average Hold Time**: TBD days
- **Portfolio Turnover**: TBD%

## 🤖 Agent Performance Analysis

### Bot Performance Comparison
"""
        
        # Analyze by bot
        by_bot = {}
        for trade in monthly_trades:
            if trade.bot_name not in by_bot:
                by_bot[trade.bot_name] = []
            by_bot[trade.bot_name].append(trade)
        
        for bot_name, bot_trades in by_bot.items():
            avg_confidence = np.mean([t.confidence for t in bot_trades]) if bot_trades else 0
            report_content += f"""
#### {bot_name}
- **Trades Generated**: {len(bot_trades)}
- **Average Confidence**: {avg_confidence:.0%}
- **Success Rate**: TBD%
"""
        
        report_content += f"""

## 📊 Portfolio Evolution

### Sector Allocation Changes
*Track how portfolio allocation has changed over the month*

### Position Analysis
*Deep dive into top performers and underperformers*

## 🔍 Strategy Performance

### What Worked
- Identify successful trading patterns
- Analyze winning positions and strategies
- Document agent decision accuracy

### Areas for Improvement  
- Review losing trades and patterns
- Identify agent weaknesses
- Suggest strategy refinements

## 🎯 Next Month Strategy

### Focus Areas
- Sectors showing strength
- Technical setups to monitor
- Risk management adjustments

### Agent Improvements
- Parameter tuning based on performance
- New data sources to integrate
- Risk model enhancements

---

*This comprehensive review analyzes all trading activity and system performance for the month.*
"""
        
        # Save report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"Monthly report generated: {report_file}")
        return report_file
    
    def _generate_weekly_chart(self, chart_path: Path, week_start: datetime, week_end: datetime):
        """Generate weekly performance chart"""
        # This would generate a more detailed weekly chart
        # For now, use the existing portfolio chart function
        self.portfolio_tracker.generate_performance_chart(chart_path)
    
    def _generate_pdf_report(self, markdown_file: Path, content: str):
        """Generate PDF version of report"""
        if not PDF_AVAILABLE:
            return
        
        try:
            # Basic HTML conversion (would need better CSS styling)
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #2E86AB; }}
                    h2 {{ color: #A23B72; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                {content.replace('# ', '<h1>').replace('## ', '<h2>').replace('### ', '<h3>')}
            </body>
            </html>
            """
            
            pdf_file = markdown_file.with_suffix('.pdf')
            weasyprint.HTML(string=html_content).write_pdf(pdf_file)
            print(f"PDF report generated: {pdf_file}")
            
        except Exception as e:
            print(f"PDF generation failed: {e}")
    
    def generate_all_reports(self):
        """Generate all report types for current period"""
        print("Generating all reports...")
        
        # Daily report
        daily_report = self.generate_daily_report()
        
        # Weekly report (if it's end of week)
        if datetime.now().weekday() == 4:  # Friday
            weekly_report = self.generate_weekly_report()
        
        # Monthly report (if it's end of month)
        tomorrow = datetime.now() + timedelta(days=1)
        if tomorrow.day == 1:  # Last day of month
            monthly_report = self.generate_monthly_report()
        
        print("Report generation complete!")

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate trading reports')
    parser.add_argument('--daily', action='store_true', help='Generate daily report')
    parser.add_argument('--weekly', action='store_true', help='Generate weekly report')
    parser.add_argument('--monthly', action='store_true', help='Generate monthly report')
    parser.add_argument('--all', action='store_true', help='Generate all applicable reports')
    
    args = parser.parse_args()
    
    generator = ReportGenerator()
    
    if args.daily:
        generator.generate_daily_report()
    elif args.weekly:
        generator.generate_weekly_report()
    elif args.monthly:
        generator.generate_monthly_report()
    elif args.all:
        generator.generate_all_reports()
    else:
        # Default to daily
        generator.generate_daily_report()

if __name__ == "__main__":
    main()