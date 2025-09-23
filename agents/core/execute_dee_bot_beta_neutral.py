"""
DEE-BOT Beta-Neutral Execution System with 2X Leverage
Executes trades based on multi-agent consensus with beta hedging
"""

import alpaca_trade_api as tradeapi
import json
from datetime import datetime, date
from pathlib import Path
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bots.dee_bot.dee_bot_beta_neutral import BetaNeutralStrategy
from bots.dee_bot.risk_manager_leveraged import LeveragedRiskManager

# DEE-BOT Alpaca Credentials
API_KEY = "PK6FZK4DAQVTD7DYVH78"
SECRET_KEY = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"
BASE_URL = "https://paper-api.alpaca.markets"

# Strategy Configuration
USE_BETA_NEUTRAL = True
USE_LEVERAGE = True
LEVERAGE_MULTIPLIER = 2.0
AUTO_EXECUTE = False  # Set to True for automatic execution without confirmation

def connect_alpaca():
    """Connect to Alpaca API"""
    try:
        api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
        account = api.get_account()
        print("=" * 80)
        print("DEE-BOT BETA-NEUTRAL EXECUTION SYSTEM (2X LEVERAGE)")
        print("=" * 80)
        print(f"[SUCCESS] Connected to Alpaca Paper Trading")
        print(f"Account Status: {account.status}")
        print(f"Buying Power: ${float(account.buying_power):,.2f}")
        print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"Cash: ${float(account.cash):,.2f}")
        
        # Calculate effective buying power with leverage
        if USE_LEVERAGE:
            effective_bp = float(account.buying_power) * LEVERAGE_MULTIPLIER
            print(f"Effective Buying Power (2X): ${effective_bp:,.2f}")
        
        return api
    except Exception as e:
        print(f"[ERROR] Connection failed: {str(e)}")
        return None

def load_recommendations():
    """Load today's trading recommendations"""
    rec_file = Path(f"C:/Users/shorg/ai-stock-trading-bot/02_data/research/reports/daily_recommendations/dee_bot_recommendations_{date.today()}.json")
    
    if not rec_file.exists():
        print("[ERROR] No recommendations file found for today")
        print("Please run generate_dee_bot_recommendations.py first")
        return None
        
    with open(rec_file, 'r') as f:
        data = json.load(f)
    
    return data

def execute_beta_neutral_strategy(api):
    """Execute beta-neutral strategy with leverage"""
    
    # Load recommendations
    print("\n" + "=" * 80)
    print("LOADING RECOMMENDATIONS")
    print("=" * 80)
    
    recommendations_data = load_recommendations()
    if not recommendations_data:
        return None
    
    print(f"Strategy: {recommendations_data['strategy']}")
    print(f"Leverage Enabled: {recommendations_data.get('leverage_enabled', False)}")
    print(f"Target Leverage: {recommendations_data.get('target_leverage', 1.0)}x")
    
    # Initialize strategies
    beta_strategy = BetaNeutralStrategy(api)
    risk_manager = LeveragedRiskManager(api, LEVERAGE_MULTIPLIER)
    
    # Check risk conditions first
    print("\n" + "=" * 80)
    print("RISK ASSESSMENT")
    print("=" * 80)
    
    margin_check = risk_manager.check_margin_requirements()
    print(f"Margin Utilization: {margin_check.get('margin_utilization', 0):.1%}")
    print(f"Can Use Leverage: {margin_check.get('can_use_leverage', False)}")
    
    drawdown_check = risk_manager.monitor_drawdown()
    print(f"Daily P&L: ${drawdown_check.get('daily_pnl', 0):,.2f}")
    print(f"Risk Action Required: {drawdown_check.get('action_required', 'NONE')}")
    
    if drawdown_check.get('action_required') == 'FORCE_CLOSE_ALL':
        print("\n[CRITICAL] Force close triggered - exiting all positions")
        return None
    
    if not margin_check.get('can_use_leverage', False):
        print("\n[WARNING] Insufficient margin for leverage - switching to 1X")
        LEVERAGE_MULTIPLIER = 1.0
    
    # Build beta-neutral portfolio
    print("\n" + "=" * 80)
    print("BUILDING BETA-NEUTRAL PORTFOLIO")
    print("=" * 80)
    
    portfolio_plan = beta_strategy.build_beta_neutral_portfolio(
        recommendations_data['top_recommendations']
    )
    
    # Display portfolio plan
    print(f"\nPortfolio Summary:")
    print(f"  Long Positions: {len(portfolio_plan['long_positions'])}")
    print(f"  Hedge Positions: {len(portfolio_plan['hedge_positions'])}")
    print(f"  Total Long Beta: {portfolio_plan['total_long_beta']:.3f}")
    print(f"  Total Hedge Beta: {portfolio_plan['total_hedge_beta']:.3f}")
    print(f"  Net Portfolio Beta: {portfolio_plan['net_beta']:.3f}")
    print(f"  Leverage: {portfolio_plan['leverage_used']}x")
    
    # Validate beta neutrality
    if abs(portfolio_plan['net_beta']) > 0.2:
        print(f"\n[WARNING] Portfolio beta {portfolio_plan['net_beta']:.3f} is not neutral")
        print("Consider adjusting hedge positions")
    
    # Calculate total capital required
    total_long_value = sum(p['value'] for p in portfolio_plan['long_positions'])
    total_hedge_value = sum(p['value'] for p in portfolio_plan['hedge_positions'])
    total_required = total_long_value + total_hedge_value
    
    print(f"\nCapital Requirements:")
    print(f"  Long Positions: ${total_long_value:,.2f}")
    print(f"  Hedge Positions: ${total_hedge_value:,.2f}")
    print(f"  Total Required: ${total_required:,.2f}")
    
    # Validate each trade with risk manager
    print("\n" + "=" * 80)
    print("TRADE VALIDATION")
    print("=" * 80)
    
    validated_trades = []
    rejected_trades = []
    
    for position in portfolio_plan['long_positions'] + portfolio_plan['hedge_positions']:
        validation = risk_manager.validate_trade(
            position['ticker'],
            position['shares'],
            'buy'
        )
        
        if validation['approved']:
            validated_trades.append(position)
            print(f"✓ {position['ticker']}: APPROVED")
        else:
            rejected_trades.append(position)
            print(f"✗ {position['ticker']}: REJECTED - {validation['reasons']}")
    
    if not validated_trades:
        print("\n[ERROR] No trades passed risk validation")
        return None
    
    # Confirm execution
    if not AUTO_EXECUTE:
        print("\n" + "=" * 80)
        print("EXECUTION CONFIRMATION")
        print("=" * 80)
        print(f"Ready to execute {len(validated_trades)} trades")
        print(f"Total value: ${sum(t['value'] for t in validated_trades):,.2f}")
        
        response = input("\nProceed with execution? (yes/no): ")
        if response.lower() != 'yes':
            print("Execution cancelled by user")
            return None
    
    # Execute trades
    print("\n" + "=" * 80)
    print("EXECUTING TRADES")
    print("=" * 80)
    
    execution_results = {
        'executed_trades': [],
        'failed_trades': [],
        'portfolio_beta': portfolio_plan['net_beta'],
        'leverage_used': portfolio_plan['leverage_used']
    }
    
    for position in validated_trades:
        print(f"\nExecuting {position['ticker']}:")
        print(f"  Shares: {position['shares']}")
        print(f"  Value: ${position['value']:,.2f}")
        print(f"  Beta: {position['beta']:.3f}")
        
        try:
            # Place market order
            order = api.submit_order(
                symbol=position['ticker'],
                qty=position['shares'],
                side='buy',
                type='market',
                time_in_force='day'
            )
            
            print(f"  [SUCCESS] Order ID: {order.id}")
            
            # Calculate and set stop loss (tighter for leverage)
            stop_loss, take_profit = risk_manager.set_dynamic_stops(
                position['ticker'],
                position['price'],
                0.02  # Assume 2% daily volatility
            )
            
            # Place stop loss order
            try:
                stop_order = api.submit_order(
                    symbol=position['ticker'],
                    qty=position['shares'],
                    side='sell',
                    type='stop',
                    stop_price=stop_loss,
                    time_in_force='gtc'
                )
                print(f"  Stop Loss: ${stop_loss:.2f} (Order ID: {stop_order.id})")
            except Exception as e:
                print(f"  [WARNING] Could not set stop loss: {str(e)}")
            
            execution_results['executed_trades'].append({
                'ticker': position['ticker'],
                'shares': position['shares'],
                'price': position['price'],
                'value': position['value'],
                'beta': position['beta'],
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'order_id': order.id,
                'timestamp': datetime.now().isoformat()
            })
            
            # Small delay to avoid rate limits
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  [ERROR] Execution failed: {str(e)}")
            execution_results['failed_trades'].append({
                'ticker': position['ticker'],
                'error': str(e)
            })
    
    # Generate risk report
    print("\n" + "=" * 80)
    print("POST-EXECUTION RISK REPORT")
    print("=" * 80)
    
    risk_report = risk_manager.generate_risk_report()
    
    print(f"Total Exposure: ${risk_report['risk_metrics'].get('total_exposure', 0):,.2f}")
    print(f"VaR (95%): ${risk_report['risk_metrics'].get('var_95', 0):,.2f}")
    print(f"Margin Utilization: {risk_report['risk_metrics'].get('margin_utilization', 0):.1%}")
    
    if risk_report['warnings']:
        print("\nRisk Warnings:")
        for warning in risk_report['warnings']:
            print(f"  ⚠ {warning}")
    
    # Save execution log
    log_dir = Path("C:/Users/shorg/ai-stock-trading-bot/09_logs/trading")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"dee_bot_beta_neutral_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    log_data = {
        'date': str(date.today()),
        'timestamp': datetime.now().isoformat(),
        'bot': 'DEE-BOT',
        'strategy': 'Beta-Neutral with 2X Leverage',
        'portfolio_plan': portfolio_plan,
        'execution_results': execution_results,
        'risk_report': risk_report,
        'summary': {
            'total_executed': len(execution_results['executed_trades']),
            'total_failed': len(execution_results['failed_trades']),
            'portfolio_beta': portfolio_plan['net_beta'],
            'leverage_used': LEVERAGE_MULTIPLIER,
            'total_value': sum(t['value'] for t in execution_results['executed_trades'])
        }
    }
    
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"\nExecution log saved: {log_file}")
    
    return log_data

def main():
    """Main execution function"""
    api = connect_alpaca()
    if not api:
        return
    
    # Execute strategy
    result = execute_beta_neutral_strategy(api)
    
    if result:
        print("\n" + "=" * 80)
        print("EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Successfully executed: {result['summary']['total_executed']} trades")
        print(f"Failed: {result['summary']['total_failed']} trades")
        print(f"Portfolio Beta: {result['summary']['portfolio_beta']:.3f}")
        print(f"Total Value Deployed: ${result['summary']['total_value']:,.2f}")
        print(f"Leverage Used: {result['summary']['leverage_used']}x")
        
        print("\n✓ DEE-BOT Beta-Neutral Strategy Execution Complete")
    else:
        print("\n✗ Execution terminated")

if __name__ == "__main__":
    main()