# Weekly Reports System

## Overview
Comprehensive weekly reporting system for dual-bot trading strategy analysis and planning.

---

## 📊 Report Types

### 1. Weekly Performance Report (Backward-Looking)
**File**: `weekly_performance_report.py`
**Purpose**: Analyze past week's trading performance
**Generated**: Friday evenings

**Contents**:
- Executive summary with total returns
- Trading activity metrics (win rate, avg win/loss)
- Top and bottom performers by bot
- Catalyst trade results
- Risk metrics (beta, Sharpe, drawdown)
- Lessons learned and action items

### 2. Weekly Trade Planner (Forward-Looking)
**File**: `weekly_trade_planner.py`
**Purpose**: Plan upcoming week's trades
**Generated**: Sunday evenings

**Contents**:
- Market outlook and key events
- Capital allocation plans
- Specific trade setups with entry/exit levels
- Catalyst calendar
- Risk management rules
- Success metrics for the week

### 3. ChatGPT Deep Research Integration
**Files**:
- `generate_weekly_prompt.py` - Creates prompts with live portfolio data
- `chatgpt_weekly_extractor.py` - Extracts recommendations from ChatGPT

**Workflow**:
1. Generate prompt with current positions
2. Get deep research from ChatGPT
3. Extract exact orders
4. Create execution plan

---

## 📅 Weekly Workflow

### Friday Evening
```bash
# Review the week's performance
python scripts-and-data/automation/weekly_performance_report.py

# Generate prompts for weekend research
python scripts-and-data/automation/generate_weekly_prompt.py
```

### Weekend
```bash
# After getting ChatGPT analysis
python scripts-and-data/automation/chatgpt_weekly_extractor.py

# Plan next week's trades
python scripts-and-data/automation/weekly_trade_planner.py
```

### Monday Morning
- Execute planned trades from trade planner
- Set stops and alerts per plan
- Update position tracking

---

## 📁 Directory Structure

```
weekly-reports/
├── performance/          # Historical performance reports
│   └── weekly_performance_YYYYMMDD_HHMMSS.pdf
├── trade_plans/         # Forward-looking trade plans
│   └── weekly_trade_plan_YYYYMMDD_HHMMSS.pdf
├── prompts/            # Generated ChatGPT prompts
│   ├── weekly_prompt_dee_YYYYMMDD.txt
│   └── weekly_prompt_shorgan_YYYYMMDD.txt
└── README.md           # This file
```

---

## 🎯 Key Metrics Tracked

### Performance Metrics
- Weekly return (% and $)
- Win rate
- Average win vs average loss
- Best and worst trades
- Risk-adjusted returns (Sharpe ratio)
- Maximum drawdown

### Planning Metrics
- Capital allocation
- Position sizing
- Catalyst events
- Entry/exit targets
- Stop loss levels
- Risk limits

---

## 🤖 Bot-Specific Analysis

### DEE-BOT (Defensive)
- Beta tracking (target: 1.0)
- S&P 100 large-cap focus
- Sector rotation signals
- Defensive positioning

### SHORGAN-BOT (Catalyst)
- Micro-cap catalyst plays
- FDA/earnings calendar
- Momentum tracking
- Cash reserve management

---

## 📈 Success Criteria

Weekly goals:
- Execute 80% of planned trades within target ranges
- Maintain stop losses on 100% of positions
- Keep DEE-BOT beta between 0.9-1.1
- Achieve 60% win rate on catalyst trades
- Document all trades with rationale

---

## 🔧 Automation Setup

To schedule weekly reports:

**Windows Task Scheduler**:
1. Create task for Friday 4:30 PM - Performance Report
2. Create task for Sunday 6:00 PM - Trade Planner

**Command**:
```
python C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\weekly_performance_report.py
```

---

## 📝 Notes

- All reports generate PDFs for easy sharing
- JSON files saved for programmatic access
- Integration with Alpaca API for live data
- ChatGPT prompts include current positions and cash
- Reports use professional formatting with color coding

Last Updated: September 22, 2025