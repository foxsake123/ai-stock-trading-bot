@echo off
REM Automated ChatGPT Trade Fetcher
REM Fetches daily trade recommendations from ChatGPT

echo ========================================
echo CHATGPT AUTOMATED TRADE FETCHER
echo ========================================
echo.

REM Navigate to project directory
cd /d C:\Users\shorg\ai-stock-trading-bot

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Install required packages if needed
echo Checking dependencies...
pip install selenium undetected-chromedriver --quiet

REM Run the fetcher
echo.
echo Starting automated ChatGPT fetcher...
echo.
python scripts-and-data\automation\automated_chatgpt_fetcher.py

REM Check if successful
if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: ChatGPT trades fetched successfully!
    echo Check: scripts-and-data\daily-json\chatgpt\
) else (
    echo.
    echo ERROR: Failed to fetch ChatGPT trades
    echo Please check the logs above
)

echo.
pause