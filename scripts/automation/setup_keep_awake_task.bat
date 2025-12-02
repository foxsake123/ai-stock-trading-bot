@echo off
echo ============================================================
echo Setting up Keep-Awake Task for AI Trading Bot
echo ============================================================
echo.

REM Get Python path
set PYTHON_PATH=C:\Users\shorg\AppData\Local\Programs\Python\Python313\python.exe
set SCRIPT_PATH=C:\Users\shorg\ai-stock-trading-bot\scripts\automation\keep_awake.py

echo Creating scheduled task...
echo Python: %PYTHON_PATH%
echo Script: %SCRIPT_PATH%
echo.

REM Delete existing task if it exists
schtasks /Delete /TN "AI Trading - Keep Awake" /F 2>nul

REM Create task to run at 6:00 AM daily
schtasks /Create /TN "AI Trading - Keep Awake" ^
    /TR "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" ^
    /SC DAILY ^
    /ST 06:00 ^
    /RL HIGHEST ^
    /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Task created successfully!
    echo.
    echo The keep-awake service will:
    echo   - Start at 6:00 AM daily
    echo   - Keep computer awake 8:00 AM - 5:00 PM on trading days
    echo   - Keep computer awake 11:00 AM - 1:00 PM on Saturdays
    echo   - Allow sleep outside those hours
    echo.
) else (
    echo.
    echo [ERROR] Failed to create task. Run as Administrator.
    echo.
)

pause
