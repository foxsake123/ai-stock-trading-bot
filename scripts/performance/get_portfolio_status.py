#!/usr/bin/env python3
"""Get current portfolio status for both bots"""

import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize APIs
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

def print_account_info(api, bot_name):
    """Print account summary"""
    account = api.get_account()
    print(f"\n{'='*80}")
    print(f"{bot_name} ACCOUNT STATUS")
    print(f"{'='*80}")
    print(f"Portfolio Value:     ${float(account.portfolio_value):>15,.2f}")
    print(f"Cash:                ${float(account.cash):>15,.2f}")
    print(f"Buying Power:        ${float(account.buying_power):>15,.2f}")
    print(f"Long Market Value:   ${float(account.long_market_value):>15,.2f}")
    print(f"Short Market Value:  ${float(account.short_market_value):>15,.2f}")
    print(f"Equity:              ${float(account.equity):>15,.2f}")
    print(f"Last Equity:         ${float(account.last_equity):>15,.2f}")

    return account

def print_positions(api, bot_name):
    """Print all positions"""
    positions = api.list_positions()

    if not positions:
        print(f"\n{bot_name}: No positions")
        return []

    print(f"\n{bot_name} POSITIONS:")
    print(f"{'Symbol':<8} {'Qty':<10} {'Avg Entry':<12} {'Current':<12} {'Market Value':<15} {'P/L $':<12} {'P/L %':<10}")
    print("-" * 95)

    long_positions = []
    short_positions = []

    for p in positions:
        qty = float(p.qty)
        if qty > 0:
            long_positions.append(p)
        else:
            short_positions.append(p)

    # Print long positions
    if long_positions:
        print("\nLONG POSITIONS:")
        for p in sorted(long_positions, key=lambda x: abs(float(x.market_value)), reverse=True):
            pl_pct = (float(p.unrealized_pl) / abs(float(p.cost_basis))) * 100 if float(p.cost_basis) != 0 else 0
            print(f"{p.symbol:<8} {p.qty:<10} ${float(p.avg_entry_price):<11.2f} ${float(p.current_price):<11.2f} ${float(p.market_value):<14.2f} ${float(p.unrealized_pl):<11.2f} {pl_pct:>8.2f}%")

    # Print short positions
    if short_positions:
        print("\nSHORT POSITIONS:")
        for p in sorted(short_positions, key=lambda x: float(x.market_value), reverse=True):
            pl_pct = (float(p.unrealized_pl) / abs(float(p.cost_basis))) * 100 if float(p.cost_basis) != 0 else 0
            print(f"{p.symbol:<8} {p.qty:<10} ${float(p.avg_entry_price):<11.2f} ${float(p.current_price):<11.2f} ${float(p.market_value):<14.2f} ${float(p.unrealized_pl):<11.2f} {pl_pct:>8.2f}%")

    return positions

def print_open_orders(api, bot_name):
    """Print all open orders"""
    orders = api.list_orders(status='open')

    if not orders:
        print(f"\n{bot_name}: No open orders")
        return []

    print(f"\n{bot_name} OPEN ORDERS ({len(orders)} total):")
    print(f"{'Symbol':<8} {'Side':<6} {'Qty':<8} {'Type':<10} {'Limit Price':<15} {'Status':<12} {'Created':<20}")
    print("-" * 95)

    for o in orders:
        limit_price = f"${float(o.limit_price):.2f}" if o.limit_price else "MARKET"
        created = o.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(o, 'created_at') else 'N/A'
        print(f"{o.symbol:<8} {o.side.upper():<6} {o.qty:<8} {o.type:<10} {limit_price:<15} {o.status:<12} {created:<20}")

    return orders

if __name__ == "__main__":
    print("\nFetching portfolio data...")

    # DEE-BOT
    dee_account = print_account_info(dee_api, "DEE-BOT")
    dee_positions = print_positions(dee_api, "DEE-BOT")
    dee_orders = print_open_orders(dee_api, "DEE-BOT")

    # SHORGAN-BOT
    shorgan_account = print_account_info(shorgan_api, "SHORGAN-BOT")
    shorgan_positions = print_positions(shorgan_api, "SHORGAN-BOT")
    shorgan_orders = print_open_orders(shorgan_api, "SHORGAN-BOT")

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"DEE-BOT Total Value:     ${float(dee_account.portfolio_value):>15,.2f}")
    print(f"SHORGAN-BOT Total Value: ${float(shorgan_account.portfolio_value):>15,.2f}")
    print(f"Combined Value:          ${float(dee_account.portfolio_value) + float(shorgan_account.portfolio_value):>15,.2f}")
    print(f"\nStarting Capital:        ${200000:>15,.2f}")
    total_value = float(dee_account.portfolio_value) + float(shorgan_account.portfolio_value)
    profit = total_value - 200000
    profit_pct = (profit / 200000) * 100
    print(f"Total Profit/Loss:       ${profit:>15,.2f} ({profit_pct:+.2f}%)")
    print()
