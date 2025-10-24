# Multi-Account Alpaca Setup - DEE-BOT & SHORGAN-BOT

## Architecture Overview

This AI Trading Bot uses **TWO separate Alpaca paper trading accounts** to implement different trading strategies independently:

### Account 1: DEE-BOT (Beta-Neutral Defensive)
- **Strategy**: Beta-neutral defensive positions
- **Focus**: Low-volatility dividend stocks (JNJ, PG, KO, VZ, etc.)
- **Goal**: Stable returns with minimal market correlation
- **Account Number**: PA36XW8J7YE9
- **Current Equity**: $102,816.33
- **Current Cash**: $48,999.58

### Account 2: SHORGAN-BOT (Catalyst-Driven)
- **Strategy**: Event-driven catalyst trades
- **Focus**: FDA catalysts, M&A arbitrage, earnings plays
- **Goal**: High-conviction tactical opportunities
- **Account Number**: PA3JDHT257IL
- **Current Equity**: $104,095.90
- **Current Cash**: $89,309.51

---

## Environment Variable Configuration

Your `.env` file contains **THREE sets of Alpaca API keys**:

### 1. DEE-BOT API Keys (Primary Account)
```bash
# DEE-BOT Paper Trading API (Account 1)
ALPACA_API_KEY_DEE=PKLW68W7RZJFTXV8LJO8
ALPACA_SECRET_KEY_DEE=HV3epwO5AqhqNQEiv3piSOVGD40ly0rW98whdGMv
```

### 2. SHORGAN-BOT API Keys (Secondary Account)
```bash
# SHORGAN-BOT Paper Trading API (Account 2)
ALPACA_API_KEY_SHORGAN=PKDNSGIY71EZGG40EHOV
ALPACA_SECRET_KEY_SHORGAN=Z0Kz1Ay7K9uXSkXomVRxl8BavEGqsfiv3qQvLhx9
```

### 3. Default/Primary Keys (Used by Scripts)
```bash
# DEE-BOT (primary variables used by trading scripts)
ALPACA_API_KEY=CKFO1ITKSVL7H902VBS2
ALPACA_SECRET_KEY=RF2ytLXhWqOB01s77fvIWFwI0NH6bY3DAFwLKq1cxKU8hGhTm5
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

**Note**: The generic `ALPACA_API_KEY` variables are set to DEE-BOT's keys by default. Scripts can override to use SHORGAN-BOT keys when needed.

---

## Setup Script Behavior

The updated `scripts/setup.py` now:

1. **Prompts for DEE-BOT keys separately**:
   ```
   📈 DEE-BOT Alpaca API Keys (Paper Trading Account 1)
   Get your keys at: https://app.alpaca.markets/paper/dashboard/overview
   DEE-BOT uses beta-neutral defensive strategies
   Enter DEE-BOT Alpaca API key:
   Enter DEE-BOT Alpaca secret key:
   ```

2. **Prompts for SHORGAN-BOT keys separately**:
   ```
   📊 SHORGAN-BOT Alpaca API Keys (Paper Trading Account 2)
   Get your keys at: https://app.alpaca.markets/paper/dashboard/overview
   SHORGAN-BOT uses catalyst-driven strategies
   Enter SHORGAN-BOT Alpaca API key:
   Enter SHORGAN-BOT Alpaca secret key:
   ```

3. **Sets default/primary keys** to DEE-BOT:
   ```python
   api_keys['ALPACA_API_KEY'] = api_keys['ALPACA_API_KEY_DEE']
   api_keys['ALPACA_SECRET_KEY'] = api_keys['ALPACA_SECRET_KEY_DEE']
   api_keys['ALPACA_BASE_URL'] = 'https://paper-api.alpaca.markets'
   ```

4. **Tests BOTH API connections** during setup:
   ```
   Testing DEE-BOT Alpaca API... ✓ ($102,816.33)
   Testing SHORGAN-BOT Alpaca API... ✓ ($104,095.90)
   ```

---

## Testing API Connections

### Test Both Accounts

Run the comprehensive test script:

```bash
python test_alpaca_dee_bot.py
```

**Expected Output**:
```
================================================================================
                   TESTING ALPACA API CONNECTIONS - BOTH BOTS
================================================================================

[1/2] Testing DEE-BOT Alpaca API...
      API Key: PKLW68W7RZJFTXV8LJO8
      [SUCCESS] DEE-BOT Alpaca API connection working
      Account: PA36XW8J7YE9
      Equity: $102,816.33
      Cash: $48,999.58

[2/2] Testing SHORGAN-BOT Alpaca API...
      API Key: PKDNSGIY71EZGG40EHOV
      [SUCCESS] SHORGAN-BOT Alpaca API connection working
      Account: PA3JDHT257IL
      Equity: $104,095.90
      Cash: $89,309.51

================================================================================
```

### Test Individual Accounts

Test only DEE-BOT:
```python
from alpaca.trading.client import TradingClient
import os
from dotenv import load_dotenv

load_dotenv()

client = TradingClient(
    os.getenv('ALPACA_API_KEY_DEE'),
    os.getenv('ALPACA_SECRET_KEY_DEE'),
    paper=True
)
account = client.get_account()
print(f"DEE-BOT Equity: ${float(account.equity):,.2f}")
```

Test only SHORGAN-BOT:
```python
from alpaca.trading.client import TradingClient
import os
from dotenv import load_dotenv

load_dotenv()

client = TradingClient(
    os.getenv('ALPACA_API_KEY_SHORGAN'),
    os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    paper=True
)
account = client.get_account()
print(f"SHORGAN-BOT Equity: ${float(account.equity):,.2f}")
```

---

## Usage in Trading Scripts

### Selecting Which Account to Use

**For DEE-BOT trades** (defensive stocks):
```python
from alpaca.trading.client import TradingClient
import os

# Use DEE-BOT API keys
client = TradingClient(
    os.getenv('ALPACA_API_KEY_DEE'),
    os.getenv('ALPACA_SECRET_KEY_DEE'),
    paper=True
)
```

**For SHORGAN-BOT trades** (catalyst plays):
```python
from alpaca.trading.client import TradingClient
import os

# Use SHORGAN-BOT API keys
client = TradingClient(
    os.getenv('ALPACA_API_KEY_SHORGAN'),
    os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    paper=True
)
```

**Using default/primary keys**:
```python
from alpaca.trading.client import TradingClient
import os

# Uses DEE-BOT keys by default (since ALPACA_API_KEY = ALPACA_API_KEY_DEE)
client = TradingClient(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_SECRET_KEY'),
    paper=True
)
```

---

## Why Two Accounts?

### Benefits of Multi-Account Architecture

1. **Strategy Isolation**:
   - DEE-BOT and SHORGAN-BOT can operate independently
   - No interference between defensive and aggressive positions
   - Clear separation of risk profiles

2. **Performance Tracking**:
   - Easy to compare strategy performance
   - DEE-BOT: Benchmark against defensive indices (SPLV, VIG)
   - SHORGAN-BOT: Benchmark against volatility plays (VIX)

3. **Risk Management**:
   - Separate capital allocation for each strategy
   - DEE-BOT: Lower leverage, longer holding periods
   - SHORGAN-BOT: Higher conviction, tactical entries/exits

4. **Regulatory Compliance**:
   - Pattern Day Trader (PDT) rules apply per account
   - Two accounts = 2x the day trading limit (if needed)

5. **Testing and Validation**:
   - Test new strategies on one account without affecting the other
   - A/B testing between defensive vs aggressive approaches

---

## Current Status (October 23, 2025)

### DEE-BOT Performance
- **Starting Capital**: $100,000 (assumed)
- **Current Equity**: $102,816.33
- **Return**: +2.82%
- **Cash Reserve**: $48,999.58 (47.7%)
- **Strategy**: Working as intended (defensive, low beta)

### SHORGAN-BOT Performance
- **Starting Capital**: $100,000 (assumed)
- **Current Equity**: $104,095.90
- **Return**: +4.10%
- **Cash Reserve**: $89,309.51 (85.8%)
- **Strategy**: Working as intended (catalyst-driven, selective)

### Combined Portfolio
- **Total Value**: $206,912.23
- **Combined Return**: +3.46%
- **Total Cash**: $138,309.09 (66.9% dry powder)
- **Status**: ✅ Both accounts operational and profitable

---

## Troubleshooting

### "unauthorized" Error

If you see `{"message": "unauthorized."}`:

1. **Check which account is failing**:
   ```bash
   python test_alpaca_dee_bot.py
   ```

2. **Verify API keys in .env**:
   ```bash
   # Show DEE-BOT keys (first 10 chars)
   cat .env | grep ALPACA_API_KEY_DEE

   # Show SHORGAN-BOT keys (first 10 chars)
   cat .env | grep ALPACA_API_KEY_SHORGAN
   ```

3. **Regenerate keys if needed**:
   - Go to: https://app.alpaca.markets/paper/dashboard/overview
   - Log in to the specific account (DEE or SHORGAN)
   - Generate new API keys
   - Update `.env` with the new keys
   - **Important**: Secret keys are only shown ONCE

4. **Test again**:
   ```bash
   python test_alpaca_dee_bot.py
   ```

### Rate Limiting

Alpaca paper trading has rate limits:
- **200 requests per minute** per account
- With 2 accounts = 400 requests/minute total
- If hitting limits, add delay between requests:
  ```python
  import time
  time.sleep(0.3)  # 300ms delay = max 200 req/min
  ```

---

## Setup Complete Verification

After running `python complete_setup.py`, you should see:

```
Testing Alpaca API Connections (Both Bots)
------------------------------------------------------------------------------

[1/2] Testing DEE-BOT Alpaca API...
  [SUCCESS] DEE-BOT Alpaca API connection working
    Account: PA36XW8J7YE9
    Equity: $102,816.33
    Cash: $48,999.58

[2/2] Testing SHORGAN-BOT Alpaca API...
  [SUCCESS] SHORGAN-BOT Alpaca API connection working
    Account: PA3JDHT257IL
    Equity: $104,095.90
    Cash: $89,309.51

[SUCCESS] At least one Alpaca API connection working
```

If both tests pass: ✅ **Setup complete! Both trading accounts are ready.**

---

## Files Updated for Multi-Account Support

1. **`scripts/setup.py`**:
   - Updated to prompt for both DEE-BOT and SHORGAN-BOT keys
   - Tests both API connections during setup
   - Sets default keys to DEE-BOT

2. **`complete_setup.py`**:
   - Updated to test both API connections
   - Shows equity/cash for both accounts
   - Validates multi-account architecture

3. **`test_alpaca_dee_bot.py`**:
   - NEW: Comprehensive test for both accounts
   - Shows account numbers, equity, and cash
   - Clear success/error messages

4. **`SETUP_FIX_GUIDE.md`**:
   - Updated to reflect multi-account architecture
   - Shows current account status
   - Provides troubleshooting for both accounts

5. **`.env`**:
   - Already had multi-account keys configured
   - No changes needed (keys working correctly)

---

**Last Updated**: October 23, 2025
**Status**: ✅ Multi-Account Setup Complete and Operational
