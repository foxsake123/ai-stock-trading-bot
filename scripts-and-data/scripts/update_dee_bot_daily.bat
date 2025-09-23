@echo off
REM Daily DEE-BOT Position Update Script
REM Runs at 4:00 PM ET daily to sync positions from Alpaca

echo ========================================
echo DEE-BOT DAILY POSITION UPDATE
echo ========================================
echo.

REM Navigate to the automation directory
cd /d C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation

REM Run the update script
python update_dee_bot_positions_daily.py

REM Check if successful
if %errorlevel% == 0 (
    echo.
    echo SUCCESS: DEE-BOT positions updated
) else (
    echo.
    echo ERROR: Failed to update DEE-BOT positions
    echo Check logs at: C:\Users\shorg\ai-stock-trading-bot\09_logs\dee_bot_errors.log
)

echo.
echo ========================================
echo Update completed at %date% %time%
echo ========================================

REM Keep window open for 5 seconds to see results
timeout /t 5 >nul