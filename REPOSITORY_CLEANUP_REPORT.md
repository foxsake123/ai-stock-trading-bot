# Repository Cleanup Report
Generated: October 26, 2025

## Executive Summary

### Critical Issues (Immediate Action Required)

1. **Multiple Alternative Data Aggregator Files** - 3 versions consuming space
2. **Dual Coordinator Files** - coordination/ and src/agents/communication/ have duplicates
3. **Large Python Cache** - 35+ __pycache__ directories consuming ~112KB
4. **HTML Coverage Reports** - 5.1MB of coverage reports in htmlcov/
5. **Backup Files** - .env.backup in root (3.5KB, should be in .gitignore)
6. **Log Files in Root** - 3 .log files (17KB total) cluttering root directory
7. **Empty nul File** - Windows-specific artifact in root

### Quick Wins (Low Risk, High Impact)

- Remove 35 __pycache__ directories (~112KB)
- Remove htmlcov/ directory (5.1MB, regenerable)
- Remove 3 root .log files (17KB)
- Remove .coverage file (53KB)
- Remove nul file (0 bytes)
- Add missing patterns to .gitignore

**Total Potential Space Savings: 5.5MB+ immediately**

### Repository Statistics

- **Total Size**: 85MB
- **Largest Directory**: reports/ (21MB)
- **Git History**: .git/ (46MB)
- **HTML Coverage**: htmlcov/ (5.1MB)
- **Documentation**: docs/ (3.3MB, 186 markdown files)
- **Tests**: tests/ (3.2MB)
- **Source Code**: src/ (1.9MB), scripts/ (1.9MB)

---

## Redundant Files Analysis

### 1. Alternative Data Aggregator - 3 Versions

**Files Found:**
```
data_sources/alternative_data_aggregator.py          901 lines  (DUPLICATE)
src/data/loaders/alternative_data_aggregator.py     483 lines  (DIFFERENT)
src/data/sources/alternative_data_aggregator.py     901 lines  (DUPLICATE)
```

**Analysis:**
- `data_sources/` and `src/data/sources/` are IDENTICAL (901 lines each)
- `src/data/loaders/` is a DIFFERENT version (483 lines)
- This suggests an incomplete migration or refactoring

**Imports Found:**
- `from data_sources`: 14 imports in codebase
- `from src.data`: 19 imports in codebase

**Recommendation - HIGH PRIORITY:**
```bash
# Option A: Keep src/data/sources/ as canonical
# 1. Update all imports from data_sources → src.data.sources
# 2. Delete data_sources/alternative_data_aggregator.py
# 3. Verify src/data/loaders/ version is still needed

# Option B: Keep data_sources/ as canonical
# 1. Update all imports from src.data → data_sources
# 2. Delete src/data/sources/alternative_data_aggregator.py
# 3. Clarify purpose of src/data/loaders/ version
```

**Risk Level**: MEDIUM - Requires import path updates

---

### 2. Catalyst Monitor - 2 Versions

**Files Found:**
```
monitoring/catalyst_monitor.py     557 lines
src/monitors/catalyst_monitor.py   552 lines  (5 lines different)
```

**Analysis:**
- Nearly identical (99% similarity)
- 5-line difference suggests minor divergence
- Different directory conventions (monitoring/ vs src/monitors/)

**Imports Found:**
- `from monitoring`: 2 imports
- `from src.monitors`: 5 imports

**Recommendation - HIGH PRIORITY:**
```bash
# Consolidate to src/monitors/ (more imports point here)
# 1. Diff the files to identify 5-line difference
# 2. Merge differences into src/monitors/catalyst_monitor.py
# 3. Update 2 imports from monitoring → src.monitors
# 4. Delete monitoring/catalyst_monitor.py
# 5. Move monitoring/ directory to archive if empty
```

**Risk Level**: LOW - Few imports to update

---

### 3. Coordinator Files - 2 Active Versions

**Files Found:**
```
communication/coordinator.py                       7,615 bytes
src/agents/communication/coordinator.py            ? bytes
docs/archive/legacy-agents-2025-10-23/communication/coordinator.py  (archived)
```

**Analysis:**
- Root `communication/` directory with single coordinator.py file
- `src/agents/communication/` has full communication package
- Archive properly contains legacy version

**Recommendation - MEDIUM PRIORITY:**
```bash
# Consolidate to src/agents/communication/
# 1. Compare communication/coordinator.py vs src/agents/communication/coordinator.py
# 2. If identical, delete communication/coordinator.py
# 3. Update imports (check main.py and other files)
# 4. Remove empty communication/ directory
```

**Risk Level**: MEDIUM - Core coordination logic

---

### 4. Reports Archive - 20MB

**Location**: `reports/archive/2025-10/`

**Contents:**
- 60+ markdown files
- 20+ PDF files (can be regenerated)
- Total size: 20MB

**Analysis:**
- Archive properly structured
- Contains dated research reports (Sept-Oct 2025)
- PDFs are regenerable from markdown

**Recommendation - LOW PRIORITY:**
```bash
# Option A: Keep as-is (properly archived)
# Option B: Compress older reports
find reports/archive/2025-10/ -name "*.pdf" -mtime +30 | xargs gzip

# Option C: Move to separate storage
# Move to Google Drive/Dropbox and add .gitignore pattern
reports/archive/2025-*/
```

**Space Savings**: Removing PDFs could free 5-8MB

**Risk Level**: LOW - Archive data

---

### 5. Scripts-and-Data Directory - 44KB

**Location**: `scripts-and-data/data/`

**Contents:**
```
data/reports/weekly/claude-research/claude_research_dee_bot_2025-10-16.md
data/reports/weekly/claude-research/claude_research_dee_bot_2025-10-16.pdf
data/reports/weekly/claude-research/claude_research_shorgan_bot_2025-10-16.md
data/reports/weekly/claude-research/claude_research_shorgan_bot_2025-10-16.pdf
```

**Analysis:**
- Contains Oct 16 research reports
- Same reports likely exist in reports/premarket/2025-10-16/
- Directory already in .gitignore but files still tracked

**Recommendation - HIGH PRIORITY:**
```bash
# Verify reports exist elsewhere
ls reports/premarket/2025-10-16/

# If duplicates confirmed, remove
git rm -r scripts-and-data/
```

**Space Savings**: 44KB

**Risk Level**: LOW - Reports duplicated elsewhere

---

### 6. Empty Directories - 20 Found

**List:**
```
.git/objects/info
.git/objects/pack
.git/refs/tags
./archive
./backtesting/scenarios
./config/bots
./configs/bots
./data/cache
./data/execution/results
./data/historical/market
./data/historical/portfolio/shorgan-bot
./data/positions
./data/research
./data/state
./deployment/aws
./docs/api
./docs/architecture
./docs/strategies
./logs/performance
./logs/trades
```

**Recommendation - LOW PRIORITY:**
```bash
# Remove truly empty directories (not placeholder directories)
# Keep structural directories like:
# - data/cache (used by system)
# - logs/performance (used by logging)
# - logs/trades (used by logging)

# Safe to remove:
rmdir archive/
rmdir backtesting/scenarios/
rmdir deployment/aws/
rmdir docs/api/
rmdir docs/architecture/
rmdir docs/strategies/
```

**Risk Level**: VERY LOW - Empty directories

---

## Python Cache and Generated Files

### Python Cache Files

**Found:**
- 35 __pycache__ directories
- 90+ .pyc files
- Total: ~112KB

**Recommendation - IMMEDIATE:**
```bash
# Remove all __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} +

# Verify .gitignore has:
__pycache__/
*.pyc
*.pyo
*.pyd
```

**Space Savings**: ~112KB

**Risk Level**: NONE - Regenerable

---

### HTML Coverage Reports

**Location**: `htmlcov/`
**Size**: 5.1MB
**Files**: 100+ HTML files

**Recommendation - IMMEDIATE:**
```bash
# Remove coverage reports
rm -rf htmlcov/

# Verify .gitignore has:
htmlcov/
.coverage
.coverage.*
coverage.xml
```

**Space Savings**: 5.1MB

**Risk Level**: NONE - Regenerable with pytest --cov

---

### Root Directory Log Files

**Files:**
```
final_research_test.log       5.7KB
research_generation.log       5.7KB
research_test.log             5.7KB
```

**Recommendation - IMMEDIATE:**
```bash
# Remove log files from root
rm *.log

# Logs should be in logs/ directory only
# Verify .gitignore has:
*.log
```

**Space Savings**: 17KB

**Risk Level**: NONE - Test artifacts

---

### Backup Files

**Files:**
```
.env.backup                   3.5KB
```

**Recommendation - IMMEDIATE:**
```bash
# Remove backup file
rm .env.backup

# Update .gitignore:
*.backup
.env.backup
```

**Space Savings**: 3.5KB

**Risk Level**: NONE - Backup file

---

### Windows Artifacts

**Files:**
```
nul                           0 bytes
```

**Recommendation - IMMEDIATE:**
```bash
# Remove Windows artifact
rm nul

# Update .gitignore:
nul
Thumbs.db
```

**Risk Level**: NONE - Windows artifact

---

### .coverage File

**File:** `.coverage` (53KB)

**Recommendation - IMMEDIATE:**
```bash
# Remove coverage database
rm .coverage

# Already in .gitignore:
.coverage
```

**Space Savings**: 53KB

**Risk Level**: NONE - Regenerable

---

## Organizational Improvements

### 1. Directory Structure Assessment

**Current Structure:**
```
ai-stock-trading-bot/
├── agents/                    (EMPTY - in .gitignore, but dir exists)
├── backtesting/               OK
├── benchmarks/                OK
├── communication/             REDUNDANT (single file, duplicate)
├── config/                    OK
├── configs/                   OK (different from config/)
├── data/                      OK
├── data_sources/              REDUNDANT? (vs src/data/)
├── deployment/                OK
├── docs/                      OK (well organized)
├── examples/                  OK
├── frontend/                  OK
├── logs/                      OK
├── monitoring/                REDUNDANT (vs src/monitors/)
├── performance/               OK
├── reporting/                 OK
├── reports/                   OK (main reports dir)
├── risk/                      OK
├── scripts/                   OK
├── scripts-and-data/          REDUNDANT (should be removed)
├── src/                       OK (canonical source)
├── systemd/                   OK
├── tests/                     OK
└── utils/                     OK
```

**Issues:**
1. `agents/` directory exists but empty (blocked by .gitignore)
2. `communication/` directory has single file (should be in src/)
3. `data_sources/` vs `src/data/` duplication
4. `monitoring/` vs `src/monitors/` duplication
5. `scripts-and-data/` should be removed

---

### 2. Import Path Consistency

**Current State:**
- Some code uses `from data_sources import X`
- Other code uses `from src.data import X`
- Mix of `from monitoring` and `from src.monitors`

**Recommendation:**
```python
# Standardize on src/ prefix for all new code
from src.agents import base_agent
from src.data.sources import alternative_data_aggregator
from src.monitors import catalyst_monitor

# Legacy directories (data_sources/, monitoring/)
# should be deprecated and removed after migration
```

---

### 3. Root Directory Cleanup

**Current Root Files (37 files):**

**Keep (Essential - 11 files):**
```
CLAUDE.md                     # Session continuity (CRITICAL)
README.md                     # Main docs
CONTRIBUTING.md               # Dev guide
requirements.txt              # Dependencies
main.py                       # Main entry point
web_dashboard.py              # Dashboard server
complete_setup.py             # Setup script
config.yaml                   # Main config
.gitignore                    # Git config
.env                          # Environment (gitignored)
.env.example                  # Example env
```

**Move to docs/ (12 files):**
```
CLEANUP_QUICK_REFERENCE.md → docs/guides/
REPOSITORY_CLEANUP_ANALYSIS.md → docs/archive/
REPORT_CLEANUP_PLAN.md → docs/guides/
DOCUMENTATION_INDEX.md → docs/
QUICKSTART.md → docs/guides/
SETUP_FIX_GUIDE.md → docs/guides/
SYSTEM_OVERVIEW.md → docs/guides/
ANTHROPIC_KEY_SETUP.txt → docs/guides/
```

**Move to scripts/ (2 files):**
```
cleanup_safe_actions.bat → scripts/maintenance/
cleanup_safe_actions.sh → scripts/maintenance/
```

**Move to tests/ or delete (2 files):**
```
Makefile → tests/ or delete if unused
run_tests.sh → tests/ (already exists?)
```

**Move to deployment/ (1 file):**
```
setup_scheduler.ps1 → deployment/windows/
```

**Remove (Generated/Temporary - 9 files):**
```
.coverage                     # Generated
final_research_test.log       # Test artifact
research_generation.log       # Test artifact
research_test.log             # Test artifact
.env.backup                   # Backup file
nul                           # Windows artifact
performance_results.png       # Generated (or move to docs/images/)
```

**After Cleanup: 11 essential files in root**

---

### 4. Documentation Organization

**Current:** 186 markdown files, 261 total files in docs/

**Structure Assessment:**
```
docs/
├── archive/              OK (30+ files)
├── daily-orders/         OK
├── guides/               OK (well organized)
├── index/                OK
├── reports/              REDUNDANT? (vs reports/ in root)
├── session-logs/         OK (but could merge with session-summaries/)
├── session-summaries/    OK
├── sessions/             REDUNDANT (vs session-summaries/)
└── [various .md files]   Should be in subdirectories
```

**Recommendations:**
1. **Merge session-logs/ and session-summaries/** into single `sessions/`
2. **Move docs/reports/** into root `reports/` directory
3. **Organize loose .md files** into appropriate subdirectories
4. **Create docs/archive/2025-09/** for old September docs

---

## .gitignore Recommendations

**Current .gitignore:** Well-structured, but missing some patterns

**Add These Patterns:**
```gitignore
# Backup files (add to existing)
*.backup
.env.backup

# Windows artifacts (add to existing)
nul
Thumbs.db

# Generated images (optional)
performance_results.png
*.png

# Root-level generated files
/*.log

# Test artifacts
fd_test_*.json

# Coverage database (already has htmlcov/, but also add)
.coverage
.coverage.*
coverage.xml

# Empty placeholder (if agents/ dir recreated)
agents/.gitkeep
```

**Verify Existing Patterns Working:**
```bash
# These should NOT be in git
git ls-files | grep -E "(\.pyc$|__pycache__|\.coverage|htmlcov/)"

# If any found, remove:
git rm --cached [files]
```

---

## Prioritized Action Plan

### Phase 1: Immediate Cleanup (5 minutes, ZERO risk)

```bash
# 1. Remove Python cache (112KB)
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 2. Remove HTML coverage (5.1MB)
rm -rf htmlcov/

# 3. Remove root log files (17KB)
rm -f *.log

# 4. Remove coverage database (53KB)
rm -f .coverage

# 5. Remove backup file (3.5KB)
rm -f .env.backup

# 6. Remove Windows artifact
rm -f nul

# Total saved: 5.3MB
# Risk: NONE (all regenerable)
```

### Phase 2: Safe Consolidations (30 minutes, LOW risk)

```bash
# 1. Remove scripts-and-data/ (44KB)
# First verify reports exist elsewhere
ls reports/premarket/2025-10-16/claude_research*.md
# If confirmed:
git rm -r scripts-and-data/

# 2. Remove empty directories (low value)
rmdir archive/ 2>/dev/null
rmdir backtesting/scenarios/ 2>/dev/null
rmdir deployment/aws/ 2>/dev/null
rmdir docs/api/ 2>/dev/null
rmdir docs/architecture/ 2>/dev/null
rmdir docs/strategies/ 2>/dev/null

# 3. Update .gitignore
cat >> .gitignore << 'EOF'

# Additional cleanup patterns
*.backup
.env.backup
nul
Thumbs.db
/*.log
.coverage.*
coverage.xml
EOF

# 4. Commit cleanup
git add .gitignore
git commit -m "chore: cleanup generated files and update gitignore"
```

### Phase 3: Module Consolidation (2-3 hours, MEDIUM risk)

**IMPORTANT: Create backup branch first**
```bash
git checkout -b cleanup/module-consolidation
```

**3.1. Consolidate Alternative Data Aggregator**
```bash
# Compare files
diff data_sources/alternative_data_aggregator.py src/data/sources/alternative_data_aggregator.py

# If identical (exit code 0):
# 1. Update imports (find all references)
grep -r "from data_sources.alternative_data_aggregator" .
grep -r "import data_sources.alternative_data_aggregator" .

# 2. Update each import to:
#    from src.data.sources.alternative_data_aggregator import X

# 3. Test thoroughly
python -m pytest tests/ -v

# 4. Remove old file
git rm data_sources/alternative_data_aggregator.py

# 5. Commit
git commit -m "refactor: consolidate alternative_data_aggregator to src/data/sources/"
```

**3.2. Consolidate Catalyst Monitor**
```bash
# Compare files (5-line diff)
diff monitoring/catalyst_monitor.py src/monitors/catalyst_monitor.py

# Merge differences into src/monitors/catalyst_monitor.py
# Update 2 imports:
grep -r "from monitoring.catalyst_monitor" .

# Test thoroughly
python -m pytest tests/test_catalyst_monitor.py -v

# Remove old file
git rm monitoring/catalyst_monitor.py
rmdir monitoring/ 2>/dev/null

# Commit
git commit -m "refactor: consolidate catalyst_monitor to src/monitors/"
```

**3.3. Consolidate Coordinator**
```bash
# Compare files
diff communication/coordinator.py src/agents/communication/coordinator.py

# If identical, update imports and remove
git rm communication/coordinator.py
rmdir communication/ 2>/dev/null

# Commit
git commit -m "refactor: consolidate coordinator to src/agents/communication/"
```

**3.4. Test Everything**
```bash
# Run full test suite
python -m pytest tests/ -v --cov

# Verify no import errors
python -c "import src.agents.communication.coordinator"
python -c "import src.data.sources.alternative_data_aggregator"
python -c "import src.monitors.catalyst_monitor"

# If all pass, merge to main
git checkout master
git merge cleanup/module-consolidation
```

### Phase 4: Root Directory Organization (1 hour, LOW risk)

```bash
# 1. Create destination directories
mkdir -p docs/guides/
mkdir -p scripts/maintenance/
mkdir -p deployment/windows/

# 2. Move documentation
git mv CLEANUP_QUICK_REFERENCE.md docs/guides/
git mv REPOSITORY_CLEANUP_ANALYSIS.md docs/archive/
git mv REPORT_CLEANUP_PLAN.md docs/guides/
git mv QUICKSTART.md docs/guides/
git mv SETUP_FIX_GUIDE.md docs/guides/
git mv SYSTEM_OVERVIEW.md docs/guides/
git mv ANTHROPIC_KEY_SETUP.txt docs/guides/

# 3. Move scripts
git mv cleanup_safe_actions.bat scripts/maintenance/
git mv cleanup_safe_actions.sh scripts/maintenance/
git mv setup_scheduler.ps1 deployment/windows/

# 4. Move or remove generated files
git mv performance_results.png docs/images/ 2>/dev/null || rm performance_results.png

# 5. Update DOCUMENTATION_INDEX.md with new paths
# (manual edit required)

# 6. Commit
git commit -m "refactor: reorganize root directory (11 essential files)"
```

### Phase 5: Documentation Consolidation (1 hour, LOW risk)

```bash
# 1. Merge session directories
mkdir -p docs/sessions/
git mv docs/session-logs/* docs/sessions/
git mv docs/session-summaries/* docs/sessions/
rmdir docs/session-logs/
rmdir docs/session-summaries/

# 2. Move docs/reports/ to root reports/
git mv docs/reports/* reports/
rmdir docs/reports/

# 3. Archive old September docs
mkdir -p docs/archive/2025-09/
git mv docs/ORDERS_FOR_SEPT_18.md docs/archive/2025-09/
git mv docs/WEEKLY_REPORT_SEPT_15_19_2025.md docs/archive/2025-09/
git mv docs/MONDAY_SUMMARY_SEPT_29.md docs/archive/2025-09/

# 4. Commit
git commit -m "docs: consolidate and organize documentation"
```

### Phase 6: Optional Archive Compression (30 minutes, LOW risk)

```bash
# Compress PDFs in archive (if desired)
cd reports/archive/2025-10/
find . -name "*.pdf" -exec gzip {} \;
cd ../../..

# Commit
git add reports/archive/
git commit -m "chore: compress archived PDFs"
```

---

## Safety Checklist

### Before Deleting Any File

- [ ] **Search for imports**: `grep -r "filename" .`
- [ ] **Check for references**: `grep -r "ClassName" .`
- [ ] **Verify backups exist**: Ensure git history or archive
- [ ] **Run tests first**: `python -m pytest tests/ -v`
- [ ] **Create feature branch**: `git checkout -b cleanup/description`
- [ ] **Commit incrementally**: Small commits, easy to revert

### Before Removing Directories

- [ ] **Verify truly empty**: `ls -la directory/`
- [ ] **Check for hidden files**: `ls -la directory/`
- [ ] **Search for path references**: `grep -r "directory/" .`
- [ ] **Remove from git first**: `git rm -r directory/` before `rmdir`

### After Each Phase

- [ ] **Run full test suite**: `python -m pytest tests/ -v`
- [ ] **Check imports work**: `python -c "import module"`
- [ ] **Verify critical paths**: Test main.py, web_dashboard.py
- [ ] **Review git status**: `git status` should be clean
- [ ] **Push to remote**: `git push origin branch-name`

---

## Risk Assessment Matrix

| Action | Risk Level | Space Savings | Time Required |
|--------|-----------|---------------|---------------|
| Remove __pycache__ | NONE | 112KB | 1 min |
| Remove htmlcov/ | NONE | 5.1MB | 1 min |
| Remove *.log files | NONE | 17KB | 1 min |
| Remove .coverage | NONE | 53KB | 1 min |
| Remove .env.backup | NONE | 3.5KB | 1 min |
| Remove nul | NONE | 0 bytes | 1 min |
| Remove scripts-and-data/ | LOW | 44KB | 5 min |
| Update .gitignore | NONE | 0 bytes | 5 min |
| Consolidate alt_data | MEDIUM | ~30KB | 1 hour |
| Consolidate catalyst | LOW | ~10KB | 30 min |
| Consolidate coordinator | MEDIUM | ~7KB | 30 min |
| Reorganize root | LOW | 0 bytes | 1 hour |
| Consolidate docs | LOW | 0 bytes | 1 hour |
| Compress archive PDFs | LOW | 5-8MB | 30 min |

**Total Potential Savings: 10-13MB**

---

## Monitoring and Validation

### After Cleanup, Verify:

```bash
# 1. Test suite passes
python -m pytest tests/ -v --cov

# 2. No broken imports
python -m py_compile $(find . -name "*.py" ! -path "./docs/*" ! -path "./htmlcov/*")

# 3. Key scripts work
python main.py --help
python web_dashboard.py --help

# 4. Repository size reduced
du -sh .
git gc --aggressive --prune=now
du -sh .git/

# 5. No untracked junk
git status --ignored

# 6. Documentation updated
cat CLAUDE.md | grep "Cleanup"
```

---

## Maintenance Going Forward

### Daily Habits

1. **Run cleanup script** before each session:
   ```bash
   find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
   ```

2. **Check for new log files** in root:
   ```bash
   ls -la *.log 2>/dev/null && echo "WARNING: Log files in root!"
   ```

3. **Monitor repository size**:
   ```bash
   du -sh . && du -sh .git/
   ```

### Weekly Habits

1. **Review new documentation**:
   - Are files in correct directories?
   - Should old docs be archived?

2. **Check for new duplicates**:
   ```bash
   fdupes -r . 2>/dev/null | head -20
   ```

3. **Update .gitignore** if new patterns emerge

### Monthly Habits

1. **Compress old reports** (>30 days):
   ```bash
   find reports/archive/ -name "*.pdf" -mtime +30 -exec gzip {} \;
   ```

2. **Git garbage collection**:
   ```bash
   git gc --aggressive --prune=now
   ```

3. **Review empty directories**:
   ```bash
   find . -type d -empty | grep -v ".git"
   ```

---

## Conclusion

This repository is well-maintained overall, with a clear structure and comprehensive documentation. The main issues are:

1. **Module duplication** from incomplete migration (data_sources/ vs src/data/)
2. **Generated files** not properly gitignored (htmlcov/, __pycache__)
3. **Root directory clutter** (37 files → could be 11)

**Recommended Priority:**
1. **Phase 1** (Immediate): Remove generated files (5 minutes, 5.3MB saved)
2. **Phase 2** (Safe): Update .gitignore, remove scripts-and-data/ (30 minutes)
3. **Phase 3** (Module consolidation): Only if you have time and need consistency (2-3 hours)
4. **Phase 4-6** (Organization): Nice-to-have, improve maintainability (2-3 hours)

**Total Time Investment:** 5 minutes to 6 hours (depending on how deep you go)
**Total Space Savings:** 5.3MB to 13MB

The repository is production-ready. This cleanup is about maintainability and consistency, not functionality.
