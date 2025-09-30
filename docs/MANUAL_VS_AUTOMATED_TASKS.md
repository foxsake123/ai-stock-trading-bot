# 📋 Manual vs Automated Tasks Guide

## 🔴 WHAT YOU NEED TO DO MANUALLY

### Weekly (Sunday Evening)

#### 1. Get ChatGPT Research (30 minutes)
```
WHEN: Sunday 5-7 PM
WHERE: ChatGPT.com

STEPS:
1. Go to ChatGPT.com
2. Copy prompt from: weekly_research_prompt.txt
3. Paste and get ChatGPT's analysis
4. Copy the ENTIRE response
5. Save using ONE of these methods:
   a) Run: python scripts-and-data/automation/save_chatgpt_report.py
      (Will prompt you to paste the research)
   b) OR save directly to:
      scripts-and-data/data/reports/weekly/chatgpt-research/CHATGPT_ACTUAL_[DATE].md
```

#### 2. Run Weekly Workflow (5 minutes)
```bash
# After saving ChatGPT research, run:
python scripts-and-data/automation/complete_weekly_workflow.py

# This will:
# - Process research through 8 agents
# - Generate consensus scores
# - Create validated trades
# - Generate TODAYS_TRADES files for the week
```

### Daily (Optional Checks)

#### Morning Check (2 minutes)
```
WHEN: 9:00-9:25 AM
WHAT: Review Telegram alerts
WHY: Confirm system is ready

Check for:
- ✅ Pre-market alert received
- ✅ Trades file exists
- ✅ No error messages
```

#### FDA/Earnings Events (As Needed)
```
WHAT: Check binary event outcomes
WHEN: After announcement
ACTION: May need manual exit/adjustment
```

---

## 🟢 WHAT'S FULLY AUTOMATED

### Daily Tasks (No Action Required)

#### 9:00 AM - Pre-Market
```
AUTOMATED:
✓ Account status check
✓ Position sync both bots
✓ Trades file verification
✓ Telegram alert sent
```

#### 9:30 AM - Market Open
```
AUTOMATED:
✓ Execute all consensus trades
✓ DEE-BOT trades via Alpaca
✓ SHORGAN-BOT trades via Alpaca
✓ Stop-loss orders placed
✓ Execution confirmations
```

#### 12:00 PM - Midday
```
AUTOMATED:
✓ Position updates
✓ P&L calculations
✓ Risk checks
```

#### 4:00 PM - Market Close
```
AUTOMATED:
✓ Final position sync
✓ Daily snapshot saved
✓ Performance tracking
```

#### 4:30 PM - Post-Market
```
AUTOMATED:
✓ Full portfolio report
✓ Daily P&L summary
✓ Winners/losers analysis
✓ Telegram report sent
✓ CSV archives updated
```

### Weekly Tasks (No Action Required)

#### Friday 4:30 PM
```
AUTOMATED:
✓ Weekly performance report
✓ Trade analysis
✓ Strategy metrics
✓ Risk assessment
```

---

## 🔄 COMPLETE WORKFLOW

```mermaid
Sunday Evening (MANUAL):
    1. Get ChatGPT Research → 2. Save to System → 3. Run Weekly Workflow
                                                           ↓
                                                   (AUTOMATED)
                                                           ↓
    Multi-Agent Processing → Consensus Scoring → Trade Validation
                                                           ↓
                                                   TODAYS_TRADES Files

Monday-Friday (AUTOMATED):
    9:00 AM → Pre-Market Check
    9:30 AM → Execute Trades
    12:00 PM → Position Update
    4:00 PM → Market Close Tasks
    4:30 PM → Send Reports
```

---

## 🚀 QUICK START COMMANDS

### Sunday Evening Setup (MANUAL)
```bash
# Step 1: Save ChatGPT research
python scripts-and-data/automation/save_chatgpt_report.py

# Step 2: Process through agents
python scripts-and-data/automation/complete_weekly_workflow.py

# Verify: Check for TODAYS_TRADES_[DATE].md files
```

### Daily Automation (SET ONCE)
```bash
# Option 1: Windows Task Scheduler (Recommended)
# Already configured if you ran setup_all_tasks.bat

# Option 2: Manual daily scheduler
python scripts-and-data/automation/daily_automation.py

# Option 3: Run specific task
python scripts-and-data/automation/daily_automation.py execute
```

---

## ⏰ TIME COMMITMENT

### Weekly
- **Sunday**: 35 minutes total
  - 30 min: Get ChatGPT research
  - 5 min: Run workflow

### Daily
- **Optional**: 2 minutes to check Telegram
- **Required**: 0 minutes (fully automated)

### Monthly
- **Optional**: 30 minutes to review performance

---

## 📱 TELEGRAM ALERTS YOU'LL RECEIVE

### Daily Alerts (Automated)
```
9:00 AM: "🔔 Pre-Market Ready"
9:35 AM: "✅ Trades Executed"
4:30 PM: "📊 Post-Market Report"
```

### Weekly Alerts (After Manual Setup)
```
Sunday: "✅ Weekly Workflow Complete"
Sunday: "📊 Validated Trades Ready"
Friday: "📈 Weekly Performance Report"
```

### Error Alerts (If Issues)
```
"⚠️ No trades file found"
"❌ Execution failed"
"🚨 Stop-loss triggered"
```

---

## 🔧 TROUBLESHOOTING

### If No Trades Execute
```bash
# Check if trades file exists
ls TODAYS_TRADES_*.md

# If missing, run weekly workflow
python scripts-and-data/automation/complete_weekly_workflow.py

# Force execution
python scripts-and-data/automation/execute_daily_trades.py
```

### If No Reports Received
```bash
# Generate manually
python scripts-and-data/automation/generate-post-market-report.py

# Check Telegram bot
python scripts-and-data/automation/test_telegram.py
```

### If Agents Don't Process
```bash
# Check research file exists
ls scripts-and-data/data/reports/weekly/chatgpt-research/

# Re-run workflow
python scripts-and-data/automation/complete_weekly_workflow.py
```

---

## 📊 DATA FLOW

1. **ChatGPT Research** (Manual Input)
   ↓
2. **Multi-Agent Processing** (Automated)
   - 8 agents analyze each trade
   - Strategy-specific weights applied
   ↓
3. **Consensus Scoring** (Automated)
   - DEE: 55+ threshold
   - SHORGAN: 60+ threshold
   ↓
4. **Trade Validation** (Automated)
   - Only high-confidence trades approved
   ↓
5. **Execution** (Automated)
   - 9:30 AM daily via Alpaca
   ↓
6. **Reporting** (Automated)
   - 4:30 PM daily via Telegram

---

## ✅ SETUP CHECKLIST

### One-Time Setup (Already Done)
- [x] Alpaca API keys configured
- [x] Telegram bot configured
- [x] Windows Task Scheduler set up
- [x] Multi-agent system installed
- [x] Alternative data sources connected

### Weekly Requirements
- [ ] Sunday: Get ChatGPT research
- [ ] Sunday: Run weekly workflow
- [ ] Monday-Friday: Monitor Telegram (optional)

### That's It!
The system handles everything else automatically.

---

## 📞 SUPPORT

### Check System Status
```bash
python scripts-and-data/automation/system_health_check.py
```

### View Current Positions
```bash
python show_holdings.py
```

### Emergency Stop All Trading
```bash
python scripts-and-data/automation/emergency_stop.py
```

---

**Remember**: You only need to provide ChatGPT research on Sunday. Everything else is automated!