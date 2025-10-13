"""
Execute DEE-BOT Orders (Oct 14, 2025)
Run this AFTER fixing API permissions
"""

import os
from datetime import datetime
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

def execute_dee_orders():
    """Execute the 3 DEE-BOT orders"""

    load_dotenv()

    # Initialize API
    api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        os.getenv('ALPACA_BASE_URL'),
        api_version='v2'
    )

    print("=" * 80)
    print("EXECUTING DEE-BOT ORDERS - OCTOBER 14, 2025")
    print("=" * 80)
    print()

    # Check account first
    try:
        account = api.get_account()
        cash = float(account.cash)
        print(f"Cash Available: ${cash:,.2f}")
        print(f"Trading Blocked: {account.trading_blocked}")
        print()

        if account.trading_blocked:
            print("❌ ERROR: Trading is blocked on this account")
            return

    except Exception as e:
        print(f"❌ Cannot access account: {e}")
        return

    # DEE orders
    orders = [
        {'symbol': 'ED', 'qty': 100, 'limit': 100.81, 'cost': 10081},
        {'symbol': 'WMT', 'qty': 45, 'limit': 160.00, 'cost': 7200},
        {'symbol': 'COST', 'qty': 5, 'limit': 915.00, 'cost': 4575}
    ]

    total_cost = sum(o['cost'] for o in orders)

    print("ORDERS TO EXECUTE:")
    print("-" * 80)
    for o in orders:
        print(f"BUY {o['qty']} {o['symbol']} @ ${o['limit']:.2f} = ${o['cost']:,}")
    print()
    print(f"Total Cost: ${total_cost:,}")
    print(f"Cash Available: ${cash:,.2f}")

    if total_cost > cash:
        print()
        print(f"⚠️  WARNING: Insufficient cash (need ${total_cost - cash:,.2f} more)")
        print("Proceeding anyway - orders may be partially filled or rejected")

    print()
    response = input("Execute these orders? (yes/no): ").strip().lower()

    if response != 'yes':
        print("Execution cancelled.")
        return

    print()
    print("EXECUTING...")
    print("-" * 80)

    results = {'successful': [], 'failed': []}

    for order in orders:
        try:
            print(f"Submitting: BUY {order['qty']} {order['symbol']} @ ${order['limit']:.2f}...")

            submitted = api.submit_order(
                symbol=order['symbol'],
                qty=order['qty'],
                side='buy',
                type='limit',
                time_in_force='day',
                limit_price=order['limit']
            )

            print(f"✅ {order['symbol']} submitted: {submitted.id}")
            results['successful'].append((order['symbol'], order['qty'], order['limit'], submitted.id))

        except Exception as e:
            print(f"❌ {order['symbol']} failed: {e}")
            results['failed'].append((order['symbol'], order['qty'], order['limit'], str(e)))

    # Summary
    print()
    print("=" * 80)
    print("EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Successful: {len(results['successful'])}/3")
    print(f"Failed: {len(results['failed'])}/3")
    print()

    if results['successful']:
        print("EXECUTED:")
        for symbol, qty, limit, order_id in results['successful']:
            print(f"  ✅ BUY {qty} {symbol} @ ${limit:.2f} (ID: {order_id})")

    if results['failed']:
        print()
        print("FAILED:")
        for symbol, qty, limit, error in results['failed']:
            print(f"  ❌ {symbol}: {error}")

    print()
    print("Next: Monitor fills and verify positions")
    print()

    # Save log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"data/daily/execution_log_dee_{timestamp}.txt"

    with open(log_file, 'w') as f:
        f.write(f"DEE-BOT Execution Log - {datetime.now()}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Successful: {len(results['successful'])}\n")
        f.write(f"Failed: {len(results['failed'])}\n\n")

        if results['successful']:
            f.write("EXECUTED:\n")
            for symbol, qty, limit, order_id in results['successful']:
                f.write(f"BUY {qty} {symbol} @ ${limit:.2f} (ID: {order_id})\n")

        if results['failed']:
            f.write("\nFAILED:\n")
            for symbol, qty, limit, error in results['failed']:
                f.write(f"{symbol}: {error}\n")

    print(f"Log saved: {log_file}")

if __name__ == '__main__':
    execute_dee_orders()
