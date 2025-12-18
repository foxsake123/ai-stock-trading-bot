"""
Mirror SHORGAN Paper positions to SHORGAN Live (scaled down)

This script:
1. Gets Paper positions and calculates target Live positions (scaled to 3% of Paper)
2. Identifies what Live needs to buy/sell to match Paper
3. Executes the trades to align portfolios
"""

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from dotenv import load_dotenv
import os
from datetime import datetime

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

def analyze_alignment():
    """Analyze what trades are needed to align Live with Paper"""
    paper, live = get_clients()

    # Get current positions
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
    live_buying_power = float(live_account.buying_power)
    live_cash = float(live_account.cash)

    print("=" * 70)
    print("MIRROR ANALYSIS: SHORGAN Paper -> Live")
    print("=" * 70)
    print(f"Scale Factor: {SCALE_FACTOR:.1%} (${LIVE_CAPITAL:,} / ${PAPER_CAPITAL:,})")
    print(f"Live Buying Power: ${live_buying_power:,.2f}")
    print(f"Live Cash: ${live_cash:,.2f}")
    print()

    # Calculate target positions for Live
    trades_to_execute = []

    print("POSITIONS TO ADD (in Paper but not in Live):")
    print("-" * 70)
    for symbol, paper_data in sorted(paper_positions.items()):
        if paper_data['side'] == 'SHORT':
            print(f"  [SKIP] {symbol}: SHORT position - Live can't short effectively")
            continue

        if paper_data['price'] > MAX_SHARE_PRICE:
            print(f"  [SKIP] {symbol}: ${paper_data['price']:.2f}/share exceeds ${MAX_SHARE_PRICE} limit")
            continue

        # Calculate target value and shares for Live
        target_value = paper_data['value'] * SCALE_FACTOR
        target_value = max(MIN_POSITION_VALUE, min(MAX_POSITION_VALUE, target_value))
        target_shares = int(target_value / paper_data['price'])

        if target_shares < 1:
            print(f"  [SKIP] {symbol}: Would need <1 share at ${paper_data['price']:.2f}")
            continue

        current_shares = int(live_positions.get(symbol, {}).get('qty', 0))
        shares_to_buy = target_shares - current_shares

        if shares_to_buy > 0:
            cost = shares_to_buy * paper_data['price']
            print(f"  [BUY] {symbol}: {shares_to_buy} shares @ ${paper_data['price']:.2f} = ${cost:.2f}")
            trades_to_execute.append({
                'action': 'BUY',
                'symbol': symbol,
                'shares': shares_to_buy,
                'price': paper_data['price']
            })
        elif shares_to_buy < 0:
            print(f"  [TRIM] {symbol}: Sell {abs(shares_to_buy)} shares (have {current_shares}, target {target_shares})")
            trades_to_execute.append({
                'action': 'SELL',
                'symbol': symbol,
                'shares': abs(shares_to_buy),
                'price': paper_data['price']
            })
        elif symbol in live_positions:
            print(f"  [OK] {symbol}: Already aligned ({current_shares} shares)")

    print()
    print("POSITIONS TO REMOVE (in Live but not in Paper):")
    print("-" * 70)
    for symbol, live_data in sorted(live_positions.items()):
        if symbol not in paper_positions:
            shares = int(live_data['qty'])
            value = live_data['value']
            print(f"  [SELL] {symbol}: {shares} shares @ ${live_data['price']:.2f} = ${value:.2f}")
            trades_to_execute.append({
                'action': 'SELL',
                'symbol': symbol,
                'shares': shares,
                'price': live_data['price']
            })

    # Calculate total cost
    total_buy = sum(t['shares'] * t['price'] for t in trades_to_execute if t['action'] == 'BUY')
    total_sell = sum(t['shares'] * t['price'] for t in trades_to_execute if t['action'] == 'SELL')

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Sells: ${total_sell:,.2f} (frees up capital)")
    print(f"Buys: ${total_buy:,.2f} (requires capital)")
    print(f"Net: ${total_sell - total_buy:+,.2f}")
    print(f"Trades to execute: {len(trades_to_execute)}")

    return trades_to_execute

def execute_alignment(trades, dry_run=True):
    """Execute trades to align Live with Paper"""
    if not trades:
        print("\nNo trades to execute - portfolios already aligned!")
        return

    paper, live = get_clients()

    print()
    print("=" * 70)
    if dry_run:
        print("DRY RUN - No trades will be executed")
    else:
        print("EXECUTING TRADES")
    print("=" * 70)

    # Execute sells first to free up capital
    sells = [t for t in trades if t['action'] == 'SELL']
    buys = [t for t in trades if t['action'] == 'BUY']

    executed = []
    failed = []

    for trade in sells + buys:
        symbol = trade['symbol']
        shares = trade['shares']
        price = trade['price']
        action = trade['action']

        if dry_run:
            print(f"  [DRY RUN] {action} {shares} {symbol} @ ${price:.2f}")
            continue

        try:
            side = OrderSide.BUY if action == 'BUY' else OrderSide.SELL
            order = LimitOrderRequest(
                symbol=symbol,
                qty=shares,
                side=side,
                time_in_force=TimeInForce.DAY,
                limit_price=round(price, 2)
            )
            result = live.submit_order(order)
            print(f"  [OK] {action} {shares} {symbol} @ ${price:.2f} - Order {result.id}")
            executed.append(trade)
        except Exception as e:
            print(f"  [FAIL] {action} {shares} {symbol} - {str(e)[:50]}")
            failed.append((trade, str(e)))

    if not dry_run:
        print()
        print(f"Executed: {len(executed)} trades")
        print(f"Failed: {len(failed)} trades")

def main():
    print()
    print("SHORGAN Paper -> Live Mirror Tool")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Analyze what needs to be done
    trades = analyze_alignment()

    if not trades:
        return

    # Ask for confirmation
    print()
    response = input("Execute these trades? (yes/no/dry): ").strip().lower()

    if response == 'yes':
        execute_alignment(trades, dry_run=False)
    elif response == 'dry':
        execute_alignment(trades, dry_run=True)
    else:
        print("Cancelled.")

if __name__ == "__main__":
    main()
