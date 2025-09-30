# Performance Tracking & Visualization System

## Overview

Professional performance tracking system inspired by [ChatGPT-Micro-Cap-Experiment](https://github.com/LuckyOne7777/ChatGPT-Micro-Cap-Experiment). Generates comparative visualizations benchmarking DEE-BOT and SHORGAN-BOT against the S&P 500.

## Key Features

- **Dual-Bot Tracking**: Separate performance metrics for DEE-BOT (defensive) and SHORGAN-BOT (aggressive)
- **S&P 500 Benchmark**: Normalized comparison against market index
- **Historical Analysis**: Time-series visualization of portfolio growth
- **Daily Updates**: Automated tracking with CSV export
- **Professional Visualization**: High-resolution graphs with comprehensive metrics

## Quick Start

### Generate Performance Graph

```bash
# Option 1: Run Python script directly
python generate_performance_graph.py

# Option 2: Use batch file (Windows)
GENERATE_PERFORMANCE_GRAPH.bat
```

### Update Portfolio CSV Files

```bash
python scripts-and-data/automation/update_portfolio_csv.py
```

## File Structure

```
ai-stock-trading-bot/
├── generate_performance_graph.py          # Main visualization script
├── performance_results.png                 # Generated performance graph
├── scripts-and-data/
│   ├── automation/
│   │   └── update_portfolio_csv.py        # CSV updater (ChatGPT format)
│   ├── daily-csv/
│   │   ├── dee_bot_portfolio_history.csv  # DEE-BOT daily tracking
│   │   ├── shorgan_bot_portfolio_history.csv  # SHORGAN-BOT tracking
│   │   └── combined_portfolio_history.csv # Combined portfolio
│   └── data/json/
│       └── performance_history.json        # Historical performance data
```

## Data Format

### CSV Structure (Compatible with ChatGPT-Micro-Cap format)

```csv
Date,Ticker,Shares,Buy Price,Cost Basis,Stop Loss,Current Price,Total Value,PnL,Action,Cash Balance,Total Equity,Bot,Side
2025-09-29,AAPL,84,226.91,19061.0,,253.8,21319.2,2258.4,HOLD,,,DEE-BOT,long
2025-09-29,TOTAL,,,,,,109865.5,4465.5,,30615.4,140480.9,DEE-BOT,
```

### JSON Structure (performance_history.json)

```json
{
  "start_date": "2025-09-10",
  "daily_records": [
    {
      "date": "2025-09-10",
      "dee_bot": {
        "value": 100246.38,
        "daily_pnl": 246.38,
        "total_return": 0.25
      },
      "shorgan_bot": {
        "value": 103770.43,
        "daily_pnl": 3493.40,
        "total_return": 3.77
      },
      "combined": {
        "total_value": 204016.81,
        "total_return": 4016.81,
        "total_positions": 14
      }
    }
  ]
}
```

## Performance Metrics

### Calculated Metrics

- **Total Return**: Percentage gain/loss from starting capital
- **Daily P&L**: Day-over-day profit/loss
- **Portfolio Value**: Current market value (positions + cash)
- **Alpha**: Outperformance vs S&P 500 benchmark
- **Position Count**: Number of active holdings
- **Unrealized P&L**: Open position gains/losses

### Visualization Features

- **Line Charts**: Time-series portfolio growth
- **Comparative Analysis**: Side-by-side DEE-BOT vs SHORGAN-BOT
- **Benchmark Overlay**: S&P 500 normalized to same starting capital
- **Performance Summary**: Key metrics text box on graph
- **Professional Styling**: Publication-ready 300 DPI output

## Automation

### Daily Workflow

1. **Morning (9:30 AM)**: Execute trades
2. **During Market**: Monitor positions
3. **Post-Market (4:30 PM)**:
   - Update CSV files: `python scripts-and-data/automation/update_portfolio_csv.py`
   - Generate graph: `python generate_performance_graph.py`
   - Send reports via Telegram

### Scheduled Tasks

Windows Task Scheduler is configured for:
- **9:30 AM**: Trade execution
- **4:30 PM**: Performance update and reporting

## Benchmarking Methodology

### S&P 500 Comparison

Following the ChatGPT-Micro-Cap methodology:

1. **Baseline Normalization**: S&P 500 data normalized to $200,000 starting capital
2. **Date Alignment**: Start date matches first portfolio data point
3. **Forward Fill**: Handle market holidays and missing data
4. **Daily Tracking**: Both portfolio and benchmark updated simultaneously

### Alpha Calculation

```python
alpha = combined_return_pct - sp500_return_pct
```

Positive alpha indicates outperformance vs market.

## Configuration

### Starting Capital

```python
INITIAL_CAPITAL_DEE = 100000.0      # DEE-BOT starting balance
INITIAL_CAPITAL_SHORGAN = 100000.0  # SHORGAN-BOT starting balance
INITIAL_CAPITAL_COMBINED = 200000.0 # Total capital
```

### API Configuration

API keys for both bots are configured in:
- `generate_performance_graph.py` (for live data fetch)
- `.env` file (for automation scripts)

## Troubleshooting

### Issue: "No performance data available"

**Solution**: Ensure `performance_history.json` exists with at least one data point.

```bash
# Check file exists
ls scripts-and-data/data/json/performance_history.json

# Verify JSON structure
cat scripts-and-data/data/json/performance_history.json
```

### Issue: "S&P 500 data unavailable"

**Cause**: yfinance API rate limiting or network issues

**Solution**: Graph will generate without benchmark. S&P 500 will be included when data becomes available.

### Issue: Graph shows incorrect dates

**Solution**: Check that `performance_history.json` has correct date format (`YYYY-MM-DD`)

## Comparison with Reference Repository

### Similarities

✅ CSV-based tracking with TOTAL row
✅ Daily portfolio snapshots
✅ S&P 500 benchmark comparison
✅ Normalized starting capital
✅ Professional matplotlib visualization

### Enhancements

🚀 **Dual-Bot Architecture**: Separate DEE-BOT and SHORGAN-BOT tracking
🚀 **JSON Performance History**: Structured historical data storage
🚀 **Real-time API Integration**: Live portfolio value fetch from Alpaca
🚀 **Automated Updates**: Windows Task Scheduler integration
🚀 **Comprehensive Metrics**: Additional analytics (alpha, position counts)

## Example Output

### Console Output

```
Generating Performance Comparison Graph...
Data source: scripts-and-data/data/json/performance_history.json
Loaded 20 data points from 2025-09-10 to 2025-09-29
Downloading S&P 500 data from 2025-09-10 to 2025-09-29...
Successfully downloaded S&P 500 data using ticker: SPY
S&P 500 benchmark data merged successfully
Performance graph saved to: performance_results.png

============================================================
PERFORMANCE METRICS
============================================================
Combined Portfolio:  $210,285.40 (+5.14%)
DEE-BOT (Defensive): $104,453.71 (+4.45%)
SHORGAN-BOT (Aggr.): $105,831.69 (+5.83%)
S&P 500 Benchmark:   $208,450.00 (+4.23%)

Alpha vs S&P 500:    +0.91%
============================================================

Performance analysis complete!
```

### Graph Features

- **Title**: "AI Trading Bot Performance vs S&P 500 Benchmark"
- **Y-Axis**: Portfolio Value ($) with currency formatting
- **X-Axis**: Date (time-series)
- **Legend**:
  - Combined Portfolio (blue, solid line)
  - DEE-BOT (green, dashed line)
  - SHORGAN-BOT (red, dashed line)
  - S&P 500 (orange, dotted line)
  - Starting Capital (gray, horizontal line)
- **Metrics Box**: Performance summary in top-left corner
- **Grid**: Light grid for readability
- **Markers**: Data points clearly marked
- **Resolution**: 300 DPI for publication quality

## Future Enhancements

### Planned Features

- [ ] Sharpe Ratio calculation
- [ ] Maximum Drawdown analysis
- [ ] Rolling volatility charts
- [ ] Win rate and trade statistics
- [ ] Weekly/Monthly performance summaries
- [ ] Export to PDF report format
- [ ] Interactive web dashboard
- [ ] Email notifications with graphs

### Advanced Analytics

- [ ] Monte Carlo simulations
- [ ] Value at Risk (VaR) calculations
- [ ] Correlation analysis
- [ ] Factor attribution
- [ ] Risk-adjusted returns (Sortino, Calmar)

## Credits

Inspired by **LuckyOne7777's** [ChatGPT-Micro-Cap-Experiment](https://github.com/LuckyOne7777/ChatGPT-Micro-Cap-Experiment) methodology for transparent, CSV-based performance tracking with S&P 500 benchmarking.

---

**Last Updated**: September 29, 2025
**Version**: 1.0.0
**Status**: 🟢 Active