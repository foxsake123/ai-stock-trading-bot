# How to Enable SHORGAN Live Trading in Alpaca
**Issue**: Orders rejected with "new orders are rejected by user request"
**Solution**: Enable trading in Alpaca dashboard

---

## 🔍 Finding the Setting

### Option 1: Account Configuration (Most Likely)

1. **Log in to Alpaca**:
   - Go to: https://app.alpaca.markets
   - Log in with your credentials

2. **Navigate to Account Page**:
   - Click your name/profile in top right
   - OR click "Account" in left sidebar
   - OR go directly to: https://app.alpaca.markets/paper/dashboard/overview

3. **Look for Trading Controls**:
   The setting might be in one of these places:

   **A. Account Settings**:
   - Click "Settings" or "Account Settings"
   - Look for section called:
     - "Trading Configuration"
     - "Trading Permissions"
     - "Order Settings"
     - "Trading Controls"

   **B. Paper Trading Toggle**:
   - Look for a toggle/switch that says:
     - "Paper Trading Mode"
     - "Enable Trading"
     - "Allow Orders"
     - "Trading Status"

   **C. API Settings**:
   - Click "API Keys" or "API" section
   - Look for:
     - "Trading Permissions" checkbox
     - "Allow Trading" toggle
     - "Order Placement" setting

4. **What to Enable**:
   - Toggle/checkbox to **ENABLED** or **ON**
   - Look for confirmation message
   - Setting should show as "Active" or "Enabled"

---

## 🔍 Option 2: Check API Key Permissions

The issue might be with the API key itself:

1. **Go to API Keys Section**:
   - https://app.alpaca.markets/paper/dashboard/api-keys
   - OR click "API" in left sidebar

2. **Check Your API Key**:
   - Find the API key that starts with: `PK...` (the one in your .env file)
   - Click on it to see details

3. **Verify Permissions**:
   - Should have checkboxes for:
     - ✅ View account data
     - ✅ Place orders (MUST BE CHECKED)
     - ✅ Cancel orders
   - If "Place orders" is UNCHECKED → CHECK IT and save

4. **If Key Missing Permissions**:
   - You may need to create a NEW API key with trading permissions
   - Click "Generate New Key"
   - Check ALL permissions including "Place orders"
   - Copy the new keys
   - Update your .env file

---

## 🔍 Option 3: Account Status Check

1. **Check Account Status**:
   - Go to Account page
   - Look for account status indicator
   - Should say: "Active" or "Good Standing"

2. **Look for Restrictions**:
   - Any red warnings or alerts?
   - Any messages about "restricted trading"?
   - Any pending actions required?

3. **Common Issues**:
   - **Pattern Day Trader flag**: Might restrict trading
   - **Insufficient funds**: Shouldn't block with $2,168 cash
   - **Account verification**: Should be complete already

---

## 📞 What Information Do I Need?

To help you better, please tell me:

1. **What do you see when you log into Alpaca?**
   - Describe the main dashboard
   - What menu options are on the left sidebar?
   - Any warnings or messages displayed?

2. **When you click "Settings" or "Account", what options appear?**
   - List the sections you see
   - Are there any trading-related toggles?

3. **In the API Keys section**:
   - Do you see your API key?
   - Are there checkboxes next to it for permissions?
   - What permissions are currently checked?

4. **Account Type**:
   - Is this definitely the PAPER trading account?
   - Or are you looking at the LIVE trading account?
   - (Paper account should show "Paper Trading" somewhere)

---

## 🔧 Alternative: Test with Simple Script

Let's see what error message Alpaca gives us:

```python
# Run this in your project directory:
python -c "
from alpaca.trading.client import TradingClient
import os
from dotenv import load_dotenv

load_dotenv()

# SHORGAN Live account
client = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY_SHORGAN_LIVE'),
    secret_key=os.getenv('ALPACA_SECRET_KEY_SHORGAN_LIVE'),
    paper=True
)

# Try to get account info
try:
    account = client.get_account()
    print(f'Account Status: {account.status}')
    print(f'Trading Blocked: {account.trading_blocked}')
    print(f'Account Blocked: {account.account_blocked}')
    print(f'Trade Suspended: {account.trade_suspended_by_user}')
except Exception as e:
    print(f'Error: {e}')
"
```

**This will tell us:**
- Is trading blocked by Alpaca?
- Is it blocked by you (user setting)?
- What the exact account status is

---

## 🎯 Most Likely Solution

Based on the error "new orders are rejected by user request", this is usually:

**Option A: Trading Disabled in Settings**
- There's a toggle somewhere in Account Settings
- It's currently set to OFF/DISABLED
- You need to set it to ON/ENABLED

**Option B: API Key Without Trading Permission**
- Your API key can VIEW data but can't PLACE orders
- Need to regenerate API key with "Place orders" permission checked

**Option C: Account Suspended Trading**
- You (or Alpaca) put a hold on trading
- Need to "Resume Trading" or "Enable Trading"

---

## 📸 Can You Send a Screenshot?

If you can send a screenshot of:
1. Your Alpaca dashboard main page
2. The Settings or Account page
3. The API Keys page

I can tell you exactly which setting to change!

---

## 🚨 If You Can't Find It

**Contact Alpaca Support**:
- Email: support@alpaca.markets
- Say: "My API orders are rejected with 'new orders are rejected by user request'. How do I enable trading on my paper account?"
- They respond within 24 hours usually

**Or Use Paper Trading Tab**:
- Some users report the setting is ONLY visible in the web interface
- NOT in the API settings
- Look for a tab called "Paper Trading" at the top
- That's where the enable/disable toggle might be

---

Tell me what you're seeing and I'll help you find the exact setting!
