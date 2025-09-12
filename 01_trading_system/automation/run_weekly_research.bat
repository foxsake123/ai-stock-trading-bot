@echo off
REM Weekly Deep Research Runner
REM This batch file ensures proper environment and logging

cd /d C:\Users\shorg\ai-stock-trading-bot
echo Starting Weekly Deep Research at %date% %time% >> 09_logs\automation\weekly_runs.log

REM Activate Python and run script
C:\Python313\python.exe 01_trading_system\automation\weekly_deep_research.py

echo Completed at %date% %time% >> 09_logs\automation\weekly_runs.log
echo ================================ >> 09_logs\automation\weekly_runs.log