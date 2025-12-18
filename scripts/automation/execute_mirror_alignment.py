"""
Execute Mirror Alignment for SHORGAN Paper -> Live
Run this at market open (9:30 AM ET) to align Live with Paper positions.

This script:
1. Cancels any remaining open orders
2. Waits for market to be open
3. Sells positions in Live that aren't in Paper
4. Buys positions that Paper has but Live doesn't (scaled to 3%)
"""

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from dotenv import load_dotenv
import os
import time
from datetime import datetime
import pytz

load_dotenv()

# Configuration
LIVE_CAPITAL = 3000  # $3K live account
PAPER_CAPITAL = 100000  # $100K paper account
SCALE_FACTOR = LIVE_CAPITAL / PAPER_CAPITAL  # 0.03 or 3%
MIN_POSITION_VALUE = 75  # Minimum $75 position
MAX_POSITION_VALUE = 300  # Maximum $300 position (10% of $3K)
MAX_SHARE_PRICE = 200  # Skip stocks over $200/share

def get_clients():
    paper = TradingClient(
        os.getenv('ALPACA_API_KEY_SHORGAN'),
        os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
        paper=True
    )
    live = TradingClient(
        os.getenv('ALPACA_API_KEY_SHORGAN_LIVE'),
        os.getenv('ALPACA_SECRET_KEY_SHORGAN_LIVE'),
        paper=False
    )
    return paper, live

def wait_for_market_open(live):
    """Wait for market to be open"""
    et = pytz.timezone('America/New_York')

    while True:
        clock = live.get_clock()
        if clock.is_open:
            print("[OK] Market is open!")
            return True

        now = datetime.now(et)
        print(f"[WAIT] Market closed. Current time: {now.strftime('%H:%M:%S')} ET")
        print(f"       Next open: {clock.next_open}")

        # Wait 30 seconds before checking again
        time.sleep(30)

def cancel_all_open_orders(live):
    """Cancel all open orders to free up shares"""
    request = GetOrdersRequest(status=QueryOrderStatus.OPEN)
    open_orders = live.get_orders(request)

    if not open_orders:
        print("[OK] No open orders to cancel")
        return

    print(f"[*] Canceling {len(open_orders)} open orders...")
    for order in open_orders:
        try:
            live.cancel_order_by_id(order.id)
            print(f"    [OK] Canceled {order.symbol} {order.side} {order.qty}")
        except Exception as e:
            print(f"    [WARN] Could not cancel {order.symbol}: {str(e)[:50]}")

    # Wait for cancellations to process
    print("[*] Waiting 5 seconds for cancellations to process...")
    time.sleep(5)

def execute_alignment():
    """Execute the full alignment process"""
    paper, live = get_clients()

    print()
    print("=" * 70)
    print("SHORGAN PAPER -> LIVE MIRROR ALIGNMENT")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Step 1: Cancel all open orders
    cancel_all_open_orders(live)

    # Step 2: Wait for market to be open
    if not live.get_clock().is_open:
        print("[*] Waiting for market to open...")
        wait_for_market_open(live)

    # Step 3: Get current positions
    paper_positions = {p.symbol: {
        'qty': float(p.qty),
        'value': abs(float(p.market_value)),
        'price': float(p.current_price),
        'side': 'LONG' if float(p.qty) > 0 else 'SHORT'
    } for p in paper.get_all_positions()}

    live_positions = {p.symbol: {
        'qty': float(p.qty),
        'value': abs(float(p.market_value)),
        'price': float(p.current_price)
    } for p in live.get_all_positions()}

    live_account = live.get_account()
    print(f"[*] Live Buying Power: ${float(live_account.buying_power):,.2f}")
    print(f"[*] Live Cash: ${float(live_account.cash):,.2f}")
    print()

    # Step 4: Execute SELLS first (positions in Live but not in Paper)
    print("-" * 70)
    print("PHASE 1: SELLING POSITIONS NOT IN PAPER")
    print("-" * 70)

    sells_executed = 0
    sells_failed = 0

    for symbol, live_data in sorted(live_positions.items()):
        if symbol not in paper_positions:
            # Sell entire position
            shares = int(live_data['qty'])
            try:
                order = MarketOrderRequest(
                    symbol=symbol,
                    qty=shares,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )
                result = live.submit_order(order)
                print(f"  [OK] SELL {shares} {symbol} @ market - Order {result.id[:8]}")
                sells_executed += 1
            except Exception as e:
                print(f"  [FAIL] SELL {shares} {symbol} - {str(e)[:50]}")
                sells_failed += 1
        elif paper_positions[symbol]['side'] == 'SHORT':
            # Paper is short, Live can't short - sell Live position
            shares = int(live_data['qty'])
            try:
                order = MarketOrderRequest(
                    symbol=symbol,
                    qty=shares,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )
                result = live.submit_order(order)
                print(f"  [OK] SELL {shares} {symbol} @ market (Paper is SHORT) - Order {result.id[:8]}")
                sells_executed += 1
            except Exception as e:
                print(f"  [FAIL] SELL {shares} {symbol} - {str(e)[:50]}")
                sells_failed += 1

    print(f"\n  Sells: {sells_executed} executed, {sells_failed} failed")

    # Wait for sells to settle
    if sells_executed > 0:
        print("\n[*] Waiting 10 seconds for sells to settle...")
        time.sleep(10)

        # Refresh buying power
        live_account = live.get_account()
        print(f"[*] Updated Buying Power: ${float(live_account.buying_power):,.2f}")

    # Step 5: Execute BUYS (positions in Paper but not in Live)
    print()
    print("-" * 70)
    print("PHASE 2: BUYING POSITIONS FROM PAPER")
    print("-" * 70)

    # Refresh live positions after sells
    live_positions = {p.symbol: {
        'qty': float(p.qty),
        'value': abs(float(p.market_value)),
        'price': float(p.current_price)
    } for p in live.get_all_positions()}

    buys_executed = 0
    buys_failed = 0
    buys_skipped = 0
    total_bought = 0

    # Sort by paper position value (largest first)
    paper_sorted = sorted(paper_positions.items(), key=lambda x: x[1]['value'], reverse=True)

    for symbol, paper_data in paper_sorted:
        # Skip shorts
        if paper_data['side'] == 'SHORT':
            print(f"  [SKIP] {symbol}: Paper is SHORT (Live can't short)")
            buys_skipped += 1
            continue

        # Skip expensive stocks
        if paper_data['price'] > MAX_SHARE_PRICE:
            print(f"  [SKIP] {symbol}: ${paper_data['price']:.2f}/share > ${MAX_SHARE_PRICE} limit")
            buys_skipped += 1
            continue

        # Calculate target shares
        target_value = paper_data['value'] * SCALE_FACTOR
        target_value = max(MIN_POSITION_VALUE, min(MAX_POSITION_VALUE, target_value))
        target_shares = int(target_value / paper_data['price'])

        if target_shares < 1:
            print(f"  [SKIP] {symbol}: Would need <1 share at ${paper_data['price']:.2f}")
            buys_skipped += 1
            continue

        # Current shares in Live
        current_shares = int(live_positions.get(symbol, {}).get('qty', 0))
        shares_to_buy = target_shares - current_shares

        if shares_to_buy <= 0:
            if current_shares > 0:
                print(f"  [OK] {symbol}: Already have {current_shares} shares (target: {target_shares})")
            continue

        # Check buying power
        estimated_cost = shares_to_buy * paper_data['price']
        live_account = live.get_account()
        buying_power = float(live_account.buying_power)

        if estimated_cost > buying_power:
            # Reduce shares to fit buying power
            affordable_shares = int(buying_power / paper_data['price'])
            if affordable_shares < 1:
                print(f"  [SKIP] {symbol}: Need ${estimated_cost:.0f}, have ${buying_power:.0f}")
                buys_skipped += 1
                continue
            shares_to_buy = affordable_shares
            estimated_cost = shares_to_buy * paper_data['price']

        try:
            order = MarketOrderRequest(
                symbol=symbol,
                qty=shares_to_buy,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )
            result = live.submit_order(order)
            print(f"  [OK] BUY {shares_to_buy} {symbol} @ market (~${estimated_cost:.0f}) - Order {result.id[:8]}")
            buys_executed += 1
            total_bought += estimated_cost

            # Small delay between orders
            time.sleep(0.5)

        except Exception as e:
            print(f"  [FAIL] BUY {shares_to_buy} {symbol} - {str(e)[:50]}")
            buys_failed += 1

    print(f"\n  Buys: {buys_executed} executed, {buys_failed} failed, {buys_skipped} skipped")
    print(f"  Total bought: ~${total_bought:,.0f}")

    # Final summary
    print()
    print("=" * 70)
    print("ALIGNMENT COMPLETE")
    print("=" * 70)

    # Wait for orders to process
    time.sleep(5)

    # Get final state
    live_account = live.get_account()
    live_positions = live.get_all_positions()

    print(f"Portfolio Value: ${float(live_account.portfolio_value):,.2f}")
    print(f"Cash: ${float(live_account.cash):,.2f}")
    print(f"Positions: {len(live_positions)}")
    print()
    print("Current Holdings:")
    for p in sorted(live_positions, key=lambda x: float(x.market_value), reverse=True):
        print(f"  {p.symbol:6} {p.qty:>5} shares @ ${float(p.current_price):>8.2f} = ${float(p.market_value):>8.2f}")

if __name__ == "__main__":
    execute_alignment()
