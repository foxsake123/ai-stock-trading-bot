#!/usr/bin/env python3
"""
Generate Weekly Deep Research PDF Reports
Converts ChatGPT weekly research into professional PDFs
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class WeeklyPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Create custom styles for the PDF"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#003366'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        # Section heading style
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            spaceBefore=20
        )

        # Subheading style
        self.subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#0066CC'),
            spaceAfter=8,
            spaceBefore=12,
            leftIndent=10
        )

        # Body text style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            leftIndent=10
        )

        # Table header style
        self.table_header_style = ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER
        )

    def generate_weekly_research_pdf(self, json_file=None, text_content=None, bot_type='both'):
        """Generate PDF from weekly research JSON or text"""

        # Create output directory
        date_str = datetime.now().strftime('%Y-%m-%d')
        week_str = f"Week_{datetime.now().strftime('%Y_W%U')}"
        pdf_dir = Path(f"../../docs/index/reports-pdf/weekly/{week_str}")
        pdf_dir.mkdir(parents=True, exist_ok=True)

        # Determine output filename
        if bot_type == 'dee':
            pdf_file = pdf_dir / f"dee_bot_weekly_research_{date_str}.pdf"
        elif bot_type == 'shorgan':
            pdf_file = pdf_dir / f"shorgan_bot_weekly_research_{date_str}.pdf"
        else:
            pdf_file = pdf_dir / f"combined_weekly_research_{date_str}.pdf"

        # Create PDF
        doc = SimpleDocTemplate(str(pdf_file), pagesize=letter)
        story = []

        # Load data
        data = {}
        if json_file and os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)
        elif text_content:
            data = self.parse_text_content(text_content)
        else:
            print("No data provided")
            return None

        # Add title
        story.append(Paragraph(f"Weekly Deep Research Report", self.title_style))
        story.append(Paragraph(f"{week_str.replace('_', ' ')}", self.body_style))
        story.append(Spacer(1, 20))

        # Add executive summary
        story.append(Paragraph("Executive Summary", self.heading_style))
        if 'executive_summary' in data:
            story.append(Paragraph(data['executive_summary'], self.body_style))
        story.append(Spacer(1, 12))

        # Process DEE-BOT section if needed
        if bot_type in ['dee', 'both'] and 'dee_bot' in data:
            story.extend(self.create_dee_bot_section(data['dee_bot']))
            if bot_type == 'both':
                story.append(PageBreak())

        # Process SHORGAN-BOT section if needed
        if bot_type in ['shorgan', 'both'] and 'shorgan_bot' in data:
            story.extend(self.create_shorgan_bot_section(data['shorgan_bot']))

        # Add risk analysis
        if 'risk_analysis' in data:
            story.append(PageBreak())
            story.extend(self.create_risk_section(data['risk_analysis']))

        # Add market outlook
        if 'market_outlook' in data:
            story.append(Paragraph("Market Outlook", self.heading_style))
            story.append(Paragraph(data['market_outlook'], self.body_style))

        # Build PDF
        doc.build(story)
        print(f"Generated PDF: {pdf_file}")
        return str(pdf_file)

    def create_dee_bot_section(self, dee_data):
        """Create DEE-BOT section for PDF"""
        elements = []

        # Section title
        elements.append(Paragraph("DEE-BOT: Defensive Beta-Neutral Strategy", self.heading_style))
        elements.append(Spacer(1, 12))

        # Portfolio Assessment
        if 'portfolio_assessment' in dee_data:
            elements.append(Paragraph("Current Portfolio Assessment", self.subheading_style))

            # Create portfolio table
            table_data = [['Symbol', 'Shares', 'Entry', 'Current', 'P&L %', 'Conviction', 'Action']]

            for position in dee_data.get('portfolio_assessment', []):
                table_data.append([
                    position.get('symbol', ''),
                    str(position.get('shares', '')),
                    f"${position.get('entry_price', 0):.2f}",
                    f"${position.get('current_price', 0):.2f}",
                    f"{position.get('pl_percent', 0):.1f}%",
                    position.get('conviction', ''),
                    position.get('action', 'HOLD')
                ])

            if len(table_data) > 1:
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(table)
                elements.append(Spacer(1, 20))

        # Candidate Analysis
        if 'candidates' in dee_data:
            elements.append(Paragraph("New Position Candidates", self.subheading_style))

            table_data = [['Symbol', 'Sector', 'Beta', 'Yield %', 'P/E', 'Score', 'Recommendation']]

            for candidate in dee_data.get('candidates', []):
                table_data.append([
                    candidate.get('symbol', ''),
                    candidate.get('sector', ''),
                    f"{candidate.get('beta', 0):.2f}",
                    f"{candidate.get('yield', 0):.2f}%",
                    f"{candidate.get('pe_ratio', 0):.1f}",
                    f"{candidate.get('score', 0):.1f}",
                    candidate.get('recommendation', '')
                ])

            if len(table_data) > 1:
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(table)
                elements.append(Spacer(1, 20))

        # Exact Orders
        if 'exact_orders' in dee_data:
            elements.append(Paragraph("Exact Trade Orders", self.subheading_style))

            for order in dee_data.get('exact_orders', []):
                order_text = f"<b>{order.get('action', '')}</b> {order.get('shares', '')} shares of <b>{order.get('symbol', '')}</b> "
                order_text += f"at {order.get('order_type', 'MARKET')} "
                if order.get('limit_price'):
                    order_text += f"(Limit: ${order.get('limit_price', 0):.2f})"
                elements.append(Paragraph(order_text, self.body_style))
            elements.append(Spacer(1, 12))

        return elements

    def create_shorgan_bot_section(self, shorgan_data):
        """Create SHORGAN-BOT section for PDF"""
        elements = []

        # Section title
        elements.append(Paragraph("SHORGAN-BOT: Catalyst-Driven Trading", self.heading_style))
        elements.append(Spacer(1, 12))

        # Catalyst Events
        if 'catalyst_events' in shorgan_data:
            elements.append(Paragraph("Upcoming Catalyst Events", self.subheading_style))

            table_data = [['Symbol', 'Event Type', 'Date', 'Impact', 'Action Plan']]

            for event in shorgan_data.get('catalyst_events', []):
                table_data.append([
                    event.get('symbol', ''),
                    event.get('event_type', ''),
                    event.get('date', ''),
                    event.get('impact', ''),
                    event.get('action', '')
                ])

            if len(table_data) > 1:
                table = Table(table_data, colWidths=[1*inch, 1.5*inch, 1*inch, 1*inch, 2*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#660033')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(table)
                elements.append(Spacer(1, 20))

        # High Conviction Trades
        if 'high_conviction' in shorgan_data:
            elements.append(Paragraph("High Conviction Opportunities", self.subheading_style))

            for trade in shorgan_data.get('high_conviction', []):
                trade_text = f"<b>{trade.get('symbol', '')}</b> - {trade.get('thesis', '')}"
                elements.append(Paragraph(trade_text, self.body_style))

                details = f"Entry: ${trade.get('entry', 0):.2f} | Target: ${trade.get('target', 0):.2f} | Stop: ${trade.get('stop', 0):.2f}"
                elements.append(Paragraph(details, self.body_style))
                elements.append(Spacer(1, 8))

        return elements

    def create_risk_section(self, risk_data):
        """Create risk analysis section"""
        elements = []

        elements.append(Paragraph("Risk Analysis", self.heading_style))

        # Portfolio risk metrics
        if 'metrics' in risk_data:
            metrics_text = f"Portfolio Beta: {risk_data['metrics'].get('beta', 0):.2f} | "
            metrics_text += f"VaR (95%): {risk_data['metrics'].get('var_95', 0):.2f}% | "
            metrics_text += f"Sharpe Ratio: {risk_data['metrics'].get('sharpe', 0):.2f}"
            elements.append(Paragraph(metrics_text, self.body_style))
            elements.append(Spacer(1, 12))

        # Risk warnings
        if 'warnings' in risk_data:
            elements.append(Paragraph("Risk Warnings", self.subheading_style))
            for warning in risk_data.get('warnings', []):
                elements.append(Paragraph(f"⚠️ {warning}", self.body_style))
            elements.append(Spacer(1, 12))

        return elements

    def parse_text_content(self, text):
        """Parse raw text content from ChatGPT"""
        # This would parse the ChatGPT output
        # For now, return a basic structure
        return {
            'executive_summary': 'Weekly research analysis from ChatGPT',
            'dee_bot': {},
            'shorgan_bot': {},
            'risk_analysis': {}
        }

    def archive_weekly_reports(self):
        """Archive all weekly reports to index folder"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        week_str = f"Week_{datetime.now().strftime('%Y_W%U')}"

        # Create archive directory
        archive_dir = Path(f"../../docs/index/reports-pdf/weekly/{week_str}")
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Archive markdown version too
        md_archive = Path(f"../../docs/index/reports-md/weekly/{week_str}")
        md_archive.mkdir(parents=True, exist_ok=True)

        print(f"Weekly reports archived to: {archive_dir}")
        return str(archive_dir)

def main():
    """Main execution"""
    print("=" * 60)
    print("WEEKLY DEEP RESEARCH PDF GENERATOR")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    generator = WeeklyPDFGenerator()

    # Check for latest ChatGPT weekly research JSON
    research_dir = Path("../../scripts-and-data/data/reports/weekly")
    json_files = list(research_dir.glob("*weekly_research*.json"))

    if json_files:
        latest_json = max(json_files, key=os.path.getctime)
        print(f"\nFound research file: {latest_json.name}")

        # Generate PDFs for both bots
        generator.generate_weekly_research_pdf(latest_json, bot_type='both')
        generator.generate_weekly_research_pdf(latest_json, bot_type='dee')
        generator.generate_weekly_research_pdf(latest_json, bot_type='shorgan')

        # Archive reports
        generator.archive_weekly_reports()
    else:
        print("No weekly research JSON found. Looking for text reports...")

        # Try to find text reports
        txt_files = list(research_dir.glob("*weekly*.txt"))
        if txt_files:
            latest_txt = max(txt_files, key=os.path.getctime)
            with open(latest_txt, 'r') as f:
                text_content = f.read()
            generator.generate_weekly_research_pdf(text_content=text_content, bot_type='both')

    print("\n" + "=" * 60)
    print("WEEKLY PDF GENERATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()