@echo off
REM Morning Trading Bot Execution Script
REM Runs at 9:30 AM ET via Windows Task Scheduler

echo ========================================
echo Starting Morning Trading Bot
echo Time: %DATE% %TIME%
echo ========================================

cd /d C:\Users\shorg\ai-stock-trading-bot

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate
) else (
    echo Warning: Virtual environment not found
    echo Using system Python
)

REM Run the trading system
python run_trading_system.py

echo ========================================
echo Trading execution complete
echo ========================================

REM Keep window open to see any errors
timeout /t 30