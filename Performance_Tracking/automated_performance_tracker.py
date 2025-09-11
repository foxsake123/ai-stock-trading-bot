"""
Automated Daily Performance Tracker
Runs daily after market close to track and report performance
"""

import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, time
import pytz
import asyncio
import schedule
import logging
from daily_performance_tracker import DailyPerformanceTracker
from send_performance_update import PerformanceReporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance_tracking.log'),
        logging.StreamHandler()
    ]
)

class AutomatedPerformanceTracker:
    """Automated daily performance tracking and reporting"""
    
    def __init__(self):
        self.eastern = pytz.timezone('US/Eastern')
        self.market_close_time = time(16, 15)  # 4:15 PM ET (15 min after close)
        self.pre_market_time = time(8, 30)     # 8:30 AM ET (before market open)
        
    def is_market_day(self):
        """Check if today is a trading day (Mon-Fri)"""
        today = datetime.now(self.eastern)
        return today.weekday() < 5  # Monday = 0, Friday = 4
    
    async def run_performance_tracking(self):
        """Run the complete performance tracking pipeline"""
        if not self.is_market_day():
            logging.info("Not a market day, skipping performance tracking")
            return
            
        logging.info("="*70)
        logging.info("STARTING AUTOMATED PERFORMANCE TRACKING")
        logging.info(f"Time: {datetime.now(self.eastern).strftime('%Y-%m-%d %I:%M %p ET')}")
        logging.info("="*70)
        
        try:
            # Step 1: Track performance from Alpaca
            logging.info("[1/2] Fetching performance data from Alpaca...")
            tracker = DailyPerformanceTracker()
            performance_data = tracker.track_all_performance()
            
            if performance_data:
                logging.info("Performance data collected successfully")
                
                # Step 2: Send Telegram update
                logging.info("[2/2] Sending Telegram update...")
                reporter = PerformanceReporter()
                await reporter.send_performance_update()
                logging.info("Telegram update sent successfully")
                
                # Log summary
                combined = performance_data.get('combined', {})
                if combined:
                    logging.info(f"Daily P&L: ${combined.get('total_daily_pnl', 0):,.2f}")
                    logging.info(f"Total Portfolio: ${combined.get('total_value', 200000):,.2f}")
            else:
                logging.error("Failed to collect performance data")
                
        except Exception as e:
            logging.error(f"Error in performance tracking: {str(e)}")
            
        logging.info("="*70)
        logging.info("PERFORMANCE TRACKING COMPLETE")
        logging.info("="*70)
    
    def run_async_task(self):
        """Wrapper to run async task in sync context"""
        asyncio.run(self.run_performance_tracking())
    
    def schedule_daily_tracking(self):
        """Schedule daily performance tracking"""
        # Schedule for 4:15 PM ET every weekday
        schedule.every().monday.at("16:15").do(self.run_async_task)
        schedule.every().tuesday.at("16:15").do(self.run_async_task)
        schedule.every().wednesday.at("16:15").do(self.run_async_task)
        schedule.every().thursday.at("16:15").do(self.run_async_task)
        schedule.every().friday.at("16:15").do(self.run_async_task)
        
        logging.info("Performance tracking scheduled for 4:15 PM ET on weekdays")
        
    def run_continuous(self):
        """Run the scheduler continuously"""
        self.schedule_daily_tracking()
        
        logging.info("Automated Performance Tracker Started")
        logging.info("Waiting for scheduled times...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Performance Tracker')
    parser.add_argument('--run-now', action='store_true', 
                       help='Run performance tracking immediately')
    parser.add_argument('--schedule', action='store_true',
                       help='Run on schedule (4:15 PM ET daily)')
    
    args = parser.parse_args()
    
    tracker = AutomatedPerformanceTracker()
    
    if args.run_now:
        # Run immediately
        tracker.run_async_task()
    elif args.schedule:
        # Run on schedule
        tracker.run_continuous()
    else:
        # Default: run once if market day
        if tracker.is_market_day():
            tracker.run_async_task()
        else:
            print("Not a market day. Use --run-now to force execution.")

if __name__ == "__main__":
    main()