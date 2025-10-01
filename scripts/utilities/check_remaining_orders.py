#!/usr/bin/env python3
"""Check remaining pending orders and evaluate cancellation"""
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

load_dotenv()

# Initialize clients
shorgan_trading = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY_SHORGAN'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    paper=True
)

dee_trading = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY_DEE'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_DEE'),
    paper=True
)

data_client = StockHistoricalDataClient(
    api_key=os.getenv('ALPACA_API_KEY_SHORGAN'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_SHORGAN')
)

print("\n" + "="*70)
print("REMAINING PENDING ORDERS - CANCELLATION EVALUATION")
print("="*70)

# Get pending orders
shorgan_orders = [o for o in shorgan_trading.get_orders() if str(o.submitted_at).startswith('2025-10-01')]
dee_orders = [o for o in dee_trading.get_orders() if str(o.submitted_at).startswith('2025-10-01')]

all_pending = []

for order in shorgan_orders:
    all_pending.append({
        'bot': 'SHORGAN',
        'client': shorgan_trading,
        'order': order,
        'symbol': order.symbol,
        'qty': int(order.qty),
        'limit_price': float(order.limit_price),
        'order_id': order.id
    })

for order in dee_orders:
    all_pending.append({
        'bot': 'DEE',
        'client': dee_trading,
        'order': order,
        'symbol': order.symbol,
        'qty': int(order.qty),
        'limit_price': float(order.limit_price),
        'order_id': order.id
    })

print(f"\nFound {len(all_pending)} pending orders\n")

# Check each order
for pending in all_pending:
    print("="*70)
    print(f"{pending['bot']}-BOT: {pending['symbol']}")
    print("="*70)

    try:
        # Get current price
        quote_request = StockLatestQuoteRequest(symbol_or_symbols=[pending['symbol']])
        quotes = data_client.get_stock_latest_quote(quote_request)
        quote = quotes[pending['symbol']]

        current_price = (quote.ask_price + quote.bid_price) / 2

        print(f"Limit Order: {pending['qty']} shares @ ${pending['limit_price']:.2f}")
        print(f"Current Bid/Ask: ${quote.bid_price:.2f} / ${quote.ask_price:.2f}")
        print(f"Current Mid: ${current_price:.2f}")

        price_diff = current_price - pending['limit_price']
        price_diff_pct = (price_diff / pending['limit_price']) * 100

        print(f"Difference: ${price_diff:.2f} ({price_diff_pct:+.1f}%)")

        cost_at_limit = pending['qty'] * pending['limit_price']
        cost_at_market = pending['qty'] * current_price
        extra_cost = cost_at_market - cost_at_limit

        print(f"Cost at limit: ${cost_at_limit:,.2f}")
        print(f"Cost at market: ${cost_at_market:,.2f}")
        print(f"Extra cost: ${extra_cost:,.2f}")

        # Decision
        print(f"\nEVALUATION:")
        if price_diff_pct >= 100:
            print(f"[X] CANCEL - Price doubled (+{price_diff_pct:.1f}%)")
        elif price_diff_pct >= 50:
            print(f"[!] CANCEL - Price significantly higher (+{price_diff_pct:.1f}%)")
        elif price_diff_pct >= 25:
            print(f"[!] REVIEW - Price moderately higher (+{price_diff_pct:.1f}%)")
        elif price_diff_pct >= 10:
            print(f"[~] KEEP - Price slightly higher (+{price_diff_pct:.1f}%)")
        elif price_diff_pct <= -10:
            print(f"[+] KEEP - Good fill likely (market below limit)")
        else:
            print(f"[+] KEEP - Price near limit ({price_diff_pct:+.1f}%)")

        pending['current_price'] = current_price
        pending['price_diff_pct'] = price_diff_pct

    except Exception as e:
        print(f"Error getting quote: {e}")
        pending['current_price'] = None
        pending['price_diff_pct'] = None

    print()

print("="*70)
print("SUMMARY")
print("="*70)

to_cancel = [p for p in all_pending if p.get('price_diff_pct') and p['price_diff_pct'] >= 25]
to_keep = [p for p in all_pending if not p.get('price_diff_pct') or p['price_diff_pct'] < 25]

print(f"\nOrders to CANCEL: {len(to_cancel)}")
for p in to_cancel:
    print(f"  * {p['bot']:8} {p['symbol']:6} - Price {p['price_diff_pct']:+.1f}% above limit")

print(f"\nOrders to KEEP: {len(to_keep)}")
for p in to_keep:
    if p.get('price_diff_pct') is not None:
        print(f"  * {p['bot']:8} {p['symbol']:6} - Price {p['price_diff_pct']:+.1f}% from limit")
    else:
        print(f"  * {p['bot']:8} {p['symbol']:6} - Could not evaluate")

print("\n" + "="*70 + "\n")

# Store results for next script
import json
with open('pending_orders_evaluation.json', 'w') as f:
    json.dump({
        'to_cancel': [{'bot': p['bot'], 'symbol': p['symbol'], 'order_id': p['order_id']} for p in to_cancel],
        'to_keep': [{'bot': p['bot'], 'symbol': p['symbol'], 'order_id': p['order_id']} for p in to_keep]
    }, f, indent=2)
