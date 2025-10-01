@echo off
echo ============================================================
echo WEEKLY PDF UPLOAD SYSTEM
echo ============================================================
echo.
echo Place your ChatGPT weekly research PDFs in the folder:
echo   weekly-uploads\
echo.
echo Then press any key to archive them...
pause

cd scripts-and-data\automation
python archive_weekly_pdfs.py

echo.
echo ============================================================
echo PDFs have been archived to:
echo   docs\index\reports-pdf\weekly\
echo ============================================================
echo.
pause