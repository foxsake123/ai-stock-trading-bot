@echo off
echo Fixing Telegram Pre-Market Reports Schedule...

REM Remove old tasks
schtasks /delete /tn "Trading-Reports-7AM" /f 2>nul
schtasks /delete /tn "Trading-Reports-PreMarket" /f 2>nul

REM Create new task
schtasks /create /tn "Trading-Reports-PreMarket" /tr "C:\Users\shorg\ai-stock-trading-bot\06_utils\tools\scheduling\send_morning_reports.bat" /sc daily /st 07:00 /f

echo.
echo Task created successfully!
echo.
echo To test manually, run:
echo   cd C:\Users\shorg\ai-stock-trading-bot\06_utils\tools\scheduling
echo   send_morning_reports.bat
echo.
echo To check task status:
echo   schtasks /query /tn "Trading-Reports-PreMarket"
pause