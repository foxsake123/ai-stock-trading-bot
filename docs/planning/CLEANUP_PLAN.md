# Root Directory Cleanup Plan
**Current State**: 71 files in root directory
**Target**: ~10-15 essential files in root
**Status**: Ready to execute

---

## Current Root Directory Issues

**Problems**:
1. **71 files in root** - Too cluttered
2. **17 Python scripts** - Should be in scripts/
3. **38+ markdown files** - Should be organized in docs/
4. **Multiple bat files** - Should be consolidated
5. **Duplicate/outdated files** - Need cleanup

---

## Proposed Organization

### Keep in Root (Essential Files Only)

**Core Files** (7):
- `README.md` - Main documentation
- `CLAUDE.md` - Session continuity
- `QUICKSTART.md` - Quick start guide
- `requirements.txt` - Dependencies
- `.env` - Environment variables (gitignored)
- `.gitignore` - Git configuration
- `LICENSE` - License file (if exists)

**Setup** (2):
- `complete_setup.py` - Windows-safe setup
- `SETUP_FIX_GUIDE.md` - Setup troubleshooting

**System Overview** (2):
- `SYSTEM_OVERVIEW.md` - Complete system guide
- `DOCUMENTATION_INDEX.md` - Doc navigation

**Total in Root**: ~11 essential files

---

## Files to Move

### 1. Python Scripts → `scripts/` or subdirectories

**Move to `scripts/`**:
```bash
backtest_recommendations.py → scripts/performance/
daily_premarket_report.py → scripts/automation/
demo_phase2.py → scripts/demos/
execute_dee_bot_rebalancing.py → scripts/execution/
execute_rebalancing.py → scripts/execution/
get_portfolio_status.py → scripts/performance/
health_check.py → scripts/monitoring/
main.py → scripts/ (or keep in root as entry point)
run_benchmarks.py → scripts/performance/
schedule_config.py → scripts/automation/
setup.py → scripts/ (duplicate of scripts/setup.py)
test_alpaca.py → tests/manual/
test_alpaca_dee_bot.py → tests/manual/
test_fd_api.py → tests/manual/
update_imports.py → scripts/utilities/
web_dashboard.py → scripts/ (or keep in root as entry point)
```

### 2. Documentation → `docs/`

**Move to `docs/guides/`**:
```bash
AUTOMATION_SETUP_COMPLETE.md → docs/guides/
ENHANCED_REPORTS_INTEGRATION.md → docs/guides/
FIX_DEE_API_PERMISSIONS.md → docs/guides/
MORNING_REPORT_SUMMARY.md → docs/guides/
PHASE2_COMPLETE.md → docs/guides/
PROJECT_COMPLETION_SUMMARY.md → docs/guides/
QUICK_REFERENCE_MULTI_ACCOUNT.md → docs/guides/
QUICK_START_ENHANCED_REPORTS.md → docs/guides/
QUICK_START_PHASE2.md → docs/guides/
SETUP_AUTOMATION.md → docs/guides/
TELEGRAM_REPORTS_GUIDE.md → docs/guides/
```

**Move to `docs/planning/`**:
```bash
ACTION_PLAN_OCT16_2025.md → docs/planning/
rebalancing_plan_2025-10-16.md → docs/planning/
REPOSITORY_REORGANIZATION_PLAN.md → docs/planning/
```

**Move to `docs/status/`**:
```bash
CHANGELOG.md → docs/status/
SESSION_COMPLETE_2025-10-23.md → docs/session-summaries/
```

**Move to `docs/archive/`** (outdated/duplicate):
```bash
DIRECTORY_STRUCTURE_VISUAL.md → docs/archive/
DOCUMENTATION_UPDATE_SUMMARY.md → docs/archive/
FOLDER_STRUCTURE.md → docs/archive/
REORGANIZATION_INDEX.md → docs/archive/
REORGANIZATION_QUICK_START.md → docs/archive/
REPOSITORY_REORGANIZATION_SUMMARY.md → docs/archive/
```

### 3. Batch Files → `scripts/windows/`

```bash
fix_scheduler.bat → scripts/windows/
run_research.bat → scripts/windows/
run_tests.bat → scripts/windows/
setup_scheduler.bat → scripts/windows/
```

### 4. Text/Report Files → `reports/setup/`

```bash
setup_complete_report.txt → reports/setup/
setup_report.txt → reports/setup/
```

### 5. Requirements Files

**Keep in Root**:
- `requirements.txt` - Main dependencies

**Move to `configs/`**:
- `requirements-dev.txt` → configs/requirements/
- `requirements-enhanced-apis.txt` → configs/requirements/

---

## Execution Plan

### Phase 1: Create Directories

```bash
mkdir -p scripts/demos
mkdir -p scripts/execution
mkdir -p scripts/utilities
mkdir -p scripts/windows
mkdir -p tests/manual
mkdir -p docs/guides
mkdir -p docs/planning
mkdir -p docs/status
mkdir -p docs/archive
mkdir -p configs/requirements
mkdir -p reports/setup
```

### Phase 2: Move Python Scripts

```bash
# Performance/monitoring scripts
mv backtest_recommendations.py scripts/performance/
mv get_portfolio_status.py scripts/performance/
mv run_benchmarks.py scripts/performance/
mv health_check.py scripts/monitoring/

# Automation scripts
mv daily_premarket_report.py scripts/automation/
mv schedule_config.py scripts/automation/

# Execution scripts
mv execute_dee_bot_rebalancing.py scripts/execution/
mv execute_rebalancing.py scripts/execution/

# Demo/test scripts
mv demo_phase2.py scripts/demos/
mv test_alpaca.py tests/manual/
mv test_alpaca_dee_bot.py tests/manual/
mv test_fd_api.py tests/manual/

# Utility scripts
mv update_imports.py scripts/utilities/

# Remove duplicate
rm setup.py  # Duplicate of scripts/setup.py
```

### Phase 3: Move Documentation

```bash
# Guides
mv AUTOMATION_SETUP_COMPLETE.md docs/guides/
mv ENHANCED_REPORTS_INTEGRATION.md docs/guides/
mv FIX_DEE_API_PERMISSIONS.md docs/guides/
mv MORNING_REPORT_SUMMARY.md docs/guides/
mv PHASE2_COMPLETE.md docs/guides/
mv PROJECT_COMPLETION_SUMMARY.md docs/guides/
mv QUICK_REFERENCE_MULTI_ACCOUNT.md docs/guides/
mv QUICK_START_ENHANCED_REPORTS.md docs/guides/
mv QUICK_START_PHASE2.md docs/guides/
mv SETUP_AUTOMATION.md docs/guides/
mv TELEGRAM_REPORTS_GUIDE.md docs/guides/

# Planning
mv ACTION_PLAN_OCT16_2025.md docs/planning/
mv rebalancing_plan_2025-10-16.md docs/planning/
mv REPOSITORY_REORGANIZATION_PLAN.md docs/planning/

# Status
mv CHANGELOG.md docs/status/
mv SESSION_COMPLETE_2025-10-23.md docs/session-summaries/

# Archive (outdated)
mv DIRECTORY_STRUCTURE_VISUAL.md docs/archive/
mv DOCUMENTATION_UPDATE_SUMMARY.md docs/archive/
mv FOLDER_STRUCTURE.md docs/archive/
mv REORGANIZATION_INDEX.md docs/archive/
mv REORGANIZATION_QUICK_START.md docs/archive/
mv REPOSITORY_REORGANIZATION_SUMMARY.md docs/archive/
```

### Phase 4: Move Batch Files

```bash
mv fix_scheduler.bat scripts/windows/
mv run_research.bat scripts/windows/
mv run_tests.bat scripts/windows/
mv setup_scheduler.bat scripts/windows/
```

### Phase 5: Move Other Files

```bash
# Setup reports
mv setup_complete_report.txt reports/setup/
mv setup_report.txt reports/setup/

# Requirements
mv requirements-dev.txt configs/requirements/
mv requirements-enhanced-apis.txt configs/requirements/
```

### Phase 6: Update References

**Update these files**:
1. `DOCUMENTATION_INDEX.md` - Update all file paths
2. `SYSTEM_OVERVIEW.md` - Update command paths
3. `README.md` - Update script paths
4. `CLAUDE.md` - Note reorganization
5. Any scripts that import from root

---

## After Cleanup - Root Directory Should Have

**Essential Files** (~11):
```
ai-stock-trading-bot/
├── README.md                           # Main docs
├── CLAUDE.md                           # Session continuity
├── QUICKSTART.md                       # Quick start
├── SYSTEM_OVERVIEW.md                  # System guide
├── DOCUMENTATION_INDEX.md              # Doc navigation
├── SETUP_FIX_GUIDE.md                  # Setup help
├── CONTRIBUTING.md                     # Dev guide
├── complete_setup.py                   # Setup script
├── main.py                             # Main entry (optional)
├── web_dashboard.py                    # Dashboard (optional)
├── requirements.txt                    # Dependencies
├── .env                                # Environment (gitignored)
├── .gitignore                          # Git config
└── LICENSE                             # License (if exists)
```

**Plus Standard Directories**:
```
├── configs/                            # Configuration files
├── data/                               # Data files
├── docs/                               # Documentation
├── logs/                               # Log files
├── reports/                            # Generated reports
├── scripts/                            # All scripts
├── src/                                # Source code
├── tests/                              # Test suite
└── [other standard dirs]
```

---

## Benefits of Cleanup

1. **Easier Navigation**: ~11 files vs 71 in root
2. **Clear Organization**: Everything has its place
3. **Professional Structure**: Industry standard layout
4. **Better Discovery**: Files grouped by purpose
5. **Reduced Confusion**: No duplicate/outdated files
6. **Easier Maintenance**: Clear what's important

---

## Risk Assessment

**Low Risk**:
- Moving docs to docs/ (just file moves)
- Moving batch files to scripts/windows/
- Archiving outdated docs

**Medium Risk**:
- Moving Python scripts (need to update imports)
- Updating DOCUMENTATION_INDEX.md paths

**Mitigation**:
- Test after each phase
- Update import statements
- Keep git history (use `git mv`)
- Create backup commit before starting

---

## Execution Steps

### Recommended Approach

1. **Create backup commit** first
2. **Phase 1**: Create directories
3. **Phase 2-5**: Move files (use `git mv` for tracking)
4. **Phase 6**: Update references
5. **Test**: Run health check, tests
6. **Commit**: Clean reorganization commit

### Commands to Execute

See individual phase commands above.

---

## Status

- [ ] Backup commit created
- [ ] Directories created
- [ ] Python scripts moved
- [ ] Documentation moved
- [ ] Batch files moved
- [ ] Other files moved
- [ ] References updated
- [ ] Tests passing
- [ ] Final commit created

---

**Ready to Execute**: Yes
**Estimated Time**: 15-20 minutes
**Recommendation**: Execute now to clean up root directory
