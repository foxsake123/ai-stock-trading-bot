@echo off
echo ========================================
echo Setting up Automated Post-Market Reports
echo Schedule: 4:30 PM ET (Monday-Friday)
echo ========================================

REM Delete existing task if it exists
schtasks /delete /tn "AI Trading Bot - Post Market 4_30PM" /f 2>nul

REM Create new scheduled task for 4:30 PM ET weekdays
schtasks /create ^
    /tn "AI Trading Bot - Post Market 4_30PM" ^
    /tr "C:\Users\shorg\ai-stock-trading-bot\automated_post_market_4_30pm.bat" ^
    /sc weekly ^
    /d MON,TUE,WED,THU,FRI ^
    /st 16:30 ^
    /f

echo.
echo Task created successfully!
echo.
echo Scheduled Reports:
echo - Post-Market Report: 4:30 PM ET Daily
echo - Sends to Telegram automatically
echo - Includes both comprehensive and daily summaries
echo.
echo To test now, run: automated_post_market_4_30pm.bat
echo.
pause