"""
SHORGAN-BOT Enhanced Trading Script
Uses catalyst detection and bot-specific API keys
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

from Core_Trading.place_alpaca_orders_enhanced import AlpacaBotTrader
from data.catalyst_detector import CatalystDetector

def get_catalyst_trades():
    """Generate trades based on catalyst detection"""
    
    print("\n[INFO] Running catalyst detection...")
    detector = CatalystDetector()
    
    # List of stocks to scan for catalysts
    watchlist = [
        "NVDA", "TSLA", "AMD", "AAPL", "MSFT",
        "META", "AMZN", "GOOGL", "NFLX", "ROKU",
        "SQ", "SHOP", "COIN", "MARA", "RIOT"
    ]
    
    trades = []
    
    for ticker in watchlist:
        print(f"  Scanning {ticker}...")
        catalysts = detector.detect_catalysts(ticker)
        
        if catalysts['recommendation'] in ['BUY', 'STRONG_BUY']:
            # Calculate position size based on confidence
            base_qty = 10
            if catalysts['recommendation'] == 'STRONG_BUY':
                qty = base_qty * 2
            else:
                qty = base_qty
            
            trades.append({
                'symbol': ticker,
                'qty': qty,
                'side': 'buy',
                'reason': catalysts['detected_catalysts'][0]['description'] if catalysts['detected_catalysts'] else 'Catalyst detected',
                'urgency': catalysts['urgency'],
                'score': catalysts['total_score']
            })
            
            print(f"    ✓ {ticker}: {catalysts['recommendation']} (Score: {catalysts['total_score']:.2f})")
    
    # Sort by urgency and score
    trades.sort(key=lambda x: (x['urgency'] == 'IMMEDIATE', x['score']), reverse=True)
    
    return trades[:5]  # Limit to top 5 trades

def place_shorgan_bot_orders():
    """Place SHORGAN-BOT orders with catalyst detection"""
    
    print("=" * 70)
    print("SHORGAN-BOT CATALYST TRADING SYSTEM")
    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Strategy: Short-term catalyst exploitation")
    print("=" * 70)
    
    # Initialize SHORGAN-BOT trader
    trader = AlpacaBotTrader("SHORGAN")
    
    # Connect to Alpaca
    if not trader.connect_to_alpaca():
        print("[ERROR] Failed to connect to Alpaca")
        return False
    
    # Get catalyst-based trades
    trades = get_catalyst_trades()
    
    if not trades:
        print("\n[INFO] No catalyst opportunities found")
        return True
    
    print(f"\n[INFO] Found {len(trades)} catalyst opportunities:")
    for trade in trades:
        print(f"  {trade['symbol']}: {trade['reason'][:50]}...")
        print(f"    Urgency: {trade['urgency']}, Score: {trade['score']:.2f}")
    
    # Place orders
    print("\n[INFO] Placing orders...")
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
    print("\n[INFO] Current SHORGAN-BOT positions:")
    positions = trader.get_positions()
    total_value = 0
    
    if positions:
        for pos in positions:
            value = float(pos.qty) * float(pos.current_price)
            total_value += value
            unrealized_pl = float(pos.unrealized_pl)
            pl_pct = float(pos.unrealized_plpc) * 100
            
            print(f"  {pos.symbol}: {pos.qty} shares @ ${float(pos.current_price):.2f}")
            print(f"    Cost Basis: ${float(pos.avg_entry_price):.2f}")
            print(f"    P&L: ${unrealized_pl:,.2f} ({pl_pct:+.2f}%)")
        
        print(f"\n  Total Position Value: ${total_value:,.2f}")
    else:
        print("  No open positions")
    
    return True

def main():
    """Main entry point"""
    try:
        success = place_shorgan_bot_orders()
        
        if success:
            print("\n[SUCCESS] SHORGAN-BOT trading session completed")
        else:
            print("\n[ERROR] SHORGAN-BOT trading session failed")
            
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()