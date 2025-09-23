#!/usr/bin/env python3
"""
Research Report Scheduler
Automates daily and weekly research report generation
Inspired by ChatGPT Micro-Cap Experiment scheduling patterns
"""

import asyncio
import schedule
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from automated_research_reporter import ResearchReportGenerator
# Optional: Import agents if needed for enhanced analysis
# from dee_bot.agents.fundamental_analyst import FundamentalAnalyst

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ReportScheduler:
    """Schedules and runs automated research reports"""
    
    def __init__(self):
        self.generator = ResearchReportGenerator()
        self.running = False
        
        # Define watchlists
        self.daily_watchlist = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", 
            "TSLA", "META", "BRK.B", "JPM", "V"
        ]
        
        self.extended_watchlist = self.daily_watchlist + [
            "UNH", "JNJ", "WMT", "PG", "MA",
            "HD", "DIS", "BAC", "XOM", "PFE"
        ]
        
        # Trading hours (Eastern Time)
        self.market_open = "09:30"
        self.market_close = "16:00"
        
    async def run_morning_analysis(self):
        """Run pre-market analysis at 8:30 AM ET"""
        logger.info("Running morning pre-market analysis...")
        
        try:
            # Generate market overview
            report = await self.generator.generate_daily_report(self.daily_watchlist)
            
            # Send notifications if configured
            await self.send_notifications(
                f"Morning Report Ready: {report['report_date']}",
                f"Market Overview: {len(report['recommendations'])} recommendations"
            )
            
            logger.info("Morning analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Error in morning analysis: {e}")
    
    async def run_midday_update(self):
        """Run midday market update at 12:30 PM ET"""
        logger.info("Running midday market update...")
        
        try:
            # Quick market check
            market_data = await self.generator.get_market_overview()
            
            # Check for significant moves
            alerts = []
            for ticker, data in market_data["major_indices"].items():
                if abs(data["change_percent"]) > 1.5:
                    alerts.append(f"{ticker}: {data['change_percent']:.2f}%")
            
            if alerts:
                await self.send_notifications(
                    "Midday Market Alert",
                    "\n".join(alerts)
                )
            
            logger.info("Midday update completed")
            
        except Exception as e:
            logger.error(f"Error in midday update: {e}")
    
    async def run_closing_report(self):
        """Run end-of-day report at 4:30 PM ET"""
        logger.info("Running closing market report...")
        
        try:
            # Generate comprehensive daily report
            report = await self.generator.generate_daily_report(self.extended_watchlist)
            
            # Generate performance graph
            graph_path = self.generator.generate_performance_graph()
            
            # Log trades from the day
            await self.log_daily_trades()
            
            # Send summary
            await self.send_notifications(
                f"Closing Report: {report['report_date']}",
                f"Daily P&L: Check {graph_path}"
            )
            
            logger.info("Closing report completed successfully")
            
        except Exception as e:
            logger.error(f"Error in closing report: {e}")
    
    async def run_weekly_summary(self):
        """Run weekly summary report on Fridays at 5:00 PM ET"""
        logger.info("Running weekly summary report...")
        
        try:
            # Generate weekly summary
            summary = await self.generator.generate_weekly_summary()
            
            # Generate extended analysis
            report_content = f"""
Weekly Trading Summary - {summary['week_ending']}
{'='*50}

Performance Metrics:
- Total Trades: {summary['total_trades']}
- Win Rate: {summary['win_rate']:.1f}%
- Total P&L: ${summary['total_pnl']:,.2f}

Top Performers:
{self._format_performers(summary['top_performers'])}

Worst Performers:
{self._format_performers(summary['worst_performers'])}

Next Week Watchlist:
{', '.join(self.daily_watchlist[:5])}
            """
            
            # Save weekly report
            report_path = Path("data/research_reports") / f"weekly_{summary['week_ending']}.txt"
            with open(report_path, 'w') as f:
                f.write(report_content)
            
            await self.send_notifications(
                "Weekly Summary Ready",
                f"Win Rate: {summary['win_rate']:.1f}% | P&L: ${summary['total_pnl']:,.2f}"
            )
            
            logger.info("Weekly summary completed successfully")
            
        except Exception as e:
            logger.error(f"Error in weekly summary: {e}")
    
    def _format_performers(self, performers: list) -> str:
        """Format performer list for report"""
        if not performers:
            return "None"
        
        lines = []
        for p in performers:
            lines.append(f"  - {p['ticker']}: ${p['pnl']:,.2f}")
        return "\n".join(lines)
    
    async def log_daily_trades(self):
        """Log trades from both bots"""
        logger.info("Logging daily trades...")
        
        # This would integrate with actual trading systems
        # For now, it's a placeholder
        pass
    
    async def send_notifications(self, subject: str, message: str):
        """Send notifications (email, Slack, etc.)"""
        logger.info(f"Notification: {subject} - {message}")
        
        # Integration with notification services would go here
        # For now, just log the notification
        
        # Save to notification log
        notif_path = Path("logs/notifications.log")
        with open(notif_path, 'a') as f:
            f.write(f"{datetime.now()}: {subject} - {message}\n")
    
    def schedule_reports(self):
        """Set up the schedule for all reports"""
        logger.info("Setting up report schedule...")
        
        # Daily reports (Monday-Friday)
        schedule.every().monday.at("08:30").do(
            lambda: asyncio.create_task(self.run_morning_analysis())
        )
        schedule.every().tuesday.at("08:30").do(
            lambda: asyncio.create_task(self.run_morning_analysis())
        )
        schedule.every().wednesday.at("08:30").do(
            lambda: asyncio.create_task(self.run_morning_analysis())
        )
        schedule.every().thursday.at("08:30").do(
            lambda: asyncio.create_task(self.run_morning_analysis())
        )
        schedule.every().friday.at("08:30").do(
            lambda: asyncio.create_task(self.run_morning_analysis())
        )
        
        # Midday updates
        schedule.every().monday.at("12:30").do(
            lambda: asyncio.create_task(self.run_midday_update())
        )
        schedule.every().tuesday.at("12:30").do(
            lambda: asyncio.create_task(self.run_midday_update())
        )
        schedule.every().wednesday.at("12:30").do(
            lambda: asyncio.create_task(self.run_midday_update())
        )
        schedule.every().thursday.at("12:30").do(
            lambda: asyncio.create_task(self.run_midday_update())
        )
        schedule.every().friday.at("12:30").do(
            lambda: asyncio.create_task(self.run_midday_update())
        )
        
        # Closing reports
        schedule.every().monday.at("16:30").do(
            lambda: asyncio.create_task(self.run_closing_report())
        )
        schedule.every().tuesday.at("16:30").do(
            lambda: asyncio.create_task(self.run_closing_report())
        )
        schedule.every().wednesday.at("16:30").do(
            lambda: asyncio.create_task(self.run_closing_report())
        )
        schedule.every().thursday.at("16:30").do(
            lambda: asyncio.create_task(self.run_closing_report())
        )
        schedule.every().friday.at("16:30").do(
            lambda: asyncio.create_task(self.run_closing_report())
        )
        
        # Weekly summary (Friday evening)
        schedule.every().friday.at("17:00").do(
            lambda: asyncio.create_task(self.run_weekly_summary())
        )
        
        logger.info("Schedule configured successfully")
    
    async def run(self):
        """Main scheduler loop"""
        self.running = True
        self.schedule_reports()
        
        logger.info("Report scheduler started")
        logger.info("Schedule:")
        logger.info("  - Morning Analysis: Mon-Fri 8:30 AM ET")
        logger.info("  - Midday Update: Mon-Fri 12:30 PM ET")
        logger.info("  - Closing Report: Mon-Fri 4:30 PM ET")
        logger.info("  - Weekly Summary: Fri 5:00 PM ET")
        
        while self.running:
            try:
                schedule.run_pending()
                await asyncio.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("Scheduler interrupted by user")
                self.running = False
                break
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("Scheduler stopped")

async def run_once():
    """Run reports once for testing"""
    scheduler = ReportScheduler()
    
    print("Running test reports...")
    
    # Run each report type
    await scheduler.run_morning_analysis()
    await scheduler.run_midday_update()
    await scheduler.run_closing_report()
    
    # Run weekly if it's Friday
    if datetime.now().weekday() == 4:
        await scheduler.run_weekly_summary()
    
    print("Test reports completed")

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Research Report Scheduler")
    parser.add_argument("--test", action="store_true", help="Run reports once for testing")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon service")
    args = parser.parse_args()
    
    if args.test:
        await run_once()
    else:
        scheduler = ReportScheduler()
        try:
            await scheduler.run()
        except KeyboardInterrupt:
            scheduler.stop()
            print("\nScheduler stopped")

if __name__ == "__main__":
    asyncio.run(main())