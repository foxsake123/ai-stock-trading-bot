# ChatGPT Report Automation Setup Guide

## Option 1: Browser Extension (RECOMMENDED)

### Step 1: Install Extension
1. Open Chrome browser
2. Go to `chrome://extensions/`
3. Enable "Developer mode" (top right)
4. Click "Load unpacked"
5. Select folder: `01_trading_system/automation/chatgpt_extension`

### Step 2: Start Local Server
```bash
# Start the report server
python 01_trading_system/automation/chatgpt_report_server.py

# Server runs on http://localhost:8888
# Keep this running while trading
```

### Step 3: Configure Extension
1. Go to ChatGPT.com
2. Click the extension icon (puzzle piece)
3. Click "Test Server Connection"
4. Enable "Auto-detect reports"

### Step 4: Auto-Capture Reports
- Extension automatically detects trading reports
- Reports saved to `02_data/research/reports/pre_market_daily/`
- No manual copying needed!

## Option 2: Selenium Automation (ADVANCED)

### Setup Requirements
```bash
pip install selenium
# Download ChromeDriver from https://chromedriver.chromium.org/
```

### Usage
```bash
# First time (saves cookies)
python 01_trading_system/automation/chatgpt_selenium_fetcher.py

# With specific conversation URL
python chatgpt_selenium_fetcher.py "https://chatgpt.com/c/your-conversation-id"
```

### Schedule Automation
Add to Windows Task Scheduler:
- Time: 6:55 AM ET
- Action: Run Python script
- Arguments: Your conversation URL

## How It Works

### Automation Flow
```
6:55 AM: ChatGPT generates report
6:55 AM: Extension/Selenium captures report
6:56 AM: Report saved as YYYY-MM-DD_chatgpt_report.json
7:00 AM: Daily pipeline reads report
7:01 AM: Trades executed automatically
7:02 AM: Telegram confirmation sent
```

### File Structure
```
02_data/research/reports/pre_market_daily/
├── 2025-09-12_chatgpt_report.json        # Today's report
├── 2025-09-12_chatgpt_report_070155.json # Backup with timestamp
└── 2025-09-11_chatgpt_report.json        # Yesterday's report
```

## Verification Commands

### Check Server Status
```bash
curl http://localhost:8888/health
```

### Test Report Parsing
```bash
curl -X POST http://localhost:8888/save_report \
  -H "Content-Type: application/json" \
  -d '{"text": "RCAT Long Entry: $10.88 Stop: $9.80 Target: $13.50"}'
```

### List Saved Reports
```bash
curl http://localhost:8888/list_reports
```

## Troubleshooting

### Extension Issues
1. **Report not detected**: Check if keywords present (symbol, entry, stop)
2. **Server connection failed**: Ensure server running on port 8888
3. **Permission denied**: Allow ChatGPT.com in extension permissions

### Server Issues
1. **Port 8888 in use**: Change port in both server.py and extension
2. **CORS errors**: Server includes CORS headers for browser requests
3. **File permissions**: Check write access to research directory

### Selenium Issues
1. **ChromeDriver not found**: Download and add to PATH
2. **Login required**: Run manually first to save cookies
3. **Conversation not found**: Use specific conversation URL

## Security Notes

- Extension only runs on ChatGPT.com
- Local server only accepts localhost connections
- No data sent to external servers
- Cookies stored locally for session persistence

## Performance

- Extension: ~1 second detection time
- Selenium: ~30 seconds full cycle
- Server: <100ms processing time
- Daily pipeline: Unchanged (fast startup)

## Backup Strategy

- Primary: `YYYY-MM-DD_chatgpt_report.json` (overwrites daily)
- Backup: `YYYY-MM-DD_chatgpt_report_HHMMSS.json` (unique timestamps)
- All reports kept for audit trail