"""
Dual Bot Report Generator - SHORGAN-BOT and DEE-BOT
Generates comprehensive HTML and PDF reports for both trading bots
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import logging
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

load_dotenv()

# Configure logging
log_dir = '09_logs/reports'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DualBotReportGenerator:
    """Generates comprehensive reports for both SHORGAN-BOT and DEE-BOT"""
    
    def __init__(self):
        """Initialize with both bot configurations"""
        
        # SHORGAN-BOT API
        self.shorgan_api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY_SHORGAN'),
            os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
        # DEE-BOT API
        self.dee_api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY_DEE'),
            os.getenv('ALPACA_SECRET_KEY_DEE'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
        self.report_dir = '07_docs/dual_bot_reports'
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Data storage for both bots
        self.shorgan_data = {}
        self.dee_data = {}
        
    def fetch_bot_data(self, api, bot_name):
        """Fetch all data for a specific bot"""
        
        data = {
            'bot_name': bot_name,
            'timestamp': datetime.now(),
            'account': {},
            'positions': [],
            'orders': [],
            'trades': [],
            'pnl': {}
        }
        
        try:
            # Get account info
            account = api.get_account()
            data['account'] = {
                'portfolio_value': float(account.portfolio_value),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'equity': float(account.equity),
                'last_equity': float(account.last_equity),
                'long_market_value': float(account.long_market_value),
                'short_market_value': float(account.short_market_value),
                'initial_margin': float(account.initial_margin or 0),
                'maintenance_margin': float(account.maintenance_margin or 0),
                'sma': float(account.sma or 0),
                'daytrade_count': int(account.daytrade_count or 0),
                'pattern_day_trader': account.pattern_day_trader
            }
            
            # Get all positions
            positions = api.list_positions()
            for pos in positions:
                data['positions'].append({
                    'symbol': pos.symbol,
                    'quantity': int(pos.qty),
                    'side': pos.side,
                    'avg_entry_price': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price or 0),
                    'market_value': float(pos.market_value or 0),
                    'cost_basis': float(pos.cost_basis or 0),
                    'unrealized_pnl': float(pos.unrealized_pl or 0),
                    'unrealized_pnl_pct': float(pos.unrealized_plpc or 0) * 100,
                    'change_today': float(pos.change_today or 0),
                    'change_today_pct': float(getattr(pos, 'change_today_pct', 0) or 0) * 100
                })
            
            # Get recent orders (30 days)
            orders = api.list_orders(
                status='all',
                after=(datetime.now() - timedelta(days=30)).isoformat() + 'Z',
                limit=200
            )
            
            for order in orders:
                data['orders'].append({
                    'id': order.id,
                    'symbol': order.symbol,
                    'side': order.side,
                    'qty': order.qty,
                    'type': order.order_type,
                    'status': order.status,
                    'filled_qty': order.filled_qty,
                    'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else None,
                    'created_at': order.created_at,
                    'filled_at': order.filled_at,
                    'limit_price': float(order.limit_price) if order.limit_price else None,
                    'stop_price': float(order.stop_price) if order.stop_price else None
                })
            
            # Calculate P&L metrics
            data['pnl'] = self.calculate_pnl_metrics(data['positions'], data['orders'])
            
        except Exception as e:
            logging.error(f"Error fetching data for {bot_name}: {e}")
        
        return data
    
    def calculate_pnl_metrics(self, positions, orders):
        """Calculate P&L metrics for a bot"""
        
        # Unrealized P&L from positions
        unrealized_pnl = sum(p['unrealized_pnl'] for p in positions)
        daily_change = sum(p['change_today'] for p in positions)
        
        # Count filled orders
        filled_orders = [o for o in orders if o['status'] == 'filled']
        buy_orders = [o for o in filled_orders if o['side'] == 'buy']
        sell_orders = [o for o in filled_orders if o['side'] == 'sell']
        
        # Calculate win rate (simplified)
        winning_positions = [p for p in positions if p['unrealized_pnl'] > 0]
        losing_positions = [p for p in positions if p['unrealized_pnl'] < 0]
        
        win_rate = (len(winning_positions) / len(positions) * 100) if positions else 0
        
        return {
            'unrealized_pnl': unrealized_pnl,
            'daily_change': daily_change,
            'total_positions': len(positions),
            'winning_positions': len(winning_positions),
            'losing_positions': len(losing_positions),
            'win_rate': win_rate,
            'total_orders': len(filled_orders),
            'buy_orders': len(buy_orders),
            'sell_orders': len(sell_orders)
        }
    
    def generate_html_report(self, shorgan_data, dee_data):
        """Generate HTML report for both bots"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Dual Bot Trading Report - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        .bot-section {{
            background: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .bot-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        h1 {{
            color: #2c3e50;
            margin: 0;
        }}
        .bot-badge {{
            background: #3498db;
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
        }}
        .shorgan-badge {{ background: #e74c3c; }}
        .dee-badge {{ background: #27ae60; }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 1px solid #ecf0f1;
            padding-bottom: 5px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .metric-label {{
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-top: 5px;
        }}
        .positive {{ color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-size: 14px;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ecf0f1;
            font-size: 14px;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .summary-box {{
            background: #e8f4f8;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .comparison-table {{
            background: #fff3cd;
            padding: 20px;
            border-radius: 8px;
            margin: 30px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="font-size: 36px; color: #2c3e50;">Dual Bot Trading Report</h1>
            <p style="color: #7f8c8d;">{datetime.now().strftime('%B %d, %Y - %H:%M ET')}</p>
        </div>
"""
        
        # Bot Comparison Summary
        html += f"""
        <div class="comparison-table">
            <h2 style="text-align: center;">Portfolio Comparison</h2>
            <table>
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>SHORGAN-BOT</th>
                        <th>DEE-BOT</th>
                        <th>Combined</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Portfolio Value</strong></td>
                        <td>${shorgan_data['account']['portfolio_value']:,.2f}</td>
                        <td>${dee_data['account']['portfolio_value']:,.2f}</td>
                        <td><strong>${shorgan_data['account']['portfolio_value'] + dee_data['account']['portfolio_value']:,.2f}</strong></td>
                    </tr>
                    <tr>
                        <td><strong>Today's Change</strong></td>
                        <td class="{'positive' if shorgan_data['pnl']['daily_change'] >= 0 else 'negative'}">${shorgan_data['pnl']['daily_change']:+,.2f}</td>
                        <td class="{'positive' if dee_data['pnl']['daily_change'] >= 0 else 'negative'}">${dee_data['pnl']['daily_change']:+,.2f}</td>
                        <td class="{'positive' if (shorgan_data['pnl']['daily_change'] + dee_data['pnl']['daily_change']) >= 0 else 'negative'}"><strong>${shorgan_data['pnl']['daily_change'] + dee_data['pnl']['daily_change']:+,.2f}</strong></td>
                    </tr>
                    <tr>
                        <td><strong>Unrealized P&L</strong></td>
                        <td class="{'positive' if shorgan_data['pnl']['unrealized_pnl'] >= 0 else 'negative'}">${shorgan_data['pnl']['unrealized_pnl']:+,.2f}</td>
                        <td class="{'positive' if dee_data['pnl']['unrealized_pnl'] >= 0 else 'negative'}">${dee_data['pnl']['unrealized_pnl']:+,.2f}</td>
                        <td class="{'positive' if (shorgan_data['pnl']['unrealized_pnl'] + dee_data['pnl']['unrealized_pnl']) >= 0 else 'negative'}"><strong>${shorgan_data['pnl']['unrealized_pnl'] + dee_data['pnl']['unrealized_pnl']:+,.2f}</strong></td>
                    </tr>
                    <tr>
                        <td><strong>Positions</strong></td>
                        <td>{shorgan_data['pnl']['total_positions']}</td>
                        <td>{dee_data['pnl']['total_positions']}</td>
                        <td><strong>{shorgan_data['pnl']['total_positions'] + dee_data['pnl']['total_positions']}</strong></td>
                    </tr>
                    <tr>
                        <td><strong>Win Rate</strong></td>
                        <td>{shorgan_data['pnl']['win_rate']:.1f}%</td>
                        <td>{dee_data['pnl']['win_rate']:.1f}%</td>
                        <td><strong>{((shorgan_data['pnl']['win_rate'] + dee_data['pnl']['win_rate']) / 2):.1f}%</strong></td>
                    </tr>
                </tbody>
            </table>
        </div>
"""
        
        # Generate section for each bot
        for bot_data, badge_class, strategy in [(shorgan_data, 'shorgan-badge', 'Micro-Cap Catalyst Trading'), 
                                                 (dee_data, 'dee-badge', 'Beta-Neutral S&P 100')]:
            
            html += f"""
        <!-- {bot_data['bot_name']} Section -->
        <div class="bot-section">
            <div class="bot-header">
                <h1>{bot_data['bot_name']}</h1>
                <div>
                    <span class="bot-badge {badge_class}">{strategy}</span>
                </div>
            </div>
            
            <!-- Account Overview -->
            <h2>Account Overview</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">${bot_data['account']['portfolio_value']:,.2f}</div>
                    <div class="metric-label">Portfolio Value</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value {'positive' if bot_data['pnl']['daily_change'] >= 0 else 'negative'}">${bot_data['pnl']['daily_change']:+,.2f}</div>
                    <div class="metric-label">Today's Change</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value {'positive' if bot_data['pnl']['unrealized_pnl'] >= 0 else 'negative'}">${bot_data['pnl']['unrealized_pnl']:+,.2f}</div>
                    <div class="metric-label">Unrealized P&L</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${bot_data['account']['cash']:,.2f}</div>
                    <div class="metric-label">Cash Balance</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{bot_data['pnl']['total_positions']}</div>
                    <div class="metric-label">Open Positions</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{bot_data['pnl']['win_rate']:.1f}%</div>
                    <div class="metric-label">Win Rate</div>
                </div>
            </div>
            
            <!-- Positions Table -->
            <h2>Current Positions</h2>
            <table>
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Qty</th>
                        <th>Side</th>
                        <th>Entry</th>
                        <th>Current</th>
                        <th>Market Value</th>
                        <th>Unrealized P&L</th>
                        <th>P&L %</th>
                        <th>Today</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            # Add positions
            for pos in sorted(bot_data['positions'], key=lambda x: x['unrealized_pnl_pct'], reverse=True):
                pnl_class = 'positive' if pos['unrealized_pnl'] >= 0 else 'negative'
                today_class = 'positive' if pos['change_today'] >= 0 else 'negative'
                
                html += f"""
                    <tr>
                        <td><strong>{pos['symbol']}</strong></td>
                        <td>{pos['quantity']}</td>
                        <td>{pos['side'].upper()}</td>
                        <td>${pos['avg_entry_price']:.2f}</td>
                        <td>${pos['current_price']:.2f}</td>
                        <td>${pos['market_value']:,.2f}</td>
                        <td class="{pnl_class}">${pos['unrealized_pnl']:,.2f}</td>
                        <td class="{pnl_class}">{pos['unrealized_pnl_pct']:+.2f}%</td>
                        <td class="{today_class}">{pos['change_today_pct']:+.2f}%</td>
                    </tr>
"""
            
            html += """
                </tbody>
            </table>
            
            <!-- Trading Activity -->
            <h2>Recent Trading Activity (30 Days)</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{total_orders}</div>
                    <div class="metric-label">Total Orders</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{buy_orders}</div>
                    <div class="metric-label">Buy Orders</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{sell_orders}</div>
                    <div class="metric-label">Sell Orders</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{winning}</div>
                    <div class="metric-label">Winning Positions</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{losing}</div>
                    <div class="metric-label">Losing Positions</div>
                </div>
            </div>
        </div>
""".format(
                total_orders=bot_data['pnl']['total_orders'],
                buy_orders=bot_data['pnl']['buy_orders'],
                sell_orders=bot_data['pnl']['sell_orders'],
                winning=bot_data['pnl']['winning_positions'],
                losing=bot_data['pnl']['losing_positions']
            )
        
        # Footer
        html += f"""
        <div style="margin-top: 50px; padding: 20px; background: #ecf0f1; border-radius: 8px; text-align: center;">
            <p style="color: #7f8c8d; margin: 0;">
                Dual Bot Trading System | Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def generate_pdf_report(self, shorgan_data, dee_data, filename):
        """Generate PDF report for both bots"""
        
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        elements.append(Paragraph('Dual Bot Trading Report', title_style))
        elements.append(Paragraph(datetime.now().strftime('%B %d, %Y'), styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Portfolio Comparison Table
        elements.append(Paragraph('Portfolio Comparison', heading_style))
        
        comparison_data = [
            ['Metric', 'SHORGAN-BOT', 'DEE-BOT', 'Combined'],
            ['Portfolio Value', 
             f"${shorgan_data['account']['portfolio_value']:,.2f}",
             f"${dee_data['account']['portfolio_value']:,.2f}",
             f"${shorgan_data['account']['portfolio_value'] + dee_data['account']['portfolio_value']:,.2f}"],
            ['Today\'s Change',
             f"${shorgan_data['pnl']['daily_change']:+,.2f}",
             f"${dee_data['pnl']['daily_change']:+,.2f}",
             f"${shorgan_data['pnl']['daily_change'] + dee_data['pnl']['daily_change']:+,.2f}"],
            ['Unrealized P&L',
             f"${shorgan_data['pnl']['unrealized_pnl']:+,.2f}",
             f"${dee_data['pnl']['unrealized_pnl']:+,.2f}",
             f"${shorgan_data['pnl']['unrealized_pnl'] + dee_data['pnl']['unrealized_pnl']:+,.2f}"],
            ['Positions',
             str(shorgan_data['pnl']['total_positions']),
             str(dee_data['pnl']['total_positions']),
             str(shorgan_data['pnl']['total_positions'] + dee_data['pnl']['total_positions'])],
            ['Win Rate',
             f"{shorgan_data['pnl']['win_rate']:.1f}%",
             f"{dee_data['pnl']['win_rate']:.1f}%",
             f"{((shorgan_data['pnl']['win_rate'] + dee_data['pnl']['win_rate']) / 2):.1f}%"]
        ]
        
        comparison_table = Table(comparison_data, colWidths=[2*inch, 1.8*inch, 1.8*inch, 1.8*inch])
        comparison_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(comparison_table)
        elements.append(PageBreak())
        
        # Generate pages for each bot
        for bot_data in [shorgan_data, dee_data]:
            # Bot header
            elements.append(Paragraph(f"{bot_data['bot_name']} Report", title_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Account Summary
            elements.append(Paragraph('Account Summary', heading_style))
            
            account_data = [
                ['Portfolio Value', f"${bot_data['account']['portfolio_value']:,.2f}"],
                ['Cash Balance', f"${bot_data['account']['cash']:,.2f}"],
                ['Buying Power', f"${bot_data['account']['buying_power']:,.2f}"],
                ['Unrealized P&L', f"${bot_data['pnl']['unrealized_pnl']:+,.2f}"],
                ['Today\'s Change', f"${bot_data['pnl']['daily_change']:+,.2f}"],
                ['Total Positions', str(bot_data['pnl']['total_positions'])],
                ['Win Rate', f"{bot_data['pnl']['win_rate']:.1f}%"]
            ]
            
            account_table = Table(account_data, colWidths=[3*inch, 3*inch])
            account_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(account_table)
            elements.append(Spacer(1, 0.25*inch))
            
            # Positions
            elements.append(Paragraph('Current Positions', heading_style))
            
            # Position table headers
            position_data = [['Symbol', 'Qty', 'Entry', 'Current', 'P&L', 'P&L %']]
            
            # Add position rows (limit to top 10 for PDF)
            for pos in sorted(bot_data['positions'], key=lambda x: x['unrealized_pnl_pct'], reverse=True)[:10]:
                position_data.append([
                    pos['symbol'],
                    str(pos['quantity']),
                    f"${pos['avg_entry_price']:.2f}",
                    f"${pos['current_price']:.2f}",
                    f"${pos['unrealized_pnl']:,.2f}",
                    f"{pos['unrealized_pnl_pct']:+.2f}%"
                ])
            
            position_table = Table(position_data, colWidths=[1*inch, 0.8*inch, 1.2*inch, 1.2*inch, 1.4*inch, 1*inch])
            position_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(position_table)
            
            if bot_data != dee_data:  # Add page break between bots
                elements.append(PageBreak())
        
        # Build PDF
        doc.build(elements)
        
        logging.info(f"PDF report saved to {filename}")
        return filename
    
    def run(self):
        """Generate comprehensive dual-bot report"""
        
        print("Generating Dual Bot Report...")
        print("-" * 50)
        
        # Fetch data for both bots
        print("Fetching SHORGAN-BOT data...")
        self.shorgan_data = self.fetch_bot_data(self.shorgan_api, 'SHORGAN-BOT')
        
        print("Fetching DEE-BOT data...")
        self.dee_data = self.fetch_bot_data(self.dee_api, 'DEE-BOT')
        
        # Generate HTML report
        print("Generating HTML report...")
        html_report = self.generate_html_report(self.shorgan_data, self.dee_data)
        
        # Save HTML report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_filename = f"{self.report_dir}/dual_bot_report_{timestamp}.html"
        
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"[SUCCESS] HTML report saved to: {html_filename}")
        
        # Generate PDF report
        print("Generating PDF report...")
        pdf_filename = f"{self.report_dir}/dual_bot_report_{timestamp}.pdf"
        
        try:
            self.generate_pdf_report(self.shorgan_data, self.dee_data, pdf_filename)
            print(f"[SUCCESS] PDF report saved to: {pdf_filename}")
        except Exception as e:
            print(f"[WARNING] PDF generation failed: {e}")
            print("HTML report is still available")
        
        # Print summary
        print("\n" + "="*50)
        print("REPORT SUMMARY")
        print("="*50)
        
        print(f"\nSHORGAN-BOT:")
        print(f"  Portfolio: ${self.shorgan_data['account']['portfolio_value']:,.2f}")
        print(f"  Positions: {self.shorgan_data['pnl']['total_positions']}")
        print(f"  Unrealized P&L: ${self.shorgan_data['pnl']['unrealized_pnl']:+,.2f}")
        print(f"  Today: ${self.shorgan_data['pnl']['daily_change']:+,.2f}")
        
        print(f"\nDEE-BOT:")
        print(f"  Portfolio: ${self.dee_data['account']['portfolio_value']:,.2f}")
        print(f"  Positions: {self.dee_data['pnl']['total_positions']}")
        print(f"  Unrealized P&L: ${self.dee_data['pnl']['unrealized_pnl']:+,.2f}")
        print(f"  Today: ${self.dee_data['pnl']['daily_change']:+,.2f}")
        
        combined_value = self.shorgan_data['account']['portfolio_value'] + self.dee_data['account']['portfolio_value']
        combined_pnl = self.shorgan_data['pnl']['unrealized_pnl'] + self.dee_data['pnl']['unrealized_pnl']
        combined_daily = self.shorgan_data['pnl']['daily_change'] + self.dee_data['pnl']['daily_change']
        
        print(f"\nCOMBINED TOTAL:")
        print(f"  Portfolio: ${combined_value:,.2f}")
        print(f"  Total P&L: ${combined_pnl:+,.2f}")
        print(f"  Today: ${combined_daily:+,.2f}")
        
        # Open HTML report in browser
        import webbrowser
        webbrowser.open(f"file:///{os.path.abspath(html_filename)}")
        
        return html_filename, pdf_filename


if __name__ == "__main__":
    generator = DualBotReportGenerator()
    generator.run()