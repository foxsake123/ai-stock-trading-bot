# QUICK FIX CHECKLIST - November 15, 2025
## Get Automation Working for Monday

**Time Required**: 10 minutes total
**Priority**: DO TONIGHT

---

## ✅ STEP-BY-STEP CHECKLIST

### **Step 1: Fix Task Scheduler Settings** (5 minutes)

```bash
# Right-click this file and select "Run as administrator":
fix_task_settings.bat
```

**What it does**:
- Recreates all 4 tasks
- Enables "Wake computer to run this task"
- Runs diagnostics to verify

**Expected output**: "[OK] NO CRITICAL ISSUES FOUND"

---

### **Step 2: Configure Windows Power Settings** (2 minutes)

1. Press **Win+I** (Settings)
2. Go to: **System → Power & Sleep**
3. Under "Screen and sleep":
   - Set **"When plugged in, PC goes to sleep after"** → **NEVER**
4. Close Settings

---

### **Step 3: Verify Research Generation** (1 minute)

```bash
# Check if research was generated:
ls reports/premarket/2025-11-18/
```

**Expected**: 6-7 files (3 markdown + 3-4 PDFs)

**If empty**, run manually:
```bash
python scripts/automation/daily_claude_research.py --force
```

Wait 10-15 minutes for completion.

---

### **Step 4: Run Final Diagnostics** (1 minute)

```bash
python diagnose_automation.py
```

**Expected output**:
```
[OK] NO CRITICAL ISSUES FOUND
Tasks appear to be configured correctly.
```

**If still showing issues**: Review the output and fix manually.

---

### **Step 5: Test Tomorrow (Saturday 12:05 PM)** (1 minute)

Check if weekend research ran automatically:

```bash
ls reports/premarket/2025-11-19/
```

**If files exist**: ✅ Automation working!
**If empty**: Computer was off or still has issues.

---

## 🎯 DONE!

Once all 5 steps complete:
- ✅ Automation fixed
- ✅ Computer won't sleep
- ✅ Research ready for Monday
- ✅ System verified

**Monday morning**: Automation will run automatically at 8:30 AM.

**Your job**: Check Telegram at 8:35 AM, 9:35 AM, 4:35 PM.

---

*If you have any issues, see AUTOMATION_ISSUES_2025-11-15.md for detailed troubleshooting.*
