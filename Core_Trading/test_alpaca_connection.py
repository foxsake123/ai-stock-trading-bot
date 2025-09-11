#!/usr/bin/env python3
"""
Test Alpaca API connection
Verifies paper trading account access
"""
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

def test_connection():
    """Test Alpaca paper trading connection"""
    
    # Get credentials
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    
    if not api_key or not secret_key:
        print("[ERROR] Alpaca credentials not found!")
        print("Please add to .env file:")
        print("  ALPACA_API_KEY=your_key_here")
        print("  ALPACA_SECRET_KEY=your_secret_here")
        return False
    
    try:
        # Connect to paper trading
        api = tradeapi.REST(
            key_id=api_key,
            secret_key=secret_key,
            base_url="https://paper-api.alpaca.markets",
            api_version='v2'
        )
        
        # Test connection
        account = api.get_account()
        
        print("[OK] Connected to Alpaca Paper Trading!")
        print("-" * 40)
        print(f"Account Number: {account.account_number}")
        print(f"Account Balance: ${float(account.portfolio_value):,.2f}")
        print(f"Buying Power: ${float(account.buying_power):,.2f}")
        print(f"Cash: ${float(account.cash):,.2f}")
        print(f"Pattern Day Trader: {account.pattern_day_trader}")
        print(f"Trading Blocked: {account.trading_blocked}")
        print(f"Account Status: {account.status}")
        print("-" * 40)
        
        # Check if market is open
        clock = api.get_clock()
        if clock.is_open:
            print("[OK] Market is OPEN")
        else:
            print(f"[INFO] Market is CLOSED")
            print(f"Next open: {clock.next_open}")
            print(f"Next close: {clock.next_close}")
        
        # List current positions
        positions = api.list_positions()
        if positions:
            print(f"\nCurrent Positions ({len(positions)}):")
            for p in positions:
                print(f"  {p.symbol}: {p.qty} shares @ ${float(p.avg_entry_price):.2f}")
        else:
            print("\n[INFO] No open positions")
        
        # Show recent orders
        orders = api.list_orders(limit=5)
        if orders:
            print(f"\nRecent Orders:")
            for order in orders:
                print(f"  {order.created_at}: {order.side} {order.qty} {order.symbol} - {order.status}")
        else:
            print("\n[INFO] No recent orders")
        
        print("\n[SUCCESS] Alpaca connection test passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to connect to Alpaca: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify API keys are correct")
        print("3. Ensure you're using paper trading keys")
        print("4. Check if Alpaca services are online")
        return False

if __name__ == "__main__":
    test_connection()