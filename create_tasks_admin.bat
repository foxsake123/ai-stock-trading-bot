@echo off
REM Run this script as Administrator to create Task Scheduler tasks
REM Right-click -> Run as administrator

echo Creating AI Trading automation tasks...
echo.

REM Task 1: Weekend Research (Saturday 12 PM)
schtasks /Create /TN "AI Trading - Weekend Research" /TR "C:\Python313\python.exe C:\Users\shorg\ai-stock-trading-bot\scripts\automation\daily_claude_research.py --force" /SC WEEKLY /D SAT /ST 12:00 /F
echo.

REM Task 2: Morning Trade Generation (Weekdays 8:30 AM)
schtasks /Create /TN "AI Trading - Morning Trade Generation" /TR "C:\Python313\python.exe C:\Users\shorg\ai-stock-trading-bot\scripts\automation\generate_todays_trades_v2.py" /SC DAILY /ST 08:30 /F
echo.

REM Task 3: Trade Execution (Weekdays 9:30 AM)
schtasks /Create /TN "AI Trading - Trade Execution" /TR "C:\Python313\python.exe C:\Users\shorg\ai-stock-trading-bot\scripts\automation\execute_daily_trades.py" /SC DAILY /ST 09:30 /F
echo.

REM Task 4: Performance Graph (Weekdays 4:30 PM)
schtasks /Create /TN "AI Trading - Daily Performance Graph" /TR "C:\Python313\python.exe C:\Users\shorg\ai-stock-trading-bot\scripts\performance\generate_performance_graph.py" /SC DAILY /ST 16:30 /F
echo.

REM Task 5: Stop Loss Monitor (Every 5 min during market hours)
schtasks /Create /TN "AI Trading - Stop Loss Monitor" /TR "C:\Python313\python.exe C:\Users\shorg\ai-stock-trading-bot\scripts\automation\monitor_stop_losses.py" /SC MINUTE /MO 5 /ST 09:30 /F
echo.

echo ================================================================================
echo Verifying tasks created...
echo ================================================================================
schtasks /Query /FO LIST | findstr /C:"AI Trading"
echo.
echo ================================================================================
echo DONE! Tasks created. Verify in Task Scheduler (Win+R -> taskschd.msc)
echo ================================================================================
pause
