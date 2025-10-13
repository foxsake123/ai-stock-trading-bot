@echo off
REM Start Pre-Market Report Web Dashboard
REM Launches Flask web server on http://localhost:5000

echo ================================================================================
echo Starting Pre-Market Report Web Dashboard
echo ================================================================================
echo.
echo Dashboard will be available at:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ================================================================================
echo.

cd C:\Users\shorg\ai-stock-trading-bot
python web_dashboard.py

pause
