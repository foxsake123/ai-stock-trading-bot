# Report Directory Cleanup Plan
## Generated: October 23, 2025

## Current State Analysis

### Directory Structure Issues Found

**1. Duplicated/Redundant Files in `reports/premarket/`**
- `latest.md` (loose file - should be in latest/)
- `premarket_report_2025-10-14.md` (old format)
- `premarket_report_2025-10-15.md` (old format, 47KB)
- `chatgpt_premarket_report_2025-10-15.md` (old format)
- `premarket_metadata_2025-10-14.json` (old format)

**2. Empty Directories** (no files, take up space)
- `reports/daily/` (empty)
- `reports/weekly/` (empty)
- `reports/monthly/` (empty)
- `reports/execution/` (empty)
- `reports/performance/` (empty)
- `reports/postmarket/` (empty - but docs/reports/post-market has content)

**3. Archive Issues**
- `reports/archive/` is 20MB (good archiving)
- Some duplicates between `reports/archive/2025-10/` subdirs and root level

**4. Scattered Report Locations**
- `data/daily/reports/` (execution logs)
- `docs/reports/post-market/` (post-market reports)
- `docs/reports/premarket/` (12KB - unclear purpose)
- `reports/premarket/` (current active)

## Recommended Actions

### Phase 1: Archive Old Format Reports
Move to `reports/archive/2025-10/old-format/`:
- `premarket_report_2025-10-14.md`
- `premarket_report_2025-10-15.md`
- `chatgpt_premarket_report_2025-10-15.md`
- `premarket_metadata_2025-10-14.json`
- `latest.md` (if different from latest/latest.md)

### Phase 2: Remove Empty Directories
Delete entirely (0 files):
- `reports/daily/`
- `reports/weekly/`
- `reports/monthly/`
- `reports/execution/`
- `reports/performance/`
- `reports/postmarket/`

### Phase 3: Consolidate Archive Duplicates
Review `reports/archive/2025-10/` for:
- Files in both date subdirs AND root level
- Move all to appropriate date subdirs
- Clean root level of dated files

### Phase 4: Organize Current Structure

**Keep Active** (current date-based system):
```
reports/premarket/YYYY-MM-DD/
├── claude_research_dee_bot_YYYY-MM-DD.md
├── claude_research_dee_bot_YYYY-MM-DD.pdf
├── claude_research_shorgan_bot_YYYY-MM-DD.md
├── claude_research_shorgan_bot_YYYY-MM-DD.pdf
└── claude_research.md (combined)
```

**Keep Latest Symlink/Copy**:
```
reports/premarket/latest/
├── claude_research.md
├── consensus.md
├── trades.md
├── chatgpt_research.md
```

### Phase 5: Document Clean Structure

Create `reports/STRUCTURE.md`:
- Explain date-based organization
- Archive policy (move to archive/ after 30 days)
- Latest/ always points to most recent
- No loose files in premarket/ root

## Expected Results

**Before**:
- 96 report files
- 20MB archive + 549KB active
- 6 empty directories
- Confusing file mix

**After**:
- ~70-80 report files (archived/removed old)
- Clean date-based structure
- 0 empty directories
- Clear documentation

## Execution Steps

1. Create archive subdirectory for old format
2. Move old format files to archive
3. Remove empty directories
4. Clean archive duplicates
5. Update README.md with clean structure
6. Commit changes

## Safety

- All moves go to archive/ (not deletion)
- Only empty dirs deleted
- Can revert via git if needed
