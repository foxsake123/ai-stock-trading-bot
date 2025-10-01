@echo off
REM ============================================================
REM Daily Claude Research Automation (Market Days Only)
REM ============================================================
REM This script generates comprehensive daily research reports
REM using Claude AI for both DEE-BOT and SHORGAN-BOT
REM
REM Schedule: Every day at 6:00 PM ET
REM Logic: Only generates if tomorrow is a trading day
REM Duration: ~5-10 minutes (Claude Extended Thinking)
REM Output: scripts-and-data/data/reports/weekly/claude-research/
REM ============================================================

echo ============================================================
echo DAILY CLAUDE RESEARCH AUTOMATION
echo ============================================================
echo.
echo [*] Starting Claude deep research generation...
echo [*] Time: %TIME%
echo [*] Date: %DATE%
echo.

cd /d C:\Users\shorg\ai-stock-trading-bot

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run daily research script (includes market day check)
python scripts-and-data\automation\daily_claude_research.py

echo.
echo ============================================================
echo [+] Script execution complete!
echo [+] Check output above to see if reports were generated
echo ============================================================

REM Don't pause for automated runs
REM pause
