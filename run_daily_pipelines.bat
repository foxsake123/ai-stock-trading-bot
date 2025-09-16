@echo off
echo ========================================
echo Running Daily Pre-Market Pipelines
echo ========================================
echo.

cd /d "C:\Users\shorg\ai-stock-trading-bot"

echo [%date% %time%] Starting pipelines...
echo.

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Run both pipelines
python 01_trading_system\automation\daily_pre_market_pipeline.py --bot BOTH

echo.
echo [%date% %time%] Pipelines complete
echo ========================================
pause