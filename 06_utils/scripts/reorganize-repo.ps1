# Repository Reorganization Script - PowerShell Version
# Usage: .\reorganize-repo.ps1 [-Apply] [-Undo]

param(
    [switch]$Apply,
    [switch]$Undo
)

$LogFile = "reorganization_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-Log {
    param($Message)
    $LogEntry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Create-Directories {
    $directories = @(
        "scripts-and-data\automation",
        "scripts-and-data\daily-logs\2025-09-10\dee-bot",
        "scripts-and-data\daily-logs\2025-09-10\shorgan-bot",
        "scripts-and-data\trading-snapshots",
        "scripts-and-data\trade-history",
        "scripts-and-data\logs",
        "docs\experiment-details\research-papers",
        "docs\guides",
        "docs\session-notes",
        "research\md\daily",
        "research\md\weekly",
        "research\md\post-market",
        "research\md\pre-market",
        "research\md\historical",
        "research\pdf\deep-research",
        "research\pdf\2025\week-37",
        "agents\communication",
        "bot-strategies\dee-bot",
        "bot-strategies\shorgan-bot",
        "data-providers\market-data",
        "data-providers\news",
        "data-providers\sentiment",
        "risk-management\models",
        "risk-management\reports",
        "risk-management\alerts",
        "performance-tracking\historical",
        "config",
        "tests\integration",
        "data",
        "_archive\deprecated\01_Trading_Scripts",
        "_archive\deprecated\Bot_Strategies",
        "_archive\deprecated\Core_Trading",
        "_archive\deprecated\config",
        "_archive\deprecated\data",
        "_archive\backtesting\strategies",
        "_archive\backtesting\results",
        "_archive\frontend",
        "_archive\old-archive"
    )
    
    foreach ($dir in $directories) {
        if ($Apply) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Log "Created directory: $dir"
        } else {
            Write-Host "Would create: $dir" -ForegroundColor Yellow
        }
    }
}

function Move-FileSafe {
    param(
        [string]$Source,
        [string]$Destination
    )
    
    if (Test-Path $Source) {
        if ($Apply) {
            $destDir = Split-Path -Parent $Destination
            if (!(Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            
            if (Test-Path $Destination) {
                Write-Log "WARNING: Destination exists, skipping: $Destination"
            } else {
                Move-Item -Path $Source -Destination $Destination -Force
                Write-Log "Moved: $Source -> $Destination"
            }
        } else {
            Write-Host "Would move: $Source -> $Destination" -ForegroundColor Cyan
        }
    } else {
        if ($Apply) {
            Write-Log "Source not found, skipping: $Source"
        }
    }
}

function Move-DirectorySafe {
    param(
        [string]$Source,
        [string]$Destination
    )
    
    if (Test-Path $Source -PathType Container) {
        if ($Apply) {
            $destDir = Split-Path -Parent $Destination
            if (!(Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            
            if (Test-Path $Destination -PathType Container) {
                Write-Log "Merging directory: $Source -> $Destination"
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
                Write-Log "Moved directory: $Source -> $Destination"
            }
        } else {
            Write-Host "Would move directory: $Source -> $Destination" -ForegroundColor Cyan
        }
    }
}

function Reorganize-Repository {
    Write-Log "Starting repository reorganization (Apply: $Apply)"
    
    # Create new directory structure
    Create-Directories
    
    # Move main trading script
    Move-FileSafe "main_enhanced.py" "trading-script.py"
    Move-FileSafe "main.py" "_archive\deprecated\main.py"
    
    # Move trading scripts
    Get-ChildItem "01_Trading_Scripts\*.py" -ErrorAction SilentlyContinue | ForEach-Object {
        $newName = ($_.Name -replace '_', '-').ToLower()
        Move-FileSafe $_.FullName "scripts-and-data\automation\$newName"
    }
    
    # Move portfolio data
    Move-DirectorySafe "02_Portfolio_Data\Daily_Snapshots" "scripts-and-data\daily-logs"
    Move-DirectorySafe "02_Portfolio_Data\Performance" "performance-tracking\historical"
    Move-DirectorySafe "02_Portfolio_Data\Trade_History" "scripts-and-data\trade-history"
    
    # Move research reports
    Move-DirectorySafe "03_Research_Reports\Daily" "research\md\daily"
    Move-DirectorySafe "03_Research_Reports\Weekly" "research\md\weekly"
    Move-DirectorySafe "03_Research_Reports\Deep_Research" "research\pdf\deep-research"
    Move-FileSafe "03_Research_Reports\automated_research_pipeline.py" "scripts-and-data\automation\automated-research-pipeline.py"
    Move-FileSafe "03_Research_Reports\openai_research_analyzer.py" "agents\openai-research-analyzer.py"
    
    # Move bot strategies
    Move-DirectorySafe "04_Bot_Strategies\DEE_BOT" "bot-strategies\dee-bot"
    Move-DirectorySafe "04_Bot_Strategies\SHORGAN_BOT" "bot-strategies\shorgan-bot"
    Move-DirectorySafe "04_Bot_Strategies\Common\daily_trades" "scripts-and-data\daily-logs"
    
    # Move data providers
    Move-DirectorySafe "05_Data_Providers\Market_Data" "data-providers\market-data"
    Move-DirectorySafe "05_Data_Providers\News" "data-providers\news"
    Move-DirectorySafe "05_Data_Providers\Sentiment" "data-providers\sentiment"
    Move-FileSafe "05_Data_Providers\data_providers.py" "data-providers\data-providers.py"
    Move-FileSafe "05_Data_Providers\enhanced_providers.py" "data-providers\enhanced-providers.py"
    Move-FileSafe "05_Data_Providers\catalyst_detector.py" "data-providers\catalyst-detector.py"
    
    # Move risk management
    Move-DirectorySafe "06_Risk_Management\Models" "risk-management\models"
    Move-DirectorySafe "06_Risk_Management\Reports" "risk-management\reports"
    Move-DirectorySafe "06_Risk_Management\Alerts" "risk-management\alerts"
    
    # Move documentation
    Move-DirectorySafe "07_Documentation\Guides" "docs\guides"
    Move-DirectorySafe "07_Documentation\Session_Notes" "docs\session-notes"
    Move-DirectorySafe "07_Documentation\Research_Papers" "docs\experiment-details\research-papers"
    
    # Move configuration
    Move-FileSafe "08_Configuration\api_config.py" "config\api-config.py"
    
    # Move utils and tests
    Move-DirectorySafe "10_Utils\Tests" "tests"
    Move-DirectorySafe "10_Utils\Scripts" "scripts-and-data\automation\utils"
    
    # Move Multi-Agent System
    Get-ChildItem "Multi-Agent_System\agents\*.py" -ErrorAction SilentlyContinue | ForEach-Object {
        $newName = $_.Name -replace '_', '-'
        Move-FileSafe $_.FullName "agents\$newName"
    }
    Move-DirectorySafe "Multi-Agent_System\communication" "agents\communication"
    
    # Move Performance Tracking
    Move-FileSafe "Performance_Tracking\daily_performance_tracker.py" "performance-tracking\daily-performance-tracker.py"
    Move-FileSafe "Performance_Tracking\portfolio_tracker.py" "performance-tracking\portfolio-tracker.py"
    Move-FileSafe "Performance_Tracking\automated_performance_tracker.py" "performance-tracking\automated-performance-tracker.py"
    
    # Move Research Reports
    Move-DirectorySafe "Research_Reports\post_market_daily" "research\md\post-market"
    Move-DirectorySafe "Research_Reports\pre_market_daily" "research\md\pre-market"
    Move-DirectorySafe "Research_Reports\weekly_analysis" "research\md\weekly"
    
    # Move duplicate Bot_Strategies
    Move-DirectorySafe "Bot_Strategies\DEE-BOT" "_archive\deprecated\Bot_Strategies\DEE-BOT"
    Move-DirectorySafe "Bot_Strategies\SHORGAN-BOT" "_archive\deprecated\Bot_Strategies\SHORGAN-BOT"
    
    # Move Core Trading
    Move-FileSafe "Core_Trading\execute_trades_20250110.py" "scripts-and-data\automation\execute-trades.py"
    Move-FileSafe "Core_Trading\trading_engine.py" "scripts-and-data\automation\trading-engine.py"
    Move-DirectorySafe "Core_Trading" "_archive\deprecated\Core_Trading"
    
    # Move Configuration
    Move-FileSafe "Configuration\requirements.txt" "requirements.txt"
    Move-FileSafe "Configuration\sp100_universe.py" "config\sp100-universe.py"
    Move-FileSafe "Configuration\telegram_setup.md" "docs\guides\telegram-setup.md"
    
    # Move Documentation
    Move-FileSafe "Documentation\CLAUDE.md" "docs\guides\claude.md"
    Move-FileSafe "Documentation\CONTINUE_SESSION_GUIDE.md" "docs\guides\continue-session-guide.md"
    Move-FileSafe "Documentation\GITHUB_REPOSITORY_GUIDE.md" "docs\guides\github-repository-guide.md"
    Move-FileSafe "Documentation\SETUP_AUTOMATED_TRADING_GUIDE.md" "docs\guides\setup-automated-trading-guide.md"
    Move-FileSafe "Documentation\SYSTEM_OVERVIEW.md" "docs\experiment-details\system-overview.md"
    
    # Archive duplicates
    Move-DirectorySafe "archive" "_archive\old-archive"
    Move-DirectorySafe "data" "_archive\deprecated\data"
    Move-DirectorySafe "config" "_archive\deprecated\config"
    
    # Move risk management files
    Move-FileSafe "risk_management\risk_monitor.py" "risk-management\risk-monitor.py"
    Move-FileSafe "risk_management\portfolio_performance.py" "risk-management\portfolio-performance.py"
    
    # Move tools
    Move-DirectorySafe "tools\idea_generation" "scripts-and-data\automation\idea-generation"
    Move-DirectorySafe "tools\reporting" "scripts-and-data\automation\reporting"
    Move-DirectorySafe "tools\scheduling" "scripts-and-data\automation\scheduling"
    Move-DirectorySafe "tools\testing" "tests\integration"
    
    # Move frontend
    Move-DirectorySafe "frontend\trading-dashboard" "_archive\frontend\trading-dashboard"
    
    # Move logs
    Move-DirectorySafe "logs" "scripts-and-data\logs"
    
    # Move trading snapshots
    Get-ChildItem "trading_snapshot_20250910_*.json" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileSafe $_.FullName "scripts-and-data\trading-snapshots\$($_.Name)"
    }
    
    # Move bot-specific logs
    Get-ChildItem "DEE_BOT_*.json" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileSafe $_.FullName "scripts-and-data\daily-logs\2025-09-10\dee-bot\$($_.Name)"
    }
    
    Get-ChildItem "SHORGAN_BOT_*.json" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileSafe $_.FullName "scripts-and-data\daily-logs\2025-09-10\shorgan-bot\$($_.Name)"
    }
    
    # Move trading logs
    Get-ChildItem "TRADING_LOG_*.json" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileSafe $_.FullName "scripts-and-data\daily-logs\2025-09-10\$($_.Name)"
    }
    
    # Move misc files
    Move-FileSafe "performance_history.json" "performance-tracking\performance-history.json"
    Move-FileSafe "trading_bot.db" "data\trading-bot.db"
    
    # Move PDFs to documentation
    Get-ChildItem "*.pdf" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileSafe $_.FullName "docs\experiment-details\research-papers\$($_.Name)"
    }
    
    # Move test files from root
    Get-ChildItem "test_*.py" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileSafe $_.FullName "tests\$($_.Name)"
    }
    
    # Move automation scripts
    Move-FileSafe "create_trading_schedule.ps1" "scripts-and-data\automation\create-trading-schedule.ps1"
    Move-FileSafe "run_morning_trades.bat" "scripts-and-data\automation\run-morning-trades.bat"
    Move-FileSafe "setup_github_repo.bat" "scripts-and-data\automation\setup-github-repo.bat"
    Move-FileSafe "generate_tree.ps1" "scripts-and-data\automation\generate-tree.ps1"
    Move-FileSafe "get_telegram_chat_id.py" "scripts-and-data\automation\get-telegram-chat-id.py"
    
    # Move documentation files
    Move-FileSafe "REPOSITORY_STRUCTURE.md" "docs\repository-structure.md"
    Move-FileSafe "DATA_INTEGRATION_SUMMARY.md" "docs\session-notes\data-integration-summary.md"
    
    # Archive deprecated scripts
    Move-FileSafe "migrate_all_files.py" "_archive\deprecated\migrate_all_files.py"
    Move-FileSafe "move_files.py" "_archive\deprecated\move_files.py"
    Move-FileSafe "REORGANIZE_REPOSITORY.py" "_archive\deprecated\REORGANIZE_REPOSITORY.py"
    
    # Clean up empty directories
    if ($Apply) {
        Get-ChildItem -Path . -Recurse -Directory | 
            Where-Object { (Get-ChildItem $_.FullName).Count -eq 0 } | 
            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Write-Log "Cleaned up empty directories"
    }
    
    Write-Log "Repository reorganization complete!"
}

# Main execution
if ($Undo) {
    Write-Host "Undo functionality will be implemented in the undo script." -ForegroundColor Yellow
    Write-Host "Please use reorganize-undo.ps1 for rollback." -ForegroundColor Yellow
} elseif ($Apply) {
    Write-Host "WARNING: This will reorganize your entire repository structure!" -ForegroundColor Red
    $confirm = Read-Host "Are you sure you want to proceed? (yes/no)"
    if ($confirm -eq "yes") {
        Reorganize-Repository
    } else {
        Write-Host "Operation cancelled." -ForegroundColor Yellow
    }
} else {
    Write-Host "DRY RUN MODE - No changes will be made" -ForegroundColor Green
    Write-Host "Use -Apply to execute changes" -ForegroundColor Yellow
    Write-Host "Use -Undo to rollback changes" -ForegroundColor Yellow
    Reorganize-Repository
}