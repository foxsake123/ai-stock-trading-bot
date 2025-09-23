"""
Reorganize root directory files into strategy-specific folders
September 18, 2025
"""

import os
import shutil
from pathlib import Path

def create_directories():
    """Create new directory structure"""
    directories = [
        'shorgan-bot/strategies',
        'shorgan-bot/analysis',
        'dee-bot/strategies',
        'dee-bot/analysis',
        'dee-bot/logs',
        'scripts-and-data/utilities',
        'docs/session-logs',
        'docs/daily-orders'
    ]

    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"[SUCCESS] Created: {dir_path}")

def move_files():
    """Move files to their new locations"""

    # Define file movements
    moves = {
        # SHORGAN-BOT files
        'CBRL_EARNINGS_STRATEGY.md': 'shorgan-bot/strategies/',
        'CBRL_EARNINGS_RESULT.md': 'shorgan-bot/strategies/',
        'INCY_FDA_STRATEGY.md': 'shorgan-bot/strategies/',
        'PROFIT_TAKING_ORDERS.md': 'shorgan-bot/strategies/',
        'stop_loss_analysis.py': 'shorgan-bot/analysis/',

        # DEE-BOT files
        'DEE_BOT_ANALYSIS.md': 'dee-bot/strategies/',
        'DEE_BOT_LOGGING_ISSUES.md': 'dee-bot/logs/',
        'check_dee_bot_positions.py': 'dee-bot/analysis/',
        'fix_dee_bot.py': 'dee-bot/analysis/',

        # General utilities
        'check_positions.py': 'scripts-and-data/utilities/',
        'check_earnings.py': 'scripts-and-data/utilities/',
        'show_holdings.py': 'scripts-and-data/utilities/',
        'review_positions.py': 'scripts-and-data/utilities/',
        'generate_premarket_analysis.py': 'scripts-and-data/utilities/',

        # Session logs
        'SESSION_SUMMARY_20250916_FINAL.md': 'docs/session-logs/',
        'SESSION_SUMMARY_20250917.md': 'docs/session-logs/',

        # Daily orders
        'ORDERS_FOR_SEPT_18.md': 'docs/daily-orders/',

        # Other docs
        'PORTFOLIO_LOGGING_STRUCTURE.md': 'docs/',
        'PRODUCT_ROADMAP_UPDATED.md': 'docs/',
    }

    moved_files = []
    failed_files = []

    for source, dest_dir in moves.items():
        if os.path.exists(source):
            dest_path = os.path.join(dest_dir, source)
            try:
                # Use git mv to preserve history
                os.system(f'git mv "{source}" "{dest_path}"')
                moved_files.append(f"{source} -> {dest_path}")
                print(f"[MOVED] {source} -> {dest_path}")
            except Exception as e:
                failed_files.append(f"{source}: {str(e)}")
                print(f"[FAILED] {source}: {str(e)}")
        else:
            print(f"[SKIP] {source} - File not found")

    return moved_files, failed_files

def create_readme():
    """Create a README.md in root"""
    readme_content = """# AI Stock Trading Bot

## Overview
Dual-strategy AI trading system combining catalyst-driven micro-cap trading (SHORGAN-BOT) with beta-neutral defensive strategies (DEE-BOT).

## Quick Start
```bash
python main.py
```

## Project Structure
- `shorgan-bot/` - Catalyst-driven micro-cap trading strategy
- `dee-bot/` - Beta-neutral S&P 100 strategy
- `01_trading_system/` - Core trading engine
- `agents/` - 9-agent consensus system
- `docs/` - Documentation
- `scripts-and-data/` - Utilities and automation

## Current Status
- **Portfolio Value**: ~$207k
- **Active Positions**: 26 (15 SHORGAN + 11 DEE)
- **Automation**: Daily updates at 9:30 AM & 4:00 PM

## Documentation
- [Product Plan](docs/PRODUCT_PLAN.md)
- [Directory Overview](docs/DIRECTORY_OVERVIEW.md)
- [Branch Workflow](docs/BRANCH_WORKFLOW.md)

## License
Private repository - All rights reserved
"""

    with open('README.md', 'w') as f:
        f.write(readme_content)
    print("[SUCCESS] Created README.md")

def main():
    print("="*60)
    print("ROOT DIRECTORY REORGANIZATION")
    print("="*60)

    # Create directories
    print("\n1. Creating new directory structure...")
    create_directories()

    # Move files
    print("\n2. Moving files to new locations...")
    moved, failed = move_files()

    # Create README
    print("\n3. Creating README.md...")
    create_readme()

    # Summary
    print("\n" + "="*60)
    print("REORGANIZATION COMPLETE")
    print(f"Successfully moved: {len(moved)} files")
    if failed:
        print(f"Failed to move: {len(failed)} files")
        for fail in failed:
            print(f"  - {fail}")

    print("\nNext steps:")
    print("1. Review the changes with: git status")
    print("2. Add README.md: git add README.md")
    print("3. Commit: git commit -m 'Reorganize root directory'")
    print("4. Push feature branch: git push origin feature/organize-root-directory")
    print("5. Create PR and merge to master")

if __name__ == "__main__":
    main()