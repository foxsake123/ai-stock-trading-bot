# API Usage Guide

This document provides comprehensive information about all APIs used in the AI Stock Trading Bot system, including costs, rate limits, and configuration options.

---

## Table of Contents

1. [APIs Overview](#apis-overview)
2. [Anthropic Claude API](#anthropic-claude-api)
3. [Alpaca Markets API](#alpaca-markets-api)
4. [Financial Datasets API](#financial-datasets-api)
5. [Yahoo Finance (yfinance)](#yahoo-finance-yfinance)
6. [Estimated Daily Costs](#estimated-daily-costs)
7. [Rate Limits and Handling](#rate-limits-and-handling)
8. [Switching Models](#switching-models)
9. [API Key Management](#api-key-management)
10. [Troubleshooting](#troubleshooting)

---

## APIs Overview

The system integrates multiple APIs for different purposes:

| API | Purpose | Cost | Required |
|-----|---------|------|----------|
| **Anthropic Claude** | AI research & report generation | Pay-per-token | Yes |
| **Alpaca Markets** | Trade execution & portfolio data | Free (paper trading) | Yes |
| **Financial Datasets** | Professional market data | $49/month | Recommended |
| **Yahoo Finance** | Free market data (backup) | Free | Optional |
| **Telegram Bot** | Trade notifications | Free | Optional |

---

## Anthropic Claude API

### Purpose
Generates comprehensive trading research reports using large language models.

### Models Used

**Primary Model:**
```python
MODEL = "claude-sonnet-4-20250514"  # Default in daily_premarket_report.py
```

**Alternative Models:**
- `claude-opus-4-20250514` - Most capable, slower, more expensive
- `claude-sonnet-4-20250514` - Balanced performance (recommended)
- `claude-haiku-4-20250301` - Fastest, cheapest, less capable

### Pricing (as of October 2025)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Speed |
|-------|----------------------|------------------------|-------|
| Claude Opus 4 | $15.00 | $75.00 | Slow |
| Claude Sonnet 4 | $3.00 | $15.00 | Medium |
| Claude Haiku 4 | $0.25 | $1.25 | Fast |

### Usage in System

**Daily Pre-Market Report:**
- Input: ~7,000 tokens (prompt + market data)
- Output: ~9,000 tokens (comprehensive report)
- Total cost per report (Sonnet 4):
  ```
  Input:  7,000 tokens × $3.00 / 1M = $0.021
  Output: 9,000 tokens × $15.00 / 1M = $0.135
  Total: $0.156 per report (~$0.16)
  ```

**Multi-Agent Consensus System:**
- 7 agents × 2,000 tokens each = 14,000 input tokens
- 7 agents × 500 output tokens each = 3,500 output tokens
- Cost per consensus (Sonnet 4):
  ```
  Input:  14,000 × $3.00 / 1M = $0.042
  Output: 3,500 × $15.00 / 1M = $0.0525
  Total: $0.095 per consensus (~$0.10)
  ```

### Configuration

**Environment Variables (.env):**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...your-key-here
```

**Getting API Key:**
1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Create new key
5. Copy to .env file

**Usage Tracking:**
- Check usage: https://console.anthropic.com/settings/usage
- Set spending limits in console
- Monitor token usage in logs

### Rate Limits

| Tier | Requests per minute | Tokens per minute |
|------|-------------------|-------------------|
| Free | 5 | 50,000 |
| Build (Tier 1) | 50 | 100,000 |
| Scale (Tier 2) | 1,000 | 400,000 |

**Rate Limit Handling:**
```python
# Automatic retry with exponential backoff (built into Anthropic SDK)
from anthropic import Anthropic, RateLimitError
import time

def call_claude_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.messages.create(...)
            return response
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
                continue
            raise
```

---

## Alpaca Markets API

### Purpose
Executes trades and fetches portfolio data for paper (simulated) trading.

### Pricing
- **Paper Trading:** 100% FREE (unlimited)
- **Live Trading:** $0 commissions (not used in this system)

### Features Used

1. **Order Execution**
   - Market orders
   - Limit orders
   - Stop-loss orders (GTC)

2. **Portfolio Data**
   - Current positions
   - Account balance
   - Buying power
   - Order history

3. **Market Data**
   - Real-time quotes
   - Historical bars
   - Latest trades

### Configuration

**Environment Variables (.env):**
```bash
ALPACA_API_KEY=PKxxxxxxxxxxxxxx
ALPACA_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

**Getting API Keys:**
1. Visit https://alpaca.markets/
2. Sign up for account
3. Navigate to "Paper Trading"
4. Copy API Key and Secret Key
5. Add to .env file

**Important:** Use paper trading URL for testing:
```python
BASE_URL = "https://paper-api.alpaca.markets"  # Paper trading
# BASE_URL = "https://api.alpaca.markets"  # Live trading (DO NOT USE)
```

### Rate Limits

| Endpoint | Limit |
|----------|-------|
| Orders (POST) | 200 per minute |
| Account (GET) | 200 per minute |
| Positions (GET) | 200 per minute |
| Market Data | 200 per minute per endpoint |

**Rate Limit Handling:**
```python
from alpaca.trading.requests import LimitOrderRequest
from alpaca.common.exceptions import APIError
import time

def place_order_with_retry(trading_client, request):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            order = trading_client.submit_order(request)
            return order
        except APIError as e:
            if "rate limit" in str(e).lower():
                time.sleep(1)
                continue
            raise
```

### Market Hours

**Regular Trading Hours:**
- Monday-Friday: 9:30 AM - 4:00 PM ET
- Closed weekends and market holidays

**Extended Hours (not used in system):**
- Pre-market: 4:00 AM - 9:30 AM ET
- After-hours: 4:00 PM - 8:00 PM ET

---

## Financial Datasets API

### Purpose
Professional-grade financial data for enhanced trading decisions.

### Pricing
- **Starter Plan:** $49/month
- **Professional Plan:** $199/month
- **Enterprise:** Custom pricing

### Features Used

1. **Real-Time Quotes**
   - Current prices
   - Bid/ask spreads
   - Volume

2. **Financial Statements**
   - Income statements
   - Balance sheets
   - Cash flow statements

3. **Insider Trading Data**
   - Form 4 filings
   - Cluster buying/selling
   - C-suite transactions

4. **Institutional Ownership**
   - Top holders
   - Ownership percentages
   - 13F filings

5. **News Sentiment**
   - Real-time news articles
   - Sentiment scoring
   - Source attribution

### Configuration

**Environment Variables (.env):**
```bash
FINANCIAL_DATASETS_API_KEY=fd_xxxxxxxxxxxxxxxxxxxxxxxx
```

**Getting API Key:**
1. Visit https://financialdatasets.ai/
2. Sign up for Starter plan ($49/month)
3. Navigate to "API Keys"
4. Copy API key
5. Add to .env file

### Rate Limits

| Plan | Requests per minute | Monthly quota |
|------|-------------------|---------------|
| Starter | 10 | 10,000 |
| Professional | 60 | 100,000 |
| Enterprise | Unlimited | Unlimited |

**Rate Limit Handling:**
```python
from financial_datasets import FinancialDatasets
import time

def fetch_with_rate_limit(api, symbol):
    try:
        data = api.get_prices(symbol)
        return data
    except Exception as e:
        if "rate limit" in str(e).lower():
            print("Rate limit hit, waiting 60 seconds...")
            time.sleep(60)
            return fetch_with_rate_limit(api, symbol)
        raise
```

### API Endpoints Used

```python
from financial_datasets import FinancialDatasets

api = FinancialDatasets(api_key=API_KEY)

# 1. Real-time prices
prices = api.get_prices(symbol="AAPL")

# 2. Financial statements
financials = api.get_financials(symbol="AAPL", statement="income", period="quarterly")

# 3. Insider trades
insider_trades = api.get_insider_trades(symbol="AAPL", limit=50)

# 4. Institutional ownership
institutional = api.get_institutional_ownership(symbol="AAPL")

# 5. News with sentiment
news = api.get_news(symbol="AAPL", limit=10)
```

---

## Yahoo Finance (yfinance)

### Purpose
Free backup data source when Financial Datasets unavailable.

### Pricing
100% FREE (no API key required)

### Features Used

1. **Market Indices**
   - S&P 500 (^GSPC)
   - VIX (^VIX)
   - 10-Year Treasury (^TNX)

2. **Futures Data**
   - ES=F (S&P 500 Futures)
   - NQ=F (Nasdaq Futures)
   - RTY=F (Russell 2000 Futures)

3. **Currency Data**
   - DX-Y.NYB (Dollar Index)

### Configuration

No configuration needed - library is built into yfinance package.

```python
import yfinance as yf

# Fetch market data
ticker = yf.Ticker("^VIX")
data = ticker.history(period="1d")
print(f"VIX: {data['Close'].iloc[-1]}")
```

### Rate Limits

**Unofficial limits (observed):**
- ~48 requests per hour per IP
- ~2,000 requests per day per IP
- Exceeding limits = temporary IP ban (1-24 hours)

**Rate Limit Handling:**
```python
import yfinance as yf
import time

def fetch_with_backoff(symbol, max_retries=3):
    for attempt in range(max_retries):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            return data
        except Exception as e:
            if "Too Many Requests" in str(e) or "429" in str(e):
                wait_time = (2 ** attempt) * 30  # 30s, 60s, 120s
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            raise
    raise Exception("Max retries exceeded")
```

### Known Issues

1. **Unreliable for high-frequency queries**
   - Solution: Use Financial Datasets API instead

2. **S&P 500 data often unavailable**
   - Issue: Yahoo Finance blocks programmatic access
   - Solution: Use Alpha Vantage or Financial Datasets

3. **No official API support**
   - Issue: Library scrapes website (can break)
   - Solution: Always have fallback data source

---

## Estimated Daily Costs

### Daily Operation Costs

| Component | Usage | Cost per Day | Cost per Month |
|-----------|-------|--------------|----------------|
| **Anthropic Claude (Sonnet 4)** | | | |
| Daily pre-market report | 1 report | $0.16 | $4.80 |
| Multi-agent consensus | 1 consensus | $0.10 | $3.00 |
| **Alpaca Markets** | | | |
| Paper trading | Unlimited | $0.00 | $0.00 |
| **Financial Datasets** | | | |
| API subscription | N/A | $1.63 | $49.00 |
| **Yahoo Finance** | | | |
| Market data | Unlimited | $0.00 | $0.00 |
| **Telegram Bot** | | | |
| Notifications | Unlimited | $0.00 | $0.00 |
| | | | |
| **TOTAL** | | **$1.89/day** | **$56.80/month** |

### Cost Optimization Strategies

1. **Use Claude Haiku for drafts**
   ```python
   # Switch to Haiku for cheaper, faster drafts
   MODEL = "claude-haiku-4-20250301"  # 83% cost savings
   ```

2. **Batch API calls**
   ```python
   # Instead of 7 separate calls, batch into 1
   # Saves 6 API requests = $0.06 per consensus
   ```

3. **Cache prompts**
   ```python
   # Use prompt caching for repeated queries
   # Reduces input token costs by 90%
   ```

4. **Limit report frequency**
   ```bash
   # Generate reports only on trading days (skip weekends)
   # Saves 8 reports/month = $1.28 savings
   ```

5. **Use free alternatives**
   ```python
   # Use yfinance instead of Financial Datasets when possible
   # Saves $49/month (but lower data quality)
   ```

---

## Rate Limits and Handling

### Centralized Rate Limiter

```python
import time
from datetime import datetime, timedelta

class RateLimiter:
    """Centralized rate limiting for all APIs"""

    def __init__(self):
        self.calls = {
            'anthropic': [],
            'alpaca': [],
            'financial_datasets': [],
            'yfinance': []
        }

    def can_call(self, api_name, limit_per_minute):
        """Check if API call is allowed"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)

        # Remove calls older than 1 minute
        self.calls[api_name] = [
            call_time for call_time in self.calls[api_name]
            if call_time > cutoff
        ]

        # Check if under limit
        if len(self.calls[api_name]) < limit_per_minute:
            self.calls[api_name].append(now)
            return True
        return False

    def wait_if_needed(self, api_name, limit_per_minute):
        """Wait until API call is allowed"""
        while not self.can_call(api_name, limit_per_minute):
            time.sleep(1)

# Usage
limiter = RateLimiter()
limiter.wait_if_needed('anthropic', limit_per_minute=50)
response = client.messages.create(...)
```

### Exponential Backoff Pattern

```python
import time
import random

def exponential_backoff(
    func,
    max_retries=5,
    base_delay=1,
    max_delay=60
):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            # Check if retryable error
            if not is_retryable_error(e):
                raise

            # Calculate delay with jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)
            total_delay = delay + jitter

            print(f"Retry {attempt + 1}/{max_retries} after {total_delay:.1f}s")
            time.sleep(total_delay)

def is_retryable_error(error):
    """Check if error is retryable"""
    retryable = [
        "rate limit",
        "too many requests",
        "timeout",
        "503",
        "429"
    ]
    error_str = str(error).lower()
    return any(term in error_str for term in retryable)
```

---

## Switching Models

### Anthropic Model Selection

**When to use each model:**

**Claude Opus 4 (Most Expensive):**
- Critical trading decisions
- Complex multi-step reasoning
- Long-form research reports
- Cost: ~$0.50 per report

**Claude Sonnet 4 (Recommended):**
- Daily pre-market reports
- Multi-agent consensus
- Balanced quality and cost
- Cost: ~$0.16 per report (default)

**Claude Haiku 4 (Cheapest):**
- Quick summaries
- Simple extractions
- High-volume batch processing
- Cost: ~$0.02 per report

### How to Switch Models

**Method 1: Edit Configuration File**
```python
# In daily_premarket_report.py line ~673
response = self.client.messages.create(
    model='claude-sonnet-4-20250514',  # Change this line
    max_tokens=16000,
    temperature=0.3,
    messages=[...]
)
```

**Method 2: Environment Variable**
```bash
# Add to .env file
CLAUDE_MODEL=claude-haiku-4-20250301

# Then in code:
model = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
```

**Method 3: Command-Line Argument**
```bash
# Run with specific model
python daily_premarket_report.py --model claude-opus-4-20250514
```

### Model Performance Comparison

| Model | Quality | Speed | Cost | Recommended For |
|-------|---------|-------|------|-----------------|
| Opus 4 | Excellent | Slow | High | Critical decisions |
| Sonnet 4 | Good | Medium | Medium | Daily reports (default) |
| Haiku 4 | Fair | Fast | Low | Summaries, drafts |

---

## API Key Management

### Security Best Practices

**1. Use Environment Variables**
```bash
# GOOD: Store in .env file
ANTHROPIC_API_KEY=sk-ant-api03-...

# BAD: Hardcode in source
api_key = "sk-ant-api03-..."  # Don't do this!
```

**2. Add .env to .gitignore**
```gitignore
# .gitignore
.env
.env.local
*.key
```

**3. Rotate Keys Regularly**
- Rotate every 90 days
- Immediately rotate if compromised
- Keep backup keys for transition

**4. Use Separate Keys for Dev/Prod**
```bash
# Development
ANTHROPIC_API_KEY_DEV=sk-ant-api03-dev...

# Production
ANTHROPIC_API_KEY_PROD=sk-ant-api03-prod...
```

**5. Monitor API Usage**
- Set spending alerts
- Review usage logs weekly
- Investigate unusual patterns

### Key Storage Options

**Option 1: .env File (Recommended for development)**
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-...
ALPACA_API_KEY=PK...
ALPACA_SECRET_KEY=...
```

**Option 2: System Environment Variables (Production)**
```bash
# Linux/Mac
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Windows
setx ANTHROPIC_API_KEY "sk-ant-api03-..."
```

**Option 3: Secrets Manager (Enterprise)**
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Google Secret Manager

---

## Troubleshooting

### Common API Errors

**Error 1: "ANTHROPIC_API_KEY not found"**
```
Solution:
1. Create .env file in project root
2. Add: ANTHROPIC_API_KEY=your-key-here
3. Restart script
```

**Error 2: "Rate limit exceeded"**
```
Solution:
1. Wait 60 seconds
2. Reduce request frequency
3. Upgrade API tier if needed
```

**Error 3: "Invalid API key"**
```
Solution:
1. Check for typos in .env file
2. Verify key is active in API console
3. Regenerate key if needed
```

**Error 4: "Insufficient credits"**
```
Solution:
1. Check Anthropic console usage
2. Add payment method if needed
3. Purchase credits
```

**Error 5: "Market closed" (Alpaca)**
```
Solution:
1. Check if market hours (9:30 AM - 4:00 PM ET)
2. Check if market holiday
3. Use queue=True for next market open
```

**Error 6: "S&P 500 data unavailable" (Yahoo Finance)**
```
Solution:
1. Known issue with Yahoo Finance blocking
2. Use Financial Datasets API instead
3. Or use Alpha Vantage API (free alternative)
```

### Debugging API Calls

**Enable Verbose Logging:**
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Logs all API requests/responses
```

**Test API Connectivity:**
```python
# Test Anthropic
from anthropic import Anthropic
client = Anthropic(api_key="sk-ant-api03-...")
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.content[0].text)  # Should print "Hello" response

# Test Alpaca
from alpaca.trading.client import TradingClient
client = TradingClient(api_key="PK...", secret_key="...")
account = client.get_account()
print(f"Account value: ${account.portfolio_value}")  # Should print portfolio value
```

### Performance Optimization

**1. Parallel API Calls**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def fetch_multiple_symbols(symbols):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_data, symbol) for symbol in symbols]
        results = [f.result() for f in futures]
    return results
```

**2. Cache Responses**
```python
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def fetch_stock_data_cached(symbol, cache_time):
    """Cache for 5 minutes (pass time // 300)"""
    return fetch_stock_data(symbol)

# Usage
data = fetch_stock_data_cached("AAPL", cache_time=int(time.time() // 300))
```

**3. Batch Requests**
```python
# Instead of:
for symbol in symbols:
    data = api.get_price(symbol)  # N requests

# Do:
data = api.get_prices_batch(symbols)  # 1 request
```

---

## API Comparison Matrix

| Feature | Anthropic | Alpaca | Financial Datasets | Yahoo Finance |
|---------|-----------|--------|-------------------|---------------|
| **Cost** | Pay-per-use | Free | $49/month | Free |
| **Rate Limits** | 50/min | 200/min | 10/min | ~48/hour |
| **Reliability** | High | High | High | Medium |
| **Data Quality** | N/A | Good | Excellent | Fair |
| **Support** | Excellent | Good | Good | None |
| **Documentation** | Excellent | Good | Good | Poor |
| **Use Case** | AI generation | Trading | Market data | Backup data |

---

*Last Updated: October 13, 2025*
*Version: 2.0*
