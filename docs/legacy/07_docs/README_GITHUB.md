# AI Stock Trading Bot Research System

## 🚀 Overview
An advanced multi-agent AI trading system that generates comprehensive market research, technical analysis, and trading signals. Inspired by the ChatGPT Micro-Cap Experiment, this system combines cutting-edge AI with systematic trading methodologies.

## 📊 Features

### Deep Research Indexes
- Daily comprehensive market analysis reports
- Technical signal generation with confidence scores
- AI-driven trade recommendations
- Risk assessment and portfolio optimization
- Sector rotation analysis
- Market regime detection

### Multi-Agent Architecture
- **7 Specialized Trading Agents**:
  - Fundamental Analyst
  - Technical Analyst
  - News Analyst
  - Sentiment Analyst
  - Bull Researcher
  - Bear Researcher
  - Risk Manager (with veto power)

### Data Integration
- **Financial Datasets API**: Real-time market data
- **Yahoo Finance**: Historical price data
- **Alpha Vantage**: Technical indicators
- **Custom Scrapers**: News and sentiment

### Automated Reporting
- Pre-market analysis (8:30 AM ET)
- Midday market updates (12:30 PM ET)
- End-of-day reports (4:30 PM ET)
- Weekly performance summaries (Friday 5:00 PM ET)

## 📁 Repository Structure

```
ai-stock-trading-bot/
├── deep_research_indexes/      # Daily research reports
│   ├── 2025/
│   │   └── 01/                # January 2025 reports
│   ├── README.md
│   └── INDEX.md               # Master index
│
├── dee_bot/                   # DEE-BOT trading system
│   ├── agents/               # AI trading agents
│   ├── data/                # Data providers
│   └── communication/       # Agent coordination
│
├── shorgan_bot/              # SHORGAN-BOT system
│   ├── agents/
│   ├── brokers/
│   └── portfolio/
│
├── automated_research_reporter.py
├── deep_research_generator.py
├── schedule_research_reports.py
├── trading_logger.py
└── README.md
```

## 🔧 Installation

### Prerequisites
- Python 3.11+
- Financial Datasets API key
- Alpaca trading account (for paper trading)

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/ai-stock-trading-bot.git
cd ai-stock-trading-bot

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Run initial setup
python setup.py
```

## 🚦 Quick Start

### Generate Research Report
```bash
# Generate today's deep research index
python deep_research_generator.py

# Run automated scheduler
python schedule_research_reports.py
```

### View Reports
Reports are generated in `deep_research_indexes/YYYY/MM/` directory.

## 📈 Performance Tracking

### Trade Logging
All trades are logged in CSV format compatible with performance analysis:
- Entry/exit prices
- Position sizes
- P&L tracking
- Risk metrics

### Visualization
```bash
# Generate performance graphs
python automated_research_reporter.py
```

## 🤖 AI Agents

Each agent specializes in specific analysis:

| Agent | Focus | Key Metrics |
|-------|-------|-------------|
| Fundamental | Valuation, earnings | P/E, ROE, debt ratios |
| Technical | Chart patterns | RSI, MACD, Bollinger Bands |
| News | Breaking news impact | Sentiment scores |
| Sentiment | Social media trends | Put/call ratios |
| Bull | Growth opportunities | Momentum indicators |
| Bear | Risk identification | Downside scenarios |
| Risk Manager | Portfolio protection | VaR, position sizing |

## 📊 Sample Research Output

### Daily Research Index Structure
```markdown
# Deep Research Index - January 10, 2025

## Market Overview
- Trend: Bullish
- Volatility: Medium
- Sentiment: Neutral

## Technical Signals
1. AAPL - Breakout above resistance
2. MSFT - MACD crossover
3. NVDA - Oversold bounce

## AI Recommendations
[Detailed trade setups with entry/exit points]

## Risk Assessment
[Portfolio risk metrics and alerts]
```

## 🔐 Risk Management

- **Position Sizing**: Max 5% per position
- **Portfolio Risk**: Max 2% daily drawdown
- **Stop Loss**: Mandatory on all positions
- **Correlation Limits**: Sector concentration < 40%

## 📝 Configuration

### API Keys Required
```env
FINANCIAL_DATASETS_API_KEY=your_key_here
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
```

### Trading Parameters
Edit `config/settings.py`:
- Initial capital
- Risk limits
- Position sizing
- Trading hours

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Test API connections
python test_fd_api.py

# Backtest strategies
python backtesting/backtest_engine.py
```

## 📊 Data Sources

- **Financial Datasets API**: Primary market data
- **Yahoo Finance**: Backup data source
- **Alpha Vantage**: Economic indicators
- **News APIs**: Benzinga, NewsAPI

## 🚀 Deployment

### Local Development
```bash
python main.py --mode development
```

### Production
```bash
# Using Docker
docker-compose up -d

# Using systemd
sudo systemctl start trading-bot
```

## 📈 Performance Metrics

System tracks:
- Sharpe Ratio
- Sortino Ratio
- Maximum Drawdown
- Win Rate
- Profit Factor
- Risk-adjusted returns

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## ⚠️ Disclaimer

This software is for educational purposes only. Not financial advice. Trading involves risk of loss. Past performance does not guarantee future results.

## 📄 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- Inspired by [ChatGPT Micro-Cap Experiment](https://github.com/LuckyOne7777/ChatGPT-Micro-Cap-Experiment)
- Financial Datasets API for market data
- Anthropic and OpenAI for LLM capabilities

## 📧 Contact

- GitHub Issues: [Report bugs](https://github.com/yourusername/ai-stock-trading-bot/issues)
- Email: your.email@example.com

---

**Last Updated**: January 10, 2025  
**Version**: 1.0.0  
**Status**: Active Development