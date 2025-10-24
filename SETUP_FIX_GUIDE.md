# Setup Issues - Fix Guide

## Issues Encountered

Your setup script encountered several issues. Here's how to fix them:

### Issue 1: Alpaca API Keys - Multi-Account Architecture ✅

**Important**: This trading bot uses **TWO separate Alpaca accounts**:
- **DEE-BOT**: Beta-neutral defensive strategies (Account 1)
- **SHORGAN-BOT**: Catalyst-driven strategies (Account 2)

**Current Status**: ✅ Both existing API keys are working correctly!

**Your Accounts**:
```
DEE-BOT Account: PA36XW8J7YE9
  Equity: $102,816.33
  Cash: $48,999.58

SHORGAN-BOT Account: PA3JDHT257IL
  Equity: $104,095.90
  Cash: $89,309.51
```

**No Action Required** - Your API keys are already configured correctly in `.env`:

```bash
# DEE-BOT Paper Trading API (Account 1)
ALPACA_API_KEY_DEE=PKLW68W7RZJFTXV8LJO8
ALPACA_SECRET_KEY_DEE=HV3epwO5AqhqNQEiv3piSOVGD40ly0rW98whdGMv

# SHORGAN-BOT Paper Trading API (Account 2)
ALPACA_API_KEY_SHORGAN=PKDNSGIY71EZGG40EHOV
ALPACA_SECRET_KEY_SHORGAN=Z0Kz1Ay7K9uXSkXomVRxl8BavEGqsfiv3qQvLhx9
```

**Test Both Accounts**:
```bash
python test_alpaca_dee_bot.py
```

You should see SUCCESS for both DEE-BOT and SHORGAN-BOT.

**Only If You Need to Regenerate Keys**:

1. **Go to Alpaca Paper Trading Dashboard**:
   https://app.alpaca.markets/paper/dashboard/overview

2. **Generate Keys for BOTH Accounts**:
   - Log in to Account 1 (DEE-BOT) - Generate API keys
   - Log in to Account 2 (SHORGAN-BOT) - Generate API keys
   - **Important**: The secret key is only shown ONCE - copy it immediately!

3. **Update .env File**:
   ```bash
   # Open .env in a text editor
   notepad .env

   # Update DEE-BOT keys:
   ALPACA_API_KEY_DEE=your-new-dee-bot-api-key
   ALPACA_SECRET_KEY_DEE=your-new-dee-bot-secret-key

   # Update SHORGAN-BOT keys:
   ALPACA_API_KEY_SHORGAN=your-new-shorgan-bot-api-key
   ALPACA_SECRET_KEY_SHORGAN=your-new-shorgan-bot-secret-key
   ```

4. **Test Both Accounts**:
   ```bash
   python test_alpaca_dee_bot.py
   ```

---

### Issue 2: Unicode Encoding Error on Windows ❌

**Error**: `'charmap' codec can't encode character '\u2713'`

**Cause**: Windows PowerShell doesn't support Unicode characters (✓, 🔴, etc.) in default encoding.

**Solution 1 - Use UTF-8 PowerShell** (Recommended):
```powershell
# Set PowerShell to UTF-8
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Run setup again
python scripts/setup.py
```

**Solution 2 - Use Command Prompt** (Alternative):
```cmd
# Open Command Prompt (cmd.exe) instead of PowerShell
chcp 65001

# Run setup
python scripts/setup.py
```

**Solution 3 - Use Windows Terminal** (Best):
- Download Windows Terminal from Microsoft Store
- It has native UTF-8 support
- Run setup from there

---

### Issue 3: Task Scheduler Timeout ⚠️

**Error**: `Command timed out`

**Cause**: Windows Task Scheduler batch script took too long (>5 minutes).

**Solution - Manual Task Scheduler Setup**:

1. **Open Task Scheduler**:
   - Press `Win + R`
   - Type `taskschd.msc`
   - Press Enter

2. **Create New Task**:
   - Click "Create Basic Task"
   - Name: `AI Trading Bot - Daily Pipeline`
   - Description: `Runs daily trading bot pipeline at 6:00 AM ET`

3. **Set Trigger**:
   - Trigger: Daily
   - Start time: 6:00 AM
   - Recur every: 1 days

4. **Set Action**:
   - Action: Start a program
   - Program/script: `python`
   - Add arguments: `C:\Users\shorg\ai-stock-trading-bot\scripts\daily_pipeline.py`
   - Start in: `C:\Users\shorg\ai-stock-trading-bot`

5. **Finish and Test**:
   - Click "Finish"
   - Right-click the task → "Run" to test

---

### Issue 4: Email Configuration ⚠️

**Problem**: You entered `shorgan0011@gmail.com` as SMTP host instead of `smtp.gmail.com`

**Fixed**: Already corrected in `.env` file:
```bash
SMTP_HOST=smtp.gmail.com  # ✓ Correct
SMTP_PORT=587             # ✓ Correct
```

**Gmail App Password Required**:

If using Gmail, you need an App Password (not your regular password):

1. Go to: https://myaccount.google.com/apppasswords
2. Select app: "Mail"
3. Select device: "Windows Computer"
4. Click "Generate"
5. Copy the 16-character password
6. Update `.env`:
   ```
   SMTP_PASSWORD=your-16-char-app-password-here
   ```

---

## Complete Manual Setup (Alternative)

If the interactive setup keeps failing, follow these manual steps:

### Step 1: Fix API Keys

```bash
# Edit .env file
notepad .env

# Update with valid keys:
ALPACA_API_KEY=YOUR_VALID_KEY
ALPACA_SECRET_KEY=YOUR_VALID_SECRET
```

### Step 2: Update Config Files

```bash
# Edit main config
notepad configs/config.yaml

# Set portfolio size:
trading:
  portfolio_size: 2000000
  bots:
    dee_bot:
      enabled: true
      allocation_pct: 50
    shorgan_bot:
      enabled: true
      allocation_pct: 50
```

### Step 3: Create Watchlists

```bash
# Create watchlist directory
mkdir data\watchlists

# Create DEE-BOT watchlist
echo # DEE-BOT Defensive Watchlist > data\watchlists\dee_bot_defensive.txt
echo JNJ >> data\watchlists\dee_bot_defensive.txt
echo PG >> data\watchlists\dee_bot_defensive.txt
echo KO >> data\watchlists\dee_bot_defensive.txt

# Create SHORGAN-BOT watchlist
echo # SHORGAN-BOT Catalyst Watchlist > data\watchlists\shorgan_bot_catalysts.txt
echo PTGX >> data\watchlists\shorgan_bot_catalysts.txt
echo SMMT >> data\watchlists\shorgan_bot_catalysts.txt
echo VKTX >> data\watchlists\shorgan_bot_catalysts.txt
```

### Step 4: Test API Connections

```bash
# Test Alpaca
python test_alpaca.py

# Should show: SUCCESS

# Test Anthropic
python -c "import anthropic; print('OK')"

# Test Financial Datasets
python -c "import requests; r = requests.get('https://api.financialdatasets.ai/prices/snapshot?ticker=AAPL', headers={'X-API-KEY': 'c93a9274-4183-446e-a9e1-6befeba1003b'}); print('OK' if r.status_code == 200 else f'ERROR: {r.status_code}')"
```

### Step 5: Run Health Check

```bash
# Run health check (skip emoji issues)
python scripts/health_check.py 2>nul
```

### Step 6: Test Report Generation

```bash
# Generate test report
python scripts/daily_pipeline.py --test

# Check output
type reports\premarket\latest\claude_research.md
```

---

## Quick Fixes Summary

### Fix 1: Alpaca API Keys
```bash
# Get new keys from: https://app.alpaca.markets/paper/dashboard/overview
# Update .env with new keys
# Test: python test_alpaca.py
```

### Fix 2: Unicode Errors
```powershell
# Set UTF-8 encoding
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### Fix 3: Email SMTP (Already Fixed)
```bash
# .env now has correct values:
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

### Fix 4: Task Scheduler
```bash
# Use manual setup (see Issue 3 above)
# Or run manually: python scripts/daily_pipeline.py
```

---

## Verify Setup is Complete

Run these commands to verify everything works:

```bash
# 1. Test Alpaca API
python test_alpaca.py
# Expected: SUCCESS

# 2. Check .env file
type .env | findstr "ALPACA_API_KEY"
# Expected: Valid API key shown

# 3. Test health check
python scripts/health_check.py
# Expected: Health score >60%

# 4. Generate test report
python scripts/daily_pipeline.py --test
# Expected: Report generated in reports/premarket/

# 5. View portfolio status
python scripts/performance/get_portfolio_status.py
# Expected: Portfolio balance shown
```

---

## Next Steps After Fixes

Once all issues are resolved:

1. ✅ Test Alpaca API connection (should succeed)
2. ✅ Verify .env file has correct values
3. ✅ Run health check (should pass)
4. ✅ Generate test report
5. ✅ Set up Task Scheduler manually
6. ✅ Test full pipeline: `python scripts/daily_pipeline.py`

---

## Need Help?

**Common Issues**:
- **Alpaca "unauthorized"**: Regenerate API keys
- **Unicode errors**: Use Windows Terminal or set UTF-8 encoding
- **SMTP errors**: Use Gmail App Password
- **Task Scheduler fails**: Set up manually via GUI

**Resources**:
- Setup Guide: `docs/SETUP_GUIDE.md`
- Quickstart: `QUICKSTART.md`
- Health Check: `python scripts/health_check.py --help`

---

**Last Updated**: October 23, 2025
