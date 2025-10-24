# Performance Graph Generation Guide
**Last Updated**: October 23, 2025

---

## Overview

The performance graph system generates professional visualizations comparing:
- **DEE-BOT** (Defensive Strategy)
- **SHORGAN-BOT** (Aggressive Strategy)
- **Combined Portfolio** (Both strategies)
- **S&P 500 Benchmark** (SPY)

All portfolios are indexed to start at $100 for easy comparison.

---

## Manual Generation

### Generate Current Performance Graph

```bash
# From repository root
python scripts/performance/generate_performance_graph.py
```

**Output**:
- Graph saved to: `performance_results.png` (root directory)
- Console displays performance metrics
- 300 DPI high-quality PNG

**Example Output**:
```
Generating Performance Comparison Graph...
Loaded 15 data points from 2025-10-09 to 2025-10-23
Downloading S&P 500 data from 2025-10-09 to 2025-10-23...
Successfully fetched 11 days of SPY data from yfinance
S&P 500 benchmark data merged successfully
Performance graph saved to: performance_results.png

============================================================
PERFORMANCE METRICS
============================================================
Combined Portfolio:  $207,289.76 (+3.64%)
DEE-BOT (Defensive): $102,772.15 (+2.77%)
SHORGAN-BOT (Aggr.): $104,517.61 (+4.52%)
S&P 500 Benchmark:   $201,234.50 (+0.62%)

Alpha vs S&P 500:    +3.02%
============================================================
```

---

## Automated Daily Generation

### Setup Task Scheduler (Windows)

**One-time setup** (runs at 4:30 PM ET daily):

```batch
# Run as Administrator
scripts\windows\setup_performance_graph.bat
```

This creates a Windows Task Scheduler entry that automatically:
1. Runs at **4:30 PM ET** daily (after market close at 4:00 PM)
2. Fetches latest portfolio values from Alpaca
3. Downloads S&P 500 benchmark data
4. Generates updated performance graph
5. Saves to `performance_results.png`

### Verify Task Created

```batch
# Check if task exists
schtasks /query /tn "AI Trading - Daily Performance Graph"

# Run task manually now (test)
schtasks /run /tn "AI Trading - Daily Performance Graph"

# View task output
type %TEMP%\ai_trading_graph.log
```

### Remove Automation

```batch
# Delete the scheduled task
schtasks /delete /tn "AI Trading - Daily Performance Graph" /f
```

---

## How It Works

### Data Sources

**Portfolio Values** (Alpaca API):
```python
# Fetches current portfolio values
DEE-BOT Account:     PA36XW8J7YE9
SHORGAN-BOT Account: PA3JDHT257IL

# From environment variables
ALPACA_API_KEY_DEE
ALPACA_SECRET_KEY_DEE
ALPACA_API_KEY_SHORGAN
ALPACA_SECRET_KEY_SHORGAN
```

**Historical Performance** (Local JSON):
```
data/daily/performance/performance_history.json
```

**S&P 500 Benchmark** (Multiple Sources):
1. **yfinance** (Yahoo Finance) - Free, usually works
2. **Alpha Vantage** - Fallback API
3. **Alpaca API** (IEX feed) - Fallback
4. **Financial Datasets API** - Premium fallback ($49/month)

### Performance Calculation

**Indexed Values**:
```python
# All portfolios start at $100 baseline
indexed_value = (current_value / starting_value) * 100

# Starting values
DEE-BOT:     $100,000 → $100 indexed
SHORGAN-BOT: $100,000 → $100 indexed
Combined:    $200,000 → $100 indexed
S&P 500:     SPY price → $100 indexed
```

**Metrics Displayed**:
- Final indexed value (e.g., $103.64 = +3.64%)
- Absolute return percentage
- Alpha vs S&P 500 (portfolio return - benchmark return)

---

## Graph Features

### Visual Elements

1. **Combined Portfolio** (Blue solid line, circles)
   - Main performance metric
   - Sum of DEE-BOT + SHORGAN-BOT

2. **DEE-BOT** (Green dashed line, squares)
   - Defensive strategy
   - Target: Beta 0.3-0.7
   - Lower volatility

3. **SHORGAN-BOT** (Red dashed line, triangles)
   - Aggressive catalyst strategy
   - Higher risk/reward
   - Event-driven trades

4. **S&P 500** (Orange dotted line, diamonds)
   - Benchmark comparison
   - Market-neutral comparison

5. **Baseline** (Gray dashed line)
   - Starting value ($100)
   - Reference line

### Performance Summary Box

Located top-left corner:
```
Performance Summary (as of 2025-10-23):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Combined:    $103.64 (+3.64%)
DEE-BOT:     $102.77 (+2.77%)
SHORGAN:     $104.52 (+4.52%)
S&P 500:     $100.62 (+0.62%)
```

---

## Customization

### Change Graph Location

Edit `scripts/performance/generate_performance_graph.py`:

```python
# Line 24
RESULTS_PATH = Path("performance_results.png")

# Change to:
RESULTS_PATH = Path("reports/performance/graph.png")
```

### Change Starting Capital

Edit initial capital constants:

```python
# Lines 34-36
INITIAL_CAPITAL_DEE = 100000.0
INITIAL_CAPITAL_SHORGAN = 100000.0
INITIAL_CAPITAL_COMBINED = 200000.0
```

### Change Graph Styling

Edit plot function (lines 354-454):

```python
# Line 358 - Figure size
fig, ax = plt.subplots(figsize=(14, 8))

# Line 370 - Line colors
color='#2E86AB'  # Blue
color='#06A77D'  # Green
color='#D62839'  # Red
color='#F77F00'  # Orange

# Line 437 - DPI (resolution)
plt.savefig(RESULTS_PATH, dpi=300, bbox_inches='tight')
```

---

## Troubleshooting

### Issue: No data available

**Error**:
```
No performance data available. Run trading system first to generate data.
```

**Solution**:
```bash
# Generate performance history first
python scripts/performance/track_daily_performance.py

# Then generate graph
python scripts/performance/generate_performance_graph.py
```

### Issue: S&P 500 data unavailable

**Error**:
```
yfinance failed: HTTP Error 429
Alpha Vantage failed: Rate limit exceeded
```

**Solution**:
- Graph will still generate without benchmark
- Wait 1 minute and try again
- Or use Financial Datasets API (set `FINANCIAL_DATASETS_API_KEY` in `.env`)

### Issue: Alpaca API connection failed

**Error**:
```
Error fetching portfolio values: Unauthorized
```

**Solution**:
```bash
# Verify environment variables
python tests/manual/test_alpaca_dee_bot.py
python tests/manual/test_alpaca_shorgan_bot.py

# Check .env file contains:
ALPACA_API_KEY_DEE=PKxxxxx
ALPACA_SECRET_KEY_DEE=xxxxx
ALPACA_API_KEY_SHORGAN=PKxxxxx
ALPACA_SECRET_KEY_SHORGAN=xxxxx
```

### Issue: Task Scheduler not running

**Symptoms**:
- Graph not updating at 4:30 PM
- Task shows "Never" as last run time

**Solution**:
```batch
# Check task status
schtasks /query /tn "AI Trading - Daily Performance Graph" /v

# Run manually to test
schtasks /run /tn "AI Trading - Daily Performance Graph"

# Check Windows Event Viewer:
eventvwr.msc → Task Scheduler logs
```

### Issue: Graph file locked/can't save

**Error**:
```
PermissionError: [Errno 13] Permission denied: 'performance_results.png'
```

**Solution**:
- Close any image viewers showing the graph
- Close Excel if graph is embedded
- Run script as Administrator
- Or change output path to different location

---

## Integration with Dashboard

### Embed in Web Dashboard

Add to `web_dashboard.py`:

```python
from flask import send_file

@app.route('/performance-graph')
def performance_graph():
    """Serve the latest performance graph"""
    graph_path = 'performance_results.png'

    if not os.path.exists(graph_path):
        # Generate on-demand if missing
        import subprocess
        subprocess.run(['python', 'scripts/performance/generate_performance_graph.py'])

    return send_file(graph_path, mimetype='image/png')
```

Add to HTML template:

```html
<h2>Performance Visualization</h2>
<img src="/performance-graph" alt="Performance Graph" style="max-width: 100%;">
<p>Last updated: {{ last_updated }}</p>
```

---

## Command Reference

**Generate graph manually**:
```bash
python scripts/performance/generate_performance_graph.py
```

**Setup daily automation (4:30 PM ET)**:
```batch
scripts\windows\setup_performance_graph.bat
```

**Run scheduled task now**:
```batch
schtasks /run /tn "AI Trading - Daily Performance Graph"
```

**Check task status**:
```batch
schtasks /query /tn "AI Trading - Daily Performance Graph" /v
```

**Delete automation**:
```batch
schtasks /delete /tn "AI Trading - Daily Performance Graph" /f
```

---

## See Also

- `scripts/performance/track_daily_performance.py` - Record daily portfolio snapshots
- `scripts/performance/get_portfolio_status.py` - View current portfolio status
- `scripts/performance/backtest_recommendations.py` - Backtest historical recommendations
- `web_dashboard.py` - Web interface for viewing reports

---

**Created**: October 23, 2025
**Status**: Production-ready, tested, automated
