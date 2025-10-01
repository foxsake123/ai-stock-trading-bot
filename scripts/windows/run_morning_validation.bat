@echo off
REM ============================================================
REM Morning Validation - 9:00 AM ET
REM ============================================================
REM Validates Claude research through multi-agent consensus
REM Runs every trading day at 9:00 AM (30 min before market)
REM ============================================================

echo ============================================================
echo MORNING VALIDATION - MULTI-AGENT CONSENSUS
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

REM Run consensus validation
python scripts-and-data\automation\consensus_validator.py --bot both

echo.
echo ============================================================
echo [+] Validation complete!
echo [+] Check execution plans in: scripts-and-data\data\execution-plans\
echo ============================================================
