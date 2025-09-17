# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Architecture

### System Overview
This is a multi-agent AI trading bot system with two primary trading strategies:
- **SHORGAN-BOT**: Catalyst-driven micro-cap trading (17 positions, $105k portfolio)
- **DEE-BOT**: Beta-neutral S&P 100 defensive strategy (3 positions, $100k portfolio)

The system uses 9 specialized agents coordinated through an async message bus to make consensus-based trading decisions.

### Agent Architecture
```
Main.py → Coordinator → Message Bus → 9 Specialized Agents:
- FundamentalAnalystAgent (agents/fundamental_analyst.py)
- TechnicalAnalystAgent (agents/technical_analyst.py)
- NewsAnalystAgent (agents/news_analyst.py)
- SentimentAnalystAgent (agents/sentiment_analyst.py)
- BullResearcherAgent (agents/bull_researcher.py)
- BearResearcherAgent (agents/bear_researcher.py)
- RiskManagerAgent (agents/risk_manager.py)
- ShorganCatalystAgent (agents/shorgan_catalyst_agent.py)
- OptionsStrategyAgent (agents/options_strategy_agent.py)
```

Each agent inherits from `BaseAgent` and implements an `analyze()` method returning:
- `recommendation`: BUY/HOLD/SELL
- `confidence`: 0.0-1.0
- `reasoning`: Explanation
- `data`: Supporting metrics

### Directory Structure (Post-Reorganization)
```
/agents/                    # Multi-agent trading system
/communication/             # Message bus and coordinator
/scripts-and-data/
  /automation/             # Trading execution scripts
  /daily-csv/             # Position tracking (dee-bot-positions.csv, shorgan-bot-positions.csv)
  /daily-json/            # Trade execution logs
/docs/                     # Reports and documentation
/01_trading_system/        # Legacy structure (still contains some active components)
/02_data/                  # Legacy data storage
```

## Critical Services & Commands

### ChatGPT Report Server
```bash
# Start the ChatGPT report capture server (REQUIRED for browser extension)
cd 01_trading_system/automation && python chatgpt_report_server.py
# Runs on http://localhost:8888
```

### Daily Automated Reports
```bash
# Generate post-market report (4:30 PM ET daily)
python scripts-and-data/automation/generate-post-market-report.py

# Process new trades through multi-agent system
python scripts-and-data/automation/process-trades.py

# Generate DEE-BOT beta-neutral trades
python scripts-and-data/automation/generate_enhanced_dee_bot_trades.py
```

### Trading Execution
```bash
# Execute SHORGAN-BOT trades
python 01_trading_system/bots/execute_shorgan_trades.py

# Execute DEE-BOT trades
python 01_trading_system/execute_dee_bot_trades.py

# Place Alpaca orders
python 01_trading_system/core/place_alpaca_orders.py
```

## API Configurations

### Alpaca Paper Trading
- API Key: `PK6FZK4DAQVTD7DYVH78`
- Secret: `iXfKe0M7chQ5aYNy9bz4YARnGtiufJFq8nMqJlfa`
- Base URL: `https://paper-api.alpaca.markets`

### Telegram Bot
- Token: `8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c`
- Chat ID: `7870288896`

## Trading Rules & Risk Management

### Position Sizing
- SHORGAN-BOT: Max 10% per position, 30% sector concentration
- DEE-BOT: Max 8% per position, beta target 1.0 ± 0.1

### Stop Losses
- Catalyst trades: -8% trailing stop
- Defensive positions: -3% fixed stop
- Portfolio daily limit: -3% (deleveraging), -7% (force close)

### Multi-Agent Consensus
```python
weights = {
    "fundamental": 0.20,
    "technical": 0.20,
    "news": 0.15,
    "sentiment": 0.10,
    "bull": 0.15,
    "bear": 0.15,
    "risk": 0.05
}
# BUY if consensus > 0.65, SELL if < 0.35, else HOLD
```

## Current Portfolio State

### Active Positions (as of Sept 17, 2025)
- Total Value: $205,338.41 (+2.54%)
- 20 positions: 17 SHORGAN-BOT, 3 DEE-BOT
- Key holdings: RGTI (+22.7%), ORCL (+21.9%), KSS (-7.4% near stop)
- Critical events: CBRL earnings (Sept 17), INCY FDA (Sept 19)

### Position Tracking Files
- `scripts-and-data/daily-csv/shorgan-bot-positions.csv`
- `scripts-and-data/daily-csv/dee-bot-positions.csv`

## Windows Task Scheduler Jobs
- **Post-Market Report**: "AI Trading Bot - Post Market 4_30PM"
- Runs: `python scripts-and-data/automation/generate-post-market-report.py`

## Common Development Tasks

### Adding a New Agent
1. Create agent file in `/agents/` inheriting from `BaseAgent`
2. Implement `analyze(ticker)` method
3. Register in `main.py` initialization
4. Add weight in consensus calculation

### Testing Trade Execution
```bash
# Test Alpaca connection
python 01_trading_system/core/test_alpaca_connection.py

# Simulate trades without execution
python 01_trading_system/core/simulate_trading.py
```

### Debugging Failed Trades
1. Check wash trade rules (Alpaca blocks day trading same symbol)
2. Verify market hours (9:30 AM - 4:00 PM ET)
3. Check position CSV files for current holdings
4. Review logs in `01_trading_system/automation/02_data/research/reports/`

## Known Issues & Workarounds

### ChatGPT Extension Float Parsing
- Issue: "could not convert string to float: '.'"
- Workaround: Use manual save tool or re-capture report

### Yahoo Finance Rate Limiting
- Issue: 429 errors on data requests
- Workaround: Use Alpaca API as primary data source

### Wash Trade Blocks
- Issue: Alpaca rejects trades for recently traded symbols
- Solution: Wait T+2 or use complex orders

## Session Handoff Protocol

When continuing work in a new session:
1. Check ChatGPT server status (port 8888)
2. Review overnight position changes in CSV files
3. Check for stopped out positions
4. Get fresh ChatGPT recommendations
5. Monitor upcoming catalysts
6. Execute any pending orders from ORDERS_FOR_SEPT_18.md

## Critical Files for Continuity
- `CLAUDE.md` - This file
- `ORDERS_FOR_SEPT_18.md` - Tomorrow's execution plan
- `PROFIT_TAKING_ORDERS.md` - Profit strategy
- `INCY_FDA_STRATEGY.md` - Thursday FDA playbook
- Position CSVs in `scripts-and-data/daily-csv/`
- Update all relevant files, update todos, update system architecture, product plan