#!/usr/bin/env python3
"""
Portfolio Rebalancing - Phase 2 (Days 2-3)
DEE-BOT: Optimize portfolio allocation and diversification
SHORGAN-BOT: Clean up losing positions
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

def execute_trade(api, symbol, qty, side, order_type='market', limit_price=None, reason=""):
    """Execute a single trade with error handling"""
    try:
        order_params = {
            'symbol': symbol,
            'qty': abs(qty),
            'side': side,
            'type': order_type,
            'time_in_force': 'day'
        }

        if order_type == 'limit' and limit_price:
            order_params['limit_price'] = str(limit_price)

        price_str = f"@ ${limit_price}" if limit_price else "@ market"
        print(f"\n  Executing: {side.upper()} {abs(qty)} {symbol} {price_str}")
        if reason:
            print(f"  Reason: {reason}")

        order = api.submit_order(**order_params)
        print(f"  ✓ SUCCESS - Order ID: {order.id}")
        return True

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False

def phase_2_dee_bot_step1_trims():
    """DEE-BOT Step 1: Trim overweight positions"""
    print_separator("PHASE 2 - DEE-BOT: STEP 1 - TRIM OVERWEIGHT POSITIONS")

    account = dee_api.get_account()
    print(f"\nCurrent DEE-BOT Status:")
    print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"  Cash: ${float(account.cash):,.2f}")

    print("\nTrims to execute:")
    print("  1. AAPL: Sell 24 shares (reduce tech concentration)")
    print("  2. MSFT: Sell 4 shares (reduce tech concentration)")
    print("  3. CVX: Sell ALL (eliminate energy overlap with XOM)")

    response = input("\nProceed with DEE-BOT trims? (yes/no): ")
    if response.lower() != 'yes':
        print("Skipped")
        return

    # Trim AAPL
    execute_trade(dee_api, 'AAPL', 24, 'sell',
                  reason="Reduce tech from 38% to 31% of portfolio")
    time.sleep(1)

    # Trim MSFT
    execute_trade(dee_api, 'MSFT', 4, 'sell',
                  reason="Further reduce tech concentration")
    time.sleep(1)

    # Exit CVX
    try:
        position = dee_api.get_position('CVX')
        qty = int(float(position.qty))
        execute_trade(dee_api, 'CVX', qty, 'sell',
                      reason="Eliminate energy overlap (keeping XOM)")
    except:
        print("\n  CVX position not found or already sold")

    print("\n✓ DEE-BOT trims complete. Generated ~$13,012 cash.")

def phase_2_dee_bot_step2_adds():
    """DEE-BOT Step 2: Add diversification positions"""
    print_separator("PHASE 2 - DEE-BOT: STEP 2 - ADD DIVERSIFICATION")

    account = dee_api.get_account()
    print(f"\nCurrent DEE-BOT Status:")
    print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"  Cash: ${float(account.cash):,.2f}")

    print("\nNew positions to add:")
    print("  1. JNJ: Buy 40 shares @ $160 = $6,400 (Healthcare/Defensive)")
    print("  2. ABBV: Buy 35 shares @ $171 = $6,000 (Healthcare/Pharma)")
    print("  3. LMT: Buy 16 shares @ $550 = $8,800 (Defense/Industrials)")
    print("  4. CAT: Buy 25 shares @ $360 = $9,000 (Industrials/Infrastructure)")
    print("\n  Total investment: $30,200")

    cash = float(account.cash)
    if cash < 30200:
        print(f"\n⚠ WARNING: Cash (${cash:,.2f}) may be insufficient")
        print("Consider executing in smaller batches or adjusting quantities")

    response = input("\nProceed with DEE-BOT additions? (yes/no): ")
    if response.lower() != 'yes':
        print("Skipped")
        return

    # Add JNJ
    execute_trade(dee_api, 'JNJ', 40, 'buy', 'limit', 160.00,
                  reason="Add healthcare defensive position")
    time.sleep(1)

    # Add ABBV
    execute_trade(dee_api, 'ABBV', 35, 'buy', 'limit', 171.00,
                  reason="Add pharma with strong dividend")
    time.sleep(1)

    # Add LMT
    execute_trade(dee_api, 'LMT', 16, 'buy', 'limit', 550.00,
                  reason="Add defense/aerospace exposure")
    time.sleep(1)

    # Add CAT
    execute_trade(dee_api, 'CAT', 25, 'buy', 'limit', 360.00,
                  reason="Add industrials/infrastructure play")

    print("\n✓ DEE-BOT additions complete. Final allocation:")
    print("  Tech: 31% (AAPL, MSFT)")
    print("  Financials: 20% (JPM)")
    print("  Healthcare: 12% (JNJ, ABBV)")
    print("  Industrials/Defense: 18% (LMT, CAT)")
    print("  Energy: 5% (XOM)")
    print("  Consumer: 5% (WMT)")
    print("  Cash: 9%")

def phase_2_shorgan_bot_cleanup():
    """SHORGAN-BOT: Clean up losing and low-conviction positions"""
    print_separator("PHASE 2 - SHORGAN-BOT: PORTFOLIO CLEANUP")

    account = shorgan_api.get_account()
    print(f"\nCurrent SHORGAN-BOT Status:")
    print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"  Cash: ${float(account.cash):,.2f}")

    print("\nPositions to clean up (losers/low conviction):")
    print("  1. FUBO: Sell 1000 shares @ market (~$3,980, -2.21%)")
    print("  2. EMBC: Sell 68 shares @ market (~$976, -5.71%)")
    print("  3. GPK: Sell 142 shares @ market (~$2,752, -8.00%)")
    print("  4. MFIC: Sell 385 shares (50%) @ market (~$4,552, -2.75%)")
    print("\n  Total cash generation: ~$12,260")

    response = input("\nProceed with SHORGAN-BOT cleanup? (yes/no): ")
    if response.lower() != 'yes':
        print("Skipped")
        return

    # Sell losers
    positions_to_sell = [
        ('FUBO', 1000, "Streaming sector weak, cut losses"),
        ('EMBC', 68, "Biotech too risky, -5.71% loss"),
        ('GPK', 142, "Packaging sector weak, -8% loss"),
        ('MFIC', 385, "Trim 50% of micro-cap exposure")
    ]

    for symbol, qty, reason in positions_to_sell:
        try:
            position = shorgan_api.get_position(symbol)
            actual_qty = min(qty, int(float(position.qty)))
            execute_trade(shorgan_api, symbol, actual_qty, 'sell', reason=reason)
            time.sleep(1)
        except Exception as e:
            print(f"\n  Skipping {symbol}: {e}")

    print("\n✓ SHORGAN-BOT cleanup complete")
    print("\nFocus on high-conviction winners:")
    print("  RGTI: +98.30% (quantum computing)")
    print("  ORCL: +20.62% (cloud infrastructure)")
    print("  BTBT: +21.99% (crypto mining)")
    print("  SAVA: +44.53% (biotech)")
    print("  SRRK: +10.43% (digital media)")

def phase_2_shorgan_bot_stops():
    """SHORGAN-BOT: Add stop losses to short positions"""
    print_separator("PHASE 2 - SHORGAN-BOT: ADD STOP LOSSES TO SHORTS")

    print("\nStop loss recommendations for short positions:")
    print("  1. IONQ: Stop at $75.00 (entry price, protect +15.91% profit)")
    print("  2. NCNO: Stop at $30.00 (entry price, protect +11.51% profit)")
    print("  3. CVX: Stop at $160.00 (allow some wiggle room from $157.27 entry)")

    print("\nNote: Stop losses for short positions must be manually set in Alpaca")
    print("or monitored daily. Programmatic stops on shorts require buy-stop orders.")

    print("\nManual monitoring checklist:")
    print("  - If IONQ closes above $75, cover immediately")
    print("  - If NCNO closes above $30, cover immediately")
    print("  - If CVX closes above $160, cover immediately")

    response = input("\nAcknowledge stop loss monitoring? (yes/no): ")
    if response.lower() == 'yes':
        print("✓ Stop loss monitoring acknowledged")

def show_final_status():
    """Show final portfolio status"""
    print_separator("PHASE 2 COMPLETE - FINAL STATUS")

    # DEE-BOT
    dee_account = dee_api.get_account()
    print("\nDEE-BOT Final Status:")
    print(f"  Portfolio Value: ${float(dee_account.portfolio_value):,.2f}")
    print(f"  Cash: ${float(dee_account.cash):,.2f} ({float(dee_account.cash)/float(dee_account.portfolio_value)*100:.1f}%)")
    print(f"  Long Market Value: ${float(dee_account.long_market_value):,.2f}")

    dee_positions = dee_api.list_positions()
    print(f"  Total Positions: {len(dee_positions)}")

    # SHORGAN-BOT
    shorgan_account = shorgan_api.get_account()
    print("\nSHORGAN-BOT Final Status:")
    print(f"  Portfolio Value: ${float(shorgan_account.portfolio_value):,.2f}")
    print(f"  Cash: ${float(shorgan_account.cash):,.2f} ({float(shorgan_account.cash)/float(shorgan_account.portfolio_value)*100:.1f}%)")
    print(f"  Long Market Value: ${float(shorgan_account.long_market_value):,.2f}")
    print(f"  Short Market Value: ${float(shorgan_account.short_market_value):,.2f}")

    shorgan_positions = shorgan_api.list_positions()
    print(f"  Total Positions: {len(shorgan_positions)}")

    # Combined
    total_value = float(dee_account.portfolio_value) + float(shorgan_account.portfolio_value)
    profit = total_value - 200000
    profit_pct = (profit / 200000) * 100

    print("\nCombined Portfolio:")
    print(f"  Total Value: ${total_value:,.2f}")
    print(f"  Starting Capital: $200,000.00")
    print(f"  Total Profit/Loss: ${profit:,.2f} ({profit_pct:+.2f}%)")

    print("\n✓ Rebalancing complete!")
    print("\nNext steps:")
    print("  1. Monitor for order fills over next 1-2 days")
    print("  2. Run 'python get_portfolio_status.py' daily")
    print("  3. Set calendar reminders for stop loss monitoring")
    print("  4. Review PORTFOLIO_REBALANCING_PLAN.md weekly")

def main():
    """Main execution"""
    print_separator("PORTFOLIO REBALANCING - PHASE 2")
    print("GRADUAL OPTIMIZATION AND CLEANUP (Days 2-3)")

    print("\nThis script will execute Phase 2 rebalancing:")
    print("\nDEE-BOT (4 steps):")
    print("  Step 1: Trim overweight positions (AAPL, MSFT, CVX)")
    print("  Step 2: Add diversification (JNJ, ABBV, LMT, CAT)")
    print("\nSHORGAN-BOT (2 steps):")
    print("  Step 3: Clean up losing positions")
    print("  Step 4: Set stop loss monitoring")

    print("\nNote: You can execute steps individually or all at once.")

    # Check market status
    clock = dee_api.get_clock()
    if not clock.is_open:
        print(f"\n⚠ WARNING: Market is CLOSED")
        print(f"Next open: {clock.next_open}")
        response = input("\nContinue? Orders will queue for market open. (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted")
            return

    print("\n" + "="*80)
    print("SELECT EXECUTION MODE:")
    print("  1. Execute ALL steps automatically")
    print("  2. Execute DEE-BOT only (Steps 1-2)")
    print("  3. Execute SHORGAN-BOT only (Steps 3-4)")
    print("  4. Execute individual steps (prompted)")
    print("  5. Exit")

    choice = input("\nEnter choice (1-5): ")

    if choice == '1':
        # Execute all
        phase_2_dee_bot_step1_trims()
        time.sleep(2)
        phase_2_dee_bot_step2_adds()
        time.sleep(2)
        phase_2_shorgan_bot_cleanup()
        time.sleep(2)
        phase_2_shorgan_bot_stops()
        show_final_status()

    elif choice == '2':
        # DEE-BOT only
        phase_2_dee_bot_step1_trims()
        time.sleep(2)
        phase_2_dee_bot_step2_adds()
        print("\n✓ DEE-BOT rebalancing complete")

    elif choice == '3':
        # SHORGAN-BOT only
        phase_2_shorgan_bot_cleanup()
        time.sleep(2)
        phase_2_shorgan_bot_stops()
        print("\n✓ SHORGAN-BOT rebalancing complete")

    elif choice == '4':
        # Individual steps
        print("\nExecuting individual steps with prompts...")
        phase_2_dee_bot_step1_trims()
        time.sleep(2)
        phase_2_dee_bot_step2_adds()
        time.sleep(2)
        phase_2_shorgan_bot_cleanup()
        time.sleep(2)
        phase_2_shorgan_bot_stops()
        show_final_status()

    else:
        print("Exiting...")
        return

if __name__ == "__main__":
    main()
