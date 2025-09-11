"""
Enhanced Post-Market Report with PDF Generation and Telegram Delivery
Generates separate reports for DEE-BOT and SHORGAN-BOT portfolios
Date: September 10, 2025
"""

import json
from datetime import datetime
import yfinance as yf
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import telegram
from telegram import Bot
import asyncio
import sys
sys.path.append('../Configuration')
sys.path.append('../Bot_Strategies')

class EnhancedPostMarketReport:
    """Generate comprehensive post-market reports with PDF and Telegram delivery"""
    
    def __init__(self):
        self.report_time = datetime.now()
        # FIXED: Using September 10, 2025
        self.report_date = "2025-09-10"
        self.report_data = {
            'report_type': 'POST_MARKET_DAILY',
            'timestamp': self.report_time.isoformat(),
            'market_date': self.report_date
        }
        
        # Separate bot portfolios
        self.dee_bot_portfolio = {
            'bot_name': 'DEE-BOT',
            'strategy': 'S&P 100 Multi-Agent Consensus',
            'positions': [],
            'daily_pnl': 0,
            'total_value': 0
        }
        
        self.shorgan_bot_portfolio = {
            'bot_name': 'SHORGAN-BOT',
            'strategy': 'Catalyst Event Trading',
            'positions': [],
            'daily_pnl': 0,
            'total_value': 0
        }
        
        # Telegram configuration (to be filled with actual credentials)
        self.telegram_bot_token = None  # Add your bot token
        self.telegram_chat_ids = []  # Add chat IDs to send to
        
    def get_market_data_with_fallback(self):
        """Get market data with fallback to mock data if API fails"""
        market_data = {}
        
        # Try to get real data first
        indices = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'Nasdaq',
            '^RUT': 'Russell 2000',
            '^VIX': 'VIX'
        }
        
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period='1d')
                if not history.empty:
                    market_data[symbol] = {
                        'name': name,
                        'close': float(history['Close'].iloc[-1]),
                        'change_pct': ((history['Close'].iloc[-1] - history['Open'].iloc[0]) / 
                                     history['Open'].iloc[0]) * 100
                    }
            except:
                # Fallback to mock data for demo
                mock_data = {
                    '^GSPC': {'close': 5950.25, 'change_pct': 0.68},
                    '^DJI': {'close': 42850.75, 'change_pct': 0.45},
                    '^IXIC': {'close': 19485.50, 'change_pct': 1.12},
                    '^RUT': {'close': 2285.30, 'change_pct': 0.92},
                    '^VIX': {'close': 15.25, 'change_pct': -5.2}
                }
                if symbol in mock_data:
                    market_data[symbol] = {
                        'name': name,
                        'close': mock_data[symbol]['close'],
                        'change_pct': mock_data[symbol]['change_pct']
                    }
        
        return market_data
    
    def analyze_dee_bot_portfolio(self):
        """Analyze DEE-BOT's S&P 100 positions"""
        # Try to get actual positions from Alpaca API or trading logs
        positions = []
        
        try:
            # TODO: Connect to Alpaca API to get actual positions
            # api = self.get_alpaca_connection()
            # positions = api.list_positions()
            pass
        except:
            pass
        
        if not positions:
            # No actual data available
            self.dee_bot_portfolio['positions'] = []
            self.dee_bot_portfolio['daily_pnl'] = "Data unavailable"
            self.dee_bot_portfolio['total_value'] = 100000  # Starting capital
            self.dee_bot_portfolio['win_rate'] = "N/A"
            self.dee_bot_portfolio['message'] = "Could not retrieve actual trading data from Alpaca"
        else:
            total_pnl = sum(p.get('pnl', 0) for p in positions)
            total_value = sum(p['shares'] * p['current_price'] for p in positions)
            
            self.dee_bot_portfolio['positions'] = positions
            self.dee_bot_portfolio['daily_pnl'] = total_pnl
            self.dee_bot_portfolio['total_value'] = total_value
            self.dee_bot_portfolio['win_rate'] = len([p for p in positions if p.get('pnl', 0) > 0]) / len(positions) * 100 if positions else 0
        
        return self.dee_bot_portfolio
    
    def analyze_shorgan_bot_portfolio(self):
        """Analyze SHORGAN-BOT's catalyst positions"""
        # Try to get actual positions from Alpaca API or trading logs
        positions = []
        
        try:
            # TODO: Connect to Alpaca API to get actual positions
            # api = self.get_alpaca_connection()
            # positions = api.list_positions()
            pass
        except:
            pass
        
        if not positions:
            # No actual data available
            self.shorgan_bot_portfolio['positions'] = []
            self.shorgan_bot_portfolio['daily_pnl'] = "Data unavailable"
            self.shorgan_bot_portfolio['total_value'] = 100000  # Starting capital
            self.shorgan_bot_portfolio['win_rate'] = "N/A"
            self.shorgan_bot_portfolio['message'] = "Could not retrieve actual trading data from Alpaca"
        else:
            total_pnl = sum(p.get('pnl', 0) for p in positions)
            total_value = sum(p['shares'] * p['current_price'] for p in positions)
            
            self.shorgan_bot_portfolio['positions'] = positions
            self.shorgan_bot_portfolio['daily_pnl'] = total_pnl
            self.shorgan_bot_portfolio['total_value'] = total_value
            self.shorgan_bot_portfolio['win_rate'] = len([p for p in positions if p.get('pnl', 0) > 0]) / len(positions) * 100 if positions else 0
        
        return self.shorgan_bot_portfolio
    
    def generate_pdf_report(self, bot_portfolio, filename=None):
        """Generate PDF report for a specific bot"""
        if not filename:
            bot_name = bot_portfolio['bot_name'].replace('-', '_')
            timestamp = datetime.now().strftime('%H%M%S')
            filename = f"{bot_name}_report_{self.report_date}_{timestamp}.pdf"
        
        # Create directory if it doesn't exist
        pdf_dir = Path(f"post_market_daily/{self.report_date}/pdf")
        pdf_dir.mkdir(parents=True, exist_ok=True)
        filepath = pdf_dir / filename
        
        # Create PDF
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Add title
        title = Paragraph(f"{bot_portfolio['bot_name']} POST-MARKET REPORT", title_style)
        story.append(title)
        
        # Add date and strategy
        date_text = Paragraph(f"Date: September 10, 2025<br/>Strategy: {bot_portfolio['strategy']}", 
                            styles['Normal'])
        story.append(date_text)
        story.append(Spacer(1, 0.2*inch))
        
        # Portfolio Summary
        summary_data = [
            ['Portfolio Summary', ''],
            ['Starting Capital', '$100,000.00'],
            ['Total Value', f"${bot_portfolio['total_value']:,.2f}"],
            ['Daily P&L', bot_portfolio['daily_pnl'] if isinstance(bot_portfolio['daily_pnl'], str) else f"${bot_portfolio['daily_pnl']:,.2f}"],
            ['Win Rate', str(bot_portfolio['win_rate'])],
            ['Positions', str(len(bot_portfolio['positions']))]
        ]
        
        if bot_portfolio.get('message'):
            summary_data.append(['Status', bot_portfolio['message']])
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Positions table
        if bot_portfolio['positions']:
            positions_data = [['Ticker', 'Shares', 'Entry', 'Current', 'P&L', 'P&L %']]
            for pos in bot_portfolio['positions']:
                positions_data.append([
                    pos['ticker'],
                    str(pos['shares']),
                    f"${pos['entry_price']:.2f}",
                    f"${pos['current_price']:.2f}",
                    f"${pos['pnl']:.2f}",
                    f"{pos['pnl_pct']:.2f}%"
                ])
        else:
            positions_data = [
                ['Position Status', ''],
                ['No positions found', 'Could not retrieve data from Alpaca API']
            ]
        
        positions_table = Table(positions_data)
        # Create table style
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
        
        # Only add P&L coloring if we have actual numeric data
        if bot_portfolio['positions'] and not isinstance(bot_portfolio['daily_pnl'], str):
            if bot_portfolio['daily_pnl'] > 0:
                table_style.append(('TEXTCOLOR', (4, 1), (4, -1), colors.green))
            else:
                table_style.append(('TEXTCOLOR', (4, 1), (4, -1), colors.red))
        
        positions_table.setStyle(TableStyle(table_style))
        story.append(positions_table)
        
        # Build PDF
        doc.build(story)
        print(f"[PDF GENERATED] {filepath}")
        return filepath
    
    async def send_telegram_report(self, pdf_path, bot_portfolio):
        """Send report via Telegram"""
        if not self.telegram_bot_token or not self.telegram_chat_ids:
            print("[TELEGRAM] Bot token or chat IDs not configured")
            return False
        
        try:
            bot = Bot(token=self.telegram_bot_token)
            
            # Prepare message text
            message = f"""
📊 *{bot_portfolio['bot_name']} Report - Sept 10, 2025*

💼 Strategy: {bot_portfolio['strategy']}
💰 Total Value: ${bot_portfolio['total_value']:,.2f}
📈 Daily P&L: ${bot_portfolio['daily_pnl']:,.2f}
🎯 Win Rate: {bot_portfolio['win_rate']:.1f}%

Top Positions:
"""
            for pos in bot_portfolio['positions'][:3]:
                emoji = "🟢" if pos['pnl'] > 0 else "🔴"
                message += f"{emoji} {pos['ticker']}: {pos['pnl_pct']:.2f}%\n"
            
            # Send to all configured chat IDs
            for chat_id in self.telegram_chat_ids:
                # Send text message
                await bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
                
                # Send PDF
                with open(pdf_path, 'rb') as pdf:
                    await bot.send_document(
                        chat_id=chat_id,
                        document=pdf,
                        filename=pdf_path.name
                    )
                
                print(f"[TELEGRAM] Report sent to chat {chat_id}")
            
            return True
            
        except Exception as e:
            print(f"[TELEGRAM ERROR] {str(e)}")
            return False
    
    def generate_complete_report(self):
        """Generate complete post-market report with PDFs and Telegram delivery"""
        print("\n" + "="*70)
        print("ENHANCED POST-MARKET REPORT")
        print(f"Date: September 10, 2025")
        print(f"Time: {datetime.now().strftime('%I:%M %p ET')}")
        print("="*70)
        
        # Get market data
        market_data = self.get_market_data_with_fallback()
        
        # Analyze both portfolios
        dee_bot = self.analyze_dee_bot_portfolio()
        shorgan_bot = self.analyze_shorgan_bot_portfolio()
        
        # Display market summary
        print("\n[MARKET SUMMARY]")
        for symbol, data in market_data.items():
            arrow = "↑" if data['change_pct'] > 0 else "↓"
            print(f"  {data['name']}: {data['close']:,.2f} ({arrow}{abs(data['change_pct']):.2f}%)")
        
        # Display DEE-BOT summary
        print(f"\n[{dee_bot['bot_name']} PORTFOLIO]")
        print(f"  Strategy: {dee_bot['strategy']}")
        print(f"  Starting Capital: $100,000")
        if dee_bot.get('message'):
            print(f"  Status: {dee_bot['message']}")
        print(f"  Positions: {len(dee_bot['positions'])}")
        if isinstance(dee_bot['daily_pnl'], str):
            print(f"  Daily P&L: {dee_bot['daily_pnl']}")
        else:
            print(f"  Daily P&L: ${dee_bot['daily_pnl']:,.2f}")
        print(f"  Total Value: ${dee_bot['total_value']:,.2f}")
        print(f"  Win Rate: {dee_bot['win_rate']}")
        
        # Display SHORGAN-BOT summary
        print(f"\n[{shorgan_bot['bot_name']} PORTFOLIO]")
        print(f"  Strategy: {shorgan_bot['strategy']}")
        print(f"  Starting Capital: $100,000")
        if shorgan_bot.get('message'):
            print(f"  Status: {shorgan_bot['message']}")
        print(f"  Positions: {len(shorgan_bot['positions'])}")
        if isinstance(shorgan_bot['daily_pnl'], str):
            print(f"  Daily P&L: {shorgan_bot['daily_pnl']}")
        else:
            print(f"  Daily P&L: ${shorgan_bot['daily_pnl']:,.2f}")
        print(f"  Total Value: ${shorgan_bot['total_value']:,.2f}")
        print(f"  Win Rate: {shorgan_bot['win_rate']}")
        
        # Generate PDFs
        print("\n[GENERATING PDF REPORTS]")
        dee_pdf = self.generate_pdf_report(dee_bot)
        shorgan_pdf = self.generate_pdf_report(shorgan_bot)
        
        # Send via Telegram (if configured)
        if self.telegram_bot_token:
            print("\n[SENDING TELEGRAM REPORTS]")
            asyncio.run(self.send_telegram_report(dee_pdf, dee_bot))
            asyncio.run(self.send_telegram_report(shorgan_pdf, shorgan_bot))
        else:
            print("\n[TELEGRAM] Not configured - Add bot token and chat IDs to enable")
        
        # Combined P&L
        print("\n" + "="*70)
        if isinstance(dee_bot['daily_pnl'], str) or isinstance(shorgan_bot['daily_pnl'], str):
            print("COMBINED DAILY P&L: Data unavailable - Could not retrieve actual trading data")
            print("Note: Both bots started with $100,000 capital each")
        else:
            total_pnl = dee_bot['daily_pnl'] + shorgan_bot['daily_pnl']
            print(f"COMBINED DAILY P&L: ${total_pnl:,.2f}")
        print("="*70)
        
        return {
            'dee_bot': dee_bot,
            'shorgan_bot': shorgan_bot,
            'market_data': market_data,
            'pdfs': [dee_pdf, shorgan_pdf]
        }
    
    def setup_telegram(self, bot_token, chat_ids):
        """Configure Telegram bot credentials"""
        self.telegram_bot_token = bot_token
        self.telegram_chat_ids = chat_ids if isinstance(chat_ids, list) else [chat_ids]
        print(f"[TELEGRAM] Configured with {len(self.telegram_chat_ids)} recipients")

if __name__ == "__main__":
    import os
    
    # Create report generator
    report = EnhancedPostMarketReport()
    
    # Check for Telegram credentials in environment or prompt
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("\n[TELEGRAM SETUP]")
        try:
            setup_telegram = input("Would you like to set up Telegram delivery? (y/n): ").strip().lower()
            
            if setup_telegram == 'y':
                bot_token = input("Enter your Telegram Bot Token: ").strip()
                chat_id = input("Enter your Telegram Chat ID: ").strip()
                
                if bot_token and chat_id:
                    report.setup_telegram(bot_token, [chat_id])
                    print("[TELEGRAM] Configured successfully!")
                else:
                    print("[TELEGRAM] Skipping - no credentials provided")
        except (EOFError, KeyboardInterrupt):
            print("[TELEGRAM] Running in non-interactive mode - skipping setup")
            print("[TELEGRAM] Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env file to enable")
    else:
        # Use environment variables
        report.setup_telegram(bot_token, [chat_id])
        print(f"[TELEGRAM] Using credentials from environment")
    
    # Generate complete report
    report.generate_complete_report()