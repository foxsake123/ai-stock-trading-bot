# ChatGPT Trading Report Automation Guide
## Complete Process Documentation

---

## 📊 OVERVIEW

The ChatGPT integration provides AI-powered trade recommendations using the TradingAgents framework. We've built multiple automation layers to minimize manual work.

---

## 🔄 CURRENT PROCESS FLOW

```mermaid
[ChatGPT] → [Automation Options] → [Parse Trades] → [Daily Execution]
```

### Three Automation Levels:

1. **Fully Automated** (New - Selenium)
2. **Semi-Automated** (Browser Extension)
3. **Manual Fallback** (Copy/Paste)

---

## 🚀 METHOD 1: FULLY AUTOMATED (RECOMMENDED)

### Setup (One-Time)
```bash
# Install dependencies
pip install selenium undetected-chromedriver

# First run (requires manual login)
python scripts-and-data/automation/automated_chatgpt_fetcher.py
```

### Daily Automated Fetch
```bash
# Option 1: Run batch file
scripts-and-data/automation/fetch_chatgpt_trades.bat

# Option 2: Direct Python
python scripts-and-data/automation/automated_chatgpt_fetcher.py
```

### Schedule with Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task: "ChatGPT Trade Fetcher"
3. Trigger: Daily at 6:45 AM
4. Action: Start `fetch_chatgpt_trades.bat`
5. Enable "Run whether user is logged on or not"

### How It Works
- Uses Selenium with undetected-chromedriver to bypass anti-bot
- Maintains persistent Chrome profile for login session
- Sends structured prompt to ChatGPT
- Parses response tables for trades
- Saves to `scripts-and-data/daily-json/chatgpt/`

---

## 🌐 METHOD 2: BROWSER EXTENSION (BACKUP)

### Setup
1. **Start Local Server**
   ```bash
   python scripts-and-data/automation/chatgpt_report_server_fixed.py
   # Runs on http://localhost:8888
   ```

2. **Install Chrome Extension**
   - Open `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select: `chatgpt_extension` folder

3. **Use Extension**
   - Go to ChatGPT.com
   - Ask for trading recommendations
   - Look for green "🟢 Server Connected" indicator
   - Click purple "📊 Extract Trading Report" button

### Visual Indicators
- 🟢 Green = Server connected, ready to capture
- 🔴 Red = Server disconnected, needs restart
- 📊 Purple button = Click to extract report

---

## 📝 METHOD 3: MANUAL FALLBACK

### When Automation Fails
```bash
# Run manual extractor
python scripts-and-data/automation/save_chatgpt_report.py

# Follow prompts to paste report
```

---

## 🎯 CHATGPT PROMPT TEMPLATE

Use this exact prompt for consistent results:

```
You are TradingAgents, an expert AI trading system. Please analyze the market and provide today's trading recommendations in the following format:

## DEE-BOT TRADES (S&P 100 Defensive)
Strategy: Beta-neutral, LONG-ONLY, $100K portfolio
| Symbol | Action | Shares | Entry | Stop | Target | Rationale |
|--------|--------|--------|-------|------|--------|-----------|
[Provide 5 defensive stock recommendations]

## SHORGAN-BOT TRADES (Catalyst Trading)
Strategy: Event-driven momentum, $100K portfolio
| Symbol | Action | Shares | Entry | Stop | Target | Catalyst |
|--------|--------|--------|-------|------|--------|----------|
[Provide 7-10 catalyst-driven recommendations]

Focus on:
- Earnings announcements
- FDA approvals
- Short squeeze setups
- Technical breakouts
- M&A activity
```

---

## 📂 OUTPUT LOCATION

All ChatGPT reports are saved to:
```
scripts-and-data/daily-json/chatgpt/
├── chatgpt_report_2025-09-29.json      # Daily file (overwrites)
└── chatgpt_report_2025-09-29_084532.json  # Timestamped backup
```

### JSON Structure:
```json
{
  "date": "2025-09-29",
  "time": "08:45:32",
  "source": "ChatGPT TradingAgents",
  "trades": [
    {
      "symbol": "AAPL",
      "action": "BUY",
      "shares": 50,
      "entry": 150.00,
      "stop": 145.00,
      "target": 160.00,
      "rationale": "Strong iPhone 16 sales"
    }
  ],
  "trade_count": 15
}
```

---

## 🔗 INTEGRATION WITH TRADING SYSTEM

### Automatic Integration
The `generate_todays_trades.py` script automatically:
1. Checks for ChatGPT reports in JSON directory
2. Parses and validates trades
3. Incorporates into TODAYS_TRADES markdown
4. Falls back to multi-agent consensus if no ChatGPT data

### Manual Override
To force use of ChatGPT recommendations:
```python
# In generate_todays_trades.py
chatgpt_data = self.get_latest_chatgpt_recommendations()
if chatgpt_data:
    # Use ChatGPT trades
    return chatgpt_data['trades']
```

---

## 📅 DAILY SCHEDULE

### Optimal Timing
```
6:45 AM - Automated ChatGPT fetch (pre-market analysis)
7:30 AM - Multi-agent consensus (if ChatGPT fails)
8:45 AM - Final ChatGPT fetch (latest data)
9:00 AM - Generate TODAYS_TRADES file
9:30 AM - Execute trades via execute_daily_trades.py
```

### Windows Task Scheduler Setup
Create 3 tasks:

1. **ChatGPT Morning Fetch** (6:45 AM)
   - Program: `fetch_chatgpt_trades.bat`

2. **ChatGPT Final Fetch** (8:45 AM)
   - Program: `fetch_chatgpt_trades.bat`

3. **Trade Generation** (9:00 AM)
   - Program: `python scripts-and-data/automation/generate_todays_trades.py`

---

## 🔧 TROUBLESHOOTING

### Issue: Selenium Detection
**Solution**: The script uses undetected-chromedriver to bypass detection

### Issue: Login Required Each Time
**Solution**: Script uses persistent Chrome profile to maintain session

### Issue: Response Not Parsing
**Solution**: Ensure ChatGPT uses exact table format with | delimiters

### Issue: Server Connection Failed
**Solution**: Check if port 8888 is available:
```bash
netstat -an | findstr :8888
```

### Issue: No Trades Extracted
**Solution**: Check raw response in JSON file for format issues

---

## ✅ VERIFICATION CHECKLIST

### Automated Fetch
- [ ] Chrome profile created in `chrome_profile/`
- [ ] First manual login completed
- [ ] Selenium fetches response successfully
- [ ] Trades parsed and saved to JSON
- [ ] Task Scheduler configured

### Extension Backup
- [ ] Server running on port 8888
- [ ] Extension shows green indicator
- [ ] Extract button visible
- [ ] Reports saved to JSON directory

### Integration
- [ ] generate_todays_trades.py finds ChatGPT reports
- [ ] Trades incorporated into daily markdown
- [ ] Execution at 9:30 AM includes ChatGPT picks

---

## 📈 SUCCESS METRICS

### Target Performance
- Automation Success Rate: >90%
- Trade Extraction Accuracy: >95%
- Daily Fetch Time: <2 minutes
- Zero manual intervention (after initial setup)

### Current Status
- Selenium automation: ✅ Implemented
- Browser extension: ✅ Working backup
- Manual fallback: ✅ Available
- System integration: ✅ Complete

---

## 🚀 QUICK START COMMANDS

```bash
# One-time setup
pip install selenium undetected-chromedriver

# Daily automated fetch
scripts-and-data/automation/fetch_chatgpt_trades.bat

# Verify output
dir scripts-and-data\daily-json\chatgpt\

# Manual server (if needed)
python scripts-and-data/automation/chatgpt_report_server_fixed.py

# Generate trades with ChatGPT data
python scripts-and-data/automation/generate_todays_trades.py
```

---

*Last Updated: September 29, 2025*
*Status: FULLY AUTOMATED with multiple fallback options*