"""
Enhanced Telegram Reporter with PDF Generation
Sends comprehensive pre-market analysis with agent reasoning
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import requests
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from dotenv import load_dotenv

load_dotenv()

class TelegramPDFReporter:
    """Generates and sends comprehensive PDF reports via Telegram"""
    
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '-4524457329')
        self.report_dir = '02_data/reports/telegram'
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def generate_premarket_pdf(self, 
                              shorgan_data: Dict,
                              dee_data: Dict,
                              agent_analyses: Dict,
                              executed_trades: List[Dict]) -> str:
        """Generate comprehensive pre-market PDF report"""
        
        timestamp = datetime.now()
        filename = f"premarket_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.report_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2e5090'),
            spaceAfter=12,
            spaceBefore=12
        )
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#3a619c'),
            spaceAfter=6
        )
        
        # Title Page
        elements.append(Paragraph("AI Trading Bot - Pre-Market Analysis", title_style))
        elements.append(Paragraph(timestamp.strftime("%B %d, %Y - %I:%M %p ET"), styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Executive Summary
        elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
        
        summary_data = [
            ['Metric', 'SHORGAN-BOT', 'DEE-BOT'],
            ['Strategy', 'Catalyst-Driven', 'Beta-Neutral'],
            ['Trades Analyzed', str(len(shorgan_data.get('trades', []))), 
             str(len(dee_data.get('trades', [])))],
            ['Trades Executed', str(len([t for t in executed_trades if t.get('bot') == 'SHORGAN'])),
             str(len([t for t in executed_trades if t.get('bot') == 'DEE']))],
            ['Portfolio Value', f"${shorgan_data.get('portfolio_value', 0):,.2f}",
             f"${dee_data.get('portfolio_value', 0):,.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # SHORGAN-BOT Section
        elements.append(PageBreak())
        elements.append(Paragraph("SHORGAN-BOT ANALYSIS", heading_style))
        
        for trade_data in shorgan_data.get('trades', []):
            symbol = trade_data.get('symbol', 'N/A')
            
            # Trade header
            elements.append(Paragraph(f"{symbol} - {trade_data.get('action', 'HOLD').upper()}", subheading_style))
            
            # Agent Analysis Table
            if symbol in agent_analyses:
                analysis = agent_analyses[symbol]
                
                agent_data = [
                    ['Agent', 'Score', 'Key Factors', 'Decision'],
                    ['Fundamental', f"{analysis.get('fundamental', {}).get('score', 0):.1f}/10",
                     analysis.get('fundamental', {}).get('factors', 'N/A'),
                     analysis.get('fundamental', {}).get('recommendation', 'N/A')],
                    ['Technical', f"{analysis.get('technical', {}).get('score', 0):.1f}/10",
                     analysis.get('technical', {}).get('factors', 'N/A'),
                     analysis.get('technical', {}).get('recommendation', 'N/A')],
                    ['News', f"{analysis.get('news', {}).get('score', 0):.1f}/10",
                     analysis.get('news', {}).get('factors', 'N/A'),
                     analysis.get('news', {}).get('recommendation', 'N/A')],
                    ['Sentiment', f"{analysis.get('sentiment', {}).get('score', 0):.1f}/10",
                     analysis.get('sentiment', {}).get('factors', 'N/A'),
                     analysis.get('sentiment', {}).get('recommendation', 'N/A')],
                    ['Bull Case', f"{analysis.get('bull', {}).get('score', 0):.1f}/10",
                     analysis.get('bull', {}).get('factors', 'N/A'),
                     'BULLISH'],
                    ['Bear Case', f"{analysis.get('bear', {}).get('score', 0):.1f}/10",
                     analysis.get('bear', {}).get('factors', 'N/A'),
                     'BEARISH'],
                    ['Risk Manager', f"{analysis.get('risk', {}).get('score', 0):.1f}/10",
                     f"Position: {analysis.get('risk', {}).get('position_size', 0)}%",
                     analysis.get('risk', {}).get('decision', 'N/A')]
                ]
                
                agent_table = Table(agent_data, colWidths=[1.2*inch, 0.8*inch, 3*inch, 1*inch])
                agent_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7ba7')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                elements.append(agent_table)
                
                # Consensus and Decision
                consensus_score = analysis.get('consensus_score', 0)
                elements.append(Spacer(1, 0.1*inch))
                elements.append(Paragraph(
                    f"<b>Consensus Score:</b> {consensus_score:.2f}/10 - "
                    f"<b>Decision:</b> {analysis.get('final_decision', 'HOLD')}",
                    styles['Normal']
                ))
                
                # Trade Details if Executed
                executed = next((t for t in executed_trades 
                               if t.get('symbol') == symbol and t.get('bot') == 'SHORGAN'), None)
                if executed:
                    elements.append(Paragraph(
                        f"<b>EXECUTED:</b> {executed.get('side', '').upper()} "
                        f"{executed.get('qty', 0)} shares @ ${executed.get('price', 0):.2f} "
                        f"at {executed.get('time', 'N/A')}",
                        styles['Normal']
                    ))
                    elements.append(Paragraph(
                        f"<b>Stop Loss:</b> ${executed.get('stop_loss', 0):.2f} | "
                        f"<b>Target:</b> ${executed.get('target', 0):.2f}",
                        styles['Normal']
                    ))
                
                # Catalyst and Reasoning
                elements.append(Spacer(1, 0.1*inch))
                elements.append(Paragraph(
                    f"<b>Catalyst:</b> {trade_data.get('catalyst', 'N/A')}",
                    styles['Normal']
                ))
                elements.append(Paragraph(
                    f"<b>Risk/Reward:</b> {trade_data.get('risk_reward', 'N/A')}",
                    styles['Normal']
                ))
                
            elements.append(Spacer(1, 0.2*inch))
        
        # DEE-BOT Section
        elements.append(PageBreak())
        elements.append(Paragraph("DEE-BOT ANALYSIS", heading_style))
        
        # Beta-Neutral Strategy Overview
        elements.append(Paragraph("Strategy: Beta-Neutral S&P 100 with 2X Leverage", styles['Normal']))
        elements.append(Paragraph(
            f"Portfolio Beta: {dee_data.get('portfolio_beta', 1.0):.2f} | "
            f"Target Beta: 1.0 | Leverage: {dee_data.get('leverage', 2.0):.1f}x",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        for trade_data in dee_data.get('trades', []):
            symbol = trade_data.get('symbol', 'N/A')
            
            # Trade header
            elements.append(Paragraph(f"{symbol} - Score: {trade_data.get('score', 0)}", subheading_style))
            
            # DEE-BOT Metrics Table
            metrics_data = [
                ['Metric', 'Value'],
                ['Beta', f"{trade_data.get('beta', 1.0):.2f}"],
                ['Momentum (5D)', f"{trade_data.get('momentum_5d', 0):.2f}%"],
                ['RSI', f"{trade_data.get('rsi', 50):.0f}"],
                ['Volatility', f"{trade_data.get('volatility', 0):.2%}"],
                ['Position Size', f"{trade_data.get('position_size_pct', 0):.1f}%"]
            ]
            
            metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7ba7')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elements.append(metrics_table)
            
            # Check if executed
            executed = next((t for t in executed_trades 
                           if t.get('symbol') == symbol and t.get('bot') == 'DEE'), None)
            if executed:
                elements.append(Spacer(1, 0.1*inch))
                elements.append(Paragraph(
                    f"<b>EXECUTED:</b> {executed.get('side', '').upper()} "
                    f"{executed.get('qty', 0)} shares @ ${executed.get('price', 0):.2f}",
                    styles['Normal']
                ))
            
            elements.append(Spacer(1, 0.2*inch))
        
        # Risk Management Section
        elements.append(PageBreak())
        elements.append(Paragraph("RISK MANAGEMENT SUMMARY", heading_style))
        
        risk_data = [
            ['Metric', 'SHORGAN-BOT', 'DEE-BOT'],
            ['Total Positions', str(shorgan_data.get('positions', 0)), 
             str(dee_data.get('positions', 0))],
            ['Portfolio Beta', 'N/A', f"{dee_data.get('portfolio_beta', 1.0):.2f}"],
            ['Leverage Used', '1.0x', f"{dee_data.get('leverage', 2.0):.1f}x"],
            ['Max Position Size', '10%', '8%'],
            ['Stop Loss Range', '8-10%', '3%'],
            ['VAR (95%)', f"${shorgan_data.get('var_95', 0):,.2f}",
             f"${dee_data.get('var_95', 0):,.2f}"]
        ]
        
        risk_table = Table(risk_data, colWidths=[2*inch, 2*inch, 2*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(risk_table)
        
        # Footer
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(
            f"Report Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S ET')}",
            styles['Normal']
        ))
        elements.append(Paragraph(
            "AI Trading Bot System - Multi-Agent Consensus Framework",
            styles['Normal']
        ))
        
        # Build PDF
        doc.build(elements)
        logging.info(f"PDF report generated: {filepath}")
        
        return filepath
    
    def send_pdf_via_telegram(self, filepath: str, caption: str = None):
        """Send PDF file via Telegram"""
        
        if not caption:
            caption = f"Pre-Market Analysis Report - {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}"
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendDocument"
            
            with open(filepath, 'rb') as f:
                files = {'document': f}
                data = {
                    'chat_id': self.telegram_chat_id,
                    'caption': caption,
                    'parse_mode': 'HTML'
                }
                
                response = requests.post(url, files=files, data=data)
                
                if response.status_code == 200:
                    logging.info("PDF sent successfully via Telegram")
                    return True
                else:
                    logging.error(f"Failed to send PDF: {response.text}")
                    return False
                    
        except Exception as e:
            logging.error(f"Error sending PDF via Telegram: {e}")
            return False
    
    def send_text_summary(self, executed_trades: List[Dict], 
                         shorgan_value: float, dee_value: float):
        """Send text summary via Telegram"""
        
        message = f"""<b>🤖 AI Trading Bot - Pre-Market Summary</b>
        
📅 {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}

<b>Portfolio Status:</b>
• SHORGAN-BOT: ${shorgan_value:,.2f}
• DEE-BOT: ${dee_value:,.2f}
• <b>Total:</b> ${(shorgan_value + dee_value):,.2f}

<b>Trades Executed:</b> {len(executed_trades)}
"""
        
        if executed_trades:
            message += "\n<b>Executed Trades:</b>\n"
            for trade in executed_trades:
                message += f"• {trade['symbol']}: {trade['side'].upper()} {trade['qty']} @ ${trade.get('price', 0):.2f}\n"
                message += f"  Bot: {trade['bot']} | Stop: ${trade.get('stop_loss', 0):.2f}\n"
        else:
            message += "\n⚠️ No trades executed this session\n"
        
        message += "\n📎 Full PDF report attached with complete agent analysis and reasoning."
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                logging.info("Text summary sent via Telegram")
            else:
                logging.error(f"Failed to send text summary: {response.text}")
                
        except Exception as e:
            logging.error(f"Error sending text summary: {e}")
    
    def generate_and_send_report(self, 
                                shorgan_data: Dict,
                                dee_data: Dict,
                                agent_analyses: Dict,
                                executed_trades: List[Dict]):
        """Generate PDF and send via Telegram with summary"""
        
        # Generate PDF
        pdf_path = self.generate_premarket_pdf(
            shorgan_data, dee_data, agent_analyses, executed_trades
        )
        
        # Send text summary first
        self.send_text_summary(
            executed_trades,
            shorgan_data.get('portfolio_value', 100000),
            dee_data.get('portfolio_value', 100000)
        )
        
        # Send PDF
        caption = f"📊 Complete Pre-Market Analysis - {datetime.now().strftime('%Y-%m-%d')}\n"
        caption += f"✅ {len(executed_trades)} trades executed\n"
        caption += "📈 Full agent reasoning and consensus scores included"
        
        self.send_pdf_via_telegram(pdf_path, caption)
        
        return pdf_path


def test_reporter():
    """Test the Telegram PDF reporter"""
    
    # Sample data for testing
    shorgan_data = {
        'portfolio_value': 103790.37,
        'positions': 14,
        'trades': [
            {
                'symbol': 'MFIC',
                'action': 'long',
                'catalyst': 'Insider buying - CEO purchased $2M worth',
                'risk_reward': '1:3',
                'size_pct': 9
            }
        ],
        'var_95': 5189.52
    }
    
    dee_data = {
        'portfolio_value': 101690.62,
        'positions': 8,
        'portfolio_beta': 0.98,
        'leverage': 1.85,
        'trades': [
            {
                'symbol': 'AAPL',
                'score': 75,
                'beta': 1.05,
                'momentum_5d': 2.3,
                'rsi': 58,
                'volatility': 0.22,
                'position_size_pct': 6.5
            }
        ],
        'var_95': 3050.72
    }
    
    agent_analyses = {
        'MFIC': {
            'fundamental': {'score': 7.5, 'factors': 'P/E 12.3, Strong earnings', 'recommendation': 'BUY'},
            'technical': {'score': 8.0, 'factors': 'Breakout pattern, Volume surge', 'recommendation': 'BUY'},
            'news': {'score': 9.0, 'factors': 'Insider buying catalyst', 'recommendation': 'STRONG BUY'},
            'sentiment': {'score': 7.0, 'factors': 'Positive social mentions', 'recommendation': 'BUY'},
            'bull': {'score': 8.5, 'factors': 'Multiple growth catalysts'},
            'bear': {'score': 4.0, 'factors': 'Limited downside risks'},
            'risk': {'score': 8.0, 'decision': 'APPROVED', 'position_size': 9},
            'consensus_score': 7.43,
            'final_decision': 'BUY'
        }
    }
    
    executed_trades = [
        {
            'symbol': 'MFIC',
            'bot': 'SHORGAN',
            'side': 'buy',
            'qty': 770,
            'price': 12.16,
            'stop_loss': 11.07,
            'target': 15.80,
            'time': '07:22:15'
        }
    ]
    
    # Create reporter and generate report
    reporter = TelegramPDFReporter()
    pdf_path = reporter.generate_and_send_report(
        shorgan_data, dee_data, agent_analyses, executed_trades
    )
    
    print(f"Test report generated and sent: {pdf_path}")


if __name__ == "__main__":
    test_reporter()