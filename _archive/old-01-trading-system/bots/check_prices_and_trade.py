"""
Quick price check and trade execution with adjusted ranges
"""
import os
import sys
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Initialize API
api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY_SHORGAN'),
    os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    'https://paper-api.alpaca.markets',
    api_version='v2'
)

def check_prices():
    """Check current prices for all target stocks"""
    symbols = ['DAKT', 'CHWY', 'AXSM', 'VNCE', 'NCNO', 'SHC']
    
    print(f"\n{'='*60}")
    print(f"PRICE CHECK - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    prices = {}
    for symbol in symbols:
        try:
            # Try getting latest trade
            latest_trade = api.get_latest_trade(symbol)
            price = latest_trade.price if latest_trade else 0
            
            # If no trade, try quote
            if price == 0:
                quote = api.get_latest_quote(symbol)
                if quote:
                    price = (quote.bid_price + quote.ask_price) / 2 if quote.bid_price > 0 else quote.ask_price
            
            prices[symbol] = price
            print(f"{symbol}: ${price:.2f}")
            
        except Exception as e:
            print(f"{symbol}: Error - {e}")
            prices[symbol] = 0
    
    return prices

def place_adjusted_orders(prices):
    """Place orders with adjusted ranges based on current prices"""
    account = api.get_account()
    portfolio_value = float(account.portfolio_value)
    
    print(f"\n{'='*60}")
    print(f"PLACING ADJUSTED ORDERS")
    print(f"Portfolio Value: ${portfolio_value:,.2f}")
    print(f"{'='*60}\n")
    
    trades = []
    
    # CHWY - Adjust to current price ($36)
    if prices.get('CHWY', 0) > 0:
        chwy_price = prices['CHWY']
        if 35 <= chwy_price <= 38.50:  # Relaxed range
            shares = int((portfolio_value * 0.15) / chwy_price)
            if shares > 0:
                trades.append({
                    'symbol': 'CHWY',
                    'qty': shares,
                    'side': 'buy',
                    'type': 'market',
                    'time_in_force': 'day'
                })
                print(f"[OK] CHWY: Buy {shares} shares at market (~${chwy_price:.2f})")
    
    # NCNO - Adjust short entry
    if prices.get('NCNO', 0) > 0:
        ncno_price = prices['NCNO']
        if 29.50 <= ncno_price <= 31.00:  # Relaxed range
            shares = int((portfolio_value * 0.10) / ncno_price)
            if shares > 0:
                trades.append({
                    'symbol': 'NCNO',
                    'qty': shares,
                    'side': 'sell',
                    'type': 'market',
                    'time_in_force': 'day'
                })
                print(f"[OK] NCNO: Short {shares} shares at market (~${ncno_price:.2f})")
    
    # SHC - Adjust short entry
    if prices.get('SHC', 0) > 0:
        shc_price = prices['SHC']
        if 15.00 <= shc_price <= 16.00:  # Relaxed range
            shares = int((portfolio_value * 0.10) / shc_price)
            if shares > 0:
                trades.append({
                    'symbol': 'SHC',
                    'qty': shares,
                    'side': 'sell',
                    'type': 'market',
                    'time_in_force': 'day'
                })
                print(f"[OK] SHC: Short {shares} shares at market (~${shc_price:.2f})")
    
    # Place orders for stocks with valid prices
    # DAKT - price is $20.89, in buy range
    if prices.get('DAKT', 0) > 0:
        dakt_price = prices['DAKT']
        if 20.50 <= dakt_price <= 22.00:  # Adjusted range
            shares = int((portfolio_value * 0.15) / dakt_price)
            if shares > 0:
                trades.append({
                    'symbol': 'DAKT',
                    'qty': shares,
                    'side': 'buy',
                    'type': 'market',
                    'time_in_force': 'day'
                })
                print(f"[OK] DAKT: Buy {shares} shares at market (~${dakt_price:.2f})")
    
    # AXSM - price is $123.01, below target but could limit buy
    if prices.get('AXSM', 0) > 0:
        axsm_price = prices['AXSM']
        if axsm_price < 130:  # Below our target, good entry
            shares = int((portfolio_value * 0.10) / axsm_price)
            if shares > 0:
                trades.append({
                    'symbol': 'AXSM',
                    'qty': shares,
                    'side': 'buy',
                    'type': 'market',
                    'time_in_force': 'day'
                })
                print(f"[OK] AXSM: Buy {shares} shares at market (~${axsm_price:.2f})")
    
    # VNCE - price is $3.40, above our target but already moving
    if prices.get('VNCE', 0) > 0:
        vnce_price = prices['VNCE']
        if vnce_price > 3.00:  # Already hit first target, skip
            print(f"[SKIP] VNCE: Price ${vnce_price:.2f} already above target $3.00")
    
    # Execute trades
    if trades:
        print(f"\nExecuting {len(trades)} trades...")
        successful = 0
        for trade in trades:
            try:
                order = api.submit_order(**trade)
                print(f"  [SUCCESS] {trade['symbol']} order placed: {order.id}")
                successful += 1
            except Exception as e:
                print(f"  [FAILED] {trade['symbol']} failed: {e}")
        
        print(f"\n{'='*60}")
        print(f"EXECUTION COMPLETE: {successful}/{len(trades)} orders placed")
        print(f"{'='*60}")
    else:
        print("No trades qualified for execution with current prices")
    
    return trades

def main():
    # Check if market is open
    clock = api.get_clock()
    if not clock.is_open:
        print("Market is closed!")
        return
    
    print("Market is OPEN - checking prices...")
    
    # Check prices
    prices = check_prices()
    
    # Place adjusted orders
    place_adjusted_orders(prices)

if __name__ == "__main__":
    main()