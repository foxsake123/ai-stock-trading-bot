# Task Scheduler Setup Guide
## Complete Trading Automation for Monday, October 28, 2025

---

## PREREQUISITES ✓

Before running the setup script, verify:

- [x] Python 3.13 installed at `C:\Python313\python.exe`
- [x] Project located at `C:\Users\shorg\ai-stock-trading-bot`
- [x] All fixes committed and pushed to GitHub
- [x] Parser working (bot-specific files)
- [x] Financial Datasets API integrated
- [x] Bot filters implemented (S&P 100, market cap, volume)
- [x] Trade generation tested (9/10 approved on Oct 24)

---

## QUICK SETUP (15 MINUTES)

### Step 1: Open Command Prompt as Administrator

**Method 1** (Keyboard shortcut):
1. Press `Windows Key + X`
2. Click "Terminal (Admin)" or "Command Prompt (Admin)"

**Method 2** (Start menu):
1. Click Start button
2. Type "cmd"
3. Right-click "Command Prompt"
4. Select "Run as administrator"

**Method 3** (Run dialog):
1. Press `Windows Key + R`
2. Type: `cmd`
3. Press `Ctrl + Shift + Enter` (runs as admin)

### Step 2: Navigate to Project Directory

```batch
cd C:\Users\shorg\ai-stock-trading-bot
```

### Step 3: Run Setup Script

```batch
scripts\windows\setup_trade_automation.bat
```

**Expected Output**:
```
========================================
 AI Trading Bot - Complete Automation
 Task Scheduler Setup
========================================

Checking Python installation...
Python 3.13.0

Creating Task Scheduler entries for trading automation...

[1/4] Evening Research Generation (6:00 PM ET)...
SUCCESS: The scheduled task "AI Trading - Evening Research" has successfully been created.
SUCCESS: Evening Research task created

[2/4] Morning Trade Generation (8:30 AM ET)...
SUCCESS: The scheduled task "AI Trading - Morning Trade Generation" has successfully been created.
SUCCESS: Morning Trade Generation task created

[3/4] Trade Execution (9:30 AM ET)...
SUCCESS: The scheduled task "AI Trading - Trade Execution" has successfully been created.
SUCCESS: Trade Execution task created

[4/4] Daily Performance Graph (4:30 PM ET)...
SUCCESS: The scheduled task "AI Trading - Daily Performance Graph" has successfully been created.
SUCCESS: Performance Graph task created

========================================
 SUCCESS - All Tasks Created!
========================================

Scheduled Tasks:
  1. Evening Research:      6:00 PM ET (daily)
  2. Trade Generation:      8:30 AM ET (weekdays)
  3. Trade Execution:       9:30 AM ET (weekdays)
  4. Performance Graph:     4:30 PM ET (weekdays)

Next Trading Day Schedule:
  6:00 PM (tonight):  Research generation for tomorrow
  8:30 AM (tomorrow): Generate trades from research
  9:30 AM (tomorrow): Execute approved trades
  4:30 PM (tomorrow): Update performance graph
```

### Step 4: Verify Tasks Created

```batch
schtasks /query /tn "AI Trading - Evening Research"
schtasks /query /tn "AI Trading - Morning Trade Generation"
schtasks /query /tn "AI Trading - Trade Execution"
schtasks /query /tn "AI Trading - Daily Performance Graph"
```

**Expected Output** (for each task):
```
Folder: \
TaskName                                 Next Run Time          Status
======================================== ====================== ===============
AI Trading - Evening Research            10/27/2025 6:00:00 PM  Ready
```

### Step 5: Visual Verification (Optional)

1. Press `Windows Key + R`
2. Type: `taskschd.msc`
3. Press Enter
4. Navigate to "Task Scheduler Library"
5. Look for 4 tasks starting with "AI Trading -"

You should see:
```
Name                                   Status    Triggers
AI Trading - Evening Research          Ready     Daily at 6:00 PM
AI Trading - Morning Trade Generation  Ready     Weekly (M-F) at 8:30 AM
AI Trading - Trade Execution           Ready     Weekly (M-F) at 9:30 AM
AI Trading - Daily Performance Graph   Ready     Weekly (M-F) at 4:30 PM
```

---

## TASK DETAILS

### Task 1: Evening Research
**Name**: AI Trading - Evening Research
**Schedule**: Daily at 6:00 PM ET
**Script**: `scripts/automation/daily_claude_research.py`
**Purpose**: Generate tomorrow's trade research using Claude Opus 4.1
**Output**:
- `reports/premarket/YYYY-MM-DD/claude_research_dee_bot_YYYY-MM-DD.md`
- `reports/premarket/YYYY-MM-DD/claude_research_shorgan_bot_YYYY-MM-DD.md`
- PDF versions for Telegram delivery

**What It Does**:
1. Calls Claude Opus 4.1 API for DEE-BOT strategy
2. Calls Claude Opus 4.1 API for SHORGAN-BOT strategy
3. Saves markdown research reports
4. Generates PDF versions
5. Sends PDFs to Telegram (if configured)
6. Combines reports into single file

**Time**: ~5-10 minutes (API calls + processing)
**Cost**: ~$0.32 per run ($0.16 per bot × 2 bots)

### Task 2: Morning Trade Generation
**Name**: AI Trading - Morning Trade Generation
**Schedule**: Weekdays (Mon-Fri) at 8:30 AM ET
**Script**: `scripts/automation/generate_todays_trades_v2.py`
**Purpose**: Validate research through multi-agent system
**Output**: `docs/TODAYS_TRADES_YYYY-MM-DD.md`

**What It Does**:
1. Parse evening research reports
2. Extract recommendations for each bot
3. Apply bot-specific filters:
   - DEE-BOT: S&P 100 only
   - SHORGAN-BOT: $500M-$50B market cap, >$250K volume
4. Fetch real-time market data (Financial Datasets API)
5. Run multi-agent validation (7 agents)
6. Calculate combined confidence scores
7. Approve/reject each trade
8. Generate formatted trade file with execution details

**Time**: ~2-3 minutes (data fetch + validation)
**Cost**: Minimal (FD API included in $49/month subscription)

### Task 3: Trade Execution
**Name**: AI Trading - Trade Execution
**Schedule**: Weekdays (Mon-Fri) at 9:30 AM ET (market open)
**Script**: `scripts/automation/execute_daily_trades.py`
**Purpose**: Execute approved trades via Alpaca API
**Output**: Execution logs in `data/daily/reports/YYYY-MM-DD/`

**What It Does**:
1. Read `docs/TODAYS_TRADES_YYYY-MM-DD.md`
2. Verify market is open
3. Pre-execution validation (cash, buying power, positions)
4. Place limit orders for approved trades
5. Log execution details (fills, partial fills, failures)
6. Send Telegram notification (if configured)

**Time**: ~1-2 minutes (order placement)
**Cost**: $0 (Alpaca commission-free trading)

### Task 4: Daily Performance Graph
**Name**: AI Trading - Daily Performance Graph
**Schedule**: Weekdays (Mon-Fri) at 4:30 PM ET (after market close)
**Script**: `scripts/performance/generate_performance_graph.py`
**Purpose**: Update portfolio performance charts
**Output**: `reports/performance/performance_graph_YYYY-MM-DD.png`

**What It Does**:
1. Fetch portfolio values for both accounts
2. Calculate daily P&L
3. Update cumulative performance chart
4. Generate benchmark comparisons (SPY)
5. Save updated graph
6. Send to Telegram (if configured)

**Time**: ~30 seconds
**Cost**: $0 (Alpaca API free)

---

## TESTING (OPTIONAL BUT RECOMMENDED)

### Test 1: Evening Research (Safe)
```batch
schtasks /run /tn "AI Trading - Evening Research"
```

**Expected**:
- Creates research files in `reports/premarket/2025-10-27/`
- Takes 5-10 minutes
- Cost: $0.32

**Verify**:
```batch
dir reports\premarket\2025-10-27
```

### Test 2: Trade Generation (Safe)
```batch
schtasks /run /tn "AI Trading - Morning Trade Generation"
```

**Expected**:
- Creates `docs/TODAYS_TRADES_2025-10-27.md`
- Takes 2-3 minutes
- Cost: $0

**Verify**:
```batch
type docs\TODAYS_TRADES_2025-10-27.md
```

### Test 3: Trade Execution (CAUTION - LIVE TRADING)
**WARNING**: This will execute REAL trades with REAL money!

**Only run if**:
- Market is open (9:30 AM - 4:00 PM ET weekdays)
- You've reviewed and approved trades in `TODAYS_TRADES_YYYY-MM-DD.md`
- You're ready for live trading

```batch
REM Only run during market hours and after reviewing trades!
schtasks /run /tn "AI Trading - Trade Execution"
```

### Test 4: Performance Graph (Safe)
```batch
schtasks /run /tn "AI Trading - Daily Performance Graph"
```

**Expected**:
- Updates performance graph
- Takes 30 seconds
- Cost: $0

**Verify**:
```batch
dir reports\performance
```

---

## MONITORING

### Check Task Status
```batch
schtasks /query /tn "AI Trading - Evening Research" /fo LIST /v
```

**Key Fields**:
- **Status**: Should be "Ready" (not "Running" or "Disabled")
- **Last Run Time**: Most recent execution timestamp
- **Last Result**: "0x0" means success, "0x1" means failure
- **Next Run Time**: When it will run next

### Check All Tasks at Once
```batch
schtasks /query /fo TABLE | findstr /i "AI Trading"
```

### View Task History (GUI)
1. Open Task Scheduler (`taskschd.msc`)
2. Click on "AI Trading - Evening Research"
3. Click "History" tab at bottom
4. Review execution history (start time, result, errors)

### Enable History (If Disabled)
1. Open Task Scheduler
2. Click "Action" menu
3. Select "Enable All Tasks History"

---

## TROUBLESHOOTING

### Problem: Task Not Running
**Check**:
1. Task status: `schtasks /query /tn "AI Trading - Evening Research"`
2. Last result code (0x0 = success, anything else = error)
3. Task Scheduler history for error messages

**Fix**:
```batch
REM Delete and recreate task
schtasks /delete /tn "AI Trading - Evening Research" /f
scripts\windows\setup_trade_automation.bat
```

### Problem: Python Not Found
**Error**: `ERROR: Python not found at C:\Python313\python.exe`

**Fix**:
1. Find Python location: `where python`
2. Edit `scripts\windows\setup_trade_automation.bat`
3. Update line 12: `set PYTHON_PATH=C:\Path\To\Your\python.exe`
4. Re-run setup script

### Problem: Permission Denied
**Error**: `ERROR: Access is denied`

**Fix**:
- Run Command Prompt as Administrator (see Step 1 above)
- Task Scheduler requires admin privileges to create system tasks

### Problem: Task Runs But Script Fails
**Check**:
1. Python script logs in `logs/` directory
2. Task Scheduler history for error codes
3. Run script manually to see errors:
   ```batch
   cd C:\Users\shorg\ai-stock-trading-bot
   python scripts\automation\daily_claude_research.py
   ```

**Common Fixes**:
- API keys not set in .env file
- Missing dependencies: `pip install -r requirements.txt`
- File path issues (check working directory)

### Problem: Tasks Created But Wrong Time
**Issue**: Times may be in local time, not ET

**Fix**:
Edit each task:
1. Open Task Scheduler
2. Double-click task
3. Click "Triggers" tab
4. Edit trigger
5. Verify time is correct for your timezone
6. Click OK to save

**Note**: Task Scheduler uses local system time, not ET. If you're in a different timezone, adjust accordingly.

---

## REMOVING AUTOMATION

### Quick Removal (All Tasks)
```batch
scripts\windows\remove_trade_automation.bat
```

### Manual Removal (Individual Task)
```batch
schtasks /delete /tn "AI Trading - Evening Research" /f
schtasks /delete /tn "AI Trading - Morning Trade Generation" /f
schtasks /delete /tn "AI Trading - Trade Execution" /f
schtasks /delete /tn "AI Trading - Daily Performance Graph" /f
```

### Disable Without Deleting
```batch
schtasks /change /tn "AI Trading - Evening Research" /disable
schtasks /change /tn "AI Trading - Morning Trade Generation" /disable
schtasks /change /tn "AI Trading - Trade Execution" /disable
schtasks /change /tn "AI Trading - Daily Performance Graph" /disable
```

### Re-enable After Disabling
```batch
schtasks /change /tn "AI Trading - Evening Research" /enable
schtasks /change /tn "AI Trading - Morning Trade Generation" /enable
schtasks /change /tn "AI Trading - Trade Execution" /enable
schtasks /change /tn "AI Trading - Daily Performance Graph" /enable
```

---

## SUNDAY EVENING CHECKLIST (Before Monday)

### 1. Verify Task Scheduler Setup ✓
- [ ] All 4 tasks created and enabled
- [ ] Next run times are correct
- [ ] No error codes from previous runs

### 2. Test Evening Research (Optional)
- [ ] Run manually: `schtasks /run /tn "AI Trading - Evening Research"`
- [ ] Verify files created in `reports/premarket/2025-10-27/`
- [ ] Review research quality

### 3. Monitor Automated Run (6:00 PM Sunday)
- [ ] Check at 6:15 PM if research files were created
- [ ] Review `reports/premarket/2025-10-28/` for Monday's research
- [ ] Verify both bot files present (DEE-BOT and SHORGAN-BOT)

### 4. Review Research (6:30 PM Sunday)
- [ ] Read DEE-BOT recommendations
- [ ] Read SHORGAN-BOT recommendations
- [ ] Spot-check if recommendations make sense
- [ ] Note any questionable picks for Monday morning review

---

## MONDAY MORNING CHECKLIST

### 8:15 AM - Pre-Trade Generation
- [ ] Verify evening research exists: `dir reports\premarket\2025-10-28`
- [ ] Check market conditions (CPI data, pre-market volatility)
- [ ] Be ready to review trades at 8:35 AM

### 8:35 AM - Post-Trade Generation
- [ ] Check trades generated: `type docs\TODAYS_TRADES_2025-10-28.md`
- [ ] Review approved trades (DEE-BOT + SHORGAN-BOT)
- [ ] Review rejected trades and reasons
- [ ] Verify confidence scores (should be ≥0.60 for approved)
- [ ] Check position sizing (DEE max 8%, SHORGAN max 10%)

### 9:25 AM - Pre-Execution
- [ ] Final review of approved trades
- [ ] Check current market prices vs limit prices
- [ ] Verify cash available in both accounts
- [ ] Be ready for 9:30 AM execution

### 9:35 AM - Post-Execution
- [ ] Check Alpaca account for fills
- [ ] Review execution logs: `dir data\daily\reports\2025-10-28`
- [ ] Verify stop losses will be placed (GTC orders)
- [ ] Note any unfilled orders (adjust limits if needed)

### 4:35 PM - End of Day
- [ ] Check performance graph updated
- [ ] Review daily P&L
- [ ] Check portfolio status: `python scripts\performance\get_portfolio_status.py`

---

## DAILY MONITORING COMMANDS

### Quick Status Check
```batch
REM Check if all tasks are ready
schtasks /query /fo TABLE | findstr /i "AI Trading"

REM Check today's trades
type docs\TODAYS_TRADES_%date:~10,4%-%date:~4,2%-%date:~7,2%.md

REM Check portfolio status
cd C:\Users\shorg\ai-stock-trading-bot
python scripts\performance\get_portfolio_status.py
```

### View Execution Logs
```batch
REM Today's execution logs
dir data\daily\reports\%date:~10,4%-%date:~4,2%-%date:~7,2%

REM View log file
type logs\trading.log | more
```

### Check Recent Research
```batch
dir /o-d reports\premarket
```

---

## EMERGENCY PROCEDURES

### Halt All Trading (Immediate)
```batch
REM Disable all scheduled tasks
schtasks /change /tn "AI Trading - Evening Research" /disable
schtasks /change /tn "AI Trading - Morning Trade Generation" /disable
schtasks /change /tn "AI Trading - Trade Execution" /disable
schtasks /change /tn "AI Trading - Daily Performance Graph" /disable
```

### Resume Trading
```batch
REM Re-enable all tasks
schtasks /change /tn "AI Trading - Evening Research" /enable
schtasks /change /tn "AI Trading - Morning Trade Generation" /enable
schtasks /change /tn "AI Trading - Trade Execution" /enable
schtasks /change /tn "AI Trading - Daily Performance Graph" /enable
```

### Skip Today's Trades
```batch
REM Disable only execution task for today
schtasks /change /tn "AI Trading - Trade Execution" /disable

REM Re-enable tonight for tomorrow
schtasks /change /tn "AI Trading - Trade Execution" /enable
```

---

## SUCCESS CRITERIA

After setup is complete, you should have:

- [x] 4 tasks visible in Task Scheduler
- [x] All tasks showing "Ready" status
- [x] Next run times correctly scheduled
- [x] Test runs successful (optional but recommended)
- [x] Documentation reviewed and understood
- [x] Emergency procedures known

**Automation Status**: 100% READY FOR MONDAY 🎉

---

**Document Created**: October 24, 2025, 5:15 PM ET
**Last Updated**: October 24, 2025
**Next Review**: Monday, October 28, 2025 (post-execution)
