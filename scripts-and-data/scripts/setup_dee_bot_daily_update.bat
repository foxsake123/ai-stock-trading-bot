@echo off
REM Setup Windows Task Scheduler for Daily DEE-BOT Updates
REM This will create a scheduled task to run at 4:00 PM ET daily

echo ========================================
echo SETTING UP DAILY DEE-BOT UPDATE TASK
echo ========================================
echo.

REM Delete existing task if it exists (ignore errors)
schtasks /delete /tn "DEE-BOT Daily Update" /f 2>nul

REM Create new scheduled task
REM Runs daily at 4:00 PM
schtasks /create ^
    /tn "DEE-BOT Daily Update" ^
    /tr "C:\Users\shorg\ai-stock-trading-bot\update_dee_bot_daily.bat" ^
    /sc DAILY ^
    /st 16:00 ^
    /ru %USERNAME% ^
    /rl HIGHEST ^
    /f

if %errorlevel% == 0 (
    echo.
    echo SUCCESS: Daily update task created!
    echo.
    echo Task Details:
    echo - Name: DEE-BOT Daily Update
    echo - Schedule: Daily at 4:00 PM
    echo - Script: update_dee_bot_daily.bat
    echo.
    echo The task will automatically update DEE-BOT positions from Alpaca every day.
    echo.

    REM Also create a task for 9:30 AM pre-market check
    schtasks /create ^
        /tn "DEE-BOT Morning Check" ^
        /tr "C:\Users\shorg\ai-stock-trading-bot\update_dee_bot_daily.bat" ^
        /sc DAILY ^
        /st 09:30 ^
        /ru %USERNAME% ^
        /rl HIGHEST ^
        /f

    echo Additional morning check task created at 9:30 AM
) else (
    echo.
    echo ERROR: Failed to create scheduled task
    echo Please run this script as Administrator
)

echo.
echo To view scheduled tasks, run: schtasks /query /tn "DEE-BOT*"
echo To run manually now, run: schtasks /run /tn "DEE-BOT Daily Update"
echo.
pause