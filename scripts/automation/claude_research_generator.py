"""
Claude-Powered Deep Research Report Generator
==============================================
Generates comprehensive weekly research reports using Claude AI
with integration to Alpaca market data and Financial Datasets API.

Bot Strategies:
- DEE-BOT: S&P 100 large caps, beta ≈ 1.0, defensive quality focus
- SHORGAN-BOT: U.S. micro/mid caps (<$300M), catalyst-driven momentum

Author: AI Trading Bot System
Date: September 30, 2025
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json
import markdown
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import HexColor
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from html.parser import HTMLParser

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from anthropic import Anthropic
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import (
    StockLatestQuoteRequest,
    StockBarsRequest,
    StockLatestTradeRequest
)
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# System prompt for Claude (defines bot behavior)
DEE_BOT_SYSTEM_PROMPT = """
You are DEE-BOT — a cautious, beta-neutral strategist managing a defensive S&P 100 portfolio.

DEE-BOT STRATEGY RULES:
- Beginning Capital: $100,000
- Universe: S&P 100 large caps only (market cap > $50B)
- Objective: Preserve capital and deliver steady, low-volatility returns
- Benchmark: Competing against SHORGAN-BOT — but prioritize capital preservation

PORTFOLIO CHARACTERISTICS:
- Beta targeting: Maintain portfolio beta ≈ 1.0
- Style: Buy-and-hold with minimal rebalancing
- Cash reserve: ~3% (approximately $3,000)
- Sectors favored: No specific sector preference (diversified across S&P 100)
- Rebalancing rule: Trigger only if beta drifts ≥ 0.15 from target

RISK MANAGEMENT:
- Avoid frequent trading (buy-and-hold philosophy)
- Employ beta hedging when portfolio beta drifts
- Prioritize defensive names with strong fundamentals
- Focus on capital preservation over aggressive returns

CONSTRAINTS:
- NO leverage, NO options, NO shorts - Long-only, full shares
- Order Type: LIMIT DAY orders preferred
- Position sizing: Balanced across 10-12 positions
- Maximum single position: ~10% of portfolio

ANALYSIS FRAMEWORK:
1. Beta Management: Calculate and monitor portfolio beta vs S&P 500
2. Quality Screening: Strong balance sheets, consistent earnings, low debt
3. Dividend Safety: Payout ratio < 60%, 5+ year dividend history
4. Rebalancing Triggers: Only when beta drifts ≥ 0.15 or fundamental deterioration

Required Report Sections:
1. Current Portfolio Assessment (beta calculation, quality scores, risk exposure)
2. Beta Drift Analysis (is rebalancing needed?)
3. Rebalancing Recommendations (if beta ≥ 0.15 drift OR quality concerns)
4. Exact Order Block (format below) - ONLY if rebalancing is triggered
5. Risk And Liquidity Checks
6. Monitoring Plan

ORDER BLOCK FORMAT (strict):
```
Action: buy or sell
Ticker: SYMBOL
Shares: integer (full shares only)
Order type: limit
Limit price: $XX.XX (based on current bid/ask)
Time in force: DAY
Intended execution date: YYYY-MM-DD
Stop loss: $XX.XX (for buys only, -8% from entry)
One-line rationale: Beta impact and quality justification
```

Requirements:
- Be thorough, professional, and data-driven
- Focus on quality over growth
- Minimize trading frequency unless rebalancing is clearly needed
- Maintain portfolio beta ≈ 1.0 at all times
"""


SHORGAN_BOT_SYSTEM_PROMPT = """
You are SHORGAN-BOT — a professional-grade, autonomous portfolio strategist.

SHORGAN-BOT STRATEGY RULES:
- Universe: U.S.-listed small- to mid-cap equities (market cap < $20B)
- Time Horizon: 1–30 day holding periods, based on catalyst-driven events
- Objective: Maximize short-term return within the allowed timeframe
- Benchmark: Competing against DEE-BOT — higher return wins

CONSTRAINTS:
- All trades must involve full-share positions only (no fractional shares)
- You may freely choose between short-term trades or longer holds within the 30-day limit
- All trading decisions must be made before the end of the timeframe

FULL CONTROL OVER:
- Position sizing, risk parameters, stop-losses, and order types
- Concentration or diversification strategy
- Allowable instruments: Stocks (long AND short) and options (e.g., debit spreads)

ANALYSIS FRAMEWORK:
1. Catalyst Calendar: Identify upcoming binary events (FDA, earnings, trials, M&A)
2. Opportunity Screening: Both long and short opportunities based on catalysts
3. Options Strategies: Consider debit spreads for high-conviction binary events
4. Technical Setup: Support/resistance levels, entry/exit points
5. Risk/Reward: Target maximum return, manage risk with stops and position sizing

Required Report Sections:
1. Catalyst Calendar (next 1-30 days with specific dates)
2. Current Portfolio Review (long positions, short positions, options positions)
3. New Opportunities (long, short, or options - ranked by R/R ratio)
4. Exact Order Block (format below)
5. Risk And Liquidity Checks
6. Monitoring Plan (catalyst dates, technical triggers)

ORDER BLOCK FORMAT (strict):
```
Action: buy, sell, buy_to_open, sell_to_open, sell_to_close, buy_to_close
Ticker: SYMBOL
Shares: integer (full shares only) OR Option: [CALL/PUT] strike expiry
Order type: limit
Limit price: $XX.XX
Time in force: DAY or GTC
Intended execution date: YYYY-MM-DD
Catalyst date: YYYY-MM-DD (if applicable)
Stop loss: $XX.XX (or stop condition)
Target price: $XX.XX (expected profit target)
One-line rationale: Catalyst + setup explanation
```

Requirements:
- All decisions must be based on deep, verifiable, and cited research
- Be aggressive, data-driven, and catalyst-focused
- Maximize returns within the 30-day timeframe
- Use full instrument suite: long stocks, short stocks, and options strategically
"""


class ClaudeResearchGenerator:
    """Generate deep research reports using Claude AI"""

    def __init__(self):
        """Initialize API clients"""
        # Claude API
        self.claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Alpaca Trading API (for portfolio data)
        self.dee_trading = TradingClient(
            api_key=os.getenv("ALPACA_API_KEY_DEE"),
            secret_key=os.getenv("ALPACA_SECRET_KEY_DEE"),
            paper=True,
            raw_data=False
        )

        self.shorgan_trading = TradingClient(
            api_key=os.getenv("ALPACA_API_KEY_SHORGAN"),
            secret_key=os.getenv("ALPACA_SECRET_KEY_SHORGAN"),
            paper=True,
            raw_data=False
        )

        # Alpaca Market Data API (for quotes/bars)
        self.market_data = StockHistoricalDataClient(
            api_key=os.getenv("ALPACA_API_KEY_DEE"),
            secret_key=os.getenv("ALPACA_SECRET_KEY_DEE")
        )

    def get_portfolio_snapshot(self, bot_name: str) -> Dict:
        """Get current portfolio holdings and account info"""
        client = self.dee_trading if bot_name == "DEE-BOT" else self.shorgan_trading

        # Get account info
        account = client.get_account()

        # Get all positions
        positions = client.get_all_positions()

        holdings = []
        for pos in positions:
            holdings.append({
                "symbol": pos.symbol,
                "qty": float(pos.qty),
                "side": pos.side,
                "avg_entry_price": float(pos.avg_entry_price),
                "current_price": float(pos.current_price),
                "market_value": float(pos.market_value),
                "unrealized_pl": float(pos.unrealized_pl),
                "unrealized_plpc": float(pos.unrealized_plpc),
                "cost_basis": float(pos.cost_basis)
            })

        return {
            "bot_name": bot_name,
            "cash": float(account.cash),
            "portfolio_value": float(account.portfolio_value),
            "buying_power": float(account.buying_power),
            "equity": float(account.equity),
            "holdings": holdings,
            "position_count": len(holdings)
        }

    def get_market_snapshot(self, tickers: List[str]) -> Dict:
        """Fetch live market data from Alpaca"""
        if not tickers:
            return {}

        try:
            # Get latest quotes
            quotes_req = StockLatestQuoteRequest(symbol_or_symbols=tickers)
            quotes = self.market_data.get_stock_latest_quote(quotes_req)

            # Get latest trades
            trades_req = StockLatestTradeRequest(symbol_or_symbols=tickers)
            trades = self.market_data.get_stock_latest_trade(trades_req)

            snapshot = {}
            for ticker in tickers:
                try:
                    q = quotes[ticker]
                    t = trades[ticker]
                    snapshot[ticker] = {
                        "bid": float(q.bid_price),
                        "ask": float(q.ask_price),
                        "bid_size": int(q.bid_size),
                        "ask_size": int(q.ask_size),
                        "last_trade_price": float(t.price),
                        "last_trade_size": int(t.size),
                        "spread": float(q.ask_price - q.bid_price),
                        "spread_pct": round((q.ask_price - q.bid_price) / q.ask_price * 100, 3)
                    }
                except (KeyError, AttributeError) as e:
                    snapshot[ticker] = {"error": str(e)}

            return snapshot

        except Exception as e:
            print(f"Error fetching market data: {e}")
            return {}

    def get_historical_bars(self, tickers: List[str], days: int = 30) -> Dict:
        """Get historical price bars for technical analysis"""
        if not tickers:
            return {}

        try:
            start_date = datetime.now() - timedelta(days=days)
            bars_req = StockBarsRequest(
                symbol_or_symbols=tickers,
                timeframe=TimeFrame.Day,
                start=start_date
            )
            bars = self.market_data.get_stock_bars(bars_req)

            history = {}
            for ticker in tickers:
                try:
                    ticker_bars = bars[ticker]
                    history[ticker] = {
                        "bars_count": len(ticker_bars),
                        "latest_close": float(ticker_bars[-1].close) if ticker_bars else None,
                        "30d_high": max([float(b.high) for b in ticker_bars]) if ticker_bars else None,
                        "30d_low": min([float(b.low) for b in ticker_bars]) if ticker_bars else None,
                        "30d_avg_volume": sum([int(b.volume) for b in ticker_bars]) / len(ticker_bars) if ticker_bars else None
                    }
                except (KeyError, IndexError, AttributeError) as e:
                    history[ticker] = {"error": str(e)}

            return history

        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return {}

    def generate_research_report(
        self,
        bot_name: str,
        week_number: Optional[int] = None,
        include_market_data: bool = True
    ) -> tuple[str, Dict]:
        """
        Generate comprehensive weekly research report using Claude

        Args:
            bot_name: "DEE-BOT" or "SHORGAN-BOT"
            week_number: Week number in experiment (optional)
            include_market_data: Whether to fetch live market data

        Returns:
            Tuple of (markdown_report, portfolio_data)
        """
        print(f"\n{'='*60}")
        print(f"Generating Claude Research Report for {bot_name}")
        print(f"{'='*60}\n")

        # 1. Get current portfolio
        print("[*] Fetching portfolio snapshot...")
        portfolio = self.get_portfolio_snapshot(bot_name)

        # Store portfolio data for PDF generation
        self.last_portfolio_data = portfolio

        # 2. Get market data for holdings
        market_snapshot = {}
        historical_data = {}

        if include_market_data and portfolio["holdings"]:
            tickers = [h["symbol"] for h in portfolio["holdings"]]
            print(f"[*] Fetching market data for {len(tickers)} holdings...")
            market_snapshot = self.get_market_snapshot(tickers)
            historical_data = self.get_historical_bars(tickers)

        # 3. Build context for Claude
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%I:%M %p ET")

        # Format portfolio holdings
        holdings_text = ""
        for h in portfolio["holdings"]:
            holdings_text += f"""
{h['symbol']}: {h['qty']:.0f} shares @ ${h['avg_entry_price']:.2f} avg
  Current: ${h['current_price']:.2f} | P&L: ${h['unrealized_pl']:+,.2f} ({h['unrealized_plpc']:+.2f}%)
  Market Value: ${h['market_value']:,.2f} | Cost Basis: ${h['cost_basis']:,.2f}
"""

        # Format market data
        market_text = ""
        for ticker, data in market_snapshot.items():
            if "error" not in data:
                market_text += f"""
{ticker}: Bid ${data['bid']:.2f} x {data['bid_size']} | Ask ${data['ask']:.2f} x {data['ask_size']}
  Last: ${data['last_trade_price']:.2f} | Spread: ${data['spread']:.3f} ({data['spread_pct']:.2f}%)
"""

        # Format historical data
        history_text = ""
        for ticker, data in historical_data.items():
            if "error" not in data and data.get("30d_avg_volume"):
                history_text += f"""
{ticker}: 30d Range ${data['30d_low']:.2f} - ${data['30d_high']:.2f}
  Avg Daily Volume: {data['30d_avg_volume']:,.0f} shares
"""

        # 4. Build Claude prompt
        week_text = f"Week {week_number}, " if week_number else ""

        user_prompt = f"""
CONTEXT:
Date: {current_date} {current_time}
Bot: {bot_name}
{week_text}6-Month Live Trading Experiment

CURRENT PORTFOLIO:
Cash Available: ${portfolio['cash']:,.2f}
Portfolio Value: ${portfolio['portfolio_value']:,.2f}
Buying Power: ${portfolio['buying_power']:,.2f}
Position Count: {portfolio['position_count']}

[Current Holdings]
{holdings_text if holdings_text else "No positions"}

[Live Market Data from Alpaca]
{market_text if market_text else "No market data available"}

[30-Day Historical Data]
{history_text if history_text else "No historical data available"}

TASK:
Generate a comprehensive Weekly Deep Research Report following your system prompt structure.

Focus on:
1. {"Quality assessment of current holdings, beta management, rebalancing needs" if bot_name == "DEE-BOT" else "Catalyst proximity, momentum status, new opportunities"}
2. {"Top S&P 100 candidates for rotation" if bot_name == "DEE-BOT" else "Upcoming catalysts in next 7-14 days"}
3. Specific trade recommendations with exact order details
4. Risk management and monitoring plan

Be thorough, data-driven, and actionable. Include specific limit prices based on market data.
"""

        # 5. Call Claude API with Extended Thinking (Deep Research Mode)
        print(f"[*] Calling Claude API (Opus 4.1 with Extended Thinking)...")
        print(f"[*] Deep research mode enabled - this may take 3-5 minutes...")
        system_prompt = DEE_BOT_SYSTEM_PROMPT if bot_name == "DEE-BOT" else SHORGAN_BOT_SYSTEM_PROMPT

        try:
            # Use streaming for Opus 4.1 (required for long-running operations >10 min)
            # Opus 4.1 max output: 32K tokens, so thinking budget must be less
            stream = self.claude.messages.stream(
                model="claude-opus-4-20250514",  # Claude Opus 4.1 for deep research
                max_tokens=32000,  # Maximum for Opus 4.1
                temperature=1.0,  # Required for extended thinking
                thinking={
                    "type": "enabled",
                    "budget_tokens": 16000  # Thinking budget (must be < max_tokens)
                },
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            # Extract text content from stream (skip thinking blocks)
            report_content = ""
            with stream as event_stream:
                for text in event_stream.text_stream:
                    report_content += text

            # Get final response for token usage stats
            response = event_stream.get_final_message()

            # 6. Add header and metadata
            report_header = f"""# CLAUDE DEEP RESEARCH REPORT - {bot_name}
## Week of {datetime.now().strftime("%B %d, %Y")}
### Generated: {current_date} at {current_time}
### Model: Claude Opus 4.1 with Extended Thinking (Anthropic)
### Portfolio Value: ${portfolio['portfolio_value']:,.2f}

---

"""

            full_report = report_header + report_content

            print(f"[+] Report generated successfully!")
            print(f"    Length: {len(full_report)} characters")
            print(f"    Tokens used: ~{response.usage.input_tokens + response.usage.output_tokens}")

            return full_report, portfolio

        except Exception as e:
            print(f"[-] Error calling Claude API: {e}")
            raise

    def save_report(self, report: str, bot_name: str, portfolio_data: Dict = None, export_pdf: bool = True) -> tuple[Path, Optional[Path]]:
        """
        Save report to file system in both Markdown and PDF formats

        Args:
            report: Markdown-formatted report content
            bot_name: "DEE-BOT" or "SHORGAN-BOT"
            portfolio_data: Portfolio snapshot data for PDF enhancements
            export_pdf: Whether to generate PDF version

        Returns:
            Tuple of (markdown_path, pdf_path)
        """
        # Create directory structure for tomorrow's trading date
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        date_str = tomorrow.strftime("%Y-%m-%d")

        report_dir = Path(f"reports/premarket/{date_str}")
        report_dir.mkdir(parents=True, exist_ok=True)

        # Generate filenames - use trading date (tomorrow) for consistency
        bot_slug = bot_name.lower().replace("-", "_")
        md_filename = f"claude_research_{bot_slug}_{date_str}.md"
        pdf_filename = f"claude_research_{bot_slug}_{date_str}.pdf"

        md_filepath = report_dir / md_filename
        pdf_filepath = report_dir / pdf_filename if export_pdf else None

        # Write Markdown file
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"[+] Markdown report saved: {md_filepath}")

        # Generate PDF if requested
        if export_pdf:
            try:
                print(f"[*] Generating PDF report...")
                # Pass portfolio data to PDF generator for visual enhancements
                self._generate_pdf(report, pdf_filepath, bot_name, portfolio_data)
                print(f"[+] PDF report saved: {pdf_filepath}")

                # Send Telegram notification with PDF
                self._send_telegram_notification(pdf_filepath, bot_name, date_str)

            except Exception as e:
                print(f"[-] PDF generation failed: {e}")
                pdf_filepath = None

        return md_filepath, pdf_filepath

    def _generate_pdf(self, markdown_content: str, output_path: Path, bot_name: str, portfolio_data: Dict = None):
        """
        Convert markdown report to professional PDF with visual enhancements

        Includes: portfolio stats, pie charts, holdings tables, P/L breakdowns
        """

        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Define styles
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=12,
            spaceBefore=0,
            leading=30
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#0066cc'),
            spaceAfter=10,
            spaceBefore=20,
            leading=20
        )

        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=HexColor('#333333'),
            spaceAfter=8,
            spaceBefore=15,
            leading=16
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            leading=14,
            spaceAfter=8
        )

        code_style = ParagraphStyle(
            'CustomCode',
            parent=styles['Code'],
            fontSize=9,
            fontName='Courier',
            leftIndent=20,
            rightIndent=20,
            spaceBefore=8,
            spaceAfter=8,
            backColor=HexColor('#f8f8f8'),
            borderColor=HexColor('#0066cc'),
            borderWidth=1,
            borderPadding=8
        )

        # Build story with portfolio summary at top
        story = []

        # Add portfolio visual dashboard if data available
        if portfolio_data:
            story.extend(self._create_portfolio_dashboard(portfolio_data, bot_name, styles))
            story.append(PageBreak())

        # Parse markdown and build rest of report
        lines = markdown_content.split('\n')

        in_code_block = False
        code_lines = []

        for line in lines:
            # Handle code blocks
            if line.startswith('```'):
                if in_code_block:
                    # End code block
                    code_text = '\n'.join(code_lines)
                    story.append(Preformatted(code_text, code_style))
                    story.append(Spacer(1, 0.2*inch))
                    code_lines = []
                in_code_block = not in_code_block
                continue

            if in_code_block:
                code_lines.append(line)
                continue

            # Handle headings
            if line.startswith('# ') and not line.startswith('## '):
                text = line[2:].strip()
                story.append(Paragraph(text, title_style))
            elif line.startswith('## '):
                text = line[3:].strip()
                story.append(Paragraph(text, heading_style))
            elif line.startswith('### '):
                text = line[4:].strip()
                story.append(Paragraph(text, subheading_style))
            elif line.startswith('---'):
                story.append(Spacer(1, 0.1*inch))
            elif line.strip():
                # Regular text - clean markdown formatting
                import re
                text = line

                # First escape XML special chars (except our markers)
                text = text.replace('&', '&amp;')

                # Convert markdown to XML tags
                text = re.sub(r'\*\*(.*?)\*\*', r'|||BOLD_START|||\1|||BOLD_END|||', text)
                text = re.sub(r'\*(.*?)\*', r'|||ITALIC_START|||\1|||ITALIC_END|||', text)

                # Now escape < and >
                text = text.replace('<', '&lt;').replace('>', '&gt;')

                # Replace our markers with actual tags
                text = text.replace('|||BOLD_START|||', '<b>').replace('|||BOLD_END|||', '</b>')
                text = text.replace('|||ITALIC_START|||', '<i>').replace('|||ITALIC_END|||', '</i>')

                try:
                    story.append(Paragraph(text, body_style))
                except:
                    # If paragraph fails, just skip this line
                    pass
            else:
                # Empty line
                story.append(Spacer(1, 0.1*inch))

        # Build PDF
        doc.build(story)

    def _create_portfolio_dashboard(self, portfolio_data: Dict, bot_name: str, styles) -> List:
        """
        Create visual portfolio dashboard with stats, charts, and tables

        Returns list of reportlab flowables (paragraphs, tables, charts)
        """
        elements = []

        # Dashboard title
        dashboard_title = ParagraphStyle(
            'DashboardTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=HexColor('#0066cc'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        elements.append(Paragraph(f"{bot_name} Portfolio Dashboard", dashboard_title))
        elements.append(Spacer(1, 0.2*inch))

        # Portfolio summary stats box
        cash = portfolio_data.get('cash', 0)
        portfolio_value = portfolio_data.get('portfolio_value', 0)
        equity = portfolio_data.get('equity', 0)
        position_count = portfolio_data.get('position_count', 0)

        # Calculate total P&L
        total_unrealized_pl = sum([h.get('unrealized_pl', 0) for h in portfolio_data.get('holdings', [])])
        total_pl_pct = (total_unrealized_pl / (portfolio_value - total_unrealized_pl) * 100) if portfolio_value > total_unrealized_pl else 0

        # Stats table
        stats_data = [
            ['Portfolio Value', f'${portfolio_value:,.2f}'],
            ['Cash Available', f'${cash:,.2f}'],
            ['Equity', f'${equity:,.2f}'],
            ['Unrealized P&L', f'${total_unrealized_pl:+,.2f} ({total_pl_pct:+.2f}%)'],
            ['Positions', str(position_count)]
        ]

        stats_table = Table(stats_data, colWidths=[2.5*inch, 2.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f0f8ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#1a1a1a')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#0066cc')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [HexColor('#ffffff'), HexColor('#f0f8ff')]),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.3*inch))

        # Pie chart for position allocation (if holdings exist)
        holdings = portfolio_data.get('holdings', [])
        if holdings:
            elements.append(Paragraph("Position Allocation", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))

            # Create pie chart
            pie_chart = self._create_pie_chart(holdings)
            elements.append(pie_chart)
            elements.append(Spacer(1, 0.3*inch))

            # Top holdings table with P&L
            elements.append(Paragraph("Current Holdings", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))

            holdings_table = self._create_holdings_table(holdings)
            elements.append(holdings_table)
        else:
            elements.append(Paragraph("No current positions", styles['Normal']))

        elements.append(Spacer(1, 0.2*inch))

        return elements

    def _create_pie_chart(self, holdings: List[Dict]) -> Drawing:
        """Create pie chart showing position allocation"""
        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 150
        pie.y = 50
        pie.width = 120
        pie.height = 120

        # Calculate position percentages
        total_value = sum([h.get('market_value', 0) for h in holdings])

        labels = []
        data = []
        for h in holdings:
            symbol = h.get('symbol', 'UNKNOWN')
            market_value = h.get('market_value', 0)
            pct = (market_value / total_value * 100) if total_value > 0 else 0
            labels.append(f"{symbol} ({pct:.1f}%)")
            data.append(market_value)

        pie.data = data
        pie.labels = labels
        pie.slices.strokeWidth = 0.5

        # Color scheme
        colors_list = [
            HexColor('#0066cc'), HexColor('#ff6b6b'), HexColor('#4ecdc4'),
            HexColor('#ffe66d'), HexColor('#a8e6cf'), HexColor('#ff8b94'),
            HexColor('#c7ceea'), HexColor('#ffd3b6'), HexColor('#ffaaa5'),
            HexColor('#dcedc1')
        ]

        for i, slice_color in enumerate(colors_list[:len(data)]):
            pie.slices[i].fillColor = slice_color

        drawing.add(pie)
        return drawing

    def _create_holdings_table(self, holdings: List[Dict]) -> Table:
        """Create detailed holdings table with P&L"""
        # Sort by market value descending
        sorted_holdings = sorted(holdings, key=lambda x: x.get('market_value', 0), reverse=True)

        # Table header
        table_data = [
            ['Symbol', 'Shares', 'Avg Entry', 'Current', 'Market Value', 'P&L ($)', 'P&L (%)']
        ]

        # Add holdings rows
        for h in sorted_holdings:
            symbol = h.get('symbol', '')
            qty = h.get('qty', 0)
            avg_entry = h.get('avg_entry_price', 0)
            current = h.get('current_price', 0)
            market_value = h.get('market_value', 0)
            pl = h.get('unrealized_pl', 0)
            pl_pct = h.get('unrealized_plpc', 0)

            table_data.append([
                symbol,
                f'{qty:.0f}',
                f'${avg_entry:.2f}',
                f'${current:.2f}',
                f'${market_value:,.2f}',
                f'${pl:+,.2f}',
                f'{pl_pct:+.2f}%'
            ])

        # Create table
        col_widths = [0.8*inch, 0.7*inch, 0.9*inch, 0.9*inch, 1.2*inch, 1.0*inch, 0.9*inch]
        table = Table(table_data, colWidths=col_widths)

        # Style table
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0066cc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Symbol left-aligned
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Numbers right-aligned

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f5f5f5')]),

            # Padding
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))

        return table

    def _send_telegram_notification(self, pdf_path: Path, bot_name: str, trade_date: str):
        """
        Send Telegram notification with PDF attachment

        Args:
            pdf_path: Path to PDF file
            bot_name: "DEE-BOT" or "SHORGAN-BOT"
            trade_date: Trading date (YYYY-MM-DD)
        """
        try:
            import requests

            TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7526351226:AAHQz1PV-4OdNmCgLdgzPJ8emHxIeGdPW6Q")
            CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7769365988")

            # Send PDF as document
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"

            caption = f"📊 *{bot_name} Research Report*\nTrade Date: {trade_date}\nGenerated: {datetime.now().strftime('%I:%M %p ET')}"

            with open(pdf_path, 'rb') as pdf_file:
                files = {'document': pdf_file}
                data = {
                    'chat_id': CHAT_ID,
                    'caption': caption,
                    'parse_mode': 'Markdown'
                }

                response = requests.post(url, data=data, files=files)

                if response.status_code == 200:
                    print(f"\n[+] Telegram PDF sent: {bot_name}")
                    print(f"    Trade Date: {trade_date}")
                    print(f"    File: {pdf_path.name}")
                else:
                    print(f"\n[-] Telegram send failed: {response.text}")

        except Exception as e:
            print(f"\n[-] Telegram notification failed: {e}")


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate Claude-powered research reports")
    parser.add_argument(
        "--bot",
        choices=["dee", "shorgan", "both"],
        default="both",
        help="Which bot to generate report for"
    )
    parser.add_argument(
        "--week",
        type=int,
        help="Week number in experiment"
    )
    parser.add_argument(
        "--no-market-data",
        action="store_true",
        help="Skip fetching live market data"
    )

    args = parser.parse_args()

    # Initialize generator
    generator = ClaudeResearchGenerator()

    # Generate reports
    bots = []
    if args.bot == "both":
        bots = ["DEE-BOT", "SHORGAN-BOT"]
    elif args.bot == "dee":
        bots = ["DEE-BOT"]
    else:
        bots = ["SHORGAN-BOT"]

    for bot_name in bots:
        try:
            report, portfolio_data = generator.generate_research_report(
                bot_name=bot_name,
                week_number=args.week,
                include_market_data=not args.no_market_data
            )

            md_path, pdf_path = generator.save_report(
                report=report,
                bot_name=bot_name,
                portfolio_data=portfolio_data,
                export_pdf=True
            )

            print(f"\n{'='*60}")
            print(f"[+] {bot_name} report complete!")
            print(f"[+] Markdown: {md_path}")
            if pdf_path:
                print(f"[+] PDF: {pdf_path}")
            print(f"{'='*60}\n")

        except Exception as e:
            print(f"\n[-] Error generating {bot_name} report: {e}\n")
            continue


if __name__ == "__main__":
    main()
