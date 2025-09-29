# DEE-BOT Trading Strategy
## TradingAgents Framework Implementation
### Capital: $100,000 (Paper Trading)

---

## 📋 STRATEGY OVERVIEW

### What DEE-BOT Is
**TradingAgents Framework**: A mini trading firm in software running multiple LLM specialists (Fundamental, News, Sentiment, Technical) whose reports feed a bull vs. bear research debate. A Trader proposes plans that Risk teams (aggressive/neutral/conservative) rewrite under constraints, with a Fund Manager as the final execution gate.

### Core Principles
- **LONG-ONLY**: No shorting allowed in DEE-BOT
- **Risk-First**: Multiple risk lenses before money moves
- **Structured State**: Compact reports prevent context loss
- **Explicit Guardrails**: Position size, stops, exposure caps per decision
- **Explainability**: All trades ship with rationale + data lineage

---

## 💰 CAPITAL & RISK PARAMETERS

### Account Setup
```
Starting Capital: $100,000 (not $1M)
Strategy: LONG-ONLY defensive positions
Max Daily Loss: 0.75% of NAV ($750)
Max 20-Day Drawdown: 5% ($5,000)
Per-Trade Risk: 0.25% of NAV ($250)
Gross Exposure Cap: 100% (fully invested max)
Net Exposure: +80% to +100% (long-only)
```

### Position Sizing
- **ATR-Based Stops**: 1.25× ATR(20) for stop distance
- **Position Size**: $250 risk / (1.25 × ATR) = shares
- **Max Position**: 10% of NAV ($10,000)
- **Concurrent Positions**: 8-12 names
- **Sector Limits**: 30% max per sector

### Universe
- **Primary**: Top 50 U.S. large/mega-caps
- **Focus**: Dividend aristocrats, defensive sectors
- **ETFs**: SPY, DIA for market exposure
- **Excluded**: Small caps, biotech, high volatility

---

## 📅 DAILY RUNBOOK (Eastern Time)

### 06:45-08:45: Ingest & Draft
```python
# Each specialist agent generates focused reports
- Fundamental Agent: Earnings, ratios, guidance changes
- Technical Agent: Chart patterns, support/resistance
- News Agent: Headlines, corporate actions
- Sentiment Agent: Social trends, analyst changes

# Bull vs Bear Debate (2-3 rounds)
Output: Thesis + Catalysts + Break conditions
```

### 08:45-09:15: Risk Gate & Sizing
```python
# Risk team converts thesis to executable orders
- Conservative Risk: Caps position at 5% NAV
- Neutral Risk: Standard 8% position
- Aggressive Risk: Up to 10% for high conviction

# Fund Manager approval required for execution
```

### 09:30-11:00: Market Entry
```python
# Disciplined entry rules
- Use limit orders with NBBO + 0.02
- TWAP over 30 minutes for large positions
- If VIX > 80th percentile: reduce size 30%
- Auto-reject if news severity > threshold
```

### 11:00-15:30: Monitor & Adapt
```python
# Continuous monitoring
- Price vs ATR stop level
- News shock detection
- Correlation spike alerts
- Portfolio beta tracking

# Mid-day re-underwrite for outliers only
```

### 15:30-16:00: End of Day
```python
# Position review
- Hold overnight only with explicit approval
- Flatten positions without clear catalyst
- Update stop losses for winners
```

### 16:00-17:00: Post-Mortem
```python
# Learning loop
- Store: Rationale, fills, outcomes
- Review: What worked, what failed
- Update: Risk parameters for next day
```

---

## 🎯 POSITIONING EXAMPLES

### Example 1: Apple (AAPL)
```
Current Price: $230
ATR(20): $4.00
Stop Distance: 1.25 × $4 = $5.00
Risk Budget: $250
Position Size: $250 / $5 = 50 shares
Notional Value: 50 × $230 = $11,500 (11.5% of NAV)
Action: Reduce to 43 shares ($9,890) to stay under 10%
```

### Example 2: Johnson & Johnson (JNJ)
```
Current Price: $165
ATR(20): $2.50
Stop Distance: 1.25 × $2.50 = $3.125
Risk Budget: $250
Position Size: $250 / $3.125 = 80 shares
Notional Value: 80 × $165 = $13,200
Action: Reduce to 60 shares ($9,900) for 10% limit
```

---

## 🛡️ RISK CONTROLS

### Four-Layer Defense
1. **Per-Trade Stop**: ATR-based, never moved down
2. **Trailing Stop**: Activated at +1.5× risk ($375 profit)
3. **Portfolio VaR**: 95% 1-day VaR ≤ 0.6% NAV
4. **Circuit Breaker**: Halt on severe news events

### Dynamic Adjustments
```python
# Volatility throttle
if realized_vol > 1.5 × median_10d:
    position_size *= 0.5

# Correlation control
if mean_correlation > 0.6:
    close_weakest_thesis()

# Beta management
if portfolio_beta > 1.2:
    reduce_high_beta_positions()
```

### Fee Management
- **Target**: < 12 bps round trip
- **Slippage Budget**: 5 bps per side
- **Review Trigger**: 2 days over budget

---

## 📊 PERFORMANCE TARGETS

### Risk Metrics
```
Max Daily Loss: 0.75% ($750)
Max Drawdown: 5% ($5,000)
Target Sharpe: > 1.2
Win Rate: > 60%
Avg Win/Loss: > 1.5
```

### Return Targets
```
Monthly: 1-2% (defensive focus)
Quarterly: 3-6%
Annual: 12-18%
```

---

## 🔄 IMPLEMENTATION WORKFLOW

### Multi-Agent Process
```mermaid
Specialists → Reports → Bull/Bear Debate →
Trader Plan → Risk Review → Fund Manager →
Execution → Monitoring → Learning
```

### Decision Audit Trail
- Every trade stores analyst snapshots
- Debate transcripts hashed
- Risk edits documented
- Execution deltas tracked

### Model Tiering
- **Quick Models**: Data fetch, formatting
- **Deep Models**: Debate, risk analysis
- **Latency Budget**: < 500ms per decision

---

## 🚦 ROLLOUT PLAN

### Week 1-2: Paper Trading
- Full automation with real quotes
- Daily scorecard on metrics
- Latency and cost optimization

### Week 3-4: Scaled Live
- Start with $10K (10% of capital)
- If Sharpe > 1.0 for 10 sessions: full $100K
- Monitor all risk metrics closely

### After 60 Days
- Review performance vs targets
- Adjust parameters based on data
- Consider position size increases if DD < 3%

---

## 🔧 TECHNICAL IMPLEMENTATION

### Required Components
```python
# Data feeds
- Real-time quotes (Alpaca)
- News API (Financial Datasets)
- Fundamentals (Financial Datasets)

# Execution
- Alpaca paper trading API
- Limit orders only
- TWAP for large positions

# Monitoring
- Position tracking (CSV)
- Risk dashboard
- Telegram alerts
```

### Integration Points
```python
# Morning workflow
1. generate_dee_bot_trades()  # AI analysis
2. risk_review()              # Multi-agent debate
3. execute_daily_trades()     # Automated execution
4. update_positions()         # Real-time tracking

# Continuous
- monitor_stops()
- check_news_alerts()
- calculate_var()
```

---

## ⚠️ CRITICAL RULES

### NEVER
- ❌ Short positions (LONG-ONLY)
- ❌ Use margin beyond settlement
- ❌ Move stops down
- ❌ Average down on losers
- ❌ Trade on rumors

### ALWAYS
- ✅ Follow position size limits
- ✅ Use stop losses
- ✅ Document rationale
- ✅ Review daily performance
- ✅ Maintain audit trail

---

## 📈 WHY THIS CONTROLS DOWNSIDE

1. **Debate-Then-Rewrite**: Pre-mortem on every trade
2. **Structured State**: Prevents compounding errors
3. **Risk-First Workflow**: Risk is primary, not secondary
4. **Multiple Veto Points**: Any risk agent can kill trade
5. **Learning Loop**: Continuous improvement from outcomes

---

## 🎯 KEY DIFFERENTIATORS

### vs Traditional Algo Trading
- Human-readable reasoning
- Adaptable to new information
- Context-aware decisions
- Natural language inputs

### vs Manual Trading
- Consistent process
- No emotional bias
- 24/7 monitoring capability
- Complete audit trail

### vs Single-Model AI
- Multi-perspective analysis
- Built-in dissent mechanism
- Structured state management
- Risk-aware by design

---

*Strategy Document Version: 1.0*
*Last Updated: September 29, 2025*
*Status: ACTIVE - LONG ONLY*

**Remember: DEE-BOT is STRICTLY LONG-ONLY. No shorting allowed.**