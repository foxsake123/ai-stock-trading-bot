# Insider Transaction Monitoring

## Overview
Automatically monitors SEC Form 4 filings to detect significant insider transactions that may signal future stock movements.

## How It Works

1. **Data Source**: SEC Form 4 filings via Financial Datasets API
2. **Significance Threshold**: Transactions >$500K
3. **Signal Generation**:
   - C-suite buys >$500K = BULLISH
   - C-suite sells >$1M = BEARISH
   - Large non-C-suite buys >$500K = BULLISH
   - Very large non-C-suite sells >$1.5M = BEARISH
   - Routine selling <$500K = NEUTRAL

## Usage

### Basic Usage
```python
from data_sources.insider_monitor import get_insider_signals
from financial_datasets import FinancialDatasetsClient

# Initialize API client
fd_client = FinancialDatasetsClient(api_key='your_api_key')

# Get signals for tickers
signals = get_insider_signals(['AAPL', 'MSFT'], fd_client, days=30)

# Access the report
print(signals['report'])  # Markdown formatted report

# Access summary statistics
print(signals['summary'])  # Summary counts
```

### Advanced Usage
```python
from data_sources.insider_monitor import InsiderMonitor

# Create monitor instance
monitor = InsiderMonitor(fd_client)

# Fetch transactions for a single ticker
transactions = monitor.fetch_recent_transactions('AAPL', days=30)

# Filter for significant transactions
significant_trans = monitor.get_significant_transactions(['AAPL', 'MSFT'], days=30)

# Generate custom report
report = monitor.generate_summary_report(significant_trans)
```

### Working with Transaction Objects
```python
for ticker, trans_list in significant_trans.items():
    for transaction in trans_list:
        print(f"{transaction.ticker}: {transaction.transaction_type}")
        print(f"  Insider: {transaction.insider_name} ({transaction.title})")
        print(f"  Value: ${transaction.value:,.0f}")
        print(f"  Signal: {transaction.signal}")
```

## Integration

### Daily Pre-Market Report
Insider signals are automatically included in the daily pre-market report under the "Insider Transaction Signals" section.

The integration is in `daily_premarket_report.py`:

```python
from data_sources.insider_monitor import get_insider_signals
from financial_datasets import FinancialDatasetsClient

# ... in report generation function ...

# Get insider signals
fd_client = FinancialDatasetsClient(api_key=os.getenv('FINANCIAL_DATASETS_API_KEY'))
all_tickers = shorgan_tickers + dee_tickers
insider_data = get_insider_signals(all_tickers, fd_client, days=30)

# Add to report
report += "\n---\n\n"
report += insider_data['report']
```

### Multi-Agent Validation
Insider transaction data can be incorporated into the multi-agent consensus system:

```python
# In FundamentalAnalyst or NewsAnalyst
from data_sources.insider_monitor import get_insider_signals

# Check for recent insider buying
insider_data = get_insider_signals([ticker], fd_client, days=7)
if insider_data['summary']['bullish_signals'] > 0:
    # Increase fundamental score
    score += 0.1
```

## Interpretation Guide

### Bullish Signals
- **Multiple C-suite buys**: Strong bullish signal
  - Insiders have non-public information
  - High confidence in company prospects
  - Often precedes positive news/earnings

- **Single large CEO buy**: Moderate bullish signal
  - CEO confidence in stock value
  - May indicate undervaluation
  - Track if followed by additional buys

- **Director buys >$1M**: Moderate bullish signal
  - Board confidence in company direction
  - Less common than executive trades

### Bearish Signals
- **Multiple C-suite sells >$2M**: Moderate bearish signal
  - May indicate overvaluation concerns
  - Could precede negative developments
  - Check if coordinated (same time period)

- **Very large sales >$5M**: Strong bearish signal
  - Insider urgency to exit position
  - Potential knowledge of upcoming headwinds
  - Track for pattern of escalating sales

### Neutral Signals
- **Routine sells <$500K**: Typically ignore
  - Often for tax planning or diversification
  - Regular scheduled sales (10b5-1 plans)
  - Part of compensation packages

- **Employee/mid-level trades**: Low signal value
  - Less access to strategic information
  - Often routine financial planning

## Signal Weighting

When multiple signals are present:

1. **Consensus Buy**: 3+ C-suite buys within 30 days
   - Weight: HIGH (add 15-20% to conviction)
   - Interpretation: Strong insider confidence

2. **Mixed Signals**: Some buys, some sells
   - Weight: LOW (add 0-5% to conviction)
   - Interpretation: Likely routine activity

3. **Consensus Sell**: 3+ C-suite sells >$2M within 30 days
   - Weight: MEDIUM (reduce 10-15% conviction)
   - Interpretation: Caution warranted

4. **Single Outlier**: One very large trade
   - Weight: MEDIUM (add/reduce 5-10%)
   - Interpretation: Warrants investigation

## Example Output

```markdown
## Insider Transaction Signals

### AAPL

| Date | Insider | Title | Type | Shares | Value | Signal |
|------|---------|-------|------|--------|-------|--------|
| 10/12 | Tim Cook | CEO | **BUY** | 10,000 | $1,750,000 | [BUY] BULLISH |
| 10/10 | Luca Maestri | CFO | **BUY** | 5,000 | $875,000 | [BUY] BULLISH |
| 10/08 | Board Member | Director | **SELL** | 2,000 | $350,000 | [HOLD] NEUTRAL |

**Net Signal:** [BUY] **BULLISH** (2 buys vs 1 sells, Net: $2,275,000)

### MSFT

| Date | Insider | Title | Type | Shares | Value | Signal |
|------|---------|-------|------|--------|-------|--------|
| 10/13 | Satya Nadella | CEO | **SELL** | 50,000 | $15,000,000 | [SELL] BEARISH |

**Net Signal:** [SELL] **BEARISH** (0 buys vs 1 sells, Net: -$15,000,000)
```

## Limitations

### Filing Delays
- Form 4 filings can be delayed up to 2 business days after transaction
- Signal is backward-looking, not predictive
- Market may already react before data available

### Not All Activity is Predictive
- Diversification is a common reason for selling
- 10b5-1 plans allow scheduled automated selling
- Compensation packages often include stock grants/exercises

### False Positives/Negatives
- Insiders can be wrong about company prospects
- Personal financial needs may drive selling
- Buying may be for portfolio rebalancing

### Best Practices
- Combine with other signals (fundamentals, technicals)
- Look for patterns over single transactions
- Weight more recent activity higher
- Consider transaction size relative to insider's holdings

## Configuration

### Customizing Thresholds

You can customize significance thresholds:

```python
monitor = InsiderMonitor(fd_client)

# Change significance threshold (default: $500K)
monitor.significance_threshold = 1_000_000  # $1M

# Add more C-suite titles
monitor.c_suite_titles.append('General Counsel')
```

### Filtering by Time

Adjust the lookback period:

```python
# Last 7 days (recent activity)
recent_signals = get_insider_signals(tickers, fd_client, days=7)

# Last 90 days (longer-term pattern)
longer_signals = get_insider_signals(tickers, fd_client, days=90)
```

## Testing

Run the comprehensive test suite:

```bash
# Run all insider monitor tests
pytest tests/test_insider_monitor.py -v

# Run with coverage report
pytest tests/test_insider_monitor.py --cov=data_sources.insider_monitor --cov-report=html

# Run specific test class
pytest tests/test_insider_monitor.py::TestSignalDetermination -v
```

Test coverage: **95.41%** (33 comprehensive tests)

## API Requirements

### Financial Datasets API
- Endpoint: `get_filings(ticker, filing_type='4', limit=50)`
- Required fields in response:
  - `filing_date` (ISO datetime)
  - `transaction_date` (ISO datetime, optional)
  - `reporting_owner` (string)
  - `title` (string)
  - `transaction_type` (string: BUY/SELL/PURCHASE/SALE)
  - `shares_traded` (int)
  - `price_per_share` (float)

### Rate Limiting
- Respect API rate limits (typically 100 requests/minute)
- Monitor uses batch requests when possible
- Implements error handling for rate limit errors

## Troubleshooting

### No Data Returned
- Check API key is valid: `fd_client.api_key`
- Verify ticker symbol is correct
- Check if company has recent insider transactions (some have none)
- Increase `days` parameter (default: 30)

### Signal Quality Issues
- Adjust `significance_threshold` if too many/few signals
- Review C-suite title detection (add industry-specific titles)
- Consider excluding routine 10b5-1 plan sales

### Performance
- Fetching 50 filings per ticker takes ~100-200ms
- Batch process large ticker lists (>50) with rate limiting
- Cache results for repeated queries on same ticker

## Future Enhancements

Planned improvements:
1. **10b5-1 Plan Detection**: Exclude scheduled automatic sales
2. **Ownership Percentage**: Weight signals by % of holdings sold/bought
3. **Historical Accuracy**: Track which insider signals preceded price moves
4. **Cluster Detection**: Identify coordinated insider activity patterns
5. **Form 3/5 Integration**: Include initial filings and annual updates
