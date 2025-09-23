"""
Real-Time Position Monitor
Check status and P&L for both trading bots
"""

import alpaca_trade_api as tradeapi
import json
from datetime import datetime
import yfinance as yf

# Bot credentials
DEE_BOT_API = "PK6FZK4DAQVTD7DYVH78"
DEE_BOT_SECRET = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"

SHORGAN_API = "PKJRLSB2MFEJUSK6UK2E" 
SHORGAN_SECRET = "QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic"

BASE_URL = "https://paper-api.alpaca.markets"

def connect_to_bot(api_key, secret_key, bot_name):
    """Connect to Alpaca account"""
    try:
        api = tradeapi.REST(api_key, secret_key, BASE_URL, api_version='v2')
        account = api.get_account()
        print(f"\n[{bot_name}] Connected Successfully")
        print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"  Buying Power: ${float(account.buying_power):,.2f}")
        return api
    except Exception as e:
        print(f"\n[{bot_name}] Connection Failed: {str(e)}")
        return None

def get_current_prices(symbols):
    """Get current market prices"""
    try:
        tickers = yf.Tickers(' '.join(symbols))
        prices = {}
        for symbol in symbols:
            ticker = tickers.tickers[symbol]
            hist = ticker.history(period="1d")
            if not hist.empty:
                prices[symbol] = round(hist['Close'].iloc[-1], 2)
        return prices
    except Exception as e:
        print(f"Error getting prices: {str(e)}")
        return {}

def check_positions(api, bot_name):
    """Check all positions for a bot"""
    try:
        positions = api.list_positions()
        orders = api.list_orders(status='all', limit=20)
        
        print(f"\n{'='*60}")
        print(f"{bot_name.upper()} POSITION STATUS")
        print(f"{'='*60}")
        
        if positions:
            total_value = 0
            total_pnl = 0
            
            print(f"\n[ACTIVE POSITIONS]")
            for pos in positions:
                market_value = float(pos.market_value)
                unrealized_pnl = float(pos.unrealized_pl)
                unrealized_pct = float(pos.unrealized_plpc) * 100
                
                print(f"  {pos.symbol}:")
                print(f"    Shares: {pos.qty}")
                print(f"    Avg Price: ${float(pos.avg_entry_price):.2f}")
                print(f"    Current: ${float(pos.market_value) / float(pos.qty):.2f}")
                print(f"    Market Value: ${market_value:,.2f}")
                print(f"    P&L: ${unrealized_pnl:,.2f} ({unrealized_pct:+.2f}%)")
                
                total_value += market_value
                total_pnl += unrealized_pnl
                
            print(f"\n[PORTFOLIO SUMMARY]")
            print(f"  Total Market Value: ${total_value:,.2f}")
            print(f"  Total P&L: ${total_pnl:,.2f}")
            
        else:
            print("\n[POSITIONS] No open positions")
        
        # Check recent orders
        print(f"\n[RECENT ORDERS]")
        pending_orders = [o for o in orders if o.status in ['new', 'partially_filled', 'accepted']]
        filled_orders = [o for o in orders if o.status == 'filled'][:5]
        
        if pending_orders:
            print("  PENDING:")
            for order in pending_orders:
                side = order.side.upper()
                price = f"${float(order.limit_price):.2f}" if order.limit_price else "MARKET"
                print(f"    {order.symbol}: {side} {order.qty} @ {price} ({order.status})")
        
        if filled_orders:
            print("  RECENT FILLS:")
            for order in filled_orders[:3]:
                side = order.side.upper()
                price = f"${float(order.filled_avg_price or 0):.2f}"
                print(f"    {order.symbol}: {side} {order.qty} @ {price}")
        
        return positions, orders
        
    except Exception as e:
        print(f"Error checking positions: {str(e)}")
        return [], []

def load_expected_positions():
    """Load expected positions from trade logs"""
    expected = {
        'DEE-BOT': {
            'AAPL': {'qty': 61, 'entry': 178.50, 'stop': 173.50, 'target': 188.50},
            'MSFT': {'qty': 29, 'entry': 412.00, 'stop': 401.38, 'target': 438.63},
            'SPY': {'qty': -6, 'entry': 545.00, 'stop': 553.75, 'target': 523.13},
            'JPM': {'qty': 71, 'entry': 200.00, 'stop': 195.63, 'target': 210.94}
        },
        'SHORGAN-BOT': {
            'PLTR': {'qty': 520, 'entry': 14.50, 'stop': 13.30, 'target': 16.00},
            'CVNA': {'qty': -100, 'entry': 48.00, 'stop': 51.50, 'target': 42.00},
            'CRWD': {'qty': 36, 'entry': 210.00, 'stop': 199.50, 'target': 225.00},
            'UPST': {'qty': -100, 'entry': 30.00, 'stop': 31.50, 'target': 27.00}
        }
    }
    return expected

def main():
    """Main monitoring function"""
    print("TRADING BOT POSITION MONITOR")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Connect to both bots
    dee_api = connect_to_bot(DEE_BOT_API, DEE_BOT_SECRET, "DEE-BOT")
    shorgan_api = connect_to_bot(SHORGAN_API, SHORGAN_SECRET, "SHORGAN-BOT")
    
    # Load expected positions
    expected = load_expected_positions()
    
    # Check DEE-BOT positions
    if dee_api:
        dee_positions, dee_orders = check_positions(dee_api, "DEE-BOT")
    
    # Check SHORGAN-BOT positions  
    if shorgan_api:
        shorgan_positions, shorgan_orders = check_positions(shorgan_api, "SHORGAN-BOT")
    
    # Get current market prices
    all_symbols = ['AAPL', 'MSFT', 'SPY', 'JPM', 'PLTR', 'CVNA', 'CRWD', 'UPST']
    current_prices = get_current_prices(all_symbols)
    
    if current_prices:
        print(f"\n{'='*60}")
        print("CURRENT MARKET PRICES")
        print(f"{'='*60}")
        for symbol, price in current_prices.items():
            print(f"  {symbol}: ${price:.2f}")
    
    # Summary
    print(f"\n{'='*60}")
    print("MONITORING STATUS")
    print(f"{'='*60}")
    print(f"[OK] DEE-BOT: {'Connected' if dee_api else 'Failed'}")
    print(f"[OK] SHORGAN-BOT: {'Connected' if shorgan_api else 'Failed'}")
    print(f"[OK] Market Data: {'Live' if current_prices else 'Failed'}")
    print(f"[TIME] Last Update: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()