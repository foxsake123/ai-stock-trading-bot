"""
Enhanced Alpaca Trading Module with Bot-Specific API Keys
Supports multiple trading bots with separate accounts
Date: January 10, 2025
"""

import json
import os
from datetime import datetime
from pathlib import Path
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

class AlpacaBotTrader:
    """Enhanced Alpaca trader with bot-specific API support"""
    
    def __init__(self, bot_name: str = "DEE"):
        """
        Initialize trader for specific bot
        
        Args:
            bot_name: Either "DEE" or "SHORGAN"
        """
        self.bot_name = bot_name.upper()
        self.api = None
        self.account = None
        
    def connect_to_alpaca(self) -> Optional[tradeapi.REST]:
        """Connect to Alpaca API with bot-specific credentials"""
        
        # Get bot-specific API credentials
        if self.bot_name == "DEE":
            api_key = os.getenv('ALPACA_API_KEY_DEE')
            secret_key = os.getenv('ALPACA_SECRET_KEY_DEE')
        elif self.bot_name == "SHORGAN":
            api_key = os.getenv('ALPACA_API_KEY_SHORGAN')
            secret_key = os.getenv('ALPACA_SECRET_KEY_SHORGAN')
        else:
            # Fallback to default keys
            api_key = os.getenv('APCA_API_KEY_ID') or os.getenv('ALPACA_API_KEY')
            secret_key = os.getenv('APCA_API_SECRET_KEY') or os.getenv('ALPACA_SECRET_KEY')
        
        if not api_key or not secret_key:
            print(f"[ERROR] Alpaca API credentials not found for {self.bot_name}-BOT")
            print(f"[INFO] Please set ALPACA_API_KEY_{self.bot_name} and ALPACA_SECRET_KEY_{self.bot_name} in .env file")
            print("\nTo get your paper trading API keys:")
            print("1. Go to https://app.alpaca.markets/paper/dashboard/overview")
            print("2. Click on 'API Keys' in the left sidebar")
            print("3. Generate new keys if needed")
            print("4. Add to .env file:")
            print(f"   ALPACA_API_KEY_{self.bot_name}=your_key_here")
            print(f"   ALPACA_SECRET_KEY_{self.bot_name}=your_secret_here")
            return None
        
        # Use paper trading endpoint
        base_url = 'https://paper-api.alpaca.markets'
        
        try:
            self.api = tradeapi.REST(
                api_key,
                secret_key,
                base_url,
                api_version='v2'
            )
            
            # Test connection
            self.account = self.api.get_account()
            print(f"[SUCCESS] Connected to Alpaca Paper Trading for {self.bot_name}-BOT")
            print(f"  Account Status: {self.account.status}")
            print(f"  Buying Power: ${float(self.account.buying_power):,.2f}")
            print(f"  Portfolio Value: ${float(self.account.portfolio_value):,.2f}")
            
            return self.api
            
        except Exception as e:
            print(f"[ERROR] Failed to connect to Alpaca: {str(e)}")
            return None
    
    def place_order(self, symbol: str, qty: int, side: str = 'buy', 
                   order_type: str = 'market', time_in_force: str = 'day') -> Optional[Dict]:
        """
        Place an order via Alpaca
        
        Args:
            symbol: Stock symbol
            qty: Number of shares
            side: 'buy' or 'sell'
            order_type: 'market', 'limit', 'stop', 'stop_limit'
            time_in_force: 'day', 'gtc', 'ioc', 'fok'
        
        Returns:
            Order details or None if failed
        """
        if not self.api:
            print("[ERROR] Not connected to Alpaca")
            return None
        
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force
            )
            
            print(f"[SUCCESS] Order placed for {self.bot_name}-BOT:")
            print(f"  Symbol: {symbol}")
            print(f"  Side: {side}")
            print(f"  Quantity: {qty}")
            print(f"  Order ID: {order.id}")
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': order.qty,
                'side': order.side,
                'type': order.type,
                'status': order.status,
                'created_at': order.created_at
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to place order: {str(e)}")
            return None
    
    def get_positions(self) -> list:
        """Get current positions"""
        if not self.api:
            return []
        
        try:
            positions = self.api.list_positions()
            return positions
        except Exception as e:
            print(f"[ERROR] Failed to get positions: {str(e)}")
            return []
    
    def get_orders(self, status: str = 'open') -> list:
        """Get orders by status"""
        if not self.api:
            return []
        
        try:
            orders = self.api.list_orders(status=status)
            return orders
        except Exception as e:
            print(f"[ERROR] Failed to get orders: {str(e)}")
            return []
    
    def cancel_all_orders(self) -> bool:
        """Cancel all open orders"""
        if not self.api:
            return False
        
        try:
            self.api.cancel_all_orders()
            print(f"[SUCCESS] All open orders cancelled for {self.bot_name}-BOT")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to cancel orders: {str(e)}")
            return False


def place_dee_bot_orders():
    """Place DEE-BOT orders using bot-specific credentials"""
    
    print("=" * 70)
    print("DEE-BOT ORDER PLACEMENT SYSTEM")
    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    # Initialize DEE-BOT trader
    trader = AlpacaBotTrader("DEE")
    
    # Connect to Alpaca
    if not trader.connect_to_alpaca():
        return False
    
    # Example orders (replace with your actual trading logic)
    orders = [
        {"symbol": "AAPL", "qty": 10, "side": "buy"},
        {"symbol": "MSFT", "qty": 5, "side": "buy"},
        {"symbol": "GOOGL", "qty": 3, "side": "buy"}
    ]
    
    print("\n[INFO] Placing orders...")
    for order in orders:
        trader.place_order(**order)
    
    # Show current positions
    print("\n[INFO] Current positions:")
    positions = trader.get_positions()
    for pos in positions:
        print(f"  {pos.symbol}: {pos.qty} shares @ ${float(pos.avg_entry_price):.2f}")
    
    return True


def place_shorgan_bot_orders():
    """Place SHORGAN-BOT orders using bot-specific credentials"""
    
    print("=" * 70)
    print("SHORGAN-BOT ORDER PLACEMENT SYSTEM")
    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    # Initialize SHORGAN-BOT trader
    trader = AlpacaBotTrader("SHORGAN")
    
    # Connect to Alpaca
    if not trader.connect_to_alpaca():
        return False
    
    # Example catalyst-based orders (replace with your actual trading logic)
    orders = [
        {"symbol": "NVDA", "qty": 5, "side": "buy"},
        {"symbol": "AMD", "qty": 10, "side": "buy"},
        {"symbol": "TSLA", "qty": 2, "side": "buy"}
    ]
    
    print("\n[INFO] Placing catalyst-driven orders...")
    for order in orders:
        trader.place_order(**order)
    
    # Show current positions
    print("\n[INFO] Current positions:")
    positions = trader.get_positions()
    for pos in positions:
        print(f"  {pos.symbol}: {pos.qty} shares @ ${float(pos.avg_entry_price):.2f}")
    
    return True


def main():
    """Main entry point with bot selection"""
    import sys
    
    print("=" * 70)
    print("ALPACA MULTI-BOT TRADING SYSTEM")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        bot = sys.argv[1].upper()
        if bot == "DEE":
            place_dee_bot_orders()
        elif bot == "SHORGAN":
            place_shorgan_bot_orders()
        else:
            print(f"[ERROR] Unknown bot: {bot}")
            print("Usage: python place_alpaca_orders_enhanced.py [DEE|SHORGAN]")
    else:
        print("\nSelect bot to trade:")
        print("1. DEE-BOT (Institutional Strategy)")
        print("2. SHORGAN-BOT (Catalyst Strategy)")
        print("3. Both Bots")
        
        choice = input("\nEnter choice (1/2/3): ").strip()
        
        if choice == "1":
            place_dee_bot_orders()
        elif choice == "2":
            place_shorgan_bot_orders()
        elif choice == "3":
            place_dee_bot_orders()
            print("\n" + "-" * 70 + "\n")
            place_shorgan_bot_orders()
        else:
            print("[ERROR] Invalid choice")


if __name__ == "__main__":
    main()