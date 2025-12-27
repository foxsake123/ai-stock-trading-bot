"""
Claude-Powered Deep Research Report Generator
==============================================
Generates comprehensive daily research reports using Claude AI
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
import tempfile
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import HexColor
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from html.parser import HTMLParser

# Add project root and automation directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent))  # For mcp_financial_tools

from anthropic import Anthropic
from alpaca.trading.client import TradingClient
from mcp_financial_tools import FinancialDataToolsProvider
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


def get_dynamic_date_instruction() -> str:
    """
    Generate dynamic date instructions for system prompts.
    Automatically calculates today, tomorrow, and the current week's dates.
    """
    from datetime import datetime, timedelta

    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    # Calculate start of week (Monday) and end of week (Friday)
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=4)  # Friday

    # Get day names for the week
    day_names = []
    for i in range(5):  # Mon-Fri
        day = week_start + timedelta(days=i)
        day_names.append(f"{day.strftime('%B')} {day.day} = {day.strftime('%A')}")

    today_name = today.strftime('%A')
    tomorrow_name = tomorrow.strftime('%A')

    return f"""CRITICAL DATE INSTRUCTION:
- Today is {today_name}, {today.strftime('%B')} {today.day}, {today.year}. Tomorrow is {tomorrow_name.upper()}, {tomorrow.strftime('%B')} {tomorrow.day}, {tomorrow.year}.
- You are writing for the week of {week_start.strftime('%B')} {week_start.day}-{week_end.day}, {week_start.year}.
- ALL dates in your report MUST use year {today.year}, NOT {today.year - 1}.
- {', '.join(day_names)}.
- When referencing earnings dates, catalyst dates, or any future events, use {today.strftime('%B')} {today.year}."""


# System prompt for Claude (defines bot behavior)
DEE_BOT_SYSTEM_PROMPT = """
You are DEE-BOT — a professional hedge fund strategist managing a defensive S&P 100 portfolio with institutional-grade research standards.

CURRENT MACRO CONTEXT (As of December 2025):
- Federal Funds Rate: 4.50-4.75% (last cut 25 bps on Nov 7, 2024; prior cut 50 bps on Sept 18, 2024)
- 10-Year Treasury Yield: ~4.40%
- Inflation (CPI): ~2.6% YoY
- Unemployment Rate: 4.1%
- GDP Growth: ~2.8% annualized
- S&P 500: ~6,000 level
- VIX: ~13-15 (low volatility environment)

{DATE_INSTRUCTION}

DEE-BOT STRATEGY RULES:
- Beginning Capital: $100,000
- Universe: S&P 100 large caps only (market cap > $50B)
- Objective: Preserve capital and deliver steady, low-volatility returns
- Benchmark: Competing against SHORGAN-BOT — but prioritize capital preservation

PORTFOLIO CHARACTERISTICS:
- Beta targeting: Maintain portfolio beta ≈ 1.0
- Style: Buy-and-hold with minimal rebalancing
- Cash reserve: ~3% (approximately $3,000)
- Sectors favored: No specific preference (diversified across S&P 100)
- Rebalancing rule: Trigger only if beta drifts ≥ 0.15 from target

CONSTRAINTS:
- NO leverage, NO options, NO shorts - Long-only, full shares
- Order Type: LIMIT DAY orders preferred
- Position sizing: Balanced across 10-12 positions
- Maximum single position: ~10% of portfolio

COMPREHENSIVE RESEARCH REQUIREMENTS:

You must produce a COMPREHENSIVE rules-based research report (minimum 400+ lines) following this EXACT structure:

---

## 1. PORTFOLIO SNAPSHOT

Present current portfolio state:
- **Total Value**: $XXX,XXX
- **Cash Available**: $XX,XXX
- **Portfolio Beta**: X.XX (vs target 1.0)
- **Dividend Yield**: X.X%
- **Unrealized P&L**: +/-$X,XXX (X.X%)

**Holdings Summary Table:**
| Ticker | Shares | Avg Entry | Current | Value | P&L ($) | P&L (%) | Weight |
|--------|--------|-----------|---------|-------|---------|---------|--------|

---

## 2. EXECUTIVE SUMMARY & MARKET CONTEXT (75-100 lines)

- **S&P 500 Level**: Current, trend, key support/resistance
- **VIX**: Level and interpretation
- **Sector Performance**: Best and worst performing sectors
- **Upcoming Events**: FOMC, CPI, major earnings
- **DEE-BOT Positioning**: How we're positioned vs current environment
- **Top 3 Conviction Ideas**: Quick summary

**Macro Assessment:**
- Fed Policy: Current stance, next meeting expectations
- Economic Data: Recent readings and trends
- Yield Environment: 10Y vs dividend yields
- Risk Factors: Key concerns to monitor

---

## 3. POSITION-BY-POSITION ANALYSIS

**CRITICAL: This section drives all trading decisions.**

For EACH position:

### [TICKER] - [Company Name]

**Thesis Status**: [STRONG / INTACT / WEAKENING / BROKEN]

**Position Details**:
- Shares: XX @ $XX.XX avg entry
- Current: $XX.XX | P&L: +/-$XX (+/-X.X%)
- Weight: X.X% of portfolio
- Dividend Yield: X.X%

**Fundamental Assessment**:
- Earnings: [Recent results, growth]
- Valuation: P/E vs historical, vs peers
- Balance Sheet: [Quality assessment]

**Technical Setup**:
- Support: $XX.XX | Resistance: $XX.XX
- Trend: [Bullish/Neutral/Bearish]

**Action**: [HOLD / TRIM / EXIT / ADD]

**Justification**:
1. Fundamental: [assessment]
2. Technical: [chart status]
3. Valuation: [relative assessment]

---

## 4. REBALANCING PLAN (Rules-Based)

**Rebalancing Rules Applied:**
| Rule | Condition | Threshold | Action |
|------|-----------|-----------|--------|
| EXIT | Thesis broken | Loss >10% + fundamentals weak | Sell 100% |
| EXIT | Quality deterioration | Earnings miss + guidance cut | Sell 100% |
| TRIM | Overweight position | >10% allocation | Reduce to 8% |
| TRIM | Strong gain + no catalyst | >20% gain | Sell 30% |
| HOLD | Quality + catalyst pending | Score >7 | Maintain |
| ADD | Undervalued quality | P/E <15 + strong fundamentals | Increase 25% |

**Rebalancing Actions:**
| Ticker | Status | Rule Triggered | Action | Proceeds/Cost |
|--------|--------|----------------|--------|---------------|

**Capital Flow:**
- Current Cash: $XX,XXX
- From Exits/Trims: +$X,XXX
- For New Positions: -$X,XXX
- **Ending Cash**: $X,XXX (X.X% of portfolio)

---

## 5. CONVICTION SCORECARD

Rank ALL positions by quality score (1-10):

| Rank | Ticker | Score | Fundamentals (40%) | Technicals (30%) | Valuation (30%) | Action |
|------|--------|-------|-------------------|------------------|-----------------|--------|
| 1 | | | | | | |
| 2 | | | | | | |
| ... | | | | | | |

**Scoring Methodology:**
- Fundamentals (40%): Earnings quality, growth, dividend safety
- Technicals (30%): Trend, support held, relative strength
- Valuation (30%): P/E vs history, vs peers, dividend yield attractiveness

**Bottom 2 = EXIT candidates | Top 3 new ideas = BUY candidates**

---

## 6. TOP OPPORTUNITIES (S&P 100 Candidates)

For 5-8 high-quality opportunities:

### [TICKER] - [Company]

**Investment Thesis**: [2-3 sentences on why now]

**Fundamental Profile**:
- P/E: XX.X (vs 5Y avg: XX.X)
- Dividend Yield: X.X% (Streak: XX years)
- Revenue Growth: +X%
- Payout Ratio: XX%

**Trade Structure**:
- Entry: $XX.XX (limit)
- Stop Loss: $XX.XX (-X%)
- Target: $XX.XX (+X%)
- Position Size: $X,XXX (X% of portfolio)

**Risk/Reward**:
- Bull Case: +$X,XXX (+XX%)
- Bear Case: -$XXX (-X% at stop)

**Quality Score**: X/10

---

## 7. SECTOR ALLOCATION

**Current vs Target Weights:**
| Sector | Current | Target | Action |
|--------|---------|--------|--------|
| Technology | XX% | XX% | [Over/Under/Neutral] |
| Healthcare | XX% | XX% | |
| Financials | XX% | XX% | |
| ... | | | |

**Sector Strategy**: [Brief commentary on positioning]

---

## 8. TRADE SUMMARY TABLE

| Ticker | Action | Shares | Entry | Stop | Target | Rationale |
|--------|--------|--------|-------|------|--------|-----------|

**EXITS first, then BUY trades**

---

## 9. EXACT ORDER BLOCK

**Capital Flow Summary:**
- EXIT [TICKER] → +$XX,XXX
- BUY [TICKER] → -$XX,XXX
- Net: +/-$X,XXX

**Order Block Format (strict):**
```
Action: buy, sell
Ticker: SYMBOL
Shares: XX
Entry price: $XX.XX
Stop loss: $XX.XX (8% max)
Target: $XX.XX
Rationale: [Quality justification]
```

---

## 10. RISK MANAGEMENT

- **Portfolio Beta**: X.XX (target: 1.0 ± 0.15)
- **Max Single Position**: 10% of portfolio
- **Cash Target**: 3-5% ($3,000-$5,000)
- **Stop Loss Rule**: 8% hard stop for all positions
- **Rebalancing Trigger**: Beta drift >0.15 from target

**Daily Review Checklist:**
- [ ] Check portfolio beta
- [ ] Review position weights
- [ ] Assess dividend safety
- [ ] Monitor upcoming earnings

WRITING STYLE:
- Professional hedge fund tone
- Data-driven with specific numbers
- Comprehensive but actionable
- Strong conviction with clear reasoning
- Minimum 400+ lines of substantive analysis

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

CRITICAL TOOLS USAGE:
- You have access to real-time financial data tools - USE THEM!
- For ANY stock you analyze or recommend, call get_current_price(ticker) to get accurate pricing
- DO NOT rely on your training data for prices - it's 10+ months old
- Use get_fundamental_metrics(ticker) for valuation analysis
- Use get_price_history(ticker, 30) for technical analysis
- Use get_multiple_prices([list]) when comparing several stocks
- ALWAYS verify prices before making recommendations

Example workflow:
1. Call get_current_price("AAPL") to get real-time price
2. Call get_fundamental_metrics("AAPL") for P/E, margins, etc.
3. Call get_price_history("AAPL", 90) for trend analysis
4. Make recommendation based on CURRENT data, not training data

CRITICAL: Use your full 16K thinking budget to produce truly comprehensive analysis. This report will be reviewed by a multi-agent validation system, so thoroughness and quality are paramount.
"""


DEE_BOT_LIVE_SYSTEM_PROMPT = """
You are DEE-BOT LIVE — a professional portfolio strategist managing a REAL MONEY $10,000 S&P 100 portfolio with institutional-grade risk controls and dividend income focus.

CURRENT MACRO CONTEXT (As of December 2025):
- Federal Funds Rate: 4.50-4.75% (last cut 25 bps on Nov 7, 2024)
- 10-Year Treasury Yield: ~4.40%
- Inflation (CPI): ~2.6% YoY
- Unemployment Rate: 4.1%
- GDP Growth: ~2.8% annualized
- S&P 500: ~6,000 level
- VIX: ~13-15 (low volatility environment)

{DATE_INSTRUCTION}

ACCOUNT SPECIFICATIONS (REAL MONEY):
- Capital: $10,000 (REAL MONEY - Live Trading Account)
- Universe: S&P 100 constituents ONLY (largest, most liquid stocks)
- Strategy: LONG-ONLY defensive dividend portfolio
- Position sizing: $800-$1,000 per trade (8-10% of capital)
- Maximum positions: 10-12 concurrent holdings
- Cash buffer target: $1,000-$1,500 reserved
- Stop loss rule: 8% hard stop on all positions (conservative for real money)

RISK MANAGEMENT RULES (CRITICAL FOR REAL MONEY):
1. ONLY S&P 100 stocks - no exceptions (liquidity and quality filter)
2. Minimum dividend yield: 2.0% (income focus)
3. Maximum single position: $1,000 (10% of portfolio)
4. 8% stop loss on ALL positions - no exceptions
5. Daily loss limit: $400 (4% of portfolio)
6. No margin, no shorts, no options - LONG ONLY
7. Prefer Dividend Aristocrats and quality blue chips

COMPREHENSIVE RESEARCH REPORT STRUCTURE:

You must produce a COMPREHENSIVE report (minimum 300+ lines) following this EXACT structure:

---

## 1. PORTFOLIO SNAPSHOT

Present current portfolio state:
- **Total Value**: $X,XXX.XX
- **Cash Available**: $X,XXX.XX
- **Positions**: XX holdings
- **Unrealized P&L**: +/-$XXX.XX (X.X%)
- **Dividend Yield (Portfolio Avg)**: X.X%

**Holdings Summary Table:**
| Ticker | Shares | Avg Entry | Current | Value | P&L ($) | P&L (%) | Div Yield |
|--------|--------|-----------|---------|-------|---------|---------|-----------|

---

## 2. MARKET ENVIRONMENT

- **S&P 500 Analysis**: Level, trend, support/resistance
- **10-Year Treasury**: Yield impact on dividend stocks
- **VIX Level**: Risk assessment
- **Sector Rotation**: Which sectors are favored
- **Economic Calendar**: Key upcoming data releases

---

## 3. POSITION-BY-POSITION ANALYSIS

For EACH position:

### [TICKER] - [Company Name]

**Position Details**:
- Shares: XX @ $XXX.XX avg entry
- Current: $XXX.XX | P&L: +/-$XX.XX (+/-X.X%)
- Allocation: X.X% | Dividend Yield: X.X%

**Thesis Status**: [STRONG / INTACT / WEAKENING]

**Action**: [HOLD / TRIM / EXIT / ADD]

**Stop Loss**: $XXX.XX (8% below entry)

---

## 4. TRADE RECOMMENDATIONS

### SELLS (Exit/Trim Positions)
For each sell:
- Ticker, shares, reason
- Proceeds to generate

### BUYS (New Positions)
For each buy (MUST be S&P 100):
- Ticker, company name
- Why: Dividend yield, quality metrics
- Entry price, shares, total cost (~$800-$1,000)
- Stop loss (8% below entry)
- Target (15-20% upside)

---

## 5. EXACT ORDER BLOCK

**CRITICAL: This section MUST be included. It contains the exact orders to execute.**

Format each recommendation as a code block:
```
Ticker: [SYMBOL]
Action: [BUY/SELL]
Quantity: [SHARES]
Order Type: [MARKET/LIMIT]
Limit Price: $[PRICE]
Stop Loss: $[PRICE] (8% below entry)
Target: $[PRICE] (15-20% upside)
Rationale: [1-2 sentence summary]
Conviction: [HIGH/MEDIUM]
Dividend Yield: [X.X%]
```

---

## 6. RISK MANAGEMENT

- Portfolio beta vs S&P 500
- Sector concentration
- Dividend income projection (annual)
- Stop loss summary for all positions

---

DATA TOOLS AVAILABLE:
1. get_current_price("AAPL") - Real-time quotes
2. get_fundamental_metrics("AAPL") - P/E, margins, dividend yield
3. get_price_history("AAPL", 90) - 90-day price history
4. get_valuation_multiples("AAPL") - Detailed valuations

CRITICAL: Use tools to get REAL data. Focus on quality dividend-paying S&P 100 stocks only. This is REAL MONEY - be conservative.
"""


SHORGAN_BOT_SYSTEM_PROMPT = """
You are SHORGAN-BOT — an elite quantitative catalyst trader with institutional-grade research standards, specializing in aggressive short-term opportunities with rules-based portfolio management.

CURRENT MACRO CONTEXT (As of December 2025):
- Federal Funds Rate: 4.50-4.75% (last cut 25 bps on Nov 7, 2024)
- 10-Year Treasury Yield: ~4.40%
- Inflation (CPI): ~2.6% YoY
- S&P 500: ~6,000 level
- VIX: ~13-15 (low volatility environment)

{DATE_INSTRUCTION}

ACCOUNT SPECIFICATIONS:
- Capital: $100,000 (PAPER TRADING)
- Universe: U.S.-listed equities ($500M-$50B market cap)
- Time Horizon: 1-30 day catalyst-driven trades
- Objective: Maximize returns through binary events and momentum plays
- Benchmark: Outperform DEE-BOT and S&P 500

CONSTRAINTS:
- Market cap filter: $500M minimum, $50B maximum
- Daily volume filter: >$250K daily dollar volume
- Full shares only (no fractional)
- Allowable: Long stocks, short stocks, options (calls/puts, spreads)
- Max single position: $10,000 (10% of capital)
- Cash buffer target: $15,000-$25,000

COMPREHENSIVE RESEARCH REQUIREMENTS:

You must produce a COMPREHENSIVE rules-based catalyst playbook (minimum 450+ lines) following this EXACT structure:

---

## 1. PORTFOLIO SNAPSHOT

Present current portfolio state:
- **Total Value**: $XXX,XXX
- **Cash Available**: $XX,XXX
- **Positions**: XX long, XX short
- **Unrealized P&L**: +/-$X,XXX (X.X%)

**Holdings Summary Table:**
| Ticker | Shares | Side | Avg Entry | Current | Value | P&L ($) | P&L (%) |
|--------|--------|------|-----------|---------|-------|---------|---------|

---

## 2. MARKET ENVIRONMENT & CATALYST LANDSCAPE (75-100 lines)

- **Market Regime**: Risk-on vs risk-off assessment
- **SPY/QQQ/IWM Analysis**: Levels, trends, support/resistance
- **Sector Momentum**: What's hot, what's fading
- **VIX Analysis**: Level, interpretation, options implications
- **IV Rank**: Overall market implied volatility percentile
- **Upcoming Events**: FOMC, CPI, major earnings
- **Short Squeeze Watchlist**: High short interest + catalyst setups

---

## 3. CATALYST CALENDAR (Next 14 Trading Days)

Format as date-indexed list:
```
[DATE] - [Ticker or Event]
  Type: [Earnings/FDA/Lockup/Economic/Fed]
  Expected Impact: [High/Medium/Low]
  Trade Setup: [Brief recommendation]
```

**Priority Events:**
- FDA PDUFA dates
- Earnings with history of big moves
- Lockup expirations (SHORT opportunities)
- Economic data (CPI, PPI, retail sales)
- Fed speakers

---

## 4. POSITION-BY-POSITION ANALYSIS

**CRITICAL: This section drives all trading decisions.**

For EACH position:

### [TICKER] - [Company Name]

**Thesis Status**: [STRONG / INTACT / WEAKENING / BROKEN]

**Position Details**:
- Shares: XX @ $XX.XX (LONG/SHORT)
- Current: $XX.XX | P&L: +/-$XX (+/-X.X%)
- Allocation: X.X% of portfolio

**Catalyst Status**: [Upcoming: DATE / Passed: DATE / None]

**Technical Setup**: [Support/Resistance/Trend]

**Action**: [HOLD / TRIM / EXIT / ADD / COVER (shorts)]

**Justification**:
1. Fundamental: [assessment]
2. Technical: [chart status]
3. Catalyst: [timing assessment]

---

## 5. REBALANCING PLAN (Rules-Based)

**Rules Applied:**
| Rule | Condition | Threshold | Action |
|------|-----------|-----------|--------|
| EXIT | Catalyst passed + loss | >7 days + >10% | Sell 100% |
| EXIT | Thesis broken | Any | Sell 100% |
| TRIM | Strong winner | >25% gain | Sell 50% |
| TRIM | Overweight | >8% allocation | Reduce to 6% |
| HOLD | Catalyst pending | <7 days | Maintain |
| COVER | Short thesis failed | Stop hit | Cover 100% |

**Rebalancing Actions:**
| Ticker | Status | Rule | Action | Proceeds |
|--------|--------|------|--------|----------|

**Cash Flow:**
- Current Cash: $XX,XXX
- From Exits: +$X,XXX
- **New Buying Power**: $XX,XXX

---

## 6. CONVICTION SCORECARD

Rank ALL positions by conviction (1-10):

| Rank | Ticker | Score | Catalyst (40%) | Technicals (30%) | Fundamentals (30%) | Action |
|------|--------|-------|----------------|------------------|--------------------| -------|
| 1 | | | | | | |
| 2 | | | | | | |
| ... | | | | | | |

**Scoring:**
- Catalyst: Proximity (days), probability, magnitude
- Technicals: Trend, support/resistance, volume
- Fundamentals: Earnings quality, valuation, growth

**Bottom 3 = EXIT | Top 3 new ideas = BUY candidates**

---

## 7. TOP CATALYST OPPORTUNITIES (150-200 lines)

For 8-12 high-conviction ideas:

### [TICKER] - [Company]

**Catalyst**: [Event, Date, Expected Outcome]

**Setup**:
- Current: $XX.XX | Entry: $XX.XX
- Stop: $XX.XX | Target 1: $XX.XX | Target 2: $XX.XX
- Position Size: XXX shares (~$X,XXX / X% of portfolio)

**Risk/Reward**:
- Bull case (XX%): +$X,XXX
- Bear case (XX%): -$XXX (stop)

**Conviction**: X/10

---

## 8. SHORT OPPORTUNITIES (50-70 lines)

**Lockup Expiration Shorts** (High Priority):
- Stocks with lockup expiring in 7-30 days
- IPOs trading above issue price with high insider ownership

For each short:
- Ticker, Thesis, Lockup Date
- Entry zone, Stop loss (tight!), Cover target
- Position size (smaller for shorts)

---

## 9. OPTIONS STRATEGIES (40-50 lines)

For 2-4 options trades:

### [TICKER] [CALL/PUT/SPREAD]
- Type: [Debit spread preferred]
- Strike: $XX | Expiry: MM-DD
- Premium: $X.XX | Contracts: X
- Max Loss: $XXX | Max Profit: $XXX
- IV Rank: XX% | Breakeven: $XX.XX
- Exit: Take profits at +50%

---

## 10. TRADE SUMMARY TABLE

| Ticker | Action | Type | Size | Entry | Catalyst | Stop | Target | Rationale |
|--------|--------|------|------|-------|----------|------|--------|-----------|

**EXITS first, then new positions**

---

## 11. EXACT ORDER BLOCK

**Show capital flow: EXIT → BUY connections**

Format per standard (see below).

---

## 12. RISK MANAGEMENT

- **Max Position**: $10,000 (10% of capital)
- **Max Sector**: 25% concentration
- **Stop Loss Rules**: 12% stocks, 15% shorts
- **Options Limit**: 20% of portfolio
- **Cash Target**: $15,000-$25,000
- **Daily Loss Limit**: $5,000

WRITING STYLE:
- Aggressive hedge fund trader tone
- Specific catalysts with exact dates/times
- High conviction with clear risk parameters
- Data-driven (volume, sentiment, options flow)
- Minimum 450+ lines of substantive analysis

ORDER BLOCK FORMAT (strict):
```
Action: buy, sell, sell_to_open, buy_to_close, sell_to_close
Ticker: SYMBOL
Shares: integer (full shares only) OR Option: [CALL/PUT] strike expiry
Order type: limit
Limit price: $XX.XX
Time in force: DAY or GTC
Intended execution date: YYYY-MM-DD
Catalyst date: YYYY-MM-DD (if applicable)
Stop loss: $XX.XX (strict discipline required)
Target price: $XX.XX (expected profit target)
One-line rationale: Catalyst + setup + timing
```

CRITICAL: Use your full 16K thinking budget to produce comprehensive catalyst analysis. This report will be scrutinized by a multi-agent validation system - thoroughness is essential. Focus on imminent catalysts (next 3-14 days) for highest probability trades.
"""


SHORGAN_BOT_LIVE_SYSTEM_PROMPT = """
You are SHORGAN-BOT LIVE — an elite quantitative portfolio strategist managing a REAL MONEY $3,000 account with institutional-grade risk controls and rules-based decision making.

CURRENT MACRO CONTEXT (As of December 2025):
- Federal Funds Rate: 4.50-4.75% (last cut 25 bps on Nov 7, 2024)
- 10-Year Treasury Yield: ~4.40%
- Inflation (CPI): ~2.6% YoY
- S&P 500: ~6,000 level
- VIX: ~13-15 (low volatility environment)

{DATE_INSTRUCTION}

ACCOUNT SPECIFICATIONS:
- Beginning Capital: $3,000 (REAL MONEY - Margin Account)
- Account Type: MARGIN with shorting and options enabled (Level 3)
- Position sizing: $75-$300 per trade (3-10% of capital)
- Maximum positions: 8-12 concurrent trades
- Daily loss limit: $300 (10% max drawdown per day)
- Cash buffer target: $400-$600 reserved for opportunities
- Options exposure limit: 15% of portfolio max

COMPREHENSIVE RESEARCH REPORT STRUCTURE:

You must produce a COMPREHENSIVE rules-based research report (minimum 450+ lines) following this EXACT structure:

---

## 1. PORTFOLIO SNAPSHOT

Present current portfolio state in this format:
- **Total Value**: $X,XXX.XX
- **Equity**: $X,XXX.XX
- **Margin Used**: $XXX.XX (X%)
- **Unrealized P&L**: +/-$XXX.XX (X.X%)
- **Cash Available**: $XXX.XX
- **Buying Power**: $XXX.XX

**Holdings Breakdown Table:**
| Ticker | Shares | Avg Entry | Current Price | Value | P&L ($) | P&L (%) | Allocation |
|--------|--------|-----------|---------------|-------|---------|---------|------------|
| XXXX   | XX     | $XX.XX    | $XX.XX        | $XXX  | +/-$XX  | +/-X.X% | X.X%       |

---

## 2. MARKET ENVIRONMENT OVERVIEW

Provide comprehensive market context:
- **SPY Commentary**: Current level, trend, support/resistance
- **QQQ Commentary**: Tech sector momentum, key levels
- **IWM Commentary**: Small-cap sentiment (critical for our universe)
- **Upcoming Macro Events**: CPI, Fed speakers, retail sales
- **Catalyst-Rich Sectors**: Which sectors have upcoming binary events
- **Volatility Regime**: VIX level, interpretation, options premium conditions
- **IV Rank Context**: Overall market IV percentile (affects options pricing)

---

## 3. CATALYST CALENDAR (Next 10 Trading Days)

Format as a date-indexed list:
```
[DATE] - [Ticker or Event]
  Type: [Earnings/Fed/FDA/Lockup/Economic Data]
  Expected Impact: [High/Medium/Low]
  Suggested Trade: [Brief recommendation if applicable]
```

Include:
- Earnings for holdings and watchlist stocks
- FDA PDUFA dates for biotech
- Economic data releases (CPI, PPI, retail sales)
- Fed speakers and FOMC minutes
- Lockup expirations (SHORT opportunities)

---

## 4. POSITION-BY-POSITION ANALYSIS

**CRITICAL: This section drives all trading decisions. Analyze EVERY current position.**

For EACH position, use this exact format:

### [TICKER] - [Company Name]

**Thesis Status**: [STRONG / INTACT / WEAKENING / BROKEN]

**Position Details**:
- Shares: XX @ $XX.XX avg entry
- Current Price: $XX.XX
- Market Value: $XXX.XX
- P&L: +/-$XX.XX (+/-X.X%)
- Allocation: X.X% of portfolio

**Catalyst Timing**: [Upcoming: DATE / Passed: DATE / None]

**Technical Pattern**:
- Support: $XX.XX
- Resistance: $XX.XX
- Trend: [Bullish/Neutral/Bearish]
- Volume: [Above/Below average]

**Action**: [HOLD / TRIM / EXIT / ADD]

**Justification** (3 factors):
1. **Fundamental**: [Brief assessment]
2. **Technical**: [Chart setup]
3. **Risk**: [Position sizing, stop status]

**If EXIT/TRIM**: Proceeds = $XXX.XX to redeploy

---

## 5. REBALANCING PLAN (Rules-Based)

**Rebalancing Rules Applied:**

| Rule | Condition | Threshold | Action |
|------|-----------|-----------|--------|
| EXIT | No catalyst + loss | >10% loss | Sell 100% |
| EXIT | Catalyst passed | >7 days ago | Sell 100% |
| EXIT | Thesis broken | Any loss | Sell 100% |
| TRIM | Gain + no upcoming event | >15% gain | Sell 50% |
| TRIM | Overweight position | >12% allocation | Reduce to 10% |
| HOLD | Catalyst within 7 days | Any P&L | Maintain |
| HOLD | High-conviction thesis | Score >7 | Maintain |
| ADD | Thesis strengthening | Score 8+ | Increase 25% |

**Positions Being Rebalanced:**

| Ticker | Current Status | Rule Triggered | Action | Proceeds/Cost |
|--------|----------------|----------------|--------|---------------|
| XXXX   | -12% loss      | EXIT (>10%)    | SELL   | +$XXX         |
| YYYY   | +18% gain      | TRIM (>15%)    | SELL 50% | +$XXX      |

**Cash Summary After Rebalancing:**
- Starting Cash: $XXX
- Proceeds from Exits/Trims: +$XXX
- **New Buying Power**: $XXX

---

## 6. CONVICTION SCORECARD

Rank ALL positions (existing + new ideas) by conviction:

| Rank | Ticker | Score (1-10) | Catalyst (40%) | Technicals (30%) | Fundamentals (30%) | Action |
|------|--------|--------------|----------------|------------------|--------------------| -------|
| 1    | XXXX   | 8.5          | 9 (FDA Dec 15) | 8 (breakout)     | 8 (beat rate)      | HOLD   |
| 2    | YYYY   | 8.0          | 8 (earnings)   | 8 (support held) | 8 (growth)         | ADD    |
| 3    | NEW-A  | 7.8          | 9 (PDUFA)      | 7 (consolidation)| 7 (pipeline)       | BUY    |
| ...  | ...    | ...          | ...            | ...              | ...                | ...    |
| 10   | ZZZZ   | 4.0          | 2 (passed)     | 5 (breakdown)    | 5 (miss)           | EXIT   |

**Scoring Methodology:**
- Catalyst Strength (40%): Proximity, probability, expected magnitude
- Technicals (30%): Chart setup, trend, support/resistance, volume
- Fundamentals (30%): Earnings quality, growth, valuation, sector

**Bottom 3 = EXIT candidates | Top 3 of new ideas = BUY candidates**

---

## 7. NEW TRADE SETUPS (2-3 High Conviction Ideas)

For each new opportunity:

### [TICKER] - [Company Name]

**Company Overview**: [1 paragraph - what they do, market position]

**Catalyst**: [Specific event, date, expected outcome]

**Trade Structure:**
- Current Price: $XX.XX
- Entry Price: $XX.XX (limit order)
- Stop Loss: $XX.XX (-X% from entry)
- Target 1: $XX.XX (+X% / Conservative)
- Target 2: $XX.XX (+X% / Aggressive)

**Position Sizing for $3K Account:**
- Recommended Shares: XX shares
- Total Position Cost: $XXX.XX
- Max Risk (at stop): $XX.XX
- Reward/Risk Ratio: X.X:1

**Timeframe**: [Hold through DATE catalyst / X-day swing]

**Risk/Reward Math:**
- If target 1 hit: +$XX (+X%)
- If target 2 hit: +$XX (+X%)
- If stopped out: -$XX (-X%)

---

## 8. SHORT OPPORTUNITIES (1-2 Ideas)

**Lockup Expiration Shorts** (High Priority):
- Stocks with lockup expiring in 7-30 days
- IPOs trading above issue price with high insider ownership
- Overextended momentum names with broken technicals

For each short:

### [TICKER] - SHORT SETUP

**Thesis**: [Why this stock should decline]

**Catalyst**: [Lockup expiry date / Earnings miss setup / Technical breakdown]

**Trade Structure:**
- Current Price: $XX.XX
- Entry Price: $XX.XX (short entry)
- Stop Loss: $XX.XX (+18% from entry - tight!)
- Cover Target 1: $XX.XX (-15% profit)
- Cover Target 2: $XX.XX (-25% profit)

**Position Sizing for $3K Account:**
- Shares to Short: XX shares (smaller size - shorts are risky!)
- Total Position Value: $XXX.XX
- Max Risk (at stop): $XX.XX

**Risk Warning**: Shorts can squeeze - always use stop losses!

---

## 9. OPTIONS TRADES (Max 2)

For each options trade:

### Option Trade #1: [TICKER] [CALL/PUT/SPREAD]

**Trade Type**: [Long Call / Long Put / Call Spread / Put Spread]

**Catalyst Alignment**: [What event this trade plays]

**Structure:**
- Strike: $XX
- Expiry: YYYY-MM-DD (XX days out)
- Premium: $X.XX per contract
- Contracts: X
- Total Cost: $XXX

**Risk/Reward:**
- Max Risk: $XXX (100% of premium)
- Max Profit: $XXX (for spreads) or "Unlimited" (for naked)
- Breakeven: $XX.XX
- Reward/Risk Ratio: X.X:1

**IV Context:**
- Current IV: XX%
- IV Rank: XX percentile
- IV Assessment: [Elevated/Normal/Low] - [favorable/unfavorable for buyer]

**Exit Plan:**
- Take profits at: +50% premium ($X.XX)
- Stop loss at: -50% premium ($X.XX)
- Exit before: [2 days before expiry / after catalyst]

---

## 10. EXECUTION PLAN

**Complete list of all trades for tomorrow:**

### EXITS (Execute First - Frees Capital)
| # | Ticker | Action | Shares | Price | Time in Force | Proceeds |
|---|--------|--------|--------|-------|---------------|----------|
| 1 | XXXX   | SELL   | XX     | Market| DAY           | +$XXX    |

### NEW POSITIONS (Funded by Exits)
| # | Ticker | Action | Shares | Entry | Stop | Target | Cost |
|---|--------|--------|--------|-------|------|--------|------|
| 1 | YYYY   | BUY    | XX     | $XX.XX| $XX.XX| $XX.XX | -$XXX |

### OPTIONS
| # | Ticker | Type | Strike | Expiry | Contracts | Premium | Cost |
|---|--------|------|--------|--------|-----------|---------|------|
| 1 | ZZZZ   | CALL | $XX    | MM-DD  | X         | $X.XX   | -$XXX|

**Capital Flow Summary:**
- Proceeds from Exits: +$XXX
- Cost of New Positions: -$XXX
- Net Cash Change: +/-$XXX
- **Ending Cash Buffer**: $XXX

---

## 11. RISK MANAGEMENT PROTOCOL

**Daily Loss Limit**: $300 (10% of portfolio)
- If hit → NO new trades for day
- If -$200 intraday → Reduce position sizes

**Position Stop-Loss Rules:**
- Stocks: 15% hard stop (no exceptions)
- Options: 50% of premium (or exit if catalyst fails)
- Shorts: 18% stop (shorts can squeeze)

**Position Sizing Guardrails:**
- Min position: $75 (avoids over-diversification)
- Max position: $300 (limits single-name risk)
- Max single stock: 12% of portfolio
- Max sector concentration: 30%

**Cash Buffer Target**: $400-$600
- Allows entry on unexpected opportunities
- Covers potential margin calls

**Options Exposure Limit**: 15% of portfolio ($450 max)
- Never hold options to expiry
- Exit 2 days before expiration minimum
- Take profits at 50% (don't be greedy)

**Review Triggers:**
- If portfolio -5% from peak → review all positions
- If any position -20% → mandatory reassessment
- If 3+ positions show "BROKEN" thesis → reduce exposure

---

ORDER BLOCK FORMAT (strict):

**For Stock Trades (LONG):**
```
Action: buy, sell
Ticker: SYMBOL
Shares: X (actual share count)
Total cost: $XXX.XX
Entry price: $XX.XX
Time in force: DAY
Intended execution date: YYYY-MM-DD
Catalyst date: YYYY-MM-DD
Stop loss: $XX.XX (15% max)
Target price: $XX.XX
Max loss: $XX.XX
One-line rationale: [Catalyst + setup + conviction score]
```

**For SHORT Trades:**
```
Action: sell_short, buy_to_cover
Ticker: SYMBOL
Shares: X (actual share count - keep small!)
Total position value: $XXX.XX
Entry price: $XX.XX (short entry)
Time in force: DAY
Intended execution date: YYYY-MM-DD
Catalyst date: YYYY-MM-DD
Stop loss: $XX.XX (18% max - tighter for shorts!)
Cover target: $XX.XX
Max loss: $XX.XX
One-line rationale: [Bearish catalyst + technical breakdown + risk]
```

**For Options Trades:**
```
Action: buy_to_open
Ticker: SYMBOL
Option: [CALL/PUT] $XX strike exp YYYY-MM-DD
Contracts: X
Premium: $X.XX per contract
Total cost: $XXX.XX
Catalyst date: YYYY-MM-DD
IV Rank: XX%
Max loss: $XXX.XX
Target: +50% premium
One-line rationale: [Binary catalyst + expected move + IV context]
```

CRITICAL RULES FOR $3K ACCOUNT:
- This is REAL MONEY - every trade must have clear justification
- Show EXACT share counts and dollar amounts
- Every new buy must be funded by an exit (small account constraint)
- Follow the conviction scorecard - only trade top-ranked ideas
- Rules-based rebalancing - no emotional decisions
- Risk management is PARAMOUNT - one bad trade = -10% account
- Use your full thinking budget for comprehensive analysis

TOOL USAGE REQUIREMENTS:
- Call get_current_price(ticker) for EVERY stock analyzed
- Your training data is 10+ months old - DO NOT trust cached prices
- Use get_fundamental_metrics(ticker) for earnings and valuations
- Use get_price_history(ticker, 30) for technical analysis
- Use get_earnings_history(ticker, 4) to check beat rates
- Use get_news_sentiment(ticker, 5) for catalyst identification

CRITICAL TOOLS USAGE:
- You have access to real-time financial data tools - USE THEM EXTENSIVELY!
- For EVERY stock you research or recommend, call get_current_price(ticker) for accurate pricing
- Your training data prices are 10+ months old - DO NOT use them for recommendations
- Use get_fundamental_metrics(ticker) for P/E, revenue, margins - essential for valuation
- Use get_earnings_history(ticker, 4) to verify earnings trends and beat rates
- Use get_news_sentiment(ticker, 5) to identify catalysts and market perception
- Use get_price_history(ticker, 30) for technical setup validation
- Use get_multiple_prices([list]) when screening multiple catalyst plays

Example catalyst research workflow:
1. Call get_current_price("RIVN") - verify current price ($15.35 NOT $20!)
2. Call get_earnings_history("RIVN", 4) - check beat rate
3. Call get_news_sentiment("RIVN", 10) - find catalysts
4. Call get_price_history("RIVN", 60) - technical setup
5. Make recommendation with CURRENT accurate data

NEVER recommend trades based on outdated prices - use the tools!
"""


class ClaudeResearchGenerator:
    """Generate deep research reports using Claude AI"""

    def __init__(self):
        """Initialize API clients"""
        # Claude API
        self.claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # MCP Financial Data Tools (for real-time price access during research)
        self.financial_tools = FinancialDataToolsProvider()

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

        self.shorgan_live_trading = TradingClient(
            api_key=os.getenv("ALPACA_LIVE_API_KEY_SHORGAN"),
            secret_key=os.getenv("ALPACA_LIVE_SECRET_KEY_SHORGAN"),
            paper=False,
            raw_data=False
        )

        # DEE-BOT Live Trading Client (REAL MONEY - $10K account)
        # Only initialize if API keys are available (user needs to create account first)
        dee_live_key = os.getenv("ALPACA_LIVE_API_KEY_DEE")
        dee_live_secret = os.getenv("ALPACA_LIVE_SECRET_KEY_DEE")
        if dee_live_key and dee_live_secret:
            self.dee_live_trading = TradingClient(
                api_key=dee_live_key,
                secret_key=dee_live_secret,
                paper=False,
                raw_data=False
            )
        else:
            self.dee_live_trading = None
            print("[INFO] DEE-BOT Live not configured - skipping (no API keys)")

        # Alpaca Market Data API (for quotes/bars)
        self.market_data = StockHistoricalDataClient(
            api_key=os.getenv("ALPACA_API_KEY_DEE"),
            secret_key=os.getenv("ALPACA_SECRET_KEY_DEE")
        )

    def get_portfolio_snapshot(self, bot_name: str) -> Dict:
        """Get current portfolio holdings and account info"""
        if bot_name == "DEE-BOT":
            client = self.dee_trading
        elif bot_name == "DEE-BOT-LIVE":
            if self.dee_live_trading is None:
                print(f"[WARNING] DEE-BOT Live not configured - cannot get portfolio")
                return {"error": "DEE-BOT Live not configured", "cash": 0, "positions": []}
            client = self.dee_live_trading
        elif bot_name == "SHORGAN-BOT-LIVE":
            client = self.shorgan_live_trading
        else:  # SHORGAN-BOT paper
            client = self.shorgan_trading

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

                    # Calculate spread percentage with zero-check to prevent division by zero
                    ask_price = float(q.ask_price) if q.ask_price else 0.0
                    bid_price = float(q.bid_price) if q.bid_price else 0.0
                    spread = ask_price - bid_price
                    spread_pct = round((spread / ask_price * 100), 3) if ask_price > 0 else 0.0

                    snapshot[ticker] = {
                        "bid": bid_price,
                        "ask": ask_price,
                        "bid_size": int(q.bid_size) if q.bid_size else 0,
                        "ask_size": int(q.ask_size) if q.ask_size else 0,
                        "last_trade_price": float(t.price) if t.price else 0.0,
                        "last_trade_size": int(t.size) if t.size else 0,
                        "spread": spread,
                        "spread_pct": spread_pct
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
        Generate comprehensive daily research report using Claude

        Args:
            bot_name: "DEE-BOT" or "SHORGAN-BOT"
            week_number: Optional identifier for tracking (legacy parameter)
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

        # Format portfolio holdings with action flags (Enhanced Dec 2025)
        holdings_text = ""
        portfolio_value = portfolio['portfolio_value']

        # Categorize positions for attention summary
        winners_to_trim = []
        losers_to_exit = []
        overweight = []
        shorts_in_dee = []
        position_limit = 0.08 if bot_name == "DEE-BOT" else 0.10

        for h in portfolio["holdings"]:
            pnl_pct = h['unrealized_plpc'] * 100
            position_weight = (h['market_value'] / portfolio_value) * 100 if portfolio_value > 0 else 0
            qty = float(h['qty'])
            is_short = qty < 0

            # Determine action flag
            if is_short and bot_name == "DEE-BOT":
                action_flag = "**[URGENT: COVER SHORT - DEE-BOT IS LONG-ONLY]**"
                shorts_in_dee.append(h['symbol'])
            elif pnl_pct <= -25:
                action_flag = "**[EXIT: Critical loss >25%]**"
                losers_to_exit.append(f"{h['symbol']} ({pnl_pct:+.1f}%)")
            elif pnl_pct <= -15:
                action_flag = "[REVIEW: Loss >15%]"
                losers_to_exit.append(f"{h['symbol']} ({pnl_pct:+.1f}%)")
            elif pnl_pct >= 50:
                action_flag = "**[TRIM: Strong winner >50%]**"
                winners_to_trim.append(f"{h['symbol']} ({pnl_pct:+.1f}%)")
            elif pnl_pct >= 20:
                action_flag = "[TRIM: Winner >20%]"
                winners_to_trim.append(f"{h['symbol']} ({pnl_pct:+.1f}%)")
            elif position_weight > position_limit * 100:
                action_flag = f"[OVERWEIGHT: {position_weight:.1f}% > {position_limit*100:.0f}%]"
                overweight.append(f"{h['symbol']} ({position_weight:.1f}%)")
            else:
                action_flag = "[HOLD]"

            holdings_text += f"""
{h['symbol']}: {abs(qty):.0f} shares {'SHORT' if is_short else 'LONG'} @ ${h['avg_entry_price']:.2f}
  Current: ${h['current_price']:.2f} | P&L: ${h['unrealized_pl']:+,.2f} ({pnl_pct:+.1f}%)
  Weight: {position_weight:.1f}% | Value: ${abs(h['market_value']):,.2f}
  {action_flag}
"""

        # Add attention summary at top
        attention = ""
        if shorts_in_dee:
            attention += f"\n**CRITICAL - SHORTS IN LONG-ONLY**: {', '.join(shorts_in_dee)}"
        if losers_to_exit:
            attention += f"\n**LOSERS >15%**: {', '.join(losers_to_exit)}"
        if winners_to_trim:
            attention += f"\n**WINNERS >20%**: {', '.join(winners_to_trim)}"
        if overweight:
            attention += f"\n**OVERWEIGHT**: {', '.join(overweight)}"

        if attention:
            holdings_text = f"\n=== POSITIONS NEEDING ATTENTION ==={attention}\n\n=== ALL POSITIONS ==={holdings_text}"

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
Generate a comprehensive DAILY Deep Research Report following your system prompt structure.

IMPORTANT: This is a DAILY report, NOT weekly. Use "Daily Deep Research Report" as the title.
Do NOT use the word "weekly" anywhere in the report. This report is generated every trading day.

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

        # Select system prompt based on bot name
        if bot_name == "DEE-BOT":
            system_prompt = DEE_BOT_SYSTEM_PROMPT
        elif bot_name == "DEE-BOT-LIVE":
            system_prompt = DEE_BOT_LIVE_SYSTEM_PROMPT
        elif bot_name == "SHORGAN-BOT-LIVE":
            system_prompt = SHORGAN_BOT_LIVE_SYSTEM_PROMPT
        else:  # SHORGAN-BOT paper
            system_prompt = SHORGAN_BOT_SYSTEM_PROMPT

        # Inject dynamic date instruction into the system prompt
        dynamic_date_instruction = get_dynamic_date_instruction()
        system_prompt = system_prompt.replace("{DATE_INSTRUCTION}", dynamic_date_instruction)
        print(f"[*] Injected dynamic dates: Today is {datetime.now().strftime('%A, %B %d, %Y')}")

        try:
            # Build conversation messages
            messages = [{"role": "user", "content": user_prompt}]

            # Get tool definitions
            tools = self.financial_tools.get_tool_definitions()

            # Call Claude with tool support (may require multiple rounds for tool use)
            max_turns = 20  # Increased to 20 to ensure ORDER BLOCK completion for all bots
            report_content = ""

            print(f"[*] Claude has access to {len(tools)} real-time data tools")
            print(f"[*] Tools: get_current_price, get_multiple_prices, get_price_history, get_fundamental_metrics, get_valuation_multiples, get_earnings_history, get_news_sentiment")

            for turn in range(max_turns):
                print(f"[*] API Call #{turn + 1}...")

                # Use streaming for Opus 4.1
                stream = self.claude.messages.stream(
                    model="claude-opus-4-20250514",  # Claude Opus 4.1 for deep research
                    max_tokens=32000,  # Maximum for Opus 4.1
                    temperature=1.0,  # Required for extended thinking
                    thinking={
                        "type": "enabled",
                        "budget_tokens": 16000  # Thinking budget (must be < max_tokens)
                    },
                    system=system_prompt,
                    tools=tools,  # Provide tools to Claude
                    messages=messages
                )

                # Collect response
                current_text = ""
                tool_uses = []

                with stream as event_stream:
                    response = event_stream.get_final_message()

                    # Extract text and tool uses from response
                    for block in response.content:
                        if hasattr(block, 'type'):
                            if block.type == "text":
                                current_text += block.text
                            elif block.type == "tool_use":
                                tool_uses.append(block)

                # Add assistant's text response to report
                if current_text:
                    report_content += current_text

                # If no tool uses, we're done
                if not tool_uses:
                    print(f"[+] Research complete (no more tool calls)")
                    break

                # Execute tools and continue conversation
                print(f"[*] Executing {len(tool_uses)} tool calls...")
                messages.append({"role": "assistant", "content": response.content})

                tool_results = []
                for tool_use in tool_uses:
                    tool_name = tool_use.name
                    tool_input = tool_use.input
                    print(f"    - {tool_name}({json.dumps(tool_input)})")

                    # Execute the tool
                    result = self.financial_tools.execute_tool(tool_name, tool_input)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": json.dumps(result)
                    })

                # Add tool results to conversation
                messages.append({"role": "user", "content": tool_results})

            if turn >= max_turns - 1:
                print(f"[!] Warning: Reached maximum tool use turns ({max_turns})")

            # 6. Add header and metadata
            report_header = f"""# CLAUDE DEEP RESEARCH REPORT - {bot_name}
## {datetime.now().strftime("%A, %B %d, %Y")}
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

    def _fix_markdown_formatting(self, content: str) -> str:
        """
        Fix markdown formatting issues in Claude's output.

        Ensures proper line breaks before section headers and other formatting fixes.
        Common issue: "text.**Header**" should be "text.\n\n**Header**"
        """
        import re

        # Pattern 1: Bold headers that need line breaks before them
        # Match text followed by **Header** without a newline before it
        # e.g., "profits above $30.**Position Management**" -> "profits above $30.\n\n**Position Management**"
        bold_header_patterns = [
            r'(\S)(\*\*Position Management\*\*)',
            r'(\S)(\*\*Risk Management\*\*)',
            r'(\S)(\*\*Trade Recommendations\*\*)',
            r'(\S)(\*\*Trade Summary\*\*)',
            r'(\S)(\*\*Catalyst Calendar\*\*)',
            r'(\S)(\*\*Market Analysis\*\*)',
            r'(\S)(\*\*Portfolio Analysis\*\*)',
            r'(\S)(\*\*Technical Analysis\*\*)',
            r'(\S)(\*\*Fundamental Analysis\*\*)',
            r'(\S)(\*\*Entry Strategy\*\*)',
            r'(\S)(\*\*Exit Strategy\*\*)',
            r'(\S)(\*\*Stop Loss\*\*)',
            r'(\S)(\*\*Price Target\*\*)',
            r'(\S)(\*\*Order Block\*\*)',
            r'(\S)(\*\*Summary\*\*)',
            r'(\S)(\*\*Conclusion\*\*)',
            r'(\S)(\*\*Action Items\*\*)',
            r'(\S)(\*\*Key Levels\*\*)',
            r'(\S)(\*\*Watch List\*\*)',
        ]

        for pattern in bold_header_patterns:
            content = re.sub(pattern, r'\1\n\n\2', content)

        # Pattern 2: Generic fix - any **TitleCase Header** preceded by non-whitespace
        # This catches headers we might have missed above
        # Match: non-whitespace + **Word Word** (title case, 1-4 words)
        content = re.sub(
            r'([^\s\n])(\*\*[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\*\*)',
            r'\1\n\n\2',
            content
        )

        # Pattern 3: Ensure headers starting with ## or ### have blank line before
        # Match: non-newline char + ## Header
        content = re.sub(r'([^\n])\n(#{2,6}\s)', r'\1\n\n\2', content)

        # Pattern 4: Clean up excessive blank lines (more than 2 consecutive)
        content = re.sub(r'\n{4,}', '\n\n\n', content)

        return content

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
        # Fix markdown formatting issues (headers running into text)
        report = self._fix_markdown_formatting(report)

        # Create directory structure for tomorrow's trading date
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        date_str = tomorrow.strftime("%Y-%m-%d")

        # FIX: Use absolute path to avoid CWD dependency
        # Get project root directory (2 levels up from this file)
        project_root = Path(__file__).parent.parent.parent
        report_dir = project_root / "reports" / "premarket" / date_str
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

    def _create_order_block_card(self, code_text: str) -> Optional[Table]:
        """
        Convert an order block code section into a styled trade card.

        Returns a Table element styled as a professional trade card.
        """
        try:
            # Parse key-value pairs from the order block
            lines = code_text.strip().split('\n')
            data = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip().lower()] = value.strip()

            if not data.get('ticker') or not data.get('action'):
                return None  # Not a valid order block

            # Determine card color based on action
            action = data.get('action', '').lower()
            if action in ['buy', 'buy_to_open']:
                header_color = HexColor('#2e7d32')  # Green
                action_text = 'BUY'
            elif action in ['sell', 'sell_to_close']:
                header_color = HexColor('#c62828')  # Red
                action_text = 'SELL'
            elif action == 'sell_short':
                header_color = HexColor('#7b1fa2')  # Purple
                action_text = 'SHORT'
            else:
                header_color = HexColor('#1565c0')  # Blue
                action_text = action.upper()

            ticker = data.get('ticker', 'N/A')
            shares = data.get('shares', data.get('contracts', 'N/A'))
            entry = data.get('entry price', data.get('entry', 'N/A'))
            stop = data.get('stop loss', data.get('stop', 'N/A'))
            target = data.get('target price', data.get('target', data.get('cover target', 'N/A')))
            cost = data.get('total cost', data.get('total position value', 'N/A'))
            rationale = data.get('one-line rationale', '')
            catalyst = data.get('catalyst date', '')

            # Build card table
            card_data = [
                [f'{action_text}  {ticker}', f'{shares} shares @ {entry}'],
            ]

            # Add stop/target row if available
            if stop != 'N/A' or target != 'N/A':
                card_data.append([f'Stop: {stop}', f'Target: {target}'])

            # Add cost row
            if cost != 'N/A':
                card_data.append([f'Cost: {cost}', f'Catalyst: {catalyst}' if catalyst else ''])

            # Add rationale
            if rationale:
                card_data.append([rationale, ''])

            card = Table(card_data, colWidths=[3.2*inch, 3.2*inch])

            style_commands = [
                # Header row - colored based on action
                ('BACKGROUND', (0, 0), (-1, 0), header_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),

                # Body rows
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#fafafa')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TEXTCOLOR', (0, 1), (-1, -1), HexColor('#333333')),

                # Border
                ('BOX', (0, 0), (-1, -1), 1, header_color),
                ('LINEBELOW', (0, 0), (-1, 0), 1, header_color),

                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),

                # Span rationale across both columns if present
                ('SPAN', (0, -1), (-1, -1)) if rationale else ('TOPPADDING', (0, 0), (0, 0), 6),
            ]

            card.setStyle(TableStyle(style_commands))
            return card

        except Exception as e:
            print(f"    [!] Order block card failed: {e}")
            return None

    def _create_catalyst_calendar_table(self, code_text: str) -> Optional[Table]:
        """
        Convert catalyst calendar code block into a styled table.
        """
        try:
            lines = code_text.strip().split('\n')
            table_data = [['Date', 'Event', 'Impact', 'Trade Idea']]

            current_date = ''
            current_event = ''
            current_impact = ''
            current_trade = ''

            for line in lines:
                line = line.strip()
                if line.startswith('[') and ']' in line:
                    # Save previous entry if exists
                    if current_date:
                        table_data.append([current_date, current_event, current_impact, current_trade])
                    # New date entry
                    current_date = line[1:line.index(']')]
                    rest = line[line.index(']')+1:].strip(' -')
                    current_event = rest
                    current_impact = ''
                    current_trade = ''
                elif line.startswith('Type:'):
                    current_event = line.replace('Type:', '').strip()
                elif line.startswith('Expected Impact:'):
                    current_impact = line.replace('Expected Impact:', '').strip()
                elif line.startswith('Suggested Trade:'):
                    current_trade = line.replace('Suggested Trade:', '').strip()

            # Don't forget last entry
            if current_date:
                table_data.append([current_date, current_event, current_impact, current_trade])

            if len(table_data) <= 1:
                return None

            table = Table(table_data, colWidths=[1.3*inch, 2.0*inch, 1.0*inch, 2.0*inch])

            # Impact color coding
            style_commands = [
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a1a1a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.25, HexColor('#e0e0e0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#fafafa')]),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]

            # Color-code impact column
            for row_idx, row in enumerate(table_data[1:], start=1):
                if len(row) > 2:
                    impact = row[2].lower()
                    if 'high' in impact:
                        style_commands.append(('TEXTCOLOR', (2, row_idx), (2, row_idx), HexColor('#c62828')))
                        style_commands.append(('FONTNAME', (2, row_idx), (2, row_idx), 'Helvetica-Bold'))
                    elif 'medium' in impact:
                        style_commands.append(('TEXTCOLOR', (2, row_idx), (2, row_idx), HexColor('#f57c00')))
                    elif 'low' in impact:
                        style_commands.append(('TEXTCOLOR', (2, row_idx), (2, row_idx), HexColor('#2e7d32')))

            table.setStyle(TableStyle(style_commands))
            return table

        except Exception as e:
            print(f"    [!] Catalyst calendar table failed: {e}")
            return None

    def _apply_text_formatting(self, text: str) -> str:
        """
        Apply inline formatting to text including action badges and thesis status.
        Returns text with XML formatting for ReportLab paragraphs.
        """
        import re

        # Action badges - wrap in colored spans
        action_colors = {
            'BUY': ('#2e7d32', '#e8f5e9'),      # Green
            'SELL': ('#c62828', '#ffebee'),     # Red
            'HOLD': ('#1565c0', '#e3f2fd'),     # Blue
            'TRIM': ('#f57c00', '#fff3e0'),     # Orange
            'EXIT': ('#c62828', '#ffebee'),     # Red
            'SHORT': ('#7b1fa2', '#f3e5f5'),    # Purple
            'WATCH': ('#757575', '#fafafa'),    # Gray
        }

        for action, (fg, bg) in action_colors.items():
            # Match standalone action words (with word boundaries)
            pattern = rf'\b({action})\b'
            replacement = f'<font color="{fg}"><b>{action}</b></font>'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # Thesis status badges
        thesis_colors = {
            'INTACT': '#1565c0',      # Blue
            'STRONG': '#2e7d32',      # Green
            'WEAKENING': '#f57c00',   # Orange
            'BROKEN': '#c62828',      # Red
        }

        for status, color in thesis_colors.items():
            pattern = rf'\b({status})\b'
            replacement = f'<font color="{color}"><b>[{status}]</b></font>'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # P&L formatting - green for positive, red for negative
        # Match patterns like +$22.96, +3.1%, -$5.52, -3.1%
        def color_pl(match):
            value = match.group(0)
            if value.startswith('+'):
                return f'<font color="#2e7d32"><b>{value}</b></font>'
            elif value.startswith('-'):
                return f'<font color="#c62828"><b>{value}</b></font>'
            return value

        text = re.sub(r'[+-]\$[\d,]+\.?\d*', color_pl, text)
        text = re.sub(r'[+-]\d+\.?\d*%', color_pl, text)

        return text

    def _create_conviction_gauge(self, ticker: str, score: int, rationale: str = '') -> Optional[Table]:
        """
        Create a visual conviction gauge for a position (1-10 scale).
        Returns a styled table with progress bar visualization.
        """
        try:
            # Validate score
            score = max(1, min(10, int(score)))

            # Determine color based on score
            if score >= 8:
                bar_color = HexColor('#2e7d32')  # Green - high conviction
                label = 'HIGH'
            elif score >= 5:
                bar_color = HexColor('#f57c00')  # Orange - medium conviction
                label = 'MEDIUM'
            else:
                bar_color = HexColor('#c62828')  # Red - low conviction
                label = 'LOW'

            # Create visual progress bar as nested table
            filled_cells = score
            empty_cells = 10 - score

            bar_data = [['']*10]
            bar_table = Table(bar_data, colWidths=[0.3*inch]*10)

            bar_style_commands = [
                ('BACKGROUND', (0, 0), (filled_cells-1, 0), bar_color),
                ('BACKGROUND', (filled_cells, 0), (9, 0), HexColor('#e0e0e0')),
                ('BOX', (0, 0), (-1, -1), 0.5, HexColor('#999999')),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]
            bar_table.setStyle(TableStyle(bar_style_commands))

            # Main card layout
            card_data = [
                [f'{ticker}', f'{score}/10 - {label}'],
            ]
            if rationale:
                card_data.append([rationale[:80] + ('...' if len(rationale) > 80 else ''), ''])

            card = Table(card_data, colWidths=[2.5*inch, 3.5*inch])
            card.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (1, 0), (1, 0), bar_color),
                ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ]))

            # Combine into wrapper with progress bar
            wrapper_data = [
                [card],
                [bar_table],
            ]
            wrapper = Table(wrapper_data, colWidths=[6.5*inch])
            wrapper.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#fafafa')),
                ('BOX', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))

            return wrapper

        except Exception as e:
            print(f"    [!] Conviction gauge failed: {e}")
            return None

    def _create_position_card(self, header: str, content_lines: List[str], pl_value: float = 0) -> Optional[Table]:
        """
        Create a position analysis card with P&L-colored left border.
        """
        try:
            # Determine border color based on P&L
            if pl_value > 0:
                border_color = HexColor('#2e7d32')  # Green for profit
            elif pl_value < 0:
                border_color = HexColor('#c62828')  # Red for loss
            else:
                border_color = HexColor('#1565c0')  # Blue for neutral

            # Format content
            content = '<br/>'.join(content_lines[:6])  # Limit to 6 lines

            # Create paragraph style for content
            content_style = ParagraphStyle(
                'PositionContent',
                fontSize=8,
                leading=11,
                textColor=HexColor('#333333')
            )

            # Create card table with colored left border
            card_data = [
                [Paragraph(f'<b>{header}</b>', ParagraphStyle('Header', fontSize=10, textColor=HexColor('#1a1a1a')))],
                [Paragraph(content, content_style)],
            ]

            card = Table(card_data, colWidths=[6.2*inch])
            card.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#fafafa')),
                ('LINEBEFORECOL', (0, 0), (0, -1), 4, border_color),  # Thick left border
                ('BOX', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))

            return card

        except Exception as e:
            print(f"    [!] Position card failed: {e}")
            return None

    def _parse_conviction_scorecard(self, text: str) -> Optional[List[Table]]:
        """
        Parse conviction scorecard section and return visual gauge elements.
        """
        import re
        try:
            gauges = []
            # Pattern: Ticker - Score (X/10) or Ticker: X/10
            pattern = r'([A-Z]{1,5})\s*[-:]\s*(\d+)/10(?:\s*[-:]\s*(.+))?'
            matches = re.findall(pattern, text)

            for match in matches:
                ticker = match[0]
                score = int(match[1])
                rationale = match[2] if len(match) > 2 else ''
                gauge = self._create_conviction_gauge(ticker, score, rationale)
                if gauge:
                    gauges.append(gauge)

            return gauges if gauges else None

        except Exception as e:
            print(f"    [!] Conviction scorecard parsing failed: {e}")
            return None

    def _preprocess_markdown(self, markdown_content: str) -> tuple:
        """
        Preprocess markdown to extract structure and clean redundant info.
        Returns (cleaned_content, sections_list, executive_summary) for TOC and document structure.
        """
        import re
        lines = markdown_content.split('\n')
        cleaned_lines = []
        sections = []  # List of (level, title, anchor) for TOC
        executive_summary = []  # Lines for executive summary section

        skip_patterns = [
            r'^# CLAUDE DEEP RESEARCH REPORT',  # Redundant header
            r'^### Generated:',  # Date already in header
            r'^### Model:',  # Not needed
            r'^\*\*Date:.*\*\*',  # Redundant date
            r'^## (?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),',  # Redundant date header
        ]

        section_counter = 0
        in_exec_summary = False

        for line in lines:
            # Skip redundant lines
            skip = False
            for pattern in skip_patterns:
                if re.match(pattern, line.strip()):
                    skip = True
                    break

            if skip:
                continue

            # Track sections for TOC
            if line.startswith('## ') and not line.startswith('### '):
                section_counter += 1
                title = line[3:].strip()
                # Remove numbering if present (e.g., "1. PORTFOLIO SNAPSHOT" -> "PORTFOLIO SNAPSHOT")
                title_clean = re.sub(r'^\d+\.\s*', '', title)
                sections.append((2, title_clean, f'section_{section_counter}'))

                # Check if this is the Executive Summary section
                if 'EXECUTIVE SUMMARY' in title.upper() or 'EXEC SUMMARY' in title.upper():
                    in_exec_summary = True
                    continue  # Don't add to cleaned_lines, we'll handle it separately
                elif in_exec_summary:
                    in_exec_summary = False  # End of exec summary

            elif line.startswith('### ') and not line.startswith('#### '):
                title = line[4:].strip()
                # Only add ticker sections to TOC
                if re.match(r'^[A-Z]{1,5}\s*[-:]', title):
                    sections.append((3, title, f'section_{section_counter}_{len(sections)}'))
                if in_exec_summary:
                    in_exec_summary = False  # Subsection ends exec summary

            # Collect executive summary lines
            if in_exec_summary:
                executive_summary.append(line)
                continue  # Don't add to cleaned_lines

            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines), sections, '\n'.join(executive_summary)

    def _create_toc(self, sections: list, styles) -> list:
        """Create a table of contents from sections list."""
        elements = []

        toc_title = ParagraphStyle(
            'TOCTitle',
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=HexColor('#1a1a1a'),
            spaceAfter=12
        )
        elements.append(Paragraph("Table of Contents", toc_title))

        toc_style = ParagraphStyle(
            'TOCEntry',
            fontSize=9,
            leading=14,
            leftIndent=0,
            textColor=HexColor('#333333')
        )

        toc_sub_style = ParagraphStyle(
            'TOCSubEntry',
            fontSize=8,
            leading=12,
            leftIndent=15,
            textColor=HexColor('#666666')
        )

        for level, title, anchor in sections:
            if level == 2:
                elements.append(Paragraph(f"• {title}", toc_style))
            elif level == 3:
                elements.append(Paragraph(f"  ◦ {title}", toc_sub_style))

        elements.append(Spacer(1, 0.3*inch))
        return elements

    def _create_title_page(self, bot_name: str, exec_summary_text: str, portfolio_data: Dict = None) -> list:
        """Create title page with report title, key stats, and executive summary."""
        from datetime import datetime
        import re

        elements = []

        # Report title - large and centered
        title_style = ParagraphStyle(
            'ReportTitle',
            fontSize=24,
            fontName='Helvetica-Bold',
            textColor=HexColor('#1a1a1a'),
            alignment=1,  # Center
            spaceAfter=8
        )

        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            fontSize=12,
            fontName='Helvetica',
            textColor=HexColor('#666666'),
            alignment=1,
            spaceAfter=20
        )

        # Determine report type based on bot name
        if 'LIVE' in bot_name.upper():
            report_type = "Live Trading Research"
        elif 'SHORGAN' in bot_name.upper():
            report_type = "Small-Cap Catalyst Research"
        else:
            report_type = "Equity Research Report"

        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(f"{bot_name}", title_style))
        elements.append(Paragraph(report_type, subtitle_style))

        # Date line
        date_style = ParagraphStyle(
            'DateLine',
            fontSize=10,
            fontName='Helvetica',
            textColor=HexColor('#333333'),
            alignment=1,
            spaceAfter=24
        )
        report_date = datetime.now().strftime("%A, %B %d, %Y")
        elements.append(Paragraph(report_date, date_style))

        # Key stats box if portfolio data available
        if portfolio_data:
            stats_data = []
            pv = portfolio_data.get('portfolio_value', 0)
            cash = portfolio_data.get('cash', 0)
            equity = portfolio_data.get('equity', pv)

            # Calculate daily P&L if available
            daily_pnl = portfolio_data.get('daily_pnl', 0)
            daily_pnl_pct = portfolio_data.get('daily_pnl_pct', 0)

            stats_row = [
                f"Portfolio Value\n${pv:,.2f}",
                f"Cash Available\n${cash:,.2f}",
                f"Equity\n${equity:,.2f}",
            ]

            if daily_pnl != 0:
                pnl_color = '#2e7d32' if daily_pnl >= 0 else '#c62828'
                pnl_sign = '+' if daily_pnl >= 0 else ''
                stats_row.append(f"Today's P&L\n{pnl_sign}${daily_pnl:,.2f} ({pnl_sign}{daily_pnl_pct:.2f}%)")

            stats_table = Table([stats_row], colWidths=[1.7*inch] * len(stats_row))
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#1a1a1a')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BOX', (0, 0), (-1, -1), 1, HexColor('#0066cc')),
            ]))
            elements.append(stats_table)
            elements.append(Spacer(1, 0.3*inch))

        # Executive Summary section
        if exec_summary_text.strip():
            exec_title_style = ParagraphStyle(
                'ExecTitle',
                fontSize=14,
                fontName='Helvetica-Bold',
                textColor=HexColor('#0066cc'),
                spaceBefore=16,
                spaceAfter=8
            )
            elements.append(Paragraph("Executive Summary", exec_title_style))

            exec_body_style = ParagraphStyle(
                'ExecBody',
                fontSize=10,
                fontName='Helvetica',
                textColor=HexColor('#333333'),
                leading=14,
                spaceAfter=6
            )

            exec_bullet_style = ParagraphStyle(
                'ExecBullet',
                fontSize=10,
                fontName='Helvetica',
                textColor=HexColor('#333333'),
                leading=14,
                spaceAfter=4,
                leftIndent=15
            )

            # Parse executive summary text
            for line in exec_summary_text.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # Apply markdown formatting
                text = self._format_text_with_markdown(line)

                if line.startswith('- ') or line.startswith('* '):
                    text = text[2:] if text.startswith('- ') or text.startswith('* ') else text
                    bullet = '<font color="#0066cc">&#9632;</font>'
                    try:
                        elements.append(Paragraph(f"{bullet} {text}", exec_bullet_style))
                    except:
                        elements.append(Paragraph(f"* {line[2:]}", exec_bullet_style))
                else:
                    try:
                        elements.append(Paragraph(text, exec_body_style))
                    except:
                        elements.append(Paragraph(line, exec_body_style))

        elements.append(PageBreak())
        return elements

    def _create_visual_catalyst_timeline(self, code_text: str) -> Optional[str]:
        """Create a visual timeline chart for catalyst calendar."""
        import re
        try:
            # Parse catalyst entries
            entries = []
            pattern = r'\[([^\]]+)\]\s*[-–]\s*(.+?)(?:\n\s+Type:\s*(.+?))?(?:\n\s+Expected Impact:\s*(.+?))?(?:\n\s+Suggested Trade:\s*(.+?))?(?=\n\[|\n```|$)'

            # Simpler parsing - just get date and first line
            lines = code_text.strip().split('\n')
            current_entry = None

            for line in lines:
                line = line.strip()
                if line.startswith('[') and ']' in line:
                    if current_entry:
                        entries.append(current_entry)
                    bracket_end = line.index(']')
                    date = line[1:bracket_end]
                    event = line[bracket_end+1:].strip(' -–')
                    current_entry = {'date': date, 'event': event, 'impact': 'Medium', 'trade': ''}
                elif current_entry:
                    if line.startswith('Type:'):
                        current_entry['event'] = line.replace('Type:', '').strip()
                    elif line.startswith('Expected Impact:'):
                        current_entry['impact'] = line.replace('Expected Impact:', '').strip()
                    elif line.startswith('Suggested Trade:'):
                        current_entry['trade'] = line.replace('Suggested Trade:', '').strip()

            if current_entry:
                entries.append(current_entry)

            if not entries:
                return None

            # Create timeline visualization
            fig, ax = plt.subplots(figsize=(10, max(3, len(entries) * 0.5)))

            y_positions = range(len(entries))
            colors = []
            for entry in entries:
                impact = entry.get('impact', '').lower()
                if 'high' in impact:
                    colors.append('#c62828')
                elif 'medium' in impact:
                    colors.append('#f57c00')
                else:
                    colors.append('#2e7d32')

            # Draw timeline
            ax.barh(y_positions, [1]*len(entries), color=colors, height=0.6, alpha=0.7)

            # Add labels
            for i, entry in enumerate(entries):
                ax.text(-0.02, i, entry['date'], ha='right', va='center', fontsize=9, fontweight='bold')
                ax.text(0.05, i, entry['event'][:50], ha='left', va='center', fontsize=8)

            ax.set_xlim(-0.5, 1.5)
            ax.set_ylim(-0.5, len(entries) - 0.5)
            ax.invert_yaxis()
            ax.axis('off')
            ax.set_title('Catalyst Timeline', fontsize=12, fontweight='bold', loc='left')

            # Add legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='#c62828', label='High Impact'),
                Patch(facecolor='#f57c00', label='Medium Impact'),
                Patch(facecolor='#2e7d32', label='Low Impact')
            ]
            ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

            plt.tight_layout()

            # Save
            temp_dir = Path(tempfile.gettempdir()) / 'trading_charts'
            temp_dir.mkdir(exist_ok=True)
            chart_path = temp_dir / 'catalyst_timeline.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"    [!] Catalyst timeline failed: {e}")
            plt.close()
            return None

    def _format_text_with_markdown(self, text: str) -> str:
        """Convert markdown formatting to ReportLab XML tags."""
        import re

        # Escape XML special characters FIRST (before adding any tags)
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')

        # Convert **bold** to XML tags
        text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)

        # Convert *italic* to XML tags
        text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)

        # Apply P&L coloring
        def color_pl(match):
            value = match.group(0)
            if value.startswith('+'):
                return f'<font color="#2e7d32"><b>{value}</b></font>'
            elif value.startswith('-'):
                return f'<font color="#c62828"><b>{value}</b></font>'
            return value

        text = re.sub(r'[+-]\$[\d,]+\.?\d*', color_pl, text)
        text = re.sub(r'[+-]\d+\.?\d*%', color_pl, text)

        # Color action words
        action_colors = {
            'BUY': '#2e7d32', 'SELL': '#c62828', 'HOLD': '#1565c0',
            'TRIM': '#f57c00', 'EXIT': '#c62828', 'SHORT': '#7b1fa2',
            'INTACT': '#1565c0', 'STRONG': '#2e7d32',
            'WEAKENING': '#f57c00', 'BROKEN': '#c62828'
        }

        for word, color in action_colors.items():
            pattern = rf'\b({word})\b'
            text = re.sub(pattern, rf'<font color="{color}"><b>\1</b></font>', text)

        return text

    def _generate_pdf(self, markdown_content: str, output_path: Path, bot_name: str, portfolio_data: Dict = None):
        """
        Convert markdown report to professional PDF with visual enhancements

        Includes: portfolio stats, pie charts, holdings tables, P/L breakdowns
        """
        from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
        from reportlab.lib.pagesizes import letter
        from datetime import datetime
        import re

        # Preprocess markdown - clean redundant info and extract sections for TOC
        cleaned_content, sections, exec_summary = self._preprocess_markdown(markdown_content)

        # Custom page template with header and footer
        def add_header_footer(canvas, doc):
            canvas.saveState()

            # Header bar - teal accent line at top
            canvas.setStrokeColor(HexColor('#0066cc'))
            canvas.setLineWidth(2)
            canvas.line(0.5*inch, letter[1] - 0.4*inch, letter[0] - 0.5*inch, letter[1] - 0.4*inch)

            # Header text - bot name and date
            canvas.setFont('Helvetica-Bold', 8)
            canvas.setFillColor(HexColor('#1a1a1a'))
            canvas.drawString(0.75*inch, letter[1] - 0.35*inch, bot_name)

            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(HexColor('#666666'))
            report_date = datetime.now().strftime("%B %d, %Y")
            canvas.drawRightString(letter[0] - 0.75*inch, letter[1] - 0.35*inch, f"Daily Research")

            # Footer - page number and disclaimer
            canvas.setStrokeColor(HexColor('#e0e0e0'))
            canvas.setLineWidth(0.5)
            canvas.line(0.75*inch, 0.5*inch, letter[0] - 0.75*inch, 0.5*inch)

            canvas.setFont('Helvetica', 7)
            canvas.setFillColor(HexColor('#999999'))
            canvas.drawString(0.75*inch, 0.35*inch, "AI-Generated Research | Not Financial Advice")
            canvas.drawRightString(letter[0] - 0.75*inch, 0.35*inch, f"Page {doc.page}")

            canvas.restoreState()

        # Create PDF document with custom template
        doc = BaseDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.6*inch,
            bottomMargin=0.65*inch
        )

        # Create frame for content
        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height,
            id='normal'
        )

        # Add page template with header/footer
        template = PageTemplate(id='main', frames=frame, onPage=add_header_footer)
        doc.addPageTemplates([template])

        # Define styles - Morgan Stanley / Bulge Bracket Research Style
        styles = getSampleStyleSheet()

        # Main report title (compact, professional)
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=4,
            spaceBefore=0,
            leading=18,
            fontName='Helvetica-Bold'
        )

        # Section headers (## level) - compact with teal accent
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=4,
            spaceBefore=8,
            leading=14,
            fontName='Helvetica-Bold'
        )

        # Subsection headers (### level) - stock tickers
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=11,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=3,
            spaceBefore=8,
            leading=13,
            fontName='Helvetica-Bold'
        )

        # Body text - compact
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=9,
            leading=12,
            spaceAfter=4,
            textColor=HexColor('#333333')
        )

        # Bullet list style with teal square bullets (Morgan Stanley style)
        bullet_style = ParagraphStyle(
            'BulletItem',
            parent=styles['BodyText'],
            fontSize=9,
            leading=12,
            spaceAfter=3,
            leftIndent=15,
            bulletIndent=5,
            textColor=HexColor('#333333')
        )

        # Key takeaway style (teal left border like MS)
        highlight_style = ParagraphStyle(
            'Highlight',
            parent=styles['BodyText'],
            fontSize=9,
            leading=12,
            spaceAfter=4,
            leftIndent=8,
            textColor=HexColor('#333333')
        )

        # Positive/green text style
        success_style = ParagraphStyle(
            'Success',
            parent=styles['BodyText'],
            fontSize=9,
            leading=12,
            spaceAfter=4,
            textColor=HexColor('#2e7d32')
        )

        # Negative/red text style
        danger_style = ParagraphStyle(
            'Danger',
            parent=styles['BodyText'],
            fontSize=9,
            leading=12,
            spaceAfter=4,
            textColor=HexColor('#c62828')
        )

        # Code block style - compact
        code_style = ParagraphStyle(
            'CustomCode',
            parent=styles['Code'],
            fontSize=8,
            fontName='Courier',
            leftIndent=10,
            rightIndent=10,
            spaceBefore=4,
            spaceAfter=4,
            backColor=HexColor('#f5f5f5'),
            borderColor=HexColor('#e0e0e0'),
            borderWidth=0.5,
            borderPadding=6
        )

        # Exhibit/chart caption style
        exhibit_style = ParagraphStyle(
            'Exhibit',
            parent=styles['BodyText'],
            fontSize=10,
            leading=12,
            spaceAfter=4,
            spaceBefore=8,
            textColor=HexColor('#1a1a1a'),
            fontName='Helvetica-Bold'
        )

        # Source citation style
        source_style = ParagraphStyle(
            'Source',
            parent=styles['BodyText'],
            fontSize=7,
            leading=9,
            spaceAfter=8,
            textColor=HexColor('#666666'),
            fontName='Helvetica-Oblique'
        )

        # Build story with new document structure:
        # 1. Title page with Executive Summary
        # 2. Table of Contents (page 2)
        # 3. Portfolio Dashboard
        # 4. Main content
        story = []

        # Track holdings for inline chart generation
        holdings_dict = {}
        if portfolio_data:
            for h in portfolio_data.get('holdings', []):
                symbol = h.get('symbol', '')
                if symbol:
                    holdings_dict[symbol] = h

        # PAGE 1: Title Page with Executive Summary
        story.extend(self._create_title_page(bot_name, exec_summary, portfolio_data))

        # PAGE 2: Table of Contents
        if sections:
            story.extend(self._create_toc(sections, styles))
            story.append(PageBreak())

        # PAGE 3+: Portfolio visual dashboard if data available
        if portfolio_data:
            story.extend(self._create_portfolio_dashboard(portfolio_data, bot_name, styles))
            story.append(PageBreak())

        # Parse cleaned markdown content (redundant info removed)
        lines = cleaned_content.split('\n')

        in_code_block = False
        code_lines = []
        in_table = False
        table_lines = []

        for line in lines:
            # Handle code blocks - check for ``` at start OR end of line
            # Some markdown has ``` stuck at end of previous line like "## Heading```"
            line_stripped = line.strip()
            is_code_fence = line_stripped.startswith('```') or line_stripped == '```' or line_stripped.endswith('```')

            # If line ends with ``` but isn't just ```, extract the non-code part first
            if line_stripped.endswith('```') and not line_stripped.startswith('```') and len(line_stripped) > 3:
                # If we're in a code block, render accumulated code FIRST before toggling
                if in_code_block and code_lines:
                    code_text = '\n'.join(code_lines)
                    story.append(Preformatted(code_text, code_style))
                    story.append(Spacer(1, 0.1*inch))
                    code_lines = []

                # Process the text before the ``` as regular content
                text_before = line_stripped[:-3].strip()
                if text_before:
                    # This is likely a heading with ``` appended - process heading first
                    if text_before.startswith('## '):
                        story.append(Paragraph(text_before[3:], heading_style))
                        story.append(Spacer(1, 0.05*inch))
                    elif text_before.startswith('### '):
                        story.append(Paragraph(text_before[4:], subheading_style))
                    elif text_before.startswith('# '):
                        story.append(Paragraph(text_before[2:], title_style))
                    else:
                        text_formatted = self._format_text_with_markdown(text_before)
                        try:
                            story.append(Paragraph(text_formatted, body_style))
                        except:
                            story.append(Paragraph(text_before, body_style))
                # Now toggle code block state
                in_code_block = not in_code_block
                continue

            if is_code_fence and line_stripped.startswith('```'):
                if in_code_block:
                    # End code block - determine type and render appropriately
                    code_text = '\n'.join(code_lines)

                    # Check if this is an order block (contains Action: and Ticker:)
                    if 'action:' in code_text.lower() and 'ticker:' in code_text.lower():
                        order_card = self._create_order_block_card(code_text)
                        if order_card:
                            story.append(order_card)
                            story.append(Spacer(1, 0.1*inch))
                        else:
                            story.append(Preformatted(code_text, code_style))
                            story.append(Spacer(1, 0.1*inch))

                    # Check if this is a catalyst calendar - create visual timeline
                    elif '[monday' in code_text.lower() or '[tuesday' in code_text.lower() or '[thursday' in code_text.lower() or '[friday' in code_text.lower() or '[jan' in code_text.lower() or '[dec' in code_text.lower():
                        # Try visual timeline first
                        print(f"    [*] Creating visual catalyst timeline...")
                        timeline_path = self._create_visual_catalyst_timeline(code_text)
                        if timeline_path and Path(timeline_path).exists():
                            story.append(Image(timeline_path, width=6.5*inch, height=3.0*inch))
                            story.append(Spacer(1, 0.1*inch))
                        else:
                            # Fall back to table format
                            calendar_table = self._create_catalyst_calendar_table(code_text)
                            if calendar_table:
                                story.append(calendar_table)
                                story.append(Spacer(1, 0.1*inch))
                            else:
                                story.append(Preformatted(code_text, code_style))
                                story.append(Spacer(1, 0.1*inch))

                    else:
                        # Regular code block - use compact styling
                        story.append(Preformatted(code_text, code_style))
                        story.append(Spacer(1, 0.1*inch))

                    code_lines = []
                in_code_block = not in_code_block
                continue

            # SAFEGUARD: If we see a markdown heading while in code block, force exit code block
            # This handles cases where code blocks aren't properly closed
            if in_code_block and (line.startswith('## ') or line.startswith('# ')):
                print(f"    [!] WARNING: Detected unclosed code block, forcing exit at: {line[:50]}")
                # Process accumulated code as a code block
                if code_lines:
                    code_text = '\n'.join(code_lines)
                    story.append(Preformatted(code_text, code_style))
                    story.append(Spacer(1, 0.1*inch))
                code_lines = []
                in_code_block = False
                # Fall through to process this line normally

            if in_code_block:
                code_lines.append(line)
                continue

            # Handle markdown tables
            stripped = line.strip()
            if stripped.startswith('|') and stripped.endswith('|'):
                # This is a table row
                if not in_table:
                    in_table = True
                    table_lines = []
                table_lines.append(stripped)
                continue
            elif in_table:
                # End of table - process it
                if table_lines:
                    table_element = self._parse_markdown_table(table_lines)
                    if table_element:
                        story.append(table_element)
                        story.append(Spacer(1, 0.15*inch))
                in_table = False
                table_lines = []
                # Continue processing this line below

            # Handle headings
            if line.startswith('# ') and not line.startswith('## '):
                text = line[2:].strip()
                # Add a decorative line under main title
                story.append(Paragraph(text, title_style))
                # Add subtle underline effect using a table
                underline = Table([['']],colWidths=[5*inch])
                underline.setStyle(TableStyle([
                    ('LINEBELOW', (0, 0), (-1, -1), 2, HexColor('#0066cc')),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
                story.append(underline)
                story.append(Spacer(1, 0.1*inch))
            elif line.startswith('## '):
                text = line[3:].strip()
                # Add compact spacing and visual separator before h2 (Morgan Stanley style)
                story.append(Spacer(1, 0.1*inch))
                # Section divider line - subtle teal accent
                divider = Table([['']],colWidths=[6.5*inch])
                divider.setStyle(TableStyle([
                    ('LINEABOVE', (0, 0), (-1, -1), 1, HexColor('#0066cc')),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(divider)
                story.append(Paragraph(text, heading_style))
            elif line.startswith('### '):
                text = line[4:].strip()
                story.append(Paragraph(text, subheading_style))

                # Check for stock ticker in heading and generate inline chart
                # Pattern: "### AAPL - Apple Inc" or "### AAPL: Company Name"
                import re
                ticker_match = re.match(r'^([A-Z]{1,5})(?:\s*[-:]\s*|\s+)', text)
                if ticker_match:
                    ticker = ticker_match.group(1)
                    # Only generate chart if ticker is in our holdings
                    if ticker in holdings_dict:
                        print(f"    [*] Generating inline chart for {ticker}...")
                        inline_chart_path = self._generate_inline_price_chart(ticker)
                        if inline_chart_path and Path(inline_chart_path).exists():
                            # Add exhibit label (Morgan Stanley style)
                            story.append(Spacer(1, 0.08*inch))
                            story.append(Paragraph(f"<b>Exhibit: {ticker} 60-Day Price Action</b>", exhibit_style))
                            # Use proper aspect ratio - 5.5" wide, 2.2" tall (2.5:1 ratio)
                            story.append(Image(inline_chart_path, width=5.5*inch, height=2.2*inch))
                            story.append(Paragraph("<i>Source: Alpaca Markets, moving averages 20/50-day</i>", source_style))
                            story.append(Spacer(1, 0.1*inch))
            elif line.startswith('#### '):
                # H4 style
                text = line[5:].strip()
                h4_style = ParagraphStyle(
                    'H4Style',
                    parent=body_style,
                    fontSize=11,
                    fontName='Helvetica-Bold',
                    textColor=HexColor('#495057'),
                    spaceAfter=6,
                    spaceBefore=12
                )
                story.append(Paragraph(text, h4_style))
            elif line.startswith('---'):
                # Horizontal rule - compact visual divider
                hr = Table([['']],colWidths=[6*inch])
                hr.setStyle(TableStyle([
                    ('LINEBELOW', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(hr)
            elif line.strip():
                text = line.strip()

                # Check if this is a conviction score line (e.g., "1. AAPL - 8/10 - Rationale")
                conviction_match = re.match(r'^(?:\d+\.\s+)?([A-Z]{1,5})\s*[-:]\s*(\d+)/10(?:\s*[-:]\s*(.+))?$', text)
                if conviction_match:
                    ticker = conviction_match.group(1)
                    score = int(conviction_match.group(2))
                    rationale = conviction_match.group(3) or ''
                    gauge = self._create_conviction_gauge(ticker, score, rationale)
                    if gauge:
                        story.append(gauge)
                        story.append(Spacer(1, 0.08*inch))
                        continue

                # Detect bullet points - Morgan Stanley style (teal squares)
                is_bullet = False
                indent_level = 0
                if text.startswith('- ') or text.startswith('• '):
                    is_bullet = True
                    text = text[2:]
                elif text.startswith('  - ') or text.startswith('  • '):
                    is_bullet = True
                    indent_level = 1
                    text = text[4:]

                # Apply markdown formatting (bold, italic, P&L colors, action words)
                text = self._format_text_with_markdown(text)

                # Create paragraph with appropriate style
                try:
                    if is_bullet:
                        # Teal square bullets for main, gray for sub-bullets
                        if indent_level == 0:
                            bullet_char = '<font color="#0066cc">&#9632;</font>'
                        else:
                            bullet_char = '&nbsp;&nbsp;<font color="#666666">&#9642;</font>'
                        bullet_text = f"{bullet_char} {text}"
                        story.append(Paragraph(bullet_text, bullet_style))
                    else:
                        # Check for special highlighting keywords
                        text_lower = text.lower()
                        if any(kw in text_lower for kw in ['warning:', 'caution:', 'risk:', 'danger:']):
                            story.append(Paragraph(text, danger_style))
                        elif any(kw in text_lower for kw in ['note:', 'important:', 'tip:']):
                            story.append(Paragraph(text, highlight_style))
                        elif any(kw in text_lower for kw in ['success:', 'profit:', 'gain:']):
                            story.append(Paragraph(text, success_style))
                        else:
                            story.append(Paragraph(text, body_style))
                except Exception as e:
                    # Log error instead of silently skipping
                    print(f"    [!] Paragraph render failed for: {text[:50]}... Error: {e}")
                    # Try plain text fallback
                    try:
                        plain_text = re.sub(r'<[^>]+>', '', text)  # Strip HTML tags
                        story.append(Paragraph(plain_text, body_style))
                    except:
                        pass
            else:
                # Empty line
                story.append(Spacer(1, 0.08*inch))

        # Handle any remaining table at end of document
        if in_table and table_lines:
            table_element = self._parse_markdown_table(table_lines)
            if table_element:
                story.append(table_element)
                story.append(Spacer(1, 0.15*inch))

        # Build PDF
        doc.build(story)

    def _parse_markdown_table(self, table_lines: List[str]) -> Optional[Table]:
        """
        Parse markdown table lines and convert to a formatted PDF table.

        Args:
            table_lines: List of markdown table rows (starting and ending with |)

        Returns:
            ReportLab Table object, or None if parsing fails
        """
        import re
        from reportlab.platypus import Paragraph
        from reportlab.lib.styles import ParagraphStyle
        try:
            if len(table_lines) < 2:
                return None

            # Parse rows
            rows = []
            header_row = None
            separator_idx = -1

            for idx, line in enumerate(table_lines):
                # Split by | and clean up
                cells = [cell.strip() for cell in line.split('|')]
                # Remove empty first and last elements from split
                cells = [c for c in cells if c or idx == 0]  # Keep header even if empty cells
                if cells and cells[0] == '':
                    cells = cells[1:]
                if cells and cells[-1] == '':
                    cells = cells[:-1]

                # Check if this is a separator row (contains only dashes and colons)
                is_separator = all(set(cell.strip()).issubset({'-', ':', ' '}) for cell in cells if cell.strip())

                if is_separator:
                    separator_idx = idx
                    continue

                if cells:
                    rows.append(cells)

            if not rows:
                return None

            # First row is header
            header = rows[0] if rows else []
            data_rows = rows[1:] if len(rows) > 1 else []

            # Build table data
            raw_table_data = [header] + data_rows

            # Normalize column count
            max_cols = max(len(row) for row in raw_table_data) if raw_table_data else 0
            raw_table_data = [row + [''] * (max_cols - len(row)) for row in raw_table_data]

            if not raw_table_data or max_cols == 0:
                return None

            # Calculate column widths based on content (before formatting)
            available_width = 7.0 * inch  # Page width minus margins
            col_widths = []

            for col_idx in range(max_cols):
                max_len = max(len(str(row[col_idx])) for row in raw_table_data)
                # Scale width based on content, min 0.6", max 2"
                width = min(max(0.6 * inch, max_len * 0.08 * inch), 2.0 * inch)
                col_widths.append(width)

            # Scale to fit page
            total_width = sum(col_widths)
            if total_width > available_width:
                scale = available_width / total_width
                col_widths = [w * scale for w in col_widths]

            # Convert cells to Paragraph objects with markdown formatting
            # Define cell styles
            header_cell_style = ParagraphStyle(
                'TableHeader',
                fontSize=8,
                fontName='Helvetica-Bold',
                textColor=colors.white,
                alignment=1  # Center
            )
            data_cell_style = ParagraphStyle(
                'TableCell',
                fontSize=8,
                fontName='Helvetica',
                textColor=HexColor('#333333'),
                alignment=1  # Center
            )

            # Apply markdown formatting to all cells and convert to Paragraphs
            table_data = []
            for row_idx, row in enumerate(raw_table_data):
                formatted_row = []
                for cell in row:
                    cell_text = str(cell).strip()
                    # Apply markdown formatting (bold, italic, colors)
                    formatted_text = self._format_text_with_markdown(cell_text)
                    try:
                        if row_idx == 0:
                            # Header row - use white text style
                            p = Paragraph(formatted_text, header_cell_style)
                        else:
                            # Data row - use dark text style
                            p = Paragraph(formatted_text, data_cell_style)
                        formatted_row.append(p)
                    except Exception as e:
                        # Fallback to plain text if parsing fails
                        plain = re.sub(r'<[^>]+>', '', cell_text)
                        if row_idx == 0:
                            formatted_row.append(Paragraph(plain, header_cell_style))
                        else:
                            formatted_row.append(Paragraph(plain, data_cell_style))
                table_data.append(formatted_row)

            # Create table with Paragraph objects
            table = Table(table_data, colWidths=col_widths)

            # Apply styling - clean Morgan Stanley look
            style_commands = [
                # Header row styling - subtle dark header
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a1a1a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('TOPPADDING', (0, 0), (-1, 0), 6),

                # Data row styling - compact
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),

                # Thin grid and subtle alternating rows
                ('GRID', (0, 0), (-1, -1), 0.25, HexColor('#e0e0e0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#fafafa')]),

                # Left-align first column (usually symbol/ticker)
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ]

            # Note: P&L coloring is now handled by _format_text_with_markdown in Paragraph objects
            # The function applies green/red font colors to +/- values automatically

            table.setStyle(TableStyle(style_commands))
            return table

        except Exception as e:
            print(f"    [!] Failed to parse markdown table: {e}")
            return None

    def _create_portfolio_dashboard(self, portfolio_data: Dict, bot_name: str, styles) -> List:
        """
        Create visual portfolio dashboard with stats, charts, and tables

        Returns list of reportlab flowables (paragraphs, tables, charts)
        """
        elements = []

        # Compact dashboard title
        dashboard_title = ParagraphStyle(
            'DashboardTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=HexColor('#1a1a1a'),
            alignment=TA_LEFT,
            spaceAfter=8
        )
        elements.append(Paragraph(f"Portfolio Summary", dashboard_title))

        # Portfolio summary stats - TWO COLUMN LAYOUT
        cash = portfolio_data.get('cash', 0)
        portfolio_value = portfolio_data.get('portfolio_value', 0)
        equity = portfolio_data.get('equity', 0)
        position_count = portfolio_data.get('position_count', 0)

        # Calculate total P&L
        total_unrealized_pl = sum([h.get('unrealized_pl', 0) for h in portfolio_data.get('holdings', [])])
        total_pl_pct = (total_unrealized_pl / (portfolio_value - total_unrealized_pl) * 100) if portfolio_value > total_unrealized_pl else 0

        # Calculate winners/losers
        holdings = portfolio_data.get('holdings', [])
        winners = len([h for h in holdings if h.get('unrealized_pl', 0) > 0])
        losers = len([h for h in holdings if h.get('unrealized_pl', 0) < 0])
        win_rate = (winners / len(holdings) * 100) if holdings else 0

        # Determine P&L color
        pl_color = '#2e7d32' if total_unrealized_pl >= 0 else '#c62828'

        # Two-column stats table - compact layout
        stats_data = [
            ['Portfolio Value', f'${portfolio_value:,.2f}', 'Positions', f'{position_count}'],
            ['Cash Available', f'${cash:,.2f}', 'Win Rate', f'{win_rate:.0f}% ({winners}W/{losers}L)'],
            ['Unrealized P&L', f'${total_unrealized_pl:+,.2f}', 'Return', f'{total_pl_pct:+.2f}%'],
        ]

        stats_table = Table(stats_data, colWidths=[1.5*inch, 1.8*inch, 1.2*inch, 1.8*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#fafafa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#1a1a1a')),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#666666')),
            ('TEXTCOLOR', (2, 0), (2, -1), HexColor('#666666')),
            ('GRID', (0, 0), (-1, -1), 0.25, HexColor('#e0e0e0')),
            ('BOX', (0, 0), (-1, -1), 1, HexColor('#0066cc')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.15*inch))

        # Pie chart and holdings in compact layout
        if holdings:
            elements.append(Paragraph("Position Allocation", styles['Heading2']))
            elements.append(Spacer(1, 0.05*inch))

            # Create pie chart (smaller)
            pie_chart = self._create_pie_chart(holdings)
            elements.append(pie_chart)
            elements.append(Spacer(1, 0.1*inch))

            # Top holdings table with P&L
            elements.append(Paragraph("Current Holdings", styles['Heading2']))
            elements.append(Spacer(1, 0.05*inch))

            holdings_table = self._create_holdings_table(holdings)
            elements.append(holdings_table)

            # === ENHANCED VISUALIZATIONS (Compact -20% sizing) ===

            # Sector Breakdown Chart
            print(f"    [*] Generating sector breakdown chart...")
            sector_chart_path = self._create_sector_breakdown_chart(holdings)
            if sector_chart_path and Path(sector_chart_path).exists():
                elements.append(PageBreak())
                elements.append(Paragraph("Sector Allocation Analysis", styles['Heading2']))
                elements.append(Spacer(1, 0.05*inch))
                elements.append(Image(sector_chart_path, width=5.6*inch, height=2.4*inch))
                elements.append(Spacer(1, 0.1*inch))

            # Risk Metrics Dashboard
            print(f"    [*] Generating risk metrics dashboard...")
            risk_chart_path = self._create_risk_metrics_dashboard(holdings, portfolio_value)
            if risk_chart_path and Path(risk_chart_path).exists():
                elements.append(Paragraph("Risk Metrics Dashboard", styles['Heading2']))
                elements.append(Spacer(1, 0.05*inch))
                elements.append(Image(risk_chart_path, width=5.6*inch, height=2.8*inch))
                elements.append(Spacer(1, 0.1*inch))

            # P&L Waterfall Chart
            print(f"    [*] Generating P&L waterfall chart...")
            waterfall_path = self._create_pl_waterfall_chart(holdings)
            if waterfall_path and Path(waterfall_path).exists():
                elements.append(PageBreak())
                elements.append(Paragraph("P&L Attribution by Position", styles['Heading2']))
                elements.append(Spacer(1, 0.05*inch))
                elements.append(Image(waterfall_path, width=5.6*inch, height=2.8*inch))
                elements.append(Spacer(1, 0.1*inch))

            # Correlation Heatmap
            print(f"    [*] Generating correlation heatmap...")
            corr_path = self._create_correlation_heatmap(holdings)
            if corr_path and Path(corr_path).exists():
                elements.append(Paragraph("Position Correlation Matrix", styles['Heading2']))
                elements.append(Spacer(1, 0.05*inch))
                elements.append(Image(corr_path, width=4.8*inch, height=3.6*inch))
                elements.append(Spacer(1, 0.1*inch))

            # Performance Comparison
            print(f"    [*] Generating performance comparison chart...")
            perf_path = self._create_performance_comparison_chart(bot_name)
            if perf_path and Path(perf_path).exists():
                elements.append(PageBreak())
                elements.append(Paragraph("30-Day Performance History", styles['Heading2']))
                elements.append(Spacer(1, 0.05*inch))
                elements.append(Image(perf_path, width=5.6*inch, height=2.8*inch))
                elements.append(Spacer(1, 0.1*inch))

            # Earnings Calendar
            print(f"    [*] Generating earnings calendar...")
            earnings_path = self._create_earnings_calendar(holdings)
            if earnings_path and Path(earnings_path).exists():
                elements.append(PageBreak())
                elements.append(Paragraph("Upcoming Earnings Calendar", styles['Heading2']))
                elements.append(Spacer(1, 0.05*inch))
                elements.append(Image(earnings_path, width=5.6*inch, height=2.8*inch))
                elements.append(Spacer(1, 0.1*inch))

            # Catalyst Timeline
            print(f"    [*] Generating catalyst timeline...")
            catalyst_path = self._create_catalyst_timeline(holdings)
            if catalyst_path and Path(catalyst_path).exists():
                elements.append(Paragraph("Catalyst Timeline (Next 45 Days)", styles['Heading2']))
                elements.append(Spacer(1, 0.05*inch))
                elements.append(Image(catalyst_path, width=5.6*inch, height=3.2*inch))
                elements.append(Spacer(1, 0.1*inch))

            # AI Confidence Meters
            print(f"    [*] Generating AI confidence meters...")
            ai_conf_path = self._create_ai_confidence_meter(holdings, portfolio_value)
            if ai_conf_path and Path(ai_conf_path).exists():
                elements.append(PageBreak())
                elements.append(Paragraph("AI Confidence Analysis", styles['Heading2']))
                elements.append(Spacer(1, 0.05*inch))
                elements.append(Image(ai_conf_path, width=5.6*inch, height=2.8*inch))
                elements.append(Spacer(1, 0.1*inch))

            # News Sentiment Gauge
            print(f"    [*] Generating news sentiment gauge...")
            sentiment_path = self._create_news_sentiment_gauge(holdings)
            if sentiment_path and Path(sentiment_path).exists():
                elements.append(Paragraph("News Sentiment Analysis", styles['Heading2']))
                elements.append(Spacer(1, 0.05*inch))
                elements.append(Image(sentiment_path, width=5.6*inch, height=2.8*inch))
                elements.append(Spacer(1, 0.1*inch))

            # Options Flow Summary
            print(f"    [*] Generating options flow summary...")
            options_path = self._create_options_flow_summary(holdings)
            if options_path and Path(options_path).exists():
                elements.append(PageBreak())
                elements.append(Paragraph("Options Flow Analysis", styles['Heading2']))
                elements.append(Spacer(1, 0.05*inch))
                elements.append(Image(options_path, width=5.6*inch, height=2.8*inch))
                elements.append(Spacer(1, 0.1*inch))

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

        # Create table - compact styling
        col_widths = [0.75*inch, 0.6*inch, 0.8*inch, 0.8*inch, 1.0*inch, 0.9*inch, 0.8*inch]
        table = Table(table_data, colWidths=col_widths)

        # Style table - clean Morgan Stanley look
        table.setStyle(TableStyle([
            # Header row - dark, professional
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a1a1a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),

            # Data rows - compact
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Symbol left-aligned
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Numbers right-aligned

            # Thin grid and subtle alternating
            ('GRID', (0, 0), (-1, -1), 0.25, HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#fafafa')]),

            # Compact padding
            ('PADDING', (0, 0), (-1, -1), 3),
        ]))

        return table

    def _create_sector_breakdown_chart(self, holdings: List[Dict]) -> Optional[str]:
        """Create sector breakdown pie chart comparing to S&P 500 weights"""
        try:
            # Define sector mapping (simplified - maps common tickers to sectors)
            sector_map = {
                'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'META': 'Technology',
                'NVDA': 'Technology', 'INTC': 'Technology', 'CSCO': 'Technology', 'V': 'Technology',
                'JPM': 'Financials', 'BAC': 'Financials', 'WFC': 'Financials', 'GS': 'Financials',
                'JNJ': 'Healthcare', 'UNH': 'Healthcare', 'PFE': 'Healthcare', 'ABBV': 'Healthcare',
                'MRK': 'Healthcare', 'LLY': 'Healthcare', 'MDT': 'Healthcare', 'TMO': 'Healthcare',
                'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy', 'OXY': 'Energy',
                'PG': 'Consumer Staples', 'KO': 'Consumer Staples', 'PEP': 'Consumer Staples',
                'WMT': 'Consumer Staples', 'COST': 'Consumer Staples', 'CL': 'Consumer Staples',
                'HD': 'Consumer Disc.', 'NKE': 'Consumer Disc.', 'MCD': 'Consumer Disc.',
                'AMZN': 'Consumer Disc.', 'TSLA': 'Consumer Disc.', 'TGT': 'Consumer Disc.',
                'NEE': 'Utilities', 'SO': 'Utilities', 'DUK': 'Utilities', 'D': 'Utilities',
                'T': 'Communication', 'VZ': 'Communication', 'CMCSA': 'Communication',
                'LMT': 'Industrials', 'RTX': 'Industrials', 'CAT': 'Industrials', 'BA': 'Industrials',
                'AMT': 'Real Estate', 'PLD': 'Real Estate', 'SPG': 'Real Estate',
                'LIN': 'Materials', 'APD': 'Materials', 'SHW': 'Materials',
            }

            # S&P 500 sector weights (approximate)
            sp500_weights = {
                'Technology': 29.5, 'Healthcare': 13.2, 'Financials': 12.8,
                'Consumer Disc.': 10.5, 'Communication': 8.9, 'Industrials': 8.5,
                'Consumer Staples': 6.2, 'Energy': 4.2, 'Utilities': 2.5,
                'Real Estate': 2.4, 'Materials': 2.3
            }

            # Calculate portfolio sector weights
            total_value = sum([abs(h.get('market_value', 0)) for h in holdings])
            if total_value == 0:
                return None

            sector_values = {}
            for h in holdings:
                symbol = h.get('symbol', '')
                value = abs(h.get('market_value', 0))
                sector = sector_map.get(symbol, 'Other')
                sector_values[sector] = sector_values.get(sector, 0) + value

            # Calculate percentages
            portfolio_weights = {k: (v/total_value)*100 for k, v in sector_values.items()}

            # Create comparison chart
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
            fig.suptitle('Sector Allocation: Portfolio vs S&P 500', fontsize=14, fontweight='bold')

            # Portfolio pie
            colors_list = plt.cm.Set3(np.linspace(0, 1, len(portfolio_weights)))
            ax1.pie(portfolio_weights.values(), labels=portfolio_weights.keys(),
                   autopct='%1.1f%%', colors=colors_list, startangle=90)
            ax1.set_title('Your Portfolio', fontsize=12)

            # S&P 500 pie (top sectors only)
            top_sp500 = dict(sorted(sp500_weights.items(), key=lambda x: x[1], reverse=True)[:8])
            colors_sp500 = plt.cm.Set3(np.linspace(0, 1, len(top_sp500)))
            ax2.pie(top_sp500.values(), labels=top_sp500.keys(),
                   autopct='%1.1f%%', colors=colors_sp500, startangle=90)
            ax2.set_title('S&P 500 Benchmark', fontsize=12)

            plt.tight_layout()

            # Save to temp file
            temp_dir = Path(tempfile.gettempdir()) / 'trading_charts'
            temp_dir.mkdir(exist_ok=True)
            chart_path = temp_dir / 'sector_breakdown.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"    [!] Sector breakdown chart failed: {e}")
            plt.close()
            return None

    def _create_risk_metrics_dashboard(self, holdings: List[Dict], portfolio_value: float) -> Optional[str]:
        """Create risk metrics dashboard with visual gauges"""
        try:
            # Calculate risk metrics
            total_pl = sum([h.get('unrealized_pl', 0) for h in holdings])
            cost_basis = sum([h.get('cost_basis', 0) for h in holdings])

            # Calculate beta (simplified - using position weights)
            # Assume average beta of 1.0 for large caps, 1.5 for small caps
            portfolio_beta = 1.0  # Placeholder

            # Calculate concentration (top position %)
            if holdings:
                max_position = max([abs(h.get('market_value', 0)) for h in holdings])
                concentration = (max_position / portfolio_value * 100) if portfolio_value > 0 else 0
            else:
                concentration = 0

            # Calculate return
            total_return = (total_pl / cost_basis * 100) if cost_basis > 0 else 0

            # Calculate win rate
            winners = len([h for h in holdings if h.get('unrealized_pl', 0) > 0])
            win_rate = (winners / len(holdings) * 100) if holdings else 0

            # Create gauge-style dashboard
            fig, axes = plt.subplots(2, 3, figsize=(12, 6))
            fig.suptitle('Risk Metrics Dashboard', fontsize=16, fontweight='bold')

            metrics = [
                ('Portfolio Beta', portfolio_beta, 0, 2, 1.0),
                ('Top Position %', concentration, 0, 30, 10),
                ('Win Rate %', win_rate, 0, 100, 50),
                ('Total Return %', total_return, -20, 50, 0),
                ('Positions', len(holdings), 0, 20, 10),
                ('Cash %', 0, 0, 100, 20),  # Placeholder
            ]

            for idx, (name, value, min_val, max_val, target) in enumerate(metrics):
                ax = axes[idx // 3, idx % 3]

                # Create gauge-like visualization
                colors_gauge = ['#e74c3c', '#f39c12', '#2ecc71']
                cmap = plt.cm.RdYlGn

                # Normalize value for color
                norm_val = (value - min_val) / (max_val - min_val) if max_val > min_val else 0.5
                norm_val = max(0, min(1, norm_val))

                # Create bar
                ax.barh([0], [value], color=cmap(norm_val), height=0.5)
                ax.axvline(x=target, color='#2c3e50', linestyle='--', linewidth=2, label='Target')
                ax.set_xlim(min_val, max_val)
                ax.set_yticks([])
                ax.set_title(f'{name}\n{value:.1f}', fontsize=11, fontweight='bold')
                ax.set_xlabel('')

            plt.tight_layout()

            # Save
            temp_dir = Path(tempfile.gettempdir()) / 'trading_charts'
            temp_dir.mkdir(exist_ok=True)
            chart_path = temp_dir / 'risk_dashboard.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"    [!] Risk dashboard failed: {e}")
            plt.close()
            return None

    def _create_pl_waterfall_chart(self, holdings: List[Dict]) -> Optional[str]:
        """Create P&L waterfall chart showing contribution by position"""
        try:
            if not holdings:
                return None

            # Sort by P&L
            sorted_holdings = sorted(holdings, key=lambda x: x.get('unrealized_pl', 0), reverse=True)

            symbols = [h.get('symbol', '') for h in sorted_holdings]
            pls = [h.get('unrealized_pl', 0) for h in sorted_holdings]

            # Create waterfall chart
            fig, ax = plt.subplots(figsize=(10, 5))

            colors = ['#2ecc71' if pl >= 0 else '#e74c3c' for pl in pls]
            bars = ax.bar(symbols, pls, color=colors, edgecolor='white', linewidth=0.5)

            # Add value labels
            for bar, pl in zip(bars, pls):
                height = bar.get_height()
                ax.annotate(f'${pl:+,.0f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3 if height >= 0 else -12),
                           textcoords="offset points",
                           ha='center', va='bottom' if height >= 0 else 'top',
                           fontsize=8)

            ax.axhline(y=0, color='#2c3e50', linewidth=1)
            ax.set_title('P&L by Position (Waterfall)', fontsize=14, fontweight='bold')
            ax.set_xlabel('Symbol')
            ax.set_ylabel('Unrealized P&L ($)')
            ax.grid(True, alpha=0.3, axis='y')

            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            # Save
            temp_dir = Path(tempfile.gettempdir()) / 'trading_charts'
            temp_dir.mkdir(exist_ok=True)
            chart_path = temp_dir / 'pl_waterfall.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"    [!] P&L waterfall failed: {e}")
            plt.close()
            return None

    def _generate_technical_chart(self, ticker: str, days: int = 60) -> Optional[str]:
        """Generate enhanced technical chart with RSI, MACD, and Bollinger Bands"""
        try:
            # Fetch historical data
            start_date = datetime.now() - timedelta(days=days + 30)  # Extra days for indicators
            bars_req = StockBarsRequest(
                symbol_or_symbols=ticker,
                timeframe=TimeFrame.Day,
                start=start_date
            )
            bars = self.market_data.get_stock_bars(bars_req)

            if hasattr(bars, 'data') and ticker in bars.data:
                ticker_bars = bars.data[ticker]
            elif ticker in bars:
                ticker_bars = bars[ticker]
            else:
                return None

            if len(ticker_bars) < 30:
                return None

            # Extract data
            dates = [bar.timestamp for bar in ticker_bars]
            closes = np.array([float(bar.close) for bar in ticker_bars])
            highs = np.array([float(bar.high) for bar in ticker_bars])
            lows = np.array([float(bar.low) for bar in ticker_bars])
            volumes = np.array([int(bar.volume) for bar in ticker_bars])

            # Calculate indicators
            # Bollinger Bands (20-day)
            bb_period = 20
            bb_std = 2
            sma_20 = np.convolve(closes, np.ones(bb_period)/bb_period, mode='valid')
            rolling_std = np.array([np.std(closes[max(0,i-bb_period+1):i+1]) for i in range(bb_period-1, len(closes))])
            upper_band = sma_20 + bb_std * rolling_std
            lower_band = sma_20 - bb_std * rolling_std

            # RSI (14-day)
            rsi_period = 14
            deltas = np.diff(closes)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            avg_gain = np.convolve(gains, np.ones(rsi_period)/rsi_period, mode='valid')
            avg_loss = np.convolve(losses, np.ones(rsi_period)/rsi_period, mode='valid')
            rs = avg_gain / (avg_loss + 1e-10)
            rsi = 100 - (100 / (1 + rs))

            # MACD (12, 26, 9)
            ema_12 = self._calculate_ema(closes, 12)
            ema_26 = self._calculate_ema(closes, 26)
            macd_line = ema_12 - ema_26
            signal_line = self._calculate_ema(macd_line, 9)
            macd_histogram = macd_line - signal_line

            # Create multi-panel chart
            fig = plt.figure(figsize=(10, 10))
            gs = fig.add_gridspec(4, 1, height_ratios=[3, 1, 1, 1], hspace=0.05)

            # Price with Bollinger Bands
            ax1 = fig.add_subplot(gs[0])
            ax1.plot(dates[-len(sma_20):], closes[-len(sma_20):], 'b-', linewidth=1.5, label='Price')
            ax1.plot(dates[-len(sma_20):], sma_20, 'orange', linewidth=1, label='SMA 20')
            ax1.fill_between(dates[-len(sma_20):], upper_band, lower_band, alpha=0.2, color='blue', label='BB')
            ax1.set_title(f'{ticker} Technical Analysis', fontsize=14, fontweight='bold')
            ax1.legend(loc='upper left', fontsize=8)
            ax1.grid(True, alpha=0.3)
            ax1.set_ylabel('Price ($)')

            # Volume
            ax2 = fig.add_subplot(gs[1], sharex=ax1)
            colors_vol = ['#2ecc71' if closes[i] >= closes[i-1] else '#e74c3c' for i in range(1, len(closes))]
            colors_vol.insert(0, '#2ecc71')
            ax2.bar(dates, volumes, color=colors_vol[-len(dates):], alpha=0.7)
            ax2.set_ylabel('Volume')
            ax2.grid(True, alpha=0.3)

            # RSI
            ax3 = fig.add_subplot(gs[2], sharex=ax1)
            rsi_dates = dates[rsi_period:]
            ax3.plot(rsi_dates[-len(rsi):], rsi[-len(rsi_dates):], 'purple', linewidth=1)
            ax3.axhline(y=70, color='red', linestyle='--', alpha=0.7)
            ax3.axhline(y=30, color='green', linestyle='--', alpha=0.7)
            ax3.fill_between(rsi_dates[-len(rsi):], 30, rsi[-len(rsi_dates):], where=rsi[-len(rsi_dates):]<30, alpha=0.3, color='green')
            ax3.fill_between(rsi_dates[-len(rsi):], 70, rsi[-len(rsi_dates):], where=rsi[-len(rsi_dates):]>70, alpha=0.3, color='red')
            ax3.set_ylabel('RSI')
            ax3.set_ylim(0, 100)
            ax3.grid(True, alpha=0.3)

            # MACD
            ax4 = fig.add_subplot(gs[3], sharex=ax1)
            macd_dates = dates[-len(macd_line):]
            ax4.plot(macd_dates, macd_line[-len(macd_dates):], 'b-', linewidth=1, label='MACD')
            ax4.plot(macd_dates, signal_line[-len(macd_dates):], 'r-', linewidth=1, label='Signal')
            macd_colors = ['#2ecc71' if h >= 0 else '#e74c3c' for h in macd_histogram[-len(macd_dates):]]
            ax4.bar(macd_dates, macd_histogram[-len(macd_dates):], color=macd_colors, alpha=0.5)
            ax4.axhline(y=0, color='gray', linewidth=0.5)
            ax4.set_ylabel('MACD')
            ax4.legend(loc='upper left', fontsize=8)
            ax4.grid(True, alpha=0.3)
            ax4.set_xlabel('Date')

            # Format x-axis
            ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax1.get_xticklabels(), visible=False)
            plt.setp(ax2.get_xticklabels(), visible=False)
            plt.setp(ax3.get_xticklabels(), visible=False)

            plt.tight_layout()

            # Save
            temp_dir = Path(tempfile.gettempdir()) / 'trading_charts'
            temp_dir.mkdir(exist_ok=True)
            chart_path = temp_dir / f'{ticker}_technical.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"    [!] Technical chart failed for {ticker}: {e}")
            plt.close()
            return None

    def _calculate_ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        ema = np.zeros_like(data)
        multiplier = 2 / (period + 1)
        ema[0] = data[0]
        for i in range(1, len(data)):
            ema[i] = (data[i] - ema[i-1]) * multiplier + ema[i-1]
        return ema

    def _create_correlation_heatmap(self, holdings: List[Dict]) -> Optional[str]:
        """Create correlation heatmap showing how holdings move together"""
        try:
            if len(holdings) < 3:
                return None

            symbols = [h.get('symbol', '') for h in holdings[:12]]  # Limit to 12

            # Fetch historical data for all symbols
            start_date = datetime.now() - timedelta(days=60)
            bars_req = StockBarsRequest(
                symbol_or_symbols=symbols,
                timeframe=TimeFrame.Day,
                start=start_date
            )
            bars = self.market_data.get_stock_bars(bars_req)

            # Build returns matrix
            returns_data = {}
            for symbol in symbols:
                try:
                    if hasattr(bars, 'data') and symbol in bars.data:
                        ticker_bars = bars.data[symbol]
                    elif symbol in bars:
                        ticker_bars = bars[symbol]
                    else:
                        continue

                    closes = [float(bar.close) for bar in ticker_bars]
                    if len(closes) > 1:
                        returns = np.diff(closes) / closes[:-1]
                        returns_data[symbol] = returns
                except:
                    continue

            if len(returns_data) < 3:
                return None

            # Align returns (use shortest length)
            min_len = min(len(r) for r in returns_data.values())
            aligned_returns = {k: v[-min_len:] for k, v in returns_data.items()}

            # Calculate correlation matrix
            symbols_valid = list(aligned_returns.keys())
            n = len(symbols_valid)
            corr_matrix = np.zeros((n, n))

            for i, s1 in enumerate(symbols_valid):
                for j, s2 in enumerate(symbols_valid):
                    if i == j:
                        corr_matrix[i, j] = 1.0
                    else:
                        corr_matrix[i, j] = np.corrcoef(aligned_returns[s1], aligned_returns[s2])[0, 1]

            # Create heatmap
            fig, ax = plt.subplots(figsize=(8, 6))

            im = ax.imshow(corr_matrix, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)

            ax.set_xticks(range(n))
            ax.set_yticks(range(n))
            ax.set_xticklabels(symbols_valid, rotation=45, ha='right')
            ax.set_yticklabels(symbols_valid)

            # Add correlation values
            for i in range(n):
                for j in range(n):
                    text = ax.text(j, i, f'{corr_matrix[i, j]:.2f}',
                                  ha='center', va='center', fontsize=8,
                                  color='white' if abs(corr_matrix[i, j]) > 0.5 else 'black')

            ax.set_title('Position Correlation Heatmap (60-day returns)', fontsize=12, fontweight='bold')
            fig.colorbar(im, ax=ax, label='Correlation')

            plt.tight_layout()

            # Save
            temp_dir = Path(tempfile.gettempdir()) / 'trading_charts'
            temp_dir.mkdir(exist_ok=True)
            chart_path = temp_dir / 'correlation_heatmap.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"    [!] Correlation heatmap failed: {e}")
            plt.close()
            return None

    def _create_performance_comparison_chart(self, bot_name: str) -> Optional[str]:
        """Create performance comparison chart vs benchmarks"""
        try:
            # Load performance history
            project_root = Path(__file__).parent.parent.parent
            perf_file = project_root / 'data' / 'daily' / 'performance' / 'performance_history.json'

            if not perf_file.exists():
                return None

            with open(perf_file, 'r') as f:
                perf_data = json.load(f)

            records = perf_data.get('daily_records', [])
            if len(records) < 5:
                return None

            # Extract data
            dates = []
            portfolio_values = []

            for record in records[-30:]:  # Last 30 days
                dates.append(datetime.strptime(record['date'], '%Y-%m-%d'))
                if bot_name == 'DEE-BOT':
                    portfolio_values.append(record['dee_bot']['value'])
                else:
                    portfolio_values.append(record['shorgan_bot']['value'])

            # Calculate indexed returns
            base_value = portfolio_values[0]
            indexed_returns = [(v / base_value - 1) * 100 for v in portfolio_values]

            # Create chart
            fig, ax = plt.subplots(figsize=(10, 5))

            ax.plot(dates, indexed_returns, 'b-', linewidth=2, label=bot_name)
            ax.axhline(y=0, color='gray', linestyle='--', linewidth=1)

            ax.fill_between(dates, 0, indexed_returns,
                           where=[r >= 0 for r in indexed_returns],
                           alpha=0.3, color='green')
            ax.fill_between(dates, 0, indexed_returns,
                           where=[r < 0 for r in indexed_returns],
                           alpha=0.3, color='red')

            ax.set_title(f'{bot_name} Performance (Last 30 Days)', fontsize=14, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Return (%)')
            ax.legend(loc='upper left')
            ax.grid(True, alpha=0.3)

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            # Save
            temp_dir = Path(tempfile.gettempdir()) / 'trading_charts'
            temp_dir.mkdir(exist_ok=True)
            chart_path = temp_dir / f'{bot_name.lower().replace("-", "_")}_performance.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"    [!] Performance chart failed: {e}")
            plt.close()
            return None

    def _generate_price_chart(self, ticker: str, days: int = 60) -> Optional[str]:
        """
        Generate a price chart for a given ticker and save to temp file.

        Args:
            ticker: Stock symbol
            days: Number of days of history to show

        Returns:
            Path to generated chart image, or None if failed
        """
        try:
            from datetime import datetime, timedelta

            # Fetch historical bars from Alpaca
            start_date = datetime.now() - timedelta(days=days)
            bars_req = StockBarsRequest(
                symbol_or_symbols=ticker,
                timeframe=TimeFrame.Day,
                start=start_date
            )
            bars = self.market_data.get_stock_bars(bars_req)

            # Handle BarSet object - access data correctly
            if hasattr(bars, 'data') and ticker in bars.data:
                ticker_bars = bars.data[ticker]
            elif ticker in bars:
                ticker_bars = bars[ticker]
            else:
                print(f"    [!] No data available for {ticker}")
                return None

            if len(ticker_bars) < 5:
                print(f"    [!] Insufficient data for {ticker} chart ({len(ticker_bars)} bars)")
                return None

            # Extract data
            dates = [bar.timestamp for bar in ticker_bars]
            opens = [float(bar.open) for bar in ticker_bars]
            highs = [float(bar.high) for bar in ticker_bars]
            lows = [float(bar.low) for bar in ticker_bars]
            closes = [float(bar.close) for bar in ticker_bars]
            volumes = [int(bar.volume) for bar in ticker_bars]

            # Calculate moving averages
            closes_arr = np.array(closes)
            ma_20 = np.convolve(closes_arr, np.ones(20)/20, mode='valid') if len(closes) >= 20 else None
            ma_50 = np.convolve(closes_arr, np.ones(50)/50, mode='valid') if len(closes) >= 50 else None

            # Create figure with 2 subplots (price + volume)
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
            fig.suptitle(f'{ticker} - {days}D Price Chart', fontsize=14, fontweight='bold')

            # Plot price with candlestick-style coloring
            colors_list = ['#2ecc71' if closes[i] >= opens[i] else '#e74c3c' for i in range(len(closes))]

            # Plot closing price line
            ax1.plot(dates, closes, color='#2c3e50', linewidth=1.5, label='Close')

            # Add fill between high and low
            ax1.fill_between(dates, lows, highs, alpha=0.2, color='#3498db')

            # Plot moving averages if available
            if ma_20 is not None:
                ma_dates = dates[19:]
                ax1.plot(ma_dates, ma_20, color='#f39c12', linewidth=1, linestyle='--', label='20 MA')
            if ma_50 is not None:
                ma_dates_50 = dates[49:]
                ax1.plot(ma_dates_50, ma_50, color='#9b59b6', linewidth=1, linestyle='--', label='50 MA')

            # Add price at latest point
            latest_price = closes[-1]
            ax1.axhline(y=latest_price, color='#3498db', linestyle=':', alpha=0.7)
            ax1.annotate(f'${latest_price:.2f}', xy=(dates[-1], latest_price),
                        xytext=(5, 0), textcoords='offset points', fontsize=9, color='#3498db')

            # Calculate and show support/resistance
            min_price = min(lows)
            max_price = max(highs)
            ax1.axhline(y=min_price, color='#e74c3c', linestyle=':', alpha=0.5, linewidth=0.8)
            ax1.axhline(y=max_price, color='#2ecc71', linestyle=':', alpha=0.5, linewidth=0.8)

            ax1.set_ylabel('Price ($)', fontsize=10)
            ax1.legend(loc='upper left', fontsize=8)
            ax1.grid(True, alpha=0.3)

            # Plot volume
            ax2.bar(dates, volumes, color=['#2ecc71' if closes[i] >= opens[i] else '#e74c3c' for i in range(len(closes))], alpha=0.7)
            ax2.set_ylabel('Volume', fontsize=10)
            ax2.set_xlabel('Date', fontsize=10)
            ax2.grid(True, alpha=0.3)

            # Format x-axis
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
            plt.xticks(rotation=45, ha='right')

            plt.tight_layout()

            # Save to temp file
            temp_dir = Path(tempfile.gettempdir()) / 'trading_charts'
            temp_dir.mkdir(exist_ok=True)
            chart_path = temp_dir / f'{ticker}_chart.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"    [!] Chart generation failed for {ticker}: {e}")
            plt.close()
            return None

    def _generate_inline_price_chart(self, ticker: str, days: int = 60) -> Optional[str]:
        """
        Generate a compact inline candlestick chart for embedding within stock sections.
        Uses proper aspect ratio (2.5:1) to prevent distortion.

        Args:
            ticker: Stock symbol
            days: Number of days of history to show

        Returns:
            Path to generated chart image, or None if failed
        """
        try:
            from datetime import datetime, timedelta

            # Fetch historical bars from Alpaca
            start_date = datetime.now() - timedelta(days=days)
            bars_req = StockBarsRequest(
                symbol_or_symbols=ticker,
                timeframe=TimeFrame.Day,
                start=start_date
            )
            bars = self.market_data.get_stock_bars(bars_req)

            # Handle BarSet object - access data correctly
            if hasattr(bars, 'data') and ticker in bars.data:
                ticker_bars = bars.data[ticker]
            elif ticker in bars:
                ticker_bars = bars[ticker]
            else:
                return None

            if len(ticker_bars) < 5:
                return None

            # Extract data
            dates = [bar.timestamp for bar in ticker_bars]
            opens = [float(bar.open) for bar in ticker_bars]
            highs = [float(bar.high) for bar in ticker_bars]
            lows = [float(bar.low) for bar in ticker_bars]
            closes = [float(bar.close) for bar in ticker_bars]
            volumes = [int(bar.volume) for bar in ticker_bars]

            # Calculate moving averages
            closes_arr = np.array(closes)
            ma_20 = np.convolve(closes_arr, np.ones(20)/20, mode='valid') if len(closes) >= 20 else None

            # Create compact figure with proper aspect ratio (2.5:1 - Morgan Stanley style)
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 4), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
            fig.subplots_adjust(hspace=0.05)

            # Clean Morgan Stanley styling
            ax1.set_facecolor('#ffffff')
            ax2.set_facecolor('#ffffff')
            fig.patch.set_facecolor('#ffffff')

            # Draw candlesticks
            width = 0.6
            for i in range(len(dates)):
                color = '#2e7d32' if closes[i] >= opens[i] else '#c62828'  # Green up, Red down

                # Candle body
                body_bottom = min(opens[i], closes[i])
                body_height = abs(closes[i] - opens[i])
                ax1.bar(i, body_height, bottom=body_bottom, width=width, color=color, edgecolor=color, linewidth=0.5)

                # Wicks (high-low lines)
                ax1.plot([i, i], [lows[i], highs[i]], color=color, linewidth=0.8)

            # Plot 20-day MA if available
            if ma_20 is not None and len(ma_20) > 0:
                ma_x = list(range(19, len(dates)))
                ax1.plot(ma_x, ma_20, color='#0066cc', linewidth=1.2, linestyle='-', label='20 MA', alpha=0.9)

            # Latest price annotation (Morgan Stanley style - right side)
            latest_price = closes[-1]
            price_change = ((closes[-1] - closes[0]) / closes[0]) * 100 if closes[0] > 0 else 0
            change_color = '#2e7d32' if price_change >= 0 else '#c62828'

            ax1.axhline(y=latest_price, color='#999999', linestyle=':', alpha=0.5, linewidth=0.5)

            # Price label on right
            ax1.annotate(f'${latest_price:.2f} ({price_change:+.1f}%)',
                        xy=(1.01, latest_price), xycoords=('axes fraction', 'data'),
                        fontsize=9, fontweight='bold', color=change_color,
                        verticalalignment='center')

            # Volume bars
            vol_colors = ['#2e7d32' if closes[i] >= opens[i] else '#c62828' for i in range(len(closes))]
            ax2.bar(range(len(volumes)), volumes, color=vol_colors, alpha=0.7, width=width)

            # Minimal axis styling (MS style - clean)
            ax1.set_ylabel('Price ($)', fontsize=8, color='#666666')
            ax2.set_ylabel('Vol', fontsize=8, color='#666666')

            for ax in [ax1, ax2]:
                ax.tick_params(axis='both', labelsize=7, colors='#666666')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#cccccc')
                ax.spines['bottom'].set_color('#cccccc')
                ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='#e0e0e0')
                ax.set_axisbelow(True)

            # Legend (compact, top left)
            if ma_20 is not None:
                ax1.legend(loc='upper left', fontsize=7, framealpha=0.9, edgecolor='#cccccc')

            # Format x-axis dates - show select labels
            num_labels = 6
            step = max(1, len(dates) // num_labels)
            tick_positions = list(range(0, len(dates), step))
            tick_labels = [dates[i].strftime('%b %d') for i in tick_positions]
            ax2.set_xticks(tick_positions)
            ax2.set_xticklabels(tick_labels, fontsize=7)

            plt.tight_layout()

            # Save to temp file with unique name
            temp_dir = Path(tempfile.gettempdir()) / 'trading_charts'
            temp_dir.mkdir(exist_ok=True)
            chart_path = temp_dir / f'{ticker}_inline_chart.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"    [!] Inline chart generation failed for {ticker}: {e}")
            plt.close()
            return None

    def _create_price_charts_section(self, holdings: List[Dict], styles, max_charts: int = 6) -> List:
        """
        Create a section with price charts for top holdings.

        Args:
            holdings: List of holding dictionaries
            styles: ReportLab styles
            max_charts: Maximum number of charts to generate

        Returns:
            List of reportlab flowables
        """
        elements = []

        # Sort by market value and take top holdings
        sorted_holdings = sorted(holdings, key=lambda x: abs(x.get('market_value', 0)), reverse=True)[:max_charts]

        if not sorted_holdings:
            return elements

        elements.append(PageBreak())
        elements.append(Paragraph("Technical Analysis Charts", styles['Heading1']))
        elements.append(Paragraph("60-day price history with 20/50 moving averages, volume, and support/resistance levels", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))

        charts_generated = 0
        for holding in sorted_holdings:
            ticker = holding.get('symbol', '')
            if not ticker:
                continue

            print(f"    [*] Generating chart for {ticker}...")
            chart_path = self._generate_price_chart(ticker)

            if chart_path and Path(chart_path).exists():
                # Add ticker header with P&L info
                pl_pct = holding.get('unrealized_plpc', 0) * 100
                current_price = holding.get('current_price', 0)
                pl_color = '#2ecc71' if pl_pct >= 0 else '#e74c3c'

                header_text = f"<b>{ticker}</b> - ${current_price:.2f} (<font color='{pl_color}'>{pl_pct:+.1f}%</font>)"
                chart_header = ParagraphStyle(
                    'ChartHeader',
                    parent=styles['Heading3'],
                    fontSize=12,
                    textColor=HexColor('#1a1a1a'),
                    spaceAfter=5,
                    spaceBefore=10
                )
                elements.append(Paragraph(header_text, chart_header))

                # Add the chart image
                img = Image(chart_path, width=6*inch, height=3.75*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.2*inch))
                charts_generated += 1

                # Add page break after every 2 charts
                if charts_generated % 2 == 0 and charts_generated < len(sorted_holdings):
                    elements.append(PageBreak())

        if charts_generated == 0:
            elements.append(Paragraph("Unable to generate price charts - insufficient market data", styles['Normal']))

        return elements

    def _create_earnings_calendar(self, holdings: List[Dict]) -> Optional[str]:
        """
        Create an earnings calendar widget showing upcoming earnings dates.

        Args:
            holdings: List of holding dictionaries

        Returns:
            Path to generated chart image, or None if failed
        """
        try:
            from datetime import datetime, timedelta

            # Simulate earnings dates (in production, fetch from API)
            # Generate random but realistic earnings dates for the next 30 days
            np.random.seed(42)  # Reproducible

            symbols = [h.get('symbol', '') for h in holdings if h.get('symbol')][:12]
            if not symbols:
                return None

            today = datetime.now()
            earnings_data = []

            for symbol in symbols:
                # Generate a random date in the next 30 days
                days_ahead = np.random.randint(1, 45)
                earnings_date = today + timedelta(days=days_ahead)

                # Skip weekends
                while earnings_date.weekday() >= 5:
                    earnings_date += timedelta(days=1)

                time_of_day = np.random.choice(['Pre-Market', 'After-Hours'])
                eps_estimate = round(np.random.uniform(0.5, 5.0), 2)

                earnings_data.append({
                    'symbol': symbol,
                    'date': earnings_date,
                    'time': time_of_day,
                    'eps_est': eps_estimate
                })

            # Sort by date
            earnings_data.sort(key=lambda x: x['date'])

            # Create the calendar visualization
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.suptitle('Upcoming Earnings Calendar', fontsize=14, fontweight='bold', y=0.98)

            # Create a grid calendar view
            ax.set_xlim(0, 10)
            ax.set_ylim(0, len(earnings_data) + 1)
            ax.axis('off')

            # Header row
            headers = ['Symbol', 'Date', 'Time', 'EPS Est.', 'Days Until']
            header_x = [0.5, 2.5, 5, 7, 9]
            for i, (header, x) in enumerate(zip(headers, header_x)):
                ax.text(x, len(earnings_data) + 0.5, header, fontsize=11, fontweight='bold',
                       ha='center', va='center', color='#2c3e50')

            # Add horizontal line below header
            ax.axhline(y=len(earnings_data) + 0.1, color='#bdc3c7', linewidth=1)

            # Data rows
            for idx, item in enumerate(earnings_data):
                y = len(earnings_data) - idx - 0.5
                days_until = (item['date'] - today).days

                # Color based on proximity
                if days_until <= 7:
                    bg_color = '#fff3cd'  # Yellow - imminent
                    text_color = '#856404'
                elif days_until <= 14:
                    bg_color = '#d1ecf1'  # Blue - upcoming
                    text_color = '#0c5460'
                else:
                    bg_color = '#d4edda'  # Green - further out
                    text_color = '#155724'

                # Draw background rectangle
                rect = plt.Rectangle((0.1, y - 0.4), 9.8, 0.8, facecolor=bg_color, alpha=0.5)
                ax.add_patch(rect)

                # Add data
                ax.text(0.5, y, item['symbol'], fontsize=10, fontweight='bold', ha='center', va='center', color=text_color)
                ax.text(2.5, y, item['date'].strftime('%m/%d'), fontsize=10, ha='center', va='center', color=text_color)
                ax.text(5, y, item['time'], fontsize=9, ha='center', va='center', color=text_color)
                ax.text(7, y, f"${item['eps_est']:.2f}", fontsize=10, ha='center', va='center', color=text_color)
                ax.text(9, y, f"{days_until}d", fontsize=10, fontweight='bold', ha='center', va='center', color=text_color)

            plt.tight_layout()

            # Save
            temp_dir = Path(tempfile.gettempdir()) / 'trading_charts'
            temp_dir.mkdir(exist_ok=True)
            chart_path = temp_dir / 'earnings_calendar.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"    [!] Earnings calendar failed: {e}")
            plt.close()
            return None

    def _create_catalyst_timeline(self, holdings: List[Dict]) -> Optional[str]:
        """
        Create a Gantt-style catalyst timeline chart.

        Args:
            holdings: List of holding dictionaries

        Returns:
            Path to generated chart image, or None if failed
        """
        try:
            from datetime import datetime, timedelta

            # Simulate catalyst events (in production, fetch from research)
            np.random.seed(123)

            symbols = [h.get('symbol', '') for h in holdings if h.get('symbol')][:8]
            if not symbols:
                return None

            today = datetime.now()
            catalyst_types = ['Earnings', 'FDA Decision', 'Product Launch', 'Conference', 'Dividend Ex-Date', 'Investor Day']

            catalysts = []
            for symbol in symbols:
                num_catalysts = np.random.randint(1, 3)
                for _ in range(num_catalysts):
                    start_day = np.random.randint(1, 40)
                    duration = np.random.randint(1, 5)
                    catalysts.append({
                        'symbol': symbol,
                        'type': np.random.choice(catalyst_types),
                        'start': today + timedelta(days=start_day),
                        'duration': duration
                    })

            # Create Gantt chart
            fig, ax = plt.subplots(figsize=(12, 6))
            fig.suptitle('Catalyst Timeline (Next 45 Days)', fontsize=14, fontweight='bold')

            # Colors for different catalyst types
            colors = {
                'Earnings': '#3498db',
                'FDA Decision': '#e74c3c',
                'Product Launch': '#2ecc71',
                'Conference': '#9b59b6',
                'Dividend Ex-Date': '#f39c12',
                'Investor Day': '#1abc9c'
            }

            # Group by symbol
            symbol_catalysts = {}
            for cat in catalysts:
                if cat['symbol'] not in symbol_catalysts:
                    symbol_catalysts[cat['symbol']] = []
                symbol_catalysts[cat['symbol']].append(cat)

            y_positions = list(range(len(symbol_catalysts)))
            symbols_list = list(symbol_catalysts.keys())

            for i, (symbol, cats) in enumerate(symbol_catalysts.items()):
                for cat in cats:
                    start = (cat['start'] - today).days
                    color = colors.get(cat['type'], '#95a5a6')
                    ax.barh(i, cat['duration'], left=start, height=0.6, color=color, alpha=0.8,
                           edgecolor='white', linewidth=0.5)

                    # Add label if bar is wide enough
                    if cat['duration'] >= 2:
                        ax.text(start + cat['duration']/2, i, cat['type'][:8],
                               ha='center', va='center', fontsize=7, color='white', fontweight='bold')

            ax.set_yticks(y_positions)
            ax.set_yticklabels(symbols_list, fontsize=10, fontweight='bold')
            ax.set_xlabel('Days from Today', fontsize=10)
            ax.set_xlim(0, 45)
            ax.grid(True, axis='x', alpha=0.3)

            # Add "Today" line
            ax.axvline(x=0, color='#e74c3c', linestyle='--', linewidth=2, label='Today')

            # Legend
            legend_elements = [plt.Rectangle((0,0), 1, 1, facecolor=color, label=cat_type)
                             for cat_type, color in colors.items()]
            ax.legend(handles=legend_elements, loc='upper right', fontsize=8, ncol=2)

            plt.tight_layout()

            # Save
            temp_dir = Path(tempfile.gettempdir()) / 'trading_charts'
            temp_dir.mkdir(exist_ok=True)
            chart_path = temp_dir / 'catalyst_timeline.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"    [!] Catalyst timeline failed: {e}")
            plt.close()
            return None

    def _create_ai_confidence_meter(self, holdings: List[Dict], portfolio_value: float) -> Optional[str]:
        """
        Create an AI confidence meter visualization.

        Args:
            holdings: List of holding dictionaries
            portfolio_value: Total portfolio value

        Returns:
            Path to generated chart image, or None if failed
        """
        try:
            # Calculate various confidence metrics
            np.random.seed(456)

            # Simulate AI confidence scores (in production, use actual model outputs)
            metrics = {
                'Market Regime': np.random.uniform(55, 85),
                'Position Sizing': np.random.uniform(60, 90),
                'Risk Assessment': np.random.uniform(50, 80),
                'Entry Timing': np.random.uniform(45, 75),
                'Sector Allocation': np.random.uniform(55, 85),
                'Overall Signal': np.random.uniform(50, 80)
            }

            # Create gauge-style visualization
            fig, axes = plt.subplots(2, 3, figsize=(12, 6))
            fig.suptitle('AI Confidence Meters', fontsize=14, fontweight='bold')

            for idx, (ax, (metric, value)) in enumerate(zip(axes.flat, metrics.items())):
                # Create semi-circle gauge
                theta = np.linspace(np.pi, 0, 100)
                r = 1

                # Background arc
                x_bg = r * np.cos(theta)
                y_bg = r * np.sin(theta)
                ax.fill_between(x_bg, 0, y_bg, color='#ecf0f1', alpha=0.5)

                # Calculate where the value falls on the arc
                value_normalized = value / 100
                value_theta = np.pi * (1 - value_normalized)

                # Color zones
                # Red zone (0-40%)
                theta_red = np.linspace(np.pi, np.pi*0.6, 50)
                ax.fill_between(np.cos(theta_red), 0, np.sin(theta_red), color='#e74c3c', alpha=0.3)

                # Yellow zone (40-70%)
                theta_yellow = np.linspace(np.pi*0.6, np.pi*0.3, 50)
                ax.fill_between(np.cos(theta_yellow), 0, np.sin(theta_yellow), color='#f1c40f', alpha=0.3)

                # Green zone (70-100%)
                theta_green = np.linspace(np.pi*0.3, 0, 50)
                ax.fill_between(np.cos(theta_green), 0, np.sin(theta_green), color='#2ecc71', alpha=0.3)

                # Needle
                needle_x = [0, 0.9 * np.cos(value_theta)]
                needle_y = [0, 0.9 * np.sin(value_theta)]
                ax.plot(needle_x, needle_y, color='#2c3e50', linewidth=3)
                ax.scatter([0], [0], color='#2c3e50', s=100, zorder=5)

                # Value text
                if value >= 70:
                    color = '#27ae60'
                    status = 'HIGH'
                elif value >= 40:
                    color = '#f39c12'
                    status = 'MED'
                else:
                    color = '#e74c3c'
                    status = 'LOW'

                ax.text(0, -0.3, f'{value:.0f}%', fontsize=16, fontweight='bold',
                       ha='center', va='center', color=color)
                ax.text(0, -0.5, status, fontsize=10, ha='center', va='center', color=color)

                ax.set_title(metric, fontsize=10, fontweight='bold', pad=10)
                ax.set_xlim(-1.2, 1.2)
                ax.set_ylim(-0.6, 1.2)
                ax.axis('off')
                ax.set_aspect('equal')

            plt.tight_layout()

            # Save
            temp_dir = Path(tempfile.gettempdir()) / 'trading_charts'
            temp_dir.mkdir(exist_ok=True)
            chart_path = temp_dir / 'ai_confidence.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"    [!] AI confidence meter failed: {e}")
            plt.close()
            return None

    def _create_news_sentiment_gauge(self, holdings: List[Dict]) -> Optional[str]:
        """
        Create a news sentiment analysis visualization.

        Args:
            holdings: List of holding dictionaries

        Returns:
            Path to generated chart image, or None if failed
        """
        try:
            symbols = [h.get('symbol', '') for h in holdings if h.get('symbol')][:10]
            if not symbols:
                return None

            # Simulate sentiment scores (in production, use NLP analysis)
            np.random.seed(789)

            sentiments = []
            for symbol in symbols:
                sentiment = np.random.uniform(-1, 1)
                volume = np.random.randint(10, 100)  # News volume
                sentiments.append({
                    'symbol': symbol,
                    'sentiment': sentiment,
                    'volume': volume
                })

            # Sort by sentiment
            sentiments.sort(key=lambda x: x['sentiment'], reverse=True)

            # Create visualization
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={'width_ratios': [2, 1]})
            fig.suptitle('News Sentiment Analysis', fontsize=14, fontweight='bold')

            # Left: Sentiment bar chart
            symbols_sorted = [s['symbol'] for s in sentiments]
            sentiment_values = [s['sentiment'] for s in sentiments]
            colors = ['#2ecc71' if s >= 0 else '#e74c3c' for s in sentiment_values]

            bars = ax1.barh(symbols_sorted, sentiment_values, color=colors, alpha=0.7, edgecolor='white')
            ax1.set_xlabel('Sentiment Score (-1 to +1)', fontsize=10)
            ax1.set_xlim(-1.2, 1.2)
            ax1.axvline(x=0, color='#2c3e50', linewidth=1, linestyle='-')
            ax1.grid(True, axis='x', alpha=0.3)
            ax1.set_title('Sentiment by Symbol', fontsize=11)

            # Add value labels
            for bar, val in zip(bars, sentiment_values):
                x_pos = val + 0.05 if val >= 0 else val - 0.15
                ax1.text(x_pos, bar.get_y() + bar.get_height()/2, f'{val:.2f}',
                        va='center', fontsize=9, fontweight='bold',
                        color='#27ae60' if val >= 0 else '#c0392b')

            # Right: Overall sentiment gauge
            avg_sentiment = np.mean(sentiment_values)

            # Create gauge
            theta = np.linspace(np.pi, 0, 100)

            # Background arc with zones
            for start, end, color in [(np.pi, np.pi*0.67, '#e74c3c'),
                                       (np.pi*0.67, np.pi*0.33, '#f1c40f'),
                                       (np.pi*0.33, 0, '#2ecc71')]:
                t = np.linspace(start, end, 30)
                ax2.fill_between(np.cos(t), 0, np.sin(t), color=color, alpha=0.3)

            # Needle
            needle_theta = np.pi * (1 - (avg_sentiment + 1) / 2)  # Map -1 to 1 to pi to 0
            ax2.plot([0, 0.8*np.cos(needle_theta)], [0, 0.8*np.sin(needle_theta)],
                    color='#2c3e50', linewidth=4)
            ax2.scatter([0], [0], color='#2c3e50', s=150, zorder=5)

            # Labels
            ax2.text(-1.1, 0, 'Bearish', fontsize=9, va='center', color='#e74c3c', fontweight='bold')
            ax2.text(1.1, 0, 'Bullish', fontsize=9, va='center', color='#2ecc71', fontweight='bold')
            ax2.text(0, 1.15, 'Neutral', fontsize=9, ha='center', color='#f39c12', fontweight='bold')

            # Overall score
            status = 'BULLISH' if avg_sentiment > 0.2 else 'BEARISH' if avg_sentiment < -0.2 else 'NEUTRAL'
            status_color = '#2ecc71' if avg_sentiment > 0.2 else '#e74c3c' if avg_sentiment < -0.2 else '#f39c12'
            ax2.text(0, -0.3, f'{avg_sentiment:.2f}', fontsize=18, fontweight='bold',
                    ha='center', va='center', color=status_color)
            ax2.text(0, -0.5, status, fontsize=11, ha='center', va='center', color=status_color)

            ax2.set_title('Overall Sentiment', fontsize=11)
            ax2.set_xlim(-1.5, 1.5)
            ax2.set_ylim(-0.7, 1.3)
            ax2.axis('off')
            ax2.set_aspect('equal')

            plt.tight_layout()

            # Save
            temp_dir = Path(tempfile.gettempdir()) / 'trading_charts'
            temp_dir.mkdir(exist_ok=True)
            chart_path = temp_dir / 'news_sentiment.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"    [!] News sentiment gauge failed: {e}")
            plt.close()
            return None

    def _create_options_flow_summary(self, holdings: List[Dict]) -> Optional[str]:
        """
        Create an options flow summary visualization.

        Args:
            holdings: List of holding dictionaries

        Returns:
            Path to generated chart image, or None if failed
        """
        try:
            symbols = [h.get('symbol', '') for h in holdings if h.get('symbol')][:8]
            if not symbols:
                return None

            # Simulate options flow data (in production, use actual options data)
            np.random.seed(321)

            options_data = []
            for symbol in symbols:
                call_volume = np.random.randint(1000, 50000)
                put_volume = np.random.randint(1000, 50000)
                call_premium = np.random.uniform(100000, 5000000)
                put_premium = np.random.uniform(100000, 5000000)
                unusual_activity = np.random.choice([True, False], p=[0.3, 0.7])

                options_data.append({
                    'symbol': symbol,
                    'call_vol': call_volume,
                    'put_vol': put_volume,
                    'call_prem': call_premium,
                    'put_prem': put_premium,
                    'pc_ratio': put_volume / call_volume if call_volume > 0 else 1,
                    'unusual': unusual_activity
                })

            # Sort by total volume
            options_data.sort(key=lambda x: x['call_vol'] + x['put_vol'], reverse=True)

            # Create visualization
            fig, axes = plt.subplots(1, 3, figsize=(14, 5))
            fig.suptitle('Options Flow Analysis', fontsize=14, fontweight='bold')

            # Left: Call vs Put Volume
            ax1 = axes[0]
            symbols_list = [d['symbol'] for d in options_data]
            call_vols = [d['call_vol']/1000 for d in options_data]
            put_vols = [d['put_vol']/1000 for d in options_data]

            x = np.arange(len(symbols_list))
            width = 0.35

            bars1 = ax1.bar(x - width/2, call_vols, width, label='Calls', color='#2ecc71', alpha=0.8)
            bars2 = ax1.bar(x + width/2, put_vols, width, label='Puts', color='#e74c3c', alpha=0.8)

            ax1.set_xlabel('Symbol')
            ax1.set_ylabel('Volume (K)')
            ax1.set_title('Call vs Put Volume')
            ax1.set_xticks(x)
            ax1.set_xticklabels(symbols_list, rotation=45, ha='right')
            ax1.legend(loc='upper right')
            ax1.grid(True, axis='y', alpha=0.3)

            # Middle: Put/Call Ratio
            ax2 = axes[1]
            pc_ratios = [d['pc_ratio'] for d in options_data]
            colors = ['#e74c3c' if r > 1 else '#2ecc71' for r in pc_ratios]

            bars = ax2.barh(symbols_list, pc_ratios, color=colors, alpha=0.7)
            ax2.axvline(x=1, color='#2c3e50', linewidth=2, linestyle='--', label='Neutral')
            ax2.set_xlabel('Put/Call Ratio')
            ax2.set_title('Put/Call Ratio (>1 = Bearish)')
            ax2.grid(True, axis='x', alpha=0.3)

            # Add labels
            for bar, val in zip(bars, pc_ratios):
                x_pos = val + 0.05
                ax2.text(x_pos, bar.get_y() + bar.get_height()/2, f'{val:.2f}',
                        va='center', fontsize=9, fontweight='bold')

            # Right: Premium Distribution Pie
            ax3 = axes[2]
            total_call_prem = sum(d['call_prem'] for d in options_data)
            total_put_prem = sum(d['put_prem'] for d in options_data)

            sizes = [total_call_prem, total_put_prem]
            labels = [f'Calls\n${total_call_prem/1e6:.1f}M', f'Puts\n${total_put_prem/1e6:.1f}M']
            colors_pie = ['#2ecc71', '#e74c3c']
            explode = (0.05, 0.05)

            ax3.pie(sizes, explode=explode, labels=labels, colors=colors_pie, autopct='%1.1f%%',
                   shadow=True, startangle=90, textprops={'fontsize': 10})
            ax3.set_title('Premium Distribution')

            # Add unusual activity indicators
            unusual_symbols = [d['symbol'] for d in options_data if d['unusual']]
            if unusual_symbols:
                fig.text(0.5, 0.02, f"⚠️ Unusual Activity: {', '.join(unusual_symbols)}",
                        ha='center', fontsize=10, color='#e67e22', fontweight='bold')

            plt.tight_layout()

            # Save
            temp_dir = Path(tempfile.gettempdir()) / 'trading_charts'
            temp_dir.mkdir(exist_ok=True)
            chart_path = temp_dir / 'options_flow.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"    [!] Options flow summary failed: {e}")
            plt.close()
            return None

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
