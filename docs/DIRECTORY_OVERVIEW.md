# AI Trading Bot - Directory Structure Overview

## 📁 Root Directory: `C:\Users\shorg\ai-stock-trading-bot\`

### Core Trading System (`01_trading_system/`)
**Purpose**: Main trading engine and automation
- `agents/` - Multi-agent consensus system (9 agents)
- `automation/` - Scheduled tasks, ChatGPT server
- `config/` - Configuration files (dee_bot_config.json, etc.)
- `strategies/` - Trading strategy implementations

### Data Management (`02_data/`)
**Purpose**: Market data fetching and storage
- Historical price data
- Real-time quote systems
- Data preprocessing

### Configuration (`03_config/`)
**Purpose**: System-wide settings
- API keys configuration
- Trading parameters
- Bot-specific settings

### Risk Management (`04_risk/`)
**Purpose**: Risk controls and monitoring
- Stop loss management
- Position sizing
- Portfolio risk metrics

### Backtesting (`05_backtesting/`)
**Purpose**: Strategy testing and validation
- Historical performance analysis
- Strategy optimization
- Walk-forward analysis

### Utilities (`06_utils/`)
**Purpose**: Helper functions and tools
- Common utilities
- Data processing helpers
- API wrappers

### Documentation (`07_docs/`)
**Purpose**: Project documentation
- Strategy guides
- API documentation
- Setup instructions

### Frontend (`08_frontend/`)
**Purpose**: User interfaces
- Web dashboard (planned)
- Monitoring interfaces
- Performance visualization

### Logs (`09_logs/`)
**Purpose**: System logging
- `trading/` - Trade execution logs
- `errors/` - Error tracking
- `performance/` - Performance metrics

### Multi-Agent System (`agents/`)
**Purpose**: 9-agent consensus system
1. **fundamental_analyst.py** - Company financials
2. **technical_analyst.py** - Chart patterns
3. **news_monitor.py** - Breaking news
4. **sentiment_tracker.py** - Market sentiment
5. **catalyst_hunter.py** - Event tracking
6. **risk_assessor.py** - Risk evaluation
7. **options_flow_analyst.py** - Options activity
8. **bull_advocate.py** - Bullish perspective
9. **bear_advocate.py** - Bearish perspective

### Communication (`communication/`)
**Purpose**: External integrations
- `telegram_bot.py` - Telegram notifications
- `discord_bot.py` - Discord alerts (planned)
- Report generation

### Portfolio Holdings (`portfolio-holdings/`)
**Purpose**: Position tracking
```
portfolio-holdings/
├── shorgan-bot/
│   ├── current/
│   │   └── positions.csv
│   └── historical/
│       └── positions_YYYY-MM-DD.csv
└── dee-bot/
    ├── current/
    │   └── positions.csv (11 positions)
    └── historical/
        └── positions_YYYY-MM-DD.csv
```

### Scripts & Data (`scripts-and-data/`)
**Purpose**: Automation and analysis scripts
- `automation/` - Daily update scripts
- `analysis/` - Performance analysis
- `extractors/` - Report parsing

### Daily Reports (`daily-reports/`)
**Purpose**: Daily trading reports
- Pre-market analysis
- Post-market summaries
- ChatGPT recommendations

### Performance Metrics (`performance-metrics/`)
**Purpose**: Performance tracking
- Daily P&L
- Win/loss ratios
- Strategy metrics

### Trade Logs (`trade-logs/`)
**Purpose**: Detailed trade history
- Entry/exit logs
- Order confirmations
- Execution details

### Research Analysis (`research-analysis/`)
**Purpose**: Market research
- Sector analysis
- Company research
- Strategy development

## 🔑 Key Files

### Root Level
- **CLAUDE.md** - Session continuity for AI assistant
- **main.py** - Main entry point (legacy)
- **.env** - Environment variables
- **mapping.csv** - File structure mapping

### Strategy Files
- **CBRL_EARNINGS_STRATEGY.md** - Earnings play analysis
- **INCY_FDA_STRATEGY.md** - FDA catalyst strategy
- **DEE_BOT_ANALYSIS.md** - Beta-neutral strategy

### Automation Scripts
- **update_dee_bot_daily.bat** - Daily position sync
- **setup_daily_snapshot_task.bat** - Snapshot scheduler
- **generate_premarket_analysis.py** - Morning analysis

## 📊 Current Status

### Active Strategies
1. **SHORGAN-BOT**: Catalyst-driven micro-cap trading
   - 15 positions
   - ~$105k deployed
   - Focus: FDA, earnings, news catalysts

2. **DEE-BOT**: Beta-neutral S&P 100
   - 11 positions (post-rebalancing)
   - $102,684.40 value
   - Target beta: 1.0

### Automation Schedule
- **7:00 AM**: Pre-market analysis
- **9:30 AM**: DEE-BOT position sync
- **4:00 PM**: DEE-BOT evening update
- **4:30 PM**: Post-market report

## 🚀 Next Development Areas

### High Priority
- PostgreSQL database migration (from CSV)
- Real-time dashboard
- Options flow integration
- Trailing stops implementation

### Medium Priority
- ML-based weight optimization
- Social sentiment analysis
- Multi-broker support
- Mobile app

### Low Priority
- Voice alerts
- AR trading interface
- Federated learning

## 📝 Notes

- All timestamps in ET (Eastern Time)
- Paper trading via Alpaca API
- Telegram bot for notifications
- ChatGPT for daily recommendations
- 9-agent consensus for decisions