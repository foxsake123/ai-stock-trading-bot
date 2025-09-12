# Chrome Extension Installation Guide

## Step 1: Start the Server ✅
Server is already running on http://localhost:8888

## Step 2: Install the Chrome Extension

### Method 1: Load Unpacked Extension
1. **Open Chrome** and go to `chrome://extensions/`
2. **Enable Developer Mode** (toggle switch in top-right corner)
3. **Click "Load unpacked"**
4. **Navigate to and select this folder**:
   ```
   C:\Users\shorg\ai-stock-trading-bot\01_trading_system\automation\chatgpt_extension
   ```
5. **Click "Select Folder"**

### Method 2: Drag and Drop
1. Open Windows Explorer
2. Navigate to: `C:\Users\shorg\ai-stock-trading-bot\01_trading_system\automation\chatgpt_extension`
3. Drag the entire `chatgpt_extension` folder to Chrome's extensions page

## Step 3: Configure Extension

1. **Go to ChatGPT.com** (https://chatgpt.com)
2. **Click the extension icon** (puzzle piece in Chrome toolbar)
3. **Click "Test Server Connection"** - should show "Server connected successfully!"
4. **Enable "Auto-detect reports"** checkbox
5. **Verify Server URL** shows `http://localhost:8888`

## Step 4: Test the Extension

### Manual Test
1. Go to your ChatGPT TradingAgents conversation
2. Generate or view a trading report with symbols like RCAT
3. Look for green button: "📊 Extract Trading Report"
4. Click the button - should show "✅ Report Saved!"

### Auto-Detection Test
1. Generate a new trading report in ChatGPT
2. Extension should automatically detect it (no action needed)
3. Check the server console for "Successfully processed report"

## Step 5: Verify Files Are Saved

Check this folder for saved reports:
```
C:\Users\shorg\ai-stock-trading-bot\02_data\research\reports\pre_market_daily\
```

Should see files like:
- `2025-09-12_chatgpt_report.json`
- `2025-09-12_chatgpt_report_143355.json` (backup)

## Troubleshooting

### Extension Not Appearing
- Refresh Chrome extensions page
- Make sure Developer Mode is enabled
- Check if folder path is correct

### Server Connection Failed
- Verify server is running (check console window)
- Try restarting server: Run `START_SERVER.bat`
- Check if port 8888 is blocked by firewall

### Reports Not Auto-Detected
- Make sure "Auto-detect reports" is enabled
- Check if your report contains trading keywords (symbol, entry, stop)
- Try manual extraction button first

### No Files Saved
- Check write permissions on research folder
- Verify server console shows "Report saved to..."
- Look for error messages in server logs

## Success Indicators

✅ Extension icon appears in Chrome toolbar
✅ Server connection test passes
✅ Manual extraction works
✅ Files appear in research folder
✅ Auto-detection works (no manual action needed)

## Daily Workflow (Once Set Up)

1. **6:55 AM**: Get your ChatGPT trading report as usual
2. **Automatic**: Extension detects and saves report
3. **7:00 AM**: Daily pipeline picks up saved report
4. **Automatic**: Trades execute based on report

**No more manual copy/paste needed!**

## Need Help?

- Server logs: Check the console window where server is running
- Extension logs: Right-click extension → "Inspect popup" → Console tab
- File location: `02_data\research\reports\pre_market_daily\`