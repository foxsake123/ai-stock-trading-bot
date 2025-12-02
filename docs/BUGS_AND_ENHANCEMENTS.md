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

*Last Updated: December 2, 2025*
