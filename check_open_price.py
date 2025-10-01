#!/usr/bin/env python3
"""Check OPEN current price and evaluate market order"""
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide

load_dotenv()

# Initialize clients
shorgan_trading = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY_SHORGAN'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    paper=True
)

data_client = StockHistoricalDataClient(
    api_key=os.getenv('ALPACA_API_KEY_SHORGAN'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_SHORGAN')
)

print("\n" + "="*70)
print("OPEN STOCK ANALYSIS - Market Order Evaluation")
print("="*70)

# Get current price
try:
    quote_request = StockLatestQuoteRequest(symbol_or_symbols=["OPEN"])
    quotes = data_client.get_stock_latest_quote(quote_request)
    quote = quotes["OPEN"]

    current_price = (quote.ask_price + quote.bid_price) / 2
    spread = quote.ask_price - quote.bid_price

    print(f"\nCurrent OPEN Quote:")
    print(f"  Bid: ${quote.bid_price:.2f}")
    print(f"  Ask: ${quote.ask_price:.2f}")
    print(f"  Mid: ${current_price:.2f}")
    print(f"  Spread: ${spread:.2f} ({spread/current_price*100:.2f}%)")

except Exception as e:
    print(f"Error getting quote: {e}")
    current_price = None

# Check existing order
print(f"\nExisting OPEN Order:")
try:
    orders = [o for o in shorgan_trading.get_orders() if o.symbol == "OPEN"]
    if orders:
        order = orders[0]
        print(f"  Order ID: {order.id}")
        print(f"  Type: {order.type}")
        print(f"  Limit Price: ${order.limit_price}")
        print(f"  Quantity: {order.qty}")
        print(f"  Status: {order.status}")
        existing_order_id = order.id
        order_qty = int(order.qty)
    else:
        print(f"  No active OPEN orders found")
        existing_order_id = None
        order_qty = 1250
except Exception as e:
    print(f"  Error: {e}")
    existing_order_id = None
    order_qty = 1250

# Trading Agent Evaluation
if current_price:
    print(f"\n{'='*70}")
    print("TRADING AGENT EVALUATION")
    print(f"{'='*70}")

    original_limit = 4.00
    position_value_at_limit = order_qty * original_limit
    position_value_at_market = order_qty * current_price
    price_difference = current_price - original_limit
    price_increase_pct = (price_difference / original_limit) * 100
    extra_cost = position_value_at_market - position_value_at_limit

    print(f"\nPrice Analysis:")
    print(f"  Original Limit Price: ${original_limit:.2f}")
    print(f"  Current Market Price: ${current_price:.2f}")
    print(f"  Price Increase: ${price_difference:.2f} (+{price_increase_pct:.1f}%)")

    print(f"\nCost Analysis:")
    print(f"  Quantity: {order_qty} shares")
    print(f"  Cost at $4.00 limit: ${position_value_at_limit:,.2f}")
    print(f"  Cost at ${current_price:.2f} market: ${position_value_at_market:,.2f}")
    print(f"  Extra Cost: ${extra_cost:,.2f}")

    print(f"\nOriginal Trade Rationale:")
    print(f"  'High short interest squeeze potential, housing stabilization, 5-10 day hold'")
    print(f"  Stop Loss: $3.40 (-15%)")
    print(f"  Target Price: $6.00 (+50%)")

    # Decision Logic
    print(f"\n{'='*70}")
    print("AGENT DECISION")
    print(f"{'='*70}")

    if current_price >= 8.00:
        # Price has doubled from original target
        decision = "REJECT"
        print(f"[X] REJECT MARKET ORDER")
        print(f"\nReasoning:")
        print(f"  1. Current price (${current_price:.2f}) is {current_price/original_limit:.1f}x the original limit")
        print(f"  2. Price is {current_price/6.00:.1f}x above the original target price ($6.00)")
        print(f"  3. Entry at ${current_price:.2f} provides poor risk/reward:")
        print(f"     - Downside to stop: ${current_price - 3.40:.2f} (-{(current_price - 3.40)/current_price*100:.1f}%)")
        print(f"     - Upside to target: Only ${6.00 - current_price:.2f} if target still valid")
        print(f"  4. Short squeeze may have already occurred")
        print(f"  5. Extra cost of ${extra_cost:,.2f} significantly impacts position sizing")
        print(f"\nRecommendation: CANCEL existing order. Price has moved beyond entry range.")

    elif current_price > 5.00:
        decision = "CONDITIONAL_REJECT"
        print(f"[!] CONDITIONAL REJECT")
        print(f"\nReasoning:")
        print(f"  1. Current price (${current_price:.2f}) is {current_price/original_limit:.1f}x the original limit")
        print(f"  2. Price is already {(current_price - original_limit)/original_limit*100:.1f}% above entry")
        print(f"  3. Risk/reward deteriorating but not completely invalid")
        print(f"  4. Extra cost: ${extra_cost:,.2f} for only ${6.00 - current_price:.2f} upside")
        print(f"\nRecommendation: Only execute if conviction remains high. Consider reducing position size.")

    else:
        decision = "APPROVE"
        print(f"[+] APPROVE MARKET ORDER")
        print(f"\nReasoning:")
        print(f"  1. Price moved {price_increase_pct:.1f}% but still within reasonable entry range")
        print(f"  2. Target of $6.00 still provides {(6.00 - current_price)/current_price*100:.1f}% upside")
        print(f"  3. Stop loss at $3.40 provides {(current_price - 3.40)/current_price*100:.1f}% downside protection")
        print(f"  4. Risk/reward ratio: {(6.00 - current_price)/(current_price - 3.40):.2f}:1")
        print(f"  5. Extra cost of ${extra_cost:,.2f} is {extra_cost/position_value_at_limit*100:.1f}% premium")
        print(f"\nRecommendation: Execute market order to secure entry.")

    print(f"\n{'='*70}\n")

    # Store decision for execution
    print(f"DECISION: {decision}")
    print(f"Existing Order ID: {existing_order_id}")

else:
    print(f"\n[!] Cannot evaluate without current price data")
    decision = "ERROR"

print("="*70 + "\n")
