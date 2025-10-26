"""
[!] EMERGENCY KILL SWITCH [!]

Run this script to immediately:
1. Cancel ALL open orders
2. (Optionally) Close ALL positions

This is your PANIC BUTTON - use it if:
- System is executing bad trades
- You see unexpected behavior
- You want to stop everything NOW

Usage:
    python scripts/emergency/halt_all_trading.py
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import ClosePositionRequest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def emergency_halt(close_positions=False, paper=True):
    """
    Emergency halt - cancel all orders and optionally close positions

    Args:
        close_positions: If True, close ALL positions (use with caution)
        paper: If True, use paper trading (False for live account)
    """
    print("\n" + "="*70)
    print("[!] EMERGENCY TRADING HALT INITIATED [!]")
    print("="*70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'PAPER' if paper else '[!] LIVE [!]'}")
    print()

    # Determine which API keys to use
    if paper:
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')
    else:
        api_key = os.getenv('ALPACA_LIVE_API_KEY')
        secret_key = os.getenv('ALPACA_LIVE_SECRET_KEY')

    if not api_key or not secret_key:
        print("[X] ERROR: API credentials not found in .env")
        print("Please check your ALPACA_API_KEY and ALPACA_SECRET_KEY")
        return

    try:
        # Connect to Alpaca
        print(f"[*] Connecting to Alpaca ({'paper' if paper else 'LIVE'} account)...")
        client = TradingClient(
            api_key=api_key,
            secret_key=secret_key,
            paper=paper
        )

        # Get account info
        account = client.get_account()
        print(f"[*] Connected to account: {account.account_number}")
        print(f"[*] Current equity: ${float(account.equity):,.2f}")
        print()

        # Step 1: Cancel ALL open orders
        print("="*70)
        print("STEP 1: CANCELING ALL OPEN ORDERS")
        print("="*70)

        try:
            orders = client.get_orders()

            if not orders:
                print("[OK] No open orders to cancel")
            else:
                print(f"[*] Found {len(orders)} open orders")

                for order in orders:
                    try:
                        client.cancel_order_by_id(order.id)
                        print(f"  [OK] Canceled: {order.symbol} {order.side} {order.qty} @ {order.limit_price or 'market'}")
                    except Exception as e:
                        print(f"  [FAIL] Failed to cancel {order.symbol}: {e}")

                print(f"\n[OK] Canceled {len(orders)} orders")

        except Exception as e:
            print(f"[ERROR] Failed to retrieve orders: {e}")

        # Step 2: Close positions (OPTIONAL)
        if close_positions:
            print("\n" + "="*70)
            print("STEP 2: CLOSING ALL POSITIONS")
            print("="*70)
            print("[!] WARNING: This will SELL/COVER all your positions!")
            print()

            try:
                positions = client.get_all_positions()

                if not positions:
                    print("[OK] No open positions to close")
                else:
                    print(f"[*] Found {len(positions)} open positions")

                    for position in positions:
                        try:
                            # Close position at market
                            client.close_position(position.symbol)
                            side = "SELL" if float(position.qty) > 0 else "COVER"
                            print(f"  [OK] {side}: {position.symbol} ({abs(float(position.qty))} shares)")
                        except Exception as e:
                            print(f"  [FAIL] Failed to close {position.symbol}: {e}")

                    print(f"\n[OK] Initiated close for {len(positions)} positions")
                    print("[*] Market orders submitted - check fills in 1-2 minutes")

            except Exception as e:
                print(f"[ERROR] Failed to retrieve positions: {e}")
        else:
            print("\n" + "="*70)
            print("STEP 2: POSITIONS NOT CLOSED (use --close-positions to close)")
            print("="*70)

            try:
                positions = client.get_all_positions()
                if positions:
                    print(f"\n[INFO] You still have {len(positions)} open positions:")
                    for pos in positions:
                        pnl = float(pos.unrealized_pl)
                        pnl_pct = float(pos.unrealized_plpc) * 100
                        print(f"  • {pos.symbol}: {pos.qty} shares (P&L: ${pnl:,.2f} / {pnl_pct:+.2f}%)")
            except:
                pass

        # Summary
        print("\n" + "="*70)
        print("[OK] EMERGENCY HALT COMPLETE")
        print("="*70)
        print("\nActions Taken:")
        print("  [+] All open orders canceled")
        if close_positions:
            print("  [+] All positions closed")
        else:
            print("  [*] Positions remain open (you can close manually)")

        print("\nNext Steps:")
        print("  1. Verify in Alpaca dashboard")
        print("  2. Disable Task Scheduler automation:")
        print("     schtasks /change /tn \"AI Trading - Trade Execution\" /disable")
        print("  3. Review what triggered the halt")
        print("  4. Fix any issues before re-enabling")
        print()

    except Exception as e:
        print(f"\n[X] CRITICAL ERROR: {e}")
        print("If this script fails, log into Alpaca dashboard manually:")
        print("Paper: https://app.alpaca.markets/paper/dashboard")
        print("Live:  https://app.alpaca.markets/dashboard")


def main():
    """Main entry point with safety confirmations"""
    import argparse

    parser = argparse.ArgumentParser(description='Emergency trading halt')
    parser.add_argument('--close-positions', action='store_true',
                       help='Close ALL positions (not just orders)')
    parser.add_argument('--live', action='store_true',
                       help='Run on LIVE account (default: paper)')
    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompts')

    args = parser.parse_args()

    # Determine mode
    paper = not args.live
    mode = "PAPER" if paper else "[!] LIVE [!]"

    print("\n" + "="*70)
    print("[!] EMERGENCY TRADING HALT [!]")
    print("="*70)
    print(f"Mode: {mode}")
    print(f"Close Positions: {'YES' if args.close_positions else 'NO (orders only)'}")
    print()

    # Safety confirmation
    if not args.force:
        if not paper:
            print("[!] WARNING: You are about to halt LIVE TRADING with REAL MONEY!")
            print()

        confirm = input(f"Type 'HALT' to proceed with {mode} emergency halt: ")

        if confirm != "HALT":
            print("\n[X] Aborted - confirmation failed")
            print("You must type exactly: HALT")
            return

    # Execute halt
    emergency_halt(close_positions=args.close_positions, paper=paper)


if __name__ == "__main__":
    main()
