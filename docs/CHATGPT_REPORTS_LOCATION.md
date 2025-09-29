# ChatGPT Deep Research Reports - Location Guide
## Complete Directory of All ChatGPT Trading Analysis

---

## 📍 PRIMARY LOCATIONS

### 1. Current Active Reports (Most Recent)
```
scripts-and-data/daily-json/chatgpt/
├── chatgpt_report_2025-09-23.json     # Monday Sept 23 trades
└── chatgpt_report_2025-09-18.json     # Previous week
```

### 2. Weekly Deep Research PDFs
```
scripts-and-data/data/reports/weekly/weekly-reports/
└── weekly_deep_research_20250922_212526.pdf    # Latest deep research
```

### 3. Daily Pre-Market Reports
```
research/data/reports/pre_market_daily/
├── 2025-09-16_chatgpt_report.pdf
├── 2025-09-16_chatgpt_report.json
└── [Multiple timestamped versions]
```

---

## 📊 REPORT TYPES & FORMATS

### JSON Reports (Trade Recommendations)
Located in multiple directories:
- `scripts-and-data/daily-json/chatgpt/` - Active trading data
- `research/data/reports/pre_market_daily/` - Historical reports
- `docs/index/reports-md/pre-market/2025-09-23/` - Archived copies

### PDF Reports (Deep Analysis)
Key locations:
- `docs/index/reports-pdf/2025-09-23/` - Daily PDFs
- `scripts-and-data/data/reports/weekly/weekly-reports/` - Weekly deep research
- `docs/legacy/07_docs/premarket_reports/` - Historical PDFs

---

## 📅 SEPTEMBER 23, 2025 REPORTS

### Monday's ChatGPT Analysis (Most Recent)
Multiple versions throughout the day:
```
2025-09-23_chatgpt_report.json         # Main file
2025-09-23_chatgpt_report_072738.json  # 7:27 AM
2025-09-23_chatgpt_report_072905.json  # 7:29 AM
2025-09-23_chatgpt_report_072941.json  # 7:29 AM
2025-09-23_chatgpt_report_072949.json  # 7:29 AM
2025-09-23_chatgpt_report_073217.json  # 7:32 AM
2025-09-23_chatgpt_report_073701.json  # 7:37 AM
2025-09-23_chatgpt_report_074205.json  # 7:42 AM
2025-09-23_chatgpt_report_074655.json  # 7:46 AM
2025-09-23_chatgpt_report_080417.json  # 8:04 AM
```

### Trades from Monday Sept 23:
1. **SRRK** - Buy 100 @ $34.50 (FDA decision catalyst)
2. **FBIO** - Buy 700 @ $4.10 (Sept 30 FDA)
3. **RIVN** - Buy 200 @ $15.50 (Q3 deliveries)
4. **IONQ** - Short 50 @ $69.00 (Overhyped)
5. **KSS** - Buy 150 @ $17.00 (Retail turnaround)

---

## 🔬 DEEP RESEARCH PAPERS

### Academic/Research PDFs
```
docs/legacy/07_docs/research_papers/
├── TradingAgents_Multi-Agents LLM Financial Trading.pdf
├── Can Large Language Models Trade - Testing Financial Theories.pdf
└── Trading-R1 -- Financial Trading with LLM Reasoning.pdf
```

---

## 🗂️ ARCHIVED REPORTS STRUCTURE

### Legacy Structure (Before Sept 23)
```
scripts-and-data/automation/legacy/02_data/research/reports/pre_market_daily/
├── 2025-09-17_chatgpt_report.json
├── 2025-09-18_chatgpt_report.json
├── 2025-09-22_chatgpt_report.json
└── 2025-09-23_chatgpt_report.json (multiple versions)
```

### Organized by Date
```
scripts-and-data/data/reports/daily/daily-reports/
├── 2025-09-16/
├── 2025-09-18/
├── 2025-09-20/
└── [Each contains PDFs and JSONs for that day]
```

---

## 🚀 ACCESSING REPORTS PROGRAMMATICALLY

### Read Latest ChatGPT JSON
```python
import json
from pathlib import Path

# Get latest report
report_path = Path('scripts-and-data/daily-json/chatgpt/chatgpt_report_2025-09-23.json')
with open(report_path, 'r') as f:
    data = json.load(f)

# Access trades
for trade in data['trades']:
    print(f"{trade['symbol']}: {trade['action']} {trade['shares']} shares")
```

### Find All ChatGPT Reports
```python
from pathlib import Path

# Find all JSON reports
json_reports = list(Path('.').glob('**/*chatgpt*.json'))
print(f"Found {len(json_reports)} ChatGPT JSON reports")

# Find all PDF reports
pdf_reports = list(Path('.').glob('**/*chatgpt*.pdf'))
print(f"Found {len(pdf_reports)} ChatGPT PDF reports")
```

---

## 📈 INTEGRATION WITH TRADING SYSTEM

### Automated Fetching (New)
```bash
# Automated ChatGPT fetcher
python scripts-and-data/automation/automated_chatgpt_fetcher.py

# Output location
scripts-and-data/daily-json/chatgpt/
```

### Manual Extraction
```bash
# Save ChatGPT report manually
python scripts-and-data/automation/save_chatgpt_report.py
```

### Trade Generation Integration
The `generate_todays_trades.py` script automatically checks:
1. `scripts-and-data/daily-json/chatgpt/` for latest reports
2. Incorporates ChatGPT recommendations into daily trades
3. Falls back to multi-agent consensus if unavailable

---

## 📋 REPORT STATISTICS

### Total Reports Found:
- **JSON Reports**: 44 files
- **PDF Reports**: 43 files
- **Deep Research**: 4 academic papers

### Most Recent Activity:
- Last JSON: September 23, 2025 (Monday)
- Last PDF: September 23, 2025
- Last Weekly Deep Research: September 22, 2025

---

## 🔍 QUICK ACCESS COMMANDS

```bash
# View latest ChatGPT trades
cat scripts-and-data/daily-json/chatgpt/chatgpt_report_2025-09-23.json

# List all ChatGPT JSONs
dir scripts-and-data\daily-json\chatgpt\*.json /b

# Find all PDFs
dir /s *.pdf | findstr chatgpt

# Count all reports
dir /s *chatgpt* | find /c "chatgpt"
```

---

## 📝 NOTES

1. **Multiple Versions**: Same day may have multiple report versions (timestamps)
2. **Legacy Folders**: Older reports in various legacy directories
3. **Format Evolution**: Earlier reports may have different JSON structure
4. **Integration Ready**: All reports accessible to automated trading system

---

*Use this guide to locate any ChatGPT deep research or trading reports*
*Most recent active reports are in scripts-and-data/daily-json/chatgpt/*