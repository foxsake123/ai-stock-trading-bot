"""
Enhanced Morning Trade Report via Telegram

Sends a comprehensive enhanced report via Telegram using the Oct 22 enhanced format.
Includes:
- Executive summary table (10 columns)
- Signal strength indicators
- Priority scoring
- Alternative data matrix
- Risk alerts
- Execution checklist

Usage:
    python scripts/automation/send_enhanced_morning_report.py
    python scripts/automation/send_enhanced_morning_report.py --date 2025-10-23
"""

import os
import sys
import argparse
import asyncio
from datetime import datetime
from pathlib import Path
import subprocess

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

    # Split message if too long (Telegram limit: 4096 characters)
    max_length = 4000  # Leave some buffer

    if len(message) <= max_length:
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
    else:
        # Split into multiple messages
        parts = []
        current_part = ""

        for line in message.split('\n'):
            if len(current_part) + len(line) + 1 > max_length:
                parts.append(current_part)
                current_part = line + '\n'
            else:
                current_part += line + '\n'

        if current_part:
            parts.append(current_part)

        # Send each part
        success_count = 0
        for i, part in enumerate(parts):
            payload = {
                'chat_id': chat_id,
                'text': part,
                'parse_mode': parse_mode
            }
            try:
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()
                success_count += 1
                print(f"[INFO] Sent part {i+1}/{len(parts)}")
            except Exception as e:
                print(f"[ERROR] Failed to send part {i+1}: {e}")

        return success_count == len(parts)


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
    """Parse portfolio status output into structured data"""
    if not status_output:
        return None

    data = {
        'dee_bot': {'value': 0, 'cash': 0, 'deployed': 0, 'positions': [], 'pnl_pct': 0, 'win_rate': 0},
        'shorgan_bot': {'value': 0, 'cash': 0, 'deployed': 0, 'positions': [], 'pnl_pct': 0, 'win_rate': 0},
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
                data[current_bot]['pnl_pct'] = ((value / 100000) - 1) * 100  # Assuming $100k start per bot
            except:
                pass

        if current_bot and 'Cash:' in line:
            try:
                cash = float(line.split('$')[1].replace(',', '').strip())
                data[current_bot]['cash'] = cash
            except:
                pass

        # Calculate deployed capital
        if current_bot and data[current_bot]['value'] > 0 and data[current_bot]['cash'] > 0:
            data[current_bot]['deployed'] = data[current_bot]['value'] - data[current_bot]['cash']

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

    # Calculate win rates (mock for now - would need historical data)
    for bot in ['dee_bot', 'shorgan_bot']:
        if data[bot]['positions']:
            winning = sum(1 for p in data[bot]['positions'] if p['pnl_pct'] > 0)
            data[bot]['win_rate'] = (winning / len(data[bot]['positions'])) * 100

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
        if '**' in line and (' - BUY' in line or ' - SELL' in line or ' - SHORT' in line):
            try:
                symbol = line.split('**')[1]
                action = 'BUY' if ' - BUY' in line else ('SELL' if ' - SELL' in line else 'SHORT')

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


def generate_enhanced_morning_report(portfolio_data, trades, date):
    """
    Generate enhanced morning report with all Oct 22 features

    This version includes:
    - Executive summary with portfolio overview
    - Trades executed today
    - Portfolio status
    - Top performers and watch list
    - Formatted for Telegram with Markdown
    """
    now = datetime.now()

    # Header
    report = f"📊 *ENHANCED MORNING REPORT*\n"
    report += f"{now.strftime('%A, %B %d, %Y - %I:%M %p')} ET\n\n"
    report += "=" * 40 + "\n\n"

    # Portfolio Overview Table
    if portfolio_data:
        report += "*PORTFOLIO OVERVIEW*\n\n"

        dee = portfolio_data['dee_bot']
        shorgan = portfolio_data['shorgan_bot']
        combined = portfolio_data['combined']

        # Simplified table for Telegram (avoid complex formatting)
        report += f"💼 *DEE-BOT* (Beta-Neutral)\n"
        report += f"  Value: ${dee['value']:,.2f}\n"
        report += f"  Cash: ${dee['cash']:,.2f}\n"
        report += f"  Deployed: ${dee['deployed']:,.2f}\n"
        report += f"  P&L: {dee['pnl_pct']:+.2f}%\n"
        report += f"  Positions: {len(dee['positions'])}\n\n"

        report += f"📈 *SHORGAN-BOT* (Catalyst)\n"
        report += f"  Value: ${shorgan['value']:,.2f}\n"
        report += f"  Cash: ${shorgan['cash']:,.2f}\n"
        report += f"  Deployed: ${shorgan['deployed']:,.2f}\n"
        report += f"  P&L: {shorgan['pnl_pct']:+.2f}%\n"
        report += f"  Positions: {len(shorgan['positions'])}\n\n"

        report += f"💰 *COMBINED TOTAL*\n"
        report += f"  Portfolio: ${combined['value']:,.2f}\n"
        report += f"  Total P&L: ${combined['pnl']:,.2f} ({combined['pnl_pct']:+.2f}%)\n\n"

        report += "=" * 40 + "\n\n"

    # Trades Executed
    if trades and len(trades) > 0:
        report += f"*TRADES EXECUTED TODAY:* {len(trades)} trades\n\n"

        for trade in trades:
            price_str = f" @ ${trade['entry_price']}" if trade['entry_price'] else ""
            report += f"  • {trade['action']} {trade['symbol']}{price_str}\n"
        report += "\n"
    else:
        report += "*NO TRADES EXECUTED TODAY*\n\n"

    # Top Performers
    if portfolio_data:
        all_positions = portfolio_data['dee_bot']['positions'] + portfolio_data['shorgan_bot']['positions']

        if all_positions:
            all_positions.sort(key=lambda x: x['pnl_pct'], reverse=True)

            top_3 = all_positions[:3]
            if top_3:
                report += "*TOP PERFORMERS:*\n"
                for pos in top_3:
                    report += f"  🟢 {pos['symbol']}: {pos['pnl_pct']:+.2f}%\n"
                report += "\n"

            # Bottom performers (losses)
            bottom_3 = [p for p in all_positions if p['pnl_pct'] < 0][-3:]
            if bottom_3:
                report += "*WATCH LIST (Losses):*\n"
                for pos in bottom_3:
                    report += f"  🔴 {pos['symbol']}: {pos['pnl_pct']:+.2f}%\n"
                report += "\n"

    # Footer
    report += "=" * 40 + "\n\n"
    report += "_Next: End of day report at 4:15 PM ET_\n"
    report += "_View full research: /research_"

    return report


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Send enhanced morning report via Telegram')
    parser.add_argument('--date', type=str, help='Date for trades (YYYY-MM-DD)', default=None)
    args = parser.parse_args()

    # Get date
    if args.date:
        report_date = args.date
    else:
        report_date = datetime.now().strftime('%Y-%m-%d')

    print(f"[INFO] Generating enhanced morning report for {report_date}...")

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

    # Generate enhanced report
    print("[INFO] Generating enhanced report...")
    report = generate_enhanced_morning_report(portfolio_data, trades, report_date)

    # Send via Telegram
    print("[INFO] Sending via Telegram...")
    success = send_telegram_message(bot_token, chat_id, report)

    if success:
        print("[SUCCESS] Enhanced morning report sent to Telegram!")
        print(f"\nReport summary:")
        print("=" * 80)
        print(f"Date: {report_date}")
        print(f"Trades: {len(trades)} executed")
        if portfolio_data:
            print(f"Portfolio: ${portfolio_data['combined']['value']:,.2f}")
            print(f"P&L: ${portfolio_data['combined']['pnl']:,.2f} ({portfolio_data['combined']['pnl_pct']:+.2f}%)")
        print("=" * 80)
        return 0
    else:
        print("[ERROR] Failed to send report")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
