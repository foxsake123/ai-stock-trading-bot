# Changelog

All notable changes to the AI Stock Trading Bot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Comprehensive repository review and scoring system (REPOSITORY_REVIEW.md)
- Standardized dependency management (requirements.txt, requirements-dev.txt)
- Test configuration with pytest.ini
- Contributing guidelines (CONTRIBUTING.md)
- This changelog

### Security
- Removed hardcoded API keys from execute_daily_trades.py
- Implemented environment variable-based credential management
- Updated .gitignore to prevent credential commits

### Changed
- Migrated to environment variables for all API credentials
- Improved .gitignore with security patterns

### Removed
- 66MB+ chrome_profile/ directory (browser cache data)
- 35+ legacy Python files (~8,000 lines of dead code)
  - agents/core/legacy/ (12 files)
  - agents/execution/legacy/ (1 file)
  - scripts-and-data/automation/legacy/ (18 files)
  - utils/tests-legacy/ (1 file)
- 9 test JSON files (fd_test_*.json)

---

## [1.0.0] - 2025-09-30

### Added
- **Performance Tracking System**
  - Indexed performance visualization (based on ChatGPT-Micro-Cap-Experiment methodology)
  - CSV-based portfolio history tracking
  - S&P 500 benchmark comparison (when available)
  - Professional matplotlib graphs with 300 DPI output
  - Alpha calculation vs market

- **Automated Weekly Research**
  - ChatGPT deep research report generation
  - Telegram delivery of weekly insights
  - HTML and Markdown report formats

- **Post-Market Reporting**
  - Live Alpaca API integration for real-time data
  - Today's P/L tracking (intraday performance)
  - Individual holdings breakdown
  - Combined portfolio summary
  - Automated 4:30 PM ET daily reports

### Fixed
- DEE-BOT margin crisis (September 30)
  - Covered prohibited NVDA short position
  - Raised $48K cash through strategic sells
  - Restored full compliance (long-only)

- Trade execution parser
  - Fixed SHORGAN sell order parsing
  - Improved emoji-tolerant regex patterns
  - Enhanced error handling

- Unicode encoding issues
  - Replaced emojis with ASCII for Windows compatibility
  - Fixed cp1252 codec errors in multiple scripts

### Changed
- Migrated to Financial Datasets API as primary data source
- Enhanced backtesting with professional metrics
- Improved multi-agent consensus system
- Updated automation pipeline for Tuesday execution

### Performance
- Combined Portfolio: +5.06% ($10,129.29 profit)
- DEE-BOT: +4.13% (defensive strategy)
- SHORGAN-BOT: +6.00% (catalyst strategy)

---

## [0.9.0] - 2025-09-23

### Added
- Financial Datasets API integration
  - Real-time price data
  - Financial statements (income, balance sheet, cash flow)
  - Insider trading activity
  - Institutional ownership tracking
  - News sentiment analysis

- Enhanced bot signal generation
  - DEE-BOT: Quality scoring (ROE, debt ratios, dividend safety)
  - SHORGAN-BOT: Catalyst scoring (earnings, momentum, insider activity)

### Fixed
- **CRITICAL**: Automated trade execution system
  - Previously, daily trades were not being executed
  - Added complete execution pipeline
  - Windows Task Scheduler integration
  - 67% execution success rate achieved

### Changed
- Upgraded from yfinance to Financial Datasets API
- Enhanced research pipeline with institutional data
- Improved fundamental analysis capabilities

---

## [0.8.0] - 2025-09-18

### Added
- Dual-bot architecture
  - DEE-BOT: Beta-neutral S&P 100 strategy
  - SHORGAN-BOT: Catalyst event trading

- 7-agent consensus system
  - Fundamental Analyst (20% weight)
  - Technical Analyst (20% weight)
  - News Analyst (15% weight)
  - Sentiment Analyst (10% weight)
  - Bull Agent (15% weight)
  - Bear Agent (15% weight)
  - Risk Manager (5% weight, veto power)

- Automation pipeline
  - Daily pre-market research
  - Automated trade execution (9:30 AM ET)
  - Post-market reporting (4:30 PM ET)
  - Weekly deep research (Sunday evenings)

### Changed
- Reorganized repository structure
- Consolidated automation scripts
- Improved documentation

---

## [0.7.0] - 2025-09-11

### Added
- Multi-agent trading system foundation
- Alpaca Markets integration (paper trading)
- Basic backtesting framework
- Position tracking and reporting

### Changed
- Initial repository setup
- Basic README and documentation

---

## Migration Notes

### Upgrading from 0.9.0 to 1.0.0
1. Update your .env file with new API keys (rotate if exposed)
2. Install new dependencies: `pip install -r requirements.txt`
3. Run: `python generate_performance_graph.py` to create visualizations
4. Review REPOSITORY_REVIEW.md for security recommendations

### Breaking Changes
None in this release. The API remains backwards compatible.

---

## Upcoming Features (Roadmap)

### Version 1.1.0 (Planned)
- [ ] CSV export for post-market reports
- [ ] Real-time risk monitoring dashboard
- [ ] Comprehensive backtesting with Sharpe/Sortino ratios
- [ ] Type hints throughout codebase
- [ ] CI/CD pipeline with GitHub Actions

### Version 1.2.0 (Planned)
- [ ] ML-enhanced signal generation
- [ ] Portfolio optimization engine
- [ ] Advanced order types (stop-loss, take-profit)
- [ ] Live trading mode (with safeguards)

### Version 2.0.0 (Future)
- [ ] Web dashboard
- [ ] Multi-broker support
- [ ] Options trading strategies
- [ ] Alternative data integrations

---

## Contributors

Thanks to all contributors who have helped make this project better!

- [@foxsake123](https://github.com/foxsake123) - Project Lead & Primary Developer

---

## Questions or Feedback?

- **Issues**: https://github.com/foxsake123/ai-stock-trading-bot/issues
- **Discussions**: https://github.com/foxsake123/ai-stock-trading-bot/discussions
- **Documentation**: See the `docs/` folder

---

*This changelog follows [Keep a Changelog](https://keepachangelog.com/) format.*
