"""
Generate PDF Post-Market Report for Both Trading Bots
September 18, 2025
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import json
import os

def load_report_data():
    """Load the latest JSON report"""
    try:
        with open('../../daily-reports/post_market_report_20250918_183717.json', 'r') as f:
            return json.load(f)
    except:
        # If specific file not found, generate new data
        from generate_post_market_report import generate_report
        return generate_report()

def create_pdf_report(data):
    """Create PDF report from data"""

    # Create PDF filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_filename = f'../../daily-reports/2025-09-18/post_market_report_{timestamp}.pdf'

    # Ensure directory exists
    os.makedirs('../../daily-reports/2025-09-18', exist_ok=True)

    # Create the PDF document
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
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
        spaceAfter=12,
        spaceBefore=20
    )

    subheading_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=6
    )

    # Title
    elements.append(Paragraph("POST-MARKET REPORT", title_style))
    elements.append(Paragraph(datetime.now().strftime('%B %d, %Y - %I:%M %p ET'), styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # Combined Summary Box
    summary_data = [
        ['COMBINED PORTFOLIO SUMMARY', ''],
        ['Total Portfolio Value:', f"${data['combined']['total_portfolio']:,.2f}"],
        ['Total Unrealized P&L:', f"${data['combined']['total_unrealized_pnl']:,.2f}"],
        ['Total Positions:', str(data['combined']['total_positions'])],
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))

    # DEE-BOT Section
    if data.get('dee_bot'):
        elements.append(Paragraph("DEE-BOT (Beta-Neutral S&P 100 Strategy)", heading_style))

        dee_summary = [
            ['Portfolio Value:', f"${data['dee_bot']['portfolio_value']:,.2f}"],
            ['Cash Available:', f"${data['dee_bot']['cash']:,.2f}"],
            ['Positions:', str(len(data['dee_bot']['positions']))],
            ['Unrealized P&L:', f"${data['dee_bot']['total_unrealized_pnl']:,.2f}"],
        ]

        dee_table = Table(dee_summary, colWidths=[2*inch, 2*inch])
        dee_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(dee_table)
        elements.append(Spacer(1, 0.2*inch))

        # DEE-BOT Top Positions
        elements.append(Paragraph("Top Positions:", subheading_style))
        dee_positions = data['dee_bot']['positions']
        sorted_dee = sorted(dee_positions, key=lambda x: x['unrealized_pnl'], reverse=True)[:5]

        position_data = [['Symbol', 'Qty', 'Avg Price', 'Current', 'P&L', 'P&L %']]
        for pos in sorted_dee:
            position_data.append([
                pos['symbol'],
                str(pos['qty']),
                f"${pos['avg_price']:.2f}",
                f"${pos['current_price']:.2f}",
                f"${pos['unrealized_pnl']:,.2f}",
                f"{pos['unrealized_pnl_pct']:.1f}%"
            ])

        position_table = Table(position_data, colWidths=[0.8*inch, 0.6*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
        position_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(position_table)

    elements.append(PageBreak())

    # SHORGAN-BOT Section
    if data.get('shorgan_bot'):
        elements.append(Paragraph("SHORGAN-BOT (Catalyst-Driven Strategy)", heading_style))

        shorgan_summary = [
            ['Portfolio Value:', f"${data['shorgan_bot']['portfolio_value']:,.2f}"],
            ['Cash Available:', f"${data['shorgan_bot']['cash']:,.2f}"],
            ['Positions:', str(len(data['shorgan_bot']['positions']))],
            ['Unrealized P&L:', f"${data['shorgan_bot']['total_unrealized_pnl']:,.2f}"],
        ]

        shorgan_table = Table(shorgan_summary, colWidths=[2*inch, 2*inch])
        shorgan_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(shorgan_table)
        elements.append(Spacer(1, 0.2*inch))

        # SHORGAN-BOT Top Positions
        elements.append(Paragraph("Top Catalyst Positions:", subheading_style))
        shorgan_positions = data['shorgan_bot']['positions']
        sorted_shorgan = sorted(shorgan_positions, key=lambda x: x['unrealized_pnl'], reverse=True)[:8]

        position_data = [['Symbol', 'Qty', 'Avg Price', 'Current', 'P&L', 'P&L %']]
        for pos in sorted_shorgan:
            position_data.append([
                pos['symbol'],
                str(pos['qty']),
                f"${pos['avg_price']:.2f}",
                f"${pos['current_price']:.2f}",
                f"${pos['unrealized_pnl']:,.2f}",
                f"{pos['unrealized_pnl_pct']:.1f}%"
            ])

        position_table = Table(position_data, colWidths=[0.8*inch, 0.6*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
        position_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(position_table)

    # Tomorrow's Focus
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("TOMORROW'S FOCUS (September 19, 2025)", heading_style))

    critical_events = [
        ['CRITICAL EVENT', 'Details'],
        ['INCY FDA Decision', 'Binary Event - Opzelura Pediatric Approval'],
        ['Position:', '61 shares @ $83.97'],
        ['Stop Loss:', '$77.25'],
        ['KSS Stop Loss:', 'Active at $15.18'],
    ]

    critical_table = Table(critical_events, colWidths=[2*inch, 4*inch])
    critical_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffe5e5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(critical_table)

    # Build the PDF
    doc.build(elements)

    print(f"\n[SUCCESS] PDF report created: {pdf_filename}")
    return pdf_filename

if __name__ == "__main__":
    print("Generating PDF Post-Market Report...")
    data = load_report_data()

    if data:
        pdf_file = create_pdf_report(data)
        print(f"Report saved to: {pdf_file}")

        # Optionally open the PDF
        import os
        os.startfile(pdf_file.replace('../../', ''))
    else:
        print("[ERROR] Could not load report data")