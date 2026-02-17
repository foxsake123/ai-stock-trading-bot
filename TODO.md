# AI Stock Trading Bot - TODO List

Last Updated: 2026-02-04

## 🔴 CRITICAL - High Priority

### System Health & Reliability
- [ ] Fix Task Scheduler wake-from-sleep issues (currently requires PC to stay on)
  - Current workaround: Keep computer on during trading hours
  - Investigate Windows Task Scheduler permission issues
  - Consider alternative: Cloud hosting (AWS/GCP/Azure)

- [x] Implement multi-agent validation calibration (calibrated, approval working)
  - Threshold lowered to 0.55, approval rate now functional
  - SHORGAN Live: 6/6 approved (Feb 12, 2026)
  - DEE-BOT: 2/2 approved, SHORGAN Paper: 4/8 approved

### Security
- [x] Rotate API keys (completed after Oct 29 exposure)
- [ ] Implement API key rotation automation (quarterly)
- [ ] Add pre-commit hook for secret detection (partially done)
- [ ] Audit all .env files for exposed credentials
- [ ] Review git history for additional exposed secrets

## 🟡 HIGH PRIORITY - Important Improvements

### Trading System Enhancements
- [ ] Complete refactoring of `claude_research_generator.py` (4,847 lines - too large)
  - Split into multiple focused modules
  - Improve maintainability

- [ ] Add unit tests for core utilities
  - `scripts/core/retry_utils.py` (304 lines - needs tests)
  - `scripts/core/order_verification.py` (346 lines - needs tests)
  - `scripts/core/health_monitor.py` (447 lines - needs tests)

- [ ] Implement stop-loss automation improvements
  - Current: Manual stop losses after fills
  - Target: Automatic trailing stop losses
  - Add dynamic stop loss adjustment based on volatility

### Data & Performance
- [ ] Backfill performance data gap (Oct 22 - Nov 10)
  - Missing ~15 trading days
  - Affects historical analysis

- [ ] Improve backtest framework
  - Current performance: -0.32% return, -0.58 Sharpe
  - Target: +3.34% return with improvements
  - Add more sophisticated metrics

- [ ] Optimize ML outcome automation
  - `scripts/automation/auto_update_outcomes.py` deployed but needs monitoring
  - Verify accuracy of Alpaca P&L extraction
  - Add model retraining pipeline

## 🟢 MEDIUM PRIORITY - Nice to Have

### Documentation
- [ ] Create API documentation for all MCP tools
  - 7 financial data tools integrated
  - Need comprehensive usage guide

- [ ] Add architecture diagrams
  - System flow diagram
  - Data pipeline visualization
  - Multi-agent validation flow

- [ ] Create troubleshooting guide
  - Common issues and resolutions
  - Task Scheduler debugging
  - API rate limit handling

### Code Quality
- [ ] Fix 11 test collection errors (import issues)
  - Standardize all imports to `src/` pattern
  - Fix 7 class name imports (missing Agent suffix)
  - Archive 6 obsolete test files

- [ ] Improve test coverage (currently 36.55%)
  - Target: 80%+ coverage
  - Focus on critical trading logic
  - Add integration tests

- [ ] Add type hints throughout codebase
  - Many functions lack type annotations
  - Would improve IDE support and catch errors earlier

### Features
- [ ] Options trading parser for SHORGAN-LIVE
  - Currently basic stock trading only
  - Add support for call/put spread parsing

- [ ] Profit-taking manager automation
  - Script exists but needs Task Scheduler integration
  - Define profit-taking rules (e.g., take 50% at +20%)

- [ ] Database integration for historical data
  - Currently using JSON files
  - Consider PostgreSQL or TimescaleDB
  - Would enable better analytics

### Monitoring & Alerts
- [ ] Create automation health monitoring dashboard
  - Visualize task success/failure rates
  - Track approval rates over time
  - Monitor API quota usage

- [ ] Implement advanced alerting
  - Circuit breaker triggers
  - Unusual trading volume
  - Large drawdowns

## 🔵 LOW PRIORITY - Future Enhancements

### Research & Analysis
- [ ] Test comprehensive valuation multiples tool
  - P/E, P/B, EV/EBITDA integration added
  - Needs production testing with real trades

- [ ] Enhance catalyst validation
  - Verify Polymarket predictions accuracy
  - Track hit rate of catalyst-driven trades

- [ ] Add sentiment analysis integration
  - Reddit, Twitter, news sentiment
  - Correlation with trade performance

### Infrastructure
- [ ] Set up CI/CD pipeline
  - Automated testing on commits
  - Deployment automation

- [ ] Implement distributed caching (Redis)
  - Currently using local node-cache
  - Would support multiple instances

- [ ] Create Docker containerization
  - Easier deployment
  - Consistent environment

### User Experience
- [ ] Build web dashboard for monitoring
  - Real-time portfolio view
  - Trade history and performance
  - Research report viewer

- [ ] Mobile app for alerts
  - Push notifications for critical events
  - Quick approve/reject trades

- [ ] Voice assistant integration
  - "Alexa, what's my portfolio performance today?"

## ✅ COMPLETED (Last 30 Days)

### February 2026
- [x] Fix ORDER BLOCK parser regex bug (report_parser.py line 83)
  - Bold markdown `**ORDER BLOCKS:**` not matched by regex
  - Caused intermittent 0-trade days for SHORGAN Live
- [x] Implement per-account circuit breakers (retry_utils.py)
  - Paper failures no longer cascade to block Live execution
  - Separate breakers: alpaca_dee_circuit, alpaca_shorgan_paper_circuit, alpaca_shorgan_live_circuit
- [x] Smart circuit breaker error classification
  - Only real API/network errors trip the breaker (timeouts, DNS, 5xx)
  - Business logic errors (insufficient qty, conflicting orders) no longer count
- [x] Execute Feb 12 trades manually after automation failure
  - DEE-BOT: SELL MA, BUY PFE
  - SHORGAN Paper: SELL AMZN, BUY CRM
  - SHORGAN Live: SELL MARA/PLUG, BUY SNAP/HIMS (with stop losses)

### January 2026
- [x] Add comprehensive system improvements (retry logic, health monitoring, order verification)
- [x] Create centralized trading configuration module
- [x] Integrate ML data collection infrastructure
- [x] Add keep-awake system to prevent automation failures
- [x] Fix position limit validation bug for SHORGAN Live
- [x] Add security pre-commit hook for secret detection

### December 2025
- [x] Fix 0% approval rate (validation system debugging)
- [x] Execute manual trades (13/15 success rate)
- [x] Implement deposit-adjusted performance tracking
- [x] Add S&P 500 benchmark to performance graph
- [x] Fix Telegram notification delivery for performance graph
- [x] Enhance multi-agent parser for comprehensive research format

### November 2025
- [x] Launch SHORGAN-BOT Live trading ($1K account)
- [x] Configure Task Scheduler for all 4 automation tasks
- [x] Generate first weekend research with MCP tools
- [x] Add trade summary tables to all research reports
- [x] Upgrade SHORGAN-BOT Live to $3K capital with options trading
- [x] Integrate valuation multiples tool (Financial Datasets MCP)

### October 2025
- [x] Complete repository cleanup (2,583 lines removed, 5.3MB freed)
- [x] Fix hardcoded API keys security issue
- [x] Implement multi-agent validation system
- [x] Create comprehensive system assessment and documentation
- [x] Execute first live trades with stop losses
- [x] Set up automated weekend research generation (Saturday 12 PM)

## 📊 METRICS TO TRACK

### System Health
- Task success rate: Target >95%
- API uptime: Target >99.5%
- Approval rate: Target 30-50%
- Win rate on approved trades: Track over time

### Performance
- Combined portfolio return vs S&P 500
- Sharpe ratio: Target >1.5
- Max drawdown: Monitor <15%
- Average profit per trade

### Development
- Test coverage: Current 36.55%, Target 80%
- Code quality score: Monitor with linters
- Documentation completeness: Target 100% of public APIs

## 📝 NOTES

### Architecture Decisions
- Multi-agent validation provides quality filter but needs calibration
- MCP tools provide real-time market data (resolved 101% price error issue)
- Deposit-adjusted returns show true trading skill vs capital injections

### Known Limitations
- Task Scheduler wake-from-sleep unreliable (use workaround: keep PC on)
- SHORGAN-BOT Paper sometimes hits 15-turn API limit (increased from 10)
- Missing performance data: Oct 22 - Nov 10 (accepting gap)
- GitHub Actions execution can run late and hit DNS issues (Feb 12 incident)
- SHORGAN Paper has stale position data (OXY/BAC showing in trades with 0 shares in account)

### System Requirements
- Windows PC must be on during trading hours (Mon-Fri 8:00 AM - 5:00 PM)
- Requires stable internet connection
- API keys: Anthropic, Alpaca, Financial Datasets, Telegram
- Recommended: 16GB RAM, SSD storage
