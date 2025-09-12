@echo off
echo ================================================
echo ChatGPT Report Server Starting...
echo ================================================
echo.
echo Server will run on http://localhost:8888
echo Keep this window open while using the extension
echo Press Ctrl+C to stop the server
echo.
echo ================================================

cd /d "C:\Users\shorg\ai-stock-trading-bot"
python 01_trading_system/automation/chatgpt_report_server.py

pause