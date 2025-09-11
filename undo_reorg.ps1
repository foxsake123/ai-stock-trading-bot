# Undo Repository Reorganization
# Reads reorg.log and reverses all operations

$LogFile = "reorg.log"
$UndoLog = "undo.log"

function Write-UndoLog {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Write-Host $logEntry
    Add-Content -Path $UndoLog -Value $logEntry -Encoding UTF8
}

function Undo-Moves {
    if (-not (Test-Path $LogFile)) {
        Write-Error "Log file not found: $LogFile"
        return
    }
    
    Write-UndoLog "Reading operations from $LogFile..."
    
    # Read log in reverse
    $lines = Get-Content $LogFile -Encoding UTF8
    [array]::Reverse($lines)
    
    foreach ($line in $lines) {
        if ($line -match '\[.*\] MOVED: (.*) -> (.*) \((.*)\)') {
            $dest = $matches[1]  # Original location
            $src = $matches[2]   # Current location
            $reason = $matches[3]
            
            if (Test-Path $src) {
                try {
                    $destDir = Split-Path -Path $dest -Parent
                    if ($destDir -and -not (Test-Path $destDir)) {
                        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                    }
                    Move-Item -Path $src -Destination $dest -Force
                    Write-UndoLog "RESTORED: $src -> $dest"
                } catch {
                    Write-UndoLog "ERROR restoring $src -> $dest : $($_.Exception.Message)"
                }
            } else {
                Write-UndoLog "SKIP: $src not found"
            }
        }
    }
}

function Restore-Deduped {
    if (-not (Test-Path "_archive\duplicates")) {
        Write-UndoLog "No duplicates archive found"
        return
    }
    
    Get-ChildItem -Path "_archive\duplicates" -Filter "*.pointer.txt" -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
        $pointerFile = $_.FullName
        $originalFile = $pointerFile -replace '\.pointer\.txt$', ''
        
        if (Test-Path $originalFile) {
            try {
                $content = Get-Content $pointerFile -ErrorAction SilentlyContinue
                $dupLine = $content | Where-Object { $_ -match '^Duplicate: (.*)' }
                
                if ($dupLine) {
                    $origPath = ($dupLine -split ': ', 2)[1].Trim()
                    $origDir = Split-Path -Path $origPath -Parent
                    
                    if ($origDir -and -not (Test-Path $origDir)) {
                        New-Item -ItemType Directory -Path $origDir -Force | Out-Null
                    }
                    Move-Item -Path $originalFile -Destination $origPath -Force
                    Write-UndoLog "RESTORED duplicate: $originalFile -> $origPath"
                    Remove-Item $pointerFile -Force
                }
            } catch {
                Write-UndoLog "ERROR restoring duplicate $originalFile : $($_.Exception.Message)"
            }
        }
    }
}

function Remove-EmptyDirectories {
    Write-UndoLog "Cleaning up empty directories..."
    
    # Remove empty canonical directories
    $canonicalDirs = @(
        "01_trading_system", "02_data", "03_config", "04_risk", "05_backtesting",
        "06_utils", "07_docs", "08_frontend", "09_logs", "_archive"
    )
    
    foreach ($dir in $canonicalDirs) {
        if (Test-Path $dir) {
            # Remove empty subdirectories first
            Get-ChildItem -Path $dir -Recurse -Directory | Sort-Object FullName -Descending | ForEach-Object {
                if ((Get-ChildItem $_.FullName -Force | Measure-Object).Count -eq 0) {
                    Remove-Item $_.FullName -Force
                    Write-UndoLog "Removed empty directory: $($_.FullName)"
                }
            }
            
            # Remove main directory if empty
            if ((Get-ChildItem $dir -Force | Measure-Object).Count -eq 0) {
                Remove-Item $dir -Force
                Write-UndoLog "Removed empty directory: $dir"
            }
        }
    }
}

# Main execution
Write-UndoLog "Starting UNDO operation..."

if (-not (Test-Path $LogFile)) {
    Write-UndoLog "ERROR: No reorg.log file found. Nothing to undo."
    exit 1
}

Undo-Moves
Restore-Deduped
Remove-EmptyDirectories

Write-UndoLog "Undo operation complete!"
Write-Host "Repository restored to pre-reorganization state." -ForegroundColor Green