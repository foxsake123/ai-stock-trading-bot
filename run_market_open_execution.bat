@echo off
REM ============================================================
REM Market Open Execution - 9:30 AM ET
REM ============================================================
REM Executes validated trades at market open
REM Monitors fills and sends notifications
REM ============================================================

echo ============================================================
echo MARKET OPEN EXECUTION - AUTOMATED TRADING
echo ============================================================
echo.
echo [*] Time: %TIME%
echo [*] Date: %DATE%
echo.

cd /d C:\Users\shorg\ai-stock-trading-bot

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Execute validated trades
python scripts-and-data\automation\auto_executor.py --bot both

echo.
echo ============================================================
echo [+] Execution complete!
echo [+] Check results in: scripts-and-data\data\execution-results\
echo ============================================================
