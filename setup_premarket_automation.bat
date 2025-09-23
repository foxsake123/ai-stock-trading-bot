@echo off
REM Setup Pre-Market Report Automation for 9:00 AM ET Daily

echo ========================================
echo Setting up Pre-Market Report Automation
echo ========================================

REM Create the scheduled task for 9:00 AM ET daily
schtasks /create /tn "AI Trading Bot - Pre-Market Report 9AM" /tr "C:\Python313\python.exe C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\generate_premarket_plan.py" /sc daily /st 09:00 /f

echo.
echo Pre-Market Report scheduled for 9:00 AM ET daily
echo Task Name: AI Trading Bot - Pre-Market Report 9AM
echo.
echo To verify: schtasks /query /tn "AI Trading Bot - Pre-Market Report 9AM"
echo To delete: schtasks /delete /tn "AI Trading Bot - Pre-Market Report 9AM" /f
echo.
pause