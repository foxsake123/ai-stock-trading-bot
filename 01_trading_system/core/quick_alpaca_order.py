"""
Quick Alpaca Order Placement for DEE-BOT
Place NVDA order based on morning recommendation
"""

import alpaca_trade_api as tradeapi

# IMPORTANT: Replace with your actual secret key
API_KEY = "PK47VDXAY430CS436NC4"
SECRET_KEY = "YOUR_SECRET_KEY_HERE"  # <-- REPLACE THIS
BASE_URL = "https://paper-api.alpaca.markets"

def place_nvda_order():
    """Place NVDA buy order for DEE-BOT"""
    
    print("DEE-BOT ALPACA ORDER - NVDA")
    print("=" * 50)
    
    if SECRET_KEY == "YOUR_SECRET_KEY_HERE":
        print("\n[ERROR] Please update SECRET_KEY in this file with your actual secret key")
        print("Get it from: https://app.alpaca.markets/paper/dashboard/overview")
        print("Click on 'Your API Keys' in the left sidebar")
        return
    
    try:
        # Connect to Alpaca
        api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
        
        # Check account
        account = api.get_account()
        print(f"\n[CONNECTED] Alpaca Paper Trading")
        print(f"  Buying Power: ${float(account.buying_power):,.2f}")
        
        # Place NVDA order
        print(f"\n[PLACING ORDER] NVDA")
        order = api.submit_order(
            symbol='NVDA',
            qty=100,
            side='buy',
            type='limit',
            time_in_force='day',
            limit_price=176.00,  # Slightly above current price
            order_class='bracket',
            stop_loss={'stop_price': 170.40},  # 3% stop loss
            take_profit={'limit_price': 184.45}  # 5% take profit
        )
        
        print(f"\n[SUCCESS] Order Placed!")
        print(f"  Order ID: {order.id}")
        print(f"  Symbol: NVDA")
        print(f"  Quantity: 100 shares")
        print(f"  Limit Price: $176.00")
        print(f"  Stop Loss: $170.40")
        print(f"  Take Profit: $184.45")
        print(f"\n[INFO] Check your Alpaca dashboard to see the order")
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")

if __name__ == "__main__":
    place_nvda_order()