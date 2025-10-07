#!/usr/bin/env python3
from alpaca.trading.client import TradingClient
import os
from dotenv import load_dotenv

load_dotenv()

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

print('='*80)
print('ALL OPEN ORDERS - DEE-BOT & SHORGAN-BOT')
print('='*80)

print('\nDEE-BOT Orders:')
dee_orders = dee_client.get_orders()
if dee_orders:
    for order in dee_orders:
        symbol = order.symbol[:20] if len(order.symbol) > 20 else order.symbol
        limit_str = f'${order.limit_price}' if order.limit_price else 'market'
        print(f'  {symbol:20s} {order.side.value:6s} {order.qty:6s} @ {limit_str:10s} - {order.status.value}')
else:
    print('  No open orders')

print(f'\nTotal DEE-BOT orders: {len(dee_orders)}')

print('\nSHORGAN-BOT Orders (Stock):')
shorgan_orders = shorgan_client.get_orders()
stock_orders = [o for o in shorgan_orders if len(o.symbol) <= 5]
options_orders = [o for o in shorgan_orders if len(o.symbol) > 5]

if stock_orders:
    for order in stock_orders:
        limit_str = f'${order.limit_price}' if order.limit_price else 'market'
        print(f'  {order.symbol:20s} {order.side.value:6s} {order.qty:6s} @ {limit_str:10s} - {order.status.value}')
else:
    print('  No stock orders')

print('\nSHORGAN-BOT Orders (Options):')
if options_orders:
    for order in options_orders:
        symbol = order.symbol[:20]
        limit_str = f'${order.limit_price}' if order.limit_price else 'market'
        print(f'  {symbol:20s} {order.side.value:6s} {order.qty:6s} @ {limit_str:10s} - {order.status.value}')
else:
    print('  No options orders')

print(f'\nTotal SHORGAN-BOT orders: {len(shorgan_orders)} ({len(stock_orders)} stock, {len(options_orders)} options)')
print(f'Combined total: {len(dee_orders) + len(shorgan_orders)} orders')
