#!/bin/bash
# Repository Reorganization Undo Script - Bash Version
# Usage: ./reorganize-undo.sh [--apply]

set -e

MODE="${1:-dry-run}"
LOG_FILE="reorganization_undo_$(date +%Y%m%d_%H%M%S).log"

log_action() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

move_file_back() {
    local dest="$1"
    local src="$2"
    
    if [ -e "$src" ]; then
        if [ "$MODE" == "--apply" ]; then
            mkdir -p "$(dirname "$dest")"
            if [ -e "$dest" ]; then
                log_action "WARNING: Original location exists, skipping: $dest"
            else
                mv "$src" "$dest"
                log_action "Restored: $src -> $dest"
            fi
        else
            echo "Would restore: $src -> $dest"
        fi
    fi
}

move_directory_back() {
    local dest="$1"
    local src="$2"
    
    if [ -d "$src" ]; then
        if [ "$MODE" == "--apply" ]; then
            mkdir -p "$(dirname "$dest")"
            if [ -d "$dest" ]; then
                log_action "Merging back directory: $src -> $dest"
                cp -r "$src"/* "$dest"/ 2>/dev/null || true
                rm -rf "$src"
            else
                mv "$src" "$dest"
                log_action "Restored directory: $src -> $dest"
            fi
        else
            echo "Would restore directory: $src -> $dest"
        fi
    fi
}

undo_reorganization() {
    log_action "Starting repository reorganization undo (Mode: $MODE)"
    
    # Restore main trading script
    move_file_back "main_enhanced.py" "trading-script.py"
    move_file_back "main.py" "_archive/deprecated/main.py"
    
    # Restore trading scripts
    mkdir -p "01_Trading_Scripts"
    for file in scripts-and-data/automation/*.py; do
        if [ -f "$file" ]; then
            original_name=$(basename "$file" | sed 's/-/_/g' | sed 's/\b\(.\)/\u\1/g')
            move_file_back "01_Trading_Scripts/$original_name" "$file"
        fi
    done
    
    # Restore portfolio data
    mkdir -p "02_Portfolio_Data"
    move_directory_back "02_Portfolio_Data/Daily_Snapshots" "scripts-and-data/daily-logs"
    move_directory_back "02_Portfolio_Data/Performance" "performance-tracking/historical"
    move_directory_back "02_Portfolio_Data/Trade_History" "scripts-and-data/trade-history"
    
    # Restore research reports
    mkdir -p "03_Research_Reports"
    move_directory_back "03_Research_Reports/Daily" "research/md/daily"
    move_directory_back "03_Research_Reports/Weekly" "research/md/weekly"
    move_directory_back "03_Research_Reports/Deep_Research" "research/pdf/deep-research"
    move_file_back "03_Research_Reports/automated_research_pipeline.py" "scripts-and-data/automation/automated-research-pipeline.py"
    move_file_back "03_Research_Reports/openai_research_analyzer.py" "agents/openai-research-analyzer.py"
    
    # Restore bot strategies
    mkdir -p "04_Bot_Strategies"
    move_directory_back "04_Bot_Strategies/DEE_BOT" "bot-strategies/dee-bot"
    move_directory_back "04_Bot_Strategies/SHORGAN_BOT" "bot-strategies/shorgan-bot"
    
    # Restore data providers
    mkdir -p "05_Data_Providers"
    move_directory_back "05_Data_Providers/Market_Data" "data-providers/market-data"
    move_directory_back "05_Data_Providers/News" "data-providers/news"
    move_directory_back "05_Data_Providers/Sentiment" "data-providers/sentiment"
    move_file_back "05_Data_Providers/data_providers.py" "data-providers/data-providers.py"
    move_file_back "05_Data_Providers/enhanced_providers.py" "data-providers/enhanced-providers.py"
    move_file_back "05_Data_Providers/catalyst_detector.py" "data-providers/catalyst-detector.py"
    
    # Restore risk management
    mkdir -p "06_Risk_Management"
    move_directory_back "06_Risk_Management/Models" "risk-management/models"
    move_directory_back "06_Risk_Management/Reports" "risk-management/reports"
    move_directory_back "06_Risk_Management/Alerts" "risk-management/alerts"
    
    # Restore documentation
    mkdir -p "07_Documentation"
    move_directory_back "07_Documentation/Guides" "docs/guides"
    move_directory_back "07_Documentation/Session_Notes" "docs/session-notes"
    move_directory_back "07_Documentation/Research_Papers" "docs/experiment-details/research-papers"
    
    # Restore configuration
    mkdir -p "08_Configuration"
    move_file_back "08_Configuration/api_config.py" "config/api-config.py"
    
    # Restore backtesting
    mkdir -p "09_Backtesting"
    move_directory_back "09_Backtesting/Strategies" "_archive/backtesting/strategies"
    move_directory_back "09_Backtesting/Results" "_archive/backtesting/results"
    
    # Restore utils
    mkdir -p "10_Utils"
    move_directory_back "10_Utils/Tests" "tests"
    move_directory_back "10_Utils/Scripts" "scripts-and-data/automation/utils"
    
    # Restore Multi-Agent System
    mkdir -p "Multi-Agent_System/agents"
    for file in agents/*.py; do
        if [ -f "$file" ]; then
            original_name=$(basename "$file" | sed 's/-/_/g')
            move_file_back "Multi-Agent_System/agents/$original_name" "$file"
        fi
    done
    move_directory_back "Multi-Agent_System/communication" "agents/communication"
    
    # Restore Performance Tracking
    mkdir -p "Performance_Tracking"
    move_file_back "Performance_Tracking/daily_performance_tracker.py" "performance-tracking/daily-performance-tracker.py"
    move_file_back "Performance_Tracking/portfolio_tracker.py" "performance-tracking/portfolio-tracker.py"
    move_file_back "Performance_Tracking/automated_performance_tracker.py" "performance-tracking/automated-performance-tracker.py"
    
    # Restore Research Reports
    mkdir -p "Research_Reports"
    move_directory_back "Research_Reports/post_market_daily" "research/md/post-market"
    move_directory_back "Research_Reports/pre_market_daily" "research/md/pre-market"
    move_directory_back "Research_Reports/weekly_analysis" "research/md/weekly"
    
    # Restore Bot_Strategies
    mkdir -p "Bot_Strategies"
    move_directory_back "Bot_Strategies/DEE-BOT" "_archive/deprecated/Bot_Strategies/DEE-BOT"
    move_directory_back "Bot_Strategies/SHORGAN-BOT" "_archive/deprecated/Bot_Strategies/SHORGAN-BOT"
    
    # Restore Core Trading
    mkdir -p "Core_Trading"
    move_file_back "Core_Trading/execute_trades_20250110.py" "scripts-and-data/automation/execute-trades.py"
    move_file_back "Core_Trading/trading_engine.py" "scripts-and-data/automation/trading-engine.py"
    move_directory_back "Core_Trading" "_archive/deprecated/Core_Trading"
    
    # Restore Configuration
    mkdir -p "Configuration"
    move_file_back "Configuration/requirements.txt" "requirements.txt"
    move_file_back "Configuration/sp100_universe.py" "config/sp100-universe.py"
    move_file_back "Configuration/telegram_setup.md" "docs/guides/telegram-setup.md"
    
    # Restore Documentation
    mkdir -p "Documentation"
    move_file_back "Documentation/CLAUDE.md" "docs/guides/claude.md"
    move_file_back "Documentation/CONTINUE_SESSION_GUIDE.md" "docs/guides/continue-session-guide.md"
    move_file_back "Documentation/GITHUB_REPOSITORY_GUIDE.md" "docs/guides/github-repository-guide.md"
    move_file_back "Documentation/SETUP_AUTOMATED_TRADING_GUIDE.md" "docs/guides/setup-automated-trading-guide.md"
    move_file_back "Documentation/SYSTEM_OVERVIEW.md" "docs/experiment-details/system-overview.md"
    
    # Restore archive
    move_directory_back "archive" "_archive/old-archive"
    
    # Restore data and config
    move_directory_back "data" "_archive/deprecated/data"
    move_directory_back "config" "_archive/deprecated/config"
    
    # Restore risk management
    mkdir -p "risk_management"
    move_file_back "risk_management/risk_monitor.py" "risk-management/risk-monitor.py"
    move_file_back "risk_management/portfolio_performance.py" "risk-management/portfolio-performance.py"
    
    # Restore tools
    mkdir -p "tools"
    move_directory_back "tools/idea_generation" "scripts-and-data/automation/idea-generation"
    move_directory_back "tools/reporting" "scripts-and-data/automation/reporting"
    move_directory_back "tools/scheduling" "scripts-and-data/automation/scheduling"
    move_directory_back "tools/testing" "tests/integration"
    
    # Restore frontend
    mkdir -p "frontend"
    move_directory_back "frontend/trading-dashboard" "_archive/frontend/trading-dashboard"
    
    # Restore logs
    move_directory_back "logs" "scripts-and-data/logs"
    
    # Restore trading snapshots to root
    for file in scripts-and-data/trading-snapshots/trading_snapshot_*.json; do
        [ -f "$file" ] && move_file_back "$(basename "$file")" "$file"
    done
    
    # Restore bot-specific logs to root
    for file in scripts-and-data/daily-logs/2025-09-10/dee-bot/DEE_BOT_*.json; do
        [ -f "$file" ] && move_file_back "$(basename "$file")" "$file"
    done
    
    for file in scripts-and-data/daily-logs/2025-09-10/shorgan-bot/SHORGAN_BOT_*.json; do
        [ -f "$file" ] && move_file_back "$(basename "$file")" "$file"
    done
    
    # Restore trading logs to root
    for file in scripts-and-data/daily-logs/2025-09-10/TRADING_LOG_*.json; do
        [ -f "$file" ] && move_file_back "$(basename "$file")" "$file"
    done
    
    # Restore misc files
    move_file_back "performance_history.json" "performance-tracking/performance-history.json"
    move_file_back "trading_bot.db" "data/trading-bot.db"
    
    # Restore PDFs to root
    for file in docs/experiment-details/research-papers/*.pdf; do
        [ -f "$file" ] && move_file_back "$(basename "$file")" "$file"
    done
    
    # Restore test files to root
    for file in tests/test_*.py; do
        [ -f "$file" ] && move_file_back "$(basename "$file")" "$file"
    done
    
    # Restore automation scripts to root
    move_file_back "create_trading_schedule.ps1" "scripts-and-data/automation/create-trading-schedule.ps1"
    move_file_back "run_morning_trades.bat" "scripts-and-data/automation/run-morning-trades.bat"
    move_file_back "setup_github_repo.bat" "scripts-and-data/automation/setup-github-repo.bat"
    move_file_back "generate_tree.ps1" "scripts-and-data/automation/generate-tree.ps1"
    move_file_back "get_telegram_chat_id.py" "scripts-and-data/automation/get-telegram-chat-id.py"
    
    # Restore documentation files
    move_file_back "REPOSITORY_STRUCTURE.md" "docs/repository-structure.md"
    move_file_back "DATA_INTEGRATION_SUMMARY.md" "docs/session-notes/data-integration-summary.md"
    
    # Restore deprecated scripts
    move_file_back "migrate_all_files.py" "_archive/deprecated/migrate_all_files.py"
    move_file_back "move_files.py" "_archive/deprecated/move_files.py"
    move_file_back "REORGANIZE_REPOSITORY.py" "_archive/deprecated/REORGANIZE_REPOSITORY.py"
    
    # Clean up empty directories
    if [ "$MODE" == "--apply" ]; then
        find . -type d -empty -delete 2>/dev/null || true
        log_action "Cleaned up empty directories"
    fi
    
    log_action "Repository reorganization undo complete!"
}

# Main execution
case "$MODE" in
    --apply)
        echo "WARNING: This will undo the repository reorganization!"
        read -p "Are you sure you want to proceed? (yes/no): " confirm
        if [ "$confirm" == "yes" ]; then
            undo_reorganization
        else
            echo "Operation cancelled."
        fi
        ;;
    *)
        echo "DRY RUN MODE - No changes will be made"
        echo "Use --apply to execute undo"
        undo_reorganization
        ;;
esac