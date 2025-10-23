"""
DEE-BOT Trade Execution System
September 11, 2025
Executes trades based on multi-agent consensus recommendations
"""

import alpaca_trade_api as tradeapi
import json
from datetime import datetime, date
from pathlib import Path
import time

# DEE-BOT Alpaca Credentials
API_KEY = "PK6FZK4DAQVTD7DYVH78"
SECRET_KEY = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"
BASE_URL = "https://paper-api.alpaca.markets"

def connect_alpaca():
    """Connect to Alpaca API"""
    try:
        api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
        account = api.get_account()
        print("=" * 80)
        print("DEE-BOT TRADE EXECUTION SYSTEM")
        print("=" * 80)
        print(f"[SUCCESS] Connected to Alpaca Paper Trading")
        print(f"Account Status: {account.status}")
        print(f"Buying Power: ${float(account.buying_power):,.2f}")
        print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"Cash: ${float(account.cash):,.2f}")
        return api
    except Exception as e:
        print(f"[ERROR] Connection failed: {str(e)}")
        return None

def load_recommendations():
    """Load today's trading recommendations"""
    rec_file = Path(f"C:/Users/shorg/ai-stock-trading-bot/02_data/research/reports/daily_recommendations/dee_bot_recommendations_{date.today()}.json")
    
    if not rec_file.exists():
        print("[ERROR] No recommendations file found for today")
        return None
        
    with open(rec_file, 'r') as f:
        data = json.load(f)
    
    return data

def get_current_price(api, symbol):
    """Get current market price for a symbol"""
    try:
        barset = api.get_latest_bar(symbol)
        return barset.c  # Close price
    except Exception as e:
        print(f"[ERROR] Could not get price for {symbol}: {str(e)}")
        return None

def calculate_position_size(api, price, portfolio_value):
    """Calculate position size based on risk management rules"""
    # Maximum 5% of portfolio per position
    max_position_value = float(portfolio_value) * 0.05
    
    # Calculate shares
    shares = int(max_position_value / price)
    
    # Ensure minimum meaningful position
    if shares < 1:
        shares = 1
    
    return shares

def place_trades(api):
    """Execute trades based on recommendations"""
    print("\n" + "=" * 80)
    print("LOADING TODAY'S RECOMMENDATIONS")
    print("=" * 80)
    
    # Load recommendations
    recommendations = load_recommendations()
    if not recommendations:
        return
    
    top_recs = recommendations['top_recommendations']
    print(f"\nFound {len(top_recs)} top recommendations for today")
    
    # Get account info
    account = api.get_account()
    portfolio_value = float(account.portfolio_value)
    buying_power = float(account.buying_power)
    
    print(f"\nAvailable buying power: ${buying_power:,.2f}")
    print(f"Portfolio value: ${portfolio_value:,.2f}")
    
    # Track orders
    executed_orders = []
    failed_orders = []
    
    print("\n" + "=" * 80)
    print("EXECUTING TRADES")
    print("=" * 80)
    
    for i, rec in enumerate(top_recs, 1):
        symbol = rec['ticker']
        action = rec['consensus_action']
        confidence = rec['confidence']
        
        if action != 'BUY':
            continue  # Only execute BUY orders for now
            
        print(f"\n[{i}] Processing {symbol} - {action} (Confidence: {confidence:.1%})")
        
        # Get current price
        current_price = get_current_price(api, symbol)
        if not current_price:
            print(f"  [SKIP] Could not get price for {symbol}")
            failed_orders.append({
                'symbol': symbol,
                'reason': 'Price unavailable'
            })
            continue
        
        print(f"  Current Price: ${current_price:.2f}")
        
        # Calculate position size
        shares = calculate_position_size(api, current_price, portfolio_value)
        position_value = shares * current_price
        
        # Check if we have enough buying power
        if position_value > buying_power:
            shares = int(buying_power / current_price * 0.95)  # Use 95% of available
            if shares < 1:
                print(f"  [SKIP] Insufficient buying power for {symbol}")
                failed_orders.append({
                    'symbol': symbol,
                    'reason': 'Insufficient funds'
                })
                continue
        
        print(f"  Position Size: {shares} shares (${position_value:,.2f})")
        
        # Calculate stop loss and take profit
        stop_loss = round(current_price * 0.97, 2)  # 3% stop loss
        take_profit = round(current_price * 1.05, 2)  # 5% take profit
        
        print(f"  Stop Loss: ${stop_loss:.2f} (-3%)")
        print(f"  Take Profit: ${take_profit:.2f} (+5%)")
        
        try:
            # Place market order
            print(f"  Placing order...")
            order = api.submit_order(
                symbol=symbol,
                qty=shares,
                side='buy',
                type='market',
                time_in_force='day'
            )
            
            print(f"  [SUCCESS] Order placed - ID: {order.id}")
            
            # Record order
            executed_orders.append({
                'symbol': symbol,
                'action': action,
                'shares': shares,
                'price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': confidence,
                'order_id': order.id,
                'timestamp': datetime.now().isoformat()
            })
            
            # Update buying power
            buying_power -= position_value
            
            # Small delay to avoid rate limits
            time.sleep(0.5)
            
            # Place stop loss order
            try:
                stop_order = api.submit_order(
                    symbol=symbol,
                    qty=shares,
                    side='sell',
                    type='stop',
                    stop_price=stop_loss,
                    time_in_force='gtc'
                )
                print(f"  [SUCCESS] Stop loss order placed - ID: {stop_order.id}")
            except Exception as e:
                print(f"  [WARNING] Could not place stop loss: {str(e)}")
            
        except Exception as e:
            print(f"  [ERROR] Order failed: {str(e)}")
            failed_orders.append({
                'symbol': symbol,
                'reason': str(e)
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Successfully executed: {len(executed_orders)} orders")
    print(f"Failed orders: {len(failed_orders)}")
    
    if executed_orders:
        print("\nExecuted Trades:")
        total_deployed = 0
        for order in executed_orders:
            value = order['shares'] * order['price']
            total_deployed += value
            print(f"  - {order['symbol']}: {order['shares']} shares @ ${order['price']:.2f} = ${value:,.2f}")
        print(f"\nTotal Capital Deployed: ${total_deployed:,.2f}")
    
    if failed_orders:
        print("\nFailed Orders:")
        for fail in failed_orders:
            print(f"  - {fail['symbol']}: {fail['reason']}")
    
    # Save execution log
    log_dir = Path("C:/Users/shorg/ai-stock-trading-bot/09_logs/trading")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"dee_bot_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    log_data = {
        'date': str(date.today()),
        'timestamp': datetime.now().isoformat(),
        'bot': 'DEE-BOT',
        'strategy': 'Multi-Agent Consensus',
        'executed_orders': executed_orders,
        'failed_orders': failed_orders,
        'summary': {
            'total_orders': len(executed_orders),
            'total_deployed': sum(o['shares'] * o['price'] for o in executed_orders),
            'average_confidence': sum(o['confidence'] for o in executed_orders) / len(executed_orders) if executed_orders else 0
        }
    }
    
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"\nExecution log saved: {log_file}")
    
    return log_data

if __name__ == "__main__":
    api = connect_alpaca()
    if api:
        result = place_trades(api)
        print("\n" + "=" * 80)
        print("DEE-BOT TRADE EXECUTION COMPLETE")
        print("=" * 80)