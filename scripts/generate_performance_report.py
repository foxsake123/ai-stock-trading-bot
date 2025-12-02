#!/usr/bin/env python3
"""
Generate Performance Report for Paper Trading Accounts
Creates a comprehensive PDF report for DEE-BOT and SHORGAN-BOT paper accounts
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

load_dotenv()

def get_account_data(api_key_env, secret_key_env, account_name):
    """Fetch account and position data from Alpaca"""
    try:
        api = TradingClient(
            os.getenv(api_key_env),
            os.getenv(secret_key_env),
            paper=True
        )
        account = api.get_account()
        positions = api.get_all_positions()

        return {
            'name': account_name,
            'portfolio_value': float(account.portfolio_value),
            'cash': float(account.cash),
            'equity': float(account.equity),
            'buying_power': float(account.buying_power),
            'positions': positions
        }
    except Exception as e:
        print(f"Error fetching {account_name}: {e}")
        return None

def format_currency(value):
    """Format number as currency"""
    return f"${value:,.2f}"

def format_percent(value):
    """Format number as percentage"""
    return f"{value:+.2f}%"

def create_pdf_report(dee_data, shorgan_data, output_path):
    """Create comprehensive PDF performance report"""

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        alignment=TA_CENTER,
        textColor=colors.gray
    )

    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.darkblue
    )

    normal_style = styles['Normal']

    story = []

    # Title
    story.append(Paragraph("AI Trading Bot Performance Report", title_style))
    story.append(Paragraph(f"Paper Trading Accounts - {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(Spacer(1, 20))

    # Executive Summary
    story.append(Paragraph("Executive Summary", section_style))

    initial_capital = 100000
    dee_return = ((dee_data['portfolio_value'] - initial_capital) / initial_capital) * 100
    shorgan_return = ((shorgan_data['portfolio_value'] - initial_capital) / initial_capital) * 100
    combined_value = dee_data['portfolio_value'] + shorgan_data['portfolio_value']
    combined_return = ((combined_value - 200000) / 200000) * 100

    summary_data = [
        ['Account', 'Portfolio Value', 'Return', 'Cash', 'Positions'],
        ['DEE-BOT', format_currency(dee_data['portfolio_value']), format_percent(dee_return),
         format_currency(dee_data['cash']), str(len(dee_data['positions']))],
        ['SHORGAN-BOT', format_currency(shorgan_data['portfolio_value']), format_percent(shorgan_return),
         format_currency(shorgan_data['cash']), str(len(shorgan_data['positions']))],
        ['COMBINED', format_currency(combined_value), format_percent(combined_return),
         format_currency(dee_data['cash'] + shorgan_data['cash']),
         str(len(dee_data['positions']) + len(shorgan_data['positions']))]
    ]

    summary_table = Table(summary_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1.3*inch, 1*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 30))

    # DEE-BOT Section
    story.append(Paragraph("DEE-BOT Paper Account", section_style))
    story.append(Paragraph(
        f"<b>Strategy:</b> Conservative dividend growth focusing on blue-chip stocks with stable dividends. "
        f"Target allocation: 70-80% equities, 20-30% cash buffer.",
        normal_style
    ))
    story.append(Spacer(1, 10))

    # DEE-BOT Positions Table
    dee_positions_data = [['Symbol', 'Shares', 'Entry Price', 'Current Price', 'Market Value', 'P&L', 'P&L %']]

    total_market_value = 0
    total_pl = 0

    for p in sorted(dee_data['positions'], key=lambda x: float(x.unrealized_pl), reverse=True):
        qty = int(float(p.qty))
        entry = float(p.avg_entry_price)
        current = float(p.current_price)
        market_val = float(p.market_value)
        pl = float(p.unrealized_pl)
        pl_pct = float(p.unrealized_plpc) * 100

        total_market_value += market_val
        total_pl += pl

        dee_positions_data.append([
            p.symbol,
            str(qty),
            format_currency(entry),
            format_currency(current),
            format_currency(market_val),
            format_currency(pl),
            format_percent(pl_pct)
        ])

    # Add totals row
    dee_positions_data.append([
        'TOTAL', '', '', '',
        format_currency(total_market_value),
        format_currency(total_pl),
        format_percent((total_pl / (total_market_value - total_pl)) * 100 if total_market_value != total_pl else 0)
    ])

    dee_table = Table(dee_positions_data, colWidths=[0.8*inch, 0.7*inch, 1*inch, 1*inch, 1.1*inch, 1*inch, 0.8*inch])
    dee_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    story.append(dee_table)
    story.append(Spacer(1, 10))

    # DEE-BOT metrics
    cash_pct = (dee_data['cash'] / dee_data['portfolio_value']) * 100
    invested_pct = 100 - cash_pct
    story.append(Paragraph(
        f"<b>Cash Allocation:</b> {cash_pct:.1f}% | <b>Invested:</b> {invested_pct:.1f}% | "
        f"<b>Unrealized P&L:</b> {format_currency(total_pl)}",
        normal_style
    ))

    story.append(PageBreak())

    # SHORGAN-BOT Section
    story.append(Paragraph("SHORGAN-BOT Paper Account", section_style))
    story.append(Paragraph(
        f"<b>Strategy:</b> Aggressive catalyst-driven trading with both long and short positions. "
        f"Focus on biotech, tech, and high-volatility plays around earnings and FDA events.",
        normal_style
    ))
    story.append(Spacer(1, 10))

    # SHORGAN-BOT Positions Table
    shorgan_positions_data = [['Symbol', 'Side', 'Shares', 'Entry', 'Current', 'Market Val', 'P&L', 'P&L %']]

    total_market_value = 0
    total_pl = 0

    for p in sorted(shorgan_data['positions'], key=lambda x: float(x.unrealized_pl), reverse=True):
        qty = int(float(p.qty))
        side = 'LONG' if qty > 0 else 'SHORT'
        entry = float(p.avg_entry_price)
        current = float(p.current_price)
        market_val = abs(float(p.market_value))
        pl = float(p.unrealized_pl)
        pl_pct = float(p.unrealized_plpc) * 100

        total_market_value += market_val
        total_pl += pl

        shorgan_positions_data.append([
            p.symbol,
            side,
            str(abs(qty)),
            format_currency(entry),
            format_currency(current),
            format_currency(market_val),
            format_currency(pl),
            format_percent(pl_pct)
        ])

    # Add totals row
    shorgan_positions_data.append([
        'TOTAL', '', '', '', '',
        format_currency(total_market_value),
        format_currency(total_pl),
        ''
    ])

    shorgan_table = Table(shorgan_positions_data, colWidths=[0.7*inch, 0.6*inch, 0.6*inch, 0.85*inch, 0.85*inch, 0.95*inch, 0.9*inch, 0.7*inch])
    shorgan_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    story.append(shorgan_table)
    story.append(Spacer(1, 10))

    # SHORGAN-BOT metrics
    cash_pct = (shorgan_data['cash'] / shorgan_data['portfolio_value']) * 100
    invested_pct = 100 - cash_pct

    # Count longs and shorts
    longs = sum(1 for p in shorgan_data['positions'] if int(float(p.qty)) > 0)
    shorts = sum(1 for p in shorgan_data['positions'] if int(float(p.qty)) < 0)

    story.append(Paragraph(
        f"<b>Cash Allocation:</b> {cash_pct:.1f}% | <b>Invested:</b> {invested_pct:.1f}% | "
        f"<b>Longs:</b> {longs} | <b>Shorts:</b> {shorts} | <b>Unrealized P&L:</b> {format_currency(total_pl)}",
        normal_style
    ))

    story.append(Spacer(1, 30))

    # Top Performers Section
    story.append(Paragraph("Top Performers (Combined)", section_style))

    all_positions = list(dee_data['positions']) + list(shorgan_data['positions'])
    top_winners = sorted(all_positions, key=lambda x: float(x.unrealized_pl), reverse=True)[:5]
    top_losers = sorted(all_positions, key=lambda x: float(x.unrealized_pl))[:5]

    story.append(Paragraph("<b>Top 5 Winners:</b>", normal_style))
    winners_data = [['Symbol', 'P&L', 'P&L %']]
    for p in top_winners:
        pl = float(p.unrealized_pl)
        pl_pct = float(p.unrealized_plpc) * 100
        winners_data.append([p.symbol, format_currency(pl), format_percent(pl_pct)])

    winners_table = Table(winners_data, colWidths=[1.5*inch, 1.5*inch, 1*inch])
    winners_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    story.append(winners_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Top 5 Losers:</b>", normal_style))
    losers_data = [['Symbol', 'P&L', 'P&L %']]
    for p in top_losers:
        pl = float(p.unrealized_pl)
        pl_pct = float(p.unrealized_plpc) * 100
        losers_data.append([p.symbol, format_currency(pl), format_percent(pl_pct)])

    losers_table = Table(losers_data, colWidths=[1.5*inch, 1.5*inch, 1*inch])
    losers_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    story.append(losers_table)

    story.append(Spacer(1, 30))

    # Footer
    story.append(Paragraph(
        f"<i>Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}</i>",
        ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.gray, alignment=TA_CENTER)
    ))
    story.append(Paragraph(
        "<i>AI Trading Bot - Automated Portfolio Management System</i>",
        ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.gray, alignment=TA_CENTER)
    ))

    # Build PDF
    doc.build(story)
    print(f"PDF report saved to: {output_path}")

def main():
    print("Fetching account data...")

    # Fetch data for both accounts
    dee_data = get_account_data('ALPACA_API_KEY_DEE', 'ALPACA_SECRET_KEY_DEE', 'DEE-BOT')
    shorgan_data = get_account_data('ALPACA_API_KEY_SHORGAN', 'ALPACA_SECRET_KEY_SHORGAN', 'SHORGAN-BOT')

    if not dee_data or not shorgan_data:
        print("Failed to fetch account data")
        return

    print(f"\nDEE-BOT: {format_currency(dee_data['portfolio_value'])} ({len(dee_data['positions'])} positions)")
    print(f"SHORGAN-BOT: {format_currency(shorgan_data['portfolio_value'])} ({len(shorgan_data['positions'])} positions)")

    # Create output path
    output_dir = project_root / "reports" / "performance"
    output_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime('%Y-%m-%d')
    output_path = output_dir / f"performance_report_{date_str}.pdf"

    print(f"\nGenerating PDF report...")
    create_pdf_report(dee_data, shorgan_data, output_path)

    print(f"\nReport saved: {output_path}")

if __name__ == "__main__":
    main()
