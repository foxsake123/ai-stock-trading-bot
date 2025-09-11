"""
Place SHORGAN-BOT Orders via Alpaca Paper Trading
Date: January 10, 2025
Production trading strategy with larger positions
"""

import alpaca_trade_api as tradeapi
import json
from datetime import datetime
from pathlib import Path

# SHORGAN-BOT Alpaca Credentials (Updated)
SHORGAN_API_KEY = "PKJRLSB2MFEJUSK6UK2E"
SHORGAN_SECRET_KEY = "QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic"
BASE_URL = "https://paper-api.alpaca.markets"

def connect_shorgan_alpaca():
    """Connect to Alpaca with Shorgan-bot credentials"""
    
    print("SHORGAN-BOT ALPACA CONNECTION")
    print("=" * 60)
    
    try:
        api = tradeapi.REST(
            SHORGAN_API_KEY,
            SHORGAN_SECRET_KEY,
            BASE_URL,
            api_version='v2'
        )
        
        # Test connection
        account = api.get_account()
        print(f"[SUCCESS] Connected to Shorgan-Bot Alpaca Account")
        print(f"  Account Status: {account.status}")
        print(f"  Buying Power: ${float(account.buying_power):,.2f}")
        print(f"  Cash: ${float(account.cash):,.2f}")
        print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
        
        return api
        
    except Exception as e:
        print(f"[ERROR] Failed to connect: {str(e)}")
        return None

def place_shorgan_orders(api):
    """Place Shorgan-bot orders based on morning research"""
    
    print("\n" + "=" * 60)
    print("PLACING SHORGAN-BOT ORDERS")
    print("Strategy: Production Trading with Larger Positions")
    print("=" * 60)
    
    # Load morning research report
    report_path = Path("data/research_reports/daily_report_2025-09-10.json")
    if report_path.exists():
        with open(report_path, 'r') as f:
            report = json.load(f)
        print(f"\n[INFO] Using research from: {report['report_date']} {report['report_time']}")
    
    orders_placed = []
    
    # Order 1: NVDA - Larger position based on momentum signal
    try:
        print(f"\n[ORDER 1] NVDA - Primary Position")
        print("  Based on: 2.98% positive momentum signal")
        
        nvda_order = api.submit_order(
            symbol='NVDA',
            qty=150,  # Larger position for Shorgan-bot
            side='buy',
            type='limit',
            time_in_force='day',
            limit_price=176.00,  # Slightly above market
            order_class='bracket',
            stop_loss={'stop_price': 169.00},  # Tighter stop for larger position
            take_profit={'limit_price': 189.00}  # Higher target (7.5%)
        )
        
        print(f"  [SUCCESS] NVDA Order Placed")
        print(f"    Order ID: {nvda_order.id}")
        print(f"    Quantity: 150 shares")
        print(f"    Limit Price: $176.00")
        print(f"    Stop Loss: $169.00 (3.8% risk)")
        print(f"    Take Profit: $189.00 (7.5% target)")
        
        orders_placed.append({
            "ticker": "NVDA",
            "order_id": nvda_order.id,
            "qty": 150,
            "limit_price": 176.00,
            "stop_loss": 169.00,
            "take_profit": 189.00
        })
        
    except Exception as e:
        print(f"  [ERROR] NVDA order failed: {str(e)}")
    
    # Order 2: SPY - Portfolio hedge/diversification
    try:
        print(f"\n[ORDER 2] SPY - Portfolio Diversification")
        print("  Purpose: Index exposure and portfolio balance")
        
        spy_order = api.submit_order(
            symbol='SPY',
            qty=20,
            side='buy',
            type='market',  # Market order for immediate execution
            time_in_force='day'
        )
        
        print(f"  [SUCCESS] SPY Order Placed")
        print(f"    Order ID: {spy_order.id}")
        print(f"    Quantity: 20 shares")
        print(f"    Type: Market Order")
        
        orders_placed.append({
            "ticker": "SPY",
            "order_id": spy_order.id,
            "qty": 20,
            "type": "market"
        })
        
    except Exception as e:
        print(f"  [ERROR] SPY order failed: {str(e)}")
    
    # Save order log
    if orders_placed:
        log_file = f"SHORGAN_BOT_ORDERS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "bot": "SHORGAN-BOT",
            "strategy": "Production Trading",
            "broker": "Alpaca Paper Trading",
            "orders": orders_placed,
            "estimated_capital": (150 * 176.00) + (20 * 580.00),  # Rough estimate
            "notes": "Larger positions with tighter risk management"
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print("\n" + "=" * 60)
        print("ORDER SUMMARY")
        print("=" * 60)
        print(f"  Total Orders Placed: {len(orders_placed)}")
        print(f"  Estimated Capital Deployed: ${log_data['estimated_capital']:,.2f}")
        print(f"  Log File: {log_file}")
        
    return orders_placed

def check_positions_and_orders(api):
    """Check current positions and pending orders"""
    
    print("\n" + "=" * 60)
    print("ACCOUNT STATUS CHECK")
    print("=" * 60)
    
    # Check positions
    try:
        positions = api.list_positions()
        if positions:
            print("\n[CURRENT POSITIONS]")
            for pos in positions:
                print(f"  {pos.symbol}: {pos.qty} shares @ ${float(pos.avg_entry_price):.2f}")
                print(f"    Market Value: ${float(pos.market_value):,.2f}")
                print(f"    P&L: ${float(pos.unrealized_pl):,.2f}")
        else:
            print("\n[POSITIONS] No open positions")
    except Exception as e:
        print(f"\n[ERROR] Could not fetch positions: {str(e)}")
    
    # Check recent orders
    try:
        orders = api.list_orders(status='all', limit=10)
        if orders:
            print("\n[RECENT ORDERS]")
            for order in orders:
                print(f"  {order.symbol}: {order.side.upper()} {order.qty} @ ${float(order.limit_price or 0):.2f}")
                print(f"    Status: {order.status}")
                print(f"    Order ID: {order.id}")
        else:
            print("\n[ORDERS] No recent orders")
    except Exception as e:
        print(f"\n[ERROR] Could not fetch orders: {str(e)}")

if __name__ == "__main__":
    print("\nSHORGAN-BOT ALPACA TRADING SYSTEM")
    print("Production Strategy with Larger Positions")
    print("=" * 60)
    
    # Connect to Alpaca
    api = connect_shorgan_alpaca()
    
    if api:
        # Check current status
        check_positions_and_orders(api)
        
        # Place new orders
        orders = place_shorgan_orders(api)
        
        if orders:
            print("\n" + "=" * 60)
            print("[SUCCESS] Shorgan-Bot orders have been placed")
            print("[INFO] Check Alpaca dashboard for order status")
            print("URL: https://app.alpaca.markets/paper/dashboard/overview")
            print("=" * 60)
        else:
            print("\n[INFO] No orders were placed")
    else:
        print("\n[ERROR] Could not connect to Alpaca")
        print("Please check API credentials")