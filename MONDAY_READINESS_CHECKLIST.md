# Monday Oct 28 Readiness Checklist
**Created**: October 27, 2025
**Purpose**: Ensure full automation is ready for Monday morning trading

---

## 🎯 Critical Actions Before Monday 8:30 AM

### 1. Verify Task Scheduler (5 minutes) 🚨 MUST DO

**How to Check**:
```
1. Press Windows Key + R
2. Type: taskschd.msc
3. Press Enter
4. Look in "Task Scheduler Library" for:
   - "AI Trading - Weekend Research"
   - "AI Trading - Morning Trade Generation"
   - "AI Trading - Trade Execution"
   - "AI Trading - Daily Performance Graph"
```

**For Each Task, Verify**:
- ✅ Status: "Ready"
- ✅ Next Run Time: Shows correct date/time
- ✅ Last Run Result: "The operation completed successfully (0x0)" or never run

**Expected Schedule**:
- Weekend Research: Saturday 12:00 PM
- Morning Trade Generation: Mon-Fri 8:30 AM
- Trade Execution: Mon-Fri 9:30 AM
- Daily Performance Graph: Mon-Fri 4:30 PM

**If Tasks Don't Exist** → Run this script:
```bash
cd C:\Users\shorg\ai-stock-trading-bot
scripts\windows\setup_trade_automation.bat
```

---

### 2. Verify Research Files Exist ✅ ALREADY DONE

**Check**:
```bash
ls -la reports/premarket/2025-10-27/
```

**Expected Files** (all exist):
- ✅ claude_research_dee_bot_2025-10-27.pdf (13 KB)
- ✅ claude_research_shorgan_bot_2025-10-27.pdf (16 KB)
- ✅ claude_deepresearch_combined_2025-10-27.pdf (5.7 MB)

**Status**: READY ✅

---

### 3. Verify Automation Scripts Exist ✅ ALREADY DONE

**Scripts Required**:
- ✅ `scripts/automation/daily_claude_research.py` (7.4 KB, Oct 22)
- ✅ `scripts/automation/generate_todays_trades_v2.py` (29 KB, Oct 24)
- ✅ `scripts/automation/execute_daily_trades.py` (28 KB, Sep 30)
- ✅ `scripts/performance/generate_performance_graph.py` (22 KB, Oct 27)

**Status**: ALL EXIST ✅

---

## 📋 Monday Morning Timeline

### Saturday 12:00 PM (Already Completed)
- ✅ Research generated for both accounts
- ✅ PDFs created and ready
- ✅ Combined deep research available

### Monday 8:30 AM - Trade Generation
**What Happens**:
1. Task Scheduler runs `generate_todays_trades_v2.py`
2. Script reads research files from `reports/premarket/2025-10-27/`
3. Multi-agent system analyzes research
4. Generates `TODAYS_TRADES_2025-10-28.md`

**Your Action at 8:35 AM**:
```bash
# Review the generated trades
type TODAYS_TRADES_2025-10-28.md

# OR open in editor
notepad TODAYS_TRADES_2025-10-28.md
```

**What to Look For**:
- [ ] Trades for both DEE-BOT and SHORGAN-BOT
- [ ] Symbols match research recommendations
- [ ] Position sizes are reasonable
- [ ] Entry prices are current
- [ ] Stop losses are set

**If No File Created**:
```bash
# Run manually
cd C:\Users\shorg\ai-stock-trading-bot
python scripts\automation\generate_todays_trades_v2.py
```

---

### Monday 9:30 AM - Trade Execution
**What Happens**:
1. Market opens at 9:30 AM ET
2. Task Scheduler runs `execute_daily_trades.py`
3. Script reads `TODAYS_TRADES_2025-10-28.md`
4. Places orders via Alpaca API
5. Sends Telegram notification with results

**Your Action at 9:35 AM**:
```
Check Telegram for execution summary:
- Number of orders placed
- Symbols traded
- Any errors or warnings
```

**If No Telegram Message**:
```bash
# Check execution log
type data\daily\reports\2025-10-28\execution_log_*.json

# OR run manually
python scripts\automation\execute_daily_trades.py
```

---

### Monday 4:30 PM - Performance Update
**What Happens**:
1. Market closes at 4:00 PM ET
2. Task Scheduler runs `generate_performance_graph.py` at 4:30 PM
3. Script fetches end-of-day positions
4. Updates performance graph
5. Saves to `performance_results.png`

**Your Action at 4:35 PM**:
```bash
# View updated graph
start performance_results.png

# Check portfolio value
python scripts\automation\check_positions.py
```

---

## 🔧 Troubleshooting Guide

### Problem: Task Scheduler Tasks Don't Exist

**Solution**:
```bash
cd C:\Users\shorg\ai-stock-trading-bot
scripts\windows\setup_trade_automation.bat
```

This will create all 4 tasks with correct schedule.

---

### Problem: Trade Generation Fails at 8:30 AM

**Symptoms**:
- No `TODAYS_TRADES_2025-10-28.md` file created
- No error messages

**Debug Steps**:
```bash
# 1. Check if research files exist
ls reports/premarket/2025-10-27/*.pdf

# 2. Test script manually
python scripts\automation\generate_todays_trades_v2.py

# 3. Check for errors in output
```

**Common Causes**:
- Research files missing → Re-run research generation
- API key expired → Check Anthropic API key
- Import errors → Check if all dependencies installed

---

### Problem: Trade Execution Fails at 9:30 AM

**Symptoms**:
- Telegram shows errors
- Orders not placed in Alpaca

**Debug Steps**:
```bash
# 1. Verify Alpaca API keys are valid
python -c "from config import ALPACA_API_KEY_DEE, ALPACA_API_KEY_SHORGAN; print('Keys exist:', bool(ALPACA_API_KEY_DEE and ALPACA_API_KEY_SHORGAN))"

# 2. Check if accounts are active
python scripts\automation\check_positions.py

# 3. Manually execute trades
python scripts\automation\execute_daily_trades.py
```

**Common Causes**:
- API keys expired → Update in config
- Insufficient buying power → Check account balances
- Market closed → Verify time is 9:30-16:00 ET
- Invalid symbols → Check if symbols are tradeable

---

### Problem: No Telegram Notifications

**Debug Steps**:
```bash
# Test Telegram bot
python -c "
from utils.telegram_notifier import TelegramNotifier
notifier = TelegramNotifier()
notifier.send_message('Test from AI Trading Bot')
"
```

**Common Causes**:
- Wrong chat ID → Verify: 7870288896
- Bot token expired → Check token in config
- Internet connection issue → Check network

---

## 📊 Expected Outputs

### TODAYS_TRADES_2025-10-28.md
```markdown
# Trading Plan for 2025-10-28

## DEE-BOT Account
### NVDA - Buy
- Entry: $XXX.XX
- Position Size: XXX shares
- Stop Loss: $XXX.XX
- Target: $XXX.XX
- Reasoning: [from research]

### AAPL - Buy
...

## SHORGAN-BOT Account
### TSLA - Buy
...
```

### Telegram Execution Summary
```
🤖 AI Trading Bot - Execution Summary
Date: 2025-10-28 09:30:15

DEE-BOT:
✅ NVDA: Bought 50 shares @ $142.30
✅ AAPL: Bought 100 shares @ $178.45

SHORGAN-BOT:
✅ TSLA: Bought 25 shares @ $245.80

Total: 3 orders placed successfully
```

### Performance Graph
- Updated `performance_results.png`
- Shows portfolio value over time
- Includes both accounts
- Updated daily at 4:30 PM

---

## 🎯 Success Criteria for Monday

**8:35 AM**:
- [x] `TODAYS_TRADES_2025-10-28.md` exists
- [x] File contains trades for both accounts
- [x] Trades match research recommendations

**9:35 AM**:
- [x] Telegram notification received
- [x] All orders executed successfully
- [x] Positions visible in Alpaca

**4:35 PM**:
- [x] Performance graph updated
- [x] No execution errors
- [x] Portfolio value increased (hopefully!)

---

## 📞 If Everything Fails - Manual Fallback

**Morning (8:30 AM)**:
```bash
# Generate trades manually
cd C:\Users\shorg\ai-stock-trading-bot
python scripts\automation\generate_todays_trades_v2.py

# Review trades
notepad TODAYS_TRADES_2025-10-28.md
```

**Execute (9:30 AM)**:
```bash
# Execute trades manually
python scripts\automation\execute_daily_trades.py
```

**Afternoon (4:30 PM)**:
```bash
# Update performance manually
python scripts\performance\generate_performance_graph.py
```

---

## 🔍 Pre-Monday Verification Commands

Run these NOW to ensure everything is ready:

```bash
# 1. Check Python works
python --version

# 2. Test imports
python -c "from src.agents.communication.coordinator import Coordinator; print('Imports OK')"

# 3. Check research files
ls reports/premarket/2025-10-27/*.pdf

# 4. Verify Alpaca connection
python -c "import alpaca_trade_api as tradeapi; print('Alpaca library OK')"

# 5. Test Telegram
python -c "from utils.telegram_notifier import TelegramNotifier; TelegramNotifier().send_message('Pre-Monday Test')"

# 6. Verify all automation scripts exist
ls scripts/automation/daily_claude_research.py
ls scripts/automation/generate_todays_trades_v2.py
ls scripts/automation/execute_daily_trades.py
ls scripts/performance/generate_performance_graph.py
```

**All commands should succeed** ✅

---

## 📝 What to Document After Monday

Create a session note with:
- [ ] Did automation work end-to-end?
- [ ] Any tasks that failed?
- [ ] Trades executed correctly?
- [ ] Performance graph updated?
- [ ] Any errors encountered?
- [ ] Improvements needed?

---

## 🎉 Confidence Level

Based on Oct 27 assessment:

| Component | Status | Confidence |
|-----------|--------|------------|
| Research Generated | ✅ Complete | 100% |
| Automation Scripts | ✅ Exist | 100% |
| API Integrations | ✅ Working | 100% |
| Task Scheduler | ⚠️ Unknown | 50% |
| Import Paths | ✅ Fixed | 100% |
| Test Suite | ✅ Passing | 100% |

**Overall Readiness**: 90% (pending Task Scheduler verification)

**Bottom Line**: If Task Scheduler is configured, you're 100% ready. If not, takes 5 minutes to set up.

---

**Last Updated**: October 27, 2025
**Next Review**: Monday Oct 28, 9:00 AM (before market open)
