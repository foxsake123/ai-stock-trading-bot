@echo off
REM Morning Research PDF Sender
REM Runs at 7 AM to send pre-generated research PDFs via Telegram

cd /d "C:\Users\shorg\dev\trading\ai-stock-trading-bot"

echo ========================================
echo Sending Morning Research PDFs
echo %date% %time%
echo ========================================

REM Send today's research PDFs (generated last night at 6 PM)
python scripts\automation\send_research_pdfs.py

echo ========================================
echo Send complete
echo Exit code: %errorlevel%
echo ========================================

exit /b %errorlevel%
