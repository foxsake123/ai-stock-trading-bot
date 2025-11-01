#!/usr/bin/env python3
"""
Automated Stop Loss Monitor
Monitors all positions and executes stop losses automatically

Features:
- Hard stops: DEE-BOT 11%, SHORGAN-BOT 18%
- Trailing stops: After +10% gain
- Executes stop market orders automatically
- Sends Telegram notifications on stop execution

Usage:
  python monitor_stop_losses.py

Should be run every 5 minutes during market hours via Task Scheduler
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, StopLossRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from pathlib import Path

# Load environment
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Stop loss settings
DEE_BOT_HARD_STOP = 0.11  # 11% loss triggers stop
SHORGAN_HARD_STOP = 0.18  # 18% loss triggers stop
TRAILING_STOP_TRIGGER = 0.10  # Start trailing after 10% gain
TRAILING_STOP_DISTANCE = 0.05  # Trail 5% below high

# Status file
STATUS_FILE = Path('data/stop_loss_status.json')

def send_telegram_notification(message):
    """Send notification to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print('[WARNING] Telegram credentials not configured')
        return False

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f'[FAIL] Telegram notification failed: {response.status_code}')
            return False
    except Exception as e:
        print(f'[ERROR] Failed to send Telegram: {e}')
        return False

def load_status():
    """Load stop loss tracking status"""
    if not STATUS_FILE.exists():
        return {}

    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f'[WARNING] Could not load status: {e}')
        return {}

def save_status(status):
    """Save stop loss tracking status"""
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(STATUS_FILE, 'w') as f:
            json.dump(status, f, indent=2)
        return True
    except Exception as e:
        print(f'[ERROR] Could not save status: {e}')
        return False

def execute_stop_loss(client, position, reason, account_name):
    """Execute stop loss for a position"""
    symbol = position.symbol
    qty = int(float(position.qty))
    current_price = float(position.current_price)
    entry_price = float(position.avg_entry_price)
    pnl = float(position.unrealized_pl)
    pnl_pct = float(position.unrealized_plpc) * 100

    print(f'[STOP LOSS] {account_name} - {symbol}')
    print(f'  Entry: ${entry_price:.2f}')
    print(f'  Current: ${current_price:.2f}')
    print(f'  P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)')
    print(f'  Reason: {reason}')

    try:
        # Execute stop market order
        order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )

        order = client.submit_order(order_data)

        print(f'[SUCCESS] Stop loss executed: Order ID {order.id}')

        # Send Telegram notification
        message = f"""🛑 *STOP LOSS EXECUTED*

*Account:* {account_name}
*Symbol:* {symbol}
*Quantity:* {qty} shares

*Entry Price:* ${entry_price:.2f}
*Exit Price:* ${current_price:.2f}
*P&L:* ${pnl:.2f} ({pnl_pct:+.2f}%)

*Reason:* {reason}
*Order ID:* {order.id}
*Time:* {datetime.now().strftime('%I:%M %p %Z')}
"""

        send_telegram_notification(message)

        return True

    except Exception as e:
        print(f'[ERROR] Failed to execute stop loss: {e}')

        # Send error notification
        message = f"""⚠️ *STOP LOSS FAILED*

*Account:* {account_name}
*Symbol:* {symbol}
*Error:* {str(e)[:200]}

*Manual action required!*
"""

        send_telegram_notification(message)

        return False

def check_position_stops(client, position, hard_stop_pct, account_name, status):
    """Check if position needs stop loss execution"""
    symbol = position.symbol
    current_price = float(position.current_price)
    entry_price = float(position.avg_entry_price)
    pnl_pct = float(position.unrealized_plpc)  # Decimal form (e.g., -0.12 for -12%)

    # Track position high for trailing stops
    position_status = status.get(symbol, {})
    high_price = position_status.get('high_price', current_price)

    # Update high if current price is higher
    if current_price > high_price:
        high_price = current_price
        position_status['high_price'] = high_price
        position_status['last_update'] = datetime.now().isoformat()
        status[symbol] = position_status

    # Calculate gain/loss from entry
    gain_from_entry = (current_price - entry_price) / entry_price

    # Check hard stop (loss threshold)
    if pnl_pct <= -hard_stop_pct:
        reason = f'Hard stop triggered: -{abs(pnl_pct)*100:.1f}% loss (limit: -{hard_stop_pct*100}%)'
        execute_stop_loss(client, position, reason, account_name)
        return True

    # Check trailing stop (if in profit)
    if gain_from_entry >= TRAILING_STOP_TRIGGER:
        # Position is up 10%+ from entry, use trailing stop
        drawdown_from_high = (high_price - current_price) / high_price

        if drawdown_from_high >= TRAILING_STOP_DISTANCE:
            reason = f'Trailing stop triggered: Price fell {drawdown_from_high*100:.1f}% from high ${high_price:.2f}'
            execute_stop_loss(client, position, reason, account_name)
            return True

    return False

def monitor_account(api_key, secret_key, hard_stop_pct, account_name, is_paper=True):
    """Monitor an account's positions for stop losses"""
    try:
        client = TradingClient(api_key, secret_key, paper=is_paper)
        account = client.get_account()

        print(f'\n[{account_name}]')
        print(f'Portfolio Value: ${float(account.portfolio_value):,.2f}')

        # Get all positions
        positions = client.get_all_positions()

        if not positions:
            print('No positions to monitor')
            return

        print(f'Monitoring {len(positions)} position(s)...')

        # Load status
        status = load_status()
        account_status = status.get(account_name, {})

        stops_executed = 0

        for position in positions:
            symbol = position.symbol
            pnl_pct = float(position.unrealized_plpc) * 100

            print(f'  {symbol}: P&L {pnl_pct:+.2f}%', end='')

            if check_position_stops(client, position, hard_stop_pct, account_name, account_status):
                stops_executed += 1
                print(' -> STOP EXECUTED')
            else:
                print(' -> OK')

        # Save updated status
        status[account_name] = account_status
        save_status(status)

        if stops_executed > 0:
            print(f'\n[ALERT] {stops_executed} stop loss(es) executed on {account_name}')

    except Exception as e:
        print(f'[ERROR] Failed to monitor {account_name}: {e}')

def main():
    """Main entry point"""
    print('=' * 80)
    print(f'STOP LOSS MONITOR - {datetime.now().strftime("%Y-%m-%d %I:%M %p")}')
    print('=' * 80)

    # Check market hours
    try:
        # Use DEE-BOT client to check market status
        client = TradingClient(
            os.getenv('ALPACA_API_KEY_DEE'),
            os.getenv('ALPACA_SECRET_KEY_DEE'),
            paper=True
        )
        clock = client.get_clock()

        if not clock.is_open:
            print('[INFO] Market is closed - skipping stop loss monitoring')
            return 0

        print(f'[INFO] Market is OPEN (closes at {clock.next_close})')

    except Exception as e:
        print(f'[WARNING] Could not check market status: {e}')
        print('[INFO] Proceeding with monitoring anyway...')

    # Monitor DEE-BOT (Paper)
    dee_api_key = os.getenv('ALPACA_API_KEY_DEE')
    dee_secret = os.getenv('ALPACA_SECRET_KEY_DEE')

    if dee_api_key and dee_secret:
        monitor_account(
            dee_api_key,
            dee_secret,
            DEE_BOT_HARD_STOP,
            'DEE-BOT Paper',
            is_paper=True
        )
    else:
        print('[WARNING] DEE-BOT credentials not found')

    # Monitor SHORGAN-BOT Live
    shorgan_api_key = os.getenv('ALPACA_LIVE_API_KEY_SHORGAN')
    shorgan_secret = os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN')

    if shorgan_api_key and shorgan_secret:
        monitor_account(
            shorgan_api_key.strip(),
            shorgan_secret.strip(),
            SHORGAN_HARD_STOP,
            'SHORGAN-BOT Live',
            is_paper=False
        )
    else:
        print('[WARNING] SHORGAN-BOT Live credentials not found')

    print('\n[COMPLETE] Stop loss monitoring finished')
    return 0

if __name__ == '__main__':
    sys.exit(main())
