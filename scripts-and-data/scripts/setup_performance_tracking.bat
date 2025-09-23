@echo off
echo Setting up daily performance tracking task...

REM Create task for daily performance tracking at 4:00 PM ET
schtasks /create /tn "AI Trading Bot - Daily Performance Tracker" /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\daily_performance_tracker.py" /sc daily /st 16:00 /f

REM Create task for morning performance check at 10:00 AM ET
schtasks /create /tn "AI Trading Bot - Morning Performance Check" /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\daily_performance_tracker.py" /sc daily /st 10:00 /f

echo.
echo Tasks created successfully!
echo.
echo Scheduled tasks:
echo 1. Daily Performance Tracker - 4:00 PM ET
echo 2. Morning Performance Check - 10:00 AM ET
echo.
pause