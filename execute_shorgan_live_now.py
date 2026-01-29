#!/usr/bin/env python3
"""Execute SHORGAN Live trades manually"""

import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import os
import requests
from datetime import datetime

load_dotenv()

# SHORGAN Live API
api = tradeapi.REST(
    os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'),
    os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'),
    'https://api.alpaca.markets',
    api_version='v2'
)

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram(msg):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    requests.post(url, data={'chat_id': CHAT_ID, 'text': msg})

def main():
    print("=" * 60)
    print("SHORGAN LIVE - MANUAL TRADE EXECUTION")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Get account
    acc = api.get_account()
    print(f"\nAccount Status:")
    print(f"  Portfolio Value: ${float(acc.portfolio_value):,.2f}")
    print(f"  Cash: ${float(acc.cash):,.2f}")
    print(f"  Buying Power: ${float(acc.buying_power):,.2f}")

    # Get positions
    positions = api.list_positions()
    print(f"\nCurrent Positions ({len(positions)}):")
    position_symbols = []
    for p in positions:
        position_symbols.append(p.symbol)
        pnl = float(p.unrealized_pl)
        pnl_pct = float(p.unrealized_plpc) * 100
        print(f"  {p.symbol}: {p.qty} shares @ ${float(p.avg_entry_price):.2f} | P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%)")

    # Check prices
    print("\nCurrent Prices:")
    symbols = ['PLUG', 'RIVN', 'SNAP', 'NFLX', 'BEAM', 'SOFI']
    prices = {}
    for sym in symbols:
        try:
            quote = api.get_latest_trade(sym)
            prices[sym] = quote.price
            print(f"  {sym}: ${quote.price:.2f}")
        except Exception as e:
            print(f"  {sym}: Error - {e}")

    # Execute trades
    print("\n" + "=" * 60)
    print("EXECUTING TRADES")
    print("=" * 60)

    executed = []
    failed = []
    skipped = []

    # SELL orders first
    sells = [
        ('BEAM', 1, 'market'),
        ('SOFI', 1, 26.25),
    ]

    for symbol, qty, price in sells:
        if symbol not in position_symbols:
            print(f"\n[SKIP] SELL {qty} {symbol} - No position")
            skipped.append(f"SELL {qty} {symbol} (no position)")
            continue

        try:
            if price == 'market':
                order = api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side='sell',
                    type='market',
                    time_in_force='day'
                )
            else:
                order = api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side='sell',
                    type='limit',
                    limit_price=price,
                    time_in_force='day'
                )
            print(f"\n[OK] SELL {qty} {symbol} @ {'MARKET' if price == 'market' else f'${price}'}")
            print(f"     Order ID: {order.id}")
            executed.append(f"SELL {qty} {symbol}")
        except Exception as e:
            print(f"\n[FAIL] SELL {qty} {symbol} - {e}")
            failed.append(f"SELL {qty} {symbol}: {e}")

    # BUY orders - skip NFLX (bad price), adjust others
    buys = [
        ('PLUG', 85, 2.35, 2.00),
        ('RIVN', 12, 16.50, 14.00),
        ('SNAP', 26, 7.50, 6.50),
        # NFLX skipped - $10 limit is wrong for $850 stock
    ]

    print("\n[SKIP] BUY NFLX - Limit price $10 incorrect (stock is ~$850)")
    skipped.append("BUY NFLX (bad limit price)")

    cash = float(acc.cash)

    for symbol, qty, limit_price, stop_price in buys:
        # Check if we have enough cash
        estimated_cost = qty * limit_price
        if estimated_cost > cash:
            print(f"\n[SKIP] BUY {qty} {symbol} @ ${limit_price} - Insufficient cash (need ${estimated_cost:.2f}, have ${cash:.2f})")
            skipped.append(f"BUY {qty} {symbol} (insufficient cash)")
            continue

        # Adjust limit price if current price is higher
        current = prices.get(symbol, limit_price)
        if current > limit_price * 1.05:  # If current is >5% above limit
            adjusted_limit = round(current * 1.01, 2)  # Set limit 1% above current
            print(f"\n[ADJUST] {symbol}: Current ${current:.2f} > Limit ${limit_price} - Adjusting to ${adjusted_limit}")
            limit_price = adjusted_limit
            estimated_cost = qty * limit_price

        try:
            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='limit',
                limit_price=limit_price,
                time_in_force='day'
            )
            print(f"\n[OK] BUY {qty} {symbol} @ ${limit_price}")
            print(f"     Order ID: {order.id}")
            print(f"     Estimated Cost: ${estimated_cost:.2f}")
            executed.append(f"BUY {qty} {symbol} @ ${limit_price}")
            cash -= estimated_cost  # Track remaining cash

        except Exception as e:
            print(f"\n[FAIL] BUY {qty} {symbol} - {e}")
            failed.append(f"BUY {qty} {symbol}: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Executed: {len(executed)}")
    for e in executed:
        print(f"  [OK] {e}")
    print(f"Skipped: {len(skipped)}")
    for s in skipped:
        print(f"  [--] {s}")
    print(f"Failed: {len(failed)}")
    for f in failed:
        print(f"  [X] {f}")

    # Send to Telegram
    msg = "** SHORGAN LIVE - TRADE EXECUTION **\n"
    msg += f"Time: {datetime.now().strftime('%H:%M ET')}\n\n"

    if executed:
        msg += "EXECUTED:\n"
        for e in executed:
            msg += f"  [OK] {e}\n"

    if skipped:
        msg += "\nSKIPPED:\n"
        for s in skipped:
            msg += f"  [--] {s}\n"

    if failed:
        msg += "\nFAILED:\n"
        for f in failed:
            msg += f"  [X] {f}\n"

    msg += f"\nAccount: ${float(acc.portfolio_value):,.2f}"

    send_telegram(msg)
    print("\n[OK] Summary sent to Telegram")


if __name__ == "__main__":
    main()
