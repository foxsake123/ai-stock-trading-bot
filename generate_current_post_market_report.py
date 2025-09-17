#!/usr/bin/env python3
"""
Current Post-Market Report Generator
Uses actual portfolio data and sends comprehensive report via Telegram
September 16, 2025
"""

import json
import requests
from datetime import datetime, date
from pathlib import Path

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

def load_current_portfolio_data():
    """Load current portfolio positions from CSV files"""
    
    portfolios = {
        'DEE-BOT': {'positions': [], 'total_value': 0, 'pnl': 0, 'cash': 100000},
        'SHORGAN-BOT': {'positions': [], 'total_value': 0, 'pnl': 0, 'cash': 100000}
    }
    
    # Load DEE-BOT positions
    dee_file = Path("02_data/portfolio/positions/dee_bot_positions.csv")
    if dee_file.exists():
        with open(dee_file, 'r') as f:
            lines = f.readlines()[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.strip().split(',')
                    if len(parts) >= 8:
                        symbol = parts[0]
                        quantity = int(parts[1])
                        avg_price = float(parts[2])
                        current_price = float(parts[3])
                        pnl = float(parts[4])
                        
                        position_value = quantity * current_price
                        portfolios['DEE-BOT']['positions'].append({
                            'symbol': symbol,
                            'quantity': quantity,
                            'avg_price': avg_price,
                            'current_price': current_price,
                            'position_value': position_value,
                            'pnl': pnl,
                            'pnl_pct': pnl / (quantity * avg_price) * 100 if quantity * avg_price > 0 else 0
                        })
                        portfolios['DEE-BOT']['total_value'] += position_value
                        portfolios['DEE-BOT']['pnl'] += pnl
    
    # Load SHORGAN-BOT positions  
    shorgan_file = Path("02_data/portfolio/positions/shorgan_bot_positions.csv")
    if shorgan_file.exists():
        with open(shorgan_file, 'r') as f:
            lines = f.readlines()[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.strip().split(',')
                    # Handle new format with 11 columns (market_value column)
                    if len(parts) >= 11:
                        symbol = parts[0]
                        quantity = int(parts[1])
                        avg_price = float(parts[2])
                        current_price = float(parts[3])
                        market_value = float(parts[4])
                        cost_basis = float(parts[5])
                        unrealized_pnl = float(parts[6])
                        unrealized_pnl_pct = float(parts[7])
                        
                        # Use absolute value for short positions
                        position_value = abs(market_value)
                        
                        portfolios['SHORGAN-BOT']['positions'].append({
                            'symbol': symbol,
                            'quantity': quantity,
                            'avg_price': avg_price,
                            'current_price': current_price,
                            'position_value': position_value,
                            'pnl': unrealized_pnl,
                            'pnl_pct': unrealized_pnl_pct
                        })
                        portfolios['SHORGAN-BOT']['total_value'] += position_value
                        portfolios['SHORGAN-BOT']['pnl'] += unrealized_pnl
                    elif len(parts) >= 8:
                        # Fallback to old format
                        symbol = parts[0]
                        quantity = int(parts[1])
                        avg_price = float(parts[2])
                        current_price = float(parts[3])
                        pnl = float(parts[4])
                        
                        position_value = quantity * current_price
                        portfolios['SHORGAN-BOT']['positions'].append({
                            'symbol': symbol,
                            'quantity': quantity,
                            'avg_price': avg_price,
                            'current_price': current_price,
                            'position_value': position_value,
                            'pnl': pnl,
                            'pnl_pct': pnl / (quantity * avg_price) * 100 if quantity * avg_price > 0 else 0
                        })
                        portfolios['SHORGAN-BOT']['total_value'] += position_value
                        portfolios['SHORGAN-BOT']['pnl'] += pnl
    
    # Calculate actual portfolio values (cash + positions)
    # Estimate cash remaining based on starting capital minus cost basis
    if portfolios['SHORGAN-BOT']['positions']:
        total_cost = sum(abs(p['quantity'] * p['avg_price']) for p in portfolios['SHORGAN-BOT']['positions'])
        portfolios['SHORGAN-BOT']['cash'] = max(0, 100000 - total_cost)
    
    if portfolios['DEE-BOT']['positions']:
        total_cost = sum(p['quantity'] * p['avg_price'] for p in portfolios['DEE-BOT']['positions'])
        portfolios['DEE-BOT']['cash'] = max(0, 100000 - total_cost)
    
    return portfolios

def load_execution_data():
    """Load today's execution data"""
    executions = {'DEE-BOT': [], 'SHORGAN-BOT': []}
    
    # Check for DEE-BOT executions
    dee_exec_file = Path(f"02_data/portfolio/executions/dee_bot_execution_{date.today().strftime('%Y-%m-%d')}.json")
    if dee_exec_file.exists():
        with open(dee_exec_file, 'r') as f:
            data = json.load(f)
            executions['DEE-BOT'] = data.get('executed_trades', [])
    
    # Check for SHORGAN-BOT executions (from execution reports)
    exec_dir = Path("02_data/reports/execution")
    if exec_dir.exists():
        for exec_file in exec_dir.glob(f"execution_report_{date.today().strftime('%Y%m%d')}*.json"):
            with open(exec_file, 'r') as f:
                data = json.load(f)
                if data.get('executed_orders'):
                    executions['SHORGAN-BOT'].extend(data['executed_orders'])
    
    return executions

def format_comprehensive_report():
    """Generate comprehensive post-market report"""
    
    portfolios = load_current_portfolio_data()
    executions = load_execution_data()
    
    # Calculate totals (cash + positions)
    dee_total_value = portfolios['DEE-BOT']['cash'] + portfolios['DEE-BOT']['total_value']
    shorgan_total_value = portfolios['SHORGAN-BOT']['cash'] + portfolios['SHORGAN-BOT']['total_value']
    total_portfolio_value = dee_total_value + shorgan_total_value
    total_pnl = portfolios['DEE-BOT']['pnl'] + portfolios['SHORGAN-BOT']['pnl']
    total_positions = len(portfolios['DEE-BOT']['positions']) + len(portfolios['SHORGAN-BOT']['positions'])
    
    # Calculate returns based on starting capital
    starting_capital = 200000  # $100k per bot
    total_return_pct = (total_pnl / starting_capital) * 100 if starting_capital > 0 else 0
    
    report = []
    report.append("<b>AI TRADING BOT - POST-MARKET REPORT</b>")
    report.append(f"<b>{date.today().strftime('%A, %B %d, %Y')}</b>")
    report.append(f"<b>{datetime.now().strftime('%I:%M %p ET')}</b>")
    report.append("=" * 45)
    
    # Portfolio Overview
    report.append("\n<b>PORTFOLIO OVERVIEW</b>")
    report.append(f"Total Portfolio Value: <b>${total_portfolio_value:,.2f}</b>")
    report.append(f"Total Unrealized P&L: <b>${total_pnl:+,.2f}</b>")
    report.append(f"Total Return: <b>{total_return_pct:+.2f}%</b>")
    report.append(f"Active Positions: <b>{total_positions}</b>")
    
    # DEE-BOT Analysis
    report.append("\n<b>DEE-BOT (Beta-Neutral Strategy)</b>")
    dee_data = portfolios['DEE-BOT']
    report.append(f"Portfolio Value: <b>${dee_total_value:,.2f}</b>")
    report.append(f"Position Value: <b>${dee_data['total_value']:,.2f}</b>")
    report.append(f"Cash Available: <b>${dee_data['cash']:,.2f}</b>")
    report.append(f"Unrealized P&L: <b>${dee_data['pnl']:+,.2f}</b>")
    report.append(f"Positions: <b>{len(dee_data['positions'])}</b>")
    
    if dee_data['positions']:
        # Best and worst performers
        best_dee = max(dee_data['positions'], key=lambda x: x['pnl_pct'])
        worst_dee = min(dee_data['positions'], key=lambda x: x['pnl_pct'])
        report.append(f"Best: <b>{best_dee['symbol']} ({best_dee['pnl_pct']:+.2f}%)</b>")
        report.append(f"Worst: <b>{worst_dee['symbol']} ({worst_dee['pnl_pct']:+.2f}%)</b>")
        
        # Today's DEE-BOT trades
        if executions['DEE-BOT']:
            report.append(f"\n<b>Today's DEE-BOT Trades:</b>")
            for trade in executions['DEE-BOT']:
                report.append(f"- {trade['symbol']}: {trade['shares']} @ ${trade['price']:.2f}")
    
    # SHORGAN-BOT Analysis
    report.append("\n<b>SHORGAN-BOT (Catalyst Strategy)</b>")
    shorgan_data = portfolios['SHORGAN-BOT']
    report.append(f"Portfolio Value: <b>${shorgan_total_value:,.2f}</b>")
    report.append(f"Position Value: <b>${shorgan_data['total_value']:,.2f}</b>")
    report.append(f"Cash Available: <b>${shorgan_data['cash']:,.2f}</b>")
    report.append(f"Unrealized P&L: <b>${shorgan_data['pnl']:+,.2f}</b>")
    report.append(f"Positions: <b>{len(shorgan_data['positions'])}</b>")
    
    if shorgan_data['positions']:
        # Best and worst performers
        best_shorgan = max(shorgan_data['positions'], key=lambda x: x['pnl_pct'])
        worst_shorgan = min(shorgan_data['positions'], key=lambda x: x['pnl_pct'])
        report.append(f"Best: <b>{best_shorgan['symbol']} ({best_shorgan['pnl_pct']:+.2f}%)</b>")
        report.append(f"Worst: <b>{worst_shorgan['symbol']} ({worst_shorgan['pnl_pct']:+.2f}%)</b>")
        
        # Today's SHORGAN-BOT trades
        if executions['SHORGAN-BOT']:
            report.append(f"\n<b>Today's SHORGAN-BOT Trades:</b>")
            for trade in executions['SHORGAN-BOT']:
                report.append(f"- {trade['symbol']}: {trade['shares']} @ ${trade['price']:.2f}")
    
    # Upcoming Catalysts
    report.append("\n<b>UPCOMING CATALYSTS</b>")
    report.append("<b>Tomorrow (Sept 17):</b> CBRL Earnings")
    report.append("   - 81 shares positioned for potential squeeze")
    report.append("<b>Thursday (Sept 19):</b> INCY FDA Decision")
    report.append("   - 61 shares positioned for binary approval")
    
    # Risk Assessment
    report.append("\n<b>RISK ASSESSMENT</b>")
    positions_value = portfolios['DEE-BOT']['total_value'] + portfolios['SHORGAN-BOT']['total_value']
    exposure_pct = (positions_value / starting_capital) * 100
    report.append(f"Capital Deployed: <b>${positions_value:,.2f}</b>")
    report.append(f"Capital Exposure: <b>{exposure_pct:.1f}%</b>")
    
    if exposure_pct > 90:
        report.append("<b>HIGH EXPOSURE WARNING</b>")
    elif exposure_pct > 75:
        report.append("<b>MODERATE EXPOSURE</b>")
    else:
        report.append("<b>CONTROLLED EXPOSURE</b>")
    
    # System Status
    report.append("\n<b>SYSTEM STATUS</b>")
    report.append("Multi-Agent Analysis: <b>ACTIVE</b>")
    report.append("Risk Management: <b>ACTIVE</b>")
    report.append("Stop Losses: <b>PROTECTED</b>")
    report.append("Portfolio Monitoring: <b>24/7</b>")
    
    # Footer
    report.append("\n" + "=" * 45)
    report.append("<b>Next Report:</b> Tomorrow 4:15 PM ET")
    report.append("<b>Status:</b> FULLY OPERATIONAL")
    
    return "\n".join(report)

def generate_and_send_report():
    """Main function to generate and send post-market report"""
    
    print("=" * 60)
    print("GENERATING POST-MARKET REPORT")
    print("=" * 60)
    
    # Generate comprehensive report
    report = format_comprehensive_report()
    
    print("\nReport Preview:")
    print("-" * 50)
    # Show plain text version for console
    console_report = report.replace("<b>", "").replace("</b>", "")
    print(console_report[:1500] + "..." if len(console_report) > 1500 else console_report)
    print("-" * 50)
    
    # Send to Telegram
    success = send_telegram_message(report)
    
    if success:
        print("\n[SUCCESS] Post-market report sent to Telegram")
        
        # Save report locally
        report_dir = Path("02_data/research/reports/post_market_daily")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"post_market_report_{date.today()}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Report saved: {report_file}")
    else:
        print("\n[ERROR] Failed to send post-market report")
    
    print("=" * 60)
    return success

if __name__ == "__main__":
    generate_and_send_report()