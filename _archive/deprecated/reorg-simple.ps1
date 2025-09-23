# Simplified PowerShell Reorganization Script
param([string]$Mode = "--dry-run")

$ErrorActionPreference = "Continue"
$reorgLog = "reorg-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

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

Write-Log "Starting reorganization in mode: $Mode"

# Create core directories first
$dirs = @(
    "agents/core", "agents/dee-bot", "agents/shorgan-bot", "agents/communication",
    "scripts-and-data/data/positions", "scripts-and-data/data/reports",
    "research/pdf", "docs/guides", "logs/trading", "_archive/deprecated"
)

foreach ($dir in $dirs) {
    if ($Mode -eq "--apply") {
        New-Item -ItemType Directory -Path $dir -Force -ErrorAction SilentlyContinue | Out-Null
    }
    Write-Log "Created directory: $dir"
}

# Process simple file moves
$moves = @(
    @{src="main.py"; dst="main.py"; reason="keep in root"},
    @{src="CLAUDE.md"; dst="docs/claude-context.md"; reason="documentation"},
    @{src="README.md"; dst="README.md"; reason="keep in root"},
    @{src="execute_tuesday_trades.py"; dst="_archive/deprecated/execute-tuesday-trades.py"; reason="archive"},
    @{src="check_kss_stop.py"; dst="scripts-and-data/scripts/check-kss-stop.py"; reason="utility"}
)

foreach ($move in $moves) {
    if (Test-Path $move.src) {
        if ($Mode -eq "--apply") {
            $destDir = Split-Path $move.dst -Parent
            if ($destDir -and $destDir -ne "") {
                New-Item -ItemType Directory -Path $destDir -Force -ErrorAction SilentlyContinue | Out-Null
            }
            try {
                if ($move.src -ne $move.dst) {
                    Copy-Item -Path $move.src -Destination $move.dst -Force
                    Remove-Item -Path $move.src -Force
                    Write-Log "MOVED: $($move.src) -> $($move.dst)" "SUCCESS"
                }
            } catch {
                Write-Log "Failed to move $($move.src): $_" "ERROR"
            }
        } else {
            Write-Log "Would move: $($move.src) -> $($move.dst)"
        }
    }
}

# Process Python files in agents directory
if (Test-Path "agents") {
    Get-ChildItem "agents/*.py" -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Log "Keeping agent file: $($_.Name)"
    }
}

# Move batch files
Get-ChildItem "*.bat" -ErrorAction SilentlyContinue | ForEach-Object {
    $dest = "scripts-and-data/scripts/$($_.Name)"
    if ($Mode -eq "--apply") {
        New-Item -ItemType Directory -Path "scripts-and-data/scripts" -Force -ErrorAction SilentlyContinue | Out-Null
        Move-Item -Path $_.FullName -Destination $dest -Force -ErrorAction SilentlyContinue
        Write-Log "MOVED: $($_.Name) -> $dest" "SUCCESS"
    } else {
        Write-Log "Would move: $($_.Name) -> $dest"
    }
}

# Archive old reorganization files
$oldFiles = @("reorganize-repo.sh", "reorganize-undo.sh", "reorg.ps1", "undo_reorg.ps1")
foreach ($file in $oldFiles) {
    if (Test-Path $file) {
        $dest = "_archive/deprecated/$file"
        if ($Mode -eq "--apply") {
            Move-Item -Path $file -Destination $dest -Force -ErrorAction SilentlyContinue
            Write-Log "ARCHIVED: $file" "SUCCESS"
        } else {
            Write-Log "Would archive: $file"
        }
    }
}

Write-Log "========================================"
if ($Mode -eq "--dry-run") {
    Write-Log "DRY RUN COMPLETE - No files were moved" "SUCCESS"
    Write-Log "To apply: .\reorg-simple.ps1 --apply"
} else {
    Write-Log "REORGANIZATION COMPLETE" "SUCCESS"
}
Write-Log "Log file: $reorgLog"