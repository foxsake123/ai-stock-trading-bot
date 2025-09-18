"""
Generate Post-Market Report for Both Trading Bots
September 18, 2025 - 4:30 PM ET
"""

from alpaca.trading.client import TradingClient
from datetime import datetime
import pandas as pd
import json

# API credentials for both bots
DEE_BOT_KEY = "PK6FZK4DAQVTD7DYVH78"
DEE_BOT_SECRET = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"

SHORGAN_BOT_KEY = "PKJRLSB2MFEJUSK6UK2E"
SHORGAN_BOT_SECRET = "QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic"

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
    print(f"Total Positions: {len(dee_data['positions']) + len(shorgan_data['positions'])}")

    # Tomorrow's Focus
    print("\n" + "-"*70)
    print("[TOMORROW] FOCUS (Sept 19)")
    print("-"*70)
    print("[CRITICAL] EVENT: INCY FDA Decision")
    print("   - Position: 61 shares @ $83.97")
    print("   - Stop Loss: $77.25")
    print("   - Binary Event: Opzelura pediatric approval")
    print("\n[WARNING] ACTIVE STOP LOSSES:")
    print("   - KSS: Stop at $15.18")
    print("   - INCY: Stop at $77.25")

    # Save report
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "dee_bot": dee_data,
        "shorgan_bot": shorgan_data,
        "combined": {
            "total_portfolio": total_portfolio,
            "total_unrealized_pnl": total_unrealized,
            "total_positions": len(dee_data['positions']) + len(shorgan_data['positions'])
        }
    }

    filename = f"../../daily-reports/post_market_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report_data, f, indent=2)

    print(f"\n[SAVED] Report saved to: {filename}")
    print("="*70)

    return report_data

def send_telegram_report(report_data):
    """Send report via Telegram"""
    import requests

    TELEGRAM_BOT_TOKEN = "7526351226:AAHQz1PV-4OdNmCgLdgzPJ8emHxIeGdPW6Q"
    CHAT_ID = "7769365988"

    # Format message
    msg = f"""📊 *POST-MARKET REPORT*
{datetime.now().strftime('%B %d, %Y - %I:%M %p ET')}

*DEE-BOT (Beta-Neutral)*
Portfolio: ${report_data['dee_bot']['portfolio_value']:,.2f}
P&L: ${report_data['dee_bot']['total_unrealized_pnl']:,.2f}
Positions: {len(report_data['dee_bot']['positions'])}

*SHORGAN-BOT (Catalyst)*
Portfolio: ${report_data['shorgan_bot']['portfolio_value']:,.2f}
P&L: ${report_data['shorgan_bot']['total_unrealized_pnl']:,.2f}
Positions: {len(report_data['shorgan_bot']['positions'])}

*COMBINED TOTAL*
Portfolio: ${report_data['combined']['total_portfolio']:,.2f}
Total P&L: ${report_data['combined']['total_unrealized_pnl']:,.2f}

🚨 *TOMORROW: INCY FDA Decision*
Position: 61 shares @ $83.97
Stop Loss: $77.25
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