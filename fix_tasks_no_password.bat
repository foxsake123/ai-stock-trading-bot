@echo off
REM Fix Task Scheduler - No Password Required Version
REM Uses "Run only when user is logged on" mode
REM Computer must be on and unlocked, but no password needed

echo ================================================================================
echo FIXING TASK SCHEDULER - NO PASSWORD VERSION
echo ================================================================================
echo.
echo This version uses "Run only when user is logged on"
echo   - No password required
echo   - Computer must be on and unlocked
echo   - You must stay logged in
echo.
pause

REM Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] This script requires Administrator privileges
    echo Right-click fix_tasks_no_password.bat and select "Run as administrator"
    pause
    exit /b 1
)

echo [OK] Running as Administrator
echo.

set "PYTHON_EXE=C:\Python313\python.exe"
set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

echo [INFO] Python executable: %PYTHON_EXE%
echo [INFO] Project directory: %PROJECT_DIR%
echo.

REM ============================================================================
REM TASK 1: Weekend Research
REM ============================================================================

echo [1/4] Creating Weekend Research task...

schtasks /Delete /TN "AI Trading - Weekend Research" /F >nul 2>&1

schtasks /Create /TN "AI Trading - Weekend Research" ^
    /TR "\"%PYTHON_EXE%\" \"%PROJECT_DIR%\scripts\automation\daily_claude_research.py\" --force" ^
    /SC WEEKLY /D SAT /ST 12:00 /F

if %errorlevel% equ 0 (
    echo [OK] Weekend Research task created
) else (
    echo [ERROR] Failed to create Weekend Research task
)
echo.

REM ============================================================================
REM TASK 2: Morning Trade Generation
REM ============================================================================

echo [2/4] Creating Morning Trade Generation task...

schtasks /Delete /TN "AI Trading - Morning Trade Generation" /F >nul 2>&1

schtasks /Create /TN "AI Trading - Morning Trade Generation" ^
    /TR "\"%PYTHON_EXE%\" \"%PROJECT_DIR%\scripts\automation\generate_todays_trades_v2.py\"" ^
    /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 08:30 /F

if %errorlevel% equ 0 (
    echo [OK] Morning Trade Generation task created
) else (
    echo [ERROR] Failed to create Morning Trade Generation task
)
echo.

REM ============================================================================
REM TASK 3: Trade Execution
REM ============================================================================

echo [3/4] Creating Trade Execution task...

schtasks /Delete /TN "AI Trading - Trade Execution" /F >nul 2>&1

schtasks /Create /TN "AI Trading - Trade Execution" ^
    /TR "\"%PYTHON_EXE%\" \"%PROJECT_DIR%\scripts\automation\execute_daily_trades.py\"" ^
    /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 09:30 /F

if %errorlevel% equ 0 (
    echo [OK] Trade Execution task created
) else (
    echo [ERROR] Failed to create Trade Execution task
)
echo.

REM ============================================================================
REM TASK 4: Performance Graph
REM ============================================================================

echo [4/4] Creating Performance Graph task...

schtasks /Delete /TN "AI Trading - Daily Performance Graph" /F >nul 2>&1

schtasks /Create /TN "AI Trading - Daily Performance Graph" ^
    /TR "\"%PYTHON_EXE%\" \"%PROJECT_DIR%\scripts\performance\generate_performance_graph.py\"" ^
    /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 16:30 /F

if %errorlevel% equ 0 (
    echo [OK] Performance Graph task created
) else (
    echo [ERROR] Failed to create Performance Graph task
)
echo.

echo ================================================================================
echo CONFIGURING WAKE-FROM-SLEEP VIA POWERSHELL
echo ================================================================================
echo.

REM Enable wake-from-sleep for each task using PowerShell
echo [1/4] Configuring Weekend Research...
powershell -Command "try { $task = Get-ScheduledTask -TaskName 'AI Trading - Weekend Research' -ErrorAction Stop; $task.Settings.WakeToRun = $true; $task.Settings.DisallowStartIfOnBatteries = $false; $task.Settings.StopIfGoingOnBatteries = $false; Set-ScheduledTask -InputObject $task -ErrorAction Stop; Write-Host '[OK] Wake-to-run enabled' } catch { Write-Host '[WARNING] Could not set wake option via PowerShell' }"
echo.

echo [2/4] Configuring Morning Trade Generation...
powershell -Command "try { $task = Get-ScheduledTask -TaskName 'AI Trading - Morning Trade Generation' -ErrorAction Stop; $task.Settings.WakeToRun = $true; $task.Settings.DisallowStartIfOnBatteries = $false; $task.Settings.StopIfGoingOnBatteries = $false; Set-ScheduledTask -InputObject $task -ErrorAction Stop; Write-Host '[OK] Wake-to-run enabled' } catch { Write-Host '[WARNING] Could not set wake option via PowerShell' }"
echo.

echo [3/4] Configuring Trade Execution...
powershell -Command "try { $task = Get-ScheduledTask -TaskName 'AI Trading - Trade Execution' -ErrorAction Stop; $task.Settings.WakeToRun = $true; $task.Settings.DisallowStartIfOnBatteries = $false; $task.Settings.StopIfGoingOnBatteries = $false; Set-ScheduledTask -InputObject $task -ErrorAction Stop; Write-Host '[OK] Wake-to-run enabled' } catch { Write-Host '[WARNING] Could not set wake option via PowerShell' }"
echo.

echo [4/4] Configuring Performance Graph...
powershell -Command "try { $task = Get-ScheduledTask -TaskName 'AI Trading - Daily Performance Graph' -ErrorAction Stop; $task.Settings.WakeToRun = $true; $task.Settings.DisallowStartIfOnBatteries = $false; $task.Settings.StopIfGoingOnBatteries = $false; Set-ScheduledTask -InputObject $task -ErrorAction Stop; Write-Host '[OK] Wake-to-run enabled' } catch { Write-Host '[WARNING] Could not set wake option via PowerShell' }"
echo.

echo ================================================================================
echo VERIFICATION
echo ================================================================================
echo.

python "%PROJECT_DIR%\diagnose_automation.py"

echo.
echo ================================================================================
echo IMPORTANT NOTES
echo ================================================================================
echo.
echo Tasks created in "Run only when user is logged on" mode:
echo   - No password required (easier setup)
echo   - Computer must be ON and UNLOCKED
echo   - You must be LOGGED IN for tasks to run
echo.
echo If PowerShell wake commands failed, you need to manually:
echo   1. Open Task Scheduler (taskschd.msc)
echo   2. For each "AI Trading" task, right-click -^> Properties
echo   3. Conditions tab: Check "Wake the computer to run this task"
echo   4. Conditions tab: Uncheck "Start only if on AC power"
echo   5. Click OK (no password needed since we use "logged on" mode)
echo.
echo NEXT STEPS:
echo   1. Configure Windows power: Settings -^> Power ^& Sleep -^> Never
echo   2. Generate research: python scripts\automation\daily_claude_research.py --force
echo   3. Keep computer on and logged in during trading hours
echo.
pause
