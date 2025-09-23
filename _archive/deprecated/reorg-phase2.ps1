# Phase 2: Move larger directory structures
param([string]$Mode = "--dry-run")

$ErrorActionPreference = "Continue"
$reorgLog = "reorg-phase2-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

function Write-Log {
    param($Message, $Type = "INFO")
    $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Type] $Message"
    Add-Content -Path $reorgLog -Value $logEntry -ErrorAction SilentlyContinue

    switch($Type) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        default { Write-Host $logEntry }
    }
}

Write-Log "Phase 2: Moving directories - Mode: $Mode"

# Directory moves
$dirMoves = @(
    @{src="01_trading_system/bots/dee_bot"; dst="agents/dee-bot/legacy-bots"; reason="consolidate dee bot"},
    @{src="01_trading_system/bots/shorgan_bot"; dst="agents/shorgan-bot/legacy-bots"; reason="consolidate shorgan bot"},
    @{src="01_trading_system/automation"; dst="scripts-and-data/automation/legacy"; reason="merge automation"},
    @{src="01_trading_system/core"; dst="agents/core/legacy"; reason="core scripts"},
    @{src="01_trading_system/config"; dst="configs/bots/legacy"; reason="bot configs"},
    @{src="01_trading_system/execution"; dst="agents/execution/legacy"; reason="execution handlers"},

    @{src="02_data/market"; dst="scripts-and-data/data/market"; reason="market data"},
    @{src="02_data/portfolio"; dst="scripts-and-data/data/portfolio"; reason="portfolio data"},
    @{src="02_data/reports"; dst="scripts-and-data/data/reports/legacy"; reason="reports"},
    @{src="02_data/research"; dst="research/data"; reason="research data"},

    @{src="03_config"; dst="configs/legacy-config"; reason="config files"},
    @{src="04_risk"; dst="risk"; reason="risk management"},
    @{src="05_backtesting"; dst="backtests"; reason="backtesting"},
    @{src="06_utils"; dst="utils/legacy"; reason="utilities"},
    @{src="07_docs"; dst="docs/legacy"; reason="documentation"},
    @{src="08_frontend"; dst="frontend/legacy-08"; reason="frontend"},
    @{src="08_trading_logs"; dst="logs/trading/legacy"; reason="trading logs"},
    @{src="09_logs"; dst="logs/legacy"; reason="logs"},

    @{src="communication"; dst="agents/communication"; reason="agent communication"},
    @{src="dee-bot"; dst="agents/dee-bot/standalone"; reason="dee bot standalone"},
    @{src="shorgan-bot"; dst="agents/shorgan-bot/standalone"; reason="shorgan bot standalone"},
    @{src="daily-reports"; dst="scripts-and-data/data/reports/daily"; reason="daily reports"},
    @{src="weekly-reports"; dst="scripts-and-data/data/reports/weekly"; reason="weekly reports"},
    @{src="portfolio-holdings"; dst="scripts-and-data/data/positions"; reason="portfolio positions"},
    @{src="trade-logs"; dst="logs/trading/trade-logs"; reason="trade logs"},
    @{src="performance-metrics"; dst="scripts-and-data/data/metrics"; reason="performance metrics"},
    @{src="research-analysis"; dst="research/analysis"; reason="research analysis"},
    @{src="post_market_daily"; dst="scripts-and-data/data/reports/post-market-legacy"; reason="post market reports"}
)

foreach ($move in $dirMoves) {
    if (Test-Path $move.src) {
        if ($Mode -eq "--apply") {
            try {
                # Ensure destination parent exists
                $destParent = Split-Path $move.dst -Parent
                if ($destParent) {
                    New-Item -ItemType Directory -Path $destParent -Force -ErrorAction SilentlyContinue | Out-Null
                }

                # Move the directory
                Move-Item -Path $move.src -Destination $move.dst -Force -ErrorAction Stop
                Write-Log "MOVED DIR: $($move.src) -> $($move.dst)" "SUCCESS"
            } catch {
                # If move fails, try copy and delete
                try {
                    Copy-Item -Path $move.src -Destination $move.dst -Recurse -Force
                    Remove-Item -Path $move.src -Recurse -Force
                    Write-Log "COPIED & REMOVED: $($move.src) -> $($move.dst)" "SUCCESS"
                } catch {
                    Write-Log "Failed to move $($move.src): $_" "ERROR"
                }
            }
        } else {
            Write-Log "Would move directory: $($move.src) -> $($move.dst)"
        }
    } else {
        Write-Log "Directory not found: $($move.src)" "WARNING"
    }
}

# Move remaining root files
$rootFiles = @(
    @{pattern="*.json"; dst="scripts-and-data/data/json"; reason="json files"},
    @{pattern="*.log"; dst="logs/system"; reason="log files"},
    @{pattern="*.pdf"; dst="research/pdf"; reason="research papers"},
    @{pattern="*.md"; dst="docs/guides"; reason="documentation"},
    @{pattern="*.txt"; dst="_archive/misc"; reason="text files"},
    @{pattern="*.csv"; dst="_archive/misc"; reason="csv files"}
)

foreach ($pattern in $rootFiles) {
    $files = Get-ChildItem -Path $pattern.pattern -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        # Skip special files
        if ($file.Name -in @("README.md", "main.py", ".gitignore", ".env", ".coveragerc")) {
            continue
        }

        if ($Mode -eq "--apply") {
            $dest = Join-Path $pattern.dst $file.Name
            $destDir = $pattern.dst

            New-Item -ItemType Directory -Path $destDir -Force -ErrorAction SilentlyContinue | Out-Null
            Move-Item -Path $file.FullName -Destination $dest -Force -ErrorAction SilentlyContinue
            Write-Log "MOVED: $($file.Name) -> $dest" "SUCCESS"
        } else {
            Write-Log "Would move: $($file.Name) -> $($pattern.dst)/$($file.Name)"
        }
    }
}

Write-Log "========================================"
if ($Mode -eq "--dry-run") {
    Write-Log "PHASE 2 DRY RUN COMPLETE" "SUCCESS"
    Write-Log "To apply: .\reorg-phase2.ps1 --apply"
} else {
    Write-Log "PHASE 2 COMPLETE" "SUCCESS"

    # Summary
    $movedCount = (Get-Content $reorgLog | Select-String "SUCCESS" | Measure-Object).Count
    $errorCount = (Get-Content $reorgLog | Select-String "ERROR" | Measure-Object).Count

    Write-Log "Files/Directories moved: $movedCount"
    Write-Log "Errors: $errorCount"
}
Write-Log "Log file: $reorgLog"