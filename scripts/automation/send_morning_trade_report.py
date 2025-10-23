"""
Morning Trade Report via Telegram

Sends a comprehensive report via Telegram after morning trades are executed.
Includes:
- Trades executed this morning
- Current portfolio status
- P&L summary
- Top performers and losers

Usage:
    python scripts/automation/send_morning_trade_report.py
    python scripts/automation/send_morning_trade_report.py --date 2025-10-23
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()


def get_telegram_config():
    """Get Telegram configuration from environment"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")

    return bot_token, chat_id


def send_telegram_message(bot_token, chat_id, message, parse_mode='Markdown'):
    """Send message via Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': parse_mode
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")
        return False


def get_portfolio_status():
    """Get current portfolio status"""
    try:
        result = subprocess.run(
            ['python', 'scripts/performance/get_portfolio_status.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except Exception as e:
        print(f"[ERROR] Failed to get portfolio status: {e}")
        return None


def parse_portfolio_status(status_output):
    """Parse portfolio status output"""
    if not status_output:
        return None

    data = {
        'dee_bot': {'value': 0, 'cash': 0, 'positions': []},
        'shorgan_bot': {'value': 0, 'cash': 0, 'positions': []},
        'combined': {'value': 0, 'pnl': 0, 'pnl_pct': 0}
    }

    lines = status_output.split('\n')
    current_bot = None
    in_positions = False

    for line in lines:
        line = line.strip()

        # Parse DEE-BOT status
        if 'DEE-BOT ACCOUNT STATUS' in line:
            current_bot = 'dee_bot'
            in_positions = False
        elif 'SHORGAN-BOT ACCOUNT STATUS' in line:
            current_bot = 'shorgan_bot'
            in_positions = False
        elif 'SUMMARY' in line:
            current_bot = None
            in_positions = False

        # Parse portfolio values
        if current_bot and 'Portfolio Value:' in line:
            try:
                value = float(line.split('$')[1].replace(',', '').strip())
                data[current_bot]['value'] = value
            except:
                pass

        if current_bot and 'Cash:' in line:
            try:
                cash = float(line.split('$')[1].replace(',', '').strip())
                data[current_bot]['cash'] = cash
            except:
                pass

        # Parse positions
        if 'LONG POSITIONS:' in line or 'SHORT POSITIONS:' in line:
            in_positions = True

        if in_positions and current_bot and line and not line.startswith('---'):
            parts = line.split()
            if len(parts) >= 6 and parts[0] not in ['Symbol', 'LONG', 'SHORT', 'DEE-BOT:', 'SHORGAN-BOT:']:
                try:
                    symbol = parts[0]
                    qty = int(parts[1])
                    pnl_pct = parts[-1].replace('%', '')
                    if pnl_pct:
                        data[current_bot]['positions'].append({
                            'symbol': symbol,
                            'qty': qty,
                            'pnl_pct': float(pnl_pct)
                        })
                except:
                    pass

        # Parse combined summary
        if 'Total Profit/Loss:' in line:
            try:
                # Format: Total Profit/Loss: $ 6,098.21 (+3.05%)
                parts = line.split('$')[1].split('(')
                data['combined']['pnl'] = float(parts[0].replace(',', '').strip())
                data['combined']['pnl_pct'] = float(parts[1].replace('%)', '').replace('+', ''))
            except:
                pass

        if 'Combined Value:' in line:
            try:
                value = float(line.split('$')[1].replace(',', '').strip())
                data['combined']['value'] = value
            except:
                pass

    return data


def read_todays_trades(date=None):
    """Read today's trades file"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    trades_file = Path(f"docs/TODAYS_TRADES_{date}.md")

    if not trades_file.exists():
        return None

    try:
        with open(trades_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read trades file: {e}")
        return None


def parse_trades_from_file(trades_content):
    """Parse trades from TODAYS_TRADES file"""
    if not trades_content:
        return []

    trades = []
    lines = trades_content.split('\n')

    for i, line in enumerate(lines):
        # Look for trade entries like "**AAPL** - BUY"
        if '**' in line and (' - BUY' in line or ' - SELL' in line or ' - SHORT' in line):
            try:
                # Extract symbol and action
                symbol = line.split('**')[1]
                action = 'BUY' if ' - BUY' in line else ('SELL' if ' - SELL' in line else 'SHORT')

                # Look for entry price in next few lines
                entry_price = None
                for j in range(i+1, min(i+5, len(lines))):
                    if 'Entry:' in lines[j] or 'Price:' in lines[j]:
                        try:
                            entry_price = lines[j].split('$')[1].split()[0]
                        except:
                            pass
                        break

                trades.append({
                    'symbol': symbol,
                    'action': action,
                    'entry_price': entry_price
                })
            except:
                pass

    return trades


def generate_morning_report(portfolio_data, trades, date):
    """Generate morning trade report message"""
    now = datetime.now()

    # Header
    report = f"📊 *MORNING TRADE REPORT*\n"
    report += f"{now.strftime('%A, %B %d, %Y - %I:%M %p')} ET\n\n"

    # Trades executed
    if trades and len(trades) > 0:
        report += f"*TRADES EXECUTED TODAY:* {len(trades)} trades\n\n"

        dee_trades = []
        shorgan_trades = []

        for trade in trades:
            # Simplified - you may want to categorize better
            if 'DEE' in str(trade):
                dee_trades.append(trade)
            else:
                shorgan_trades.append(trade)

        if dee_trades:
            report += f"*DEE-BOT Trades:*\n"
            for trade in dee_trades:
                price_str = f" @ ${trade['entry_price']}" if trade['entry_price'] else ""
                report += f"  • {trade['action']} {trade['symbol']}{price_str}\n"
            report += "\n"

        if shorgan_trades:
            report += f"*SHORGAN-BOT Trades:*\n"
            for trade in shorgan_trades:
                price_str = f" @ ${trade['entry_price']}" if trade['entry_price'] else ""
                report += f"  • {trade['action']} {trade['symbol']}{price_str}\n"
            report += "\n"
    else:
        report += f"*NO TRADES EXECUTED TODAY*\n\n"

    # Current portfolio status
    if portfolio_data:
        report += f"*CURRENT PORTFOLIO STATUS*\n\n"

        # DEE-BOT
        dee = portfolio_data['dee_bot']
        report += f"*DEE-BOT (Beta-Neutral)*\n"
        report += f"Portfolio: ${dee['value']:,.2f}\n"
        report += f"Cash: ${dee['cash']:,.2f}\n"
        report += f"Positions: {len(dee['positions'])}\n\n"

        # SHORGAN-BOT
        shorgan = portfolio_data['shorgan_bot']
        report += f"*SHORGAN-BOT (Catalyst)*\n"
        report += f"Portfolio: ${shorgan['value']:,.2f}\n"
        report += f"Cash: ${shorgan['cash']:,.2f}\n"
        report += f"Positions: {len(shorgan['positions'])}\n\n"

        # Combined
        combined = portfolio_data['combined']
        report += f"*COMBINED TOTAL*\n"
        report += f"Portfolio: ${combined['value']:,.2f}\n"
        report += f"Total P/L: ${combined['pnl']:,.2f} ({combined['pnl_pct']:+.2f}%)\n\n"

        # Top performers
        all_positions = dee['positions'] + shorgan['positions']
        if all_positions:
            all_positions.sort(key=lambda x: x['pnl_pct'], reverse=True)

            top_3 = all_positions[:3]
            if top_3:
                report += f"*TOP PERFORMERS:*\n"
                for pos in top_3:
                    report += f"  🟢 {pos['symbol']}: {pos['pnl_pct']:+.2f}%\n"
                report += "\n"

            # Bottom performers (losses)
            bottom_3 = [p for p in all_positions if p['pnl_pct'] < 0][-3:]
            if bottom_3:
                report += f"*WATCH LIST (Losses):*\n"
                for pos in bottom_3:
                    report += f"  🔴 {pos['symbol']}: {pos['pnl_pct']:+.2f}%\n"
                report += "\n"

    # Footer
    report += f"_Next report: End of day (4:15 PM ET)_"

    return report


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Send morning trade report via Telegram')
    parser.add_argument('--date', type=str, help='Date for trades (YYYY-MM-DD)', default=None)
    args = parser.parse_args()

    # Get date
    if args.date:
        report_date = args.date
    else:
        report_date = datetime.now().strftime('%Y-%m-%d')

    print(f"[INFO] Generating morning trade report for {report_date}...")

    # Get Telegram config
    try:
        bot_token, chat_id = get_telegram_config()
    except ValueError as e:
        print(f"[ERROR] {e}")
        print("[INFO] Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env file")
        return 1

    # Get portfolio status
    print("[INFO] Fetching portfolio status...")
    portfolio_output = get_portfolio_status()
    portfolio_data = parse_portfolio_status(portfolio_output)

    if not portfolio_data:
        print("[WARNING] Could not parse portfolio data")

    # Read today's trades
    print("[INFO] Reading today's trades...")
    trades_content = read_todays_trades(report_date)
    trades = parse_trades_from_file(trades_content) if trades_content else []

    if trades:
        print(f"[INFO] Found {len(trades)} trades")
    else:
        print("[INFO] No trades found for today")

    # Generate report
    print("[INFO] Generating report...")
    report = generate_morning_report(portfolio_data, trades, report_date)

    # Send via Telegram
    print("[INFO] Sending via Telegram...")
    success = send_telegram_message(bot_token, chat_id, report)

    if success:
        print("[SUCCESS] Morning trade report sent to Telegram!")
        print(f"\nReport preview:")
        print("=" * 80)
        print(report.replace('*', '').replace('_', ''))
        print("=" * 80)
        return 0
    else:
        print("[ERROR] Failed to send report")
        return 1


if __name__ == "__main__":
    sys.exit(main())
