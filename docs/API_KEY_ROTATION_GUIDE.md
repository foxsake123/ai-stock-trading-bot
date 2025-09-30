# API Key Rotation Guide

**CRITICAL**: If API keys are ever exposed (committed to git, shared accidentally, etc.), rotate them immediately following this guide.

---

## 🚨 When to Rotate Keys

Rotate your API keys if:
- ✅ Keys were committed to version control (even if removed later)
- ✅ Keys were shared in chat, email, or public forum
- ✅ You suspect unauthorized access
- ✅ Regular security rotation (recommended quarterly)
- ✅ Team member with key access leaves

---

## 📋 Step-by-Step Rotation Process

### Step 1: Generate New Keys at Alpaca Markets

#### For DEE-BOT Account
1. **Login to Alpaca**: https://app.alpaca.markets/paper/dashboard/overview
2. Navigate to **Settings** → **API Keys**
3. Find your DEE-BOT keys (or create new if first time)
4. Click **Regenerate** or **Create New API Key**
5. **Save immediately**:
   - API Key ID: `PKxxxxxxxxxxxxxxxxxx`
   - Secret Key: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### For SHORGAN-BOT Account
1. Switch to SHORGAN account (or repeat login)
2. Navigate to **Settings** → **API Keys**
3. Click **Regenerate** or **Create New API Key**
4. **Save immediately**:
   - API Key ID: `PKxxxxxxxxxxxxxxxxxx`
   - Secret Key: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**⚠️ IMPORTANT**: Copy keys immediately. Alpaca only shows the secret key once!

---

### Step 2: Update Your .env File

1. **Open your `.env` file** (in project root):
   ```bash
   # Windows
   notepad .env

   # macOS/Linux
   nano .env
   ```

2. **Update the keys**:
   ```bash
   # DEE-BOT (Paper Trading)
   ALPACA_API_KEY_DEE=PK_YOUR_NEW_DEE_KEY_HERE
   ALPACA_SECRET_KEY_DEE=YOUR_NEW_DEE_SECRET_HERE

   # SHORGAN-BOT (Paper Trading)
   ALPACA_API_KEY_SHORGAN=PK_YOUR_NEW_SHORGAN_KEY_HERE
   ALPACA_SECRET_KEY_SHORGAN=YOUR_NEW_SHORGAN_SECRET_HERE

   # Other keys remain unchanged
   TELEGRAM_BOT_TOKEN=your_telegram_token
   TELEGRAM_CHAT_ID=your_chat_id
   FINANCIAL_DATASETS_API_KEY=your_fd_key
   ALPHA_VANTAGE_API_KEY=your_av_key
   ```

3. **Save and close** the file

4. **Verify .env is in .gitignore**:
   ```bash
   grep "\.env" .gitignore
   ```
   Should return: `.env`

---

### Step 3: Test New Keys

Run a quick test to verify the new keys work:

```bash
# Test DEE-BOT connection
python utils/trading/check_balances.py

# Or test with a quick script
python -c "
from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
import os

load_dotenv()

# Test DEE-BOT
try:
    dee = TradingClient(
        os.getenv('ALPACA_API_KEY_DEE'),
        os.getenv('ALPACA_SECRET_KEY_DEE'),
        paper=True
    )
    account = dee.get_account()
    print(f'✅ DEE-BOT connected: ${float(account.portfolio_value):,.2f}')
except Exception as e:
    print(f'❌ DEE-BOT failed: {e}')

# Test SHORGAN-BOT
try:
    shorgan = TradingClient(
        os.getenv('ALPACA_API_KEY_SHORGAN'),
        os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
        paper=True
    )
    account = shorgan.get_account()
    print(f'✅ SHORGAN-BOT connected: ${float(account.portfolio_value):,.2f}')
except Exception as e:
    print(f'❌ SHORGAN-BOT failed: {e}')
"
```

**Expected Output**:
```
✅ DEE-BOT connected: $104,126.00
✅ SHORGAN-BOT connected: $106,003.00
```

---

### Step 4: Delete Old Keys from Alpaca

1. Return to **Alpaca Settings** → **API Keys**
2. Find the **old keys** (will show as "Last used: X days ago")
3. Click **Delete** or **Revoke**
4. Confirm deletion

This ensures the old (exposed) keys can no longer be used.

---

### Step 5: Clean Git History (If Keys Were Committed)

If keys were committed to git, they're in the history even if removed. Options:

#### Option A: For Public Repos (REQUIRED)
Use BFG Repo-Cleaner to remove sensitive data:

```bash
# 1. Download BFG: https://rtyley.github.io/bfg-repo-cleaner/
# 2. Create a file with the exposed keys
echo "PK6FZK4DAQVTD7DYVH78" > keys-to-remove.txt
echo "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt" >> keys-to-remove.txt
echo "PKJRLSB2MFEJUSK6UK2E" >> keys-to-remove.txt
echo "QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic" >> keys-to-remove.txt

# 3. Run BFG
java -jar bfg.jar --replace-text keys-to-remove.txt

# 4. Clean and push
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin --force --all

# 5. Delete keys-to-remove.txt
rm keys-to-remove.txt
```

#### Option B: For Private Repos (Optional)
If the repo is private and only you have access, rotation alone is sufficient. The old keys in history are useless once revoked.

---

### Step 6: Update GitHub Secrets (If Using CI/CD)

If you've set up GitHub Actions with secrets:

1. Go to **GitHub Repository** → **Settings** → **Secrets and variables** → **Actions**
2. Click **Update** next to each secret:
   - `ALPACA_API_KEY_DEE`
   - `ALPACA_SECRET_KEY_DEE`
   - `ALPACA_API_KEY_SHORGAN`
   - `ALPACA_SECRET_KEY_SHORGAN`
3. Paste the new values
4. Save

---

## ✅ Verification Checklist

After rotation, verify:

- [ ] New keys work (test script passes)
- [ ] Old keys deleted from Alpaca
- [ ] `.env` file updated with new keys
- [ ] `.env` is in `.gitignore`
- [ ] Test trades execute successfully
- [ ] Automated reports still generate
- [ ] GitHub Secrets updated (if applicable)
- [ ] Old keys removed from git history (if exposed publicly)

---

## 🔐 Prevention Best Practices

### Do's ✅
- Use environment variables exclusively (`.env` file)
- Add `.env` to `.gitignore` immediately
- Use `python-dotenv` to load credentials
- Rotate keys quarterly (every 3 months)
- Use different keys for dev/prod
- Enable 2FA on Alpaca account

### Don'ts ❌
- Never hardcode API keys in source code
- Never commit `.env` file to git
- Never share keys in Slack/Discord/email
- Never use production keys for testing
- Never screenshot code with keys visible
- Never push keys to public repos

---

## 📝 Example Secure Code Pattern

**❌ WRONG - Hardcoded**:
```python
API_KEY = "PK6FZK4DAQVTD7DYVH78"
SECRET_KEY = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"
```

**✅ CORRECT - Environment Variables**:
```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('ALPACA_API_KEY_DEE')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY_DEE')

if not API_KEY or not SECRET_KEY:
    raise ValueError("API keys not found in environment")
```

---

## 🆘 Emergency Contact

If you discover a security issue:
1. **Immediately** rotate all keys
2. Check Alpaca account for unauthorized activity
3. Review git history for other exposed secrets
4. Consider filing a security report if needed

---

## 📚 Additional Resources

- **Alpaca API Keys**: https://alpaca.markets/docs/trading/getting-started/#authentication
- **Git Secrets**: https://github.com/awslabs/git-secrets
- **BFG Repo-Cleaner**: https://rtyley.github.io/bfg-repo-cleaner/
- **GitHub Secrets**: https://docs.github.com/en/actions/security-guides/encrypted-secrets

---

**Last Updated**: September 30, 2025
**Next Review**: December 30, 2025 (Quarterly)
