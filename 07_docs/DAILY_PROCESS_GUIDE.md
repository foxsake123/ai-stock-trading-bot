# Daily Trading Process Guide - SHORGAN-BOT

## Quick Reference: How to Use ChatGPT Reports

### Option 1: Manual Copy/Paste (Recommended)
**Time: 6:55 AM ET Daily**

1. **Get ChatGPT Report**
   - Go to your ChatGPT TradingAgents conversation
   - Copy the entire daily report

2. **Save to System**
   ```bash
   python 01_trading_system/automation/save_chatgpt_report.py
   ```
   - Paste report when prompted
   - Type 'END' on new line
   - System validates and saves

3. **Verify Save**
   - Check: `02_data/research/reports/pre_market_daily/`
   - Look for: `2025-09-12_chatgpt_report.json`

4. **Pipeline Runs at 7:00 AM**
   - Automatically picks up saved ChatGPT report
   - Executes trades based on report
   - Sends Telegram confirmation

### Option 2: Quick Command Line
```bash
# Copy report to clipboard first, then:
echo "PASTE_REPORT_HERE" | python save_chatgpt_report.py --quick
```

## How the System Knows Which Report to Use

### Priority Order (Implemented)
1. **ChatGPT Report** (`*_chatgpt_report.json`) - Highest Priority
2. **OpenAI Report** (`*_openai_research.json`) - Fallback
3. **Most Recent Report** - Emergency Fallback

### File Naming Convention
- ChatGPT: `YYYY-MM-DD_chatgpt_report.json`
- OpenAI: `YYYY-MM-DD_openai_research.json`
- System matches TODAY's date in filename

## Daily Schedule

### 6:55 AM ET - Pre-Market Prep
1. Copy ChatGPT report
2. Run save script
3. Verify saved correctly

### 7:00 AM ET - Automated Pipeline
- Reads saved ChatGPT report
- Runs multi-agent analysis
- Executes approved trades
- Updates portfolio CSV
- Sends Telegram report

### 9:30 AM ET - Market Open
- Monitor positions
- Check stop losses
- Review execution quality

### 4:00 PM ET - Market Close
- Update portfolio values
- Generate daily report
- Archive trade logs

## Troubleshooting

### Report Not Found
```bash
# Check if file exists
ls 02_data/research/reports/pre_market_daily/*chatgpt*

# If missing, save manually:
python save_chatgpt_report.py
```

### Wrong Date on Report
- System ONLY uses reports matching TODAY's date
- Old reports ignored (except emergency fallback)
- Solution: Re-save with correct date

### Trades Not Executing
1. Check report was saved: `*_chatgpt_report.json`
2. Check pipeline logs: `09_logs/automation/`
3. Verify Alpaca connection
4. Check cash balance

## Manual Override Commands

### Force Pipeline Run
```bash
python 01_trading_system/automation/daily_pre_market_pipeline.py
```

### Test Report Parsing
```bash
python -c "from save_chatgpt_report import ChatGPTReportSaver; s = ChatGPTReportSaver(); s.interactive_save()"
```

### Check What Report Will Be Used
```bash
python -c "
import os
from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')
dir = '02_data/research/reports/pre_market_daily'
chatgpt = f'{dir}/{today}_chatgpt_report.json'
openai = f'{dir}/{today}_openai_research.json'
if os.path.exists(chatgpt):
    print(f'Will use ChatGPT report: {chatgpt}')
elif os.path.exists(openai):
    print(f'Will use OpenAI report: {openai}')
else:
    print('No report found - will generate via API')
"
```

## Important Notes

1. **ChatGPT reports have priority** - System always uses ChatGPT over OpenAI
2. **Date matching is strict** - Must be today's date
3. **Manual save required** - No automatic ChatGPT retrieval
4. **7 AM automation works** - But needs report saved first
5. **Backup everything** - Reports saved with timestamp

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| No trades executed | No report saved | Save ChatGPT report before 7 AM |
| Wrong trades executed | Using OpenAI instead | Ensure ChatGPT report saved |
| Old trades executed | Using yesterday's report | Save today's report |
| Parse errors | Format changed | Check parser in save_chatgpt_report.py |

## Contact & Logs
- Telegram alerts: Check bot messages
- System logs: `09_logs/automation/`
- Trade logs: `08_trading_logs/trades/`
- Portfolio: `02_data/portfolio/positions/`