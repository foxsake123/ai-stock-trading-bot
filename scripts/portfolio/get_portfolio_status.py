#!/usr/bin/env python3
"""
Quick Portfolio Status Checker
Displays current portfolio value and positions for both DEE-BOT and SHORGAN-BOT
"""

import os
import sys
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass

# Load environment variables
load_dotenv()

def get_portfolio_status():
    """Get current portfolio status from Alpaca"""

    # Initialize Alpaca client
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')

    if not api_key or not secret_key:
        print("ERROR: ALPACA_API_KEY and ALPACA_SECRET_KEY must be set in .env file")
        sys.exit(1)

    try:
        client = TradingClient(api_key, secret_key, paper=(base_url != 'https://api.alpaca.markets'))

        # Get account info
        account = client.get_account()

        # Get all positions
        positions = client.get_all_positions()

        # Print header
        print("\n" + "="*80)
        print("AI TRADING BOT - PORTFOLIO STATUS")
        print("="*80)

        # Account summary
        print(f"\nACCOUNT SUMMARY")
        print(f"   Portfolio Value:    ${float(account.portfolio_value):,.2f}")
        print(f"   Cash Available:     ${float(account.cash):,.2f}")
        print(f"   Buying Power:       ${float(account.buying_power):,.2f}")
        print(f"   Equity:             ${float(account.equity):,.2f}")

        # Calculate P&L
        initial_value = 200000.00  # Starting capital
        total_return = float(account.portfolio_value) - initial_value
        total_return_pct = (total_return / initial_value) * 100

        print(f"\nPERFORMANCE")
        print(f"   Total Return:       ${total_return:,.2f} ({total_return_pct:+.2f}%)")
        print(f"   Day P&L:            ${float(account.equity) - float(account.last_equity):,.2f}")

        # Positions
        print(f"\nPOSITIONS ({len(positions)} total)")

        if not positions:
            print("   No open positions")
        else:
            # Sort positions by unrealized P&L
            positions_sorted = sorted(positions, key=lambda p: float(p.unrealized_pl), reverse=True)

            print(f"\n   {'Symbol':<8} {'Qty':<8} {'Entry':<10} {'Current':<10} {'P&L':<12} {'P&L %':<8}")
            print(f"   {'-'*70}")

            total_pl = 0
            for pos in positions_sorted:
                symbol = pos.symbol
                qty = int(pos.qty)
                avg_entry = float(pos.avg_entry_price)
                current_price = float(pos.current_price)
                unrealized_pl = float(pos.unrealized_pl)
                unrealized_plpc = float(pos.unrealized_plpc) * 100

                total_pl += unrealized_pl

                # Color code P&L
                pl_symbol = "+" if unrealized_pl >= 0 else ""

                print(f"   {symbol:<8} {qty:<8} ${avg_entry:<9.2f} ${current_price:<9.2f} {pl_symbol}${unrealized_pl:<11.2f} {unrealized_plpc:+.2f}%")

            print(f"   {'-'*70}")
            print(f"   {'TOTAL':<8} {'':<8} {'':<10} {'':<10} ${total_pl:<11.2f}")

        # Check for any orders
        orders = client.get_orders()
        open_orders = [o for o in orders if o.status in ['new', 'partially_filled', 'accepted']]

        if open_orders:
            print(f"\nOPEN ORDERS ({len(open_orders)} total)")
            for order in open_orders[:10]:  # Show max 10
                side = order.side.upper()
                print(f"   {side:<5} {order.qty} {order.symbol} @ ${order.limit_price or order.stop_price or 'MARKET'} ({order.status})")

        print("\n" + "="*80 + "\n")

    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    get_portfolio_status()
