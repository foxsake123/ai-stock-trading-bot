# URGENT ACTIONS NEEDED - Nov 5, 2025

## CRITICAL ISSUE: API Keys Need Rotation

**Status**: API authentication is failing with 401 Unauthorized errors
**Root Cause**: API keys were exposed in Git history (documented in Oct 29 session)
**Impact**: Cannot check portfolio status, automation will fail
**Priority**: HIGHEST - Must be done IMMEDIATELY

### How to Rotate Keys (10-15 minutes):

1. **Login to Alpaca Dashboard**: https://alpaca.markets/
2. **Navigate to Paper Trading Account (DEE-BOT)**:
   - Click "Paper Trading" → "API Keys"
   - Click "Generate New Key"
   - Save the new Key ID and Secret Key
   - Delete the old key
3. **Navigate to Paper Trading Account (SHORGAN-BOT)**:
   - Repeat the same process
   - Save the new Key ID and Secret Key
   - Delete the old key
4. **Navigate to Live Trading Account (SHORGAN-BOT Live)**:
   - Click "Live Trading" → "API Keys"
   - Generate new key and delete old key
   - Save the new Key ID and Secret Key
5. **Update .env file**:
   ```
   # DEE-BOT Paper Account
   ALPACA_API_KEY_DEE=<new_key_id>
   ALPACA_SECRET_KEY_DEE=<new_secret_key>

   # SHORGAN-BOT Paper Account
   ALPACA_API_KEY_SHORGAN=<new_key_id>
   ALPACA_SECRET_KEY_SHORGAN=<new_secret_key>

   # SHORGAN-BOT Live Account
   ALPACA_LIVE_API_KEY_SHORGAN=<new_key_id>
   ALPACA_LIVE_SECRET_KEY_SHORGAN=<new_secret_key>
   ```
6. **Test the new keys**:
   ```bash
   python check_portfolio.py
   ```

**Security Score**: Currently 5/10, will be 9/10 after rotation

---

## ACTION 2: Setup Task Scheduler (5 minutes)

**Status**: Automation has NOT been running for 5 days
**Impact**: No research generated since Oct 27, no automated trading
**Priority**: HIGH

### Steps:

1. **Right-click** `setup_week1_tasks.bat` in the project root
2. **Select** "Run as administrator"
3. **Press any key** when prompted to continue
4. **Wait** for the script to complete (~30 seconds)
5. **Verify** by opening Task Scheduler:
   - Press Win+R
   - Type `taskschd.msc`
   - Look for 6 tasks starting with "AI Trading -"
   - All should show "Ready" status

### Expected Tasks:
1. AI Trading - Weekend Research (Saturday 12 PM)
2. AI Trading - Morning Trade Generation (Weekdays 8:30 AM)
3. AI Trading - Trade Execution (Weekdays 9:30 AM)
4. AI Trading - Daily Performance Graph (Weekdays 4:30 PM)
5. AI Trading - Stop Loss Monitor (Every 5 min during market hours)
6. AI Trading - Profit Taking (Hourly during market hours)

---

## ACTION 3: Generate Missing Research (Running Now)

**Status**: Research generation running in background with --force flag
**Impact**: Catch up on 5 days of missing research
**Priority**: HIGH (Automated - in progress)

This is being done automatically. Check `reports/premarket/` folder in a few minutes for new reports.

---

## ACTION 4: Check Portfolio Status (After Key Rotation)

**Status**: Blocked by API key issue
**Priority**: MEDIUM (do after key rotation)

Once keys are rotated, run:
```bash
python check_portfolio.py
```

This will show:
- DEE-BOT (Paper) balance
- SHORGAN-BOT (Paper) balance
- SHORGAN-BOT (Live $1K) balance
- Combined total

---

## ACTION 5: Generate Today's Trades (If Market Open)

**Status**: Market is CLOSED (Tuesday Nov 5, 3:45 AM ET)
**Next Market Open**: Tuesday Nov 5, 9:30 AM ET
**Priority**: MEDIUM (wait until market open)

At 8:30 AM or later, run:
```bash
python scripts/automation/generate_todays_trades_v2.py
```

Then review the trades in `docs/TODAYS_TRADES_2025-11-05.md`

---

## Summary of Current State

**System Health**: 6.0/10 (degraded due to API key issue)

| Component | Status | Notes |
|-----------|--------|-------|
| API Keys | ❌ FAILED | 401 Unauthorized - MUST rotate |
| Task Scheduler | ❌ NOT SETUP | No tasks configured |
| Research Generation | 🔄 RUNNING | Catching up (5 days behind) |
| Portfolio Access | ❌ BLOCKED | Needs new API keys |
| Automation | ❌ OFFLINE | Hasn't run for 5 days |

**After completing Actions 1 & 2**:
- System Health: 6.0/10 → 8.5/10
- Automation: Fully operational
- Security: 5/10 → 9/10
- Ready for Monday trading ✅

---

## Timeline

**NOW (3:45 AM)**:
- ✅ Research generation started (running in background)
- ⏳ Waiting for you to rotate API keys

**ASAP (Next 30 minutes)**:
1. Rotate API keys (10-15 min)
2. Run setup_week1_tasks.bat (5 min)
3. Verify tasks in Task Scheduler (2 min)
4. Test portfolio access (1 min)

**8:30 AM**:
- Generate today's trades
- Review for approval

**9:30 AM** (Market Open):
- Automated trade execution
- Monitor via Telegram

**All Day**:
- Stop loss monitoring (every 5 min)
- Profit taking (hourly)

**4:30 PM**:
- Performance graph update
- Daily P&L review

---

## Questions?

Check these docs:
- `docs/TASK_SCHEDULER_SETUP_WEEK1.md` - Complete setup guide
- `docs/SECURITY_INCIDENT_2025-10-29_HARDCODED_API_KEYS.md` - Security incident details
- `docs/WEEK1_ENHANCEMENTS_2025-10-31.md` - System enhancements guide
- `CLAUDE.md` - Full session history

Or ask me directly!
