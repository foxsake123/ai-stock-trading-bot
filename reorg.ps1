# Repository Reorganization Script
# Usage: .\reorg.ps1 [-DryRun] [-Apply] [-Undo]

param(
    [switch]$DryRun = $true,
    [switch]$Apply = $false,
    [switch]$Undo = $false
)

$LogFile = "reorg.log"
$MappingFile = "mapping.csv"
$HashLog = "hash_manifest.txt"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Write-Host $logEntry
    if ($Apply) {
        Add-Content -Path $LogFile -Value $logEntry -Encoding UTF8
    }
}

function New-Directories {
    $dirs = @(
        "01_trading_system\agents", "01_trading_system\bots\dee_bot", "01_trading_system\bots\shorgan_bot", "01_trading_system\core",
        "02_data\market", "02_data\portfolio\performance", "02_data\research\daily", "02_data\research\reports", "02_data\misc",
        "03_config\api", "03_config\trading",
        "04_risk\models", "04_risk\reports",
        "05_backtesting\strategies", "05_backtesting\results",
        "06_utils\scripts", "06_utils\tests", "06_utils\tools",
        "07_docs\guides", "07_docs\research_papers",
        "08_frontend",
        "09_logs\system", "09_logs\trading", "09_logs\snapshots",
        "_archive\duplicates", "_archive\deprecated", "_archive\legacy_structure\_corrupted"
    )
    
    foreach ($dir in $dirs) {
        if ($Apply) {
            if (-not (Test-Path $dir)) {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
                Write-Log "Created directory: $dir"
            }
        } else {
            Write-Host "Would create: $dir"
        }
    }
}

function Get-FileHashSHA256 {
    param([string]$FilePath)
    
    if (Test-Path -Path $FilePath -PathType Leaf) {
        $hash = Get-FileHash -Path $FilePath -Algorithm SHA256
        return $hash.Hash
    }
    return "DIRECTORY"
}

function Move-FileWithCheck {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$Reason
    )
    
    # Handle wildcards - expand the source pattern
    if ($Source.Contains("*")) {
        $files = Get-ChildItem -Path $Source -ErrorAction SilentlyContinue
    } else {
        if (Test-Path $Source) {
            $files = Get-Item $Source
        } else {
            return
        }
    }
    
    foreach ($file in $files) {
        $destPath = $Destination
        if (Test-Path -Path $Destination -PathType Container -ErrorAction SilentlyContinue) {
            $destPath = Join-Path -Path $Destination -ChildPath $file.Name
        }
        
        if ($Apply) {
            # Check if destination exists
            if (Test-Path -Path $destPath) {
                $srcHash = Get-FileHashSHA256 -FilePath $file.FullName
                $destHash = Get-FileHashSHA256 -FilePath $destPath
                if ($srcHash -eq $destHash) {
                    Write-Log "Skip (identical): $($file.FullName) -> $destPath"
                    continue
                } else {
                    # Append number to avoid overwrite
                    $n = 1
                    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($destPath)
                    $extension = [System.IO.Path]::GetExtension($destPath)
                    $directory = [System.IO.Path]::GetDirectoryName($destPath)
                    
                    while (Test-Path -Path "$directory\$baseName ($n)$extension") {
                        $n++
                    }
                    $destPath = "$directory\$baseName ($n)$extension"
                }
            }
            
            # Create parent directory
            $destDir = Split-Path -Path $destPath -Parent
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            
            # Move the file
            Move-Item -Path $file.FullName -Destination $destPath -Force
            Write-Log "MOVED: $($file.FullName) -> $destPath ($Reason)"
            $hash = Get-FileHashSHA256 -FilePath $destPath
            "$hash|$($file.FullName)|$destPath|$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Add-Content -Path $HashLog -Encoding UTF8
        } else {
            Write-Log "Would move: $($file.FullName) -> $destPath ($Reason)"
        }
    }
}

function Apply-Mapping {
    Write-Log "Processing mapping.csv..."
    
    if (-not (Test-Path $MappingFile)) {
        Write-Log "ERROR: mapping.csv not found!"
        return
    }
    
    $mappings = Import-Csv -Path $MappingFile
    foreach ($map in $mappings) {
        if (-not $map.source_path.StartsWith('#') -and $map.source_path.Trim() -ne '') {
            Move-FileWithCheck -Source $map.source_path -Destination $map.dest_path -Reason $map.reason
        }
    }
}

function Auto-Classify {
    Write-Log "Auto-classifying remaining files..."
    
    # PowerShell scripts
    Get-ChildItem -Path . -Filter "*.ps1" -Depth 0 -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne "reorg.ps1" -and $_.Name -ne "undo_reorg.ps1" } | ForEach-Object {
        Move-FileWithCheck -Source $_.FullName -Destination "06_utils\scripts\" -Reason "auto-classify PowerShell"
    }
    
    # Batch scripts
    Get-ChildItem -Path . -Filter "*.bat" -Depth 0 -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileWithCheck -Source $_.FullName -Destination "06_utils\scripts\" -Reason "auto-classify batch"
    }
    
    # Test files
    Get-ChildItem -Path . -Filter "test_*.py" -Depth 0 -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileWithCheck -Source $_.FullName -Destination "06_utils\tests\" -Reason "auto-classify test"
    }
    
    # Documentation (except README.md)
    Get-ChildItem -Path . -Filter "*.md" -Depth 0 -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne "README.md" } | ForEach-Object {
        Move-FileWithCheck -Source $_.FullName -Destination "07_docs\guides\" -Reason "auto-classify markdown"
    }
    
    # PDFs
    Get-ChildItem -Path . -Filter "*.pdf" -Depth 0 -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileWithCheck -Source $_.FullName -Destination "07_docs\research_papers\" -Reason "auto-classify PDF"
    }
    
    # Trading logs
    Get-ChildItem -Path . -Filter "DEE_BOT_*.json" -Depth 0 -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileWithCheck -Source $_.FullName -Destination "09_logs\trading\" -Reason "auto-classify DEE-BOT logs"
    }
    
    Get-ChildItem -Path . -Filter "SHORGAN_BOT_*.json" -Depth 0 -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileWithCheck -Source $_.FullName -Destination "09_logs\trading\" -Reason "auto-classify SHORGAN-BOT logs"
    }
    
    Get-ChildItem -Path . -Filter "TRADING_LOG_*.json" -Depth 0 -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileWithCheck -Source $_.FullName -Destination "09_logs\trading\" -Reason "auto-classify trading logs"
    }
    
    # Snapshot logs
    Get-ChildItem -Path . -Filter "trading_snapshot_*.json" -Depth 0 -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileWithCheck -Source $_.FullName -Destination "09_logs\snapshots\" -Reason "auto-classify snapshots"
    }
    
    # Risk alerts
    Get-ChildItem -Path . -Filter "risk_alerts_*.json" -Depth 0 -ErrorAction SilentlyContinue | ForEach-Object {
        Move-FileWithCheck -Source $_.FullName -Destination "09_logs\trading\" -Reason "auto-classify risk alerts"
    }
    
    # Utilities
    if (Test-Path "get_telegram_chat_id.py") {
        Move-FileWithCheck -Source "get_telegram_chat_id.py" -Destination "06_utils\tools\" -Reason "auto-classify utility"
    }
}

# Main execution
if ($Undo) {
    Write-Log "Starting UNDO operation..."
    if (Test-Path "undo_reorg.ps1") {
        & .\undo_reorg.ps1
    } else {
        Write-Log "ERROR: undo_reorg.ps1 not found!"
    }
    exit
}

if ($Apply) {
    Write-Log "Starting ACTUAL reorganization..."
    $DryRun = $false
} else {
    Write-Log "Starting DRY RUN reorganization..."
}

New-Directories
Apply-Mapping
Auto-Classify

Write-Log "Reorganization complete!"