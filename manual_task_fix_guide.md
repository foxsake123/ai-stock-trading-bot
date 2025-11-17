# Manual Task Scheduler Fix Guide
## Enable "Wake Computer" for All Tasks

**Time Required**: 5 minutes
**Why Needed**: PowerShell commands to enable wake-from-sleep didn't work

---

## 📋 STEP-BY-STEP INSTRUCTIONS

### **1. Open Task Scheduler**

Press **Win+R**, type `taskschd.msc`, press Enter

---

### **2. Find AI Trading Tasks**

In left panel:
- Click **Task Scheduler Library**
- You'll see 4-5 "AI Trading" tasks in the middle panel

---

### **3. Fix EACH Task** (Repeat for all 4 tasks)

**Tasks to fix**:
1. AI Trading - Weekend Research
2. AI Trading - Morning Trade Generation
3. AI Trading - Trade Execution
4. AI Trading - Daily Performance Graph

**For EACH task**:

#### **a. Right-click task → Properties**

#### **b. General Tab**:
- ☑ Check: **"Run whether user is logged on or not"**
- ☑ Check: **"Run with highest privileges"**
- Select: **"Configure for: Windows 10"** (or your Windows version)

#### **c. Conditions Tab** ← CRITICAL:
- ☑ Check: **"Wake the computer to run this task"**
- ☐ UNCHECK: **"Start the task only if the computer is on AC power"**
- ☐ UNCHECK: **"Stop if the computer switches to battery power"**

#### **d. Settings Tab**:
- ☑ Check: **"Allow task to be run on demand"**
- ☐ UNCHECK: **"Stop the task if it runs longer than:"**
  - OR set to "2 hours" if you can't uncheck
- ☑ Check: **"If the running task does not end when requested, force it to stop"**
- ☑ Check: **"If the task is already running, then the following rule applies:"**
  - Select: **"Do not start a new instance"**

#### **e. Click OK**

- If prompted for password, enter your Windows password
- Click OK to save

---

### **4. Verify After All 4 Tasks**

Run diagnostics again:

```bash
python diagnose_automation.py
```

**Expected**: "Wake Computer: Yes" for all 4 tasks

---

## ✅ QUICK CHECKLIST (For Each Task)

**General Tab**:
- [X] Run whether user is logged on or not
- [X] Run with highest privileges

**Conditions Tab** ← MOST IMPORTANT:
- [X] Wake the computer to run this task
- [ ] Start only if on AC power (UNCHECKED)
- [ ] Stop if switches to battery (UNCHECKED)

**Settings Tab**:
- [X] Allow task to be run on demand
- [ ] Stop if runs longer than (UNCHECKED or 2 hours)

---

## 🎯 VISUAL GUIDE

When you open **Conditions Tab**, it should look like this:

```
☑ Start the task only if the computer is idle
  [Wait for idle for: 10 minutes]
  [ ] Stop if the computer ceases to be idle
  [ ] Restart if the idle state resumes

☑ Wake the computer to run this task    ← CHECK THIS!

Power
  [ ] Start the task only if the computer is on AC power    ← UNCHECK!
  [ ] Stop if the computer switches to battery power    ← UNCHECK!
```

---

## ⚠️ COMMON MISTAKES

**DON'T**:
- ❌ Leave "Start only if on AC power" CHECKED
- ❌ Leave "Wake computer" UNCHECKED
- ❌ Forget to click OK (changes won't save)
- ❌ Skip any of the 4 tasks

**DO**:
- ✅ Click OK after each task
- ✅ Enter password if prompted
- ✅ Verify all 4 tasks are fixed
- ✅ Run diagnostics to confirm

---

## 🔍 HOW TO VERIFY IT WORKED

**Option 1**: Run diagnostics
```bash
python diagnose_automation.py
```

Look for:
```
Wake Computer................. Yes    ← Should say "Yes"
```

**Option 2**: Check Task Scheduler
- Double-click task
- Go to Conditions tab
- Verify "Wake the computer to run this task" is CHECKED

---

## ⏱️ TIME ESTIMATE

- Task 1 (Weekend Research): 1 minute
- Task 2 (Morning Trade Generation): 1 minute
- Task 3 (Trade Execution): 1 minute
- Task 4 (Performance Graph): 1 minute
- Verification: 30 seconds

**Total**: ~5 minutes

---

*Created: November 15, 2025*
*Priority: CRITICAL*
*Next Step: Generate research after tasks are fixed*
