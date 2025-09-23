@echo off
echo ================================================
echo Generating Comprehensive Trading Report
echo ================================================
echo.
echo This will create a detailed HTML report with:
echo - ALL positions with complete details
echo - Full P&L analysis
echo - Complete trade history
echo - Market commentary
echo - Active catalysts
echo - Risk metrics
echo - Performance charts
echo.

cd /d "C:\Users\shorg\ai-stock-trading-bot"
python 01_trading_system/automation/comprehensive_report_generator.py daily

echo.
echo ================================================
echo Report generation complete!
echo Check: 07_docs\daily_comprehensive_reports\
echo ================================================
pause