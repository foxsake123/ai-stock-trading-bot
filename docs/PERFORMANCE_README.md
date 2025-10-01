# 📊 Performance Visualization System

## Quick Start

### Generate Performance Graph
```bash
python generate_performance_graph.py
```
Output: `performance_results.png` (300 DPI, publication quality)

### View Current Performance
```
Combined Portfolio:  $210,285.40 (+5.14%)
DEE-BOT (Defensive): $104,453.71 (+4.45%)
SHORGAN-BOT (Aggr.): $105,831.69 (+5.83%)
```

## What This Does

This system creates professional performance graphs comparing your AI trading bots (DEE-BOT and SHORGAN-BOT) against the S&P 500 benchmark, inspired by the [ChatGPT-Micro-Cap-Experiment](https://github.com/LuckyOne7777/ChatGPT-Micro-Cap-Experiment) methodology.

### Features
✅ **Dual-Bot Tracking**: Separate performance lines for defensive (DEE) and aggressive (SHORGAN) strategies
✅ **S&P 500 Benchmark**: Normalized comparison showing alpha vs market
✅ **Historical Time-Series**: Complete portfolio growth history
✅ **Professional Styling**: High-resolution graphs with comprehensive metrics
✅ **Automated Updates**: Integrates with daily trading pipeline

## Example Output

The graph shows:
- **Blue Line**: Combined portfolio (both bots)
- **Green Dashed**: DEE-BOT (defensive strategy)
- **Red Dashed**: SHORGAN-BOT (aggressive strategy)
- **Orange Dotted**: S&P 500 benchmark (normalized to same starting capital)
- **Metrics Box**: Current values and returns in top-left corner

## Files Created

| File | Purpose |
|------|---------|
| `generate_performance_graph.py` | Main visualization script |
| `performance_results.png` | Generated performance graph (300 DPI) |
| `GENERATE_PERFORMANCE_GRAPH.bat` | Quick execution (Windows) |
| `docs/PERFORMANCE_TRACKING.md` | Complete documentation |
| `scripts-and-data/automation/update_portfolio_csv.py` | CSV tracker |

## Data Sources

### Real-Time Data
- Fetches current portfolio values from Alpaca API
- Updates DEE-BOT and SHORGAN-BOT positions automatically

### Historical Data
- Reads from `scripts-and-data/data/json/performance_history.json`
- Tracks daily performance since September 10, 2025

### Benchmark Data
- Downloads S&P 500 historical data via yfinance
- Normalizes to $200,000 starting capital (matching combined portfolio)

## Daily Workflow

1. **Morning (9:30 AM)**: Automated trade execution
2. **Post-Market (4:30 PM)**:
   ```bash
   # Update portfolio CSV files
   python scripts-and-data/automation/update_portfolio_csv.py

   # Generate performance graph
   python generate_performance_graph.py
   ```

## CSV Format (Compatible with Reference Repo)

```csv
Date,Ticker,Shares,Buy Price,Cost Basis,Stop Loss,Current Price,Total Value,PnL,Action,Cash Balance,Total Equity,Bot,Side
2025-09-29,AAPL,84,226.91,19061.0,,253.8,21319.2,2258.4,HOLD,,,DEE-BOT,long
2025-09-29,TOTAL,,,,,,109865.5,4465.5,,30615.4,140480.9,DEE-BOT,
```

## Configuration

### Starting Capital
```python
INITIAL_CAPITAL_DEE = 100000.0      # DEE-BOT
INITIAL_CAPITAL_SHORGAN = 100000.0  # SHORGAN-BOT
INITIAL_CAPITAL_COMBINED = 200000.0 # Total
```

### API Keys
Configure in `.env`:
```
ALPACA_API_KEY_DEE=your_key_here
ALPACA_SECRET_KEY_DEE=your_secret_here
ALPACA_API_KEY_SHORGAN=your_key_here
ALPACA_SECRET_KEY_SHORGAN=your_secret_here
```

## Metrics Explained

### Total Return
Percentage gain/loss from starting capital
```
Return % = (Current Value - Starting Capital) / Starting Capital * 100
```

### Alpha
Outperformance vs S&P 500 benchmark
```
Alpha = Portfolio Return % - S&P 500 Return %
```
Positive alpha = beating the market

### Unrealized P&L
Current gain/loss on open positions (not yet realized)

## Troubleshooting

### "No performance data available"
**Fix**: Run the trading system to generate `performance_history.json`

### "S&P 500 data unavailable"
**Cause**: yfinance API rate limiting
**Result**: Graph generates without benchmark line (still shows portfolio performance)

### Graph shows incorrect values
**Fix**: Ensure Alpaca API keys are correct and accounts are accessible

## Advanced Usage

### Custom Date Range
Edit `generate_performance_graph.py`:
```python
start_date = pd.Timestamp("2025-09-01")
end_date = pd.Timestamp("2025-09-30")
```

### Add Additional Metrics
Extend the `calculate_performance_metrics()` function to include:
- Sharpe Ratio
- Maximum Drawdown
- Win Rate
- Average Trade Duration

### Export Data
CSV files are automatically created in `scripts-and-data/daily-csv/`:
- `dee_bot_portfolio_history.csv`
- `shorgan_bot_portfolio_history.csv`
- `combined_portfolio_history.csv`

## Credits

Performance tracking methodology inspired by **LuckyOne7777's** excellent [ChatGPT-Micro-Cap-Experiment](https://github.com/LuckyOne7777/ChatGPT-Micro-Cap-Experiment) repository, which demonstrates transparent, CSV-based portfolio tracking with S&P 500 benchmarking.

## Related Documentation

- **Complete Guide**: [docs/PERFORMANCE_TRACKING.md](docs/PERFORMANCE_TRACKING.md)
- **System Architecture**: [README.md](README.md)
- **DEE-BOT Strategy**: [docs/DEE_BOT_STRATEGY.md](docs/DEE_BOT_STRATEGY.md)
- **SHORGAN Strategy**: [docs/SHORGAN_STRATEGY.md](docs/SHORGAN_STRATEGY.md)

---

**Version**: 1.0.0
**Last Updated**: September 29, 2025
**Status**: 🟢 Operational