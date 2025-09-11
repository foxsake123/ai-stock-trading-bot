"""
Pre-Market Daily Research Report Generator
Runs at 8:30 AM ET before market open
Analyzes overnight news, futures, and generates trading signals
"""

import json
from datetime import datetime, time
import yfinance as yf
from pathlib import Path
import sys
sys.path.append('../Multi-Agent_System')
sys.path.append('../Bot_Strategies')
sys.path.append('../Configuration')

class PreMarketReport:
    """Generate comprehensive pre-market analysis report"""
    
    def __init__(self):
        self.report_time = datetime.now()
        self.report_data = {
            'report_type': 'PRE_MARKET_DAILY',
            'timestamp': self.report_time.isoformat(),
            'market_date': self.report_time.strftime('%Y-%m-%d')
        }
        
    def analyze_futures(self):
        """Analyze futures markets for market direction"""
        futures_symbols = {
            'ES=F': 'S&P 500 Futures',
            'NQ=F': 'Nasdaq Futures',
            'YM=F': 'Dow Futures',
            'RTY=F': 'Russell 2000 Futures',
            'GC=F': 'Gold Futures',
            'CL=F': 'Crude Oil Futures',
            '^VIX': 'Volatility Index',
            'DX-Y.NYB': 'US Dollar Index'
        }
        
        futures_data = {}
        for symbol, name in futures_symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                history = ticker.history(period='2d')
                
                if not history.empty:
                    current = history['Close'].iloc[-1]
                    previous = history['Close'].iloc[-2] if len(history) > 1 else current
                    change_pct = ((current - previous) / previous) * 100
                    
                    futures_data[symbol] = {
                        'name': name,
                        'current': round(current, 2),
                        'change_pct': round(change_pct, 2),
                        'signal': self._interpret_futures_signal(symbol, change_pct)
                    }
            except:
                continue
                
        self.report_data['futures_analysis'] = futures_data
        return futures_data
    
    def _interpret_futures_signal(self, symbol, change_pct):
        """Interpret futures movement into trading signal"""
        if symbol in ['ES=F', 'NQ=F', 'YM=F']:
            if change_pct > 0.5:
                return 'BULLISH'
            elif change_pct < -0.5:
                return 'BEARISH'
            else:
                return 'NEUTRAL'
        elif symbol == '^VIX':
            if change_pct > 5:
                return 'RISK_OFF'
            elif change_pct < -5:
                return 'RISK_ON'
            else:
                return 'NEUTRAL'
        return 'NEUTRAL'
    
    def analyze_overnight_movers(self):
        """Identify significant overnight movers in S&P 100"""
        from sp100_universe import get_sp100_tickers
        
        movers = {
            'gainers': [],
            'losers': [],
            'volume_surges': []
        }
        
        # Check top S&P 100 stocks for overnight moves
        tickers = get_sp100_tickers()[:30]  # Check top 30 for efficiency
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                history = stock.history(period='2d', prepost=True)
                
                if not history.empty:
                    # Calculate overnight change
                    yesterday_close = history['Close'].iloc[-2] if len(history) > 1 else 0
                    current = history['Close'].iloc[-1]
                    change_pct = ((current - yesterday_close) / yesterday_close * 100) if yesterday_close else 0
                    
                    move_data = {
                        'ticker': ticker,
                        'price': round(current, 2),
                        'change_pct': round(change_pct, 2)
                    }
                    
                    if change_pct > 2:
                        movers['gainers'].append(move_data)
                    elif change_pct < -2:
                        movers['losers'].append(move_data)
                        
            except:
                continue
        
        # Sort by magnitude of move
        movers['gainers'].sort(key=lambda x: x['change_pct'], reverse=True)
        movers['losers'].sort(key=lambda x: x['change_pct'])
        
        self.report_data['overnight_movers'] = movers
        return movers
    
    def generate_trading_signals(self):
        """Generate trading signals for the day"""
        signals = {
            'strong_buy': [],
            'buy': [],
            'hold': [],
            'sell': [],
            'strong_sell': []
        }
        
        # Market sentiment based on futures
        futures = self.report_data.get('futures_analysis', {})
        sp_futures = futures.get('ES=F', {})
        vix = futures.get('^VIX', {})
        
        market_bias = 'NEUTRAL'
        if sp_futures.get('change_pct', 0) > 0.5 and vix.get('change_pct', 0) < 0:
            market_bias = 'BULLISH'
        elif sp_futures.get('change_pct', 0) < -0.5 and vix.get('change_pct', 0) > 5:
            market_bias = 'BEARISH'
        
        # Generate signals based on market bias and movers
        movers = self.report_data.get('overnight_movers', {})
        
        if market_bias == 'BULLISH':
            # In bullish market, focus on strong gainers
            for gainer in movers.get('gainers', [])[:5]:
                if gainer['change_pct'] > 3:
                    signals['strong_buy'].append({
                        'ticker': gainer['ticker'],
                        'reason': f"Strong overnight gain {gainer['change_pct']}% with bullish market"
                    })
                else:
                    signals['buy'].append({
                        'ticker': gainer['ticker'],
                        'reason': f"Positive momentum {gainer['change_pct']}%"
                    })
        
        elif market_bias == 'BEARISH':
            # In bearish market, consider shorts or defensive positions
            for loser in movers.get('losers', [])[:5]:
                if loser['change_pct'] < -3:
                    signals['strong_sell'].append({
                        'ticker': loser['ticker'],
                        'reason': f"Significant overnight loss {loser['change_pct']}% with bearish market"
                    })
        
        self.report_data['trading_signals'] = signals
        self.report_data['market_bias'] = market_bias
        return signals
    
    def analyze_economic_calendar(self):
        """Check for important economic events today"""
        # This would normally connect to an economic calendar API
        events = [
            {'time': '8:30 AM', 'event': 'Initial Jobless Claims', 'importance': 'HIGH'},
            {'time': '10:00 AM', 'event': 'Consumer Confidence', 'importance': 'MEDIUM'},
            {'time': '2:00 PM', 'event': 'FOMC Minutes', 'importance': 'HIGH'}
        ]
        
        self.report_data['economic_events'] = events
        return events
    
    def generate_report(self):
        """Generate complete pre-market report"""
        print("\n" + "="*70)
        print("PRE-MARKET DAILY RESEARCH REPORT")
        print(f"Date: {self.report_data['market_date']}")
        print(f"Time: {datetime.now().strftime('%I:%M %p ET')}")
        print("="*70)
        
        # Analyze all components
        self.analyze_futures()
        self.analyze_overnight_movers()
        self.generate_trading_signals()
        self.analyze_economic_calendar()
        
        # Display futures
        print("\n[FUTURES ANALYSIS]")
        for symbol, data in self.report_data['futures_analysis'].items():
            arrow = "↑" if data['change_pct'] > 0 else "↓"
            print(f"  {data['name']}: {data['current']} ({arrow}{abs(data['change_pct'])}%) - {data['signal']}")
        
        # Display market bias
        print(f"\n[MARKET BIAS]: {self.report_data['market_bias']}")
        
        # Display overnight movers
        print("\n[OVERNIGHT MOVERS]")
        print("  Top Gainers:")
        for gainer in self.report_data['overnight_movers']['gainers'][:3]:
            print(f"    {gainer['ticker']}: +{gainer['change_pct']}%")
        print("  Top Losers:")
        for loser in self.report_data['overnight_movers']['losers'][:3]:
            print(f"    {loser['ticker']}: {loser['change_pct']}%")
        
        # Display trading signals
        print("\n[TRADING SIGNALS]")
        signals = self.report_data['trading_signals']
        if signals['strong_buy']:
            print("  STRONG BUY:")
            for sig in signals['strong_buy']:
                print(f"    • {sig['ticker']}: {sig['reason']}")
        if signals['buy']:
            print("  BUY:")
            for sig in signals['buy']:
                print(f"    • {sig['ticker']}: {sig['reason']}")
        
        # Display economic events
        print("\n[ECONOMIC CALENDAR]")
        for event in self.report_data['economic_events']:
            print(f"  {event['time']}: {event['event']} ({event['importance']})")
        
        # Save report
        self.save_report()
        
        return self.report_data
    
    def save_report(self):
        """Save report to file"""
        # Create directory for today if it doesn't exist
        date_str = self.report_data['market_date']
        report_dir = Path(f"pre_market_daily/{date_str}")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON version
        json_file = report_dir / f"pre_market_{date_str}.json"
        with open(json_file, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        
        print(f"\n[SAVED] Report saved to {json_file}")
        return json_file

if __name__ == "__main__":
    report = PreMarketReport()
    report.generate_report()