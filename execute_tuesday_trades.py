"""
Tuesday September 23, 2025 Trade Execution Script
Executes the weekly trade plan for both DEE-BOT and SHORGAN-BOT
Note: Monday's trades should have already been executed
"""

import os
import sys
import time
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Bot configurations
BOTS = {
    'DEE': {
        'api_key': 'PK6FZK4DAQVTD7DYVH78',
        'secret_key': 'OvdGPcvzYHQmJnGhLVxsvrobMcrpYLmqGKYesmcS',
        'name': 'DEE-BOT'
    },
    'SHORGAN': {
        'api_key': 'PKJRLSB2MFEJUSK6UK2E',
        'secret_key': 'eTSRAfs9AobCJyqGkycrHFLdD2sAOp8DpqOGVvvr',
        'name': 'SHORGAN-BOT'
    }
}

# Tuesday's trade plan - positioning for Wednesday BBAI earnings
TUESDAY_TRADES = {
    'DEE': [
        # DEE-BOT should maintain defensive positioning
        # Monday's rebalancing should have already been done
    ],
    'SHORGAN': [
        # Monitor BBAI for entry ahead of Wednesday earnings
        # Consider adding if it dips below $2.00
        {'action': 'BUY', 'symbol': 'BBAI', 'qty': 500, 'order_type': 'LIMIT', 'limit_price': 1.95, 'reason': 'Wednesday earnings catalyst', 'stop_loss': 1.75},
        # If Monday's SOUN order didn't fill, try again
        {'action': 'BUY', 'symbol': 'SOUN', 'qty': 1000, 'order_type': 'LIMIT', 'limit_price': 5.45, 'reason': 'AI voice catalyst (retry)', 'stop_loss': 4.85},
    ]
}

def get_current_position(client, symbol):
    """Get current position for a symbol"""
    try:
        positions = client.get_all_positions()
        for pos in positions:
            if pos.symbol == symbol:
                return int(pos.qty)
        return 0
    except Exception as e:
        print(f"Error getting position for {symbol}: {e}")
        return 0

def execute_trade(client, trade, bot_name, dry_run=False):
    """Execute a single trade"""
    symbol = trade['symbol']
    action = trade['action']
    qty = trade['qty']
    order_type = trade['order_type']
    reason = trade.get('reason', '')

    print(f"\n[{bot_name}] {action} {qty} shares of {symbol}")
    print(f"  Reason: {reason}")

    if dry_run:
        print(f"  DRY RUN: Would {action.lower()} {qty} {symbol} via {order_type}")
        return None

    try:
        if order_type == 'MARKET':
            # Market order
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if action == 'BUY' else OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )
            order = client.submit_order(order_data)
            print(f"  ✓ Market order submitted: {order.id}")

        elif order_type == 'LIMIT':
            # Limit order
            limit_price = trade.get('limit_price')
            if not limit_price:
                print(f"  ✗ ERROR: No limit price specified for {symbol}")
                return None

            order_data = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if action == 'BUY' else OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
                limit_price=limit_price
            )
            order = client.submit_order(order_data)
            print(f"  ✓ Limit order submitted at ${limit_price}: {order.id}")

        # Set stop loss if specified
        if action == 'BUY' and 'stop_loss' in trade:
            time.sleep(2)  # Wait for fill
            stop_price = trade['stop_loss']
            stop_data = StopOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.GTC,
                stop_price=stop_price
            )
            stop_order = client.submit_order(stop_data)
            print(f"  ✓ Stop loss set at ${stop_price}: {stop_order.id}")

        return order

    except Exception as e:
        print(f"  ✗ ERROR executing trade: {e}")
        return None

def check_account_status(client, bot_name):
    """Check account status before trading"""
    try:
        account = client.get_account()
        print(f"\n{bot_name} Account Status:")
        print(f"  Cash: ${float(account.cash):,.2f}")
        print(f"  Buying Power: ${float(account.buying_power):,.2f}")
        print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"  Pattern Day Trader: {account.pattern_day_trader}")
        return True
    except Exception as e:
        print(f"Error checking account: {e}")
        return False

def main():
    print("=" * 60)
    print("TUESDAY TRADE EXECUTION SCRIPT")
    print(f"Date: {datetime.now().strftime('%B %d, %Y %I:%M %p ET')}")
    print("=" * 60)

    # Ask for confirmation
    print("\nThis script will execute the following trades:")
    print("\nDEE-BOT:")
    trades_dee = TUESDAY_TRADES.get('DEE', [])
    if trades_dee:
        for trade in trades_dee:
            print(f"  - {trade['action']} {trade['qty']} {trade['symbol']}: {trade['reason']}")
    else:
        print("  - No trades scheduled (maintaining defensive positions)")

    print("\nSHORGAN-BOT:")
    for trade in TUESDAY_TRADES['SHORGAN']:
        print(f"  - {trade['action']} {trade['qty']} {trade['symbol']}: {trade['reason']}")

    # Dry run option
    response = input("\nChoose mode:\n1. DRY RUN (test only)\n2. EXECUTE TRADES (real)\n3. CANCEL\n\nEnter choice (1/2/3): ")

    if response == '3':
        print("Execution cancelled.")
        return

    dry_run = (response == '1')
    if dry_run:
        print("\n*** DRY RUN MODE - NO TRADES WILL BE EXECUTED ***")
    else:
        confirm = input("\n⚠️  REAL TRADING MODE - Are you sure? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Execution cancelled.")
            return

    # Execute trades for each bot
    for bot_key, bot_config in BOTS.items():
        print(f"\n{'='*40}")
        print(f"Processing {bot_config['name']}")
        print('='*40)

        # Create client
        client = TradingClient(
            bot_config['api_key'],
            bot_config['secret_key'],
            paper=True
        )

        # Check account status
        if not check_account_status(client, bot_config['name']):
            print(f"Skipping {bot_config['name']} due to account error")
            continue

        # Execute trades
        trades = TUESDAY_TRADES.get(bot_key, [])
        if not trades:
            print(f"No trades scheduled for {bot_config['name']}")
            continue

        for trade in trades:
            # Check if we need to verify position first
            if trade['action'] == 'SELL':
                current_qty = get_current_position(client, trade['symbol'])
                if current_qty < trade['qty']:
                    print(f"\n⚠️  Warning: Only {current_qty} shares of {trade['symbol']} available (wanted {trade['qty']})")
                    if current_qty > 0:
                        trade['qty'] = current_qty
                        print(f"  Adjusting to sell {current_qty} shares")
                    else:
                        print(f"  Skipping trade - no position")
                        continue

            execute_trade(client, trade, bot_config['name'], dry_run)

            if not dry_run:
                time.sleep(2)  # Pause between trades

    print("\n" + "="*60)
    print("EXECUTION COMPLETE")
    print("="*60)

    if not dry_run:
        print("\nNext steps:")
        print("1. Verify all orders in Alpaca dashboard")
        print("2. Check fill status")
        print("3. Confirm stop losses are set")
        print("4. Update position tracking CSV files")
        print("5. Monitor BBAI for Wednesday earnings setup")

if __name__ == "__main__":
    # Check if market is open (basic check)
    now = datetime.now()
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        print("⚠️  WARNING: Market is closed (weekend)")
        response = input("Continue anyway? (yes/no): ")
        if response.lower() != 'yes':
            sys.exit()

    main()