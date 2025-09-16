@echo off
echo ================================================
echo Setting Up All Trading Bot Schedules
echo ================================================
echo.

REM Daily Pre-Market Pipeline (7:00 AM ET)
schtasks /create /tn "TradingBot_DailyPreMarket" /tr "python C:\Users\shorg\ai-stock-trading-bot\01_trading_system\automation\daily_pre_market_pipeline.py" /sc daily /st 07:00 /f
echo [OK] Daily Pre-Market Pipeline scheduled for 7:00 AM

REM Post-Market Comprehensive Report (4:30 PM ET)
schtasks /create /tn "TradingBot_PostMarket" /tr "python C:\Users\shorg\ai-stock-trading-bot\01_trading_system\automation\comprehensive_report_generator.py daily" /sc daily /st 16:30 /f
echo [OK] Post-Market Comprehensive Report scheduled for 4:30 PM

REM Weekly Comprehensive Report (Sunday 2:00 PM ET)
schtasks /create /tn "TradingBot_WeeklyReport" /tr "python C:\Users\shorg\ai-stock-trading-bot\01_trading_system\automation\comprehensive_report_generator.py weekly" /sc weekly /d SUN /st 14:00 /f
echo [OK] Weekly Comprehensive Report scheduled for Sundays at 2:00 PM

REM Monthly Comprehensive Report (1st of month, 2:00 PM ET)
schtasks /create /tn "TradingBot_MonthlyReport" /tr "python C:\Users\shorg\ai-stock-trading-bot\01_trading_system\automation\comprehensive_report_generator.py monthly" /sc monthly /d 1 /st 14:00 /f
echo [OK] Monthly Comprehensive Report scheduled for 1st of each month at 2:00 PM

REM ChatGPT Report Server (Start at 6:50 AM daily)
schtasks /create /tn "TradingBot_ReportServer" /tr "python C:\Users\shorg\ai-stock-trading-bot\01_trading_system\automation\chatgpt_report_server.py" /sc daily /st 06:50 /f
echo [OK] ChatGPT Report Server scheduled to start at 6:50 AM

echo.
echo ================================================
echo All schedules created successfully!
echo ================================================
echo.
echo Schedule Summary:
echo - 6:50 AM: ChatGPT Report Server starts
echo - 7:00 AM: Daily Pre-Market Pipeline
echo - 4:30 PM: Post-Market Portfolio Update
echo - Sundays 2:00 PM: Weekly Report
echo.
echo To view all schedules: schtasks /query /tn TradingBot*
echo To delete a schedule: schtasks /delete /tn "TradingBot_NAME"
echo.
pause