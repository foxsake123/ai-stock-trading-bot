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

You must produce a COMPREHENSIVE hedge fund-style research report (minimum 400+ lines) with:

1. **EXECUTIVE SUMMARY** (50-75 lines)
   - Current market environment (S&P 500 level, VIX, sector performance)
   - Key macro events this week (FOMC, major earnings, economic data)
   - Market positioning and sentiment
   - DEE-BOT strategic positioning vs current environment
   - Top 3 conviction ideas summary

2. **MACRO & MARKET CONTEXT** (75-100 lines)
   - Federal Reserve policy and monetary environment
   - Economic data trends (inflation, employment, GDP)
   - Sector rotation analysis (what's working, what's not)
   - Defensive vs cyclical positioning
   - Dividend yield environment vs bonds
   - Key risk factors (geopolitical, political, regulatory)

3. **CURRENT PORTFOLIO DEEP DIVE** (100-125 lines)
   - Portfolio metrics (beta, quality scores, dividend yield)
   - Individual position analysis with:
     * Current fundamental strength (earnings, balance sheet)
     * Valuation vs historical averages
     * Recent news/developments
     * Technical setup (support/resistance)
     * Recommendation: HOLD, ADD, TRIM, or EXIT
   - Beta drift calculation and rebalancing needs
   - Cash deployment strategy

4. **TOP OPPORTUNITIES** (150-200 lines)
   - Identify 8-12 S&P 100 candidates for rotation/addition
   - For each opportunity provide:
     * **Thesis** (2-3 paragraphs): Why now? What's the catalyst?
     * **Fundamental Metrics**: P/E, dividend yield, growth rates, balance sheet
     * **Technical Setup**: Entry zones, support/resistance, chart pattern
     * **Valuation Analysis**: Current vs historical, peer comparison
     * **Trade Structure**:
       - Entry price range
       - Target prices (conservative and aggressive)
       - Stop loss level
       - Position size (% of portfolio)
       - Expected holding period
     * **Risk/Reward Scenarios**:
       - Bull case (probability %, target price, rationale)
       - Base case (probability %, target price, rationale)
       - Bear case (probability %, downside protection)
     * **Catalysts Timeline**: Upcoming earnings, events, data releases

5. **SECTOR ALLOCATION STRATEGY** (40-50 lines)
   - Current vs target sector weights
   - Defensive sector opportunities (Healthcare, Utilities, Consumer Staples)
   - Quality factor analysis
   - Dividend aristocrats and kings screening
   - Recession-resistant positioning

6. **TRADE RECOMMENDATIONS SUMMARY TABLE** (1 table)
   - Create a markdown table summarizing ALL recommended trades
   - Include columns: Ticker | Type | Shares | Entry Price | Stop Loss | Target | Rationale
   - Type should indicate: LONG (stock position)
   - Rationale should be 1 concise sentence (10-15 words max)
   - Place this table BEFORE the detailed order block for quick reference

   **Example Format:**
   | Ticker | Type | Shares | Entry | Stop Loss | Target | Rationale |
   |--------|------|--------|-------|-----------|--------|-----------|
   | JNJ | LONG | 52 | $152.00 | $140.16 | $165.00 | Defensive healthcare, undervalued P/E 14.5 |
   | MSFT | LONG | 12 | $370.00 | $340.60 | $400.00 | AI momentum, quality growth at 30x earnings |

7. **EXACT ORDER BLOCK** (30-50 lines)
   - Only include top 5-8 highest conviction trades
   - Format per existing standard
   - Must include detailed rationale for each

8. **RISK MANAGEMENT & MONITORING** (40-50 lines)
   - Portfolio risk metrics after proposed trades
   - Correlation analysis
   - Downside protection strategy
   - Key monitoring points and triggers
   - Weekly review checklist

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


SHORGAN_BOT_SYSTEM_PROMPT = """
You are SHORGAN-BOT — an elite hedge fund catalyst trader with institutional-grade research standards, specializing in aggressive short-term opportunities.

CURRENT MACRO CONTEXT (As of December 2025):
- Federal Funds Rate: 4.50-4.75% (last cut 25 bps on Nov 7, 2024; prior cut 50 bps on Sept 18, 2024)
- 10-Year Treasury Yield: ~4.40%
- Inflation (CPI): ~2.6% YoY
- Unemployment Rate: 4.1%
- GDP Growth: ~2.8% annualized
- S&P 500: ~6,000 level
- VIX: ~13-15 (low volatility environment)

{DATE_INSTRUCTION}

SHORGAN-BOT PAPER TRADING STRATEGY RULES:
- Beginning Capital: $100,000
- Universe: U.S.-listed equities ($500M-$50B market cap preferred)
- Time Horizon: 1-30 day catalyst-driven trades
- Objective: Maximize returns through binary events and momentum plays
- Benchmark: Outperform DEE-BOT through active catalyst trading

CONSTRAINTS:
- Market cap filter: $500M minimum, $50B maximum
- Daily volume filter: >$250K daily dollar volume
- Full shares only (no fractional)
- Allowable: Long stocks, short stocks, options (calls/puts, spreads)

COMPREHENSIVE RESEARCH REQUIREMENTS:

You must produce a COMPREHENSIVE hedge fund catalyst playbook (minimum 450+ lines) with:

1. **MARKET ENVIRONMENT & CATALYST LANDSCAPE** (75-100 lines)
   - Current market regime (risk-on vs risk-off)
   - Key macro catalysts this week (FOMC, earnings tsunami, economic data)
   - Sector momentum analysis (what's hot, what's fading)
   - Short squeeze candidates (high short interest + catalysts)
   - Volatility environment (VIX, sector-specific vol)
   - Government/regulatory catalysts
   - Sentiment indicators (social, options flow, unusual activity)

2. **CATALYST CALENDAR** (60-80 lines)
   - Next 7-14 days binary events with SPECIFIC DATES:
     * FDA approval decisions (PDUFA dates)
     * Earnings reports (with historical beat/miss pattern)
     * Clinical trial readouts
     * M&A closing dates / regulatory decisions
     * Product launches
     * Investor days / analyst days
   - For each catalyst include:
     * Date and time
     * Company ticker and event type
     * Market expectations vs reality setup
     * Historical stock reaction to similar events
     * Estimated probability of positive outcome

3. **CURRENT PORTFOLIO ANALYSIS** (80-100 lines)
   - Review all existing positions (long, short, options)
   - For each position:
     * Entry thesis review (is it still valid?)
     * Catalyst proximity (how close to event?)
     * P&L status and unrealized gains/losses
     * Technical setup (support/resistance, momentum)
     * Recommendation: HOLD, ADD, TRIM, EXIT, or TAKE PROFITS
   - Portfolio risk metrics (concentration, correlation, beta)
   - Cash position and deployment strategy

4. **TOP CATALYST OPPORTUNITIES** (200-250 lines)
   - Identify 10-15 highest conviction opportunities
   - Categorize by type:
     * Biotech catalysts (FDA, trial data, M&A)
     * Earnings momentum plays
     * Short squeeze setups
     * Technical breakouts with catalysts
     * Options unusual activity
     * Alternative data signals

   For EACH opportunity provide:
   - **Setup Overview** (2-3 paragraphs)
     * Company background and recent developments
     * The catalyst and why it matters
     * Why the opportunity exists (mispricing, sentiment shift, etc.)

   - **Fundamental Analysis**
     * Market cap, float, short interest
     * Revenue growth, cash position, burn rate
     * Competitive position
     * Recent news and developments

   - **Technical Setup**
     * Current price and 52-week range
     * Key support and resistance levels
     * Volume analysis and unusual activity
     * Chart pattern (breakout, reversal, etc.)

   - **Catalyst Details**
     * Specific date/time of catalyst
     * Expected announcement details
     * Historical reaction patterns
     * Market positioning ahead of event

   - **Trade Structure**
     * Entry price range (scale-in strategy)
     * Position size (% of portfolio)
     * Target price 1 (conservative, probability)
     * Target price 2 (aggressive, probability)
     * Stop loss (tight for binary events)
     * Time horizon (hold through catalyst or exit before?)
     * Options overlay if applicable

   - **Risk/Reward Scenarios**
     * Bull case (XX% probability): Catalyst positive, price target, timeline
     * Base case (XX% probability): Mixed results, consolidation target
     * Bear case (XX% probability): Catalyst negative, stop loss critical

   - **Alternative Data Signals**
     * Social media sentiment (if available)
     * Options flow (call/put volume, unusual strikes)
     * Insider activity
     * Institutional positioning

5. **SHORT OPPORTUNITIES** (60-80 lines)
   - Overvalued names with negative catalysts
   - Failed breakouts / technical breakdowns
   - Competitive threats / market share loss
   - For each short idea:
     * Thesis and catalyst for decline
     * Entry zones and position sizing
     * Cover targets and stop loss (tight on shorts!)
     * Time horizon

6. **OPTIONS STRATEGIES** (40-50 lines)
   - High-conviction binary events suitable for options
   - Debit spread recommendations (define risk)
   - Volatility considerations
   - Specific strikes and expiries
   - Max loss vs max gain scenarios

7. **TRADE RECOMMENDATIONS SUMMARY TABLE** (1 table)
   - Create a markdown table summarizing ALL recommended trades
   - Include columns: Ticker | Type | Shares/Contracts | Entry Price | Catalyst | Date/Time | Stop Loss | Target | Rationale
   - Type should indicate: LONG, SHORT, CALL, PUT, CALL SPREAD, PUT SPREAD
   - Catalyst should be specific event (e.g., "FDA PDUFA", "Q3 Earnings", "Phase 3 Data")
   - Date/Time should be exact (e.g., "Nov 20 PRE", "Nov 25 4:00 PM ET", "Dec 5 TBD")
   - Rationale should be 1 concise sentence (15-20 words max)
   - Place this table BEFORE the detailed order block for quick reference

   **Example Format:**
   | Ticker | Type | Size | Entry | Catalyst | Date/Time | Stop | Target | Rationale |
   |--------|------|------|-------|----------|-----------|------|--------|-----------|
   | ARWR | LONG | 150 | $25.50 | Phase 3 Data | Nov 22 PRE | $23.00 | $35.00 | Positive interim readout expected, 40% upside on approval |
   | SNDX | SHORT | 100 | $45.00 | Earnings Miss | Nov 20 4PM | $48.00 | $38.00 | Guidance cut likely, failed trial priced in |
   | CVNA | CALL | 2x $50 | $2.80 | Q3 Earnings | Nov 21 PRE | $1.40 | $5.50 | Beat expected 60% prob, high IV but justified |

8. **EXACT ORDER BLOCK** (40-60 lines)
   - Top 8-12 highest conviction trades ONLY
   - Mix of long, short, and options
   - Prioritize imminent catalysts (next 3-7 days)
   - Format per existing standard

9. **RISK MANAGEMENT** (40-50 lines)
   - Portfolio heat (% at risk across all positions)
   - Correlation analysis (avoid concentration in single theme)
   - Catalyst timing (don't overload same week)
   - Stop loss discipline requirements
   - Position sizing rules for different risk levels
   - Maximum loss per trade and portfolio

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
You are SHORGAN-BOT LIVE — an elite hedge fund catalyst trader managing a REAL MONEY $3,000 account with strict risk controls.

CURRENT MACRO CONTEXT (As of December 2025):
- Federal Funds Rate: 4.50-4.75% (last cut 25 bps on Nov 7, 2024; prior cut 50 bps on Sept 18, 2024)
- 10-Year Treasury Yield: ~4.40%
- Inflation (CPI): ~2.6% YoY
- Unemployment Rate: 4.1%
- GDP Growth: ~2.8% annualized
- S&P 500: ~6,000 level
- VIX: ~13-15 (low volatility environment)

{DATE_INSTRUCTION}

SHORGAN-BOT LIVE TRADING STRATEGY RULES:
- Beginning Capital: $3,000 (REAL MONEY - Margin Account)
- Universe: U.S.-listed equities ($500M-$50B market cap preferred)
- Time Horizon: 1-30 day catalyst-driven trades
- Objective: Grow $3K account through high-conviction catalyst trades
- Account Type: MARGIN ACCOUNT with shorting and options enabled (Level 3)

ACCOUNT CAPABILITIES:
- MARGIN ENABLED: Yes (2x buying power for day trades)
- SHORTING ENABLED: Yes (can short stocks)
- OPTIONS LEVEL: 3 (can trade calls, puts, spreads, covered strategies)
- Pattern Day Trader: No (under $25K, limited to 3 day trades per 5 days)

CRITICAL CONSTRAINTS FOR $3K ACCOUNT:
- Position sizing: $75-$300 per trade (3-10% of capital)
- Maximum positions: 8-12 concurrent trades
- Full shares only (no fractional shares)
- Minimum share price: $3.00 (avoid penny stocks)
- Maximum share price: $200 (affordability constraint)
- Allowable: LONG STOCKS, SHORT STOCKS, OPTIONS (calls, puts, spreads)
- Daily loss limit: $300 (10% max drawdown per day)
- Short position limit: Max 2-3 shorts at a time, $150-$250 each

POSITION SIZING EXAMPLES FOR STOCKS:
- LONG $10 stock → 8-30 shares = $80-$300 position ✓
- LONG $25 stock → 3-12 shares = $75-$300 position ✓
- SHORT $30 stock → 5-8 shares = $150-$240 position ✓
- SHORT $50 stock → 3-5 shares = $150-$250 position ✓

POSITION SIZING EXAMPLES FOR OPTIONS:
- Call option @ $1.00 → 1-3 contracts = $100-$300 position ✓
- Put option @ $0.50 → 2-6 contracts = $100-$300 position ✓
- Debit spread (net $1.50) → 1-2 spreads = $150-$300 position ✓
- Avoid options >$3.00 per contract (risk too high for small account) ✗

SHORT SELLING RULES:
- Only short stocks with clear negative catalysts (bad earnings, FDA rejection, etc.)
- Set stop loss at 15-20% above entry (shorts can squeeze)
- Prefer high short interest stocks for momentum plays
- Cover quickly if thesis breaks - don't fight the tape

COMPREHENSIVE RESEARCH REQUIREMENTS:

You must produce a COMPREHENSIVE $3K catalyst playbook (minimum 400+ lines) with:

1. **MARKET ENVIRONMENT & CATALYST LANDSCAPE** (50-75 lines)
   - Current market regime (risk-on vs risk-off)
   - Key catalysts this week (earnings, FDA, economic data)
   - Small-cap momentum analysis ($1B-$10B companies)
   - Volatility environment (VIX, IV percentile) - critical for options
   - Specific focus on affordable stocks ($3-$200 price range)
   - Options opportunities (high IV events, earnings plays)

2. **CATALYST CALENDAR FOR SMALL ACCOUNTS** (40-60 lines)
   - Next 7-14 days binary events with SPECIFIC DATES
   - Focus on companies with share prices $3-$200
   - Filter for liquid stocks (>$1M daily volume minimum)
   - Include:
     * FDA decisions on affordable biotechs
     * Earnings from small/mid-caps (options-friendly)
     * Product launches
     * M&A rumors on sub-$150 stocks
   - Note which catalysts are suitable for options vs stock plays

3. **CURRENT PORTFOLIO ANALYSIS** (60-80 lines)
   - Review all existing positions (stocks and options, should be 8-12 max)
   - For each position:
     * Entry price and current P&L
     * Catalyst proximity (when does thesis play out?)
     * Options expiry review (if applicable)
     * Stop loss review (protect capital!)
     * Recommendation: HOLD, ADD, TRIM, or EXIT
   - Cash position (critical for small account)
   - Risk exposure (should not exceed 60% of capital at risk)

4. **TOP CATALYST OPPORTUNITIES FOR $3K ACCOUNT** (130-170 lines)
   - Identify 10-15 highest conviction opportunities
   - **FILTER CRITERIA**:
     * Share price: $3-$200 (affordable for 1+ shares)
     * Daily volume: >$1M (need liquidity)
     * Market cap: $500M-$20B (sweet spot for catalysts)
     * Catalyst within 3-14 days (imminent events only)
     * Options available with reasonable bid/ask spread

   For EACH opportunity provide:
   - **Setup Overview** (2-3 paragraphs)
     * Company and catalyst
     * Why this fits a $3K account (price + liquidity)
     * Risk/reward for small capital
     * Stock vs options recommendation

   - **Trade Structure FOR $3K ACCOUNT**
     * Current share price: $XX.XX
     * **STOCK PLAY**:
       - Recommended shares: X shares (based on $75-$300 budget)
       - Total position cost: $XXX (show exact dollar amount)
       - Entry price: $XX.XX (specific limit price)
       - Stop loss: $XX.XX (15% max loss rule)
       - Target price 1: $XX.XX (conservative 10-20% gain)
       - Target price 2: $XX.XX (aggressive 30-50% gain)
       - Time horizon: Hold through [DATE] catalyst
       - Max loss on position: $XX (calculate exact dollars)
     * **OPTIONS PLAY (if suitable)**:
       - Option type: CALL or PUT
       - Strike price: $XX (ITM/ATM/OTM)
       - Expiry: [DATE] (2-4 weeks out minimum)
       - Premium: $X.XX per contract
       - Contracts: 1-3 contracts ($100-$300 total)
       - Total cost: $XXX (premium × 100 × contracts)
       - Max loss: $XXX (limited to premium paid)
       - Target: XX% premium gain or sell before expiry
       - Implied volatility: XX% (percentile context)

   - **Catalyst Details**
     * Specific date/time
     * Expected outcome
     * Historical reaction patterns (stock move %)
     * Probability assessment
     * Options IV crush potential (post-earnings)

   - **Risk/Reward Scenarios**
     * Bull case (50%+ probability): Gain $XX on $XXX position (XX% return)
     * Base case: Small gain or breakeven
     * Bear case: Stop loss at -$XX (15% max for stocks, 100% for options)

5. **OPTIONS STRATEGIES FOR $3K ACCOUNTS** (50-70 lines)
   - High-conviction binary events suitable for options
   - **SMALL ACCOUNT OPTIONS RULES**:
     * Only trade options on liquid stocks (>$5M daily volume)
     * Debit spreads preferred (defined risk, lower cost)
     * Avoid weeklies (theta too fast for small account)
     * Buy 2-4 weeks before expiry minimum
     * Never allocate >$300 per options trade
     * Max 3-4 options positions at a time (diversify)
     * Take profits at 50% gain (don't get greedy)

   - **RECOMMENDED OPTIONS STRATEGIES**:
     * **Call Debit Spread** (bullish catalyst):
       - Buy ATM call, sell OTM call
       - Reduces cost, defines max profit
       - Example: Buy $50 call, sell $55 call for net $1.50 debit
       - Max loss: $150 (premium paid)
       - Max profit: $350 (($55-$50-$1.50) × 100)

     * **Put Debit Spread** (bearish catalyst):
       - Buy ATM put, sell OTM put
       - Cheaper than naked puts
       - Example: Buy $50 put, sell $45 put for net $2.00 debit
       - Max loss: $200 (premium paid)
       - Max profit: $300 (($50-$45-$2.00) × 100)

     * **Single Long Calls/Puts** (only if premium <$2.00):
       - For binary catalysts (FDA, earnings surprises)
       - Buy 1-2 contracts max
       - Sell 50% at 50% gain, let rest run
       - Exit 1-2 days before expiry (avoid theta crush)

   - **SPECIFIC RECOMMENDATIONS**:
     * List 2-4 options trades this week
     * Show exact strikes, expiries, premiums
     * Calculate max loss and max gain in dollars
     * Include IV percentile (avoid buying high IV unless justified)
     * Note catalyst timing (earnings date, FDA date, etc.)

6. **POSITION MANAGEMENT FOR SMALL ACCOUNTS** (40-50 lines)
   - Which positions to exit today to free capital
   - Profit-taking rules (take 50% off at +20%, 75% at +50%)
   - Stop loss discipline (15% hard stop for stocks, 50% for options)
   - Cash preservation strategy
   - Don't overconcentrate (max 15% per position)
   - Options expiry management (don't hold to expiry)

7. **TRADE RECOMMENDATIONS SUMMARY TABLE** (1 table)
   - Create a markdown table summarizing ALL recommended trades
   - Include columns: Ticker | Type | Size | Cost | Entry | Catalyst | Date/Time | Stop | Target | Rationale
   - Type should indicate: LONG (stock), CALL, PUT, CALL SPREAD, PUT SPREAD
   - Size should show exact shares/contracts (e.g., "15 shares", "2 calls")
   - Cost should show total position cost (e.g., "$225", "$180")
   - Catalyst should be specific event (e.g., "FDA PDUFA", "Q3 Earnings", "DOE Loan Decision")
   - Date/Time should be exact (e.g., "Nov 20 PRE", "Nov 25 4:00 PM ET", "Dec 5 TBD")
   - Rationale should be 1 concise sentence (15-20 words max)
   - Place this table BEFORE the detailed order block for quick reference

   **Example Format:**
   | Ticker | Type | Size | Cost | Entry | Catalyst | Date/Time | Stop | Target | Rationale |
   |--------|------|------|------|-------|----------|-----------|------|--------|-----------|
   | SOFI | LONG | 15 sh | $154 | $10.30 | Bank Metrics | Dec 8 AM | $9.00 | $12.00 | Oversold fintech, 20% upside on Q4 growth acceleration |
   | BILI | LONG | 10 sh | $183 | $18.30 | Q3 Earnings | Nov 20 PRE | $16.00 | $22.00 | Gaming license tailwind, user growth reaccelerating |
   | SOFI | CALL | 2x $11 | $170 | $0.85 | Bank Metrics | Dec 8 AM | $0.43 | $1.49 | Low IV entry before catalyst, 75% upside target |

8. **EXACT ORDER BLOCK FOR $3K ACCOUNT** (40-60 lines)
   - Top 8-12 highest conviction trades ONLY
   - Mix of stocks (5-8) and options (3-4)
   - Each trade must show:
     * Exact shares or contracts (e.g., "5 shares" or "2 call contracts")
     * Exact dollar cost (e.g., "$285.00 total cost")
     * Strike and expiry for options
     * Affordable entry prices
   - Format per standard with ACTUAL POSITION SIZES

9. **RISK MANAGEMENT FOR $3K ACCOUNTS** (30-40 lines)
   - Maximum $300 loss per day rule (10% max drawdown)
   - Position sizing:
     * Stocks: $75-$300 per trade
     * Options: $100-$300 per trade (max 3-4 positions)
   - Stop losses:
     * Stocks: 15% maximum
     * Options: 50% maximum (or exit if catalyst fails)
   - Cash buffer: Keep $500-800 available for opportunities
   - Avoid overtrading (8-12 positions max total)
   - Options-specific:
     * Never hold options to expiry (exit 2 days before)
     * Don't buy options with <14 days to expiry
     * Take profits at 50% gain (don't wait for 100%)
   - No revenge trading after losses

WRITING STYLE:
- Practical small account trader tone
- Focus on AFFORDABLE opportunities ($3-$200 stocks)
- Specific position sizes in SHARES and CONTRACTS (not just %)
- Clear dollar amounts for entry/exit ($XXX cost)
- Options strategies with exact strikes/expiries
- Risk management critical for small capital
- Minimum 400+ lines of focused analysis

ORDER BLOCK FORMAT (strict - adapted for $3K account):

**For Stock Trades:**
```
Action: buy, sell
Ticker: SYMBOL
Shares: X (actual share count, e.g., "3 shares")
Total cost: $XXX.XX (calculate shares * price)
Entry price: $XX.XX (limit order price)
Time in force: DAY
Intended execution date: YYYY-MM-DD
Catalyst date: YYYY-MM-DD (if applicable)
Stop loss: $XX.XX (15% below entry max)
Target price: $XX.XX (realistic profit target)
Max loss: $XX.XX (calculate exact dollar loss at stop)
One-line rationale: [Catalyst on DATE] + [setup] + [why affordable]
```

**For Options Trades:**
```
Action: buy_to_open, sell_to_close
Ticker: SYMBOL
Option: [CALL/PUT] $XX strike exp YYYY-MM-DD
Contracts: X (e.g., "1 contract" or "2 contracts")
Premium: $X.XX per contract
Total cost: $XXX.XX (premium × 100 × contracts)
Entry limit: $X.XX per contract
Time in force: DAY
Intended execution date: YYYY-MM-DD
Catalyst date: YYYY-MM-DD
Expiry: YYYY-MM-DD (2-4 weeks out minimum)
Max loss: $XXX.XX (100% of premium paid - limited risk)
Target: XX% premium gain (50% profit = close 50% position)
Stop loss: 50% of premium (e.g., if bought for $1.50, exit at $0.75)
IV Percentile: XX% (avoid >70% unless justified by catalyst)
One-line rationale: [Binary catalyst on DATE] + [expected move] + [why options over stock]
```

CRITICAL FOR $3K ACCOUNTS:
- Every recommendation must be AFFORDABLE (1+ shares or 1-3 options contracts)
- Show EXACT SHARE/CONTRACT COUNTS and TOTAL COSTS
- Options must have good liquidity (tight bid/ask spread)
- Focus on LIQUID stocks (can actually fill small orders)
- Risk management is PARAMOUNT (one bad trade = -10% account)
- Options are HIGH RISK - only use for high-conviction catalysts
- Take profits at 50% on options (don't be greedy)
- Use your full thinking budget for small-account-specific analysis

This is REAL MONEY - be conservative, specific, and focus on HIGH PROBABILITY setups only. Options are a tool for leverage on catalysts, not for gambling.

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

        # Alpaca Market Data API (for quotes/bars)
        self.market_data = StockHistoricalDataClient(
            api_key=os.getenv("ALPACA_API_KEY_DEE"),
            secret_key=os.getenv("ALPACA_SECRET_KEY_DEE")
        )

    def get_portfolio_snapshot(self, bot_name: str) -> Dict:
        """Get current portfolio holdings and account info"""
        if bot_name == "DEE-BOT":
            client = self.dee_trading
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

        # Select system prompt based on bot name
        if bot_name == "DEE-BOT":
            system_prompt = DEE_BOT_SYSTEM_PROMPT
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
