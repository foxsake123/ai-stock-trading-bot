# AI Stock Trading Bot - Complete Workflow Documentation

## System Architecture Overview

The system employs a **Multi-Agent Collaborative Framework** where 7 specialized AI agents work together to analyze markets, make trading decisions, and manage risk. Two distinct trading bots (SHORGAN-BOT and DEE-BOT) utilize this framework with different strategies.

## The 7-Agent System

### 1. Fundamental Analyst Agent (`agents/fundamental_analyst.py`)
- **Role**: Analyzes company financials and economic indicators
- **Inputs**: Stock symbol, market data, financial statements
- **Outputs**: Valuation scores, P/E analysis, debt assessment
- **Decision Weight**: 20% in final consensus

### 2. Technical Analyst Agent (`agents/technical_analyst.py`)
- **Role**: Performs technical analysis and pattern recognition
- **Inputs**: Price data, volume, historical charts
- **Outputs**: RSI, MACD, support/resistance levels, trend signals
- **Decision Weight**: 20% in final consensus

### 3. News Analyst Agent (`agents/news_analyst.py`)
- **Role**: Monitors and analyzes breaking news impact
- **Inputs**: News feeds, press releases, earnings reports
- **Outputs**: News sentiment score, impact assessment
- **Decision Weight**: 15% in final consensus

### 4. Sentiment Analyst Agent (`agents/sentiment_analyst.py`)
- **Role**: Tracks social media and market sentiment
- **Inputs**: Twitter, Reddit, StockTwits, options flow
- **Outputs**: Sentiment scores, retail vs institutional positioning
- **Decision Weight**: 10% in final consensus

### 5. Bull Researcher Agent (`agents/bull_researcher.py`)
- **Role**: Identifies positive catalysts and opportunities
- **Inputs**: All analyst reports
- **Outputs**: Bull case score, growth catalysts, upside targets
- **Decision Weight**: 15% in final consensus

### 6. Bear Researcher Agent (`agents/bear_researcher.py`)
- **Role**: Identifies risks and potential downside
- **Inputs**: All analyst reports
- **Outputs**: Bear case score, risk factors, downside scenarios
- **Decision Weight**: 15% in final consensus

### 7. Risk Manager Agent (`agents/risk_manager.py`)
- **Role**: Final decision maker with veto power
- **Inputs**: All agent analyses, portfolio metrics
- **Outputs**: Trade approval/rejection, position sizing, stop losses
- **Decision Weight**: 5% + VETO POWER

## Complete Trading Workflow

### Phase 1: Research Generation (6:30 AM - 7:00 AM ET)

#### SHORGAN-BOT Research Flow:
```
1. ChatGPT TradingAgents Analysis
   ↓
2. Browser Extension Capture / Manual Input
   ↓
3. Save to: 02_data/research/reports/pre_market_daily/
   ↓
4. Format: JSON with trades, catalysts, risk metrics
```

#### DEE-BOT Research Flow:
```
1. Automated S&P 100 Analysis
   ↓
2. Calculate Beta, Momentum, RSI for each stock
   ↓
3. Rank by Beta-Neutral Score
   ↓
4. Generate Top 5 Recommendations
   ↓
5. Save to: 02_data/research/reports/dee_bot/
```

### Phase 2: Multi-Agent Analysis (7:00 AM - 7:15 AM ET)

```
For Each Trade Recommendation:
│
├─→ Fundamental Analyst
│   └─→ Analyzes: P/E, Revenue, Debt, Market Cap
│       └─→ Output: Value Score (0-10)
│
├─→ Technical Analyst
│   └─→ Analyzes: RSI, MACD, Volume, Price Action
│       └─→ Output: Technical Score (0-10)
│
├─→ News Analyst
│   └─→ Analyzes: Recent Headlines, Earnings, SEC Filings
│       └─→ Output: News Impact Score (0-10)
│
├─→ Sentiment Analyst
│   └─→ Analyzes: Social Media, Options Flow, Put/Call Ratio
│       └─→ Output: Sentiment Score (0-10)
│
├─→ Bull Researcher
│   └─→ Synthesizes: All Positive Factors
│       └─→ Output: Bull Case Score (0-10)
│
├─→ Bear Researcher
│   └─→ Synthesizes: All Risk Factors
│       └─→ Output: Bear Case Score (0-10)
│
└─→ Risk Manager (FINAL DECISION)
    ├─→ Evaluates: All Agent Scores
    ├─→ Checks: Portfolio Risk Metrics
    ├─→ Calculates: Position Size
    └─→ Decision: APPROVE/REJECT + Stop Loss
```

### Phase 3: Consensus Building (7:15 AM - 7:20 AM ET)

```python
Consensus Score = (
    Fundamental * 0.20 +
    Technical * 0.20 +
    News * 0.15 +
    Sentiment * 0.10 +
    Bull * 0.15 +
    Bear * 0.15 +
    Risk * 0.05
)

Trade Execution Criteria:
- Consensus Score > 6.5
- Risk Manager Approval = TRUE
- Portfolio Risk Check = PASS
- Position Size Calculated
```

### Phase 4: Trade Execution (7:20 AM - 7:30 AM ET)

```
If Trade Approved:
│
├─→ Submit Market Order via Alpaca API
│   └─→ Order Type: Market
│   └─→ Time in Force: Day
│
├─→ Set Stop Loss Order
│   └─→ Type: Stop
│   └─→ Stop Price: Entry - (Stop Loss %)
│
├─→ Update Portfolio CSV
│   └─→ Record: Symbol, Quantity, Price, Time
│
└─→ Send Telegram Notification
    └─→ Include: Trade Details + Agent Consensus
```

### Phase 5: Reporting & Documentation (7:30 AM - 7:45 AM ET)

```
Generate Reports:
│
├─→ PDF Pre-Market Report
│   ├─→ All Agent Analyses
│   ├─→ Consensus Scores
│   ├─→ Trade Decisions
│   └─→ Risk Metrics
│
├─→ HTML Dashboard
│   ├─→ Portfolio Overview
│   ├─→ Position Details
│   └─→ P&L Analysis
│
└─→ Telegram Summary
    ├─→ Trades Executed
    ├─→ Agent Reasoning
    └─→ Portfolio Status
```

## Decision Matrix Example

### Example: MFIC Trade Decision (Sept 16, 2025)

| Agent | Score | Key Factors | Weight | Contribution |
|-------|-------|-------------|--------|--------------|
| Fundamental | 7.5 | Undervalued P/E, Strong earnings | 20% | 1.50 |
| Technical | 8.0 | Breakout pattern, Rising volume | 20% | 1.60 |
| News | 9.0 | Insider buying catalyst | 15% | 1.35 |
| Sentiment | 7.0 | Positive social mentions | 10% | 0.70 |
| Bull | 8.5 | Multiple growth catalysts | 15% | 1.28 |
| Bear | 4.0 | Limited downside risks | 15% | 0.60 |
| Risk | 8.0 | Good risk/reward ratio | 5% | 0.40 |
| **TOTAL** | **7.43** | **APPROVED** | 100% | **7.43** |

**Risk Manager Decision**: 
- ✅ APPROVED
- Position Size: 9% of portfolio (770 shares @ $12.16)
- Stop Loss: $11.07 (9% below entry)
- Risk Score: 3.5/10 (Acceptable)

## Communication Protocol

### Agent Message Format
```json
{
  "agent_id": "technical_analyst_001",
  "agent_type": "technical",
  "timestamp": "2025-09-16T07:15:32Z",
  "ticker": "MFIC",
  "analysis": {
    "score": 8.0,
    "signals": {
      "rsi": 58,
      "macd": "bullish_crossover",
      "volume": "above_average",
      "pattern": "ascending_triangle"
    },
    "confidence": 0.85,
    "timeframe": "short"
  },
  "recommendation": {
    "action": "BUY",
    "reasoning": "Strong technical setup with breakout potential"
  }
}
```

### Coordinator Aggregation
```python
# communication/coordinator.py
def aggregate_decisions(self, agent_reports):
    """Aggregate all agent analyses into final decision"""
    
    # Collect scores
    scores = {
        'fundamental': agent_reports['fundamental']['score'],
        'technical': agent_reports['technical']['score'],
        'news': agent_reports['news']['score'],
        'sentiment': agent_reports['sentiment']['score'],
        'bull': agent_reports['bull']['score'],
        'bear': agent_reports['bear']['score'],
        'risk': agent_reports['risk']['score']
    }
    
    # Calculate weighted consensus
    consensus = (
        scores['fundamental'] * 0.20 +
        scores['technical'] * 0.20 +
        scores['news'] * 0.15 +
        scores['sentiment'] * 0.10 +
        scores['bull'] * 0.15 +
        scores['bear'] * 0.15 +
        scores['risk'] * 0.05
    )
    
    # Risk Manager veto check
    if agent_reports['risk']['decision'] == 'REJECT':
        return {'execute': False, 'reason': 'Risk Manager Veto'}
    
    # Consensus threshold
    if consensus < 6.5:
        return {'execute': False, 'reason': f'Low consensus: {consensus}'}
    
    return {
        'execute': True,
        'consensus_score': consensus,
        'position_size': agent_reports['risk']['position_size'],
        'stop_loss': agent_reports['risk']['stop_loss']
    }
```

## Bot-Specific Strategies

### SHORGAN-BOT Strategy
- **Focus**: Micro-cap catalyst-driven trades
- **Universe**: Stocks < $20B market cap
- **Catalysts**: Insider buying, M&A, earnings beats
- **Position Size**: 5-10% per trade
- **Stop Loss**: 8-10%
- **Target**: 1:3+ risk/reward

### DEE-BOT Strategy
- **Focus**: Beta-neutral S&P 100
- **Universe**: S&P 100 components
- **Target Beta**: 1.0 (market neutral)
- **Leverage**: 2.0x
- **Position Size**: 3-8% (beta-adjusted)
- **Stop Loss**: 3% trailing
- **Rebalance**: Weekly to maintain beta

## File Structure & Data Flow

```
ai-stock-trading-bot/
│
├── agents/                      # 7 Specialist Agents
│   ├── fundamental_analyst.py
│   ├── technical_analyst.py
│   ├── news_analyst.py
│   ├── sentiment_analyst.py
│   ├── bull_researcher.py
│   ├── bear_researcher.py
│   └── risk_manager.py
│
├── communication/               # Agent Communication
│   ├── coordinator.py          # Central decision aggregator
│   ├── message_bus.py          # Async message passing
│   └── protocols.py            # Message formats
│
├── 01_trading_system/
│   └── automation/
│       ├── daily_pre_market_pipeline.py    # Main orchestrator
│       ├── dee_bot_research_generator.py   # DEE research
│       ├── save_chatgpt_report.py          # SHORGAN input
│       └── dual_bot_report_generator.py    # Reporting
│
└── 02_data/
    ├── research/reports/        # Research outputs
    │   ├── pre_market_daily/    # SHORGAN reports
    │   └── dee_bot/             # DEE reports
    └── portfolio/positions/     # Position tracking
```

## Performance Metrics Tracked

### Per Trade Metrics
- Entry/Exit prices and times
- Agent consensus scores
- Individual agent scores
- Stop loss adherence
- Actual vs expected performance

### Portfolio Metrics
- Total P&L
- Win rate
- Average win/loss
- Sharpe ratio
- Maximum drawdown
- Portfolio beta (DEE-BOT)
- Sector diversification

### Agent Performance
- Accuracy by agent type
- Consensus vs actual outcomes
- Risk manager override frequency
- Agent disagreement patterns

## Continuous Improvement Loop

```
Daily Performance Review (Post-Market):
│
├─→ Analyze Agent Accuracy
│   └─→ Which agents were most accurate?
│
├─→ Review Consensus Failures
│   └─→ Why did losing trades get approved?
│
├─→ Update Agent Weights
│   └─→ Adjust weights based on performance
│
└─→ Refine Risk Parameters
    └─→ Tighten/loosen based on results
```

## Emergency Protocols

### Circuit Breakers
- Daily loss > 5%: STOP all trading
- Single position loss > 15%: Emergency exit
- Correlation spike > 0.8: Reduce positions
- VIX > 30: Reduce leverage (DEE-BOT)

### Manual Override
- Risk Manager can override any trade
- Human operator can pause system
- Emergency shutdown script available
- All positions can be liquidated instantly

---

*This workflow ensures systematic, multi-perspective analysis of every trade with proper risk management and documentation.*