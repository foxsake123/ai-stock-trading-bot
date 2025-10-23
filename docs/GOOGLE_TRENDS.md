# Google Trends Integration

## Overview

The Google Trends integration monitors retail investor search interest for stock tickers to detect sentiment shifts that may signal trading opportunities. Retail interest spikes often precede increased volatility and momentum moves.

## Features

- **Real-time search interest tracking** (0-100 scale)
- **Signal classification**: SPIKE, ELEVATED, NORMAL, LOW
- **Multi-ticker batch fetching** with rate limiting
- **7-day and 30-day averages** for trend detection
- **Related queries** to understand context
- **Professional markdown reports** ready for analysis

## Installation

```bash
pip install pytrends==4.9.2
```

## Quick Start

### Basic Usage

```python
from data_sources.trends_monitor import TrendsMonitor, get_trends_signals

# Initialize monitor
monitor = TrendsMonitor()

# Fetch trends for a single ticker
trends_data = monitor.fetch_trends_data('AAPL')
print(f"Current interest: {trends_data.current_interest}")
print(f"Signal: {trends_data.signal}")
print(f"7-day change: {trends_data.change_pct_7d:.1f}%")
```

### Batch Fetching (Recommended)

```python
# Fetch trends for multiple tickers
tickers = ['AAPL', 'TSLA', 'NVDA', 'MSFT']
trends_dict = monitor.batch_fetch(tickers)

# Generate summary report
report = monitor.generate_summary_report(trends_dict)
print(report)
```

### Convenience Function

```python
# One-line usage for complete analysis
result = get_trends_signals(['AAPL', 'TSLA', 'NVDA'])

print(result['report'])  # Markdown formatted report
print(f"Spike signals: {result['summary']['spike_signals']}")
print(f"Average interest: {result['summary']['avg_interest']:.1f}")
```

## Signal Classification

### SPIKE
- **Definition**: Current interest ≥ 2.0× 7-day average
- **Interpretation**: Significant retail attention surge
- **Trading Implication**: Often precedes high volatility moves
- **Example**: Interest jumps from 30 to 70+ in a day

### ELEVATED
- **Definition**: Current interest ≥ 1.5× 7-day average
- **Interpretation**: Increased retail attention
- **Trading Implication**: Building momentum, watch for continuation
- **Example**: Interest rises from 40 to 65

### NORMAL
- **Definition**: Current interest between 0.5× and 1.5× 7-day average
- **Interpretation**: Typical interest level
- **Trading Implication**: Neutral sentiment, no unusual activity
- **Example**: Interest at 45 with 7-day average of 50

### LOW
- **Definition**: Current interest < 0.5× 7-day average
- **Interpretation**: Declining retail attention
- **Trading Implication**: Potential loss of momentum
- **Example**: Interest drops from 60 to 20

## Data Model

### TrendsData Class

```python
@dataclass
class TrendsData:
    ticker: str                # Stock ticker symbol
    current_interest: int      # Current interest (0-100)
    avg_7d: float             # 7-day average interest
    avg_30d: float            # 30-day average interest
    change_pct_7d: float      # % change from 7-day average
    change_pct_30d: float     # % change from 30-day average
    signal: str               # SPIKE, ELEVATED, NORMAL, or LOW
    timestamp: datetime       # When data was fetched
```

## API Reference

### TrendsMonitor Class

#### `__init__()`
Initialize Google Trends monitor.

**Raises**:
- `ImportError`: If pytrends library not installed

**Example**:
```python
monitor = TrendsMonitor()
```

#### `fetch_trends_data(ticker, timeframe='today 1-m')`
Fetch Google Trends data for a single ticker.

**Parameters**:
- `ticker` (str): Stock ticker symbol
- `timeframe` (str, optional): Google Trends timeframe. Default: 'today 1-m' (last 30 days)

**Returns**:
- `TrendsData` object or `None` if error

**Example**:
```python
data = monitor.fetch_trends_data('AAPL')
if data:
    print(f"{data.ticker}: {data.signal} signal")
```

#### `batch_fetch(tickers, timeframe='today 1-m')`
Fetch trends data for multiple tickers with rate limiting.

**Parameters**:
- `tickers` (List[str]): List of ticker symbols
- `timeframe` (str, optional): Google Trends timeframe

**Returns**:
- `Dict[str, TrendsData]`: Dictionary mapping ticker to TrendsData

**Rate Limiting**: 2-second delay between requests to avoid Google blocking

**Example**:
```python
tickers = ['AAPL', 'TSLA', 'NVDA']
results = monitor.batch_fetch(tickers)

for ticker, data in results.items():
    print(f"{ticker}: Interest={data.current_interest}, Signal={data.signal}")
```

#### `get_related_queries(ticker)`
Get related and rising search queries for a ticker.

**Parameters**:
- `ticker` (str): Stock ticker symbol

**Returns**:
- `Dict` with keys 'top' and 'rising' containing query lists

**Example**:
```python
queries = monitor.get_related_queries('AAPL')
print("Top queries:", queries['top'])
print("Rising queries:", queries['rising'])
```

#### `generate_summary_report(trends_data)`
Generate markdown-formatted summary report.

**Parameters**:
- `trends_data` (Dict[str, TrendsData]): Dictionary of ticker to TrendsData

**Returns**:
- `str`: Markdown formatted report

**Example**:
```python
trends_dict = monitor.batch_fetch(['AAPL', 'TSLA'])
report = monitor.generate_summary_report(trends_dict)
print(report)
```

### Convenience Functions

#### `get_trends_signals(tickers)`
One-function interface for complete trends analysis.

**Parameters**:
- `tickers` (List[str]): List of ticker symbols

**Returns**:
- `Dict` with keys:
  - `trends_data`: Dictionary of ticker to TrendsData
  - `report`: Markdown formatted summary
  - `summary`: Statistics (total_tickers, spike_signals, elevated_signals, avg_interest)

**Example**:
```python
result = get_trends_signals(['AAPL', 'TSLA', 'NVDA', 'MSFT'])

# Print report
print(result['report'])

# Access raw data
for ticker, data in result['trends_data'].items():
    if data.signal == 'SPIKE':
        print(f"ALERT: {ticker} showing interest SPIKE!")

# Check summary stats
print(f"Tickers analyzed: {result['summary']['total_tickers']}")
print(f"Spike signals: {result['summary']['spike_signals']}")
```

## Sample Output

### Report Example

```markdown
## Google Trends Sentiment

*Retail investor interest levels (0-100 scale)*

| Ticker | Current | 7d Avg | 30d Avg | Change (7d) | Signal |
|--------|---------|--------|---------|-------------|--------|
| **NVDA** | 89 | 42.3 | 38.1 | +110% | [FIRE] SPIKE |
| **TSLA** | 67 | 45.2 | 41.8 | +48% | [CHART] ELEVATED |
| **AAPL** | 52 | 48.7 | 46.2 | +7% | [MINUS] NORMAL |
| **MSFT** | 28 | 62.4 | 58.9 | -55% | [DOWN] LOW |

**Interpretation:**
- [FIRE] 1 ticker(s) showing **significant retail interest spike** (2x+ above average)
- [CHART] 1 ticker(s) with **elevated interest** (50%+ above average)

*Note: Spikes often precede increased volatility. Consider for short-term momentum plays.*
```

## Integration with Trading System

### Pre-Market Analysis

```python
from data_sources.trends_monitor import get_trends_signals

# Your watchlist from research
watchlist = ['PTGX', 'SMMT', 'VKTX', 'ARQT', 'GKOS']

# Get trends signals
result = get_trends_signals(watchlist)

# Add to pre-market report
with open('reports/premarket/latest/trends.md', 'w') as f:
    f.write(result['report'])

# Alert on spikes
for ticker, data in result['trends_data'].items():
    if data.signal == 'SPIKE':
        send_telegram_alert(f"SPIKE: {ticker} retail interest up {data.change_pct_7d:.0f}%")
```

### Multi-Agent Validation

```python
from data_sources.trends_monitor import TrendsMonitor

monitor = TrendsMonitor()

def alternative_data_check(ticker):
    """Add Google Trends to agent analysis"""
    trends = monitor.fetch_trends_data(ticker)

    if trends and trends.signal == 'SPIKE':
        return {
            'signal': 'BULLISH',
            'confidence': 0.75,
            'reason': f'Retail interest spike: {trends.change_pct_7d:.0f}% above 7-day avg'
        }
    elif trends and trends.signal == 'LOW':
        return {
            'signal': 'BEARISH',
            'confidence': 0.60,
            'reason': 'Declining retail interest'
        }
    else:
        return {
            'signal': 'NEUTRAL',
            'confidence': 0.50,
            'reason': 'Normal retail interest level'
        }
```

## Rate Limiting & Best Practices

### Rate Limits
- **Default delay**: 2 seconds between requests
- **Google's limits**: ~100 requests per hour (unofficial)
- **Best practice**: Use batch_fetch() instead of multiple fetch_trends_data() calls

### Recommended Usage
```python
# GOOD: Batch fetch with rate limiting
monitor = TrendsMonitor()
results = monitor.batch_fetch(['AAPL', 'TSLA', 'NVDA'])  # Handles rate limiting automatically

# AVOID: Rapid individual requests
for ticker in ['AAPL', 'TSLA', 'NVDA']:
    data = monitor.fetch_trends_data(ticker)  # No automatic rate limiting
```

### Error Handling
```python
from data_sources.trends_monitor import TrendsMonitor

monitor = TrendsMonitor()

try:
    trends = monitor.fetch_trends_data('AAPL')
    if trends:
        print(f"Signal: {trends.signal}")
    else:
        print("No data available (likely API error or ticker not found)")
except Exception as e:
    print(f"Error fetching trends: {e}")
```

## Timeframe Options

Google Trends supports various timeframes:

- `'now 1-H'` - Last 1 hour
- `'now 4-H'` - Last 4 hours
- `'now 1-d'` - Last 1 day
- `'now 7-d'` - Last 7 days
- `'today 1-m'` - Last 30 days (default)
- `'today 3-m'` - Last 90 days
- `'today 12-m'` - Last 12 months
- `'today 5-y'` - Last 5 years
- `'all'` - All available data

**Example**:
```python
# Get 7-day trends for intraday momentum
intraday_trends = monitor.fetch_trends_data('TSLA', timeframe='now 7-d')

# Get 3-month trends for longer-term analysis
longterm_trends = monitor.fetch_trends_data('TSLA', timeframe='today 3-m')
```

## Trading Strategies Using Trends Data

### 1. Retail Momentum Play
**Trigger**: SPIKE signal (2x+ above average)
**Strategy**: Enter on spike confirmation, ride retail momentum
**Risk**: Spikes can reverse quickly, use tight stops
**Example**: NVDA spikes to 85 interest (2.5x avg) → Enter long with 3% stop

### 2. Contrarian Fade
**Trigger**: Multiple SPIKE signals in sector
**Strategy**: Fade the move when over-extended
**Risk**: Momentum can continue longer than expected
**Example**: 5 EV stocks all showing SPIKE → Consider shorting weakest on overbought RSI

### 3. Catalyst Confirmation
**Trigger**: ELEVATED signal before known catalyst
**Strategy**: Confirm retail awareness before FDA/earnings
**Risk**: Spike might be priced in
**Example**: PTGX showing ELEVATED before M&A ruling → Confirms retail positioning

### 4. Dead Money Avoidance
**Trigger**: LOW signal on existing position
**Strategy**: Exit or reduce position if losing retail attention
**Risk**: Could miss turnaround
**Example**: Position down 5% with LOW signal → Cut loss before momentum dies

## Performance Considerations

### Speed
- Single ticker: ~2-3 seconds
- 10 tickers (batch): ~25 seconds (includes rate limiting)
- Related queries: ~3 seconds

### Caching Recommendations
```python
import time
from data_sources.trends_monitor import TrendsMonitor

class CachedTrendsMonitor:
    def __init__(self, cache_duration=3600):  # 1 hour cache
        self.monitor = TrendsMonitor()
        self.cache = {}
        self.cache_duration = cache_duration

    def get_trends(self, ticker):
        now = time.time()
        if ticker in self.cache:
            data, timestamp = self.cache[ticker]
            if now - timestamp < self.cache_duration:
                return data

        # Cache miss or expired - fetch fresh data
        data = self.monitor.fetch_trends_data(ticker)
        if data:
            self.cache[ticker] = (data, now)
        return data
```

## Troubleshooting

### Issue: "No module named 'pytrends'"
**Solution**: Install pytrends library
```bash
pip install pytrends==4.9.2
```

### Issue: "Too many requests" or 429 errors
**Solution**:
1. Increase rate_limit_delay: `monitor.rate_limit_delay = 5`
2. Reduce batch size
3. Add sleep between batches

### Issue: "No trends data for TICKER"
**Solution**:
1. Verify ticker symbol is correct
2. Try different timeframe (e.g., 'today 3-m' instead of 'today 1-m')
3. Some tickers have low search volume - this is expected

### Issue: Empty DataFrame returned
**Solution**:
1. Ticker might not have search interest
2. Try searching for company name instead: `"AAPL stock"`
3. Check if ticker is actively traded

## Testing

The trends monitor includes comprehensive test suite with 31 tests covering:
- Initialization and setup
- Signal determination logic
- Trends data fetching
- Batch fetching with rate limiting
- Related queries
- Report generation
- Edge cases and error handling

**Run tests**:
```bash
python -m pytest tests/test_trends_monitor.py -v --cov=data_sources.trends_monitor
```

**Expected result**:
```
31 passed
Coverage: 94.59%
```

## API Costs

Google Trends is **FREE** with rate limiting:
- No API key required
- No subscription fees
- Unofficial limits: ~100 requests/hour
- Use responsibly to avoid temporary blocks

## References

- [pytrends Documentation](https://github.com/GeneralMills/pytrends)
- [Google Trends](https://trends.google.com/)
- Enhancement 1B specification (project roadmap)

## Changelog

### Version 1.0.0 (October 22, 2025)
- Initial implementation
- 31 comprehensive tests (94.59% coverage)
- Signal classification (SPIKE, ELEVATED, NORMAL, LOW)
- Batch fetching with rate limiting
- Markdown report generation
- Related queries support
- Convenience function interface

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review test suite for usage examples
3. See `data_sources/trends_monitor.py` source code
4. File issue in project repository

---

**Last Updated**: October 22, 2025
**Version**: 1.0.0
**Test Coverage**: 94.59% (31/31 tests passing)
**Status**: Production Ready ✅
