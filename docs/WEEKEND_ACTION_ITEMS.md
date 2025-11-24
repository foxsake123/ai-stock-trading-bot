# Weekend Action Items - Complete Before Monday 8:30 AM
**Created**: November 23, 2025
**Status**: 3 tasks remaining (45 minutes total)

---

## 🎯 Quick Summary

**Code Fixes**: ✅ 100% Complete (all done by Claude Code)
**User Actions**: ⏳ 0% Complete (you need to do these 3 tasks)

**If completed**: Monday will be the **first fully automated trading day!**

---

## ⏳ Task 1: Enable SHORGAN Live Trading (5 minutes)

**Priority**: 🔴 CRITICAL
**Status**: ⏳ NOT DONE
**Impact**: Unlocks 5 queued trades ($900), deploys 77% cash

### Steps:

1. **Go to Alpaca**:
   - Visit: https://app.alpaca.markets
   - Log in to your account

2. **Navigate to Settings**:
   - Click your username/profile icon
   - Select "Account Settings"

3. **Enable Trading**:
   - Find "Trading Configuration" section
   - Look for setting: "Allow new orders" or "Trading enabled"
   - Toggle to **ENABLED**
   - Click "Save" or "Update"

4. **Verify**:
   - Setting should show as "Enabled" or "Active"
   - No red warnings about rejected orders

5. **Test (Optional)**:
   ```bash
   cd C:\Users\shorg\ai-stock-trading-bot
   python execute_shorgan_live_friday.py
   ```
   - Should show 5 trades ready to execute
   - Type "YES" to execute or "NO" to skip test

### What This Fixes:
- Current error: "new orders are rejected by user request"
- SHORGAN Live has 5 trades ready from Friday research
- Account has 77% cash ($2,168) ready to deploy

---

## ⏳ Task 2: Configure Task Scheduler (30 minutes)

**Priority**: 🔴 CRITICAL
**Status**: ⏳ NOT DONE
**Impact**: Enables all Monday automation (research, trades, execution, performance)

### Steps:

1. **Navigate to Project**:
   ```
   C:\Users\shorg\ai-stock-trading-bot
   ```

2. **Run Setup Script**:
   - Find file: `setup_week1_tasks.bat`
   - Right-click the file
   - Select: **"Run as Administrator"**
   - If prompted, enter Windows administrator password
   - Wait for script to complete (~5 minutes)
   - Look for success messages

3. **Verify Tasks Created**:
   - Press Win+R
   - Type: `taskschd.msc`
   - Press Enter
   - Navigate to: "Task Scheduler Library"
   - Look for 5 tasks starting with "AI Trading":
     * AI Trading - Weekend Research
     * AI Trading - Morning Trade Generation
     * AI Trading - Trade Execution
     * AI Trading - Daily Performance Graph
     * AI Trading - Stop Loss Monitor

4. **Check Task Settings**:
   For each task, right-click → Properties and verify:
   - ✅ **Triggers tab**: Schedule is correct
   - ✅ **Actions tab**: Python path is correct
   - ✅ **Conditions tab**: "Start only if on AC power" is UNCHECKED
   - ✅ **Settings tab**: "Run task as soon as possible" is CHECKED

### What This Creates:

**Weekend Research** (Saturday 12:00 PM):
- Generates research for all 3 accounts
- Creates PDFs and sends to Telegram
- Next run: Saturday, Nov 30

**Morning Trade Generation** (Weekdays 8:30 AM):
- Extracts trades from research
- Runs multi-agent validation
- Creates TODAYS_TRADES file
- First run: Monday, Nov 25 at 8:30 AM

**Trade Execution** (Weekdays 9:30 AM):
- Executes approved trades
- Places stop loss orders
- Sends execution summary to Telegram
- First run: Monday, Nov 25 at 9:30 AM

**Performance Graph** (Weekdays 4:30 PM):
- Updates portfolio performance chart
- Shows all 3 accounts vs S&P 500
- Sends to Telegram
- First run: Monday, Nov 25 at 4:30 PM

**Stop Loss Monitor** (Every 5 min, 9:30 AM - 4:00 PM):
- Monitors all positions for stop loss triggers
- Executes protective sells if needed
- Sends alerts to Telegram

---

## ⏳ Task 3: Test Automation Tasks (10 minutes)

**Priority**: 🟡 HIGH
**Status**: ⏳ NOT DONE
**Impact**: Confirms automation will work Monday morning

### Steps:

1. **Open Task Scheduler**:
   - Press Win+R
   - Type: `taskschd.msc`
   - Press Enter

2. **Test Each Task**:
   For each "AI Trading" task:

   a. **Right-click** the task
   b. Select **"Run"**
   c. Watch status change to "Running"
   d. Wait for status to change to "Ready" (task complete)
   e. Check for output files (see below)

3. **Verify Outputs**:

   **Weekend Research**:
   - Check: `reports/premarket/2025-11-24/`
   - Should see: 3 markdown files + 3 PDFs
   - Check Telegram for PDFs

   **Morning Trade Generation**:
   - Check: `docs/TODAYS_TRADES_2025-11-24.md`
   - Should see: Trade recommendations for all 3 accounts
   - Should show approval percentages

   **Trade Execution**:
   - Will show: "No trades to execute" (if run outside market hours)
   - This is normal - just verify it runs without errors

   **Performance Graph**:
   - Check: `performance_results.png` in project root
   - Should see: Chart with 4 lines (DEE, SHORGAN Paper, SHORGAN Live, S&P 500)
   - Check Telegram for chart

   **Stop Loss Monitor**:
   - Will show: Monitoring status or "Market closed"
   - This is normal - just verify it runs without errors

4. **Check Task History**:
   - Right-click each task → Properties
   - Go to "History" tab
   - Should see successful execution events
   - No error messages

### What You're Testing:
- ✅ Tasks can run without errors
- ✅ Python paths are correct
- ✅ API keys work
- ✅ File paths are correct
- ✅ Telegram notifications work
- ✅ Scripts have proper permissions

---

## 🖥️ Task 4: Computer Settings

**Priority**: 🔴 CRITICAL
**Status**: ⏳ NEEDS VERIFICATION

### Windows Sleep Settings:

1. **Open Settings**:
   - Press Win+I
   - Go to: System → Power & Sleep

2. **Set Sleep to NEVER**:
   - "When plugged in, PC goes to sleep after" → **Never**
   - "When plugged in, turn off my screen after" → Your choice (can be 15 min)

3. **Verify**:
   - Computer will stay on indefinitely when plugged in
   - Only screen will turn off, not the computer itself

### Weekend Plan:

**Option A: Leave Computer On** (Recommended)
- Leave computer ON Friday night
- Leave computer ON all weekend
- Make sure it's plugged in
- Screen can turn off, computer stays on

**Option B: Turn On Before 8:25 AM Monday**
- Set alarm for 8:20 AM Monday
- Turn computer on
- Log in to Windows
- Wait until 8:25 AM
- Automation runs at 8:30 AM

### Monday Morning Requirements:
- ✅ Computer is ON
- ✅ Computer is plugged in (AC power)
- ✅ User is logged in to Windows
- ✅ No lock screen active
- ✅ Time is before 8:30 AM

---

## ✅ Success Criteria

**After completing all 4 tasks, you should have:**

1. ✅ SHORGAN Live trading enabled in Alpaca
2. ✅ 5 Task Scheduler tasks created and verified
3. ✅ All tasks tested and working
4. ✅ Windows sleep set to NEVER
5. ✅ Computer settings confirmed

**Monday morning, if all complete:**
- 8:30 AM: Research auto-generates with accurate macro data ✅
- 8:30 AM: Trades auto-generate from complete research ✅
- 9:30 AM: Trades auto-execute on all 3 accounts ✅
- 4:30 PM: Performance graph auto-updates ✅
- **NO manual intervention required** ✅

---

## 🚨 Troubleshooting

**If Task Scheduler setup fails:**
```
Common issues:
- Not running as Administrator → Right-click, "Run as Administrator"
- Python path wrong → Check if Python is at C:\Python313\python.exe
- Permission denied → Disable antivirus temporarily, try again
```

**If tasks won't run:**
```
Common issues:
- Computer asleep → Set sleep to NEVER
- User not logged in → Must be logged in for tasks to run
- Conditions preventing run → Check "Conditions" tab, uncheck "AC power" requirement
```

**If SHORGAN Live still can't trade:**
```
Common issues:
- Wrong account → Make sure you're in SHORGAN Live account
- Setting not saved → Click "Save" after enabling trading
- Still disabled → Contact Alpaca support (rare)
```

---

## 📞 If You Need Help

**Immediate help:**
- Review full session summary: `docs/session-summaries/SESSION_SUMMARY_2025-11-23_WEEKEND_CRITICAL_FIXES.md`
- Check CLAUDE.md for latest status
- Check Task Scheduler History tab for error messages

**Monday morning verification:**
- 8:35 AM: Check if `docs/TODAYS_TRADES_2025-11-25.md` exists
- If not → Run manually: `python scripts/automation/generate_todays_trades_v2.py`

---

## 📊 Estimated Time

| Task | Time | Difficulty |
|------|------|------------|
| Enable SHORGAN Live Trading | 5 min | Easy |
| Configure Task Scheduler | 30 min | Medium |
| Test Automation Tasks | 10 min | Easy |
| Computer Settings | 5 min | Easy |
| **Total** | **50 min** | **Medium** |

**Best time to do this**: Saturday or Sunday afternoon when you have 1 hour free

---

## 🎯 Why These Are Critical

**Without SHORGAN Live enabled:**
- 5 trades stuck in queue
- 77% cash ($2,168) not deployed
- Missing profit opportunities

**Without Task Scheduler:**
- NO automation Monday morning
- Must manually generate research (30 min)
- Must manually generate trades (10 min)
- Must manually execute trades (10 min)
- Must manually update performance (5 min)
- Total: 55 minutes of manual work EVERY trading day

**Without computer settings:**
- Computer goes to sleep before 8:30 AM
- Automation doesn't run
- Wake up to no trades executed
- Same as Nov 20 failure

**Bottom Line**: These 50 minutes of work this weekend save you 55 minutes EVERY trading day going forward. That's 275 minutes saved per week (4.6 hours)!

---

**Good luck! You've got this! 🚀**
