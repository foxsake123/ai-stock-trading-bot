@echo off
REM AI Trading Bot - Test Runner Script (Windows)
REM Runs comprehensive test suite with coverage reporting

echo ================================================================================
echo AI TRADING BOT - TEST SUITE
echo ================================================================================
echo.

REM Check if pytest is installed
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo Error: pytest is not installed
    echo Install with: pip install pytest pytest-cov pytest-mock
    exit /b 1
)

echo Step 1: Running Unit Tests
echo --------------------------------------------------------------------------------
python -m pytest tests/test_*.py -v -m "not integration" --tb=short
echo.

echo Step 2: Running Integration Tests
echo --------------------------------------------------------------------------------
python -m pytest tests/test_integration.py -v -m integration --tb=short
echo.

echo Step 3: Running All Tests with Coverage
echo --------------------------------------------------------------------------------
python -m pytest tests/ -v ^
    --cov=. ^
    --cov-report=html ^
    --cov-report=term-missing ^
    --tb=short
echo.

echo ================================================================================
echo TEST SUITE COMPLETE
echo ================================================================================
echo.
echo Coverage Report:
echo   - HTML: htmlcov\index.html
echo   - Open with: start htmlcov\index.html
echo.
echo Test Summary:
python -m pytest tests/ --collect-only -q 2>nul | findstr /R "test.*py"
echo.
echo Next Steps:
echo   1. Review coverage report in htmlcov\index.html
echo   2. Fix any failing tests
echo   3. Aim for ^>50%% coverage on new code
echo.
echo ================================================================================

pause
