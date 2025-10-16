"""
Generate Post-Market Report for Both Trading Bots
Runs daily at 4:15 PM ET to send Telegram summary
"""

from alpaca.trading.client import TradingClient
from datetime import datetime, timedelta
import pandas as pd
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API credentials for both bots (from environment variables)
DEE_BOT_KEY = os.getenv("ALPACA_API_KEY_DEE")
DEE_BOT_SECRET = os.getenv("ALPACA_SECRET_KEY_DEE")

SHORGAN_BOT_KEY = os.getenv("ALPACA_API_KEY_SHORGAN")
SHORGAN_BOT_SECRET = os.getenv("ALPACA_SECRET_KEY_SHORGAN")

def get_bot_positions(api_key, secret_key, bot_name):
    """Get current positions for a bot"""
    try:
        client = TradingClient(api_key, secret_key, paper=True)
        account = client.get_account()
        positions = client.get_all_positions()

        bot_data = {
            "name": bot_name,
            "portfolio_value": float(account.portfolio_value),
            "cash": float(account.cash),
            "buying_power": float(account.buying_power),
            "positions": [],
            "total_market_value": 0,
            "total_unrealized_pnl": 0,
            "total_realized_pnl": float(account.daytradingratio) if hasattr(account, 'daytradingratio') else 0
        }

        for position in positions:
            pos_data = {
                "symbol": position.symbol,
                "qty": int(position.qty),
                "avg_price": float(position.avg_entry_price),
                "current_price": float(position.current_price),
                "market_value": float(position.market_value),
                "unrealized_pnl": float(position.unrealized_pl),
                "unrealized_pnl_pct": (float(position.unrealized_pl) / (float(position.avg_entry_price) * int(position.qty))) * 100,
                "change_today": float(position.change_today) if hasattr(position, 'change_today') else 0
            }
            bot_data["positions"].append(pos_data)
            bot_data["total_market_value"] += pos_data["market_value"]
            bot_data["total_unrealized_pnl"] += pos_data["unrealized_pnl"]

        return bot_data
    except Exception as e:
        print(f"Error getting {bot_name} positions: {str(e)}")
        return None

def generate_report():
    """Generate comprehensive post-market report"""

    print("="*70)
    print("              POST-MARKET REPORT - DUAL BOT SYSTEM")
    print(f"                   {datetime.now().strftime('%B %d, %Y - %I:%M %p ET')}")
    print("="*70)

    # Get DEE-BOT data
    dee_data = get_bot_positions(DEE_BOT_KEY, DEE_BOT_SECRET, "DEE-BOT")

    # Get SHORGAN-BOT data
    shorgan_data = get_bot_positions(SHORGAN_BOT_KEY, SHORGAN_BOT_SECRET, "SHORGAN-BOT")

    # Combined metrics
    total_portfolio = 0
    total_unrealized = 0

    # DEE-BOT Section
    if dee_data:
        print("\n" + "-"*70)
        print("[DEE-BOT] Beta-Neutral S&P 100 Strategy")
        print("-"*70)
        print(f"Portfolio Value: ${dee_data['portfolio_value']:,.2f}")
        print(f"Cash Available: ${dee_data['cash']:,.2f}")
        print(f"Positions: {len(dee_data['positions'])}")
        print(f"Total Unrealized P&L: ${dee_data['total_unrealized_pnl']:,.2f}")

        print("\nTop Performers:")
        sorted_positions = sorted(dee_data['positions'], key=lambda x: x['unrealized_pnl_pct'], reverse=True)
        for pos in sorted_positions[:3]:
            print(f"  [+] {pos['symbol']}: {pos['qty']} shares | +${pos['unrealized_pnl']:,.2f} ({pos['unrealized_pnl_pct']:.1f}%)")

        print("\nBottom Performers:")
        for pos in sorted_positions[-3:]:
            if pos['unrealized_pnl'] < 0:
                print(f"  [-] {pos['symbol']}: {pos['qty']} shares | ${pos['unrealized_pnl']:,.2f} ({pos['unrealized_pnl_pct']:.1f}%)")

        total_portfolio += dee_data['portfolio_value']
        total_unrealized += dee_data['total_unrealized_pnl']

    # SHORGAN-BOT Section
    if shorgan_data:
        print("\n" + "-"*70)
        print("[SHORGAN-BOT] Catalyst-Driven Micro-Cap Strategy")
        print("-"*70)
        print(f"Portfolio Value: ${shorgan_data['portfolio_value']:,.2f}")
        print(f"Cash Available: ${shorgan_data['cash']:,.2f}")
        print(f"Positions: {len(shorgan_data['positions'])}")
        print(f"Total Unrealized P&L: ${shorgan_data['total_unrealized_pnl']:,.2f}")

        print("\nTop Performers:")
        sorted_positions = sorted(shorgan_data['positions'], key=lambda x: x['unrealized_pnl_pct'], reverse=True)
        for pos in sorted_positions[:3]:
            print(f"  [+] {pos['symbol']}: {pos['qty']} shares | +${pos['unrealized_pnl']:,.2f} ({pos['unrealized_pnl_pct']:.1f}%)")

        print("\nBottom Performers:")
        for pos in sorted_positions[-3:]:
            if pos['unrealized_pnl'] < 0:
                print(f"  [-] {pos['symbol']}: {pos['qty']} shares | ${pos['unrealized_pnl']:,.2f} ({pos['unrealized_pnl_pct']:.1f}%)")

        # Highlight catalyst plays
        print("\n[CATALYST] Key Positions:")
        catalyst_stocks = ["INCY", "KSS", "RGTI", "ORCL", "IONQ", "BBAI"]
        for pos in shorgan_data['positions']:
            if pos['symbol'] in catalyst_stocks:
                status = "[+]" if pos['unrealized_pnl'] > 0 else "[-]"
                print(f"  {status} {pos['symbol']}: ${pos['market_value']:,.2f} | P&L: ${pos['unrealized_pnl']:,.2f}")

        total_portfolio += shorgan_data['portfolio_value']
        total_unrealized += shorgan_data['total_unrealized_pnl']

    # Combined Summary
    print("\n" + "="*70)
    print("[COMBINED] PORTFOLIO SUMMARY")
    print("="*70)
    print(f"Total Portfolio Value: ${total_portfolio:,.2f}")
    print(f"Total Unrealized P&L: ${total_unrealized:,.2f}")

    total_positions = 0
    if dee_data:
        total_positions += len(dee_data['positions'])
    if shorgan_data:
        total_positions += len(shorgan_data['positions'])
    print(f"Total Positions: {total_positions}")

    # Tomorrow's Focus - Dynamic based on current holdings
    print("\n" + "-"*70)
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%b %d")
    print(f"[TOMORROW] FOCUS ({tomorrow_date})")
    print("-"*70)

    # Find positions with upcoming catalysts or near stop losses
    if shorgan_data:
        catalyst_positions = []
        stop_loss_warnings = []

        for pos in shorgan_data['positions']:
            # Warn if position is down >10%
            if pos['unrealized_pnl_pct'] < -10:
                stop_loss_warnings.append(f"   - {pos['symbol']}: Down {pos['unrealized_pnl_pct']:.1f}%")

        if stop_loss_warnings:
            print("[WARNING] POSITIONS NEAR STOP LOSS:")
            for warning in stop_loss_warnings[:5]:
                print(warning)

    print("\n[INFO] Review Claude research for tomorrow's trade plan")

    # Only save and send if we have data
    if not dee_data or not shorgan_data:
        print("\n[ERROR] Failed to fetch portfolio data - cannot generate report")
        return None

    # Save report
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "dee_bot": dee_data,
        "shorgan_bot": shorgan_data,
        "combined": {
            "total_portfolio": total_portfolio,
            "total_unrealized_pnl": total_unrealized,
            "total_positions": total_positions
        }
    }

    # Save to daily reports directory
    date_str = datetime.now().strftime('%Y-%m-%d')
    report_dir = Path(f"docs/reports/post-market")
    report_dir.mkdir(parents=True, exist_ok=True)

    json_filename = report_dir / f"post_market_report_{date_str}.json"
    txt_filename = report_dir / f"post_market_report_{date_str}.txt"

    # Save JSON version
    with open(json_filename, 'w') as f:
        json.dump(report_data, f, indent=2)

    # Save text version (for easy viewing)
    with open(txt_filename, 'w') as f:
        f.write(f"POST-MARKET REPORT\n")
        f.write(f"{datetime.now().strftime('%A, %B %d, %Y - %I:%M %p ET')}\n")
        f.write("="*70 + "\n\n")
        f.write(f"DEE-BOT Portfolio: ${report_data['dee_bot']['portfolio_value']:,.2f}\n")
        f.write(f"SHORGAN-BOT Portfolio: ${report_data['shorgan_bot']['portfolio_value']:,.2f}\n")
        f.write(f"Combined Total: ${report_data['combined']['total_portfolio']:,.2f}\n")
        f.write(f"Total P/L: ${report_data['combined']['total_unrealized_pnl']:,.2f}\n")

    print(f"\n[SAVED] Reports saved:")
    print(f"   JSON: {json_filename}")
    print(f"   TXT: {txt_filename}")
    print("="*70)

    return report_data

def send_telegram_report(report_data):
    """Send report via Telegram"""
    import requests

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7526351226:AAHQz1PV-4OdNmCgLdgzPJ8emHxIeGdPW6Q")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7769365988")

    # Calculate P/L percentages
    dee_total = report_data['dee_bot']['portfolio_value']
    dee_pnl_pct = (report_data['dee_bot']['total_unrealized_pnl'] / (dee_total - report_data['dee_bot']['total_unrealized_pnl'])) * 100 if dee_total else 0

    shorgan_total = report_data['shorgan_bot']['portfolio_value']
    shorgan_pnl_pct = (report_data['shorgan_bot']['total_unrealized_pnl'] / (shorgan_total - report_data['shorgan_bot']['total_unrealized_pnl'])) * 100 if shorgan_total else 0

    combined_pnl_pct = (report_data['combined']['total_unrealized_pnl'] / (report_data['combined']['total_portfolio'] - report_data['combined']['total_unrealized_pnl'])) * 100

    # Format message
    msg = f"""📊 *POST-MARKET REPORT*
{datetime.now().strftime('%A, %B %d, %Y - %I:%M %p ET')}

*DEE-BOT (Beta-Neutral)*
Portfolio: ${report_data['dee_bot']['portfolio_value']:,.2f}
P&L: ${report_data['dee_bot']['total_unrealized_pnl']:,.2f} ({dee_pnl_pct:+.2f}%)
Positions: {len(report_data['dee_bot']['positions'])}

*SHORGAN-BOT (Catalyst)*
Portfolio: ${report_data['shorgan_bot']['portfolio_value']:,.2f}
P&L: ${report_data['shorgan_bot']['total_unrealized_pnl']:,.2f} ({shorgan_pnl_pct:+.2f}%)
Positions: {len(report_data['shorgan_bot']['positions'])}

*COMBINED TOTAL*
Portfolio: ${report_data['combined']['total_portfolio']:,.2f}
Total P&L: ${report_data['combined']['total_unrealized_pnl']:,.2f} ({combined_pnl_pct:+.2f}%)

📈 Review Claude research for tomorrow's trade plan
"""

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("\n[SUCCESS] Report sent to Telegram")
        else:
            print(f"\n[ERROR] Telegram send failed: {response.text}")
    except Exception as e:
        print(f"\n[ERROR] Telegram send failed: {str(e)}")

if __name__ == "__main__":
    report = generate_report()
    if report:
        send_telegram_report(report)