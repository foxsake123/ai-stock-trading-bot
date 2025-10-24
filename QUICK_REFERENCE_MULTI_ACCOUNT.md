# Quick Reference: Multi-Account Alpaca Setup

## Current Account Status ✅

```
DEE-BOT (Defensive)          SHORGAN-BOT (Catalyst)
Account: PA36XW8J7YE9         Account: PA3JDHT257IL
Equity:  $102,816.33          Equity:  $104,095.90
Cash:    $48,999.58           Cash:    $89,309.51
Return:  +2.82%               Return:  +4.10%
```

**Combined Portfolio**: $206,912.23 (+3.46% return)

---

## API Keys in .env

```bash
# DEE-BOT (Account 1)
ALPACA_API_KEY_DEE=PKLW68W7RZJFTXV8LJO8
ALPACA_SECRET_KEY_DEE=HV3epwO5AqhqNQEiv3piSOVGD40ly0rW98whdGMv

# SHORGAN-BOT (Account 2)
ALPACA_API_KEY_SHORGAN=PKDNSGIY71EZGG40EHOV
ALPACA_SECRET_KEY_SHORGAN=Z0Kz1Ay7K9uXSkXomVRxl8BavEGqsfiv3qQvLhx9
```

---

## Quick Test Commands

```bash
# Test both accounts
python test_alpaca_dee_bot.py

# Run complete setup (tests all APIs)
python complete_setup.py

# Interactive setup (prompts for both API keys)
python scripts/setup.py
```

---

## Using in Code

**DEE-BOT (defensive trades)**:
```python
from alpaca.trading.client import TradingClient
import os

client = TradingClient(
    os.getenv('ALPACA_API_KEY_DEE'),
    os.getenv('ALPACA_SECRET_KEY_DEE'),
    paper=True
)
```

**SHORGAN-BOT (catalyst trades)**:
```python
from alpaca.trading.client import TradingClient
import os

client = TradingClient(
    os.getenv('ALPACA_API_KEY_SHORGAN'),
    os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    paper=True
)
```

---

## Documentation

- **Complete Guide**: `docs/MULTI_ACCOUNT_SETUP.md`
- **Troubleshooting**: `SETUP_FIX_GUIDE.md` (Issue 1)
- **Session Details**: `docs/session-summaries/SESSION_SUMMARY_2025-10-23_MULTI_ACCOUNT_FIX.md`

---

**Last Updated**: October 23, 2025
**Status**: ✅ Both accounts operational
