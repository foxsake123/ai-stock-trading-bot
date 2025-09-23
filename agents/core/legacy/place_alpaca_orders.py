"""
Place DEE-BOT Orders via Alpaca Paper Trading
Date: January 10, 2025
"""

import json
import os
from datetime import datetime
from pathlib import Path
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def connect_to_alpaca():
    """Connect to Alpaca API (paper trading)"""
    
    # Check for API credentials
    api_key = os.getenv('APCA_API_KEY_ID') or os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('APCA_API_SECRET_KEY') or os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("[ERROR] Alpaca API credentials not found in environment variables")
        print("[INFO] Please set APCA_API_KEY_ID and APCA_API_SECRET_KEY in .env file")
        print("\nTo get your paper trading API keys:")
        print("1. Go to https://app.alpaca.markets/paper/dashboard/overview")
        print("2. Click on 'API Keys' in the left sidebar")
        print("3. Generate new keys if needed")
        print("4. Add to .env file:")
        print("   APCA_API_KEY_ID=your_key_here")
        print("   APCA_API_SECRET_KEY=your_secret_here")
        return None
    
    # Use paper trading endpoint
    base_url = 'https://paper-api.alpaca.markets'
    
    try:
        api = tradeapi.REST(
            api_key,
            secret_key,
            base_url,
            api_version='v2'
        )
        
        # Test connection
        account = api.get_account()
        print(f"[SUCCESS] Connected to Alpaca Paper Trading")
        print(f"  Account Status: {account.status}")
        print(f"  Buying Power: ${float(account.buying_power):,.2f}")
        print(f"  Cash: ${float(account.cash):,.2f}")
        
        return api
        
    except Exception as e:
        print(f"[ERROR] Failed to connect to Alpaca: {str(e)}")
        return None

def place_dee_bot_orders_alpaca(api):
    """Place DEE-BOT orders through Alpaca API"""
    
    print("\n" + "=" * 70)
    print("PLACING DEE-BOT ORDERS VIA ALPACA")
    print("=" * 70)
    
    # Load morning research report
    report_path = Path("data/research_reports/daily_report_2025-09-10.json")
    if not report_path.exists():
        print("[ERROR] Morning research report not found!")
        return False
    
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    recommendations = report.get("recommendations", [])
    watchlist = report.get("watchlist_analysis", {})
    
    orders_placed = []
    
    for rec in recommendations:
        if rec["action"] == "BUY":
            ticker = rec["ticker"]
            stock_data = watchlist.get(ticker, {})
            current_price = stock_data.get("price", 0)
            
            print(f"\n[PLACING ORDER] {ticker}")
            print(f"  Current Price: ${current_price:.2f}")
            print(f"  Signal: {rec['action']}")
            print(f"  Reason: {rec['reason']}")
            
            try:
                # Place limit order slightly above market price
                limit_price = round(current_price * 1.001, 2)
                
                # Submit order to Alpaca
                order = api.submit_order(
                    symbol=ticker,
                    qty=100,  # Conservative position size
                    side='buy',
                    type='limit',
                    time_in_force='day',
                    limit_price=limit_price,
                    order_class='bracket',  # Bracket order for stop loss and take profit
                    stop_loss={'stop_price': round(current_price * 0.97, 2)},  # 3% stop loss
                    take_profit={'limit_price': round(current_price * 1.05, 2)}  # 5% take profit
                )
                
                print(f"  [SUCCESS] Order placed!")
                print(f"    Order ID: {order.id}")
                print(f"    Status: {order.status}")
                print(f"    Qty: {order.qty}")
                print(f"    Limit Price: ${float(order.limit_price):.2f}")
                print(f"    Stop Loss: ${round(current_price * 0.97, 2):.2f}")
                print(f"    Take Profit: ${round(current_price * 1.05, 2):.2f}")
                
                orders_placed.append({
                    "order_id": order.id,
                    "ticker": ticker,
                    "qty": order.qty,
                    "side": order.side,
                    "type": order.type,
                    "limit_price": float(order.limit_price),
                    "status": order.status,
                    "submitted_at": order.submitted_at,
                    "stop_loss": round(current_price * 0.97, 2),
                    "take_profit": round(current_price * 1.05, 2)
                })
                
            except Exception as e:
                print(f"  [ERROR] Failed to place order: {str(e)}")
    
    # Save order log
    if orders_placed:
        log_file = f"ALPACA_ORDERS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "bot": "DEE-BOT",
            "broker": "Alpaca",
            "mode": "Paper Trading",
            "orders": orders_placed
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2, default=str)
        
        print("\n" + "=" * 70)
        print("ORDER SUMMARY")
        print("=" * 70)
        print(f"  Total Orders Placed: {len(orders_placed)}")
        print(f"  Log File: {log_file}")
        print("\n[INFO] Orders should now be visible in your Alpaca dashboard")
        print("  URL: https://app.alpaca.markets/paper/dashboard/overview")
        
        return True
    
    return False

def check_existing_positions(api):
    """Check existing positions in Alpaca account"""
    
    print("\n[CHECKING EXISTING POSITIONS]")
    
    try:
        positions = api.list_positions()
        
        if positions:
            print("  Current Positions:")
            for position in positions:
                print(f"    {position.symbol}: {position.qty} shares @ ${float(position.avg_entry_price):.2f}")
                print(f"      Market Value: ${float(position.market_value):.2f}")
                print(f"      P&L: ${float(position.unrealized_pl):.2f}")
        else:
            print("  No open positions")
            
    except Exception as e:
        print(f"  [ERROR] Failed to fetch positions: {str(e)}")

def check_recent_orders(api):
    """Check recent orders"""
    
    print("\n[CHECKING RECENT ORDERS]")
    
    try:
        orders = api.list_orders(status='all', limit=5)
        
        if orders:
            print("  Recent Orders:")
            for order in orders:
                print(f"    {order.symbol}: {order.side} {order.qty} @ ${float(order.limit_price or 0):.2f}")
                print(f"      Status: {order.status}")
                print(f"      Submitted: {order.submitted_at}")
        else:
            print("  No recent orders")
            
    except Exception as e:
        print(f"  [ERROR] Failed to fetch orders: {str(e)}")

if __name__ == "__main__":
    print("\nDEE-BOT ALPACA ORDER PLACEMENT")
    print("=" * 70)
    
    # Connect to Alpaca
    api = connect_to_alpaca()
    
    if api:
        # Check existing positions and orders
        check_existing_positions(api)
        check_recent_orders(api)
        
        # Place new orders
        success = place_dee_bot_orders_alpaca(api)
        
        if success:
            print("\n[SUCCESS] Orders have been placed via Alpaca Paper Trading")
            print("[INFO] Check your Alpaca dashboard to see the orders")
        else:
            print("\n[INFO] No orders were placed")
    else:
        print("\n[ERROR] Could not connect to Alpaca. Please configure API credentials.")