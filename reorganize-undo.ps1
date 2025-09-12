# Repository Reorganization Undo Script - PowerShell Version
# Usage: .\reorganize-undo.ps1 [-Apply]

param(
    [switch]$Apply
)

$LogFile = "reorganization_undo_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-Log {
    param($Message)
    $LogEntry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Move-FileBack {
    param(
        [string]$Destination,
        [string]$Source
    )
    
    if (Test-Path $Source) {
        if ($Apply) {
            $destDir = Split-Path -Parent $Destination
            if (!(Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            
            if (Test-Path $Destination) {
                Write-Log "WARNING: Original location exists, skipping: $Destination"
            } else {
                Move-Item -Path $Source -Destination $Destination -Force
                Write-Log "Restored: $Source -> $Destination"
            }
        } else {
            Write-Host "Would restore: $Source -> $Destination" -ForegroundColor Cyan
        }
    }
}

function Move-DirectoryBack {
    param(
        [string]$Destination,
        [string]$Source
    )
    
    if (Test-Path $Source -PathType Container) {
        if ($Apply) {
            $destDir = Split-Path -Parent $Destination
            if (!(Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            
            if (Test-Path $Destination -PathType Container) {
                Write-Log "Merging back directory: $Source -> $Destination"
                Get-ChildItem -Path $Source -Recurse | ForEach-Object {
                    $targetPath = Join-Path $Destination $_.FullName.Substring($Source.Length)
                    if ($_.PSIsContainer) {
                        New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
                    } else {
                        Move-Item -Path $_.FullName -Destination $targetPath -Force
                    }
                }
                Remove-Item -Path $Source -Recurse -Force
            } else {
                Move-Item -Path $Source -Destination $Destination -Force
                Write-Log "Restored directory: $Source -> $Destination"
            }
        } else {
            Write-Host "Would restore directory: $Source -> $Destination" -ForegroundColor Cyan
        }
    }
}

function Undo-Reorganization {
    Write-Log "Starting repository reorganization undo (Apply: $Apply)"
    
    # Restore main trading script
    Move-FileBack "main_enhanced.py" "trading-script.py"
    Move-FileBack "main.py" "_archive\deprecated\main.py"
    
    # Restore trading scripts
    New-Item -ItemType Directory -Path "01_Trading_Scripts" -Force -ErrorAction SilentlyContinue | Out-Null
    Get-ChildItem "scripts-and-data\automation\*.py" -ErrorAction SilentlyContinue | ForEach-Object {
        $originalName = ($_.Name -replace '-', '_')
        Move-FileBack "01_Trading_Scripts\$originalName" $_.FullName
    }
    
    # Restore portfolio data
    New-Item -ItemType Directory -Path "02_Portfolio_Data" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-DirectoryBack "02_Portfolio_Data\Daily_Snapshots" "scripts-and-data\daily-logs"
    Move-DirectoryBack "02_Portfolio_Data\Performance" "performance-tracking\historical"
    Move-DirectoryBack "02_Portfolio_Data\Trade_History" "scripts-and-data\trade-history"
    
    # Restore research reports
    New-Item -ItemType Directory -Path "03_Research_Reports" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-DirectoryBack "03_Research_Reports\Daily" "research\md\daily"
    Move-DirectoryBack "03_Research_Reports\Weekly" "research\md\weekly"
    Move-DirectoryBack "03_Research_Reports\Deep_Research" "research\pdf\deep-research"
    Move-FileBack "03_Research_Reports\automated_research_pipeline.py" "scripts-and-data\automation\automated-research-pipeline.py"
    Move-FileBack "03_Research_Reports\openai_research_analyzer.py" "agents\openai-research-analyzer.py"
    
    # Restore bot strategies
    New-Item -ItemType Directory -Path "04_Bot_Strategies" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-DirectoryBack "04_Bot_Strategies\DEE_BOT" "bot-strategies\dee-bot"
    Move-DirectoryBack "04_Bot_Strategies\SHORGAN_BOT" "bot-strategies\shorgan-bot"
    
    # Restore data providers
    New-Item -ItemType Directory -Path "05_Data_Providers" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-DirectoryBack "05_Data_Providers\Market_Data" "data-providers\market-data"
    Move-DirectoryBack "05_Data_Providers\News" "data-providers\news"
    Move-DirectoryBack "05_Data_Providers\Sentiment" "data-providers\sentiment"
    Move-FileBack "05_Data_Providers\data_providers.py" "data-providers\data-providers.py"
    Move-FileBack "05_Data_Providers\enhanced_providers.py" "data-providers\enhanced-providers.py"
    Move-FileBack "05_Data_Providers\catalyst_detector.py" "data-providers\catalyst-detector.py"
    
    # Restore risk management
    New-Item -ItemType Directory -Path "06_Risk_Management" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-DirectoryBack "06_Risk_Management\Models" "risk-management\models"
    Move-DirectoryBack "06_Risk_Management\Reports" "risk-management\reports"
    Move-DirectoryBack "06_Risk_Management\Alerts" "risk-management\alerts"
    
    # Restore documentation
    New-Item -ItemType Directory -Path "07_Documentation" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-DirectoryBack "07_Documentation\Guides" "docs\guides"
    Move-DirectoryBack "07_Documentation\Session_Notes" "docs\session-notes"
    Move-DirectoryBack "07_Documentation\Research_Papers" "docs\experiment-details\research-papers"
    
    # Restore configuration
    New-Item -ItemType Directory -Path "08_Configuration" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-FileBack "08_Configuration\api_config.py" "config\api-config.py"
    
    # Restore backtesting
    New-Item -ItemType Directory -Path "09_Backtesting" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-DirectoryBack "09_Backtesting\Strategies" "_archive\backtesting\strategies"
    Move-DirectoryBack "09_Backtesting\Results" "_archive\backtesting\results"
    
    # Restore utils
    New-Item -ItemType Directory -Path "10_Utils" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-DirectoryBack "10_Utils\Tests" "tests"
    Move-DirectoryBack "10_Utils\Scripts" "scripts-and-data\automation\utils"
    
    # Restore Multi-Agent System
    New-Item -ItemType Directory -Path "Multi-Agent_System\agents" -Force -ErrorAction SilentlyContinue | Out-Null
    Get-ChildItem "agents\*.py" -ErrorAction SilentlyContinue | ForEach-Object {
        $originalName = $_.Name -replace '-', '_'
        Move-FileBack "Multi-Agent_System\agents\$originalName" $_.FullName
    }
    Move-DirectoryBack "Multi-Agent_System\communication" "agents\communication"
    
    # Restore Performance Tracking
    New-Item -ItemType Directory -Path "Performance_Tracking" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-FileBack "Performance_Tracking\daily_performance_tracker.py" "performance-tracking\daily-performance-tracker.py"
    Move-FileBack "Performance_Tracking\portfolio_tracker.py" "performance-tracking\portfolio-tracker.py"
    Move-FileBack "Performance_Tracking\automated_performance_tracker.py" "performance-tracking\automated-performance-tracker.py"
    
    # Restore Research Reports
    New-Item -ItemType Directory -Path "Research_Reports" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-DirectoryBack "Research_Reports\post_market_daily" "research\md\post-market"
    Move-DirectoryBack "Research_Reports\pre_market_daily" "research\md\pre-market"
    Move-DirectoryBack "Research_Reports\weekly_analysis" "research\md\weekly"
    
    # Restore Bot_Strategies
    New-Item -ItemType Directory -Path "Bot_Strategies" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-DirectoryBack "Bot_Strategies\DEE-BOT" "_archive\deprecated\Bot_Strategies\DEE-BOT"
    Move-DirectoryBack "Bot_Strategies\SHORGAN-BOT" "_archive\deprecated\Bot_Strategies\SHORGAN-BOT"
    
    # Restore Core Trading
    New-Item -ItemType Directory -Path "Core_Trading" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-FileBack "Core_Trading\execute_trades_20250110.py" "scripts-and-data\automation\execute-trades.py"
    Move-FileBack "Core_Trading\trading_engine.py" "scripts-and-data\automation\trading-engine.py"
    Move-DirectoryBack "Core_Trading" "_archive\deprecated\Core_Trading"
    
    # Restore Configuration
    New-Item -ItemType Directory -Path "Configuration" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-FileBack "Configuration\requirements.txt" "requirements.txt"
    Move-FileBack "Configuration\sp100_universe.py" "config\sp100-universe.py"
    Move-FileBack "Configuration\telegram_setup.md" "docs\guides\telegram-setup.md"
    
    # Restore Documentation
    New-Item -ItemType Directory -Path "Documentation" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-FileBack "Documentation\CLAUDE.md" "docs\guides\claude.md"
    Move-FileBack "Documentation\CONTINUE_SESSION_GUIDE.md" "docs\guides\continue-session-guide.md"
    Move-FileBack "Documentation\GITHUB_REPOSITORY_GUIDE.md" "docs\guides\github-repository-guide.md"
    Move-FileBack "Documentation\SETUP_AUTOMATED_TRADING_GUIDE.md" "docs\guides\setup-automated-trading-guide.md"
    Move-FileBack "Documentation\SYSTEM_OVERVIEW.md" "docs\experiment-details\system-overview.md"
    
    # Restore archive
    Move-DirectoryBack "archive" "_archive\old-archive"
    
    # Restore data and config
    Move-DirectoryBack "data" "_archive\deprecated\data"
    Move-DirectoryBack "config" "_archive\deprecated\config"
    
    # Restore risk management
    New-Item -ItemType Directory -Path "risk_management" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-FileBack "risk_management\risk_monitor.py" "risk-management\risk-monitor.py"
    Move-FileBack "risk_management\portfolio_performance.py" "risk-management\portfolio-performance.py"
    
    # Restore tools
    New-Item -ItemType Directory -Path "tools" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-DirectoryBack "tools\idea_generation" "scripts-and-data\automation\idea-generation"
    Move-DirectoryBack "tools\reporting" "scripts-and-data\automation\reporting"
    Move-DirectoryBack "tools\scheduling" "scripts-and-data\automation\scheduling"
    Move-DirectoryBack "tools\testing" "tests\integration"
    
    # Restore frontend
    New-Item -ItemType Directory -Path "frontend" -Force -ErrorAction SilentlyContinue | Out-Null
    Move-DirectoryBack "frontend\trading-dashboard" "_archive\frontend\trading-dashboard"
    
    # Restore logs
    Move-DirectoryBack "logs" "scripts-and-data\logs"
    
    # Restore trading snapshots to root
    Get-ChildItem "scripts-and-data\trading-snapshots\trading_snapshot_*.json" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileBack $_.Name $_.FullName
    }
    
    # Restore bot-specific logs to root
    Get-ChildItem "scripts-and-data\daily-logs\2025-09-10\dee-bot\DEE_BOT_*.json" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileBack $_.Name $_.FullName
    }
    
    Get-ChildItem "scripts-and-data\daily-logs\2025-09-10\shorgan-bot\SHORGAN_BOT_*.json" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileBack $_.Name $_.FullName
    }
    
    # Restore trading logs to root
    Get-ChildItem "scripts-and-data\daily-logs\2025-09-10\TRADING_LOG_*.json" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileBack $_.Name $_.FullName
    }
    
    # Restore misc files
    Move-FileBack "performance_history.json" "performance-tracking\performance-history.json"
    Move-FileBack "trading_bot.db" "data\trading-bot.db"
    
    # Restore PDFs to root
    Get-ChildItem "docs\experiment-details\research-papers\*.pdf" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileBack $_.Name $_.FullName
    }
    
    # Restore test files to root
    Get-ChildItem "tests\test_*.py" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileBack $_.Name $_.FullName
    }
    
    # Restore automation scripts to root
    Move-FileBack "create_trading_schedule.ps1" "scripts-and-data\automation\create-trading-schedule.ps1"
    Move-FileBack "run_morning_trades.bat" "scripts-and-data\automation\run-morning-trades.bat"
    Move-FileBack "setup_github_repo.bat" "scripts-and-data\automation\setup-github-repo.bat"
    Move-FileBack "generate_tree.ps1" "scripts-and-data\automation\generate-tree.ps1"
    Move-FileBack "get_telegram_chat_id.py" "scripts-and-data\automation\get-telegram-chat-id.py"
    
    # Restore documentation files
    Move-FileBack "REPOSITORY_STRUCTURE.md" "docs\repository-structure.md"
    Move-FileBack "DATA_INTEGRATION_SUMMARY.md" "docs\session-notes\data-integration-summary.md"
    
    # Restore deprecated scripts
    Move-FileBack "migrate_all_files.py" "_archive\deprecated\migrate_all_files.py"
    Move-FileBack "move_files.py" "_archive\deprecated\move_files.py"
    Move-FileBack "REORGANIZE_REPOSITORY.py" "_archive\deprecated\REORGANIZE_REPOSITORY.py"
    
    # Clean up empty directories
    if ($Apply) {
        Get-ChildItem -Path . -Recurse -Directory | 
            Where-Object { (Get-ChildItem $_.FullName).Count -eq 0 } | 
            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Write-Log "Cleaned up empty directories"
    }
    
    Write-Log "Repository reorganization undo complete!"
}

# Main execution
if ($Apply) {
    Write-Host "WARNING: This will undo the repository reorganization!" -ForegroundColor Red
    $confirm = Read-Host "Are you sure you want to proceed? (yes/no)"
    if ($confirm -eq "yes") {
        Undo-Reorganization
    } else {
        Write-Host "Operation cancelled." -ForegroundColor Yellow
    }
} else {
    Write-Host "DRY RUN MODE - No changes will be made" -ForegroundColor Green
    Write-Host "Use -Apply to execute undo" -ForegroundColor Yellow
    Undo-Reorganization
}