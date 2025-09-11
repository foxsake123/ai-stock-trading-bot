@echo off
REM Setup GitHub Repository Structure
REM Creates all necessary directories and files for GitHub repo

echo ========================================
echo Setting up GitHub Repository Structure
echo ========================================

REM Create main directory structure
echo Creating directory structure...

mkdir "Trading Reports\Daily Research" 2>nul
mkdir "Trading Reports\Weekly Summaries" 2>nul
mkdir "Trading Reports\Monthly Reviews" 2>nul  
mkdir "Trading Reports\Performance Charts" 2>nul

mkdir "Portfolio Data\Trade Logs" 2>nul
mkdir "Portfolio Data\Position Tracking" 2>nul
mkdir "Portfolio Data\Performance Metrics" 2>nul
mkdir "Portfolio Data\Market Data" 2>nul
mkdir "Portfolio Data\News Data" 2>nul
mkdir "Portfolio Data\Sentiment Data" 2>nul

mkdir "Agents" 2>nul
mkdir "Trading Engine" 2>nul
mkdir "Data Sources" 2>nul
mkdir "Configuration" 2>nul
mkdir "Notifications" 2>nul
mkdir "Testing\backtesting" 2>nul
mkdir "Testing\paper_trading_results" 2>nul
mkdir "Testing\unit_tests" 2>nul
mkdir "Documentation" 2>nul

REM Create .gitkeep files for empty directories
echo Creating .gitkeep files...
echo. > "Trading Reports\Daily Research\.gitkeep"
echo. > "Trading Reports\Weekly Summaries\.gitkeep"
echo. > "Trading Reports\Monthly Reviews\.gitkeep"
echo. > "Trading Reports\Performance Charts\.gitkeep"
echo. > "Portfolio Data\Trade Logs\.gitkeep"
echo. > "Portfolio Data\Position Tracking\.gitkeep"
echo. > "Portfolio Data\Performance Metrics\.gitkeep"
echo. > "Portfolio Data\Market Data\.gitkeep"
echo. > "Portfolio Data\News Data\.gitkeep"
echo. > "Portfolio Data\Sentiment Data\.gitkeep"
echo. > "Testing\backtesting\.gitkeep"
echo. > "Testing\paper_trading_results\.gitkeep"
echo. > "Testing\unit_tests\.gitkeep"

REM Copy/move files to proper directories
echo Organizing files into proper structure...

REM Move agents if they exist
if exist "agents\*.py" (
    move "agents\*.py" "Agents\" 2>nul
)

REM Move trading engine files
move "automated_trade_executor.py" "Trading Engine\" 2>nul
move "trade_signal_generator.py" "Trading Engine\" 2>nul
move "portfolio_tracker.py" "Trading Engine\" 2>nul

REM Move data source files  
if exist "dee_bot\data\financial_datasets_api.py" (
    copy "dee_bot\data\financial_datasets_api.py" "Data Sources\" 2>nul
)
move "data_collection_system.py" "Data Sources\" 2>nul

REM Move configuration files
move "AUTOMATION_CONFIG.md" "Configuration\" 2>nul
copy ".env" "Configuration\.env.example" 2>nul

REM Move notification files
move "send_telegram_now.py" "Notifications\" 2>nul
move "send_telegram_*.py" "Notifications\" 2>nul
move "test_notifications.py" "Notifications\" 2>nul

REM Move testing files
move "test_*.py" "Testing\" 2>nul

REM Copy GitHub README
copy "README_FOR_GITHUB.md" "README.md" 2>nul

echo.
echo ========================================
echo GitHub Repository Structure Created!
echo ========================================
echo.
echo Next steps:
echo 1. Initialize git repository: git init
echo 2. Add files: git add .
echo 3. Create initial commit: git commit -m "Initial commit"
echo 4. Create GitHub repository online
echo 5. Add remote: git remote add origin [repo-url]
echo 6. Push: git push -u origin main
echo.
echo Directory structure ready for GitHub!
pause