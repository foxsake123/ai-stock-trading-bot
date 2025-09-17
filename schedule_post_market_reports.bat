@echo off
echo Setting up automated post-market reports...

REM Create scheduled task for post-market reports at 4:15 PM ET weekdays
schtasks /create /tn "AI Trading Bot - Post Market Report" /tr "python \"C:\Users\shorg\ai-stock-trading-bot\generate_current_post_market_report.py\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 16:15 /f

echo.
echo Scheduled task created successfully!
echo Post-market reports will be sent daily at 4:15 PM ET
echo.
pause