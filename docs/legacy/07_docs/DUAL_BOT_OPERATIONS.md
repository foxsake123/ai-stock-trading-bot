# Dual-Bot Trading System Operations Guide

## Overview
This system runs two distinct trading bots with different strategies:
- **SHORGAN-BOT**: Micro-cap catalyst-driven trading
- **DEE-BOT**: Beta-neutral S&P 100 with 2X leverage

## Daily Operations Workflow

### Pre-Market Pipeline (7:00 AM ET)

#### 1. SHORGAN-BOT Process
- **Research Source**: ChatGPT TradingAgents reports
- **Process**:
  1. ChatGPT report is saved via browser extension or manual input
  2. Multi-agent system analyzes each recommendation
  3. Risk manager approves/rejects trades
  4. Approved trades execute via Alpaca API
  5. Stop losses set automatically

#### 2. DEE-BOT Process  
- **Research Source**: Automated generation using Alpaca data
- **Process**:
  1. Analyzes S&P 100 components
  2. Calculates beta, momentum, RSI metrics
  3. Ranks opportunities by score
  4. Generates beta-neutral recommendations
  5. Executes trades maintaining 1.0 portfolio beta

### Running the Pipelines

#### Automatic Execution (Both Bots)
```batch
run_daily_pipelines.bat
```

#### Manual Execution
```python
# Run both bots
python 01_trading_system/automation/daily_pre_market_pipeline.py --bot BOTH

# Run SHORGAN-BOT only
python 01_trading_system/automation/daily_pre_market_pipeline.py --bot SHORGAN

# Run DEE-BOT only  
python 01_trading_system/automation/daily_pre_market_pipeline.py --bot DEE
```

### Report Generation

#### Daily Reports
```python
# Generate combined HTML/PDF report
python 01_trading_system/automation/dual_bot_report_generator.py
```

#### Weekly Reports
```python
# Generate weekly performance summary
python 01_trading_system/automation/weekly_report_generator.py
```

## ChatGPT Integration

### Browser Extension Setup
1. Open Chrome Extensions (chrome://extensions/)
2. Enable Developer mode
3. Load unpacked: `01_trading_system/automation/chatgpt_extension/`
4. Extension auto-captures reports from ChatGPT.com

### Manual Report Saving
```python
# Interactive save tool
python 01_trading_system/automation/save_chatgpt_report.py
```

### Report Server
```python
# Start server for browser extension
python 01_trading_system/automation/chatgpt_report_server.py
```
- Runs on http://localhost:8888
- Receives reports from browser extension
- Saves to: `02_data/research/reports/pre_market_daily/`

## Research Report Generators

### SHORGAN-BOT Research
- **Source**: ChatGPT TradingAgents
- **Format**: JSON with trades, catalysts, risk metrics
- **Location**: `02_data/research/reports/pre_market_daily/`

### DEE-BOT Research  
```python
# Generate DEE-BOT research report
python 01_trading_system/automation/dee_bot_research_generator.py
```
- **Source**: Automated analysis of S&P 100
- **Strategy**: Beta-neutral with 2X leverage
- **Location**: `02_data/research/reports/dee_bot/`

## Portfolio Management

### Position Tracking
- SHORGAN: `02_data/portfolio/positions/shorgan_bot_positions.csv`
- DEE: `02_data/portfolio/positions/dee_bot_positions.csv`

### Configuration Files
- SHORGAN: `01_trading_system/config/shorgan_bot_config.json`
- DEE: `01_trading_system/config/dee_bot_config.json`

### Current Holdings (as of 2025-09-16)

#### SHORGAN-BOT ($103,790.37)
- 14 positions including:
  - MFIC: 770 shares @ $12.16 (insider buying catalyst)
  - Various micro/small-cap catalyst plays
  
#### DEE-BOT ($101,690.62)
- 8 positions (target 15-20)
- Portfolio beta: 0.98 (target 1.0)
- Leverage: 1.85x (target 2.0x)

## Risk Management

### Position Sizing
- SHORGAN: 5-10% per position (2-5% for binary events)
- DEE: 3-8% per position (beta-adjusted)

### Stop Losses
- SHORGAN: 8-10% for catalyst trades
- DEE: 3% trailing stop

### Portfolio Limits
- Maximum 20 positions per bot
- Daily loss limit: 5% circuit breaker
- Sector exposure: Max 25% per sector

## Monitoring & Alerts

### Telegram Notifications
- Pre-market analysis summaries
- Trade executions
- Error alerts
- Daily P&L updates

### Log Files
- Location: `09_logs/automation/`
- Daily pipeline logs
- Trade execution logs
- Error logs

## Troubleshooting

### Common Issues

#### ChatGPT Report Not Captured
1. Check browser extension is enabled
2. Verify server is running (port 8888)
3. Use manual save as fallback

#### Yahoo Finance Rate Limiting
- DEE-BOT uses Alpaca data to avoid rate limits
- Simplified generator: `generate_dee_bot_report.py`

#### Trade Execution Failures
1. Check Alpaca API credentials in .env
2. Verify market hours
3. Check account buying power
4. Review risk manager rejections in logs

## Scheduled Automation

### Windows Task Scheduler Setup
1. Open Task Scheduler
2. Create Basic Task: "Daily Trading Pipeline"
3. Trigger: Daily at 7:00 AM
4. Action: Start `run_daily_pipelines.bat`
5. Additional settings:
   - Wake computer to run
   - Run whether user logged in or not
   - Run with highest privileges

### Linux/Mac Cron Setup
```cron
0 7 * * 1-5 cd /path/to/ai-stock-trading-bot && python 01_trading_system/automation/daily_pre_market_pipeline.py --bot BOTH
```

## Performance Tracking

### Key Metrics
- Total Portfolio Value
- Daily P&L
- Win Rate
- Sharpe Ratio
- Portfolio Beta (DEE-BOT)
- Sector Diversification

### Report Locations
- Daily: `02_data/reports/daily/`
- Weekly: `02_data/reports/weekly/`
- Research: `02_data/research/reports/`

## Emergency Procedures

### Stop All Trading
```python
# Emergency shutdown script
python 01_trading_system/emergency_shutdown.py
```

### Cancel All Orders
- Log into Alpaca dashboard
- Cancel all open orders
- Set trading restrictions if needed

### Recovery
1. Review logs for issues
2. Check positions and P&L
3. Verify system configuration
4. Resume with reduced position sizes

## Contact & Support
- Alpaca Support: https://alpaca.markets/support
- System Logs: `09_logs/`
- Configuration: See CLAUDE.md for detailed setup