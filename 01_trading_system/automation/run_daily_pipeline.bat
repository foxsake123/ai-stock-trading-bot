@echo off
REM Daily Pre-Market Pipeline Runner
REM This batch file ensures proper environment and logging

cd /d C:\Users\shorg\ai-stock-trading-bot
echo Starting Daily Pre-Market Pipeline at %date% %time% >> 09_logs\automation\daily_runs.log

REM Activate Python and run script
C:\Python313\python.exe 01_trading_system\automation\daily_pre_market_pipeline.py

echo Completed at %date% %time% >> 09_logs\automation\daily_runs.log
echo ================================ >> 09_logs\automation\daily_runs.log