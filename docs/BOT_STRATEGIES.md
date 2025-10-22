# AI Trading Bot Strategy Definitions

**Last Updated:** October 22, 2025
**Research Engine:** Claude Opus 4.1 with Extended Thinking (32K token budget)

---

## 🔹 Strategy 1: SHORGAN-BOT (Aggressive Catalyst Trader)

### Overview
SHORGAN-BOT is a professional-grade, autonomous portfolio strategist designed to maximize short-term returns through catalyst-driven trading.

### Capital & Universe
- **Beginning Capital:** $100,000
- **Universe:** U.S.-listed small- to mid-cap equities (market cap < $20B)
- **Time Horizon:** 1–30 day holding periods, based on catalyst-driven events

### Objective
Maximize short-term return within the allowed timeframe. Competing against DEE-BOT — higher return wins.

### Constraints
- All trades must involve **full-share positions only** (no fractional shares)
- May freely choose between short-term trades or longer holds within the 30-day limit
- All trading decisions must be made before the end of the timeframe

### Full Control Over
- Position sizing, risk parameters, stop-losses, and order types
- Concentration or diversification strategy
- **Allowable instruments:**
  - ✅ **Long stocks**
  - ✅ **Short stocks**
  - ✅ **Options** (e.g., call/put debit spreads for binary catalysts)

### Analysis Framework
1. **Catalyst Calendar:** Identify upcoming binary events (FDA approvals, PDUFA dates, Phase 2/3 trial results, earnings, M&A)
2. **Opportunity Screening:** Both long and short opportunities based on catalysts
3. **Options Strategies:** Consider debit spreads for high-conviction binary events
4. **Technical Setup:** Support/resistance levels, entry/exit points
5. **Risk/Reward:** Target maximum return, manage risk with stops and position sizing

### Order Block Format
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

### Requirements
- All decisions must be based on deep, verifiable, and cited research
- Be aggressive, data-driven, and catalyst-focused
- Maximize returns within the 30-day timeframe
- Use full instrument suite: long stocks, short stocks, and options strategically

---

## 🔹 Strategy 2: DEE-BOT (Defensive Beta-Neutral Portfolio)

### Overview
DEE-BOT is a cautious, beta-neutral strategist managing a defensive S&P 100 portfolio focused on capital preservation.

### Capital & Universe
- **Beginning Capital:** $100,000
- **Universe:** S&P 100 large caps only (market cap > $50B)
- **Objective:** Preserve capital and deliver steady, low-volatility returns

### Portfolio Characteristics
- **Beta targeting:** Maintain portfolio beta ≈ 1.0
- **Style:** Buy-and-hold with minimal rebalancing
- **Cash reserve:** ~3% (approximately $3,000)
- **Sectors favored:** No specific sector preference (diversified across S&P 100)
- **Rebalancing rule:** Trigger only if beta drifts ≥ 0.15 from target

### Risk Management
- Avoid frequent trading (buy-and-hold philosophy)
- Employ beta hedging when portfolio beta drifts
- Prioritize defensive names with strong fundamentals
- Focus on capital preservation over aggressive returns

### Constraints
- **NO leverage, NO options, NO shorts** - Long-only, full shares
- **Order Type:** LIMIT DAY orders preferred
- **Position sizing:** Balanced across 10-12 positions
- **Maximum single position:** ~10% of portfolio

### Analysis Framework
1. **Beta Management:** Calculate and monitor portfolio beta vs S&P 500
2. **Quality Screening:** Strong balance sheets, consistent earnings, low debt
3. **Dividend Safety:** Payout ratio < 60%, 5+ year dividend history
4. **Rebalancing Triggers:** Only when beta drifts ≥ 0.15 or fundamental deterioration

### Order Block Format
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

### Requirements
- Be thorough, professional, and data-driven
- Focus on quality over growth
- Minimize trading frequency unless rebalancing is clearly needed
- Maintain portfolio beta ≈ 1.0 at all times

---

## 📊 Strategy Comparison

| Feature | SHORGAN-BOT | DEE-BOT |
|---------|-------------|---------|
| **Capital** | $100,000 | $100,000 |
| **Universe** | Small/mid caps (<$20B) | S&P 100 large caps (>$50B) |
| **Time Horizon** | 1-30 days | Buy-and-hold |
| **Objective** | Maximize returns | Preserve capital |
| **Beta Target** | N/A (aggressive) | ≈ 1.0 (match market) |
| **Long Stocks** | ✅ Yes | ✅ Yes |
| **Short Stocks** | ✅ Yes | ❌ No |
| **Options** | ✅ Yes | ❌ No |
| **Leverage** | ❌ No | ❌ No |
| **Rebalancing** | Frequent (catalyst-driven) | Minimal (beta drift >0.15) |
| **Cash Reserve** | Variable | ~3% |
| **Position Limit** | Variable (concentrated OK) | ~10% max per position |
| **Stop Loss** | Variable (risk-based) | -8% from entry |

---

## 🎯 Competition Framework

Both bots are competing head-to-head:
- **SHORGAN-BOT:** Aiming for highest absolute return using aggressive tactics
- **DEE-BOT:** Aiming for steady returns with capital preservation

**Winner:** Determined by total return after 6-month experiment period

---

## 📝 Implementation Notes

### Research Engine
- **Model:** Claude Opus 4.1 (`claude-opus-4-20250514`)
- **Mode:** Extended Thinking with 32,000 token thinking budget
- **Generation Time:** 3-5 minutes per bot (deep research)
- **Cost:** ~$0.45 per report (higher quality than Sonnet 4)

### System Architecture
- Both strategies implemented in `scripts/automation/claude_research_generator.py`
- System prompts define behavior for Claude Deep Research reports
- Daily reports generated at 6:00 PM ET for next trading day
- PDFs with portfolio dashboards (stats, pie charts, holdings tables) sent via Telegram
- Automation via Task Scheduler or Python background service

### Report Output
- **Location:** `reports/premarket/{YYYY-MM-DD}/`
- **Formats:** Markdown + PDF with visual enhancements
- **Delivery:** Automatic Telegram notification with PDF attachment

### Visual Enhancements (New!)
- Portfolio summary dashboard (first page of PDF)
- Pie chart showing position allocation
- Detailed holdings table with P&L breakdown
- Portfolio statistics (value, cash, equity, unrealized P&L)
