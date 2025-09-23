# PowerShell Undo Script for AI Trading Bot Reorganization
# Standalone undo mechanism with safeguards

param(
    [Parameter(Mandatory=$false)]
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"

# Find the most recent reorg log
$reorgLogs = Get-ChildItem -Filter "reorg-*.log" | Sort-Object LastWriteTime -Descending
if ($reorgLogs.Count -eq 0) {
    Write-Host "ERROR: No reorganization log found. Nothing to undo." -ForegroundColor Red
    exit 1
}

$latestLog = $reorgLogs[0]
Write-Host "Found reorganization log: $($latestLog.Name)" -ForegroundColor Yellow

# Confirmation prompt
if (-not $Force) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "REORGANIZATION UNDO UTILITY" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "This will reverse the reorganization performed on:" -ForegroundColor Yellow
    Write-Host "  Log file: $($latestLog.Name)" -ForegroundColor Yellow
    Write-Host "  Date: $($latestLog.LastWriteTime)" -ForegroundColor Yellow
    Write-Host "`nThis operation will:"
    Write-Host "  1. Move all files back to their original locations"
    Write-Host "  2. Recreate original directory structure"
    Write-Host "  3. Remove new directories if empty"
    Write-Host "`nAre you sure you want to continue? (Y/N): " -NoNewline -ForegroundColor Red

    $confirmation = Read-Host
    if ($confirmation -ne 'Y' -and $confirmation -ne 'y') {
        Write-Host "Undo cancelled by user." -ForegroundColor Green
        exit 0
    }
}

# Parse log file and extract moves
$logContent = Get-Content $latestLog.FullName
$moves = @()
$duplicates = @()

foreach ($line in $logContent) {
    if ($line -match "\[SUCCESS\] MOVED: (.+) -> (.+) \| Reason:") {
        $moves += @{
            Source = $matches[1].Trim()
            Destination = $matches[2].Trim()
        }
    } elseif ($line -match "\[WARNING\] DUPLICATE: (.+) -> (.+) \(identical to") {
        $duplicates += @{
            Source = $matches[1].Trim()
            Archive = $matches[2].Trim()
        }
    }
}

Write-Host "`nFound $($moves.Count) file moves to undo" -ForegroundColor Yellow
Write-Host "Found $($duplicates.Count) duplicates to restore" -ForegroundColor Yellow

# Create undo log
$undoLog = "undo-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
Add-Content -Path $undoLog -Value "Undo operation started: $(Get-Date)"
Add-Content -Path $undoLog -Value "Reversing changes from: $($latestLog.Name)"

# Reverse moves (process in reverse order)
[array]::Reverse($moves)
$successCount = 0
$errorCount = 0

foreach ($move in $moves) {
    $currentLocation = $move.Destination
    $originalLocation = $move.Source

    if (Test-Path $currentLocation) {
        try {
            # Create original directory if needed
            $origDir = Split-Path -Parent $originalLocation
            if (-not (Test-Path $origDir)) {
                New-Item -ItemType Directory -Path $origDir -Force | Out-Null
            }

            # Move file back
            Move-Item -Path $currentLocation -Destination $originalLocation -Force
            Write-Host "✓ Restored: $originalLocation" -ForegroundColor Green
            Add-Content -Path $undoLog -Value "RESTORED: $currentLocation -> $originalLocation"
            $successCount++
        } catch {
            Write-Host "✗ Failed to restore: $originalLocation - $_" -ForegroundColor Red
            Add-Content -Path $undoLog -Value "ERROR: Failed to restore $originalLocation - $_"
            $errorCount++
        }
    } else {
        Write-Host "⚠ File not found at: $currentLocation" -ForegroundColor Yellow
        Add-Content -Path $undoLog -Value "WARNING: File not found at $currentLocation"
    }
}

# Restore duplicates
foreach ($dup in $duplicates) {
    $archiveLocation = $dup.Archive
    $originalLocation = $dup.Source

    if (Test-Path $archiveLocation) {
        try {
            # Create original directory if needed
            $origDir = Split-Path -Parent $originalLocation
            if (-not (Test-Path $origDir)) {
                New-Item -ItemType Directory -Path $origDir -Force | Out-Null
            }

            # Restore duplicate
            Move-Item -Path $archiveLocation -Destination $originalLocation -Force
            Write-Host "✓ Restored duplicate: $originalLocation" -ForegroundColor Green
            Add-Content -Path $undoLog -Value "RESTORED DUPLICATE: $archiveLocation -> $originalLocation"

            # Remove pointer file if exists
            $pointerFile = "$archiveLocation.pointer"
            if (Test-Path $pointerFile) {
                Remove-Item $pointerFile -Force
            }
        } catch {
            Write-Host "✗ Failed to restore duplicate: $originalLocation - $_" -ForegroundColor Red
            Add-Content -Path $undoLog -Value "ERROR: Failed to restore duplicate $originalLocation - $_"
        }
    }
}

# Clean up empty directories created during reorganization
Write-Host "`nCleaning up empty directories..." -ForegroundColor Yellow
$dirsToCheck = @(
    "agents/core", "agents/dee-bot", "agents/shorgan-bot", "agents/communication",
    "agents/execution", "agents/legacy", "scripts-and-data/data",
    "research", "utils/extensions", "logs/trading", "_archive/duplicates"
)

foreach ($dir in $dirsToCheck) {
    if (Test-Path $dir) {
        $items = Get-ChildItem $dir -Force -ErrorAction SilentlyContinue
        if ($items.Count -eq 0) {
            Remove-Item $dir -Force -Recurse -ErrorAction SilentlyContinue
            Write-Host "  Removed empty directory: $dir" -ForegroundColor Gray
        }
    }
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "UNDO OPERATION COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Files restored: $successCount" -ForegroundColor Green
Write-Host "Errors: $errorCount" -ForegroundColor $(if ($errorCount -gt 0) { "Red" } else { "Green" })
Write-Host "Undo log: $undoLog" -ForegroundColor Yellow

Add-Content -Path $undoLog -Value "Undo operation completed: $(Get-Date)"
Add-Content -Path $undoLog -Value "Files restored: $successCount"
Add-Content -Path $undoLog -Value "Errors: $errorCount"

# Verify main.py is back
if (Test-Path "main.py") {
    Write-Host "`n✓ main.py is present" -ForegroundColor Green
} else {
    Write-Host "`n⚠ WARNING: main.py not found in root" -ForegroundColor Red
}

Write-Host "`nRepository structure has been restored to original state." -ForegroundColor Green
Write-Host "Run 'git status' to verify changes." -ForegroundColor Yellow