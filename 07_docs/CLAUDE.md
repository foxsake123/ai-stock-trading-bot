# AI Stock Trading Bot - Project Documentation

## Project Overview
This is a multi-agent AI trading bot system based on the TradingAgents framework. The system uses specialized AI agents working collaboratively to analyze markets, make trading decisions, and manage risk.

## Architecture

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
- Weighted voting system based on agent confidence and historical accuracy
- Risk Manager has veto power for high-risk trades
- Final decisions require consensus threshold (configurable)

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

## Trading Bot Specific Guidelines

### Risk Management Rules
1. **Position Sizing**: Never risk more than 2% of portfolio on a single trade
2. **Diversification**: Maximum 20% allocation to any single position
3. **Stop Loss**: Mandatory stop-loss orders on all positions
4. **Daily Loss Limit**: Circuit breaker at 5% daily portfolio loss
5. **Correlation Limits**: Monitor and limit correlated positions

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