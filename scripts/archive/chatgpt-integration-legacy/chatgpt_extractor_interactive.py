"""
Interactive ChatGPT Report Extractor and PDF Generator
For both pre-market and post-market reports
"""

import json
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

def get_chatgpt_input():
    """Get ChatGPT report from user input"""
    print("="*70)
    print("         CHATGPT REPORT EXTRACTOR")
    print("="*70)
    print("\nINSTRUCTIONS:")
    print("1. Copy your ChatGPT pre-market recommendations")
    print("2. Paste them here")
    print("3. Type 'END' on a new line when done")
    print("-"*70)
    print()

    lines = []
    while True:
        line = input()
        if line.strip().upper() == 'END':
            break
        lines.append(line)

    return '\n'.join(lines)

def parse_recommendations(text):
    """Parse the pasted text for trade recommendations"""

    dee_trades = []
    shorgan_trades = []

    lines = text.split('\n')
    current_bot = None

    for line in lines:
        # Identify which bot section we're in
        if 'DEE-BOT' in line.upper() or 'DEE BOT' in line.upper():
            current_bot = 'dee'
        elif 'SHORGAN' in line.upper():
            current_bot = 'shorgan'

        # Parse trade lines
        if current_bot:
            # Look for BUY/SELL patterns
            if 'BUY' in line.upper():
                parts = line.upper().split('BUY')
                if len(parts) > 1:
                    # Extract symbol and quantity
                    trade_part = parts[1].strip()
                    words = trade_part.split()
                    if len(words) >= 2:
                        symbol = words[0]
                        try:
                            qty = int(''.join(filter(str.isdigit, words[1])))
                            trade = {
                                'action': 'BUY',
                                'symbol': symbol,
                                'quantity': qty,
                                'notes': ' '.join(words[2:]) if len(words) > 2 else ''
                            }
                            if current_bot == 'dee':
                                dee_trades.append(trade)
                            else:
                                shorgan_trades.append(trade)
                        except:
                            pass

            elif 'SELL' in line.upper():
                parts = line.upper().split('SELL')
                if len(parts) > 1:
                    trade_part = parts[1].strip()
                    words = trade_part.split()
                    if len(words) >= 2:
                        symbol = words[0]
                        try:
                            qty = int(''.join(filter(str.isdigit, words[1])))
                            trade = {
                                'action': 'SELL',
                                'symbol': symbol,
                                'quantity': qty,
                                'notes': ' '.join(words[2:]) if len(words) > 2 else ''
                            }
                            if current_bot == 'dee':
                                dee_trades.append(trade)
                            else:
                                shorgan_trades.append(trade)
                        except:
                            pass

    return dee_trades, shorgan_trades

def create_pdf_report(dee_trades, shorgan_trades):
    """Create PDF report from extracted trades"""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    date_str = datetime.now().strftime('%Y-%m-%d')

    # Create directory
    pdf_dir = f'../../daily-reports/{date_str}'
    os.makedirs(pdf_dir, exist_ok=True)

    pdf_filename = f'{pdf_dir}/chatgpt_extracted_{timestamp}.pdf'

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
    elements.append(Paragraph("CHATGPT TRADING RECOMMENDATIONS", title_style))
    elements.append(Paragraph(datetime.now().strftime('%B %d, %Y - %I:%M %p ET'), styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # DEE-BOT Section
    elements.append(Paragraph("DEE-BOT TRADES (Beta-Neutral S&P 100)", heading_style))

    if dee_trades:
        dee_data = [['Action', 'Symbol', 'Quantity', 'Notes']]
        for trade in dee_trades:
            dee_data.append([
                trade['action'],
                trade['symbol'],
                str(trade['quantity']),
                trade.get('notes', '')[:30]
            ])

        dee_table = Table(dee_data, colWidths=[1*inch, 1*inch, 1*inch, 2.5*inch])
        dee_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (3, 0), (3, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(dee_table)
    else:
        elements.append(Paragraph("No DEE-BOT trades extracted", styles['Normal']))

    elements.append(Spacer(1, 0.3*inch))

    # SHORGAN-BOT Section
    elements.append(Paragraph("SHORGAN-BOT TRADES (Catalyst-Driven)", heading_style))

    if shorgan_trades:
        shorgan_data = [['Action', 'Symbol', 'Quantity', 'Notes']]
        for trade in shorgan_trades:
            shorgan_data.append([
                trade['action'],
                trade['symbol'],
                str(trade['quantity']),
                trade.get('notes', '')[:30]
            ])

        shorgan_table = Table(shorgan_data, colWidths=[1*inch, 1*inch, 1*inch, 2.5*inch])
        shorgan_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (3, 0), (3, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffe5e5')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(shorgan_table)
    else:
        elements.append(Paragraph("No SHORGAN-BOT trades extracted", styles['Normal']))

    # Summary
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("SUMMARY", heading_style))

    summary_data = [
        ['Bot', 'Total Trades', 'Buy Orders', 'Sell Orders'],
        ['DEE-BOT', str(len(dee_trades)),
         str(sum(1 for t in dee_trades if t['action'] == 'BUY')),
         str(sum(1 for t in dee_trades if t['action'] == 'SELL'))],
        ['SHORGAN-BOT', str(len(shorgan_trades)),
         str(sum(1 for t in shorgan_trades if t['action'] == 'BUY')),
         str(sum(1 for t in shorgan_trades if t['action'] == 'SELL'))],
    ]

    summary_table = Table(summary_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(summary_table)

    # Build PDF
    doc.build(elements)

    return pdf_filename

def save_to_json(dee_trades, shorgan_trades):
    """Save extracted trades to JSON"""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    date_str = datetime.now().strftime('%Y-%m-%d')

    json_dir = f'../../daily-reports/{date_str}'
    os.makedirs(json_dir, exist_ok=True)

    json_filename = f'{json_dir}/chatgpt_trades_{timestamp}.json'

    data = {
        'timestamp': datetime.now().isoformat(),
        'dee_bot': dee_trades,
        'shorgan_bot': shorgan_trades,
        'total_trades': len(dee_trades) + len(shorgan_trades)
    }

    with open(json_filename, 'w') as f:
        json.dump(data, f, indent=2)

    return json_filename

def main():
    """Main execution"""

    # Get input from user
    text = get_chatgpt_input()

    if not text.strip():
        print("\nNo text provided")
        return

    # Parse the text
    print("\n" + "="*70)
    print("EXTRACTING TRADES...")
    dee_trades, shorgan_trades = parse_recommendations(text)

    print(f"\nExtracted:")
    print(f"  DEE-BOT: {len(dee_trades)} trades")
    for trade in dee_trades:
        print(f"    - {trade['action']} {trade['quantity']} {trade['symbol']}")

    print(f"\n  SHORGAN-BOT: {len(shorgan_trades)} trades")
    for trade in shorgan_trades:
        print(f"    - {trade['action']} {trade['quantity']} {trade['symbol']}")

    # Save to JSON
    print("\n" + "-"*70)
    print("SAVING FILES...")
    json_file = save_to_json(dee_trades, shorgan_trades)
    print(f"  JSON saved: {json_file}")

    # Create PDF
    pdf_file = create_pdf_report(dee_trades, shorgan_trades)
    print(f"  PDF saved: {pdf_file}")

    print("\n" + "="*70)
    print("EXTRACTION COMPLETE!")
    print("="*70)

    # Ask if user wants to execute trades
    print("\nDo you want to execute these trades? (yes/no): ", end='')
    if input().strip().lower() == 'yes':
        print("\n[NOTE] Trade execution would happen here")
        print("       Integration with Alpaca API required")

if __name__ == "__main__":
    main()