# Repository Directory Structure - Visual Guide

**Date:** October 23, 2025
**Purpose:** Visual reference for proposed repository organization

---

## 📊 High-Level View

```
ai-stock-trading-bot/          → Root
│
├── 📁 config/                  → ⚙️ ALL CONFIGURATION
├── 📁 src/                     → 🧠 ALL PRODUCTION CODE
├── 📁 scripts/                 → 🚀 ALL OPERATIONS
├── 📁 tests/                   → 🧪 ALL TESTING
├── 📁 backtesting/             → 📈 BACKTESTING ENGINE
├── 📁 data/                    → 💾 DATA STORAGE
├── 📁 reports/                 → 📊 OUTPUT REPORTS
├── 📁 logs/                    → 📝 APPLICATION LOGS
├── 📁 docs/                    → 📚 DOCUMENTATION
├── 📁 notebooks/               → 📓 JUPYTER NOTEBOOKS
│
├── README.md                   → 📖 Main documentation
├── CHANGELOG.md                → 📋 Version history
├── LICENSE                     → ⚖️ License
├── requirements.txt            → 📦 Dependencies
└── .env.example                → 🔐 Config template
```

---

## 🎯 Data Flow Visualization

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DAILY WORKFLOW                                │
└─────────────────────────────────────────────────────────────────────┘

6:00 PM (Evening Before)
    ↓
┌─────────────────────┐
│ scripts/automation/ │ → daily_research.py
│   └─ Research Gen  │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ src/agents/         │ → Run all 7 agents
│   └─ AI Analysis   │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ src/reports/        │ → Generate reports
│   └─ Report Gen    │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ reports/premarket/  │ → Save research
│   └─ {YYYY-MM-DD}/  │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ src/notifications/  │ → Send to Telegram
│   └─ Telegram      │
└─────────────────────┘

8:30 AM (Next Morning)
    ↓
┌─────────────────────┐
│ scripts/automation/ │ → generate_trades.py
│   └─ Trade Gen     │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ src/strategies/     │ → DEE-BOT, SHORGAN-BOT
│   └─ Strategy Logic│
└─────────────────────┘
    ↓
┌─────────────────────┐
│ src/risk/           │ → Validate risk
│   └─ Risk Mgmt     │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ docs/               │ → Save trades
│   └─ TODAYS_TRADES │
└─────────────────────┘

9:30 AM (Market Open)
    ↓
┌─────────────────────┐
│ scripts/automation/ │ → execute_trades.py
│   └─ Execute       │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ src/execution/      │ → Order manager
│   └─ Trade Exec    │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ data/state/         │ → Update positions
│   └─ positions.json│
└─────────────────────┘

9:45 AM (Post Open)
    ↓
┌─────────────────────┐
│ scripts/automation/ │ → send_enhanced_morning_report.py
│   └─ Morning Report│
└─────────────────────┘
    ↓
┌─────────────────────┐
│ src/notifications/  │ → Send to Telegram
│   └─ Telegram      │
└─────────────────────┘

4:15 PM (Post Close)
    ↓
┌─────────────────────┐
│ scripts/automation/ │ → generate_postmarket_report.py
│   └─ EOD Report    │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ reports/postmarket/ │ → Save report
│   └─ {YYYY-MM-DD}/  │
└─────────────────────┘
```

---

## 📁 Detailed Directory Tree

### /config/ - Configuration
```
config/
├── __init__.py
├── settings.py                 # Central settings loader
├── api_keys.yaml              # API credentials (gitignored)
├── api_keys.example.yaml      # Template
├── schedule.yaml              # Automation schedule
├── trading.yaml               # Trading parameters
├── risk_limits.yaml           # Risk rules
├── notifications.yaml         # Alert config
└── bots/
    ├── dee_bot.yaml           # DEE-BOT config
    └── shorgan_bot.yaml       # SHORGAN-BOT config
```

### /src/ - Core Code
```
src/
├── __init__.py
│
├── agents/                    # 🤖 AI Decision Makers
│   ├── __init__.py
│   ├── base_agent.py
│   ├── fundamental_analyst.py
│   ├── technical_analyst.py
│   ├── news_analyst.py
│   ├── sentiment_analyst.py
│   ├── risk_manager.py
│   ├── bull_researcher.py
│   ├── bear_researcher.py
│   ├── alternative_data_agent.py
│   ├── shorgan_catalyst_agent.py
│   ├── options_strategy_agent.py
│   ├── debate_system.py
│   └── communication/
│       ├── coordinator.py
│       ├── message_bus.py
│       └── protocols.py
│
├── strategies/                # 📊 Trading Strategies
│   ├── __init__.py
│   ├── base_strategy.py
│   ├── dee_bot/              # Beta-Neutral
│   │   ├── strategy.py
│   │   ├── executor.py
│   │   ├── monitor.py
│   │   └── config.py
│   └── shorgan_bot/          # Catalyst-Driven
│       ├── strategy.py
│       ├── executor.py
│       ├── monitor.py
│       └── config.py
│
├── data/                      # 📥 Data Pipeline
│   ├── __init__.py
│   ├── sources/              # External APIs
│   │   ├── alpaca.py
│   │   ├── financial_datasets.py
│   │   ├── sec_filings.py
│   │   ├── google_trends.py
│   │   └── reddit_sentiment.py
│   ├── loaders/              # Data loaders
│   │   ├── market_data.py
│   │   ├── fundamental_data.py
│   │   └── alternative_data.py
│   ├── processors/           # Data processing
│   │   ├── cleaners.py
│   │   ├── normalizers.py
│   │   └── validators.py
│   └── aggregator.py
│
├── signals/                   # 📡 Signal Generation
│   ├── __init__.py
│   ├── generators/
│   │   ├── technical.py
│   │   ├── fundamental.py
│   │   ├── sentiment.py
│   │   └── composite.py
│   └── combiners.py
│
├── execution/                 # 💼 Trade Execution
│   ├── __init__.py
│   ├── order_manager.py
│   ├── position_tracker.py
│   ├── risk_validator.py
│   └── fill_handler.py
│
├── risk/                      # 🛡️ Risk Management
│   ├── __init__.py
│   ├── portfolio_risk.py
│   ├── position_sizing.py
│   ├── kelly_criterion.py
│   ├── stop_loss_manager.py
│   └── drawdown_monitor.py
│
├── reports/                   # 📄 Report Generation
│   ├── __init__.py
│   ├── generators/
│   │   ├── premarket.py
│   │   ├── postmarket.py
│   │   ├── morning_summary.py
│   │   └── performance.py
│   ├── formatters/
│   │   ├── markdown.py
│   │   ├── pdf.py
│   │   └── telegram.py
│   └── templates/
│       └── report_template.md
│
├── notifications/             # 🔔 Alerts
│   ├── __init__.py
│   ├── telegram.py
│   ├── email.py
│   ├── slack.py
│   └── discord.py
│
├── monitoring/                # 📊 System Health
│   ├── __init__.py
│   ├── health_check.py
│   ├── pipeline_monitor.py
│   └── performance_tracker.py
│
├── integration/               # 🔗 Phase 2
│   ├── __init__.py
│   ├── phase2_integration.py
│   └── phase2_config.py
│
└── utils/                     # 🔧 Utilities
    ├── __init__.py
    ├── logging.py
    ├── datetime_helpers.py
    ├── file_io.py
    └── validators.py
```

### /scripts/ - Operations
```
scripts/
├── automation/               # Daily automation
│   ├── daily_research.py
│   ├── generate_trades.py
│   ├── execute_trades.py
│   ├── send_morning_report.py
│   ├── send_enhanced_morning_report.py
│   ├── send_research_pdfs.py
│   └── generate_postmarket_report.py
│
├── portfolio/                # Portfolio management
│   ├── get_status.py
│   ├── rebalance.py
│   └── update_positions.py
│
├── monitoring/               # Health checks
│   ├── health_check.py
│   └── pipeline_health.py
│
├── setup/                    # Installation
│   ├── install.sh
│   ├── install.bat
│   ├── setup_scheduler_linux.sh
│   └── setup_scheduler_windows.bat
│
└── utilities/                # Utilities
    ├── migrate_data.py
    └── cleanup_logs.py
```

### /tests/ - Testing
```
tests/
├── __init__.py
├── conftest.py              # Pytest config
│
├── unit/                    # Unit tests (mirrors src/)
│   ├── agents/
│   ├── strategies/
│   ├── data/
│   ├── signals/
│   ├── execution/
│   └── risk/
│
├── integration/             # Integration tests
│   ├── test_full_pipeline.py
│   ├── test_api_connections.py
│   └── test_multi_agent_flow.py
│
├── performance/             # Performance tests
│   ├── test_benchmarks.py
│   └── test_phase2_performance.py
│
└── fixtures/                # Test data
    ├── market_data.json
    └── mock_responses.py
```

### /backtesting/ - Backtesting
```
backtesting/
├── __init__.py
├── engine.py                # Backtest engine
├── monte_carlo.py           # Monte Carlo
├── metrics.py               # Performance metrics
├── attribution.py           # Portfolio attribution
└── scenarios/               # Test scenarios
    ├── historical_2024.yaml
    └── stress_test.yaml
```

### /data/ - Storage
```
data/
├── cache/                   # Temporary (can delete)
│   ├── .gitkeep
│   └── README.md
│
├── historical/              # Long-term data
│   ├── prices/
│   ├── fundamentals/
│   └── alternative/
│
└── state/                   # Current state
    ├── positions.json       # Active positions
    ├── trades_history.json  # Trade log
    └── performance.json     # Performance metrics
```

### /reports/ - Outputs
```
reports/
├── premarket/               # Research reports
│   └── {YYYY-MM-DD}/
│       ├── claude_research.md
│       ├── claude_research_dee_bot.pdf
│       └── claude_research_shorgan_bot.pdf
│
├── postmarket/              # Daily summaries
│   └── {YYYY-MM-DD}/
│       └── report.txt
│
├── performance/             # Performance reports
│   └── {YYYY-MM}/
│       ├── monthly_summary.md
│       └── performance_graph.png
│
└── archive/                 # Old reports (>90 days)
    └── {YYYY-MM}/
```

### /logs/ - Logging
```
logs/
├── system/                  # System logs
│   └── {YYYY-MM-DD}.log
│
├── trading/                 # Trading logs
│   └── {YYYY-MM-DD}.log
│
├── errors/                  # Error logs
│   └── {YYYY-MM-DD}.log
│
└── .gitignore              # Ignore all .log files
```

### /docs/ - Documentation
```
docs/
├── README.md               # Documentation index
│
├── architecture/           # System design
│   ├── system_design.md
│   ├── data_flow.md
│   └── agent_communication.md
│
├── guides/                 # How-to guides
│   ├── installation.md
│   ├── configuration.md
│   ├── daily_operations.md
│   ├── backtesting.md
│   └── troubleshooting.md
│
├── strategies/             # Strategy docs
│   ├── dee_bot_strategy.md
│   └── shorgan_bot_strategy.md
│
├── api/                    # API reference
│   ├── agents_api.md
│   ├── data_sources_api.md
│   └── execution_api.md
│
└── sessions/               # Session summaries
    └── {YYYY-MM-DD}_session_summary.md
```

---

## 🔄 Module Dependencies

```
┌─────────────┐
│   config/   │  ← Configuration Layer
└─────────────┘
      ↓
┌─────────────────────────────────────────┐
│              src/                       │
│  ┌────────┐  ┌──────────┐  ┌─────────┐ │
│  │ agents │→ │strategies│→ │execution│ │
│  └────────┘  └──────────┘  └─────────┘ │
│      ↓            ↓             ↓       │
│  ┌────────┐  ┌──────────┐  ┌─────────┐ │
│  │ data   │  │ signals  │  │  risk   │ │
│  └────────┘  └──────────┘  └─────────┘ │
│      ↓                                  │
│  ┌────────────────────────────────┐    │
│  │ reports / notifications / utils│    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘
      ↓
┌─────────────┐
│  scripts/   │  ← Execution Layer
└─────────────┘
      ↓
┌─────────────────────────────────┐
│  data/ reports/ logs/           │  ← Storage Layer
└─────────────────────────────────┘
```

---

## 📊 Size Comparison

### Before Reorganization
```
Root:           70+ files
Total folders:  ~40 directories
Depth:          Up to 6 levels deep
Redundancy:     3 data folders, 2 session folders
```

### After Reorganization
```
Root:           ~10 files
Total folders:  ~30 directories
Depth:          Max 4 levels deep
Redundancy:     None (consolidated)
```

**Improvement:** 40% fewer directories, 86% cleaner root, 33% shallower hierarchy

---

## 🎯 Key Paths Reference

### Daily Operations
```
Research:        scripts/automation/daily_research.py
Trade Gen:       scripts/automation/generate_trades.py
Execute:         scripts/automation/execute_trades.py
Morning Report:  scripts/automation/send_enhanced_morning_report.py
EOD Report:      scripts/automation/generate_postmarket_report.py
```

### Configuration
```
API Keys:        config/api_keys.yaml
Trading Params:  config/trading.yaml
Risk Limits:     config/risk_limits.yaml
DEE-BOT Config:  config/bots/dee_bot.yaml
SHORGAN Config:  config/bots/shorgan_bot.yaml
```

### State & Data
```
Positions:       data/state/positions.json
Trade History:   data/state/trades_history.json
Performance:     data/state/performance.json
Market Data:     data/historical/prices/
```

### Reports
```
Today Research:  reports/premarket/{today}/
Today EOD:       reports/postmarket/{today}/
This Month:      reports/performance/{YYYY-MM}/
```

### Logs
```
System Logs:     logs/system/{YYYY-MM-DD}.log
Trading Logs:    logs/trading/{YYYY-MM-DD}.log
Error Logs:      logs/errors/{YYYY-MM-DD}.log
```

---

## 💡 Finding Files Fast

### "Where should I put...?"

| What | Where | Why |
|------|-------|-----|
| New agent | `src/agents/` | All AI logic |
| New strategy | `src/strategies/{bot}/` | Strategy code |
| New script | `scripts/{category}/` | Operational |
| New test | `tests/unit/{module}/` | Mirrors src/ |
| New config | `config/` | Settings |
| Generated report | `reports/{type}/{date}/` | Outputs |
| State file | `data/state/` | Current state |
| Historical data | `data/historical/` | Long-term |
| Documentation | `docs/{category}/` | Docs |

### "Where to find...?"

| Looking for | Location | Path |
|-------------|----------|------|
| Fundamental agent | Agents | `src/agents/fundamental_analyst.py` |
| DEE-BOT strategy | Strategies | `src/strategies/dee_bot/strategy.py` |
| Daily research script | Automation | `scripts/automation/daily_research.py` |
| Agent tests | Tests | `tests/unit/agents/test_fundamental_analyst.py` |
| API keys | Config | `config/api_keys.yaml` |
| Today's research | Reports | `reports/premarket/{today}/` |
| Current positions | State | `data/state/positions.json` |
| System logs | Logs | `logs/system/{today}.log` |

---

## ✅ Checklist: "Is My Structure Correct?"

After reorganization, verify:

**Root Directory:**
- [ ] <15 files in root
- [ ] README.md present
- [ ] CHANGELOG.md present
- [ ] LICENSE present
- [ ] requirements.txt present
- [ ] .env.example present (not .env)

**Folder Structure:**
- [ ] All configs in /config/
- [ ] All source in /src/
- [ ] All scripts in /scripts/
- [ ] All tests in /tests/
- [ ] All data in /data/
- [ ] All reports in /reports/
- [ ] All logs in /logs/
- [ ] All docs in /docs/

**Functionality:**
- [ ] Tests pass: `pytest tests/`
- [ ] Health check passes
- [ ] Can import from src/
- [ ] Scripts run without errors
- [ ] Automation still works

---

**Version:** 1.0
**Last Updated:** October 23, 2025
**Purpose:** Visual reference for repository structure
