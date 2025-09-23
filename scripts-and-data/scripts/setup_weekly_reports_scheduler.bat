@echo off
echo Setting up Windows Task Scheduler for Weekly Reports...

REM Weekly Performance Report - Friday 4:30 PM
schtasks /create /tn "AI Trading Bot - Weekly Performance Report" /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\weekly_performance_report.py" /sc WEEKLY /d FRI /st 16:30 /f

REM Weekly Trade Planner - Sunday 6:00 PM
schtasks /create /tn "AI Trading Bot - Weekly Trade Planner" /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\weekly_trade_planner.py" /sc WEEKLY /d SUN /st 18:00 /f

REM Weekly Prompt Generator - Sunday 5:00 PM (before trade planner)
schtasks /create /tn "AI Trading Bot - Weekly Prompt Generator" /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\generate_weekly_prompt.py" /sc WEEKLY /d SUN /st 17:00 /f

echo.
echo Task Scheduler Setup Complete!
echo.
echo Scheduled Tasks:
echo - Friday 4:30 PM: Weekly Performance Report (backward-looking)
echo - Sunday 5:00 PM: Generate ChatGPT Prompts
echo - Sunday 6:00 PM: Weekly Trade Planner (forward-looking)
echo.
echo To view scheduled tasks: schtasks /query /tn "AI Trading Bot*"
pause