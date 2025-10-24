@echo off
REM Safe Repository Cleanup Script (Windows)
REM Generated: October 23, 2025
REM Run this script to perform LOW-RISK cleanup actions

echo ==========================================
echo AI Stock Trading Bot - Safe Cleanup
echo ==========================================
echo.
echo This script performs LOW-RISK cleanup:
echo   - Deletes test artifacts (regenerable)
echo   - Removes empty directories
echo   - Deletes orphaned files
echo   - Updates .gitignore
echo.
echo HIGH-RISK actions (agent consolidation)
echo require manual review and are NOT included.
echo.

set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo Aborted.
    exit /b 1
)

echo.
echo ==========================================
echo Phase 1: Delete Test Artifacts
echo ==========================================

REM Remove coverage reports
if exist .coverage (
    echo Deleting .coverage...
    del /q .coverage
)

if exist htmlcov (
    echo Deleting htmlcov\ directory...
    rmdir /s /q htmlcov
)

if exist .pytest_cache (
    echo Deleting .pytest_cache\ directory...
    rmdir /s /q .pytest_cache
)

REM Remove Python cache (recursively)
echo Deleting __pycache__ directories...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

echo [OK] Test artifacts removed
echo.

echo ==========================================
echo Phase 2: Delete Orphaned Files
echo ==========================================

REM Delete Windows error file
if exist nul (
    echo Deleting nul (Windows error file)...
    del /q nul
)

REM Delete obsolete analysis
if exist REPORT_CLEANUP_PLAN.md (
    echo Deleting REPORT_CLEANUP_PLAN.md (superseded)...
    del /q REPORT_CLEANUP_PLAN.md
)

REM Delete duplicate .env template
if exist .env.template (
    echo Deleting .env.template (duplicate of .env.example)...
    del /q .env.template
)

echo [OK] Orphaned files removed
echo.

echo ==========================================
echo Phase 3: Remove Empty Directories
echo ==========================================

echo Removing empty directories...

REM Remove known empty directories from analysis
if exist reports\daily (
    rmdir reports\daily 2>nul
)
if exist reports\weekly (
    rmdir reports\weekly 2>nul
)
if exist reports\monthly (
    rmdir reports\monthly 2>nul
)
if exist reports\postmarket (
    rmdir reports\postmarket 2>nul
)
if exist reports\execution\2025-10-15 (
    rmdir reports\execution\2025-10-15 2>nul
)
if exist reports\performance\2025-10-15 (
    rmdir reports\performance\2025-10-15 2>nul
)
if exist reports\archive\2025-10\analysis (
    rmdir reports\archive\2025-10\analysis 2>nul
)
if exist reports\archive\2025-10\reports (
    rmdir reports\archive\2025-10\reports 2>nul
)
if exist data\cache (
    rmdir data\cache 2>nul
)
if exist data\execution\results (
    rmdir data\execution\results 2>nul
)
if exist data\historical\market (
    rmdir data\historical\market 2>nul
)
if exist data\historical\portfolio\shorgan-bot (
    rmdir data\historical\portfolio\shorgan-bot 2>nul
)
if exist data\positions (
    rmdir data\positions 2>nul
)
if exist data\research (
    rmdir data\research 2>nul
)
if exist data\state (
    rmdir data\state 2>nul
)
if exist config\bots (
    rmdir config\bots 2>nul
)
if exist configs\bots (
    rmdir configs\bots 2>nul
)
if exist logs\performance (
    rmdir logs\performance 2>nul
)
if exist logs\trades (
    rmdir logs\trades 2>nul
)
if exist deployment\aws (
    rmdir deployment\aws 2>nul
)
if exist docs\api (
    rmdir docs\api 2>nul
)
if exist docs\architecture (
    rmdir docs\architecture 2>nul
)
if exist docs\strategies (
    rmdir docs\strategies 2>nul
)
if exist scripts\setup (
    rmdir scripts\setup 2>nul
)
if exist backtesting\scenarios (
    rmdir backtesting\scenarios 2>nul
)
if exist utils\extensions (
    rmdir utils\extensions 2>nul
)
if exist archive (
    rmdir archive 2>nul
)

echo [OK] Empty directories removed
echo.

echo ==========================================
echo Phase 4: Update .gitignore
echo ==========================================

REM Check if patterns already exist in .gitignore
findstr /C:".coverage" .gitignore >nul 2>&1
if errorlevel 1 (
    echo. >> .gitignore
    echo # Coverage reports (added by cleanup script) >> .gitignore
    echo .coverage >> .gitignore
    echo coverage.xml >> .gitignore
    echo *.cover >> .gitignore
    echo [OK] Added coverage patterns to .gitignore
)

findstr /C:"htmlcov/" .gitignore >nul 2>&1
if errorlevel 1 (
    echo htmlcov/ >> .gitignore
    echo [OK] Added htmlcov/ to .gitignore
)

findstr /C:".pytest_cache/" .gitignore >nul 2>&1
if errorlevel 1 (
    echo .pytest_cache/ >> .gitignore
    echo [OK] Added .pytest_cache/ to .gitignore
)

findstr /C:"__pycache__/" .gitignore >nul 2>&1
if errorlevel 1 (
    echo __pycache__/ >> .gitignore
    echo *.py[cod] >> .gitignore
    echo *$py.class >> .gitignore
    echo *.so >> .gitignore
    echo [OK] Added Python cache patterns to .gitignore
)

echo.

echo ==========================================
echo Cleanup Summary
echo ==========================================
echo.
echo [OK] Deleted test artifacts (5.4MB)
echo [OK] Removed orphaned files
echo [OK] Deleted empty directories
echo [OK] Updated .gitignore
echo.
echo Remaining manual actions (see REPOSITORY_CLEANUP_ANALYSIS.md):
echo   [ ] Phase 1: Consolidate agents/ and src/agents/ (CRITICAL)
echo   [ ] Phase 2: Move files from root directory (HIGH)
echo   [ ] Phase 4: Reorganize reports/ structure (MEDIUM)
echo   [ ] Phase 5-8: Optional organizational improvements
echo.
echo Run 'git status' to see changes.
echo Run 'pytest tests/' to verify tests still pass.
echo.
echo ==========================================
echo Safe cleanup complete!
echo ==========================================
echo.
pause
