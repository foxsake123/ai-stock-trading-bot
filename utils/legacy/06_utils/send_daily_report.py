"""
Daily Performance Report - Telegram Notification System
September 11, 2025
Sends comprehensive daily trading report to Telegram
"""

import requests
import json
from datetime import datetime, date
from pathlib import Path

# Telegram Bot Configuration
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
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("[SUCCESS] Message sent to Telegram")
            return True
        else:
            print(f"[ERROR] Failed to send message: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Telegram send failed: {str(e)}")
        return False

def load_portfolio_data():
    """Load the latest portfolio monitoring data"""
    monitor_dir = Path("C:/Users/shorg/ai-stock-trading-bot/04_risk/reports")
    
    # Get the most recent monitoring file
    monitor_files = list(monitor_dir.glob("portfolio_monitor_*.json"))
    if not monitor_files:
        return None
    
    latest_file = max(monitor_files, key=lambda p: p.stat().st_mtime)
    
    with open(latest_file, 'r') as f:
        return json.load(f)

def load_execution_data():
    """Load today's execution data"""
    trading_dir = Path("C:/Users/shorg/ai-stock-trading-bot/09_logs/trading")
    
    # Get today's DEE-BOT execution
    dee_files = list(trading_dir.glob(f"dee_bot_execution_{date.today().strftime('%Y%m%d')}*.json"))
    dee_data = None
    if dee_files:
        with open(max(dee_files, key=lambda p: p.stat().st_mtime), 'r') as f:
            dee_data = json.load(f)
    
    return dee_data

def format_daily_report():
    """Generate formatted daily report"""
    
    # Load data
    portfolio_data = load_portfolio_data()
    execution_data = load_execution_data()
    
    if not portfolio_data:
        return "ERROR: No portfolio data available"
    
    # Extract key metrics
    combined = portfolio_data['combined_metrics']
    dee_bot = portfolio_data['portfolios'].get('DEE-BOT', {})
    shorgan_bot = portfolio_data['portfolios'].get('SHORGAN-BOT', {})
    
    # Format the report
    report = []
    report.append("<b>AI STOCK TRADING BOT - DAILY REPORT</b>")
    report.append(f"<b>Date: {date.today()}</b>")
    report.append("=" * 35)
    
    # Portfolio Summary
    report.append("\n<b>PORTFOLIO SUMMARY</b>")
    report.append(f"Total Value: <b>${combined['total_value']:,.2f}</b>")
    report.append(f"Total Positions: {combined['total_positions']}")
    report.append(f"Unrealized P&L: <b>${combined['total_unrealized_pl']:+,.2f}</b>")
    
    # DEE-BOT Performance
    if dee_bot:
        report.append("\n<b>DEE-BOT (Conservative)</b>")
        report.append(f"Value: ${dee_bot['portfolio_value']:,.2f}")
        report.append(f"Positions: {len(dee_bot['positions'])}")
        report.append(f"P&L: ${dee_bot['risk_metrics']['total_unrealized_pl']:+,.2f}")
        
        # Top performers
        if dee_bot['positions']:
            best = max(dee_bot['positions'], key=lambda x: x['unrealized_plpc'])
            report.append(f"Best: {best['symbol']} ({best['unrealized_plpc']:+.2f}%)")
    
    # SHORGAN-BOT Performance
    if shorgan_bot:
        report.append("\n<b>SHORGAN-BOT (Aggressive)</b>")
        report.append(f"Value: ${shorgan_bot['portfolio_value']:,.2f}")
        report.append(f"Positions: {len(shorgan_bot['positions'])}")
        report.append(f"P&L: ${shorgan_bot['risk_metrics']['total_unrealized_pl']:+,.2f}")
        
        # Top performers
        if shorgan_bot['positions']:
            best = max(shorgan_bot['positions'], key=lambda x: x['unrealized_plpc'])
            report.append(f"Best: {best['symbol']} ({best['unrealized_plpc']:+.2f}%)")
    
    # Today's Trades
    if execution_data:
        report.append("\n<b>TODAY'S TRADES</b>")
        report.append(f"Executed: {len(execution_data['executed_orders'])} orders")
        report.append(f"Capital Deployed: ${execution_data['summary']['total_deployed']:,.2f}")
        
        # List trades
        for order in execution_data['executed_orders'][:3]:  # Top 3
            report.append(f"- {order['symbol']}: {order['shares']}sh @ ${order['price']:.2f}")
    
    # Risk Warnings
    if portfolio_data['warnings']:
        report.append("\n<b>RISK ALERTS</b>")
        for warning in portfolio_data['warnings']:
            report.append(f"[WARNING] {warning}")
    
    # Market Status
    report.append("\n<b>MARKET STATUS</b>")
    report.append("Strategy: Multi-Agent Consensus")
    report.append("Risk Level: CONTROLLED")
    report.append("Next Update: Tomorrow 4:15 PM ET")
    
    # Footer
    report.append("\n" + "=" * 35)
    report.append("System Status: OPERATIONAL")
    
    return "\n".join(report)

def send_daily_report():
    """Main function to send daily report"""
    
    print("=" * 60)
    print("SENDING DAILY PERFORMANCE REPORT")
    print("=" * 60)
    
    # Generate report
    report = format_daily_report()
    
    print("\nReport Preview:")
    print("-" * 40)
    # Convert HTML tags for console display
    console_report = report.replace("<b>", "").replace("</b>", "")
    print(console_report)
    print("-" * 40)
    
    # Send to Telegram
    success = send_telegram_message(report)
    
    if success:
        print("\n[SUCCESS] Daily report sent to Telegram")
        
        # Save report locally
        report_dir = Path("C:/Users/shorg/ai-stock-trading-bot/02_data/research/reports/daily_reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"daily_report_{date.today()}.txt"
        with open(report_file, 'w') as f:
            f.write(console_report)
        
        print(f"Report saved: {report_file}")
    else:
        print("\n[ERROR] Failed to send daily report")
    
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    send_daily_report()
    print("\nDaily report process complete!")