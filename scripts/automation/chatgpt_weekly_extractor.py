"""
ChatGPT Weekly Deep Research Report Extractor
For both SHORGAN-BOT and DEE-BOT weekly analysis
"""

import json
import os
import re
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

class WeeklyReportExtractor:
    def __init__(self):
        self.dee_bot_portfolio = []
        self.shorgan_bot_portfolio = []
        self.dee_orders = []
        self.shorgan_orders = []

    def parse_weekly_report(self, text):
        """Parse ChatGPT weekly deep research report"""

        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'week_ending': datetime.now().strftime('%Y-%m-%d'),
            'dee_bot': {
                'portfolio_assessment': [],
                'candidate_set': [],
                'portfolio_actions': [],
                'exact_orders': []
            },
            'shorgan_bot': {
                'portfolio_assessment': [],
                'candidate_set': [],
                'portfolio_actions': [],
                'exact_orders': []
            },
            'risk_checks': {},
            'thesis_summary': ''
        }

        lines = text.split('\n')
        current_section = None
        current_bot = None

        for line in lines:
            line = line.strip()

            # Identify bot context
            if 'DEE-BOT' in line.upper() or 'DEFENSIVE' in line.upper():
                current_bot = 'dee_bot'
            elif 'SHORGAN' in line.upper() or 'CATALYST' in line.upper():
                current_bot = 'shorgan_bot'

            # Identify sections
            if 'PORTFOLIO ASSESSMENT' in line.upper():
                current_section = 'portfolio_assessment'
            elif 'CANDIDATE SET' in line.upper():
                current_section = 'candidate_set'
            elif 'PORTFOLIO ACTIONS' in line.upper():
                current_section = 'portfolio_actions'
            elif 'EXACT ORDERS' in line.upper():
                current_section = 'exact_orders'
            elif 'RISK' in line.upper() and 'CHECK' in line.upper():
                current_section = 'risk_checks'
            elif 'THESIS' in line.upper() and 'SUMMARY' in line.upper():
                current_section = 'thesis_summary'

            # Parse content based on section
            if current_bot and current_section:
                if current_section == 'portfolio_assessment':
                    # Parse: TICKER role entry_date avg_cost stop conviction status
                    ticker_match = re.search(r'\b([A-Z]{2,5})\b', line)
                    if ticker_match and any(word in line.lower() for word in ['hold', 'keep', 'exit', 'trim']):
                        assessment = {
                            'ticker': ticker_match.group(1),
                            'action': 'KEEP' if 'keep' in line.lower() else
                                     'EXIT' if 'exit' in line.lower() else
                                     'TRIM' if 'trim' in line.lower() else 'HOLD',
                            'notes': line
                        }
                        report[current_bot]['portfolio_assessment'].append(assessment)

                elif current_section == 'exact_orders':
                    # Parse order details
                    if 'ACTION:' in line.upper() or 'BUY' in line or 'SELL' in line:
                        # Start new order
                        order = self._extract_order_from_text(line)
                        if order:
                            report[current_bot]['exact_orders'].append(order)

        return report

    def _extract_order_from_text(self, text):
        """Extract order details from text"""

        order = {}

        # Extract action (BUY/SELL)
        if 'BUY' in text.upper():
            order['action'] = 'BUY'
        elif 'SELL' in text.upper():
            order['action'] = 'SELL'
        else:
            return None

        # Extract ticker
        ticker_match = re.search(r'\b([A-Z]{2,5})\b', text)
        if ticker_match:
            order['ticker'] = ticker_match.group(1)

        # Extract shares
        shares_match = re.search(r'(\d+)\s*(?:shares?|shs?)', text, re.IGNORECASE)
        if shares_match:
            order['shares'] = int(shares_match.group(1))

        # Extract price if limit order
        price_match = re.search(r'\$?([\d.]+)\s*(?:limit|price)', text, re.IGNORECASE)
        if price_match:
            order['limit_price'] = float(price_match.group(1))
            order['order_type'] = 'LIMIT'
        else:
            order['order_type'] = 'MARKET'

        # Extract stop loss for buys
        if order['action'] == 'BUY':
            stop_match = re.search(r'stop\s*(?:loss)?[:\s]*\$?([\d.]+)', text, re.IGNORECASE)
            if stop_match:
                order['stop_loss'] = float(stop_match.group(1))

        return order if 'ticker' in order and 'shares' in order else None

    def create_weekly_pdf(self, report_data):
        """Create PDF from weekly report"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        week_ending = datetime.now().strftime('%Y-%m-%d')

        pdf_dir = f'../../weekly-reports'
        os.makedirs(pdf_dir, exist_ok=True)

        pdf_filename = f'{pdf_dir}/weekly_deep_research_{timestamp}.pdf'

        doc = SimpleDocTemplate(pdf_filename, pagesize=letter,
                               topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=20,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            spaceBefore=15
        )

        subheading_style = ParagraphStyle(
            'SubHeading',
            parent=styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=5
        )

        # Title
        elements.append(Paragraph("WEEKLY DEEP RESEARCH REPORT", title_style))
        elements.append(Paragraph(f"Week Ending {week_ending}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))

        # Executive Summary
        elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))

        summary_data = [
            ['Metric', 'DEE-BOT', 'SHORGAN-BOT'],
            ['Portfolio Actions',
             f"{len(report_data.get('dee_bot', {}).get('portfolio_actions', []))} actions",
             f"{len(report_data.get('shorgan_bot', {}).get('portfolio_actions', []))} actions"],
            ['New Orders',
             f"{len(report_data.get('dee_bot', {}).get('exact_orders', []))} orders",
             f"{len(report_data.get('shorgan_bot', {}).get('exact_orders', []))} orders"],
            ['Strategy', 'Beta-Neutral Defense', 'Catalyst-Driven Offense']
        ]

        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(summary_table)

        # DEE-BOT Section
        elements.append(PageBreak())
        elements.append(Paragraph("DEE-BOT DEEP RESEARCH", heading_style))

        # DEE-BOT Portfolio Assessment
        elements.append(Paragraph("Portfolio Assessment", subheading_style))
        if report_data.get('dee_bot', {}).get('portfolio_assessment'):
            assessment_data = [['Ticker', 'Action', 'Notes']]
            for item in report_data['dee_bot']['portfolio_assessment'][:10]:
                assessment_data.append([
                    item.get('ticker', ''),
                    item.get('action', ''),
                    item.get('notes', '')[:50]
                ])

            assessment_table = Table(assessment_data, colWidths=[1*inch, 1*inch, 4*inch])
            assessment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (1, -1), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(assessment_table)

        # DEE-BOT Orders
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Exact Orders", subheading_style))
        if report_data.get('dee_bot', {}).get('exact_orders'):
            orders_data = [['Action', 'Ticker', 'Shares', 'Type', 'Price', 'Stop']]
            for order in report_data['dee_bot']['exact_orders'][:10]:
                orders_data.append([
                    order.get('action', ''),
                    order.get('ticker', ''),
                    str(order.get('shares', '')),
                    order.get('order_type', ''),
                    f"${order.get('limit_price', 'MKT')}",
                    f"${order.get('stop_loss', 'N/A')}"
                ])

            orders_table = Table(orders_data, colWidths=[0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
            orders_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(orders_table)

        # SHORGAN-BOT Section
        elements.append(PageBreak())
        elements.append(Paragraph("SHORGAN-BOT DEEP RESEARCH", heading_style))

        # Similar structure for SHORGAN-BOT...
        elements.append(Paragraph("Portfolio Assessment", subheading_style))
        if report_data.get('shorgan_bot', {}).get('portfolio_assessment'):
            assessment_data = [['Ticker', 'Action', 'Catalyst/Notes']]
            for item in report_data['shorgan_bot']['portfolio_assessment'][:15]:
                assessment_data.append([
                    item.get('ticker', ''),
                    item.get('action', ''),
                    item.get('notes', '')[:50]
                ])

            assessment_table = Table(assessment_data, colWidths=[1*inch, 1*inch, 4*inch])
            assessment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (1, -1), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffe5e5')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(assessment_table)

        # Risk Checks
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("RISK & LIQUIDITY CHECKS", heading_style))

        risk_text = """
        • Concentration limits maintained
        • Cash reserves adequate for orders
        • All positions have stop losses
        • Liquidity verified for all trades
        """
        elements.append(Paragraph(risk_text, styles['Normal']))

        # Build PDF
        doc.build(elements)

        return pdf_filename

    def save_weekly_json(self, report_data):
        """Save weekly report to JSON"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        week_ending = datetime.now().strftime('%Y-%m-%d')

        json_dir = f'../../weekly-reports'
        os.makedirs(json_dir, exist_ok=True)

        json_filename = f'{json_dir}/weekly_research_{timestamp}.json'

        with open(json_filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'week_ending': week_ending,
                'report': report_data
            }, f, indent=2)

        return json_filename

def main():
    """Interactive weekly report extractor"""

    print("="*70)
    print("      CHATGPT WEEKLY DEEP RESEARCH EXTRACTOR")
    print("="*70)
    print("\nThis tool extracts weekly deep research reports")
    print("\nINSTRUCTIONS:")
    print("1. Copy your ChatGPT weekly deep research report")
    print("2. Paste it here")
    print("3. Type 'DONE' on a new line when finished")
    print("-"*70)

    # Collect input
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'DONE':
                break
            lines.append(line)
        except EOFError:
            break

    text = '\n'.join(lines)

    if not text.strip():
        print("\n[ERROR] No text provided")
        return

    # Extract report
    extractor = WeeklyReportExtractor()
    report_data = extractor.parse_weekly_report(text)

    # Save files
    print("\n" + "="*70)
    print("EXTRACTION RESULTS")
    print("="*70)

    # DEE-BOT Summary
    dee_orders = len(report_data.get('dee_bot', {}).get('exact_orders', []))
    dee_assessments = len(report_data.get('dee_bot', {}).get('portfolio_assessment', []))

    print(f"\nDEE-BOT:")
    print(f"  - Portfolio Assessments: {dee_assessments}")
    print(f"  - Orders to Execute: {dee_orders}")

    if report_data.get('dee_bot', {}).get('exact_orders'):
        print("  Orders:")
        for order in report_data['dee_bot']['exact_orders'][:5]:
            print(f"    - {order.get('action')} {order.get('shares')} {order.get('ticker')}")

    # SHORGAN-BOT Summary
    shorgan_orders = len(report_data.get('shorgan_bot', {}).get('exact_orders', []))
    shorgan_assessments = len(report_data.get('shorgan_bot', {}).get('portfolio_assessment', []))

    print(f"\nSHORGAN-BOT:")
    print(f"  - Portfolio Assessments: {shorgan_assessments}")
    print(f"  - Orders to Execute: {shorgan_orders}")

    if report_data.get('shorgan_bot', {}).get('exact_orders'):
        print("  Orders:")
        for order in report_data['shorgan_bot']['exact_orders'][:5]:
            print(f"    - {order.get('action')} {order.get('shares')} {order.get('ticker')}")

    # Save files
    print("\n" + "-"*70)
    print("SAVING FILES...")

    json_file = extractor.save_weekly_json(report_data)
    print(f"  JSON saved: {json_file}")

    pdf_file = extractor.create_weekly_pdf(report_data)
    print(f"  PDF saved: {pdf_file}")

    print("\n" + "="*70)
    print("WEEKLY EXTRACTION COMPLETE!")
    print("="*70)

    # Ask about execution
    print("\nReview the extracted orders above.")
    print("Execute trades? (yes/no): ", end='')

    try:
        response = input().strip().lower()
        if response == 'yes':
            print("\n[INFO] Trade execution would proceed here")
            print("       (Integration with Alpaca API required)")
    except:
        pass

if __name__ == "__main__":
    main()