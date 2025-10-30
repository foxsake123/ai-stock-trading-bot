# SECURITY INCIDENT REPORT
## Hardcoded API Keys in Source Code
### Date: October 29, 2025
### Severity: **CRITICAL**
### Status: Code Fixed - Key Rotation Required

---

## INCIDENT SUMMARY

**Type**: Credential Exposure
**Affected File**: `src/risk/risk_monitor.py` (lines 11-15)
**Exposure Type**: Hardcoded API keys committed to Git repository
**Discovery Date**: October 29, 2025
**Fixed Date**: October 29, 2025 (code fixed, keys NOT yet rotated)

---

## WHAT WAS EXPOSED

### Hardcoded Credentials (Lines 11-15 of risk_monitor.py)

```python
# COMPROMISED - DO NOT USE THESE KEYS
DEE_BOT_API = "PK6FZK4DAQVTD7DYVH78"
DEE_BOT_SECRET = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"

SHORGAN_API = "PKJRLSB2MFEJUSK6UK2E"
SHORGAN_SECRET = "QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic"
```

### Accounts Affected

1. **DEE-BOT Paper Trading Account**
   - Current Value: ~$102,476.84
   - Account Type: Paper (simulated trading)
   - Risk Level: MEDIUM (paper account, but still credentials)

2. **SHORGAN-BOT Paper Trading Account**
   - Current Value: ~$109,480.28
   - Account Type: Paper (simulated trading)
   - Risk Level: MEDIUM (paper account, but still credentials)

**NOTE**: These appear to be PAPER trading credentials, not live trading credentials. Impact is reduced but still a security violation.

---

## EXPOSURE SCOPE

### How Keys Were Exposed

1. **Committed to Git**: Keys were hardcoded in source file
2. **Git History**: Keys exist in commit history (permanent exposure)
3. **Remote Repository**: If pushed to GitHub/GitLab, keys are publicly visible
4. **Duration**: Unknown - depends on when `risk_monitor.py` was first committed

### Who Has Access

**Anyone with**:
- Access to the Git repository
- Access to GitHub/GitLab if repo is public or shared
- Access to any cloned copy of the repository
- Access to Git history (keys remain even after removal)

### What Can Be Done With These Keys

With these API keys, an attacker could:
- View portfolio positions and holdings
- View trading history and performance
- Execute trades (BUY/SELL) on the paper accounts
- Modify or cancel existing orders
- Transfer funds (if enabled)
- View account balance and transaction history

**PAPER ACCOUNTS**: Limited financial risk (no real money) but:
- Can disrupt trading bot performance
- Can corrupt performance history
- Can interfere with strategy testing
- Still a security best practice violation

---

## REMEDIATION ACTIONS

### ✅ COMPLETED (Code Fix)

1. **Fixed Source Code** (`src/risk/risk_monitor.py`)
   - Removed hardcoded keys
   - Added `import os` and `from dotenv import load_dotenv`
   - Changed to use environment variables:
     ```python
     DEE_BOT_API = os.getenv("ALPACA_PAPER_API_KEY_DEE") or os.getenv("ALPACA_PAPER_API_KEY")
     DEE_BOT_SECRET = os.getenv("ALPACA_PAPER_SECRET_KEY_DEE") or os.getenv("ALPACA_PAPER_SECRET_KEY")
     SHORGAN_API = os.getenv("ALPACA_PAPER_API_KEY_SHORGAN")
     SHORGAN_SECRET = os.getenv("ALPACA_PAPER_SECRET_KEY_SHORGAN")
     ```

### ⚠️ REQUIRED (Key Rotation)

2. **Rotate Alpaca API Keys** (HIGHEST PRIORITY)

   **Steps**:
   ```
   a. Log into Alpaca dashboard: https://app.alpaca.markets/
   b. Navigate to: Settings → API Keys
   c. For DEE-BOT Paper Account:
      - Delete key: PK6FZK4DAQVTD7DYVH78
      - Generate new key pair
      - Update .env file with new credentials
   d. For SHORGAN-BOT Paper Account:
      - Delete key: PKJRLSB2MFEJUSK6UK2E
      - Generate new key pair
      - Update .env file with new credentials
   e. Test that all scripts work with new keys
   f. Confirm old keys are revoked
   ```

   **Time Required**: 10-15 minutes
   **Impact**: None (seamless key rotation)

3. **Verify .env File Security**
   ```bash
   # Ensure .env is in .gitignore
   cat .gitignore | grep ".env"

   # If not present, add it:
   echo ".env" >> .gitignore
   git add .gitignore
   git commit -m "security: ensure .env is ignored"
   ```

### 📋 RECOMMENDED (Best Practices)

4. **Git History Cleansing** (Optional but Recommended)

   **WARNING**: This rewrites Git history and requires force push

   ```bash
   # Use BFG Repo-Cleaner to remove keys from history
   # Download: https://rtyley.github.io/bfg-repo-cleaner/

   # Create backup first
   git clone --mirror <repo-url> repo-backup

   # Remove sensitive data
   bfg --replace-text passwords.txt repo.git

   # Force push (CAUTION)
   git push --force --all
   ```

   **Alternative**: Create new repository and migrate (clean start)

5. **Security Audit**
   ```bash
   # Search for other potential hardcoded secrets
   grep -r "api_key\|secret\|password\|token" src/ scripts/ --include="*.py" | grep -v ".pyc"

   # Check for AWS, Azure, Google Cloud credentials
   grep -r "AWS_ACCESS\|AZURE_\|GOOGLE_APPLICATION" . --include="*.py"

   # Verify all sensitive values use environment variables
   ```

6. **Add Pre-Commit Hook**

   Create `.git/hooks/pre-commit`:
   ```bash
   #!/bin/bash
   # Prevent commits with potential secrets
   if grep -r "PK[A-Z0-9]\{20\}\|SK[a-zA-Z0-9]\{40\}" --include="*.py" src/ scripts/; then
       echo "ERROR: Potential API key detected in commit"
       exit 1
   fi
   ```

---

## RISK ASSESSMENT

### Current Risk Level: **MEDIUM** (was CRITICAL before code fix)

**Factors Reducing Risk**:
- ✅ Paper trading accounts (no real money at risk)
- ✅ Code fixed (no new exposures)
- ✅ Repository likely private

**Factors Increasing Risk**:
- ❌ Keys still valid (not rotated)
- ❌ Keys in Git history (permanent exposure)
- ❌ Unknown how long keys were exposed
- ❌ Unknown if repository was ever public/shared

### Financial Impact

**Worst Case Scenario** (if keys used maliciously):
- Paper accounts corrupted: $0 real money loss
- Trading history lost: LOW impact (can regenerate)
- Strategy performance corrupted: MEDIUM impact (weeks of data)
- Time to restore: 2-4 hours

**Best Practice Impact**:
- Security violation regardless of account type
- Should treat ALL credentials as sensitive
- Paper today, live tomorrow - good habits matter

---

## LESSONS LEARNED

### What Went Wrong

1. **No Code Review**: File committed without security review
2. **No Secret Scanning**: No automated tool to detect hardcoded secrets
3. **Developer Education**: Pattern of hardcoding suggests training gap
4. **No Pre-Commit Hooks**: No preventive controls in Git workflow

### Prevention for Future

1. **Mandatory Environment Variables**
   - ALL API keys, tokens, passwords in `.env`
   - Never hardcode credentials
   - Use `python-dotenv` or similar library

2. **Automated Scanning**
   - Install `detect-secrets` or `git-secrets`
   - Run on pre-commit hook
   - Scan repository weekly

3. **Code Review Checklist**
   - [ ] No hardcoded credentials
   - [ ] All secrets from environment
   - [ ] `.env.example` provided (without real values)
   - [ ] `.gitignore` includes `.env`

4. **Security Training**
   - Document credential handling best practices
   - Add to developer onboarding
   - Regular security awareness reminders

---

## VERIFICATION CHECKLIST

### Immediate Actions (Next 30 Minutes)
- [x] Fix source code to use environment variables
- [x] Document incident in this report
- [ ] **Rotate API keys in Alpaca dashboard** ← CRITICAL
- [ ] Test that bot works with new keys
- [ ] Confirm old keys are revoked

### Short-Term (Next 24 Hours)
- [ ] Verify `.env` is in `.gitignore`
- [ ] Search codebase for other hardcoded secrets
- [ ] Update `.env.example` with required variables
- [ ] Test full automation cycle with new keys

### Long-Term (Next Week)
- [ ] Install secret scanning tool
- [ ] Add pre-commit hooks
- [ ] Review and update security documentation
- [ ] Create credential rotation procedure
- [ ] Consider Git history cleansing (optional)

---

## COMMUNICATION

### Who Was Notified
- User (via this report)
- Development team (if applicable)

### External Notification Required
- ❌ NO - Paper trading accounts only
- ❌ NO - No user funds at risk
- ✅ YES - Best practice to log and learn from

### Regulatory/Compliance
- Not applicable (personal trading bot)
- If this were production: Would require incident report

---

## TECHNICAL DETAILS

### File Changes

**Before (Vulnerable)**:
```python
# src/risk/risk_monitor.py (lines 11-15)
DEE_BOT_API = "PK6FZK4DAQVTD7DYVH78"
DEE_BOT_SECRET = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"
SHORGAN_API = "PKJRLSB2MFEJUSK6UK2E"
SHORGAN_SECRET = "QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic"
```

**After (Secure)**:
```python
# src/risk/risk_monitor.py (lines 6-21)
import os
from dotenv import load_dotenv

load_dotenv()

DEE_BOT_API = os.getenv("ALPACA_PAPER_API_KEY_DEE") or os.getenv("ALPACA_PAPER_API_KEY")
DEE_BOT_SECRET = os.getenv("ALPACA_PAPER_SECRET_KEY_DEE") or os.getenv("ALPACA_PAPER_SECRET_KEY")
SHORGAN_API = os.getenv("ALPACA_PAPER_API_KEY_SHORGAN")
SHORGAN_SECRET = os.getenv("ALPACA_PAPER_SECRET_KEY_SHORGAN")
```

### Environment Variables Required

Add to `.env` file (after rotating keys):
```bash
# DEE-BOT Paper Trading
ALPACA_PAPER_API_KEY_DEE=<new_key>
ALPACA_PAPER_SECRET_KEY_DEE=<new_secret>

# SHORGAN-BOT Paper Trading
ALPACA_PAPER_API_KEY_SHORGAN=<new_key>
ALPACA_PAPER_SECRET_KEY_SHORGAN=<new_secret>
```

---

## REFERENCES

- **OWASP Top 10**: A07:2021 – Identification and Authentication Failures
- **CWE-798**: Use of Hard-coded Credentials
- **Alpaca API Security**: https://alpaca.markets/docs/api-references/api-documentation/how-to/api-keys/
- **Git Secrets Detection**: https://github.com/awslabs/git-secrets

---

## SIGN-OFF

**Incident Reported By**: AI Trading Bot System (Claude)
**Date**: October 29, 2025
**Status**: IN PROGRESS - Code fixed, keys NOT rotated
**Next Action**: User must rotate API keys in Alpaca dashboard

---

**CRITICAL REMINDER**: Even though these are paper trading keys, they must be rotated immediately as a security best practice. Hardcoded credentials are never acceptable regardless of account type.
