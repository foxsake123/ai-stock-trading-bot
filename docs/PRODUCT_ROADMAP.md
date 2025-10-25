# AI Trading Bot - Product Roadmap
## October 2025 - March 2026

**Current Status**: Production Ready (Oct 24, 2025)
**Next Milestone**: First Automated Trading Day (Oct 28, 2025)
**Vision**: Fully automated, multi-strategy trading system with 60%+ win rate

---

## Current System (v1.0 - Oct 24, 2025)

### What's Working
- ✅ Dual-bot strategy (DEE-BOT defensive, SHORGAN-BOT catalyst)
- ✅ Claude Opus 4.1 Deep Research (automated nightly)
- ✅ Financial Datasets API (real-time market data)
- ✅ 7-agent multi-agent validation system
- ✅ FD-verified approval path (80/20 weighting)
- ✅ Bot-specific filters (S&P 100, market cap, volume)
- ✅ Complete automation (Task Scheduler - 4 daily tasks)
- ✅ 90% approval rate in testing (9/10 trades)

### Known Limitations
- ⚠️ No options trading support (rejected due to lack of options data)
- ⚠️ ChatGPT research manual (requires user action at 7 PM)
- ⚠️ No Telegram notifications (manual file checking required)
- ⚠️ Generic catalyst descriptions ("Event catalyst" vs specific events)
- ⚠️ Agent weights static (not optimized based on performance)

---

## Phase 1: Stabilization & Monitoring
**Timeline**: Week 1-2 (Oct 28 - Nov 8, 2025)
**Goal**: Ensure reliable automated operation
**Priority**: CRITICAL

### Week 1: Initial Deployment (Oct 28 - Nov 1)

**Daily Monitoring Schedule**:
- 6:15 PM: Check evening research generated
- 8:35 AM: Review approved trades before execution
- 9:35 AM: Verify fills and execution logs
- 4:35 PM: Check daily P&L and performance

**Metrics to Track**:
- Approval rate (target: ≥60%, current: 90%)
- Execution success rate (target: ≥90%)
- Win rate (target: ≥55%)
- Sharpe ratio (target: ≥1.0)
- Max drawdown (target: <15%)

**Expected Issues**:
- Edge cases in parser (handle gracefully)
- API rate limits (add retries and backoff)
- Unexpected market conditions (adjust thresholds)
- Task Scheduler reliability (monitor task history)

**Success Criteria**:
- [ ] 5 consecutive trading days without critical failures
- [ ] Approval rate ≥ 60% average
- [ ] No missed research or execution runs
- [ ] All 4 Task Scheduler tasks running reliably

### Week 2: Performance Analysis (Nov 4 - Nov 8)

**Analysis Tasks**:
1. Calculate actual approval rate vs expected (90%)
2. Measure agent voting accuracy (which agents were right/wrong)
3. Analyze rejected trades (were they good or bad decisions?)
4. Review combined confidence vs actual performance
5. Identify any pattern in failures or errors

**Optimization Targets**:
- If approval rate < 50%: Lower threshold or adjust weighting
- If too many approvals (>95%): Raise threshold to be more selective
- If certain agents consistently wrong: Lower their voting weight
- If FD API failures: Add Yahoo Finance fallback logic

**Deliverables**:
- Week 1 performance report (5-day summary)
- Agent accuracy analysis (which agents to trust more)
- Confidence calibration analysis (is 0.55 the right threshold?)
- Bug fixes for any issues discovered

**Success Criteria**:
- [ ] First week report completed
- [ ] Agent weights adjusted based on performance
- [ ] Any critical bugs fixed
- [ ] Confidence threshold optimized (if needed)

---

## Phase 2: Core Enhancements
**Timeline**: Week 3-4 (Nov 11 - Nov 22, 2025)
**Goal**: Add missing features and improve usability
**Priority**: HIGH

### Enhancement 1: Telegram Notifications
**Effort**: 1 hour
**Priority**: HIGH (immediate visibility)

**Features**:
- Trade generation alert (8:30 AM daily)
  - "DEE-BOT: 4 approved, 0 rejected"
  - "SHORGAN-BOT: 5 approved, 1 rejected"
  - Link to trades file
- Execution confirmation (9:35 AM daily)
  - "Executed 9 trades: 7 filled, 2 pending"
  - Fill prices and quantities
- Daily P&L summary (4:30 PM daily)
  - "DEE-BOT: +0.5% ($500)"
  - "SHORGAN-BOT: +1.2% ($1,200)"
  - "Combined: +0.85% ($1,700)"

**Implementation**:
- Use existing Telegram Bot API integration
- Add notification calls in each automation script
- Format messages with markdown for readability
- Include direct links to files/dashboards

**Success Criteria**:
- [ ] Notifications delivered within 1 minute of event
- [ ] All 3 notification types working (generation, execution, P&L)
- [ ] Messages formatted clearly and readable on mobile

### Enhancement 2: Catalyst Extraction
**Effort**: 2 hours
**Priority**: MEDIUM (improves transparency)

**Problem**: Research shows specific catalysts (e.g., "Oct 29 earnings", "Phase 2b data Nov 15"), but trades file shows generic "Event catalyst"

**Solution**:
- Enhance parser to extract catalyst text from research
- Parse date references (e.g., "Oct 29", "Nov 15")
- Format catalyst in trades file:
  - Before: "Event catalyst"
  - After: "Earnings (Oct 29)" or "FDA PDUFA (Nov 15)"

**Implementation**:
- Add regex patterns to extract catalyst sentences
- Parse date references with dateutil
- Update StockRecommendation dataclass to store detailed catalyst
- Display in TODAYS_TRADES markdown

**Success Criteria**:
- [ ] Specific catalysts displayed (not generic)
- [ ] Dates extracted correctly from research
- [ ] Catalyst type identified (earnings, FDA, product, M&A)

### Enhancement 3: ChatGPT Research Automation
**Effort**: 4 hours
**Priority**: MEDIUM (removes manual step)

**Current**: User manually generates ChatGPT Deep Research at 7 PM

**Solution**: Automate ChatGPT research using Playwright

**Implementation**:
1. Install Playwright: `pip install playwright`
2. Create `scripts/automation/automated_chatgpt_research.py`
3. Use Playwright to:
   - Open ChatGPT in headless browser
   - Submit same prompts as Claude research
   - Wait for responses
   - Parse and save markdown
4. Schedule for 7:00 PM daily (after Claude completes)

**Challenges**:
- ChatGPT login/authentication (may need session cookies)
- Rate limits (Deep Research may have usage limits)
- Response parsing (different format than Claude)
- Reliability (ChatGPT UI changes may break automation)

**Success Criteria**:
- [ ] ChatGPT research generated automatically
- [ ] Saved to `reports/premarket/YYYY-MM-DD/chatgpt_research.md`
- [ ] Quality comparable to manual generation
- [ ] No manual intervention required

### Enhancement 4: Performance Dashboard
**Effort**: 6 hours
**Priority**: MEDIUM (visibility and analytics)

**Features**:
- Web-based dashboard (Flask + Chart.js)
- Daily trades view:
  - Approved vs rejected count
  - Confidence distribution
  - Top recommendations
- Approval rate chart (last 30 days)
- Agent voting breakdown:
  - Which agents voted BUY/HOLD/SELL per trade
  - Agent accuracy over time
- Historical performance:
  - Cumulative P&L chart
  - Win rate by strategy (DEE vs SHORGAN)
  - Best/worst trades

**Implementation**:
- Create `web/dashboard.py` (Flask app)
- Store trade results in SQLite database
- Create charts with Chart.js
- Add real-time updates (auto-refresh)

**Success Criteria**:
- [ ] Dashboard accessible at http://localhost:5000/dashboard
- [ ] Shows last 30 days of trades
- [ ] Agent voting breakdown visible
- [ ] Charts update daily automatically

---

## Phase 3: Advanced Features
**Timeline**: Month 2 (Nov 25 - Dec 20, 2025)
**Goal**: Optimize performance and add sophisticated features
**Priority**: MEDIUM

### Feature 1: Options Trading Support
**Effort**: 8 hours
**Priority**: MEDIUM (unlock new strategies)

**Current**: Options trades (like VKTX call spread) rejected due to lack of options data

**Solution**: Integrate options data provider

**Options for Data Provider**:
1. **Tradier API** (recommended)
   - Free for 60 days, then $10/month
   - Complete options chain data
   - Greeks, IV, bid/ask spreads
2. **CBOE DataShop**
   - More comprehensive but expensive ($50+/month)
3. **Alpaca Options API**
   - Free if already using Alpaca
   - Limited data (no Greeks)

**Implementation**:
1. Create `scripts/data/tradier_api.py`
2. Fetch options chains for recommended tickers
3. Validate spread parameters:
   - Check if strikes exist
   - Verify liquidity (open interest, volume)
   - Calculate max risk/reward
4. Add options-specific validation in multi-agent system
5. Support spread types: verticals, calendars, diagonals

**Success Criteria**:
- [ ] Options data fetched from provider
- [ ] Call/put spreads validated correctly
- [ ] Max risk calculated accurately
- [ ] Options trades approved (if criteria met)

### Feature 2: Agent Performance Tracking
**Effort**: 10 hours
**Priority**: HIGH (optimize decision-making)

**Current**: All agents have equal voting weight, static

**Goal**: Weight agents dynamically based on historical accuracy

**Implementation**:
1. Create `performance/agent_tracker.py`
2. Log every agent recommendation with trade outcome:
   ```json
   {
     "date": "2025-10-28",
     "ticker": "PG",
     "agent": "FundamentalAnalyst",
     "vote": "BUY",
     "confidence": 0.75,
     "outcome": {
       "executed": true,
       "return": 0.05,
       "days_held": 7,
       "win": true
     }
   }
   ```
3. Calculate agent accuracy metrics:
   - Win rate (% of BUY votes that were profitable)
   - Average return when agent said BUY
   - False positive rate (BUY votes that lost)
   - False negative rate (HOLD votes that would have won)
4. Adjust voting weights monthly:
   - High accuracy agent: +10% weight
   - Low accuracy agent: -10% weight
   - Cap adjustments at ±30%

**Example Adjustment**:
```
FundamentalAnalyst: 75% win rate → 1.2x weight (boosted)
TechnicalAnalyst: 45% win rate → 0.8x weight (reduced)
BullResearcher: 55% win rate → 1.0x weight (unchanged)
```

**Success Criteria**:
- [ ] Agent votes logged with outcomes
- [ ] Accuracy calculated monthly
- [ ] Weights adjusted automatically
- [ ] System becomes more accurate over time

### Feature 3: Confidence Threshold Optimization
**Effort**: 6 hours
**Priority**: MEDIUM (maximize performance)

**Current**: 0.55 confidence threshold chosen arbitrarily

**Goal**: Find optimal threshold through backtesting

**Implementation**:
1. Collect 30 days of trade data (recommendations + outcomes)
2. Backtest different thresholds (0.45, 0.50, 0.55, 0.60, 0.65, 0.70)
3. For each threshold, calculate:
   - Number of trades approved
   - Win rate
   - Average return
   - Sharpe ratio
   - Max drawdown
4. Find threshold that maximizes risk-adjusted returns
5. A/B test new threshold vs current (50/50 split for 1 week)
6. Adopt better-performing threshold

**Expected Results**:
- Lower threshold (0.50): More trades, lower win rate
- Higher threshold (0.65): Fewer trades, higher win rate
- Optimal likely around 0.55-0.60

**Success Criteria**:
- [ ] Optimal threshold identified through backtesting
- [ ] A/B test completed (1 week)
- [ ] System using optimized threshold
- [ ] Performance improved (higher Sharpe ratio)

### Feature 4: Alternative Data Enhancement
**Effort**: 8 hours
**Priority**: LOW (incremental improvement)

**Current**: Basic alternative data (insider trades, options flow, social sentiment)

**Enhancements**:
1. **Dark Pool Data**
   - Detect large institutional buying/selling
   - Track unusual dark pool activity
   - Signal: Large dark pool buy = bullish
2. **Institutional Holdings**
   - Monitor 13F filings (quarterly)
   - Track hedge fund positions
   - Signal: Smart money accumulation = bullish
3. **News Sentiment (Real-Time)**
   - Monitor news feeds (Bloomberg, Reuters)
   - Sentiment analysis on headlines
   - Signal: Positive news spike = bullish
4. **Supply Chain Data**
   - Track shipping volumes (e.g., Apple iPhone production)
   - Credit card transaction data
   - Signal: Strong transaction data = bullish for retail

**Data Sources**:
- Dark pools: Quandl ($50/month)
- 13F filings: SEC Edgar (free)
- News sentiment: Alpha Vantage (free tier)
- Alternative data: Quiver Quantitative ($50/month)

**Success Criteria**:
- [ ] 2+ new data sources integrated
- [ ] Alternative data scores calculated
- [ ] Incorporated into multi-agent validation
- [ ] Incremental improvement in approval accuracy

---

## Phase 4: Scale & Optimize
**Timeline**: Month 3 (Dec 21 - Jan 20, 2026)
**Goal**: Reduce costs, increase efficiency, scale system
**Priority**: LOW

### Optimization 1: Multi-LLM Strategy
**Effort**: 6 hours
**Priority**: MEDIUM (cost reduction)

**Current**: Claude Opus 4.1 for all research ($0.16 per run × 2 bots × 30 days = $9.60/month)

**Goal**: Reduce API costs by 60-70% without sacrificing quality

**Strategy**:
1. **Initial Screening** (GPT-4o-mini)
   - Fast, cheap model ($0.02 per run)
   - Generate 20-30 stock candidates
   - Rough scoring (0-100)
2. **Deep Validation** (Claude Opus 4.1)
   - Expensive but accurate model
   - Analyze only top 10 candidates from screening
   - Detailed research and recommendations

**Cost Comparison**:
```
Current:
  Claude Opus × 2 bots × 30 days = $9.60/month

Optimized:
  GPT-4o-mini × 2 bots × 30 days = $1.20/month
  Claude Opus × 2 bots × 10 stocks/day × 30 days = $3.20/month
  Total = $4.40/month (54% savings)
```

**Implementation**:
1. Create `scripts/research/multi_llm_research.py`
2. Phase 1: GPT-4o-mini screening
   - Generate 30 candidates with rough scores
3. Phase 2: Claude Opus deep dive
   - Analyze top 10 from screening
   - Full research reports
4. Combine results into final recommendations

**Success Criteria**:
- [ ] API costs reduced by ≥50%
- [ ] Research quality maintained (no drop in approval rate)
- [ ] Generation time < 15 minutes (currently ~10 minutes)

### Optimization 2: Historical Backtesting
**Effort**: 12 hours
**Priority**: MEDIUM (validate strategy)

**Goal**: Prove multi-agent system would have performed well historically

**Implementation**:
1. Collect historical trade recommendations (last 6 months)
2. Run multi-agent validation on each recommendation
3. Compare to actual outcomes:
   - What would approval rate have been?
   - What would win rate have been?
   - What would returns have been?
4. Identify patterns:
   - Which types of trades work best?
   - Which catalysts are most reliable?
   - Which market conditions favor the strategy?
5. Optimize agent weights based on historical accuracy

**Backtest Scenarios**:
- Bull market (Sep-Oct 2024)
- Correction (Aug 2024)
- Volatile market (election period)
- Post-earnings season
- Pre-Fed meetings

**Success Criteria**:
- [ ] 6 months of historical data analyzed
- [ ] Approval rate calculated (target: ≥50%)
- [ ] Win rate calculated (target: ≥55%)
- [ ] Agent weights optimized based on results
- [ ] Strategy validated or adjusted

### Optimization 3: Kelly Criterion Position Sizing
**Effort**: 8 hours
**Priority**: MEDIUM (maximize returns)

**Current**: Fixed position sizes (8% DEE max, 10% SHORGAN max)

**Goal**: Optimize position sizes based on confidence and historical win rate

**Kelly Formula**:
```
f = (bp - q) / b

Where:
  f = fraction of capital to bet
  b = odds received (average win / average loss)
  p = probability of winning (win rate)
  q = probability of losing (1 - p)
```

**Implementation**:
1. Calculate historical Kelly parameters:
   - Win rate (p): 60% (from first month)
   - Average win: +8%
   - Average loss: -5%
   - Odds (b): 8% / 5% = 1.6
2. Calculate Kelly fraction:
   - f = (1.6 × 0.6 - 0.4) / 1.6 = 0.35 (35% of capital)
3. Use fractional Kelly (25% of full Kelly for safety):
   - Recommended: 0.35 × 0.25 = 8.75% per position
4. Adjust by confidence:
   - High confidence (0.75): 8.75% × (0.75/0.55) = 11.9% → 10% (capped)
   - Medium confidence (0.65): 8.75% × (0.65/0.55) = 10.3% → 10% (capped)
   - Low confidence (0.55): 8.75% × (0.55/0.55) = 8.75%

**Success Criteria**:
- [ ] Kelly parameters calculated from historical data
- [ ] Position sizing formula implemented
- [ ] Sizes adjusted by confidence level
- [ ] Max position limits enforced (8% DEE, 10% SHORGAN)
- [ ] Better risk-adjusted returns (higher Sharpe ratio)

### Optimization 4: Real-Time Monitoring
**Effort**: 10 hours
**Priority**: LOW (nice to have)

**Features**:
1. **Live P&L Dashboard**
   - Real-time portfolio value
   - Intraday P&L by position
   - Overall daily P&L
2. **Position Monitor**
   - Current positions with entry prices
   - Unrealized P&L per position
   - Distance to stop loss
3. **Alert System**
   - Stop loss breached (immediate Telegram alert)
   - Position up >10% (consider profit-taking)
   - Position down >8% (approaching stop)
4. **Catalyst Countdown**
   - Days until catalyst event (earnings, FDA decision)
   - Auto-close reminder (e.g., "Exit FUBO before Oct 29 earnings")

**Implementation**:
- Create `web/realtime_monitor.py` (Flask app)
- Fetch live data from Alpaca API (quotes, positions)
- WebSocket for real-time updates
- Telegram alerts for critical events

**Success Criteria**:
- [ ] Dashboard shows real-time P&L
- [ ] Alerts delivered within 1 minute of event
- [ ] Catalyst countdowns accurate
- [ ] Auto-close reminders sent 1 day before event

---

## Phase 5: Advanced Strategies (Future)
**Timeline**: Month 4+ (Jan 21, 2026+)
**Goal**: Expand beyond current strategies
**Priority**: RESEARCH

### Strategy 1: Earnings Momentum
**Concept**: Trade stocks reporting earnings with positive surprises

**Implementation**:
- Monitor earnings calendar
- Predict earnings surprise using alternative data
- Enter positions 1-2 days before earnings
- Exit on earnings day or day after

### Strategy 2: M&A Arbitrage
**Concept**: Trade merger spreads when deals announced

**Implementation**:
- Monitor M&A announcements
- Calculate arbitrage spread (offer price vs current price)
- Assess deal risk (regulatory, financing, shareholder approval)
- Enter positions with favorable risk/reward (>15% spread, >70% probability)

### Strategy 3: Sector Rotation
**Concept**: Rotate between sectors based on economic cycle

**Implementation**:
- Track economic indicators (GDP, unemployment, inflation)
- Identify current phase (early cycle, mid cycle, late cycle, recession)
- Overweight outperforming sectors (e.g., tech in early cycle)
- Underweight underperforming sectors (e.g., utilities in early cycle)

### Strategy 4: Mean Reversion
**Concept**: Trade oversold/overbought conditions

**Implementation**:
- Identify stocks with extreme RSI (>70 or <30)
- Validate with fundamentals (strong company, temporary selloff)
- Enter contrarian positions
- Exit when RSI normalizes

---

## Resource Requirements

### Current Monthly Costs
```
Claude Opus 4.1:        $9.60  (research)
Financial Datasets:    $49.00  (market data)
Alpaca Trading:         $0.00  (commission-free)
Total:                 $58.60/month
```

### Phase 2 Additional Costs (Nov 11-22)
```
Telegram Bot:          $0.00  (free)
ChatGPT automation:    $0.00  (no extra API calls)
Dashboard hosting:     $0.00  (localhost)
Total Added:           $0.00
```

### Phase 3 Additional Costs (Nov 25 - Dec 20)
```
Tradier Options:      $10.00  (options data)
Quandl Dark Pools:    $50.00  (alternative data)
Total Added:          $60.00
New Monthly Total:   $118.60
```

### Phase 4 Cost Savings (Dec 21 - Jan 20)
```
Multi-LLM Strategy:   -$5.20  (54% savings on research)
New Monthly Total:   $113.40
```

### Break-Even Analysis
```
Monthly Costs:        $113.40
Required Profit:      $113.40/month = $3.78/day

At $200K portfolio:
  Daily Return Needed: 0.0019% (0.19 basis points)
  Monthly Return:      0.057% (5.7 basis points)

Very achievable with current 90% approval rate and 60%+ expected win rate
```

---

## Success Metrics

### Month 1 (Oct 28 - Nov 28)
- **Approval Rate**: ≥60% (current: 90% in testing)
- **Win Rate**: ≥55% (industry standard: 50%)
- **Sharpe Ratio**: ≥1.0 (market: ~0.8)
- **Max Drawdown**: <15%
- **System Uptime**: ≥95% (no missed executions)

### Month 2 (Nov 29 - Dec 28)
- **Approval Rate**: ≥65% (improved with agent optimization)
- **Win Rate**: ≥58%
- **Sharpe Ratio**: ≥1.2
- **Max Drawdown**: <12%
- **Agent Accuracy**: ≥60% (individual agent win rates)

### Month 3 (Dec 29 - Jan 28)
- **Approval Rate**: ≥70%
- **Win Rate**: ≥60%
- **Sharpe Ratio**: ≥1.5
- **Max Drawdown**: <10%
- **API Cost Reduction**: ≥50%

### Month 6 (Apr 28, 2026)
- **Total Return**: ≥15% (vs SPY: ~8%)
- **Cumulative Alpha**: ≥7% (vs market)
- **System Reliability**: ≥99% uptime
- **Fully Automated**: No manual intervention needed

---

## Risk Management

### Risk 1: Model Overfitting
**Mitigation**:
- Out-of-sample testing (test on unseen data)
- Walk-forward optimization (retrain monthly)
- Avoid optimizing on too few trades (<100 minimum)

### Risk 2: Market Regime Change
**Mitigation**:
- Adaptive thresholds (adjust monthly based on performance)
- Multiple strategies (defensive + catalyst)
- Reduced position sizes in high volatility

### Risk 3: Data Provider Failure
**Mitigation**:
- Multiple data sources (FD API primary, Yahoo backup, Alpaca tertiary)
- Graceful degradation (accept lower approval rate vs no trades)
- Manual override always available

### Risk 4: Regulatory Changes
**Mitigation**:
- Monitor SEC rules for algorithmic trading
- Maintain audit trail of all decisions
- User approval required before execution (8:35 AM review)
- Kill switch readily available

---

## Next Review

**Date**: November 8, 2025 (end of Week 2)
**Focus**: Performance analysis, optimization decisions
**Deliverables**: Week 1-2 report, agent accuracy analysis, roadmap adjustments

**Key Questions**:
1. Is approval rate meeting expectations (≥60%)?
2. Are agents voting accurately (≥55% win rate)?
3. Should we adjust confidence threshold?
4. Which enhancements should we prioritize?
5. Any critical bugs discovered?

---

**Document Created**: October 24, 2025
**Last Updated**: October 24, 2025
**Next Update**: November 8, 2025
**Status**: ACTIVE ROADMAP
