# Lessons Learned & Recurring Issues
## AI Trading Bot - Central Reference Document
## Last Updated: January 27, 2026

This document captures every significant mistake, root cause, and prevention strategy. It is the system's institutional memory. Reference this before making changes.

---

## CATEGORY 1: TRADING STRATEGY MISTAKES

### MISTAKE T-001: SHORGAN Paper Excessive Positions (30 positions)
- **When**: Discovered Jan 26, 2026
- **Impact**: 37% win rate, -$500 open P&L despite +7.94% total return
- **Root Cause**: System prompt allowed 8-12 positions but no hard cap. Research kept recommending new entries without requiring exits first.
- **Fix Applied**:
  - Added MAX POSITIONS: 15-20 to system prompt constraints
  - Added "EXIT too many positions" rebalancing rule
  - Added Filter 7 in validation: blocks new buys when at max positions
- **Prevention**: Hard cap enforced in both prompt AND validation code

### MISTAKE T-002: SHORGAN Paper Margin Explosion (-$111K cash)
- **When**: Discovered Jan 26, 2026
- **Impact**: Significant margin risk. Sharp downturn could trigger margin calls.
- **Root Cause**: No margin limit in system prompt. Cash buffer target ($15-25K) was a suggestion, not enforced.
- **Fix Applied**:
  - Added MARGIN FLOOR: Cash must stay above -$30,000 to system prompt
  - Added "EXIT margin too high" rebalancing rule
- **Prevention**: Margin limit in prompt. Future: add hard validation check on margin levels.

### MISTAKE T-003: SHORGAN Low Win Rate (33-37%)
- **When**: Ongoing since inception
- **Impact**: Many small losers drag performance. Winners need to be much larger to compensate.
- **Root Cause**: Too many low-conviction speculative entries. Catalyst-driven strategy picks quantity over quality.
- **Fix Applied**:
  - Tightened conviction requirements to 7+ for new entries
  - Reduced new opportunity count from "8-12" to "5-8 high-conviction only"
  - Added Filter 8: blocks LOW conviction SHORGAN buys
  - Tightened stop losses: 12% stocks -> 10%, 15% shorts -> 12%
  - Tightened exit rules: catalyst passed 7 days -> 5 days, loss threshold 10% -> 7%
- **Prevention**: Quality > quantity in prompt. Validation blocks low conviction.

### MISTAKE T-004: SHORGAN Live Underperformance (-4.5%)
- **When**: Since inception ($3K account)
- **Impact**: Losing real money. 33% win rate.
- **Root Cause**: Small account spread across too many positions. Same loose selection criteria as paper.
- **Fix Applied**:
  - Hard cap 12 positions (was soft 8-12)
  - Exit threshold tightened: >5% loss with no catalyst -> exit
  - Added "drifting loser" rule: >3% loss + no catalyst in 14 days -> exit
  - Explicit instruction to be aggressive on exits, selective on entries
- **Prevention**: Smaller account needs higher selectivity. Fewer, better trades.

### MISTAKE T-005: NFLX $10 Limit Order for $850 Stock
- **When**: Jan 20, 2026 (SHORGAN Live manual execution)
- **Impact**: Would have been a terrible fill or just expired
- **Root Cause**: Research generated unrealistic limit price. No sanity check.
- **Fix Applied**: Manual skip during execution
- **Prevention**: Future: add price sanity check (limit price must be within 10% of current)

---

## CATEGORY 2: AUTOMATION & INFRASTRUCTURE FAILURES

### MISTAKE A-001: Railway Crashes Repeatedly
- **When**: Jan 20 crash, Jan 25 CLI expiry, multiple earlier incidents
- **Impact**: Missed trading days. No research, no trades, no performance updates.
- **Root Cause (3 issues)**:
  1. Procfile used `web:` - Railway expected HTTP health checks, killed non-responsive process
  2. Restart policy `ON_FAILURE` with 3 max retries - stopped restarting after 3 crashes
  3. No error handling in main scheduler loop - any exception killed the process
- **Fix Applied** (Jan 26, 2026):
  1. Changed Procfile to `worker:` (no HTTP health checks)
  2. Changed restart to `ALWAYS` with 10 retries
  3. Added try/except in main loop with Telegram alerts after 5 consecutive errors
- **Prevention**: Worker process type + always-restart + crash-proof loop. Monitor 9 AM heartbeat.

### MISTAKE A-002: Task Scheduler Wake-From-Sleep Failure
- **When**: Nov 11-14, 2025 (entire week lost)
- **Impact**: Zero trades executed for a full week
- **Root Cause**: Windows Task Scheduler "Wake computer" setting wouldn't save. Computer slept through scheduled times.
- **Fix Applied**: Keep computer on during trading hours (pragmatic workaround)
- **Prevention**: Migrated to Railway (always-on cloud). Local Task Scheduler is backup only.

### MISTAKE A-003: Task Scheduler Wrong Python Path
- **When**: Dec 28, 2025
- **Impact**: Weekend research failed, no trades generated Dec 29
- **Root Cause**: Python installed at `C:\Python313\` but scheduler had `C:\Users\...\Python313\`
- **Fix Applied**: Manually corrected paths in Task Scheduler (Jan 6, 2026)
- **Prevention**: Use Railway as primary. Verify paths after any Python update.

### MISTAKE A-004: API Rate Limiting (30K tokens/min)
- **When**: Nov 20, 2025
- **Impact**: SHORGAN research incomplete (hit turn limit before ORDER BLOCK)
- **Root Cause**: Generating 3 research reports simultaneously hit Anthropic rate limits
- **Fix Applied**: Sequential generation with 120-second delays between reports
- **Prevention**: Built into `daily_claude_research.py` pipeline

### MISTAKE A-005: Relative Path Dependencies
- **When**: Nov 18, 2025
- **Impact**: SHORGAN research files saved to wrong directory, appeared missing
- **Root Cause**: `save_report()` used relative path `Path("reports/...")` which resolved from CWD
- **Fix Applied**: Changed to absolute paths `Path(__file__).parent.parent.parent / "reports"`
- **Prevention**: Always use absolute paths anchored to `__file__` or project root

### MISTAKE A-006: Railway CLI Session Expiry
- **When**: Jan 25, 2026
- **Impact**: Could not manage Railway deployment from CLI
- **Root Cause**: Railway CLI tokens expire after inactivity period
- **Note**: Running deployments are NOT affected by CLI expiry. Only management operations need re-auth.
- **Fix**: Run `railway login` when needed
- **Prevention**: This is normal behavior. The deployment continues running regardless.

### MISTAKE A-007: CircuitBreaker API Mismatch Crashes Railway
- **When**: Jan 27, 2026
- **Impact**: Railway stuck in infinite retry loop since 6 AM, Telegram spam every 30 seconds
- **Root Cause**: `railway_scheduler.py` called `can_execute()` (doesn't exist) and `record_failure()` (needs exception arg). Code was written assuming a different API than what `CircuitBreaker` class actually implements.
- **Fix Applied**:
  - Changed `can_execute()` to `state == "OPEN"`
  - Wrapped `record_failure(e)` in try/except
  - Added 23 smoke tests to verify API contract
- **Prevention**: Run `pytest tests/test_railway_scheduler_smoke.py -v` before every Railway deployment. Tests verify exact CircuitBreaker method signatures.

### MISTAKE A-008: Missing main() Function Blocks Railway Trade Gen
- **When**: Jan 27, 2026 (caught before crash)
- **Impact**: Would have crashed Railway's 8:30 AM trade generation on Jan 28
- **Root Cause**: `generate_todays_trades_v2.py` only had a `__main__` block, no `main()` function. Railway scheduler does `from ... import main`.
- **Fix Applied**: Added `main(date_str=None)` wrapper function
- **Prevention**: Smoke test `TestRunTrades::test_success_path` catches this by mocking the import path.

### MISTAKE A-009: Dead API Key Takes Priority Over Working Key
- **When**: Jan 27, 2026 (caught during pipeline verification)
- **Impact**: DEE-BOT Paper Alpaca connection would fail on Railway during trade validation
- **Root Cause**: `generate_todays_trades_v2.py` used `os.environ.get('ALPACA_API_KEY') or os.environ.get('ALPACA_API_KEY_DEE')`. The dead key `ALPACA_API_KEY` (rotated but still set in env) is non-None, so the `or` fallback to the working `ALPACA_API_KEY_DEE` never triggers.
- **Fix Applied**: Swapped priority to `os.environ.get('ALPACA_API_KEY_DEE') or os.environ.get('ALPACA_API_KEY')`
- **Prevention**: When rotating API keys, remove the old env var entirely rather than leaving it set. Pre-deployment pipeline verification catches connectivity issues.

### MISTAKE A-010: CircuitBreaker API Mismatch in execute_daily_trades.py
- **When**: Jan 28, 2026 (discovered during manual trade execution)
- **Impact**: Trade execution crashed immediately on first trade
- **Root Cause**: Same bug as A-007 but in different file. `execute_daily_trades.py` called `can_execute()` (doesn't exist) and `record_failure()` (needs exception arg).
- **Fix Applied**: Changed `can_execute()` to `state == "OPEN"`, wrapped `record_failure(e)` in try/except
- **Prevention**: The smoke tests (A-007) caught the scheduler, but didn't cover the executor. Need smoke tests for execute_daily_trades.py too.

---

## CATEGORY 3: DATA & CONFIGURATION ISSUES

### MISTAKE D-001: Performance History JSON Corruption
- **When**: Jan 26, 2026
- **Impact**: Performance graph showed only 2 data points instead of 107
- **Root Cause**: JSON file had records appended outside the array structure: `}    {` at end of file
- **Fix Applied**: Removed duplicate record, restored clean JSON (109 data points)
- **Prevention**: Future: validate JSON structure after writes. Add backup before modification.

### MISTAKE D-002: Hardcoded API Keys in Source Code
- **When**: Discovered Oct 29, 2025
- **Impact**: Keys exposed in git history (permanent)
- **Root Cause**: Developer hardcoded keys in `src/risk/risk_monitor.py` during initial development
- **Fix Applied**: Changed to `os.getenv()`, rotated all keys, added pre-commit hook
- **Prevention**: Pre-commit hook scans for key patterns. `.env.example` template.

### MISTAKE D-003: Deposit-Inflated Performance
- **When**: Nov 10, 2025
- **Impact**: SHORGAN Live showed +101% return (fake - was deposit inflation)
- **Root Cause**: Performance calculation didn't account for deposits ($1K -> $2K -> $3K)
- **Fix Applied**: Created `shorgan_live_deposits.json`, deposit-adjusted return calculation
- **Prevention**: All performance calculations use deposit-adjusted formula

### MISTAKE D-004: Stale Research Used for Trading
- **When**: Nov 6, 2025 (research from Nov 5, executed Nov 6 at 2:11 PM)
- **Impact**: Catalyst-driven trades executed after catalysts had passed (APPS down 25%, PAYO down 28%)
- **Root Cause**: 27-hour delay between research and execution
- **Fix Applied**: Research freshness check blocks stale research for live trades
- **Prevention**: Same-day research generation at 6 AM, execution at 9:30 AM

---

## CATEGORY 4: VALIDATION & CALIBRATION

### MISTAKE V-001: 100% Approval Rate (Rubber-Stamping)
- **When**: Oct 27-28, 2025
- **Impact**: All trades approved regardless of quality
- **Root Cause**: External confidence boost override made agent opinions irrelevant
- **Fix Applied**: Hybrid validation - external confidence primary, agents as veto
- **Prevention**: Monitor approval rates. Target 30-50%. Alert if >80% or <20%.

### MISTAKE V-002: 0% Approval Rate (All Rejected)
- **When**: Nov 5-6, 2025
- **Impact**: Zero trades executed despite valid research
- **Root Cause**: MEDIUM conviction (70%) * weak agents (75%) = 52.5% < 55% threshold
- **Fix Applied**: Reduced veto penalties (25% -> 20% for weak consensus)
- **Prevention**: Gap was only 2.5 percentage points. Small calibration changes have big effects.

---

## RECURRING PATTERNS (Meta-Lessons)

### Pattern 1: Single Points of Failure
Every major incident had a single point of failure. Railway was the only automation. Task Scheduler was the only scheduler. Yahoo Finance was the only data source.
**Rule**: Always have a manual fallback procedure documented.

### Pattern 2: Silent Failures Are Worse Than Loud Failures
The worst incidents (Nov 11-14 week of no trades, Railway crash Jan 20) were silent. Nobody knew until much later.
**Rule**: Every automated process must send a Telegram notification on success AND failure. No silent runs.

### Pattern 3: Configuration Drift
Settings that worked at launch (position limits, conviction thresholds, approval rates) gradually became wrong as the system evolved.
**Rule**: Review all thresholds monthly. Log actual vs expected metrics.

### Pattern 4: Complexity Creep in Positions
SHORGAN Paper grew to 30 positions. SHORGAN Live grew to 12. More positions = lower quality = lower win rate.
**Rule**: Hard cap on positions enforced in code, not just prompts.

### Pattern 5: Margin/Leverage Creep
SHORGAN Paper went to -$111K cash without any alert or block.
**Rule**: Margin limits must be enforced in validation code, not just suggested in prompts.

---

## PREVENTION CHECKLIST (Before Each Change)

Before modifying the trading system, verify:

- [ ] Does this change affect position sizing? If yes, test with both paper and live accounts.
- [ ] Does this change affect validation thresholds? If yes, run calibration test.
- [ ] Does this change affect automation scheduling? If yes, verify Railway deployment + local backup.
- [ ] Does this change create a new single point of failure? If yes, add fallback.
- [ ] Does this change use relative paths? If yes, change to absolute.
- [ ] Does this change involve API keys? If yes, use environment variables only.
- [ ] Have I documented this change in BUGS_AND_ENHANCEMENTS.md?
- [ ] Have I updated this LESSONS_LEARNED.md if applicable?

---

## MONTHLY REVIEW ITEMS

1. **Position count**: SHORGAN Paper < 20, SHORGAN Live < 12
2. **Margin exposure**: SHORGAN Paper cash > -$30K
3. **Win rates**: Target DEE > 60%, SHORGAN > 45%
4. **Approval rates**: Target 30-50% (not 0%, not 100%)
5. **Automation uptime**: Railway heartbeat received daily at 9 AM
6. **Performance vs benchmark**: Track alpha monthly

---

*This document is the system's institutional memory. Update it after every incident, every fix, every lesson.*
