# Claude Deep Research Setup Guide

## Overview

This guide explains how to use Claude AI for generating comprehensive weekly trading research reports. Claude offers superior analysis compared to ChatGPT for deep research tasks.

---

## Why Claude for Research?

### Advantages Over ChatGPT

| Feature | Claude Sonnet 4 | ChatGPT GPT-4 |
|---------|----------------|---------------|
| **Context Window** | 200K tokens (~150K words) | 8K-32K tokens |
| **Cost per Report** | ~$0.30 | ~$0.90 |
| **Multi-stock Analysis** | ✅ 20+ stocks simultaneously | ❌ Fragmented approach |
| **Financial Reasoning** | ✅ Superior | ✅ Good |
| **Report Structure** | ✅ Highly consistent | ⚠️ Variable |
| **Risk Assessment** | ✅ More nuanced | ✅ Good |

### Key Benefits

1. **Deeper Context**: Analyze all holdings + candidates in single prompt
2. **Better Quality Screening**: More sophisticated quality metrics (DEE-BOT)
3. **Superior Catalyst Analysis**: Better at identifying R/R setups (SHORGAN-BOT)
4. **Consistent Format**: Reliable structured output every time
5. **Lower Cost**: ~66% cheaper than ChatGPT for comprehensive reports

---

## Setup Instructions

### Step 1: Add Credits to Anthropic Account

1. **Visit**: https://console.anthropic.com/settings/billing
2. **Add Credits**: Minimum $5 recommended
   - $5 = ~16 comprehensive reports
   - Cost per report: ~$0.30 ($0.15 input + $0.15 output)
3. **Your API Key**: Already in `.env` file
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-oOrO0cE_kFyfqHzsd...
   ```

### Step 2: Test the System

```bash
# Test DEE-BOT report generation
python scripts-and-data/automation/claude_research_generator.py --bot dee

# Test SHORGAN-BOT report generation
python scripts-and-data/automation/claude_research_generator.py --bot shorgan

# Generate both reports
python scripts-and-data/automation/claude_research_generator.py --bot both
```

### Step 3: Review Generated Reports

Reports are saved to:
```
scripts-and-data/data/reports/weekly/claude-research/
├── claude_research_dee_bot_2025-09-30.md
└── claude_research_shorgan_bot_2025-09-30.md
```

---

## Bot-Specific Strategies

### DEE-BOT (Defensive Large-Cap)

**Strategy Focus**:
- S&P 100 large caps only (market cap > $50B)
- Beta ≈ 1.0 (match market with quality)
- Quality metrics: ROE > 15%, Debt/Equity < 1.0, Dividend > 2%
- Position size: 8% per position, 10-12 total
- Stop loss: -8% from entry

**Claude Analysis Includes**:
- Quality rankings of S&P 100 candidates
- Beta management and portfolio rebalancing
- Dividend safety analysis
- Risk exposure by sector
- Exact limit prices for rotations

### SHORGAN-BOT (Catalyst-Driven Micro-Caps)

**Strategy Focus**:
- U.S. micro/mid caps (market cap < $300M)
- Catalyst-driven: FDA approvals, earnings, insider buying
- Target: 2-5x momentum plays
- Position size: 10% per position, 8-10 total
- Stop loss: -15% or catalyst failure

**Claude Analysis Includes**:
- Catalyst calendar (7-14 days forward)
- Momentum screening (RSI, volume, breakouts)
- Insider activity and institutional flows
- Technical setups (entry/exit levels)
- Risk/reward ratios for each opportunity

---

## Automation Setup

### Option 1: Windows Task Scheduler (Recommended)

1. **Open Task Scheduler**: Win + R → `taskschd.msc`

2. **Create New Task**:
   - Name: "Claude Tuesday Research"
   - Description: "Generate weekly Claude research reports"
   - Trigger: Weekly on Tuesday at 6:00 PM ET
   - Action: Run batch file
     ```
     C:\Users\shorg\ai-stock-trading-bot\setup_tuesday_claude_research.bat
     ```

3. **Test Manual Run**:
   ```cmd
   setup_tuesday_claude_research.bat
   ```

### Option 2: Manual Weekly Execution

Run every Tuesday evening:
```bash
# Generate both reports
python scripts-and-data/automation/claude_research_generator.py --bot both --week 5

# Or run the batch file
setup_tuesday_claude_research.bat
```

---

## Report Structure

### DEE-BOT Report Sections

1. **Current Portfolio Assessment**
   - Beta calculation
   - Quality scores for each holding
   - Sector exposure
   - Risk metrics

2. **Rebalancing Recommendations**
   - Positions to trim/exit
   - Positions to add/increase
   - Rationale for each change

3. **Quality Rankings**
   - Top 10 S&P 100 candidates
   - Quality scores (ROE, debt, dividends)
   - Current valuations

4. **Exact Order Block**
   ```
   Action: buy
   Ticker: JNJ
   Shares: 45
   Order type: limit
   Limit price: $162.50
   Time in force: DAY
   Intended execution date: 2025-10-01
   Stop loss: $149.50 (-8%)
   One-line rationale: Quality defensive play, 2.8% yield, ROE 18%
   ```

5. **Risk & Liquidity Checks**
6. **Monitoring Plan**

### SHORGAN-BOT Report Sections

1. **Catalyst Calendar**
   - Next 7-14 days of binary events
   - FDA PDUFA dates
   - Earnings releases
   - Trial results

2. **Current Portfolio Review**
   - Thesis updates for each holding
   - Catalyst proximity
   - Technical status
   - Exit triggers

3. **New Catalyst Opportunities**
   - Ranked by R/R ratio
   - Catalyst description
   - Technical setup
   - Entry/exit levels

4. **Exact Order Block**
   ```
   Action: buy
   Ticker: FBIO
   Shares: 850
   Order type: limit
   Limit price: $11.75 (below ask)
   Time in force: DAY
   Intended execution date: 2025-10-01
   Catalyst date: 2025-10-15 (PDUFA)
   Stop loss: $9.99 (-15%)
   Target price: $28.00 (2.4x upside)
   One-line rationale: Phase 3 success, PDUFA Oct 15, high insider ownership
   ```

5. **Risk & Liquidity Checks**
   - Average daily volume > $500K
   - Bid/ask spread < 2%

6. **Monitoring Plan**
   - Catalyst date reminders
   - Technical trigger levels

---

## Cost Analysis

### Claude Sonnet 4 Pricing

- **Input**: $3.00 per 1M tokens
- **Output**: $15.00 per 1M tokens

### Typical Report Costs

**DEE-BOT Report**:
- Input: ~30K tokens (portfolio + S&P 100 data) = $0.09
- Output: ~8K tokens (report) = $0.12
- **Total**: ~$0.21 per report

**SHORGAN-BOT Report**:
- Input: ~40K tokens (portfolio + catalysts + technicals) = $0.12
- Output: ~10K tokens (report) = $0.15
- **Total**: ~$0.27 per report

**Weekly Cost** (both bots): ~$0.48 per week = **$2/month**

### Comparison

| Service | Monthly Cost | Quality | Context |
|---------|-------------|---------|---------|
| **Claude** | **$2** | **Superior** | **200K tokens** |
| ChatGPT Plus | $20 | Good | 32K tokens |
| ChatGPT API | ~$12 | Good | 32K tokens |

**Verdict**: Claude is 6-10x cheaper with better analysis quality.

---

## Usage Tips

### 1. Run After Market Close
Schedule for 6:00 PM ET Tuesday to include:
- Full day's price action
- After-hours news
- Earnings releases

### 2. Combine with Financial Datasets API
Claude works best with comprehensive data:
```bash
# Pre-fetch data before Claude run
python scripts-and-data/automation/financial_datasets_integration.py
```

### 3. Review Before Execution
- Read full report (don't auto-execute)
- Validate limit prices against current market
- Verify catalyst dates
- Check position sizing

### 4. Week Number Tracking
```bash
# Specify week number for context
python claude_research_generator.py --bot both --week 6
```

### 5. Skip Market Data If Needed
```bash
# Faster generation without live data
python claude_research_generator.py --bot both --no-market-data
```

---

## Troubleshooting

### Error: "Credit balance too low"
**Solution**: Add credits at https://console.anthropic.com/settings/billing

### Error: "Connection timeout"
**Solution**: Check internet connection, Alpaca API status

### Error: "No positions found"
**Solution**: Normal if portfolio is all cash, report will focus on opportunities

### Error: "Invalid API key"
**Solution**: Verify `.env` file has correct `ANTHROPIC_API_KEY`

---

## Migration from ChatGPT

### What to Keep
- Daily quick summaries (ChatGPT is fine for this)
- Conversational interface
- Ad-hoc questions

### What to Replace
- ✅ Weekly deep research reports → **Claude**
- ✅ Multi-stock comparative analysis → **Claude**
- ✅ Comprehensive risk assessment → **Claude**
- ✅ Detailed order planning → **Claude**

### Hybrid Approach
```
Monday-Friday: ChatGPT for quick daily updates
Tuesday Evening: Claude for comprehensive weekly research
Weekend: Manual review and planning
```

---

## Next Steps

1. **[IMMEDIATE]** Add $5 credits to Anthropic account
2. **[TODAY]** Test generate one report manually
3. **[THIS WEEK]** Set up Tuesday automation
4. **[ONGOING]** Compare Claude vs ChatGPT quality

---

## Support

**Documentation**:
- Claude API Docs: https://docs.anthropic.com/
- Alpaca API Docs: https://alpaca.markets/docs/
- Script Location: `scripts-and-data/automation/claude_research_generator.py`

**Quick Commands**:
```bash
# Test balances
python utils/trading/check_balances.py

# Generate reports
python scripts-and-data/automation/claude_research_generator.py --bot both

# Check scheduled tasks
schtasks /query /tn "Claude Tuesday Research"
```

---

**Last Updated**: September 30, 2025
**Next Review**: After first production run
**Status**: Ready for production (pending Anthropic credits)
