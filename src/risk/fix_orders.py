"""
Fix Pending Orders - Adjust Limit Prices or Convert to Market
"""

import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot credentials from environment variables (NEVER hardcode!)
DEE_BOT_API = os.getenv("ALPACA_API_KEY_DEE")
DEE_BOT_SECRET = os.getenv("ALPACA_SECRET_KEY_DEE")

SHORGAN_API = os.getenv("ALPACA_API_KEY_SHORGAN")
SHORGAN_SECRET = os.getenv("ALPACA_SECRET_KEY_SHORGAN")

BASE_URL = "https://paper-api.alpaca.markets"

def fix_dee_bot_orders():
    """Cancel and replace DEE-BOT orders with market prices"""

    if not DEE_BOT_API or not DEE_BOT_SECRET:
        print("[ERROR] DEE-BOT credentials not found in environment variables")
        return

    try:
        api = tradeapi.REST(DEE_BOT_API, DEE_BOT_SECRET, BASE_URL, api_version='v2')

        print("DEE-BOT ORDER ADJUSTMENT")
        print("="*50)

        # Get pending orders
        pending_orders = api.list_orders(status='new')

        if pending_orders:
            print(f"Found {len(pending_orders)} pending orders")

            # Cancel all pending orders first
            for order in pending_orders:
                if order.symbol in ['AAPL', 'MSFT', 'JPM']:  # Skip NVDA (wrong order)
                    try:
                        api.cancel_order(order.id)
                        print(f"[OK] Cancelled {order.symbol} order: {order.id}")
                    except Exception as e:
                        print(f"[ERROR] Failed to cancel {order.symbol}: {str(e)}")

            # Place new market orders for core positions
            core_positions = [
                {'symbol': 'AAPL', 'qty': 61, 'reason': 'iPhone 16 momentum'},
                {'symbol': 'MSFT', 'qty': 29, 'reason': 'AI/Copilot growth'},
                {'symbol': 'JPM', 'qty': 71, 'reason': 'Banking strength'}
            ]

            for pos in core_positions:
                try:
                    order = api.submit_order(
                        symbol=pos['symbol'],
                        qty=pos['qty'],
                        side='buy',
                        type='market',
                        time_in_force='day'
                    )
                    print(f"[OK] Placed market order: {pos['symbol']} {pos['qty']} shares")
                    print(f"   Order ID: {order.id}")
                    print(f"   Reason: {pos['reason']}")
                except Exception as e:
                    print(f"[ERROR] Failed to place {pos['symbol']} order: {str(e)}")
        else:
            print("No pending orders found")

    except Exception as e:
        print(f"Error connecting to DEE-BOT: {str(e)}")

def fix_shorgan_orders():
    """Fix SHORGAN-BOT catalyst orders"""

    if not SHORGAN_API or not SHORGAN_SECRET:
        print("[ERROR] SHORGAN-BOT credentials not found in environment variables")
        return

    try:
        api = tradeapi.REST(SHORGAN_API, SHORGAN_SECRET, BASE_URL, api_version='v2')

        print("\nSHORGAN-BOT ORDER ADJUSTMENT")
        print("="*50)

        # Get pending orders
        pending_orders = api.list_orders(status='new')

        catalyst_orders = []
        for order in pending_orders:
            if order.symbol in ['PLTR', 'CRWD']:  # Our catalyst trades
                catalyst_orders.append(order)

        if catalyst_orders:
            print(f"Found {len(catalyst_orders)} catalyst orders pending")

            for order in catalyst_orders:
                # Cancel and replace with market order
                try:
                    api.cancel_order(order.id)
                    print(f"[OK] Cancelled {order.symbol} limit order")

                    # Place market order
                    new_order = api.submit_order(
                        symbol=order.symbol,
                        qty=order.qty,
                        side=order.side,
                        type='market',
                        time_in_force='day'
                    )
                    print(f"[OK] Placed market order: {order.symbol} {order.qty} shares")
                    print(f"   Order ID: {new_order.id}")

                except Exception as e:
                    print(f"[ERROR] Failed to fix {order.symbol}: {str(e)}")
        else:
            print("No catalyst orders found to fix")

    except Exception as e:
        print(f"Error connecting to SHORGAN-BOT: {str(e)}")

def main():
    """Fix both bots' pending orders"""
    print("FIXING PENDING ORDERS")
    print("="*60)
    print("Converting limit orders to market orders for immediate execution")
    print("="*60)

    # Fix DEE-BOT orders
    fix_dee_bot_orders()

    # Fix SHORGAN-BOT orders
    fix_shorgan_orders()

    print("\n" + "="*60)
    print("ORDER FIXES COMPLETE")
    print("Run position_monitor.py again to verify fills")
    print("="*60)

if __name__ == "__main__":
    main()
