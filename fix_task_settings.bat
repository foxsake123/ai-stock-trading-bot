@echo off
REM Fix Task Scheduler settings to enable wake-from-sleep and proper execution
REM Run as Administrator

echo ================================================================================
echo FIXING TASK SCHEDULER SETTINGS
echo ================================================================================
echo.
echo This will fix all "AI Trading" tasks to:
echo   1. Wake computer from sleep
echo   2. Run whether user is logged on or not
echo   3. Run with highest privileges
echo.
pause

REM Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] This script requires Administrator privileges
    echo Right-click fix_task_settings.bat and select "Run as administrator"
    pause
    exit /b 1
)

echo [OK] Running as Administrator
echo.

set "PYTHON_EXE=C:\Python313\python.exe"
set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

echo Fixing task settings...
echo.

REM ============================================================================
REM FIX TASK 1: Weekend Research
REM ============================================================================

echo [1/4] Fixing Weekend Research task...

schtasks /Delete /TN "AI Trading - Weekend Research" /F >nul 2>&1

schtasks /Create /TN "AI Trading - Weekend Research" ^
    /TR "\"%PYTHON_EXE%\" \"%PROJECT_DIR%\scripts\automation\daily_claude_research.py\" --force" ^
    /SC WEEKLY /D SAT /ST 12:00 /F /RL HIGHEST ^
    /RU "%USERNAME%" /IT

if %errorlevel% equ 0 (
    echo [OK] Weekend Research configured
) else (
    echo [ERROR] Failed to configure Weekend Research
)

REM Enable wake-from-sleep
powershell -Command "$task = Get-ScheduledTask -TaskName 'AI Trading - Weekend Research'; $task.Settings.WakeToRun = $true; Set-ScheduledTask -InputObject $task" >nul 2>&1

echo.

REM ============================================================================
REM FIX TASK 2: Morning Trade Generation
REM ============================================================================

echo [2/4] Fixing Morning Trade Generation task...

schtasks /Delete /TN "AI Trading - Morning Trade Generation" /F >nul 2>&1

schtasks /Create /TN "AI Trading - Morning Trade Generation" ^
    /TR "\"%PYTHON_EXE%\" \"%PROJECT_DIR%\scripts\automation\generate_todays_trades_v2.py\"" ^
    /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 08:30 /F /RL HIGHEST ^
    /RU "%USERNAME%" /IT

if %errorlevel% equ 0 (
    echo [OK] Morning Trade Generation configured
) else (
    echo [ERROR] Failed to configure Morning Trade Generation
)

REM Enable wake-from-sleep
powershell -Command "$task = Get-ScheduledTask -TaskName 'AI Trading - Morning Trade Generation'; $task.Settings.WakeToRun = $true; Set-ScheduledTask -InputObject $task" >nul 2>&1

echo.

REM ============================================================================
REM FIX TASK 3: Trade Execution
REM ============================================================================

echo [3/4] Fixing Trade Execution task...

schtasks /Delete /TN "AI Trading - Trade Execution" /F >nul 2>&1

schtasks /Create /TN "AI Trading - Trade Execution" ^
    /TR "\"%PYTHON_EXE%\" \"%PROJECT_DIR%\scripts\automation\execute_daily_trades.py\"" ^
    /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 09:30 /F /RL HIGHEST ^
    /RU "%USERNAME%" /IT

if %errorlevel% equ 0 (
    echo [OK] Trade Execution configured
) else (
    echo [ERROR] Failed to configure Trade Execution
)

REM Enable wake-from-sleep
powershell -Command "$task = Get-ScheduledTask -TaskName 'AI Trading - Trade Execution'; $task.Settings.WakeToRun = $true; Set-ScheduledTask -InputObject $task" >nul 2>&1

echo.

REM ============================================================================
REM FIX TASK 4: Performance Graph
REM ============================================================================

echo [4/4] Fixing Performance Graph task...

schtasks /Delete /TN "AI Trading - Daily Performance Graph" /F >nul 2>&1

schtasks /Create /TN "AI Trading - Daily Performance Graph" ^
    /TR "\"%PYTHON_EXE%\" \"%PROJECT_DIR%\scripts\performance\generate_performance_graph.py\"" ^
    /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 16:30 /F /RL HIGHEST ^
    /RU "%USERNAME%" /IT

if %errorlevel% equ 0 (
    echo [OK] Performance Graph configured
) else (
    echo [ERROR] Failed to configure Performance Graph
)

REM Enable wake-from-sleep
powershell -Command "$task = Get-ScheduledTask -TaskName 'AI Trading - Daily Performance Graph'; $task.Settings.WakeToRun = $true; Set-ScheduledTask -InputObject $task" >nul 2>&1

echo.

REM ============================================================================
REM VERIFICATION
REM ============================================================================

echo ================================================================================
echo VERIFICATION
echo ================================================================================
echo.

python "%PROJECT_DIR%\diagnose_automation.py"

echo.
echo ================================================================================
echo NEXT STEPS
echo ================================================================================
echo.
echo 1. Configure Windows Power Settings:
echo    - Open Settings -^> System -^> Power ^& Sleep
echo    - Set "When plugged in, PC goes to sleep after" to NEVER
echo.
echo 2. Test weekend research generation:
echo    python scripts\automation\daily_claude_research.py --force
echo.
echo 3. Verify tasks will wake computer:
echo    - Task Scheduler should now show "Wake the computer to run this task: Yes"
echo.
pause
