#!/usr/bin/env python3
"""
Emergency Rebalancing - Phase 1
DEE-BOT: Cancel orders and restore positive cash
SHORGAN-BOT: Cover PG short and cancel PEP short
"""

import alpaca_trade_api as tradeapi
import os
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

dee_api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY_DEE'),
    os.getenv('ALPACA_SECRET_KEY_DEE'),
    'https://paper-api.alpaca.markets',
    api_version='v2'
)

shorgan_api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY_SHORGAN'),
    os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    'https://paper-api.alpaca.markets',
    api_version='v2'
)

def print_separator(title=""):
    """Print section separator"""
    print("\n" + "="*80)
    if title:
        print(title)
        print("="*80)

def check_market_status():
    """Check if market is open"""
    clock = dee_api.get_clock()
    if not clock.is_open:
        print(f"\nWARNING: Market is CLOSED")
        print(f"Next open: {clock.next_open}")
        print("Orders will be queued for market open")
        return False
    else:
        print(f"\nMarket is OPEN")
        return True

def phase_1_dee_bot():
    """DEE-BOT: Cancel orders and restore cash"""
    print_separator("PHASE 1: DEE-BOT EMERGENCY REBALANCING")

    # Current status
    print("\n[STATUS] Current DEE-BOT account:")
    account = dee_api.get_account()
    print(f"    Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"    Cash: ${float(account.cash):,.2f}")
    print(f"    Long Market Value: ${float(account.long_market_value):,.2f}")

    # Step 1: Cancel ALL open orders
    print("\n[STEP 1] Canceling all open orders...")
    orders = dee_api.list_orders(status='open')
    if orders:
        for order in orders:
            try:
                print(f"    Canceling: {order.side} {order.qty} {order.symbol} @ ${order.limit_price}")
                dee_api.cancel_order(order.id)
                print(f"    ✓ Canceled order {order.id}")
            except Exception as e:
                print(f"    ✗ Error canceling {order.symbol}: {e}")
        print(f"    Canceled {len(orders)} orders")
    else:
        print("    No open orders to cancel")

    time.sleep(1)

    # Step 2: Sell PG (full position)
    print("\n[STEP 2] Selling PG (full position - 160 shares)...")
    print("    Rationale: Largest position, minimal loss (-0.18%), defensive overlap")
    try:
        # Check current position
        position = dee_api.get_position('PG')
        qty = int(float(position.qty))
        print(f"    Current PG position: {qty} shares")

        order = dee_api.submit_order(
            symbol='PG',
            qty=qty,
            side='sell',
            type='market',
            time_in_force='day'
        )
        print(f"    ✓ SUCCESS: Sold {qty} PG - Order ID: {order.id}")
        print(f"    Expected cash from sale: ~${qty * 152.22:,.2f}")
    except Exception as e:
        print(f"    ✗ ERROR: {e}")

    time.sleep(1)

    # Step 3: Sell CL (full position)
    print("\n[STEP 3] Selling CL (full position - 136 shares)...")
    print("    Rationale: Small loss (-0.63%), consumer staples overlap, lowest conviction")
    try:
        # Check current position
        position = dee_api.get_position('CL')
        qty = int(float(position.qty))
        print(f"    Current CL position: {qty} shares")

        order = dee_api.submit_order(
            symbol='CL',
            qty=qty,
            side='sell',
            type='market',
            time_in_force='day'
        )
        print(f"    ✓ SUCCESS: Sold {qty} CL - Order ID: {order.id}")
        print(f"    Expected cash from sale: ~${qty * 79.14:,.2f}")
    except Exception as e:
        print(f"    ✗ ERROR: {e}")

    # Step 4: Wait for orders to fill
    print("\n[STEP 4] Waiting for orders to fill (5 seconds)...")
    time.sleep(5)

    # Step 5: Check new account status
    print("\n[STEP 5] New DEE-BOT account status:")
    account = dee_api.get_account()
    print(f"    Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"    Cash: ${float(account.cash):,.2f}")
    print(f"    Buying Power: ${float(account.buying_power):,.2f}")
    print(f"    Long Market Value: ${float(account.long_market_value):,.2f}")

    cash_value = float(account.cash)
    if cash_value > 0:
        print(f"    ✓ SUCCESS: Cash is now POSITIVE (${cash_value:,.2f})")
    else:
        print(f"    ⚠ WARNING: Cash is still negative (${cash_value:,.2f})")
        print(f"    May need to wait for orders to fully settle")

    # Show remaining positions
    print("\n[STEP 6] Remaining DEE-BOT positions:")
    positions = dee_api.list_positions()
    print(f"    Total positions: {len(positions)}")
    for p in positions:
        print(f"    {p.symbol}: {p.qty} shares @ ${float(p.current_price):.2f} = ${float(p.market_value):,.2f}")

def phase_1_shorgan_bot():
    """SHORGAN-BOT: Cover PG short and cancel PEP short"""
    print_separator("PHASE 1: SHORGAN-BOT ADJUSTMENTS")

    # Current status
    print("\n[STATUS] Current SHORGAN-BOT account:")
    account = shorgan_api.get_account()
    print(f"    Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"    Cash: ${float(account.cash):,.2f}")
    print(f"    Short Market Value: ${float(account.short_market_value):,.2f}")

    # Step 1: Cancel PEP short order
    print("\n[STEP 1] Canceling PEP short order...")
    print("    Rationale: Too much defensive/consumer staples short exposure")
    orders = shorgan_api.list_orders(status='open', symbols=['PEP'])
    if orders:
        for order in orders:
            try:
                print(f"    Canceling: {order.side} {order.qty} {order.symbol}")
                shorgan_api.cancel_order(order.id)
                print(f"    ✓ Canceled PEP order {order.id}")
            except Exception as e:
                print(f"    ✗ Error: {e}")
    else:
        print("    No PEP orders found")

    time.sleep(1)

    # Step 2: Cover PG short (buy back shares)
    print("\n[STEP 2] Covering PG short position...")
    print("    Rationale: DEE-BOT selling PG, eliminate cross-bot exposure, minimal profit")
    try:
        # Check current short position
        position = shorgan_api.get_position('PG')
        qty = abs(int(float(position.qty)))  # Make positive
        print(f"    Current PG short: {position.qty} shares (need to buy {qty})")
        print(f"    Current P/L: ${float(position.unrealized_pl):,.2f} ({float(position.unrealized_plpc)*100:.2f}%)")

        order = shorgan_api.submit_order(
            symbol='PG',
            qty=qty,
            side='buy',
            type='market',
            time_in_force='day'
        )
        print(f"    ✓ SUCCESS: Covered {qty} PG short - Order ID: {order.id}")
        print(f"    Cash required: ~${qty * 152.22:,.2f}")
    except Exception as e:
        print(f"    ✗ ERROR: {e}")

    # Step 3: Wait for orders to fill
    print("\n[STEP 3] Waiting for orders to fill (5 seconds)...")
    time.sleep(5)

    # Step 4: Check new account status
    print("\n[STEP 4] New SHORGAN-BOT account status:")
    account = shorgan_api.get_account()
    print(f"    Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"    Cash: ${float(account.cash):,.2f}")
    print(f"    Short Market Value: ${float(account.short_market_value):,.2f}")

    # Show remaining short positions
    print("\n[STEP 5] Remaining SHORGAN-BOT short positions:")
    positions = shorgan_api.list_positions()
    short_positions = [p for p in positions if float(p.qty) < 0]
    print(f"    Total short positions: {len(short_positions)}")
    for p in short_positions:
        pl_pct = float(p.unrealized_plpc) * 100
        print(f"    {p.symbol}: {p.qty} shares @ ${float(p.current_price):.2f} = ${float(p.market_value):,.2f} (P/L: {pl_pct:+.2f}%)")

def save_execution_log(results):
    """Save execution log"""
    log_file = f"scripts-and-data/trade-logs/rebalance_phase1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    import json
    with open(log_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n[LOG] Execution log saved to: {log_file}")

def main():
    """Main execution"""
    print_separator("EMERGENCY PORTFOLIO REBALANCING - PHASE 1")
    print("IMMEDIATE ACTIONS TO RESTORE POSITIVE CASH")
    print("\nActions to be taken:")
    print("\nDEE-BOT:")
    print("  1. Cancel all pending buy orders (JPM, LMT, ABBV)")
    print("  2. Sell 160 PG @ market (~$24,355)")
    print("  3. Sell 136 CL @ market (~$10,763)")
    print("  → Expected cash: +$29,974 (positive balance restored)")
    print("\nSHORGAN-BOT:")
    print("  1. Cancel PEP short order")
    print("  2. Cover 132 PG short @ market (~$20,093)")
    print("  → Eliminates cross-bot PG exposure")

    # Check market status
    market_open = check_market_status()
    if not market_open:
        response = input("\nMarket is closed. Continue anyway? Orders will queue. (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted")
            return

    # Confirm execution
    print("\n" + "="*80)
    response = input("Proceed with Phase 1 rebalancing? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted")
        return

    # Execute Phase 1
    start_time = datetime.now()

    try:
        phase_1_dee_bot()
        phase_1_shorgan_bot()

        print_separator("PHASE 1 COMPLETE")
        print(f"Execution time: {(datetime.now() - start_time).total_seconds():.1f} seconds")

        print("\nNext steps:")
        print("1. Wait 5-10 minutes for all orders to fully settle")
        print("2. Run: python get_portfolio_status.py")
        print("3. Verify DEE-BOT cash is positive")
        print("4. Verify SHORGAN-BOT no longer has PG short")
        print("5. Review PORTFOLIO_REBALANCING_PLAN.md for Phase 2 actions")
        print("\nPhase 2 (Days 2-3):")
        print("- DEE-BOT: Trim tech positions, add healthcare/industrials")
        print("- SHORGAN-BOT: Clean up losing positions, add stop losses")

    except Exception as e:
        print(f"\n✗ ERROR during execution: {e}")
        print("Check positions manually and review logs")

if __name__ == "__main__":
    main()
