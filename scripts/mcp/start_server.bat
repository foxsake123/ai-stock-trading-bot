@echo off
echo ==========================================
echo    STOCK-BOT Server Launcher
echo ==========================================
echo.

cd /d "%~dp0"

:: Set master key (change this for production!)
set MASTER_KEY=PTU0qkUU2s8SbyLgFcSV8x3iXwVBoODqV849jcG-6Mk
set PORT=8888

echo Starting server on http://localhost:%PORT%
echo.
echo Press Ctrl+C to stop
echo.

python stock_bot_server.py

pause
