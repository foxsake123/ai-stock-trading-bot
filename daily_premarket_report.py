"""
Daily Pre-Market Report Generator
Generates comprehensive trading analysis before market open
"""

import os
import sys
import json
import logging
import smtplib
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import pytz
import pandas as pd
import yfinance as yf
from anthropic import Anthropic
from dotenv import load_dotenv

# Import schedule configuration
from schedule_config import get_next_trading_day, get_current_time_et

# Load environment variables
load_dotenv()

# Configure logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'daily_premarket.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class PreMarketReportGenerator:
    """
    Generates daily pre-market trading reports using Claude AI
    """

    def __init__(self):
        """
        Initialize the report generator with API clients and configuration
        """
        logger.info("Initializing PreMarketReportGenerator")

        # Load API keys from environment
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.alpaca_api_key = os.getenv('ALPACA_API_KEY')
        self.alpaca_secret_key = os.getenv('ALPACA_SECRET_KEY')

        # Validate API keys
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        if not self.alpaca_api_key or not self.alpaca_secret_key:
            logger.warning("Alpaca API keys not found - portfolio data unavailable")

        # Portfolio configuration
        self.portfolio_value = 100000
        logger.info(f"Portfolio value: ${self.portfolio_value:,}")

        # Trading date configuration
        self.trading_date = get_next_trading_day()
        self.generation_date = get_current_time_et()
        logger.info(f"Trading date: {self.trading_date}")
        logger.info(f"Generation date: {self.generation_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")

        # Initialize Anthropic client
        try:
            self.client = Anthropic(api_key=self.anthropic_api_key)
            logger.info("Anthropic client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise

        # Output directory configuration
        self.output_dir = Path('reports/premarket')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {self.output_dir.absolute()}")

        # Load stock recommendations
        self.recommendations = self.load_recommendations()

    def load_recommendations(self) -> pd.DataFrame:
        """
        Load stock recommendations from CSV or use defaults

        Returns:
            pd.DataFrame: Stock recommendations with columns: Ticker, Strategy, Catalyst, Risk, Conviction
        """
        csv_path = Path('data/daily_recommendations.csv')

        # Try to load from CSV
        if csv_path.exists():
            logger.info(f"Loading recommendations from {csv_path}")
            try:
                df = pd.read_csv(csv_path)
                logger.info(f"Loaded {len(df)} recommendations from CSV")
                return df
            except Exception as e:
                logger.warning(f"Failed to load CSV: {e}. Using default recommendations.")

        # Use default recommendations
        logger.info("Using default stock recommendations")

        default_recommendations = [
            # SHORGAN-BOT stocks (catalyst-driven)
            {
                'Ticker': 'SNDX',
                'Strategy': 'SHORGAN',
                'Catalyst': 'Oct 25 PDUFA for Revuforj',
                'Risk': 9,
                'Conviction': 9
            },
            {
                'Ticker': 'GKOS',
                'Strategy': 'SHORGAN',
                'Catalyst': 'Oct 20 PDUFA for Epioxa',
                'Risk': 7,
                'Conviction': 7
            },
            {
                'Ticker': 'ARWR',
                'Strategy': 'SHORGAN',
                'Catalyst': 'Nov 18 PDUFA for plozasiran',
                'Risk': 8,
                'Conviction': 8
            },
            {
                'Ticker': 'ALT',
                'Strategy': 'SHORGAN',
                'Catalyst': 'Nov 11 Q3 earnings + IMPACT data',
                'Risk': 5,
                'Conviction': 5
            },
            {
                'Ticker': 'CAPR',
                'Strategy': 'SHORGAN',
                'Catalyst': 'Q4 HOPE-3 Phase 3 data',
                'Risk': 6,
                'Conviction': 6
            },
            # DEE-BOT stocks (defensive)
            {
                'Ticker': 'DUK',
                'Strategy': 'DEE',
                'Catalyst': 'Long-term defensive utility',
                'Risk': 8,
                'Conviction': 8
            },
            {
                'Ticker': 'ED',
                'Strategy': 'DEE',
                'Catalyst': 'Long-term defensive utility',
                'Risk': 9,
                'Conviction': 9
            },
            {
                'Ticker': 'PEP',
                'Strategy': 'DEE',
                'Catalyst': 'Long-term defensive consumer staples',
                'Risk': 6,
                'Conviction': 6
            }
        ]

        df = pd.DataFrame(default_recommendations)
        logger.info(f"Loaded {len(df)} default recommendations ({len(df[df['Strategy'] == 'SHORGAN'])} SHORGAN, {len(df[df['Strategy'] == 'DEE'])} DEE)")
        return df

    def fetch_market_data(self) -> Dict:
        """
        Fetch 6pm ET market snapshot: futures, VIX, dollar index, treasury yields

        Returns:
            Dict: Market data for all indicators
        """
        logger.info("Fetching market data snapshot")

        # Market indicators to fetch
        indicators = {
            '^VIX': 'VIX Index',
            'ES=F': 'S&P 500 Futures',
            'NQ=F': 'Nasdaq Futures',
            'RTY=F': 'Russell 2000 Futures',
            'DX-Y.NYB': 'Dollar Index',
            '^TNX': '10-Year Treasury Yield'
        }

        market_data = {}

        for symbol, name in indicators.items():
            try:
                logger.info(f"Fetching {name} ({symbol})")
                ticker = yf.Ticker(symbol)

                # Get current data
                info = ticker.info
                hist = ticker.history(period='2d')

                if len(hist) == 0:
                    logger.warning(f"No data available for {symbol}")
                    continue

                # Get most recent price
                current_price = hist['Close'].iloc[-1]

                # Calculate change percent
                if len(hist) >= 2:
                    previous_close = hist['Close'].iloc[-2]
                    change_percent = ((current_price - previous_close) / previous_close) * 100
                else:
                    change_percent = 0.0

                # Get after-hours price if available
                after_hours_price = None
                if 'postMarketPrice' in info and info['postMarketPrice']:
                    after_hours_price = info['postMarketPrice']
                elif 'regularMarketPrice' in info and info['regularMarketPrice']:
                    after_hours_price = info['regularMarketPrice']

                # Store data
                market_data[symbol] = {
                    'name': name,
                    'current_price': round(current_price, 2),
                    'change_percent': round(change_percent, 2),
                    'after_hours_price': round(after_hours_price, 2) if after_hours_price else None
                }

                logger.info(f"  {name}: ${current_price:.2f} ({change_percent:+.2f}%)")

            except Exception as e:
                logger.error(f"Failed to fetch {symbol} ({name}): {e}")
                # Continue with other indicators even if one fails
                continue

        logger.info(f"Successfully fetched {len(market_data)}/{len(indicators)} market indicators")
        return market_data

    def generate_report(self) -> str:
        """
        Generate the pre-market report

        Returns:
            str: Generated report content
        """
        logger.info("Starting report generation")

        try:
            # Fetch market data snapshot
            market_data = self.fetch_market_data()

            # Create prompt with market data
            prompt = self._create_prompt(market_data)
            logger.info(f"Prompt created ({len(prompt)} characters)")

            # Call Claude API
            report = self.call_claude_api(prompt)
            logger.info(f"Report generated successfully ({len(report)} characters)")

            return report

        except Exception as e:
            logger.error(f"Error generating report: {e}", exc_info=True)
            raise

    def _create_prompt(self, market_data: Dict) -> str:
        """
        Create the prompt for Claude API

        Args:
            market_data: Dictionary of market indicators and their values

        Returns:
            str: Formatted prompt
        """
        # Format market data section
        market_snapshot = "\nMarket Snapshot (6:00 PM ET):\n"
        if market_data:
            for symbol, data in market_data.items():
                name = data['name']
                price = data['current_price']
                change = data['change_percent']
                market_snapshot += f"- {name}: ${price:.2f} ({change:+.2f}%)\n"
        else:
            market_snapshot += "- Market data unavailable\n"

        prompt = f"""Generate a comprehensive pre-market trading report for {self.trading_date}.

Portfolio Information:
- Portfolio Value: ${self.portfolio_value:,}
- Trading Date: {self.trading_date}
- Generation Time: {self.generation_date.strftime('%Y-%m-%d %H:%M:%S %Z')}
{market_snapshot}
Please provide:
1. Market overview and key events
2. Sector analysis
3. Top stock opportunities
4. Risk factors to watch
5. Trading recommendations

Keep the analysis professional, data-driven, and actionable.
"""
        return prompt

    def generate_comprehensive_prompt(self, market_data: Dict) -> str:
        """
        Generate comprehensive hedge-fund-level prompt for Claude

        Args:
            market_data: Dictionary of market indicators and their values

        Returns:
            str: Comprehensive formatted prompt
        """
        # Format trading date
        trading_date_formatted = self.trading_date.strftime('%B %d, %Y')
        generation_time_formatted = self.generation_date.strftime('%B %d, %Y at %I:%M %p %Z')

        # Format market data section
        market_snapshot = ""
        if market_data:
            for symbol, data in market_data.items():
                name = data['name']
                price = data['current_price']
                change = data['change_percent']
                after_hours = data.get('after_hours_price')

                market_snapshot += f"- **{name}**: ${price:.2f} ({change:+.2f}%)"
                if after_hours and after_hours != price:
                    market_snapshot += f" | After-hours: ${after_hours:.2f}"
                market_snapshot += "\n"
        else:
            market_snapshot = "- Market data unavailable at generation time\n"

        # Extract recommendations by strategy
        shorgan_stocks = self.recommendations[self.recommendations['Strategy'] == 'SHORGAN'].to_dict('records')
        dee_stocks = self.recommendations[self.recommendations['Strategy'] == 'DEE'].to_dict('records')

        # Format SHORGAN recommendations
        shorgan_list = ""
        for stock in shorgan_stocks:
            shorgan_list += f"- **{stock['Ticker']}**: {stock['Catalyst']} (Risk: {stock['Risk']}/10, Conviction: {stock['Conviction']}/10)\n"

        # Format DEE recommendations
        dee_list = ""
        for stock in dee_stocks:
            dee_list += f"- **{stock['Ticker']}**: {stock['Catalyst']} (Risk: {stock['Risk']}/10, Conviction: {stock['Conviction']}/10)\n"

        prompt = f"""# COMPREHENSIVE PRE-MARKET TRADING REPORT

## Report Metadata
- **Trading Day**: {trading_date_formatted}
- **Generated**: {generation_time_formatted}
- **Portfolio Value**: ${self.portfolio_value:,}
- **Report Type**: Dual-strategy pre-market analysis (SHORGAN-BOT + DEE-BOT)

---

## INSTRUCTIONS

You are a hedge-fund-level trading analyst generating a comprehensive pre-market research report for a dual-strategy automated trading system. This report must provide actionable, data-driven recommendations for tomorrow's market open ({trading_date_formatted}).

The portfolio operates two distinct strategies:

### SHORGAN-BOT Strategy
- **Objective**: High-conviction catalyst-driven trades
- **Time Horizon**: 2-8 weeks
- **Position Sizing**: 5-7 positions total
- **Capital Allocation**: 10-15% of portfolio per position
- **Focus**: Earnings surprises, FDA approvals, mergers, product launches, regulatory changes
- **Risk Profile**: Aggressive with defined stop-losses

### DEE-BOT Strategy
- **Objective**: Defensive beta-neutral core holdings
- **Time Horizon**: 3-12 months
- **Position Sizing**: 3-5 positions total
- **Capital Allocation**: 60% of portfolio distributed across positions
- **Focus**: S&P 100 stocks with strong fundamentals, dividend safety, low volatility
- **Risk Profile**: Conservative wealth preservation

---

## REQUIRED ANALYSIS SECTIONS

### 1. EXECUTIVE SUMMARY TABLE
Provide a concise overview table:

| Metric | Value |
|--------|-------|
| Market Sentiment | [Bullish/Bearish/Neutral] |
| VIX Level | [Current level and interpretation] |
| Key Catalysts Today | [Top 3 events] |
| Recommended SHORGAN Positions | [Number] |
| Recommended DEE Positions | [Number] |
| Overall Risk Level | [Low/Medium/High] |

### 2. OVERNIGHT MARKET CONTEXT
Analyze what happened while U.S. markets were closed:

**Asian Markets**
- Major index performance (Nikkei, Hang Seng, Shanghai)
- Key economic data releases
- Sector-specific movements

**European Markets**
- FTSE, DAX, CAC performance
- ECB or Bank of England developments
- Commodity price movements (oil, gold, base metals)

**U.S. Futures & Pre-Market**
- S&P 500, Nasdaq, Russell 2000 futures direction
- After-hours earnings reactions
- Major pre-market movers (>3% moves)

**Market Data Snapshot (6:00 PM ET Previous Day)**
{market_snapshot}

### 3. SHORGAN-BOT RECOMMENDATIONS (5-7 TRADES)

**Priority Stocks to Analyze:**
{shorgan_list}

For each recommended position, provide:

**Format:**
#### [TICKER] - [Company Name]
- **Action**: BUY/SHORT
- **Entry Price**: $XX.XX (specific price, not range)
- **Position Size**: XXX shares (calculated from portfolio value)
- **Stop-Loss**: $XX.XX (X% below entry)
- **Price Target**: $XX.XX (X% upside)
- **Time Horizon**: X weeks
- **Catalyst**: [Specific upcoming event with date]
- **Catalyst Timeline**: [Date and expected impact]
- **Risk/Reward Ratio**: X:1
- **Technical Setup**: [Chart pattern, support/resistance levels]
- **Why Now**: [Timing rationale - why this exact entry point]
- **Bear Case**: [What could go wrong]
- **Data Sources**: [Where you got this information]

**Include positions across different catalyst types:**
- 2-3 earnings-driven trades
- 1-2 FDA/regulatory approval plays
- 1-2 technical breakout/breakdown trades
- 0-1 merger arbitrage or event-driven trades

### 4. DEE-BOT RECOMMENDATIONS (3-5 DEFENSIVE STOCKS)

**Priority Stocks to Analyze:**
{dee_list}

For each recommended position, provide:

**Format:**
#### [TICKER] - [Company Name]
- **Action**: BUY
- **Entry Price**: $XX.XX
- **Position Size**: XXX shares (aiming for ~20% portfolio allocation each)
- **Sector**: [Sector name]
- **Dividend Yield**: X.XX%
- **Beta**: X.XX (vs S&P 500)
- **Key Fundamentals**:
  - P/E Ratio: XX.X
  - ROE: XX.X%
  - Debt/Equity: X.XX
  - Free Cash Flow: $XXX million
- **Defensive Qualities**: [Why this is a safe holding]
- **Valuation**: [Fair value analysis]
- **Dividend Safety**: [Payout ratio, coverage analysis]
- **Recent Insider Activity**: [Buys/sells in last 3 months]
- **Institutional Ownership**: [Top holders]

**Portfolio must be beta-neutral (target beta: 0.95-1.05 vs S&P 500)**

### 5. PORTFOLIO MANAGEMENT
**Current Portfolio Review** (if applicable):
- Positions to hold
- Positions to trim or exit
- Stop-loss adjustments

**Cash Management**:
- Recommended cash allocation: X%
- Available buying power: $XXX,XXX
- Reserve for opportunistic trades: $XX,XXX

**Risk Limits**:
- Maximum position size: 15% per SHORGAN trade
- Maximum sector concentration: 30%
- Maximum portfolio beta: 1.2

### 6. EXECUTION GUIDANCE FOR TOMORROW'S OPEN
**Pre-Market (7:00-9:30 AM ET)**:
- Key economic data releases (exact times)
- Earnings reports to watch
- News flow to monitor

**Market Open Strategy (9:30-10:00 AM)**:
- Order types to use (limit vs market)
- Specific entry triggers
- Volume/liquidity considerations

**Intraday Monitoring**:
- FOMC statements, Fed speakers
- Sector rotation patterns
- Technical level breaks

**End-of-Day Actions**:
- GTC stop-loss order placement
- Position sizing adjustments

### 7. ALTERNATIVE DATA INTEGRATION
Incorporate non-traditional data sources:

**Sentiment Analysis**:
- Social media trends (StockTwits, Twitter/X)
- News sentiment scores
- Options flow (unusual activity)

**Supply Chain Signals**:
- Shipping data
- Inventory levels
- Commodity price trends

**Insider Activity**:
- Recent Form 4 filings
- Cluster buying/selling patterns
- C-suite transactions

### 8. RISK DISCLOSURES
Include standard disclaimers:
- Not financial advice
- Past performance doesn't guarantee future results
- Consult licensed financial advisor
- Paper trading account (if applicable)

---

## OUTPUT FORMAT REQUIREMENTS

1. **Use Markdown formatting** throughout
2. **Include tables** for Executive Summary and portfolio allocations
3. **Provide specific entry prices** - never use ranges like "$50-$55"
4. **Include precise timing** - exact dates and times for catalysts
5. **Cite data sources** - where did you get earnings dates, FDA decisions, etc.
6. **Be concise but comprehensive** - aim for 3,000-4,000 words total
7. **Use professional hedge-fund language** - avoid retail trading jargon
8. **Include risk warnings** - this is real money (even if paper trading)

---

## CURRENT MARKET DATA (as of {generation_time_formatted})

{market_snapshot}

---

Now generate the comprehensive pre-market trading report for {trading_date_formatted} following ALL sections and formatting requirements above.
"""
        return prompt

    def generate_mock_report(self, market_data: Dict) -> str:
        """
        Generate a mock report for testing (without API call)

        Args:
            market_data: Dictionary of market indicators

        Returns:
            str: Mock report content
        """
        trading_date_formatted = self.trading_date.strftime('%B %d, %Y')
        generation_time_formatted = self.generation_date.strftime('%B %d, %Y at %I:%M %p %Z')

        # Get recommendation lists
        shorgan_stocks = self.recommendations[self.recommendations['Strategy'] == 'SHORGAN']
        dee_stocks = self.recommendations[self.recommendations['Strategy'] == 'DEE']

        # Format market data
        market_snapshot = ""
        if market_data:
            for symbol, data in market_data.items():
                market_snapshot += f"- **{data['name']}**: ${data['current_price']:.2f} ({data['change_percent']:+.2f}%)\n"
        else:
            market_snapshot = "- Market data unavailable\n"

        mock_report = f"""# Pre-Market Trading Report (TEST MODE)
**Date:** {trading_date_formatted}
**Generated:** {generation_time_formatted}
**Portfolio Value:** ${self.portfolio_value:,}

---

## TEST MODE NOTICE
This is a mock report generated for testing purposes. No AI analysis was performed.

---

## Market Data Snapshot
{market_snapshot}

## SHORGAN-BOT Recommendations ({len(shorgan_stocks)} positions)

"""

        for _, stock in shorgan_stocks.iterrows():
            mock_report += f"""### {stock['Ticker']}
- **Catalyst**: {stock['Catalyst']}
- **Risk Score**: {stock['Risk']}/10
- **Conviction Score**: {stock['Conviction']}/10
- **Entry Price**: [Would be provided by AI analysis]
- **Position Size**: [Would be calculated]
- **Stop-Loss**: [Would be determined]
- **Price Target**: [Would be analyzed]

"""

        mock_report += f"""## DEE-BOT Recommendations ({len(dee_stocks)} positions)

"""

        for _, stock in dee_stocks.iterrows():
            mock_report += f"""### {stock['Ticker']}
- **Strategy**: {stock['Catalyst']}
- **Risk Score**: {stock['Risk']}/10
- **Conviction Score**: {stock['Conviction']}/10
- **Entry Price**: [Would be provided by AI analysis]
- **Position Size**: [Would be calculated]
- **Dividend Yield**: [Would be fetched]
- **Beta**: [Would be analyzed]

"""

        mock_report += """## Execution Guidance
[Would include detailed pre-market, open, and intraday strategies]

## Risk Disclosures
This is a test report. Not financial advice. For testing purposes only.

---

**Generated with Claude Code** - TEST MODE
"""

        return mock_report

    def call_claude_api(self, prompt: str) -> str:
        """
        Call Claude API to generate content

        Args:
            prompt: The prompt to send to Claude

        Returns:
            str: Generated response text
        """
        logger.info("Calling Claude API")

        try:
            response = self.client.messages.create(
                model='claude-sonnet-4-20250514',
                max_tokens=16000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract text from response
            if response.content and len(response.content) > 0:
                text = response.content[0].text
                logger.info(f"Claude API response received ({len(text)} characters)")
                return text
            else:
                raise ValueError("Empty response from Claude API")

        except Exception as e:
            logger.error(f"Claude API call failed: {e}", exc_info=True)
            raise

    def save_report(self, report: str) -> Path:
        """
        Save the generated report to files

        Args:
            report: Report content to save

        Returns:
            Path: Path to the saved report file
        """
        logger.info("Saving report to files")

        try:
            # Create filename with trading date
            filename = f"premarket_report_{self.trading_date.strftime('%Y-%m-%d')}.md"
            filepath = self.output_dir / filename

            # Save report to dated file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to: {filepath}")

            # Also save as latest.md for easy access
            latest_path = self.output_dir / 'latest.md'
            with open(latest_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report also saved as: {latest_path}")

            return filepath

        except Exception as e:
            logger.error(f"Error saving report: {e}", exc_info=True)
            raise

    def generate_metadata(self) -> dict:
        """
        Generate metadata about the report

        Returns:
            dict: Metadata dictionary
        """
        metadata = {
            'trading_date': self.trading_date.isoformat(),
            'generation_date': self.generation_date.isoformat(),
            'portfolio_value': self.portfolio_value,
            'model': 'claude-sonnet-4-20250514',
            'version': '1.0.0'
        }
        return metadata

    def save_metadata(self, metadata: dict) -> Path:
        """
        Save report metadata to JSON file

        Args:
            metadata: Metadata dictionary

        Returns:
            Path: Path to the saved metadata file
        """
        filename = f"premarket_metadata_{self.trading_date.strftime('%Y-%m-%d')}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Metadata saved to: {filepath}")
        return filepath

    def extract_summary(self, report: str) -> str:
        """
        Extract summary from report for email body

        Args:
            report: Full report content

        Returns:
            str: Summary text (max 500 chars)
        """
        lines = report.split('\n')
        summary_lines = []
        char_count = 0

        # Extract first 20 lines or until first ## heading after initial content
        for i, line in enumerate(lines[:30]):
            # Stop at second ## heading (after title)
            if i > 0 and line.startswith('##'):
                break

            summary_lines.append(line)
            char_count += len(line)

            # Stop at 500 characters
            if char_count > 500:
                break

        summary = '\n'.join(summary_lines[:20])

        # Truncate to 500 chars if needed
        if len(summary) > 500:
            summary = summary[:497] + '...'

        return summary

    def send_email_notification(self, report: str, filepath: Path) -> None:
        """
        Send email notification with report attachment

        Args:
            report: Report content
            filepath: Path to saved report file
        """
        # Check if email is enabled
        if os.getenv('EMAIL_ENABLED', '').lower() != 'true':
            logger.info("Email notifications disabled (EMAIL_ENABLED != 'true')")
            return

        logger.info("Preparing email notification...")

        try:
            # Get email configuration from environment
            sender_email = os.getenv('EMAIL_SENDER')
            sender_password = os.getenv('EMAIL_PASSWORD')
            recipient_email = os.getenv('EMAIL_RECIPIENT')

            # Validate email configuration
            if not sender_email or not sender_password or not recipient_email:
                logger.error("Email configuration incomplete. Required: EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT")
                return

            # Format trading date for subject
            trading_date_str = self.trading_date.strftime('%B %d, %Y')

            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f'Pre-Market Report for {trading_date_str} - Generated at 6pm ET'

            # Extract summary and create email body
            summary = self.extract_summary(report)

            # Get recommendation counts
            shorgan_count = len(self.recommendations[self.recommendations['Strategy'] == 'SHORGAN'])
            dee_count = len(self.recommendations[self.recommendations['Strategy'] == 'DEE'])

            body = f"""Pre-Market Trading Report

Trading Date: {trading_date_str}
Generated: {self.generation_date.strftime('%B %d, %Y at %I:%M %p %Z')}
Portfolio Value: ${self.portfolio_value:,}

SHORGAN-BOT Positions: {shorgan_count}
DEE-BOT Positions: {dee_count}

Report Summary:
{summary}

---

The full report is attached as a markdown file.

You can also find the report at:
{filepath.absolute()}

Best regards,
AI Trading Bot
"""

            # Attach body as text
            msg.attach(MIMEText(body, 'plain'))

            # Attach report file
            try:
                with open(filepath, 'rb') as f:
                    attachment = MIMEBase('application', 'octet-stream')
                    attachment.set_payload(f.read())
                    encoders.encode_base64(attachment)
                    attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename={filepath.name}'
                    )
                    msg.attach(attachment)
                logger.info(f"Attached report file: {filepath.name}")
            except Exception as e:
                logger.error(f"Failed to attach report file: {e}")

            # Send email via Gmail SMTP
            logger.info(f"Sending email to {recipient_email}...")

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)

            logger.info("Email notification sent successfully!")

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Email authentication failed: {e}")
            logger.error("Check EMAIL_PASSWORD (use Gmail App Password, not regular password)")
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}", exc_info=True)

    def send_slack_notification(self, report: str) -> None:
        """
        Send Slack webhook notification

        Args:
            report: Report content
        """
        # Check if Slack webhook is configured
        slack_webhook = os.getenv('SLACK_WEBHOOK')
        if not slack_webhook:
            logger.info("Slack notifications disabled (SLACK_WEBHOOK not set)")
            return

        logger.info("Preparing Slack notification...")

        try:
            # Format trading date for header
            trading_date_str = self.trading_date.strftime('%B %d, %Y')

            # Extract summary (truncate to 1000 chars for Slack limit)
            summary = self.extract_summary(report)
            if len(summary) > 1000:
                summary = summary[:997] + '...'

            # Get recommendation counts
            shorgan_count = len(self.recommendations[self.recommendations['Strategy'] == 'SHORGAN'])
            dee_count = len(self.recommendations[self.recommendations['Strategy'] == 'DEE'])

            # Create Slack blocks payload
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"Pre-Market Report for {trading_date_str}",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Generated:*\n{self.generation_date.strftime('%B %d, %Y at %I:%M %p %Z')}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Portfolio Value:*\n${self.portfolio_value:,}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*SHORGAN Positions:*\n{shorgan_count}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*DEE-BOT Positions:*\n{dee_count}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Report Summary:*\n```{summary}```"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "AI Trading Research System"
                        }
                    ]
                }
            ]

            # Send to Slack webhook
            payload = {"blocks": blocks}
            response = requests.post(slack_webhook, json=payload, timeout=10)
            response.raise_for_status()

            logger.info("Slack notification sent successfully!")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Slack notification: {e}")
        except Exception as e:
            logger.error(f"Error preparing Slack notification: {e}", exc_info=True)

    def send_discord_notification(self, report: str) -> None:
        """
        Send Discord webhook notification

        Args:
            report: Report content
        """
        # Check if Discord webhook is configured
        discord_webhook = os.getenv('DISCORD_WEBHOOK')
        if not discord_webhook:
            logger.info("Discord notifications disabled (DISCORD_WEBHOOK not set)")
            return

        logger.info("Preparing Discord notification...")

        try:
            # Format trading date for title
            trading_date_str = self.trading_date.strftime('%B %d, %Y')

            # Extract summary (truncate to 1500 chars for Discord limit)
            summary = self.extract_summary(report)
            if len(summary) > 1500:
                summary = summary[:1497] + '...'

            # Get recommendation counts
            shorgan_count = len(self.recommendations[self.recommendations['Strategy'] == 'SHORGAN'])
            dee_count = len(self.recommendations[self.recommendations['Strategy'] == 'DEE'])

            # Create Discord embed payload
            embed = {
                "title": f"Pre-Market Report for {trading_date_str}",
                "description": f"```\n{summary}\n```",
                "color": 3447003,  # Blue color
                "fields": [
                    {
                        "name": "Generated",
                        "value": self.generation_date.strftime('%B %d, %Y at %I:%M %p %Z'),
                        "inline": True
                    },
                    {
                        "name": "Portfolio Value",
                        "value": f"${self.portfolio_value:,}",
                        "inline": True
                    },
                    {
                        "name": "SHORGAN Positions",
                        "value": str(shorgan_count),
                        "inline": True
                    },
                    {
                        "name": "DEE-BOT Positions",
                        "value": str(dee_count),
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "AI Trading Research System"
                }
            }

            # Send to Discord webhook
            payload = {"embeds": [embed]}
            response = requests.post(discord_webhook, json=payload, timeout=10)
            response.raise_for_status()

            logger.info("Discord notification sent successfully!")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Discord notification: {e}")
        except Exception as e:
            logger.error(f"Error preparing Discord notification: {e}", exc_info=True)

    def send_notifications(self, report: str, filepath: Path) -> None:
        """
        Send all notifications (email, Slack, Discord)

        Args:
            report: Report content
            filepath: Path to saved report file
        """
        logger.info("Sending notifications...")

        # Send email notification
        self.send_email_notification(report, filepath)

        # Send Slack notification
        self.send_slack_notification(report)

        # Send Discord notification
        self.send_discord_notification(report)

        logger.info("Notification process completed")


def main():
    """
    Main execution function
    """
    logger.info("=" * 80)
    logger.info("Starting Daily Pre-Market Report Generation")
    logger.info("=" * 80)

    # Check if ANTHROPIC_API_KEY is set
    if not os.environ.get('ANTHROPIC_API_KEY'):
        error_msg = "Error: ANTHROPIC_API_KEY not set. Add to .env file"
        logger.error(error_msg)
        print(f"\n{error_msg}\n")
        print("Create a .env file in the project root with:")
        print("ANTHROPIC_API_KEY=your_api_key_here\n")
        return 1

    # Check for test mode flag
    test_mode = '--test' in sys.argv
    if test_mode:
        logger.info("Running in TEST MODE (no API calls)")

    try:
        # Create generator instance
        generator = PreMarketReportGenerator()

        # Check next trading day calculation
        try:
            trading_date_str = generator.trading_date.strftime('%B %d, %Y (%A)')
            logger.info(f"Next trading day calculated: {trading_date_str}")
        except Exception as e:
            logger.error(f"Error calculating next trading day: {e}")
            raise

        # Fetch market data
        logger.info("Fetching market data...")
        market_data = generator.fetch_market_data()
        market_data_status = "SUCCESS" if market_data else "FAILED"

        # Get recommendation counts
        shorgan_count = len(generator.recommendations[generator.recommendations['Strategy'] == 'SHORGAN'])
        dee_count = len(generator.recommendations[generator.recommendations['Strategy'] == 'DEE'])

        # Print summary before generating report
        print("\n" + "=" * 80)
        print("PRE-GENERATION SUMMARY")
        print("=" * 80)
        print(f"Trading Date:        {trading_date_str}")
        print(f"Generation Time:     {generator.generation_date.strftime('%B %d, %Y at %I:%M %p %Z')}")
        print(f"SHORGAN Positions:   {shorgan_count}")
        print(f"DEE-BOT Positions:   {dee_count}")
        print(f"Market Data Status:  {market_data_status} ({len(market_data)}/6 indicators)")
        print(f"Test Mode:           {'YES' if test_mode else 'NO'}")
        print("=" * 80 + "\n")

        # Generate report
        if test_mode:
            logger.info("Step 1: Generating mock report (test mode)")
            report = generator.generate_mock_report(market_data)
            print("\nTEST MODE: Mock report generated successfully\n")
        else:
            logger.info("Step 1: Generating report content")
            try:
                prompt = generator.generate_comprehensive_prompt(market_data)
                report = generator.call_claude_api(prompt)
                logger.info(f"Report generated successfully ({len(report)} characters)")
            except Exception as e:
                error_msg = f"Error calling Claude API: {str(e)}"
                logger.error(error_msg, exc_info=True)
                print(f"\n{error_msg}\n")
                raise

        # Save report
        logger.info("Step 2: Saving report to files")
        try:
            filepath = generator.save_report(report)
        except Exception as e:
            error_msg = f"Error saving report: {str(e)}"
            logger.error(error_msg, exc_info=True)
            print(f"\n{error_msg}\n")
            raise

        # Send notifications
        logger.info("Step 3: Sending notifications")
        try:
            generator.send_notifications(report, filepath)
        except Exception as e:
            logger.warning(f"Failed to send notifications: {e}")
            # Don't fail the entire process if notifications fail

        # Generate and save metadata
        logger.info("Step 4: Saving metadata")
        metadata = generator.generate_metadata()
        metadata_path = generator.save_metadata(metadata)

        # Success summary
        logger.info("=" * 80)
        logger.info("Report generation completed successfully!")
        logger.info(f"Report saved to: {filepath}")
        logger.info(f"Metadata saved to: {metadata_path}")
        logger.info(f"Trading date: {generator.trading_date}")
        logger.info("=" * 80)

        return 0

    except ValueError as e:
        logger.error("=" * 80)
        logger.error(f"CONFIGURATION ERROR: {str(e)}")
        logger.error("=" * 80)
        return 1
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"FATAL ERROR: Report generation failed")
        logger.error(f"Error: {str(e)}")
        logger.error("=" * 80, exc_info=True)
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
