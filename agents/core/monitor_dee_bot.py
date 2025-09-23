"""
DEE-BOT Real-Time Monitoring Dashboard
Monitors beta-neutral positions and risk metrics
"""

import alpaca_trade_api as tradeapi
import json
from datetime import datetime, date
from pathlib import Path
import time
import sys

# DEE-BOT Alpaca Credentials
API_KEY = "PK6FZK4DAQVTD7DYVH78"
SECRET_KEY = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"
BASE_URL = "https://paper-api.alpaca.markets"

class DashboardMonitor:
    """Real-time monitoring for DEE-BOT positions"""
    
    def __init__(self, api):
        self.api = api
        self.initial_values = {}
        self.alerts = []
        
    def get_account_summary(self):
        """Get current account status"""
        try:
            account = self.api.get_account()
            
            return {
                'equity': float(account.equity),
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value),
                'cash': float(account.cash),
                'market_value': float(account.long_market_value) if hasattr(account, 'long_market_value') else 0,
                'status': account.status
            }
        except Exception as e:
            print(f"[ERROR] Failed to get account: {str(e)}")
            return None
    
    def get_positions_summary(self):
        """Get current positions with P&L"""
        try:
            positions = self.api.list_positions()
            
            if not positions:
                return {
                    'count': 0,
                    'total_value': 0,
                    'total_pnl': 0,
                    'positions': []
                }
            
            position_data = []
            total_value = 0
            total_pnl = 0
            
            for pos in positions:
                value = float(pos.market_value)
                pnl = float(pos.unrealized_pl)
                pnl_pct = float(pos.unrealized_plpc) * 100
                
                total_value += value
                total_pnl += pnl
                
                position_data.append({
                    'symbol': pos.symbol,
                    'qty': int(pos.qty),
                    'side': pos.side,
                    'market_value': value,
                    'avg_entry': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price) if hasattr(pos, 'current_price') else 0,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct
                })
            
            return {
                'count': len(positions),
                'total_value': total_value,
                'total_pnl': total_pnl,
                'total_pnl_pct': (total_pnl / total_value * 100) if total_value > 0 else 0,
                'positions': sorted(position_data, key=lambda x: abs(x['pnl']), reverse=True)
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to get positions: {str(e)}")
            return None
    
    def calculate_portfolio_beta(self):
        """Calculate current portfolio beta"""
        try:
            positions = self.api.list_positions()
            if not positions:
                return 0.0
            
            # Load beta values from today's recommendations
            rec_file = Path(f"C:/Users/shorg/ai-stock-trading-bot/02_data/research/reports/daily_recommendations/dee_bot_recommendations_{date.today()}.json")
            
            beta_map = {}
            if rec_file.exists():
                with open(rec_file, 'r') as f:
                    data = json.load(f)
                    for analysis in data.get('all_analyses', []):
                        beta_map[analysis['ticker']] = analysis.get('beta', 1.0)
            
            # Calculate weighted beta
            total_value = sum(float(p.market_value) for p in positions)
            if total_value == 0:
                return 0.0
            
            weighted_beta = 0.0
            for pos in positions:
                weight = float(pos.market_value) / total_value
                beta = beta_map.get(pos.symbol, 1.0)
                weighted_beta += weight * beta
            
            return round(weighted_beta, 3)
            
        except Exception as e:
            print(f"[ERROR] Failed to calculate beta: {str(e)}")
            return 0.0
    
    def check_risk_alerts(self, account_summary, positions_summary):
        """Check for risk conditions"""
        alerts = []
        
        # Check daily P&L
        if positions_summary and positions_summary['total_pnl_pct'] <= -3:
            alerts.append({
                'level': 'WARNING',
                'message': f"Daily loss exceeds 3%: {positions_summary['total_pnl_pct']:.2f}%"
            })
        
        if positions_summary and positions_summary['total_pnl_pct'] <= -5:
            alerts.append({
                'level': 'CRITICAL',
                'message': f"Daily loss exceeds 5%: {positions_summary['total_pnl_pct']:.2f}%"
            })
        
        # Check portfolio beta
        portfolio_beta = self.calculate_portfolio_beta()
        if abs(portfolio_beta) > 0.2:
            alerts.append({
                'level': 'WARNING',
                'message': f"Portfolio beta not neutral: {portfolio_beta:.3f}"
            })
        
        # Check margin utilization
        if account_summary:
            margin_util = 1 - (account_summary['buying_power'] / account_summary['equity'])
            if margin_util > 0.75:
                alerts.append({
                    'level': 'WARNING',
                    'message': f"High margin utilization: {margin_util:.1%}"
                })
        
        # Check individual position losses
        if positions_summary:
            for pos in positions_summary['positions']:
                if pos['pnl_pct'] <= -5:
                    alerts.append({
                        'level': 'WARNING',
                        'message': f"{pos['symbol']} down {pos['pnl_pct']:.1f}% - consider stop loss"
                    })
        
        return alerts
    
    def display_dashboard(self):
        """Display monitoring dashboard"""
        # Clear screen (platform specific)
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 80)
        print("DEE-BOT MONITORING DASHBOARD - BETA NEUTRAL (2X LEVERAGE)")
        print("=" * 80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Account Summary
        account = self.get_account_summary()
        if account:
            print("\n📊 ACCOUNT SUMMARY")
            print("-" * 40)
            print(f"Equity:          ${account['equity']:,.2f}")
            print(f"Portfolio Value: ${account['portfolio_value']:,.2f}")
            print(f"Buying Power:    ${account['buying_power']:,.2f}")
            print(f"Cash:            ${account['cash']:,.2f}")
            
            # Calculate leverage
            if account['equity'] > 0:
                leverage = account['market_value'] / account['equity']
                print(f"Current Leverage: {leverage:.2f}x")
        
        # Portfolio Beta
        portfolio_beta = self.calculate_portfolio_beta()
        print(f"\n🎯 PORTFOLIO BETA: {portfolio_beta:.3f}")
        if abs(portfolio_beta) <= 0.1:
            print("   Status: ✓ NEUTRAL")
        else:
            print("   Status: ⚠ NOT NEUTRAL")
        
        # Positions Summary
        positions = self.get_positions_summary()
        if positions and positions['count'] > 0:
            print("\n📈 POSITIONS SUMMARY")
            print("-" * 40)
            print(f"Open Positions:  {positions['count']}")
            print(f"Total Value:     ${positions['total_value']:,.2f}")
            print(f"Total P&L:       ${positions['total_pnl']:+,.2f} ({positions['total_pnl_pct']:+.2f}%)")
            
            print("\nTop Positions by P&L:")
            for i, pos in enumerate(positions['positions'][:5], 1):
                symbol = pos['symbol'].ljust(6)
                qty = str(pos['qty']).rjust(4)
                value = f"${pos['market_value']:,.0f}".rjust(10)
                pnl = f"${pos['pnl']:+,.0f}".rjust(10)
                pnl_pct = f"({pos['pnl_pct']:+.1f}%)".rjust(8)
                
                # Color coding for P&L
                if pos['pnl'] > 0:
                    indicator = "🟢"
                elif pos['pnl'] < -pos['market_value'] * 0.03:
                    indicator = "🔴"
                else:
                    indicator = "🟡"
                
                print(f"  {indicator} {symbol} x{qty} {value} {pnl} {pnl_pct}")
        else:
            print("\n📈 No open positions")
        
        # Risk Alerts
        alerts = self.check_risk_alerts(account, positions)
        if alerts:
            print("\n⚠️  RISK ALERTS")
            print("-" * 40)
            for alert in alerts:
                if alert['level'] == 'CRITICAL':
                    print(f"🔴 {alert['message']}")
                else:
                    print(f"🟡 {alert['message']}")
        else:
            print("\n✅ No risk alerts")
        
        # Orders
        try:
            open_orders = self.api.list_orders(status='open')
            if open_orders:
                print(f"\n📝 OPEN ORDERS: {len(open_orders)}")
                for order in open_orders[:3]:
                    print(f"  - {order.symbol}: {order.side} {order.qty} @ {order.order_type}")
        except:
            pass
        
        print("\n" + "=" * 80)
        print("Press Ctrl+C to exit | Updates every 30 seconds")
    
    def run(self, refresh_interval=30):
        """Run monitoring loop"""
        try:
            while True:
                self.display_dashboard()
                time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user")
            return

def main():
    """Main monitoring function"""
    # Connect to Alpaca
    try:
        api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
        
        # Test connection
        account = api.get_account()
        print(f"Connected to Alpaca - Account Status: {account.status}")
        
    except Exception as e:
        print(f"[ERROR] Failed to connect to Alpaca: {str(e)}")
        return
    
    # Initialize and run monitor
    monitor = DashboardMonitor(api)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--once':
            # Display once and exit
            monitor.display_dashboard()
            return
        elif sys.argv[1] == '--fast':
            # Fast refresh (10 seconds)
            monitor.run(refresh_interval=10)
        else:
            # Custom interval
            try:
                interval = int(sys.argv[1])
                monitor.run(refresh_interval=interval)
            except:
                monitor.run()
    else:
        # Default 30 second refresh
        monitor.run()

if __name__ == "__main__":
    main()