@echo off
REM Setup Windows Task Scheduler for Daily Performance Graph Generation
REM Runs at 4:30 PM ET daily (after market close)

echo ========================================
echo  AI Trading Bot - Performance Graph
echo  Task Scheduler Setup
echo ========================================
echo.

REM Get Python path
set PYTHON_PATH=C:\Python313\python.exe
set SCRIPT_PATH=C:\Users\shorg\ai-stock-trading-bot\scripts\performance\generate_performance_graph.py

echo Checking Python installation...
%PYTHON_PATH% --version
if errorlevel 1 (
    echo ERROR: Python not found at %PYTHON_PATH%
    echo Please update PYTHON_PATH in this script
    pause
    exit /b 1
)

echo.
echo Creating Task Scheduler entry...
echo Task: AI Trading - Daily Performance Graph
echo Time: 4:30 PM ET (16:30) daily
echo Script: %SCRIPT_PATH%
echo.

REM Create the scheduled task
schtasks /create ^
    /tn "AI Trading - Daily Performance Graph" ^
    /tr "%PYTHON_PATH% %SCRIPT_PATH%" ^
    /sc daily ^
    /st 16:30 ^
    /ru SYSTEM ^
    /f

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create scheduled task
    echo Try running this script as Administrator
    pause
    exit /b 1
)

echo.
echo ========================================
echo  SUCCESS - Task Scheduler Setup Complete
echo ========================================
echo.
echo The performance graph will now generate automatically at 4:30 PM ET daily
echo.
echo To verify the task was created:
echo   schtasks /query /tn "AI Trading - Daily Performance Graph"
echo.
echo To run the task manually now:
echo   schtasks /run /tn "AI Trading - Daily Performance Graph"
echo.
echo To delete the task:
echo   schtasks /delete /tn "AI Trading - Daily Performance Graph" /f
echo.
echo Graph will be saved to: performance_results.png
echo.
pause
