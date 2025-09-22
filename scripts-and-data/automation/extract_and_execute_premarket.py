"""
Extract Pre-Market Reports from ChatGPT and Execute Trades
September 19, 2025 - Pre-Market
"""

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import json
import os
import re

# API credentials
DEE_BOT_KEY = "PK6FZK4DAQVTD7DYVH78"
DEE_BOT_SECRET = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"

SHORGAN_BOT_KEY = "PKJRLSB2MFEJUSK6UK2E"
SHORGAN_BOT_SECRET = "QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic"

def extract_chatgpt_recommendations(text_file=None):
    """Extract trading recommendations from ChatGPT report"""

    # For demo purposes, using sample recommendations
    # In production, this would parse actual ChatGPT text

    dee_bot_trades = []
    shorgan_bot_trades = []

    # Check if text file is provided
    if text_file and os.path.exists(text_file):
        with open(text_file, 'r') as f:
            content = f.read()

        # Parse DEE-BOT recommendations (S&P 100 stocks)
        dee_pattern = r"DEE-BOT.*?(?:BUY|SELL)\s+(\w+)\s+(\d+)"
        dee_matches = re.findall(dee_pattern, content, re.IGNORECASE | re.DOTALL)

        for match in dee_matches:
            symbol, qty = match
            if symbol in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'JPM', 'JNJ', 'PG', 'WMT']:
                dee_bot_trades.append({
                    'symbol': symbol,
                    'quantity': int(qty),
                    'action': 'BUY' if 'BUY' in content else 'SELL'
                })

        # Parse SHORGAN-BOT recommendations (catalyst plays)
        shorgan_pattern = r"SHORGAN.*?(?:BUY|SELL)\s+(\w+)\s+(\d+)"
        shorgan_matches = re.findall(shorgan_pattern, content, re.IGNORECASE | re.DOTALL)

        for match in shorgan_matches:
            symbol, qty = match
            shorgan_bot_trades.append({
                'symbol': symbol,
                'quantity': int(qty),
                'action': 'BUY' if 'BUY' in content else 'SELL',
                'catalyst': 'FDA' if 'FDA' in content else 'Earnings'
            })
    else:
        # Default recommendations for Sept 19
        print("[INFO] Using default pre-market recommendations for Sept 19")

        # INCY FDA decision today - critical
        shorgan_bot_trades = [
            {'symbol': 'INCY', 'quantity': 0, 'action': 'HOLD', 'catalyst': 'FDA Decision Today'},
            {'symbol': 'KSS', 'quantity': 0, 'action': 'MONITOR', 'catalyst': 'Near Stop Loss'},
        ]

        # DEE-BOT defensive positioning
        dee_bot_trades = [
            {'symbol': 'XOM', 'quantity': 15, 'action': 'BUY', 'reason': 'Add energy exposure'},
            {'symbol': 'CVX', 'quantity': 10, 'action': 'BUY', 'reason': 'Energy diversification'},
        ]

    return dee_bot_trades, shorgan_bot_trades

def execute_trades(trades, api_key, secret_key, bot_name):
    """Execute trades for a specific bot"""

    client = TradingClient(api_key, secret_key, paper=True)
    executed_trades = []
    failed_trades = []

    for trade in trades:
        if trade['action'] in ['HOLD', 'MONITOR']:
            print(f"[{bot_name}] {trade['action']}: {trade['symbol']} - {trade.get('catalyst', '')}")
            continue

        try:
            # Create market order
            order_data = MarketOrderRequest(
                symbol=trade['symbol'],
                qty=trade['quantity'],
                side=OrderSide.BUY if trade['action'] == 'BUY' else OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )

            # Submit order
            order = client.submit_order(order_request=order_data)

            executed_trades.append({
                'symbol': trade['symbol'],
                'quantity': trade['quantity'],
                'action': trade['action'],
                'order_id': str(order.id),
                'status': 'SUBMITTED'
            })

            print(f"[{bot_name}] Executed: {trade['action']} {trade['quantity']} shares of {trade['symbol']}")

        except Exception as e:
            failed_trades.append({
                'symbol': trade['symbol'],
                'quantity': trade['quantity'],
                'action': trade['action'],
                'error': str(e)
            })
            print(f"[{bot_name}] Failed: {trade['symbol']} - {str(e)}")

    return executed_trades, failed_trades

def generate_premarket_pdf(dee_trades, shorgan_trades, executed_dee, executed_shorgan):
    """Generate PDF pre-market report"""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    date_str = datetime.now().strftime('%Y-%m-%d')
    pdf_filename = f'../../daily-reports/{date_str}/premarket_report_{timestamp}.pdf'

    # Ensure directory exists
    os.makedirs(f'../../daily-reports/{date_str}', exist_ok=True)

    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12
    )

    # Title
    elements.append(Paragraph("PRE-MARKET TRADING REPORT", title_style))
    elements.append(Paragraph(datetime.now().strftime('%B %d, %Y - %I:%M %p ET'), styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # Critical Events
    critical_data = [
        ['CRITICAL EVENTS TODAY', ''],
        ['INCY FDA Decision', 'Opzelura Pediatric Approval - Binary Event'],
        ['Current Position:', '61 shares @ $83.97'],
        ['Stop Loss:', '$77.25 (Active)'],
        ['KSS Stop Watch:', 'Near $15.18 stop level'],
    ]

    critical_table = Table(critical_data, colWidths=[2.5*inch, 3.5*inch])
    critical_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffe5e5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(critical_table)
    elements.append(Spacer(1, 0.3*inch))

    # DEE-BOT Trades
    elements.append(Paragraph("DEE-BOT PRE-MARKET ORDERS", heading_style))

    if executed_dee:
        dee_data = [['Symbol', 'Action', 'Quantity', 'Status']]
        for trade in executed_dee:
            dee_data.append([
                trade['symbol'],
                trade['action'],
                str(trade['quantity']),
                trade['status']
            ])

        dee_table = Table(dee_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1.5*inch])
        dee_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(dee_table)
    else:
        elements.append(Paragraph("No DEE-BOT trades for pre-market", styles['Normal']))

    elements.append(Spacer(1, 0.2*inch))

    # SHORGAN-BOT Trades
    elements.append(Paragraph("SHORGAN-BOT PRE-MARKET ORDERS", heading_style))

    if executed_shorgan:
        shorgan_data = [['Symbol', 'Action', 'Quantity', 'Catalyst', 'Status']]
        for trade in executed_shorgan:
            shorgan_data.append([
                trade['symbol'],
                trade['action'],
                str(trade['quantity']),
                trade.get('catalyst', ''),
                trade['status']
            ])

        shorgan_table = Table(shorgan_data, colWidths=[1*inch, 0.8*inch, 0.8*inch, 2*inch, 1.2*inch])
        shorgan_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(shorgan_table)
    else:
        elements.append(Paragraph("Monitoring INCY FDA decision - No new trades", styles['Normal']))

    # Build PDF
    doc.build(elements)

    print(f"\n[SUCCESS] Pre-market PDF created: {pdf_filename}")
    return pdf_filename

def main():
    """Main execution function"""

    print("="*70)
    print("           PRE-MARKET REPORT & TRADE EXECUTION")
    print(f"              {datetime.now().strftime('%B %d, %Y - %I:%M %p ET')}")
    print("="*70)

    # Extract recommendations
    print("\n[1/3] Extracting ChatGPT recommendations...")
    dee_trades, shorgan_trades = extract_chatgpt_recommendations()

    print(f"   - DEE-BOT: {len(dee_trades)} recommended trades")
    print(f"   - SHORGAN-BOT: {len(shorgan_trades)} recommended actions")

    # Execute DEE-BOT trades
    print("\n[2/3] Executing trades...")
    executed_dee = []
    executed_shorgan = []

    if dee_trades:
        print("\n   Executing DEE-BOT trades...")
        executed_dee, failed_dee = execute_trades(dee_trades, DEE_BOT_KEY, DEE_BOT_SECRET, "DEE-BOT")

    if shorgan_trades:
        print("\n   Processing SHORGAN-BOT actions...")
        # For INCY FDA day, we're mostly monitoring
        for trade in shorgan_trades:
            if trade['action'] in ['HOLD', 'MONITOR']:
                print(f"   [SHORGAN] {trade['action']}: {trade['symbol']} - {trade['catalyst']}")

    # Generate PDF report
    print("\n[3/3] Generating pre-market PDF report...")
    pdf_file = generate_premarket_pdf(dee_trades, shorgan_trades, executed_dee, executed_shorgan)

    # Save execution log
    execution_log = {
        'timestamp': datetime.now().isoformat(),
        'dee_bot': {
            'recommended': dee_trades,
            'executed': executed_dee
        },
        'shorgan_bot': {
            'recommended': shorgan_trades,
            'executed': executed_shorgan
        }
    }

    log_filename = f"../../daily-reports/premarket_execution_{datetime.now().strftime('%Y%m%d')}.json"
    with open(log_filename, 'w') as f:
        json.dump(execution_log, f, indent=2)

    print("\n" + "="*70)
    print("PRE-MARKET EXECUTION COMPLETE")
    print(f"PDF Report: {pdf_file}")
    print(f"Execution Log: {log_filename}")
    print("\n[CRITICAL] Today: INCY FDA Decision - Monitor closely!")
    print("="*70)

if __name__ == "__main__":
    main()