@echo off
echo Setting up Dual-Bot Automation (DEE-BOT + SHORGAN-BOT)...
echo.

REM Remove old single-bot tasks if they exist
schtasks /delete /tn "AI Trading Bot - DEE-BOT Morning Update" /f 2>nul
schtasks /delete /tn "AI Trading Bot - DEE-BOT Afternoon Update" /f 2>nul

REM Morning Position Update - 9:30 AM (Both Bots)
echo Creating morning position update (9:30 AM)...
schtasks /create /tn "AI Trading Bot - Morning Position Update" /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\update_all_bot_positions.py" /sc DAILY /st 09:30 /f

REM Afternoon Position Update - 4:00 PM (Both Bots)
echo Creating afternoon position update (4:00 PM)...
schtasks /create /tn "AI Trading Bot - Afternoon Position Update" /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\update_all_bot_positions.py" /sc DAILY /st 16:00 /f

REM Daily Portfolio Snapshot - 4:00 PM (Both Bots)
echo Creating daily portfolio snapshot (4:00 PM)...
schtasks /create /tn "AI Trading Bot - Daily Portfolio Snapshot" /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\daily_portfolio_snapshot.py" /sc DAILY /st 16:00 /f

REM Post-Market Report - 4:30 PM (Both Bots)
echo Creating post-market report (4:30 PM)...
schtasks /create /tn "AI Trading Bot - Post Market Report" /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\generate_post_market_report.py" /sc DAILY /st 16:30 /f

echo.
echo Automation Setup Complete!
echo.
echo Daily Schedule:
echo - 9:30 AM:  Update both bot positions (market open)
echo - 4:00 PM:  Update positions + portfolio snapshot (market close)
echo - 4:30 PM:  Generate post-market report for both bots
echo.
echo Weekly Schedule (already set):
echo - Friday 4:30 PM:  Weekly performance report
echo - Sunday 5:00 PM:  Generate weekly prompts
echo - Sunday 6:00 PM:  Weekly trade planner
echo.
echo To view all scheduled tasks:
schtasks /query /tn "AI Trading Bot*" /v
pause