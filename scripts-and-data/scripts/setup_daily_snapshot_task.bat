@echo off
REM Setup Windows Task Scheduler for Daily Portfolio Snapshots
REM This creates a scheduled task to run at 4:00 PM ET every weekday

echo Setting up Daily Portfolio Snapshot Task...
echo.

REM Delete existing task if it exists
schtasks /delete /tn "AI Trading Bot - Daily Snapshot" /f 2>nul

REM Create new scheduled task
REM Runs Monday-Friday at 4:00 PM ET
schtasks /create ^
  /tn "AI Trading Bot - Daily Snapshot" ^
  /tr "C:\Users\shorg\ai-stock-trading-bot\run_daily_snapshot.bat" ^
  /sc WEEKLY ^
  /d MON,TUE,WED,THU,FRI ^
  /st 16:00 ^
  /f

echo.
echo Task created successfully!
echo.
echo The Daily Portfolio Snapshot will run:
echo - Every weekday (Monday-Friday)
echo - At 4:00 PM ET
echo - Saving snapshots to scripts-and-data\daily-snapshots\
echo.
echo To run manually: run_daily_snapshot.bat
echo To view task: Task Scheduler > "AI Trading Bot - Daily Snapshot"
echo.

pause