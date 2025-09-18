"""
Execute Morning Trades - September 18, 2025
CBRL exit (earnings miss), RGTI/ORCL profit taking
"""

import alpaca_trade_api as tradeapi
from datetime import datetime
import time
import json

# Alpaca credentials - SHORGAN-BOT account
API_KEY = 'PKJRLSB2MFEJUSK6UK2E'
SECRET_KEY = 'QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic'
BASE_URL = 'https://paper-api.alpaca.markets'

# Initialize API
api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

def execute_trade(symbol, qty, side, order_type='market', time_in_force='day'):
    """Execute a single trade"""
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=order_type,
            time_in_force=time_in_force
        )
        print(f"[SUCCESS] {side.upper()} {qty} shares of {symbol} - Order ID: {order.id}")
        return order
    except Exception as e:
        print(f"[ERROR] Failed to {side} {symbol}: {e}")
        return None

def check_market_open():
    """Check if market is open"""
    clock = api.get_clock()
    if clock.is_open:
        print("Market is OPEN")
        return True
    else:
        next_open = clock.next_open
        print(f"Market is CLOSED. Opens at {next_open}")
        return False

def main():
    print("="*60)
    print("MORNING TRADE EXECUTION - September 18, 2025")
    print("="*60)

    # Check market status
    if not check_market_open():
        print("\nWaiting for market to open...")
        # In production, would wait until market opens
        # For now, proceed with orders that will queue

    print("\nExecuting trades:")
    print("-"*40)

    # Trade 1: EXIT CBRL (earnings miss)
    print("\n1. CBRL - EXIT POSITION (Earnings miss -10%)")
    cbrl_order = execute_trade('CBRL', 81, 'sell')

    # Small delay between orders
    time.sleep(2)

    # Trade 2: RGTI profit taking (50% position)
    print("\n2. RGTI - TAKE PROFITS (Sell 50% = 65 shares)")
    rgti_order = execute_trade('RGTI', 65, 'sell')

    time.sleep(2)

    # Trade 3: ORCL profit taking (50% position)
    print("\n3. ORCL - TAKE PROFITS (Sell 50% = 21 shares)")
    orcl_order = execute_trade('ORCL', 21, 'sell')

    # Log trades
    trades_log = {
        'timestamp': datetime.now().isoformat(),
        'trades': [
            {'symbol': 'CBRL', 'qty': 81, 'side': 'sell', 'reason': 'Earnings miss -10%'},
            {'symbol': 'RGTI', 'qty': 65, 'side': 'sell', 'reason': 'Profit taking +22.7%'},
            {'symbol': 'ORCL', 'qty': 21, 'side': 'sell', 'reason': 'Profit taking +21.9%'}
        ]
    }

    # Save log
    log_file = f'scripts-and-data/trade-logs/morning_trades_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(log_file, 'w') as f:
        json.dump(trades_log, f, indent=2)

    print("\n" + "="*60)
    print("TRADE SUMMARY:")
    print("-"*40)
    if cbrl_order:
        print("CBRL: Exited 81 shares (earnings miss)")
    else:
        print("CBRL: Failed to exit - check position")

    if rgti_order:
        print("RGTI: Sold 65 shares (locked profits)")
    else:
        print("RGTI: Failed to sell - check position")

    if orcl_order:
        print("ORCL: Sold 21 shares (locked profits)")
    else:
        print("ORCL: Failed to sell - check position")
    print("-"*40)
    print(f"Trades logged to: {log_file}")

    # Check positions after trades
    print("\n" + "="*60)
    print("REMAINING POSITIONS TO MONITOR:")
    print("-"*40)
    print("- KSS: Watch stop at $15.18 (currently at $15.59)")
    print("- INCY: 61 shares for FDA decision Sept 19")
    print("- RGTI: 65 shares remaining (other half)")
    print("- ORCL: 21 shares remaining (other half)")
    print("="*60)

if __name__ == "__main__":
    main()