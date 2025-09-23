# AI Trading Bot Repository Reorganization Plan
## Following LuckyOne7777's ChatGPT-Micro-Cap-Experiment Structure

---

## 1. CURRENT STATE SUMMARY

### Statistics
- **Total Directories**: 95+ folders
- **Total Files**: ~500+ files
- **Numbered Folders**: 9 (01_trading_system through 09_logs)
- **Duplicate Structures**: Multiple (dee-bot, shorgan-bot, frontend, docs)
- **Root Clutter**: 30+ files in root directory
- **Naming Conventions**: Mixed (snake_case, camelCase, kebab-case, UPPERCASE)

### Major Issues
1. **Fragmented Bot Logic**: DEE and SHORGAN spread across 4+ locations each
2. **Duplicate Automation**: Scripts in 01_trading_system/automation AND scripts-and-data/automation
3. **Multiple Doc Folders**: docs/, 07_docs/, daily-reports/, weekly-reports/
4. **Inconsistent Naming**: Mixed conventions throughout
5. **Deep Nesting**: Some paths 6+ levels deep (e.g., 01_trading_system/automation/02_data/research/reports/pre_market_daily/)

---

## 2. PROPOSED STRUCTURE

```
ai-stock-trading-bot/
├── main.py                           # Single entrypoint
├── README.md                         # Project documentation
├── .gitignore                        # Git configuration
│
├── agents/                           # All agent logic
│   ├── core/                        # Core agents & engine
│   │   ├── base-agent.py
│   │   ├── trading-engine.py
│   │   └── main-enhanced.py
│   ├── dee-bot/                     # DEE bot consolidated
│   │   ├── strategies/
│   │   ├── analysis/
│   │   └── dee-bot-beta-neutral.py
│   ├── shorgan-bot/                 # SHORGAN bot consolidated
│   │   ├── strategies/
│   │   ├── analysis/
│   │   └── shorgan-catalyst.py
│   ├── communication/               # Agent communication
│   │   ├── message-bus.py
│   │   └── coordinator.py
│   ├── execution/                   # Order execution
│   │   └── complex-order-handler.py
│   └── *.py                         # Individual agent files
│
├── scripts-and-data/                # Scripts and data
│   ├── automation/                  # Automation scripts
│   │   ├── generate-premarket-plan.py
│   │   ├── process-trades.py
│   │   └── *.py
│   ├── scripts/                     # Utility scripts
│   │   ├── setup/                  # Setup scripts
│   │   └── *.bat, *.ps1
│   ├── data/                       # All data files
│   │   ├── positions/              # Portfolio positions
│   │   ├── performance/            # Performance data
│   │   ├── reports/                # Generated reports
│   │   │   ├── daily/
│   │   │   ├── weekly/
│   │   │   └── post-market/
│   │   ├── market/                 # Market data
│   │   ├── portfolio/              # Portfolio data
│   │   └── db/                     # Database files
│   └── utilities/                  # Utility functions
│
├── research/                        # Research & analysis
│   ├── pdf/                        # Academic papers
│   │   └── trading-r1.pdf
│   ├── md/                         # Markdown research
│   ├── chatgpt/                    # ChatGPT reports
│   ├── multi-agent/                # Multi-agent analysis
│   └── reports/                    # Research reports
│       └── pre-market/
│
├── docs/                           # Documentation
│   ├── guides/                     # User guides
│   ├── claude-context.md           # Claude context
│   ├── session-logs/               # Session logs
│   ├── daily-orders/               # Daily order docs
│   └── reports/                    # Doc reports
│
├── configs/                        # Configuration
│   ├── .env                        # Environment vars
│   ├── bots/                       # Bot configs
│   └── claude/                     # Claude settings
│
├── frontend/                       # Frontend apps
│   └── trading-dashboard/
│
├── backtests/                      # Backtesting
│   ├── strategies/
│   └── results/
│
├── risk/                           # Risk management
│   ├── models/
│   └── reports/
│
├── utils/                          # Utilities
│   ├── tests/                     # Test files
│   ├── tools/                     # Helper tools
│   └── extensions/                # Extensions
│       └── chatgpt/               # ChatGPT extension
│
├── logs/                          # All logs
│   ├── trading/                   # Trading logs
│   │   ├── dee/
│   │   └── shorgan/
│   ├── system/                    # System logs
│   ├── snapshots/                 # Snapshots
│   └── automation/                # Automation logs
│
└── _archive/                      # Archived files
    ├── deprecated/                # Deprecated scripts
    ├── duplicates/                # Duplicate files
    ├── legacy/                    # Legacy code
    ├── misc/                      # Miscellaneous
    ├── temp/                      # Temporary files
    └── logs/                      # Old logs
```

---

## 3. KEY IMPROVEMENTS

### Consolidation
- **Agents**: All agent logic in single `agents/` directory
- **Bots**: DEE and SHORGAN each in single location
- **Data**: All data under `scripts-and-data/data/`
- **Logs**: All logs under single `logs/` directory
- **Docs**: Single `docs/` directory for documentation

### Standardization
- **Naming**: All files/folders use kebab-case
- **Structure**: Maximum 4 levels deep
- **Organization**: Clear separation of concerns

### Deduplication
- **Scripts**: Merged duplicate automation scripts
- **Reports**: Consolidated report locations
- **Configs**: Single configs directory

---

## 4. MIGRATION STATISTICS

### Files to Move
- **Core Scripts**: 5 remain in root, 25 to archive
- **Agent Files**: ~50 files to consolidate
- **Automation**: ~80 files to organize
- **Data Files**: ~200 files to restructure
- **Documentation**: ~60 files to consolidate
- **Logs**: ~100 files to reorganize

### Folders to Merge
- **9 numbered folders** → appropriate destinations
- **4 report folders** → scripts-and-data/data/reports/
- **3 frontend folders** → frontend/
- **Multiple bot folders** → agents/dee-bot/ and agents/shorgan-bot/

### Archive Destinations
- **deprecated/**: Old reorganization scripts, dated execution files
- **duplicates/**: Files with same SHA-256 hash
- **legacy/**: Old numbered folder structure
- **misc/**: Images, corrupted files, temporary files
- **temp/**: Cache directories, build artifacts

---

## 5. EXECUTION PLAN

### Phase 1: Preparation
1. Create all destination directories
2. Generate SHA-256 hashes for deduplication
3. Create reorg.log for tracking

### Phase 2: Core Moves
1. Move agent files to agents/
2. Consolidate bot directories
3. Organize automation scripts

### Phase 3: Data Organization
1. Merge all data files to scripts-and-data/data/
2. Consolidate logs to logs/
3. Organize reports by type

### Phase 4: Cleanup
1. Archive deprecated files
2. Remove empty directories
3. Update import paths in Python files

### Phase 5: Validation
1. Verify all files moved correctly
2. Check for broken imports
3. Test main.py execution

---

## 6. ROLLBACK PLAN

### Undo Mechanism
- All moves logged in reorg.log
- Undo script reverses operations in reverse order
- Original structure preserved in _archive/legacy_structure/

### Safety Features
- Dry-run mode for preview
- No deletions, only moves
- SHA-256 verification for duplicates
- Timestamped backup of mapping

---

## NEXT STEPS

1. Review this plan and mapping.csv
2. Run dry-run to preview changes
3. Execute reorganization with --apply flag
4. Test system functionality
5. Commit changes to git

---

*Generated: September 23, 2025*
*Target Structure: LuckyOne7777's ChatGPT-Micro-Cap-Experiment*
*Methodology: TradingAgents + Trading-R1 aligned*