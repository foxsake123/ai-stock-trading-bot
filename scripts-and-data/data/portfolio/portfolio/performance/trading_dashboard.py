"""
Real-Time Trading Dashboard
Monitor both bots with live P&L and performance metrics
"""

import alpaca_trade_api as tradeapi
import json
from datetime import datetime
import time
import os

# Bot credentials
DEE_BOT_API = "PK6FZK4DAQVTD7DYVH78"
DEE_BOT_SECRET = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"

SHORGAN_API = "PKJRLSB2MFEJUSK6UK2E" 
SHORGAN_SECRET = "QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic"

BASE_URL = "https://paper-api.alpaca.markets"

class TradingDashboard:
    def __init__(self):
        self.dee_api = None
        self.shorgan_api = None
        self.connect_apis()
    
    def connect_apis(self):
        """Connect to both Alpaca accounts"""
        try:
            self.dee_api = tradeapi.REST(DEE_BOT_API, DEE_BOT_SECRET, BASE_URL, api_version='v2')
            self.shorgan_api = tradeapi.REST(SHORGAN_API, SHORGAN_SECRET, BASE_URL, api_version='v2')
            print("[OK] Connected to both trading accounts")
        except Exception as e:
            print(f"[ERROR] Connection failed: {str(e)}")
    
    def clear_screen(self):
        """Clear screen for refresh"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_bot_data(self, api, bot_name):
        """Get comprehensive data for one bot"""
        try:
            account = api.get_account()
            positions = api.list_positions()
            orders = api.list_orders(status='all', limit=10)
            
            # Calculate metrics
            total_value = float(account.portfolio_value)
            buying_power = float(account.buying_power)
            
            position_data = []
            total_pnl = 0
            
            for pos in positions:
                pnl = float(pos.unrealized_pl)
                pnl_pct = float(pos.unrealized_plpc) * 100
                total_pnl += pnl
                
                position_data.append({
                    'symbol': pos.symbol,
                    'qty': int(pos.qty),
                    'side': 'LONG' if int(pos.qty) > 0 else 'SHORT',
                    'avg_price': float(pos.avg_entry_price),
                    'market_value': float(pos.market_value),
                    'pnl': pnl,
                    'pnl_pct': pnl_pct
                })
            
            # Sort by P&L (best first)
            position_data.sort(key=lambda x: x['pnl'], reverse=True)
            
            return {
                'bot_name': bot_name,
                'portfolio_value': total_value,
                'buying_power': buying_power,
                'total_pnl': total_pnl,
                'positions': position_data,
                'position_count': len(position_data),
                'pending_orders': len([o for o in orders if o.status in ['new', 'partially_filled']])
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to get {bot_name} data: {str(e)}")
            return None
    
    def display_bot_summary(self, data):
        """Display summary for one bot"""
        if not data:
            return
            
        bot = data['bot_name']
        print(f"\n{'='*60}")
        print(f"{bot} PERFORMANCE DASHBOARD")
        print(f"{'='*60}")
        
        # Portfolio overview
        print(f"Portfolio Value:  ${data['portfolio_value']:,.2f}")
        print(f"Buying Power:     ${data['buying_power']:,.2f}")
        print(f"Total P&L:        ${data['total_pnl']:,.2f}")
        print(f"Active Positions: {data['position_count']}")
        print(f"Pending Orders:   {data['pending_orders']}")
        
        # Position details
        if data['positions']:
            print(f"\n[POSITIONS - Sorted by P&L]")
            print(f"{'Symbol':<8} {'Side':<6} {'Qty':<8} {'Avg Price':<12} {'P&L':<12} {'%':<8}")
            print("-" * 60)
            
            for pos in data['positions']:
                pnl_color = "+" if pos['pnl'] >= 0 else ""
                print(f"{pos['symbol']:<8} {pos['side']:<6} {pos['qty']:<8} "
                      f"${pos['avg_price']:<11.2f} {pnl_color}${pos['pnl']:<11.2f} {pnl_color}{pos['pnl_pct']:<7.1f}%")
        
        return data['total_pnl']
    
    def display_combined_summary(self, dee_pnl, shorgan_pnl):
        """Display combined portfolio summary"""
        total_pnl = dee_pnl + shorgan_pnl
        
        print(f"\n{'='*60}")
        print("COMBINED PORTFOLIO SUMMARY")
        print(f"{'='*60}")
        print(f"DEE-BOT P&L:      ${dee_pnl:,.2f}")
        print(f"SHORGAN-BOT P&L:  ${shorgan_pnl:,.2f}")
        print(f"TOTAL P&L:        ${total_pnl:,.2f}")
        
        if total_pnl >= 0:
            print(f"Status: PROFITABLE (+${total_pnl:.2f})")
        else:
            print(f"Status: DOWN (${total_pnl:.2f})")
    
    def save_snapshot(self, dee_data, shorgan_data):
        """Save current state to file"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'dee_bot': dee_data,
            'shorgan_bot': shorgan_data,
            'combined_pnl': (dee_data['total_pnl'] if dee_data else 0) + 
                           (shorgan_data['total_pnl'] if shorgan_data else 0)
        }
        
        filename = f"trading_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        return filename
    
    def run_dashboard(self, refresh_seconds=30):
        """Run live dashboard with auto-refresh"""
        print("STARTING LIVE TRADING DASHBOARD")
        print(f"Auto-refresh every {refresh_seconds} seconds")
        print("Press Ctrl+C to stop")
        print("="*60)
        
        while True:
            try:
                self.clear_screen()
                
                # Header
                print("LIVE TRADING DASHBOARD")
                print(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Get data from both bots
                dee_data = self.get_bot_data(self.dee_api, "DEE-BOT") if self.dee_api else None
                shorgan_data = self.get_bot_data(self.shorgan_api, "SHORGAN-BOT") if self.shorgan_api else None
                
                # Display bot summaries
                dee_pnl = 0
                shorgan_pnl = 0
                
                if dee_data:
                    dee_pnl = self.display_bot_summary(dee_data)
                
                if shorgan_data:
                    shorgan_pnl = self.display_bot_summary(shorgan_data)
                
                # Combined summary
                self.display_combined_summary(dee_pnl, shorgan_pnl)
                
                # Save snapshot
                snapshot_file = self.save_snapshot(dee_data, shorgan_data)
                print(f"\nSnapshot saved: {snapshot_file}")
                
                print(f"\nNext refresh in {refresh_seconds} seconds... (Ctrl+C to stop)")
                time.sleep(refresh_seconds)
                
            except KeyboardInterrupt:
                print("\n\nDashboard stopped by user")
                break
            except Exception as e:
                print(f"\n[ERROR] Dashboard error: {str(e)}")
                print("Retrying in 10 seconds...")
                time.sleep(10)

def run_single_update():
    """Run dashboard once without auto-refresh"""
    dashboard = TradingDashboard()
    
    if dashboard.dee_api and dashboard.shorgan_api:
        print("CURRENT TRADING STATUS")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get data
        dee_data = dashboard.get_bot_data(dashboard.dee_api, "DEE-BOT")
        shorgan_data = dashboard.get_bot_data(dashboard.shorgan_api, "SHORGAN-BOT")
        
        # Display
        dee_pnl = 0
        shorgan_pnl = 0
        
        if dee_data:
            dee_pnl = dashboard.display_bot_summary(dee_data)
        
        if shorgan_data:
            shorgan_pnl = dashboard.display_bot_summary(shorgan_data)
        
        # Combined
        dashboard.display_combined_summary(dee_pnl, shorgan_pnl)
        
        # Save
        snapshot_file = dashboard.save_snapshot(dee_data, shorgan_data)
        print(f"\nSnapshot saved: {snapshot_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        # Live dashboard with auto-refresh
        dashboard = TradingDashboard()
        dashboard.run_dashboard(30)  # Refresh every 30 seconds
    else:
        # Single update
        run_single_update()