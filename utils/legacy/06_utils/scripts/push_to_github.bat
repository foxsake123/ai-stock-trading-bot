@echo off
REM Push to GitHub Repository
REM Replace YOUR_USERNAME with your actual GitHub username

echo ========================================
echo PUSH TO GITHUB
echo ========================================
echo.

REM Add remote origin (replace with your repository URL)
echo Adding GitHub remote...
git remote add origin https://github.com/YOUR_USERNAME/ai-stock-trading-bot.git

REM Verify remote was added
git remote -v

echo.
echo Pushing to GitHub...
git push -u origin master

echo.
echo ========================================
echo PUSH COMPLETE!
echo ========================================
echo.
echo Your repository is now on GitHub!
echo URL: https://github.com/YOUR_USERNAME/ai-stock-trading-bot
echo.
pause