@echo off
REM Research Report Scheduler - Windows Batch File
REM Runs the automated research report scheduler

echo Starting Research Report Scheduler...
echo =====================================
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo No virtual environment found, using system Python
)

REM Run the scheduler
python schedule_research_reports.py

REM Keep window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error occurred! Error code: %ERRORLEVEL%
    pause
)