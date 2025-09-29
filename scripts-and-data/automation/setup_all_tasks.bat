@echo off
REM Setup all Windows Task Scheduler tasks for the AI Trading Bot
REM This creates a complete automated trading pipeline

echo ========================================
echo AI TRADING BOT - TASK SCHEDULER SETUP
echo ========================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

echo Setting up automated tasks...
echo.

REM 1. ChatGPT Morning Fetch (6:45 AM)
echo [1/5] Creating ChatGPT Morning Fetch (6:45 AM)...
schtasks /create /tn "AI Trading Bot - ChatGPT Morning Fetch" /xml "C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\ChatGPT_Morning_Fetch.xml" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo      SUCCESS: ChatGPT Morning Fetch scheduled
) else (
    echo      WARNING: Could not create ChatGPT Morning task
)

REM 2. ChatGPT Final Fetch (8:45 AM)
echo [2/5] Creating ChatGPT Final Fetch (8:45 AM)...
schtasks /create /tn "AI Trading Bot - ChatGPT Final Fetch" /tr "C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\fetch_chatgpt_trades.bat" /sc daily /st 08:45 /f >nul 2>&1
if %errorlevel% equ 0 (
    echo      SUCCESS: ChatGPT Final Fetch scheduled
) else (
    echo      WARNING: Could not create ChatGPT Final task
)

REM 3. Generate Today's Trades (9:00 AM)
echo [3/5] Creating Trade Generation (9:00 AM)...
schtasks /create /tn "AI Trading Bot - Generate Trades" /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\generate_todays_trades.py" /sc daily /st 09:00 /f >nul 2>&1
if %errorlevel% equ 0 (
    echo      SUCCESS: Trade Generation scheduled
) else (
    echo      WARNING: Could not create Trade Generation task
)

REM 4. Execute Daily Trades (9:30 AM) - Already exists
echo [4/5] Verifying Trade Execution (9:30 AM)...
schtasks /query /tn "AI Trading Bot - Morning Trade Execution 930AM" >nul 2>&1
if %errorlevel% equ 0 (
    echo      SUCCESS: Trade Execution already configured
) else (
    echo      Creating Trade Execution task...
    schtasks /create /tn "AI Trading Bot - Morning Trade Execution 930AM" /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\execute_daily_trades.py" /sc daily /st 09:30 /f >nul 2>&1
)

REM 5. Post-Market Report (4:30 PM) - Already exists
echo [5/5] Verifying Post-Market Report (4:30 PM)...
schtasks /query /tn "AI Trading Bot - Post Market 4_30PM" >nul 2>&1
if %errorlevel% equ 0 (
    echo      SUCCESS: Post-Market Report already configured
) else (
    echo      Creating Post-Market Report task...
    schtasks /create /tn "AI Trading Bot - Post Market 4_30PM" /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\generate-post-market-report.py" /sc daily /st 16:30 /f >nul 2>&1
)

echo.
echo ========================================
echo TASK SCHEDULER SUMMARY
echo ========================================
echo.
echo Daily Schedule:
echo   6:45 AM - ChatGPT Morning Analysis
echo   8:45 AM - ChatGPT Final Update
echo   9:00 AM - Generate Trading Plan
echo   9:30 AM - Execute Trades
echo   4:30 PM - Post-Market Report
echo.
echo Checking all tasks...
echo.

REM List all AI Trading Bot tasks
schtasks /query /tn "AI Trading Bot*" 2>nul | findstr "AI Trading Bot"

echo.
echo ========================================
echo SETUP COMPLETE
echo ========================================
echo.
echo All tasks have been configured.
echo The system will run automatically starting tomorrow.
echo.
echo To test the pipeline manually:
echo   1. Run fetch_chatgpt_trades.bat
echo   2. Run generate_todays_trades.py
echo   3. Run execute_daily_trades.py
echo.
pause