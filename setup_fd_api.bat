@echo off
echo ============================================================
echo FINANCIAL DATASETS API SETUP
echo ============================================================
echo.
echo Please add your Financial Datasets API key to the .env file
echo.
echo Steps:
echo 1. Open .env file in a text editor
echo 2. Find the line: FINANCIAL_DATASETS_API_KEY=your_api_key_here
echo 3. Replace "your_api_key_here" with your actual API key
echo 4. Save the file
echo.
echo Your API key can be found at:
echo https://financialdatasets.ai/dashboard
echo.
echo After adding the key, run:
echo   python test_fd_integration.py
echo.
echo to verify the integration is working.
echo.
pause
notepad .env