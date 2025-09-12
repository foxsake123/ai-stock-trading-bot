@echo off
REM Setup Windows Task Scheduler for SHORGAN-BOT automation
REM Run this as Administrator

echo ========================================
echo Setting up SHORGAN-BOT Scheduled Tasks
echo ========================================

REM Set paths
set PYTHON_PATH=C:\Python313\python.exe
set BOT_PATH=C:\Users\shorg\ai-stock-trading-bot
set DAILY_SCRIPT=%BOT_PATH%\01_trading_system\automation\daily_pre_market_pipeline.py
set WEEKLY_SCRIPT=%BOT_PATH%\01_trading_system\automation\weekly_deep_research.py

REM Create Daily Pre-Market Task (7:00 AM ET, Monday-Friday)
echo.
echo Creating Daily Pre-Market Task (7:00 AM ET)...
schtasks /create /tn "SHORGAN_BOT_Daily_PreMarket" /tr "\"%PYTHON_PATH%\" \"%DAILY_SCRIPT%\"" /sc WEEKLY /d MON,TUE,WED,THU,FRI /st 07:00 /f

REM Create Weekly Deep Research Task (Sunday 2:00 PM ET)
echo.
echo Creating Weekly Research Task (Sunday 2:00 PM ET)...
schtasks /create /tn "SHORGAN_BOT_Weekly_Research" /tr "\"%PYTHON_PATH%\" \"%WEEKLY_SCRIPT%\"" /sc WEEKLY /d SUN /st 14:00 /f

REM Create Daily Performance Tracker (4:15 PM ET, Monday-Friday)
echo.
echo Creating Daily Performance Tracker (4:15 PM ET)...
schtasks /create /tn "SHORGAN_BOT_Daily_Performance" /tr "\"%PYTHON_PATH%\" \"%BOT_PATH%\02_data\portfolio\performance\automated_performance_tracker.py\"" /sc WEEKLY /d MON,TUE,WED,THU,FRI /st 16:15 /f

echo.
echo ========================================
echo Task Schedule Summary:
echo ========================================
echo 1. Daily Pre-Market: Mon-Fri @ 7:00 AM ET
echo 2. Weekly Research: Sunday @ 2:00 PM ET
echo 3. Daily Performance: Mon-Fri @ 4:15 PM ET
echo.
echo To view tasks: schtasks /query /tn SHORGAN_BOT*
echo To delete a task: schtasks /delete /tn "TASK_NAME"
echo.
pause