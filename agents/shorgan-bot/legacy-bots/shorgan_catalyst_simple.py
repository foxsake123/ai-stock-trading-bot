"""
SHORGAN-BOT Catalyst Trading System
September 10, 2025 - Small/Mid-Cap Focus
"""

import alpaca_trade_api as tradeapi
import json
from datetime import datetime

# SHORGAN-BOT Alpaca Credentials
API_KEY = "PKJRLSB2MFEJUSK6UK2E"
SECRET_KEY = "QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic"
BASE_URL = "https://paper-api.alpaca.markets"

def connect_alpaca():
    """Connect to Alpaca API"""
    try:
        api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
        account = api.get_account()
        print("SHORGAN-BOT CATALYST TRADING SYSTEM")
        print("=" * 60)
        print(f"[SUCCESS] Connected to Alpaca")
        print(f"Buying Power: ${float(account.buying_power):,.2f}")
        print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
        return api
    except Exception as e:
        print(f"[ERROR] Connection failed: {str(e)}")
        return None

def place_catalyst_trades(api):
    """Place catalyst-driven trades"""
    
    print("\n" + "=" * 60)
    print("EXECUTING CATALYST TRADES")
    print("=" * 60)
    
    trades_executed = []
    
    # 1. PLTR - LONG (AI Contract Rumors)
    try:
        print("\n[1] PLTR - LONG POSITION")
        print("  Catalyst: AI contract rumors")
        print("  Size: $7,500 (520 shares @ $14.50)")
        
        order = api.submit_order(
            symbol='PLTR',
            qty=520,
            side='buy',
            type='limit',
            time_in_force='day',
            limit_price=14.50,
            order_class='bracket',
            stop_loss={'stop_price': 13.30},
            take_profit={'limit_price': 16.00}
        )
        
        print(f"  [SUCCESS] Order ID: {order.id}")
        print(f"  Stop: $13.30 (-8.3%) | Target: $16.00 (+10.3%)")
        trades_executed.append({"symbol": "PLTR", "side": "buy", "qty": 520, "price": 14.50, "order_id": order.id})
        
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
    
    # 2. CVNA - SHORT (Parabolic Exhaustion)
    try:
        print("\n[2] CVNA - SHORT POSITION")
        print("  Catalyst: Parabolic exhaustion")
        print("  Size: $5,000 (100 shares @ $48.00)")
        
        order = api.submit_order(
            symbol='CVNA',
            qty=100,
            side='sell',
            type='limit',
            time_in_force='day',
            limit_price=48.00,
            order_class='bracket',
            stop_loss={'stop_price': 51.50},
            take_profit={'limit_price': 42.00}
        )
        
        print(f"  [SUCCESS] Order ID: {order.id}")
        print(f"  Stop: $51.50 (-7.3%) | Target: $42.00 (+12.5%)")
        trades_executed.append({"symbol": "CVNA", "side": "sell", "qty": 100, "price": 48.00, "order_id": order.id})
        
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
    
    # 3. CRWD - LONG (Cybersecurity Demand)
    try:
        print("\n[3] CRWD - LONG POSITION")
        print("  Catalyst: Cybersecurity demand surge")
        print("  Size: $7,500 (36 shares @ $210.00)")
        
        order = api.submit_order(
            symbol='CRWD',
            qty=36,
            side='buy',
            type='limit',
            time_in_force='day',
            limit_price=210.00,
            order_class='bracket',
            stop_loss={'stop_price': 199.50},
            take_profit={'limit_price': 225.00}
        )
        
        print(f"  [SUCCESS] Order ID: {order.id}")
        print(f"  Stop: $199.50 (-5.0%) | Target: $225.00 (+7.1%)")
        trades_executed.append({"symbol": "CRWD", "side": "buy", "qty": 36, "price": 210.00, "order_id": order.id})
        
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
    
    # 4. UPST - SHORT (Breaking Support)
    try:
        print("\n[4] UPST - SHORT POSITION")
        print("  Catalyst: Breaking key support level")
        print("  Size: $3,000 (100 shares @ $30.00)")
        
        order = api.submit_order(
            symbol='UPST',
            qty=100,
            side='sell',
            type='limit',
            time_in_force='day',
            limit_price=30.00,
            order_class='bracket',
            stop_loss={'stop_price': 31.50},
            take_profit={'limit_price': 27.00}
        )
        
        print(f"  [SUCCESS] Order ID: {order.id}")
        print(f"  Stop: $31.50 (-5.0%) | Target: $27.00 (+10.0%)")
        trades_executed.append({"symbol": "UPST", "side": "sell", "qty": 100, "price": 30.00, "order_id": order.id})
        
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
    
    # Options trades note
    print("\n[OPTIONS TRADES] - Manual execution required")
    print("  [5] DDOG - ATM Straddle ($110 strike, 3 contracts) - $2,400")
    print("  [6] ROKU - Call Options ($65 strike, 3 contracts) - $1,050")
    print("  Note: Alpaca paper trading has limited options support")
    
    return trades_executed

def save_trading_log(trades):
    """Save trading log"""
    total_capital = sum([
        520 * 14.50,  # PLTR
        100 * 48.00,  # CVNA
        36 * 210.00,  # CRWD
        100 * 30.00,  # UPST
        2400,          # DDOG options
        1050           # ROKU options
    ])
    
    log_data = {
        "date": "2025-09-10",
        "bot": "SHORGAN-BOT",
        "strategy": "Small/Mid-Cap Catalyst System",
        "executed_trades": trades,
        "total_capital_deployed": total_capital,
        "target_return": "$2,000-4,000",
        "daily_loss_limit": "$3,000",
        "execution_time": datetime.now().isoformat()
    }
    
    filename = f"SHORGAN_CATALYST_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    return filename, log_data

if __name__ == "__main__":
    # Connect to Alpaca
    api = connect_alpaca()
    
    if api:
        # Execute catalyst trades
        trades = place_catalyst_trades(api)
        
        # Save log
        log_file, log_data = save_trading_log(trades)
        
        # Summary
        print("\n" + "=" * 60)
        print("TRADING SUMMARY")
        print("=" * 60)
        print(f"Executed Trades: {len(trades)}")
        print(f"Total Capital: ${log_data['total_capital_deployed']:,.2f}")
        print(f"Expected Return: {log_data['target_return']}")
        print(f"Log File: {log_file}")
        print("=" * 60)
        print("\n[SUCCESS] Shorgan-bot catalyst trades submitted!")
        print("Check Alpaca dashboard: https://app.alpaca.markets/paper/dashboard/overview")
    else:
        print("\n[ERROR] Could not execute trades - connection failed")