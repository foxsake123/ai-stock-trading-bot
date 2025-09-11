"""
Live Post-Market Report with Alpaca Integration
Fetches actual paper trading data and sends via Telegram
Date: September 10, 2025
"""

import json
from datetime import datetime
import alpaca_trade_api as tradeapi
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import telegram
from telegram import Bot
import asyncio
import os
import sys
sys.path.append('../Configuration')

class LivePostMarketReport:
    """Generate live post-market report with actual Alpaca data"""
    
    def __init__(self):
        self.report_time = datetime.now()
        self.report_date = "2025-09-10"
        
        # Alpaca credentials from updated .env file
        self.dee_bot_api = {
            'key': os.getenv('ALPACA_API_KEY_DEE', 'PK6FZK4DAQVTD7DYVH78'),
            'secret': os.getenv('ALPACA_SECRET_KEY_DEE', 'JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt'),
            'base_url': 'https://paper-api.alpaca.markets'
        }
        
        # SHORGAN-BOT with its own credentials
        self.shorgan_bot_api = {
            'key': os.getenv('ALPACA_API_KEY_SHORGAN', 'PKJRLSB2MFEJUSK6UK2E'),
            'secret': os.getenv('ALPACA_SECRET_KEY_SHORGAN', 'QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic'),
            'base_url': 'https://paper-api.alpaca.markets'
        }
        
        # Telegram credentials from .env
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '7870288896')
        
    def connect_alpaca(self, api_credentials):
        """Connect to Alpaca API"""
        try:
            api = tradeapi.REST(
                api_credentials['key'],
                api_credentials['secret'],
                api_credentials['base_url'],
                api_version='v2'
            )
            return api
        except Exception as e:
            print(f"[ERROR] Failed to connect to Alpaca: {str(e)}")
            return None
    
    def get_dee_bot_data(self):
        """Get DEE-BOT's actual positions and P&L"""
        api = self.connect_alpaca(self.dee_bot_api)
        if not api:
            return None
            
        portfolio_data = {
            'bot_name': 'DEE-BOT',
            'strategy': 'S&P 100 Multi-Agent Consensus',
            'positions': [],
            'daily_pnl': 0,
            'total_value': 100000,
            'cash': 100000,
            'market_value': 0,
            'win_rate': 0
        }
        
        try:
            # Get account info
            account = api.get_account()
            portfolio_data['total_value'] = float(account.portfolio_value)
            portfolio_data['cash'] = float(account.cash)
            portfolio_data['market_value'] = float(account.long_market_value) if hasattr(account, 'long_market_value') else 0
            
            # Calculate daily P&L (portfolio value - starting capital)
            portfolio_data['daily_pnl'] = portfolio_data['total_value'] - 100000
            
            # Get positions
            positions = api.list_positions()
            for pos in positions:
                position_data = {
                    'ticker': pos.symbol,
                    'shares': int(pos.qty),
                    'entry_price': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price) if hasattr(pos, 'current_price') else float(pos.avg_entry_price),
                    'market_value': float(pos.market_value),
                    'pnl': float(pos.unrealized_pl) if hasattr(pos, 'unrealized_pl') else 0,
                    'pnl_pct': float(pos.unrealized_plpc) * 100 if hasattr(pos, 'unrealized_plpc') else 0
                }
                portfolio_data['positions'].append(position_data)
            
            # Calculate win rate
            if portfolio_data['positions']:
                winning = len([p for p in portfolio_data['positions'] if p['pnl'] > 0])
                portfolio_data['win_rate'] = (winning / len(portfolio_data['positions'])) * 100
            else:
                portfolio_data['win_rate'] = 0
                
            print(f"[DEE-BOT] Retrieved {len(portfolio_data['positions'])} positions")
            print(f"  Portfolio Value: ${portfolio_data['total_value']:,.2f}")
            print(f"  Daily P&L: ${portfolio_data['daily_pnl']:,.2f}")
            
        except Exception as e:
            print(f"[ERROR] Failed to get DEE-BOT data: {str(e)}")
            
        return portfolio_data
    
    def get_shorgan_bot_data(self):
        """Get SHORGAN-BOT's actual positions and P&L"""
        api = self.connect_alpaca(self.shorgan_bot_api)
        if not api:
            return None
            
        portfolio_data = {
            'bot_name': 'SHORGAN-BOT',
            'strategy': 'Catalyst Event Trading',
            'positions': [],
            'daily_pnl': 0,
            'total_value': 100000,
            'cash': 100000,
            'market_value': 0,
            'win_rate': 0
        }
        
        try:
            # Get account info
            account = api.get_account()
            portfolio_data['total_value'] = float(account.portfolio_value)
            portfolio_data['cash'] = float(account.cash)
            portfolio_data['market_value'] = float(account.long_market_value) if hasattr(account, 'long_market_value') else 0
            
            # Calculate daily P&L
            portfolio_data['daily_pnl'] = portfolio_data['total_value'] - 100000
            
            # Get positions
            positions = api.list_positions()
            for pos in positions:
                position_data = {
                    'ticker': pos.symbol,
                    'shares': int(pos.qty),
                    'entry_price': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price) if hasattr(pos, 'current_price') else float(pos.avg_entry_price),
                    'market_value': float(pos.market_value),
                    'pnl': float(pos.unrealized_pl) if hasattr(pos, 'unrealized_pl') else 0,
                    'pnl_pct': float(pos.unrealized_plpc) * 100 if hasattr(pos, 'unrealized_plpc') else 0
                }
                portfolio_data['positions'].append(position_data)
            
            # Calculate win rate
            if portfolio_data['positions']:
                winning = len([p for p in portfolio_data['positions'] if p['pnl'] > 0])
                portfolio_data['win_rate'] = (winning / len(portfolio_data['positions'])) * 100
            else:
                portfolio_data['win_rate'] = 0
                
            print(f"[SHORGAN-BOT] Retrieved {len(portfolio_data['positions'])} positions")
            print(f"  Portfolio Value: ${portfolio_data['total_value']:,.2f}")
            print(f"  Daily P&L: ${portfolio_data['daily_pnl']:,.2f}")
            
        except Exception as e:
            print(f"[ERROR] Failed to get SHORGAN-BOT data: {str(e)}")
            
        return portfolio_data
    
    def generate_pdf_report(self, bot_data, filename=None):
        """Generate PDF report for a bot"""
        if not filename:
            bot_name = bot_data['bot_name'].replace('-', '_')
            timestamp = datetime.now().strftime('%H%M%S')
            filename = f"{bot_name}_live_report_{self.report_date}_{timestamp}.pdf"
        
        # Create directory
        pdf_dir = Path(f"post_market_daily/{self.report_date}/pdf")
        pdf_dir.mkdir(parents=True, exist_ok=True)
        filepath = pdf_dir / filename
        
        # Create PDF
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        title = Paragraph(f"{bot_data['bot_name']} LIVE TRADING REPORT", title_style)
        story.append(title)
        
        # Date and strategy
        date_text = Paragraph(f"Date: September 10, 2025<br/>Strategy: {bot_data['strategy']}", styles['Normal'])
        story.append(date_text)
        story.append(Spacer(1, 0.2*inch))
        
        # Portfolio Summary
        summary_data = [
            ['Portfolio Summary', ''],
            ['Starting Capital', '$100,000.00'],
            ['Current Value', f"${bot_data['total_value']:,.2f}"],
            ['Cash Available', f"${bot_data['cash']:,.2f}"],
            ['Market Value', f"${bot_data['market_value']:,.2f}"],
            ['Daily P&L', f"${bot_data['daily_pnl']:,.2f}"],
            ['Win Rate', f"{bot_data['win_rate']:.1f}%"],
            ['Active Positions', str(len(bot_data['positions']))]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            # Color P&L
            ('TEXTCOLOR', (1, 5), (1, 5), colors.green if bot_data['daily_pnl'] > 0 else colors.red)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Positions table
        if bot_data['positions']:
            positions_data = [['Ticker', 'Shares', 'Entry', 'Current', 'P&L', 'P&L %']]
            for pos in bot_data['positions']:
                positions_data.append([
                    pos['ticker'],
                    str(pos['shares']),
                    f"${pos['entry_price']:.2f}",
                    f"${pos['current_price']:.2f}",
                    f"${pos['pnl']:.2f}",
                    f"{pos['pnl_pct']:.2f}%"
                ])
            
            positions_table = Table(positions_data)
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]
            
            # Color P&L column
            for i, pos in enumerate(bot_data['positions'], 1):
                if pos['pnl'] > 0:
                    table_style.append(('TEXTCOLOR', (4, i), (5, i), colors.green))
                else:
                    table_style.append(('TEXTCOLOR', (4, i), (5, i), colors.red))
            
            positions_table.setStyle(TableStyle(table_style))
            story.append(positions_table)
        else:
            no_pos = Paragraph("No active positions", styles['Normal'])
            story.append(no_pos)
        
        # Build PDF
        doc.build(story)
        print(f"[PDF GENERATED] {filepath}")
        return filepath
    
    async def send_telegram_report(self, pdf_path, bot_data):
        """Send report via Telegram"""
        try:
            bot = Bot(token=self.telegram_bot_token)
            
            # Prepare message
            emoji = "🟢" if bot_data['daily_pnl'] > 0 else "🔴" if bot_data['daily_pnl'] < 0 else "⚪"
            message = f"""
{emoji} *{bot_data['bot_name']} Live Report - Sept 10, 2025*

💼 Strategy: {bot_data['strategy']}
💰 Portfolio Value: ${bot_data['total_value']:,.2f}
💵 Cash Available: ${bot_data['cash']:,.2f}
📊 Market Value: ${bot_data['market_value']:,.2f}
📈 Daily P&L: ${bot_data['daily_pnl']:,.2f} ({(bot_data['daily_pnl']/100000)*100:.2f}%)
🎯 Win Rate: {bot_data['win_rate']:.1f}%
📍 Active Positions: {len(bot_data['positions'])}

*Top Positions:*"""
            
            # Add position details
            for pos in bot_data['positions'][:5]:  # Top 5 positions
                p_emoji = "🟢" if pos['pnl'] > 0 else "🔴"
                message += f"\n{p_emoji} {pos['ticker']}: {pos['shares']} shares @ ${pos['current_price']:.2f} ({pos['pnl_pct']:+.2f}%)"
            
            # Send message
            await bot.send_message(
                chat_id=self.telegram_chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
            # Send PDF
            with open(pdf_path, 'rb') as pdf:
                await bot.send_document(
                    chat_id=self.telegram_chat_id,
                    document=pdf,
                    filename=pdf_path.name
                )
            
            print(f"[TELEGRAM] Report sent successfully!")
            return True
            
        except Exception as e:
            print(f"[TELEGRAM ERROR] {str(e)}")
            return False
    
    def generate_complete_report(self):
        """Generate complete live trading report"""
        print("\n" + "="*70)
        print("LIVE POST-MARKET REPORT")
        print(f"Date: September 10, 2025")
        print(f"Time: {datetime.now().strftime('%I:%M %p ET')}")
        print("="*70)
        
        # Get live data from Alpaca
        print("\n[FETCHING LIVE DATA FROM ALPACA]")
        dee_bot_data = self.get_dee_bot_data()
        shorgan_bot_data = self.get_shorgan_bot_data()
        
        if not dee_bot_data or not shorgan_bot_data:
            print("[ERROR] Could not fetch data from one or both accounts")
            return
        
        # Display summary
        print("\n" + "="*70)
        print("PORTFOLIO SUMMARY")
        print("="*70)
        
        print(f"\n[{dee_bot_data['bot_name']}]")
        print(f"  Portfolio Value: ${dee_bot_data['total_value']:,.2f}")
        print(f"  Daily P&L: ${dee_bot_data['daily_pnl']:,.2f} ({(dee_bot_data['daily_pnl']/100000)*100:+.2f}%)")
        print(f"  Positions: {len(dee_bot_data['positions'])}")
        print(f"  Win Rate: {dee_bot_data['win_rate']:.1f}%")
        
        print(f"\n[{shorgan_bot_data['bot_name']}]")
        print(f"  Portfolio Value: ${shorgan_bot_data['total_value']:,.2f}")
        print(f"  Daily P&L: ${shorgan_bot_data['daily_pnl']:,.2f} ({(shorgan_bot_data['daily_pnl']/100000)*100:+.2f}%)")
        print(f"  Positions: {len(shorgan_bot_data['positions'])}")
        print(f"  Win Rate: {shorgan_bot_data['win_rate']:.1f}%")
        
        # Combined metrics
        total_value = dee_bot_data['total_value'] + shorgan_bot_data['total_value']
        total_pnl = dee_bot_data['daily_pnl'] + shorgan_bot_data['daily_pnl']
        total_positions = len(dee_bot_data['positions']) + len(shorgan_bot_data['positions'])
        
        print("\n" + "="*70)
        print("COMBINED PORTFOLIO")
        print("="*70)
        print(f"  Total Value: ${total_value:,.2f}")
        print(f"  Combined P&L: ${total_pnl:,.2f} ({(total_pnl/200000)*100:+.2f}%)")
        print(f"  Total Positions: {total_positions}")
        
        # Generate PDFs
        print("\n[GENERATING PDF REPORTS]")
        dee_pdf = self.generate_pdf_report(dee_bot_data)
        shorgan_pdf = self.generate_pdf_report(shorgan_bot_data)
        
        # Send via Telegram
        print("\n[SENDING TELEGRAM REPORTS]")
        asyncio.run(self.send_telegram_report(dee_pdf, dee_bot_data))
        asyncio.run(self.send_telegram_report(shorgan_pdf, shorgan_bot_data))
        
        print("\n" + "="*70)
        print("REPORT COMPLETE")
        print("="*70)
        
        return {
            'dee_bot': dee_bot_data,
            'shorgan_bot': shorgan_bot_data,
            'combined_pnl': total_pnl,
            'combined_value': total_value
        }

if __name__ == "__main__":
    report = LivePostMarketReport()
    report.generate_complete_report()