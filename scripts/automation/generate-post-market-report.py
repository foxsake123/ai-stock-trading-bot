#!/usr/bin/env python3
"""
Post-Market Report Generator with Live Alpaca Data
Includes today's trades, individual holdings, and daily performance
"""

import os
import json
import csv
import requests
from datetime import datetime, date
from pathlib import Path
from alpaca.trading.client import TradingClient
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c"
TELEGRAM_CHAT_ID = "7870288896"

def send_telegram_message(message):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("[SUCCESS] Message sent to Telegram")
            return True
        else:
            print(f"[ERROR] Failed to send message: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Telegram send failed: {str(e)}")
        return False

def get_todays_trades():
    """Get today's executed trades from the most recent log file"""
    log_dir = Path("scripts-and-data/trade-logs")
    if not log_dir.exists():
        return [], []

    # Find today's log files
    today = datetime.now().strftime("%Y%m%d")
    log_files = sorted(log_dir.glob(f"daily_execution_{today}_*.json"), reverse=True)

    dee_trades = []
    shorgan_trades = []

    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                data = json.load(f)

            if 'executed_trades' in data:
                for trade in data['executed_trades']:
                    bot = trade.get('bot', 'UNKNOWN')
                    trade_str = f"{trade['action']} {trade['shares']} {trade['symbol']} @ ${trade.get('price', 'MKT')}"

                    if bot == 'DEE-BOT':
                        dee_trades.append(trade_str)
                    elif bot == 'SHORGAN-BOT':
                        shorgan_trades.append(trade_str)
        except Exception as e:
            print(f"Error reading log {log_file}: {e}")
            continue

    return dee_trades, shorgan_trades

def get_live_portfolio_data(client, bot_name, starting_capital):
    """Fetch live portfolio data from Alpaca"""
    try:
        account = client.get_account()
        positions = client.get_all_positions()

        # Account level data
        portfolio_value = float(account.portfolio_value)
        cash = float(account.cash)
        equity = float(account.equity)

        # Calculate total P&L
        pnl = portfolio_value - starting_capital
        pnl_pct = (pnl / starting_capital) * 100

        # Process positions
        holdings = []
        total_todays_pl = 0
        total_todays_pl_pct = 0

        for pos in positions:
            qty = int(pos.qty)
            side = "SHORT" if pos.side == "short" else "LONG"
            price = float(pos.current_price)
            value = float(pos.market_value)
            avg_entry = float(pos.avg_entry_price)
            cost_basis = float(pos.cost_basis)

            # Total P/L (unrealized)
            unrealized = float(pos.unrealized_pl)
            unrealized_pct = float(pos.unrealized_plpc) * 100

            # Today's P/L (intraday change)
            todays_pl = float(pos.unrealized_intraday_pl)
            todays_pl_pct = float(pos.unrealized_intraday_plpc) * 100

            total_todays_pl += todays_pl

            holdings.append({
                'symbol': pos.symbol,
                'qty': qty,
                'side': side,
                'price': price,
                'value': value,
                'avg_entry': avg_entry,
                'cost_basis': cost_basis,
                'todays_pl': todays_pl,
                'todays_pl_pct': todays_pl_pct,
                'unrealized_pl': unrealized,
                'unrealized_pct': unrealized_pct
            })

        # Sort by absolute value (largest positions first)
        holdings.sort(key=lambda x: abs(x['value']), reverse=True)

        # Calculate today's portfolio P/L percentage
        if portfolio_value > 0:
            todays_portfolio_pct = (total_todays_pl / portfolio_value) * 100
        else:
            todays_portfolio_pct = 0

        return {
            'portfolio_value': portfolio_value,
            'cash': cash,
            'equity': equity,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'todays_pl': total_todays_pl,
            'todays_pl_pct': todays_portfolio_pct,
            'positions_count': len(holdings),
            'holdings': holdings
        }

    except Exception as e:
        print(f"[ERROR] Failed to get data for {bot_name}: {e}")
        return None

def format_report(dee_data, shorgan_data, dee_trades, shorgan_trades):
    """Format the comprehensive post-market report"""

    now = datetime.now()

    # Calculate combined totals
    combined_value = dee_data['portfolio_value'] + shorgan_data['portfolio_value']
    combined_pnl = dee_data['pnl'] + shorgan_data['pnl']
    combined_pnl_pct = (combined_pnl / 200000) * 100

    # Calculate combined today's P/L
    combined_todays_pl = dee_data['todays_pl'] + shorgan_data['todays_pl']
    combined_todays_pl_pct = (combined_todays_pl / combined_value) * 100 if combined_value > 0 else 0

    report = f"""<b>POST-MARKET REPORT</b>
{now.strftime('%A, %B %d, %Y - %I:%M %p ET')}
============================================

<b>DEE-BOT HOLDINGS ({dee_data['positions_count']} positions)</b>
+-------+-----+--------+------+-----------+-----------+------------+-------------+-------------+-------------+
| Asset | Qty | Price  | Side | Mkt Value | Avg Entry | Cost Basis | Today P/L % | Today P/L $ | Total P/L % |
+-------+-----+--------+------+-----------+-----------+------------+-------------+-------------+-------------+"""

    # DEE-BOT holdings
    for holding in dee_data['holdings']:
        report += f"\n| {holding['symbol']:<5} | {holding['qty']:>3} | ${holding['price']:>6.2f} | {holding['side']:<4} | ${holding['value']:>8,.2f} | ${holding['avg_entry']:>8.2f} | ${holding['cost_basis']:>9,.2f} | {holding['todays_pl_pct']:>+10.2f}% | ${holding['todays_pl']:>+10.2f} | {holding['unrealized_pct']:>+10.2f}% |"

    # DEE-BOT Total row
    dee_total_value = sum(h['value'] for h in dee_data['holdings'])
    dee_total_cost = sum(h['cost_basis'] for h in dee_data['holdings'])
    report += f"\n+-------+-----+--------+------+-----------+-----------+------------+-------------+-------------+-------------+"
    report += f"\n| TOTAL |     |        |      | ${dee_total_value:>8,.2f} |           | ${dee_total_cost:>9,.2f} | {dee_data['todays_pl_pct']:>+10.2f}% | ${dee_data['todays_pl']:>+10.2f} | {dee_data['pnl_pct']:>+10.2f}% |"
    report += f"\n+-------+-----+--------+------+-----------+-----------+------------+-------------+-------------+-------------+"

    report += f"""

<b>SHORGAN-BOT HOLDINGS ({shorgan_data['positions_count']} positions)</b>
+-------+------+--------+-------+-----------+-----------+------------+-------------+-------------+-------------+
| Asset | Qty  | Price  | Side  | Mkt Value | Avg Entry | Cost Basis | Today P/L % | Today P/L $ | Total P/L % |
+-------+------+--------+-------+-----------+-----------+------------+-------------+-------------+-------------+"""

    # SHORGAN-BOT holdings
    for holding in shorgan_data['holdings']:
        report += f"\n| {holding['symbol']:<5} | {holding['qty']:>4} | ${holding['price']:>6.2f} | {holding['side']:<5} | ${holding['value']:>8,.2f} | ${holding['avg_entry']:>8.2f} | ${holding['cost_basis']:>9,.2f} | {holding['todays_pl_pct']:>+10.2f}% | ${holding['todays_pl']:>+10.2f} | {holding['unrealized_pct']:>+10.2f}% |"

    # SHORGAN-BOT Total row
    shorgan_total_value = sum(h['value'] for h in shorgan_data['holdings'])
    shorgan_total_cost = sum(h['cost_basis'] for h in shorgan_data['holdings'])
    report += f"\n+-------+------+--------+-------+-----------+-----------+------------+-------------+-------------+-------------+"
    report += f"\n| TOTAL |      |        |       | ${shorgan_total_value:>8,.2f} |           | ${shorgan_total_cost:>9,.2f} | {shorgan_data['todays_pl_pct']:>+10.2f}% | ${shorgan_data['todays_pl']:>+10.2f} | {shorgan_data['pnl_pct']:>+10.2f}% |"
    report += f"\n+-------+------+--------+-------+-----------+-----------+------------+-------------+-------------+-------------+"

    report += f"""

<b>COMBINED PORTFOLIO SUMMARY</b>
Portfolio Value:  ${combined_value:>12,.2f}
Today's P/L:      ${combined_todays_pl:>+12,.2f} ({combined_todays_pl_pct:>+6.2f}%)
Total P/L:        ${combined_pnl:>+12,.2f} ({combined_pnl_pct:>+6.2f}%)
Active Positions: {dee_data['positions_count'] + shorgan_data['positions_count']:>3}

<b>TODAY'S TRADES</b>
DEE-BOT:    {len(dee_trades)} trades
SHORGAN:    {len(shorgan_trades)} trades

============================================
Next Report: 4:30 PM ET | System: Online
============================================"""

    return report

def save_report(report_text):
    """Save report to file"""
    report_dir = Path("docs/reports/post-market")
    report_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    report_file = report_dir / f"post_market_report_{today}.txt"

    with open(report_file, 'w') as f:
        # Strip HTML tags for text file
        clean_text = report_text.replace('<b>', '').replace('</b>', '')
        f.write(clean_text)

    print(f"Report saved: {report_file}")
    return report_file

def save_csv_report(dee_data, shorgan_data):
    """Save portfolio data to CSV for easy analysis"""
    report_dir = Path("docs/reports/post-market")
    report_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    csv_file = report_dir / f"post_market_report_{today}.csv"

    # Prepare CSV data
    rows = []

    # Header row
    rows.append([
        'Bot',
        'Symbol',
        'Quantity',
        'Side',
        'Current Price',
        'Market Value',
        'Avg Entry Price',
        'Cost Basis',
        'Today P/L %',
        'Today P/L $',
        'Total P/L %',
        'Total P/L $'
    ])

    # DEE-BOT holdings
    for holding in dee_data['holdings']:
        rows.append([
            'DEE-BOT',
            holding['symbol'],
            holding['qty'],
            holding['side'],
            f"${holding['price']:.2f}",
            f"${holding['value']:,.2f}",
            f"${holding['avg_entry']:.2f}",
            f"${holding['cost_basis']:,.2f}",
            f"{holding['todays_pl_pct']:+.2f}%",
            f"${holding['todays_pl']:+,.2f}",
            f"{holding['unrealized_pct']:+.2f}%",
            f"${holding['unrealized_pl']:+,.2f}"
        ])

    # DEE-BOT totals
    rows.append([
        'DEE-BOT',
        'TOTAL',
        len(dee_data['holdings']),
        '',
        '',
        f"${sum(h['value'] for h in dee_data['holdings']):,.2f}",
        '',
        f"${sum(h['cost_basis'] for h in dee_data['holdings']):,.2f}",
        f"{dee_data['todays_pl_pct']:+.2f}%",
        f"${dee_data['todays_pl']:+,.2f}",
        f"{dee_data['pnl_pct']:+.2f}%",
        f"${dee_data['pnl']:+,.2f}"
    ])

    # Empty row separator
    rows.append([''] * 12)

    # SHORGAN-BOT holdings
    for holding in shorgan_data['holdings']:
        rows.append([
            'SHORGAN-BOT',
            holding['symbol'],
            holding['qty'],
            holding['side'],
            f"${holding['price']:.2f}",
            f"${holding['value']:,.2f}",
            f"${holding['avg_entry']:.2f}",
            f"${holding['cost_basis']:,.2f}",
            f"{holding['todays_pl_pct']:+.2f}%",
            f"${holding['todays_pl']:+,.2f}",
            f"{holding['unrealized_pct']:+.2f}%",
            f"${holding['unrealized_pl']:+,.2f}"
        ])

    # SHORGAN-BOT totals
    rows.append([
        'SHORGAN-BOT',
        'TOTAL',
        len(shorgan_data['holdings']),
        '',
        '',
        f"${sum(h['value'] for h in shorgan_data['holdings']):,.2f}",
        '',
        f"${sum(h['cost_basis'] for h in shorgan_data['holdings']):,.2f}",
        f"{shorgan_data['todays_pl_pct']:+.2f}%",
        f"${shorgan_data['todays_pl']:+,.2f}",
        f"{shorgan_data['pnl_pct']:+.2f}%",
        f"${shorgan_data['pnl']:+,.2f}"
    ])

    # Empty row separator
    rows.append([''] * 12)

    # Combined summary
    combined_value = dee_data['portfolio_value'] + shorgan_data['portfolio_value']
    combined_pnl = dee_data['pnl'] + shorgan_data['pnl']
    combined_pnl_pct = (combined_pnl / 200000) * 100
    combined_todays_pl = dee_data['todays_pl'] + shorgan_data['todays_pl']
    combined_todays_pl_pct = (combined_todays_pl / combined_value) * 100 if combined_value > 0 else 0

    rows.append([
        'COMBINED',
        'PORTFOLIO',
        dee_data['positions_count'] + shorgan_data['positions_count'],
        '',
        '',
        f"${combined_value:,.2f}",
        '',
        '$200,000.00',
        f"{combined_todays_pl_pct:+.2f}%",
        f"${combined_todays_pl:+,.2f}",
        f"{combined_pnl_pct:+.2f}%",
        f"${combined_pnl:+,.2f}"
    ])

    # Write CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"CSV report saved: {csv_file}")
    return csv_file

def main():
    """Main execution"""
    print("="*60)
    print("GENERATING POST-MARKET REPORT")
    print("="*60)

    # Initialize Alpaca clients
    dee_client = TradingClient(
        os.getenv('ALPACA_API_KEY_DEE'),
        os.getenv('ALPACA_SECRET_KEY_DEE'),
        paper=True
    )

    shorgan_client = TradingClient(
        os.getenv('ALPACA_API_KEY_SHORGAN'),
        os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
        paper=True
    )

    # Fetch live data
    print("Fetching live portfolio data from Alpaca...")
    dee_data = get_live_portfolio_data(dee_client, "DEE-BOT", 100000)
    shorgan_data = get_live_portfolio_data(shorgan_client, "SHORGAN-BOT", 100000)

    if not dee_data or not shorgan_data:
        print("[ERROR] Failed to fetch portfolio data")
        return

    # Get today's trades
    print("Loading today's trade history...")
    dee_trades, shorgan_trades = get_todays_trades()

    # Generate report
    print("Generating report...")
    report = format_report(dee_data, shorgan_data, dee_trades, shorgan_trades)

    # Preview
    print("\nReport Preview:")
    print("-" * 50)
    clean_preview = report.replace('<b>', '').replace('</b>', '')
    print(clean_preview[:1500])  # Show first 1500 chars
    if len(clean_preview) > 1500:
        print("... (truncated)")
    print("-" * 50)

    # Save report (TXT)
    report_file = save_report(report)

    # Save CSV report
    csv_file = save_csv_report(dee_data, shorgan_data)

    # Send to Telegram
    send_telegram_message(report)

    print("\n[SUCCESS] Post-market report generated and sent")
    print(f"TXT: {report_file}")
    print(f"CSV: {csv_file}")
    print("="*60)

if __name__ == "__main__":
    main()
