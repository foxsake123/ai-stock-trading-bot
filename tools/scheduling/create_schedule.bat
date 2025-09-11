@echo off
echo Creating scheduled task for trading reports...
schtasks /create /tn "Trading-Reports-8AM" /tr "C:\Users\shorg\ai-stock-trading-bot\send_morning_reports.bat" /sc daily /st 08:00 /f
echo.
echo Task created! Reports will be sent daily at 8:00 AM ET
echo.
echo To test now: schtasks /run /tn "Trading-Reports-8AM"
echo To view task: schtasks /query /tn "Trading-Reports-8AM"
echo To delete task: schtasks /delete /tn "Trading-Reports-8AM" /f
pause