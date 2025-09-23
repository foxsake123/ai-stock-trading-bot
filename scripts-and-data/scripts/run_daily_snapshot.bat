@echo off
REM Daily Portfolio Snapshot Generator
REM Run this at market close (4:00 PM ET) each trading day

echo ============================================================
echo DAILY PORTFOLIO SNAPSHOT
echo %date% %time%
echo ============================================================

REM Navigate to project directory
cd /d C:\Users\shorg\ai-stock-trading-bot

REM Activate Python environment if needed
REM call venv\Scripts\activate

REM Run the snapshot generator
python scripts-and-data\automation\daily_portfolio_snapshot.py

REM Send notification via Telegram (optional)
REM python scripts-and-data\automation\send_daily_report.py

echo.
echo Snapshot complete!
echo Check scripts-and-data\daily-snapshots\ for today's files
echo.

REM Keep window open for review (remove for scheduled task)
pause