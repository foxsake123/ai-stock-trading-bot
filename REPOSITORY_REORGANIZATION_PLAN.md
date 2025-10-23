# AI Trading Bot - Repository Reorganization Plan
**Date:** October 23, 2025
**Version:** 2.0

---

## 📋 Executive Summary

This document proposes a complete reorganization of the AI trading bot repository to improve:
- **Scalability** - Clear separation of concerns
- **Maintainability** - Logical grouping of related components
- **Clarity** - Obvious purpose for every directory
- **Workflow** - Streamlined daily operations and development

**Current Issues Identified:**
1. Redundant directories (`data/`, `data_sources/`, `scripts-and-data/`)
2. Scattered configuration files (root level clutter)
3. Mixed concerns (agents in multiple locations)
4. Duplicate session tracking (`docs/sessions/`, `session-summaries/`)
5. Unclear data flow (reports in multiple locations)

---

## 🎯 Proposed Directory Structure

```
ai-stock-trading-bot/
│
├── README.md                    # Main documentation
├── CHANGELOG.md                 # Version history
├── LICENSE
├── setup.py                     # Package installation
├── pyproject.toml               # Modern Python project config
│
├── config/                      # ⚙️ All configuration files
│   ├── __init__.py
│   ├── settings.py              # Central settings loader
│   ├── api_keys.yaml            # API credentials (gitignored)
│   ├── api_keys.example.yaml   # Template for users
│   ├── schedule.yaml            # Automation schedule
│   ├── trading.yaml             # Trading parameters
│   ├── risk_limits.yaml         # Risk management rules
│   ├── notifications.yaml       # Telegram, email, Slack config
│   └── bots/
│       ├── dee_bot.yaml         # DEE-BOT specific config
│       └── shorgan_bot.yaml     # SHORGAN-BOT specific config
│
├── src/                         # 🧠 Core application code
│   ├── __init__.py
│   │
│   ├── agents/                  # AI decision-making agents
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── fundamental_analyst.py
│   │   ├── technical_analyst.py
│   │   ├── news_analyst.py
│   │   ├── sentiment_analyst.py
│   │   ├── risk_manager.py
│   │   ├── bull_researcher.py
│   │   ├── bear_researcher.py
│   │   ├── alternative_data_agent.py
│   │   ├── shorgan_catalyst_agent.py
│   │   ├── options_strategy_agent.py
│   │   ├── debate_system.py
│   │   └── communication/
│   │       ├── __init__.py
│   │       ├── coordinator.py
│   │       ├── message_bus.py
│   │       └── protocols.py
│   │
│   ├── strategies/              # 📊 Trading strategies
│   │   ├── __init__.py
│   │   ├── base_strategy.py
│   │   ├── dee_bot/
│   │   │   ├── __init__.py
│   │   │   ├── strategy.py      # Beta-neutral strategy logic
│   │   │   ├── executor.py      # Trade execution
│   │   │   ├── monitor.py       # Position monitoring
│   │   │   └── config.py        # Strategy-specific config
│   │   └── shorgan_bot/
│   │       ├── __init__.py
│   │       ├── strategy.py      # Catalyst-driven strategy
│   │       ├── executor.py
│   │       ├── monitor.py
│   │       └── config.py
│   │
│   ├── data/                    # 📥 Data acquisition & processing
│   │   ├── __init__.py
│   │   ├── sources/
│   │   │   ├── __init__.py
│   │   │   ├── alpaca.py        # Alpaca API client
│   │   │   ├── financial_datasets.py
│   │   │   ├── sec_filings.py
│   │   │   ├── google_trends.py
│   │   │   └── reddit_sentiment.py
│   │   ├── loaders/
│   │   │   ├── __init__.py
│   │   │   ├── market_data.py
│   │   │   ├── fundamental_data.py
│   │   │   └── alternative_data.py
│   │   ├── processors/
│   │   │   ├── __init__.py
│   │   │   ├── cleaners.py
│   │   │   ├── normalizers.py
│   │   │   └── validators.py
│   │   └── aggregator.py        # Alternative data aggregation
│   │
│   ├── signals/                 # 📡 Signal generation
│   │   ├── __init__.py
│   │   ├── generators/
│   │   │   ├── __init__.py
│   │   │   ├── technical.py
│   │   │   ├── fundamental.py
│   │   │   ├── sentiment.py
│   │   │   └── composite.py
│   │   └── combiners.py
│   │
│   ├── execution/               # 💼 Trade execution
│   │   ├── __init__.py
│   │   ├── order_manager.py
│   │   ├── position_tracker.py
│   │   ├── risk_validator.py
│   │   └── fill_handler.py
│   │
│   ├── risk/                    # 🛡️ Risk management
│   │   ├── __init__.py
│   │   ├── portfolio_risk.py
│   │   ├── position_sizing.py
│   │   ├── kelly_criterion.py
│   │   ├── stop_loss_manager.py
│   │   └── drawdown_monitor.py
│   │
│   ├── reports/                 # 📄 Report generation
│   │   ├── __init__.py
│   │   ├── generators/
│   │   │   ├── __init__.py
│   │   │   ├── premarket.py
│   │   │   ├── postmarket.py
│   │   │   ├── morning_summary.py
│   │   │   └── performance.py
│   │   ├── formatters/
│   │   │   ├── __init__.py
│   │   │   ├── markdown.py
│   │   │   ├── pdf.py
│   │   │   └── telegram.py
│   │   └── templates/
│   │       └── report_template.md
│   │
│   ├── notifications/           # 🔔 Alert system
│   │   ├── __init__.py
│   │   ├── telegram.py
│   │   ├── email.py
│   │   ├── slack.py
│   │   └── discord.py
│   │
│   ├── monitoring/              # 📊 System health monitoring
│   │   ├── __init__.py
│   │   ├── health_check.py
│   │   ├── pipeline_monitor.py
│   │   └── performance_tracker.py
│   │
│   ├── integration/             # 🔗 Phase 2 enhancements
│   │   ├── __init__.py
│   │   ├── phase2_integration.py
│   │   └── phase2_config.py
│   │
│   └── utils/                   # 🔧 Utilities
│       ├── __init__.py
│       ├── logging.py
│       ├── datetime_helpers.py
│       ├── file_io.py
│       └── validators.py
│
├── scripts/                     # 🚀 Executable scripts
│   ├── automation/
│   │   ├── daily_research.py
│   │   ├── generate_trades.py
│   │   ├── execute_trades.py
│   │   ├── send_morning_report.py
│   │   ├── send_enhanced_morning_report.py
│   │   ├── send_research_pdfs.py
│   │   └── generate_postmarket_report.py
│   │
│   ├── portfolio/
│   │   ├── get_status.py
│   │   ├── rebalance.py
│   │   └── update_positions.py
│   │
│   ├── monitoring/
│   │   ├── health_check.py
│   │   └── pipeline_health.py
│   │
│   ├── setup/
│   │   ├── install.sh
│   │   ├── install.bat
│   │   ├── setup_scheduler_linux.sh
│   │   └── setup_scheduler_windows.bat
│   │
│   └── utilities/
│       ├── migrate_data.py
│       └── cleanup_logs.py
│
├── tests/                       # 🧪 Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration
│   │
│   ├── unit/                    # Unit tests
│   │   ├── agents/
│   │   ├── strategies/
│   │   ├── data/
│   │   ├── signals/
│   │   ├── execution/
│   │   └── risk/
│   │
│   ├── integration/             # Integration tests
│   │   ├── test_full_pipeline.py
│   │   ├── test_api_connections.py
│   │   └── test_multi_agent_flow.py
│   │
│   ├── performance/             # Performance tests
│   │   ├── test_benchmarks.py
│   │   └── test_phase2_performance.py
│   │
│   └── fixtures/                # Test data
│       ├── market_data.json
│       └── mock_responses.py
│
├── backtesting/                 # 📈 Backtesting framework
│   ├── __init__.py
│   ├── engine.py                # Backtest engine
│   ├── monte_carlo.py           # Monte Carlo simulation
│   ├── metrics.py               # Performance metrics
│   ├── attribution.py           # Portfolio attribution
│   └── scenarios/               # Backtest scenarios
│       ├── historical_2024.yaml
│       └── stress_test.yaml
│
├── data/                        # 💾 Data storage
│   ├── cache/                   # Temporary cached data
│   │   ├── .gitkeep
│   │   └── README.md
│   ├── historical/              # Historical market data
│   │   ├── prices/
│   │   ├── fundamentals/
│   │   └── alternative/
│   └── state/                   # Application state
│       ├── positions.json       # Current positions
│       ├── trades_history.json  # Trade log
│       └── performance.json     # Performance metrics
│
├── reports/                     # 📊 Generated reports
│   ├── premarket/               # Pre-market research
│   │   └── {YYYY-MM-DD}/
│   │       ├── claude_research.md
│   │       ├── claude_research_dee_bot.pdf
│   │       └── claude_research_shorgan_bot.pdf
│   │
│   ├── postmarket/              # Post-market summaries
│   │   └── {YYYY-MM-DD}/
│   │       └── report.txt
│   │
│   ├── performance/             # Performance reports
│   │   └── {YYYY-MM}/
│   │       ├── monthly_summary.md
│   │       └── performance_graph.png
│   │
│   └── archive/                 # Old reports (>90 days)
│       └── {YYYY-MM}/
│
├── logs/                        # 📝 Application logs
│   ├── system/                  # System logs
│   │   └── {YYYY-MM-DD}.log
│   ├── trading/                 # Trading logs
│   │   └── {YYYY-MM-DD}.log
│   ├── errors/                  # Error logs
│   │   └── {YYYY-MM-DD}.log
│   └── .gitignore               # Ignore all .log files
│
├── docs/                        # 📚 Documentation
│   ├── README.md                # Documentation index
│   ├── architecture/
│   │   ├── system_design.md
│   │   ├── data_flow.md
│   │   └── agent_communication.md
│   │
│   ├── guides/
│   │   ├── installation.md
│   │   ├── configuration.md
│   │   ├── daily_operations.md
│   │   ├── backtesting.md
│   │   └── troubleshooting.md
│   │
│   ├── strategies/
│   │   ├── dee_bot_strategy.md
│   │   └── shorgan_bot_strategy.md
│   │
│   ├── api/
│   │   ├── agents_api.md
│   │   ├── data_sources_api.md
│   │   └── execution_api.md
│   │
│   └── sessions/                # Session summaries
│       └── {YYYY-MM-DD}_session_summary.md
│
├── notebooks/                   # 📓 Jupyter notebooks (optional)
│   ├── exploratory/
│   │   ├── data_analysis.ipynb
│   │   └── strategy_testing.ipynb
│   └── reports/
│       └── monthly_review.ipynb
│
├── .github/                     # GitHub configuration
│   ├── workflows/
│   │   ├── tests.yml
│   │   └── lint.yml
│   └── ISSUE_TEMPLATE/
│
├── .env.example                 # Environment template
├── .gitignore
├── .coveragerc                  # Coverage configuration
├── pytest.ini                   # Pytest configuration
├── mypy.ini                     # Type checking config
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
└── requirements-test.txt        # Test dependencies
```

---

## 📂 Folder Explanations

### `/config/` - Configuration Management
**Purpose:** Centralized configuration for all system settings
- **Why separate?** Makes it easy to find and modify settings
- **Benefits:**
  - Single source of truth for all configurations
  - Easy to version control (except API keys)
  - Clear separation between different bot configurations
- **Contents:**
  - API credentials (gitignored)
  - Trading parameters
  - Risk limits
  - Schedule configuration
  - Bot-specific settings

### `/src/` - Core Application Code
**Purpose:** All production code organized by domain
- **Why this structure?** Follows clean architecture principles
- **Benefits:**
  - Clear separation of concerns
  - Easy to find related functionality
  - Reusable components
  - Testable modules
- **Subfolders:**
  - `agents/` - AI decision-making logic
  - `strategies/` - Trading strategy implementations
  - `data/` - Data acquisition and processing
  - `signals/` - Signal generation logic
  - `execution/` - Trade execution logic
  - `risk/` - Risk management
  - `reports/` - Report generation
  - `notifications/` - Alert systems
  - `monitoring/` - Health checks
  - `utils/` - Shared utilities

### `/scripts/` - Executable Scripts
**Purpose:** Daily operational scripts
- **Why separate?** Clear entry points for automation
- **Benefits:**
  - Easy to schedule (cron, Task Scheduler)
  - Simple command-line execution
  - Clear operational workflow
- **Subfolders:**
  - `automation/` - Daily automated tasks
  - `portfolio/` - Portfolio management
  - `monitoring/` - Health checks
  - `setup/` - Installation scripts

### `/tests/` - Test Suite
**Purpose:** Comprehensive testing
- **Why organized this way?** Mirrors src/ structure
- **Benefits:**
  - Easy to find tests for specific modules
  - Clear separation of test types
  - Reusable fixtures
- **Structure:**
  - `unit/` - Unit tests (mirrors src/)
  - `integration/` - Integration tests
  - `performance/` - Performance benchmarks
  - `fixtures/` - Test data

### `/backtesting/` - Backtesting Framework
**Purpose:** Strategy validation and historical analysis
- **Why separate?** Different workflow from live trading
- **Benefits:**
  - Self-contained backtesting logic
  - Easy to run scenarios
  - Clear performance attribution
- **Contents:**
  - Backtest engine
  - Monte Carlo simulation
  - Performance metrics
  - Attribution analysis

### `/data/` - Data Storage
**Purpose:** All persistent data
- **Why this structure?** Clear data lifecycle
- **Benefits:**
  - Organized by purpose
  - Easy to clean cache
  - State persistence for resuming
- **Subfolders:**
  - `cache/` - Temporary data (can be deleted)
  - `historical/` - Long-term historical data
  - `state/` - Current system state (positions, trades)

### `/reports/` - Generated Reports
**Purpose:** Output of all report generation
- **Why date-organized?** Easy to find specific reports
- **Benefits:**
  - Chronological organization
  - Easy archiving
  - Clear audit trail
- **Structure:**
  - `premarket/` - Research reports
  - `postmarket/` - Daily summaries
  - `performance/` - Monthly/yearly reviews
  - `archive/` - Old reports

### `/logs/` - Application Logs
**Purpose:** System and trading logs
- **Why separate folders?** Different log purposes
- **Benefits:**
  - Easy to search specific log types
  - Separate retention policies
  - Clear debugging trail
- **Types:**
  - `system/` - Application logs
  - `trading/` - Trade execution logs
  - `errors/` - Error tracking

### `/docs/` - Documentation
**Purpose:** All project documentation
- **Why organized?** Different doc types
- **Benefits:**
  - Easy to navigate
  - Clear documentation structure
  - Separate code from docs
- **Subfolders:**
  - `architecture/` - System design
  - `guides/` - How-to guides
  - `strategies/` - Strategy documentation
  - `api/` - API documentation
  - `sessions/` - Session summaries

---

## 📝 File Naming Conventions

### Python Modules
```python
# Module names: lowercase with underscores
fundamental_analyst.py
position_tracker.py
send_morning_report.py

# Class names: PascalCase
class FundamentalAnalyst:
    pass

class PositionTracker:
    pass

# Functions: lowercase with underscores
def analyze_stock(ticker: str) -> Dict:
    pass

def send_telegram_message(message: str) -> bool:
    pass
```

### Configuration Files
```yaml
# Format: purpose.yaml
api_keys.yaml
schedule.yaml
trading.yaml
risk_limits.yaml
notifications.yaml

# Bot-specific: botname_purpose.yaml
dee_bot.yaml
shorgan_bot.yaml
```

### Report Files
```
# Pre-market reports
reports/premarket/2025-10-23/claude_research.md
reports/premarket/2025-10-23/claude_research_dee_bot_2025-10-23.pdf
reports/premarket/2025-10-23/claude_research_shorgan_bot_2025-10-23.pdf

# Post-market reports
reports/postmarket/2025-10-23/report.txt

# Performance reports
reports/performance/2025-10/monthly_summary.md
reports/performance/2025-10/performance_graph.png
```

### Log Files
```
# Date-stamped logs
logs/system/2025-10-23.log
logs/trading/2025-10-23.log
logs/errors/2025-10-23.log
```

### State Files
```json
# Current state (JSON for easy parsing)
data/state/positions.json
data/state/trades_history.json
data/state/performance.json
```

---

## 🔄 Workflow Processes

### 1. Daily Operations Workflow

```bash
# Evening (6:00 PM) - Research Generation
scripts/automation/daily_research.py
# → Generates reports/premarket/{date}/claude_research.md
# → Sends PDFs via Telegram

# Morning (8:30 AM) - Trade Generation
scripts/automation/generate_trades.py
# → Reads reports/premarket/{date}/
# → Generates TODAYS_TRADES_{date}.md
# → Saves to docs/

# Market Open (9:30 AM) - Trade Execution
scripts/automation/execute_trades.py
# → Reads TODAYS_TRADES_{date}.md
# → Executes approved trades
# → Updates data/state/positions.json

# Post Open (9:45 AM) - Morning Report
scripts/automation/send_enhanced_morning_report.py
# → Reads data/state/positions.json
# → Generates and sends morning summary

# Market Close (4:15 PM) - Post-Market Report
scripts/automation/generate_postmarket_report.py
# → Reads day's performance
# → Generates reports/postmarket/{date}/
# → Sends Telegram summary
```

### 2. Strategy Version Management

```python
# Strategy versioning in git
git tag -a dee-bot-v1.2.0 -m "Beta-neutral strategy update"
git tag -a shorgan-bot-v2.1.0 -m "Catalyst improvements"

# Strategy config versioning
config/bots/dee_bot.yaml:
  version: "1.2.0"
  last_updated: "2025-10-23"
  changes: "Updated beta target to 0.45"

# Code organization
src/strategies/dee_bot/
  ├── strategy.py          # Current version
  ├── config.py            # Current config
  └── versions/            # Historical versions
      ├── v1.0.0/
      ├── v1.1.0/
      └── v1.2.0/
```

### 3. Session Persistence & Resume

```python
# State management
from src.utils.state import StateManager

state = StateManager()

# Save state
state.save({
    'positions': current_positions,
    'pending_orders': pending_orders,
    'last_update': datetime.now(),
    'session_id': session_id
})

# Resume from state
state = StateManager.load_latest()
positions = state['positions']
pending_orders = state['pending_orders']

# Session tracking
docs/sessions/2025-10-23_session_summary.md:
  - Session ID
  - Start time
  - End time
  - Trades executed
  - System status
  - Next steps
```

### 4. Code Change Tracking

```bash
# Feature branch workflow
git checkout -b feature/enhanced-risk-management
# ... make changes ...
git commit -m "feat: add enhanced risk management"
git push origin feature/enhanced-risk-management
# ... create PR, review, merge ...

# Change log automation
CHANGELOG.md automatically updated via conventional commits:
  feat: New feature
  fix: Bug fix
  docs: Documentation changes
  refactor: Code refactoring
  test: Test additions/changes
  chore: Maintenance tasks

# Version bumping
bump2version patch  # 1.0.0 → 1.0.1
bump2version minor  # 1.0.0 → 1.1.0
bump2version major  # 1.0.0 → 2.0.0
```

### 5. Environment Setup

```bash
# Python virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt          # Production
pip install -r requirements-dev.txt      # Development
pip install -r requirements-test.txt     # Testing

# Install package in editable mode
pip install -e .

# Pre-commit hooks (optional)
pre-commit install
```

### 6. Testing Workflow

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests
pytest tests/performance/             # Performance tests

# Run with coverage
pytest --cov=src tests/
pytest --cov=src --cov-report=html tests/

# Run specific test file
pytest tests/unit/agents/test_fundamental_analyst.py

# Run tests matching pattern
pytest -k "test_risk"
```

---

## 🚀 Migration Plan

### Phase 1: Create New Structure (1-2 hours)
```bash
# 1. Create new directory structure
mkdir -p config/bots
mkdir -p src/{agents,strategies,data,signals,execution,risk,reports,notifications,monitoring,integration,utils}
mkdir -p scripts/{automation,portfolio,monitoring,setup,utilities}
mkdir -p tests/{unit,integration,performance,fixtures}
mkdir -p backtesting/scenarios
mkdir -p data/{cache,historical,state}
mkdir -p reports/{premarket,postmarket,performance,archive}
mkdir -p logs/{system,trading,errors}
mkdir -p docs/{architecture,guides,strategies,api,sessions}

# 2. Create __init__.py files
find src -type d -exec touch {}/__init__.py \;
find tests -type d -exec touch {}/__init__.py \;
touch backtesting/__init__.py
```

### Phase 2: Move Configuration (30 minutes)
```bash
# Move config files to config/
mv config.yaml config/
mv schedule_config.py config/schedule.yaml
mv .env config/api_keys.yaml  # Rename and restructure

# Create bot-specific configs
# Extract DEE-BOT config → config/bots/dee_bot.yaml
# Extract SHORGAN-BOT config → config/bots/shorgan_bot.yaml
```

### Phase 3: Reorganize Source Code (2-3 hours)
```bash
# Move agents to src/agents/
mv agents/*.py src/agents/
mv agents/communication src/agents/

# Move strategies
mkdir -p src/strategies/dee_bot src/strategies/shorgan_bot
mv agents/core/execute_dee_bot*.py src/strategies/dee_bot/
mv agents/core/generate_dee_bot*.py src/strategies/dee_bot/
mv agents/dee-bot/standalone/analysis/*.py src/strategies/dee_bot/
# Similar for SHORGAN-BOT

# Move data sources
mv data_sources/* src/data/sources/
mv src/data/*.py src/data/loaders/

# Move signals
mv src/signals/*.py src/signals/generators/

# Move execution
mv scripts/execution/*.py src/execution/

# Move risk
mv risk/*.py src/risk/

# Move reports
mv src/reports/*.py src/reports/generators/
```

### Phase 4: Reorganize Scripts (1 hour)
```bash
# Move automation scripts
mv scripts/automation/*.py scripts/automation/
# Ensure naming consistency

# Move portfolio scripts
mv scripts/portfolio/*.py scripts/portfolio/
mv get_portfolio_status.py scripts/portfolio/get_status.py

# Move monitoring
mv scripts/monitoring/*.py scripts/monitoring/
mv health_check.py scripts/monitoring/health_check.py
```

### Phase 5: Reorganize Tests (1 hour)
```bash
# Move unit tests
mv tests/agents/* tests/unit/agents/
# Create tests for each src/ module

# Move integration tests
mv tests/integration/* tests/integration/

# Move performance tests
mv tests/performance/* tests/performance/
mv benchmarks/*.py tests/performance/
```

### Phase 6: Reorganize Data & Reports (30 minutes)
```bash
# Consolidate data directories
mv data/historical data/historical/
mv data/daily data/cache/
# Remove redundant data/ folders

# Organize reports
mv reports/premarket reports/premarket/
mv reports/archive reports/archive/
# Create date-based structure
```

### Phase 7: Clean Up Root (30 minutes)
```bash
# Move docs
mv *.md docs/  # Except README, CHANGELOG, LICENSE
mv docs/session-summaries/* docs/sessions/

# Move backtesting
mv backtesting/* backtesting/
mv backtest_recommendations.py backtesting/

# Remove redundant directories
rm -rf scripts-and-data/
rm -rf C:Usersshorgai-stock-trading-botbenchmarksreports/
rm -rf session-summaries/
```

### Phase 8: Update Imports (2-3 hours)
```python
# Update all import statements
# Old: from agents.fundamental_analyst import FundamentalAnalyst
# New: from src.agents.fundamental_analyst import FundamentalAnalyst

# Use find-and-replace or automated refactoring tool
# Test after each batch of changes
```

### Phase 9: Update Scripts & Tests (1-2 hours)
```bash
# Update script imports and paths
# Update test imports
# Verify all tests pass
pytest tests/

# Update documentation
# Update README with new structure
```

### Phase 10: Validation (1 hour)
```bash
# Run full test suite
pytest tests/ --cov=src

# Run health check
python scripts/monitoring/health_check.py

# Test daily workflow
python scripts/automation/daily_research.py --test
python scripts/automation/generate_trades.py --test
python scripts/automation/execute_trades.py --dry-run

# Commit changes
git add .
git commit -m "refactor: reorganize repository structure"
git push origin reorganization-branch
```

---

## 📋 Best Practices Going Forward

### 1. Version Control
```bash
# Use conventional commits
git commit -m "feat: add new risk metric"
git commit -m "fix: correct position sizing bug"
git commit -m "docs: update installation guide"

# Create feature branches
git checkout -b feature/enhanced-signals
git checkout -b fix/stop-loss-issue
git checkout -b docs/api-documentation

# Tag releases
git tag -a v2.0.0 -m "Major reorganization release"
git push origin v2.0.0
```

### 2. Code Organization
- **One class per file** (unless very related)
- **Clear module responsibilities** (single responsibility principle)
- **Avoid circular dependencies** (use dependency injection)
- **Keep functions small** (<50 lines ideally)
- **Document public APIs** (docstrings for all public functions)

### 3. Configuration Management
```yaml
# Use YAML for configurations
# Keep defaults in code, overrides in config
# Separate dev/test/prod configurations
# Never commit API keys (use .env.example)

config/
  ├── defaults.yaml        # Default settings
  ├── development.yaml     # Dev overrides
  ├── production.yaml      # Prod overrides
  └── api_keys.yaml        # Secrets (gitignored)
```

### 4. Testing Standards
```python
# Aim for >80% code coverage
# Write tests before fixing bugs (TDD)
# Use fixtures for common test data
# Mock external APIs in tests
# Test edge cases and error conditions

# Test naming convention
def test_<function>_<scenario>_<expected_result>():
    # Example: test_calculate_position_size_high_volatility_reduces_size
    pass
```

### 5. Documentation Standards
```markdown
# Keep docs up to date with code
# Use Markdown for all documentation
# Include code examples in docs
# Update CHANGELOG with every release
# Document breaking changes clearly

docs/
  ├── README.md              # Start here
  ├── architecture/          # How it works
  ├── guides/                # How to use it
  ├── api/                   # API reference
  └── sessions/              # What happened
```

### 6. Dependency Management
```txt
# Pin major versions in requirements.txt
alpaca-trade-api==3.0.2
anthropic==0.18.1

# Use requirements-dev.txt for dev tools
pytest==8.0.0
black==24.1.1
mypy==1.8.0

# Document why each dependency is needed
# Regularly update dependencies (security)
# Use dependabot for automated updates
```

### 7. Logging Standards
```python
# Use structured logging
import logging

logger = logging.getLogger(__name__)

# Log levels
logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning - potential issue")
logger.error("Error occurred")
logger.critical("Critical failure")

# Include context in logs
logger.info(f"Executing trade: {ticker} {action} {quantity} shares")
logger.error(f"Failed to fetch data for {ticker}: {error}")
```

### 8. State Management
```python
# Save state regularly
# State should be JSON-serializable
# Include timestamps
# Version state format

{
  "version": "2.0.0",
  "timestamp": "2025-10-23T09:30:00Z",
  "positions": [...],
  "pending_orders": [...],
  "last_trade_id": 12345
}
```

---

## ✅ Benefits of New Structure

### For Development
- ✅ **Clear organization** - Know exactly where to add new code
- ✅ **Easy testing** - Tests mirror source structure
- ✅ **Reusable components** - Clear module boundaries
- ✅ **Better IDE support** - Clear import paths

### For Operations
- ✅ **Simple automation** - Scripts in one place
- ✅ **Easy monitoring** - Logs and health checks organized
- ✅ **Clear data flow** - Input → Process → Output
- ✅ **State recovery** - Easy to resume from crashes

### For Collaboration
- ✅ **Onboarding** - New developers understand structure quickly
- ✅ **Code reviews** - Clear what changed and why
- ✅ **Documentation** - Everything documented in logical places
- ✅ **Standards** - Consistent patterns throughout

### For Maintenance
- ✅ **Bug fixes** - Easy to locate affected code
- ✅ **Updates** - Clear dependency management
- ✅ **Refactoring** - Modular design allows incremental changes
- ✅ **Scaling** - Easy to add new features without breaking existing

---

## 🎯 Success Metrics

After reorganization, you should be able to:

1. **Find any file in <10 seconds** by knowing its purpose
2. **Add a new feature** without touching >3 directories
3. **Run tests** with 100% passing after migration
4. **Execute daily workflow** with no manual intervention
5. **Onboard new developer** in <1 hour with clear docs
6. **Resume from crash** using saved state
7. **Deploy updates** with confidence (tests pass)
8. **Track changes** with clear git history

---

## 📞 Support

For questions or issues during migration:
1. Check `docs/guides/migration.md`
2. Review `CHANGELOG.md` for recent changes
3. Run `python scripts/monitoring/health_check.py`
4. Check logs in `logs/system/`

---

**Version:** 2.0
**Last Updated:** October 23, 2025
**Status:** Ready for Implementation
**Estimated Migration Time:** 8-12 hours
