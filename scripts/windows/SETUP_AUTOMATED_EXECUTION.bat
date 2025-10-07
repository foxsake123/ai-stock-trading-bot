@echo off
REM Setup Automated Execution for Oct 8, 2025
REM This creates a Windows Task Scheduler task to run at 9:30 AM ET

echo ================================================================================
echo AI TRADING BOT - AUTOMATED EXECUTION SETUP
echo ================================================================================
echo.

cd /d %~dp0\..\..

echo Setting up Windows Task Scheduler for Oct 8, 2025 at 9:30 AM ET...
echo.

REM Delete existing task if it exists
schtasks /delete /tn "AI_Trading_Bot_Execute_Oct8_2025" /f >nul 2>&1

REM Create new task from XML
schtasks /create /tn "AI_Trading_Bot_Execute_Oct8_2025" /xml "scripts\windows\Oct8_Execution_Task.xml" /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Automated execution scheduled!
    echo.
    echo Task Name: AI_Trading_Bot_Execute_Oct8_2025
    echo Execution Time: October 8, 2025 at 9:30 AM ET
    echo Action: Execute 9 approved trades
    echo.
    echo The system will automatically:
    echo 1. Execute all 9 limit orders at market open
    echo 2. Place 4 GTC stop-loss orders after fills
    echo 3. Send Telegram notifications throughout
    echo.
    echo You can verify the task in Task Scheduler:
    echo - Press Win+R, type "taskschd.msc", press Enter
    echo - Look for "AI_Trading_Bot_Execute_Oct8_2025"
    echo.
    echo To run manually right now, use:
    echo scripts\windows\EXECUTE_OCT8_TRADES.bat
    echo.
) else (
    echo.
    echo [ERROR] Failed to create scheduled task
    echo You may need to run this script as Administrator
    echo.
    echo Right-click this file and select "Run as administrator"
    echo.
)

echo Sending confirmation via Telegram...
python scripts\automation\send_automation_confirmation.py

echo.
echo Press any key to exit...
pause >nul
