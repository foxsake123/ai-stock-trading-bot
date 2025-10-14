# Changelog

All notable changes to the AI Stock Trading Bot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-10-13

### Added - Pre-Market Report System

#### Daily Pre-Market Report Generator
- **New System**: Comprehensive hedge-fund-level pre-market analysis
- **Report Generation**: Claude Sonnet 4 generates 3,000-4,000 word reports
- **Scheduling**: Automated 6:00 PM ET daily generation (Monday-Friday)
- **Market Data**: Real-time VIX, futures, treasuries, dollar index
- **Dual Strategy**: SHORGAN-BOT (catalyst-driven) + DEE-BOT (defensive) analysis
- **Test Mode**: Generate mock reports without API calls (`--test` flag)
- **Output Files**: Markdown reports + JSON metadata

#### Notification System
- **Email Notifications**: Gmail SMTP with attachments and summary
- **Slack Integration**: Webhook notifications with rich formatting
- **Discord Integration**: Embed notifications with styled cards
- **Multi-Channel**: All three channels supported simultaneously
- **Failure Tolerance**: Continues if one notification channel fails

#### Web Dashboard
- **Report Viewer**: Beautiful HTML interface on http://localhost:5000
- **Report List**: View all generated reports with metadata
- **Markdown Rendering**: GitHub-style markdown with syntax highlighting
- **Download Feature**: Download original markdown files
- **JSON API**: `/api/reports` endpoint for programmatic access
- **Responsive Design**: Mobile-friendly interface

#### Scheduling & Automation
- **Linux Systemd**: Professional timer/service configuration with persistence
- **Windows Task Scheduler**: XML task definition with wake-on-timer
- **Automated Execution**: Runs Monday-Friday at 6:00 PM ET
- **Holiday Awareness**: Automatically skips weekends and market holidays
- **Error Handling**: Graceful failure with logging

#### Health Monitoring
- **Health Check Script**: Comprehensive system diagnostics
- **API Connectivity**: Tests Anthropic and Alpaca APIs
- **File Permissions**: Verifies write access to critical directories
- **Report Validation**: Checks latest report generation
- **Verbose Mode**: Detailed debugging with `--verbose` flag
- **Exit Codes**: 0 = pass, 1 = fail (CI/CD friendly)

#### Testing Infrastructure
- **Pytest Suite**: 63 comprehensive unit tests
- **Test Coverage**: 59/63 tests passing (94% success rate)
- **Code Coverage**: 9% overall (daily_premarket_report.py: 52%, schedule_config.py: 59%)
- **Fixtures**: Mock environment, market data, API responses
- **Test Files**: conftest.py, test_schedule_config.py, test_report_generator.py, test_notifications.py
- **Configuration**: pytest.ini with coverage thresholds and markers

#### Documentation
- **Example Report**: Comprehensive example showing all sections (examples/example_report.md)
- **Trading Strategies**: 90-page guide covering SHORGAN-BOT and DEE-BOT strategies (docs/TRADING_STRATEGIES.md)
- **API Usage Guide**: Complete API reference with costs and rate limits (docs/API_USAGE.md)
- **README Updates**: Enhanced with test statistics and new features
- **CHANGELOG**: This file for version tracking
- **CONTRIBUTING**: Guide for contributors (see CONTRIBUTING.md)

### Changed

#### Schedule Configuration
- **Trading Day Calculation**: Enhanced `get_next_trading_day()` function
- **Holiday Detection**: 2025 market holidays list (NYSE/NASDAQ)
- **Timezone Handling**: Proper US/Eastern (ET) timezone support with pytz
- **Market Hours**: Respects 9:30 AM - 4:00 PM ET trading window

#### Performance Tracking
- **Indexed Charts**: All strategies start at $100 for easy comparison
- **S&P 500 Benchmark**: Alpha calculation vs market (outperformance tracking)
- **CSV Tracking**: Automated portfolio value updates
- **Graph Generation**: 300 DPI performance visualizations

#### Repository Structure
- **Root Cleanup**: Reduced from 75 → 22 files (71% reduction)
- **Organization**: Created docs/, examples/, tests/, scripts/windows/
- **Archive System**: Old documentation moved to docs/archive/
- **Batch Files**: Organized into scripts/windows/ directory

### Fixed

#### Health Check System
- **Unicode Error**: Replaced ✓/✗ with [PASS]/[FAIL] for Windows compatibility
- **API Testing**: Properly tests Anthropic and Alpaca connectivity
- **File Checks**: Validates write permissions for reports/ and logs/
- **Error Handling**: Graceful degradation if API keys missing

#### Test Suite
- **Import Errors**: Fixed Anthropic module patching in tests
- **Mock Data**: Corrected market_data fixture structure
- **Type Issues**: Fixed date vs datetime object inconsistencies
- **Time Handling**: Adjusted test times to after market close (5:00 PM ET)
- **Coverage Config**: Added correct source paths to pytest.ini

---

## [1.0.0] - 2025-09-29

### Added - Initial Release

#### Core Trading System
- **Multi-Agent Architecture**: 7 specialized AI agents with weighted consensus
  - Fundamental Analyst (20% weight)
  - Technical Analyst (20% weight)
  - News Analyst (15% weight)
  - Sentiment Analyst (10% weight)
  - Bull Researcher (15% weight)
  - Bear Researcher (15% weight)
  - Risk Manager (5% weight + veto power)

#### Dual-Bot Strategy
- **SHORGAN-BOT**: Aggressive catalyst-driven trading
  - Capital: $100,000
  - Strategy: 2-8 week momentum trades
  - Focus: Small/mid-cap with binary events (FDA, earnings, M&A)
  - Stop-loss: 15-20% per position
  - Target: 20-40% gains per trade

- **DEE-BOT**: Defensive beta-neutral portfolio
  - Capital: $100,000
  - Strategy: LONG-ONLY S&P 100 dividend aristocrats
  - Focus: Utilities, consumer staples, healthcare
  - Target Beta: 0.40-0.60
  - Target Return: 8-12% + dividends

#### Execution & Monitoring
- **Alpaca Integration**: Paper trading via Alpaca Markets API
- **Automated Execution**: Daily trade execution at 9:30 AM ET
- **Position Tracking**: Real-time portfolio monitoring
- **Stop-Loss Orders**: Automatic GTC stop placement
- **Telegram Notifications**: Real-time trade alerts

#### Data Sources
- **Financial Datasets API**: Professional market data ($49/month)
  - Real-time prices and quotes
  - Financial statements (income, balance, cash flow)
  - Insider trading data (Form 4 filings)
  - Institutional ownership (13F filings)
  - News with sentiment analysis

- **Yahoo Finance (yfinance)**: Backup data source (free)
  - Market indices (S&P 500, VIX, futures)
  - Historical price data
  - Basic fundamentals

#### Performance Tracking
- **CSV Tracking**: Daily portfolio snapshots
- **Performance Graphs**: Professional visualization
- **Benchmarking**: Comparison vs S&P 500
- **Alpha Calculation**: Outperformance measurement

#### Reporting System
- **Post-Market Reports**: Daily 4:30 PM ET reports
- **Position Updates**: Morning 9:30 AM updates
- **Weekly Reports**: Friday performance summaries
- **Trade Planning**: Next week strategy

#### Risk Management
- **Position Limits**: Max 10% per position (SHORGAN), 35% (DEE)
- **Sector Limits**: Max 30% sector concentration
- **Daily Loss Limit**: 3% circuit breaker
- **Stop-Loss**: Required on all SHORGAN positions
- **Beta Control**: DEE portfolio maintains 0.40-0.60 beta

#### Documentation
- **README**: Comprehensive project documentation
- **Architecture Docs**: System design and agent descriptions
- **Strategy Docs**: Trading strategy explanations
- **Session Summaries**: Development logs and decisions

### Repository Features
- **Git Tracking**: Professional commit history
- **Branch Strategy**: Main/master branch for stable code
- **Environment Config**: .env file for API keys
- **Dependencies**: requirements.txt with pinned versions

### Performance (Initial)
- **Combined Portfolio**: $210,285 (+5.14% return)
- **DEE-BOT**: $104,454 (+4.45% return)
- **SHORGAN-BOT**: $105,832 (+5.83% return)
- **Win Rate**: 65%
- **Sharpe Ratio**: 1.4
- **Max Drawdown**: -8.3%

---

## [Unreleased]

### Planned Features

#### Testing Expansion
- [ ] Increase test coverage to 50%+ (currently 9%)
- [ ] Add integration tests for live API calls
- [ ] Add agent-specific test suites
- [ ] Performance/load testing
- [ ] Backtesting validation tests

#### Backtesting System
- [ ] Historical performance analysis
- [ ] Strategy parameter optimization
- [ ] Walk-forward testing
- [ ] Monte Carlo simulations
- [ ] Risk metric calculations (Sharpe, Sortino, Calmar)

#### Real-Time Dashboard
- [ ] Live position monitoring
- [ ] Real-time P&L updates
- [ ] Risk metrics dashboard
- [ ] Alert system for stop-loss triggers
- [ ] Trade execution history

#### Machine Learning Integration
- [ ] Pattern recognition for technical analysis
- [ ] Sentiment analysis on news/social media
- [ ] Reinforcement learning for position sizing
- [ ] Anomaly detection for risk management

#### Enhanced Reporting
- [ ] PDF report generation
- [ ] Interactive charts (Plotly/D3.js)
- [ ] Trade attribution analysis
- [ ] Sector rotation analysis
- [ ] Correlation heatmaps

#### Mobile Support
- [ ] Mobile-responsive web dashboard
- [ ] Native mobile app (iOS/Android)
- [ ] Push notifications
- [ ] Mobile trade approval

#### Data Enhancements
- [ ] Alternative data sources (satellite imagery, credit card data)
- [ ] Options flow analysis
- [ ] Dark pool trading data
- [ ] Earnings call transcripts
- [ ] SEC filing analysis (10-K, 10-Q, 8-K)

#### Compliance & Auditing
- [ ] Trade audit log
- [ ] Compliance rule engine
- [ ] Tax loss harvesting automation
- [ ] Regulatory reporting (1099 forms)
- [ ] Wash sale detection

---

## Version History Summary

| Version | Release Date | Major Features | Status |
|---------|--------------|----------------|--------|
| **2.0.0** | 2025-10-13 | Pre-market reports, notifications, web dashboard, tests | Current |
| **1.0.0** | 2025-09-29 | Multi-agent trading, dual-bot strategy, execution | Stable |

---

## Upgrade Guide

### Upgrading from 1.0.0 to 2.0.0

**1. Install New Dependencies:**
```bash
pip install -r requirements.txt
# New packages: flask, markdown, pytest, pytest-mock, pytest-cov
```

**2. Update Environment Variables:**
```bash
# Add to .env file (all optional):
EMAIL_ENABLED=true
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_RECIPIENT=recipient@example.com
SLACK_WEBHOOK=https://hooks.slack.com/services/...
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
```

**3. Test New Features:**
```bash
# Generate test report
python daily_premarket_report.py --test

# Start web dashboard
python web_dashboard.py

# Run health check
python health_check.py --verbose

# Run test suite
pytest tests/ -v
```

**4. Set Up Scheduling (Optional):**
```bash
# Linux (systemd)
sudo cp systemd/premarket-report.* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable premarket-report.timer
sudo systemctl start premarket-report.timer

# Windows (Task Scheduler)
schtasks /create /tn "PreMarketReport" /xml systemd/premarket_report_task.xml
```

**5. Verify Installation:**
```bash
# Check Python version
python --version  # Should be 3.13+

# Verify all tests pass
pytest tests/ -v

# Check health status
python health_check.py
```

**Breaking Changes:**
- None (fully backward compatible)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Reporting bugs
- Requesting features
- Submitting pull requests
- Code style guidelines
- Development workflow

---

## Support

- **Issues**: [GitHub Issues](https://github.com/foxsake123/ai-stock-trading-bot/issues)
- **Documentation**: See `/docs` folder
- **Updates**: Check this CHANGELOG for latest changes

---

*For detailed information about any version, see the corresponding git tag or release notes.*
