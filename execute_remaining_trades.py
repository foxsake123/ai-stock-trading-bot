#!/usr/bin/env python3
"""Execute remaining trades from today's execution plans"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

load_dotenv()

def execute_remaining():
    """Execute trades that haven't been placed yet"""

    # Initialize clients
    dee_client = TradingClient(
        api_key=os.getenv('ALPACA_API_KEY_DEE'),
        secret_key=os.getenv('ALPACA_SECRET_KEY_DEE'),
        paper=True
    )

    shorgan_client = TradingClient(
        api_key=os.getenv('ALPACA_API_KEY_SHORGAN'),
        secret_key=os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
        paper=True
    )

    # Get existing orders
    dee_orders = {o.symbol for o in dee_client.get_orders()}
    shorgan_orders = {o.symbol for o in shorgan_client.get_orders()}

    print("="*70)
    print("EXECUTING REMAINING TRADES")
    print("="*70)

    # Load execution plans
    dee_plan_path = Path("scripts-and-data/data/execution-plans/execution_plan_dee_bot_2025-10-01.json")
    shorgan_plan_path = Path("scripts-and-data/data/execution-plans/execution_plan_shorgan_bot_2025-10-01.json")

    # Execute DEE-BOT trades
    print("\nDEE-BOT:")
    with open(dee_plan_path, 'r') as f:
        dee_plan = json.load(f)

    for trade in dee_plan['approved_trades']:
        if trade['ticker'] in dee_orders:
            print(f"  [SKIP] {trade['ticker']} - already ordered")
            continue

        try:
            order_request = LimitOrderRequest(
                symbol=trade['ticker'],
                qty=trade['shares'],
                side=OrderSide.BUY if trade['action'] == 'buy' else OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
                limit_price=trade['limit_price']
            )
            order = dee_client.submit_order(order_request)
            print(f"  [+] {trade['ticker']}: {trade['shares']} @ ${trade['limit_price']} - Order {order.id}")
        except Exception as e:
            print(f"  [-] {trade['ticker']}: FAILED - {e}")

    # Execute SHORGAN-BOT trades
    print("\nSHORGAN-BOT:")
    with open(shorgan_plan_path, 'r') as f:
        shorgan_plan = json.load(f)

    for trade in shorgan_plan['approved_trades']:
        if trade['ticker'] in shorgan_orders:
            print(f"  [SKIP] {trade['ticker']} - already ordered")
            continue

        try:
            order_request = LimitOrderRequest(
                symbol=trade['ticker'],
                qty=trade['shares'],
                side=OrderSide.BUY if trade['action'] == 'buy' else OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
                limit_price=trade['limit_price']
            )
            order = shorgan_client.submit_order(order_request)
            print(f"  [+] {trade['ticker']}: {trade['shares']} @ ${trade['limit_price']} - Order {order.id}")
        except Exception as e:
            print(f"  [-] {trade['ticker']}: FAILED - {e}")

    print("\n" + "="*70)

if __name__ == "__main__":
    execute_remaining()
