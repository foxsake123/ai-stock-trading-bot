"""
Weekly Research Report Generator
================================
Generates comprehensive weekly research reports using Claude AI
with integration to Alpaca market data and Financial Datasets API.

Runs every Sunday at 12:00 PM ET to prepare for the upcoming trading week.

Author: AI Trading Bot System
Date: January 2026
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json

# Add project root and automation directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent))

from anthropic import Anthropic
from alpaca.trading.client import TradingClient
from mcp_financial_tools import FinancialDataToolsProvider
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_weekly_date_instruction() -> str:
    """Generate dynamic date instructions for weekly reports."""
    today = datetime.now()

    # Calculate the upcoming week (Monday to Friday)
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7  # If today is Monday, get next Monday
    if today.weekday() == 6:  # Sunday
        days_until_monday = 1

    week_start = today + timedelta(days=days_until_monday)
    week_end = week_start + timedelta(days=4)  # Friday

    # Get day-by-day breakdown
    day_breakdown = []
    for i in range(5):
        day = week_start + timedelta(days=i)
        day_breakdown.append(f"- {day.strftime('%A, %B %d')}")

    return f"""CRITICAL DATE INSTRUCTION:
- Today is {today.strftime('%A, %B %d, %Y')} (Report Generation Day)
- This report covers the trading week of {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}
- ALL dates must use year {week_start.year}

TRADING DAYS THIS WEEK:
{chr(10).join(day_breakdown)}

When referencing:
- Earnings dates: Use exact dates in {week_start.strftime('%B %Y')}
- Catalyst events: Specify day of week + date
- Economic data: Include release time (usually 8:30 AM ET)
"""


WEEKLY_RESEARCH_SYSTEM_PROMPT = """
You are a senior hedge fund strategist preparing a comprehensive WEEKLY research report for an AI-powered trading system managing three accounts:

1. **DEE-BOT** ($100K Paper) - Defensive S&P 100 large-caps, beta ~ 1.0
2. **SHORGAN Paper** ($100K Paper) - Catalyst-driven small/mid-caps, momentum
3. **SHORGAN Live** ($3K Real Money) - Small-cap catalysts, strict risk management

{DATE_INSTRUCTION}

---

## REPORT STRUCTURE (Target: 800-1200 lines)

### SECTION 1: WEEKLY MARKET OVERVIEW (100-150 lines)

**1.1 Market Performance Recap**
- S&P 500, Nasdaq, Russell 2000: Weekly % change
- VIX: Current level, interpretation
- 10-Year Treasury: Yield and movement
- Dollar Index (DXY): Strength/weakness

**1.2 Sector Heat Map**
| Sector | Weekly % | YTD % | Outlook |
|--------|----------|-------|---------|
Rank all 11 GICS sectors.

**1.3 Economic Calendar This Week**
| Date | Time | Event | Consensus | Prior | Impact |
|------|------|-------|-----------|-------|--------|
Include: CPI, PPI, Retail Sales, Jobless Claims, Fed Speakers, FOMC

**1.4 Earnings Calendar**
| Date | Pre/Post | Ticker | Company | Est. EPS | Relevance |
|------|----------|--------|---------|----------|-----------|
Major S&P 500 earnings + any holdings.

**1.5 Macro Thesis**
- Fed Policy outlook
- Inflation trends
- Growth indicators
- Key risk events

---

### SECTION 2: PORTFOLIO PERFORMANCE REVIEW (100-150 lines)

**2.1 Account Summary**
| Account | Value | Weekly P&L | YTD Return | vs S&P 500 |
|---------|-------|------------|------------|------------|
| DEE-BOT | | | | |
| SHORGAN Paper | | | | |
| SHORGAN Live | | | | |
| **COMBINED** | | | | |

**2.2 Best & Worst Performers**
- Top 5 winners across all accounts
- Top 5 losers across all accounts
- Attribution analysis

**2.3 Last Week's Trade Review**
- Trades executed
- Fill quality
- Missed opportunities
- Lessons learned

---

### SECTION 3: DEE-BOT ANALYSIS ($100K Defensive) (150-200 lines)

**3.1 Portfolio Snapshot**
| Ticker | Shares | Entry | Current | Value | P&L | Weight | Yield |
|--------|--------|-------|---------|-------|-----|--------|-------|

**3.2 Beta Analysis**
- Current Beta: X.XX (Target: 1.0)
- Rebalancing needed? [Yes/No]

**3.3 Position-by-Position Review**
For EACH position:
- Thesis Status: STRONG / INTACT / WEAKENING / BROKEN
- Recent News/Earnings
- Technical Setup
- Action: HOLD / TRIM / EXIT / ADD

**3.4 Weekly Watchlist**
| Ticker | Entry | Stop | Target | Catalyst | Conviction |
|--------|-------|------|--------|----------|------------|
5-7 potential adds from S&P 100.

**3.5 DEE-BOT Trade Recommendations**
```
Action: [BUY/SELL]
Ticker: [SYMBOL]
Shares: [NUMBER]
Order Type: LIMIT DAY
Limit Price: $XX.XX
Stop Loss: $XX.XX
Rationale: [Brief reason]
```

---

### SECTION 4: SHORGAN PAPER ANALYSIS ($100K Catalyst) (150-200 lines)

**4.1 Portfolio Snapshot**
| Ticker | Position | Entry | Current | Value | P&L | Catalyst | Date |
|--------|----------|-------|---------|-------|-----|----------|------|

**4.2 Catalyst Calendar for the Week**
| Date | Ticker | Event | Expected Move | Our Position |
|------|--------|-------|---------------|--------------|

**4.3 Position Reviews**
For each position:
- Catalyst Status: PENDING / PASSED / FAILED
- Price vs Entry
- Action: HOLD / EXIT / ADD

**4.4 New Opportunities (10-15 setups)**
| Ticker | Setup | Entry | Stop | Target | Catalyst | Date | R:R |
|--------|-------|-------|------|--------|----------|------|-----|

**4.5 Short Opportunities (3-5 setups)**
| Ticker | Entry | Cover | Stop | Catalyst | Conviction |
|--------|-------|-------|------|----------|------------|

**4.6 SHORGAN Paper Trade Recommendations**
[Order block format]

---

### SECTION 5: SHORGAN LIVE ANALYSIS ($3K Real Money) (150-200 lines)

**CRITICAL: This is REAL MONEY. Conservative sizing required.**

**5.1 Portfolio Snapshot**
| Ticker | Shares | Entry | Current | Value | P&L | % of Port |
|--------|--------|-------|---------|-------|-----|-----------|

**5.2 Risk Metrics**
- Cash: $XXX (XX%)
- Margin Used: $0 (MUST be zero)
- Max Position: $300 (10% limit)
- Weekly Loss Limit: $450 (15%)

**5.3 Position Reviews**
For each of the 10 positions:
- Original Thesis
- Current Status
- P&L
- Action: HOLD / TRIM / EXIT

**5.4 Weekly Trade Plan**

**SELLS (Execute Monday open)**
| Ticker | Shares | Type | Target Price | Reason |
|--------|--------|------|--------------|--------|

**BUYS (After sells fill)**
| Ticker | Shares | Entry | Stop | Target | Catalyst | Cost |
|--------|--------|-------|------|--------|----------|------|

**Position Sizing Rules:**
- Max position: $300 (10%)
- Stop loss: 15-18% on all
- Take profits: +20%, +30%

**5.5 SHORGAN Live Trade Recommendations**
```
Action: [BUY/SELL]
Ticker: [SYMBOL]
Shares: [NUMBER]
Order Type: LIMIT DAY
Limit Price: $XX.XX
Stop Loss: $XX.XX
Total Cost: $XXX.XX
Rationale: [Brief reason]
```

---

### SECTION 6: RISK MANAGEMENT (50-75 lines)

**6.1 Portfolio Risk**
| Account | Beta | Max DD | Correlation |
|---------|------|--------|-------------|

**6.2 Stop Loss Status**
Flag positions within 5% of stop.

**6.3 Concentration Risk**
- Largest position
- Sector concentration

**6.4 Week's Risk Events**
| Event | Date | Impact | Hedge |
|-------|------|--------|-------|

---

### SECTION 7: TOP 10 CONVICTION TRADES (75-100 lines)

Rank your highest conviction ideas:

| Rank | Account | Ticker | Action | Entry | Stop | Target | Catalyst | R:R | Conv |
|------|---------|--------|--------|-------|------|--------|----------|-----|------|
| 1 | | | | | | | | | 10/10 |
| 2 | | | | | | | | | 9/10 |
...through 10

**Detailed Thesis for Top 3:**
1. [5-7 sentences]
2. [5-7 sentences]
3. [5-7 sentences]

---

### SECTION 8: COMPLETE ORDER BLOCKS

**DEE-BOT ORDERS**
```
Action: [BUY/SELL]
Ticker: [SYMBOL]
Shares: [NUMBER]
Order Type: LIMIT DAY
Limit Price: $XX.XX
Stop Loss: $XX.XX (GTC)
Rationale: [One sentence]
```

**SHORGAN PAPER ORDERS**
[Same format]

**SHORGAN LIVE ORDERS**
[Same format - conservative sizing!]

---

## TOOLS AVAILABLE

You have access to real-time data tools:
1. `get_current_price(ticker)` - Current price
2. `get_multiple_prices(tickers[])` - Batch prices
3. `get_price_history(ticker, days)` - Historical data
4. `get_fundamental_metrics(ticker)` - Fundamentals
5. `get_valuation_multiples(ticker)` - Valuations
6. `get_earnings_history(ticker, quarters)` - Earnings
7. `get_news_sentiment(ticker, limit)` - News

**USE THESE TOOLS** for accurate real-time data!

---

## OUTPUT REQUIREMENTS

1. **Length**: 800-1200 lines minimum
2. **Tables**: Markdown tables throughout
3. **Specificity**: Exact prices, shares, dates
4. **Actionable**: Clear HOLD/BUY/SELL for every position
5. **Risk-Defined**: Entry, stop, target for every trade
6. **Catalyst-Dated**: Specific dates for SHORGAN trades
7. **Conservative**: SHORGAN Live appropriately sized for $3K

---

## PORTFOLIO DATA

{PORTFOLIO_DATA}

---

Generate the comprehensive weekly research report now.
"""


class WeeklyResearchGenerator:
    """Generates weekly research reports using Claude AI."""

    def __init__(self):
        """Initialize the weekly research generator."""
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.tools_provider = FinancialDataToolsProvider()

        # Initialize Alpaca clients
        self._init_alpaca_clients()

        # Output directory
        self.output_dir = Path(__file__).parent.parent.parent / "reports" / "weekly"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _init_alpaca_clients(self):
        """Initialize Alpaca trading clients for all accounts."""
        # DEE-BOT Paper
        self.dee_bot_client = TradingClient(
            os.getenv("ALPACA_API_KEY"),
            os.getenv("ALPACA_SECRET_KEY"),
            paper=True
        )

        # SHORGAN Paper
        self.shorgan_paper_client = TradingClient(
            os.getenv("ALPACA_API_KEY_SHORGAN"),
            os.getenv("ALPACA_SECRET_KEY_SHORGAN"),
            paper=True
        )

        # SHORGAN Live
        self.shorgan_live_client = TradingClient(
            os.getenv("ALPACA_API_KEY_SHORGAN_LIVE"),
            os.getenv("ALPACA_SECRET_KEY_SHORGAN_LIVE"),
            paper=False
        )

    def get_portfolio_snapshot(self, client: TradingClient, account_name: str) -> str:
        """Get portfolio snapshot for an account."""
        try:
            account = client.get_account()
            positions = client.get_all_positions()

            snapshot = f"\n### {account_name}\n"
            snapshot += f"- **Portfolio Value**: ${float(account.portfolio_value):,.2f}\n"
            snapshot += f"- **Cash**: ${float(account.cash):,.2f}\n"
            snapshot += f"- **Buying Power**: ${float(account.buying_power):,.2f}\n"
            snapshot += f"- **Positions**: {len(positions)}\n\n"

            if positions:
                snapshot += "| Ticker | Shares | Avg Entry | Current | Value | P&L | P&L % |\n"
                snapshot += "|--------|--------|-----------|---------|-------|-----|-------|\n"

                for p in sorted(positions, key=lambda x: float(x.unrealized_pl), reverse=True):
                    current_price = float(p.current_price) if p.current_price else 0
                    avg_entry = float(p.avg_entry_price)
                    value = float(p.market_value)
                    pnl = float(p.unrealized_pl)
                    pnl_pct = float(p.unrealized_plpc) * 100

                    snapshot += f"| {p.symbol} | {p.qty} | ${avg_entry:.2f} | ${current_price:.2f} | ${value:,.2f} | ${pnl:+,.2f} | {pnl_pct:+.1f}% |\n"

            return snapshot

        except Exception as e:
            return f"\n### {account_name}\n[Error fetching data: {e}]\n"

    def get_all_portfolios(self) -> str:
        """Get portfolio snapshots for all accounts."""
        portfolios = ""

        portfolios += self.get_portfolio_snapshot(self.dee_bot_client, "DEE-BOT (Paper $100K)")
        portfolios += self.get_portfolio_snapshot(self.shorgan_paper_client, "SHORGAN Paper ($100K)")
        portfolios += self.get_portfolio_snapshot(self.shorgan_live_client, "SHORGAN Live ($3K REAL)")

        return portfolios

    def generate_report(self) -> str:
        """Generate the weekly research report using Claude."""
        print("\n" + "=" * 70)
        print("WEEKLY RESEARCH REPORT GENERATOR")
        print("=" * 70)

        # Get portfolio data
        print("\n[*] Fetching portfolio snapshots...")
        portfolio_data = self.get_all_portfolios()

        # Build the prompt
        date_instruction = get_weekly_date_instruction()
        system_prompt = WEEKLY_RESEARCH_SYSTEM_PROMPT.format(
            DATE_INSTRUCTION=date_instruction,
            PORTFOLIO_DATA=portfolio_data
        )

        print(f"[*] Calling Claude API (Extended Thinking)...")
        print(f"[*] This may take 5-10 minutes for comprehensive analysis...")

        # Get tools
        tools = self.tools_provider.get_tool_definitions()

        # Initial API call
        messages = [{"role": "user", "content": "Generate the comprehensive weekly research report for the upcoming trading week."}]

        response = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16000,
            system=system_prompt,
            tools=tools,
            messages=messages
        )

        # Handle tool use loop
        api_calls = 1
        max_calls = 25

        while response.stop_reason == "tool_use" and api_calls < max_calls:
            api_calls += 1
            print(f"[*] API Call #{api_calls}...")

            # Process tool calls
            tool_results = []
            for content in response.content:
                if content.type == "tool_use":
                    tool_name = content.name
                    tool_input = content.input
                    print(f"    - {tool_name}({json.dumps(tool_input)[:50]}...)")

                    result = self.tools_provider.execute_tool(tool_name, tool_input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": json.dumps(result) if isinstance(result, dict) else str(result)
                    })

            # Continue conversation
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            response = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=16000,
                system=system_prompt,
                tools=tools,
                messages=messages
            )

        # Extract final text
        report_text = ""
        for content in response.content:
            if hasattr(content, 'text'):
                report_text += content.text

        print(f"\n[+] Report generated successfully!")
        print(f"    API Calls: {api_calls}")
        print(f"    Length: {len(report_text):,} characters")

        return report_text

    def save_report(self, report: str) -> Path:
        """Save the weekly report to file."""
        today = datetime.now()

        # Calculate week dates
        days_until_monday = (7 - today.weekday()) % 7
        if today.weekday() == 6:  # Sunday
            days_until_monday = 1
        week_start = today + timedelta(days=days_until_monday)
        week_end = week_start + timedelta(days=4)

        # Create filename
        week_str = f"{week_start.strftime('%Y-%m-%d')}_to_{week_end.strftime('%Y-%m-%d')}"
        filename = f"weekly_research_{week_str}.md"
        filepath = self.output_dir / filename

        # Add header
        header = f"""# Weekly Research Report
## Trading Week: {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}
## Generated: {today.strftime('%A, %B %d, %Y at %I:%M %p ET')}

---

"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header + report)

        print(f"\n[+] Report saved: {filepath}")
        return filepath

    def run(self) -> Path:
        """Run the weekly research generation."""
        report = self.generate_report()
        filepath = self.save_report(report)
        return filepath


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate weekly research report")
    parser.add_argument("--force", action="store_true", help="Force generation regardless of day")
    args = parser.parse_args()

    today = datetime.now()

    # Check if it's Sunday (or force mode)
    if today.weekday() != 6 and not args.force:
        print(f"[!] Today is {today.strftime('%A')}. Weekly reports run on Sundays.")
        print(f"[!] Use --force to generate anyway.")
        return

    print("=" * 70)
    print("WEEKLY RESEARCH REPORT GENERATION")
    print(f"Date: {today.strftime('%A, %B %d, %Y at %I:%M %p')}")
    print("=" * 70)

    generator = WeeklyResearchGenerator()
    filepath = generator.run()

    print("\n" + "=" * 70)
    print("[+] WEEKLY RESEARCH GENERATION COMPLETE")
    print(f"[+] Report: {filepath}")
    print("=" * 70)


if __name__ == "__main__":
    main()
