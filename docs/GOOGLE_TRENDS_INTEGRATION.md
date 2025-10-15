# Google Trends Integration

## Overview
Tracks retail investor interest and search momentum using Google Trends data to identify potential trading opportunities based on public sentiment.

## How It Works

1. **Data Source**: Google Trends API via `pytrends` library
2. **Metrics Tracked**:
   - Current search interest (0-100 scale)
   - 7-day and 30-day averages
   - Trend direction (RISING, FALLING, STABLE)
   - Momentum score (-1.0 to 1.0)
   - Breakout detection (2x+ average interest)
   - Related search queries

3. **Signal Generation**:
   - **BULLISH**: Breakout with rising trend OR strong positive momentum
   - **BEARISH**: Falling trend with negative momentum OR very low interest
   - **NEUTRAL**: Stable or mixed signals

## Installation

```bash
pip install pytrends
```

## Usage

### Basic Usage
```python
from data_sources.google_trends_monitor import get_trends_signals

# Get trends for multiple tickers
signals = get_trends_signals(['AAPL', 'TSLA', 'NVDA'])

# Print the report
print(signals['report'])

# Access summary
print(f"Bullish signals: {signals['summary']['bullish_signals']}")
print(f"Breakouts: {signals['summary']['breakouts']}")
```

### Advanced Usage
```python
from data_sources.google_trends_monitor import GoogleTrendsMonitor

# Create monitor
monitor = GoogleTrendsMonitor()

# Analyze single ticker
trend_data = monitor.analyze_ticker('AAPL', company_name='Apple Inc')

print(f"Current interest: {trend_data.current_interest}/100")
print(f"Trend: {trend_data.trend_direction}")
print(f"Momentum: {trend_data.momentum_score:+.2f}")
print(f"Signal: {trend_data.signal}")
print(f"Breakout: {trend_data.is_breakout}")
print(f"Related queries: {trend_data.related_queries}")
```

### Compare Multiple Tickers
```python
# Compare relative interest
comparison = monitor.compare_tickers(['AAPL', 'MSFT', 'GOOGL', 'AMZN'])

print(f"Winner: {comparison.winner}")
print(f"Interest scores: {comparison.interest_scores}")
print(f"Relative strength: {comparison.relative_strength}")
```

## Integration

### Daily Pre-Market Report
Add to `daily_premarket_report.py`:

```python
from data_sources.google_trends_monitor import get_trends_signals

# ... in report generation function ...

# Get trends signals
all_tickers = shorgan_tickers + dee_tickers
trends_data = get_trends_signals(all_tickers)

# Add to report
report += "\n---\n\n"
report += trends_data['report']
```

### Multi-Agent System Integration
Boost agent scores based on trends:

```python
# In FundamentalAnalyst or SentimentAnalyst
from data_sources.google_trends_monitor import GoogleTrendsMonitor

monitor = GoogleTrendsMonitor()
trend_data = monitor.analyze_ticker(ticker)

# Adjust score based on momentum
if trend_data.is_breakout:
    score += 0.15  # Strong retail interest
elif trend_data.momentum_score > 0.3:
    score += 0.10  # Rising interest
elif trend_data.momentum_score < -0.3:
    score -= 0.10  # Falling interest
```

## Interpretation Guide

### Bullish Signals

**1. Breakout + Rising Trend**
- Current interest >2x 30-day average
- Momentum increasing
- Interpretation: Retail FOMO building
- Example: Meme stock rallies, earnings hype

**2. Strong Positive Momentum**
- 7-day avg significantly > 30-day avg
- Rising search volume
- Interpretation: Growing public awareness
- Example: New product launch, positive news

**3. High Related Query Volume**
- Many related searches appearing
- Queries show buying intent
- Interpretation: Active retail research
- Example: "buy AAPL", "AAPL stock forecast"

### Bearish Signals

**1. Falling Trend + Negative Momentum**
- Current interest < 7-day avg < 30-day avg
- Declining search volume
- Interpretation: Losing retail interest
- Example: Post-earnings cooldown

**2. Very Low Interest (<10 consistently)**
- Minimal search activity
- Below threshold for retail attention
- Interpretation: No public awareness/interest
- Example: Small-cap stocks, distressed companies

**3. Sudden Drop After Peak**
- Sharp decline from recent high
- Negative momentum accelerating
- Interpretation: Retail losing conviction
- Example: Failed breakout, disappointing news

### Neutral Signals

**1. Stable Interest**
- Current ~= 7-day ~= 30-day avg
- Low volatility
- Interpretation: Steady, no catalyst
- Example: Large-cap blue chips (normal state)

**2. Mixed Signals**
- Rising interest but low absolute value
- Or high interest but declining
- Interpretation: Conflicting signals
- Example: Sector rotation, indecision

## Signal Weighting

When integrating with trading decisions:

**High Weight Scenarios (add 15-20% conviction)**:
- Breakout + rising trend + bullish catalyst
- Very high momentum (>0.7) with news confirmation
- Multiple related queries showing buying intent

**Medium Weight Scenarios (add 5-10%)**:
- Rising trend without breakout
- Moderate momentum (0.3-0.5)
- Increasing interest on known catalyst

**Low Weight Scenarios (ignore or reduce 5%)**:
- Low absolute interest (<20) even if rising
- Falling trend from already-low base
- Mixed/stable signals

**Contrarian Scenarios**:
- Extreme breakout (>5x average) may signal exhaustion
- Very high interest (>90) for extended period may indicate top

## Example Output

```markdown
## Google Trends Analysis

| Ticker | Interest | Trend | Momentum | Signal | Notes |
|--------|----------|-------|----------|--------|-------|
| AAPL | 85/100 | RISING | +0.62 | [BUY] BULLISH | BREAKOUT, 62% momentum, 5 related |
| TSLA | 78/100 | RISING | +0.45 | [BUY] BULLISH | 45% momentum |
| NVDA | 92/100 | STABLE | +0.15 | [HOLD] NEUTRAL | - |
| AMZN | 35/100 | FALLING | -0.40 | [SELL] BEARISH | 40% momentum |

**Summary**: 4 tickers analyzed, 2 bullish, 1 bearish, 2 breakouts
```

## Timeframes

Different timeframes for different strategies:

**Intraday/Swing Trading** (`timeframe='now 1-d'`):
- Very short-term interest spikes
- News-driven momentum
- Higher noise, use with caution

**Short-Term Trading** (`timeframe='today 1-m'`):
- Past month trends
- Good for catalyst plays (earnings, announcements)
- Default for most use cases

**Longer-Term Analysis** (`timeframe='today 3-m'`):
- Broader trend identification
- Sector rotation signals
- Less reactive to daily noise

## Limitations

### 1. Lagging Indicator
- Retail interest follows institutional moves
- Breakouts often occur AFTER price moves
- Best used for confirmation, not prediction

### 2. Quality vs Quantity
- High search volume ≠ buying activity
- Could indicate fear/selling as much as greed/buying
- Combine with price action for context

### 3. Meme Stock Distortion
- Some stocks have permanently elevated search interest
- Baseline shifts over time (Tesla, GME, AMC)
- Compare relative changes, not absolute values

### 4. Geographic Limitations
- US-focused data (geo='US')
- May miss international sentiment
- Global stocks may have different patterns

### 5. Rate Limiting
- Google Trends has rate limits
- 2-second delay enforced between requests
- Large ticker lists take time to process

## Best Practices

**1. Combine with Price Action**
```python
# Good: Rising trends + price breakout
if trend_data.is_breakout and price > resistance:
    # Strong confluence

# Bad: Rising trends + price breakdown
if trend_data.is_breakout and price < support:
    # Divergence - exercise caution
```

**2. Use Company Names for Better Data**
```python
# Better results
monitor.analyze_ticker('AAPL', company_name='Apple Inc')

# vs just ticker
monitor.analyze_ticker('AAPL')
```

**3. Normalize for Stock Size**
```python
# Small caps: Lower absolute interest threshold
if market_cap < 1_billion and trend_data.current_interest > 15:
    # Significant for small cap

# Large caps: Higher threshold
if market_cap > 100_billion and trend_data.current_interest < 50:
    # Low for mega cap
```

**4. Track Changes Over Time**
```python
# Store historical trend data
# Compare week-over-week momentum
# Identify acceleration/deceleration
```

## Configuration

### Customize Thresholds

```python
monitor = GoogleTrendsMonitor()

# Adjust breakout threshold (default: 2.0)
monitor.breakout_threshold = 3.0  # Require 3x average for breakout

# Adjust trend thresholds (default: ±0.20)
monitor.rising_threshold = 0.30  # Require 30% increase for "rising"
monitor.falling_threshold = -0.30  # Require 30% decrease for "falling"

# Adjust request delay (default: 2 seconds)
monitor.request_delay = 3  # 3 seconds between API requests
```

## Testing

Run the comprehensive test suite:

```bash
# Run all Google Trends tests
pytest tests/test_google_trends_monitor.py -v

# Run with coverage
pytest tests/test_google_trends_monitor.py --cov=data_sources.google_trends_monitor --cov-report=html

# Run specific test class
pytest tests/test_google_trends_monitor.py::TestTrendAnalysis -v
```

**Test Coverage**: 93.40% (45 comprehensive tests)

## API Requirements

### PyTrends Library
- Install: `pip install pytrends`
- No API key required
- Free to use with rate limits

### Rate Limits
- ~2-3 requests per second recommended
- Automatic rate limiting enforced in code
- Excessive requests may result in temporary blocks

### Respect Google's Terms
- For personal/research use
- Do not abuse or scrape excessively
- Consider caching results

## Troubleshooting

### No Data Returned
```python
# Check keyword spelling
trend_data = monitor.analyze_ticker('AAPL')  # Correct

# Try with company name
trend_data = monitor.analyze_ticker('AAPL', company_name='Apple')

# Verify ticker has sufficient search volume
if trend_data.current_interest == 0:
    print("Ticker too small or misspelled")
```

### Rate Limit Errors
```python
# Increase delay between requests
monitor.request_delay = 5  # 5 seconds

# Process tickers in smaller batches
for batch in chunks(all_tickers, 10):
    signals = get_trends_signals(batch)
    time.sleep(10)  # Wait between batches
```

### ConnectionError / Timeout
```python
# Pytrends may timeout on slow connections
# Retry logic built into module
# Check internet connection
```

## Future Enhancements

Planned improvements:
1. **Historical Trend Storage**: Track search interest over time for backtesting
2. **Regional Analysis**: Compare US vs international search patterns
3. **Query Classification**: Categorize related queries (bullish/bearish/neutral)
4. **Correlation Analysis**: Correlate search spikes with price movements
5. **Sector Comparison**: Compare ticker trends vs sector average
6. **Alert System**: Notify when breakouts occur
