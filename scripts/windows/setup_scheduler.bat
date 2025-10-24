@echo off
echo Setting up Task Scheduler for AI Trading Research...
echo.

REM Create evening research task (6:00 PM ET daily)
schtasks /create /tn "AI Trading - Evening Research" /tr "C:\Python313\python.exe C:\Users\shorg\ai-stock-trading-bot\scripts\automation\daily_claude_research.py" /sc daily /st 18:00 /f

echo.
echo Task Scheduler setup complete!
echo.
echo Scheduled tasks:
echo - Evening Research: 6:00 PM ET daily
echo.
pause
