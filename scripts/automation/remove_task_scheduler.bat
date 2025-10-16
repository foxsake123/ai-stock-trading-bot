@echo off
REM =============================================================================
REM AI Trading Bot - Remove Task Scheduler Tasks
REM Deletes all Windows scheduled tasks for the trading bot
REM =============================================================================

echo ========================================================================
echo AI TRADING BOT - REMOVE SCHEDULED TASKS
echo ========================================================================
echo.
echo This script will DELETE all AI Trading Bot scheduled tasks:
echo   - Evening Research (6:00 PM)
echo   - Evening Health Check (6:30 PM)
echo   - Morning Trade Generation (8:30 AM)
echo   - Morning Health Check (9:00 AM)
echo   - Trade Execution (9:30 AM)
echo.
echo WARNING: This cannot be undone!
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Removing tasks...
echo.

schtasks /delete /tn "AI Trading - Evening Research" /f 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Removed: Evening Research
) else (
    echo [SKIP] Evening Research task not found
)

schtasks /delete /tn "AI Trading - Evening Health Check" /f 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Removed: Evening Health Check
) else (
    echo [SKIP] Evening Health Check task not found
)

schtasks /delete /tn "AI Trading - Morning Trade Generation" /f 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Removed: Morning Trade Generation
) else (
    echo [SKIP] Morning Trade Generation task not found
)

schtasks /delete /tn "AI Trading - Morning Health Check" /f 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Removed: Morning Health Check
) else (
    echo [SKIP] Morning Health Check task not found
)

schtasks /delete /tn "AI Trading - Trade Execution" /f 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Removed: Trade Execution
) else (
    echo [SKIP] Trade Execution task not found
)

echo.
echo ========================================================================
echo REMOVAL COMPLETE
echo ========================================================================
echo.
echo All AI Trading Bot tasks have been removed from Task Scheduler.
echo.
echo To recreate tasks, run:
echo   scripts\automation\setup_task_scheduler.bat
echo.
echo ========================================================================

exit /b 0
