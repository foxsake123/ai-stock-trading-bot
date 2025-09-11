"""
Daily Performance Tracker
Tracks and reports actual trading performance for both bots
This is NOT research - this is live performance monitoring
"""

import json
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
from pathlib import Path
import pandas as pd
import os
import sys
sys.path.append('../Configuration')

class DailyPerformanceTracker:
    """Track daily performance metrics for both trading bots"""
    
    def __init__(self):
        self.date = datetime.now().strftime('%Y-%m-%d')
        self.timestamp = datetime.now().isoformat()
        
        # Bot credentials from .env
        self.dee_bot_api = {
            'key': os.getenv('ALPACA_API_KEY_DEE', 'PK6FZK4DAQVTD7DYVH78'),
            'secret': os.getenv('ALPACA_SECRET_KEY_DEE', 'JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt'),
            'base_url': 'https://paper-api.alpaca.markets'
        }
        
        self.shorgan_bot_api = {
            'key': os.getenv('ALPACA_API_KEY_SHORGAN', 'PKJRLSB2MFEJUSK6UK2E'),
            'secret': os.getenv('ALPACA_SECRET_KEY_SHORGAN', 'QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic'),
            'base_url': 'https://paper-api.alpaca.markets'
        }
        
        # Performance data structure
        self.performance_data = {
            'date': self.date,
            'timestamp': self.timestamp,
            'dee_bot': {},
            'shorgan_bot': {},
            'combined': {}
        }
    
    def connect_alpaca(self, credentials):
        """Connect to Alpaca API"""
        try:
            return tradeapi.REST(
                credentials['key'],
                credentials['secret'],
                credentials['base_url'],
                api_version='v2'
            )
        except Exception as e:
            print(f"[ERROR] Connection failed: {str(e)}")
            return None
    
    def track_bot_performance(self, bot_name, api_credentials):
        """Track performance for a specific bot"""
        api = self.connect_alpaca(api_credentials)
        if not api:
            return None
        
        performance = {
            'bot_name': bot_name,
            'timestamp': datetime.now().isoformat(),
            'account': {},
            'positions': [],
            'orders_today': [],
            'metrics': {}
        }
        
        try:
            # Get account information
            account = api.get_account()
            performance['account'] = {
                'portfolio_value': float(account.portfolio_value),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'equity': float(account.equity),
                'last_equity': float(account.last_equity),
                'long_market_value': float(account.long_market_value) if hasattr(account, 'long_market_value') else 0,
                'short_market_value': float(account.short_market_value) if hasattr(account, 'short_market_value') else 0,
                'initial_margin': float(account.initial_margin) if hasattr(account, 'initial_margin') else 0,
                'maintenance_margin': float(account.maintenance_margin) if hasattr(account, 'maintenance_margin') else 0,
                'daytrade_count': int(account.daytrade_count) if hasattr(account, 'daytrade_count') else 0
            }
            
            # Calculate daily P&L
            starting_capital = 100000  # Both bots start with $100K
            current_value = performance['account']['portfolio_value']
            daily_pnl = current_value - performance['account']['last_equity']
            total_pnl = current_value - starting_capital
            
            # Get positions
            positions = api.list_positions()
            for pos in positions:
                position_data = {
                    'symbol': pos.symbol,
                    'qty': int(pos.qty),
                    'side': pos.side,
                    'market_value': float(pos.market_value),
                    'cost_basis': float(pos.cost_basis),
                    'unrealized_pl': float(pos.unrealized_pl) if hasattr(pos, 'unrealized_pl') else 0,
                    'unrealized_plpc': float(pos.unrealized_plpc) * 100 if hasattr(pos, 'unrealized_plpc') else 0,
                    'avg_entry_price': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price) if hasattr(pos, 'current_price') else 0,
                    'lastday_price': float(pos.lastday_price) if hasattr(pos, 'lastday_price') else 0,
                    'change_today': float(pos.change_today) if hasattr(pos, 'change_today') else 0
                }
                performance['positions'].append(position_data)
            
            # Get today's orders
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            orders = api.list_orders(status='all', after=today_start.isoformat() + 'Z')
            for order in orders:
                order_data = {
                    'symbol': order.symbol,
                    'qty': int(order.qty) if order.qty else 0,
                    'filled_qty': int(order.filled_qty) if order.filled_qty else 0,
                    'side': order.side,
                    'type': order.order_type,
                    'status': order.status,
                    'submitted_at': order.submitted_at,
                    'filled_at': order.filled_at if hasattr(order, 'filled_at') else None,
                    'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else 0,
                    'limit_price': float(order.limit_price) if order.limit_price else 0
                }
                performance['orders_today'].append(order_data)
            
            # Calculate key metrics
            performance['metrics'] = {
                'starting_capital': starting_capital,
                'current_value': current_value,
                'daily_pnl': daily_pnl,
                'daily_pnl_pct': (daily_pnl / performance['account']['last_equity']) * 100 if performance['account']['last_equity'] else 0,
                'total_pnl': total_pnl,
                'total_return_pct': (total_pnl / starting_capital) * 100,
                'position_count': len(performance['positions']),
                'orders_today': len(performance['orders_today']),
                'win_rate': self.calculate_win_rate(performance['positions']),
                'largest_winner': self.find_largest_winner(performance['positions']),
                'largest_loser': self.find_largest_loser(performance['positions']),
                'cash_percentage': (performance['account']['cash'] / current_value) * 100 if current_value else 0,
                'invested_percentage': (performance['account']['long_market_value'] / current_value) * 100 if current_value else 0
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to track {bot_name}: {str(e)}")
            
        return performance
    
    def calculate_win_rate(self, positions):
        """Calculate win rate from positions"""
        if not positions:
            return 0
        winners = sum(1 for p in positions if p['unrealized_pl'] > 0)
        return (winners / len(positions)) * 100
    
    def find_largest_winner(self, positions):
        """Find largest winning position"""
        if not positions:
            return None
        winners = [p for p in positions if p['unrealized_pl'] > 0]
        if not winners:
            return None
        best = max(winners, key=lambda x: x['unrealized_pl'])
        return {
            'symbol': best['symbol'],
            'pnl': best['unrealized_pl'],
            'pnl_pct': best['unrealized_plpc']
        }
    
    def find_largest_loser(self, positions):
        """Find largest losing position"""
        if not positions:
            return None
        losers = [p for p in positions if p['unrealized_pl'] < 0]
        if not losers:
            return None
        worst = min(losers, key=lambda x: x['unrealized_pl'])
        return {
            'symbol': worst['symbol'],
            'pnl': worst['unrealized_pl'],
            'pnl_pct': worst['unrealized_plpc']
        }
    
    def track_all_performance(self):
        """Track performance for both bots"""
        print("\n" + "="*70)
        print("DAILY PERFORMANCE TRACKING")
        print(f"Date: {self.date}")
        print("="*70)
        
        # Track DEE-BOT
        print("\n[TRACKING] DEE-BOT Performance...")
        dee_performance = self.track_bot_performance('DEE-BOT', self.dee_bot_api)
        if dee_performance and 'metrics' in dee_performance:
            self.performance_data['dee_bot'] = dee_performance
            print(f"  Portfolio Value: ${dee_performance['metrics']['current_value']:,.2f}")
            print(f"  Daily P&L: ${dee_performance['metrics']['daily_pnl']:,.2f} ({dee_performance['metrics']['daily_pnl_pct']:.2f}%)")
            print(f"  Total Return: ${dee_performance['metrics']['total_pnl']:,.2f} ({dee_performance['metrics']['total_return_pct']:.2f}%)")
        
        # Track SHORGAN-BOT
        print("\n[TRACKING] SHORGAN-BOT Performance...")
        shorgan_performance = self.track_bot_performance('SHORGAN-BOT', self.shorgan_bot_api)
        if shorgan_performance and 'metrics' in shorgan_performance:
            self.performance_data['shorgan_bot'] = shorgan_performance
            print(f"  Portfolio Value: ${shorgan_performance['metrics']['current_value']:,.2f}")
            print(f"  Daily P&L: ${shorgan_performance['metrics']['daily_pnl']:,.2f} ({shorgan_performance['metrics']['daily_pnl_pct']:.2f}%)")
            print(f"  Total Return: ${shorgan_performance['metrics']['total_pnl']:,.2f} ({shorgan_performance['metrics']['total_return_pct']:.2f}%)")
        
        # Calculate combined metrics
        if dee_performance and 'metrics' in dee_performance and shorgan_performance and 'metrics' in shorgan_performance:
            self.performance_data['combined'] = {
                'total_value': dee_performance['metrics']['current_value'] + shorgan_performance['metrics']['current_value'],
                'total_daily_pnl': dee_performance['metrics']['daily_pnl'] + shorgan_performance['metrics']['daily_pnl'],
                'total_return': dee_performance['metrics']['total_pnl'] + shorgan_performance['metrics']['total_pnl'],
                'total_positions': dee_performance['metrics']['position_count'] + shorgan_performance['metrics']['position_count'],
                'total_orders_today': dee_performance['metrics']['orders_today'] + shorgan_performance['metrics']['orders_today']
            }
            
            print("\n" + "="*70)
            print("COMBINED PERFORMANCE")
            print("="*70)
            print(f"  Total Portfolio Value: ${self.performance_data['combined']['total_value']:,.2f}")
            print(f"  Combined Daily P&L: ${self.performance_data['combined']['total_daily_pnl']:,.2f}")
            print(f"  Total Return: ${self.performance_data['combined']['total_return']:,.2f}")
            print(f"  Active Positions: {self.performance_data['combined']['total_positions']}")
        
        # Save performance data
        self.save_performance_data()
        
        return self.performance_data
    
    def save_performance_data(self):
        """Save performance data to JSON file"""
        # Create directory structure
        save_dir = Path(f"daily_performance/{self.date}")
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Save detailed performance
        filename = save_dir / f"performance_{datetime.now().strftime('%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.performance_data, f, indent=2, default=str)
        
        print(f"\n[SAVED] Performance data: {filename}")
        
        # Update performance history
        self.update_performance_history()
        
        return filename
    
    def update_performance_history(self):
        """Update cumulative performance history"""
        history_file = Path("performance_history.json")
        
        # Load existing history or create new
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = {
                'start_date': self.date,
                'daily_records': []
            }
        
        # Add today's summary
        today_summary = {
            'date': self.date,
            'timestamp': self.timestamp,
            'dee_bot': {
                'value': self.performance_data['dee_bot']['metrics']['current_value'] if 'dee_bot' in self.performance_data else 100000,
                'daily_pnl': self.performance_data['dee_bot']['metrics']['daily_pnl'] if 'dee_bot' in self.performance_data else 0,
                'total_return': self.performance_data['dee_bot']['metrics']['total_return_pct'] if 'dee_bot' in self.performance_data else 0
            },
            'shorgan_bot': {
                'value': self.performance_data['shorgan_bot']['metrics']['current_value'] if 'shorgan_bot' in self.performance_data else 100000,
                'daily_pnl': self.performance_data['shorgan_bot']['metrics']['daily_pnl'] if 'shorgan_bot' in self.performance_data else 0,
                'total_return': self.performance_data['shorgan_bot']['metrics']['total_return_pct'] if 'shorgan_bot' in self.performance_data else 0
            },
            'combined': self.performance_data.get('combined', {})
        }
        
        # Append or update today's record
        existing_today = False
        for i, record in enumerate(history['daily_records']):
            if record['date'] == self.date:
                history['daily_records'][i] = today_summary
                existing_today = True
                break
        
        if not existing_today:
            history['daily_records'].append(today_summary)
        
        # Save updated history
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        print(f"[UPDATED] Performance history: {history_file}")

if __name__ == "__main__":
    tracker = DailyPerformanceTracker()
    tracker.track_all_performance()