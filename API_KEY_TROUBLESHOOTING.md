# API Key Troubleshooting - SHORGAN-BOT Paper Account

## Current Status (as of Nov 5, 4:15 AM)

| Account | API Status | Portfolio Value | Notes |
|---------|-----------|----------------|--------|
| DEE-BOT (Paper) | ✅ WORKING | $100,846.08 | Keys working perfectly |
| SHORGAN-BOT (Paper) | ❌ FAILED | Unknown | 401 Unauthorized error |
| SHORGAN-BOT (Live) | ✅ WORKING | $2,002.66 | Keys working perfectly |

## Problem

The SHORGAN-BOT Paper account is still returning `401 Unauthorized` even after rotating keys.

**Current keys in .env**:
```
ALPACA_API_KEY_SHORGAN=PKV2XHQUC4E4SPYRMTWXGMEHZA
ALPACA_SECRET_KEY_SHORGAN=Z0Kz1Ay7K9uXSkXomVRxl8BavEGqsfiv3qQvLhx9
```

## Possible Causes

### 1. Keys Copied Incorrectly
The most common issue - a character was missed or added when copying from Alpaca dashboard to .env file.

**Solution**:
1. Login to https://alpaca.markets/
2. Navigate to **Paper Trading** account (NOT Live Trading)
3. Go to API Keys section
4. Find the key you just created
5. **CAREFULLY** copy both:
   - API Key ID (starts with PK...)
   - Secret Key
6. Update `.env` file:
   ```
   ALPACA_API_KEY_SHORGAN=<paste_key_id_here>
   ALPACA_SECRET_KEY_SHORGAN=<paste_secret_here>
   ```
7. Make sure there are:
   - NO extra spaces before or after the =
   - NO quotes around the keys
   - NO line breaks in the middle of a key

### 2. Keys Not Activated Yet
Newly generated keys can take 1-2 minutes to propagate through Alpaca's system.

**Solution**: Wait 2-3 minutes and test again:
```bash
python test_api_keys.py
```

### 3. Wrong Alpaca Account
You might have multiple Alpaca accounts and generated keys for the wrong one.

**Solution**:
1. In Alpaca dashboard, verify you're in the **Paper Trading** account
2. Check the account email/username - is it the one you expect?
3. If you have multiple accounts, make sure you're generating keys for SHORGAN-BOT

### 4. Old Keys Not Deleted
Sometimes old keys interfere with new ones.

**Solution**:
1. In Alpaca dashboard → Paper Trading → API Keys
2. **Delete** all keys
3. Generate ONE new set of keys
4. Copy to .env file
5. Test immediately

## How to Test Keys

Run this command to test all three accounts:
```bash
python test_api_keys.py
```

Expected output:
```
[OK] DEE-BOT: $100,846.08
[OK] SHORGAN-BOT Paper: $XXX,XXX.XX
[OK] SHORGAN-BOT Live: $2,002.66
```

## Step-by-Step Fix (Recommended)

1. **Login to Alpaca**: https://alpaca.markets/

2. **Select Paper Trading Account**
   - Make sure you're in the PAPER trading view (not Live)

3. **Go to API Keys Section**
   - Usually under Settings → API Keys or similar

4. **Delete ALL existing keys**
   - This ensures no conflicts

5. **Generate ONE new key**
   - Click "Generate New Key" or similar button
   - Give it a name like "SHORGAN-BOT-Nov5"

6. **IMMEDIATELY copy both values**
   - API Key ID: Should start with "PK" (26 characters)
   - Secret Key: Long string (~40 characters)

7. **Open .env file in notepad**
   ```bash
   notepad .env
   ```

8. **Find these two lines and update them**:
   ```
   ALPACA_API_KEY_SHORGAN=PKV2XHQUC4E4SPYRMTWXGMEHZA
   ALPACA_SECRET_KEY_SHORGAN=Z0Kz1Ay7K9uXSkXomVRxl8BavEGqsfiv3qQvLhx9
   ```

   Replace with your NEW values (no spaces, no quotes):
   ```
   ALPACA_API_KEY_SHORGAN=YOUR_NEW_KEY_HERE
   ALPACA_SECRET_KEY_SHORGAN=YOUR_NEW_SECRET_HERE
   ```

9. **Save the file** (Ctrl+S)

10. **Close notepad**

11. **Test immediately**:
    ```bash
    python test_api_keys.py
    ```

12. **Should see**:
    ```
    [OK] DEE-BOT: $100,846.08
    [OK] SHORGAN-BOT Paper: $XXX,XXX.XX
    [OK] SHORGAN-BOT Live: $2,002.66
    ```

## If Still Failing

If you've tried all the above and it's still failing:

1. **Double-check you're in PAPER account** (not Live)
   - Paper trading has its own separate API keys
   - Live trading has different keys

2. **Check for hidden characters**:
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(repr(os.getenv('ALPACA_API_KEY_SHORGAN'))); print(repr(os.getenv('ALPACA_SECRET_KEY_SHORGAN')))"
   ```
   - Should NOT see any `\n`, `\r`, or extra spaces

3. **Try regenerating keys one more time**
   - Delete all keys in dashboard
   - Generate fresh set
   - Copy very carefully
   - Test within 30 seconds

## Current Working Keys (for reference)

These keys ARE working:
- **DEE-BOT**: Currently working with keys in .env ✅
- **SHORGAN Live**: Currently working with keys in .env ✅

So we know:
- The .env file format is correct
- Python can read the .env file
- Alpaca API connection is working
- It's specifically the SHORGAN Paper keys that are wrong

## Next Steps

1. Go through the "Step-by-Step Fix" above
2. Test with `python test_api_keys.py`
3. Once all 3 show [OK], you're ready to:
   - Generate complete research (all 3 accounts)
   - Setup Task Scheduler
   - Run full automation

## Questions?

If you're still stuck after trying all the above, check:
- Are you sure you have a SHORGAN-BOT Paper Trading account?
- Did you maybe delete the Paper account and only have Live?
- Is the email/login correct for the Paper account?
