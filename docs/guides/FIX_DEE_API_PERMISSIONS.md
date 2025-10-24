# Fix DEE-BOT API Trading Permissions

**Issue**: DEE-BOT API keys are READ-ONLY and cannot place trades.

**Error**: `unauthorized` when attempting to submit orders.

**Root Cause**: API keys were generated without "Trading" permission enabled.

---

## Solution: 3-Step Process

### Step 1: Generate New API Keys in Alpaca Dashboard

1. **Log into Alpaca**:
   - Go to: https://app.alpaca.markets/ (or https://paper-api.alpaca.markets/)
   - Use your **DEE-BOT account** credentials

2. **Navigate to API Keys**:
   - Click **"Settings"** or **"Account"** in sidebar
   - Click **"API Keys"** section

3. **Check Current Keys**:
   - Find your existing API key
   - Check if "Trading" permission is enabled
   - If NOT enabled, you need new keys

4. **Generate New Key with Trading Permission**:
   - Click **"Generate New Key"** or **"Create API Key"**
   - **Name**: `DEE-BOT Trading Key` (or similar)
   - **Permissions**: CHECK ALL THREE BOXES:
     - ✅ **Account** (read account data)
     - ✅ **Trading** (place/modify/cancel orders) ⬅️ **CRITICAL**
     - ✅ **Data** (access market data)
   - Click **"Generate"** or **"Create"**

5. **Copy Credentials** (IMPORTANT):
   - **Key ID**: Copy this (looks like: `PKxxxxxxxxxxxxxx`)
   - **Secret Key**: Copy this immediately (looks like: `xxxxxxxxxxxxxxxxxxxxxxxxxx`)
   - **⚠️ WARNING**: Secret key is shown ONLY ONCE - save it now!

6. **Delete Old Key** (optional):
   - After confirming new keys work, delete the old read-only key

---

### Step 2: Update .env File with New Keys

Run the update script:

```bash
python update_dee_keys.py
```

**It will prompt you for**:
1. New API Key ID
2. New Secret Key

**It will update** these lines in `.env`:
```
ALPACA_API_KEY=YOUR_NEW_KEY_ID
ALPACA_SECRET_KEY=YOUR_NEW_SECRET_KEY
```

**Alternative (Manual)**:
- Open `.env` file in text editor
- Find `ALPACA_API_KEY=...`
- Replace with your new Key ID
- Find `ALPACA_SECRET_KEY=...`
- Replace with your new Secret Key
- Save file

---

### Step 3: Verify Trading Permissions

Run the verification script:

```bash
python verify_dee_trading.py
```

**Expected Output** (if successful):
```
✅ API client initialized
✅ Account Status: ACTIVE
✅ Cash: $23,853.17
✅ Positions retrieved: 5 positions
✅ Orders retrieved: 0 open orders
✅ TEST ORDER SUBMITTED: xxxxx
✅ TEST ORDER CANCELLED: xxxxx

✅ ALL TESTS PASSED - API HAS FULL TRADING PERMISSIONS
```

**If it fails**:
- Check that you copied keys correctly
- Verify "Trading" permission was enabled in Alpaca dashboard
- Try regenerating keys again

---

### Step 4: Execute DEE-BOT Orders

Once verification passes, execute the pending orders:

```bash
python execute_dee_orders.py
```

**This will submit**:
```
BUY 100 ED @ $100.81 = $10,081
BUY 45 WMT @ $160.00 = $7,200
BUY 5 COST @ $915.00 = $4,575

Total: $21,856
```

**Expected Result**:
```
✅ ED submitted: order-id-1
✅ WMT submitted: order-id-2
✅ COST submitted: order-id-3

Successful: 3/3
```

---

## Troubleshooting

### Issue: "unauthorized" persists after updating keys

**Solution**:
1. Verify you're updating the correct `.env` file
2. Check that `.env` is in the project root directory
3. Restart any running Python processes
4. Run `python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('ALPACA_API_KEY'))"` to verify key loaded

### Issue: "trading_blocked" = True

**Solution**:
- Your Alpaca account has trading restrictions
- Contact Alpaca support to enable trading
- Check if account needs additional verification

### Issue: Keys work but orders still fail

**Possible Causes**:
1. **Insufficient cash**: Check account cash balance
2. **Market closed**: Orders must be placed during market hours (9:30 AM - 4:00 PM ET)
3. **Limit price too far**: Alpaca may reject limit orders far from current price
4. **Symbol restrictions**: Some symbols may not be tradeable

### Issue: Can't find API Keys in Alpaca dashboard

**Different Account Structures**:
- **Paper Trading**: https://paper-api.alpaca.markets/
- **Live Trading**: https://app.alpaca.markets/
- Check you're logged into the correct account type

---

## Quick Reference

### File Locations

```
.env                           # Contains API keys
update_dee_keys.py             # Updates keys in .env
verify_dee_trading.py          # Tests if trading works
execute_dee_orders.py          # Executes pending orders
FIX_DEE_API_PERMISSIONS.md     # This guide
```

### Command Sequence

```bash
# After getting new keys from Alpaca:

# 1. Update keys
python update_dee_keys.py

# 2. Verify permissions
python verify_dee_trading.py

# 3. Execute orders (if verification passes)
python execute_dee_orders.py
```

---

## Current Status (Oct 14, 2025)

### ✅ SHORGAN-BOT: Working
```
ARWR: 47 shares @ $36.65 ✅ FILLED
Stop: $28.00 ✅ ACTIVE
Cash: $26,133.61
```

### ❌ DEE-BOT: Blocked (Pending Fix)
```
Pending Orders:
1. ED: 100 shares @ $100.81
2. WMT: 45 shares @ $160.00
3. COST: 5 shares @ $915.00

Cash: $23,853.17 (available)
Issue: API keys lack trading permission
```

---

## Support

If issues persist:
1. Check Alpaca status: https://status.alpaca.markets/
2. Contact Alpaca support: support@alpaca.markets
3. Review Alpaca API docs: https://alpaca.markets/docs/

---

**Next Step**: Go to Alpaca dashboard and regenerate API keys with Trading permission enabled!
