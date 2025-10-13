@echo off
REM Pre-Market Report Generator - Manual Execution
REM This batch file allows easy manual testing of the report generator

echo ================================================================================
echo Pre-Market Report Generator - Manual Execution
echo ================================================================================
echo.
echo Starting report generation...
echo Working directory: C:\Users\CHANGE_USERNAME\ai-stock-trading-bot
echo.

REM Change to project directory
cd /d C:\Users\CHANGE_USERNAME\ai-stock-trading-bot

REM Run the report generator
python daily_premarket_report.py

echo.
echo ================================================================================
echo Report generation completed
echo Check reports/premarket/ folder for output
echo ================================================================================
echo.

pause
