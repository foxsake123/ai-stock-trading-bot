# Final cleanup phase
param([string]$Mode = "--dry-run")

$ErrorActionPreference = "Continue"
Write-Host "Final Cleanup Phase - Mode: $Mode" -ForegroundColor Cyan

# Clean up remaining items in root
$cleanup = @(
    @{src="G0pmQ66XUAEHqBk.jpeg"; dst="_archive/misc/image.jpeg"},
    @{src="nul"; dst="_archive/misc/nul"},
    @{src="reorganize_root.py"; dst="_archive/deprecated/reorganize-root.py"},
    @{src="reorg-new.ps1"; dst="_archive/deprecated/reorg-new.ps1"},
    @{src="reorg-new.sh"; dst="_archive/deprecated/reorg-new.sh"},
    @{src="reorg-phase2.ps1"; dst="_archive/deprecated/reorg-phase2.ps1"},
    @{src="reorg-simple.ps1"; dst="_archive/deprecated/reorg-simple.ps1"},
    @{src="undo-reorg.ps1"; dst="_archive/deprecated/undo-reorg.ps1"},
    @{src="undo-reorg.sh"; dst="_archive/deprecated/undo-reorg.sh"},
    @{src="test_weekly_extraction.py"; dst="utils/tests/test-weekly-extraction.py"},
    @{src=".gitignore_new"; dst="_archive/misc/gitignore-new"}
)

foreach ($item in $cleanup) {
    if (Test-Path $item.src) {
        if ($Mode -eq "--apply") {
            $destDir = Split-Path $item.dst -Parent
            New-Item -ItemType Directory -Path $destDir -Force -ErrorAction SilentlyContinue | Out-Null
            Move-Item -Path $item.src -Destination $item.dst -Force -ErrorAction SilentlyContinue
            Write-Host "  Moved: $($item.src) -> $($item.dst)" -ForegroundColor Green
        } else {
            Write-Host "  Would move: $($item.src) -> $($item.dst)" -ForegroundColor Yellow
        }
    }
}

# Move index folder
if (Test-Path "index") {
    if ($Mode -eq "--apply") {
        Move-Item -Path "index" -Destination "docs/index" -Force -ErrorAction SilentlyContinue
        Write-Host "  Moved: index -> docs/index" -ForegroundColor Green
    } else {
        Write-Host "  Would move: index -> docs/index" -ForegroundColor Yellow
    }
}

# Clean up remaining 01_trading_system items
if (Test-Path "01_trading_system") {
    $remaining = Get-ChildItem "01_trading_system" -File -ErrorAction SilentlyContinue
    foreach ($file in $remaining) {
        $dest = "agents/core/$($file.Name)"
        if ($Mode -eq "--apply") {
            Move-Item -Path $file.FullName -Destination $dest -Force -ErrorAction SilentlyContinue
            Write-Host "  Moved: $($file.Name) -> agents/core" -ForegroundColor Green
        } else {
            Write-Host "  Would move: $($file.Name) -> agents/core" -ForegroundColor Yellow
        }
    }

    # Try to remove remaining directories
    if ($Mode -eq "--apply") {
        Get-ChildItem "01_trading_system" -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            if ((Get-ChildItem $_.FullName -Force | Measure-Object).Count -eq 0) {
                Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
            }
        }

        if ((Get-ChildItem "01_trading_system" -Force | Measure-Object).Count -eq 0) {
            Remove-Item "01_trading_system" -Force -ErrorAction SilentlyContinue
            Write-Host "  Removed empty directory: 01_trading_system" -ForegroundColor Gray
        }
    }
}

# Clean up 02_data if empty
if (Test-Path "02_data") {
    if ($Mode -eq "--apply") {
        $items = Get-ChildItem "02_data" -Force -ErrorAction SilentlyContinue
        if ($items.Count -eq 0) {
            Remove-Item "02_data" -Force -ErrorAction SilentlyContinue
            Write-Host "  Removed empty directory: 02_data" -ForegroundColor Gray
        } else {
            # Move any remaining misc items
            Get-ChildItem "02_data" -Recurse -File | ForEach-Object {
                $dest = "_archive/misc/02_data_$($_.Name)"
                Move-Item -Path $_.FullName -Destination $dest -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

# Remove empty directories
if ($Mode -eq "--apply") {
    $emptyDirs = Get-ChildItem -Directory -Recurse |
                 Where-Object { (Get-ChildItem $_.FullName -Force -ErrorAction SilentlyContinue | Measure-Object).Count -eq 0 } |
                 Sort-Object -Property FullName -Descending

    foreach ($dir in $emptyDirs) {
        Remove-Item $dir.FullName -Force -ErrorAction SilentlyContinue
        Write-Host "  Removed empty: $($dir.Name)" -ForegroundColor Gray
    }
}

Write-Host "`nCleanup Summary:" -ForegroundColor Cyan
if ($Mode -eq "--dry-run") {
    Write-Host "  DRY RUN - No changes made" -ForegroundColor Yellow
    Write-Host "  To apply: .\reorg-cleanup.ps1 --apply" -ForegroundColor Yellow
} else {
    Write-Host "  Cleanup complete!" -ForegroundColor Green

    # Final structure check
    Write-Host "`nFinal Root Directory:" -ForegroundColor Cyan
    Get-ChildItem -Name | ForEach-Object {
        if ($_ -match "^\..*$|^main\.py$|^README\.md$|^agents$|^configs$|^scripts-and-data$|^research$|^docs$|^frontend$|^backtests$|^risk$|^utils$|^logs$|^_archive$") {
            Write-Host "  OK $_" -ForegroundColor Green
        } else {
            Write-Host "  ? $_" -ForegroundColor Yellow
        }
    }
}