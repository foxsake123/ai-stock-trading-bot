@echo off
REM Execute Oct 8, 2025 Approved Trades
REM Automated execution with Telegram notifications

echo ================================================================================
echo AI TRADING BOT - AUTOMATED EXECUTION
echo October 8, 2025 - User Approved Orders
echo ================================================================================
echo.

cd /d %~dp0\..\..

echo Activating environment and executing trades...
echo.

python scripts\automation\execute_oct8_trades.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] All trades executed successfully
    echo Check Telegram for execution summary
) else (
    echo.
    echo [WARNING] Some trades may have failed
    echo Check logs and Telegram for details
)

echo.
echo Press any key to exit...
pause >nul
