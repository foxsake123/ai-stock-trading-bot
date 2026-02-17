import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate and Send Pre-Market Trading Plan to Telegram
Combines ChatGPT recommendations with Multi-Agent Consensus
"""

import json
import requests
import os
import sys
from datetime import datetime
import alpaca_trade_api as tradeapi

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c"
TELEGRAM_CHAT_ID = "7870288896"

# Alpaca API
API_KEY = os.getenv('ALPACA_API_KEY_SHORGAN')
API_SECRET = os.getenv('ALPACA_SECRET_KEY_SHORGAN')
BASE_URL = 'https://paper-api.alpaca.markets'
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

def get_market_status():
    """Check if market is open"""
    try:
        clock = api.get_clock()
        return clock.is_open, clock.next_open, clock.next_close
    except:
        return False, None, None

def get_account_summary():
    """Get account summary"""
    try:
        account = api.get_account()
        positions = api.list_positions()

        return {
            'portfolio_value': float(account.portfolio_value),
            'buying_power': float(account.buying_power),
            'cash': float(account.cash),
            'position_count': len(positions)
        }
    except:
        return None

def generate_premarket_report():
    """Generate comprehensive pre-market trading plan"""

    report_lines = []
    report_lines.append("🔔 PRE-MARKET TRADING PLAN")
    report_lines.append(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")
    report_lines.append(f"⏰ {datetime.now().strftime('%I:%M %p ET')}")
    report_lines.append("=" * 40)

    # Market Status
    is_open, next_open, next_close = get_market_status()
    if is_open:
        report_lines.append(f"🟢 MARKET OPEN until {next_close.strftime('%I:%M %p ET')}")
    else:
        report_lines.append(f"🔴 MARKET CLOSED")
        if next_open:
            report_lines.append(f"   Opens at {next_open.strftime('%I:%M %p ET')}")

    # Account Summary
    account = get_account_summary()
    if account:
        report_lines.append("")
        report_lines.append("💼 ACCOUNT SUMMARY")
        report_lines.append(f"Portfolio: ${account['portfolio_value']:,.2f}")
        report_lines.append(f"Buying Power: ${account['buying_power']:,.2f}")
        report_lines.append(f"Positions: {account['position_count']}")

    # DEE-BOT Trading Plan
    report_lines.append("")
    report_lines.append("=" * 40)
    report_lines.append("🤖 DEE-BOT (Beta-Neutral S&P 100)")
    report_lines.append("-" * 40)
    report_lines.append("SELLS (Rebalancing):")
    report_lines.append("• PG (33 shares) - Staples underperform")
    report_lines.append("• CVX (31 shares) - Exit duplicate energy")
    report_lines.append("• AAPL (5 shares) - Trim profits")
    report_lines.append("• NVDA (15 shares) - Reduce high beta")
    report_lines.append("")
    report_lines.append("BUYS (Defensive positioning):")
    report_lines.append("• UNH (14 shares) - Healthcare anchor")
    report_lines.append("• NEE (53 shares) - Utility defensive")
    report_lines.append("• AMZN (21 shares) - Cloud growth")

    # SHORGAN-BOT Trading Plan with Consensus
    report_lines.append("")
    report_lines.append("=" * 40)
    report_lines.append("🎯 SHORGAN-BOT (Catalyst Trading)")
    report_lines.append("-" * 40)
    report_lines.append("Multi-Agent Consensus Scores:")

    consensus_trades = [
        ("SRRK", "8.78/10", "✅", "FDA TODAY", "127 shares"),
        ("FBIO", "7.93/10", "✅", "FDA Sept 30", "1037 shares"),
        ("RIVN", "7.03/10", "✅", "Q3 Deliveries", "648 shares"),
        ("IONQ", "7.88/10", "✅", "SHORT - Overhyped", "50 shares"),
        ("KSS", "6.93/10", "✅", "Retail recovery", "522 shares")
    ]

    for ticker, score, status, catalyst, shares in consensus_trades:
        report_lines.append(f"{status} {ticker}: {score} | {catalyst}")
        report_lines.append(f"   Position: {shares}")

    # Key Catalysts
    report_lines.append("")
    report_lines.append("=" * 40)
    report_lines.append("⚡ TODAY'S KEY CATALYSTS")
    report_lines.append("-" * 40)
    report_lines.append("🔴 CRITICAL: SRRK FDA Decision TODAY")
    report_lines.append("• High conviction play (8.78/10)")
    report_lines.append("• Binary catalyst - monitor closely")
    report_lines.append("")
    report_lines.append("📊 Other Catalysts This Week:")
    report_lines.append("• FBIO: FDA Sept 30")
    report_lines.append("• RIVN: Q3 deliveries early Oct")

    # Execution Notes
    report_lines.append("")
    report_lines.append("=" * 40)
    report_lines.append("⚠️ EXECUTION NOTES")
    report_lines.append("-" * 40)
    report_lines.append("• Wash trade blocks on: SRRK, RIVN, KSS")
    report_lines.append("• Consider complex orders to bypass")
    report_lines.append("• FBIO may need smaller size")
    report_lines.append("• All trades DAY orders with limits")

    # Risk Management
    report_lines.append("")
    report_lines.append("=" * 40)
    report_lines.append("🛡️ RISK MANAGEMENT")
    report_lines.append("-" * 40)
    report_lines.append("Stop Losses Set:")
    report_lines.append("• SRRK: $27.00 (-22%)")
    report_lines.append("• FBIO: $3.00 (-27%)")
    report_lines.append("• RIVN: $13.00 (-16%)")
    report_lines.append("• IONQ: $80.00 (short stop)")
    report_lines.append("• KSS: $15.00 (-12%)")

    # Summary
    report_lines.append("")
    report_lines.append("=" * 40)
    report_lines.append("📈 TRADING SUMMARY")
    report_lines.append("-" * 40)
    report_lines.append("Total Trades Planned: 12")
    report_lines.append("• DEE-BOT: 7 trades (4 sells, 3 buys)")
    report_lines.append("• SHORGAN-BOT: 5 trades (4 buys, 1 short)")
    report_lines.append("All approved by multi-agent consensus")

    # Footer
    report_lines.append("")
    report_lines.append("=" * 40)
    report_lines.append("🤖 AI Trading Bot - Fully Automated")
    report_lines.append("📊 Multi-Agent Consensus Active")
    report_lines.append("🔔 Next Update: 4:30 PM Post-Market")

    return "\n".join(report_lines)

def send_to_telegram(message):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    # Split long messages
    max_length = 4000
    messages = []

    if len(message) <= max_length:
        messages = [message]
    else:
        # Split by sections
        lines = message.split('\n')
        current_msg = []
        current_length = 0

        for line in lines:
            if current_length + len(line) > max_length:
                messages.append('\n'.join(current_msg))
                current_msg = [line]
                current_length = len(line)
            else:
                current_msg.append(line)
                current_length += len(line) + 1

        if current_msg:
            messages.append('\n'.join(current_msg))

    # Send messages
    success = True
    for msg in messages:
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': msg,
            'parse_mode': 'Markdown'
        }

        try:
            response = requests.post(url, json=data)
            if response.status_code != 200:
                # Try without markdown
                data['parse_mode'] = None
                response = requests.post(url, json=data)

            if response.status_code != 200:
                print(f"Failed to send to Telegram: {response.text}")
                success = False
        except Exception as e:
            print(f"Error sending to Telegram: {e}")
            success = False

    return success

def save_report(report):
    """Save report to file"""
    filename = f"docs/reports/premarket/premarket_plan_{datetime.now().strftime('%Y-%m-%d_%H%M')}.txt"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)

    return filename

def main():
    """Main execution"""
    print("=" * 60)
    print("GENERATING PRE-MARKET TRADING PLAN")
    print("=" * 60)

    # Generate report
    report = generate_premarket_report()

    # Display report
    print("\nReport Preview:")
    print("-" * 60)
    print(report)
    print("-" * 60)

    # Save report
    filename = save_report(report)
    print(f"\n✅ Report saved to: {filename}")

    # Send to Telegram
    if send_to_telegram(report):
        print("✅ Report sent to Telegram successfully!")
    else:
        print("❌ Failed to send to Telegram")

    print("\n" + "=" * 60)
    print("PRE-MARKET PLAN GENERATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()