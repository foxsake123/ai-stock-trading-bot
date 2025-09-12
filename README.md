# AI Stock Trading Bot System

## 📊 Live Performance (as of September 12, 2025, 11:45 AM ET)

| Metric | Value | Status |
|--------|-------|--------|
| **Total Portfolio Value** | **$205,480.99** | 🟢 +2.74% |
| **Today's P&L** | +$1,385.55 | 🟢 Excellent |
| **Unrealized P&L** | +$5,480.99 | 🟢 Strong |
| **Active Positions** | 22 | ⚡ Active |
| **Win Rate** | 68% | 🎯 Above Target |
| **Leverage Used** | ~2X | 📊 Beta-Neutral |

## Overview

Professional multi-agent AI trading system featuring two specialized bots:
- **DEE-BOT**: Conservative S&P 100 institutional-grade trading
- **SHORGAN-BOT**: Aggressive catalyst-driven opportunity trading

Built on a sophisticated 7-agent consensus framework with real-time risk management and automated trade execution via Alpaca Paper Trading API.

## 🏗️ System Architecture

```
ai-stock-trading-bot/
├── 01_trading_system/      # Core trading logic and bots
│   ├── agents/            # 7 specialized AI agents
│   ├── bots/              # DEE-BOT and SHORGAN-BOT
│   └── execution/         # Trade execution modules
│
├── 02_data/               # Data storage and research
│   ├── market/            # Historical and real-time data
│   ├── portfolio/         # Performance tracking
│   └── research/          # Analysis and reports
│
├── 03_config/             # Configuration and settings
├── 04_risk/               # Risk management system
├── 05_backtesting/        # Strategy testing
├── 06_utils/              # Utilities and helpers
├── 07_docs/               # Documentation
├── 08_frontend/           # Web dashboard (React)
└── 09_logs/               # System and trading logs
```

## 🤖 Trading Bots

### DEE-BOT (Beta-Neutral Strategy with 2X Leverage)
- **Current Value**: $101,690.62 (+1.69%)
- **Strategy**: Beta-neutral S&P 100 multi-agent consensus
- **Risk Profile**: Conservative with leverage (3% stop-loss)
- **Leverage**: 2X target (beta-adjusted positions)
- **Portfolio Beta**: ~1.0 (market neutral)
- **Best Position**: AAPL (+3.14%)
- **API**: Alpaca Paper Trading

### SHORGAN-BOT (Aggressive Strategy)
- **Current Value**: $103,398.18 (+3.40%)
- **Strategy**: Catalyst event trading
- **Risk Profile**: Aggressive (4% stop-loss)
- **Focus**: Small/mid-cap opportunities
- **Best Position**: ORCL (+32.33%)
- **API**: Alpaca Paper Trading

## 🧠 Multi-Agent Consensus System

Seven specialized AI agents collaborate to make trading decisions:

| Agent | Role | Focus Area |
|-------|------|------------|
| **Fundamental Analyst** | Valuation | P/E ratios, earnings, financials |
| **Technical Analyst** | Charts | RSI, MACD, support/resistance |
| **News Analyst** | Events | Breaking news, market impact |
| **Sentiment Analyst** | Social | Reddit, Twitter, retail sentiment |
| **Bull Researcher** | Opportunities | Growth catalysts, upside |
| **Bear Researcher** | Risks | Downside protection, warnings |
| **Risk Manager** | Control | Position sizing, veto power |

**Consensus Requirements**: 60% agent agreement with Risk Manager override capability

## ⚡ Quick Start

### Prerequisites
```bash
# Python 3.11+ required
pip install -r requirements.txt
```

### Configuration
Create `.env` file with your API keys:
```env
# DEE-BOT Alpaca Credentials
DEE_BOT_API_KEY=your_api_key
DEE_BOT_SECRET_KEY=your_secret_key

# SHORGAN-BOT Alpaca Credentials  
SHORGAN_BOT_API_KEY=your_api_key
SHORGAN_BOT_SECRET_KEY=your_secret_key

# Market Data
ALPHA_VANTAGE_API_KEY=your_api_key

# Notifications
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Running the System

#### Generate Trading Recommendations
```bash
# DEE-BOT multi-agent analysis
python 01_trading_system/generate_dee_bot_recommendations.py

# SHORGAN-BOT catalyst scanner
python 01_trading_system/generate_shorgan_bot_recommendations.py
```

#### Execute Trades
```bash
# Execute DEE-BOT trades
python 01_trading_system/execute_dee_bot_trades.py

# Execute SHORGAN-BOT trades
python 01_trading_system/execute_shorgan_bot_trades.py
```

#### Monitor Portfolio
```bash
# Real-time portfolio monitoring
python 04_risk/portfolio_monitor.py

# Send daily report to Telegram
python 06_utils/send_daily_report.py
```

## 📈 Daily Trading Schedule

| Time (ET) | Activity | Description |
|-----------|----------|-------------|
| **8:30 AM** | Pre-Market Analysis | Generate recommendations |
| **9:30 AM** | Market Open | Execute opening trades |
| **10:00 AM** | Position Check | Monitor and adjust |
| **12:00 PM** | Midday Review | Risk assessment |
| **3:30 PM** | EOD Preparation | Final adjustments |
| **4:15 PM** | Daily Report | Telegram notification |
| **4:30 PM** | Post-Market | Performance analysis |

## 🛡️ Risk Management

### Position Limits
- Maximum 5% of portfolio per position
- Maximum 20% sector concentration
- Daily loss limit: 5% circuit breaker
- Mandatory stop-loss on all positions

### Current Risk Metrics
- **Portfolio Exposure**: 123.7% (leveraged via margin)
- **Largest Position**: NVDA (21.5% of DEE-BOT)
- **Average Position Return**: +2.0%
- **Risk Warnings**: High exposure, concentration alerts

## 📊 Performance Tracking

### Key Metrics Tracked
- Daily/Weekly/Monthly P&L
- Sharpe Ratio
- Maximum Drawdown
- Win Rate
- Risk-Adjusted Returns

### Recent Performance
- **September 10**: +$3,739.78 (+1.87%)
- **September 11**: +$78.63 (+0.04%)
- **Week-to-Date**: +$4,818.41 (+2.41%)

## 📱 Notifications

Daily performance reports are automatically sent via Telegram at 4:15 PM ET including:
- Portfolio value and P&L
- Top performing positions
- New trades executed
- Risk alerts
- Market status

## 🔧 Advanced Features

### Backtesting
```python
from 05_backtesting import backtest_strategy
results = backtest_strategy('dee_bot', start_date='2024-01-01')
```

### Custom Agents
Extend the base agent class to create custom analysis agents:
```python
from 01_trading_system.agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def analyze(self, ticker):
        # Your custom analysis logic
        return recommendation
```

## 📚 Documentation

- [System Architecture](07_docs/SYSTEM_ARCHITECTURE.md)
- [Trading Strategies](07_docs/TRADING_STRATEGIES.md)
- [API Documentation](07_docs/API_DOCUMENTATION.md)
- [Risk Management Guide](07_docs/RISK_MANAGEMENT.md)
- [Session Continuation Guide](07_docs/SESSION_CONTINUATION_GUIDE.md)

## 🚀 Upcoming Features

- [ ] Options trading capability
- [ ] Real-time WebSocket data feeds
- [ ] Machine learning optimization
- [ ] Advanced portfolio optimization
- [ ] Live trading mode (currently paper only)
- [ ] Web dashboard completion

## ⚠️ Disclaimer

This is a paper trading system for educational and research purposes. Not financial advice. Always perform your own due diligence before making investment decisions.

## 📄 License

Proprietary - All rights reserved

## 🤝 Support

For issues or questions, please check the [documentation](07_docs/) or create an issue on GitHub.

---

**System Status**: 🟢 OPERATIONAL | **Last Updated**: September 11, 2025, 9:55 AM ET