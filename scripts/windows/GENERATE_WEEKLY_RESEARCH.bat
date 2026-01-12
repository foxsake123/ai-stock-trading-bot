@echo off
REM ============================================
REM GENERATE WEEKLY RESEARCH REPORT
REM Uses Claude AI with Financial Datasets MCP
REM ============================================

echo.
echo ============================================
echo WEEKLY RESEARCH REPORT GENERATOR
echo Using Claude AI + Financial Datasets
echo ============================================
echo.

cd /d C:\Users\shorg\ai-stock-trading-bot

echo Starting weekly research generation...
echo This may take 5-10 minutes...
echo.

C:\Python313\python.exe scripts\automation\weekly_research_generator.py --force

echo.
echo ============================================
echo WEEKLY RESEARCH COMPLETE
echo ============================================
echo.

echo Report saved to: reports\weekly\
echo.

echo This report contains:
echo - Weekly market overview and sector analysis
echo - Portfolio performance review (all 3 accounts)
echo - DEE-BOT position analysis and trades
echo - SHORGAN Paper catalyst plays
echo - SHORGAN Live recommendations (real money)
echo - Top 10 conviction trades for the week
echo - Complete order blocks
echo.

pause
