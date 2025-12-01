@echo off
echo Creating Task Scheduler tasks...

schtasks /Create /TN "AI Trading - Morning Trade Generation" /TR "C:\Users\shorg\AppData\Local\Programs\Python\Python313\python.exe C:\Users\shorg\ai-stock-trading-bot\scripts\automation\generate_todays_trades_v2.py" /SC DAILY /ST 08:30 /F
echo Created: Morning Trade Generation

schtasks /Create /TN "AI Trading - Trade Execution" /TR "C:\Users\shorg\AppData\Local\Programs\Python\Python313\python.exe C:\Users\shorg\ai-stock-trading-bot\scripts\automation\execute_daily_trades.py" /SC DAILY /ST 09:30 /F
echo Created: Trade Execution

schtasks /Create /TN "AI Trading - Performance Graph" /TR "C:\Users\shorg\AppData\Local\Programs\Python\Python313\python.exe C:\Users\shorg\ai-stock-trading-bot\scripts\performance\generate_performance_graph.py" /SC DAILY /ST 16:30 /F
echo Created: Performance Graph

schtasks /Create /TN "AI Trading - Weekend Research" /TR "C:\Users\shorg\AppData\Local\Programs\Python\Python313\python.exe C:\Users\shorg\ai-stock-trading-bot\scripts\automation\daily_claude_research.py" /SC WEEKLY /D SAT /ST 12:00 /F
echo Created: Weekend Research

echo.
echo Verifying tasks...
schtasks /query /fo TABLE | findstr "AI Trading"

echo.
echo Done!
