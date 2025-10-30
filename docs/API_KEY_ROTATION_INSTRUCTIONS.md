# CRITICAL: API Key Rotation Required
## Date: October 30, 2025
## Severity: CRITICAL SECURITY

---

## ⚠️ WHY THIS IS CRITICAL

**Hardcoded API keys were exposed in Git history** (now fixed in code, but keys are compromised):

```
DEE-BOT Paper:     PK6FZK4DAQVTD7DYVH78
SHORGAN-BOT Paper: PKJRLSB2MFEJUSK6UK2E
```

These keys are **permanently exposed** in Git commits and must be rotated immediately.

---

## 📋 STEP-BY-STEP ROTATION INSTRUCTIONS

### **Step 1: Log into Alpaca Dashboard**
1. Go to: https://app.alpaca.markets/
2. Log in with your credentials
3. Navigate to: **Paper Trading** section

### **Step 2: Rotate DEE-BOT Paper Account Keys**
1. Click on **Settings** or **API Keys**
2. Find the key starting with `PK6FZK4DAQVTD7DYVH78`
3. Click **Delete** or **Revoke** this key
4. Click **Generate New Key**
5. **COPY BOTH**:
   - API Key ID (starts with `PK...`)
   - Secret Key (starts with `...` - only shown once!)

### **Step 3: Rotate SHORGAN-BOT Paper Account Keys**
1. Switch to SHORGAN-BOT paper account (if separate)
2. Find the key starting with `PKJRLSB2MFEJUSK6UK2E`
3. Click **Delete** or **Revoke** this key
4. Click **Generate New Key**
5. **COPY BOTH**:
   - API Key ID
   - Secret Key

### **Step 4: Update .env File**
1. Open `.env` file in root directory of project
2. Find these lines:
   ```
   ALPACA_PAPER_API_KEY_DEE=PK6FZK4DAQVTD7DYVH78
   ALPACA_PAPER_SECRET_KEY_DEE=JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt

   ALPACA_PAPER_API_KEY_SHORGAN=PKJRLSB2MFEJUSK6UK2E
   ALPACA_PAPER_SECRET_KEY_SHORGAN=QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic
   ```

3. Replace with your NEW keys:
   ```
   ALPACA_PAPER_API_KEY_DEE=<new_key_from_step_2>
   ALPACA_PAPER_SECRET_KEY_DEE=<new_secret_from_step_2>

   ALPACA_PAPER_API_KEY_SHORGAN=<new_key_from_step_3>
   ALPACA_PAPER_SECRET_KEY_SHORGAN=<new_secret_from_step_3>
   ```

4. Save the file

### **Step 5: Test New Keys**
Run this command to verify new keys work:
```bash
python scripts/automation/daily_claude_research.py --help
```

If you see the help message without errors, keys are working!

### **Step 6: Verify Old Keys Are Revoked**
Try running with old keys (should fail):
- Go back to Alpaca dashboard
- Confirm old keys are deleted/revoked
- Should show "Invalid API key" or similar if tested

---

## ⏱️ TIME REQUIRED: 10-15 minutes

---

## ✅ VERIFICATION CHECKLIST

After completing rotation:
- [ ] DEE-BOT old key revoked in Alpaca dashboard
- [ ] SHORGAN-BOT old key revoked in Alpaca dashboard
- [ ] New keys generated for both accounts
- [ ] `.env` file updated with new keys
- [ ] Test script runs successfully with new keys
- [ ] Old keys confirmed deleted in Alpaca

---

## 🔒 SECURITY BEST PRACTICES

### **What We Fixed Today**:
1. ✅ Removed hardcoded keys from `src/risk/risk_monitor.py`
2. ✅ Changed to environment variables (`python-dotenv`)
3. ✅ Created this rotation guide

### **What You Must Do**:
1. ⚠️ **ROTATE KEYS** (old keys compromised in Git history)
2. ⚠️ Verify `.env` is in `.gitignore` (it should be)
3. ⚠️ Never commit `.env` file to Git

### **Long-Term**:
Consider rotating keys every 90 days as best practice, even if not compromised.

---

## 📞 IF YOU HAVE ISSUES

**Can't find API keys in Alpaca dashboard?**
- Look under Settings → API Keys
- Or Paper Trading → API Management
- Or Profile → API Keys

**New keys not working?**
- Make sure you copied both API Key and Secret Key
- Check for extra spaces in `.env` file
- Verify file is named exactly `.env` (not `.env.txt`)

**Script still failing?**
- Check `.env` file location (should be in project root)
- Run: `python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('DEE:', os.getenv('ALPACA_PAPER_API_KEY_DEE')[:10])"`
- Should print first 10 characters of your new key

---

**Status**: ⚠️ CODE FIXED, KEYS NOT YET ROTATED
**Action Required**: USER MUST ROTATE KEYS ASAP
**Impact**: Security compliance, prevent unauthorized access
