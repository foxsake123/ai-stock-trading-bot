# 🤖 Trading Bot Automation Dashboard

## Current Status
- **ChatGPT Report Server**: ✅ Running on http://localhost:8888
- **Chrome Extension**: 🟢 Ready for installation
- **Scheduled Tasks**: 📅 Ready to configure

---

## 📊 Report URLs & Endpoints

### View Reports Online
- **List All Reports**: http://localhost:8888/list_reports
- **Latest Report**: http://localhost:8888/get_latest
- **Server Health**: http://localhost:8888/health

### Report File Locations
```
📁 Daily ChatGPT Reports:
   C:\Users\shorg\ai-stock-trading-bot\02_data\research\reports\pre_market_daily\

📁 Daily Portfolio Reports:
   C:\Users\shorg\ai-stock-trading-bot\07_docs\daily_reports\

📁 Weekly Reports:
   C:\Users\shorg\ai-stock-trading-bot\07_docs\weekly_reports\

📁 P&L History:
   C:\Users\shorg\ai-stock-trading-bot\02_data\portfolio\history\
```

---

## ⏰ Automation Schedule

| Time | Task | Description | Script |
|------|------|-------------|--------|
| **6:50 AM** | Report Server | Starts server for ChatGPT capture | `chatgpt_report_server.py` |
| **6:55 AM** | Manual Action | Generate ChatGPT report | Visit ChatGPT |
| **7:00 AM** | Pre-Market | Executes trades from ChatGPT report | `daily_pre_market_pipeline.py` |
| **4:30 PM** | Post-Market | Updates portfolio & sends summary | `post_market_updater.py` |
| **Sun 2PM** | Weekly Report | Generates performance analysis | `weekly_report_generator.py` |

---

## 🚀 Quick Start Commands

### Start Everything
```bash
# 1. Start report server (keep running)
python 01_trading_system/automation/chatgpt_report_server.py

# 2. Setup all schedules
setup_all_schedules.bat

# 3. Install Chrome extension
# Go to chrome://extensions/ → Load unpacked → Select chatgpt_extension folder
```

### Manual Runs
```bash
# Run pre-market pipeline now
python 01_trading_system/automation/daily_pre_market_pipeline.py

# Generate post-market report now
python 01_trading_system/automation/post_market_updater.py

# Generate weekly report now
python 01_trading_system/automation/weekly_report_generator.py
```

### Check Status
```bash
# View all scheduled tasks
schtasks /query /tn TradingBot*

# Check if server is running
curl http://localhost:8888/health

# View saved reports
curl http://localhost:8888/list_reports
```

---

## 📈 Report Types

### 1. **ChatGPT Trading Reports** (Daily 7AM)
- Source: ChatGPT TradingAgents
- Capture: Chrome Extension (automatic)
- Format: JSON with trades, entries, stops
- Usage: Fed to multi-agent system for execution

### 2. **Post-Market Portfolio Updates** (Daily 4:30PM)
- Updates all position values
- Calculates daily P&L
- Tracks performance metrics
- Sends Telegram summary

### 3. **Weekly Performance Reports** (Sunday 2PM)
- Week's trading summary
- Win/loss analysis
- Position performance ranking
- Risk metrics review

---

## 🔧 Troubleshooting

### Extension Not Capturing
```bash
# Check server is running
curl http://localhost:8888/health

# View server logs (in console window)
# Look for "Successfully processed report"

# Test with sample data
curl -X POST http://localhost:8888/save_report \
  -H "Content-Type: application/json" \
  -d '{"text": "AAPL Entry: $150 Stop: $145 Target: $160"}'
```

### Reports Not Generated
```bash
# Check task scheduler
schtasks /query /tn TradingBot_DailyPreMarket /v

# Run manually to test
python 01_trading_system/automation/daily_pre_market_pipeline.py

# Check logs
dir 09_logs\automation\*.log
```

### View Historical Data
```python
# Python script to view P&L history
import pandas as pd
df = pd.read_csv('02_data/portfolio/history/pnl_history.csv')
print(df.tail(10))
```

---

## 📱 Telegram Notifications

You'll receive automated messages for:
- ✅ Pre-market trade executions (7:00 AM)
- 📊 Post-market summary (4:30 PM)
- 📈 Weekly performance report (Sunday 2:00 PM)
- ⚠️ Error notifications (when issues occur)

---

## 🎯 Daily Workflow

```mermaid
6:50 AM: Server starts
   ↓
6:55 AM: You view ChatGPT report
   ↓
6:55 AM: Extension auto-captures
   ↓
7:00 AM: Pipeline reads report
   ↓
7:01 AM: Trades execute
   ↓
7:02 AM: Telegram confirmation
   ↓
9:30 AM - 4:00 PM: Market hours
   ↓
4:30 PM: Portfolio update
   ↓
4:31 PM: Daily summary sent
```

---

## 💾 Data Persistence

All data is automatically saved:
- Trade history: `08_trading_logs/trades/`
- Portfolio snapshots: `02_data/portfolio/positions/`
- P&L history: `02_data/portfolio/history/`
- Research reports: `02_data/research/reports/`
- Performance reports: `07_docs/`

---

## 🔐 Security Notes

- Server only accepts localhost connections
- No external API access required for capture
- ChatGPT credentials stay in browser
- All data stored locally

---

*Last Updated: September 12, 2025*