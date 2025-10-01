#!/usr/bin/env python3
"""
ChatGPT Research Trade Executor
Executes trades from ChatGPT research markdown files
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv

load_dotenv()


def parse_chatgpt_research(file_path):
    """Parse trades from ChatGPT research markdown file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    trades = []

    # Find ORDER BLOCK section
    order_block_match = re.search(r'## 4\. EXACT ORDER BLOCK(.*?)(?=\n## [^#]|$)', content, re.DOTALL)
    if not order_block_match:
        print(f"[!] No ORDER BLOCK found in {file_path}")
        return trades

    order_block = order_block_match.group(1)

    # Extract individual trade blocks
    trade_pattern = r'```\s*(.*?)\s*```'
    trade_blocks = re.findall(trade_pattern, order_block, re.DOTALL)

    for block in trade_blocks:
        trade_data = {}

        for line in block.strip().split('\n'):
            if ':' not in line:
                continue

            key, value = line.split(':', 1)
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()

            if key == 'action':
                trade_data['action'] = value
            elif key == 'ticker':
                trade_data['ticker'] = value
            elif key == 'shares':
                trade_data['shares'] = int(value)
            elif key == 'limit_price' or key == 'price':
                trade_data['limit_price'] = float(value.replace('$', '').replace(',', ''))
            elif key == 'stop_loss':
                if not value.upper().startswith('N/A'):
                    try:
                        trade_data['stop_loss'] = float(value.replace('$', '').replace(',', ''))
                    except ValueError:
                        pass
            elif key == 'target_price':
                if not value.upper().startswith('N/A'):
                    try:
                        trade_data['target_price'] = float(value.replace('$', '').replace(',', ''))
                    except ValueError:
                        pass
            elif key == 'one-line_rationale':
                trade_data['rationale'] = value

        if trade_data.get('ticker'):
            trades.append(trade_data)

    return trades


def execute_trade(client, trade, bot_name):
    """Execute a single trade"""
    print(f"\n[*] {bot_name}: {trade['action'].upper()} {trade['shares']} {trade['ticker']} @ ${trade['limit_price']}")
    print(f"    Rationale: {trade.get('rationale', 'N/A')}")

    try:
        side = OrderSide.BUY if trade['action'] == 'buy' else OrderSide.SELL

        order_request = LimitOrderRequest(
            symbol=trade['ticker'],
            qty=trade['shares'],
            side=side,
            time_in_force=TimeInForce.DAY,
            limit_price=trade['limit_price']
        )

        order = client.submit_order(order_request)

        print(f"[+] Order submitted: {order.id}")
        print(f"    Status: {order.status}")

        return {'success': True, 'order_id': str(order.id), 'trade': trade}

    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return {'success': False, 'error': str(e), 'trade': trade}


def main():
    print("\n" + "="*70)
    print("CHATGPT RESEARCH TRADE EXECUTOR")
    print("="*70)

    date = datetime.now().strftime('%Y-%m-%d')

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

    # Parse DEE-BOT trades
    dee_file = Path(f"data/daily/reports/{date}/chatgpt_research_dee_bot_{date}.md")
    if dee_file.exists():
        print(f"\n[*] Parsing DEE-BOT trades from {dee_file.name}")
        dee_trades = parse_chatgpt_research(dee_file)
        print(f"[+] Found {len(dee_trades)} DEE-BOT trades")

        # Execute DEE-BOT trades
        dee_results = []
        for trade in dee_trades:
            result = execute_trade(dee_client, trade, "DEE-BOT")
            dee_results.append(result)
    else:
        print(f"[!] DEE-BOT file not found: {dee_file}")
        dee_results = []

    # Parse SHORGAN-BOT trades
    shorgan_file = Path(f"data/daily/reports/{date}/chatgpt_research_shorgan_bot_{date}.md")
    if shorgan_file.exists():
        print(f"\n[*] Parsing SHORGAN-BOT trades from {shorgan_file.name}")
        shorgan_trades = parse_chatgpt_research(shorgan_file)
        print(f"[+] Found {len(shorgan_trades)} SHORGAN-BOT trades")

        # Execute SHORGAN-BOT trades
        shorgan_results = []
        for trade in shorgan_trades:
            result = execute_trade(shorgan_client, trade, "SHORGAN-BOT")
            shorgan_results.append(result)
    else:
        print(f"[!] SHORGAN-BOT file not found: {shorgan_file}")
        shorgan_results = []

    # Summary
    print("\n" + "="*70)
    print("EXECUTION SUMMARY")
    print("="*70)

    dee_success = sum(1 for r in dee_results if r['success'])
    shorgan_success = sum(1 for r in shorgan_results if r['success'])

    print(f"DEE-BOT: {dee_success}/{len(dee_results)} executed successfully")
    print(f"SHORGAN-BOT: {shorgan_success}/{len(shorgan_results)} executed successfully")
    print(f"Total: {dee_success + shorgan_success}/{len(dee_results) + len(shorgan_results)} trades executed")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
