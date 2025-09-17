@echo off
echo ========================================
echo AI Trading Bot - Automated Post-Market Report
echo Time: 4:30 PM ET Daily
echo ========================================

REM Change to the project directory
cd /d C:\Users\shorg\ai-stock-trading-bot

REM Start the ChatGPT server if not running
echo Checking ChatGPT server status...
powershell -Command "if (!(Get-NetTCPConnection -LocalPort 8888 -ErrorAction SilentlyContinue)) { Start-Process python -ArgumentList '01_trading_system/automation/chatgpt_report_server.py' -WindowStyle Hidden }"

REM Wait 5 seconds for server to start
timeout /t 5 /nobreak >nul

REM Generate comprehensive post-market report
echo Generating post-market report...
python generate_current_post_market_report.py

REM Also run the basic daily report
echo Sending daily summary...
python 06_utils/send_daily_report.py

echo ========================================
echo Post-market reports completed
echo Reports sent to Telegram
echo ========================================