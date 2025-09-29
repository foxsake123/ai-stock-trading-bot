@echo off
echo ========================================
echo CHECKING WINDOWS TASK SCHEDULER TASKS
echo ========================================
echo.

echo Checking for AI Trading Bot tasks...
echo.

schtasks /query 2>nul | findstr /i "AI Trading Bot" >nul
if %errorlevel% equ 0 (
    echo Found AI Trading Bot tasks:
    echo.
    schtasks /query 2>nul | findstr /i "AI Trading Bot"
) else (
    echo No AI Trading Bot tasks found.
    echo.
    echo Please run setup_all_tasks.bat as Administrator to configure.
)

echo.
echo ========================================
echo To setup all tasks:
echo   1. Right-click setup_all_tasks.bat
echo   2. Select "Run as administrator"
echo ========================================
echo.
pause