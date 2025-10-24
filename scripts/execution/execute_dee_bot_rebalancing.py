"""
DEE-BOT Rebalancing Trades - October 23, 2025
==============================================
Execute 3 rebalancing orders to fix sector concentration
"""

import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv

load_dotenv()

# Initialize DEE-BOT trading client
dee_client = TradingClient(
    api_key=os.getenv("ALPACA_API_KEY_DEE"),
    secret_key=os.getenv("ALPACA_SECRET_KEY_DEE"),
    paper=True
)

print("="*70)
print("DEE-BOT REBALANCING EXECUTION - October 23, 2025")
print("="*70)
print()

# Define trades
trades = [
    {
        "action": "SELL",
        "symbol": "MRK",
        "qty": 50,  # Reduced from 90 shares (sell ~55%)
        "limit_price": 87.20,
        "rationale": "Reduce healthcare overweight"
    },
    {
        "action": "SELL",
        "symbol": "UNH",
        "qty": 10,  # Reduced from 22 shares (sell ~45%)
        "limit_price": 357.50,
        "rationale": "Reduce healthcare overweight"
    }
]

executed = []
failed = []

for i, trade in enumerate(trades, 1):
    print(f"[{i}/3] {trade['action']} {trade['qty']} {trade['symbol']} @ ${trade['limit_price']}")
    print(f"      Rationale: {trade['rationale']}")

    try:
        # Create order request
        order_request = LimitOrderRequest(
            symbol=trade['symbol'],
            qty=trade['qty'],
            side=OrderSide.BUY if trade['action'] == 'BUY' else OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
            limit_price=trade['limit_price']
        )

        # Submit order
        order = dee_client.submit_order(order_request)

        print(f"      [OK] Order submitted successfully!")
        print(f"      Order ID: {order.id}")
        print(f"      Status: {order.status}")
        print()

        executed.append({
            "symbol": trade['symbol'],
            "order_id": order.id,
            "status": order.status
        })

    except Exception as e:
        print(f"      [FAIL] Order failed: {e}")
        print()

        failed.append({
            "symbol": trade['symbol'],
            "error": str(e)
        })

# Summary
print("="*70)
print("EXECUTION SUMMARY")
print("="*70)
print(f"[OK] Executed: {len(executed)}/{len(trades)}")
print(f"[FAIL] Failed: {len(failed)}/{len(trades)}")
print()

if executed:
    print("Successfully Executed:")
    for order in executed:
        print(f"  - {order['symbol']}: {order['order_id']} ({order['status']})")
    print()

if failed:
    print("Failed Orders:")
    for order in failed:
        print(f"  - {order['symbol']}: {order['error']}")
    print()

print("Expected Net Cash Generated: ~$14,183")
print("Sector Rebalance: Healthcare 41% → ~25-30%")
print("="*70)
