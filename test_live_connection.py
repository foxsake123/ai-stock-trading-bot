#!/usr/bin/env python3
"""
Test SHORGAN-BOT Live API Connection
Run this BEFORE enabling live trading to verify everything works
"""

import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

print("="*80)
print("TESTING SHORGAN-BOT LIVE ACCOUNT CONNECTION")
print("="*80)

# Get live API keys
live_key = os.getenv('ALPACA_LIVE_API_KEY_SHORGAN')
live_secret = os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN')

if not live_key or not live_secret:
    print("\n❌ LIVE API KEYS NOT FOUND IN .ENV")
    print("\nPlease add these lines to your .env file:")
    print("ALPACA_LIVE_API_KEY_SHORGAN=your_key_here")
    print("ALPACA_LIVE_SECRET_KEY_SHORGAN=your_secret_here")
    exit(1)

print(f"\n✅ Live API Key found: {live_key[:15]}...")
print(f"✅ Live Secret found: {live_secret[:15]}...")

try:
    # Connect to LIVE account
    api = tradeapi.REST(
        live_key,
        live_secret,
        'https://api.alpaca.markets',  # LIVE URL
        api_version='v2'
    )

    print("\n" + "="*80)
    print("ACCOUNT INFORMATION")
    print("="*80)

    account = api.get_account()

    print(f"\n✅ CONNECTION SUCCESSFUL - LIVE ACCOUNT")
    print(f"\nAccount ID: {account.id}")
    print(f"Account Number: {account.account_number}")
    print(f"Account Status: {account.status}")
    print(f"Account Blocked: {account.account_blocked}")
    print(f"Trading Blocked: {account.trading_blocked}")

    print(f"\n" + "="*80)
    print("BALANCE & BUYING POWER")
    print("="*80)

    cash = float(account.cash)
    portfolio_value = float(account.portfolio_value)
    buying_power = float(account.buying_power)

    print(f"\nCash: ${cash:,.2f}")
    print(f"Portfolio Value: ${portfolio_value:,.2f}")
    print(f"Buying Power: ${buying_power:,.2f}")
    print(f"Equity: ${float(account.equity):,.2f}")

    # Warnings
    if portfolio_value < 1000:
        print(f"\n⚠️  WARNING: Portfolio value (${portfolio_value:,.2f}) is less than expected $1,000")

    if buying_power < 500:
        print(f"\n⚠️  WARNING: Low buying power (${buying_power:,.2f})")

    print(f"\n" + "="*80)
    print("DAY TRADING & MARGIN")
    print("="*80)

    print(f"\nPattern Day Trader: {account.pattern_day_trader}")
    print(f"Day Trade Count: {account.daytrade_count}")
    print(f"Multiplier: {account.multiplier}")
    print(f"Shorting Enabled: {account.shorting_enabled}")

    print(f"\n" + "="*80)
    print("CURRENT POSITIONS")
    print("="*80)

    positions = api.list_positions()
    print(f"\nOpen Positions: {len(positions)}")

    if positions:
        for pos in positions:
            pnl = float(pos.unrealized_pl)
            pnl_pct = float(pos.unrealized_plpc) * 100
            print(f"\n  {pos.symbol}:")
            print(f"    Qty: {pos.qty} shares")
            print(f"    Avg Entry: ${float(pos.avg_entry_price):.2f}")
            print(f"    Current: ${float(pos.current_price):.2f}")
            print(f"    P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)")
    else:
        print("  None")

    print(f"\n" + "="*80)
    print("OPEN ORDERS")
    print("="*80)

    orders = api.list_orders(status='open')
    print(f"\nOpen Orders: {len(orders)}")

    if orders:
        for order in orders:
            print(f"\n  {order.symbol}:")
            print(f"    Side: {order.side}")
            print(f"    Qty: {order.qty}")
            print(f"    Type: {order.type}")
            print(f"    Status: {order.status}")
    else:
        print("  None")

    print(f"\n" + "="*80)
    print("READINESS CHECK")
    print("="*80)

    ready = True
    issues = []

    if account.status != 'ACTIVE':
        ready = False
        issues.append(f"Account status is {account.status}, not ACTIVE")

    if account.account_blocked:
        ready = False
        issues.append("Account is blocked")

    if account.trading_blocked:
        ready = False
        issues.append("Trading is blocked")

    if portfolio_value < 500:
        ready = False
        issues.append(f"Portfolio value too low: ${portfolio_value:,.2f}")

    if buying_power < 100:
        ready = False
        issues.append(f"Buying power too low: ${buying_power:,.2f}")

    if ready:
        print("\n✅ ACCOUNT READY FOR LIVE TRADING")
        print("\nYour settings:")
        print(f"  • Max Position Size: $100")
        print(f"  • Max Positions: 10")
        print(f"  • Daily Loss Limit: $100 (10% of capital)")
        print(f"  • Max Trades/Day: 5 (top 5 highest-confidence)")
        print(f"  • Trade Types: Long, Short, Options (all enabled)")
        print("\n🚨 READY TO GO LIVE TOMORROW (Oct 28, 2025)")
    else:
        print("\n❌ ACCOUNT NOT READY")
        print("\nIssues found:")
        for issue in issues:
            print(f"  • {issue}")

    print("\n" + "="*80)

except Exception as e:
    print(f"\n❌ CONNECTION FAILED")
    print(f"\nError: {type(e).__name__}")
    print(f"Message: {e}")
    print("\nPossible issues:")
    print("  • API keys are incorrect")
    print("  • API keys are for paper account, not live")
    print("  • Account not approved for trading")
    print("  • Network connection issue")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80 + "\n")
