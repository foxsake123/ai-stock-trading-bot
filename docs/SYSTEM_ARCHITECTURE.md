# System Architecture
## AI Stock Trading Bot - Technical Documentation
## Version 3.0 - September 29, 2025 - Production Ready

---

## 🏗️ ARCHITECTURE OVERVIEW

```
┌───────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                         │
├─────────────────┬─────────────────┬───────────────────────────┤
│  Telegram Bot   │  Web Dashboard  │   ChatGPT Extension       │
└────────┬────────┴────────┬────────┴────────────┬──────────────┘
         │                 │                     │
         ▼                 ▼                     ▼
┌────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATION LAYER                       │
├────────────────────────────────────────────────────────────────┤
│                         Coordinator                            │
│                      Message Bus (Async)                       │
└───────────┬────────────────────────────────────┬──────────────┘
            │                                    │
            ▼                                    ▼
┌───────────────────────────┐      ┌────────────────────────────┐
│   MULTI-AGENT SYSTEM      │      │    EXECUTION ENGINE        │
├───────────────────────────┤      ├────────────────────────────┤
│ • Fundamental Analyst     │      │ • SHORGAN-BOT (Catalyst)   │
│ • Technical Analyst       │      │ • DEE-BOT (Beta-Neutral)   │
│ • News Analyst           │      │ • Risk Manager             │
│ • Sentiment Analyst      │      │ • Order Executor           │
│ • Bull Researcher        │      └────────────┬───────────────┘
│ • Bear Researcher        │                   │
│ • Risk Manager           │                   ▼
└───────────┬───────────────┘      ┌────────────────────────────┐
            │                       │     BROKER INTERFACE       │
            ▼                       ├────────────────────────────┤
┌───────────────────────────┐      │ • Alpaca Paper Trading     │
│    DATA LAYER             │      │ • Market Data Feed         │
├───────────────────────────┤      │ • Order Management         │
│ • Yahoo Finance           │      └────────────────────────────┘
│ • Alpaca Market Data      │
│ • ChatGPT Reports         │
│ • CSV/JSON Storage        │
└───────────────────────────┘
```

---

## 📁 DIRECTORY STRUCTURE

```
ai-stock-trading-bot/
│
├── agents/                    # Multi-Agent Trading System
│   ├── base_agent.py         # Abstract base class
│   ├── fundamental_analyst.py # P/E, earnings, financials
│   ├── technical_analyst.py  # RSI, MACD, patterns
│   ├── news_analyst.py       # News sentiment analysis
│   ├── sentiment_analyst.py  # Social media sentiment
│   ├── bull_agent.py         # Bullish perspective
│   ├── bear_agent.py         # Bearish perspective
│   ├── risk_manager.py       # Risk assessment
│   ├── catalyst_hunter.py    # Event-driven opportunities
│   └── options_analyst.py    # Options flow analysis
│
├── communication/            # Inter-Agent Communication
│   ├── message_bus.py       # Async message passing
│   ├── coordinator.py       # Agent orchestration
│   └── protocols.py         # Communication protocols
│
├── scripts-and-data/        # Automation & Data Management
│   ├── automation/          # Trading scripts
│   │   ├── process-trades.py          # Multi-agent processor
│   │   ├── execute-dee-bot.py         # DEE-BOT executor
│   │   ├── generate-post-market.py    # Daily reports
│   │   └── chatgpt_report_server.py   # ChatGPT bridge
│   │
│   ├── daily-csv/          # Position tracking
│   │   ├── shorgan-bot-positions.csv
│   │   └── dee-bot-positions.csv
│   │
│   └── daily-json/         # Execution data
│       ├── trades/
│       ├── executions/
│       └── chatgpt/
│
├── docs/                   # Documentation
│   ├── reports/           # Generated reports
│   ├── PRODUCT_PLAN.md    # Feature roadmap
│   ├── ARCHITECTURE.md    # This file
│   └── CLAUDE.md          # Session continuity
│
├── web-dashboard/         # UI Components (Future)
│
└── main.py               # System entry point
```

---

## 🔄 DATA FLOW

### 1. Market Data Ingestion
```
Yahoo Finance API → Data Validator → Cache Layer → Agents
Alpaca API ────────┘                      │
ChatGPT Reports ──────────────────────────┘
```

### 2. Multi-Agent Analysis
```
Market Data → Individual Agents → Consensus Builder → Trading Decision
                     ↓                    ↓
              Agent Scores         Weighted Average
                                  (Configurable Weights)
```

### 3. Trade Execution
```
Decision → Risk Check → Position Sizing → Order Creation → Alpaca API
              ↓              ↓                ↓
         Stop Loss      Max Position    Order Tracking
```

### 4. Reporting Pipeline
```
Positions → P&L Calc → Report Generator → Telegram Bot
              ↓              ↓
          CSV Update    PDF Creation
```

---

## 🤖 AGENT SPECIFICATIONS

### Base Agent Interface
```python
class BaseAgent:
    async def analyze(ticker: str) -> dict:
        return {
            'recommendation': 'BUY|HOLD|SELL',
            'confidence': 0.0-1.0,
            'reasoning': str,
            'data': dict
        }
```

### Agent Weights (Configurable)
```python
DEFAULT_WEIGHTS = {
    'fundamental': 0.20,
    'technical': 0.20,
    'news': 0.15,
    'sentiment': 0.10,
    'bull': 0.15,
    'bear': 0.15,
    'risk': 0.05
}
```

### Consensus Calculation
```python
consensus = sum(agent_score * weight) / sum(weights)
action = 'BUY' if consensus > 0.65 else 'SELL' if consensus < 0.35 else 'HOLD'
```

---

## 💼 TRADING STRATEGIES

### SHORGAN-BOT (Catalyst-Driven)
- **Focus**: Micro-cap stocks < $2B market cap
- **Strategy**: Event-driven (earnings, FDA, M&A)
- **Position Size**: Max 10% per position
- **Stop Loss**: 8% trailing
- **Target**: 15% profit per trade
- **Hold Period**: 1-10 days

### DEE-BOT (Beta-Neutral)
- **Focus**: S&P 100 defensive stocks
- **Strategy**: Beta targeting (1.0 ± 0.1)
- **Position Size**: Max 8% per position
- **Stop Loss**: 3% fixed
- **Target**: 8% profit per trade
- **Hold Period**: 5-30 days

---

## 🔐 SECURITY MEASURES

### API Key Management
- Environment variables for sensitive data
- Key rotation every 90 days
- Separate keys for paper/live trading
- Encrypted storage for backups

### Access Control
- IP whitelisting for server access
- 2FA for critical operations
- Audit logging for all trades
- Encrypted communication channels

### Risk Limits
```python
RISK_LIMITS = {
    'max_daily_loss': 0.03,      # 3% portfolio
    'max_position_size': 0.10,    # 10% per stock
    'max_sector_exposure': 0.30,  # 30% sector
    'force_close_loss': 0.07,     # 7% stop all
    'max_leverage': 2.0           # 2x margin
}
```

---

## 📊 PERFORMANCE MONITORING

### Real-time Metrics
- Position P&L updates every 30 seconds
- Portfolio value tracking
- Risk exposure calculations
- Agent performance scoring

### Daily Reports
- 4:30 PM ET post-market summary
- Position changes and rationale
- Next day catalyst preview
- System health status

### Analytics Dashboard (Planned)
```
┌─────────────────────────────────────┐
│         Portfolio Overview          │
├──────────┬──────────┬───────────────┤
│   P&L    │ Exposure │   Positions   │
│ +$5,081  │  58.2%   │      20       │
└──────────┴──────────┴───────────────┘

┌─────────────────────────────────────┐
│         Agent Performance           │
├──────────┬──────────┬───────────────┤
│  Agent   │ Accuracy │  Avg Return   │
│ Fundmtl  │   72%    │    +3.2%      │
│ Technical│   68%    │    +2.8%      │
└──────────┴──────────┴───────────────┘
```

---

## 🚀 SCALING CONSIDERATIONS

### Current Limitations
- Single-threaded execution
- CSV file storage
- Manual ChatGPT integration
- Windows-specific scheduling

### Planned Improvements
1. **Async Processing**: Full async/await implementation
2. **Database Migration**: PostgreSQL with TimescaleDB
3. **Microservices**: Separate agent containers
4. **Cloud Deployment**: AWS/GCP with auto-scaling
5. **Stream Processing**: Kafka for real-time data

### Performance Targets
- < 100ms order execution
- < 1s multi-agent consensus
- 99.9% uptime
- 1000+ concurrent positions
- Real-time data for 5000+ symbols

---

## 🔧 TECHNOLOGY STACK

### Current Stack
```yaml
Languages:
  - Python: 3.11
  - JavaScript: ES6 (extension)

APIs:
  - Alpaca: Trading & market data
  - Yahoo Finance: Supplemental data
  - Telegram: Notifications
  - ChatGPT: Research reports

Libraries:
  - yfinance: Market data
  - alpaca-trade-api: Trading
  - pandas: Data manipulation
  - asyncio: Async operations
  - requests: HTTP client

Infrastructure:
  - Windows 11: Host OS
  - Task Scheduler: Automation
  - GitHub: Version control
  - CSV/JSON: Data storage
```

### Target Stack
```yaml
Languages:
  - Python: 3.11+ (backend)
  - TypeScript: (frontend)
  - Go: (performance-critical)

Frameworks:
  - FastAPI: REST API
  - React/Next.js: Dashboard
  - Socket.io: Real-time updates

Databases:
  - PostgreSQL: Transactional
  - TimescaleDB: Time-series
  - Redis: Caching
  - InfluxDB: Metrics

Infrastructure:
  - Docker: Containerization
  - Kubernetes: Orchestration
  - AWS/GCP: Cloud platform
  - Terraform: Infrastructure as code
```

---

## 📡 EXTERNAL INTEGRATIONS

### Data Sources
- **Alpaca**: Real-time quotes, trades, bars
- **Yahoo Finance**: Fundamentals, options chains
- **ChatGPT**: AI-generated research
- **News APIs**: Reuters, Bloomberg (planned)
- **Social Media**: Reddit, Twitter (planned)

### Execution Venues
- **Alpaca**: Primary broker (paper trading)
- **Interactive Brokers**: Backup (planned)
- **TD Ameritrade**: Options (planned)

### Monitoring & Alerts
- **Telegram**: Real-time notifications
- **Email**: Daily summaries (planned)
- **SMS**: Critical alerts (planned)
- **Discord**: Community updates (planned)

---

## 🔄 DEPLOYMENT PIPELINE

### Local Development
```bash
# Start all services
python main.py

# Run ChatGPT server
python scripts-and-data/automation/chatgpt_report_server.py

# Generate reports
python scripts-and-data/automation/generate-post-market-report.py
```

### Production Deployment (Planned)
```bash
# Docker deployment
docker-compose up -d

# Kubernetes deployment
kubectl apply -f k8s/

# Health check
curl http://api.tradingbot.com/health
```

---

## 📈 SYSTEM EVOLUTION

### Version History
- **v1.0**: Basic single-agent system
- **v2.0**: Multi-agent consensus
- **v2.5**: Dual-bot architecture (current)
- **v3.0**: Database migration (planned)
- **v4.0**: Cloud deployment (planned)
- **v5.0**: ML optimization (planned)

### Future Architecture
```
┌─────────────────────────────────────┐
│        Machine Learning Layer        │
│   (Pattern Recognition, RL, NLP)    │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│      Intelligent Agent Network      │
│   (Self-optimizing, Adaptive)       │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│    Distributed Execution Engine     │
│   (Multi-broker, Multi-market)      │
└─────────────────────────────────────┘
```

---

*Architecture designed for scalability, reliability, and continuous evolution.*