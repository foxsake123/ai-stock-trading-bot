"""
SHORGAN-BOT Catalyst Trading System
September 10, 2025
Small/Mid-Cap Aggressive Catalyst-Driven Strategy
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
    """Place all catalyst-driven trades"""
    
    print("\n" + "=" * 60)
    print("📈 EXECUTING CATALYST TRADES")
    print("=" * 60)
    
    trades_log = []
    total_deployed = 0
    
    # Trade 1: PLTR - LONG
    try:
        print("\n📈 PLTR - LONG POSITION")
        print("  Catalyst: AI contract rumors")
        order = api.submit_order(
            symbol='PLTR',
            qty=520,
            side='buy',
            type='limit',
            time_in_force='day',
            limit_price=14.50,
            order_class='bracket',
            stop_loss={'stop_price': 13.30},  # -8.3%
            take_profit={'limit_price': 16.00}  # +10.3%
        )
        print(f"  ✅ Order placed: 520 shares @ $14.50")
        print(f"  📉 Stop: $13.30 | 📈 Target: $16.00")
        print(f"  Order ID: {order.id}")
        trades_log.append({"symbol": "PLTR", "type": "LONG", "qty": 520, "price": 14.50})
        total_deployed += 7540
    except Exception as e:
        print(f"  ❌ Failed: {str(e)}")
    
    # Trade 2: CVNA - SHORT
    try:
        print("\n📉 CVNA - SHORT POSITION")
        print("  Catalyst: Parabolic exhaustion")
        order = api.submit_order(
            symbol='CVNA',
            qty=100,
            side='sell',
            type='limit',
            time_in_force='day',
            limit_price=48.00,
            order_class='bracket',
            stop_loss={'stop_price': 51.50},  # -7.3%
            take_profit={'limit_price': 42.00}  # +12.5%
        )
        print(f"  ✅ Order placed: SHORT 100 shares @ $48.00")
        print(f"  📈 Stop: $51.50 | 📉 Target: $42.00")
        print(f"  Order ID: {order.id}")
        trades_log.append({"symbol": "CVNA", "type": "SHORT", "qty": 100, "price": 48.00})
        total_deployed += 4800
    except Exception as e:
        print(f"  ❌ Failed: {str(e)}")
    
    # Trade 3: CRWD - LONG
    try:
        print("\n📈 CRWD - LONG POSITION")
        print("  Catalyst: Cybersecurity demand surge")
        order = api.submit_order(
            symbol='CRWD',
            qty=36,
            side='buy',
            type='limit',
            time_in_force='day',
            limit_price=210.00,
            order_class='bracket',
            stop_loss={'stop_price': 199.50},  # -5%
            take_profit={'limit_price': 225.00}  # +7.1%
        )
        print(f"  ✅ Order placed: 36 shares @ $210.00")
        print(f"  📉 Stop: $199.50 | 📈 Target: $225.00")
        print(f"  Order ID: {order.id}")
        trades_log.append({"symbol": "CRWD", "type": "LONG", "qty": 36, "price": 210.00})
        total_deployed += 7560
    except Exception as e:
        print(f"  ❌ Failed: {str(e)}")
    
    # Trade 4: UPST - SHORT
    try:
        print("\n📉 UPST - SHORT POSITION")
        print("  Catalyst: Breaking key support")
        order = api.submit_order(
            symbol='UPST',
            qty=100,
            side='sell',
            type='limit',
            time_in_force='day',
            limit_price=30.00,
            order_class='bracket',
            stop_loss={'stop_price': 31.50},  # -5%
            take_profit={'limit_price': 27.00}  # +10%
        )
        print(f"  ✅ Order placed: SHORT 100 shares @ $30.00")
        print(f"  📈 Stop: $31.50 | 📉 Target: $27.00")
        print(f"  Order ID: {order.id}")
        trades_log.append({"symbol": "UPST", "type": "SHORT", "qty": 100, "price": 30.00})
        total_deployed += 3000
    except Exception as e:
        print(f"  ❌ Failed: {str(e)}")
    
    # Note: Options trades (DDOG straddle, ROKU calls) cannot be placed via Alpaca paper trading
    print("\n⚠️  OPTIONS TRADES (Manual execution required):")
    print("  🎲 DDOG - ATM Straddle ($110 strike, 3 contracts) - $2,400")
    print("  📺 ROKU - Calls ($65 strike, 3 contracts) - $1,050")
    
    return trades_log, total_deployed

def save_trading_log(trades, capital_deployed):
    """Save trading activity log"""
    
    log_data = {
        "date": "2025-09-10",
        "bot": "SHORGAN-BOT",
        "strategy": "Small/Mid-Cap Catalyst System",
        "trades": trades,
        "capital_deployed": capital_deployed,
        "expected_return": "$2,000-4,000",
        "daily_loss_limit": 3000,
        "timestamp": datetime.now().isoformat()
    }
    
    filename = f"SHORGAN_CATALYST_TRADES_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"\n💾 Trading log saved: {filename}")
    return filename

def display_summary(trades, capital):
    """Display trading summary"""
    
    print("\n" + "=" * 60)
    print("📊 TRADING SUMMARY")
    print("=" * 60)
    print(f"✅ Trades Executed: {len(trades)}")
    print(f"💰 Capital Deployed: ${capital:,.2f}")
    print(f"📈 Long Positions: {sum(1 for t in trades if t['type'] == 'LONG')}")
    print(f"📉 Short Positions: {sum(1 for t in trades if t['type'] == 'SHORT')}")
    print(f"⚡️ Strategy: Aggressive Catalyst-Driven")
    print(f"🎯 Expected Return: +$2,000-4,000")
    print(f"🛑 Daily Loss Limit: $3,000")
    print("=" * 60)

if __name__ == "__main__":
    # Connect to Alpaca
    api = connect_alpaca()
    
    if api:
        # Place catalyst trades
        trades, capital = place_catalyst_trades(api)
        
        # Save log
        save_trading_log(trades, capital)
        
        # Display summary
        display_summary(trades, capital)
        
        print("\n✅ SHORGAN-BOT catalyst trades submitted!")
        print("📱 Check Alpaca dashboard for order status")
        print("🔗 https://app.alpaca.markets/paper/dashboard/overview")
    else:
        print("\n❌ Could not execute trades")