"""
Daily Pre-Market Report Generator
Generates comprehensive trading analysis before market open
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

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


def main():
    """
    Main execution function
    """
    logger.info("=" * 80)
    logger.info("Starting Daily Pre-Market Report Generation")
    logger.info("=" * 80)

    try:
        # Create generator instance
        generator = PreMarketReportGenerator()

        # Generate report
        logger.info("Step 1: Generating report content")
        report = generator.generate_report()

        # Save report
        logger.info("Step 2: Saving report to files")
        filepath = generator.save_report(report)

        # Generate and save metadata
        logger.info("Step 3: Saving metadata")
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

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"FATAL ERROR: Report generation failed")
        logger.error(f"Error: {str(e)}")
        logger.error("=" * 80, exc_info=True)
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
