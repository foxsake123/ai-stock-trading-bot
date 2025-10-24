# AI Trading Bot - Quick Start

Get your AI Trading Bot up and running in **5 minutes** with the interactive setup script.

## Prerequisites

✅ Python 3.9+ installed ([Download](https://www.python.org/downloads/))
✅ 1 GB free disk space
✅ Internet connection
✅ API keys ready (see below)

## API Keys Needed

Before starting setup, create accounts and get your API keys:

1. **Anthropic** (Required) - Claude Deep Research
   - Sign up: https://console.anthropic.com/
   - Get key: https://console.anthropic.com/settings/keys
   - Format: `sk-ant-api03-xxxxx`

2. **Alpaca** (Required) - Paper Trading
   - Sign up: https://app.alpaca.markets/signup
   - Get keys: https://app.alpaca.markets/paper/dashboard/overview
   - Format: `PKxxxxx` (API key) + secret key

3. **Financial Datasets** (Required) - Market Data
   - Sign up: https://financialdatasets.ai
   - Get key: https://financialdatasets.ai/dashboard
   - Format: Your API key

4. **Telegram** (Optional) - Mobile Notifications
   - Create bot: Message @BotFather on Telegram
   - Get chat ID: Message @userinfobot
   - Format: `123456:ABCxxxxx` (bot token) + `-1001234567890` (chat ID)

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/foxsake123/ai-stock-trading-bot.git
cd ai-stock-trading-bot
```

### Step 2: Run Interactive Setup

```bash
python scripts/setup.py
```

### Step 3: Follow Prompts

The script will guide you through:
1. ✅ System requirements check
2. 📁 Directory creation (40+ directories)
3. 📦 Dependency installation (50+ packages)
4. 🔑 API key configuration (interactive)
5. ⚙️ Portfolio & strategy setup
6. 📋 Watchlist creation
7. 📝 Logging initialization
8. 🧪 API connection testing
9. ⏰ Automation setup (optional)
10. 🏥 Health check validation

**Total Time**: ~5 minutes (mostly automatic)

### Step 4: Verify Setup

```bash
# Check setup report
cat setup_report.txt

# Run health check
python scripts/health_check.py

# Generate test report
python scripts/daily_pipeline.py --test
```

## First Run

### Option 1: Manual Execution

```bash
# Generate daily research report
python scripts/daily_pipeline.py

# View generated report
cat reports/premarket/latest/claude_research.md
```

### Option 2: Web Dashboard

```bash
# Start dashboard
python web_dashboard.py

# Open browser
# Navigate to: http://localhost:5000
```

### Option 3: Automated (If enabled in setup)

Daily execution happens automatically at 6:00 AM ET:
- Linux: systemd timer
- Windows: Task Scheduler

Check logs: `tail -f logs/app/app_$(date +%Y%m%d).log`

## Configuration

All settings in `.env` and `configs/config.yaml`:

```bash
# Edit environment variables
nano .env

# Edit trading configuration
nano configs/config.yaml
```

**Key Settings**:
- **Portfolio Size**: `trading.portfolio_size: 200000`
- **DEE-BOT Allocation**: `trading.bots.dee_bot.allocation_pct: 50`
- **SHORGAN-BOT Allocation**: `trading.bots.shorgan_bot.allocation_pct: 50`

## Useful Commands

```bash
# Health check
python scripts/health_check.py

# Portfolio status
python scripts/performance/get_portfolio_status.py

# Generate report (test mode)
python scripts/daily_pipeline.py --test

# Generate report (live)
python scripts/daily_pipeline.py

# Start web dashboard
python web_dashboard.py

# Run tests
pytest tests/ -v

# View logs
tail -f logs/app/app_$(date +%Y%m%d).log
```

## Troubleshooting

### Setup Failed?

```bash
# Check Python version (need 3.9+)
python --version

# Check pip
pip --version

# Manually install dependencies
pip install -r requirements.txt

# Run setup again
python scripts/setup.py
```

### API Connection Failed?

```bash
# Verify API keys in .env
cat .env

# Test Anthropic manually
python -c "import anthropic; print('OK')"

# Test Alpaca manually
python -c "from alpaca.trading.client import TradingClient; print('OK')"
```

### Need Help?

1. **Setup Guide**: [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) - Complete documentation
2. **Health Monitoring**: [docs/HEALTH_MONITORING.md](docs/HEALTH_MONITORING.md)
3. **Utils Reference**: [docs/UTILS_DOCUMENTATION.md](docs/UTILS_DOCUMENTATION.md)
4. **Main README**: [README.md](README.md)

## Next Steps

After setup completes:

### Week 1: Paper Trading Validation

- [ ] **Day 1**: Run test report, verify API connections
- [ ] **Day 2-7**: Execute daily pipeline each morning
- [ ] **Monitor**: Check logs for errors daily
- [ ] **Review**: Portfolio performance each evening
- [ ] **Adjust**: Tune configuration based on results

### Week 2-4: Strategy Refinement

- [ ] **Backtest**: Review recommendation accuracy
- [ ] **Optimize**: Adjust position sizing and allocation
- [ ] **Monitor**: Track win rate and Sharpe ratio
- [ ] **Iterate**: Refine watchlists and strategies

### Month 2: Live Trading (If Validated)

- [ ] **Validate**: 30-day paper trading with >60% win rate
- [ ] **Safety**: Review risk limits and kill switches
- [ ] **Deploy**: Switch to live trading with small capital
- [ ] **Scale**: Gradually increase position sizes
- [ ] **Monitor**: Daily performance tracking

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              AI TRADING BOT ARCHITECTURE                │
└─────────────────────────────────────────────────────────┘

Evening (6:00 PM ET):
  ├── Claude Deep Research → reports/premarket/YYYY-MM-DD/
  └── ChatGPT Research (manual) → reports/premarket/YYYY-MM-DD/

Morning (8:30 AM ET):
  ├── Parse Research → Recommendations
  ├── Multi-Agent Validation → 7 agents vote
  ├── Risk Management → Position sizing
  └── Consensus → Approved trades

Market Open (9:30 AM ET):
  ├── Execute Approved Trades → Alpaca API
  └── Monitor Execution → Trade logs

Market Close (4:00 PM ET):
  ├── Portfolio Status → P&L tracking
  └── Performance Report → Telegram/Email

Continuous:
  ├── Health Monitoring → System checks
  └── Alert System → Notifications
```

## Features

✅ **Dual-AI Research**: Claude + ChatGPT consensus
✅ **Multi-Agent Validation**: 7-agent voting system
✅ **Risk Management**: Position sizing, stop losses
✅ **Performance Tracking**: Daily P&L, win rates
✅ **Web Dashboard**: Real-time monitoring
✅ **Automated Execution**: Scheduled daily runs
✅ **Health Monitoring**: Comprehensive system checks
✅ **Multi-Channel Alerts**: Telegram, Email, Slack

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/foxsake123/ai-stock-trading-bot/issues)
- **License**: MIT

---

**Version**: 2.0.0
**Last Updated**: October 23, 2025

🚀 **Happy Trading!**
