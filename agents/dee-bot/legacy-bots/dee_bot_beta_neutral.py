"""
DEE-BOT Beta Neutral Strategy with 2X Leverage
Implements market-neutral positioning with leverage for enhanced returns
"""

import alpaca_trade_api as tradeapi
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
import json
from pathlib import Path
from typing import Dict, List, Tuple

# DEE-BOT Alpaca Credentials
API_KEY = "PK6FZK4DAQVTD7DYVH78"
SECRET_KEY = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"
BASE_URL = "https://paper-api.alpaca.markets"

# Strategy Configuration
LEVERAGE_MULTIPLIER = 2.0  # 2X leverage
BETA_NEUTRAL_THRESHOLD = 0.1  # Acceptable beta deviation from 0
MAX_POSITION_SIZE = 0.15  # Max 15% per position (pre-leverage)
PORTFOLIO_HEAT = 0.8  # Use 80% of buying power for positions
REBALANCE_THRESHOLD = 0.2  # Rebalance when beta deviates by 0.2

class BetaNeutralStrategy:
    """Implements beta neutral strategy with leverage"""
    
    def __init__(self, api):
        self.api = api
        self.portfolio_beta = 0.0
        self.positions = {}
        self.market_data = {}
        
    def calculate_beta(self, ticker: str, period: int = 252) -> float:
        """Calculate stock beta relative to SPY"""
        try:
            # Get historical data
            stock = yf.Ticker(ticker)
            spy = yf.Ticker("SPY")
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period)
            
            stock_data = stock.history(start=start_date, end=end_date)['Close']
            spy_data = spy.history(start=start_date, end=end_date)['Close']
            
            # Calculate returns
            stock_returns = stock_data.pct_change().dropna()
            spy_returns = spy_data.pct_change().dropna()
            
            # Calculate beta
            covariance = np.cov(stock_returns, spy_returns)[0][1]
            variance = np.var(spy_returns)
            beta = covariance / variance if variance != 0 else 1.0
            
            return round(beta, 3)
            
        except Exception as e:
            print(f"[WARNING] Could not calculate beta for {ticker}: {str(e)}")
            return 1.0  # Default to market beta
    
    def get_portfolio_beta(self) -> float:
        """Calculate weighted portfolio beta"""
        try:
            positions = self.api.list_positions()
            if not positions:
                return 0.0
                
            total_value = sum(float(p.market_value) for p in positions)
            if total_value == 0:
                return 0.0
                
            weighted_beta = 0.0
            for position in positions:
                weight = float(position.market_value) / total_value
                beta = self.calculate_beta(position.symbol)
                weighted_beta += weight * beta
                
            return round(weighted_beta, 3)
            
        except Exception as e:
            print(f"[ERROR] Could not calculate portfolio beta: {str(e)}")
            return 0.0
    
    def find_hedge_candidates(self, target_beta: float) -> List[Dict]:
        """Find stocks to achieve target beta"""
        candidates = []
        
        # High beta stocks for long positions
        high_beta_stocks = ['NVDA', 'AMD', 'TSLA', 'AMZN', 'META', 'GOOGL']
        
        # Low/negative beta stocks for hedging
        low_beta_stocks = ['XLU', 'VZ', 'T', 'PG', 'KO', 'JNJ', 'WMT']
        
        # Inverse ETFs for negative beta
        inverse_etfs = ['SH', 'PSQ', 'DOG', 'SDS', 'QID']
        
        all_tickers = high_beta_stocks + low_beta_stocks + inverse_etfs
        
        for ticker in all_tickers:
            beta = self.calculate_beta(ticker)
            candidates.append({
                'ticker': ticker,
                'beta': beta,
                'type': 'inverse' if ticker in inverse_etfs else 'stock'
            })
            
        # Sort by beta difference from target
        candidates.sort(key=lambda x: abs(x['beta'] - target_beta))
        
        return candidates
    
    def calculate_leverage_position_size(self, price: float, confidence: float, account_value: float) -> int:
        """Calculate position size with leverage"""
        # Base position size (before leverage)
        base_position_pct = min(MAX_POSITION_SIZE, confidence * 0.2)
        
        # Apply leverage
        leveraged_position_value = account_value * base_position_pct * LEVERAGE_MULTIPLIER
        
        # Calculate shares
        shares = int(leveraged_position_value / price)
        
        return shares
    
    def build_beta_neutral_portfolio(self, recommendations: List[Dict]) -> Dict:
        """Build a beta-neutral portfolio from recommendations"""
        account = self.api.get_account()
        buying_power = float(account.buying_power)
        portfolio_value = float(account.portfolio_value)
        
        # Calculate effective buying power with leverage
        effective_buying_power = buying_power * LEVERAGE_MULTIPLIER * PORTFOLIO_HEAT
        
        portfolio_plan = {
            'long_positions': [],
            'hedge_positions': [],
            'total_long_beta': 0.0,
            'total_hedge_beta': 0.0,
            'net_beta': 0.0,
            'leverage_used': 0.0
        }
        
        # Process long positions from recommendations
        long_allocation = effective_buying_power * 0.6  # 60% for longs
        hedge_allocation = effective_buying_power * 0.4  # 40% for hedges
        
        for rec in recommendations[:5]:  # Top 5 recommendations
            if rec['consensus_action'] != 'BUY':
                continue
                
            ticker = rec['ticker']
            beta = self.calculate_beta(ticker)
            
            # Get current price
            try:
                barset = self.api.get_latest_bar(ticker)
                price = barset.c
            except:
                continue
                
            # Calculate position size with leverage
            position_value = long_allocation * 0.2  # Equal weight top 5
            shares = int(position_value / price)
            
            if shares > 0:
                portfolio_plan['long_positions'].append({
                    'ticker': ticker,
                    'shares': shares,
                    'price': price,
                    'value': shares * price,
                    'beta': beta,
                    'weighted_beta': beta * (shares * price / effective_buying_power)
                })
                
                portfolio_plan['total_long_beta'] += beta * (shares * price / effective_buying_power)
        
        # Calculate required hedge beta
        target_hedge_beta = -portfolio_plan['total_long_beta']
        
        # Find hedge positions
        hedge_candidates = self.find_hedge_candidates(0)
        
        remaining_hedge_value = hedge_allocation
        for candidate in hedge_candidates:
            if remaining_hedge_value <= 0:
                break
                
            ticker = candidate['ticker']
            beta = candidate['beta']
            
            # Skip if beta doesn't help neutralize
            if portfolio_plan['net_beta'] > 0 and beta > 0:
                continue
            if portfolio_plan['net_beta'] < 0 and beta < 0:
                continue
                
            try:
                barset = self.api.get_latest_bar(ticker)
                price = barset.c
            except:
                continue
                
            # Calculate hedge size
            hedge_value = min(remaining_hedge_value, hedge_allocation * 0.3)
            shares = int(hedge_value / price)
            
            if shares > 0:
                portfolio_plan['hedge_positions'].append({
                    'ticker': ticker,
                    'shares': shares,
                    'price': price,
                    'value': shares * price,
                    'beta': beta,
                    'weighted_beta': beta * (shares * price / effective_buying_power)
                })
                
                portfolio_plan['total_hedge_beta'] += beta * (shares * price / effective_buying_power)
                remaining_hedge_value -= shares * price
        
        # Calculate net portfolio beta
        portfolio_plan['net_beta'] = portfolio_plan['total_long_beta'] + portfolio_plan['total_hedge_beta']
        portfolio_plan['leverage_used'] = LEVERAGE_MULTIPLIER
        
        return portfolio_plan
    
    def execute_portfolio(self, portfolio_plan: Dict) -> Dict:
        """Execute the beta-neutral portfolio trades"""
        execution_results = {
            'executed_trades': [],
            'failed_trades': [],
            'portfolio_beta': portfolio_plan['net_beta'],
            'leverage_used': portfolio_plan['leverage_used']
        }
        
        print("\n" + "=" * 80)
        print("EXECUTING BETA-NEUTRAL PORTFOLIO (2X LEVERAGE)")
        print("=" * 80)
        print(f"Target Portfolio Beta: {portfolio_plan['net_beta']:.3f}")
        print(f"Leverage Multiplier: {LEVERAGE_MULTIPLIER}x")
        
        # Execute long positions
        print("\n--- LONG POSITIONS ---")
        for position in portfolio_plan['long_positions']:
            print(f"\n{position['ticker']}:")
            print(f"  Beta: {position['beta']:.3f}")
            print(f"  Shares: {position['shares']}")
            print(f"  Value: ${position['value']:,.2f}")
            
            try:
                order = self.api.submit_order(
                    symbol=position['ticker'],
                    qty=position['shares'],
                    side='buy',
                    type='market',
                    time_in_force='day'
                )
                
                print(f"  [SUCCESS] Order placed - ID: {order.id}")
                
                # Set stop loss (tighter for leveraged positions)
                stop_price = position['price'] * 0.98  # 2% stop loss
                stop_order = self.api.submit_order(
                    symbol=position['ticker'],
                    qty=position['shares'],
                    side='sell',
                    type='stop',
                    stop_price=stop_price,
                    time_in_force='gtc'
                )
                
                execution_results['executed_trades'].append({
                    'ticker': position['ticker'],
                    'side': 'buy',
                    'shares': position['shares'],
                    'price': position['price'],
                    'beta': position['beta'],
                    'stop_loss': stop_price
                })
                
            except Exception as e:
                print(f"  [ERROR] Failed: {str(e)}")
                execution_results['failed_trades'].append({
                    'ticker': position['ticker'],
                    'error': str(e)
                })
        
        # Execute hedge positions
        print("\n--- HEDGE POSITIONS ---")
        for position in portfolio_plan['hedge_positions']:
            print(f"\n{position['ticker']}:")
            print(f"  Beta: {position['beta']:.3f}")
            print(f"  Shares: {position['shares']}")
            print(f"  Value: ${position['value']:,.2f}")
            
            try:
                order = self.api.submit_order(
                    symbol=position['ticker'],
                    qty=position['shares'],
                    side='buy',
                    type='market',
                    time_in_force='day'
                )
                
                print(f"  [SUCCESS] Order placed - ID: {order.id}")
                
                execution_results['executed_trades'].append({
                    'ticker': position['ticker'],
                    'side': 'buy',
                    'shares': position['shares'],
                    'price': position['price'],
                    'beta': position['beta'],
                    'type': 'hedge'
                })
                
            except Exception as e:
                print(f"  [ERROR] Failed: {str(e)}")
                execution_results['failed_trades'].append({
                    'ticker': position['ticker'],
                    'error': str(e)
                })
        
        return execution_results
    
    def monitor_and_rebalance(self) -> Dict:
        """Monitor portfolio beta and rebalance if needed"""
        current_beta = self.get_portfolio_beta()
        
        print(f"\nCurrent Portfolio Beta: {current_beta:.3f}")
        
        rebalance_needed = abs(current_beta) > BETA_NEUTRAL_THRESHOLD
        
        if rebalance_needed:
            print(f"[ALERT] Rebalancing needed - Beta deviation: {current_beta:.3f}")
            
            # Calculate rebalancing trades
            if current_beta > BETA_NEUTRAL_THRESHOLD:
                # Need more negative beta (hedges)
                print("Action: Increase hedge positions")
            elif current_beta < -BETA_NEUTRAL_THRESHOLD:
                # Need more positive beta
                print("Action: Reduce hedge positions or add long positions")
        else:
            print("[OK] Portfolio is beta neutral")
        
        return {
            'current_beta': current_beta,
            'rebalance_needed': rebalance_needed,
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Main execution function"""
    # Connect to Alpaca
    api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
    
    # Initialize strategy
    strategy = BetaNeutralStrategy(api)
    
    # Load recommendations
    rec_file = Path(f"C:/Users/shorg/ai-stock-trading-bot/02_data/research/reports/daily_recommendations/dee_bot_recommendations_{date.today()}.json")
    
    if not rec_file.exists():
        print("[ERROR] No recommendations file found for today")
        print("Please run generate_dee_bot_recommendations.py first")
        return
    
    with open(rec_file, 'r') as f:
        data = json.load(f)
    
    recommendations = data['top_recommendations']
    
    # Build beta-neutral portfolio
    portfolio_plan = strategy.build_beta_neutral_portfolio(recommendations)
    
    print("\n" + "=" * 80)
    print("PORTFOLIO PLAN SUMMARY")
    print("=" * 80)
    print(f"Long Positions: {len(portfolio_plan['long_positions'])}")
    print(f"Hedge Positions: {len(portfolio_plan['hedge_positions'])}")
    print(f"Total Long Beta: {portfolio_plan['total_long_beta']:.3f}")
    print(f"Total Hedge Beta: {portfolio_plan['total_hedge_beta']:.3f}")
    print(f"Net Portfolio Beta: {portfolio_plan['net_beta']:.3f}")
    print(f"Leverage Used: {portfolio_plan['leverage_used']}x")
    
    # Confirm execution
    response = input("\nExecute this portfolio? (yes/no): ")
    if response.lower() == 'yes':
        results = strategy.execute_portfolio(portfolio_plan)
        
        # Save execution log
        log_dir = Path("C:/Users/shorg/ai-stock-trading-bot/09_logs/trading")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"dee_bot_beta_neutral_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_data = {
            'date': str(date.today()),
            'timestamp': datetime.now().isoformat(),
            'strategy': 'Beta Neutral with 2X Leverage',
            'portfolio_plan': portfolio_plan,
            'execution_results': results
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"\nExecution log saved: {log_file}")
        
        # Monitor portfolio
        print("\n" + "=" * 80)
        print("PORTFOLIO MONITORING")
        print("=" * 80)
        monitoring = strategy.monitor_and_rebalance()
        print(f"Monitoring complete: Beta = {monitoring['current_beta']:.3f}")
    else:
        print("Execution cancelled")

if __name__ == "__main__":
    main()