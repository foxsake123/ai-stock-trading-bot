"""
Generate PDF from ChatGPT Research Report
"""

import json
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_chatgpt_pdf():
    """Generate PDF from ChatGPT JSON report"""
    
    # Load the JSON report
    json_path = '02_data/research/reports/pre_market_daily/2025-09-16_chatgpt_report.json'
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Create PDF
    pdf_dir = '02_data/research/reports/pre_market_daily'
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, '2025-09-16_chatgpt_report.pdf')
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
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
        fontSize=18,
        textColor=colors.HexColor('#2e5090'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#3a619c'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceAfter=8
    )
    
    # Title
    elements.append(Paragraph("ChatGPT TradingAgents Research Report", title_style))
    elements.append(Paragraph(f"Monday, September 16, 2025 - Pre-Market Analysis", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Market Context
    elements.append(Paragraph("MARKET CONTEXT", heading_style))
    elements.append(Paragraph(data['market_context'], body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Market Sentiment
    sentiment_color = colors.green if 'BULLISH' in data['market_sentiment'] else colors.red
    sentiment_style = ParagraphStyle(
        'Sentiment',
        parent=body_style,
        fontSize=14,
        textColor=sentiment_color,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Market Sentiment: {data['market_sentiment']}", sentiment_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Primary Trade Recommendation
    elements.append(Paragraph("PRIMARY TRADE RECOMMENDATION", heading_style))
    
    trade = data['trades'][0]
    
    # Trade Summary Box
    trade_data = [
        ['Symbol', 'MFIC'],
        ['Action', 'LONG'],
        ['Position Size', f"{trade['size_pct']}% of portfolio"],
        ['Entry', trade['entry_trigger']],
        ['Stop Loss', f"{trade['stop_pct']}% below entry"],
        ['Target 1', f"+{trade['target']}%"],
        ['Target 2', f"+{trade['target2']}%"],
        ['Confidence', trade['confidence'].upper()]
    ]
    
    trade_table = Table(trade_data, colWidths=[2*inch, 4*inch])
    trade_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4788')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d0d0d0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
    ]))
    elements.append(trade_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Catalyst
    elements.append(Paragraph("<b>Catalyst:</b>", subheading_style))
    elements.append(Paragraph(trade['catalyst'], body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Options Strategy
    elements.append(Paragraph("<b>Options Strategy:</b>", subheading_style))
    elements.append(Paragraph(trade['options_strategy'], body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Profit Taking Rules
    elements.append(Paragraph("<b>Profit Taking:</b>", subheading_style))
    elements.append(Paragraph(trade['profit_taking'], body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Watchlist
    elements.append(Paragraph("WATCHLIST CATEGORIES", heading_style))
    
    watchlist_data = [['Category', 'Catalyst', 'Size', 'Stop', 'Target', 'Confidence']]
    for item in data['watchlist']:
        watchlist_data.append([
            item['category'],
            item['catalyst'],
            f"{item['size_pct']}%",
            f"{item['stop_pct']}%",
            str(item['target']),
            item['confidence']
        ])
    
    watchlist_table = Table(watchlist_data, colWidths=[1.5*inch, 2.5*inch, 0.6*inch, 0.6*inch, 0.8*inch, 0.8*inch])
    watchlist_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7ba7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
    ]))
    elements.append(watchlist_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Risk Management
    elements.append(Paragraph("RISK MANAGEMENT PARAMETERS", heading_style))
    
    risk = data['risk_management']
    risk_data = [
        ['Parameter', 'Value'],
        ['Maximum Position Size', f"{risk['max_position_size_pct']}%"],
        ['High-Risk Catalyst Size', f"{risk['catalyst_high_risk_size_pct']}%"],
        ['Options Max Loss', f"{risk['options_max_loss_pct']}%"],
        ['Portfolio Hedge', risk['portfolio_hedge']],
        ['Move Stop to B/E', f"At +{risk['profit_taking_rules']['move_to_breakeven_at_pct']}%"],
        ['Trailing Stop (Volatile)', f"{risk['profit_taking_rules']['trailing_stop_volatile_pct']}%"],
        ['Trailing Stop (Stable)', f"{risk['profit_taking_rules']['trailing_stop_stable_pct']}%"]
    ]
    
    risk_table = Table(risk_data, colWidths=[3*inch, 3*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7ba7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
    ]))
    elements.append(risk_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Portfolio Adjustments
    elements.append(Paragraph("PORTFOLIO ADJUSTMENTS", heading_style))
    for adjustment in data['portfolio_adjustments']:
        elements.append(Paragraph(f"• {adjustment}", body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Execution Notes
    elements.append(Paragraph("EXECUTION NOTES", heading_style))
    for note in data['execution_notes']:
        elements.append(Paragraph(f"• {note}", body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("─" * 80, footer_style))
    elements.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}", footer_style))
    elements.append(Paragraph("ChatGPT TradingAgents - SHORGAN-BOT Strategy", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    print(f"PDF generated successfully: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    pdf_path = generate_chatgpt_pdf()
    print(f"\nChatGPT Research Report PDF created at:")
    print(f"{os.path.abspath(pdf_path)}")