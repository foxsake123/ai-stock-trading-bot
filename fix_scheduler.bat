@echo off
echo Fixing Task Scheduler for AI Trading Research...
echo.

REM Delete old task
schtasks /delete /tn "AI Trading - Evening Research" /f

REM Create new task with working directory
schtasks /create /tn "AI Trading - Evening Research" /tr "C:\Users\shorg\ai-stock-trading-bot\run_research.bat" /sc daily /st 18:00 /f

echo.
echo Task Scheduler fixed!
echo The task will now run from the correct directory.
echo.
echo Next run: Today at 6:00 PM (and daily after that)
echo.
pause
