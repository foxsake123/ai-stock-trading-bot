# AI Stock Trading Bot - Complete Project Structure

## 📁 Repository Overview
```
ai-stock-trading-bot/
│
├── 📂 01_Trading_Scripts/          # Core trading engines
│   ├── execute_with_ai_research.py # OpenAI research integration
│   ├── main.py                     # Main orchestrator
│   ├── main_enhanced.py            # Enhanced with data providers
│   ├── place_alpaca_orders.py      # Alpaca trading module
│   └── place_alpaca_orders_enhanced.py # Multi-bot support
│
├── 📂 02_Portfolio_Data/           # Performance tracking
│   ├── Daily_Snapshots/            # Daily portfolio snapshots
│   ├── Trade_History/              # Historical trades
│   ├── Performance/                # Performance metrics
│   └── README.md
│
├── 📂 03_Research_Reports/         # AI-generated research
│   ├── Daily/                      # Daily trading reports
│   │   ├── morning_brief_*.json
│   │   └── research_*.json
│   ├── Weekly/                     # Weekly analysis
│   ├── Deep_Research/              # In-depth analysis
│   ├── Session_Summaries/          # Development logs
│   ├── openai_research_analyzer.py # OpenAI GPT-4 integration
│   ├── automated_research_pipeline.py # Automated research
│   └── README.md
│
├── 📂 04_Bot_Strategies/           # Trading bot strategies
│   ├── DEE_BOT/                    # Institutional strategy
│   │   ├── place_orders.py
│   │   ├── place_orders_enhanced.py
│   │   ├── place_alpaca_orders.py
│   │   └── place_sp100_orders.py
│   ├── SHORGAN_BOT/                # Catalyst strategy
│   │   ├── place_orders.py
│   │   └── place_orders_enhanced.py
│   ├── AI_Agents/                  # Multi-agent system
│   ├── Common/
│   │   └── daily_trades/           # Executable trade lists
│   └── README.md
│
├── 📂 05_Data_Providers/           # Data sources
│   ├── enhanced_providers.py       # Multi-source data hub
│   ├── data_providers.py           # Comprehensive providers
│   ├── catalyst_detector.py        # Catalyst detection
│   ├── Market_Data/                # Price data
│   ├── News/                       # News feeds
│   ├── Sentiment/                  # Social sentiment
│   ├── Economic/                   # Economic indicators
│   ├── Communication/              # Message bus
│   └── README.md
│
├── 📂 06_Risk_Management/          # Risk controls
│   ├── Models/                     # Risk models
│   ├── Reports/                    # Risk reports
│   ├── Alerts/                     # Alert system
│   └── README.md
│
├── 📂 07_Documentation/            # All documentation
│   ├── README.md                   # Main documentation
│   ├── README_ORIGINAL.md          # Original README
│   ├── Session_Notes/              # Development logs
│   │   ├── DATA_INTEGRATION_SUMMARY.md
│   │   └── REORGANIZATION_SUMMARY.md
│   ├── Research_Papers/            # Academic papers
│   │   ├── TradingAgents.pdf
│   │   └── shorgan_bot_report.pdf
│   ├── API_Docs/                   # API documentation
│   └── Guides/                     # Setup guides
│
├── 📂 08_Configuration/            # Settings & config
│   ├── .env                        # API keys (gitignored)
│   ├── api_config.py               # API configuration
│   └── README.md
│
├── 📂 09_Backtesting/              # Historical testing
│   ├── Results/                    # Test results
│   ├── Performance/                # Metrics
│   ├── Strategies/                 # Strategy tests
│   └── README.md
│
├── 📂 10_Utils/                    # Helper scripts
│   ├── Tests/                      # Test scripts
│   │   ├── test_enhanced_data.py
│   │   ├── test_reddit_sentiment.py
│   │   ├── test_data_sources.py
│   │   └── test_alpaca_connection.py
│   ├── Scripts/                    # Utility scripts
│   └── README.md
│
├── 📂 Archive/                     # Old/deprecated code
│
└── 📄 Root Files
    ├── README.md                   # Main project README
    ├── REPOSITORY_STRUCTURE.md     # This file
    ├── requirements.txt            # Python dependencies
    ├── .gitignore                  # Git ignore rules
    └── tree.txt                    # Full file tree

```

## 🔧 Key Components

### Trading Engines
- **main_enhanced.py**: Main orchestrator with enhanced data providers
- **execute_with_ai_research.py**: OpenAI GPT-4 powered research and execution

### Bot Strategies
- **DEE-BOT**: Institutional trading, S&P 100 focus, value investing
- **SHORGAN-BOT**: Catalyst-driven, momentum trading, short-term plays

### Data Integration
- **Alpha Vantage**: Market data
- **NewsAPI**: Financial news
- **Reddit API**: Social sentiment (r/wallstreetbets)
- **FRED**: Economic indicators
- **OpenAI GPT-4**: AI research generation

### APIs Configured
- ✅ OpenAI (GPT-4)
- ✅ Alpaca (Trading)
- ✅ Alpha Vantage (Market Data)
- ✅ NewsAPI (News)
- ✅ Reddit (Sentiment)
- ✅ FRED (Economic)
- ✅ Polygon.io (Configured)

## 📊 Current Status

### Portfolio Performance
- **DEE-BOT**: ~$100,278
- **SHORGAN-BOT**: ~$103,932
- **Combined**: ~$204,210

### Recent Developments
- ✅ OpenAI integration complete
- ✅ Repository reorganized
- ✅ Multi-source data providers
- ✅ Automated research pipeline
- ✅ Bot-specific API keys

## 🚀 Quick Commands

### Daily Operations
```bash
# Generate AI research
python 03_Research_Reports/automated_research_pipeline.py --generate

# Execute with AI research
python 01_Trading_Scripts/execute_with_ai_research.py --full

# Run DEE-BOT
python 04_Bot_Strategies/DEE_BOT/place_orders_enhanced.py

# Run SHORGAN-BOT
python 04_Bot_Strategies/SHORGAN_BOT/place_orders_enhanced.py
```

### Testing
```bash
# Test all data sources
python 10_Utils/Tests/test_enhanced_data.py

# Test OpenAI
python test_openai_research.py

# Test Reddit sentiment
python 10_Utils/Tests/test_reddit_sentiment.py
```

## 📈 Architecture

### Multi-Agent System
1. Fundamental Analyst
2. Technical Analyst
3. News Analyst
4. Sentiment Analyst
5. Bull Researcher
6. Bear Researcher
7. Risk Manager (Veto Power)

### Data Flow
```
Market Data → Data Providers → AI Agents → Coordinator → Trading Decision → Execution
     ↑                                                           ↓
OpenAI Research ←────────────────────────────────────────── Risk Management
```

## 📝 Notes

- All sensitive data in `.env` (gitignored)
- Paper trading mode active
- OpenAI costs ~$0.01-0.03 per analysis
- Reddit rate limit: 60 requests/minute
- Alpha Vantage: 5 API calls/minute (free tier)

---

Generated: January 10, 2025
Version: 2.0 (Post-Reorganization)