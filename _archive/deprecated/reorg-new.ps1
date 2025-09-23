# PowerShell Reorganization Script for AI Trading Bot
# Target: LuckyOne7777 ChatGPT-Micro-Cap-Experiment structure
# Date: September 23, 2025

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("--dry-run", "--apply", "--undo")]
    [string]$Mode = "--dry-run"
)

$ErrorActionPreference = "Stop"
$reorgLog = "reorg-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
$mappingFile = "mapping-complete.csv"

# Initialize logging
function Write-Log {
    param($Message, $Type = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp [$Type] $Message"
    Add-Content -Path $reorgLog -Value $logEntry

    switch($Type) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        default { Write-Host $logEntry }
    }
}

# Create directory structure
function Initialize-Directories {
    $directories = @(
        "agents/core",
        "agents/dee-bot/strategies",
        "agents/dee-bot/analysis",
        "agents/shorgan-bot/strategies",
        "agents/shorgan-bot/analysis",
        "agents/communication",
        "agents/execution",
        "agents/legacy",
        "scripts-and-data/automation",
        "scripts-and-data/scripts/setup",
        "scripts-and-data/data/positions",
        "scripts-and-data/data/performance",
        "scripts-and-data/data/reports/daily",
        "scripts-and-data/data/reports/weekly",
        "scripts-and-data/data/reports/post-market",
        "scripts-and-data/data/market",
        "scripts-and-data/data/portfolio",
        "scripts-and-data/data/metrics",
        "scripts-and-data/data/json",
        "scripts-and-data/data/db",
        "scripts-and-data/utilities",
        "research/pdf",
        "research/md",
        "research/chatgpt",
        "research/multi-agent",
        "research/reports/pre-market",
        "research/data",
        "docs/guides",
        "docs/session-logs",
        "docs/daily-orders",
        "docs/reports",
        "docs/index",
        "docs/legacy",
        "configs/bots",
        "configs/claude",
        "frontend/legacy",
        "backtests/strategies",
        "backtests/results",
        "risk/models",
        "risk/reports",
        "utils/tests",
        "utils/tools",
        "utils/extensions/chatgpt",
        "utils/legacy",
        "logs/trading/dee",
        "logs/trading/shorgan",
        "logs/system",
        "logs/snapshots",
        "logs/automation",
        "_archive/deprecated",
        "_archive/duplicates",
        "_archive/legacy",
        "_archive/misc",
        "_archive/temp/pytest-cache",
        "_archive/temp/pycache",
        "_archive/logs",
        "_archive/legacy_structure"
    )

    foreach ($dir in $directories) {
        if ($Mode -eq "--apply") {
            if (-not (Test-Path $dir)) {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
                Write-Log "Created directory: $dir" "SUCCESS"
            }
        } else {
            Write-Log "Would create directory: $dir" "INFO"
        }
    }
}

# Calculate SHA-256 hash for deduplication
function Get-FileHashSHA256 {
    param($FilePath)
    if (Test-Path $FilePath -PathType Leaf) {
        try {
            return (Get-FileHash -Path $FilePath -Algorithm SHA256).Hash
        } catch {
            return $null
        }
    }
    return $null
}

# Move file with logging
function Move-FileWithLog {
    param($Source, $Destination, $Reason)

    if (-not (Test-Path $Source)) {
        Write-Log "Source not found: $Source" "WARNING"
        return
    }

    $destDir = Split-Path -Parent $Destination

    if ($Mode -eq "--apply") {
        # Create destination directory if needed
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }

        # Check for duplicates
        if (Test-Path $Destination) {
            $sourceHash = Get-FileHashSHA256 $Source
            $destHash = Get-FileHashSHA256 $Destination

            if ($sourceHash -eq $destHash) {
                # Files are identical, archive the source
                $dupDest = "_archive/duplicates/$(Split-Path -Leaf $Source)"
                Move-Item -Path $Source -Destination $dupDest -Force
                Write-Log "DUPLICATE: $Source -> $dupDest (identical to $Destination)" "WARNING"
                # Create pointer file
                Set-Content -Path "$dupDest.pointer" -Value "Original location: $Destination"
                return
            } else {
                # Files differ, rename destination
                $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
                $newDest = "$Destination.$timestamp"
                Move-Item -Path $Source -Destination $newDest -Force
                Write-Log "MOVED: $Source -> $newDest (collision resolved)" "SUCCESS"
                return
            }
        }

        Move-Item -Path $Source -Destination $Destination -Force
        Write-Log "MOVED: $Source -> $Destination | Reason: $Reason" "SUCCESS"
    } else {
        Write-Log "DRY-RUN: Would move $Source -> $Destination | Reason: $Reason" "INFO"
    }
}

# Process mapping file
function Process-Mapping {
    if (-not (Test-Path $mappingFile)) {
        Write-Log "Mapping file not found: $mappingFile" "ERROR"
        exit 1
    }

    $csv = Import-Csv $mappingFile
    $totalMoves = ($csv | Where-Object { -not $_.source_path.StartsWith("#") }).Count
    $currentMove = 0

    foreach ($row in $csv) {
        if ($row.source_path.StartsWith("#")) { continue }

        $currentMove++
        Write-Progress -Activity "Processing files" -Status "$currentMove of $totalMoves" -PercentComplete (($currentMove / $totalMoves) * 100)

        # Handle wildcards
        if ($row.source_path.Contains("*")) {
            try {
                $files = @(Get-ChildItem -Path $row.source_path -ErrorAction SilentlyContinue)
                if ($files.Count -gt 0) {
                    foreach ($file in $files) {
                        $destPath = $row.dest_path
                        if ($destPath.EndsWith("/") -or $destPath.EndsWith("\")) {
                            $destPath = Join-Path $destPath (Split-Path -Leaf $file.FullName)
                        }
                        # Convert to kebab-case
                        $destName = (Split-Path -Leaf $destPath) -replace '_', '-' -replace '([A-Z])', '-$1' -replace '^-', '' -replace '--', '-'
                        if ((Split-Path -Parent $destPath) -ne "") {
                            $destPath = Join-Path (Split-Path -Parent $destPath) $destName.ToLower()
                        } else {
                            $destPath = $destName.ToLower()
                        }

                        Move-FileWithLog -Source $file.FullName -Destination $destPath -Reason $row.reason
                    }
                } else {
                    Write-Log "No files found for pattern: $($row.source_path)" "WARNING"
                }
            } catch {
                Write-Log "Error processing wildcard: $($row.source_path) - $_" "WARNING"
            }
        } else {
            # Single file move
            if ($row.source_path -and $row.dest_path) {
                $destPath = $row.dest_path
                if (Test-Path $row.source_path) {
                    # Convert to kebab-case if not keeping in root
                    if ($destPath -ne $row.source_path) {
                        $destName = (Split-Path -Leaf $destPath) -replace '_', '-' -replace '([A-Z])', '-$1' -replace '^-', '' -replace '--', '-'
                        $parentPath = Split-Path -Parent $destPath
                        if ($parentPath -ne "") {
                            $destPath = Join-Path $parentPath $destName.ToLower()
                        } else {
                            $destPath = $destName.ToLower()
                        }
                    }
                    Move-FileWithLog -Source $row.source_path -Destination $destPath -Reason $row.reason
                } else {
                    Write-Log "Source not found: $($row.source_path)" "WARNING"
                }
            } else {
                Write-Log "Invalid mapping entry - source: $($row.source_path), dest: $($row.dest_path)" "WARNING"
            }
        }
    }
}

# Clean empty directories
function Remove-EmptyDirectories {
    $emptyDirs = Get-ChildItem -Directory -Recurse |
                 Where-Object { (Get-ChildItem $_.FullName -Force).Count -eq 0 } |
                 Sort-Object -Property FullName -Descending

    foreach ($dir in $emptyDirs) {
        if ($Mode -eq "--apply") {
            Remove-Item $dir.FullName -Force
            Write-Log "Removed empty directory: $($dir.FullName)" "SUCCESS"
        } else {
            Write-Log "Would remove empty directory: $($dir.FullName)" "INFO"
        }
    }
}

# Undo functionality
function Undo-Reorganization {
    $latestLog = Get-ChildItem -Filter "reorg-*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

    if (-not $latestLog) {
        Write-Log "No reorg log found to undo" "ERROR"
        exit 1
    }

    Write-Log "Undoing changes from: $($latestLog.Name)" "INFO"

    $logContent = Get-Content $latestLog.FullName
    $moves = $logContent | Where-Object { $_ -match "MOVED:" }

    # Reverse the order for undo
    [array]::Reverse($moves)

    foreach ($move in $moves) {
        if ($move -match "MOVED: (.+) -> (.+) \|") {
            $source = $matches[2].Trim()
            $destination = $matches[1].Trim()

            if (Test-Path $source) {
                $destDir = Split-Path -Parent $destination
                if (-not (Test-Path $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }
                Move-Item -Path $source -Destination $destination -Force
                Write-Log "UNDONE: $source -> $destination" "SUCCESS"
            }
        }
    }
}

# Main execution
function Main {
    Write-Log "========================================" "INFO"
    Write-Log "AI Trading Bot Repository Reorganization" "INFO"
    Write-Log "Mode: $Mode" "INFO"
    Write-Log "========================================" "INFO"

    if ($Mode -eq "--undo") {
        Undo-Reorganization
    } else {
        # Step 1: Initialize directories
        Write-Log "Step 1: Initializing directory structure..." "INFO"
        Initialize-Directories

        # Step 2: Process mapping
        Write-Log "Step 2: Processing file moves..." "INFO"
        Process-Mapping

        # Step 3: Clean empty directories
        Write-Log "Step 3: Cleaning empty directories..." "INFO"
        Remove-EmptyDirectories

        # Step 4: Summary
        Write-Log "========================================" "INFO"
        if ($Mode -eq "--dry-run") {
            Write-Log "DRY RUN COMPLETE - No files were moved" "SUCCESS"
            Write-Log "To apply changes, run: .\reorg-new.ps1 --apply" "INFO"
        } else {
            Write-Log "REORGANIZATION COMPLETE" "SUCCESS"
            Write-Log "To undo, run: .\reorg-new.ps1 --undo" "INFO"
        }
        Write-Log "Log file: $reorgLog" "INFO"
    }
}

# Run main
Main