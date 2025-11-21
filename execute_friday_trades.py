#!/usr/bin/env python3
"""
Execute Friday Nov 21 trades for DEE-BOT
Run this at 9:30 AM when market opens
"""

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def execute_dee_bot_trades():
    """Execute DEE-BOT trades for Friday Nov 21"""

    trading_client = TradingClient(
        os.getenv('ALPACA_API_KEY_DEE'),
        os.getenv('ALPACA_SECRET_KEY_DEE'),
        paper=True
    )

    data_client = StockHistoricalDataClient(
        os.getenv('ALPACA_API_KEY_DEE'),
        os.getenv('ALPACA_SECRET_KEY_DEE')
    )

    print("=" * 70)
    print(f"FRIDAY NOV 21 TRADE EXECUTION - DEE-BOT")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # SELL ORDERS (Market orders)
    sell_orders = [
        {'ticker': 'UNH', 'shares': 34, 'rationale': 'Exit -14% loss, regulatory overhang'},
        {'ticker': 'MSFT', 'shares': 17, 'rationale': 'Reduce growth tech at 34x P/E'},
        {'ticker': 'LMT', 'shares': 14, 'rationale': 'Defense execution issues'},
        {'ticker': 'COST', 'shares': 7, 'rationale': 'Trim high-dollar position'},
    ]

    print("\n[SELL ORDERS]")
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

    # BUY ORDERS (Market orders with stop losses to follow)
    buy_orders = [
        {'ticker': 'PFE', 'shares': 160, 'stop_loss': 21.90, 'rationale': 'Deep value pharma, 6.4% yield'},
        {'ticker': 'CSCO', 'shares': 115, 'stop_loss': 67.50, 'rationale': 'AI infrastructure play, 3.1% yield'},
        {'ticker': 'SO', 'shares': 76, 'stop_loss': 79.30, 'rationale': 'Defensive utility, 3.6% yield'},
        {'ticker': 'MDT', 'shares': 68, 'stop_loss': 89.00, 'rationale': 'Medical devices, 3.4% yield'},
    ]

    print("\n[BUY ORDERS]")
    filled_buys = []

    for order in buy_orders:
        try:
            market_order = MarketOrderRequest(
                symbol=order['ticker'],
                qty=order['shares'],
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )

            response = trading_client.submit_order(market_order)
            print(f"  [OK] {order['ticker']}: BUY {order['shares']} shares @ MARKET")
            print(f"    Order ID: {response.id}")
            print(f"    Status: {response.status}")
            print(f"    Stop Loss: ${order['stop_loss']:.2f}")
            print(f"    Rationale: {order['rationale']}")

            filled_buys.append(order)
        except Exception as e:
            print(f"  [ERROR] {order['ticker']}: {e}")

    # Wait a moment for orders to fill, then place stop losses
    if filled_buys:
        print("\n[WAITING 30 SECONDS FOR FILLS...]")
        import time
        time.sleep(30)

        print("\n[PLACING STOP LOSS ORDERS]")
        for order in filled_buys:
            try:
                # Get current position to verify fill
                try:
                    position = trading_client.get_open_position(order['ticker'])
                    print(f"  Position {order['ticker']}: {position.qty} shares @ ${position.avg_entry_price}")
                except:
                    print(f"  [WARNING] {order['ticker']}: No position found, order may not have filled")
                    continue

                # Place GTC stop loss
                stop_order = LimitOrderRequest(
                    symbol=order['ticker'],
                    qty=order['shares'],
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.GTC,
                    limit_price=order['stop_loss']
                )

                response = trading_client.submit_order(stop_order)
                print(f"  [OK] {order['ticker']}: STOP LOSS @ ${order['stop_loss']:.2f} (GTC)")
                print(f"    Order ID: {response.id}")
            except Exception as e:
                print(f"  [ERROR] {order['ticker']}: STOP LOSS ERROR - {e}")

    print("\n" + "=" * 70)
    print("TRADE EXECUTION COMPLETE")
    print(f"SELLS: {len(sell_orders)} orders")
    print(f"BUYS: {len(buy_orders)} orders")
    print(f"STOP LOSSES: {len(filled_buys)} orders")
    print("=" * 70)

if __name__ == "__main__":
    execute_dee_bot_trades()
