@echo off
REM ================================================
REM TUESDAY SEPTEMBER 30, 2025 - 9:30 AM EXECUTION
REM Manual execution script if Task Scheduler fails
REM ================================================

echo ================================================
echo AI TRADING BOT - TUESDAY EXECUTION
echo Time: %DATE% %TIME%
echo ================================================
echo.

REM Navigate to project directory
cd /d C:\Users\shorg\ai-stock-trading-bot

echo [1/5] Checking system status...
python quick_check.py
echo.

echo [2/5] Verifying trades file exists...
if exist "docs\TODAYS_TRADES_2025-09-30.md" (
    echo [OK] Tuesday trades file found
    type "docs\TODAYS_TRADES_2025-09-30.md" | findstr /c:"Total Trades"
) else (
    echo [WARNING] No trades file, generating now...
    python scripts-and-data\automation\generate_todays_trades.py
)
echo.

echo [3/5] Starting execution with validation...
echo.
echo ================================================
echo EXECUTING TRADES WITH VALIDATION
echo Expected success rate: 85%+
echo ================================================
echo.

REM Execute trades
python scripts-and-data\automation\execute_daily_trades.py

echo.
echo ================================================
echo EXECUTION COMPLETE
echo ================================================
echo.

echo [4/5] Updating position files...
python scripts-and-data\automation\update_all_bot_positions.py
echo.

echo [5/5] Quick status check...
python scripts-and-data\automation\system_dashboard.py --quick
echo.

echo ================================================
echo TUESDAY EXECUTION FINISHED
echo Check trade logs for detailed results
echo ================================================
echo.

REM Show latest log file
echo Latest execution log:
dir scripts-and-data\trade-logs\*.json /b /o-d | head -1

echo.
pause