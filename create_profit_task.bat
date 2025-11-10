@echo off
echo Creating Profit Taking Manager task...
schtasks /Delete /TN "AI Trading - Profit Taking Manager" /F >nul 2>&1
schtasks /Create /TN "AI Trading - Profit Taking Manager" /TR "\"C:\Python313\python.exe\" \"C:\Users\shorg\ai-stock-trading-bot\scripts\automation\manage_profit_taking.py\"" /SC HOURLY /ST 09:30 /ET 16:30 /F /RL HIGHEST
echo Done!
pause
