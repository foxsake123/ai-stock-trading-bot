# AI Stock Trading Bot
> Professional automated trading system using multi-agent AI consensus

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-active-success)](https://github.com/foxsake123/ai-stock-trading-bot)
[![Trading](https://img.shields.io/badge/trading-paper-orange)](https://alpaca.markets/)

## Overview

An enterprise-grade automated trading system that leverages multiple AI agents to make intelligent trading decisions. The system manages two distinct portfolios with different strategies:

- **DEE-BOT**: Defensive, beta-neutral strategy focused on S&P 100 stocks (LONG-ONLY)
- **SHORGAN-BOT**: Aggressive catalyst-driven strategy for small/mid-cap momentum plays

### Key Features
- 🤖 Multi-agent consensus system (7 specialized agents)
- 📊 Real-time execution via Alpaca Markets API
- 📈 Professional data from Financial Datasets API
- 🔔 Telegram notifications for trade alerts
- ⚡ Fully automated daily execution (9:30 AM ET)
- 📝 Comprehensive risk management and position tracking

## Quick Start

### Prerequisites
```bash
# Python 3.13 or higher required
python --version

# Install dependencies
pip install -r requirements.txt
```

### Configuration
1. Copy `config/api_keys.example.yaml` to `config/api_keys.yaml`
2. Add your API credentials:
   - Alpaca Markets (paper trading)
   - Financial Datasets API
   - Telegram Bot Token

### Running the System
```bash
# Manual execution
python main.py

# Execute daily trades
python scripts/automation/execute_daily_trades.py

# Update positions
python scripts/automation/update_all_bot_positions.py

# Generate reports
python scripts/automation/generate-post-market-report.py

# Generate performance graph (NEW!)
python generate_performance_graph.py

# Generate daily pre-market report (NEW!)
python daily_premarket_report.py          # Production mode
python daily_premarket_report.py --test   # Test mode (no API calls)
```

## Pre-Market Report Generator

The Daily Pre-Market Report Generator creates comprehensive hedge-fund-level trading analysis before market open.

### Installation

1. **Create a `.env` file** in the project root:
```bash
# Required API keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret_key
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

2. **Install dependencies** (if not already installed):
```bash
pip install anthropic python-dotenv pandas pytz yfinance
```

### Features

- **Dual-Strategy Analysis**: SHORGAN-BOT (catalyst-driven) + DEE-BOT (defensive)
- **Market Data Integration**: Real-time VIX, futures, dollar index, treasury yields
- **Stock Recommendations**: Configurable via CSV or default stocks
- **Comprehensive Prompts**: 7,000+ character hedge-fund-level prompts
- **Test Mode**: Generate mock reports without API calls

### Usage

#### Test Mode (No API Calls)
```bash
python daily_premarket_report.py --test
```
- Generates mock report with structure
- No Claude API calls (free testing)
- Validates all components
- Saves report files

#### Production Mode (Full Analysis)
```bash
python daily_premarket_report.py
```
- Fetches real-time market data
- Calls Claude Sonnet 4 for analysis
- Generates comprehensive 3,000-4,000 word report
- Saves to `reports/premarket/`

### Configuration

#### Default Stocks (8 positions)

**SHORGAN-BOT** (catalyst-driven):
- SNDX: Oct 25 PDUFA for Revuforj
- GKOS: Oct 20 PDUFA for Epioxa
- ARWR: Nov 18 PDUFA for plozasiran
- ALT: Nov 11 Q3 earnings + IMPACT data
- CAPR: Q4 HOPE-3 Phase 3 data

**DEE-BOT** (defensive):
- DUK: Long-term defensive utility
- ED: Long-term defensive utility
- PEP: Long-term defensive consumer staples

#### Custom Recommendations

Create `data/daily_recommendations.csv`:
```csv
Ticker,Strategy,Catalyst,Risk,Conviction
NVDA,SHORGAN,Q4 earnings beat,7,8
AAPL,DEE,Long-term defensive tech,5,9
```

### Output Files

```
reports/premarket/
├── premarket_report_2025-10-14.md       # Dated report
├── latest.md                             # Latest report (symlink)
└── premarket_metadata_2025-10-14.json   # Metadata
```

### Report Sections

1. **Executive Summary Table** - Market sentiment, VIX, catalysts
2. **Overnight Market Context** - Asia/Europe/US futures
3. **SHORGAN-BOT Recommendations** - 5-7 catalyst trades
4. **DEE-BOT Recommendations** - 3-5 defensive stocks
5. **Portfolio Management** - Cash, risk limits, rebalancing
6. **Execution Guidance** - Pre-market, open, intraday, EOD
7. **Alternative Data** - Sentiment, supply chain, insider activity
8. **Risk Disclosures** - Standard disclaimers

### Scheduling

**Windows Task Scheduler**:
```bash
# Run daily at 6:00 PM ET (generates report for next trading day)
schtasks /create /tn "PreMarket Report" /tr "python C:\path\to\daily_premarket_report.py" /sc daily /st 18:00
```

**Linux/Mac Cron**:
```bash
# Run daily at 6:00 PM ET
0 18 * * * cd /path/to/project && python daily_premarket_report.py
```

### Troubleshooting

**Error: ANTHROPIC_API_KEY not set**
- Create `.env` file with your API key
- Get key from: https://console.anthropic.com/

**Error: Market data failed (0/6 indicators)**
- Yahoo Finance rate limiting (normal)
- Reports still generate with partial data
- Wait 1-2 minutes between runs

**Error: Trading date calculation failed**
- Check `schedule_config.py` for market holidays
- Update holidays list for new year

## System Architecture

### Trading Flow
```
Market Data → AI Agents → Consensus → Risk Review → Execution → Monitoring
     ↓           ↓           ↓           ↓            ↓           ↓
  Financial  7 Specialist  Weighted    Position    Alpaca API  Real-time
  Datasets    Agents       Voting      Sizing                  Tracking
```

### Multi-Agent System
| Agent | Role | Weight |
|-------|------|--------|
| Fundamental | Company analysis | 20% |
| Technical | Chart patterns | 20% |
| News | Headlines & events | 15% |
| Sentiment | Social media trends | 10% |
| Bull | Optimistic view | 15% |
| Bear | Pessimistic view | 15% |
| Risk | Veto power | 5% |

## Portfolio Strategies

### DEE-BOT (Defensive)
- **Capital**: $100,000
- **Strategy**: LONG-ONLY, beta-neutral
- **Focus**: S&P 100 dividend aristocrats
- **Risk**: 0.75% daily loss limit
- **Positions**: 8-12 holdings
- **Rebalance**: Monthly or 15% drift

### SHORGAN-BOT (Aggressive)
- **Capital**: $100,000
- **Strategy**: Catalyst-driven momentum
- **Focus**: Small/mid-cap with events
- **Risk**: 8% stop loss per position
- **Positions**: 15-25 holdings
- **Targets**: 15-25% profit taking

## Daily Operation

### Automated Schedule
- **06:45 AM**: Data ingestion and analysis
- **08:45 AM**: Risk review and position sizing
- **09:30 AM**: Automated trade execution
- **11:00 AM**: Position monitoring begins
- **04:30 PM**: Post-market report generation

### Manual Tasks
1. Create `TODAYS_TRADES_YYYY-MM-DD.md` (if not auto-generated)
2. Review execution logs for failures
3. Monitor critical positions

## Performance

### Current Statistics (Sept 29, 2025)
```
Combined Portfolio: $210,285 (+5.14%)
DEE-BOT:           $104,454 (+4.45%)
SHORGAN-BOT:       $105,832 (+5.83%)
Win Rate: 65%
Sharpe Ratio: 1.4
Max Drawdown: -8.3%
```

### Performance Tracking
Professional visualization system benchmarking both bots against S&P 500:
- **Generate Graph**: `python generate_performance_graph.py`
- **Documentation**: See [docs/PERFORMANCE_TRACKING.md](docs/PERFORMANCE_TRACKING.md)
- **Methodology**: Based on [ChatGPT-Micro-Cap-Experiment](https://github.com/LuckyOne7777/ChatGPT-Micro-Cap-Experiment)

### Top Performers
- RGTI: +94% (quantum computing)
- SRRK: +21% (biotech catalyst)
- ORCL: +18% (cloud expansion)

## Project Structure

```
ai-stock-trading-bot/
├── agents/                 # Multi-agent trading system
├── scripts/
│   ├── automation/        # Core trading scripts
│   ├── utilities/         # Helper utilities
│   └── windows/           # Windows batch files
├── data/
│   ├── daily/             # Daily positions and performance
│   ├── research/          # Claude/ChatGPT research
│   └── reports/           # Execution reports
├── docs/
│   ├── strategies/        # Trading strategies
│   ├── reports/           # Daily/weekly reports
│   ├── archive/           # Archived documentation
│   └── session-summaries/ # Development logs
├── configs/               # Configuration files
├── tests/                 # Test suite
└── main.py               # Entry point
```

## Risk Management

### Position Limits
- Max position size: 10% of portfolio
- Max sector exposure: 30%
- Daily loss limit: 3% (circuit breaker)
- Stop losses on all positions

### Monitoring
- Real-time position tracking
- Telegram alerts for trades
- Automated stop loss triggers
- Daily performance reports

## Development

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/integration/
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Documentation

- [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- [DEE-BOT Strategy](docs/DEE_BOT_STRATEGY.md)
- [SHORGAN Strategy](docs/SHORGAN_STRATEGY.md)
- [API Documentation](docs/API_REFERENCE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Support

- **Issues**: [GitHub Issues](https://github.com/foxsake123/ai-stock-trading-bot/issues)
- **Documentation**: See `/docs` folder
- **Updates**: Via Telegram bot notifications

## License

Private repository - All rights reserved

## Disclaimer

This is a paper trading system for educational purposes. Not financial advice. Always conduct your own research before making investment decisions.

---

**Version**: 2.0.0
**Last Updated**: September 29, 2025
**Status**: 🟢 Active Development