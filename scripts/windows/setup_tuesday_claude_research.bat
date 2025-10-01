@echo off
REM ============================================================
REM Tuesday Automation - Claude Deep Research Generation
REM ============================================================
REM This script generates comprehensive weekly research reports
REM using Claude AI for both DEE-BOT and SHORGAN-BOT
REM
REM Schedule: Every Tuesday at 6:00 PM ET
REM Duration: ~5-10 minutes (Claude API calls)
REM Output: scripts-and-data/data/reports/weekly/claude-research/
REM ============================================================

echo ============================================================
echo TUESDAY CLAUDE RESEARCH AUTOMATION
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

REM Generate research reports for both bots
echo [*] Generating DEE-BOT research report...
python scripts-and-data\automation\claude_research_generator.py --bot dee --week 5

echo.
echo [*] Generating SHORGAN-BOT research report...
python scripts-and-data\automation\claude_research_generator.py --bot shorgan --week 5

echo.
echo ============================================================
echo [+] Claude research generation complete!
echo [+] Check: scripts-and-data\data\reports\weekly\claude-research\
echo ============================================================

pause
