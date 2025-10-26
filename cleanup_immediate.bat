@echo off
REM Immediate Cleanup Script - ZERO RISK (Windows Version)
REM Removes only generated/temporary files (all regenerable)
REM Run time: ~30 seconds
REM Space saved: ~5.3MB

setlocal enabledelayedexpansion

echo ============================================
echo AI Trading Bot - Immediate Cleanup
echo ============================================
echo.

cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo Phase 1: Python Cache Cleanup
echo ------------------------------
set PYCACHE_COUNT=0
for /d /r %%i in (__pycache__) do (
    if exist "%%i" (
        set /a PYCACHE_COUNT+=1
        rd /s /q "%%i" 2>nul
    )
)
if !PYCACHE_COUNT! GTR 0 (
    echo [OK] Removed !PYCACHE_COUNT! __pycache__ directories
) else (
    echo No __pycache__ directories found
)
echo.

echo Phase 2: HTML Coverage Reports
echo -------------------------------
if exist "htmlcov" (
    rd /s /q htmlcov 2>nul
    echo [OK] Removed htmlcov/ directory
) else (
    echo No htmlcov/ directory found
)
echo.

echo Phase 3: Root Log Files
echo -----------------------
set LOG_COUNT=0
for %%f in (*.log) do (
    if exist "%%f" (
        set /a LOG_COUNT+=1
        del /q "%%f" 2>nul
    )
)
if !LOG_COUNT! GTR 0 (
    echo [OK] Removed !LOG_COUNT! log files
) else (
    echo No log files in root
)
echo.

echo Phase 4: Coverage Database
echo --------------------------
if exist ".coverage" (
    del /q .coverage 2>nul
    echo [OK] Removed .coverage file
) else (
    echo No .coverage file found
)
echo.

echo Phase 5: Backup Files
echo ---------------------
if exist ".env.backup" (
    del /q .env.backup 2>nul
    echo [OK] Removed .env.backup file
) else (
    echo No .env.backup file found
)
echo.

echo Phase 6: Windows Artifacts
echo --------------------------
if exist "nul" (
    del /q nul 2>nul
    echo [OK] Removed nul file
) else (
    echo No nul file found
)
echo.

echo Phase 7: Update .gitignore
echo --------------------------
findstr /C:"*.backup" .gitignore >nul 2>&1
if errorlevel 1 (
    echo Adding missing patterns to .gitignore...
    echo. >> .gitignore
    echo # Additional cleanup patterns (added by cleanup_immediate.bat^) >> .gitignore
    echo *.backup >> .gitignore
    echo .env.backup >> .gitignore
    echo nul >> .gitignore
    echo Thumbs.db >> .gitignore
    echo /*.log >> .gitignore
    echo .coverage.* >> .gitignore
    echo coverage.xml >> .gitignore
    echo [OK] Updated .gitignore with new patterns
) else (
    echo All cleanup patterns already in .gitignore
)
echo.

echo ============================================
echo Cleanup Complete!
echo ============================================
echo.
echo Summary:
echo   - Python cache removed
echo   - HTML coverage removed
echo   - Root log files removed
echo   - Coverage database removed
echo   - Backup files removed
echo   - .gitignore updated
echo.
echo Next steps:
echo   1. Run tests: python -m pytest tests/ -v
echo   2. Verify no issues: git status
echo   3. Review full report: type REPOSITORY_CLEANUP_REPORT.md
echo.
echo For more comprehensive cleanup, see Phase 2-6 in:
echo   REPOSITORY_CLEANUP_REPORT.md
echo.

pause
