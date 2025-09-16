# AI Stock Trading Bot - Project Documentation

## Project Overview
This is a multi-agent AI trading bot system based on the TradingAgents framework. The system uses specialized AI agents working collaboratively to analyze markets, make trading decisions, and manage risk.

**Current Performance (September 16, 2025, 1:00 PM ET)**:
- Total Portfolio Value: $206,243.48 (+3.12%)
- DEE-BOT: $102,690.85 (+2.69%) - Beta-neutral with 2X leverage
- SHORGAN-BOT: $103,552.63 (+3.55%)
- Active Positions: 25 (17 SHORGAN + 8 DEE)
- Today's Trades: MFIC, INCY, CBRL, RIVN executed
- Portfolio Beta: ~0.98 (near market neutral)

## Architecture

### Multi-Agent Workflow Overview

The system implements a sophisticated multi-agent collaborative framework where 7 specialized AI agents work together to analyze markets and make trading decisions. Each agent has a specific role and contributes to a weighted consensus system.

**Agent Consensus Formula**:
```
Consensus Score = 
  Fundamental (20%) + Technical (20%) + News (15%) + 
  Sentiment (10%) + Bull (15%) + Bear (15%) + Risk (5%)
```

**Trade Execution Criteria**:
- Consensus Score > 6.5
- Risk Manager Approval = TRUE
- Portfolio Risk Check = PASS

### Core Components

#### 1. Trading Agents (7 Specialist Agents)
The system implements 7 specialized agents, each with distinct responsibilities:

1. **Fundamental Analyst Agent** (`agents/fundamental_analyst.py`)
   - Analyzes company financials, earnings reports, and economic indicators
   - Evaluates P/E ratios, debt levels, revenue growth, and market position
   - Provides long-term value assessments

2. **Technical Analyst Agent** (`agents/technical_analyst.py`)
   - Performs technical analysis using indicators (RSI, MACD, Bollinger Bands, etc.)
   - Identifies chart patterns and support/resistance levels
   - Generates short to medium-term trading signals

3. **News Analyst Agent** (`agents/news_analyst.py`)
   - Monitors real-time news feeds and financial headlines
   - Assesses news impact on stock prices
   - Identifies market-moving events and breaking news

4. **Sentiment Analyst Agent** (`agents/sentiment_analyst.py`)
   - Analyzes social media sentiment (Twitter, Reddit, StockTwits)
   - Tracks retail and institutional sentiment indicators
   - Monitors options flow and put/call ratios

5. **Bull Researcher Agent** (`agents/bull_researcher.py`)
   - Focuses on positive catalysts and growth opportunities
   - Identifies bullish trends and momentum
   - Provides optimistic market perspectives

6. **Bear Researcher Agent** (`agents/bear_researcher.py`)
   - Identifies risks, vulnerabilities, and potential downside
   - Analyzes bearish indicators and warning signals
   - Provides critical counterarguments to bullish theses

7. **Risk Manager Agent** (`agents/risk_manager.py`)
   - Oversees portfolio risk metrics (VaR, Sharpe ratio, max drawdown)
   - Sets position sizing and stop-loss levels
   - Has veto power over trades exceeding risk thresholds

### Communication Protocol

#### Agent Decision Flow
```
Research Input → 7 Parallel Agent Analyses → 
Coordinator Aggregation → Risk Manager Review → 
Trade Decision → Execution/Rejection
```

#### Structured Report Format
All agents communicate using a standardized JSON report format:

```json
{
  "agent_id": "string",
  "agent_type": "string",
  "timestamp": "ISO 8601",
  "ticker": "string",
  "recommendation": {
    "action": "BUY|SELL|HOLD",
    "confidence": 0.0-1.0,
    "timeframe": "intraday|short|medium|long"
  },
  "analysis": {
    "key_factors": [],
    "metrics": {},
    "reasoning": "string"
  },
  "risk_assessment": {
    "risk_level": "LOW|MEDIUM|HIGH",
    "stop_loss": "number",
    "take_profit": "number"
  }
}
```

#### Decision Aggregation
- Central coordinator (`communication/coordinator.py`) collects all agent reports
- Weighted voting system: Fundamental (20%), Technical (20%), News (15%), Sentiment (10%), Bull (15%), Bear (15%), Risk (5%)
- Risk Manager has **VETO POWER** for high-risk trades
- Final decisions require consensus threshold > 6.5
- All trades must pass portfolio risk checks

## Code Style and Conventions

### Python Style Guide
- Follow PEP 8 conventions
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use descriptive variable names (no single letters except in loops)

### Project Structure
```
ai-stock-trading-bot/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py           # Abstract base class for all agents
│   ├── fundamental_analyst.py
│   ├── technical_analyst.py
│   ├── news_analyst.py
│   ├── sentiment_analyst.py
│   ├── bull_researcher.py
│   ├── bear_researcher.py
│   └── risk_manager.py
├── communication/
│   ├── __init__.py
│   ├── coordinator.py          # Central message coordinator
│   ├── message_bus.py          # Async message passing
│   └── protocols.py            # Message format definitions
├── data/
│   ├── __init__.py
│   ├── market_data.py          # Real-time and historical data
│   ├── news_feed.py            # News data ingestion
│   └── sentiment_data.py       # Social media data
├── risk_management/
│   ├── __init__.py
│   ├── portfolio_manager.py    # Portfolio tracking
│   ├── risk_metrics.py         # Risk calculations
│   └── position_sizing.py      # Position size calculator
├── backtesting/
│   ├── __init__.py
│   ├── backtest_engine.py      # Main backtesting logic
│   ├── performance_metrics.py  # Performance analysis
│   └── strategy_tester.py      # Strategy validation
├── config/
│   ├── __init__.py
│   ├── settings.py              # Global settings
│   └── trading_rules.yaml      # Trading rules configuration
├── tests/
│   └── (test files)
├── .env.example                 # Environment variables template
├── requirements.txt
└── main.py                      # Entry point

```

### Error Handling
- Use structured logging with `structlog`
- Implement circuit breakers for external API calls
- Graceful degradation when individual agents fail
- All exceptions should be caught and logged at the agent level

### Testing Requirements
- Minimum 80% code coverage
- Unit tests for each agent's decision logic
- Integration tests for agent communication
- Backtesting validation for all strategies

## Daily Trading Workflow

### Pre-Market Pipeline (7:00 AM ET)
1. **Research Generation** (6:30-7:00 AM)
   - SHORGAN: ChatGPT TradingAgents reports captured
   - DEE: Automated S&P 100 analysis generated

2. **Multi-Agent Analysis** (7:00-7:15 AM)
   - Each agent analyzes recommendations in parallel
   - Scores generated on 0-10 scale

3. **Consensus Building** (7:15-7:20 AM)
   - Weighted scores aggregated
   - Risk Manager final review

4. **Trade Execution** (7:20-7:30 AM)
   - Approved trades submitted via Alpaca
   - Stop losses automatically set

5. **Reporting** (7:30-7:45 AM)
   - PDF reports generated
   - Telegram notifications sent
   - Portfolio CSVs updated

## Trading Bot Configurations

### DEE-BOT Configuration (LATEST: Beta-Neutral with 2X Leverage System)
- **Strategy**: Beta-neutral S&P 100 multi-agent consensus with 2X leverage
- **Capital**: $100,000 starting (currently $101,796.08)
- **Universe**: S&P 100 large-cap stocks with beta diversification
- **Position Sizing**: 3-8% per position with Kelly Criterion optimization (25% Kelly fraction)
- **Portfolio Beta Target**: 0.0 (market neutral, tolerance ±0.1)
- **Current Beta**: 0.98 (managed through hedge positions)
- **Leverage**: 2.0x maximum (currently using 1.85x)
- **Allocation**: 60% long positions, 40% hedge positions
- **Stop Loss**: Dynamic 2% (leveraged adjusted)
- **Take Profit**: 5% target (2.5x volatility multiplier)
- **Risk Management**: 
  - Automatic deleveraging at 3% daily loss
  - Force close all at 7% daily loss
  - Margin buffer 25% minimum
  - Sector concentration max 3 positions
- **Hedge Instruments**: Inverse ETFs (SH, PSQ, SDS, QID)
- **Positions**: 8 current, target 10 maximum
- **Research**: Automated daily 7-agent consensus system
- **Files**:
  - Main: `execute_dee_bot_beta_neutral.py`
  - Config: `config/dee_bot_config.json`
  - Monitor: `monitor_dee_bot.py`
  - Master: `run_dee_bot.py`
- **Alpaca API Key**: PK6FZK4DAQVTD7DYVH78

### SHORGAN-BOT Configuration  
- **Strategy**: Aggressive micro-cap catalyst-driven trading
- **Capital**: $100,000 starting (currently $103,552.63)
- **Universe**: Micro/small/mid-cap catalyst stocks (<$20B market cap)
- **Position Sizing**: 5-10% per position (2-5% for binary events)
- **Stop Loss**: 8-10% for catalyst trades
- **Risk/Reward**: Target 1:3+ ratio
- **Current Positions**: 17 (MFIC, INCY, CBRL, RIVN added 9/16)
- **Latest Trades (9/16)**: 
  - MFIC: 770 @ $12.16 (insider buying)
  - INCY: 61 @ $83.97 (FDA 9/19)
  - CBRL: 81 @ $51.00 (earnings 9/17)
  - RIVN: 357 @ $14.50 (Q3 deliveries)
- **Research**: ChatGPT TradingAgents daily reports
- **Alpaca API Key**: PKJRLSB2MFEJUSK6UK2E

## Trading Bot Specific Guidelines

### Risk Management Rules (UPDATED)
1. **Position Sizing**: Maximum 5% of portfolio per position
2. **Diversification**: Maximum 20% allocation to any single position
3. **Stop Loss**: Mandatory stop-loss orders on all positions (3-4%)
4. **Daily Loss Limit**: Circuit breaker at 5% daily portfolio loss
5. **Correlation Limits**: Monitor and limit correlated positions
6. **Exposure Monitoring**: Alert when total exposure exceeds 80%

### Data Requirements
- Real-time market data with < 1 second latency
- 5 years of historical data for backtesting
- News data from multiple sources (Reuters, Bloomberg, etc.)
- Social sentiment data updated every 5 minutes

### Performance Metrics
- Track Sharpe Ratio, Sortino Ratio, Maximum Drawdown
- Win rate and profit factor
- Average trade duration and turnover
- Risk-adjusted returns vs. benchmark (S&P 500)

### Compliance and Ethics
- No insider trading or market manipulation
- Comply with PDT (Pattern Day Trading) rules
- Implement pre-trade compliance checks
- Maintain audit trail of all trading decisions

## Automation & Scheduling

### Daily Automation
```batch
# Run both bots' pipelines
run_daily_pipelines.bat

# Or run individually
python 01_trading_system/automation/daily_pre_market_pipeline.py --bot SHORGAN
python 01_trading_system/automation/daily_pre_market_pipeline.py --bot DEE
```

### Report Generation
```python
# Generate combined HTML/PDF reports
python 01_trading_system/automation/dual_bot_report_generator.py

# Generate weekly summary
python 01_trading_system/automation/weekly_report_generator.py
```

### Windows Task Scheduler
- Task: "Daily Trading Pipeline"
- Trigger: 7:00 AM ET weekdays
- Action: Run `run_daily_pipelines.bat`

## Development Workflow

### Git Workflow
- Main branch: Production-ready code
- Develop branch: Integration branch
- Feature branches: `feature/agent-name` or `feature/description`
- Hotfix branches: `hotfix/issue-description`

### Testing Commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=./ --cov-report=html

# Run specific test file
pytest tests/test_agents.py

# Run linting
flake8 . && mypy . && black --check .
```

### Environment Setup
1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and configure API keys

## API Keys Required
- OpenAI API key for GPT integration
- Anthropic API key for Claude integration
- Alpha Vantage API key for market data
- Optional: Twitter API for sentiment analysis
- Optional: Reddit API for sentiment analysis

## Security Considerations
- Never commit API keys or secrets
- Use environment variables for all sensitive data
- Implement rate limiting on all external API calls
- Encrypt sensitive data at rest
- Use secure WebSocket connections for real-time data

## Performance Optimization
- Use async/await for concurrent agent operations
- Implement caching for frequently accessed data
- Use Redis for inter-agent message passing
- Batch API requests where possible
- Profile and optimize hot paths in decision-making

## Monitoring and Observability
- Prometheus metrics for system performance
- Structured logging with correlation IDs
- Real-time dashboard for trading activity
- Alert system for anomalies and errors
- Daily performance reports

## Deployment
- Docker containerization for each component
- Kubernetes orchestration for production
- CI/CD pipeline with GitHub Actions
- Blue-green deployment strategy
- Automated rollback on failure

## Future Enhancements
- Reinforcement learning for strategy optimization
- Additional specialized agents (Options, Crypto, Forex)
- Multi-asset class support
- Advanced portfolio optimization algorithms
- Real-time strategy adaptation based on market regime