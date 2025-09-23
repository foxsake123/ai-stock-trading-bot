"""
OpenAI Research Fetcher
Retrieves daily pre-market analysis from OpenAI API
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any
import openai
from dotenv import load_dotenv
import time
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

load_dotenv()

class OpenAIResearchFetcher:
    """Fetches pre-market research from OpenAI"""
    
    def __init__(self):
        # Set OpenAI API key
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Output directory
        self.output_dir = '02_data/research/reports/pre_market_daily'
        os.makedirs(self.output_dir, exist_ok=True)
        
    def create_research_prompt(self) -> str:
        """Create prompt for OpenAI to generate research"""
        today = datetime.now().strftime('%B %d, %Y')
        
        return f"""Generate pre-market trading recommendations for {today} using SHORGAN-BOT's $100K portfolio.
        
        TRADING STYLE:
        - Aggressive catalyst-driven trades
        - Focus on micro to mid-cap U.S. stocks
        - Long/short equity positions with options overlays
        - Target 5-8 high-conviction trades daily
        - Position sizes: 5-15% per trade
        - Risk/reward minimum 1:2
        
        CATALYST PRIORITIES (in order):
        1. Earnings surprises (especially beats with raised guidance)
        2. Major insider buying/selling (>$1M transactions)
        3. FDA approvals, clinical trial results (biotech)
        4. M&A announcements or rumors
        5. Analyst upgrades/downgrades from major firms
        6. Technical breakouts from key levels
        7. Unusual options activity
        
        For each trade, provide this EXACT JSON structure:
        {{
            "symbol": "TICKER",
            "action": "long" or "short",
            "catalyst": "Specific catalyst description",
            "entry_min": 0.00,
            "entry_max": 0.00,
            "stop": 0.00,
            "target": 0.00,
            "size_pct": 10,
            "profit_taking": {{"price1": 0.5, "price2": 1.0}},
            "risk_reward_ratio": 2.5,
            "confidence_score": 8.5
        }}
        
        Also include market_context with:
        - S&P futures status
        - Key economic releases today
        - VIX level
        - Overall market sentiment
        
        And risk_metrics:
        - portfolio_var_95
        - expected_daily_volatility
        - sharpe_ratio_ytd
        
        Return as valid JSON with keys: "date", "trades" (array), "market_context" (object), "risk_metrics" (object)"""
    
    def fetch_research_from_openai(self) -> Dict:
        """Fetch research from OpenAI API"""
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # or "gpt-4" or "gpt-3.5-turbo"
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional trading analyst providing daily pre-market research."
                    },
                    {
                        "role": "user",
                        "content": self.create_research_prompt()
                    }
                ],
                temperature=0.7,
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            research_text = response.choices[0].message.content
            research_data = json.loads(research_text)
            
            logging.info("Successfully fetched research from OpenAI")
            return research_data
            
        except Exception as e:
            logging.error(f"Error fetching from OpenAI: {e}")
            return None
    
    def fetch_from_custom_gpt(self, custom_gpt_id: str = None) -> Dict:
        """
        Fetch from a specific Custom GPT or Assistant
        Note: You'll need to use the Assistants API for this
        """
        try:
            if custom_gpt_id:
                # Use Assistants API to interact with your custom GPT
                assistant = self.client.beta.assistants.retrieve(custom_gpt_id)
                
                # Create a thread
                thread = self.client.beta.threads.create()
                
                # Send message
                message = self.client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content="Generate today's pre-market trading recommendations"
                )
                
                # Run the assistant
                run = self.client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=assistant.id
                )
                
                # Wait for completion
                while run.status != "completed":
                    time.sleep(1)
                    run = self.client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                
                # Get messages
                messages = self.client.beta.threads.messages.list(thread_id=thread.id)
                
                # Extract research from latest message
                research_text = messages.data[0].content[0].text.value
                
                # Parse if JSON, otherwise convert to structured format
                if research_text.startswith('{'):
                    return json.loads(research_text)
                else:
                    return self.parse_text_to_json(research_text)
            else:
                # Use standard completion if no custom GPT specified
                return self.fetch_research_from_openai()
                
        except Exception as e:
            logging.error(f"Error fetching from custom GPT: {e}")
            return None
    
    def parse_text_to_json(self, text: str) -> Dict:
        """Convert text research to structured JSON"""
        # This would parse your specific format
        # For now, return a template
        return {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "trades": [],
            "market_context": {},
            "raw_text": text
        }
    
    def save_research(self, research: Dict) -> str:
        """Save research to file"""
        try:
            # Save as JSON
            date_str = datetime.now().strftime('%Y-%m-%d')
            json_path = os.path.join(self.output_dir, f'{date_str}_openai_research.json')
            
            with open(json_path, 'w') as f:
                json.dump(research, f, indent=2)
            
            # Also save as markdown for readability
            md_path = os.path.join(self.output_dir, f'{date_str}_pre_market.md')
            md_content = self.json_to_markdown(research)
            
            with open(md_path, 'w') as f:
                f.write(md_content)
            
            # Generate PDF report
            pdf_path = os.path.join(self.output_dir, f'{date_str}_pre_market_report.pdf')
            self.generate_pdf_report(research, pdf_path)
            
            logging.info(f"Research saved to {json_path}, {md_path}, and {pdf_path}")
            return json_path
            
        except Exception as e:
            logging.error(f"Error saving research: {e}")
            return None
    
    def json_to_markdown(self, research: Dict) -> str:
        """Convert JSON research to markdown format"""
        md = f"# Pre-Market Research - {research.get('date', datetime.now().strftime('%Y-%m-%d'))}\n\n"
        
        # Market context
        if 'market_context' in research:
            md += "## Market Context\n"
            for key, value in research['market_context'].items():
                md += f"- **{key}**: {value}\n"
            md += "\n"
        
        # Trades
        if 'trades' in research:
            md += "## Trade Recommendations\n\n"
            for trade in research['trades']:
                md += f"### {trade.get('symbol', 'N/A')}\n"
                md += f"- **Action**: {trade.get('action', 'N/A')}\n"
                md += f"- **Entry**: ${trade.get('entry_min', 0):.2f} - ${trade.get('entry_max', 0):.2f}\n"
                md += f"- **Stop**: ${trade.get('stop', 0):.2f}\n"
                md += f"- **Target**: ${trade.get('target', 0):.2f}\n"
                md += f"- **Size**: {trade.get('size_pct', 0)}%\n"
                md += f"- **Catalyst**: {trade.get('catalyst', 'N/A')}\n\n"
        
        return md
    
    def generate_pdf_report(self, research: Dict, pdf_path: str):
        """Generate PDF report from research data"""
        try:
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=18)
            
            # Container for page elements
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f2937'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#374151'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Title
            title = Paragraph(f"SHORGAN-BOT Pre-Market Report", title_style)
            elements.append(title)
            
            date_para = Paragraph(f"<b>Date:</b> {research.get('date', datetime.now().strftime('%Y-%m-%d'))}", styles['Normal'])
            elements.append(date_para)
            elements.append(Spacer(1, 20))
            
            # Market Context Section
            if 'market_context' in research:
                elements.append(Paragraph("Market Context", heading_style))
                
                context_data = []
                for key, value in research.get('market_context', {}).items():
                    context_data.append([key.replace('_', ' ').title(), str(value)])
                
                if context_data:
                    context_table = Table(context_data, colWidths=[2.5*inch, 4*inch])
                    context_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                        ('PADDING', (0, 0), (-1, -1), 8),
                    ]))
                    elements.append(context_table)
                    elements.append(Spacer(1, 20))
            
            # Trade Recommendations Section
            if 'trades' in research:
                elements.append(Paragraph("Trade Recommendations", heading_style))
                
                # Create trades table
                trade_data = [['Symbol', 'Action', 'Entry Range', 'Stop', 'Target', 'Size %', 'Catalyst']]
                
                for trade in research.get('trades', []):
                    trade_data.append([
                        trade.get('symbol', ''),
                        trade.get('action', '').upper(),
                        f"${trade.get('entry_min', 0):.2f}-${trade.get('entry_max', 0):.2f}",
                        f"${trade.get('stop', 0):.2f}",
                        f"${trade.get('target', 0):.2f}",
                        f"{trade.get('size_pct', 0)}%",
                        trade.get('catalyst', '')[:30] + '...' if len(trade.get('catalyst', '')) > 30 else trade.get('catalyst', '')
                    ])
                
                if len(trade_data) > 1:
                    trades_table = Table(trade_data, colWidths=[0.8*inch, 0.7*inch, 1.2*inch, 0.7*inch, 0.7*inch, 0.6*inch, 2.2*inch])
                    trades_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4b5563')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                        ('PADDING', (0, 0), (-1, -1), 6),
                    ]))
                    elements.append(trades_table)
                    elements.append(Spacer(1, 20))
            
            # Risk Metrics Section
            if 'risk_metrics' in research:
                elements.append(Paragraph("Risk Metrics", heading_style))
                
                risk_data = []
                metrics = research.get('risk_metrics', {})
                
                risk_data.append(['Portfolio VAR (95%)', f"${metrics.get('portfolio_var_95', 0):,.2f}"])
                risk_data.append(['Portfolio VAR (99%)', f"${metrics.get('portfolio_var_99', 0):,.2f}"])
                risk_data.append(['Expected Daily Volatility', f"{metrics.get('expected_daily_volatility', 0):.1%}"])
                risk_data.append(['Sharpe Ratio (YTD)', f"{metrics.get('sharpe_ratio_ytd', 0):.2f}"])
                risk_data.append(['Beta to S&P 500', f"{metrics.get('beta_sp500', 0):.2f}"])
                risk_data.append(['Gross Exposure', f"{metrics.get('gross_exposure', 0):.1%}"])
                risk_data.append(['Net Exposure', f"{metrics.get('net_exposure', 0):.1%}"])
                
                risk_table = Table(risk_data, colWidths=[3*inch, 2*inch])
                risk_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                    ('PADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(risk_table)
                elements.append(Spacer(1, 20))
            
            # Footer
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#6b7280'),
                alignment=TA_CENTER
            )
            
            footer = Paragraph(f"Generated by SHORGAN-BOT Trading System | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style)
            elements.append(Spacer(1, 30))
            elements.append(footer)
            
            # Build PDF
            doc.build(elements)
            logging.info(f"PDF report generated: {pdf_path}")
            
        except Exception as e:
            logging.error(f"Error generating PDF: {e}")
    
    def run(self, custom_gpt_id: str = None) -> Dict:
        """Main execution"""
        logging.info("Fetching research from OpenAI...")
        
        # Fetch research
        if custom_gpt_id:
            research = self.fetch_from_custom_gpt(custom_gpt_id)
        else:
            research = self.fetch_research_from_openai()
        
        if research:
            # Save to files
            self.save_research(research)
            return research
        else:
            logging.error("Failed to fetch research")
            return None

def main():
    """Example usage"""
    # Add OPENAI_API_KEY to your .env file first!
    
    fetcher = OpenAIResearchFetcher()
    
    # Option 1: Use standard GPT-4
    research = fetcher.run()
    
    # Option 2: Use your custom GPT (need the assistant ID)
    # research = fetcher.run(custom_gpt_id="asst_xxxxxxxxxxxxx")
    
    if research:
        print(f"Research fetched: {len(research.get('trades', []))} trades")
    else:
        print("Failed to fetch research")

if __name__ == "__main__":
    main()