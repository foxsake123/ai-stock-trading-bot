"""
DEE-BOT Enhanced Trading Script
Institutional-style trading with bot-specific API keys
Date: January 10, 2025
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent / 'Core_Trading'))
sys.path.append(str(Path(__file__).parent.parent.parent / 'data'))
sys.path.append(str(Path(__file__).parent.parent.parent / 'agents'))

from Core_Trading.place_alpaca_orders_enhanced import AlpacaBotTrader
from data.enhanced_providers import EnhancedDataHub
import asyncio

def get_institutional_trades():
    """Generate institutional-style trades based on comprehensive analysis"""
    
    print("\n[INFO] Running institutional analysis...")
    
    # S&P 100 universe for institutional focus
    institutional_watchlist = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META",  # Tech giants
        "BRK.B", "JPM", "V", "MA", "BAC",         # Financials
        "JNJ", "UNH", "PFE", "ABBV", "MRK",       # Healthcare
        "XOM", "CVX", "COP",                       # Energy
        "PG", "KO", "PEP", "WMT", "COST"          # Consumer
    ]
    
    trades = []
    hub = EnhancedDataHub()
    
    async def analyze_stocks():
        for ticker in institutional_watchlist[:10]:  # Limit to top 10 for speed
            print(f"  Analyzing {ticker}...")
            
            try:
                # Get comprehensive data
                market_data = await hub.get_market_data(ticker)
                news = await hub.get_news(ticker, limit=5)
                
                # Simple institutional criteria
                score = 0
                reasons = []
                
                # Check P/E ratio (value investing)
                pe_ratio = market_data.get('pe_ratio', 0)
                if 10 < pe_ratio < 25:
                    score += 0.3
                    reasons.append(f"P/E ratio: {pe_ratio:.1f}")
                
                # Check market cap (prefer large cap)
                market_cap = market_data.get('market_cap', 0)
                if market_cap > 100_000_000_000:  # $100B+
                    score += 0.3
                    reasons.append("Large cap stability")
                
                # Check news sentiment
                if news and len(news) > 0:
                    score += 0.2
                    reasons.append(f"{len(news)} recent news articles")
                
                # Check price (momentum)
                price = market_data.get('price', 0)
                if price > 0:
                    score += 0.2
                    
                if score >= 0.6:  # Threshold for institutional interest
                    trades.append({
                        'symbol': ticker,
                        'qty': max(5, int(100 / price)) if price > 0 else 5,  # Position sizing
                        'side': 'buy',
                        'reason': ', '.join(reasons),
                        'score': score,
                        'price': price
                    })
                    
                    print(f"    ✓ {ticker}: Score {score:.2f} - {reasons[0] if reasons else 'Qualified'}")
                    
            except Exception as e:
                print(f"    ✗ Error analyzing {ticker}: {str(e)[:50]}")
                continue
    
    # Run async analysis
    asyncio.run(analyze_stocks())
    
    # Sort by score
    trades.sort(key=lambda x: x['score'], reverse=True)
    
    return trades[:5]  # Limit to top 5 trades

def place_dee_bot_orders():
    """Place DEE-BOT orders with institutional strategy"""
    
    print("=" * 70)
    print("DEE-BOT INSTITUTIONAL TRADING SYSTEM")
    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Strategy: Institutional accumulation patterns")
    print("=" * 70)
    
    # Initialize DEE-BOT trader
    trader = AlpacaBotTrader("DEE")
    
    # Connect to Alpaca
    if not trader.connect_to_alpaca():
        print("[ERROR] Failed to connect to Alpaca")
        return False
    
    # Get institutional-style trades
    trades = get_institutional_trades()
    
    if not trades:
        print("\n[INFO] No institutional opportunities found")
        return True
    
    print(f"\n[INFO] Found {len(trades)} institutional opportunities:")
    for trade in trades:
        print(f"  {trade['symbol']}: {trade['reason'][:60]}...")
        print(f"    Score: {trade['score']:.2f}, Qty: {trade['qty']} @ ${trade.get('price', 0):.2f}")
    
    # Place orders
    print("\n[INFO] Placing institutional orders...")
    successful_orders = []
    
    for trade in trades:
        print(f"\n  Placing order for {trade['symbol']}...")
        order = trader.place_order(
            symbol=trade['symbol'],
            qty=trade['qty'],
            side=trade['side']
        )
        
        if order:
            successful_orders.append(order)
            print(f"    ✓ Order placed: {trade['qty']} shares of {trade['symbol']}")
        else:
            print(f"    ✗ Failed to place order for {trade['symbol']}")
    
    # Show summary
    print("\n" + "=" * 70)
    print("ORDER SUMMARY")
    print("=" * 70)
    
    if successful_orders:
        print(f"Successfully placed {len(successful_orders)} orders:")
        for order in successful_orders:
            print(f"  - {order['symbol']}: {order['qty']} shares ({order['side']})")
    else:
        print("No orders were successfully placed")
    
    # Show current positions
    print("\n[INFO] Current DEE-BOT positions:")
    positions = trader.get_positions()
    total_value = 0
    total_pl = 0
    
    if positions:
        for pos in positions:
            value = float(pos.qty) * float(pos.current_price)
            total_value += value
            unrealized_pl = float(pos.unrealized_pl)
            total_pl += unrealized_pl
            pl_pct = float(pos.unrealized_plpc) * 100
            
            print(f"  {pos.symbol}: {pos.qty} shares @ ${float(pos.current_price):.2f}")
            print(f"    Cost Basis: ${float(pos.avg_entry_price):.2f}")
            print(f"    P&L: ${unrealized_pl:,.2f} ({pl_pct:+.2f}%)")
        
        print(f"\n  Total Position Value: ${total_value:,.2f}")
        print(f"  Total Unrealized P&L: ${total_pl:,.2f}")
    else:
        print("  No open positions")
    
    # Show account summary
    print("\n[INFO] Account Summary:")
    account = trader.account
    if account:
        print(f"  Buying Power: ${float(account.buying_power):,.2f}")
        print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"  Cash: ${float(account.cash):,.2f}")
    
    return True

def main():
    """Main entry point"""
    try:
        success = place_dee_bot_orders()
        
        if success:
            print("\n[SUCCESS] DEE-BOT trading session completed")
        else:
            print("\n[ERROR] DEE-BOT trading session failed")
            
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()