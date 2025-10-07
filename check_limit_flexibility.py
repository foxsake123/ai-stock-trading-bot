#!/usr/bin/env python3
"""
Check if limit orders are flexible enough to fill
"""

from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.trading.requests import ReplaceOrderRequest
import os
from dotenv import load_dotenv

load_dotenv()

def check_and_adjust_limits():
    trading_client_shorgan = TradingClient(
        api_key=os.getenv('ALPACA_API_KEY_SHORGAN'),
        secret_key=os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
        paper=True
    )

    trading_client_dee = TradingClient(
        api_key=os.getenv('ALPACA_API_KEY_DEE'),
        secret_key=os.getenv('ALPACA_SECRET_KEY_DEE'),
        paper=True
    )

    data_client = StockHistoricalDataClient(
        api_key=os.getenv('ALPACA_API_KEY_SHORGAN'),
        secret_key=os.getenv('ALPACA_SECRET_KEY_SHORGAN')
    )

    print('='*80)
    print('LIMIT ORDER FLEXIBILITY CHECK')
    print('='*80)

    # Get all open orders from both accounts
    dee_orders = trading_client_dee.get_orders()
    shorgan_orders = trading_client_shorgan.get_orders()

    # Track which client to use for each order
    order_clients = {}
    for order in dee_orders:
        order_clients[order.id] = ('DEE-BOT', trading_client_dee)
    for order in shorgan_orders:
        order_clients[order.id] = ('SHORGAN-BOT', trading_client_shorgan)

    all_orders = list(dee_orders) + list(shorgan_orders)

    # Get current prices for symbols with pending orders
    symbols = list(set([o.symbol for o in all_orders if o.status.value == 'new' and len(o.symbol) <= 5]))

    if not symbols:
        print('\nNo pending stock orders found')
        return

    request = StockLatestQuoteRequest(symbol_or_symbols=symbols)
    quotes = data_client.get_stock_latest_quote(request)

    print('\nStock Orders vs Current Prices:')
    print('-'*80)
    print(f"{'Bot':12s} {'Symbol':8s} {'Side':6s} {'Qty':6s} {'Limit':10s} {'Ask':10s} {'Diff %':10s} {'Status':15s}")
    print('-'*80)

    adjustments = []

    for order in all_orders:
        if order.status.value == 'new' and len(order.symbol) <= 5:
            symbol = order.symbol
            quote = quotes.get(symbol)
            bot_name, client = order_clients[order.id]

            if quote:
                limit = float(order.limit_price) if order.limit_price else 0
                bid = float(quote.bid_price)
                ask = float(quote.ask_price)

                # Determine if limit is too tight
                if order.side.value == 'buy':
                    diff_pct = ((limit - ask) / ask) * 100 if ask > 0 else 0
                    status = 'GOOD' if diff_pct >= -2 else 'OK' if diff_pct >= -5 else 'TOO TIGHT'
                    suggested = ask * 1.03  # 3% above ask for flexibility
                else:
                    diff_pct = ((limit - bid) / bid) * 100 if bid > 0 else 0
                    status = 'GOOD' if diff_pct <= 2 else 'OK' if diff_pct <= 5 else 'TOO TIGHT'
                    suggested = bid * 0.97  # 3% below bid for flexibility

                print(f"{bot_name:12s} {symbol:8s} {order.side.value:6s} {order.qty:6s} ${limit:8.2f} ${ask:8.2f} {diff_pct:8.1f}% {status:15s}")

                if status == 'TOO TIGHT':
                    adjustments.append({
                        'order_id': order.id,
                        'bot': bot_name,
                        'client': client,
                        'symbol': symbol,
                        'side': order.side.value,
                        'qty': order.qty,
                        'current_limit': limit,
                        'suggested_limit': suggested,
                        'current_market': ask if order.side.value == 'buy' else bid
                    })

    if adjustments:
        print('\n' + '='*80)
        print('RECOMMENDED ADJUSTMENTS')
        print('='*80)
        for adj in adjustments:
            print(f"{adj['bot']:12s} {adj['symbol']:8s} {adj['side']:6s} - Current: ${adj['current_limit']:.2f}, Market: ${adj['current_market']:.2f}, Suggested: ${adj['suggested_limit']:.2f}")

        print('\nUpdating orders to more flexible limits...')

        for adj in adjustments:
            try:
                # Replace order with new limit price
                replace_request = ReplaceOrderRequest(
                    qty=int(adj['qty']),
                    limit_price=adj['suggested_limit']
                )
                result = adj['client'].replace_order_by_id(adj['order_id'], replace_request)
                print(f"[+] Updated {adj['symbol']} limit to ${adj['suggested_limit']:.2f}")
            except Exception as e:
                print(f"[-] Failed to update {adj['symbol']}: {e}")

        print('\n[SUCCESS] Orders updated for better fill probability')
    else:
        print('\n[GOOD] All limit orders are within reasonable range of current prices')

if __name__ == "__main__":
    check_and_adjust_limits()
