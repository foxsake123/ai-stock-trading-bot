"""
Post-Market Daily Research Report Generator
Runs at 4:30 PM ET after market close
Analyzes day's performance, evaluates trades, and prepares for next day
"""

import json
from datetime import datetime, timedelta
import yfinance as yf
from pathlib import Path
import sys
sys.path.append('../Multi-Agent_System')
sys.path.append('../Bot_Strategies')
sys.path.append('../Configuration')
sys.path.append('../Performance_Tracking')

class PostMarketReport:
    """Generate comprehensive post-market analysis report"""
    
    def __init__(self):
        self.report_time = datetime.now()
        self.report_data = {
            'report_type': 'POST_MARKET_DAILY',
            'timestamp': self.report_time.isoformat(),
            'market_date': self.report_time.strftime('%Y-%m-%d')
        }
        
    def analyze_market_performance(self):
        """Analyze overall market performance for the day"""
        indices = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'Nasdaq',
            '^RUT': 'Russell 2000',
            '^VIX': 'VIX'
        }
        
        market_data = {}
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period='1d')
                
                if not history.empty:
                    open_price = history['Open'].iloc[0]
                    close_price = history['Close'].iloc[0]
                    high = history['High'].iloc[0]
                    low = history['Low'].iloc[0]
                    volume = history['Volume'].iloc[0]
                    
                    change = close_price - open_price
                    change_pct = (change / open_price) * 100
                    
                    market_data[symbol] = {
                        'name': name,
                        'open': round(open_price, 2),
                        'close': round(close_price, 2),
                        'high': round(high, 2),
                        'low': round(low, 2),
                        'change': round(change, 2),
                        'change_pct': round(change_pct, 2),
                        'volume': volume,
                        'trend': self._determine_trend(change_pct)
                    }
            except:
                continue
                
        self.report_data['market_performance'] = market_data
        return market_data
    
    def _determine_trend(self, change_pct):
        """Determine market trend based on percentage change"""
        if change_pct > 1:
            return 'STRONG_BULLISH'
        elif change_pct > 0.3:
            return 'BULLISH'
        elif change_pct > -0.3:
            return 'NEUTRAL'
        elif change_pct > -1:
            return 'BEARISH'
        else:
            return 'STRONG_BEARISH'
    
    def analyze_sector_performance(self):
        """Analyze sector performance for the day"""
        sectors = {
            'XLK': 'Technology',
            'XLF': 'Financials',
            'XLV': 'Healthcare',
            'XLE': 'Energy',
            'XLI': 'Industrials',
            'XLY': 'Consumer Discretionary',
            'XLP': 'Consumer Staples',
            'XLB': 'Materials',
            'XLRE': 'Real Estate',
            'XLU': 'Utilities'
        }
        
        sector_data = {}
        for symbol, name in sectors.items():
            try:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period='1d')
                
                if not history.empty:
                    change_pct = ((history['Close'].iloc[0] - history['Open'].iloc[0]) / 
                                 history['Open'].iloc[0]) * 100
                    
                    sector_data[name] = {
                        'symbol': symbol,
                        'change_pct': round(change_pct, 2),
                        'performance': 'OUTPERFORM' if change_pct > 0.5 else 'UNDERPERFORM' if change_pct < -0.5 else 'INLINE'
                    }
            except:
                continue
        
        # Sort by performance
        sorted_sectors = sorted(sector_data.items(), key=lambda x: x[1]['change_pct'], reverse=True)
        self.report_data['sector_performance'] = dict(sorted_sectors)
        return sector_data
    
    def analyze_portfolio_performance(self):
        """Analyze performance of today's trades"""
        # This would normally connect to the trading system to get actual trades
        # For now, we'll create a sample structure
        
        portfolio_performance = {
            'trades_executed': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0,
            'win_rate': 0,
            'best_trade': None,
            'worst_trade': None,
            'positions_held': []
        }
        
        # Check for today's trade files
        trade_files = Path('.').glob('*_ORDERS_*.json')
        for file in trade_files:
            try:
                with open(file, 'r') as f:
                    trade_data = json.load(f)
                    if trade_data.get('execution_time', '').startswith(self.report_data['market_date']):
                        portfolio_performance['trades_executed'] += len(trade_data.get('orders', []))
            except:
                continue
        
        self.report_data['portfolio_performance'] = portfolio_performance
        return portfolio_performance
    
    def identify_tomorrow_opportunities(self):
        """Identify potential opportunities for next trading day"""
        from sp100_universe import get_sp100_tickers
        
        opportunities = {
            'momentum_plays': [],
            'reversal_candidates': [],
            'breakout_watch': [],
            'earnings_plays': []
        }
        
        # Analyze top S&P 100 stocks for patterns
        tickers = get_sp100_tickers()[:50]  # Analyze top 50
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                history = stock.history(period='5d')
                
                if len(history) >= 5:
                    today_change = ((history['Close'].iloc[-1] - history['Open'].iloc[-1]) / 
                                  history['Open'].iloc[-1]) * 100
                    five_day_change = ((history['Close'].iloc[-1] - history['Close'].iloc[0]) / 
                                     history['Close'].iloc[0]) * 100
                    
                    # Momentum plays - strong consistent uptrend
                    if today_change > 1 and five_day_change > 3:
                        opportunities['momentum_plays'].append({
                            'ticker': ticker,
                            'today_change': round(today_change, 2),
                            '5d_change': round(five_day_change, 2),
                            'signal': 'CONTINUATION'
                        })
                    
                    # Reversal candidates - oversold bounce
                    elif today_change > 1 and five_day_change < -5:
                        opportunities['reversal_candidates'].append({
                            'ticker': ticker,
                            'today_change': round(today_change, 2),
                            '5d_change': round(five_day_change, 2),
                            'signal': 'REVERSAL'
                        })
                    
                    # Breakout watch - testing resistance
                    elif today_change > 0.5 and history['High'].iloc[-1] == history['High'].max():
                        opportunities['breakout_watch'].append({
                            'ticker': ticker,
                            'today_change': round(today_change, 2),
                            'high': round(history['High'].iloc[-1], 2),
                            'signal': 'BREAKOUT_PENDING'
                        })
                        
            except:
                continue
        
        # Limit to top 5 in each category
        for key in opportunities:
            opportunities[key] = opportunities[key][:5]
        
        self.report_data['tomorrow_opportunities'] = opportunities
        return opportunities
    
    def generate_trading_plan(self):
        """Generate trading plan for next session"""
        market_perf = self.report_data.get('market_performance', {})
        sp500 = market_perf.get('^GSPC', {})
        vix = market_perf.get('^VIX', {})
        
        # Determine market regime
        market_regime = 'NEUTRAL'
        if sp500.get('trend') in ['BULLISH', 'STRONG_BULLISH'] and vix.get('change_pct', 0) < 0:
            market_regime = 'RISK_ON'
        elif sp500.get('trend') in ['BEARISH', 'STRONG_BEARISH'] and vix.get('change_pct', 0) > 10:
            market_regime = 'RISK_OFF'
        
        # Generate plan based on regime
        trading_plan = {
            'market_regime': market_regime,
            'position_sizing': 'NORMAL' if market_regime != 'RISK_OFF' else 'REDUCED',
            'focus_sectors': [],
            'avoid_sectors': [],
            'key_levels': {},
            'risk_management': {}
        }
        
        # Identify focus sectors
        sector_perf = self.report_data.get('sector_performance', {})
        for sector, data in sector_perf.items():
            if data['performance'] == 'OUTPERFORM':
                trading_plan['focus_sectors'].append(sector)
            elif data['performance'] == 'UNDERPERFORM':
                trading_plan['avoid_sectors'].append(sector)
        
        # Set key levels for S&P 500
        if sp500:
            trading_plan['key_levels'] = {
                'support': round(sp500['low'] * 0.995, 2),
                'resistance': round(sp500['high'] * 1.005, 2),
                'pivot': round((sp500['high'] + sp500['low'] + sp500['close']) / 3, 2)
            }
        
        # Risk management rules
        trading_plan['risk_management'] = {
            'max_position_size': '5%' if market_regime == 'RISK_ON' else '3%',
            'stop_loss': '2%' if market_regime != 'RISK_OFF' else '1.5%',
            'daily_loss_limit': '2%' if market_regime != 'RISK_OFF' else '1%'
        }
        
        self.report_data['tomorrow_trading_plan'] = trading_plan
        return trading_plan
    
    def generate_report(self):
        """Generate complete post-market report"""
        print("\n" + "="*70)
        print("POST-MARKET DAILY RESEARCH REPORT")
        print(f"Date: {self.report_data['market_date']}")
        print(f"Time: {datetime.now().strftime('%I:%M %p ET')}")
        print("="*70)
        
        # Analyze all components
        self.analyze_market_performance()
        self.analyze_sector_performance()
        self.analyze_portfolio_performance()
        self.identify_tomorrow_opportunities()
        self.generate_trading_plan()
        
        # Display market performance
        print("\n[MARKET PERFORMANCE]")
        for symbol, data in self.report_data['market_performance'].items():
            arrow = "↑" if data['change_pct'] > 0 else "↓"
            print(f"  {data['name']}: {data['close']} ({arrow}{abs(data['change_pct'])}%) - {data['trend']}")
        
        # Display sector performance
        print("\n[SECTOR PERFORMANCE]")
        for sector, data in list(self.report_data['sector_performance'].items())[:5]:
            arrow = "↑" if data['change_pct'] > 0 else "↓"
            print(f"  {sector}: {arrow}{abs(data['change_pct'])}% - {data['performance']}")
        
        # Display portfolio performance
        portfolio = self.report_data['portfolio_performance']
        print("\n[PORTFOLIO PERFORMANCE]")
        print(f"  Trades Executed: {portfolio['trades_executed']}")
        print(f"  Win Rate: {portfolio['win_rate']}%")
        print(f"  Total P&L: ${portfolio['total_pnl']}")
        
        # Display tomorrow's opportunities
        print("\n[TOMORROW'S OPPORTUNITIES]")
        opps = self.report_data['tomorrow_opportunities']
        if opps['momentum_plays']:
            print("  Momentum Plays:")
            for opp in opps['momentum_plays'][:3]:
                print(f"    • {opp['ticker']}: {opp['signal']} (5d: {opp['5d_change']}%)")
        if opps['reversal_candidates']:
            print("  Reversal Candidates:")
            for opp in opps['reversal_candidates'][:3]:
                print(f"    • {opp['ticker']}: {opp['signal']} (Today: +{opp['today_change']}%)")
        
        # Display trading plan
        plan = self.report_data['tomorrow_trading_plan']
        print("\n[TOMORROW'S TRADING PLAN]")
        print(f"  Market Regime: {plan['market_regime']}")
        print(f"  Position Sizing: {plan['position_sizing']}")
        print(f"  Focus Sectors: {', '.join(plan['focus_sectors'][:3]) if plan['focus_sectors'] else 'None'}")
        print(f"  Key S&P Levels: Support {plan['key_levels'].get('support', 'N/A')}, Resistance {plan['key_levels'].get('resistance', 'N/A')}")
        
        # Save report
        self.save_report()
        
        return self.report_data
    
    def save_report(self):
        """Save report to file"""
        # Create directory for today if it doesn't exist
        date_str = self.report_data['market_date']
        report_dir = Path(f"post_market_daily/{date_str}")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON version
        json_file = report_dir / f"post_market_{date_str}.json"
        with open(json_file, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        
        print(f"\n[SAVED] Report saved to {json_file}")
        return json_file

if __name__ == "__main__":
    report = PostMarketReport()
    report.generate_report()