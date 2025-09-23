"""
Portfolio Monitor and Risk Assessment System
September 11, 2025
Monitors all positions and calculates risk metrics for both bots
"""

import alpaca_trade_api as tradeapi
import json
from datetime import datetime, date
from pathlib import Path

# Bot credentials
DEE_BOT = {
    'API_KEY': 'PK6FZK4DAQVTD7DYVH78',
    'SECRET_KEY': 'JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt',
    'name': 'DEE-BOT'
}

SHORGAN_BOT = {
    'API_KEY': 'PKJRLSB2MFEJUSK6UK2E',
    'SECRET_KEY': 'QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic',
    'name': 'SHORGAN-BOT'
}

BASE_URL = "https://paper-api.alpaca.markets"

def connect_bot(bot_config):
    """Connect to a specific bot's Alpaca account"""
    try:
        api = tradeapi.REST(bot_config['API_KEY'], bot_config['SECRET_KEY'], BASE_URL, api_version='v2')
        return api
    except Exception as e:
        print(f"[ERROR] {bot_config['name']} connection failed: {str(e)}")
        return None

def get_positions(api, bot_name):
    """Get all positions for a bot"""
    try:
        positions = api.list_positions()
        position_data = []
        
        for position in positions:
            current_price = float(position.current_price)
            avg_entry = float(position.avg_entry_price)
            qty = int(position.qty)
            market_value = float(position.market_value)
            unrealized_pl = float(position.unrealized_pl)
            unrealized_plpc = float(position.unrealized_plpc) * 100
            
            position_data.append({
                'symbol': position.symbol,
                'quantity': qty,
                'avg_entry': avg_entry,
                'current_price': current_price,
                'market_value': market_value,
                'unrealized_pl': unrealized_pl,
                'unrealized_plpc': unrealized_plpc,
                'side': position.side
            })
            
        return position_data
    except Exception as e:
        print(f"[ERROR] Could not get positions for {bot_name}: {str(e)}")
        return []

def calculate_risk_metrics(positions, account_value):
    """Calculate portfolio risk metrics"""
    if not positions:
        return {
            'total_positions': 0,
            'total_exposure': 0,
            'largest_position': 0,
            'portfolio_concentration': 0,
            'total_unrealized_pl': 0,
            'avg_position_return': 0
        }
    
    total_exposure = sum(abs(p['market_value']) for p in positions)
    largest_position = max(abs(p['market_value']) for p in positions)
    total_unrealized_pl = sum(p['unrealized_pl'] for p in positions)
    avg_return = sum(p['unrealized_plpc'] for p in positions) / len(positions)
    
    return {
        'total_positions': len(positions),
        'total_exposure': total_exposure,
        'largest_position': largest_position,
        'portfolio_concentration': (largest_position / account_value * 100) if account_value > 0 else 0,
        'total_unrealized_pl': total_unrealized_pl,
        'avg_position_return': avg_return,
        'exposure_ratio': (total_exposure / account_value * 100) if account_value > 0 else 0
    }

def monitor_portfolio():
    """Monitor both bot portfolios and assess risk"""
    
    print("=" * 80)
    print("PORTFOLIO MONITOR & RISK ASSESSMENT")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    portfolio_data = {}
    combined_metrics = {
        'total_value': 0,
        'total_positions': 0,
        'total_exposure': 0,
        'total_unrealized_pl': 0
    }
    
    # Monitor each bot
    for bot_config in [DEE_BOT, SHORGAN_BOT]:
        print(f"\n{bot_config['name']} PORTFOLIO STATUS")
        print("-" * 40)
        
        api = connect_bot(bot_config)
        if not api:
            continue
            
        # Get account info
        account = api.get_account()
        portfolio_value = float(account.portfolio_value)
        cash = float(account.cash)
        buying_power = float(account.buying_power)
        
        print(f"Portfolio Value: ${portfolio_value:,.2f}")
        print(f"Cash: ${cash:,.2f}")
        print(f"Buying Power: ${buying_power:,.2f}")
        
        # Get positions
        positions = get_positions(api, bot_config['name'])
        
        if positions:
            print(f"\nOpen Positions ({len(positions)}):")
            for pos in positions:
                pl_sign = '+' if pos['unrealized_pl'] >= 0 else ''
                print(f"  {pos['symbol']}: {pos['quantity']} shares @ ${pos['avg_entry']:.2f}")
                print(f"    Current: ${pos['current_price']:.2f} | P&L: {pl_sign}${pos['unrealized_pl']:.2f} ({pl_sign}{pos['unrealized_plpc']:.2f}%)")
        else:
            print("\nNo open positions")
        
        # Calculate risk metrics
        risk_metrics = calculate_risk_metrics(positions, portfolio_value)
        
        print(f"\nRisk Metrics:")
        print(f"  Total Exposure: ${risk_metrics['total_exposure']:,.2f} ({risk_metrics['exposure_ratio']:.1f}% of portfolio)")
        print(f"  Largest Position: ${risk_metrics['largest_position']:,.2f} ({risk_metrics['portfolio_concentration']:.1f}% concentration)")
        print(f"  Unrealized P&L: ${risk_metrics['total_unrealized_pl']:+,.2f}")
        print(f"  Avg Position Return: {risk_metrics['avg_position_return']:+.2f}%")
        
        # Store data
        portfolio_data[bot_config['name']] = {
            'portfolio_value': portfolio_value,
            'cash': cash,
            'buying_power': buying_power,
            'positions': positions,
            'risk_metrics': risk_metrics
        }
        
        # Update combined metrics
        combined_metrics['total_value'] += portfolio_value
        combined_metrics['total_positions'] += len(positions)
        combined_metrics['total_exposure'] += risk_metrics['total_exposure']
        combined_metrics['total_unrealized_pl'] += risk_metrics['total_unrealized_pl']
    
    # Combined portfolio analysis
    print("\n" + "=" * 80)
    print("COMBINED PORTFOLIO ANALYSIS")
    print("=" * 80)
    print(f"Total Portfolio Value: ${combined_metrics['total_value']:,.2f}")
    print(f"Total Positions: {combined_metrics['total_positions']}")
    print(f"Total Exposure: ${combined_metrics['total_exposure']:,.2f}")
    print(f"Total Unrealized P&L: ${combined_metrics['total_unrealized_pl']:+,.2f}")
    print(f"Exposure Ratio: {(combined_metrics['total_exposure'] / combined_metrics['total_value'] * 100):.1f}%")
    
    # Risk warnings
    print("\nRISK WARNINGS:")
    warnings = []
    
    if combined_metrics['total_exposure'] / combined_metrics['total_value'] > 0.8:
        warnings.append("HIGH EXPOSURE: Over 80% of capital deployed")
    
    for bot_name, data in portfolio_data.items():
        if data['risk_metrics']['portfolio_concentration'] > 20:
            warnings.append(f"{bot_name}: Position concentration >20%")
        if data['risk_metrics']['total_unrealized_pl'] < -2000:
            warnings.append(f"{bot_name}: Significant unrealized losses")
    
    if warnings:
        for warning in warnings:
            print(f"  [WARNING] {warning}")
    else:
        print("  [OK] All risk parameters within limits")
    
    # Save monitoring report
    output_dir = Path("C:/Users/shorg/ai-stock-trading-bot/04_risk/reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"portfolio_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    monitor_data = {
        'timestamp': datetime.now().isoformat(),
        'date': str(date.today()),
        'portfolios': portfolio_data,
        'combined_metrics': combined_metrics,
        'warnings': warnings
    }
    
    with open(output_file, 'w') as f:
        json.dump(monitor_data, f, indent=2)
    
    print(f"\n" + "=" * 80)
    print(f"Monitoring report saved: {output_file}")
    print("=" * 80)
    
    return monitor_data

if __name__ == "__main__":
    monitor_data = monitor_portfolio()
    print("\nPortfolio monitoring complete!")