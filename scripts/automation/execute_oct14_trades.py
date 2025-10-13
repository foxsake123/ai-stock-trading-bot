"""
Execute Oct 14, 2025 Trading Orders
DEE-BOT: 4 orders (WMT, COST, MRK, UNH)
SHORGAN-BOT: 0 orders (all blocked by wash sales)
"""

import os
import sys
from datetime import datetime
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Load environment
load_dotenv()

def execute_trades():
    """Execute Oct 14 approved trades"""

    # Initialize Alpaca APIs
    dee_api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        os.getenv('ALPACA_BASE_URL'),
        api_version='v2'
    )

    print("=" * 80)
    print("EXECUTION PLAN - OCTOBER 14, 2025")
    print("=" * 80)
    print()

    # DEE-BOT Orders
    dee_orders = [
        {'symbol': 'WMT', 'qty': 45, 'limit': 160.00, 'stop': 150.00, 'target': 175.00},
        {'symbol': 'COST', 'qty': 5, 'limit': 915.00, 'stop': 850.00, 'target': 1000.00},
        {'symbol': 'MRK', 'qty': 53, 'limit': 90.00, 'stop': 82.00, 'target': 100.00},
        {'symbol': 'UNH', 'qty': 11, 'limit': 360.00, 'stop': 330.00, 'target': 400.00},
    ]

    total_cost = sum(o['qty'] * o['limit'] for o in dee_orders)

    print("DEE-BOT ORDERS (4 total)")
    print("-" * 80)
    for order in dee_orders:
        cost = order['qty'] * order['limit']
        print(f"BUY {order['qty']} {order['symbol']} @ ${order['limit']:.2f} = ${cost:,.0f}")
        print(f"   Stop: ${order['stop']:.2f}, Target: ${order['target']:.2f}")

    print()
    print(f"Total Cost: ${total_cost:,.0f}")
    print()

    print("SHORGAN-BOT ORDERS")
    print("-" * 80)
    print("Execute: 0 trades (all blocked by wash sales)")
    print()

    # Confirm execution
    response = input("Execute these orders? (yes/no): ").strip().lower()

    if response != 'yes':
        print("Execution cancelled.")
        return

    print()
    print("=" * 80)
    print("EXECUTING DEE-BOT ORDERS")
    print("=" * 80)
    print()

    results = {
        'successful': [],
        'failed': []
    }

    # Execute DEE-BOT orders
    for order in dee_orders:
        try:
            print(f"Submitting: BUY {order['qty']} {order['symbol']} @ ${order['limit']:.2f}...")

            submitted_order = dee_api.submit_order(
                symbol=order['symbol'],
                qty=order['qty'],
                side='buy',
                type='limit',
                time_in_force='day',
                limit_price=order['limit']
            )

            print(f"[OK] Order submitted: {submitted_order.id}")
            results['successful'].append({
                'account': 'DEE-BOT',
                'symbol': order['symbol'],
                'qty': order['qty'],
                'limit': order['limit'],
                'order_id': submitted_order.id
            })

        except Exception as e:
            print(f"[FAILED] {order['symbol']}: {str(e)}")
            results['failed'].append({
                'account': 'DEE-BOT',
                'symbol': order['symbol'],
                'qty': order['qty'],
                'limit': order['limit'],
                'error': str(e)
            })

    # Summary
    print()
    print("=" * 80)
    print("EXECUTION SUMMARY")
    print("=" * 80)
    print()
    print(f"Successful: {len(results['successful'])}/{len(dee_orders)}")
    print(f"Failed: {len(results['failed'])}/{len(dee_orders)}")
    print()

    if results['successful']:
        print("EXECUTED ORDERS:")
        for r in results['successful']:
            print(f"  {r['account']}: BUY {r['qty']} {r['symbol']} @ ${r['limit']:.2f}")

    if results['failed']:
        print()
        print("FAILED ORDERS:")
        for r in results['failed']:
            print(f"  {r['account']}: {r['symbol']} - {r['error']}")

    print()
    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Monitor fills in real-time")
    print("2. Place stop-loss orders after fills (optional for DEE-BOT)")
    print("3. Check ARQT FDA decision news")
    print("4. Generate end-of-day performance report")
    print()

    # Save execution log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"data/daily/execution_log_{timestamp}.txt"

    with open(log_file, 'w') as f:
        f.write(f"Execution Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Successful: {len(results['successful'])}\n")
        f.write(f"Failed: {len(results['failed'])}\n\n")

        if results['successful']:
            f.write("EXECUTED:\n")
            for r in results['successful']:
                f.write(f"{r['account']}: BUY {r['qty']} {r['symbol']} @ ${r['limit']:.2f} (ID: {r['order_id']})\n")

        if results['failed']:
            f.write("\nFAILED:\n")
            for r in results['failed']:
                f.write(f"{r['account']}: {r['symbol']} - {r['error']}\n")

    print(f"Execution log saved: {log_file}")
    print()

if __name__ == '__main__':
    execute_trades()
