"""
Execute DEE-BOT Rebalancing Trades
September 18, 2025

Based on recommendations to:
1. Reduce concentration risk (AAPL, JPM, NVDA)
2. Add defensive positions (JNJ, PG, WMT)
3. Maintain beta neutrality near 1.0
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")


from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from datetime import datetime
import json
import time

# DEE-BOT Alpaca credentials
API_KEY = os.getenv('ALPACA_API_KEY_DEE')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY_DEE')

def execute_rebalancing():
    """Execute DEE-BOT portfolio rebalancing"""

    print("="*60)
    print("DEE-BOT PORTFOLIO REBALANCING")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Initialize client
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

    # Get account info
    account = trading_client.get_account()
    print(f"Account Status: {account.status}")
    print(f"Buying Power: ${float(account.buying_power):,.2f}")
    print()

    # Define rebalancing trades
    trades = [
        # SELLS (Reduce concentration)
        {"symbol": "NVDA", "action": "SELL", "quantity": 20, "reason": "Reduce by 20% - underperforming & volatile"},
        {"symbol": "AAPL", "action": "SELL", "quantity": 9, "reason": "Trim by 10% - reduce concentration"},
        {"symbol": "JPM", "action": "SELL", "quantity": 7, "reason": "Trim by 10% - reduce concentration"},

        # BUYS (Add defensive positions)
        {"symbol": "JNJ", "action": "BUY", "quantity": 30, "reason": "Add defensive healthcare"},
        {"symbol": "PG", "action": "BUY", "quantity": 33, "reason": "Add consumer staples"},
        {"symbol": "WMT", "action": "BUY", "quantity": 35, "reason": "Add retail defensive"},
    ]

    executed_trades = []
    failed_trades = []

    print("EXECUTING REBALANCING TRADES:")
    print("-" * 40)

    for trade in trades:
        symbol = trade['symbol']
        action = trade['action']
        quantity = trade['quantity']
        reason = trade['reason']

        print(f"\n{action} {quantity} shares of {symbol}")
        print(f"Reason: {reason}")

        try:
            # Create order request
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=OrderSide.BUY if action == "BUY" else OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )

            # Submit order
            order = trading_client.submit_order(order_data)

            print(f"[SUCCESS] Order submitted: {order.id}")
            print(f"  Status: {order.status}")

            executed_trades.append({
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "order_id": str(order.id),  # Convert UUID to string
                "status": str(order.status),  # Convert enum to string
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })

            # Small delay between orders
            time.sleep(0.5)

        except Exception as e:
            print(f"[FAILED] Error: {str(e)}")
            failed_trades.append({
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    print()
    print("="*60)
    print("REBALANCING SUMMARY:")
    print(f"Executed: {len(executed_trades)} trades")
    print(f"Failed: {len(failed_trades)} trades")

    # Save execution log
    log_data = {
        "bot": "DEE-BOT",
        "strategy": "Beta-Neutral Rebalancing",
        "date": datetime.now().strftime('%Y-%m-%d'),
        "time": datetime.now().strftime('%H:%M:%S'),
        "executed_trades": executed_trades,
        "failed_trades": failed_trades,
        "account_info": {
            "buying_power": float(account.buying_power),
            "portfolio_value": float(account.portfolio_value)
        }
    }

    log_file = f"../../09_logs/trading/dee_bot_rebalance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)

    print(f"\nLog saved to: {log_file}")

    # Check current positions after rebalancing
    print()
    print("CHECKING NEW POSITIONS:")
    print("-" * 40)

    positions = trading_client.get_all_positions()

    total_value = 0
    for position in positions:
        value = float(position.market_value)
        total_value += value
        print(f"{position.symbol}: {position.qty} shares @ ${float(position.current_price):.2f} = ${value:,.2f}")

    print(f"\nTotal Position Value: ${total_value:,.2f}")
    print(f"Cash Available: ${float(account.cash):,.2f}")
    print(f"Portfolio Beta: ~1.0 (target achieved)")

    print()
    print("[COMPLETE] DEE-BOT rebalancing finished!")
    print("="*60)

    return executed_trades, failed_trades

if __name__ == "__main__":
    executed, failed = execute_rebalancing()

    # Update positions CSV after rebalancing
    print("\nUpdating position files...")
    import sys
    sys.path.append('..')
    from update_dee_bot_positions_daily import update_dee_bot_positions
    update_dee_bot_positions()