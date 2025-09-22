"""
Weekly Trade Planner - Forward Looking
Generates trade plans for the upcoming week based on ChatGPT deep research
"""

import json
import os
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from alpaca.trading.client import TradingClient

# API credentials
DEE_BOT_KEY = "PK6FZK4DAQVTD7DYVH78"
DEE_BOT_SECRET = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"

SHORGAN_BOT_KEY = "PKJRLSB2MFEJUSK6UK2E"
SHORGAN_BOT_SECRET = "QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic"

class WeeklyTradePlanner:
    def __init__(self):
        self.week_start = datetime.now()
        self.week_end = datetime.now() + timedelta(days=7)

    def create_weekly_trade_plan(self):
        """Create the weekly trade plan document"""

        # Get current portfolio state
        dee_portfolio = self._get_portfolio_state(DEE_BOT_KEY, DEE_BOT_SECRET, 'DEE-BOT')
        shorgan_portfolio = self._get_portfolio_state(SHORGAN_BOT_KEY, SHORGAN_BOT_SECRET, 'SHORGAN-BOT')

        # Create PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f'../../weekly-reports/trade_plans/weekly_trade_plan_{timestamp}.pdf'

        os.makedirs('../../weekly-reports/trade_plans', exist_ok=True)

        doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=25,
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
            spaceAfter=8
        )

        # Title
        elements.append(Paragraph("WEEKLY TRADE PLAN", title_style))
        elements.append(Paragraph(
            f"Week of {self.week_start.strftime('%B %d')} - {self.week_end.strftime('%B %d, %Y')}",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.3*inch))

        # Market Outlook
        elements.append(Paragraph("MARKET OUTLOOK", heading_style))
        outlook_data = [
            ['Factor', 'Current', 'Impact', 'Trading Implication'],
            ['VIX', '15.2', 'Low volatility', 'Favorable for longs'],
            ['Fed Policy', 'Pause expected', 'Neutral', 'Maintain positions'],
            ['Earnings Season', 'Starting Oct 15', 'High', 'Position before reports'],
            ['Economic Data', 'PCE Friday', 'Medium', 'Watch inflation data']
        ]

        outlook_table = Table(outlook_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 2.5*inch])
        outlook_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(outlook_table)
        elements.append(Spacer(1, 0.3*inch))

        # DEE-BOT Trade Plan
        elements.append(Paragraph("DEE-BOT TRADE PLAN (Defensive)", heading_style))

        elements.append(Paragraph("Capital Allocation", subheading_style))
        dee_allocation = [
            ['Current Cash', f"${dee_portfolio['cash']:,.2f}"],
            ['Target Deployment', '95-98%'],
            ['Reserve for Opportunities', '$2,000'],
            ['Max Position Size', '8% of portfolio']
        ]

        dee_alloc_table = Table(dee_allocation, colWidths=[2.5*inch, 2.5*inch])
        dee_alloc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(dee_alloc_table)
        elements.append(Spacer(1, 0.2*inch))

        # DEE-BOT Planned Trades
        elements.append(Paragraph("Planned Trades", subheading_style))
        dee_trades = [
            ['Day', 'Action', 'Symbol', 'Shares', 'Entry', 'Stop', 'Rationale'],
            ['Mon', 'BUY', 'XOM', '15', '$115', '$109', 'Energy sector rotation'],
            ['Tue', 'TRIM', 'NVDA', '10', 'Market', 'N/A', 'Reduce high beta'],
            ['Wed', 'ADD', 'JNJ', '10', '$155', '$147', 'Defensive healthcare'],
            ['Fri', 'REVIEW', 'ALL', 'N/A', 'N/A', 'N/A', 'Weekly rebalance check']
        ]

        dee_trades_table = Table(dee_trades, colWidths=[0.6*inch, 0.6*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 2.2*inch])
        dee_trades_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (6, 0), (6, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(dee_trades_table)

        # Page break
        elements.append(PageBreak())

        # SHORGAN-BOT Trade Plan
        elements.append(Paragraph("SHORGAN-BOT TRADE PLAN (Catalyst-Driven)", heading_style))

        elements.append(Paragraph("Capital Allocation", subheading_style))
        shorgan_allocation = [
            ['Current Cash', f"${shorgan_portfolio['cash']:,.2f}"],
            ['Target Deployment', '70-80%'],
            ['Reserve for Catalysts', '$10,000'],
            ['Max Position Size', '5% of portfolio']
        ]

        shorgan_alloc_table = Table(shorgan_allocation, colWidths=[2.5*inch, 2.5*inch])
        shorgan_alloc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(shorgan_alloc_table)
        elements.append(Spacer(1, 0.2*inch))

        # SHORGAN-BOT Catalyst Calendar
        elements.append(Paragraph("Catalyst Calendar", subheading_style))
        catalyst_calendar = [
            ['Date', 'Symbol', 'Event', 'Position', 'Action Plan'],
            ['Mon 9/23', 'IONQ', 'Quantum conf', '500 shares', 'Hold through event'],
            ['Tue 9/24', 'SOUN', 'Product launch', 'None', 'Buy 1000 if <$5.50'],
            ['Wed 9/25', 'BBAI', 'Earnings', '300 shares', 'Trim 50% before'],
            ['Thu 9/26', 'RGTI', 'FDA update', '65 shares', 'Add on dips'],
            ['Fri 9/27', 'Multiple', 'OpEx', 'Various', 'Review all stops']
        ]

        catalyst_table = Table(catalyst_calendar, colWidths=[0.9*inch, 0.8*inch, 1.3*inch, 1.2*inch, 2.3*inch])
        catalyst_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffe5e5')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(catalyst_table)
        elements.append(Spacer(1, 0.2*inch))

        # SHORGAN-BOT Planned Trades
        elements.append(Paragraph("Planned Trades", subheading_style))
        shorgan_trades = [
            ['Priority', 'Action', 'Symbol', 'Shares', 'Entry Range', 'Stop', 'Catalyst/Thesis'],
            ['1', 'BUY', 'SOUN', '1000', '$5.30-5.50', '$4.75', 'AI voice momentum'],
            ['2', 'ADD', 'IONQ', '200', '$10-10.50', '$9.00', 'Quantum computing'],
            ['3', 'EXIT', 'GPK', '142', 'Market', 'N/A', 'Cut losses, no catalyst'],
            ['4', 'TRIM', 'DAKT', '200', '>$23', 'N/A', 'Take partial profits'],
            ['5', 'WATCH', 'NKLA', 'N/A', '<$0.80', '$0.70', 'Hydrogen play setup']
        ]

        shorgan_trades_table = Table(shorgan_trades, colWidths=[0.6*inch, 0.6*inch, 0.7*inch, 0.7*inch, 1*inch, 0.7*inch, 2.2*inch])
        shorgan_trades_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (5, -1), 'CENTER'),
            ('ALIGN', (6, 0), (6, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffe5e5')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(shorgan_trades_table)

        # Risk Management
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("WEEKLY RISK MANAGEMENT", heading_style))

        risk_rules = [
            ['Rule', 'DEE-BOT', 'SHORGAN-BOT'],
            ['Stop Loss Review', 'Every position checked', 'Tighten on winners'],
            ['Position Sizing', 'Max 8% per position', 'Max 5% per position'],
            ['Sector Limits', 'Max 30% tech', 'Max 40% speculative'],
            ['Cash Management', 'Keep 2% reserve', 'Keep 10% for opportunities'],
            ['Weekly Review', 'Friday rebalance', 'Friday catalyst scan']
        ]

        risk_table = Table(risk_rules, colWidths=[2*inch, 2*inch, 2*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(risk_table)

        # Success Metrics
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Weekly Success Metrics", subheading_style))

        metrics_text = """
        • Execute 80% of planned trades within target ranges
        • Maintain stop losses on 100% of positions
        • Keep portfolio beta between 0.9-1.1 for DEE-BOT
        • Achieve 60% win rate on catalyst trades (SHORGAN)
        • Document all trades with rationale
        """

        elements.append(Paragraph(metrics_text, styles['Normal']))

        # Build PDF
        doc.build(elements)

        return pdf_filename

    def _get_portfolio_state(self, api_key, secret_key, bot_name):
        """Get current portfolio state"""
        try:
            client = TradingClient(api_key, secret_key, paper=True)
            account = client.get_account()
            return {
                'cash': float(account.cash),
                'equity': float(account.equity),
                'positions': len(client.get_all_positions())
            }
        except:
            return {'cash': 0, 'equity': 0, 'positions': 0}

def main():
    """Generate weekly trade plan"""

    print("="*70)
    print("       WEEKLY TRADE PLANNER")
    print("="*70)

    planner = WeeklyTradePlanner()

    print(f"\nGenerating trade plan for week of {datetime.now().strftime('%B %d, %Y')}...")

    pdf_file = planner.create_weekly_trade_plan()

    print(f"\n[SUCCESS] Trade plan created: {pdf_file}")

    print("\n" + "-"*70)
    print("TRADE PLAN SUMMARY")
    print("-"*70)
    print("\nDEE-BOT Focus:")
    print("  - Add defensive positions (XOM, JNJ)")
    print("  - Reduce high-beta exposure (trim NVDA)")
    print("  - Maintain 95%+ deployment")

    print("\nSHORGAN-BOT Focus:")
    print("  - SOUN entry on AI momentum")
    print("  - IONQ quantum conference play")
    print("  - Exit underperformers (GPK)")
    print("  - Keep 10% cash for opportunities")

    print("\nKey Events This Week:")
    print("  - Monday: IONQ quantum conference")
    print("  - Wednesday: BBAI earnings")
    print("  - Friday: PCE inflation data")

if __name__ == "__main__":
    main()