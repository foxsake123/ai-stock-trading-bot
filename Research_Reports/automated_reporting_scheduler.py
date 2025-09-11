#!/usr/bin/env python3
"""
Automated Reporting Scheduler
Schedules and manages automated generation of trading reports
Similar to ChatGPT Micro-Cap Experiment scheduling
"""

import schedule
import asyncio
import logging
from datetime import datetime, time, timedelta
from pathlib import Path
import sys
sys.path.append('.')

from report_generator import ReportGenerator
from data_collection_system import DataCollectionSystem
from portfolio_tracker import PortfolioTracker
import send_telegram_now  # For notifications

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automated_reports.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedReportingScheduler:
    """Manages automated report generation and data collection"""
    
    def __init__(self):
        """Initialize the automated reporting scheduler"""
        self.report_generator = ReportGenerator()
        self.data_collector = DataCollectionSystem()
        self.portfolio_tracker = PortfolioTracker()
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Scheduling status
        self.is_market_day = self._is_trading_day()
        self.last_report_date = None
    
    def _is_trading_day(self) -> bool:
        """Check if today is a trading day (weekday, non-holiday)"""
        today = datetime.now()
        
        # Basic check - weekday only (would need holiday calendar for accuracy)
        return today.weekday() < 5  # Monday=0, Friday=4
    
    async def run_morning_data_collection(self):
        """Run morning data collection at 8:30 AM ET"""
        logger.info("Starting morning data collection...")
        
        try:
            # Collect all market data
            results = await self.data_collector.run_daily_collection()
            
            # Update portfolio with latest positions (would integrate with Alpaca)
            # For now, just log the collection results
            logger.info(f"Morning data collection complete: {len(results['market_data'])} tickers")
            
            # Send notification
            await self._send_notification("📊 Morning data collection complete")
            
        except Exception as e:
            logger.error(f"Morning data collection failed: {e}")
            await self._send_notification(f"❌ Morning data collection failed: {str(e)}")
    
    async def run_midday_update(self):
        """Run midday portfolio update at 12:30 PM ET"""
        logger.info("Running midday portfolio update...")
        
        try:
            # Generate quick status update
            if self.portfolio_tracker.portfolio_history:
                latest = self.portfolio_tracker.portfolio_history[-1]
                daily_pnl = latest.daily_pnl
                daily_return = (daily_pnl / latest.total_value) * 100 if latest.total_value > 0 else 0
                
                status_msg = f"📈 Midday Update:\n"
                status_msg += f"Portfolio: ${latest.total_value:,.2f}\n"
                status_msg += f"Daily P&L: ${daily_pnl:+,.2f} ({daily_return:+.2f}%)\n"
                status_msg += f"Positions: {len(latest.positions)}"
                
                await self._send_notification(status_msg)
            else:
                await self._send_notification("📊 Midday update: No portfolio data available")
                
        except Exception as e:
            logger.error(f"Midday update failed: {e}")
            await self._send_notification(f"❌ Midday update failed: {str(e)}")
    
    async def run_daily_report_generation(self):
        """Generate end-of-day report at 4:30 PM ET"""
        logger.info("Generating daily report...")
        
        try:
            # Generate daily report
            report_file = self.report_generator.generate_daily_report()
            
            # Update last report date
            self.last_report_date = datetime.now().date()
            
            # Send notification with summary
            if self.portfolio_tracker.portfolio_history:
                latest = self.portfolio_tracker.portfolio_history[-1]
                metrics = self.portfolio_tracker.calculate_performance_metrics()
                
                summary = f"📊 Daily Report Generated:\n"
                summary += f"Portfolio: ${latest.total_value:,.2f}\n"
                summary += f"Daily P&L: ${latest.daily_pnl:+,.2f}\n"
                summary += f"Total Return: {metrics.get('total_return', 0):+.2f}%\n"
                summary += f"Report: {report_file.name}"
                
                await self._send_notification(summary)
            else:
                await self._send_notification(f"📊 Daily report generated: {report_file.name}")
            
            logger.info(f"Daily report generated successfully: {report_file}")
            
        except Exception as e:
            logger.error(f"Daily report generation failed: {e}")
            await self._send_notification(f"❌ Daily report failed: {str(e)}")
    
    async def run_weekly_report_generation(self):
        """Generate weekly report on Friday at 5:00 PM ET"""
        logger.info("Generating weekly report...")
        
        try:
            report_file = self.report_generator.generate_weekly_report()
            
            # Calculate weekly performance
            weekly_summary = "📅 Weekly Report Generated:\n"
            
            if self.portfolio_tracker.portfolio_history:
                # Get week's performance (simplified)
                week_start = datetime.now() - timedelta(days=7)
                week_snapshots = [s for s in self.portfolio_tracker.portfolio_history 
                                if s.date.date() >= week_start.date()]
                
                if len(week_snapshots) >= 2:
                    week_return = ((week_snapshots[-1].total_value - week_snapshots[0].total_value) 
                                 / week_snapshots[0].total_value) * 100
                    weekly_summary += f"Weekly Return: {week_return:+.2f}%\n"
                
                # Count week's trades
                week_trades = [t for t in self.portfolio_tracker.trades 
                             if t.timestamp.date() >= week_start.date()]
                weekly_summary += f"Trades This Week: {len(week_trades)}\n"
            
            weekly_summary += f"Report: {report_file.name}"
            
            await self._send_notification(weekly_summary)
            logger.info(f"Weekly report generated successfully: {report_file}")
            
        except Exception as e:
            logger.error(f"Weekly report generation failed: {e}")
            await self._send_notification(f"❌ Weekly report failed: {str(e)}")
    
    async def run_monthly_report_generation(self):
        """Generate monthly report on last day of month"""
        logger.info("Generating monthly report...")
        
        try:
            report_file = self.report_generator.generate_monthly_report()
            
            monthly_summary = f"📈 Monthly Report Generated:\n"
            monthly_summary += f"Report: {report_file.name}\n"
            monthly_summary += "Deep dive analysis available"
            
            await self._send_notification(monthly_summary)
            logger.info(f"Monthly report generated successfully: {report_file}")
            
        except Exception as e:
            logger.error(f"Monthly report generation failed: {e}")
            await self._send_notification(f"❌ Monthly report failed: {str(e)}")
    
    async def _send_notification(self, message: str):
        """Send notification via Telegram or other channels"""
        try:
            # Use existing Telegram notification system
            import subprocess
            
            # Run the telegram notification script
            result = subprocess.run([
                'python', 'send_telegram_now.py', 
                '--message', f"🤖 Trading Bot Report\n\n{message}"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("Notification sent successfully")
            else:
                logger.warning(f"Notification failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    def setup_schedule(self):
        """Set up the automated scheduling"""
        logger.info("Setting up automated report schedule...")
        
        # Only schedule on trading days
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        
        for day in weekdays:
            # Morning data collection - 8:30 AM ET
            getattr(schedule.every(), day).at("08:30").do(
                lambda: asyncio.create_task(self.run_morning_data_collection())
            )
            
            # Midday update - 12:30 PM ET  
            getattr(schedule.every(), day).at("12:30").do(
                lambda: asyncio.create_task(self.run_midday_update())
            )
            
            # Daily report - 4:30 PM ET
            getattr(schedule.every(), day).at("16:30").do(
                lambda: asyncio.create_task(self.run_daily_report_generation())
            )
        
        # Weekly report - Friday 5:00 PM ET
        schedule.every().friday.at("17:00").do(
            lambda: asyncio.create_task(self.run_weekly_report_generation())
        )
        
        # Monthly report - Last trading day of month at 6:00 PM ET
        # (Would need more sophisticated logic for actual last trading day)
        schedule.every().day.at("18:00").do(
            self._check_monthly_report
        )
        
        logger.info("Schedule configured:")
        logger.info("  - 8:30 AM: Morning data collection")  
        logger.info("  - 12:30 PM: Midday portfolio update")
        logger.info("  - 4:30 PM: Daily report generation")
        logger.info("  - Friday 5:00 PM: Weekly report")
        logger.info("  - Month-end 6:00 PM: Monthly report")
    
    def _check_monthly_report(self):
        """Check if we should generate monthly report"""
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        # If tomorrow is first of month and today is weekday, generate monthly
        if tomorrow.day == 1 and today.weekday() < 5:
            asyncio.create_task(self.run_monthly_report_generation())
    
    async def run_scheduler(self):
        """Run the main scheduler loop"""
        logger.info("Starting automated reporting scheduler...")
        
        # Setup schedule
        self.setup_schedule()
        
        # Send startup notification
        await self._send_notification("🤖 Automated reporting scheduler started")
        
        # Main loop
        try:
            while True:
                # Run pending scheduled tasks
                schedule.run_pending()
                
                # Sleep for 60 seconds before checking again
                await asyncio.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            await self._send_notification("🛑 Automated reporting scheduler stopped")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            await self._send_notification(f"❌ Scheduler error: {str(e)}")
    
    def run_manual_reports(self, report_type: str = "all"):
        """Manually trigger report generation"""
        logger.info(f"Running manual {report_type} report generation...")
        
        if report_type in ["daily", "all"]:
            asyncio.run(self.run_daily_report_generation())
        
        if report_type in ["weekly", "all"]:
            asyncio.run(self.run_weekly_report_generation())
        
        if report_type in ["monthly", "all"]:
            asyncio.run(self.run_monthly_report_generation())

def main():
    """Main function for running the scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Trading Report Scheduler')
    parser.add_argument('--manual', choices=['daily', 'weekly', 'monthly', 'all'], 
                       help='Manually generate specific report type')
    parser.add_argument('--daemon', action='store_true', 
                       help='Run as daemon with automated scheduling')
    
    args = parser.parse_args()
    
    scheduler = AutomatedReportingScheduler()
    
    if args.manual:
        # Run manual report generation
        scheduler.run_manual_reports(args.manual)
    elif args.daemon:
        # Run as daemon
        asyncio.run(scheduler.run_scheduler())
    else:
        # Default: generate daily report
        scheduler.run_manual_reports("daily")

if __name__ == "__main__":
    main()