@echo off
echo ========================================
echo Task Scheduler Working Directory Fix
echo ========================================
echo.
echo This will set the working directory for all trading tasks.
echo You may be prompted for administrator approval.
echo.
pause

powershell -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File %~dp0fix_task_scheduler.ps1' -Verb RunAs -Wait"

echo.
echo Done! Check the output above for results.
pause
