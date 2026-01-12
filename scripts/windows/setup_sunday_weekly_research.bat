@echo off
REM ============================================
REM Setup Sunday Weekly Research Task
REM Runs every Sunday at 12:00 PM ET
REM ============================================

echo.
echo ============================================
echo SETTING UP SUNDAY WEEKLY RESEARCH TASK
echo ============================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Set variables
set TASK_NAME=AI Trading - Sunday Weekly Research
set PYTHON_PATH=C:\Python313\python.exe
set PROJECT_PATH=C:\Users\shorg\ai-stock-trading-bot
set SCRIPT_PATH=%PROJECT_PATH%\scripts\automation\weekly_research_generator.py

REM Delete existing task if it exists
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

REM Create the task - runs every Sunday at 12:00 PM
echo Creating scheduled task: %TASK_NAME%
schtasks /create ^
    /tn "%TASK_NAME%" ^
    /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" ^
    /sc weekly ^
    /d SUN ^
    /st 12:00 ^
    /ru "%USERNAME%" ^
    /rl HIGHEST ^
    /f

if %errorLevel% equ 0 (
    echo.
    echo [SUCCESS] Task created successfully!
    echo.
    echo Task Details:
    echo   Name: %TASK_NAME%
    echo   Schedule: Every Sunday at 12:00 PM
    echo   Script: %SCRIPT_PATH%
    echo.
) else (
    echo.
    echo [ERROR] Failed to create task
    echo.
)

REM Verify task was created
echo Verifying task...
schtasks /query /tn "%TASK_NAME%" /fo LIST

echo.
echo ============================================
echo To test the task manually:
echo   schtasks /run /tn "%TASK_NAME%"
echo.
echo To view task in Task Scheduler:
echo   1. Press Win+R, type taskschd.msc
echo   2. Look for "%TASK_NAME%"
echo ============================================
echo.

pause
