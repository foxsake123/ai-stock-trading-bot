@echo off
REM Setup Windows Task Scheduler for Complete Trading Automation
REM Runs on US market trading days only (excludes weekends and holidays)

echo ========================================
echo  AI Trading Bot - Complete Automation
echo  Task Scheduler Setup
echo ========================================
echo.

REM Get Python path
set PYTHON_PATH=C:\Python313\python.exe
set BOT_DIR=C:\Users\shorg\ai-stock-trading-bot

echo Checking Python installation...
%PYTHON_PATH% --version
if errorlevel 1 (
    echo ERROR: Python not found at %PYTHON_PATH%
    echo Please update PYTHON_PATH in this script
    pause
    exit /b 1
)

echo.
echo Creating Task Scheduler entries for trading automation...
echo.

REM =============================================================================
REM TASK 1: Evening Research Generation (6:00 PM ET daily)
REM =============================================================================
echo [1/4] Evening Research Generation (6:00 PM ET)...
schtasks /create ^
    /tn "AI Trading - Evening Research" ^
    /tr "%PYTHON_PATH% %BOT_DIR%\scripts\automation\daily_claude_research.py" ^
    /sc daily ^
    /st 18:00 ^
    /ru SYSTEM ^
    /f

if errorlevel 1 (
    echo ERROR: Failed to create Evening Research task
    pause
    exit /b 1
)
echo SUCCESS: Evening Research task created

echo.

REM =============================================================================
REM TASK 2: Morning Trade Generation (8:30 AM ET weekdays)
REM =============================================================================
echo [2/4] Morning Trade Generation (8:30 AM ET)...
schtasks /create ^
    /tn "AI Trading - Morning Trade Generation" ^
    /tr "%PYTHON_PATH% %BOT_DIR%\scripts\automation\generate_todays_trades_v2.py" ^
    /sc weekly ^
    /d MON,TUE,WED,THU,FRI ^
    /st 08:30 ^
    /ru SYSTEM ^
    /f

if errorlevel 1 (
    echo ERROR: Failed to create Morning Trade Generation task
    pause
    exit /b 1
)
echo SUCCESS: Morning Trade Generation task created

echo.

REM =============================================================================
REM TASK 3: Trade Execution (9:30 AM ET weekdays)
REM =============================================================================
echo [3/4] Trade Execution (9:30 AM ET)...
schtasks /create ^
    /tn "AI Trading - Trade Execution" ^
    /tr "%PYTHON_PATH% %BOT_DIR%\scripts\automation\execute_daily_trades.py" ^
    /sc weekly ^
    /d MON,TUE,WED,THU,FRI ^
    /st 09:30 ^
    /ru SYSTEM ^
    /f

if errorlevel 1 (
    echo ERROR: Failed to create Trade Execution task
    pause
    exit /b 1
)
echo SUCCESS: Trade Execution task created

echo.

REM =============================================================================
REM TASK 4: Performance Graph (4:30 PM ET weekdays)
REM =============================================================================
echo [4/4] Daily Performance Graph (4:30 PM ET)...
schtasks /create ^
    /tn "AI Trading - Daily Performance Graph" ^
    /tr "%PYTHON_PATH% %BOT_DIR%\scripts\performance\generate_performance_graph.py" ^
    /sc weekly ^
    /d MON,TUE,WED,THU,FRI ^
    /st 16:30 ^
    /ru SYSTEM ^
    /f

if errorlevel 1 (
    echo ERROR: Failed to create Performance Graph task
    pause
    exit /b 1
)
echo SUCCESS: Performance Graph task created

echo.
echo ========================================
echo  SUCCESS - All Tasks Created!
echo ========================================
echo.
echo Scheduled Tasks:
echo   1. Evening Research:      6:00 PM ET (daily)
echo   2. Trade Generation:      8:30 AM ET (weekdays)
echo   3. Trade Execution:       9:30 AM ET (weekdays)
echo   4. Performance Graph:     4:30 PM ET (weekdays)
echo.
echo Next Trading Day Schedule:
echo   6:00 PM (tonight):  Research generation for tomorrow
echo   8:30 AM (tomorrow): Generate trades from research
echo   9:30 AM (tomorrow): Execute approved trades
echo   4:30 PM (tomorrow): Update performance graph
echo.
echo To verify tasks:
echo   schtasks /query /tn "AI Trading - Evening Research"
echo   schtasks /query /tn "AI Trading - Morning Trade Generation"
echo   schtasks /query /tn "AI Trading - Trade Execution"
echo   schtasks /query /tn "AI Trading - Daily Performance Graph"
echo.
echo To run tasks manually now (testing):
echo   schtasks /run /tn "AI Trading - Evening Research"
echo   schtasks /run /tn "AI Trading - Morning Trade Generation"
echo   schtasks /run /tn "AI Trading - Trade Execution"
echo   schtasks /run /tn "AI Trading - Daily Performance Graph"
echo.
echo To remove all tasks:
echo   scripts\windows\remove_trade_automation.bat
echo.
pause
