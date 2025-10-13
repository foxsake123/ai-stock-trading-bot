"""
Execute Oct 14, 2025 Consensus Trading Plan
Validated through Claude + ChatGPT multi-agent analysis
Wash sale checked and cleared
"""

import os
import sys
from datetime import datetime
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Load environment
load_dotenv()

def execute_consensus_trades():
    """Execute consensus-validated Oct 14 trades"""

    # Initialize Alpaca APIs
    dee_api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        os.getenv('ALPACA_BASE_URL'),
        api_version='v2'
    )

    shorgan_api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY_SHORGAN'),
        os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
        os.getenv('ALPACA_BASE_URL'),
        api_version='v2'
    )

    print("=" * 80)
    print("CONSENSUS EXECUTION PLAN - OCTOBER 14, 2025")
    print("Research: Claude + ChatGPT Multi-Agent Analysis")
    print("=" * 80)
    print()

    # SHORGAN Orders (1 trade)
    shorgan_orders = [
        {
            'symbol': 'ARWR',
            'qty': 47,
            'limit': 36.94,
            'stop': 28.00,
            'target': 55.00,
            'conviction': '8/10',
            'catalyst': 'Nov 18 PDUFA'
        }
    ]

    # DEE Orders (3 trades)
    dee_orders = [
        {
            'symbol': 'ED',
            'qty': 100,
            'limit': 100.81,
            'stop': None,
            'target': 105.00,
            'conviction': '9/10',
            'catalyst': 'Long-term defensive'
        },
        {
            'symbol': 'WMT',
            'qty': 45,
            'limit': 160.00,
            'stop': None,
            'target': 175.00,
            'conviction': '8/10',
            'catalyst': 'Defensive retail'
        },
        {
            'symbol': 'COST',
            'qty': 5,
            'limit': 915.00,
            'stop': None,
            'target': 1000.00,
            'conviction': '8/10',
            'catalyst': 'Add to winner'
        }
    ]

    total_shorgan = sum(o['qty'] * o['limit'] for o in shorgan_orders)
    total_dee = sum(o['qty'] * o['limit'] for o in dee_orders)

    print("SHORGAN-BOT ORDERS (1 trade)")
    print("-" * 80)
    for order in shorgan_orders:
        cost = order['qty'] * order['limit']
        print(f"BUY {order['qty']} {order['symbol']} @ ${order['limit']:.2f} = ${cost:,.0f}")
        print(f"   Conviction: {order['conviction']}, Catalyst: {order['catalyst']}")
        if order['stop']:
            print(f"   Stop: ${order['stop']:.2f}, Target: ${order['target']:.2f}")
        print()

    print(f"Total SHORGAN: ${total_shorgan:,.0f}")
    print()

    print("DEE-BOT ORDERS (3 trades)")
    print("-" * 80)
    for order in dee_orders:
        cost = order['qty'] * order['limit']
        print(f"BUY {order['qty']} {order['symbol']} @ ${order['limit']:.2f} = ${cost:,.0f}")
        print(f"   Conviction: {order['conviction']}, Catalyst: {order['catalyst']}")
        if order['target']:
            print(f"   Target: ${order['target']:.2f}")
        print()

    print(f"Total DEE: ${total_dee:,.0f}")
    print()
    print(f"COMBINED TOTAL: ${total_shorgan + total_dee:,.0f}")
    print()

    # Confirm execution
    response = input("Execute these consensus-validated orders? (yes/no): ").strip().lower()

    if response != 'yes':
        print("Execution cancelled.")
        return

    print()
    print("=" * 80)
    print("EXECUTING ORDERS")
    print("=" * 80)
    print()

    results = {
        'successful': [],
        'failed': []
    }

    # Execute SHORGAN orders
    print("SHORGAN-BOT:")
    print("-" * 80)
    for order in shorgan_orders:
        try:
            print(f"Submitting: BUY {order['qty']} {order['symbol']} @ ${order['limit']:.2f}...")

            submitted_order = shorgan_api.submit_order(
                symbol=order['symbol'],
                qty=order['qty'],
                side='buy',
                type='limit',
                time_in_force='day',
                limit_price=order['limit']
            )

            print(f"[OK] Order submitted: {submitted_order.id}")
            results['successful'].append({
                'account': 'SHORGAN-BOT',
                'symbol': order['symbol'],
                'qty': order['qty'],
                'limit': order['limit'],
                'order_id': submitted_order.id
            })

            # Place stop-loss if specified
            if order['stop']:
                print(f"Placing stop-loss @ ${order['stop']:.2f}...")
                stop_order = shorgan_api.submit_order(
                    symbol=order['symbol'],
                    qty=order['qty'],
                    side='sell',
                    type='stop',
                    time_in_force='gtc',
                    stop_price=order['stop']
                )
                print(f"[OK] Stop-loss placed: {stop_order.id}")

        except Exception as e:
            print(f"[FAILED] {order['symbol']}: {str(e)}")
            results['failed'].append({
                'account': 'SHORGAN-BOT',
                'symbol': order['symbol'],
                'qty': order['qty'],
                'limit': order['limit'],
                'error': str(e)
            })

    print()
    print("DEE-BOT:")
    print("-" * 80)
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
    total_orders = len(shorgan_orders) + len(dee_orders)
    print(f"Successful: {len(results['successful'])}/{total_orders}")
    print(f"Failed: {len(results['failed'])}/{total_orders}")
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
    print("2. Verify ARWR stop-loss placed @ $28.00")
    print("3. Check ARQT FDA decision (Oct 13 PDUFA)")
    print("4. Monitor existing GKOS position (Oct 20 PDUFA)")
    print("5. Monitor existing SNDX position (Oct 25 PDUFA)")
    print("6. Generate end-of-day performance report")
    print()

    # Save execution log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"data/daily/execution_log_consensus_{timestamp}.txt"

    with open(log_file, 'w') as f:
        f.write(f"Consensus Execution Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write("Research Sources: Claude + ChatGPT Multi-Agent Analysis\n")
        f.write("Wash Sale Validated: All trades cleared\n\n")
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
    execute_consensus_trades()
