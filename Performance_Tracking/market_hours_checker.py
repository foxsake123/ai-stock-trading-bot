"""
Market Hours Checker
Determines if markets are open and best times to run reports
"""

from datetime import datetime, time, timedelta
import pytz
import holidays

class MarketHoursChecker:
    """Check market hours and trading days"""
    
    def __init__(self):
        self.eastern = pytz.timezone('US/Eastern')
        self.us_holidays = holidays.US(years=range(2024, 2027))
        
        # Standard market hours (ET)
        self.pre_market_start = time(4, 0)    # 4:00 AM
        self.market_open = time(9, 30)        # 9:30 AM
        self.market_close = time(16, 0)       # 4:00 PM
        self.after_hours_end = time(20, 0)    # 8:00 PM
        
        # Report timing
        self.pre_market_report_time = time(8, 30)   # 8:30 AM ET
        self.post_market_report_time = time(16, 15)  # 4:15 PM ET
        
    def get_current_et_time(self):
        """Get current Eastern Time"""
        return datetime.now(self.eastern)
    
    def is_trading_day(self, date=None):
        """Check if given date is a trading day"""
        if date is None:
            date = self.get_current_et_time().date()
        
        # Check if weekend
        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check if US market holiday
        if date in self.us_holidays:
            return False
            
        return True
    
    def get_market_status(self):
        """Get current market status"""
        now = self.get_current_et_time()
        current_time = now.time()
        
        if not self.is_trading_day(now.date()):
            return {
                'status': 'CLOSED',
                'reason': 'Weekend' if now.weekday() >= 5 else 'Holiday',
                'next_open': self.get_next_market_open()
            }
        
        if current_time < self.pre_market_start:
            return {
                'status': 'CLOSED',
                'reason': 'Before pre-market',
                'next_phase': 'Pre-market at 4:00 AM ET'
            }
        elif current_time < self.market_open:
            return {
                'status': 'PRE_MARKET',
                'next_phase': 'Market opens at 9:30 AM ET'
            }
        elif current_time < self.market_close:
            return {
                'status': 'OPEN',
                'closes_at': '4:00 PM ET'
            }
        elif current_time < self.after_hours_end:
            return {
                'status': 'AFTER_HOURS',
                'ends_at': '8:00 PM ET'
            }
        else:
            return {
                'status': 'CLOSED',
                'reason': 'After hours ended',
                'next_open': self.get_next_market_open()
            }
    
    def get_next_market_open(self):
        """Get next market open time"""
        now = self.get_current_et_time()
        next_day = now.date() + timedelta(days=1)
        
        # Find next trading day
        while not self.is_trading_day(next_day):
            next_day += timedelta(days=1)
        
        next_open = datetime.combine(next_day, self.market_open)
        next_open = self.eastern.localize(next_open)
        
        return next_open.strftime('%A, %B %d at 9:30 AM ET')
    
    def should_run_pre_market_report(self):
        """Check if it's time for pre-market report"""
        now = self.get_current_et_time()
        current_time = now.time()
        
        if not self.is_trading_day(now.date()):
            return False
        
        # Run between 8:30 AM and 9:25 AM ET
        return time(8, 30) <= current_time <= time(9, 25)
    
    def should_run_post_market_report(self):
        """Check if it's time for post-market report"""
        now = self.get_current_et_time()
        current_time = now.time()
        
        if not self.is_trading_day(now.date()):
            return False
        
        # Run between 4:15 PM and 5:00 PM ET
        return time(16, 15) <= current_time <= time(17, 0)
    
    def get_report_schedule(self):
        """Get today's report schedule"""
        now = self.get_current_et_time()
        
        if not self.is_trading_day(now.date()):
            return {
                'trading_day': False,
                'message': f"No reports today - {('Weekend' if now.weekday() >= 5 else 'Holiday')}"
            }
        
        return {
            'trading_day': True,
            'date': now.strftime('%Y-%m-%d'),
            'pre_market_report': '8:30 AM ET',
            'post_market_report': '4:15 PM ET',
            'current_time': now.strftime('%I:%M %p ET'),
            'market_status': self.get_market_status()
        }

def main():
    """Test market hours checker"""
    checker = MarketHoursChecker()
    
    print("="*60)
    print("MARKET HOURS CHECKER")
    print("="*60)
    
    # Current time
    et_time = checker.get_current_et_time()
    print(f"Current ET Time: {et_time.strftime('%Y-%m-%d %I:%M %p')}")
    print(f"Day of Week: {et_time.strftime('%A')}")
    print()
    
    # Trading day status
    is_trading = checker.is_trading_day()
    print(f"Is Trading Day: {'Yes' if is_trading else 'No'}")
    print()
    
    # Market status
    status = checker.get_market_status()
    print(f"Market Status: {status['status']}")
    for key, value in status.items():
        if key != 'status':
            print(f"  {key}: {value}")
    print()
    
    # Report schedule
    schedule = checker.get_report_schedule()
    print("Report Schedule:")
    for key, value in schedule.items():
        print(f"  {key}: {value}")
    print()
    
    # Check if reports should run
    print("Report Triggers:")
    print(f"  Should run pre-market report: {checker.should_run_pre_market_report()}")
    print(f"  Should run post-market report: {checker.should_run_post_market_report()}")

if __name__ == "__main__":
    main()