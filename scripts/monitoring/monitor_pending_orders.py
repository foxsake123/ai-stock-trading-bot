"""
Monitor Pending DEE-BOT Orders (ED, COST)
Checks order status and provides recommendations
"""

import os
from datetime import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

def monitor_pending():
    """Monitor pending orders and provide status"""

    # Initialize API
    api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        os.getenv('ALPACA_BASE_URL'),
        api_version='v2'
    )

    print("=" * 80)
    print("PENDING ORDER MONITOR - DEE-BOT")
    print(f"Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print("=" * 80)
    print()

    # Get pending orders
    try:
        pending_orders = api.list_orders(status='open', limit=10)
        print(f"Total Pending Orders: {len(pending_orders)}")
        print()
    except Exception as e:
        print(f"[ERROR] Cannot fetch orders: {e}")
        return

    if not pending_orders:
        print("[INFO] No pending orders found")
        print()
        print("All orders have either:")
        print("- Filled successfully")
        print("- Been cancelled")
        print("- Expired (day orders at 4 PM)")
        return

    # Track our specific orders
    ed_order = None
    cost_order = None

    for order in pending_orders:
        if order.symbol == 'ED':
            ed_order = order
        elif order.symbol == 'COST':
            cost_order = order

    # Get current prices
    print("PENDING ORDERS STATUS:")
    print("-" * 80)

    if ed_order:
        print("ED (Consolidated Edison):")
        print(f"  Order ID: {ed_order.id}")
        print(f"  Side: {ed_order.side.upper()}")
        print(f"  Quantity: {ed_order.qty} shares")
        print(f"  Limit Price: ${float(ed_order.limit_price):.2f}")
        print(f"  Status: {ed_order.status}")
        print(f"  Created: {ed_order.created_at}")
        print(f"  Time in Force: {ed_order.time_in_force}")

        # Get current price
        try:
            quote = api.get_latest_trade('ED')
            current_price = float(quote.price)
            print(f"  Current Price: ${current_price:.2f}")
            diff = current_price - float(ed_order.limit_price)
            print(f"  Price Gap: ${diff:+.2f} ({diff/float(ed_order.limit_price)*100:+.1f}%)")

            if current_price <= float(ed_order.limit_price):
                print("  [ACTION] Price at/below limit - should fill soon!")
            else:
                print(f"  [WAITING] Price ${diff:.2f} above limit")

        except Exception as e:
            print(f"  [WARNING] Cannot get current price: {e}")

        print()

    if cost_order:
        print("COST (Costco):")
        print(f"  Order ID: {cost_order.id}")
        print(f"  Side: {cost_order.side.upper()}")
        print(f"  Quantity: {cost_order.qty} shares")
        print(f"  Limit Price: ${float(cost_order.limit_price):.2f}")
        print(f"  Status: {cost_order.status}")
        print(f"  Created: {cost_order.created_at}")
        print(f"  Time in Force: {cost_order.time_in_force}")

        # Get current price
        try:
            quote = api.get_latest_trade('COST')
            current_price = float(quote.price)
            print(f"  Current Price: ${current_price:.2f}")
            diff = current_price - float(cost_order.limit_price)
            print(f"  Price Gap: ${diff:+.2f} ({diff/float(cost_order.limit_price)*100:+.1f}%)")

            if current_price <= float(cost_order.limit_price):
                print("  [ACTION] Price at/below limit - should fill soon!")
            else:
                print(f"  [WAITING] Price ${diff:.2f} above limit")

        except Exception as e:
            print(f"  [WARNING] Cannot get current price: {e}")

        print()

    # Summary and recommendations
    print("=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)
    print()

    if ed_order or cost_order:
        print("OPTION 1: Keep Waiting")
        print("- Pro: May fill if prices pull back")
        print("- Con: Could wait indefinitely")
        print("- Action: Monitor daily")
        print()

        print("OPTION 2: Adjust Limits")
        print("- Pro: Higher chance of execution")
        print("- Con: Pay higher price")
        print("- Action: Cancel and resubmit at market price")
        print()

        print("OPTION 3: Cancel Orders")
        print("- Pro: Free up mental bandwidth")
        print("- Con: Miss execution if prices drop")
        print("- Action: Cancel and wait for better opportunities")
        print()

        print("CURRENT STRATEGY:")
        print("- Orders are DAY type (expire at 4 PM ET)")
        print("- If not filled by market close, they auto-cancel")
        print("- Can resubmit tomorrow if still want exposure")
        print()

    # Check if market is closed
    try:
        clock = api.get_clock()
        if clock.is_open:
            print(f"[INFO] Market is OPEN - orders active")
            print(f"       Closes at: {clock.next_close.strftime('%I:%M %p ET')}")
        else:
            print(f"[INFO] Market is CLOSED - orders inactive")
            print(f"       Opens at: {clock.next_open.strftime('%Y-%m-%d %I:%M %p ET')}")
    except:
        pass

    print()
    print("To cancel orders: python -c \"...api.cancel_order('ORDER_ID')...\"")
    print("To adjust limits: Cancel old, submit new with different limit price")
    print()

if __name__ == '__main__':
    monitor_pending()
