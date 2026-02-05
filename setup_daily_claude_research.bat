@echo off
REM Daily Claude Research Generator
REM Runs at 6 PM ET to generate next-day research reports

cd /d "C:\Users\shorg\dev\trading\ai-stock-trading-bot"

echo ========================================
echo Starting Claude Daily Research
echo %date% %time%
echo ========================================

python scripts\automation\daily_claude_research.py

echo ========================================
echo Research generation complete
echo Exit code: %errorlevel%
echo ========================================

exit /b %errorlevel%
