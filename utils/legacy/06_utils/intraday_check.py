"""
Intraday Performance Check
September 12, 2025
Real-time portfolio status and P&L calculation
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

# Yesterday's closing values (September 11, 2025)
YESTERDAY_VALUES = {
    'DEE-BOT': 100697.26,
    'SHORGAN-BOT': 103398.18,
    'COMBINED': 204095.44
}

def connect_bot(bot_config):
    """Connect to a specific bot's Alpaca account"""
    try:
        api = tradeapi.REST(bot_config['API_KEY'], bot_config['SECRET_KEY'], BASE_URL, api_version='v2')
        return api
    except Exception as e:
        print(f"[ERROR] {bot_config['name']} connection failed: {str(e)}")
        return None

def get_positions_detail(api):
    """Get detailed position information"""
    positions = api.list_positions()
    position_details = []
    total_unrealized_pl = 0
    
    for pos in positions:
        unrealized_pl = float(pos.unrealized_pl)
        unrealized_plpc = float(pos.unrealized_plpc) * 100
        total_unrealized_pl += unrealized_pl
        
        position_details.append({
            'symbol': pos.symbol,
            'qty': int(pos.qty),
            'current_price': float(pos.current_price),
            'avg_entry': float(pos.avg_entry_price),
            'market_value': float(pos.market_value),
            'unrealized_pl': unrealized_pl,
            'unrealized_plpc': unrealized_plpc,
            'change_today': float(pos.change_today) if hasattr(pos, 'change_today') else 0
        })
    
    return position_details, total_unrealized_pl

def check_intraday_performance():
    """Check current intraday performance for both bots"""
    
    print("=" * 80)
    print("INTRADAY PERFORMANCE CHECK")
    print(f"Date: {date.today()} - Time: {datetime.now().strftime('%I:%M %p ET')}")
    print("=" * 80)
    
    combined_current_value = 0
    combined_daily_pl = 0
    all_positions = []
    
    for bot_config in [DEE_BOT, SHORGAN_BOT]:
        print(f"\n{bot_config['name']} STATUS")
        print("-" * 40)
        
        api = connect_bot(bot_config)
        if not api:
            continue
        
        # Get account info
        account = api.get_account()
        current_value = float(account.portfolio_value)
        cash = float(account.cash)
        buying_power = float(account.buying_power)
        
        # Calculate daily P&L
        yesterday_value = YESTERDAY_VALUES[bot_config['name']]
        daily_pl = current_value - yesterday_value
        daily_return_pct = (daily_pl / yesterday_value) * 100
        
        # Total return from start
        starting_capital = 100000
        total_return = current_value - starting_capital
        total_return_pct = (total_return / starting_capital) * 100
        
        print(f"Current Value: ${current_value:,.2f}")
        print(f"Yesterday Close: ${yesterday_value:,.2f}")
        print(f"Today's P&L: ${daily_pl:+,.2f} ({daily_return_pct:+.2f}%)")
        print(f"Total Return: ${total_return:+,.2f} ({total_return_pct:+.2f}%)")
        print(f"Cash: ${cash:,.2f}")
        print(f"Buying Power: ${buying_power:,.2f}")
        
        # Get positions
        positions, unrealized_pl = get_positions_detail(api)
        
        if positions:
            print(f"\nTop Movers Today:")
            # Sort by today's change
            sorted_positions = sorted(positions, key=lambda x: x['unrealized_plpc'], reverse=True)
            
            # Show top 3 gainers
            for i, pos in enumerate(sorted_positions[:3], 1):
                print(f"  {i}. {pos['symbol']}: ${pos['current_price']:.2f} ({pos['unrealized_plpc']:+.2f}%)")
            
            # Show worst performer if losing
            worst = sorted_positions[-1]
            if worst['unrealized_plpc'] < 0:
                print(f"  Worst: {worst['symbol']}: ${worst['current_price']:.2f} ({worst['unrealized_plpc']:+.2f}%)")
        
        # Update combined totals
        combined_current_value += current_value
        combined_daily_pl += daily_pl
        all_positions.extend(positions)
        
        # Store bot data
        bot_data = {
            'name': bot_config['name'],
            'current_value': current_value,
            'daily_pl': daily_pl,
            'daily_return_pct': daily_return_pct,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'positions_count': len(positions),
            'unrealized_pl': unrealized_pl
        }
    
    # Combined Portfolio Summary
    print("\n" + "=" * 80)
    print("COMBINED PORTFOLIO")
    print("=" * 80)
    
    yesterday_combined = YESTERDAY_VALUES['COMBINED']
    combined_daily_return_pct = (combined_daily_pl / yesterday_combined) * 100
    combined_total_return = combined_current_value - 200000
    combined_total_return_pct = (combined_total_return / 200000) * 100
    
    print(f"Current Total Value: ${combined_current_value:,.2f}")
    print(f"Yesterday's Close: ${yesterday_combined:,.2f}")
    print(f"Today's P&L: ${combined_daily_pl:+,.2f} ({combined_daily_return_pct:+.2f}%)")
    print(f"Total Return (from $200K): ${combined_total_return:+,.2f} ({combined_total_return_pct:+.2f}%)")
    print(f"Total Positions: {len(all_positions)}")
    
    # Market Hours Status
    clock = api.get_clock()
    if clock.is_open:
        print(f"\nMarket Status: [OPEN]")
        time_to_close = (clock.next_close - clock.timestamp).total_seconds() / 3600
        print(f"Hours until close: {time_to_close:.1f}")
    else:
        print(f"\nMarket Status: [CLOSED]")
        if clock.next_open:
            time_to_open = (clock.next_open - clock.timestamp).total_seconds() / 3600
            print(f"Hours until open: {time_to_open:.1f}")
    
    # Performance Rating
    print("\n" + "=" * 80)
    print("INTRADAY PERFORMANCE RATING")
    print("=" * 80)
    
    if combined_daily_pl > 1000:
        rating = "EXCELLENT"
        comment = "Strong gains across portfolios!"
    elif combined_daily_pl > 0:
        rating = "POSITIVE"
        comment = "On track for a profitable day."
    elif combined_daily_pl > -500:
        rating = "SLIGHTLY DOWN"
        comment = "Minor pullback, monitoring positions."
    else:
        rating = "NEGATIVE"
        comment = "Significant losses, review risk management."
    
    print(f"Rating: {rating}")
    print(f"Comment: {comment}")
    
    # Quick Stats
    print("\nQuick Stats:")
    print(f"• Best Performing Bot: {'DEE-BOT' if DEE_BOT['name'] == max([DEE_BOT, SHORGAN_BOT], key=lambda x: daily_pl)['name'] else 'SHORGAN-BOT'}")
    print(f"• Average Position Return: {sum(p['unrealized_plpc'] for p in all_positions) / len(all_positions):.2f}%")
    print(f"• Winning Positions: {sum(1 for p in all_positions if p['unrealized_pl'] > 0)}/{len(all_positions)}")
    
    # Save intraday snapshot
    snapshot_dir = Path("C:/Users/shorg/ai-stock-trading-bot/09_logs/snapshots")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    snapshot_file = snapshot_dir / f"intraday_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    snapshot_data = {
        'timestamp': datetime.now().isoformat(),
        'date': str(date.today()),
        'market_open': clock.is_open,
        'combined_value': combined_current_value,
        'combined_daily_pl': combined_daily_pl,
        'combined_daily_return_pct': combined_daily_return_pct,
        'dee_bot': {
            'value': current_value if bot_config['name'] == 'DEE-BOT' else 0,
            'daily_pl': daily_pl if bot_config['name'] == 'DEE-BOT' else 0,
        },
        'rating': rating
    }
    
    with open(snapshot_file, 'w') as f:
        json.dump(snapshot_data, f, indent=2)
    
    print(f"\nSnapshot saved: {snapshot_file}")
    print("=" * 80)
    
    return snapshot_data

if __name__ == "__main__":
    intraday_data = check_intraday_performance()
    print("\nIntraday check complete!")