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
python scripts-and-data/automation/execute_daily_trades.py

# Update positions
python scripts-and-data/automation/update_all_bot_positions.py

# Generate reports
python scripts-and-data/automation/generate-post-market-report.py
```

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
Portfolio Value: $210,255
Total Return: +5.13% ($10,255)
Win Rate: 65%
Sharpe Ratio: 1.4
Max Drawdown: -8.3%
```

### Top Performers
- RGTI: +94% (quantum computing)
- SRRK: +21% (biotech catalyst)
- ORCL: +18% (cloud expansion)

## Project Structure

```
ai-stock-trading-bot/
├── agents/                 # Multi-agent trading system
├── scripts-and-data/
│   ├── automation/        # Core trading scripts
│   ├── daily-csv/         # Position tracking
│   └── trade-logs/        # Execution history
├── docs/
│   ├── strategies/        # Trading strategies
│   ├── reports/           # Daily/weekly reports
│   └── sessions/          # Development logs
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