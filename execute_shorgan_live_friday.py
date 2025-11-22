#!/usr/bin/env python3
"""
Execute SHORGAN-BOT Live trades for Friday Nov 21
Based on research ORDER BLOCK section
"""

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopLimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def execute_shorgan_live_trades():
    """Execute SHORGAN-BOT Live trades for Friday Nov 21"""

    trading_client = TradingClient(
        os.getenv('ALPACA_API_KEY_SHORGAN_LIVE'),
        os.getenv('ALPACA_SECRET_KEY_SHORGAN_LIVE'),
        paper=False  # REAL MONEY!
    )

    data_client = StockHistoricalDataClient(
        os.getenv('ALPACA_API_KEY_SHORGAN_LIVE'),
        os.getenv('ALPACA_SECRET_KEY_SHORGAN_LIVE')
    )

    print("=" * 70)
    print(f"FRIDAY NOV 21 TRADE EXECUTION - SHORGAN-BOT LIVE")
    print(f"[WARNING] REAL MONEY ACCOUNT - \$3K LIVE TRADING")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Check current account status
    account = trading_client.get_account()
    print(f"\nAccount Status:")
    print(f"  Portfolio Value: \${float(account.portfolio_value):,.2f}")
    print(f"  Cash: \${float(account.cash):,.2f}")
    print(f"  Buying Power: \${float(account.buying_power):,.2f}")
    print()

    # SELL ORDERS (Exit position)
    sell_orders = [
        {'ticker': 'LCID', 'shares': 10, 'rationale': 'Cut biggest loser in half to free capital'},
    ]

    print("[SELL ORDERS]")
    for order in sell_orders:
        try:
            market_order = MarketOrderRequest(
                symbol=order['ticker'],
                qty=order['shares'],
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )

            response = trading_client.submit_order(market_order)
            print(f"  [OK] {order['ticker']}: SELL {order['shares']} shares @ MARKET")
            print(f"    Order ID: {response.id}")
            print(f"    Status: {response.status}")
            print(f"    Rationale: {order['rationale']}")
        except Exception as e:
            print(f"  [ERROR] {order['ticker']}: {e}")

    # BUY ORDERS (Stock positions)
    buy_orders = [
        {'ticker': 'MARA', 'shares': 20, 'limit': 10.30, 'stop_loss': 8.75, 'rationale': 'Bitcoin \$100K catalyst'},
        {'ticker': 'SNAP', 'shares': 30, 'limit': 7.80, 'stop_loss': 6.65, 'rationale': 'Oversold with AR glasses catalyst'},
        {'ticker': 'PINS', 'shares': 10, 'limit': 24.90, 'stop_loss': 21.25, 'rationale': 'Holiday shopping catalyst'},
        {'ticker': 'PATH', 'shares': 18, 'limit': 12.80, 'stop_loss': 10.90, 'rationale': 'Enterprise AI automation'},
    ]

    print("\n[BUY ORDERS - LIMIT ORDERS]")
    filled_buys = []

    for order in buy_orders:
        try:
            # Place limit order at specified price
            limit_order = LimitOrderRequest(
                symbol=order['ticker'],
                qty=order['shares'],
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
                limit_price=order['limit']
            )

            response = trading_client.submit_order(limit_order)
            print(f"  [OK] {order['ticker']}: BUY {order['shares']} shares @ \${order['limit']:.2f} LIMIT")
            print(f"    Order ID: {response.id}")
            print(f"    Status: {response.status}")
            print(f"    Stop Loss: \${order['stop_loss']:.2f}")
            print(f"    Rationale: {order['rationale']}")

            filled_buys.append(order)
        except Exception as e:
            print(f"  [ERROR] {order['ticker']}: {e}")

    print("\n[NOTE] Stop losses will need to be placed manually after limit orders fill")
    print("[NOTE] Options orders (MARA calls) not executed - requires options approval")

    print("\n" + "=" * 70)
    print("TRADE EXECUTION COMPLETE")
    print(f"SELLS: {len(sell_orders)} orders")
    print(f"BUYS (LIMIT): {len(buy_orders)} orders")
    print(f"STOP LOSSES: Place manually after fills")
    print("=" * 70)

if __name__ == "__main__":
    print("\n[WARNING] This script trades REAL MONEY on SHORGAN-BOT Live account")
    print("[WARNING] Current balance: ~\$2,826")
    confirm = input("\nType 'YES' to confirm execution: ")

    if confirm == 'YES':
        execute_shorgan_live_trades()
    else:
        print("\n[CANCELLED] Execution aborted")
