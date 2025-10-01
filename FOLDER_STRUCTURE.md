# AI Trading Bot - Folder Structure

## 📁 Clean, Organized Structure (Updated Oct 1, 2025)

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
│   │   └── ...
│   │
│   ├── backtesting/               # Backtesting scripts
│   │   ├── backtest_engine.py
│   │   └── ...
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
│   └── utilities/                 # Utility scripts
│       ├── check_remaining_orders.py
│       ├── cancel_all_pending.py
│       └── ...
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
├── docs/                          # Documentation
│
└── [Legacy root scripts]          # Keep for backward compatibility
    ├── main.py
    ├── generate_performance_graph.py
    ├── update_performance_history.py
    └── ...
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

## 🔧 Backward Compatibility

Key scripts remain in root directory for backward compatibility:
- `generate_performance_graph.py` (updated to use new paths)
- `update_performance_history.py` (updated to use new paths)
- `get_portfolio_status.py`

All scripts work correctly with the new structure.

---

## 📝 Migration Notes

**Date**: October 1, 2025
**Changes**: Complete reorganization from `scripts-and-data/` structure to clean `data/` and `scripts/` structure
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
