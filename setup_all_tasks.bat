@echo off
REM Complete Task Scheduler Setup - Creates ALL 6 tasks from scratch
REM Run as Administrator

setlocal enabledelayedexpansion

echo ================================================================================
echo AI TRADING BOT - Complete Task Scheduler Setup
echo ================================================================================
echo.
echo This script will create 6 Windows Task Scheduler tasks from scratch:
echo   1. Weekend Research (Saturday 12 PM)
echo   2. Morning Trade Generation (Weekdays 8:30 AM)
echo   3. Trade Execution (Weekdays 9:30 AM)
echo   4. Performance Graph (Weekdays 4:30 PM)
echo   5. Stop Loss Monitor (Every 5 minutes during market hours)
echo   6. Profit Taking Manager (Hourly during market hours)
echo.
echo IMPORTANT: This script must be run as Administrator
echo.
pause

REM Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] This script requires Administrator privileges
    echo Right-click setup_all_tasks.bat and select "Run as administrator"
    pause
    exit /b 1
)

echo [OK] Running as Administrator
echo.

REM Set variables - CORRECTED PYTHON PATH
set "PYTHON_EXE=C:\Python313\python.exe"
set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

echo [INFO] Python executable: %PYTHON_EXE%
echo [INFO] Project directory: %PROJECT_DIR%
echo.

REM Verify Python exists
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found at %PYTHON_EXE%
    echo Please verify Python installation path
    pause
    exit /b 1
)

echo [OK] Python executable found
echo.

REM ============================================================================
REM TASK 1: Weekend Research (Saturday 12 PM)
REM ============================================================================

echo [1/6] Creating Weekend Research task...

REM Delete existing task if it exists
schtasks /Delete /TN "AI Trading - Weekend Research" /F >nul 2>&1

REM Create new task
schtasks /Create /TN "AI Trading - Weekend Research" /TR "\"%PYTHON_EXE%\" \"%PROJECT_DIR%\scripts\automation\daily_claude_research.py\" --force" /SC WEEKLY /D SAT /ST 12:00 /F /RL HIGHEST

if %errorlevel% equ 0 (
    echo [OK] Weekend Research task created
) else (
    echo [ERROR] Failed to create Weekend Research task
)
echo.

REM ============================================================================
REM TASK 2: Morning Trade Generation (Weekdays 8:30 AM)
REM ============================================================================

echo [2/6] Creating Morning Trade Generation task...

REM Delete existing task if it exists
schtasks /Delete /TN "AI Trading - Morning Trade Generation" /F >nul 2>&1

REM Create new task
schtasks /Create /TN "AI Trading - Morning Trade Generation" /TR "\"%PYTHON_EXE%\" \"%PROJECT_DIR%\scripts\automation\generate_todays_trades_v2.py\"" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 08:30 /F /RL HIGHEST

if %errorlevel% equ 0 (
    echo [OK] Morning Trade Generation task created
) else (
    echo [ERROR] Failed to create Morning Trade Generation task
)
echo.

REM ============================================================================
REM TASK 3: Trade Execution (Weekdays 9:30 AM)
REM ============================================================================

echo [3/6] Creating Trade Execution task...

REM Delete existing task if it exists
schtasks /Delete /TN "AI Trading - Trade Execution" /F >nul 2>&1

REM Create new task
schtasks /Create /TN "AI Trading - Trade Execution" /TR "\"%PYTHON_EXE%\" \"%PROJECT_DIR%\scripts\automation\execute_daily_trades.py\"" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 09:30 /F /RL HIGHEST

if %errorlevel% equ 0 (
    echo [OK] Trade Execution task created
) else (
    echo [ERROR] Failed to create Trade Execution task
)
echo.

REM ============================================================================
REM TASK 4: Performance Graph (Weekdays 4:30 PM)
REM ============================================================================

echo [4/6] Creating Performance Graph task...

REM Delete existing task if it exists
schtasks /Delete /TN "AI Trading - Daily Performance Graph" /F >nul 2>&1

REM Create new task
schtasks /Create /TN "AI Trading - Daily Performance Graph" /TR "\"%PYTHON_EXE%\" \"%PROJECT_DIR%\scripts\performance\generate_performance_graph.py\"" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 16:30 /F /RL HIGHEST

if %errorlevel% equ 0 (
    echo [OK] Performance Graph task created
) else (
    echo [ERROR] Failed to create Performance Graph task
)
echo.

REM ============================================================================
REM TASK 5: Stop Loss Monitor (Every 5 minutes during market hours)
REM ============================================================================

echo [5/6] Creating Stop Loss Monitor task...

REM Delete existing task if it exists
schtasks /Delete /TN "AI Trading - Stop Loss Monitor" /F >nul 2>&1

REM Create new task - runs every 5 minutes on weekdays
REM Note: The script itself checks if market is open
schtasks /Create /TN "AI Trading - Stop Loss Monitor" /TR "\"%PYTHON_EXE%\" \"%PROJECT_DIR%\scripts\automation\monitor_stop_losses.py\"" /SC MINUTE /MO 5 /ST 09:30 /ET 16:00 /F /RL HIGHEST

if %errorlevel% equ 0 (
    echo [OK] Stop Loss Monitor task created
) else (
    echo [ERROR] Failed to create Stop Loss Monitor task
)
echo.

REM ============================================================================
REM TASK 6: Profit Taking Manager (Hourly during market hours)
REM ============================================================================

echo [6/6] Creating Profit Taking Manager task...

REM Delete existing task if it exists
schtasks /Delete /TN "AI Trading - Profit Taking" /F >nul 2>&1

REM Create new task - runs hourly on weekdays
REM Note: The script itself checks if market is open
schtasks /Create /TN "AI Trading - Profit Taking" /TR "\"%PYTHON_EXE%\" \"%PROJECT_DIR%\scripts\automation\manage_profit_taking.py\"" /SC HOURLY /ST 09:30 /ET 16:30 /F /RL HIGHEST

if %errorlevel% equ 0 (
    echo [OK] Profit Taking task created
) else (
    echo [ERROR] Failed to create Profit Taking task
)
echo.

REM ============================================================================
REM VERIFICATION
REM ============================================================================

echo ================================================================================
echo VERIFICATION
echo ================================================================================
echo.

python "%PROJECT_DIR%\verify_tasks.py"

echo.
echo ================================================================================
echo SETUP COMPLETE
echo ================================================================================
echo.
echo All tasks should now be configured. Review the output above.
echo.
echo NEXT STEPS:
echo   1. Check that verify_tasks.py shows 6/6 tasks configured
echo   2. Open Task Scheduler GUI to view all tasks
echo   3. Test each task manually if desired
echo.
pause
