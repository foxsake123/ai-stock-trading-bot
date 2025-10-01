@echo off
echo ============================================
echo SETTING UP TUESDAY AUTOMATION
echo ============================================

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run as Administrator
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

echo.
echo Creating automated task for Tuesday execution...

REM Create task for Tuesday 9:30 AM execution
schtasks /create /tn "AI Trading Bot - Tuesday Execution" /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\execute_daily_trades.py" /sc once /st 09:30 /sd 10/01/2025 /f

echo.
echo Task created for Tuesday, October 1, 2025 at 9:30 AM

echo.
echo ============================================
echo SETUP COMPLETE
echo ============================================
echo.
echo Tuesday trades will execute automatically at 9:30 AM
echo No manual action required!
echo.
pause