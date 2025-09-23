#!/bin/bash
# Repository Reorganization Script - Bash Version
# Usage: ./reorganize-repo.sh [--apply|--undo]

set -e

MODE="${1:-dry-run}"
LOG_FILE="reorganization_$(date +%Y%m%d_%H%M%S).log"

log_action() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

create_directories() {
    local dirs=(
        "scripts-and-data/automation"
        "scripts-and-data/daily-logs/2025-09-10/dee-bot"
        "scripts-and-data/daily-logs/2025-09-10/shorgan-bot"
        "scripts-and-data/trading-snapshots"
        "scripts-and-data/trade-history"
        "scripts-and-data/logs"
        "docs/experiment-details/research-papers"
        "docs/guides"
        "docs/session-notes"
        "research/md/daily"
        "research/md/weekly"
        "research/md/post-market"
        "research/md/pre-market"
        "research/md/historical"
        "research/pdf/deep-research"
        "research/pdf/2025/week-37"
        "agents/communication"
        "bot-strategies/dee-bot"
        "bot-strategies/shorgan-bot"
        "data-providers/market-data"
        "data-providers/news"
        "data-providers/sentiment"
        "risk-management/models"
        "risk-management/reports"
        "risk-management/alerts"
        "performance-tracking/historical"
        "config"
        "tests/integration"
        "data"
        "_archive/deprecated/01_Trading_Scripts"
        "_archive/deprecated/Bot_Strategies"
        "_archive/deprecated/Core_Trading"
        "_archive/deprecated/config"
        "_archive/deprecated/data"
        "_archive/backtesting/strategies"
        "_archive/backtesting/results"
        "_archive/frontend"
        "_archive/old-archive"
    )
    
    for dir in "${dirs[@]}"; do
        if [ "$MODE" == "--apply" ]; then
            mkdir -p "$dir"
            log_action "Created directory: $dir"
        else
            echo "Would create: $dir"
        fi
    done
}

move_file_safe() {
    local src="$1"
    local dest="$2"
    
    if [ -e "$src" ]; then
        if [ "$MODE" == "--apply" ]; then
            # Create destination directory if it doesn't exist
            mkdir -p "$(dirname "$dest")"
            
            # Check if destination exists
            if [ -e "$dest" ]; then
                log_action "WARNING: Destination exists, skipping: $dest"
            else
                mv "$src" "$dest"
                log_action "Moved: $src -> $dest"
            fi
        else
            echo "Would move: $src -> $dest"
        fi
    else
        [ "$MODE" == "--apply" ] && log_action "Source not found, skipping: $src"
    fi
}

move_directory_safe() {
    local src="$1"
    local dest="$2"
    
    if [ -d "$src" ]; then
        if [ "$MODE" == "--apply" ]; then
            mkdir -p "$(dirname "$dest")"
            if [ -d "$dest" ]; then
                log_action "Merging directory: $src -> $dest"
                cp -r "$src"/* "$dest"/ 2>/dev/null || true
                rm -rf "$src"
            else
                mv "$src" "$dest"
                log_action "Moved directory: $src -> $dest"
            fi
        else
            echo "Would move directory: $src -> $dest"
        fi
    fi
}

reorganize_repository() {
    log_action "Starting repository reorganization (Mode: $MODE)"
    
    # Create new directory structure
    create_directories
    
    # Move main trading script
    move_file_safe "main_enhanced.py" "trading-script.py"
    move_file_safe "main.py" "_archive/deprecated/main.py"
    
    # Move trading scripts
    for file in 01_Trading_Scripts/*.py; do
        [ -f "$file" ] && move_file_safe "$file" "scripts-and-data/automation/$(basename "$file" | tr '_' '-' | tr '[:upper:]' '[:lower:]')"
    done
    
    # Move portfolio data
    move_directory_safe "02_Portfolio_Data/Daily_Snapshots" "scripts-and-data/daily-logs"
    move_directory_safe "02_Portfolio_Data/Performance" "performance-tracking/historical"
    move_directory_safe "02_Portfolio_Data/Trade_History" "scripts-and-data/trade-history"
    
    # Move research reports
    move_directory_safe "03_Research_Reports/Daily" "research/md/daily"
    move_directory_safe "03_Research_Reports/Weekly" "research/md/weekly"
    move_directory_safe "03_Research_Reports/Deep_Research" "research/pdf/deep-research"
    move_file_safe "03_Research_Reports/automated_research_pipeline.py" "scripts-and-data/automation/automated-research-pipeline.py"
    move_file_safe "03_Research_Reports/openai_research_analyzer.py" "agents/openai-research-analyzer.py"
    
    # Move bot strategies
    move_directory_safe "04_Bot_Strategies/DEE_BOT" "bot-strategies/dee-bot"
    move_directory_safe "04_Bot_Strategies/SHORGAN_BOT" "bot-strategies/shorgan-bot"
    move_directory_safe "04_Bot_Strategies/Common/daily_trades" "scripts-and-data/daily-logs"
    
    # Move data providers
    move_directory_safe "05_Data_Providers/Market_Data" "data-providers/market-data"
    move_directory_safe "05_Data_Providers/News" "data-providers/news"
    move_directory_safe "05_Data_Providers/Sentiment" "data-providers/sentiment"
    move_file_safe "05_Data_Providers/data_providers.py" "data-providers/data-providers.py"
    move_file_safe "05_Data_Providers/enhanced_providers.py" "data-providers/enhanced-providers.py"
    move_file_safe "05_Data_Providers/catalyst_detector.py" "data-providers/catalyst-detector.py"
    
    # Move risk management
    move_directory_safe "06_Risk_Management/Models" "risk-management/models"
    move_directory_safe "06_Risk_Management/Reports" "risk-management/reports"
    move_directory_safe "06_Risk_Management/Alerts" "risk-management/alerts"
    
    # Move documentation
    move_directory_safe "07_Documentation/Guides" "docs/guides"
    move_directory_safe "07_Documentation/Session_Notes" "docs/session-notes"
    move_directory_safe "07_Documentation/Research_Papers" "docs/experiment-details/research-papers"
    
    # Move configuration
    move_file_safe "08_Configuration/api_config.py" "config/api-config.py"
    
    # Move utils and tests
    move_directory_safe "10_Utils/Tests" "tests"
    move_directory_safe "10_Utils/Scripts" "scripts-and-data/automation/utils"
    
    # Move Multi-Agent System
    for file in Multi-Agent_System/agents/*.py; do
        [ -f "$file" ] && move_file_safe "$file" "agents/$(basename "$file" | tr '_' '-')"
    done
    move_directory_safe "Multi-Agent_System/communication" "agents/communication"
    
    # Move Performance Tracking
    move_file_safe "Performance_Tracking/daily_performance_tracker.py" "performance-tracking/daily-performance-tracker.py"
    move_file_safe "Performance_Tracking/portfolio_tracker.py" "performance-tracking/portfolio-tracker.py"
    move_file_safe "Performance_Tracking/automated_performance_tracker.py" "performance-tracking/automated-performance-tracker.py"
    
    # Move Research Reports
    move_directory_safe "Research_Reports/post_market_daily" "research/md/post-market"
    move_directory_safe "Research_Reports/pre_market_daily" "research/md/pre-market"
    move_directory_safe "Research_Reports/weekly_analysis" "research/md/weekly"
    
    # Move duplicate Bot_Strategies
    move_directory_safe "Bot_Strategies/DEE-BOT" "_archive/deprecated/Bot_Strategies/DEE-BOT"
    move_directory_safe "Bot_Strategies/SHORGAN-BOT" "_archive/deprecated/Bot_Strategies/SHORGAN-BOT"
    
    # Move Core Trading
    move_file_safe "Core_Trading/execute_trades_20250110.py" "scripts-and-data/automation/execute-trades.py"
    move_file_safe "Core_Trading/trading_engine.py" "scripts-and-data/automation/trading-engine.py"
    move_directory_safe "Core_Trading" "_archive/deprecated/Core_Trading"
    
    # Move Configuration
    move_file_safe "Configuration/requirements.txt" "requirements.txt"
    move_file_safe "Configuration/sp100_universe.py" "config/sp100-universe.py"
    move_file_safe "Configuration/telegram_setup.md" "docs/guides/telegram-setup.md"
    
    # Move Documentation
    move_file_safe "Documentation/CLAUDE.md" "docs/guides/claude.md"
    move_file_safe "Documentation/CONTINUE_SESSION_GUIDE.md" "docs/guides/continue-session-guide.md"
    move_file_safe "Documentation/GITHUB_REPOSITORY_GUIDE.md" "docs/guides/github-repository-guide.md"
    move_file_safe "Documentation/SETUP_AUTOMATED_TRADING_GUIDE.md" "docs/guides/setup-automated-trading-guide.md"
    move_file_safe "Documentation/SYSTEM_OVERVIEW.md" "docs/experiment-details/system-overview.md"
    
    # Archive duplicates
    move_directory_safe "archive" "_archive/old-archive"
    move_directory_safe "data" "_archive/deprecated/data"
    move_directory_safe "config" "_archive/deprecated/config"
    
    # Move risk management files
    move_file_safe "risk_management/risk_monitor.py" "risk-management/risk-monitor.py"
    move_file_safe "risk_management/portfolio_performance.py" "risk-management/portfolio-performance.py"
    
    # Move tools
    move_directory_safe "tools/idea_generation" "scripts-and-data/automation/idea-generation"
    move_directory_safe "tools/reporting" "scripts-and-data/automation/reporting"
    move_directory_safe "tools/scheduling" "scripts-and-data/automation/scheduling"
    move_directory_safe "tools/testing" "tests/integration"
    
    # Move frontend
    move_directory_safe "frontend/trading-dashboard" "_archive/frontend/trading-dashboard"
    
    # Move logs
    move_directory_safe "logs" "scripts-and-data/logs"
    
    # Move trading snapshots
    for file in trading_snapshot_20250910_*.json; do
        [ -f "$file" ] && move_file_safe "$file" "scripts-and-data/trading-snapshots/$(basename "$file")"
    done
    
    # Move bot-specific logs
    for file in DEE_BOT_*.json; do
        [ -f "$file" ] && move_file_safe "$file" "scripts-and-data/daily-logs/2025-09-10/dee-bot/$(basename "$file")"
    done
    
    for file in SHORGAN_BOT_*.json; do
        [ -f "$file" ] && move_file_safe "$file" "scripts-and-data/daily-logs/2025-09-10/shorgan-bot/$(basename "$file")"
    done
    
    # Move trading logs
    for file in TRADING_LOG_*.json; do
        [ -f "$file" ] && move_file_safe "$file" "scripts-and-data/daily-logs/2025-09-10/$(basename "$file")"
    done
    
    # Move misc files
    move_file_safe "performance_history.json" "performance-tracking/performance-history.json"
    move_file_safe "trading_bot.db" "data/trading-bot.db"
    
    # Move PDFs to documentation
    for file in *.pdf; do
        [ -f "$file" ] && move_file_safe "$file" "docs/experiment-details/research-papers/$(basename "$file")"
    done
    
    # Move test files from root
    for file in test_*.py; do
        [ -f "$file" ] && move_file_safe "$file" "tests/$(basename "$file")"
    done
    
    # Move automation scripts
    move_file_safe "create_trading_schedule.ps1" "scripts-and-data/automation/create-trading-schedule.ps1"
    move_file_safe "run_morning_trades.bat" "scripts-and-data/automation/run-morning-trades.bat"
    move_file_safe "setup_github_repo.bat" "scripts-and-data/automation/setup-github-repo.bat"
    move_file_safe "generate_tree.ps1" "scripts-and-data/automation/generate-tree.ps1"
    move_file_safe "get_telegram_chat_id.py" "scripts-and-data/automation/get-telegram-chat-id.py"
    
    # Move documentation files
    move_file_safe "REPOSITORY_STRUCTURE.md" "docs/repository-structure.md"
    move_file_safe "DATA_INTEGRATION_SUMMARY.md" "docs/session-notes/data-integration-summary.md"
    
    # Archive deprecated scripts
    move_file_safe "migrate_all_files.py" "_archive/deprecated/migrate_all_files.py"
    move_file_safe "move_files.py" "_archive/deprecated/move_files.py"
    move_file_safe "REORGANIZE_REPOSITORY.py" "_archive/deprecated/REORGANIZE_REPOSITORY.py"
    
    # Clean up empty directories
    if [ "$MODE" == "--apply" ]; then
        find . -type d -empty -delete 2>/dev/null || true
        log_action "Cleaned up empty directories"
    fi
    
    log_action "Repository reorganization complete!"
}

# Main execution
case "$MODE" in
    --apply)
        echo "WARNING: This will reorganize your entire repository structure!"
        read -p "Are you sure you want to proceed? (yes/no): " confirm
        if [ "$confirm" == "yes" ]; then
            reorganize_repository
        else
            echo "Operation cancelled."
        fi
        ;;
    --undo)
        echo "Undo functionality will be implemented in the undo script."
        echo "Please use reorganize-undo.sh for rollback."
        ;;
    *)
        echo "DRY RUN MODE - No changes will be made"
        echo "Use --apply to execute changes"
        echo "Use --undo to rollback changes"
        reorganize_repository
        ;;
esac