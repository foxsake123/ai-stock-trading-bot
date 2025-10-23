# Options Flow Analyzer - Complete Guide

## Overview

The Options Flow Analyzer detects unusual options activity to generate high-conviction trading signals. It monitors put/call ratios, large block trades, sweep orders, and multi-leg strategies to identify where "smart money" is positioning.

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│              Options Flow Analysis Pipeline                 │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  OptionsDataFetcher - Fetches options chains and flow data  │
│  - Yahoo Finance (free, delayed)                            │
│  - Financial Datasets API (paid, real-time)                 │
│  - Calculates Greeks (delta, gamma, theta, vega)            │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  OptionsFlowAnalyzer - Main analysis engine                 │
│  - Calculates put/call ratios                               │
│  - Measures flow imbalance (calls - puts)                   │
│  - Tracks net delta/gamma exposure                          │
│  - Generates bullish/bearish signals                        │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  UnusualActivityDetector - Pattern detection                │
│  - Large block trades (>$100k premium)                       │
│  - Sweep orders (multi-exchange aggressive)                 │
│  - Unusual volume (>3x average)                              │
│  - Multi-leg strategies (spreads, straddles)                 │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  OptionsFlowSignal - Final trading signal                   │
│  - Overall signal (VERY_BULLISH to VERY_BEARISH)            │
│  - Confidence (0-1)                                          │
│  - Supporting metrics and reasoning                          │
└──────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Installation

Install required dependencies:

```bash
pip install yfinance scipy pandas aiohttp
```

### 2. Environment Setup

Add to `.env`:

```bash
# Financial Datasets API (for real-time flow - optional but recommended)
FINANCIAL_DATASETS_API_KEY=your_api_key_here
```

### 3. Basic Usage

```python
import asyncio
from src.data.options_data_fetcher import OptionsDataFetcher
from src.analysis.options_flow import OptionsFlowAnalyzer

async def analyze_options():
    # Initialize data fetcher
    fetcher = OptionsDataFetcher(
        yahoo_enabled=True,  # Free data
        fd_api_key="your_api_key"  # Optional: paid real-time data
    )

    # Initialize analyzer
    analyzer = OptionsFlowAnalyzer(
        data_fetcher=fetcher,
        large_trade_threshold=100000,  # $100k minimum
        unusual_volume_multiplier=3.0   # 3x average = unusual
    )

    # Analyze a ticker
    signal = await analyzer.analyze_ticker("AAPL", minutes_back=60)

    print(f"Signal: {signal.signal} (Confidence: {signal.confidence:.1%})")
    print(f"Reasoning: {signal.reasoning}")
    print(f"Put/Call Ratio: {signal.put_call_metrics.volume_ratio:.2f}")
    print(f"Flow Imbalance: ${signal.flow_imbalance.total_imbalance:,.0f}")
    print(f"Net Delta: {signal.delta_gamma.net_delta:,.0f}")
    print(f"Large Trades: {signal.large_trades_count}")
    print(f"Sweep Orders: {signal.sweep_orders_count}")

# Run
asyncio.run(analyze_options())
```

**Example Output:**
```
Signal: VERY_BULLISH (Confidence: 85%)
Reasoning: Strong bullish flow imbalance: $2,450,000 net bullish | Large bullish delta exposure: 12,500 ($1,875,000 notional) | 5 large trades (>$100k premium) | 3 sweep orders (urgent flow)
Put/Call Ratio: 0.42
Flow Imbalance: $2,450,000
Net Delta: 12,500
Large Trades: 5
Sweep Orders: 3
```

## Core Components

### 1. OptionsDataFetcher (`src/data/options_data_fetcher.py`)

Fetches options chain data and real-time flow.

**Key Methods:**

```python
# Fetch complete options chain
chain = await fetcher.fetch_options_chain("AAPL", expiration=None)

# Fetch recent options flow
flows = await fetcher.fetch_options_flow("AAPL", minutes_back=60, min_premium=10000)

# Get available expirations
expirations = await fetcher.get_expirations("AAPL")

# Get current stock price
spot_price = await fetcher.get_spot_price("AAPL")

# Calculate Greeks
contract_with_greeks = fetcher.calculate_greeks(contract, spot_price)
```

**Data Sources:**
- **Yahoo Finance** (free): Basic chain data, delayed
- **Financial Datasets API** (paid): Real-time flow, sweeps, Greeks

### 2. OptionsFlowAnalyzer (`src/analysis/options_flow.py`)

Main analysis engine generating trading signals.

**Key Metrics:**

**Put/Call Ratio:**
```python
# High ratio (>1.5) = More puts than calls = Bearish
# Low ratio (<0.7) = More calls than puts = Bullish
# Deviation from average is more important than absolute value
```

**Flow Imbalance:**
```python
# Positive imbalance = Net call buying or put selling = Bullish
# Negative imbalance = Net put buying or call selling = Bearish
# Imbalance > 20% of total flow = Strong signal
```

**Delta Exposure:**
```python
# Positive net delta = Bullish positioning
# Negative net delta = Bearish positioning
# Delta * spot * 100 = Notional exposure
```

**Signal Generation:**
```python
signal = await analyzer.analyze_ticker("AAPL")

# Component signals
print(signal.put_call_signal)  # From P/C ratio
print(signal.flow_imbalance_signal)  # From flow imbalance
print(signal.delta_exposure_signal)  # From delta/gamma
print(signal.unusual_activity_signal)  # From unusual trades

# Combined signal (weighted)
print(signal.signal)  # VERY_BULLISH, BULLISH, NEUTRAL, BEARISH, VERY_BEARISH
print(signal.confidence)  # 0-1
```

**Daily Summary Report:**
```python
# Generate summary for multiple tickers
tickers = ["AAPL", "TSLA", "NVDA", "AMD", "MSFT"]
report = await analyzer.generate_daily_summary(tickers, minutes_back=390)

# Save report
with open("reports/options_flow_daily.md", "w") as f:
    f.write(report)
```

### 3. UnusualActivityDetector (`src/signals/unusual_activity.py`)

Detects unusual patterns indicating "smart money" activity.

**Unusual Trade Detection:**

```python
from src.signals.unusual_activity import UnusualActivityDetector

detector = UnusualActivityDetector(
    block_trade_threshold=100000,  # $100k
    unusual_volume_multiplier=3.0,  # 3x average
    unusual_strike_threshold=0.05,  # 5% OTM/ITM
    large_oi_change_threshold=500   # 500 contracts
)

# Detect unusual trades
unusual_trades = detector.detect_unusual_trades(
    ticker="AAPL",
    flows=flows,
    chain=chain,
    spot_price=150.0
)

for trade in unusual_trades:
    print(f"Unusual Trade: ${trade.flow.premium:,.0f} premium")
    print(f"  Block: {trade.is_block_trade}")
    print(f"  Sweep: {trade.is_sweep}")
    print(f"  Volume: {trade.volume_multiple:.1f}x average")
    print(f"  Conviction: {trade.conviction_score:.1%}")
    print(f"  Reasoning: {' | '.join(trade.reasoning)}")
```

**Multi-Leg Strategy Detection:**

```python
# Detect spreads, straddles, etc.
strategies = detector.detect_multi_leg_strategies(
    ticker="AAPL",
    flows=flows,
    time_window_seconds=60
)

for strategy in strategies:
    print(f"{strategy.strategy_type}: {strategy.sentiment}")
    print(f"  Legs: {len(strategy.legs)}")
    print(f"  Net Premium: ${strategy.net_premium:,.0f}")
    print(f"  Net Delta: {strategy.net_delta:,.0f}")
    print(f"  Reasoning: {strategy.reasoning}")
```

**Supported Strategies:**
- Call/Put Spreads (bullish/bearish)
- Straddles (volatility play)
- Strangles (volatility play)
- Calendar Spreads (time decay)
- Butterflies, Iron Condors, Collars

**Activity Level Classification:**

```python
level = detector.get_activity_level(ticker="AAPL", flows=flows, chain=chain)

# Levels: NORMAL, ELEVATED (2-3x), HIGH (3-5x), VERY_HIGH (5-10x), EXTREME (>10x)
```

## Integration with Trading Bot

### Add to Alternative Data Aggregator

```python
from src.analysis.options_flow import OptionsFlowAnalyzer, FlowSignal

# In your AlternativeDataAgent
async def get_options_flow_score(self, ticker: str) -> float:
    """Get options flow contribution to composite score"""

    signal = await self.options_analyzer.analyze_ticker(ticker)

    # Convert signal to score (-1 to +1)
    signal_scores = {
        FlowSignal.VERY_BULLISH: 1.0,
        FlowSignal.BULLISH: 0.5,
        FlowSignal.NEUTRAL: 0.0,
        FlowSignal.BEARISH: -0.5,
        FlowSignal.VERY_BEARISH: -1.0
    }

    base_score = signal_scores[signal.signal]

    # Weight by confidence
    weighted_score = base_score * signal.confidence

    return weighted_score

# In composite_score calculation
options_score = await self.get_options_flow_score(ticker)
composite_score = (
    insider_score * 0.3 +
    google_trends_score * 0.2 +
    options_score * 0.5  # Options flow heavily weighted
)
```

### Generate Pre-Market Report

```python
# In scripts/automation/daily_claude_research.py

async def add_options_flow_section(ticker: str, report: str) -> str:
    """Add options flow analysis to research report"""

    fetcher = OptionsDataFetcher(fd_api_key=os.getenv('FINANCIAL_DATASETS_API_KEY'))
    analyzer = OptionsFlowAnalyzer(data_fetcher=fetcher)

    signal = await analyzer.analyze_ticker(ticker, minutes_back=390)  # Full trading day

    # Add section to report
    options_section = f"""
## Options Flow Analysis

**Signal**: {signal.signal} ({signal.confidence:.1%} confidence)

**Key Metrics**:
- Put/Call Ratio: {signal.put_call_metrics.volume_ratio:.2f} ({signal.put_call_metrics.volume_ratio_deviation:+.1f} std devs)
- Flow Imbalance: ${signal.flow_imbalance.total_imbalance:,.0f} ({signal.flow_imbalance.imbalance_ratio:+.1%})
- Net Delta Exposure: {signal.delta_gamma.net_delta:,.0f} contracts (${signal.delta_gamma.delta_notional:,.0f} notional)
- Large Trades: {signal.large_trades_count} (>$100k premium)
- Sweep Orders: {signal.sweep_orders_count} (urgent flow)

**Interpretation**: {signal.reasoning}

**Component Signals**:
- Put/Call: {signal.put_call_signal}
- Flow Imbalance: {signal.flow_imbalance_signal}
- Delta Exposure: {signal.delta_exposure_signal}
- Unusual Activity: {signal.unusual_activity_signal}
"""

    return report + options_section
```

### Real-Time Alerts

```python
# Monitor for significant options activity
async def monitor_options_flow(tickers: List[str]):
    """Monitor options flow and send alerts for significant activity"""

    fetcher = OptionsDataFetcher()
    analyzer = OptionsFlowAnalyzer(data_fetcher=fetcher)
    detector = UnusualActivityDetector()

    while True:
        for ticker in tickers:
            signal = await analyzer.analyze_ticker(ticker, minutes_back=15)  # Last 15 min

            # Alert on high-confidence signals
            if signal.confidence > 0.7:
                await send_telegram_alert(
                    f"🚨 {ticker} Options Alert\n"
                    f"Signal: {signal.signal} ({signal.confidence:.1%})\n"
                    f"{signal.reasoning}\n"
                    f"Large trades: {signal.large_trades_count}, Sweeps: {signal.sweep_orders_count}"
                )

            # Alert on unusual activity
            flows = await fetcher.fetch_options_flow(ticker, minutes_back=15)
            chain = await fetcher.fetch_options_chain(ticker)
            spot = await fetcher.get_spot_price(ticker)

            unusual_trades = detector.detect_unusual_trades(ticker, flows, chain, spot)

            for trade in unusual_trades:
                if trade.conviction_score > 0.7:
                    await send_telegram_alert(
                        f"🔔 {ticker} Unusual Options Trade\n"
                        f"Premium: ${trade.flow.premium:,.0f}\n"
                        f"Sentiment: {trade.flow.sentiment}\n"
                        f"Conviction: {trade.conviction_score:.1%}\n"
                        f"{' | '.join(trade.reasoning)}"
                    )

        await asyncio.sleep(300)  # Check every 5 minutes
```

## Best Practices

### 1. Data Source Strategy

**Free (Yahoo Finance)**:
- Good for basic analysis
- 15-20 minute delay
- Limited to chain data
- No real-time flow

**Paid (Financial Datasets API)**:
- Real-time flow data
- Sweep order detection
- Greeks included
- Worth it for serious trading

**Recommendation**: Start with Yahoo for testing, upgrade to FD API for live trading.

### 2. Signal Interpretation

**High Confidence (>70%)**:
- Multiple signals align
- Large trades + sweeps confirm direction
- Flow imbalance >40%
- Act on these signals

**Medium Confidence (40-70%)**:
- Mixed signals
- Moderate activity
- Use as supporting evidence
- Combine with other analysis

**Low Confidence (<40%)**:
- Conflicting signals
- Low activity
- Ignore or wait for confirmation

### 3. Timeframes

**Intraday (15-60 min)**:
- Detect immediate smart money moves
- React to breaking catalysts
- Day trading opportunities

**Daily (Full trading day)**:
- Identify swing trade setups
- Confirm multi-day trends
- Position sizing guidance

**Weekly (5 trading days)**:
- Validate longer-term thesis
- Options expiration analysis
- Major positioning changes

### 4. Position Sizing Based on Flow

```python
# Example position sizing logic
def calculate_position_size(signal: OptionsFlowSignal, base_size: float) -> float:
    """Adjust position size based on options flow signal"""

    # Start with base size
    size = base_size

    # Adjust for confidence
    size *= signal.confidence

    # Increase for very strong signals
    if signal.signal == FlowSignal.VERY_BULLISH:
        size *= 1.5
    elif signal.signal == FlowSignal.VERY_BEARISH:
        size *= 1.5

    # Increase for sweep orders (urgent smart money)
    if signal.sweep_orders_count >= 3:
        size *= 1.2

    # Increase for large trades (institutional)
    if signal.large_trades_count >= 5:
        size *= 1.2

    # Cap at 2x base size
    size = min(size, base_size * 2.0)

    return size
```

### 5. False Signal Mitigation

**Avoid:**
- Low volume stocks (options may be illiquid)
- Expiration week (unusual activity is normal)
- Earnings day (volatility makes flow unreliable)
- First 30 min of trading (opening imbalances)

**Confirm with:**
- Price action (does stock move with flow?)
- Technical levels (flow at support/resistance?)
- News/catalysts (flow ahead of announcement?)
- Insider trading (insiders buying with bullish flow?)

## Testing

Run comprehensive test suite:

```bash
# Run all options flow tests
pytest tests/test_options_flow.py -v

# Run with coverage
pytest tests/test_options_flow.py --cov=src.data --cov=src.analysis --cov=src.signals --cov-report=html

# Run specific test classes
pytest tests/test_options_flow.py::TestOptionsFlowAnalyzer -v
pytest tests/test_options_flow.py::TestUnusualActivityDetector -v
```

## Performance Metrics

Track signal accuracy:

```python
# Track signals and outcomes
class OptionsFlowTracker:
    def __init__(self):
        self.signals = []

    def record_signal(self, ticker: str, signal: OptionsFlowSignal, entry_price: float):
        """Record a signal for tracking"""
        self.signals.append({
            'ticker': ticker,
            'timestamp': datetime.now(),
            'signal': signal.signal,
            'confidence': signal.confidence,
            'entry_price': entry_price,
            'exit_price': None,
            'return': None,
            'correct': None
        })

    def update_outcome(self, ticker: str, exit_price: float, days_held: int = 1):
        """Update with actual outcome"""
        for signal in reversed(self.signals):
            if signal['ticker'] == ticker and signal['exit_price'] is None:
                signal['exit_price'] = exit_price
                signal['return'] = (exit_price - signal['entry_price']) / signal['entry_price']

                # Determine if signal was correct
                if signal['signal'] in [FlowSignal.BULLISH, FlowSignal.VERY_BULLISH]:
                    signal['correct'] = signal['return'] > 0
                elif signal['signal'] in [FlowSignal.BEARISH, FlowSignal.VERY_BEARISH]:
                    signal['correct'] = signal['return'] < 0
                else:
                    signal['correct'] = abs(signal['return']) < 0.02

                break

    def get_statistics(self):
        """Get accuracy statistics"""
        completed = [s for s in self.signals if s['correct'] is not None]

        if not completed:
            return {}

        correct_count = sum(1 for s in completed if s['correct'])
        accuracy = correct_count / len(completed)

        avg_return = sum(s['return'] for s in completed) / len(completed)

        # By confidence bucket
        high_conf = [s for s in completed if s['confidence'] > 0.7]
        high_conf_accuracy = sum(1 for s in high_conf if s['correct']) / len(high_conf) if high_conf else 0

        return {
            'total_signals': len(self.signals),
            'completed': len(completed),
            'accuracy': accuracy,
            'avg_return': avg_return,
            'high_confidence_accuracy': high_conf_accuracy
        }
```

## Troubleshooting

**Issue**: No flow data returned
- **Check**: Financial Datasets API key is valid
- **Solution**: Verify key in .env, check API quota

**Issue**: Put/call ratio always neutral
- **Check**: Historical data is being accumulated
- **Solution**: Run analyzer for 30 days to build averages

**Issue**: No unusual activity detected
- **Check**: Thresholds may be too high
- **Solution**: Lower unusual_volume_multiplier (e.g., 2.0x instead of 3.0x)

**Issue**: Too many false signals
- **Check**: Confidence threshold
- **Solution**: Only act on signals with confidence >70%

## API Costs

**Yahoo Finance**: FREE
- Unlimited requests
- 15-20 minute delay
- Basic chain data only

**Financial Datasets API**: $49-199/month
- Real-time flow data
- Sweep order detection
- Greeks included
- 10,000-50,000 requests/month

**Recommendation**: $49/month plan sufficient for 10-20 tickers monitored throughout trading day.

---

**Version**: 1.0.0
**Last Updated**: October 23, 2025
**Files**: 2,743 lines (609 fetcher + 730 analyzer + 641 detector + 763 tests)
**Test Coverage**: 60+ comprehensive tests across all components
