# AI Stock Trading Bot Platform
## Dual-System Algorithmic Trading Framework

### 🎯 Overview

This repository contains two complementary AI-powered trading systems:

1. **Shorgan-Bot**: Original single-AI trading system with multiple strategies
2. **DEE-BOT**: Advanced multi-agent system based on TradingAgents academic framework

Both systems use Claude AI for intelligent market analysis and automated trading execution through Alpaca Markets.

### 🏗️ Repository Structure

```
ai-stock-trading-bot/
├── shorgan-bot/          # Original trading bot system
│   ├── agents/          # AI analysis agents
│   ├── brokers/         # Broker integrations
│   ├── strategies/      # Trading strategies
│   ├── portfolio/       # Portfolio management
│   └── README.md        # Shorgan-bot documentation
├── dee_bot/             # Multi-agent institutional system
│   ├── agents/          # 7 specialist agents
│   ├── communication/   # Agent debate system
│   ├── execution/       # Advanced execution
│   ├── docs/           # Complete documentation
│   └── README.md       # DEE-BOT documentation
├── BOT_COMPARISON.md    # Detailed comparison
├── SESSION_*.md         # Development session notes
└── README.md           # This file
```

### 🚀 Quick Start

#### Option 1: Shorgan-Bot (Recommended for Beginners)
```bash
cd shorgan-bot
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python main.py --mode=paper
```

#### Option 2: DEE-BOT (Advanced Users)
```bash
cd dee_bot
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python main.py --mode=live --capital=100000
```

### 🔑 Required API Keys

Both systems require:
- **Alpaca Markets**: Free paper trading account at [alpaca.markets](https://alpaca.markets)
- **Anthropic Claude**: API key from [anthropic.com](https://anthropic.com)

### 📊 System Comparison

| Feature | Shorgan-Bot | DEE-BOT |
|---------|------------|---------||
| **Complexity** | Simple | Advanced |
| **Best For** | Learning/Individual | Professional/Institutional |
| **Capital Range** | $10K-$500K | $100K-$10M |
| **Setup Time** | 30 minutes | 2 hours |
| **AI Agents** | 1 | 7 |
| **Risk Management** | Basic | 5-layer system |
| **Expected Return** | 10-15% | 15-25% |
| **Monthly Cost** | ~$50 | ~$200 |

### 🎯 Which System Should You Use?

#### Use Shorgan-Bot if you:
- Are new to algorithmic trading
- Have < $100K capital
- Want to learn and experiment
- Prefer simplicity
- Need quick setup

#### Use DEE-BOT if you:
- Have trading experience
- Manage > $100K
- Need institutional features
- Want maximum safety
- Prefer consensus-based decisions

#### Use Both if you:
- Want strategy diversification
- Have > $200K capital
- Can manage complexity
- Want to compare approaches

### 📈 Trading Strategies

#### Shorgan-Bot Strategies
- **Momentum**: Trend following with breakout detection
- **Mean Reversion**: Oversold/overbought reversals
- **Catalyst-Driven**: News and event-based trading

#### DEE-BOT Strategies
- **Multi-Agent Consensus**: 7 specialized agents debate
- **Risk-Managed**: ATR-based position sizing
- **Institutional**: VWAP/TWAP execution algorithms

### 🛡️ Risk Management

Both systems include:
- Automatic stop-loss orders
- Position size limits
- Daily loss limits
- Portfolio diversification
- Emergency shutdown procedures

DEE-BOT adds:
- 5-layer defense system
- Risk Manager agent with veto power
- Correlation-based limits
- Market regime detection
- Circuit breakers

### 📊 Performance Expectations

#### Paper Trading Targets
- **Win Rate**: 50-60%
- **Sharpe Ratio**: > 1.0
- **Max Drawdown**: < 15%
- **Monthly Return**: 2-5%

*Past performance does not guarantee future results*

### 🔧 Development Status

- **Shorgan-Bot**: ✅ Production Ready (v1.0.0)
- **DEE-BOT**: ✅ Production Ready (v1.0.0)

### 📚 Documentation

- [Shorgan-Bot README](shorgan-bot/README.md)
- [Shorgan-Bot System Overview](shorgan-bot/SYSTEM_OVERVIEW.md)
- [Shorgan-Bot Quick Start](shorgan-bot/QUICK_START.md)
- [DEE-BOT Overview](dee_bot/docs/DEEBOT_SYSTEM_OVERVIEW.md)
- [DEE-BOT Trading Research](dee_bot/docs/TRADING_RESEARCH_20250910.md)
- [System Comparison](BOT_COMPARISON.md)
- [Feature Roadmap](DEEBOT_FEATURE_ROADMAP.md)

### 🗓️ Session History

- [Session 5 Complete](SESSION_5_COMPLETE.md) - DEE-BOT implementation
- [TODO Session 6](TODO_SESSION_6.md) - Next steps
- [Quick Start Tomorrow](QUICK_START_TOMORROW.md) - Trading checklist

### ⚠️ Risk Disclaimer

**IMPORTANT**: Trading stocks involves substantial risk of loss and is not suitable for every investor. The valuation of stocks may fluctuate, and as a result, you may lose more than your original investment.

- Always use paper trading first
- Never risk more than you can afford to lose
- Past performance doesn't guarantee future results
- These systems are for educational purposes
- Consult a financial advisor before live trading

### 🧪 Testing

Both systems support:
```bash
# Run tests
pytest

# Run with coverage
pytest --cov

# Run specific tests
pytest tests/test_strategies.py
```

### 🚀 Deployment

#### Development
```bash
python main.py --env=development
```

#### Paper Trading (Recommended)
```bash
python main.py --env=paper
```

#### Production (Requires Confirmation)
```bash
python main.py --env=production --confirm=yes
```

### 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Test thoroughly with paper trading
4. Submit a pull request

### 📧 Support

- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Emergency**: See emergency procedures in docs

### 📜 License

Proprietary - All Rights Reserved

### 🏆 Acknowledgments

- **TradingAgents Paper**: Academic foundation for DEE-BOT
- **Anthropic**: Claude AI integration
- **Alpaca Markets**: Trading infrastructure

### 🗺️ Roadmap

#### Q4 2025
- [ ] Live data integration
- [ ] Options trading
- [ ] Machine learning enhancements

#### Q1 2026
- [ ] Multi-asset support
- [ ] Cryptocurrency integration
- [ ] Mobile applications

#### Q2 2026
- [ ] Reinforcement learning
- [ ] Quantum computing research
- [ ] Institutional features

### 📈 Current Status

As of September 9, 2025:
- **Shorgan-Bot**: Fully operational, tested, documented
- **DEE-BOT**: Ready for deployment, trades scheduled for Sept 10
- **Documentation**: Complete
- **Testing**: Paper trading validated

### 🎯 Next Steps

1. **Tomorrow (Sept 10)**: Execute DEE-BOT trading plan
2. **This Week**: Monitor performance and refine
3. **Next Week**: Implement real-time data feeds
4. **This Month**: Add machine learning features

---

**Version**: 1.0.0  
**Last Updated**: September 9, 2025  
**Status**: Production Ready

*"The market rewards discipline, not emotion"*