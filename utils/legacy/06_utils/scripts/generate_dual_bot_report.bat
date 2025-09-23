@echo off
echo ================================================
echo Dual Bot Report Generator
echo ================================================
echo.
echo Generating comprehensive reports for:
echo   - SHORGAN-BOT (Micro-cap Catalyst Trading)
echo   - DEE-BOT (Beta-neutral S&P 100)
echo.
echo Reports will include:
echo   - HTML version (opens in browser)
echo   - PDF version (for printing/sharing)
echo.

cd /d "C:\Users\shorg\ai-stock-trading-bot"
python 01_trading_system/automation/dual_bot_report_generator.py

echo.
echo ================================================
echo Reports saved to: 07_docs\dual_bot_reports\
echo ================================================
pause