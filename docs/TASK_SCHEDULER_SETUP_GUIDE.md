# Task Scheduler Setup Guide
## AI Trading Bot Automation

**Created**: October 16, 2025
**Purpose**: Complete guide for setting up Windows Task Scheduler automation

---

## Overview

The AI Trading Bot uses Windows Task Scheduler to automate the complete trading pipeline:

```
6:00 PM  → Generate Claude research for tomorrow
6:30 PM  → Verify research completed (alert if missing)
8:30 AM  → Generate trade recommendations
9:00 AM  → Verify trades generated (alert if missing)
9:30 AM  → Execute approved trades
```

---

## Quick Setup (5 Minutes)

### Step 1: Run Setup Script

Open Command Prompt or PowerShell **as Administrator**:

```batch
cd C:\Users\shorg\ai-stock-trading-bot
scripts\automation\setup_task_scheduler.bat
```

Press Enter when prompted. The script will create all 5 tasks.

### Step 2: Verify Tasks Created

```batch
schtasks /query /tn "AI Trading*"
```

You should see 5 tasks listed:
- AI Trading - Evening Research
- AI Trading - Evening Health Check
- AI Trading - Morning Trade Generation
- AI Trading - Morning Health Check
- AI Trading - Trade Execution

### Step 3: Test a Task Manually

```batch
schtasks /run /tn "AI Trading - Evening Research"
```

This will trigger the evening research immediately (useful for testing).

---

## Task Details

### Task 1: Evening Research (6:00 PM)

**Name**: `AI Trading - Evening Research`
**Schedule**: Daily at 6:00 PM ET
**Script**: `scripts/automation/daily_claude_research.py`
**Purpose**: Generate Claude Deep Research for tomorrow's trading

**What it does**:
1. Checks if tomorrow is a trading day
2. Fetches market data for analysis
3. Calls Claude API with comprehensive trading prompt
4. Saves report to `reports/premarket/YYYY-MM-DD/claude_research.md`

**Output**:
- File: `reports/premarket/2025-10-17/claude_research.md`
- Size: ~40-50 KB
- Contains: Stock recommendations, catalysts, entry/exit prices

**Troubleshooting**:
- Check logs: `data/logs/daily_research.log`
- Manual run: `python scripts/automation/daily_claude_research.py --force`
- Verify API key: Check `ANTHROPIC_API_KEY` in `.env`

---

### Task 2: Evening Health Check (6:30 PM)

**Name**: `AI Trading - Evening Health Check`
**Schedule**: Daily at 6:30 PM ET
**Script**: `scripts/monitoring/pipeline_health_monitor.py --check research`
**Purpose**: Verify evening research completed successfully

**What it does**:
1. Checks if `claude_research.md` exists for tomorrow
2. Verifies file size >1KB (not empty)
3. Sends email alert if missing

**Email Alert Example** (if research missing):
```
Subject: [AI Trading Bot - CRITICAL] MISSING CLAUDE RESEARCH

Expected file not found: reports/premarket/2025-10-17/claude_research.md

Immediate Actions:
1. Run manually: python scripts/automation/daily_claude_research.py --force
2. Check Task Scheduler logs
3. Verify ANTHROPIC_API_KEY in .env

Without Claude research, tomorrow's trade generation will fail.
```

**Configuration**:
- Email: Set `GMAIL_USER` and `GMAIL_APP_PASSWORD` in `.env`
- Optional Telegram: Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

---

### Task 3: Morning Trade Generation (8:30 AM)

**Name**: `AI Trading - Morning Trade Generation`
**Schedule**: Daily at 8:30 AM ET
**Script**: `scripts/automation/generate_todays_trades_v2.py`
**Purpose**: Generate validated trade recommendations

**What it does**:
1. Reads Claude research from last night
2. Reads ChatGPT research (manual file)
3. Runs each recommendation through 7-agent validation:
   - FundamentalAnalyst (Financial Datasets API)
   - TechnicalAnalyst
   - NewsAnalyst
   - SentimentAnalyst
   - BullResearcher
   - BearResearcher
   - RiskManager (veto power)
4. Calculates combined confidence (40% external + 60% internal)
5. Approves trades with >55% confidence
6. Saves to `docs/TODAYS_TRADES_YYYY-MM-DD.md`

**Output**:
- File: `docs/TODAYS_TRADES_2025-10-17.md`
- Contains: Approved trades, rejected trades, confidence scores, execution checklist

**Requirements**:
- `reports/premarket/YYYY-MM-DD/claude_research.md` (automated)
- `reports/premarket/YYYY-MM-DD/chatgpt_research.md` (manual - you create this)

**Note**: You need to manually create the ChatGPT research file by 8:30 AM each day.

---

### Task 4: Morning Health Check (9:00 AM)

**Name**: `AI Trading - Morning Health Check`
**Schedule**: Daily at 9:00 AM ET
**Script**: `scripts/monitoring/pipeline_health_monitor.py --check trades`
**Purpose**: Verify trades were generated successfully

**What it does**:
1. Checks if `TODAYS_TRADES_YYYY-MM-DD.md` exists
2. Parses file for approval statistics
3. Sends alert if 0 trades approved or approval rate <20%

**Email Alert Examples**:

**Zero Approvals**:
```
Subject: [AI Trading Bot - WARNING] ZERO TRADES APPROVED

Trade generation completed but ALL 22 recommendations were rejected.

Approval Rate: 0% (0 approved / 22 rejected)

Possible Causes:
1. Data API failures (check for 429 errors)
2. All recommendations had low confidence (<55%)
3. Risk Manager vetoed all trades
4. Negative cash balance triggering rejections

No trades will execute at 9:30 AM unless manually approved.
```

**Low Approval Rate**:
```
Subject: [AI Trading Bot - WARNING] LOW APPROVAL RATE: 15%

Stats: 3 approved / 17 rejected (15% approval rate)

This is below the expected 30-50% approval rate.

Review the trades file to understand why.
```

---

### Task 5: Trade Execution (9:30 AM)

**Name**: `AI Trading - Trade Execution`
**Schedule**: Daily at 9:30 AM ET
**Script**: `scripts/automation/execute_daily_trades.py`
**Purpose**: Execute approved trades via Alpaca API

**What it does**:
1. Reads `docs/TODAYS_TRADES_YYYY-MM-DD.md`
2. Filters for trades with status: APPROVED
3. Submits market orders via Alpaca API
4. Logs execution results

**Safety Features**:
- Only executes trades marked APPROVED
- Verifies sufficient cash before placing orders
- Logs all orders for audit trail
- Sends email summary of executions

**Output**:
- Logs: `reports/execution/YYYY-MM-DD/execution_log.json`
- Contains: Order IDs, fill prices, timestamps, errors

---

## Manual Operations

### Run Research Manually (Bypass Schedule)

```bash
python scripts/automation/daily_claude_research.py --force
```

This bypasses time/date checks and generates research immediately.

### Run Trade Generation Manually

```bash
python scripts/automation/generate_todays_trades_v2.py
```

### Run Health Monitor Manually

```bash
# Check all stages
python scripts/monitoring/pipeline_health_monitor.py

# Check specific stage
python scripts/monitoring/pipeline_health_monitor.py --check research
python scripts/monitoring/pipeline_health_monitor.py --check trades

# Check specific date
python scripts/monitoring/pipeline_health_monitor.py --date 2025-10-17
```

### Trigger a Task Manually

```batch
schtasks /run /tn "AI Trading - Evening Research"
```

---

## Task Management

### View Task Details

```batch
schtasks /query /tn "AI Trading - Evening Research" /fo LIST /v
```

### Enable a Task

```batch
schtasks /change /tn "AI Trading - Evening Research" /enable
```

### Disable a Task

```batch
schtasks /change /tn "AI Trading - Evening Research" /disable
```

### Delete a Task

```batch
schtasks /delete /tn "AI Trading - Evening Research" /f
```

### Delete All AI Trading Tasks

```batch
scripts\automation\remove_task_scheduler.bat
```

---

## Troubleshooting

### Task Not Running

**Check Task Status**:
```batch
schtasks /query /tn "AI Trading - Evening Research" /fo LIST /v
```

Look for:
- Status: Should be "Ready" or "Running"
- Last Run Time: Should show recent execution
- Last Result: Should be "0x0" (success)

**Common Issues**:

1. **Task Disabled**:
   ```batch
   schtasks /change /tn "AI Trading - Evening Research" /enable
   ```

2. **Python Not in PATH**:
   - Edit task to use full Python path: `C:\Python313\python.exe`

3. **Working Directory Wrong**:
   - Task should run from project root
   - Edit task: Start in: `C:\Users\shorg\ai-stock-trading-bot`

4. **Permissions Issue**:
   - Run Task Scheduler as Administrator
   - Recreate task with `/rl HIGHEST` flag

### Check Task Logs

**Windows Event Viewer**:
1. Open Event Viewer (`eventvwr.msc`)
2. Navigate to: Windows Logs → Application
3. Filter by: Task Scheduler
4. Look for task name in description

**Script Logs**:
- Research: `data/logs/daily_research.log`
- Trade Generation: Console output (redirect to file if needed)
- Health Monitor: Console output

### Email Alerts Not Sending

**Check Configuration**:
```bash
# Verify .env file has:
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
ALERT_EMAIL=your-email@gmail.com  # Optional, defaults to GMAIL_USER
```

**Generate Gmail App Password**:
1. Go to: https://myaccount.google.com/apppasswords
2. Create new app password for "AI Trading Bot"
3. Copy 16-character password to `.env`

**Test Email**:
```bash
python scripts/monitoring/pipeline_health_monitor.py --alert-on-success
```

---

## Environment Variables Required

Add these to your `.env` file:

```bash
# Anthropic (for research generation)
ANTHROPIC_API_KEY=sk-ant-...

# Financial Datasets (for fundamental data)
FINANCIAL_DATASETS_API_KEY=your-key-here

# Alpaca (for trade execution)
ALPACA_API_KEY_DEE=your-key-here
ALPACA_SECRET_KEY_DEE=your-secret-here
ALPACA_API_KEY_SHORGAN=your-key-here
ALPACA_SECRET_KEY_SHORGAN=your-secret-here

# Email Alerts (optional but recommended)
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
ALERT_EMAIL=your-email@gmail.com

# Telegram Alerts (optional)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=123456789
```

---

## Testing the Complete Pipeline

### Day Before (Evening)

**6:00 PM - Manual Test**:
```bash
python scripts/automation/daily_claude_research.py --force
```

Expected output: `reports/premarket/2025-10-17/claude_research.md`

**6:30 PM - Health Check**:
```bash
python scripts/monitoring/pipeline_health_monitor.py --check research
```

Expected: `[PASS] Evening Research exists for 2025-10-17`

### Morning Of (Trading Day)

**7:00 AM - Create ChatGPT Research**:
1. Read Claude research from last night
2. Submit same questions to ChatGPT Deep Research
3. Save response to: `reports/premarket/2025-10-17/chatgpt_research.md`

**8:30 AM - Generate Trades**:
```bash
python scripts/automation/generate_todays_trades_v2.py
```

Expected output: `docs/TODAYS_TRADES_2025-10-17.md`

**9:00 AM - Health Check**:
```bash
python scripts/monitoring/pipeline_health_monitor.py --check trades
```

Expected: `[PASS] Trades for 2025-10-17: X approved, Y rejected`

**9:30 AM - Execute Trades** (automated):
- Check Alpaca dashboard for orders
- Verify fills within 5-10 minutes

---

## Monitoring & Maintenance

### Daily Checklist

**Evening (6:00-7:00 PM)**:
- [ ] Receive email: "Evening research complete"
- [ ] No email = Check logs and run manually with --force

**Morning (7:00-8:30 AM)**:
- [ ] Review Claude research from last night
- [ ] Create ChatGPT research file
- [ ] Verify both files exist before 8:30 AM

**Morning (9:00-9:30 AM)**:
- [ ] Receive email: "Trade generation complete (X approved)"
- [ ] Review `TODAYS_TRADES_YYYY-MM-DD.md`
- [ ] Verify approved trades look reasonable

**After Market Open (9:30-10:00 AM)**:
- [ ] Check Alpaca dashboard for order fills
- [ ] Run: `python scripts/performance/get_portfolio_status.py`
- [ ] Verify portfolio balances are positive (no margin)

### Weekly Maintenance

- [ ] Review approval rates (should be 30-50%)
- [ ] Check agent performance (which agents are most accurate?)
- [ ] Review email alerts (any recurring issues?)
- [ ] Update market holidays list in `daily_claude_research.py`

### Monthly Maintenance

- [ ] Review total return vs benchmarks
- [ ] Analyze which strategies performed best
- [ ] Update agent weights based on historical accuracy
- [ ] Clean up old reports (archive files >30 days)

---

## Advanced Configuration

### Customize Schedule Times

Edit the setup script or use `schtasks /change`:

```batch
# Change evening research to 5:00 PM
schtasks /change /tn "AI Trading - Evening Research" /st 17:00

# Change trade execution to 9:35 AM (5 minutes after open)
schtasks /change /tn "AI Trading - Trade Execution" /st 09:35
```

### Add Logging to Task

Redirect task output to log file:

```batch
schtasks /create /tn "AI Trading - Evening Research" ^
  /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts\automation\daily_claude_research.py > C:\Users\shorg\ai-stock-trading-bot\data\logs\task_research.log 2>&1" ^
  /sc daily /st 18:00 /ru "%USERNAME%" /rl HIGHEST /f
```

### Run Tasks on Multiple Computers

Export task XML:
```batch
schtasks /query /tn "AI Trading - Evening Research" /xml > task_evening_research.xml
```

Import on another computer:
```batch
schtasks /create /tn "AI Trading - Evening Research" /xml task_evening_research.xml
```

---

## Emergency Procedures

### Stop All Trading Immediately

```batch
# Disable all tasks
schtasks /change /tn "AI Trading - Evening Research" /disable
schtasks /change /tn "AI Trading - Morning Trade Generation" /disable
schtasks /change /tn "AI Trading - Trade Execution" /disable
```

### Resume Trading

```batch
# Enable all tasks
schtasks /change /tn "AI Trading - Evening Research" /enable
schtasks /change /tn "AI Trading - Morning Trade Generation" /enable
schtasks /change /tn "AI Trading - Trade Execution" /enable
```

### Missed Research Recovery

If evening research didn't run:

```bash
# 1. Generate research manually
python scripts/automation/daily_claude_research.py --force

# 2. Create ChatGPT research manually

# 3. Verify files exist
ls reports/premarket/2025-10-17/

# 4. Continue with normal morning pipeline
```

### Zero Trades Approved Recovery

If all trades were rejected at 9:00 AM:

```bash
# 1. Check rejection reasons
cat docs/TODAYS_TRADES_2025-10-17.md

# 2. Verify APIs are working
python scripts/monitoring/pipeline_health_monitor.py

# 3. If API issue, wait and regenerate
python scripts/automation/generate_todays_trades_v2.py

# 4. If fundamental issue, skip trading for the day
```

---

## FAQ

**Q: What if I want to skip trading for a day?**
A: Disable the Trade Execution task:
```batch
schtasks /change /tn "AI Trading - Trade Execution" /disable
```

**Q: Can I run research for a specific date?**
A: Yes, but you'll need to modify the script to accept a `--date` parameter (not currently implemented).

**Q: What happens if my computer is off at 6 PM?**
A: The task won't run. When the computer starts, you can run manually with `--force`.

**Q: Can I get SMS alerts instead of email?**
A: Yes, use Telegram (configure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`).

**Q: How do I know if the Financial Datasets API is working?**
A: Run: `python scripts/monitoring/pipeline_health_monitor.py`
Should show: `[PASS] Financial Datasets API: OK (AAPL @ $XXX.XX)`

**Q: What's the cost per day?**
A:
- Claude Sonnet 4: ~$0.16 per report
- Financial Datasets: $49/month (unlimited)
- Alpaca: Free (paper trading)
- Total: ~$52.50/month (~$2.40/day)

---

## Support

**Documentation**:
- Architecture Audit: `docs/AUTOMATION_ARCHITECTURE_AUDIT_2025-10-16.md`
- Session Summary: `docs/session-summaries/SESSION_SUMMARY_2025-10-16_CRITICAL_FIXES.md`
- CLAUDE.md: Session continuity and history

**Logs**:
- Research: `data/logs/daily_research.log`
- Windows Event Viewer: `eventvwr.msc` → Application → Task Scheduler

**Manual Recovery**:
- Research: `python scripts/automation/daily_claude_research.py --force`
- Trades: `python scripts/automation/generate_todays_trades_v2.py`
- Health Check: `python scripts/monitoring/pipeline_health_monitor.py`

---

**Last Updated**: October 16, 2025
**Status**: Complete and tested
**Next Review**: After 7 days of automated operation
