# ChatGPT Chrome Extension Setup Guide
## Post-Market Report Automation

### ✅ Current Status (Sept 16, 2025, 10:16 PM ET)
- **Server Status**: ✅ RUNNING on http://localhost:8888
- **Extension**: Installed but needs reconnection
- **Scheduled Reports**: Set for 4:30 PM ET daily

---

## 🔧 Quick Fix Steps

### Step 1: Verify Server is Running
```bash
# Check server status
curl http://localhost:8888/health

# Or manually start server if needed
cd C:\Users\shorg\ai-stock-trading-bot\01_trading_system\automation
python chatgpt_report_server.py
```

### Step 2: Reconnect Chrome Extension
1. Open Chrome and go to `chrome://extensions/`
2. Find "ChatGPT Trading Report Extractor"
3. Click "Details" → "Reload"
4. Make sure it's enabled
5. Go to https://chatgpt.com
6. Click the extension icon in toolbar
7. You should see "Server Status: Connected ✓"

### Step 3: Test Connection
1. In ChatGPT, ask for a trading report with keywords like:
   - "Generate RCAT trade"
   - "TradingAgents report"
   - "Symbol: AAPL, Entry: $150"
2. The extension should automatically detect and send to server
3. Check server logs for confirmation

---

## 📅 Automated Post-Market Reports

### Schedule Configuration
- **Time**: 4:30 PM ET (16:30) Monday-Friday
- **Reports Generated**:
  1. Comprehensive post-market analysis
  2. Daily performance summary
  3. Upcoming catalyst alerts
  4. Risk assessment
- **Delivery**: Telegram notifications

### To Enable Automation
```batch
# Run this to set up Windows Task Scheduler
C:\Users\shorg\ai-stock-trading-bot\setup_4_30pm_reports.bat
```

### Manual Test
```batch
# Test the automated report generation
C:\Users\shorg\ai-stock-trading-bot\automated_post_market_4_30pm.bat
```

---

## 🐛 Troubleshooting

### Extension Shows "Not Connected"
1. **Check Server Port**:
   ```powershell
   Get-NetTCPConnection -LocalPort 8888
   ```

2. **Check CORS Headers** - Server should allow localhost:
   ```python
   # In chatgpt_report_server.py
   @app.after_request
   def after_request(response):
       response.headers.add('Access-Control-Allow-Origin', '*')
       return response
   ```

3. **Check Extension Permissions**:
   - Must have access to `http://localhost:8888/*`
   - Must have access to `https://chatgpt.com/*`

### Server Not Starting
1. **Port Already in Use**:
   ```batch
   # Kill process using port 8888
   for /f "tokens=5" %a in ('netstat -aon ^| findstr :8888') do taskkill /F /PID %a
   ```

2. **Python Dependencies**:
   ```bash
   pip install flask flask-cors
   ```

### Extension Not Detecting Reports
- The extension looks for keywords: RCAT, trade, entry, stop, target, symbol, TradingAgents
- Must have trading-related content with symbols and prices
- Check console logs: F12 → Console tab on ChatGPT page

---

## 📊 What Happens at 4:30 PM ET

1. **Windows Task Scheduler triggers** `automated_post_market_4_30pm.bat`
2. **Script checks** if ChatGPT server is running (starts if not)
3. **Generates reports**:
   - Portfolio values for DEE-BOT and SHORGAN-BOT
   - P&L analysis and best/worst performers
   - Upcoming catalyst events
   - Risk assessment
4. **Sends to Telegram** automatically
5. **Saves local copies** in `02_data/research/reports/`

---

## 🔄 Integration with ChatGPT Reports

When you generate reports in ChatGPT:
1. The extension detects trading content automatically
2. Sends to local server at http://localhost:8888
3. Server processes and saves to JSON format
4. Can be included in automated 4:30 PM reports

### Expected ChatGPT Report Format
```
TradingAgents Report - [Date]
Symbol: AAPL
Action: LONG
Entry: $150.00
Stop: $145.00
Target: $160.00
Confidence: HIGH
```

---

## ✅ Verification Checklist

- [ ] Server running on port 8888
- [ ] Extension shows "Connected" status
- [ ] Test report successfully captured
- [ ] Windows Task created for 4:30 PM
- [ ] Telegram receiving test messages
- [ ] Reports saving to local directory

---

## 📞 Support

If issues persist:
1. Check server logs in console window
2. Check Chrome DevTools console on ChatGPT page
3. Verify all files in `01_trading_system/automation/chatgpt_extension/`
4. Restart both server and Chrome extension