"""
Execute RCAT Trade for SHORGAN-BOT
Based on today's ChatGPT catalyst recommendation
"""

import os
import sys
import time
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def execute_rcat_trade():
    """Execute RCAT long position for SHORGAN-BOT"""
    
    # SHORGAN-BOT API ONLY
    api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY_SHORGAN'),
        os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
        'https://paper-api.alpaca.markets',
        api_version='v2'
    )
    
    print("="*60)
    print("EXECUTING RCAT TRADE - SHORGAN-BOT")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Get account info
    account = api.get_account()
    portfolio_value = float(account.portfolio_value)
    cash = float(account.cash)
    buying_power = float(account.buying_power)
    
    print(f"\nAccount Status:")
    print(f"Portfolio Value: ${portfolio_value:,.2f}")
    print(f"Cash: ${cash:,.2f}")
    print(f"Buying Power: ${buying_power:,.2f}")
    
    # Check if we have positive buying power after cleanup
    if buying_power <= 0:
        print("\n[ERROR] Insufficient buying power. Need to close more positions.")
        return False
    
    # Get RCAT quote
    try:
        quote = api.get_latest_quote('RCAT')
        current_price = quote.ask_price if quote.ask_price > 0 else quote.bid_price
        
        print(f"\nRCAT Current Price: ${current_price:.2f}")
        
        # Calculate position size (10% of portfolio as per recommendation)
        position_size = portfolio_value * 0.10
        shares = int(position_size / current_price)
        
        # Ensure we don't exceed buying power
        max_shares = int(buying_power / current_price)
        shares = min(shares, max_shares)
        
        if shares <= 0:
            print("[ERROR] Cannot buy any shares with current buying power")
            return False
        
        print(f"\nTrade Details:")
        print(f"Position Size: ${position_size:,.2f} (10% of portfolio)")
        print(f"Shares to Buy: {shares}")
        print(f"Total Cost: ${shares * current_price:,.2f}")
        
        # Execute if price is in target range (11.30-11.50 or current if close)
        if current_price <= 12.00:  # Slightly relaxed from original 11.50
            # Place market order
            order = api.submit_order(
                symbol='RCAT',
                qty=shares,
                side='buy',
                type='market',
                time_in_force='day'
            )
            
            print(f"\n[SUCCESS] Order placed!")
            print(f"Order ID: {order.id}")
            print(f"Symbol: RCAT")
            print(f"Quantity: {shares} shares")
            print(f"Type: MARKET BUY")
            
            # Wait for fill
            time.sleep(3)
            
            # Set stop loss at $9.80
            stop_order = api.submit_order(
                symbol='RCAT',
                qty=shares,
                side='sell',
                type='stop',
                time_in_force='gtc',
                stop_price=9.80
            )
            
            print(f"\n[SUCCESS] Stop loss set at $9.80")
            print(f"Stop Order ID: {stop_order.id}")
            
            print("\n" + "="*60)
            print("RCAT TRADE COMPLETE")
            print("Catalyst: Unusual call flow, bullish options activity")
            print("Target 1: $13.50 | Target 2: $15.00")
            print("="*60)
            
            return True
            
        else:
            print(f"\n[SKIP] Price ${current_price:.2f} above entry range")
            print("Will monitor for better entry")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Failed to execute RCAT trade: {e}")
        return False

def check_final_status():
    """Check final account status after trades"""
    api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY_SHORGAN'),
        os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
        'https://paper-api.alpaca.markets',
        api_version='v2'
    )
    
    account = api.get_account()
    positions = api.list_positions()
    
    print("\n" + "="*60)
    print("FINAL SHORGAN-BOT STATUS")
    print("="*60)
    
    print(f"\nPortfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"Cash: ${float(account.cash):,.2f}")
    print(f"Number of Positions: {len(positions)}")
    
    # Check for micro-cap compliance
    large_caps = []
    for pos in positions:
        if pos.symbol in ['SPY', 'NVDA', 'AMD', 'ORCL', 'GOOGL', 'MSFT', 'AAPL']:
            large_caps.append(pos.symbol)
    
    if large_caps:
        print(f"\n[WARNING] Still holding large-caps: {', '.join(large_caps)}")
    else:
        print("\n[OK] Portfolio compliant with micro-cap focus")

if __name__ == "__main__":
    # Execute RCAT trade
    success = execute_rcat_trade()
    
    # Check final status
    check_final_status()