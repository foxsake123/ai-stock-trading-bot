"""
Check current positions and execute new trades avoiding wash trade issues
"""

import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import datetime
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Initialize Alpaca
API_KEY = 'PK6FZK4DAQVTD7DYVH78'
API_SECRET = 'OJPdMDllGBYhiWLVpLcRLEFjmof8s6NHKKrKC2C9'
BASE_URL = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

def check_account_status():
    """Check account status and positions"""
    account = api.get_account()

    print("=" * 60)
    print("ACCOUNT STATUS")
    print("=" * 60)
    print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"Buying Power: ${float(account.buying_power):,.2f}")
    print(f"Cash Available: ${float(account.cash):,.2f}")
    print(f"Day Trade Count: {account.daytrade_count}")

    # Get all positions
    positions = api.list_positions()

    print(f"\nActive Positions: {len(positions)}")
    print("=" * 60)

    # Categorize positions
    shorgan_positions = []
    dee_positions = []

    # Read position files to categorize
    try:
        shorgan_df = pd.read_csv('scripts-and-data/daily-csv/shorgan-bot-positions.csv')
        shorgan_symbols = set(shorgan_df['symbol'].tolist())
    except:
        shorgan_symbols = set()

    try:
        dee_df = pd.read_csv('scripts-and-data/daily-csv/dee-bot-positions.csv')
        dee_symbols = set(dee_df['symbol'].tolist())
    except:
        dee_symbols = set()

    total_pnl = 0
    catalyst_positions = ['CBRL', 'INCY', 'RGTI', 'RCAT', 'RIVN', 'MFIC']

    print("\n📊 KEY CATALYST POSITIONS:")
    print("-" * 40)

    for pos in positions:
        if pos.symbol in catalyst_positions:
            pnl = float(pos.unrealized_pl)
            pnl_pct = float(pos.unrealized_plpc) * 100
            total_pnl += pnl

            status = "🔥" if pos.symbol in ['CBRL', 'INCY'] else "📈"

            print(f"{status} {pos.symbol}: {pos.qty} shares @ ${pos.avg_entry_price}")
            print(f"   Current: ${pos.current_price} ({pnl_pct:+.2f}%)")
            print(f"   P&L: ${pnl:+,.2f}")

            if pos.symbol == 'CBRL':
                print("   ⚠️ EARNINGS TONIGHT - Monitor closely!")
            elif pos.symbol == 'INCY':
                print("   ⚠️ FDA DECISION Sept 19 - Binary event!")
            print()

    print(f"\nTotal Unrealized P&L: ${total_pnl:+,.2f}")

    return account, positions

def find_new_trade_opportunities():
    """Find stocks we don't already own that could be traded"""

    # Get current position symbols
    positions = api.list_positions()
    owned_symbols = {pos.symbol for pos in positions}

    # Potential new trades (avoiding wash trade issues)
    new_opportunities = [
        {'symbol': 'AAPL', 'action': 'LONG', 'reason': 'Tech strength'},
        {'symbol': 'NVDA', 'action': 'LONG', 'reason': 'AI momentum'},
        {'symbol': 'AMD', 'action': 'LONG', 'reason': 'Semiconductor recovery'},
        {'symbol': 'SOFI', 'action': 'LONG', 'reason': 'Fintech growth'},
        {'symbol': 'PLTR', 'action': 'LONG', 'reason': 'Government contracts'},
    ]

    print("\n🎯 NEW TRADE OPPORTUNITIES (No wash trade issues):")
    print("-" * 40)

    available_trades = []
    for opp in new_opportunities:
        if opp['symbol'] not in owned_symbols:
            try:
                # Get current price
                snapshot = api.get_snapshot(opp['symbol'])
                price = snapshot.latest_trade.price if snapshot.latest_trade else snapshot.latest_quote.ask_price

                print(f"{opp['symbol']}: ${price:.2f} - {opp['reason']}")
                available_trades.append({
                    'symbol': opp['symbol'],
                    'price': price,
                    'action': opp['action'],
                    'reason': opp['reason']
                })
            except Exception as e:
                print(f"{opp['symbol']}: Unable to get price")

    return available_trades

def execute_safe_trades(available_trades, max_position_pct=0.05):
    """Execute trades that won't trigger wash trade warnings"""

    account = api.get_account()
    portfolio_value = float(account.portfolio_value)

    print("\n💰 EXECUTING SAFE TRADES:")
    print("-" * 40)

    executed = []

    for trade in available_trades[:2]:  # Limit to 2 new positions
        try:
            position_size = portfolio_value * max_position_pct
            shares = int(position_size / trade['price'])

            if shares > 0:
                print(f"Placing order: {trade['symbol']} - {shares} shares @ ${trade['price']:.2f}")

                order = api.submit_order(
                    symbol=trade['symbol'],
                    qty=shares,
                    side='buy',
                    type='limit',
                    limit_price=round(trade['price'] * 1.01, 2),  # 1% above current
                    time_in_force='day'
                )

                print(f"✅ Order placed: {order.id}")
                executed.append(trade['symbol'])

        except Exception as e:
            print(f"❌ Failed to execute {trade['symbol']}: {str(e)}")

    return executed

def main():
    print("=" * 60)
    print("ALPACA TRADING SYSTEM - POSITION CHECK & EXECUTION")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print("=" * 60)

    # Check account status
    account, positions = check_account_status()

    # Find new opportunities
    new_trades = find_new_trade_opportunities()

    # Execute safe trades if we have buying power
    if float(account.buying_power) > 10000 and new_trades:
        response = input("\n\nExecute new trades? (y/n): ")
        if response.lower() == 'y':
            executed = execute_safe_trades(new_trades)
            print(f"\n✅ Executed {len(executed)} trades")
        else:
            print("\n❌ Trade execution cancelled")
    else:
        print("\n⚠️ Insufficient buying power or no opportunities")

    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("1. Monitor CBRL closely - earnings tonight!")
    print("2. Set stop losses for all positions")
    print("3. Prepare exit strategy for CBRL post-earnings")
    print("4. Watch INCY for FDA news Thursday")
    print("=" * 60)

if __name__ == "__main__":
    main()