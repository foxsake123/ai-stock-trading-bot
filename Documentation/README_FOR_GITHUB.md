# 🤖 AI Multi-Agent Stock Trading System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Paper Trading](https://img.shields.io/badge/Trading-Paper%20Mode-orange)](https://alpaca.markets)

> **⚠️ IMPORTANT NOTICE**: This system starts in **PAPER TRADING** mode by default. No real money trades are executed without explicit configuration and extensive testing.

A sophisticated multi-agent AI trading system combining deep research, technical analysis, and automated execution with comprehensive safety controls.

## 🎯 Overview

This project implements a multi-agent trading system where specialized AI agents work together to:
- Analyze market conditions using real-time data
- Generate trading signals based on technical, fundamental, and sentiment analysis  
- Execute trades with configurable automation levels
- Track portfolio performance with detailed reporting
- Generate comprehensive research reports

**Inspired by**: [ChatGPT Micro-Cap Experiment](https://github.com/LuckyOne7777/ChatGPT-Micro-Cap-Experiment) which achieved +29.22% returns vs S&P 500's +4.11% using AI-driven decisions.

## 🚀 Key Features

### Multi-Agent Architecture
- **Fundamental Analyst**: Company financials, earnings, economic indicators
- **Technical Analyst**: Chart patterns, indicators (RSI, MACD, Bollinger Bands)  
- **News Analyst**: Real-time news impact assessment
- **Sentiment Analyst**: Social media and options flow analysis
- **Bull/Bear Researchers**: Opposing viewpoints for balanced analysis
- **Risk Manager**: Portfolio risk oversight with veto power

### Safety-First Design
- **Paper Trading Default**: No real money at risk initially
- **Progressive Automation**: Manual → Semi-Auto → Full Auto
- **Risk Controls**: Position limits, daily loss limits, stop-losses
- **Emergency Stop**: Multiple ways to halt trading immediately

### Comprehensive Reporting
- **Daily Research Reports**: Market analysis and trade recommendations
- **Portfolio Tracking**: Real-time P&L, positions, performance metrics
- **Trade Logging**: Complete audit trail of all decisions
- **Performance Analytics**: Sharpe ratio, drawdown, win rate analysis

## 📁 Repository Structure

```
ai-stock-trading-bot/
├── 📊 Trading Reports/
│   ├── Daily Research/           # Daily market analysis reports
│   ├── Weekly Summaries/         # Weekly performance summaries  
│   ├── Monthly Reviews/          # Monthly deep dive analysis
│   └── Performance Charts/       # Visual performance tracking
│
├── 📈 Portfolio Data/
│   ├── Trade Logs/              # Complete trade execution history
│   ├── Position Tracking/       # Current and historical positions
│   ├── Performance Metrics/     # P&L, returns, risk metrics
│   └── Market Data/            # Price data and technical indicators
│
├── 🤖 Agents/
│   ├── fundamental_analyst.py   # Financial analysis agent
│   ├── technical_analyst.py     # Technical analysis agent
│   ├── news_analyst.py         # News impact assessment
│   ├── sentiment_analyst.py    # Social sentiment analysis
│   ├── bull_researcher.py      # Bullish research agent
│   ├── bear_researcher.py      # Bearish research agent
│   └── risk_manager.py         # Risk management oversight
│
├── 🔧 Trading Engine/
│   ├── automated_trade_executor.py    # Main execution system
│   ├── trade_signal_generator.py     # Signal processing
│   ├── portfolio_manager.py          # Portfolio tracking
│   └── risk_management.py            # Risk controls
│
├── 📊 Data Sources/
│   ├── financial_datasets_api.py     # Financial Datasets API
│   ├── market_data.py                # Yahoo Finance, Alpha Vantage
│   ├── news_feeds.py                 # News data ingestion
│   └── sentiment_data.py             # Social media data
│
├── 📋 Configuration/
│   ├── .env.example                  # Environment variables template
│   ├── trading_rules.yaml            # Trading rules and parameters
│   └── AUTOMATION_CONFIG.md          # Safety and setup guide
│
├── 🔍 Research Reports/             # Deep research analysis
│   └── YYYY/MM/                     # Organized by year/month
│       ├── research_index_YYYYMMDD.md
│       └── charts/
│
├── 📱 Notifications/
│   ├── telegram_bot.py              # Telegram notifications
│   ├── email_reports.py             # Email summaries
│   └── slack_integration.py         # Slack alerts
│
├── 🧪 Testing/
│   ├── backtesting/                 # Historical strategy testing
│   ├── paper_trading_results/       # Paper trading performance
│   └── unit_tests/                  # Code testing
│
└── 📚 Documentation/
    ├── API_DOCUMENTATION.md          # API usage guides
    ├── AGENT_ARCHITECTURE.md         # Multi-agent system design
    ├── RISK_MANAGEMENT.md            # Risk controls explained
    └── DEPLOYMENT_GUIDE.md           # Production deployment
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone repository
git clone https://github.com/yourusername/ai-stock-trading-bot.git
cd ai-stock-trading-bot

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Configure API Keys
```bash
# Edit .env file with your API keys
ALPACA_API_KEY=your_paper_trading_key
ALPACA_SECRET_KEY=your_paper_secret_key
FINANCIAL_DATASETS_API_KEY=your_fd_api_key
```

### 3. Test Connection
```bash
# Verify Alpaca paper trading connection
python test_alpaca_connection.py

# Check system status
python check_trading_status.py
```

### 4. Run First Analysis
```bash
# Generate research report (paper mode)
python generate_daily_research.py
```

## 📊 Performance Tracking

### Key Metrics
- **Total Return**: Portfolio performance vs benchmark
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades

### Reporting Schedule
- **Daily**: Market analysis and trade signals (8:30 AM)
- **Midday**: Portfolio updates (12:30 PM)
- **End of Day**: Performance summary (4:30 PM)
- **Weekly**: Comprehensive review (Friday 5:00 PM)

## 🛡️ Safety Features

### Default Safety Mode
- **Paper Trading Only**: No real money at risk
- **Manual Approval Required**: Human oversight for all trades
- **Position Limits**: Maximum position sizes enforced
- **Daily Loss Limits**: Circuit breakers prevent large losses

## ⚠️ Disclaimer

**This software is for educational and research purposes only.**

- Past performance does not guarantee future results
- All trading involves risk of loss
- Start with paper trading and small positions
- Never risk more than you can afford to lose

## 🏆 Acknowledgments

- Inspired by the [ChatGPT Micro-Cap Experiment](https://github.com/LuckyOne7777/ChatGPT-Micro-Cap-Experiment)
- Built with [Alpaca Markets](https://alpaca.markets) for trading execution  
- Market data provided by [Financial Datasets](https://financialdatasets.ai)

---

**⭐ Star this repo if you find it helpful!**