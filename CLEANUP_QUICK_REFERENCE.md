# Repository Cleanup - Quick Reference
## AI Stock Trading Bot | October 23, 2025

---

## Executive Summary

**Current State:** 40MB repository, 27 root files, 30+ empty directories, duplicate agent code
**Target State:** 24.8MB repository, 15-18 root files, 0 empty directories, consolidated code
**Potential Savings:** 15.2MB (38% reduction)

**Files Created:**
1. `REPOSITORY_CLEANUP_ANALYSIS.md` - Comprehensive 50-page analysis
2. `cleanup_safe_actions.sh` - Automated safe cleanup (Linux/Mac)
3. `cleanup_safe_actions.bat` - Automated safe cleanup (Windows)
4. `CLEANUP_QUICK_REFERENCE.md` - This file

---

## Critical Issues Found

### 1. DUPLICATE AGENT CODE (CRITICAL)
- **Problem:** `agents/` (628KB) and `src/agents/` (1.8MB) contain overlapping but DIFFERENT code
- **Impact:** Which version is correct? Maintenance nightmare!
- **Action Required:** Manual review and consolidation
- **Priority:** CRITICAL (must fix before other changes)
- **Time:** 2-3 hours
- **Risk:** HIGH (requires careful import path updates)

### 2. TEST ARTIFACTS IN VERSION CONTROL (HIGH)
- **Problem:** 5.4MB of regenerable files committed (htmlcov/, .coverage, __pycache__)
- **Impact:** Bloated repository, unnecessary clutter
- **Action Required:** Delete and add to .gitignore
- **Priority:** HIGH (safe and easy)
- **Time:** 5 minutes (automated script available)
- **Risk:** NONE (all files are regenerable)

### 3. ROOT DIRECTORY CLUTTER (HIGH)
- **Problem:** 27 files in root (target: 15-18)
- **Impact:** Hard to find important files
- **Action Required:** Move files to appropriate subdirectories
- **Priority:** HIGH
- **Time:** 1 hour
- **Risk:** LOW (just file moves)

### 4. SCATTERED REPORT LOCATIONS (MEDIUM)
- **Problem:** 5 different report directories, old format files mixed with new
- **Impact:** Confusing structure
- **Action Required:** Consolidate to clean date-based structure
- **Priority:** MEDIUM
- **Time:** 1-2 hours
- **Risk:** LOW (archiving, not deleting)

### 5. 30+ EMPTY DIRECTORIES (MEDIUM)
- **Problem:** Empty directories throughout repository
- **Impact:** Clutter, confusion
- **Action Required:** Delete all empty directories
- **Priority:** MEDIUM (quick win)
- **Time:** 5 minutes (automated script available)
- **Risk:** NONE

---

## Quick Start - Safe Cleanup (5 minutes)

**For Windows:**
```batch
cleanup_safe_actions.bat
```

**For Linux/Mac:**
```bash
chmod +x cleanup_safe_actions.sh
./cleanup_safe_actions.sh
```

**What it does:**
- Deletes test artifacts (5.4MB): `.coverage`, `htmlcov/`, `.pytest_cache/`
- Removes Python cache: `__pycache__/` directories
- Deletes orphaned files: `nul`, `REPORT_CLEANUP_PLAN.md`, `.env.template`
- Removes 30+ empty directories
- Updates `.gitignore` with test artifact patterns

**What it DOESN'T do:**
- Touch agent code (requires manual review)
- Move files from root (requires path updates)
- Reorganize reports (requires validation)

**After running:**
```bash
git status                    # See what changed
pytest tests/ -v              # Verify tests still pass
git add .gitignore           # Stage .gitignore changes
git commit -m "chore: remove test artifacts and empty directories"
```

**Result:** ~5.4MB freed, cleaner repository, NO risk

---

## Implementation Priority

### Phase 1: CRITICAL - Agent Consolidation (2-3 hours)
**Status:** ⚠️ REQUIRES MANUAL REVIEW

**The Problem:**
```
agents/fundamental_analyst.py          (agents/ version)
src/agents/fundamental_analyst.py      (src/agents/ version)
                                       ↑ DIFFERENT FILES! ↑
```

**Before You Start:**
1. Run full test suite: `pytest tests/ -v`
2. Check which imports are used: `grep -r "from agents" . && grep -r "from src.agents" .`
3. Based on CLAUDE.md, `agents/` appears to be canonical

**Steps:**
1. Compare file sizes: `du -sh agents/ src/agents/`
2. Compare specific files: `diff agents/fundamental_analyst.py src/agents/fundamental_analyst.py`
3. Identify which directory is canonical (likely `agents/`)
4. Search for imports: `grep -r "from src\.agents" --include="*.py" .`
5. Update all imports from `from src.agents` to `from agents`
6. Test: `pytest tests/ -v`
7. Delete non-canonical directory: `rm -rf src/agents/`
8. Test again: `pytest tests/ -v`
9. Commit: `git commit -m "refactor: consolidate agent code to agents/ directory"`

**Files Only in agents/ (must preserve):**
- `agents/core/` - Execution scripts
- `agents/dee-bot/standalone/` - Analysis scripts
- `agents/shorgan-bot/standalone/` - Strategy docs
- `agents/technical_analyst.py`
- `agents/debate_system.py`

**Files Only in src/agents/ (evaluate before deleting):**
- `src/agents/bear_analyst.py`
- `src/agents/bull_analyst.py`
- `src/agents/debate_coordinator.py`
- `src/agents/debate_orchestrator.py`
- `src/agents/neutral_moderator.py`

**Verification:**
```bash
# After consolidation
pytest tests/ -v              # All 471 tests should pass
python -m py_compile agents/*.py  # No import errors
grep -r "from src\.agents" --include="*.py" .  # Should return nothing
```

---

### Phase 2: HIGH - Root Directory Cleanup (1 hour)
**Status:** ✅ LOW RISK (just file moves)

**Current Root (27 files):**
```
.coverage ..................... DELETE (test artifact)
.env .......................... KEEP (ensure .gitignored)
.env.example .................. KEEP
.env.template ................. DELETE (duplicate)
CLAUDE.md ..................... KEEP (primary docs)
complete_setup.py ............. KEEP
config.yaml ................... MOVE to config/main_config.yaml
CONTRIBUTING.md ............... KEEP
DOCUMENTATION_INDEX.md ........ KEEP
main.py ....................... KEEP
Makefile ...................... KEEP
nul ........................... DELETE (Windows error)
performance_results.png ....... MOVE to docs/images/
pytest.ini .................... KEEP
QUICKSTART.md ................. KEEP
README.md ..................... KEEP
REPORT_CLEANUP_PLAN.md ........ DELETE (obsolete)
requirements.txt .............. KEEP
run_tests.sh .................. MOVE to scripts/testing/
SETUP_FIX_GUIDE.md ............ MOVE to docs/setup/
setup_scheduler.ps1 ........... MOVE to scripts/windows/
SYSTEM_OVERVIEW.md ............ MOVE to docs/
web_dashboard.py .............. MOVE to scripts/dashboard/
```

**Commands:**
```bash
# Create directories
mkdir -p docs/images docs/setup scripts/testing scripts/dashboard

# Move files
mv config.yaml config/main_config.yaml
mv performance_results.png docs/images/
mv SETUP_FIX_GUIDE.md docs/setup/
mv SYSTEM_OVERVIEW.md docs/
mv run_tests.sh scripts/testing/
mv setup_scheduler.ps1 scripts/windows/
mv web_dashboard.py scripts/dashboard/

# Update any hardcoded paths in scripts
grep -r "web_dashboard.py" --include="*.py" --include="*.bat" --include="*.sh" .
# Update found references to new location

# Test
python scripts/dashboard/web_dashboard.py --help
bash scripts/testing/run_tests.sh
```

**Result:** 27 → 18 root files (-33%)

---

### Phase 3: HIGH - Delete Empty Directories (5 minutes)
**Status:** ✅ AUTOMATED (run script)

Already handled by `cleanup_safe_actions.sh` or `.bat`

---

### Phase 4: MEDIUM - Reports Consolidation (1-2 hours)
**Status:** ⚠️ REQUIRES VALIDATION

**Target Structure:**
```
reports/
├── premarket/
│   ├── YYYY-MM-DD/          # Active daily research
│   │   ├── claude_research.md
│   │   ├── claude_research_dee_bot_YYYY-MM-DD.md
│   │   ├── claude_research_shorgan_bot_YYYY-MM-DD.md
│   │   └── (PDFs)
│   └── latest/              # Symlink to most recent
├── postmarket/YYYY-MM-DD/   # Daily summaries
├── execution/YYYY-MM-DD/    # Trade execution logs
└── archive/YYYY-MM/         # Old reports (30+ days)
```

**Actions:**

1. **Archive old format files:**
   ```bash
   mkdir -p reports/archive/2025-10/old-format
   mv reports/premarket/*.md reports/archive/2025-10/old-format/ 2>/dev/null || true
   mv reports/premarket/*.json reports/archive/2025-10/old-format/ 2>/dev/null || true
   # Preserve date-based directories
   ```

2. **Move execution logs:**
   ```bash
   mkdir -p reports/execution
   mv data/daily/reports/* reports/execution/ 2>/dev/null || true
   ```

3. **Move postmarket reports:**
   ```bash
   mkdir -p reports/postmarket
   mv docs/reports/post-market/* reports/postmarket/ 2>/dev/null || true
   ```

4. **Archive scripts-and-data:**
   ```bash
   mkdir -p reports/archive/2025-10/old-weekly-structure
   mv scripts-and-data/* reports/archive/2025-10/old-weekly-structure/ 2>/dev/null || true
   rmdir scripts-and-data 2>/dev/null || true
   ```

5. **Move instagram log:**
   ```bash
   mkdir -p logs/notifications
   mv reports/instagram_notifications.log logs/notifications/ 2>/dev/null || true
   ```

6. **Update scripts with new paths:**
   ```bash
   grep -r "data/daily/reports" --include="*.py" .
   # Update found references to reports/execution/

   grep -r "docs/reports/post-market" --include="*.py" .
   # Update found references to reports/postmarket/
   ```

**Verification:**
```bash
# Check old locations are empty
ls data/daily/reports/
ls docs/reports/post-market/
ls scripts-and-data/ 2>/dev/null

# Check new structure
tree reports/ -L 2

# Test report generation
python scripts/automation/daily_claude_research.py --help
```

---

### Phases 5-8: OPTIONAL Improvements

**Phase 5: Reorganize Deployment Files (30 min)**
- Move systemd files to deployment/systemd/
- Move Windows files to deployment/windows/
- See REPOSITORY_CLEANUP_ANALYSIS.md for details

**Phase 6: Consolidate Windows Scripts (30 min)**
- Organize .bat files by purpose (automation/setup/manual)
- See REPOSITORY_CLEANUP_ANALYSIS.md for details

**Phase 7: Documentation Cleanup (1-2 hours)**
- Archive old status/summary files
- Consolidate overlapping docs
- See REPOSITORY_CLEANUP_ANALYSIS.md for details

**Phase 8: Archive Frontend Code (15 min)**
- Move unused React dashboard to archive/
- See REPOSITORY_CLEANUP_ANALYSIS.md for details

---

## Testing After Each Phase

**After EVERY phase, run:**
```bash
# 1. Check git status
git status

# 2. Run test suite
pytest tests/ -v

# 3. Verify no broken imports
python -m py_compile **/*.py

# 4. Test key scripts
python scripts/automation/daily_claude_research.py --help
python scripts/dashboard/web_dashboard.py --help

# 5. If all pass, commit
git add .
git commit -m "chore: [describe cleanup action]"
```

**If tests fail:**
1. Check for import errors in output
2. Update import paths to new locations
3. Re-run tests
4. Don't proceed until tests pass

---

## Space Savings Summary

| Action | Savings | Risk |
|--------|---------|------|
| Delete test artifacts | 5.4MB | NONE |
| Delete agent duplication | 1.8MB | HIGH* |
| Root directory cleanup | 603KB | LOW |
| Delete obsolete dirs | 44KB | LOW |
| Documentation moves | 200KB | LOW |
| Miscellaneous | 3KB | NONE |
| **TOTAL** | **~8MB** | **Varies** |

*Risk is HIGH only during transition; LOW after successful consolidation

---

## Final Checklist

**Before you start:**
- [ ] Commit all current changes (`git commit -am "checkpoint before cleanup"`)
- [ ] Run full test suite (`pytest tests/ -v`) - should see 471 passing
- [ ] Create backup branch (`git checkout -b pre-cleanup-backup`)
- [ ] Read REPOSITORY_CLEANUP_ANALYSIS.md (comprehensive guide)

**Safe cleanup (5 minutes):**
- [ ] Run `cleanup_safe_actions.bat` (Windows) or `cleanup_safe_actions.sh` (Linux/Mac)
- [ ] Verify tests pass: `pytest tests/ -v`
- [ ] Commit: `git commit -m "chore: remove test artifacts and empty directories"`

**Agent consolidation (2-3 hours):**
- [ ] Compare `agents/` vs `src/agents/` file by file
- [ ] Determine canonical location (likely `agents/`)
- [ ] Search for `from src.agents` imports
- [ ] Update all import paths
- [ ] Test: `pytest tests/ -v`
- [ ] Delete non-canonical directory
- [ ] Test again: `pytest tests/ -v`
- [ ] Commit: `git commit -m "refactor: consolidate agent code"`

**Root cleanup (1 hour):**
- [ ] Create directories: `docs/images`, `docs/setup`, `scripts/testing`, `scripts/dashboard`
- [ ] Move files per Phase 2 list
- [ ] Update hardcoded paths in scripts
- [ ] Test moved scripts
- [ ] Commit: `git commit -m "chore: organize root directory"`

**Reports consolidation (1-2 hours):**
- [ ] Archive old format files
- [ ] Move execution logs to `reports/execution/`
- [ ] Move postmarket reports to `reports/postmarket/`
- [ ] Update script paths
- [ ] Test report generation
- [ ] Commit: `git commit -m "chore: consolidate reports structure"`

**Optional improvements:**
- [ ] Phase 5: Deployment files (30 min)
- [ ] Phase 6: Windows scripts (30 min)
- [ ] Phase 7: Documentation (1-2 hours)
- [ ] Phase 8: Frontend archive (15 min)

**Final verification:**
- [ ] All tests pass: `pytest tests/ -v` (471 tests)
- [ ] No broken imports: `python -m py_compile **/*.py`
- [ ] Git status clean: `git status`
- [ ] Root directory has 15-18 files (down from 27)
- [ ] No empty directories: `find . -type d -empty | grep -v .git`
- [ ] Repository size reduced: `du -sh .` (should be ~25MB)

---

## Getting Help

**If something breaks:**
1. Check git log: `git log --oneline -10`
2. Revert last commit: `git revert HEAD`
3. Or restore from backup branch: `git checkout pre-cleanup-backup`

**If tests fail:**
1. Read pytest output carefully
2. Check for import errors
3. Search for old file paths: `grep -r "old/path" --include="*.py" .`
4. Update to new paths
5. Re-run tests

**If imports are broken:**
1. Search for old import: `grep -r "from old_location" --include="*.py" .`
2. Replace with new import path
3. Test specific file: `python -m py_compile path/to/file.py`
4. Run test suite: `pytest tests/ -v`

---

## Success Metrics

**Before Cleanup:**
- Repository size: 40MB
- Root directory: 27 files
- Empty directories: 30+
- Duplicate code: agents/ + src/agents/
- Organization score: 68/100

**After Cleanup (Target):**
- Repository size: 24.8MB (-38%)
- Root directory: 15-18 files (-33%)
- Empty directories: 0
- Duplicate code: Consolidated
- Organization score: 92/100

**All tests passing:** 471/471 ✓

---

## Quick Commands Reference

```bash
# Safe cleanup (automated)
./cleanup_safe_actions.sh        # Linux/Mac
cleanup_safe_actions.bat         # Windows

# Test suite
pytest tests/ -v                 # Run all tests
pytest tests/agents/ -v          # Test agents only

# Find imports
grep -r "from agents" --include="*.py" .
grep -r "from src.agents" --include="*.py" .

# Find file references
grep -r "web_dashboard.py" --include="*.py" --include="*.bat" .
grep -r "data/daily/reports" --include="*.py" .

# Check for empty directories
find . -type d -empty | grep -v .git

# Repository size
du -sh .
du -sh */ | sort -h

# Git status
git status
git log --oneline -10
git diff HEAD~1

# Verify Python files
python -m py_compile **/*.py
```

---

**For full details, see:**
- `REPOSITORY_CLEANUP_ANALYSIS.md` (50 pages, comprehensive analysis)
- `cleanup_safe_actions.sh` (automated safe cleanup script)
- `cleanup_safe_actions.bat` (Windows version)

**Generated:** October 23, 2025
**Status:** Ready to execute
**Estimated Total Time:** 6-8 hours (can be done incrementally)
