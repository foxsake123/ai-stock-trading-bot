"""
Risk Monitoring & Alert System
Monitor positions against risk limits and send alerts
"""

import alpaca_trade_api as tradeapi
from datetime import datetime
import json

# Bot credentials
DEE_BOT_API = "PK6FZK4DAQVTD7DYVH78"
DEE_BOT_SECRET = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"

SHORGAN_API = "PKJRLSB2MFEJUSK6UK2E" 
SHORGAN_SECRET = "QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic"

BASE_URL = "https://paper-api.alpaca.markets"

# Risk limits
RISK_LIMITS = {
    'DEE-BOT': {
        'daily_loss_limit': -750,
        'position_risk_limit': -500,
        'portfolio_risk_pct': -5.0
    },
    'SHORGAN-BOT': {
        'daily_loss_limit': -3000,
        'position_risk_limit': -1000,
        'portfolio_risk_pct': -8.0
    }
}

class RiskMonitor:
    def __init__(self):
        self.alerts = []
        self.connect_apis()
    
    def connect_apis(self):
        """Connect to both accounts"""
        try:
            self.dee_api = tradeapi.REST(DEE_BOT_API, DEE_BOT_SECRET, BASE_URL, api_version='v2')
            self.shorgan_api = tradeapi.REST(SHORGAN_API, SHORGAN_SECRET, BASE_URL, api_version='v2')
        except Exception as e:
            print(f"[ERROR] Connection failed: {str(e)}")
    
    def add_alert(self, level, bot, message, position=None):
        """Add alert to list"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'level': level,  # INFO, WARNING, CRITICAL
            'bot': bot,
            'message': message,
            'position': position
        }
        self.alerts.append(alert)
        
        # Print alert immediately
        level_symbol = {'INFO': '[INFO]', 'WARNING': '[WARN]', 'CRITICAL': '[CRIT]'}
        print(f"{level_symbol[level]} {bot}: {message}")
    
    def check_position_risk(self, bot_name, positions, limits):
        """Check individual position risks"""
        for pos in positions:
            pnl = float(pos.unrealized_pl)
            pnl_pct = float(pos.unrealized_plpc) * 100
            
            # Check if position loss exceeds limit
            if pnl < limits['position_risk_limit']:
                self.add_alert('WARNING', bot_name, 
                    f"{pos.symbol} position loss ${pnl:.2f} exceeds limit ${limits['position_risk_limit']}",
                    pos.symbol)
            
            # Check for extreme losses
            if pnl_pct < -10:
                self.add_alert('WARNING', bot_name,
                    f"{pos.symbol} down {pnl_pct:.1f}% - monitor closely", pos.symbol)
            
            # Check for extreme gains (might need taking profits)
            if pnl_pct > 30:
                self.add_alert('INFO', bot_name,
                    f"{pos.symbol} up {pnl_pct:.1f}% - consider taking profits", pos.symbol)
    
    def check_portfolio_risk(self, bot_name, account, total_pnl, limits):
        """Check portfolio-level risks"""
        portfolio_value = float(account.portfolio_value)
        pnl_pct = (total_pnl / portfolio_value) * 100
        
        # Daily loss limit
        if total_pnl < limits['daily_loss_limit']:
            self.add_alert('CRITICAL', bot_name,
                f"Daily P&L ${total_pnl:.2f} exceeds limit ${limits['daily_loss_limit']} - HALT TRADING")
        
        # Portfolio percentage risk
        if pnl_pct < limits['portfolio_risk_pct']:
            self.add_alert('CRITICAL', bot_name,
                f"Portfolio down {pnl_pct:.1f}% exceeds {limits['portfolio_risk_pct']}% limit")
        
        # Buying power alerts
        buying_power = float(account.buying_power)
        if buying_power < 1000:
            self.add_alert('WARNING', bot_name,
                f"Low buying power: ${buying_power:.2f}")
    
    def check_bot_risk(self, api, bot_name):
        """Comprehensive risk check for one bot"""
        try:
            account = api.get_account()
            positions = api.list_positions()
            
            # Calculate total P&L
            total_pnl = sum(float(pos.unrealized_pl) for pos in positions)
            
            limits = RISK_LIMITS[bot_name]
            
            # Check position-level risks
            if positions:
                self.check_position_risk(bot_name, positions, limits)
            
            # Check portfolio-level risks
            self.check_portfolio_risk(bot_name, account, total_pnl, limits)
            
            # Success info
            if total_pnl > 0:
                self.add_alert('INFO', bot_name, f"Portfolio profitable: +${total_pnl:.2f}")
            
            return {
                'bot': bot_name,
                'portfolio_value': float(account.portfolio_value),
                'total_pnl': total_pnl,
                'position_count': len(positions),
                'risk_status': 'OK' if total_pnl > limits['daily_loss_limit'] else 'AT_RISK'
            }
            
        except Exception as e:
            self.add_alert('CRITICAL', bot_name, f"Risk check failed: {str(e)}")
            return None
    
    def run_risk_check(self):
        """Run comprehensive risk check"""
        print("RISK MONITORING SYSTEM")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        self.alerts = []  # Reset alerts
        
        # Check both bots
        dee_status = self.check_bot_risk(self.dee_api, 'DEE-BOT')
        shorgan_status = self.check_bot_risk(self.shorgan_api, 'SHORGAN-BOT')
        
        # Overall risk summary
        print(f"\n{'='*60}")
        print("RISK SUMMARY")
        print(f"{'='*60}")
        
        if dee_status:
            print(f"DEE-BOT Status: {dee_status['risk_status']}")
            print(f"  Portfolio: ${dee_status['portfolio_value']:,.2f}")
            print(f"  P&L: ${dee_status['total_pnl']:,.2f}")
            print(f"  Positions: {dee_status['position_count']}")
        
        if shorgan_status:
            print(f"SHORGAN-BOT Status: {shorgan_status['risk_status']}")
            print(f"  Portfolio: ${shorgan_status['portfolio_value']:,.2f}")
            print(f"  P&L: ${shorgan_status['total_pnl']:,.2f}")
            print(f"  Positions: {shorgan_status['position_count']}")
        
        # Alert summary
        alert_counts = {'INFO': 0, 'WARNING': 0, 'CRITICAL': 0}
        for alert in self.alerts:
            alert_counts[alert['level']] += 1
        
        print(f"\nAlert Summary:")
        print(f"  INFO: {alert_counts['INFO']}")
        print(f"  WARNING: {alert_counts['WARNING']}")
        print(f"  CRITICAL: {alert_counts['CRITICAL']}")
        
        # Save alerts
        if self.alerts:
            alert_file = f"risk_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(alert_file, 'w') as f:
                json.dump(self.alerts, f, indent=2)
            print(f"\nAlerts saved to: {alert_file}")
        
        return self.alerts

if __name__ == "__main__":
    monitor = RiskMonitor()
    alerts = monitor.run_risk_check()