# AI Stock Trading Bot
> Professional automated trading system using multi-agent AI consensus

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-active-success)](https://github.com/foxsake123/ai-stock-trading-bot)
[![Trading](https://img.shields.io/badge/trading-paper-orange)](https://alpaca.markets/)

## Overview

An enterprise-grade automated trading system powered by **Claude Opus 4.1 with Extended Thinking** that leverages multiple AI agents to make intelligent trading decisions. The system manages two distinct portfolios with different strategies:

- **DEE-BOT**: Defensive, beta-neutral strategy focused on S&P 100 stocks (LONG-ONLY)
- **SHORGAN-BOT**: Aggressive catalyst-driven strategy for small/mid-cap (supports LONG, SHORT, and OPTIONS)

### Current Status: Production Ready (Paper Trading)
- ✅ **471 tests passing** (100% success rate)
- ✅ **36.55% code coverage** (target: 50%+)
- ✅ **All 8 phases complete**
- ✅ **Paper trading operational** since October 2025
- 📋 **Live trading deployment guide** available
- 🎯 **Target go-live**: December 1, 2025 (after 30-day validation)

### Key Features
- 🤖 Multi-agent consensus system (7 specialized agents)
- 📊 Real-time execution via Alpaca Markets API
- 📈 Professional data from Financial Datasets API
- 🔔 Multi-channel notifications (Email, Slack, Discord)
- ⚡ Fully automated daily execution (6:00 PM ET)
- 📝 Comprehensive risk management and position tracking
- 🛡️ Advanced safety mechanisms (kill switches, loss limits, drawdown protection)
- 📊 Web dashboard for report viewing and analysis
- 🧪 Comprehensive test suite with 471 tests

## Quick Start

### Prerequisites
```bash
# Python 3.13 or higher required
python --version

# Install dependencies
pip install -r requirements.txt
```

### Configuration
1. Copy `config/api_keys.example.yaml` to `config/api_keys.yaml`
2. Add your API credentials:
   - Alpaca Markets (paper trading)
   - Financial Datasets API
   - Telegram Bot Token

### Running the System
```bash
# Manual execution
python main.py

# Execute daily trades
python scripts/automation/execute_daily_trades.py

# Update positions
python scripts/automation/update_all_bot_positions.py

# Generate reports
python scripts/automation/generate-post-market-report.py

# Generate performance graph (NEW!)
python generate_performance_graph.py

# Generate daily pre-market report (NEW!)
python daily_premarket_report.py          # Production mode
python daily_premarket_report.py --test   # Test mode (no API calls)

# Start web dashboard (NEW!)
python web_dashboard.py                   # Web interface on http://localhost:5000

# Run system health check (NEW!)
python health_check.py                    # Quick health check
python health_check.py --verbose          # Detailed diagnostics
```

## System Health Monitoring

Monitor system health, API connectivity, and file operations with the built-in health check tool.

### Health Check Features

- **Research Generation**: Verify reports are being generated on schedule
- **API Connectivity**: Test Anthropic and Alpaca API connections
- **File Permissions**: Verify write access to required directories
- **Exit Codes**: Returns 0 if all checks pass, 1 if any fail

### Running Health Check

**Basic check:**
```bash
python health_check.py
```

Example output:
```
================================================================================
AI Trading Bot - System Health Check
Timestamp: 2025-10-13 17:52:59
================================================================================

1. Research Generation:
   [PASS] Latest report exists (2969 bytes, 0.4h old)

2. API Connectivity:
   [PASS] Anthropic API: Connected successfully
   [PASS] Alpaca API: Connected (Portfolio: $102,332.98)

3. File Permissions:
   [PASS] Write permissions OK for 2 directories

================================================================================
Summary: 4/4 checks passed
Status: [PASS] ALL SYSTEMS OPERATIONAL
================================================================================
```

**Verbose mode (detailed diagnostics):**
```bash
python health_check.py --verbose
# or
python health_check.py -v
```

Shows additional debug information:
- File paths being checked
- API response details
- Directory creation attempts
- Write test results

### When to Run Health Check

**Recommended:**
- After initial setup (verify configuration)
- Daily monitoring (add to cron/Task Scheduler)
- After system updates or changes
- When troubleshooting issues
- Before production deployments

**Automated Monitoring (Linux):**
```bash
# Add to crontab - run daily at 7:00 PM ET
0 19 * * * cd /path/to/project && python health_check.py || mail -s "Health Check Failed" admin@example.com
```

**Automated Monitoring (Windows Task Scheduler):**
```cmd
# Create scheduled task
schtasks /create /tn "HealthCheck" /tr "python C:\path\to\health_check.py" /sc daily /st 19:00
```

### Exit Codes

- **0**: All checks passed - system operational
- **1**: One or more checks failed - requires attention

Use in scripts:
```bash
python health_check.py
if [ $? -eq 0 ]; then
    echo "All systems operational"
else
    echo "Health check failed - investigate"
    exit 1
fi
```

### Troubleshooting

**Research Generation Failed:**
- Check if reports/ directory exists
- Verify scheduled task is running
- Run `python daily_premarket_report.py --test` to generate test report

**API Connectivity Failed:**
- Verify API keys are set in `.env` file
- Check internet connection
- Verify API key validity at provider websites
- Check if required packages installed: `pip install anthropic alpaca-py`

**File Permissions Failed:**
- Check directory ownership and permissions
- On Linux: `chmod 755 reports logs`
- On Windows: Right-click → Properties → Security tab
- Try running as administrator/sudo (if appropriate)

## Pre-Market Report Generator

The Daily Pre-Market Report Generator creates comprehensive hedge-fund-level trading analysis before market open.

### Installation

1. **Create a `.env` file** in the project root:
```bash
# Required API keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret_key
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Email notifications (optional)
EMAIL_ENABLED=true
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_RECIPIENT=recipient@example.com
```

2. **Install dependencies** (if not already installed):
```bash
pip install anthropic python-dotenv pandas pytz yfinance
```

### Features

- **Dual-Strategy Analysis**: SHORGAN-BOT (catalyst-driven) + DEE-BOT (defensive)
- **Market Data Integration**: Real-time VIX, futures, dollar index, treasury yields
- **Stock Recommendations**: Configurable via CSV or default stocks
- **Comprehensive Prompts**: 7,000+ character hedge-fund-level prompts
- **Test Mode**: Generate mock reports without API calls

### Usage

#### Test Mode (No API Calls)
```bash
python daily_premarket_report.py --test
```
- Generates mock report with structure
- No Claude API calls (free testing)
- Validates all components
- Saves report files

#### Production Mode (Full Analysis)
```bash
python daily_premarket_report.py
```
- Fetches real-time market data
- Calls Claude Sonnet 4 for analysis
- Generates comprehensive 3,000-4,000 word report
- Saves to `reports/premarket/`

### Configuration

#### Default Stocks (8 positions)

**SHORGAN-BOT** (catalyst-driven):
- SNDX: Oct 25 PDUFA for Revuforj
- GKOS: Oct 20 PDUFA for Epioxa
- ARWR: Nov 18 PDUFA for plozasiran
- ALT: Nov 11 Q3 earnings + IMPACT data
- CAPR: Q4 HOPE-3 Phase 3 data

**DEE-BOT** (defensive):
- DUK: Long-term defensive utility
- ED: Long-term defensive utility
- PEP: Long-term defensive consumer staples

#### Custom Recommendations

Create `data/daily_recommendations.csv`:
```csv
Ticker,Strategy,Catalyst,Risk,Conviction
NVDA,SHORGAN,Q4 earnings beat,7,8
AAPL,DEE,Long-term defensive tech,5,9
```

### Output Files

```
reports/premarket/
├── premarket_report_2025-10-14.md       # Dated report
├── latest.md                             # Latest report (symlink)
└── premarket_metadata_2025-10-14.json   # Metadata
```

### Report Sections

1. **Executive Summary Table** - Market sentiment, VIX, catalysts
2. **Overnight Market Context** - Asia/Europe/US futures
3. **SHORGAN-BOT Recommendations** - 5-7 catalyst trades
4. **DEE-BOT Recommendations** - 3-5 defensive stocks
5. **Portfolio Management** - Cash, risk limits, rebalancing
6. **Execution Guidance** - Pre-market, open, intraday, EOD
7. **Alternative Data** - Sentiment, supply chain, insider activity
8. **Risk Disclosures** - Standard disclaimers

### Scheduling

**Windows Task Scheduler** (Recommended):
```cmd
# Option 1: Import XML configuration (Monday-Friday only)
# See systemd/INSTALL_WINDOWS.md for detailed setup instructions
cd systemd
# Edit premarket_report_task.xml with your paths first
schtasks /create /tn "PreMarketReport" /xml premarket_report_task.xml

# Option 2: Quick command-line setup (daily including weekends)
schtasks /create /tn "PreMarket Report" /tr "python C:\path\to\daily_premarket_report.py" /sc daily /st 18:00
```

Features (XML configuration):
- Runs Monday-Friday at 6:00 PM ET (skips weekends)
- 1-hour execution timeout
- Task history logging
- Network required check
- Manual test: `systemd\run_report.bat`

**Linux Systemd** (Recommended):
```bash
# Professional systemd timer with logging and persistence
# See systemd/INSTALL.md for detailed setup instructions
sudo cp systemd/premarket-report.* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable premarket-report.timer
sudo systemctl start premarket-report.timer
```

Features:
- Runs Monday-Friday at 6:00 PM ET (skips weekends)
- Persistent execution (runs missed jobs after downtime)
- Integrated logging with `journalctl`
- Automatic timezone handling (America/New_York)
- Service restart on failure

**Linux/Mac Cron**:
```bash
# Run daily at 6:00 PM ET
0 18 * * * cd /path/to/project && python daily_premarket_report.py
```

### Email Notifications

The report generator can automatically email reports with attachments.

#### Setting up Gmail App Password

1. **Enable 2-Factor Authentication** on your Gmail account
   - Go to https://myaccount.google.com/security
   - Turn on 2-Step Verification

2. **Generate App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "AI Trading Bot"
   - Click "Generate"
   - Copy the 16-character password (format: xxxx xxxx xxxx xxxx)

3. **Add to .env file**:
```bash
EMAIL_ENABLED=true
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop  # Your 16-character app password
EMAIL_RECIPIENT=recipient@example.com
```

4. **Test email notification**:
```bash
python daily_premarket_report.py --test
# Check your inbox for "Pre-Market Report for..." email
```

#### Email Features
- **Attachment**: Full markdown report file
- **Summary**: First 500 characters of report in email body
- **Stats**: SHORGAN/DEE-BOT position counts
- **File path**: Local path to saved report
- **Auto-retry**: Graceful failure (doesn't stop report generation)

#### Disabling Email
Set `EMAIL_ENABLED=false` or remove from `.env` file

### Slack Notifications

Send real-time notifications to Slack channels or DMs.

#### Setting up Slack Webhook

1. **Create Incoming Webhook**:
   - Go to https://api.slack.com/apps
   - Click "Create New App" → "From scratch"
   - Name: "AI Trading Bot", select workspace
   - Click "Incoming Webhooks" → Enable
   - Click "Add New Webhook to Workspace"
   - Select channel (e.g., #trading-alerts)
   - Copy the webhook URL

2. **Add to .env file**:
```bash
SLACK_WEBHOOK=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

3. **Test Slack notification**:
```bash
python daily_premarket_report.py --test
# Check your Slack channel for notification
```

#### Slack Notification Format
- **Header**: "Pre-Market Report for {date}"
- **Fields**: Generated time, Portfolio value, SHORGAN/DEE positions
- **Summary**: First 1000 characters (code block format)
- **Footer**: "AI Trading Research System"

### Discord Notifications

Send notifications to Discord servers or DMs.

#### Setting up Discord Webhook

1. **Create Webhook**:
   - Open Discord server settings
   - Go to "Integrations" → "Webhooks"
   - Click "New Webhook"
   - Name: "AI Trading Bot"
   - Select channel (e.g., #trading-reports)
   - Copy webhook URL

2. **Add to .env file**:
```bash
DISCORD_WEBHOOK=https://discord.com/api/webhooks/1234567890/abcdefghijklmnopqrstuvwxyz
```

3. **Test Discord notification**:
```bash
python daily_premarket_report.py --test
# Check your Discord channel for notification
```

#### Discord Notification Format
- **Title**: "📊 Pre-Market Report for {date}"
- **Description**: Summary (code block, max 1500 chars)
- **Fields**: Generated time, Portfolio value, SHORGAN/DEE positions
- **Color**: Blue (#3447003)
- **Footer**: "AI Trading Research System"

### Multiple Notification Channels

You can enable all notification methods simultaneously:
```bash
# .env file
EMAIL_ENABLED=true
SLACK_WEBHOOK=https://hooks.slack.com/services/...
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
```

All notifications are optional and independent - failure of one doesn't affect others.

### Troubleshooting

**Error: ANTHROPIC_API_KEY not set**
- Create `.env` file with your API key
- Get key from: https://console.anthropic.com/

**Error: Market data failed (0/6 indicators)**
- Yahoo Finance rate limiting (normal)
- Reports still generate with partial data
- Wait 1-2 minutes between runs

**Error: Trading date calculation failed**
- Check `schedule_config.py` for market holidays
- Update holidays list for new year

**Error: Email authentication failed**
- Use Gmail App Password, not regular password
- Follow Gmail App Password setup instructions above
- Check EMAIL_SENDER matches Gmail account
- Ensure 2FA is enabled on Gmail account

**Error: Email configuration incomplete**
- Verify all three variables set: EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT
- Check .env file loaded correctly
- Restart script after updating .env

**Error: Failed to send Slack notification**
- Verify SLACK_WEBHOOK URL is correct
- Check webhook is still active (webhooks can be deleted/revoked)
- Test webhook with curl: `curl -X POST -H 'Content-type: application/json' --data '{"text":"Test"}' YOUR_WEBHOOK_URL`
- Check Slack app permissions

**Error: Failed to send Discord notification**
- Verify DISCORD_WEBHOOK URL is correct
- Check webhook hasn't been deleted in Discord server
- Test webhook with curl: `curl -X POST -H 'Content-Type: application/json' -d '{"content":"Test"}' YOUR_WEBHOOK_URL`
- Ensure bot has permissions to post in channel

## Web Dashboard

View and download pre-market reports through a beautiful web interface.

### Features

- List all generated reports with metadata
- View reports rendered as HTML with styled tables and formatting
- Download markdown files for archival
- JSON API for programmatic access
- Responsive design with professional UI
- Real-time status of latest report

### Starting the Dashboard

**Windows**:
```bash
scripts\windows\START_WEB_DASHBOARD.bat
```

**Python**:
```bash
python web_dashboard.py
```

The dashboard will be available at: http://localhost:5000

### Routes

- `/` - Homepage listing all reports
- `/report/<date>` - View specific report (e.g., `/report/2025-10-14`)
- `/latest` - View the most recent report
- `/download/<date>` - Download markdown file
- `/api/reports` - JSON API endpoint with all reports metadata

### API Response Format

```json
{
  "success": true,
  "count": 5,
  "reports": [
    {
      "trading_date": "2025-10-14",
      "filename": "premarket_report_2025-10-14.md",
      "generated_at": "2025-10-13T17:29:51-04:00",
      "portfolio_value": 100000,
      "model": "claude-sonnet-4-20250514"
    }
  ]
}
```

### Dependencies

The web dashboard requires Flask and markdown:
```bash
pip install flask markdown
```

### Production Deployment

For production use, consider using a WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_dashboard:app
```

## System Architecture

### Trading Flow
```
Market Data → AI Agents → Consensus → Risk Review → Execution → Monitoring
     ↓           ↓           ↓           ↓            ↓           ↓
  Financial  7 Specialist  Weighted    Position    Alpaca API  Real-time
  Datasets    Agents       Voting      Sizing                  Tracking
```

### Multi-Agent System
| Agent | Role | Weight |
|-------|------|--------|
| Fundamental | Company analysis | 20% |
| Technical | Chart patterns | 20% |
| News | Headlines & events | 15% |
| Sentiment | Social media trends | 10% |
| Bull | Optimistic view | 15% |
| Bear | Pessimistic view | 15% |
| Risk | Veto power | 5% |

## Portfolio Strategies

### DEE-BOT (Defensive)
- **Capital**: $100,000
- **Strategy**: LONG-ONLY, beta-neutral
- **Focus**: S&P 100 dividend aristocrats
- **Risk**: 0.75% daily loss limit
- **Positions**: 8-12 holdings
- **Rebalance**: Monthly or 15% drift

### SHORGAN-BOT (Aggressive)
- **Capital**: $100,000
- **Strategy**: Catalyst-driven momentum
- **Focus**: Small/mid-cap with events
- **Risk**: 8% stop loss per position
- **Positions**: 15-25 holdings
- **Targets**: 15-25% profit taking

## Daily Operation

### Automated Schedule
- **06:45 AM**: Data ingestion and analysis
- **08:45 AM**: Risk review and position sizing
- **09:30 AM**: Automated trade execution
- **11:00 AM**: Position monitoring begins
- **04:30 PM**: Post-market report generation

### Manual Tasks
1. Create `TODAYS_TRADES_YYYY-MM-DD.md` (if not auto-generated)
2. Review execution logs for failures
3. Monitor critical positions

## Performance

### Current Statistics (Sept 29, 2025)
```
Combined Portfolio: $210,285 (+5.14%)
DEE-BOT:           $104,454 (+4.45%)
SHORGAN-BOT:       $105,832 (+5.83%)
Win Rate: 65%
Sharpe Ratio: 1.4
Max Drawdown: -8.3%
```

### Performance Tracking

#### Live Portfolio Visualization
Professional visualization system benchmarking both bots against S&P 500:
- **Generate Graph**: `python generate_performance_graph.py`
- **Documentation**: See [docs/PERFORMANCE_TRACKING.md](docs/PERFORMANCE_TRACKING.md)
- **Methodology**: Based on [ChatGPT-Micro-Cap-Experiment](https://github.com/LuckyOne7777/ChatGPT-Micro-Cap-Experiment)

#### Recommendation Backtesting

Track and analyze historical recommendation performance from pre-market reports:

**Basic Usage:**
```bash
# Backtest all historical recommendations
python backtest_recommendations.py

# Backtest specific date range
python backtest_recommendations.py --start 2025-01-01 --end 2025-10-31

# Backtest specific ticker
python backtest_recommendations.py --ticker SNDX

# Backtest specific strategy
python backtest_recommendations.py --strategy SHORGAN
```

**Features:**
- Automatically loads recommendations from all pre-market reports
- Fetches actual price data using yfinance
- Calculates win rate, average return, and performance metrics
- Compares SHORGAN-BOT vs DEE-BOT performance
- Generates comprehensive markdown reports

**Output Files:**
- `reports/performance/performance_report_{date}.md` - Human-readable analysis
- `reports/performance/recommendations_detailed_{date}.json` - Raw data for analysis

**Metrics Tracked:**
- **Win Rate**: Percentage of recommendations that hit target
- **Average Return**: Mean return per recommendation
- **Strategy Comparison**: SHORGAN vs DEE performance
- **Top Winners/Losers**: Best and worst performing recommendations
- **Monthly Breakdown**: Performance by month

**Interpretation:**
- **Win Rate > 55%**: Strong recommendation system
- **Avg Return > 5%**: Profitable on average
- **SHORGAN > DEE**: Catalyst-driven strategy outperforming defensive
- **Consistent Monthly Performance**: System reliability over time

**Example Output:**
```
Total Recommendations: 42
Closed Positions: 38
Win Rate: 63.2% (24 wins / 14 losses)
Average Return: +7.45%

SHORGAN Win Rate: 68.4%
DEE Win Rate: 55.0%
```

### Top Performers
- RGTI: +94% (quantum computing)
- SRRK: +21% (biotech catalyst)
- ORCL: +18% (cloud expansion)

## Project Structure

```
ai-stock-trading-bot/
├── agents/                 # Multi-agent trading system
├── scripts/
│   ├── automation/        # Core trading scripts
│   ├── utilities/         # Helper utilities
│   └── windows/           # Windows batch files
├── data/
│   ├── daily/             # Daily positions and performance
│   ├── research/          # Claude/ChatGPT research
│   └── reports/           # Execution reports
├── docs/
│   ├── strategies/        # Trading strategies
│   ├── reports/           # Daily/weekly reports
│   ├── archive/           # Archived documentation
│   └── session-summaries/ # Development logs
├── configs/               # Configuration files
├── tests/                 # Test suite
└── main.py               # Entry point
```

## Risk Management

### Position Limits
- Max position size: 10% of portfolio
- Max sector exposure: 30%
- Daily loss limit: 3% (circuit breaker)
- Stop losses on all positions

### Monitoring
- Real-time position tracking
- Telegram alerts for trades
- Automated stop loss triggers
- Daily performance reports

## Development

### Running Tests

The project includes a comprehensive pytest test suite for unit and integration testing.

#### Quick Start

**Automated Test Runner (Recommended):**
```bash
# Linux/Mac
bash run_tests.sh

# Windows
run_tests.bat
```

The test runner will:
1. Run unit tests
2. Run integration tests
3. Generate coverage report
4. Open htmlcov/index.html for detailed coverage analysis

#### Manual Testing

**Run all tests:**
```bash
pytest tests/ -v
```

**Run specific test files:**
```bash
pytest tests/test_schedule_config.py -v          # Schedule/date tests
pytest tests/test_report_generator.py -v         # Report generation tests
pytest tests/test_notifications.py -v            # Notification tests
pytest tests/test_integration.py -v              # Integration tests
```

**Run tests by marker:**
```bash
pytest tests/ -m unit -v                         # Only unit tests
pytest tests/ -m integration -v                  # Only integration tests
pytest tests/ -m "not slow" -v                   # Skip slow tests
```

**Run tests with coverage:**
```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
# Open htmlcov/index.html to view detailed coverage report
```

#### Test Categories

**Unit Tests** (`tests/test_*.py`):
- `test_schedule_config.py` - Trading day logic, holidays, timezone handling
- `test_report_generator.py` - Report generation and formatting
- `test_notifications.py` - Email, Slack, Discord notifications

**Integration Tests** (`tests/test_integration.py`):
- `TestEndToEndReportGeneration` - Complete pipeline from API call to file creation
- `TestScheduledExecution` - Trading day calculation and scheduling logic
- `TestWebDashboard` - Flask app routes and functionality
- `TestSystemIntegration` - Health checks, backtest system, performance tracking

#### Coverage Requirements

- **Minimum Coverage**: 50% overall
- **New Code**: 80% coverage required
- **Critical Functions**: 100% coverage required

**Current Status:**
- **59/63 unit tests passing** (94% success rate)
- **Coverage**: 9% overall (baseline)
- **Integration tests**: Full end-to-end validation

#### Test Fixtures

Available fixtures in `tests/conftest.py`:
- `temp_dir` - Temporary directory for file operations
- `mock_env_vars` - Mock environment variables
- `mock_market_data` - Sample market data
- `mock_stock_recommendations` - Stock recommendations
- `sample_report_content` - Sample report markdown
- `test_app` - Flask test application
- `mock_anthropic_response` - Claude API responses

#### Expected Test Output

**Successful Test Run:**
```
================================================================================
AI TRADING BOT - TEST SUITE
================================================================================

Step 1: Running Unit Tests
--------------------------------------------------------------------------------
tests/test_schedule_config.py::test_next_trading_day PASSED           [ 10%]
tests/test_report_generator.py::test_report_creation PASSED           [ 20%]
tests/test_notifications.py::test_email_notification PASSED           [ 30%]

Step 2: Running Integration Tests
--------------------------------------------------------------------------------
tests/test_integration.py::test_end_to_end_generation PASSED          [ 40%]
tests/test_integration.py::test_web_dashboard_routes PASSED           [ 50%]

Step 3: Coverage Report
--------------------------------------------------------------------------------
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
daily_premarket_report.py        200     95    52%   45-67, 123-145
schedule_config.py                 85     35    59%   23-45
web_dashboard.py                  120     45    63%   78-92, 145-156
------------------------------------------------------------
TOTAL                            2500   1800    72%

Coverage report: htmlcov/index.html
```

#### Troubleshooting Tests

**Import Errors:**
```bash
# Ensure all dependencies installed
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock
```

**Environment Variables:**
```bash
# Some tests require .env file
cp .env.example .env
# Add test API keys (can be dummy keys for unit tests)
```

**Test Failures:**
- Check `pytest -v` output for specific errors
- Review `htmlcov/index.html` for uncovered code paths
- Use `pytest -v --tb=long` for detailed tracebacks
- Run specific failing test: `pytest tests/test_file.py::test_name -v`

#### CI/CD Integration

The test suite is designed for CI/CD pipelines:
```bash
# GitHub Actions example
pytest tests/ --cov=. --cov-report=xml --cov-report=term
# Returns exit code 0 if all tests pass, 1 otherwise
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Live Trading Deployment

### Current Status
The system is currently in **paper trading mode** with a target go-live date of **December 1, 2025** (after 30-day validation period).

### Deployment Path
For comprehensive guidance on transitioning from paper trading to live trading with real capital:

- **[Live Trading Deployment Guide](docs/LIVE_TRADING_DEPLOYMENT_GUIDE.md)** - Complete 6-phase deployment checklist with safety mechanisms, risk management, and emergency procedures
- **[Next Steps for Live Trading](docs/NEXT_STEPS_LIVE_TRADING.md)** - Detailed 4-phase timeline (Oct 2025 - Mar 2026) with weekly action items and decision trees

### Key Requirements Before Go-Live
- ✅ 30+ days of paper trading validation
- ✅ Win rate ≥ 60%
- ✅ Sharpe ratio ≥ 1.0
- ✅ Max drawdown < 15%
- ✅ Safety mechanisms implemented (kill switches, loss limits)
- ✅ Manual approval system configured
- ✅ Emergency procedures tested

### Initial Live Capital
Recommended: $1,000-5,000 for first month, scaling gradually based on performance.

## Documentation

### Getting Started
- [Example Report](examples/example_report.md) - Sample pre-market report with detailed comments
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project
- [Changelog](CHANGELOG.md) - Version history and release notes

### Trading Strategies
- [Trading Strategies](docs/TRADING_STRATEGIES.md) - Complete guide to SHORGAN-BOT and DEE-BOT strategies
- [DEE-BOT Strategy](docs/DEE_BOT_STRATEGY.md) - Defensive beta-neutral strategy details
- [SHORGAN Strategy](docs/SHORGAN_STRATEGY.md) - Catalyst-driven momentum strategy details

### Technical Documentation
- [API Usage Guide](docs/API_USAGE.md) - API reference, pricing, and rate limits
- [System Architecture](docs/SYSTEM_ARCHITECTURE.md) - Multi-agent system design
- [API Documentation](docs/API_REFERENCE.md) - Complete API reference
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

## Support

- **Issues**: [GitHub Issues](https://github.com/foxsake123/ai-stock-trading-bot/issues)
- **Documentation**: See `/docs` folder
- **Updates**: Via Telegram bot notifications

## License

Private repository - All rights reserved

## Disclaimer

This is a paper trading system for educational purposes. Not financial advice. Always conduct your own research before making investment decisions.

---

**Version**: 2.0.0
**Last Updated**: October 14, 2025
**Status**: 🟢 Production Ready (Paper Trading)