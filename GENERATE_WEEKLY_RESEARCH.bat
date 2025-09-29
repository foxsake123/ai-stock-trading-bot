@echo off
REM ================================================
REM GENERATE WEEKLY CHATGPT RESEARCH REPORT
REM For Week of Sept 30 - Oct 4, 2025
REM ================================================

echo ================================================
echo WEEKLY CHATGPT DEEP RESEARCH GENERATOR
echo Week of September 30 - October 4, 2025
echo ================================================
echo.

cd /d C:\Users\shorg\ai-stock-trading-bot

echo This will generate the foundational weekly research report
echo that both DEE-BOT and SHORGAN-BOT should use for trading.
echo.

echo OPTIONS:
echo 1. Automated ChatGPT fetch (requires Chrome login)
echo 2. Manual ChatGPT input (copy/paste from browser)
echo 3. Generate from existing data
echo.

echo ================================================
echo STEP 1: Fetching ChatGPT Analysis
echo ================================================
echo.

REM Try automated fetch first
echo Attempting automated ChatGPT fetch...
python scripts-and-data\automation\automated_chatgpt_fetcher.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Automated fetch failed. Please use manual method:
    echo.
    echo MANUAL STEPS:
    echo 1. Go to ChatGPT.com
    echo 2. Use the prompt from weekly_research_prompt.txt
    echo 3. Copy the full response
    echo 4. Run: python scripts-and-data\automation\save_chatgpt_report.py
    echo.
)

echo.
echo ================================================
echo STEP 2: Generate Weekly Research Report
echo ================================================
echo.

python scripts-and-data\automation\generate_weekly_chatgpt_research.py

echo.
echo ================================================
echo WEEKLY RESEARCH COMPLETE
echo ================================================
echo.

echo Report saved to:
echo scripts-and-data\data\reports\weekly\chatgpt-research\
echo.

echo This report contains:
echo - Macro market analysis for the week
echo - DEE-BOT top 10 defensive picks
echo - SHORGAN-BOT top 15 catalyst plays
echo - Daily event calendar
echo - Risk management guidelines
echo.

pause