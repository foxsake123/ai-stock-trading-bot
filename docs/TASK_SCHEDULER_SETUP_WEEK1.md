# Task Scheduler Setup for Week 1 Enhancements
## Windows Task Scheduler Configuration Guide

**Date**: October 31, 2025
**Purpose**: Complete Week 1 Priority 4 - Schedule all automation tasks with monitoring

---

## OVERVIEW

This guide configures 6 Windows Task Scheduler tasks:

1. **Weekend Research** - Saturday 12 PM (existing, update to use monitored wrapper)
2. **Morning Trade Generation** - Weekdays 8:30 AM (existing, update to use monitored wrapper)
3. **Trade Execution** - Weekdays 9:30 AM (existing, update to use monitored wrapper)
4. **Performance Graph** - Weekdays 4:30 PM (existing, update to use monitored wrapper)
5. **Stop Loss Monitor** - Every 5 minutes during market hours (NEW)
6. **Profit Taking Manager** - Hourly during market hours (NEW)

---

## QUICK START

### Option 1: Automated Setup (Recommended)

1. Open PowerShell as Administrator
2. Run the automated setup script:
```powershell
cd C:\Users\shorg\ai-stock-trading-bot
.\setup_week1_tasks.bat
```

### Option 2: Manual Setup (If automated fails)

Follow the detailed instructions below for each task.

---

## TASK 1: Weekend Research (UPDATE EXISTING)

**Current**: Uses `scripts/automation/daily_claude_research.py`
**New**: Use `scripts/automation/daily_claude_research_monitored.py`

### Steps:

1. Open Task Scheduler (Win+R → `taskschd.msc`)
2. Find "AI Trading - Weekend Research" in Task Scheduler Library
3. Right-click → Properties
4. Go to "Actions" tab
5. Edit the action
6. Change "Program/script" to:
   ```
   C:\Users\shorg\AppData\Local\Programs\Python\Python313\python.exe
   ```
7. Change "Add arguments" to:
   ```
   scripts/automation/daily_claude_research_monitored.py --force
   ```
8. Click OK to save

---

## TASK 2: Morning Trade Generation (UPDATE EXISTING)

**Current**: Uses `scripts/automation/generate_todays_trades_v2.py`
**New**: Use `scripts/automation/generate_todays_trades_monitored.py`

### Steps:

1. Open Task Scheduler
2. Find "AI Trading - Morning Trade Generation"
3. Right-click → Properties
4. Go to "Actions" tab
5. Edit the action
6. Keep "Program/script" as:
   ```
   C:\Users\shorg\AppData\Local\Programs\Python\Python313\python.exe
   ```
7. Change "Add arguments" to:
   ```
   scripts/automation/generate_todays_trades_monitored.py
   ```
8. Click OK to save

---

## TASK 3: Trade Execution (UPDATE EXISTING)

**Current**: Uses `scripts/automation/execute_daily_trades.py`
**New**: Use `scripts/automation/execute_daily_trades_monitored.py`

### Steps:

1. Open Task Scheduler
2. Find "AI Trading - Trade Execution"
3. Right-click → Properties
4. Go to "Actions" tab
5. Edit the action
6. Keep "Program/script" as:
   ```
   C:\Users\shorg\AppData\Local\Programs\Python\Python313\python.exe
   ```
7. Change "Add arguments" to:
   ```
   scripts/automation/execute_daily_trades_monitored.py
   ```
8. Click OK to save

---

## TASK 4: Performance Graph (UPDATE EXISTING)

**Current**: Uses `scripts/performance/generate_performance_graph.py`
**New**: Use `scripts/automation/generate_performance_graph_monitored.py`

### Steps:

1. Open Task Scheduler
2. Find "AI Trading - Daily Performance Graph"
3. Right-click → Properties
4. Go to "Actions" tab
5. Edit the action
6. Keep "Program/script" as:
   ```
   C:\Users\shorg\AppData\Local\Programs\Python\Python313\python.exe
   ```
7. Change "Add arguments" to:
   ```
   scripts/automation/generate_performance_graph_monitored.py
   ```
8. Click OK to save

---

## TASK 5: Stop Loss Monitor (NEW)

**Purpose**: Monitor all positions every 5 minutes and execute stop losses automatically

### Steps:

1. Open Task Scheduler
2. Click "Create Task" (NOT "Create Basic Task")
3. **General Tab**:
   - Name: `AI Trading - Stop Loss Monitor`
   - Description: `Monitors positions every 5 minutes and executes hard/trailing stops automatically`
   - Security options:
     - [x] Run whether user is logged on or not
     - [x] Run with highest privileges

4. **Triggers Tab**:
   - Click "New..."
   - Begin the task: `On a schedule`
   - Settings: `Daily`
   - Start: (Choose today's date)
   - Start time: `09:30:00` (9:30 AM)
   - Recur every: `1 days`
   - [x] **Repeat task every: 5 minutes**
   - **For a duration of: 6 hours 30 minutes** (covers 9:30 AM to 4:00 PM)
   - [x] Enabled
   - Click OK

5. **Actions Tab**:
   - Click "New..."
   - Action: `Start a program`
   - Program/script:
     ```
     C:\Users\shorg\AppData\Local\Programs\Python\Python313\python.exe
     ```
   - Add arguments:
     ```
     scripts/automation/monitor_stop_losses.py
     ```
   - Start in:
     ```
     C:\Users\shorg\ai-stock-trading-bot
     ```
   - Click OK

6. **Conditions Tab**:
   - [ ] Start the task only if the computer is on AC power (UNCHECK THIS)
   - [ ] Stop if the computer switches to battery power (UNCHECK THIS)

7. **Settings Tab**:
   - [x] Allow task to be run on demand
   - [x] Run task as soon as possible after a scheduled start is missed
   - [ ] Stop the task if it runs longer than: (UNCHECK - no timeout)
   - If the running task does not end when requested: `Do not stop`

8. Click OK to create the task

---

## TASK 6: Profit Taking Manager (NEW)

**Purpose**: Check positions hourly and take profits at +20% (50% position) and +30% (25% position)

### Steps:

1. Open Task Scheduler
2. Click "Create Task"
3. **General Tab**:
   - Name: `AI Trading - Profit Taking`
   - Description: `Takes profits at predefined levels: 50% @ +20%, 25% @ +30%`
   - Security options:
     - [x] Run whether user is logged on or not
     - [x] Run with highest privileges

4. **Triggers Tab**:
   - Click "New..."
   - Begin the task: `On a schedule`
   - Settings: `Daily`
   - Start: (Choose today's date)
   - Start time: `09:30:00` (9:30 AM)
   - Recur every: `1 days`
   - [x] **Repeat task every: 1 hour**
   - **For a duration of: 7 hours** (covers 9:30 AM to 4:30 PM)
   - [x] Enabled
   - Click OK

5. **Actions Tab**:
   - Click "New..."
   - Action: `Start a program`
   - Program/script:
     ```
     C:\Users\shorg\AppData\Local\Programs\Python\Python313\python.exe
     ```
   - Add arguments:
     ```
     scripts/automation/manage_profit_taking.py
     ```
   - Start in:
     ```
     C:\Users\shorg\ai-stock-trading-bot
     ```
   - Click OK

6. **Conditions Tab**:
   - [ ] Start the task only if the computer is on AC power (UNCHECK)
   - [ ] Stop if the computer switches to battery power (UNCHECK)

7. **Settings Tab**:
   - [x] Allow task to be run on demand
   - [x] Run task as soon as possible after a scheduled start is missed
   - [ ] Stop the task if it runs longer than: (UNCHECK)
   - If the running task does not end when requested: `Do not stop`

8. Click OK to create the task

---

## VERIFICATION

### Step 1: Verify All Tasks Created

Open Task Scheduler and verify you see all 6 tasks:

```
AI Trading - Weekend Research          (Saturday 12:00 PM)
AI Trading - Morning Trade Generation  (Weekdays 8:30 AM)
AI Trading - Trade Execution           (Weekdays 9:30 AM)
AI Trading - Daily Performance Graph   (Weekdays 4:30 PM)
AI Trading - Stop Loss Monitor         (Every 5 min, 9:30 AM - 4:00 PM)
AI Trading - Profit Taking             (Hourly, 9:30 AM - 4:30 PM)
```

### Step 2: Test Each Task Manually

Right-click each task → "Run" to test:

#### Test 1: Weekend Research
```powershell
# Expected: Research generated (if Saturday) or skipped (if not Saturday)
# Check: Telegram for success/failure notification
```

#### Test 2: Morning Trade Generation
```powershell
# Expected: Trades generated with approval rate summary
# Check: TODAYS_TRADES_2025-MM-DD.md created
# Check: Telegram notification with approval rate
```

#### Test 3: Trade Execution
```powershell
# Expected: Trades executed from today's file
# Check: Telegram notification with execution summary
```

#### Test 4: Performance Graph
```powershell
# Expected: performance_results.png updated
# Check: Telegram notification with graph
```

#### Test 5: Stop Loss Monitor
```powershell
# Expected: "Market is closed" message (if after hours)
# Expected: Position monitoring output (if market open)
# Check: No Telegram notification unless stop loss triggered
```

#### Test 6: Profit Taking
```powershell
# Expected: Position checks, profit taking if conditions met
# Check: Telegram notification if profits taken
```

### Step 3: Check Task Scheduler History

1. Open Task Scheduler
2. Click "Enable All Tasks History" (in right panel if not enabled)
3. For each task, go to "History" tab
4. Verify "Task completed" events appear after manual runs

### Step 4: Check Automation Health Status

```powershell
cd C:\Users\shorg\ai-stock-trading-bot
python scripts/monitoring/automation_health_monitor.py --check
```

Expected output:
```
Overall Health: GOOD
Message: All systems operational

Task Status:
  Weekend Research Generation: success
  Morning Trade Generation: success
  Trade Execution: success
  Performance Graph Update: success
```

---

## TROUBLESHOOTING

### Issue: Task says "Ready" but never runs

**Solution**:
1. Right-click task → Properties → Triggers
2. Verify trigger is enabled (checkbox)
3. Verify "Start" date is today or in the past
4. Check "Conditions" tab - ensure AC power requirements are disabled

### Issue: Task runs but script fails

**Solution**:
1. Check Task Scheduler History for error details
2. Verify Python path is correct:
   ```powershell
   where python
   # Should show: C:\Users\shorg\AppData\Local\Programs\Python\Python313\python.exe
   ```
3. Verify "Start in" directory is set correctly
4. Run script manually to see actual error:
   ```powershell
   cd C:\Users\shorg\ai-stock-trading-bot
   python scripts/automation/[script_name].py
   ```

### Issue: No Telegram notifications

**Solution**:
1. Verify environment variables are set:
   ```powershell
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('TELEGRAM_BOT_TOKEN'))"
   ```
2. Test Telegram manually:
   ```powershell
   python scripts/monitoring/automation_health_monitor.py --task research --status success
   ```

### Issue: Stop loss monitor runs too frequently

**Solution**:
1. Task Scheduler may not honor 5-minute intervals perfectly
2. This is normal - script checks market hours anyway
3. If it's truly excessive (e.g., every minute), recreate the task

### Issue: Profit taking not executing

**Solution**:
1. Check if positions meet profit-taking thresholds (+20%, +30%)
2. Review `data/daily/profit_taking/profit_taking_history.json`
3. Run manually and check output:
   ```powershell
   python scripts/automation/manage_profit_taking.py
   ```

---

## MONITORING SCHEDULE

### Weekday Automation Timeline

**Pre-Market**:
- 8:30 AM: Trade generation (monitored) → Telegram alert with approval rate

**Market Hours**:
- 9:30 AM: Trade execution (monitored) → Telegram alert with results
- 9:30 AM - 4:00 PM: Stop loss monitor (every 5 min)
- 9:30 AM - 4:30 PM: Profit taking (hourly)

**After Market**:
- 4:30 PM: Performance graph (monitored) → Telegram alert with graph

**Weekend**:
- Saturday 12:00 PM: Research generation (monitored) → Telegram alerts (3 PDFs)

---

## SUCCESS CRITERIA

After setup, you should receive these Telegram notifications:

### Monday 8:30 AM:
```
✅ INFO

Morning Trade Generation
Status: ✅ SUCCESS
Time: 08:30 AM EDT
Schedule: Weekdays 8:30 AM

Details:
• trades_approved: 15
• trades_total: 30
• approval_rate: 50.0%
• status: OK
```

### Monday 9:30 AM:
```
✅ INFO

Trade Execution
Status: ✅ SUCCESS
Time: 09:30 AM EDT
Schedule: Weekdays 9:30 AM

Details:
• output: Trades executed
```

### If Stop Loss Triggered:
```
🛑 STOP LOSS EXECUTED

Account: SHORGAN-BOT Live
Symbol: FUBO
Quantity: 27 shares

Entry Price: $3.50
Exit Price: $2.87
P&L: -$17.01 (-18.0%)

Reason: Hard stop triggered: -18.0% loss (limit: -18%)
Order ID: abc123...
Time: 02:15 PM EDT
```

### If Profit Taken:
```
💰 PROFIT TAKEN

Account: DEE-BOT Paper
Symbol: MSFT
Action: Sold 50% of position

Entry Price: $400.00
Current Price: $480.00
P&L on Sale: +$40/share (+20.0%)

Level: 50% @ +20% gain
Shares Sold: 5
Remaining: 5 shares (let run with trailing stop)
Time: 11:45 AM EDT
```

---

## NEXT STEPS AFTER SETUP

1. **Monitor Monday Morning** (Nov 3):
   - 8:35 AM: Check TODAYS_TRADES file for approval rate
   - 9:35 AM: Verify trades executed correctly
   - Throughout day: Watch for stop loss / profit taking alerts

2. **Week 2 Enhancements** (After Week 1 100% complete):
   - Fix 11 test collection errors (3 hours)
   - Add parser unit tests (2 hours)
   - Multi-agent validation backtest (4 hours)
   - Separate live account trade generation (3 hours)

3. **System Monitoring**:
   - Check health status daily:
     ```powershell
     python scripts/monitoring/automation_health_monitor.py --check
     ```
   - Review Telegram notifications for any failures
   - If CRITICAL alerts (2+ consecutive failures), investigate immediately

---

## FILE REFERENCE

**Monitored Wrappers**:
- `scripts/automation/daily_claude_research_monitored.py`
- `scripts/automation/generate_todays_trades_monitored.py`
- `scripts/automation/execute_daily_trades_monitored.py`
- `scripts/automation/generate_performance_graph_monitored.py`

**Risk Management**:
- `scripts/automation/monitor_stop_losses.py`
- `scripts/automation/manage_profit_taking.py`

**Monitoring System**:
- `scripts/monitoring/automation_health_monitor.py`

**Data Files** (created automatically):
- `data/automation_status.json` - Health monitor status
- `data/stop_loss_status.json` - Position high tracking
- `data/daily/profit_taking/profit_taking_history.json` - Profit taking history

---

**Setup Time**: 30-45 minutes (manual) or 5 minutes (automated)
**Impact**: Complete Week 1 enhancements, system reliability 9/10
**Status After Completion**: Week 1 100% complete, ready for Week 2

---

*Generated: October 31, 2025, 11:15 PM ET*
*Part of: Week 1 Enhancements - Automation Monitoring & Risk Management*
