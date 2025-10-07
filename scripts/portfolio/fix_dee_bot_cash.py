#!/usr/bin/env python3
"""
Fix DEE-BOT Negative Cash Balance
Sell positions to restore positive cash
"""

import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv

load_dotenv()

dee_api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY_DEE'),
    os.getenv('ALPACA_SECRET_KEY_DEE'),
    'https://paper-api.alpaca.markets',
    api_version='v2'
)

def main():
    print("="*80)
    print("DEE-BOT EMERGENCY CASH REBALANCE")
    print("="*80)

    # Check current status
    account = dee_api.get_account()
    cash = float(account.cash)
    portfolio_value = float(account.portfolio_value)

    print(f"\nCurrent Status:")
    print(f"  Portfolio Value: ${portfolio_value:,.2f}")
    print(f"  Cash Balance: ${cash:,.2f}")
    print(f"  Long Market Value: ${float(account.long_market_value):,.2f}")

    if cash >= 0:
        print(f"\n[OK] Cash balance is positive. No action needed.")
        return

    print(f"\n[WARNING] NEGATIVE CASH: ${cash:,.2f}")
    print(f"Need to raise: ${abs(cash) + 1000:,.2f} (negative + $1000 buffer)")

    # Cancel all pending orders first
    print("\n[STEP 1] Canceling all pending orders...")
    orders = dee_api.list_orders(status='open')
    for order in orders:
        try:
            print(f"  Canceling: {order.side} {order.qty} {order.symbol}")
            dee_api.cancel_order(order.id)
        except Exception as e:
            print(f"  Error: {e}")

    # Get all positions
    positions = dee_api.list_positions()

    # Sort by P/L percentage (sell losers first, or smallest positions)
    sorted_positions = sorted(positions, key=lambda p: float(p.unrealized_plpc))

    print(f"\n[STEP 2] Selling positions to restore positive cash...")
    print(f"\nCurrent positions (sorted by P/L%):")
    for pos in sorted_positions:
        pnl_pct = float(pos.unrealized_plpc) * 100
        market_value = float(pos.market_value)
        print(f"  {pos.symbol:6} ${market_value:>10,.2f}  {pnl_pct:>7.2f}%")

    # Strategy: Sell positions to raise needed cash
    # Priority: Sell positions with smallest losses or gains first
    target_raise = abs(cash) + 1000  # Add $1000 buffer
    total_raised = 0

    print(f"\nTarget to raise: ${target_raise:,.2f}")
    print(f"\nExecuting sales...")

    for pos in sorted_positions:
        if total_raised >= target_raise:
            break

        market_value = float(pos.market_value)
        qty = int(float(pos.qty))

        # Sell this position
        try:
            print(f"\n  Selling {qty} {pos.symbol} (${market_value:,.2f})...")
            order = dee_api.submit_order(
                symbol=pos.symbol,
                qty=qty,
                side='sell',
                type='market',
                time_in_force='day'
            )
            print(f"  [OK] Order placed: {order.id}")
            total_raised += market_value
            print(f"  Running total raised: ${total_raised:,.2f}")

            if total_raised >= target_raise:
                print(f"\n[SUCCESS] Target reached! Raised ${total_raised:,.2f}")
                break

        except Exception as e:
            print(f"  [ERROR] Error selling {pos.symbol}: {e}")

    # Final status
    print("\n" + "="*80)
    print("REBALANCE COMPLETE")
    print("="*80)
    print(f"\nPositions sold to raise cash: ${total_raised:,.2f}")
    print(f"\nWait for market open for orders to execute.")
    print(f"Expected new cash balance: ${cash + total_raised:,.2f}")
    print("\nRe-check portfolio status after market open.")

if __name__ == "__main__":
    main()
