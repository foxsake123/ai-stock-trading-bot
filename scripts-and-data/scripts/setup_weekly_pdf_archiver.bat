@echo off
echo Setting up weekly PDF archiving task...

REM Create task for weekly PDF archiving (Sunday 10 PM)
schtasks /create /tn "AI Trading Bot - Weekly PDF Archiver" /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts-and-data\automation\archive_weekly_pdfs.py" /sc weekly /d SUN /st 22:00 /f

echo.
echo Task created successfully!
echo.
echo The system will automatically check for PDFs every Sunday at 10 PM
echo.
echo You can also manually archive PDFs anytime by:
echo 1. Placing PDFs in: weekly-uploads\
echo 2. Running: upload_weekly_pdfs.bat
echo.
pause