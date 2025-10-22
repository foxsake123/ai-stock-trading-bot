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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor
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
You are a professional-grade portfolio analyst for DEE-BOT, a defensive large-cap trading strategy.

DEE-BOT STRATEGY RULES:
- Universe: S&P 100 large caps only (market cap > $50B)
- Objective: Beta ≈ 1.0, match market with quality stocks
- Focus: Defensive sectors (Healthcare, Consumer Staples, Utilities)
- Quality Metrics: ROE > 15%, Debt/Equity < 1.0, Dividend yield > 2%
- Position Size: 8% per position, 10-12 positions total
- NO leverage, NO options, NO shorts - Long-only, full shares
- Order Type: LIMIT DAY orders preferred

ANALYSIS FRAMEWORK:
1. Quality Screening: Strong balance sheets, consistent earnings
2. Dividend Safety: Payout ratio < 60%, 5+ year history
3. Beta Management: Portfolio beta should stay near 1.0
4. Risk Management: Stop losses at -8% from entry

Required Report Sections:
1. Current Portfolio Assessment (beta, quality scores, risk exposure)
2. Rebalancing Recommendations (maintain 10-12 positions)
3. Quality Rankings (top S&P 100 candidates)
4. Exact Order Block (format below)
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
One-line rationale: Brief explanation
```

Be thorough, professional, and data-driven. Focus on quality over growth.
"""


SHORGAN_BOT_SYSTEM_PROMPT = """
You are a professional-grade portfolio analyst for SHORGAN-BOT, an aggressive catalyst-driven trading strategy.

SHORGAN-BOT STRATEGY RULES:
- Universe: U.S. micro/mid caps (market cap < $300M preferred)
- Objective: Capture 2-5x momentum plays on catalysts
- Focus: FDA approvals, earnings surprises, insider buying, momentum breakouts
- Catalyst Types: PDUFA dates, Phase 2/3 results, earnings beats, acquisition rumors
- Position Size: 10% per position, 8-10 positions typical
- NO leverage, NO options, NO shorts - Long-only, full shares
- Order Type: LIMIT DAY orders, aggressive limit prices for entry

ANALYSIS FRAMEWORK:
1. Catalyst Calendar: Identify upcoming binary events (FDA, earnings, trials)
2. Momentum Screening: RSI 50-70, volume surges, price breakouts
3. Insider Activity: Recent insider buying, institutional accumulation
4. Technical Setup: Support/resistance levels, entry/exit points
5. Risk/Reward: Target 2-5x upside, stop at -15% or catalyst failure

Required Report Sections:
1. Catalyst Calendar (next 7-14 days with specific dates)
2. Current Portfolio Review (thesis updates, catalyst proximity)
3. New Catalyst Opportunities (ranked by R/R ratio)
4. Exact Order Block (format below)
5. Risk And Liquidity Checks (ADV > $500K, spread < 2%)
6. Monitoring Plan (catalyst dates, technical triggers)

ORDER BLOCK FORMAT (strict):
```
Action: buy or sell
Ticker: SYMBOL
Shares: integer (full shares only)
Order type: limit
Limit price: $XX.XX (aggressive for entry, below ask)
Time in force: DAY
Intended execution date: YYYY-MM-DD
Catalyst date: YYYY-MM-DD (if applicable)
Stop loss: $XX.XX (for buys only, -15% or catalyst failure)
Target price: $XX.XX (expected upside)
One-line rationale: Catalyst + setup explanation
```

Be aggressive, data-driven, and catalyst-focused. We want 2-5x winners.
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
    ) -> str:
        """
        Generate comprehensive weekly research report using Claude

        Args:
            bot_name: "DEE-BOT" or "SHORGAN-BOT"
            week_number: Week number in experiment (optional)
            include_market_data: Whether to fetch live market data

        Returns:
            Markdown-formatted research report
        """
        print(f"\n{'='*60}")
        print(f"Generating Claude Research Report for {bot_name}")
        print(f"{'='*60}\n")

        # 1. Get current portfolio
        print("[*] Fetching portfolio snapshot...")
        portfolio = self.get_portfolio_snapshot(bot_name)

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
        print(f"[*] Calling Claude API (Sonnet 4 with Extended Thinking)...")
        print(f"[*] Deep research mode enabled - this may take 2-3 minutes...")
        system_prompt = DEE_BOT_SYSTEM_PROMPT if bot_name == "DEE-BOT" else SHORGAN_BOT_SYSTEM_PROMPT

        try:
            response = self.claude.messages.create(
                model="claude-sonnet-4-20250514",  # Latest Sonnet 4 model
                max_tokens=16000,
                temperature=1.0,  # Required for extended thinking
                thinking={
                    "type": "enabled",
                    "budget_tokens": 10000  # Extended thinking for deep research
                },
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            # Extract text content (skip thinking blocks)
            report_content = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    report_content += block.text

            # 6. Add header and metadata
            report_header = f"""# CLAUDE DEEP RESEARCH REPORT - {bot_name}
## Week of {datetime.now().strftime("%B %d, %Y")}
### Generated: {current_date} at {current_time}
### Model: Claude Sonnet 4 (Anthropic)
### Portfolio Value: ${portfolio['portfolio_value']:,.2f}

---

"""

            full_report = report_header + report_content

            print(f"[+] Report generated successfully!")
            print(f"    Length: {len(full_report)} characters")
            print(f"    Tokens used: ~{response.usage.input_tokens + response.usage.output_tokens}")

            return full_report

        except Exception as e:
            print(f"[-] Error calling Claude API: {e}")
            raise

    def save_report(self, report: str, bot_name: str, export_pdf: bool = True) -> tuple[Path, Optional[Path]]:
        """
        Save report to file system in both Markdown and PDF formats

        Args:
            report: Markdown-formatted report content
            bot_name: "DEE-BOT" or "SHORGAN-BOT"
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
                self._generate_pdf(report, pdf_filepath, bot_name)
                print(f"[+] PDF report saved: {pdf_filepath}")

                # Send Telegram notification with PDF
                self._send_telegram_notification(pdf_filepath, bot_name, date_str)

            except Exception as e:
                print(f"[-] PDF generation failed: {e}")
                pdf_filepath = None

        return md_filepath, pdf_filepath

    def _generate_pdf(self, markdown_content: str, output_path: Path, bot_name: str):
        """Convert markdown report to professional PDF using reportlab"""

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

        # Parse markdown and build story
        story = []
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
            report = generator.generate_research_report(
                bot_name=bot_name,
                week_number=args.week,
                include_market_data=not args.no_market_data
            )

            md_path, pdf_path = generator.save_report(report, bot_name, export_pdf=True)

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
