"""
Weekly Analysis Report Generator
Runs every Friday after market close
Comprehensive weekly performance review and next week planning
"""

import json
from datetime import datetime, timedelta
import yfinance as yf
from pathlib import Path
import pandas as pd
import sys
sys.path.append('../Multi-Agent_System')
sys.path.append('../Bot_Strategies')
sys.path.append('../Configuration')

class WeeklyAnalysisReport:
    """Generate comprehensive weekly analysis report"""
    
    def __init__(self):
        self.report_time = datetime.now()
        self.week_end = self.report_time.strftime('%Y-%m-%d')
        self.week_start = (self.report_time - timedelta(days=4)).strftime('%Y-%m-%d')
        self.report_data = {
            'report_type': 'WEEKLY_ANALYSIS',
            'timestamp': self.report_time.isoformat(),
            'week_ending': self.week_end,
            'week_starting': self.week_start
        }
        
    def analyze_weekly_market_performance(self):
        """Analyze market performance for the entire week"""
        indices = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'Nasdaq',
            '^RUT': 'Russell 2000',
            '^VIX': 'VIX',
            'GLD': 'Gold',
            'TLT': 'Bonds',
            'DXY': 'Dollar Index'
        }
        
        weekly_performance = {}
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period='1wk')
                
                if not history.empty:
                    week_open = history['Open'].iloc[0]
                    week_close = history['Close'].iloc[-1]
                    week_high = history['High'].max()
                    week_low = history['Low'].min()
                    week_volume = history['Volume'].sum()
                    
                    change = week_close - week_open
                    change_pct = (change / week_open) * 100
                    
                    weekly_performance[symbol] = {
                        'name': name,
                        'week_open': round(week_open, 2),
                        'week_close': round(week_close, 2),
                        'week_high': round(week_high, 2),
                        'week_low': round(week_low, 2),
                        'week_change': round(change, 2),
                        'week_change_pct': round(change_pct, 2),
                        'total_volume': int(week_volume),
                        'trend': self._determine_weekly_trend(change_pct),
                        'volatility': round((week_high - week_low) / week_open * 100, 2)
                    }
            except:
                continue
                
        self.report_data['weekly_market_performance'] = weekly_performance
        return weekly_performance
    
    def _determine_weekly_trend(self, change_pct):
        """Determine weekly trend strength"""
        if change_pct > 3:
            return 'STRONG_UPTREND'
        elif change_pct > 1:
            return 'UPTREND'
        elif change_pct > -1:
            return 'SIDEWAYS'
        elif change_pct > -3:
            return 'DOWNTREND'
        else:
            return 'STRONG_DOWNTREND'
    
    def analyze_top_performers(self):
        """Identify top performing stocks of the week"""
        from sp100_universe import get_sp100_tickers
        
        performers = {
            'top_gainers': [],
            'top_losers': [],
            'most_volatile': [],
            'highest_volume': []
        }
        
        # Analyze S&P 100 stocks
        tickers = get_sp100_tickers()
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                history = stock.history(period='1wk')
                info = stock.info
                
                if not history.empty and len(history) >= 5:
                    week_open = history['Open'].iloc[0]
                    week_close = history['Close'].iloc[-1]
                    week_high = history['High'].max()
                    week_low = history['Low'].min()
                    avg_volume = history['Volume'].mean()
                    
                    change_pct = ((week_close - week_open) / week_open) * 100
                    volatility = ((week_high - week_low) / week_open) * 100
                    
                    stock_data = {
                        'ticker': ticker,
                        'name': info.get('longName', ticker),
                        'sector': info.get('sector', 'Unknown'),
                        'week_change_pct': round(change_pct, 2),
                        'volatility': round(volatility, 2),
                        'avg_volume': int(avg_volume),
                        'close': round(week_close, 2)
                    }
                    
                    # Categorize performance
                    if change_pct > 5:
                        performers['top_gainers'].append(stock_data)
                    elif change_pct < -5:
                        performers['top_losers'].append(stock_data)
                    
                    if volatility > 10:
                        performers['most_volatile'].append(stock_data)
                    
                    if avg_volume > 50_000_000:
                        performers['highest_volume'].append(stock_data)
                        
            except:
                continue
        
        # Sort and limit results
        performers['top_gainers'].sort(key=lambda x: x['week_change_pct'], reverse=True)
        performers['top_losers'].sort(key=lambda x: x['week_change_pct'])
        performers['most_volatile'].sort(key=lambda x: x['volatility'], reverse=True)
        performers['highest_volume'].sort(key=lambda x: x['avg_volume'], reverse=True)
        
        # Keep top 10 in each category
        for key in performers:
            performers[key] = performers[key][:10]
        
        self.report_data['top_performers'] = performers
        return performers
    
    def analyze_portfolio_weekly_performance(self):
        """Analyze portfolio performance for the week"""
        weekly_stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0,
            'win_rate': 0,
            'best_day': None,
            'worst_day': None,
            'total_invested': 0,
            'week_roi': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0
        }
        
        # Aggregate daily performance (would normally pull from database)
        daily_pnl = []
        for i in range(5):  # 5 trading days
            day_date = (self.report_time - timedelta(days=i)).strftime('%Y-%m-%d')
            # This would normally fetch actual P&L data
            daily_pnl.append({'date': day_date, 'pnl': 0})
        
        self.report_data['portfolio_weekly_performance'] = weekly_stats
        return weekly_stats
    
    def generate_next_week_outlook(self):
        """Generate outlook and strategy for next week"""
        outlook = {
            'market_outlook': '',
            'key_events': [],
            'earnings_calendar': [],
            'recommended_strategy': '',
            'sector_focus': [],
            'risk_factors': [],
            'target_positions': []
        }
        
        # Determine market outlook based on weekly performance
        market_perf = self.report_data.get('weekly_market_performance', {})
        sp500 = market_perf.get('^GSPC', {})
        vix = market_perf.get('^VIX', {})
        
        if sp500.get('trend') in ['UPTREND', 'STRONG_UPTREND'] and vix.get('week_change_pct', 0) < 0:
            outlook['market_outlook'] = 'BULLISH'
            outlook['recommended_strategy'] = 'AGGRESSIVE_LONG'
        elif sp500.get('trend') in ['DOWNTREND', 'STRONG_DOWNTREND']:
            outlook['market_outlook'] = 'BEARISH'
            outlook['recommended_strategy'] = 'DEFENSIVE'
        else:
            outlook['market_outlook'] = 'NEUTRAL'
            outlook['recommended_strategy'] = 'BALANCED'
        
        # Key events for next week (would normally pull from economic calendar)
        outlook['key_events'] = [
            {'date': 'Monday', 'event': 'Manufacturing PMI', 'importance': 'HIGH'},
            {'date': 'Wednesday', 'event': 'FOMC Minutes', 'importance': 'HIGH'},
            {'date': 'Friday', 'event': 'Non-Farm Payrolls', 'importance': 'CRITICAL'}
        ]
        
        # Sector recommendations based on weekly performance
        top_performers = self.report_data.get('top_performers', {})
        if top_performers.get('top_gainers'):
            sectors = {}
            for stock in top_performers['top_gainers']:
                sector = stock['sector']
                sectors[sector] = sectors.get(sector, 0) + 1
            
            # Get top 3 performing sectors
            sorted_sectors = sorted(sectors.items(), key=lambda x: x[1], reverse=True)
            outlook['sector_focus'] = [s[0] for s in sorted_sectors[:3]]
        
        # Risk factors
        if vix.get('week_change_pct', 0) > 20:
            outlook['risk_factors'].append('Elevated volatility')
        if sp500.get('volatility', 0) > 5:
            outlook['risk_factors'].append('High market uncertainty')
        
        self.report_data['next_week_outlook'] = outlook
        return outlook
    
    def generate_action_items(self):
        """Generate specific action items for next week"""
        action_items = {
            'portfolio_adjustments': [],
            'watchlist_additions': [],
            'risk_management_updates': [],
            'research_priorities': []
        }
        
        # Portfolio adjustments based on weekly analysis
        top_performers = self.report_data.get('top_performers', {})
        
        # Add top gainers with momentum to watchlist
        for gainer in top_performers.get('top_gainers', [])[:5]:
            action_items['watchlist_additions'].append({
                'ticker': gainer['ticker'],
                'reason': f"Strong weekly momentum +{gainer['week_change_pct']}%",
                'action': 'MONITOR_FOR_CONTINUATION'
            })
        
        # Review losers for potential reversals
        for loser in top_performers.get('top_losers', [])[:3]:
            action_items['research_priorities'].append({
                'ticker': loser['ticker'],
                'task': 'Analyze for oversold bounce opportunity',
                'priority': 'HIGH' if loser['week_change_pct'] < -10 else 'MEDIUM'
            })
        
        # Risk management updates
        market_perf = self.report_data.get('weekly_market_performance', {})
        vix = market_perf.get('^VIX', {})
        
        if vix.get('week_change_pct', 0) > 20:
            action_items['risk_management_updates'].append({
                'action': 'REDUCE_POSITION_SIZES',
                'reason': 'VIX increased significantly',
                'adjustment': 'Reduce max position to 3%'
            })
        
        self.report_data['action_items'] = action_items
        return action_items
    
    def generate_report(self):
        """Generate complete weekly analysis report"""
        print("\n" + "="*80)
        print("WEEKLY ANALYSIS REPORT")
        print(f"Week: {self.week_start} to {self.week_end}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
        print("="*80)
        
        # Generate all analyses
        self.analyze_weekly_market_performance()
        self.analyze_top_performers()
        self.analyze_portfolio_weekly_performance()
        self.generate_next_week_outlook()
        self.generate_action_items()
        
        # Display market performance
        print("\n[WEEKLY MARKET PERFORMANCE]")
        for symbol, data in list(self.report_data['weekly_market_performance'].items())[:5]:
            arrow = "↑" if data['week_change_pct'] > 0 else "↓"
            print(f"  {data['name']}: {arrow}{abs(data['week_change_pct'])}% - {data['trend']}")
            print(f"    Range: ${data['week_low']} - ${data['week_high']} (Vol: {data['volatility']}%)")
        
        # Display top performers
        print("\n[TOP WEEKLY PERFORMERS]")
        performers = self.report_data['top_performers']
        print("  Top Gainers:")
        for stock in performers['top_gainers'][:5]:
            print(f"    • {stock['ticker']}: +{stock['week_change_pct']}% ({stock['sector']})")
        print("  Top Losers:")
        for stock in performers['top_losers'][:5]:
            print(f"    • {stock['ticker']}: {stock['week_change_pct']}% ({stock['sector']})")
        
        # Display portfolio performance
        portfolio = self.report_data['portfolio_weekly_performance']
        print("\n[PORTFOLIO WEEKLY SUMMARY]")
        print(f"  Total Trades: {portfolio['total_trades']}")
        print(f"  Win Rate: {portfolio['win_rate']}%")
        print(f"  Week P&L: ${portfolio['total_pnl']}")
        print(f"  Week ROI: {portfolio['week_roi']}%")
        
        # Display next week outlook
        outlook = self.report_data['next_week_outlook']
        print("\n[NEXT WEEK OUTLOOK]")
        print(f"  Market Outlook: {outlook['market_outlook']}")
        print(f"  Recommended Strategy: {outlook['recommended_strategy']}")
        print(f"  Sector Focus: {', '.join(outlook['sector_focus']) if outlook['sector_focus'] else 'Diversified'}")
        print("  Key Events:")
        for event in outlook['key_events'][:3]:
            print(f"    • {event['date']}: {event['event']} ({event['importance']})")
        
        # Display action items
        actions = self.report_data['action_items']
        print("\n[ACTION ITEMS FOR NEXT WEEK]")
        print("  Watchlist Additions:")
        for item in actions['watchlist_additions'][:3]:
            print(f"    • {item['ticker']}: {item['reason']}")
        if actions['risk_management_updates']:
            print("  Risk Management Updates:")
            for update in actions['risk_management_updates']:
                print(f"    • {update['action']}: {update['reason']}")
        
        # Save report
        self.save_report()
        
        return self.report_data
    
    def save_report(self):
        """Save report to file"""
        # Create directory for this week
        report_dir = Path(f"weekly_analysis/{self.week_end}")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON version
        json_file = report_dir / f"weekly_report_{self.week_end}.json"
        with open(json_file, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        
        print(f"\n[SAVED] Report saved to {json_file}")
        return json_file

if __name__ == "__main__":
    report = WeeklyAnalysisReport()
    report.generate_report()