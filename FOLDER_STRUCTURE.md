# AI Trading Bot - Folder Structure

## 📁 Clean, Organized Structure (Updated Oct 1, 2025 - Phase 3)

```
ai-stock-trading-bot/
│
├── data/                          # All data files
│   ├── daily/                     # Daily operational data
│   │   ├── performance/           # Daily performance tracking
│   │   │   └── performance_history.json
│   │   ├── positions/             # Current position snapshots
│   │   └── reports/               # Daily reports by date
│   │       ├── 2025-09-16/
│   │       ├── 2025-10-01/
│   │       └── ...
│   │
│   ├── historical/                # Historical archives
│   │   ├── market/                # Market data (S&P 500, etc.)
│   │   ├── portfolio/             # Portfolio history
│   │   │   ├── dee-bot/
│   │   │   └── shorgan-bot/
│   │   └── trades/                # Trade logs
│   │
│   ├── execution/                 # Execution data
│   │   ├── plans/                 # Execution plans
│   │   └── results/               # Execution results
│   │
│   └── research/                  # Research reports
│       ├── claude/                # Claude research
│       └── chatgpt/               # ChatGPT research
│
├── scripts/                       # All executable scripts
│   ├── automation/                # Automation scripts
│   │   ├── execute_chatgpt_trades.py
│   │   ├── execute_daily_trades.py
│   │   ├── consensus_validator.py
│   │   ├── generate_research_html.py
│   │   └── ...
│   │
│   ├── backtesting/               # Backtesting scripts
│   │   ├── backtest_engine.py
│   │   ├── strategies.py
│   │   └── run_backtest.py
│   │
│   ├── performance/               # Performance tracking
│   │   ├── generate_performance_graph.py
│   │   ├── update_performance_history.py
│   │   └── get_portfolio_status.py
│   │
│   ├── portfolio/                 # Portfolio management
│   │   ├── rebalance_phase1.py
│   │   └── rebalance_phase2.py
│   │
│   ├── utilities/                 # Utility scripts
│   │   ├── check_remaining_orders.py
│   │   ├── cancel_all_pending.py
│   │   ├── check_orders.py
│   │   └── setup_alternative_data.py
│   │
│   └── windows/                   # Windows automation (NEW)
│       ├── GENERATE_PERFORMANCE_GRAPH.bat
│       ├── EXECUTE_TUESDAY_930AM.bat
│       ├── execute_morning_trades_automated.bat
│       ├── Morning_Trade_Execution_930AM.xml
│       └── ... (12 batch files + prompts)
│
├── agents/                        # Trading agents
│   ├── base_agent.py
│   ├── fundamental_analyst.py
│   ├── technical_analyst.py
│   └── ...
│
├── communication/                 # Communication modules
│   ├── telegram_bot.py
│   └── ...
│
├── docs/                          # Documentation (NEW)
│   ├── CHANGELOG.md
│   ├── CONTRIBUTING.md
│   ├── PERFORMANCE_README.md
│   ├── daily_monitoring_checklist.md
│   └── archive/                   # Archived documentation
│       ├── SESSION_SUMMARY_2025-09-29_EVENING.md
│       ├── PORTFOLIO_REBALANCING_PLAN.md
│       ├── REPOSITORY_REVIEW.md
│       └── ... (13 archived docs)
│
├── tests/                         # Test files (NEW)
│   ├── test_complete_system.py
│   ├── test_live_data_sources.py
│   └── test_tuesday_setup.py
│
└── [ROOT: 22 Essential Files]     # Minimal, clean root
    ├── main.py
    ├── generate_performance_graph.py
    ├── update_performance_history.py
    ├── execute_chatgpt_trades.py
    ├── get_portfolio_status.py
    ├── setup.py
    ├── README.md
    ├── CLAUDE.md
    ├── CLAUDE_UPDATE_OCT1.md
    ├── FOLDER_STRUCTURE.md
    ├── LICENSE
    └── ... (config files: .env, .gitignore, requirements.txt, etc.)
```

---

## 🎯 Quick Navigation

### Performance & Monitoring
```bash
# Generate performance graph
python scripts/performance/generate_performance_graph.py

# Update performance history
python scripts/performance/update_performance_history.py

# Check portfolio status
python scripts/performance/get_portfolio_status.py
```

### Portfolio Management
```bash
# Rebalance portfolios
python scripts/portfolio/rebalance_phase1.py
python scripts/portfolio/rebalance_phase2.py
```

### Automation
```bash
# Execute ChatGPT trades
python scripts/automation/execute_chatgpt_trades.py

# Execute daily trades
python scripts/automation/execute_daily_trades.py
```

### Utilities
```bash
# Check pending orders
python scripts/utilities/check_remaining_orders.py

# Cancel all pending orders
python scripts/utilities/cancel_all_pending.py
```

---

## 📊 Data Locations

| Data Type | Location | Purpose |
|-----------|----------|---------|
| Daily Performance | `data/daily/performance/` | Performance tracking JSON |
| Current Positions | `data/daily/positions/` | Latest position snapshots |
| Daily Reports | `data/daily/reports/{date}/` | Research and execution reports |
| Historical Data | `data/historical/portfolio/` | Past portfolio snapshots |
| Trade Logs | `data/historical/trades/` | Historical trade records |
| Research Reports | `data/research/claude/` | Claude & ChatGPT research |
| Execution Plans | `data/execution/plans/` | Trading execution plans |

---

## ✅ Benefits of New Structure

1. **Clear Organization**: Each folder has a single, clear purpose
2. **Easy Navigation**: Find what you need in seconds
3. **No Nesting**: Eliminated duplicate folders (portfolio/portfolio, market/market)
4. **Scalable**: Easy to add new data/scripts
5. **Professional**: Follows industry best practices

---

## 🔧 Root Directory Philosophy

**22 Essential Files Only:**
- **Core Scripts (6)**: Frequently-used scripts remain in root for quick access
- **Key Documentation (4)**: README, CLAUDE session docs, folder guide, LICENSE
- **Configuration (12)**: .env, .gitignore, requirements.txt, pytest.ini, etc.

**Everything Else Organized:**
- Documentation → `docs/` and `docs/archive/`
- Tests → `tests/`
- Batch files → `scripts/windows/`
- Utility scripts → `scripts/utilities/`

All scripts work correctly with the new structure. Root scripts can call organized scripts seamlessly.

---

## 📝 Migration Notes

**Phase 1-2 (Oct 1, 2025 - Afternoon):**
- Reorganized from `scripts-and-data/` to clean `data/` and `scripts/` structure
- Deleted 11 duplicate files
- Archived 6 completed documentation files
- **Result**: 75 → 53 files in root

**Phase 3 (Oct 1, 2025 - Evening):**
- Created `docs/` and `docs/archive/` directories
- Created `scripts/windows/` for batch files
- Moved tests to `tests/` directory
- Organized all documentation and utility scripts
- **Result**: 53 → 22 files in root (71% total reduction!)

**Status**: ✅ Complete and tested
**Scripts Updated**: All path references updated to new structure
**Tests Passed**: Performance graph generation, portfolio status, all working

---

## 💡 Tips

- All daily operational data is in `data/daily/`
- All historical archives are in `data/historical/`
- All executable scripts are in `scripts/` organized by category
- Performance tracking has its own dedicated folder in `scripts/performance/`
- Automation scripts are all in `scripts/automation/`

The new structure makes it easy to find what you need and scale the system!
