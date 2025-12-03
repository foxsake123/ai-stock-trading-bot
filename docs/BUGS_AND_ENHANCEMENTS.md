# Bugs and Enhancement Tracking
## AI Trading Bot - December 2025

---

## Known Bugs

### BUG-001: Market Data Float Division by Zero
- **Status**: OPEN
- **Priority**: LOW
- **Location**: `scripts/automation/daily_claude_research.py`
- **Error**: "Error fetching market data: float division by zero"
- **Impact**: Minor - research still generates correctly
- **Root Cause**: Division without zero-check in market data calculations
- **Fix**: Add `if denominator != 0` check before division
- **Discovered**: Dec 2, 2025

### BUG-002: Report Combining Path Error
- **Status**: OPEN
- **Priority**: MEDIUM
- **Location**: `scripts/automation/daily_claude_research.py` - combining section
- **Error**: "No such file or directory: 'scripts\\reports\\premarket\\...'"
- **Impact**: Combined report not created (individual reports work fine)
- **Root Cause**: Using relative path instead of absolute path
- **Fix**: Use `Path(__file__).parent.parent.parent / "reports"` like individual saves
- **Discovered**: Dec 2, 2025

### BUG-003: AVDX Asset Not Active
- **Status**: CLOSED (External)
- **Priority**: N/A
- **Description**: AVDX orders failed with "asset is not active"
- **Impact**: One trade could not execute
- **Root Cause**: External - stock halted/delisted
- **Resolution**: No fix needed - skip inactive assets in future
- **Discovered**: Dec 2, 2025

---

## Enhancement Backlog

### Priority 1: Critical (1-2 hours each)

| ID | Enhancement | Effort | Status |
|----|-------------|--------|--------|
| ENH-001 | Fix BUG-001 (division by zero) | 30 min | TODO |
| ENH-002 | Fix BUG-002 (path error) | 30 min | TODO |
| ENH-003 | Add asset status check before ordering | 1 hr | TODO |

### Priority 2: ML System (4-6 hours total)

| ID | Enhancement | Effort | Status |
|----|-------------|--------|--------|
| ENH-010 | Schedule outcome tracking (4:30 PM daily) | 1 hr | TODO |
| ENH-011 | Build training data pipeline | 2 hr | TODO |
| ENH-012 | Feature engineering (market conditions) | 2 hr | TODO |
| ENH-013 | Initial model training (after 100+ trades) | 3 hr | TODO |

### Priority 3: Automation Reliability (2-3 hours total)

| ID | Enhancement | Effort | Status |
|----|-------------|--------|--------|
| ENH-020 | Health monitoring with Telegram alerts | 1 hr | TODO |
| ENH-021 | Retry logic with exponential backoff | 1 hr | TODO |
| ENH-022 | Execution verification (confirm fills) | 1 hr | TODO |

### Priority 4: Performance (3-4 hours total)

| ID | Enhancement | Effort | Status |
|----|-------------|--------|--------|
| ENH-030 | Batch ticker requests efficiently | 1 hr | TODO |
| ENH-031 | Cache market data within session | 1 hr | TODO |
| ENH-032 | Parallelize independent operations | 2 hr | TODO |

### Priority 5: Risk Management (4-6 hours total)

| ID | Enhancement | Effort | Status |
|----|-------------|--------|--------|
| ENH-040 | Implement trailing stops | 2 hr | TODO |
| ENH-041 | Position correlation check | 2 hr | TODO |
| ENH-042 | Daily risk report generation | 2 hr | TODO |

---

## Completed Enhancements (Dec 2025)

| Date | Enhancement | Description |
|------|-------------|-------------|
| Dec 2 | Position limit fix | Use invested capital for SHORGAN Live |
| Dec 2 | Keep-awake script | Prevent Windows sleep during trading |
| Dec 2 | ML data collection | Infrastructure for training data |
| Dec 2 | ML integration | Auto-log trades to training data |
| Dec 2 | Repository cleanup | Root directory 70+ to 19 files |
| Dec 2 | Performance graph fix | Fixed SHORGAN Live spike/dip (schema detection) |
| Dec 2 | PDF report generator | Created performance report PDF generator |
| Dec 2 | PROD-021 Drawdown alerts | Alert when portfolio drops >5% from peak |
| Dec 2 | PROD-023 Daily loss limiter | Block trading if daily loss exceeds threshold |
| Dec 2 | PROD-003 Trade execution alerts | Telegram alerts for each trade with details |

---

## ML Training Data Status

**Current Stats** (Dec 2, 2025):
- Trade records: 0 (infrastructure just deployed)
- Outcome records: 0
- Features logged: symbol, action, conviction, agent_scores, approval status

**Target for Model Training**:
- Minimum: 100 trade records with outcomes
- Ideal: 500+ trade records
- Estimated time to 100 trades: 2-3 weeks (at ~8 trades/day)

---

## System Health Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Automation Success Rate | ~80% | 95% | Needs keep-awake |
| Trade Fill Rate | 85% | 90% | Good |
| Research Generation | 100% | 100% | Good |
| Position Limit Compliance | 100% | 100% | Fixed Dec 2 |
| API Rate Limit Compliance | 100% | 100% | Good |

---

## Next Steps (Priority Order)

1. **Dec 3**: Verify keep-awake prevents automation failures
2. **Dec 4-5**: Fix BUG-001 and BUG-002
3. **Week 2**: Add outcome tracking to Task Scheduler
4. **Week 3-4**: Collect 100+ trades, begin ML analysis
5. **Week 5+**: Train and integrate initial ML model

---

## Product Enhancement Suggestions (High Value)

### Priority A: User Experience & Visibility

| ID | Enhancement | Value | Effort | Description |
|----|-------------|-------|--------|-------------|
| PROD-001 | Daily P&L Email/SMS | HIGH | 2 hr | Send daily summary with P&L, trades executed, portfolio value |
| PROD-002 | Web Dashboard | HIGH | 8 hr | Simple Flask/Streamlit dashboard showing real-time portfolio |
| PROD-003 | Trade Execution Alerts | HIGH | 1 hr | Telegram alert with fill price, P&L impact for each trade |
| PROD-004 | Weekly Performance Report | MEDIUM | 2 hr | Automated PDF with weekly returns, best/worst trades, sector exposure |

### Priority B: Trading Intelligence

| ID | Enhancement | Value | Effort | Description |
|----|-------------|-------|--------|-------------|
| PROD-010 | Earnings Calendar Integration | HIGH | 3 hr | Auto-flag positions with upcoming earnings, suggest pre-earnings actions |
| PROD-011 | Sector Rotation Signals | HIGH | 4 hr | Track sector momentum, suggest rotation trades |
| PROD-012 | Correlation-Based Position Sizing | MEDIUM | 3 hr | Reduce position sizes when adding correlated assets |
| PROD-013 | News Sentiment Scoring | MEDIUM | 4 hr | Score news headlines, flag significant sentiment shifts |

### Priority C: Risk Management

| ID | Enhancement | Value | Effort | Description |
|----|-------------|-------|--------|-------------|
| PROD-020 | Portfolio Heat Map | HIGH | 2 hr | Visual showing sector/position concentration risk |
| PROD-021 | Drawdown Alerts | HIGH | 1 hr | Alert when portfolio drops >5% from peak |
| PROD-022 | Beta-Adjusted Position Limits | MEDIUM | 2 hr | Limit high-beta positions to control volatility |
| PROD-023 | Max Loss Per Day Limit | HIGH | 1 hr | Auto-stop trading if daily loss exceeds threshold |

### Priority D: ML & Analytics

| ID | Enhancement | Value | Effort | Description |
|----|-------------|-------|--------|-------------|
| PROD-030 | Trade Win Rate Dashboard | MEDIUM | 2 hr | Track win rate by strategy, timeframe, sector |
| PROD-031 | Conviction Score Calibration | HIGH | 3 hr | Analyze if HIGH conviction trades outperform MEDIUM |
| PROD-032 | Agent Performance Tracking | MEDIUM | 2 hr | Track which agent (fundamental, technical, etc.) is most predictive |
| PROD-033 | Backtest New Strategies | HIGH | 4 hr | Framework to backtest strategy changes before deployment |

### Priority E: Automation & Reliability

| ID | Enhancement | Value | Effort | Description |
|----|-------------|-------|--------|-------------|
| PROD-040 | Cloud Deployment | HIGH | 6 hr | Move to AWS/GCP for 24/7 reliability (no sleep issues) |
| PROD-041 | Graceful Degradation | MEDIUM | 2 hr | Continue with cached data if API fails |
| PROD-042 | Multi-Broker Support | LOW | 8 hr | Add support for IBKR, Schwab as backup |
| PROD-043 | Paper-to-Live Sync | MEDIUM | 3 hr | Auto-sync successful paper strategies to live account |

---

## Recommended Next 5 Enhancements (Quick Wins)

Based on value/effort ratio:

1. ~~**PROD-021 Drawdown Alerts** (1 hr, HIGH value)~~ - ✅ DONE Dec 2
2. ~~**PROD-003 Trade Execution Alerts** (1 hr, HIGH value)~~ - ✅ DONE Dec 2
3. ~~**PROD-023 Max Loss Per Day** (1 hr, HIGH value)~~ - ✅ DONE Dec 2
4. **PROD-001 Daily P&L Email** (2 hr, HIGH value) - User experience
5. **PROD-020 Portfolio Heat Map** (2 hr, HIGH value) - Risk visualization

### Updated Top 5 (Dec 2):
1. **PROD-001 Daily P&L Email** (2 hr) - Daily summary with portfolio value, trades
2. **PROD-020 Portfolio Heat Map** (2 hr) - Visual sector/position concentration
3. **PROD-010 Earnings Calendar** (3 hr) - Flag positions with upcoming earnings
4. **PROD-031 Conviction Calibration** (3 hr) - Analyze HIGH vs MEDIUM trade performance
5. **PROD-040 Cloud Deployment** (6 hr) - Move to AWS/GCP for 24/7 reliability

---

*Last Updated: December 2, 2025 (Evening)*
