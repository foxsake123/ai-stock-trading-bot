"""
Execute Oct 14, 2025 Consensus Trading Plan - NON-INTERACTIVE
"""

import os
import sys
from datetime import datetime
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

load_dotenv()

def execute_now():
    """Execute consensus trades immediately"""

    # Initialize APIs
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
    print("EXECUTING CONSENSUS ORDERS - OCTOBER 14, 2025")
    print("=" * 80)
    print()

    results = {'successful': [], 'failed': []}

    # SHORGAN: ARWR
    print("SHORGAN-BOT:")
    print("-" * 80)
    try:
        print("Submitting: BUY 47 ARWR @ $36.94...")
        order = shorgan_api.submit_order(
            symbol='ARWR',
            qty=47,
            side='buy',
            type='limit',
            time_in_force='day',
            limit_price=36.94
        )
        print(f"[OK] ARWR order submitted: {order.id}")
        results['successful'].append(('SHORGAN', 'ARWR', 47, 36.94, order.id))

        # Place stop-loss
        print("Placing stop-loss @ $28.00...")
        stop = shorgan_api.submit_order(
            symbol='ARWR',
            qty=47,
            side='sell',
            type='stop',
            time_in_force='gtc',
            stop_price=28.00
        )
        print(f"[OK] Stop-loss placed: {stop.id}")

    except Exception as e:
        print(f"[FAILED] ARWR: {str(e)}")
        results['failed'].append(('SHORGAN', 'ARWR', 47, 36.94, str(e)))

    print()

    # DEE: ED, WMT, COST
    print("DEE-BOT:")
    print("-" * 80)

    dee_orders = [
        ('ED', 100, 100.81),
        ('WMT', 45, 160.00),
        ('COST', 5, 915.00)
    ]

    for symbol, qty, limit in dee_orders:
        try:
            print(f"Submitting: BUY {qty} {symbol} @ ${limit:.2f}...")
            order = dee_api.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='limit',
                time_in_force='day',
                limit_price=limit
            )
            print(f"[OK] {symbol} order submitted: {order.id}")
            results['successful'].append(('DEE', symbol, qty, limit, order.id))

        except Exception as e:
            print(f"[FAILED] {symbol}: {str(e)}")
            results['failed'].append(('DEE', symbol, qty, limit, str(e)))

    # Summary
    print()
    print("=" * 80)
    print("EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Successful: {len(results['successful'])}/4")
    print(f"Failed: {len(results['failed'])}/4")
    print()

    if results['successful']:
        print("EXECUTED:")
        for account, symbol, qty, limit, order_id in results['successful']:
            print(f"  {account}: BUY {qty} {symbol} @ ${limit:.2f} (ID: {order_id})")

    if results['failed']:
        print()
        print("FAILED:")
        for account, symbol, qty, limit, error in results['failed']:
            print(f"  {account}: {symbol} - {error}")

    print()
    print("Next: Monitor fills and check ARQT FDA decision")
    print()

    # Save log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"data/daily/execution_log_{timestamp}.txt"

    with open(log_file, 'w') as f:
        f.write(f"Execution Log - {datetime.now()}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Successful: {len(results['successful'])}\n")
        f.write(f"Failed: {len(results['failed'])}\n\n")

        if results['successful']:
            f.write("EXECUTED:\n")
            for account, symbol, qty, limit, order_id in results['successful']:
                f.write(f"{account}: BUY {qty} {symbol} @ ${limit:.2f} (ID: {order_id})\n")

        if results['failed']:
            f.write("\nFAILED:\n")
            for account, symbol, qty, limit, error in results['failed']:
                f.write(f"{account}: {symbol} - {error}\n")

    print(f"Log saved: {log_file}")

if __name__ == '__main__':
    execute_now()
