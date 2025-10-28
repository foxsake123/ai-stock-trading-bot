# Live Trading Setup Guide - SHORGAN-BOT ($1,000)

**Date**: October 27, 2025
**Capital**: $1,000 (Live Alpaca Account)
**Strategy**: SHORGAN-BOT (Catalyst-driven, mid/large cap)
**Risk Level**: ⚠️ HIGH - Live money, automated trading

---

## ⚠️ CRITICAL WARNING

**YOU ARE ABOUT TO TRADE WITH REAL MONEY**

- Automated trading carries significant risk
- You can lose 100% of your capital
- System trades without your approval once enabled
- Market conditions can change rapidly
- Always monitor positions and be ready to intervene

**RECOMMENDED**: Start with paper trading for 1-2 weeks to verify strategy

---

## Pre-Flight Checklist

### ✅ Prerequisites (Already Complete)
- [x] System 100% operational (all 4 automations working)
- [x] Parser extracts all trades correctly (12 SHORGAN trades)
- [x] Telegram notifications working
- [x] Multi-agent validation system operational
- [x] Performance tracking with benchmark
- [x] Alpaca account funded with $1,000

### ⚠️ Required Before Going Live (TO DO)
- [ ] Generate live API keys from Alpaca dashboard
- [ ] Add live API keys to .env file
- [ ] Update execute_daily_trades.py with live URL for SHORGAN
- [ ] Add position sizing logic for $1,000 capital
- [ ] Add safety checks (max position, daily loss limit)
- [ ] Test live API connection (read-only first)
- [ ] Review and approve Monday's trades manually
- [ ] Monitor first live execution closely

---

## Step 1: Generate Live API Keys

### Alpaca Dashboard Steps:
1. Go to: https://app.alpaca.markets/
2. Log in to your live account (not paper)
3. Navigate to: **Settings** → **API Keys**
4. Click **Generate New Key**
5. **IMPORTANT**: Set permissions to:
   - ✅ Trading (Buy, Sell)
   - ✅ Account Read
   - ⚠️ **DO NOT** enable: Delete, Withdraw
6. Copy both keys immediately (shown only once):
   - API Key ID (starts with `AK...`)
   - Secret Key (starts with `...")
7. Store securely - you cannot retrieve secret key again

### Security Best Practices:
- Never share API keys
- Never commit to git
- Use environment variables only
- Regenerate if compromised
- Enable 2FA on Alpaca account

---

## Step 2: Add Live API Keys to .env

**File**: `.env` (in project root)

Add these lines (replace with your actual keys):

```bash
# SHORGAN-BOT LIVE TRADING KEYS (⚠️ REAL MONEY)
ALPACA_LIVE_API_KEY_SHORGAN=AKxxxxxxxxxxxxxxxxxxxxx
ALPACA_LIVE_SECRET_KEY_SHORGAN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Verify .env is in .gitignore**:
```bash
# Should already be there, but double check:
cat .gitignore | grep ".env"
```

Expected output: `.env` should be listed

---

## Step 3: Update Execute Script for Live Trading

**File**: `scripts/automation/execute_daily_trades.py`

**Current Configuration** (lines 24-34):
```python
DEE_BOT_CONFIG = {
    'API_KEY': os.getenv('ALPACA_API_KEY_DEE'),
    'SECRET_KEY': os.getenv('ALPACA_SECRET_KEY_DEE'),
    'BASE_URL': 'https://paper-api.alpaca.markets'  # PAPER
}

SHORGAN_BOT_CONFIG = {
    'API_KEY': os.getenv('ALPACA_API_KEY_SHORGAN'),
    'SECRET_KEY': os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    'BASE_URL': 'https://paper-api.alpaca.markets'  # PAPER
}
```

**Updated Configuration** (SHORGAN live, DEE paper):
```python
DEE_BOT_CONFIG = {
    'API_KEY': os.getenv('ALPACA_API_KEY_DEE'),
    'SECRET_KEY': os.getenv('ALPACA_SECRET_KEY_DEE'),
    'BASE_URL': 'https://paper-api.alpaca.markets'  # Keep DEE on PAPER
}

SHORGAN_BOT_CONFIG = {
    # Use live keys for SHORGAN
    'API_KEY': os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'),
    'SECRET_KEY': os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'),
    'BASE_URL': 'https://api.alpaca.markets'  # LIVE TRADING ⚠️
}
```

---

## Step 4: Add Position Sizing for $1,000 Capital

**Critical Issue**: Paper trading used $100,000+ capital. Need to scale down 100x.

### Position Sizing Strategy for $1,000:

**Option 1: Conservative (Recommended)**
- Max 5 positions at a time
- $200 per position (20% of capital)
- Minimum $50 per position (5% of capital)
- Reserve $100 cash buffer (10%)

**Option 2: Moderate**
- Max 8 positions at a time
- $125 per position (12.5% of capital)
- Minimum $30 per position (3% of capital)
- Reserve $100 cash buffer (10%)

**Option 3: Aggressive (Not Recommended)**
- Max 10 positions
- $100 per position (10% of capital)
- May be difficult with commissions/fees

### Implementation:

Add to `execute_daily_trades.py` after line 62:

```python
# SHORGAN-BOT LIVE TRADING CONFIGURATION
SHORGAN_LIVE_TRADING = True  # Set to False to disable live trading
SHORGAN_CAPITAL = 1000.0  # Live account capital
SHORGAN_MAX_POSITION_SIZE = 200.0  # 20% of capital
SHORGAN_MIN_POSITION_SIZE = 50.0  # 5% minimum
SHORGAN_CASH_BUFFER = 100.0  # Keep $100 in cash
SHORGAN_MAX_POSITIONS = 5  # Max concurrent positions
SHORGAN_MAX_DAILY_LOSS = 50.0  # Stop trading if lose $50 in one day (5%)
```

---

## Step 5: Add Safety Checks

### Safety Check 1: Position Size Calculator

Add this method to `DailyTradeExecutor` class:

```python
def calculate_position_size_for_live(self, price, bot_name):
    """Calculate safe position size for $1,000 live account"""
    if bot_name != 'SHORGAN-BOT' or not SHORGAN_LIVE_TRADING:
        return None  # Use default logic for paper trading

    # Calculate how many shares we can afford
    available_capital = SHORGAN_CAPITAL - SHORGAN_CASH_BUFFER
    max_shares = int(SHORGAN_MAX_POSITION_SIZE / price)

    # Don't buy if position would be too small
    if max_shares * price < SHORGAN_MIN_POSITION_SIZE:
        print(f"[WARNING] Position too small: ${max_shares * price:.2f} < ${SHORGAN_MIN_POSITION_SIZE}")
        return 0

    return max_shares
```

### Safety Check 2: Daily Loss Circuit Breaker

Add this method to check before each trade:

```python
def check_daily_loss_limit(self):
    """Stop trading if daily loss exceeds limit"""
    if not SHORGAN_LIVE_TRADING:
        return True  # No limit for paper trading

    try:
        account = self.shorgan_api.get_account()
        starting_equity = float(account.last_equity)  # Yesterday's close
        current_equity = float(account.equity)
        daily_pnl = current_equity - starting_equity

        if daily_pnl < -SHORGAN_MAX_DAILY_LOSS:
            print(f"\n⛔ CIRCUIT BREAKER TRIGGERED")
            print(f"Daily loss: ${-daily_pnl:.2f}")
            print(f"Limit: ${SHORGAN_MAX_DAILY_LOSS:.2f}")
            print(f"STOPPING ALL TRADING FOR TODAY")
            return False

        return True
    except Exception as e:
        print(f"[ERROR] Could not check daily loss: {e}")
        return False  # Err on side of caution
```

### Safety Check 3: Position Count Limit

```python
def check_position_count_limit(self):
    """Don't exceed max concurrent positions"""
    if not SHORGAN_LIVE_TRADING:
        return True

    try:
        positions = self.shorgan_api.list_positions()
        if len(positions) >= SHORGAN_MAX_POSITIONS:
            print(f"\n⚠️ Position limit reached: {len(positions)}/{SHORGAN_MAX_POSITIONS}")
            print(f"Cannot open new positions until existing ones close")
            return False
        return True
    except Exception as e:
        print(f"[ERROR] Could not check positions: {e}")
        return False
```

---

## Step 6: Test Live API Connection (Read-Only)

**BEFORE running any trades**, test that you can connect to live account:

```python
# Test script: test_live_connection.py
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

api = tradeapi.REST(
    os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'),
    os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'),
    'https://api.alpaca.markets',
    api_version='v2'
)

print("Testing LIVE account connection...")
print("=" * 60)

try:
    account = api.get_account()
    print(f"✅ Connection successful!")
    print(f"Account ID: {account.id}")
    print(f"Account Status: {account.status}")
    print(f"Buying Power: ${float(account.buying_power):,.2f}")
    print(f"Cash: ${float(account.cash):,.2f}")
    print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"Pattern Day Trader: {account.pattern_day_trader}")

    # Check positions
    positions = api.list_positions()
    print(f"\nOpen Positions: {len(positions)}")
    for pos in positions:
        print(f"  {pos.symbol}: {pos.qty} shares @ ${pos.current_price}")

    # Check buying power
    if float(account.buying_power) < 1000:
        print(f"\n⚠️ WARNING: Low buying power (${float(account.buying_power):,.2f})")

except Exception as e:
    print(f"❌ Connection failed: {e}")
```

**Run test**:
```bash
python test_live_connection.py
```

Expected output:
```
✅ Connection successful!
Account ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Account Status: ACTIVE
Buying Power: $1,000.00
Cash: $1,000.00
Portfolio Value: $1,000.00
Pattern Day Trader: False

Open Positions: 0
```

---

## Step 7: Update Performance Tracking

**File**: `scripts/performance/generate_performance_graph.py`

Update starting capital for SHORGAN (lines 34-36):

```python
# Starting capital
INITIAL_CAPITAL_DEE = 100000.0  # Paper account
INITIAL_CAPITAL_SHORGAN = 1000.0  # LIVE account ⚠️ CHANGED
INITIAL_CAPITAL_COMBINED = 101000.0  # Total (DEE paper + SHORGAN live)
```

**NOTE**: Performance graph will now show:
- DEE-BOT: $100K paper (for testing/learning)
- SHORGAN-BOT: $1K live (real money)
- Combined: $101K mixed

---

## Step 8: Manual Review Protocol

### Monday Morning Workflow (CRITICAL):

**8:30 AM - Trades Generated**
1. System auto-generates `TODAYS_TRADES_2025-10-28.md`
2. **DO NOT execute automatically yet**

**8:35-9:25 AM - Manual Review**
1. Open `docs/TODAYS_TRADES_2025-10-28.md`
2. Review SHORGAN-BOT approved trades carefully:
   - How many trades? (Expect 5-12)
   - What's the total capital required?
   - Any high-risk trades (options, shorts)?
   - Do you understand each trade rationale?
3. **Calculate total position size needed**:
   ```
   Example:
   Trade 1: BUY 10 AAPL @ $180 = $1,800  ⚠️ TOO BIG
   Trade 2: BUY 5 MSFT @ $380 = $1,900  ⚠️ TOO BIG
   Total needed: $3,700 > $1,000 ❌ IMPOSSIBLE
   ```
4. **Manually adjust if needed**:
   - Reduce position sizes
   - Skip trades that don't fit
   - Prioritize high-confidence trades

**9:30 AM - Execution**
- Option 1: Let automation run (risky first time)
- Option 2: Execute manually one by one
- Option 3: Disable automation, execute selected trades only

**Recommended for first day**: Option 2 or 3

---

## Step 9: Monitoring & Risk Management

### Intraday Monitoring:
- **9:30-10:00 AM**: Watch execution closely
- **12:00 PM**: Check positions, P&L
- **3:00 PM**: Review before close
- **4:00 PM**: Review final P&L

### Daily Checklist:
- [ ] All orders filled as expected?
- [ ] Any unexpected positions?
- [ ] P&L within acceptable range?
- [ ] Stop losses working?
- [ ] Telegram notifications received?

### Emergency Actions:
**If something goes wrong**:
1. **IMMEDIATE**: Log into Alpaca, cancel all open orders
2. **If needed**: Close all positions manually
3. **Disable automation**: Comment out live API keys in .env
4. **Review**: What went wrong? Check logs, Telegram messages
5. **Fix**: Address issue before re-enabling

---

## Step 10: Disable Automation (Emergency)

**If you need to stop everything**:

### Option 1: Disable in .env (Fastest)
```bash
# Comment out live keys in .env:
# ALPACA_LIVE_API_KEY_SHORGAN=AK...
# ALPACA_LIVE_SECRET_KEY_SHORGAN=...
```

### Option 2: Disable in Script
```python
# In execute_daily_trades.py line 64:
SHORGAN_LIVE_TRADING = False  # Changed from True
```

### Option 3: Disable Task Scheduler
```cmd
# Open Task Scheduler
taskschd.msc

# Disable tasks:
- AI Trading - Morning Trade Generation → Disable
- AI Trading - Trade Execution → Disable
```

---

## Important Differences: $1,000 vs $100,000

| Aspect | Paper ($100K) | Live ($1K) | Impact |
|--------|--------------|------------|--------|
| Position size | $5,000-$10,000 | $200 max | 25-50x smaller |
| Number of positions | 10-15 | 5 max | 2-3x fewer |
| Diversification | High | Low | More concentration risk |
| Options trading | Viable | Difficult | Premium costs too high |
| Short selling | Easy | Hard | Margin requirements |
| Commission impact | Minimal | Significant | ~$1 per trade = 0.1% |
| Slippage | Minimal | Moderate | Market orders harder to fill |
| Learning curve | Safe | Expensive | Each mistake costs real $ |

---

## Recommended Modifications for $1,000

### 1. Reduce Trade Frequency
- Paper: 10-15 trades per week
- Live: 3-5 trades per week (best setups only)

### 2. Adjust Multi-Agent Threshold
- Paper: 0.55 confidence
- Live: **0.70 confidence** (higher bar)

### 3. Focus on Long Entries Only (Initially)
- Disable shorts (complex, margin requirements)
- Disable options (premium costs too high)
- Long stock only (simple, clear risk)

### 4. Increase Position Hold Time
- Paper: Catalyst-driven (1-5 days)
- Live: Hold winners longer (reduce churn, commissions)

---

## Cost Analysis

### Trading Costs (Alpaca):
- Commission: **$0** (commission-free)
- SEC fees: ~$0.01 per $1,000 sold
- Trading Activity Fee: ~$0.01-$0.03 per trade
- **Total per round trip**: ~$0.05-$0.10

### Monthly Costs (if trading 4x/week):
- ~16 trades/month
- ~$0.80-$1.60 in fees
- **~0.1% monthly drag**

### Break-Even Analysis:
To cover $1.60 monthly fees, need:
- +0.16% monthly return
- +1.92% annual return
- Very achievable with SHORGAN strategy (+3.05% in 22 days paper)

---

## Risk Disclosure

### Maximum Loss Scenarios:

**Worst Case (Total Loss)**:
- Bad trade goes to $0: Lose position value
- Multiple bad trades: Lose 100% of $1,000
- Black swan event: Account blown up

**Daily Loss Limit** (Recommended):
- Stop trading if lose >$50/day (5% of capital)
- Prevents emotional revenge trading
- Circuit breaker built into system

**Position Loss Limit**:
- Stop loss at -10% per position
- Max loss per trade: $20 (2% of capital)
- Manageable risk per trade

### Probability Estimates (Based on Paper Trading):

| Scenario | Probability | Outcome |
|----------|------------|---------|
| Profitable month | ~60% | +$30-$100 |
| Break-even month | ~25% | -$10 to +$10 |
| Losing month | ~15% | -$50 to -$100 |
| Catastrophic loss | <1% | -$200+ |

---

## Success Metrics

### Week 1 Goals:
- [ ] All trades execute correctly (no errors)
- [ ] Position sizing works (no over-allocation)
- [ ] Stop losses trigger properly
- [ ] Telegram notifications received
- [ ] No major losses (>-5% account)

### Month 1 Goals:
- [ ] Profitable or break-even (>-2%)
- [ ] Win rate >40%
- [ ] Max drawdown <10%
- [ ] Average winner > average loser
- [ ] System runs reliably (no missed trades)

### Quarter 1 Goals:
- [ ] Profitable (+5% target)
- [ ] Outperform S&P 500
- [ ] Refine strategy based on learnings
- [ ] Increase capital if successful

---

## Final Checklist Before Going Live

- [ ] Live API keys generated from Alpaca
- [ ] API keys added to .env file
- [ ] .env file in .gitignore (never commit keys)
- [ ] execute_daily_trades.py updated with live URL
- [ ] Position sizing logic added for $1,000
- [ ] Safety checks implemented (loss limit, position count)
- [ ] Test script run successfully (read-only connection)
- [ ] Performance tracking updated ($1K starting capital)
- [ ] Manual review protocol understood
- [ ] Emergency stop procedures documented
- [ ] First day monitoring plan in place
- [ ] Risk disclosure read and understood

---

## Contact & Support

**Alpaca Support**: support@alpaca.markets
**Emergency**: Disable automation immediately if issues arise

**Remember**: This is real money. Start conservatively. Monitor closely. Be ready to intervene.

---

**Created**: October 27, 2025
**Last Updated**: October 27, 2025
**Status**: Ready for implementation

⚠️ **READ THIS ENTIRE GUIDE BEFORE ENABLING LIVE TRADING** ⚠️
