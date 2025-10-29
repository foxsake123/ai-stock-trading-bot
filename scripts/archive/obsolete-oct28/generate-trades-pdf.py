"""
Generate PDF Report for ChatGPT Trades
"""

import json
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import requests
from dotenv import load_dotenv

load_dotenv()

def generate_trades_pdf():
    """Generate comprehensive PDF report of new trades"""
    
    # Load the report
    with open('02_data/research/reports/pre_market_daily/2025-09-16_chatgpt_full_report.json', 'r') as f:
        data = json.load(f)
    
    # Create PDF
    pdf_dir = '02_data/reports/trades'
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f'trades_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2e5090'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    elements.append(Paragraph("AI Trading Bot - Trade Recommendations", title_style))
    elements.append(Paragraph(f"September 16, 2025 - 5 Catalyst-Driven Trades", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Market Context
    elements.append(Paragraph("MARKET CONTEXT", heading_style))
    elements.append(Paragraph(data['market_context'], styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Trade Summary Table
    elements.append(Paragraph("TRADE SUMMARY", heading_style))
    
    summary_data = [
        ['Symbol', 'Catalyst', 'Size', 'Risk', 'Target', 'Confidence']
    ]
    
    for trade in data['trades']:
        summary_data.append([
            trade['symbol'],
            trade['catalyst'][:40] + '...' if len(trade['catalyst']) > 40 else trade['catalyst'],
            f"{trade['size_pct']}%",
            trade.get('risk_level', 'medium'),
            f"+{trade.get('target_pct', 20)}%",
            trade['confidence']
        ])
    
    summary_table = Table(summary_data, colWidths=[0.8*inch, 2.5*inch, 0.6*inch, 0.8*inch, 0.7*inch, 0.9*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7ba7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    elements.append(summary_table)
    elements.append(PageBreak())
    
    # Detailed Trade Analysis
    for i, trade in enumerate(data['trades'], 1):
        elements.append(Paragraph(f"TRADE #{i}: {trade['symbol']}", heading_style))
        
        # Trade details
        detail_data = [
            ['Parameter', 'Value'],
            ['Action', trade['action'].upper()],
            ['Catalyst', trade['catalyst']],
            ['Entry Trigger', trade.get('entry_trigger', 'Market order')],
            ['Stop Loss', f"-{trade['stop_pct']}%"],
            ['Target 1', f"+{trade.get('target_pct', 20)}%"],
            ['Target 2', f"+{trade.get('target2', trade.get('target_pct', 20) + 10)}%" if 'target2' in trade else 'N/A'],
            ['Position Size', f"{trade['size_pct']}% of portfolio"],
            ['Risk Level', trade.get('risk_level', 'medium').upper()],
            ['Confidence', trade['confidence'].upper()]
        ]
        
        if 'options_strategy' in trade:
            detail_data.append(['Options Strategy', trade['options_strategy']])
        if 'short_interest' in trade:
            detail_data.append(['Short Interest', f"{trade['short_interest']}%"])
        if 'insider_activity' in trade:
            detail_data.append(['Insider Activity', trade['insider_activity']])
        
        detail_table = Table(detail_data, colWidths=[2*inch, 4*inch])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        elements.append(detail_table)
        
        # Notes
        if 'note' in trade:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(f"<b>Notes:</b> {trade['note']}", styles['Normal']))
        
        # Profit taking
        if 'profit_taking' in trade:
            elements.append(Paragraph(f"<b>Profit Taking:</b> {trade['profit_taking']}", styles['Normal']))
        
        elements.append(Spacer(1, 0.3*inch))
    
    # Risk Management Section
    elements.append(PageBreak())
    elements.append(Paragraph("RISK MANAGEMENT", heading_style))
    
    risk_data = [
        ['Parameter', 'Value'],
        ['Max Position Size', f"{data['risk_management']['max_position_size_pct']}%"],
        ['Current Allocation', f"{data['risk_management']['current_allocation_pct']}%"],
        ['Max Portfolio Allocation', f"{data['risk_management']['max_portfolio_allocation_pct']}%"],
        ['Scale Out Level', f"+{data['risk_management']['profit_taking_rules']['scale_out_at_pct']}%"],
        ['Scale Out Amount', f"{data['risk_management']['profit_taking_rules']['scale_out_amount_pct']}%"],
        ['Portfolio Hedge', data['risk_management']['portfolio_hedge']]
    ]
    
    risk_table = Table(risk_data, colWidths=[3*inch, 3*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7ba7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(risk_table)
    
    # Portfolio Recommendations
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("PORTFOLIO ADJUSTMENTS", heading_style))
    
    recs = data['portfolio_recommendations']
    elements.append(Paragraph(f"<b>Keep:</b> {', '.join(recs['keep'])}", styles['Normal']))
    elements.append(Paragraph(f"<b>Trim:</b> {', '.join(recs['trim'])}", styles['Normal']))
    elements.append(Paragraph(f"<b>Add:</b> {', '.join(recs['add'])}", styles['Normal']))
    elements.append(Paragraph(f"<b>Drop:</b> {', '.join(recs['drop'])}", styles['Normal']))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("-" * 80, footer_style))
    elements.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    print(f"PDF generated: {pdf_path}")
    return pdf_path

def send_to_telegram(pdf_path):
    """Send PDF report to Telegram"""
    
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '-4524457329')
    
    if not telegram_token:
        print("No Telegram token found")
        return
    
    # Prepare message
    message = """📊 **New Trade Recommendations - Sep 16, 2025**

**5 Catalyst-Driven Trades:**
1. SRRK - FDA PDUFA Sept 22 (3% position)
2. INCY - FDA PDUFA Sept 19 (5% position)
3. CBRL - Earnings short squeeze Sept 17 (4% position)
4. PASG - Insider buying + clinical data (2% position)
5. RIVN - Q3 deliveries October (5% position)

**Total Allocation:** 19% of portfolio
**Risk Level:** Mixed (2 neutral, 2 risky, 1 very risky)

**Key Catalysts This Week:**
• Sept 17: CBRL earnings (34% short interest)
• Sept 19: INCY FDA decision
• Sept 22: SRRK FDA decision

Full analysis with multi-agent scores attached."""
    
    # Send text message
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        'chat_id': telegram_chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Text message sent to Telegram")
    
    # Send PDF
    url = f"https://api.telegram.org/bot{telegram_token}/sendDocument"
    with open(pdf_path, 'rb') as f:
        files = {'document': f}
        data = {
            'chat_id': telegram_chat_id,
            'caption': '📎 Complete trade analysis with entry/exit strategies'
        }
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("PDF sent to Telegram")

if __name__ == "__main__":
    pdf_path = generate_trades_pdf()
    send_to_telegram(pdf_path)
    print("\n✅ Report generated and sent!")