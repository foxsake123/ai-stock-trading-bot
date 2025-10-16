@echo off
REM =============================================================================
REM AI Trading Bot - Task Scheduler Setup
REM Creates Windows scheduled tasks for automated trading pipeline
REM =============================================================================

echo ========================================================================
echo AI TRADING BOT - TASK SCHEDULER SETUP
echo ========================================================================
echo.
echo This script will create 4 scheduled tasks:
echo   1. Evening Research (6:00 PM daily) - Generate Claude research
echo   2. Evening Health Check (6:30 PM daily) - Verify research completed
echo   3. Morning Trade Generation (8:30 AM daily) - Generate trade recommendations
echo   4. Trade Execution (9:30 AM daily) - Execute approved trades
echo.
echo Press Ctrl+C to cancel, or
pause

REM Get Python path
set PYTHON_PATH=python
set PROJECT_ROOT=%~dp0..\..

echo.
echo [1/5] Creating Evening Research Task (6:00 PM)...
echo.

schtasks /create /tn "AI Trading - Evening Research" /tr "%PYTHON_PATH% %PROJECT_ROOT%\scripts\automation\daily_claude_research.py" /sc daily /st 18:00 /ru "%USERNAME%" /rl HIGHEST /f

if %ERRORLEVEL% EQU 0 (
    echo [OK] Evening Research task created successfully
) else (
    echo [ERROR] Failed to create Evening Research task
    goto :error
)

echo.
echo [2/5] Creating Evening Health Check Task (6:30 PM)...
echo.

schtasks /create /tn "AI Trading - Evening Health Check" /tr "%PYTHON_PATH% %PROJECT_ROOT%\scripts\monitoring\pipeline_health_monitor.py --check research" /sc daily /st 18:30 /ru "%USERNAME%" /rl HIGHEST /f

if %ERRORLEVEL% EQU 0 (
    echo [OK] Evening Health Check task created successfully
) else (
    echo [ERROR] Failed to create Evening Health Check task
    goto :error
)

echo.
echo [3/5] Creating Morning Trade Generation Task (8:30 AM)...
echo.

schtasks /create /tn "AI Trading - Morning Trade Generation" /tr "%PYTHON_PATH% %PROJECT_ROOT%\scripts\automation\generate_todays_trades_v2.py" /sc daily /st 08:30 /ru "%USERNAME%" /rl HIGHEST /f

if %ERRORLEVEL% EQU 0 (
    echo [OK] Morning Trade Generation task created successfully
) else (
    echo [ERROR] Failed to create Morning Trade Generation task
    goto :error
)

echo.
echo [4/5] Creating Trade Execution Task (9:30 AM)...
echo.

schtasks /create /tn "AI Trading - Trade Execution" /tr "%PYTHON_PATH% %PROJECT_ROOT%\scripts\automation\execute_daily_trades.py" /sc daily /st 09:30 /ru "%USERNAME%" /rl HIGHEST /f

if %ERRORLEVEL% EQU 0 (
    echo [OK] Trade Execution task created successfully
) else (
    echo [ERROR] Failed to create Trade Execution task
    goto :error
)

echo.
echo [5/5] Creating Morning Health Check Task (9:00 AM)...
echo.

schtasks /create /tn "AI Trading - Morning Health Check" /tr "%PYTHON_PATH% %PROJECT_ROOT%\scripts\monitoring\pipeline_health_monitor.py --check trades" /sc daily /st 09:00 /ru "%USERNAME%" /rl HIGHEST /f

if %ERRORLEVEL% EQU 0 (
    echo [OK] Morning Health Check task created successfully
) else (
    echo [ERROR] Failed to create Morning Health Check task
    goto :error
)

echo.
echo ========================================================================
echo SETUP COMPLETE
echo ========================================================================
echo.
echo All 5 scheduled tasks created successfully!
echo.
echo Daily Schedule:
echo   6:00 PM - Generate Claude research for tomorrow
echo   6:30 PM - Check research file exists (alert if missing)
echo   8:30 AM - Generate trade recommendations
echo   9:00 AM - Check trades file exists (alert if missing)
echo   9:30 AM - Execute approved trades
echo.
echo To verify tasks were created:
echo   schtasks /query /tn "AI Trading*"
echo.
echo To disable a task:
echo   schtasks /change /tn "AI Trading - Evening Research" /disable
echo.
echo To enable a task:
echo   schtasks /change /tn "AI Trading - Evening Research" /enable
echo.
echo To delete all tasks:
echo   scripts\automation\remove_task_scheduler.bat
echo.
echo ========================================================================
goto :end

:error
echo.
echo ========================================================================
echo ERROR: Task creation failed
echo ========================================================================
echo.
echo Troubleshooting:
echo   1. Run this script as Administrator
echo   2. Verify Python is in PATH: python --version
echo   3. Check project path is correct: %PROJECT_ROOT%
echo   4. Review error message above
echo.
exit /b 1

:end
exit /b 0
