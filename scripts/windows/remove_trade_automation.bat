@echo off
REM Remove all AI Trading Bot Task Scheduler entries

echo ========================================
echo  AI Trading Bot - Remove Automation
echo ========================================
echo.
echo This will DELETE all scheduled trading tasks.
echo.
pause

echo.
echo Removing scheduled tasks...
echo.

REM Try both old and new task names for research
schtasks /delete /tn "AI Trading - Weekend Research" /f 2>nul
if errorlevel 1 (
    schtasks /delete /tn "AI Trading - Evening Research" /f 2>nul
    if errorlevel 1 (
        echo [SKIP] Weekend/Evening Research task not found
    ) else (
        echo [DELETED] Evening Research task (old name)
    )
) else (
    echo [DELETED] Weekend Research task
)

schtasks /delete /tn "AI Trading - Morning Trade Generation" /f 2>nul
if errorlevel 1 (
    echo [SKIP] Morning Trade Generation task not found
) else (
    echo [DELETED] Morning Trade Generation task
)

schtasks /delete /tn "AI Trading - Trade Execution" /f 2>nul
if errorlevel 1 (
    echo [SKIP] Trade Execution task not found
) else (
    echo [DELETED] Trade Execution task
)

schtasks /delete /tn "AI Trading - Daily Performance Graph" /f 2>nul
if errorlevel 1 (
    echo [SKIP] Daily Performance Graph task not found
) else (
    echo [DELETED] Daily Performance Graph task
)

echo.
echo ========================================
echo  Removal Complete
echo ========================================
echo.
pause
