# Repository Reorganization - Quick Start Guide

**Date:** October 23, 2025
**Estimated Time:** 8-12 hours
**Status:** Ready to Execute

---

## 🎯 Overview

This guide provides a quick-start path to reorganize your AI trading bot repository for better scalability, maintainability, and clarity.

**See `REPOSITORY_REORGANIZATION_PLAN.md` for complete details.**

---

## 📊 Before vs After

### Current Issues
- ❌ 70+ files in root directory
- ❌ Redundant data directories (data/, data_sources/, scripts-and-data/)
- ❌ Scattered configs (root clutter)
- ❌ Mixed concerns (agents in multiple places)
- ❌ Unclear data flow

### After Reorganization
- ✅ Clean root with 7-10 key files
- ✅ Single /data/ directory with clear structure
- ✅ All configs in /config/
- ✅ All agents in /src/agents/
- ✅ Clear: config → src → scripts → data → reports → logs

---

## 🚀 Quick Migration (Recommended Order)

### Step 1: Backup (5 minutes)
```bash
# Create backup branch
git checkout -b backup-before-reorganization
git add .
git commit -m "backup: pre-reorganization state"
git push origin backup-before-reorganization

# Create reorganization branch
git checkout -b reorganization
```

### Step 2: Create New Structure (10 minutes)
```bash
# Run this script to create all directories
mkdir -p config/bots
mkdir -p src/{agents,strategies,data,signals,execution,risk,reports,notifications,monitoring,integration,utils}
mkdir -p scripts/{automation,portfolio,monitoring,setup,utilities}
mkdir -p tests/{unit,integration,performance,fixtures}
mkdir -p backtesting/scenarios
mkdir -p data/{cache,historical,state}
mkdir -p reports/{premarket,postmarket,performance,archive}
mkdir -p logs/{system,trading,errors}
mkdir -p docs/{architecture,guides,strategies,api,sessions}

# Create __init__.py files
find src -type d -exec touch {}/__init__.py \;
find tests -type d -exec touch {}/__init__.py \;
touch backtesting/__init__.py
```

### Step 3: Move Core Files (30-45 minutes)

**Priority 1: Configuration** (10 min)
```bash
# Move configs
mv config.yaml config/
cp .env config/api_keys.yaml  # Copy, don't move original
mv schedule_config.py config/schedule.yaml

# Create .env.example if not exists
cp config/api_keys.yaml .env.example
# Edit .env.example to remove real keys
```

**Priority 2: Source Code** (20 min)
```bash
# Move agents
mv agents/*.py src/agents/
mv agents/communication src/agents/

# Move strategies (complex, do carefully)
# See detailed steps in full plan

# Move data sources
mv data_sources/* src/data/sources/ 2>/dev/null || true
```

**Priority 3: Scripts** (10 min)
```bash
# Already mostly organized, just verify
ls scripts/automation/
ls scripts/portfolio/
ls scripts/monitoring/
```

**Priority 4: Tests** (5 min)
```bash
# Move unit tests
mv tests/agents/* tests/unit/agents/ 2>/dev/null || true
```

### Step 4: Update Imports (1-2 hours)

**Strategy: Incremental Updates**
```bash
# 1. Update one module at a time
# 2. Run tests after each update
# 3. Fix any broken imports

# Example: Update fundamental_analyst.py
# Old: from agents.base_agent import BaseAgent
# New: from src.agents.base_agent import BaseAgent

# Use search-and-replace:
# Find: "from agents."
# Replace: "from src.agents."
```

### Step 5: Validation (30 minutes)
```bash
# Run tests
pytest tests/ -v

# Run health check
python scripts/monitoring/health_check.py

# Test daily workflow (dry-run)
python scripts/automation/send_enhanced_morning_report.py --help
```

### Step 6: Clean Up (30 minutes)
```bash
# Remove redundant directories
rm -rf scripts-and-data/  # After verifying no unique files
rm -rf C:Usersshorgai-stock-trading-botbenchmarksreports/

# Move session summaries
mv session-summaries/* docs/sessions/
rm -rf session-summaries/

# Move markdown docs to docs/
mv *.md docs/ || true  # Keep README.md, CHANGELOG.md, LICENSE in root
```

### Step 7: Commit & Test (15 minutes)
```bash
# Commit changes
git add .
git commit -m "refactor: reorganize repository structure

- Move configs to /config/
- Consolidate source code in /src/
- Organize tests by type
- Create clear data/reports/logs structure
- Update imports throughout codebase

BREAKING CHANGE: Import paths changed from 'agents.*' to 'src.agents.*'
"

# Run full test suite
pytest tests/ --cov=src

# If all tests pass
git push origin reorganization

# Create PR or merge to main
```

---

## 🎨 New Structure at a Glance

```
ai-stock-trading-bot/
├── config/              # ⚙️ All settings
│   ├── api_keys.yaml
│   ├── trading.yaml
│   └── bots/
│
├── src/                 # 🧠 Core code
│   ├── agents/
│   ├── strategies/
│   ├── data/
│   ├── execution/
│   └── reports/
│
├── scripts/             # 🚀 Operations
│   ├── automation/
│   ├── portfolio/
│   └── monitoring/
│
├── tests/               # 🧪 Testing
│   ├── unit/
│   ├── integration/
│   └── performance/
│
├── data/                # 💾 Storage
│   ├── cache/
│   ├── historical/
│   └── state/
│
├── reports/             # 📊 Outputs
│   ├── premarket/
│   ├── postmarket/
│   └── performance/
│
├── logs/                # 📝 Logs
│   ├── system/
│   ├── trading/
│   └── errors/
│
└── docs/                # 📚 Docs
    ├── guides/
    ├── strategies/
    └── sessions/
```

---

## 🔥 Critical Migration Notes

### DO NOT Move These (Yet)
1. `.env` - Keep working copy, copy to config/
2. `requirements.txt` - Keep in root
3. `.gitignore` - Keep in root
4. `pytest.ini` - Keep in root
5. `README.md` - Keep in root

### Import Path Changes
```python
# Before
from agents.fundamental_analyst import FundamentalAnalyst
from data.loaders import load_market_data

# After
from src.agents.fundamental_analyst import FundamentalAnalyst
from src.data.loaders.market_data import load_market_data
```

### Test After Each Step
```bash
# Quick test
pytest tests/unit/agents/test_fundamental_analyst.py -v

# Full test
pytest tests/ --tb=short

# Health check
python scripts/monitoring/health_check.py
```

---

## 📋 Checklist

### Pre-Migration
- [ ] Read full plan: `REPOSITORY_REORGANIZATION_PLAN.md`
- [ ] Create backup branch
- [ ] Understand import path changes
- [ ] Have 2-3 hours of uninterrupted time

### During Migration
- [ ] Create new directory structure
- [ ] Move configuration files
- [ ] Move source code to src/
- [ ] Move scripts (verify automation paths)
- [ ] Move tests to appropriate folders
- [ ] Update all imports
- [ ] Run tests after each major change

### Post-Migration
- [ ] All tests passing: `pytest tests/`
- [ ] Health check passing: `python scripts/monitoring/health_check.py`
- [ ] Daily workflow works: Test automation scripts
- [ ] Documentation updated: README, guides
- [ ] Git committed and pushed
- [ ] Clean up redundant directories

---

## 🆘 If Something Breaks

### Test Failures
```bash
# 1. Identify failing test
pytest tests/ -v

# 2. Check import error
# Most likely: Import path needs updating

# 3. Fix import in test or source
# Old: from agents.X import Y
# New: from src.agents.X import Y

# 4. Re-run test
pytest tests/path/to/test.py -v
```

### Script Failures
```bash
# 1. Check error message
python scripts/automation/daily_research.py

# 2. Update import paths in script
# 3. Update any hardcoded file paths
# 4. Test again
```

### Rollback
```bash
# If you need to rollback
git checkout backup-before-reorganization
git checkout -b main-backup
git push origin main-backup

# You can always return to this state
```

---

## 💡 Tips

1. **Go Slowly** - Move one module, test, commit
2. **Use Search** - Find all imports at once
3. **Test Often** - Catch issues early
4. **Keep Notes** - Document what broke and how you fixed it
5. **Ask Questions** - Review full plan if unsure

---

## 🎯 Success Criteria

After migration, verify:

✅ **Structure**
- All configs in /config/
- All source in /src/
- All tests in /tests/
- Clean root directory

✅ **Functionality**
- All tests pass
- Health check passes
- Can run daily automation
- Can generate reports

✅ **Documentation**
- README updated
- Import paths documented
- Migration notes saved

---

## 📚 Reference Documents

- **Full Plan:** `REPOSITORY_REORGANIZATION_PLAN.md` (complete details)
- **Before/After:** See "Proposed Directory Structure" in full plan
- **Migration Steps:** See "Migration Plan" section in full plan
- **Best Practices:** See "Best Practices Going Forward" in full plan

---

## ⏱️ Estimated Timeline

| Step | Time | Can Pause? |
|------|------|------------|
| Backup | 5 min | ✅ Yes |
| Create structure | 10 min | ✅ Yes |
| Move config | 10 min | ✅ Yes |
| Move source | 20 min | ✅ Yes |
| Move scripts | 10 min | ✅ Yes |
| Move tests | 5 min | ✅ Yes |
| Update imports | 2 hours | ✅ Yes (commit often) |
| Validation | 30 min | ❌ Finish this |
| Clean up | 30 min | ✅ Yes |
| **TOTAL** | **4-6 hours** | |

**Note:** Can be done over multiple sessions if you commit after each step.

---

## 🚦 Start Here

1. **Read this document** (5 min)
2. **Review full plan** (15 min): `REPOSITORY_REORGANIZATION_PLAN.md`
3. **Create backup** (5 min): `git checkout -b backup-before-reorganization`
4. **Begin Step 1** (Create structure)

**Good luck! The new structure will make your codebase much more maintainable.** 🚀

---

**Last Updated:** October 23, 2025
**Version:** 1.0
**Status:** Ready to Execute
