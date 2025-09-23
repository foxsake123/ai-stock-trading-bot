@echo off
REM Daily Performance Tracking Batch Script
REM Runs after market close at 4:15 PM ET

echo ========================================
echo DAILY PERFORMANCE TRACKING
echo ========================================
echo.

REM Navigate to project directory
cd /d "C:\Users\shorg\ai-stock-trading-bot\Performance_Tracking"

REM Activate virtual environment if exists
if exist "..\venv\Scripts\activate.bat" (
    call ..\venv\Scripts\activate.bat
)

REM Run the performance tracker
echo Running performance tracker...
python automated_performance_tracker.py --run-now

echo.
echo ========================================
echo PERFORMANCE TRACKING COMPLETE
echo ========================================

REM Keep window open for 5 seconds to see results
timeout /t 5 /nobreak > nul