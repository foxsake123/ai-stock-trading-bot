from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, StopLossRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass
import os
from dotenv import load_dotenv

load_dotenv()

client = TradingClient(
    os.getenv('ALPACA_API_KEY_SHORGAN_LIVE'),
    os.getenv('ALPACA_SECRET_KEY_SHORGAN_LIVE'),
    paper=False
)

print('SHORGAN-BOT LIVE - Emergency Fixes')
print('=' * 60)
print()

# Step 1: Cut the 3 worst losers
print('Step 1: Cutting worst losers (ROKU, SOFI, RIVN)')
print('-' * 60)

losers_to_cut = ['ROKU', 'SOFI', 'RIVN']

for symbol in losers_to_cut:
    try:
        # Get position
        position = client.get_open_position(symbol)
        qty = int(float(position.qty))
        current_price = float(position.current_price)
        unrealized_pl = float(position.unrealized_pl)
        unrealized_plpc = float(position.unrealized_plpc) * 100

        # Submit market sell order
        order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )

        order = client.submit_order(order_data)
        print(f'[SELL] {symbol}: {qty} shares @ ${current_price:.2f}')
        print(f'       Loss: ${unrealized_pl:.2f} ({unrealized_plpc:+.2f}%)')
        print(f'       Order: {order.id}')

    except Exception as e:
        print(f'[ERROR] {symbol}: {str(e)}')

print()

# Step 2: Place stop losses on remaining positions
print('Step 2: Placing 15% stop losses on remaining positions')
print('-' * 60)

positions = client.get_all_positions()

# Get current open stop orders to avoid duplicates
try:
    from alpaca.trading.requests import GetOrdersRequest
    from alpaca.trading.enums import QueryOrderStatus
    orders_request = GetOrdersRequest(status=QueryOrderStatus.OPEN)
    open_orders = client.get_orders(filter=orders_request)
    existing_stops = {o.symbol for o in open_orders if o.stop_price}
except:
    existing_stops = set()

for pos in positions:
    symbol = pos.symbol

    # Skip the ones we just sold
    if symbol in losers_to_cut:
        continue

    # Skip if stop already exists
    if symbol in existing_stops:
        print(f'[SKIP] {symbol}: Stop loss already exists')
        continue

    try:
        qty = int(float(pos.qty))
        current_price = float(pos.current_price)
        avg_entry = float(pos.avg_entry_price)

        # Calculate 15% stop loss from average entry price
        stop_price = round(avg_entry * 0.85, 2)

        # If current price is below stop, use current price - 2% instead
        if current_price < stop_price:
            stop_price = round(current_price * 0.98, 2)

        # Submit stop loss order
        from alpaca.trading.requests import StopOrderRequest

        order_data = StopOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC,
            stop_price=stop_price
        )

        order = client.submit_order(order_data)
        pct_below = ((stop_price - current_price) / current_price) * 100
        print(f'[STOP] {symbol}: {qty} shares @ ${stop_price:.2f} ({pct_below:+.1f}% from current)')
        print(f'       Entry: ${avg_entry:.2f}, Current: ${current_price:.2f}')
        print(f'       Order: {order.id}')

    except Exception as e:
        print(f'[ERROR] {symbol}: {str(e)}')

print()
print('=' * 60)
print('Done! Check Alpaca dashboard to verify orders.')
