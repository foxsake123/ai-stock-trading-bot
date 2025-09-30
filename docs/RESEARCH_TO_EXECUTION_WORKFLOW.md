# ChatGPT Research to Execution Workflow

## 🔄 PROPER WORKFLOW PROCESS

### Step 1: ChatGPT Deep Research (External)
- **Source**: ChatGPT.com using TradingAgents prompts
- **Frequency**: Weekly (Sunday evening)
- **Output**: Comprehensive research with specific trade recommendations
- **Format**: Markdown with citations and exact orders

### Step 2: Import Research into System
```bash
# Save ChatGPT research
python scripts-and-data/automation/save_chatgpt_report.py

# Or manually save to:
scripts-and-data/data/reports/weekly/chatgpt-research/CHATGPT_ACTUAL_[DATE].md
```

### Step 3: Multi-Agent Processing
```bash
# Process through agents with strategy-specific weights
python scripts-and-data/automation/process_chatgpt_research.py
```

This runs the ChatGPT recommendations through 8 specialized agents:
- Fundamental Analyst
- Technical Analyst
- Sentiment Analyst
- News Analyst
- Risk Manager
- Bull Researcher
- Bear Researcher
- Alternative Data Agent

### Step 4: Strategy-Specific Consensus

#### DEE-BOT Weights (Defensive)
```python
dee_bot_weights = {
    'fundamental': 0.25,  # Higher - focus on quality
    'technical': 0.15,
    'sentiment': 0.10,
    'news': 0.10,
    'risk': 0.20,         # Higher - risk management priority
    'bull': 0.05,
    'bear': 0.10,         # More cautious
    'alternative': 0.05
}
```

#### SHORGAN-BOT Weights (Catalyst-Driven)
```python
shorgan_bot_weights = {
    'fundamental': 0.10,
    'technical': 0.15,
    'sentiment': 0.15,    # Higher - sentiment matters
    'news': 0.15,         # Higher - catalyst focus
    'risk': 0.10,
    'bull': 0.15,         # More aggressive
    'bear': 0.05,
    'alternative': 0.15   # Higher - alt data for catalysts
}
```

### Step 5: Consensus Output
The system generates:
1. **CONSENSUS_TRADES_[DATE].md** - Final validated trades
2. **consensus_trades.json** - Structured data
3. **Confidence scores** for each trade

### Step 6: Execution File Generation
```bash
# Generate daily execution file
python scripts-and-data/automation/generate_todays_trades.py
```

Creates: `TODAYS_TRADES_[DATE].md` with:
- Consensus-validated trades only
- Exact order specifications
- Risk management parameters
- Execution sequence

### Step 7: Automated Execution
```bash
# Execute at market open
python scripts-and-data/automation/execute_daily_trades.py
```

---

## 📊 CONSENSUS SCORING

### Score Interpretation
- **> 70**: STRONGLY AGREE - High confidence execution
- **60-70**: AGREE - Execute with standard position size
- **50-60**: NEUTRAL - Consider but reduce size
- **40-50**: DISAGREE - Skip or review manually
- **< 40**: STRONGLY DISAGREE - Do not execute

### Minimum Thresholds
- **DEE-BOT**: Requires 55+ consensus to execute
- **SHORGAN-BOT**: Requires 60+ consensus (higher risk tolerance)

---

## 🔍 AGENT RESPONSIBILITIES

### Fundamental Analyst
- Evaluates financial metrics
- Checks valuations
- Reviews earnings quality

### Technical Analyst
- Chart patterns
- Support/resistance levels
- Momentum indicators

### Sentiment Analyst
- Market sentiment
- Fear/greed indicators
- Positioning data

### News Analyst
- Recent news impact
- Upcoming catalysts
- Event risk assessment

### Risk Manager
- Position sizing
- Portfolio impact
- Downside risk

### Bull Researcher
- Bullish catalysts
- Upside potential
- Growth drivers

### Bear Researcher
- Bearish risks
- Downside scenarios
- Red flags

### Alternative Data Agent
- Options flow
- Dark pools
- Social sentiment
- Insider activity

---

## 🚨 OVERRIDE CONDITIONS

ChatGPT recommendations may be overridden if:

1. **Risk Manager flags critical issue** (veto power)
2. **Consensus < 50** (majority disagree)
3. **Alternative data shows contrary signals**
4. **Position would violate risk limits**

---

## 📈 EXAMPLE WORKFLOW

### Monday Morning Process:
```bash
# 1. Import Sunday's ChatGPT research
python save_chatgpt_report.py

# 2. Run multi-agent consensus
python process_chatgpt_research.py
# Output: CONSENSUS_TRADES_2025-10-01.md

# 3. Generate execution file
python generate_todays_trades.py
# Output: TODAYS_TRADES_2025-10-01.md

# 4. Execute at 9:30 AM
python execute_daily_trades.py
```

### What Gets Executed:
- Only trades with consensus > threshold
- DEE-BOT: Defensive trades with score > 55
- SHORGAN-BOT: Catalyst trades with score > 60

---

## 📋 AUDIT TRAIL

All decisions are logged:
1. Original ChatGPT recommendation
2. Each agent's individual score
3. Weighted consensus calculation
4. Final decision (execute/skip)
5. Actual execution results

Files:
- `scripts-and-data/data/consensus_trades.json`
- `scripts-and-data/data/execution_log.json`
- `scripts-and-data/daily-csv/[bot]-positions.csv`

---

## 🔧 CONFIGURATION

### To adjust strategy weights:
Edit: `scripts-and-data/automation/process_chatgpt_research.py`

### To change consensus thresholds:
```python
# DEE-BOT threshold
if consensus_score > 55:  # Adjust this

# SHORGAN-BOT threshold
if consensus_score > 60:  # Adjust this
```

### To add new agents:
1. Create agent in `agents/` directory
2. Add to processor initialization
3. Set weight in strategy configs

---

## ⚠️ IMPORTANT NOTES

1. **ChatGPT research is the starting point**, not the final decision
2. **Multi-agent consensus validates** and may reject trades
3. **Different strategies** require different consensus weights
4. **Risk management** can override any recommendation
5. **Alternative data** provides additional validation layer

This ensures that ChatGPT's research is properly validated through multiple independent agents before execution, with strategy-specific decision-making for each bot.