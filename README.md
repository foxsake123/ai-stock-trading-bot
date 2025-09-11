# AI Stock Trading Bot System

## Overview
Professional multi-agent AI trading system featuring DEE-BOT and SHORGAN-BOT, built on the TradingAgents framework with comprehensive market analysis and risk management.

## Repository Structure

```
ai-stock-trading-bot/
├── Core_Trading/           # Main trading engine and execution
│   ├── trading_engine.py   # Central orchestrator
│   └── [execution modules]
│
├── Bot_Strategies/         # Individual bot strategies
│   ├── DEE-BOT/           # S&P 100 multi-agent consensus bot
│   │   ├── sp100_scanner.py
│   │   └── [order placement]
│   └── SHORGAN-BOT/       # Catalyst event trading bot
│       └── [catalyst trades]
│
├── Multi-Agent_System/     # 7-agent collaborative framework
│   ├── agents/            # Specialized analysis agents
│   └── communication/     # Inter-agent messaging
│
├── Research_Reports/       # Market research and analysis
│   ├── pre_market_report.py    # Daily 8:30 AM analysis
│   ├── post_market_report.py   # Daily 4:30 PM review
│   └── weekly_analysis_report.py # Friday comprehensive review
│
├── Market_Data/           # Data collection and processing
├── Performance_Tracking/  # Portfolio monitoring and metrics
├── risk_management/       # Risk controls and position sizing
├── Configuration/         # Settings and universe definitions
└── Documentation/         # Guides and documentation
```

## Trading Bots

### DEE-BOT
- **Strategy**: S&P 100 multi-agent consensus trading
- **Universe**: S&P 100 large-cap stocks
- **Approach**: Conservative, consensus-based decisions
- **Risk**: 2-3% stop loss, 5-6% profit targets
- **Capital Allocation**: 60%

### SHORGAN-BOT  
- **Strategy**: Catalyst event trading
- **Universe**: All US equities
- **Approach**: Aggressive, event-driven
- **Risk**: Wider stops for volatility
- **Capital Allocation**: 40%

## Multi-Agent System

The system employs 7 specialized AI agents:

1. **Fundamental Analyst** - Company financials and valuation
2. **Technical Analyst** - Chart patterns and indicators
3. **News Analyst** - Real-time news impact assessment
4. **Sentiment Analyst** - Social media and market sentiment
5. **Bull Researcher** - Positive catalysts and opportunities
6. **Bear Researcher** - Risk identification and warnings
7. **Risk Manager** - Portfolio risk oversight (veto power)

## Daily Schedule

- **8:30 AM ET**: Pre-market analysis and signals
- **9:30 AM ET**: Execute opening trades
- **Intraday**: Monitor positions every 30 minutes
- **4:30 PM ET**: Post-market analysis and review
- **Friday 5:00 PM ET**: Weekly comprehensive report

## Research Reports

### Pre-Market Daily (8:30 AM)
- Futures analysis
- Overnight movers
- Economic calendar
- Trading signals for the day

### Post-Market Daily (4:30 PM)
- Market performance review
- Portfolio P&L analysis
- Tomorrow's opportunities
- Next session trading plan

### Weekly Analysis (Friday)
- Week performance summary
- Top gainers/losers
- Sector rotation analysis
- Next week outlook and strategy

## Quick Start

1. Install dependencies:
```bash
pip install -r Configuration/requirements.txt
```

2. Configure API credentials in `.env`

3. Run the trading engine:
```bash
python Core_Trading/trading_engine.py
```

4. For demo mode:
```python
from Core_Trading.trading_engine import TradingEngine
engine = TradingEngine(mode='PAPER')
engine.run_demo()
```

## Risk Management

- Maximum 2% portfolio risk per trade
- Sector diversification limits (max 30% tech, 25% financials)
- Daily loss limit circuit breaker at 5%
- Mandatory stop-loss on all positions
- Position sizing based on confidence scores

## Performance Metrics

- Sharpe Ratio
- Win Rate  
- Maximum Drawdown
- Risk-Adjusted Returns
- Daily/Weekly/Monthly P&L

## Technologies

- Python 3.11+
- yFinance for market data
- Alpaca API for trading
- Multi-agent consensus system
- Real-time risk management

## License

Proprietary - All rights reserved