"""
Generate PDF from ChatGPT Premarket Report
"""

import json
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_premarket_pdf():
    # Load JSON report
    report_file = '02_data/research/reports/pre_market_daily/2025-09-16_chatgpt_report.json'
    with open(report_file, 'r') as f:
        report = json.load(f)
    
    # Create PDF
    pdf_file = f"07_docs/premarket_reports/premarket_{report['date']}.pdf"
    os.makedirs(os.path.dirname(pdf_file), exist_ok=True)
    
    doc = SimpleDocTemplate(pdf_file, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10
    )
    
    # Title
    elements.append(Paragraph('SHORGAN-BOT Premarket Trading Plan', title_style))
    elements.append(Paragraph(f"Monday, September 16, 2025", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Market Context
    elements.append(Paragraph('Market Context', heading_style))
    elements.append(Paragraph(report['market_context'], styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Trading Opportunities
    elements.append(Paragraph('Primary Trade: MFIC', heading_style))
    
    trade = report['trades'][0]
    trade_data = [
        ['Symbol', 'MFIC'],
        ['Action', 'Long Equity'],
        ['Catalyst', trade['catalyst']],
        ['Entry', trade['entry_trigger']],
        ['Stop Loss', f"{trade['stop_pct']}% below entry"],
        ['Target 1', f"+{trade['target']}%"],
        ['Target 2', f"+{trade['target2']}%"],
        ['Position Size', f"{trade['size_pct']}% of portfolio"],
        ['Options', trade['options_strategy']],
        ['Profit Taking', trade['profit_taking']]
    ]
    
    trade_table = Table(trade_data, colWidths=[2*inch, 4*inch])
    trade_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.beige])
    ]))
    
    elements.append(trade_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Watchlist
    elements.append(Paragraph('Additional Opportunities', heading_style))
    
    watchlist_data = [
        ['Category', 'Size %', 'Stop %', 'Target', 'Notes']
    ]
    
    for item in report['watchlist']:
        watchlist_data.append([
            item['category'],
            str(item['size_pct']) + '%',
            str(item['stop_pct']) + '%',
            str(item['target']),
            item['note'][:40] + '...' if len(item['note']) > 40 else item['note']
        ])
    
    watchlist_table = Table(watchlist_data, colWidths=[1.5*inch, 0.8*inch, 0.8*inch, 1.2*inch, 2.2*inch])
    watchlist_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.beige])
    ]))
    
    elements.append(watchlist_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Risk Management
    elements.append(Paragraph('Risk Management Rules', heading_style))
    
    risk_text = f"""
    • Maximum position size: {report['risk_management']['max_position_size_pct']}% of portfolio
    • High-risk trades: {report['risk_management']['catalyst_high_risk_size_pct']}% only
    • Options maximum loss: {report['risk_management']['options_max_loss_pct']}% per trade
    • Portfolio hedge: {report['risk_management']['portfolio_hedge']}
    • Stop losses are mandatory for all positions
    • Move to breakeven at +{report['risk_management']['profit_taking_rules']['move_to_breakeven_at_pct']}%
    • Trailing stops: {report['risk_management']['profit_taking_rules']['trailing_stop_volatile_pct']}% (volatile) / {report['risk_management']['profit_taking_rules']['trailing_stop_stable_pct']}% (stable)
    """
    
    elements.append(Paragraph(risk_text, styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Portfolio Adjustments
    elements.append(Paragraph('Portfolio Adjustments Required', heading_style))
    
    adjustments = '<br/>'.join([f"• {adj}" for adj in report['portfolio_adjustments']])
    elements.append(Paragraph(adjustments, styles['Normal']))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph(f"Market Sentiment: {report['market_sentiment']}", footer_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M ET')}", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    print(f"[SUCCESS] PDF saved to: {pdf_file}")
    return pdf_file

if __name__ == "__main__":
    generate_premarket_pdf()