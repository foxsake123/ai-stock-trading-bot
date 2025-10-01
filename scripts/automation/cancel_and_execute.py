"""
Cancel stop orders and execute morning trades
September 18, 2025
"""

import alpaca_trade_api as tradeapi
import time

# SHORGAN-BOT credentials
API_KEY = 'PKJRLSB2MFEJUSK6UK2E'
SECRET_KEY = 'QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic'
BASE_URL = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

def cancel_stop_orders(symbols):
    """Cancel stop orders for specific symbols"""
    orders = api.list_orders(status='open')
    cancelled = []

    for order in orders:
        if order.symbol in symbols and order.order_type in ['stop', 'stop_limit']:
            try:
                api.cancel_order(order.id)
                print(f"[CANCELLED] Stop order for {order.symbol} ({order.qty} shares)")
                cancelled.append(order.symbol)
                time.sleep(0.5)  # Small delay
            except Exception as e:
                print(f"[ERROR] Failed to cancel {order.symbol}: {e}")

    return cancelled

def execute_trade(symbol, qty, side):
    """Execute market order"""
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type='market',
            time_in_force='day'
        )
        print(f"[SUCCESS] {side.upper()} {qty} shares of {symbol} - Order ID: {order.id}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to {side} {symbol}: {e}")
        return False

def main():
    print("="*60)
    print("CANCEL STOP ORDERS AND EXECUTE TRADES")
    print("="*60)

    # Symbols we need to trade
    trade_symbols = ['CBRL', 'RGTI', 'ORCL']

    # Step 1: Cancel stop orders
    print("\nStep 1: Cancelling stop orders...")
    print("-"*40)
    cancelled = cancel_stop_orders(trade_symbols)

    if cancelled:
        print(f"\nCancelled stop orders for: {', '.join(cancelled)}")
        print("Waiting 2 seconds for orders to clear...")
        time.sleep(2)

    # Step 2: Execute trades
    print("\nStep 2: Executing trades...")
    print("-"*40)

    # CBRL - Exit full position
    print("\n1. CBRL - EXIT FULL POSITION (earnings miss)")
    cbrl_success = execute_trade('CBRL', 81, 'sell')
    time.sleep(1)

    # RGTI - Sell half position
    print("\n2. RGTI - TAKE PROFITS (sell 50%)")
    rgti_success = execute_trade('RGTI', 65, 'sell')
    time.sleep(1)

    # ORCL - Sell half position
    print("\n3. ORCL - TAKE PROFITS (sell 50%)")
    orcl_success = execute_trade('ORCL', 21, 'sell')

    # Step 3: Re-apply stop orders for remaining positions
    print("\n" + "="*60)
    print("Step 3: Re-applying stop orders for remaining positions...")
    print("-"*40)

    remaining_stops = {
        'KSS': {'qty': 90, 'stop': 15.18},
        'INCY': {'qty': 61, 'stop': 77.25},  # 8% stop
        'RGTI': {'qty': 65, 'stop': 17.35},  # Remaining half
        'ORCL': {'qty': 21, 'stop': 268.66}  # Remaining half
    }

    for symbol, params in remaining_stops.items():
        try:
            order = api.submit_order(
                symbol=symbol,
                qty=params['qty'],
                side='sell',
                type='stop',
                stop_price=params['stop'],
                time_in_force='gtc'
            )
            print(f"[STOP SET] {symbol}: {params['qty']} shares @ ${params['stop']:.2f}")
        except Exception as e:
            print(f"[ERROR] Failed to set stop for {symbol}: {e}")

    # Summary
    print("\n" + "="*60)
    print("EXECUTION SUMMARY")
    print("="*60)

    if cbrl_success:
        print("[SUCCESS] CBRL: Exited 81 shares (earnings miss)")
    else:
        print("[FAILED] CBRL: Check position manually")

    if rgti_success:
        print("[SUCCESS] RGTI: Sold 65 shares (locked +22.7% profit)")
    else:
        print("[FAILED] RGTI: Check position manually")

    if orcl_success:
        print("[SUCCESS] ORCL: Sold 21 shares (locked +21.9% profit)")
    else:
        print("[FAILED] ORCL: Check position manually")

    print("\n" + "="*60)
    print("POSITIONS TO MONITOR:")
    print("-"*40)
    print("- KSS: 90 shares, stop @ $15.18")
    print("- INCY: 61 shares for FDA Sept 19")
    print("- RGTI: 65 shares remaining")
    print("- ORCL: 21 shares remaining")
    print("="*60)

if __name__ == "__main__":
    main()