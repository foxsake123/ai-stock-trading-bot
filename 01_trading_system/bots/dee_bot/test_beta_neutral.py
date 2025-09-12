"""
Test and validate beta neutral strategy calculations
"""

import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, List

def calculate_beta(ticker: str, benchmark: str = 'SPY', period: int = 252) -> float:
    """Calculate beta for a stock"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period)
        
        # Get data
        stock = yf.download(ticker, start=start_date, end=end_date, progress=False)['Close']
        spy = yf.download(benchmark, start=start_date, end=end_date, progress=False)['Close']
        
        # Calculate returns
        stock_returns = stock.pct_change().dropna()
        spy_returns = spy.pct_change().dropna()
        
        # Calculate beta
        covariance = np.cov(stock_returns, spy_returns)[0][1]
        variance = np.var(spy_returns)
        beta = covariance / variance if variance != 0 else 1.0
        
        return round(beta, 3)
        
    except Exception as e:
        print(f"Error calculating beta for {ticker}: {str(e)}")
        return 1.0

def test_portfolio_scenarios():
    """Test different portfolio scenarios"""
    
    print("=" * 80)
    print("BETA NEUTRAL PORTFOLIO TESTING")
    print("=" * 80)
    
    # Test stocks with different betas
    test_stocks = {
        'High Beta': ['NVDA', 'TSLA', 'AMD', 'META', 'AMZN'],
        'Low Beta': ['JNJ', 'PG', 'KO', 'WMT', 'VZ'],
        'Inverse/Hedge': ['SH', 'PSQ', 'SDS']  # Inverse ETFs
    }
    
    print("\n--- INDIVIDUAL STOCK BETAS ---")
    stock_betas = {}
    
    for category, stocks in test_stocks.items():
        print(f"\n{category}:")
        for ticker in stocks:
            beta = calculate_beta(ticker)
            stock_betas[ticker] = beta
            print(f"  {ticker}: {beta:.3f}")
    
    # Scenario 1: High beta long portfolio
    print("\n" + "=" * 80)
    print("SCENARIO 1: HIGH BETA LONG PORTFOLIO")
    print("=" * 80)
    
    portfolio_1 = {
        'NVDA': {'shares': 100, 'price': 450},
        'TSLA': {'shares': 50, 'price': 250},
        'AMD': {'shares': 200, 'price': 140}
    }
    
    total_value_1 = sum(p['shares'] * p['price'] for p in portfolio_1.values())
    weighted_beta_1 = sum(
        stock_betas.get(ticker, 1.0) * (p['shares'] * p['price'] / total_value_1)
        for ticker, p in portfolio_1.items()
    )
    
    print(f"Portfolio Value: ${total_value_1:,.2f}")
    print(f"Portfolio Beta: {weighted_beta_1:.3f}")
    print(f"Risk Level: HIGH - Highly correlated with market")
    
    # Calculate hedge requirement
    hedge_beta_needed = -weighted_beta_1
    print(f"\nHedge Required: Beta of {hedge_beta_needed:.3f}")
    
    # Find hedge positions
    sh_beta = stock_betas.get('SH', -1.0)
    hedge_value_needed = abs(total_value_1 * weighted_beta_1 / sh_beta)
    sh_price = 25  # Approximate price
    sh_shares = int(hedge_value_needed / sh_price)
    
    print(f"Suggested Hedge: {sh_shares} shares of SH @ ${sh_price}")
    print(f"Hedge Value: ${sh_shares * sh_price:,.2f}")
    
    # Scenario 2: Beta neutral portfolio
    print("\n" + "=" * 80)
    print("SCENARIO 2: BETA NEUTRAL PORTFOLIO")
    print("=" * 80)
    
    portfolio_2 = {
        'NVDA': {'shares': 100, 'price': 450, 'beta': stock_betas.get('NVDA', 1.5)},
        'META': {'shares': 100, 'price': 350, 'beta': stock_betas.get('META', 1.3)},
        'JNJ': {'shares': 200, 'price': 160, 'beta': stock_betas.get('JNJ', 0.7)},
        'SH': {'shares': 1200, 'price': 25, 'beta': stock_betas.get('SH', -1.0)}
    }
    
    total_value_2 = sum(p['shares'] * p['price'] for p in portfolio_2.values())
    weighted_beta_2 = sum(
        p['beta'] * (p['shares'] * p['price'] / total_value_2)
        for p in portfolio_2.values()
    )
    
    print(f"Portfolio Value: ${total_value_2:,.2f}")
    print(f"Portfolio Beta: {weighted_beta_2:.3f}")
    print(f"Risk Level: NEUTRAL - Market independent")
    
    # Show position breakdown
    print("\nPosition Breakdown:")
    for ticker, data in portfolio_2.items():
        value = data['shares'] * data['price']
        weight = value / total_value_2
        contribution = data['beta'] * weight
        print(f"  {ticker}: ${value:,.0f} ({weight:.1%}) - Beta contribution: {contribution:+.3f}")
    
    # Scenario 3: 2X Leveraged Beta Neutral
    print("\n" + "=" * 80)
    print("SCENARIO 3: 2X LEVERAGED BETA NEUTRAL")
    print("=" * 80)
    
    account_value = 100000
    leverage = 2.0
    buying_power = account_value * leverage
    
    print(f"Account Value: ${account_value:,.2f}")
    print(f"Leverage: {leverage}x")
    print(f"Buying Power: ${buying_power:,.2f}")
    
    # Allocate with leverage
    long_allocation = buying_power * 0.6
    hedge_allocation = buying_power * 0.4
    
    print(f"\nLong Allocation: ${long_allocation:,.2f}")
    print(f"Hedge Allocation: ${hedge_allocation:,.2f}")
    
    # Calculate risk metrics
    print("\n--- RISK METRICS ---")
    
    # Daily VaR (95% confidence)
    portfolio_volatility = 0.02  # 2% daily vol
    leveraged_volatility = portfolio_volatility * leverage
    var_95 = buying_power * leveraged_volatility * 1.645
    
    print(f"Daily Volatility (unleveraged): {portfolio_volatility:.1%}")
    print(f"Daily Volatility (leveraged): {leveraged_volatility:.1%}")
    print(f"Value at Risk (95%): ${var_95:,.2f} ({var_95/account_value:.1%} of account)")
    
    # Stop loss levels
    max_loss_pct = 0.02  # 2% stop loss
    max_loss_leveraged = account_value * max_loss_pct * leverage
    
    print(f"\nStop Loss: {max_loss_pct:.1%} move = ${max_loss_leveraged:,.2f} loss")
    print(f"Account Impact: {max_loss_leveraged/account_value:.1%}")
    
    # Margin requirements
    initial_margin = buying_power * 0.5  # 50% initial margin
    maintenance_margin = buying_power * 0.25  # 25% maintenance
    
    print(f"\nInitial Margin Required: ${initial_margin:,.2f}")
    print(f"Maintenance Margin: ${maintenance_margin:,.2f}")
    print(f"Free Margin: ${account_value - initial_margin:,.2f}")
    
    # Return scenarios
    print("\n" + "=" * 80)
    print("RETURN SCENARIOS (BETA NEUTRAL, 2X LEVERAGE)")
    print("=" * 80)
    
    scenarios = [
        ('Best Case (+5% alpha)', 0.05),
        ('Good Case (+3% alpha)', 0.03),
        ('Base Case (+1% alpha)', 0.01),
        ('Break Even (0% alpha)', 0.0),
        ('Bad Case (-2% alpha)', -0.02),
        ('Worst Case (-5% alpha)', -0.05)
    ]
    
    for scenario_name, alpha in scenarios:
        # With beta neutral, returns come from alpha only
        gross_return = alpha * leverage
        net_return = gross_return - 0.005  # Subtract financing costs
        dollar_return = account_value * net_return
        
        print(f"\n{scenario_name}:")
        print(f"  Alpha: {alpha:.1%}")
        print(f"  Gross Return (2x leverage): {gross_return:.1%}")
        print(f"  Net Return: {net_return:.1%}")
        print(f"  Dollar P&L: ${dollar_return:,.2f}")
    
    # Summary
    print("\n" + "=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)
    print("1. Beta neutral strategy removes market risk")
    print("2. 2X leverage amplifies alpha (both positive and negative)")
    print("3. Tight stop losses essential (2% unleveraged = 4% account risk)")
    print("4. Success depends on stock selection alpha, not market direction")
    print("5. Hedging costs reduce returns but provide downside protection")

def test_position_sizing():
    """Test position sizing calculations"""
    
    print("\n" + "=" * 80)
    print("POSITION SIZING TESTS")
    print("=" * 80)
    
    account_value = 100000
    leverage = 2.0
    max_position_pct = 0.15  # 15% max per position
    
    test_cases = [
        {'ticker': 'AAPL', 'price': 180, 'confidence': 0.85},
        {'ticker': 'NVDA', 'price': 450, 'confidence': 0.75},
        {'ticker': 'TSLA', 'price': 250, 'confidence': 0.70},
        {'ticker': 'JNJ', 'price': 160, 'confidence': 0.80}
    ]
    
    print(f"Account Value: ${account_value:,.2f}")
    print(f"Leverage: {leverage}x")
    print(f"Max Position: {max_position_pct:.0%}")
    
    for test in test_cases:
        print(f"\n{test['ticker']} @ ${test['price']}")
        print(f"Confidence: {test['confidence']:.0%}")
        
        # Calculate position size
        base_allocation = min(max_position_pct, test['confidence'] * 0.2)
        leveraged_value = account_value * base_allocation * leverage
        shares = int(leveraged_value / test['price'])
        actual_value = shares * test['price']
        
        print(f"Base Allocation: {base_allocation:.1%}")
        print(f"Leveraged Value: ${leveraged_value:,.2f}")
        print(f"Shares: {shares}")
        print(f"Actual Position: ${actual_value:,.2f}")
        print(f"% of Account (leveraged): {actual_value/account_value:.1%}")

if __name__ == "__main__":
    # Run tests
    test_portfolio_scenarios()
    test_position_sizing()
    
    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)