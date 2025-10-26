# Saturday Research Setup Guide
**Issue**: No research reports generated on October 26, 2025

---

## Problems Identified

### 1. Anthropic API Key Invalid (CRITICAL)
**Error**: `Error code: 401 - invalid x-api-key`
**Location**: `.env` file, line with `ANTHROPIC_API_KEY`

**Current Status**: API key appears truncated or expired

**Fix Required**:
```bash
# Edit .env file and update with valid Anthropic API key
ANTHROPIC_API_KEY=sk-ant-api03-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Get New Key**:
1. Visit: https://console.anthropic.com/settings/keys
2. Create new API key
3. Copy full key (starts with `sk-ant-api03-`)
4. Paste into `.env` file

---

### 2. Telegram Chat ID Format Wrong
**Error**: `chat not found` (400 error)
**Current**: `TELEGRAM_CHAT_ID=@shorganbot` (username format - won't work)
**Required**: Numeric chat ID

**Fix Required**:
```bash
# Edit .env file - change from username to numeric ID
TELEGRAM_CHAT_ID=1234567890  # Your actual numeric chat ID
```

**Get Your Chat ID**:
1. Message your bot: `@shorganbot`
2. Visit: https://api.telegram.org/bot8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c/getUpdates
3. Look for `"chat":{"id":XXXXXXX}`
4. Copy that number (e.g., 1234567890)
5. Update `.env` file

---

### 3. Task Scheduler Not Set Up
**Status**: No automated tasks found
**Issue**: You updated the script but haven't re-run setup

**Fix Required**:
```batch
# Run as Administrator
cd C:\Users\shorg\ai-stock-trading-bot
scripts\windows\setup_trade_automation.bat
```

**This will create**:
- Weekend Research: Saturday 12:00 PM
- Trade Generation: Weekdays 8:30 AM
- Trade Execution: Weekdays 9:30 AM
- Performance Graph: Weekdays 4:30 PM

---

## Complete Setup Steps

### Step 1: Fix Anthropic API Key (CRITICAL - 2 minutes)

1. **Get new API key**:
   - Visit: https://console.anthropic.com/settings/keys
   - Click "Create Key"
   - Name it: "AI Trading Bot - Oct 2025"
   - Copy the full key (200+ characters)

2. **Update .env file**:
   ```bash
   # Open in notepad
   notepad .env
   
   # Find line with ANTHROPIC_API_KEY
   # Replace entire line with:
   ANTHROPIC_API_KEY=sk-ant-api03-[YOUR_FULL_KEY_HERE]
   
   # Save and close
   ```

### Step 2: Fix Telegram Chat ID (2 minutes)

1. **Get your numeric chat ID**:
   ```bash
   # Method 1: Use Python
   python -c "import requests; print(requests.get('https://api.telegram.org/bot8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c/getUpdates').json())"
   
   # Look for: "chat":{"id":XXXXXXX}
   ```

2. **Update .env file**:
   ```bash
   # Change from
   TELEGRAM_CHAT_ID=@shorganbot
   
   # To (use your actual number)
   TELEGRAM_CHAT_ID=1234567890
   ```

### Step 3: Set Up Task Scheduler (5 minutes)

1. **Open Command Prompt as Administrator**:
   - Press Windows Key + X
   - Click "Terminal (Admin)"

2. **Run setup script**:
   ```batch
   cd C:\Users\shorg\ai-stock-trading-bot
   scripts\windows\setup_trade_automation.bat
   ```

3. **Verify tasks created**:
   ```batch
   schtasks /query /tn "AI Trading - Weekend Research"
   ```

### Step 4: Test Research Generation (10 minutes)

1. **Generate research manually**:
   ```bash
   python scripts/automation/daily_claude_research.py --force
   ```

2. **Expected output**:
   ```
   [+] Generating research for: Monday, October 27, 2025
   [*] Calling Claude API (Opus 4.1 with Extended Thinking)...
   [*] Deep research mode enabled - this may take 3-5 minutes...
   [+] DEE-BOT report complete!
       Markdown: reports/premarket/2025-10-27/claude_research_dee_bot_2025-10-27.md
       PDF: reports/premarket/2025-10-27/claude_research_dee_bot_2025-10-27.pdf
       [+] Telegram PDF sent: DEE-BOT
   
   [+] SHORGAN-BOT report complete!
       Markdown: reports/premarket/2025-10-27/claude_research_shorgan_bot_2025-10-27.md
       PDF: reports/premarket/2025-10-27/claude_research_shorgan_bot_2025-10-27.pdf
       [+] Telegram PDF sent: SHORGAN-BOT
   ```

3. **Check Telegram**:
   - You should receive 2 PDF files
   - One for DEE-BOT research
   - One for SHORGAN-BOT research

---

## Verification Checklist

Before Monday trading:

- [ ] Anthropic API key updated in .env
- [ ] Telegram chat ID updated (numeric format)
- [ ] Task Scheduler tasks created (4 tasks)
- [ ] Research generation tested manually
- [ ] PDFs received in Telegram
- [ ] Research files exist in reports/premarket/2025-10-27/

---

## Automated Schedule (After Setup)

Once setup is complete, this will happen automatically:

**Every Saturday at 12:00 PM**:
- Generate research for Monday
- Send PDFs to Telegram
- Ready for review

**Every Monday at 8:30 AM**:
- Generate trades from Saturday research
- Validate through multi-agent system
- Create TODAYS_TRADES file

**Every Monday at 9:30 AM**:
- Execute approved trades
- Place stop-loss orders
- Send execution summary to Telegram

**Every Weekday at 4:30 PM**:
- Update performance graph
- Track P&L
- Save to reports/performance/

---

## Troubleshooting

### "Invalid API key" error
- Check API key starts with `sk-ant-api03-`
- Verify full key copied (200+ characters)
- Create new key at console.anthropic.com

### "Chat not found" error
- Telegram ID must be numeric (e.g., 1234567890)
- Not username format (@shorganbot won't work)
- Get ID from /getUpdates endpoint

### Task Scheduler issues
- Run Command Prompt as Administrator
- Verify Python path: `C:\Python313\python.exe`
- Check task exists: `schtasks /query /tn "AI Trading - Weekend Research"`

### No PDFs generated
- Check Anthropic API key valid
- Verify markdown files created first
- Check logs in reports/premarket/[date]/

---

## Quick Commands

```bash
# Test research generation
python scripts/automation/daily_claude_research.py --force

# Check Task Scheduler status
schtasks /query /fo TABLE | findstr "AI Trading"

# View portfolio status
python scripts/performance/get_portfolio_status.py

# Cancel all open orders (if needed)
python cancel_stale_orders.py
```

---

**Created**: October 26, 2025, 3:45 PM ET
**Status**: Setup Required Before Monday Trading
