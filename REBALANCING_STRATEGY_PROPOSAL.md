# Auto-Rebalancing Strategy Proposal
**Created**: October 27, 2025
**Status**: Proposal - Awaiting User Approval
**Config Flag**: `ENABLE_AUTO_REBALANCING=false` (.env line 93)

---

## 🎯 Current State

**Auto-rebalancing is DISABLED** (as of Oct 27, 2025)

- Research generates new trades weekly (Saturday 12 PM)
- Trades executed Monday 9:30 AM
- Positions held indefinitely until:
  - Stop loss triggers
  - Manual close
  - New research recommends exit

**Problem**: Positions can become stale, winners can become over-sized, losers can linger.

---

## 📊 Proposed Rebalancing Strategy

### Option 1: Weekly Review & Refresh (RECOMMENDED)
**Trigger**: Every Saturday during research generation
**Process**:
1. Claude research analyzes current portfolio
2. Identifies positions to HOLD, EXIT, or TRIM
3. Recommends new entries to replace exits
4. Monday execution includes both entries and exits

**Rules**:
- Exit positions held >14 days with no catalyst progress
- Trim winners that exceed 15% position size (take profits)
- Close losers approaching stop loss (5% buffer)
- Maximum 5 exits per week (gradual rebalancing)

**Example Output**:
```markdown
## PORTFOLIO REBALANCING

### EXITS (Free up capital for new opportunities)
- **ENPH**: EXIT - Held 18 days, catalyst passed, up 12% → Lock in gains
- **SHOP**: EXIT - Held 21 days, down 8%, approaching stop → Cut losses
- **AMD**: TRIM 50% - Position grew to 18% of portfolio → Reduce concentration

### NEW ENTRIES (Replace exits)
- **TSLA**: BUY - New catalyst: Model 3 refresh (Nov 15)
- **NVDA**: BUY - Oversold, earnings beat expected (Nov 20)
```

**Pros**:
- Keeps portfolio fresh with current catalysts
- Locks in gains from winners
- Cuts losses before hitting hard stops
- Aligns with existing weekly research schedule

**Cons**:
- May exit trades prematurely
- Could miss long-term runners
- Generates more taxable events

---

### Option 2: Daily Profit-Taking & Loss-Cutting
**Trigger**: Every day at 4:30 PM (after market close)
**Process**:
1. Scan all positions for profit/loss thresholds
2. Auto-close positions meeting criteria
3. Log exits for next Monday's research

**Rules**:
- **Profit Taking**: Close 50% of position at +25% gain
- **Loss Cutting**: Close position at -12% loss (before stop at -15%)
- **Stale Positions**: Close after 30 days with <5% movement
- **Concentration Risk**: Trim if position >20% of portfolio

**Pros**:
- Locks in gains automatically
- Cuts losses before catastrophic drops
- Runs daily, requires no manual intervention

**Cons**:
- May sell too early in strong trends
- More aggressive than weekly
- Could conflict with multi-agent validation

---

### Option 3: Hybrid (Weekly + Daily Guards)
**Trigger**: Weekly refresh + daily safety checks
**Process**:
1. **Daily (4:30 PM)**: Check profit-taking and loss-cutting thresholds only
2. **Weekly (Saturday)**: Full portfolio review, identify staleness, recommend refreshes

**Rules**:
- Daily: Only exit extreme winners (+30%) or dangerous losers (-13%)
- Weekly: Full review for staleness, concentration, new opportunities
- Combined: Best of both worlds

**Pros**:
- Safety guardrails prevent disasters
- Weekly refresh keeps strategy aligned
- Balanced approach

**Cons**:
- More complex to implement
- Two different rebalancing logics

---

## 🤖 Recommended Implementation

**For DEE-BOT (Defensive, $100K paper)**:
- **Weekly Rebalancing** (Option 1)
- Review every Saturday with research
- Max 3 exits per week
- Profit take at +20%
- Exit stale positions after 21 days

**For SHORGAN-BOT (Aggressive, $1K live)**:
- **Daily Guards + Weekly Refresh** (Option 3)
- Daily: Exit +30% winners (lock gains), -12% losers (cut losses)
- Weekly: Full review, refresh event-driven positions
- Max 2 exits per week from weekly review
- Daily guards act as circuit breakers

---

## 🛠️ Implementation Plan

### Phase 1: Create Rebalancing Logic (2 hours)
1. Create `scripts/automation/portfolio_rebalancer.py`
2. Functions:
   - `analyze_current_positions()` - Fetch all open positions
   - `check_profit_thresholds()` - Identify +25%/+30% winners
   - `check_loss_thresholds()` - Identify -12%/-13% losers
   - `check_staleness()` - Identify 14/21/30 day holds
   - `check_concentration()` - Identify >15%/20% positions
   - `generate_exit_orders()` - Create exit orders
3. Respect `ENABLE_AUTO_REBALANCING` flag from .env

### Phase 2: Integrate with Research (1 hour)
1. Modify `claude_research_generator.py`
2. Add portfolio context to prompts:
   - Current positions with age and P&L
   - Positions flagged for exit consideration
3. Claude recommends HOLD/EXIT for each position
4. Parser extracts exit recommendations

### Phase 3: Integrate with Execution (30 min)
1. Modify `execute_daily_trades.py`
2. Process exit orders before entry orders
3. Ensure capital freed up for new positions
4. Log all rebalancing activity

### Phase 4: Add Automation Trigger (30 min)
1. Option A: Daily at 4:30 PM (after performance graph)
2. Option B: Weekly on Saturday (before research)
3. Option C: Both (hybrid)

---

## ⚙️ Configuration Variables

Add to `.env`:

```bash
# Rebalancing Configuration
ENABLE_AUTO_REBALANCING=false  # Master switch (already exists)
REBALANCING_MODE=weekly  # daily, weekly, hybrid
REBALANCING_PROFIT_THRESHOLD=25  # % gain to trigger profit-taking
REBALANCING_LOSS_THRESHOLD=12  # % loss to trigger exit (before stop)
REBALANCING_STALE_DAYS=21  # Days without catalyst progress
REBALANCING_MAX_POSITION_SIZE=15  # % of portfolio (concentration limit)
REBALANCING_MAX_EXITS_PER_WEEK=5  # Gradual rebalancing
```

---

## 🚨 Safety Considerations

**Before Enabling**:
- [ ] Test rebalancing logic with paper accounts (both DEE and SHORGAN)
- [ ] Verify exit orders don't conflict with stop losses
- [ ] Ensure sufficient capital for new entries
- [ ] Add manual override/approval for first week
- [ ] Log all rebalancing decisions for review

**Risks**:
- **Selling winners too early**: Could miss 50%+ runners
- **Tax implications**: More short-term capital gains
- **Strategy drift**: May deviate from original research intent
- **Execution conflicts**: Exit and entry orders at same time

**Mitigations**:
- Start with paper accounts only
- Manual review of rebalancing log before execution
- Conservative thresholds (+30% profit, not +25%)
- Weekly rebalancing is less aggressive than daily

---

## 📈 Expected Impact

### Without Rebalancing (Current State)
- **Pros**: Let winners run, avoid unnecessary trading
- **Cons**: Stale positions, concentration risk, slow capital rotation
- **Annual Trades**: ~50 (1 per week)

### With Weekly Rebalancing
- **Pros**: Fresh portfolio, locked gains, reduced concentration
- **Cons**: May exit early, more taxable events
- **Annual Trades**: ~150 (3 per week = 2 new + 1 exit)

### With Hybrid (Daily + Weekly)
- **Pros**: Best risk management, captures big moves
- **Cons**: Most complex, highest trade count
- **Annual Trades**: ~200 (varies with volatility)

---

## 🎯 Recommendation

**For tomorrow (Oct 28, 2025) LIVE TRADING START**:
- ⛔ **KEEP REBALANCING DISABLED**
- Let first week of trades play out naturally
- Observe how positions perform
- Gather data on win rates, hold times, P&L

**After 1 week (Nov 4, 2025)**:
- Enable Weekly Rebalancing for SHORGAN-BOT paper account (test)
- Review results on Nov 11
- If successful, enable for SHORGAN-BOT live with manual approval

**After 1 month (Nov 28, 2025)**:
- Consider Hybrid mode (Daily guards + Weekly refresh)
- Full automation without manual approval
- Monitor for 2 weeks before trusting completely

---

## 🔧 To Enable Auto-Rebalancing

**When you're ready**:

1. **Edit .env file**:
   ```bash
   ENABLE_AUTO_REBALANCING=true
   REBALANCING_MODE=weekly
   ```

2. **Run rebalancing setup**:
   ```bash
   python scripts/setup/configure_rebalancing.py
   ```

3. **Test with paper account**:
   ```bash
   python scripts/automation/portfolio_rebalancer.py --dry-run
   ```

4. **Enable in Task Scheduler** (if desired):
   - Daily: 4:30 PM (after performance graph)
   - Weekly: Saturday 11:55 AM (before research)

---

## 📞 Questions to Answer Before Implementing

1. **Risk Tolerance**: How much drawdown are you comfortable with before forcing an exit?
   - Current: -15% stop loss
   - Proposed: -12% auto-exit (before stop triggers)

2. **Profit Taking**: When should winners be trimmed?
   - Conservative: +20% (lock gains quickly)
   - Moderate: +25% (let winners run a bit)
   - Aggressive: +30% (maximize upside)

3. **Position Freshness**: How long before a position is considered stale?
   - Aggressive: 14 days (high turnover)
   - Moderate: 21 days (3 weeks)
   - Conservative: 30 days (monthly refresh)

4. **Rebalancing Frequency**: How often to rebalance?
   - Daily: Maximum responsiveness, highest trade count
   - Weekly: Balanced, aligns with research schedule
   - Monthly: Minimal trading, let strategies play out

5. **Manual Review**: Do you want to approve rebalancing exits before execution?
   - Yes: Safer, you maintain control
   - No: Fully automated, hands-off

---

## 📝 Next Steps

**IMMEDIATE** (Oct 27, 2025):
- [x] Document rebalancing strategy options
- [x] Present to user for feedback
- [ ] User decides on preferred approach
- [ ] User answers 5 questions above

**SHORT-TERM** (Nov 4-11, 2025):
- [ ] Implement chosen rebalancing strategy
- [ ] Test with paper accounts
- [ ] Validate logic with backtest
- [ ] Deploy with manual approval

**LONG-TERM** (Dec 2025):
- [ ] Full automation after 1 month of live trading
- [ ] Monitor rebalancing impact on returns
- [ ] Adjust thresholds based on results
- [ ] Compare rebalanced vs non-rebalanced performance

---

**STATUS**: Awaiting user decision on rebalancing strategy
**FLAG**: `ENABLE_AUTO_REBALANCING=false` (keep disabled for now)
**RECOMMENDATION**: Weekly rebalancing starting Nov 4, 2025

---

**Questions? Need clarification on any option?**
Reply with your preferred strategy (Option 1, 2, or 3) and answers to the 5 questions above.
