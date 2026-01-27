# Bugs and Enhancement Tracking
## AI Trading Bot - December 2025

---

## Known Bugs

### BUG-001: Market Data Float Division by Zero
- **Status**: FIXED ✅
- **Priority**: LOW
- **Location**: `scripts/automation/claude_research_generator.py` (line 832)
- **Error**: "Error fetching market data: float division by zero"
- **Impact**: Minor - research still generates correctly
- **Root Cause**: Division by `ask_price` without zero-check in `get_market_snapshot()`
- **Fix**: Added zero-checks for all price/size fields before calculations
- **Fixed**: Dec 3, 2025
- **Discovered**: Dec 2, 2025

### BUG-002: Report Combining Path Error
- **Status**: FIXED ✅
- **Priority**: MEDIUM
- **Location**: `scripts/automation/daily_claude_research.py` (line 261)
- **Error**: "No such file or directory: 'scripts\\reports\\premarket\\...'"
- **Impact**: Combined report not created (individual reports work fine)
- **Root Cause**: `Path(__file__).parent.parent` only went up to `scripts/`, not project root
- **Fix**: Changed to `Path(__file__).parent.parent.parent` (3 levels up)
- **Fixed**: Dec 3, 2025
- **Discovered**: Dec 2, 2025

### BUG-003: AVDX Asset Not Active
- **Status**: CLOSED (External)
- **Priority**: N/A
- **Description**: AVDX orders failed with "asset is not active"
- **Impact**: One trade could not execute
- **Root Cause**: External - stock halted/delisted
- **Resolution**: No fix needed - skip inactive assets in future
- **Discovered**: Dec 2, 2025

### BUG-004: Task Scheduler Wrong Python Path
- **Status**: FIXED ✅
- **Priority**: HIGH
- **Description**: 3 Task Scheduler tasks have wrong Python path
- **Affected Tasks**:
  - AI Trading - Weekend Research
  - AI Trading - Keep Awake
  - AI Trading - Performance Graph
- **Wrong Path**: `C:\Users\shorg\AppData\Local\Programs\Python\Python313\python.exe`
- **Correct Path**: `C:\Python313\python.exe`
- **Impact**: Weekend Research failed Dec 28, no trades generated Dec 29
- **Error Code**: 2147942402 (0x80070002 = File not found)
- **Fix**: Manual - Task Scheduler → Properties → Actions → Edit → Change path
- **Discovered**: Dec 29, 2025
- **Fixed**: Jan 6, 2026

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
| Dec 27 | Security: Remove hardcoded API keys | Replaced hardcoded keys in `src/risk/*.py` with `os.getenv()` |
| Dec 27 | Live trade confirmation prompt | Added `_confirm_live_trades()` requiring "YES" to proceed |
| Dec 27 | Circuit breaker re-check | Re-check daily loss limit before EACH live trade |
| Dec 27 | Position limit re-check | Re-check position count before EACH live trade |
| Dec 27 | Stop loss failure alerts | Telegram alert when stop loss placement fails |
| Dec 27 | Max retry limit | Added MAX_RETRY_ATTEMPTS=3 to prevent infinite retries |
| Dec 27 | Higher live threshold | Increased approval threshold from 55% to 65% for live |
| Dec 27 | Research freshness check | Block stale research (>1 day old) for live trades |
| Dec 27 | Clean up .env duplicates | Removed duplicate ALPACA_API_KEY_SHORGAN entries |
| Dec 3 | Dynamic date injection | System prompts now auto-generate dates (no more manual updates) |
| Dec 3 | Pre-market trading | Extended hours trading enabled (4:00-9:30 AM, 4:00-8:00 PM ET) |
| Dec 3 | BUG-001 fix | Division by zero in market data - added zero-checks |
| Dec 3 | BUG-002 fix | Report combining path error - corrected path levels |
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

---

## Recent Session Log (Jan 2026)

### Jan 5-6, 2026 - Trading Pipeline & Rebalancing
- Ran full trading pipeline manually
- Trade results: DEE-BOT 8/0 approved, SHORGAN Paper 6/2, SHORGAN Live 0/9
- 5 successful executions
- SHORGAN Live rebalanced: 13 positions -> 9 positions
- Created `assess_shorgan_live.py` and `rebalance_shorgan_live.py` utility scripts
- All SHORGAN Live positions now profitable except NCNO (-0.8%)
- Total unrealized P&L: ~$194

### BUG-004 Fixed (Jan 6, 2026)
User manually updated all 3 Task Scheduler paths. All tasks now show "Status: Ready".

---

### Jan 26, 2026 - Performance Assessment & System Tightening

**Issues Found:**
- BUG-005: Performance history JSON corruption (FIXED - duplicate record outside array)
- BUG-006: Railway using `web:` instead of `worker:` causing crashes (FIXED)
- BUG-007: SHORGAN Paper at 30 positions with -$111K margin (FIXED - caps added)

**Fixes Applied:**
- Fixed corrupted `performance_history.json` (109 data points restored)
- Railway: Changed to `worker:` type, `ALWAYS` restart, crash-proof main loop
- SHORGAN Paper: Added margin floor (-$30K), position cap (20), conviction min (7+)
- SHORGAN Paper: Tightened stops (12% -> 10%), exit rules (7 day -> 5 day)
- SHORGAN Live: Tightened exit rules (>5% loss + no catalyst -> exit)
- Added validation Filter 7 (position count cap) and Filter 8 (conviction minimum)
- Created `docs/LESSONS_LEARNED.md` - central mistake/prevention reference

**See also:** `docs/LESSONS_LEARNED.md` for comprehensive root cause analysis

---

*Last Updated: January 26, 2026*
