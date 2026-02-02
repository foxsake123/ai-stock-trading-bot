#!/usr/bin/env python3
"""
Sync positions from Alpaca to local CSV files
Fixes the stale position data issue
"""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

load_dotenv()

def sync_positions():
    """Sync positions from Alpaca to local CSV"""
    
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("ERROR: Missing Alpaca credentials")
        return
    
    client = TradingClient(api_key, secret_key, paper=True)
    
    # Get current positions
    positions = client.get_all_positions()
    print(f"Found {len(positions)} positions in Alpaca")
    
    # Prepare data
    now = datetime.now().isoformat()
    
    # Write to multiple CSV files
    files_to_update = [
        'data/daily/positions/shorgan-bot-positions.csv',
        'data/daily/positions/dee-bot-positions.csv',
        'data/daily/positions/combined-portfolio.csv',
    ]
    
    for csv_path in files_to_update:
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'symbol', 'quantity', 'avg_price', 'current_price', 
                'market_value', 'cost_basis', 'unrealized_pnl', 
                'unrealized_pnl_pct', 'change_today', 'change_today_pct', 
                'last_updated'
            ])
            
            for p in positions:
                writer.writerow([
                    p.symbol,
                    p.qty,
                    p.avg_entry_price,
                    p.current_price,
                    p.market_value,
                    p.cost_basis,
                    p.unrealized_pl,
                    float(p.unrealized_plpc) * 100 if p.unrealized_plpc else 0,
                    p.change_today,
                    0,  # change_today_pct not available
                    now
                ])
        
        print(f"[OK] Updated: {csv_path}")
    
    # Show positions
    print(f"\n{'Symbol':<8} {'Qty':>8} {'Entry':>10} {'Current':>10} {'P&L':>12}")
    print("-" * 55)
    for p in positions:
        pnl = float(p.unrealized_pl)
        print(f"{p.symbol:<8} {p.qty:>8} ${float(p.avg_entry_price):>8.2f} ${float(p.current_price):>8.2f} ${pnl:>+10.2f}")
    
    # Show and optionally cancel open orders
    orders = client.get_orders()
    print(f"\nOpen Orders: {len(orders)}")
    
    if orders:
        for o in orders:
            price = o.limit_price or o.stop_price or "MKT"
            print(f"  {o.side.upper():>4} {o.qty:>5} {o.symbol:<6} @ ${price} - {o.status}")
        
        # Ask to cancel
        print(f"\n[!] Found {len(orders)} stale orders. Run with --cancel to remove them.")
    
    return len(positions), len(orders)


def cancel_all_orders():
    """Cancel all open orders"""
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    client = TradingClient(api_key, secret_key, paper=True)
    
    orders = client.get_orders()
    print(f"Canceling {len(orders)} orders...")
    
    for o in orders:
        try:
            client.cancel_order_by_id(o.id)
            print(f"  [X] Canceled: {o.side} {o.qty} {o.symbol}")
        except Exception as e:
            print(f"  [!] Failed to cancel {o.symbol}: {e}")
    
    print("Done!")


if __name__ == "__main__":
    import sys
    
    if "--cancel" in sys.argv:
        cancel_all_orders()
    else:
        sync_positions()
