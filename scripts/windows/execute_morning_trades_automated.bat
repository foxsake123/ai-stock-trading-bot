@echo off
echo ============================================================
echo AUTOMATED MORNING TRADE EXECUTION
echo ============================================================
echo.
echo Starting automated trade execution at %date% %time%
echo.

cd /d "C:\Users\shorg\ai-stock-trading-bot"

echo Executing daily trades from TODAYS_TRADES file...
echo.

python scripts-and-data\automation\execute_daily_trades.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] All trades executed successfully
    echo.
) else (
    echo.
    echo [WARNING] Some trades failed - check execution logs
    echo.
)

echo Execution completed at %date% %time%
echo.

REM Optional: Send notification
echo Sending completion notification...
python scripts-and-data\automation\send_execution_notification.py

echo ============================================================
echo EXECUTION COMPLETE
echo ============================================================

pause