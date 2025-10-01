# PORTFOLIO REBALANCING PLAN
**Date:** October 1, 2025
**Analysis Timestamp:** Market Hours

---

## EXECUTIVE SUMMARY

### Critical Issue Identified
**DEE-BOT has NEGATIVE CASH of -$5,143.84** with 3 pending BUY orders totaling $23,935 that will worsen the margin situation significantly.

### Current State
- **DEE-BOT**: $103,850.37 portfolio value, -$5,143.84 cash (on margin)
- **SHORGAN-BOT**: $105,872.00 portfolio value, $61,165.20 cash (healthy)
- **Combined**: $209,722.37 total (+4.86% return)

### Key Problems
1. DEE-BOT is overextended on margin with negative cash
2. DEE-BOT has 3 pending buy orders that will make situation worse
3. SHORGAN-BOT has $56K in short exposure (acceptable for aggressive strategy)
4. Portfolio concentration risk in some positions

---

## PART 1: IMMEDIATE ACTIONS (Priority 1 - NEXT HOUR)

### Action 1.1: Cancel ALL Pending DEE-BOT Orders
**Immediate cancellation required - these orders will increase margin usage**

| Symbol | Side | Qty | Limit Price | Total Value | Status |
|--------|------|-----|-------------|-------------|--------|
| JPM    | BUY  | 55  | $145.00     | $7,975      | CANCEL |
| LMT    | BUY  | 18  | $445.00     | $8,010      | CANCEL |
| ABBV   | BUY  | 53  | $150.00     | $7,950      | CANCEL |
| **TOTAL** | | | | **$23,935** | |

**Rationale:** These orders would increase negative cash from -$5,143 to approximately -$29,078 (severe margin usage)

### Action 1.2: Trim DEE-BOT Positions to Restore Positive Cash
**Target: Generate $10,000-$15,000 cash to restore positive balance with safety buffer**

#### Recommended Sells (Prioritized)

**1. Sell 160 PG @ Market ($152.22 current)**
- Current Value: $24,355
- P/L: -$44.52 (-0.18%)
- Cash Generated: ~$24,355
- **Rationale:** Largest position, minimal loss, underperforming, defensive overlap with SHORGAN shorts

**2. Sell 136 CL @ Market ($79.14 current)**
- Current Value: $10,763
- P/L: -$68.68 (-0.63%)
- Cash Generated: ~$10,763
- **Rationale:** Small loss, consumer staples overlap with PG, lowest conviction

**Total Cash Generated: ~$35,118**
**New Cash Balance: ~$29,974 (positive and healthy)**

**Alternative Conservative Approach (if you want to keep some exposure):**

**Option A: Sell only PG**
- Generates ~$24,355
- New cash: ~$19,211 (positive with buffer)
- Maintains 7 positions

**Option B: Trim multiple positions**
- Sell 80 PG (half): ~$12,177
- Sell 136 CL (full): ~$10,763
- Sell 22 XOM (half): ~$2,457
- Total: ~$25,397
- New cash: ~$20,253

### Action 1.3: Execution Order for DEE-BOT

**IMMEDIATE EXECUTION SCRIPT:**

```python
# 1. Cancel all pending orders
cancel_order(JPM)
cancel_order(LMT)
cancel_order(ABBV)

# 2. Execute sell orders (in sequence)
sell_market(160, 'PG')    # Full position
sell_market(136, 'CL')    # Full position
```

---

## PART 2: SHORGAN-BOT REVIEW

### 2.1 Current Short Position Analysis

| Symbol | Qty | Avg Entry | Current | Market Value | P/L | P/L % | Assessment |
|--------|-----|-----------|---------|--------------|-----|-------|------------|
| PG     | -132| $153.04   | $152.22 | -$20,093    | +$107.90 | +0.53% | **COVER** |
| CVX    | -93 | $157.27   | $154.37 | -$14,356    | +$269.24 | +1.84% | **HOLD** |
| IONQ   | -200| $74.58    | $62.71  | -$12,542    | +$2,373.85 | +15.91% | **HOLD** |
| NCNO   | -348| $29.72    | $26.30  | -$9,152     | +$1,190.16 | +11.51% | **HOLD** |
| **TOTAL** | | | | **-$56,143** | **+$3,941** | **+7.02%** | |

### 2.2 Short Position Recommendations

**COVER: PG (Procter & Gamble)**
- **Reason 1:** DEE-BOT is selling PG anyway - eliminate cross-bot exposure
- **Reason 2:** Minimal profit ($107.90) - not worth the risk
- **Reason 3:** Defensive stock unlikely to have major downside catalyst
- **Action:** Cover 132 shares @ market (~$152.22)
- **Cash Impact:** Requires $20,093 (have $61,165 available)

**HOLD: CVX (Chevron)**
- **Reason:** Small profit, energy sector under pressure, keep short thesis
- **Risk:** Low-moderate (stable dividend stock)
- **Monitor:** Cover if oil prices spike >$85/barrel

**HOLD: IONQ (Quantum Computing)**
- **Reason:** Strong profit (+15.91%), high volatility sector, valid short thesis
- **Risk:** High volatility - set stop loss at $75/share (entry price)
- **Monitor:** Quantum computing hype can be extreme

**HOLD: NCNO (nCino Inc)**
- **Reason:** Good profit (+11.51%), fintech under pressure
- **Risk:** Moderate - set stop loss at $30/share

### 2.3 SHORGAN-BOT Open Orders Review

| Symbol | Side | Qty | Limit Price | Total Value | Recommendation |
|--------|------|-----|-------------|-------------|----------------|
| PEP    | SELL | 30  | $167.00     | $5,010      | **CANCEL** (initiate short) |
| RIVN   | BUY  | 345 | $14.50      | $5,002      | **KEEP** (add to position) |
| RIG    | BUY  | 1290| $3.10       | $3,999      | **KEEP** (new position) |
| GKOS   | BUY  | 50  | $79.00      | $3,950      | **KEEP** (add to position) |

**PEP Order Analysis:**
- This would create ANOTHER defensive consumer staples short
- Already shorting PG and CVX (enough defensive exposure)
- **CANCEL THIS ORDER**

---

## PART 3: REBALANCING PLAN (Next 1-3 Days)

### 3.1 DEE-BOT Target Portfolio Structure

**Target Metrics:**
- Portfolio Value: ~$100,000 (close to starting capital)
- Cash Buffer: $10,000-$15,000 (10-15%)
- Number of Positions: 6-8 (concentrated quality)
- Max Position Size: 12-15% per stock
- Sector Diversification: No more than 30% in any sector

**After Immediate Sales (PG, CL):**
- Remaining Value: ~$73,876 in positions
- Cash: ~$29,974
- Positions: 6 (AAPL, JPM, MSFT, WMT, XOM, CVX)

**Recommended Portfolio Composition:**

| Sector | Symbol | Current Shares | Target Shares | Action | Target Value | % of Portfolio |
|--------|--------|----------------|---------------|--------|--------------|----------------|
| Tech   | AAPL   | 84             | 60            | TRIM   | $15,379      | 15.4%          |
| Tech   | MSFT   | 34             | 30            | TRIM   | $15,576      | 15.6%          |
| Financials | JPM | 64            | 64            | HOLD   | $19,919      | 19.9%          |
| Consumer | WMT  | 50             | 50            | HOLD   | $5,073       | 5.1%           |
| Energy | XOM    | 44             | 44            | HOLD   | $4,914       | 4.9%           |
| Energy | CVX    | 31             | 0             | SELL   | $0           | 0.0%           |
| Healthcare | JNJ | 0            | 40            | BUY    | $6,400       | 6.4%           |
| Healthcare | ABBV| 0            | 35            | BUY    | $6,000       | 6.0%           |
| Defense | LMT   | 0             | 16            | BUY    | $8,800       | 8.8%           |
| Industrials | CAT | 0           | 25            | BUY    | $9,000       | 9.0%           |
| **CASH** | | | | | **$8,939**   | **8.9%**       |
| **TOTAL** | | | | | **$100,000** | **100%**       |

**Sector Allocation:**
- Technology: 31% (AAPL, MSFT)
- Financials: 20% (JPM)
- Healthcare: 12% (JNJ, ABBV)
- Industrials/Defense: 18% (LMT, CAT)
- Energy: 5% (XOM)
- Consumer: 5% (WMT)
- Cash: 9%

### 3.2 SHORGAN-BOT Target Portfolio Structure

**Current Status: HEALTHY**
- Cash: $61,165 (58% of portfolio)
- Long Positions: $100,850 (95%)
- Short Positions: -$56,143 (-53%)
- Net Long Exposure: $44,707 (42%)

**Assessment:** SHORGAN-BOT is operating correctly for an aggressive catalyst-driven strategy

**Recommended Adjustments:**

1. **Cover PG short** (as discussed): Frees up $20,093
2. **Deploy more cash** into high-conviction longs: Currently too much sitting idle
3. **Add stop losses** on all short positions
4. **Reduce number of positions:** 17 long positions is too many - focus on top 10

**Target Portfolio:**
- Cash: 20-25% ($21,000-$26,000)
- Long Exposure: 100-120% ($106,000-$127,000)
- Short Exposure: 30-40% ($32,000-$42,000)
- Net Long: 60-80%

**Position Cleanup (Long Positions):**

**SELL/TRIM (Low Conviction or Losses):**
1. **FUBO** (1000 shares, -2.21%): Sell - streaming sector weak
2. **EMBC** (68 shares, -5.71%): Sell - biotech too risky
3. **GPK** (142 shares, -8.00%): Sell - packaging sector weak
4. **MFIC** (770 shares, -2.75%): Trim 50% - reduce micro-cap exposure
5. **GKOS** (44 shares, -3.66%): Hold current, fill open order if triggered

**HOLD/ADD (High Conviction Winners):**
1. **RGTI** (+98.30%): HOLD - quantum computing winner
2. **ORCL** (+20.62%): HOLD - cloud infrastructure strength
3. **BTBT** (+21.99%): HOLD - crypto mining play
4. **SAVA** (+44.53%): HOLD - biotech lottery ticket
5. **SRRK** (+10.43%): HOLD - digital media growth
6. **UNH** (+0.95%): HOLD - healthcare stability
7. **SPY** (+2.87%): HOLD - market exposure

**Total Cleanup Cash Generated:** ~$13,000
**New Cash after PG cover:** $61,165 + $13,000 - $20,093 = $54,072

---

## PART 4: EXECUTION SCRIPT

### Phase 1: Immediate (Next Hour)

```python
#!/usr/bin/env python3
"""
Emergency Rebalancing - Phase 1
DEE-BOT: Cancel orders and restore positive cash
SHORGAN-BOT: Cover PG short and cancel PEP short
"""

import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv

load_dotenv()

dee_api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY_DEE'),
    os.getenv('ALPACA_SECRET_KEY_DEE'),
    'https://paper-api.alpaca.markets',
    api_version='v2'
)

shorgan_api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY_SHORGAN'),
    os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    'https://paper-api.alpaca.markets',
    api_version='v2'
)

def phase_1_dee_bot():
    """DEE-BOT: Cancel orders and restore cash"""
    print("="*80)
    print("PHASE 1: DEE-BOT EMERGENCY REBALANCING")
    print("="*80)

    # Step 1: Cancel ALL open orders
    print("\n[1] Canceling all open orders...")
    orders = dee_api.list_orders(status='open')
    for order in orders:
        print(f"    Canceling: {order.side} {order.qty} {order.symbol}")
        dee_api.cancel_order(order.id)
    print(f"    Canceled {len(orders)} orders")

    # Step 2: Sell PG (full position)
    print("\n[2] Selling PG (full position - 160 shares)...")
    try:
        order = dee_api.submit_order(
            symbol='PG',
            qty=160,
            side='sell',
            type='market',
            time_in_force='day'
        )
        print(f"    SUCCESS: Sold PG - Order ID: {order.id}")
    except Exception as e:
        print(f"    ERROR: {e}")

    # Step 3: Sell CL (full position)
    print("\n[3] Selling CL (full position - 136 shares)...")
    try:
        order = dee_api.submit_order(
            symbol='CL',
            qty=136,
            side='sell',
            type='market',
            time_in_force='day'
        )
        print(f"    SUCCESS: Sold CL - Order ID: {order.id}")
    except Exception as e:
        print(f"    ERROR: {e}")

    # Step 4: Check new account status
    print("\n[4] New account status:")
    import time
    time.sleep(2)  # Wait for orders to process
    account = dee_api.get_account()
    print(f"    Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"    Cash: ${float(account.cash):,.2f}")
    print(f"    Buying Power: ${float(account.buying_power):,.2f}")

def phase_1_shorgan_bot():
    """SHORGAN-BOT: Cover PG short and cancel PEP short"""
    print("\n" + "="*80)
    print("PHASE 1: SHORGAN-BOT ADJUSTMENTS")
    print("="*80)

    # Step 1: Cancel PEP short order
    print("\n[1] Canceling PEP short order...")
    orders = shorgan_api.list_orders(status='open', symbols=['PEP'])
    for order in orders:
        print(f"    Canceling: {order.side} {order.qty} {order.symbol}")
        shorgan_api.cancel_order(order.id)

    # Step 2: Cover PG short (buy back 132 shares)
    print("\n[2] Covering PG short position (buy 132 shares)...")
    try:
        order = shorgan_api.submit_order(
            symbol='PG',
            qty=132,
            side='buy',
            type='market',
            time_in_force='day'
        )
        print(f"    SUCCESS: Covered PG short - Order ID: {order.id}")
    except Exception as e:
        print(f"    ERROR: {e}")

    # Step 3: Check new account status
    print("\n[3] New account status:")
    import time
    time.sleep(2)
    account = shorgan_api.get_account()
    print(f"    Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"    Cash: ${float(account.cash):,.2f}")
    print(f"    Short Market Value: ${float(account.short_market_value):,.2f}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("EMERGENCY PORTFOLIO REBALANCING - PHASE 1")
    print("IMMEDIATE ACTIONS TO RESTORE POSITIVE CASH")
    print("="*80)

    # Check market status
    clock = dee_api.get_clock()
    if not clock.is_open:
        print(f"\nWARNING: Market is CLOSED")
        print(f"Next open: {clock.next_open}")
        print("Orders will be queued for market open")
        response = input("\nContinue anyway? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted")
            exit()

    # Execute Phase 1
    phase_1_dee_bot()
    phase_1_shorgan_bot()

    print("\n" + "="*80)
    print("PHASE 1 COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Monitor order fills (allow 5-10 minutes)")
    print("2. Run get_portfolio_status.py to verify new balances")
    print("3. Proceed to Phase 2 (gradual rebalancing over 1-3 days)")
```

### Phase 2: Gradual Rebalancing (Days 2-3)

**DEE-BOT:**
1. Trim AAPL: Sell 24 shares (~$6,151)
2. Trim MSFT: Sell 4 shares (~$2,076)
3. Sell CVX: Sell all 31 shares (~$4,785)
4. Buy JNJ: 40 shares (~$6,400)
5. Buy ABBV: 35 shares (~$6,000)
6. Buy LMT: 16 shares (~$8,800)
7. Buy CAT: 25 shares (~$9,000)

**SHORGAN-BOT:**
1. Sell FUBO: 1000 shares (~$3,980)
2. Sell EMBC: 68 shares (~$976)
3. Sell GPK: 142 shares (~$2,752)
4. Trim MFIC: 385 shares (~$4,552)
5. Deploy cash into top performers or new high-conviction ideas

---

## PART 5: RISK MANAGEMENT

### 5.1 Stop Loss Recommendations

**SHORGAN-BOT Short Positions:**
- **IONQ:** Stop loss at $75.00 (entry price) - risk $2,373 profit
- **NCNO:** Stop loss at $30.00 (entry price) - risk $1,190 profit
- **CVX:** Stop loss at $160.00 - acceptable $246 loss

### 5.2 Position Limits

**DEE-BOT:**
- Max position size: 15% of portfolio (~$15,000)
- Max sector allocation: 30% (~$30,000)
- Minimum cash: 8-10% (~$8,000-$10,000)

**SHORGAN-BOT:**
- Max long position: 10% of portfolio (~$10,500)
- Max short position: 8% of portfolio (~$8,500)
- Net exposure range: 40-80% long
- Minimum cash: 20% (~$21,000)

### 5.3 Monitoring Checklist

**Daily:**
- [ ] Check cash balances (DEE must stay positive)
- [ ] Monitor short positions for squeeze risk
- [ ] Review P&L on all positions

**Weekly:**
- [ ] Rebalance if cash < 10% (DEE) or < 20% (SHORGAN)
- [ ] Trim losers > -5%
- [ ] Review sector allocation
- [ ] Update stop losses

---

## SUMMARY OF RECOMMENDATIONS

### Immediate (Priority 1 - Next Hour)

**DEE-BOT:**
1. Cancel 3 pending buy orders (JPM, LMT, ABBV)
2. Sell 160 PG @ market
3. Sell 136 CL @ market
4. Target outcome: +$29,974 cash (positive balance restored)

**SHORGAN-BOT:**
1. Cancel PEP short order
2. Cover 132 PG short @ market
3. Target outcome: Eliminate cross-bot PG exposure

### Short-term (Priority 2 - Days 2-3)

**DEE-BOT:**
1. Trim AAPL and MSFT (reduce tech concentration)
2. Sell CVX (energy overlap)
3. Add defensive positions: JNJ, ABBV, LMT, CAT
4. Target: 6-8 positions, 9% cash buffer

**SHORGAN-BOT:**
1. Sell 4 losing/low-conviction positions
2. Focus on top 10-12 winners
3. Add stop losses to all shorts
4. Target: Cleaner portfolio, 20-25% cash

### Risk Controls

1. **Stop losses** on all SHORGAN shorts
2. **Position limits**: 15% max (DEE), 10% max (SHORGAN)
3. **Cash minimums**: 8% (DEE), 20% (SHORGAN)
4. **Daily monitoring** of margin usage

---

## EXPECTED OUTCOMES

**After Phase 1 (Immediate):**
- DEE-BOT: $103,850 portfolio, +$29,974 cash (positive), 6 positions
- SHORGAN-BOT: $105,872 portfolio, $54,072 cash, 3 shorts (down from 4)
- Combined: $209,722 (+4.86% return maintained)

**After Phase 2 (3 days):**
- DEE-BOT: ~$100,000 portfolio, $9,000 cash, 10 positions, better diversification
- SHORGAN-BOT: ~$106,000 portfolio, $25,000 cash, 12 positions, cleaner portfolio
- Combined: ~$206,000 (+3% return, more sustainable structure)

**Risk Reduction:**
- Eliminated DEE-BOT margin usage (critical fix)
- Reduced position count (focus on quality)
- Better sector diversification
- Proper cash buffers established
- Stop losses in place for shorts

---

## FILES CREATED

1. **get_portfolio_status.py** - Real-time portfolio monitoring script
2. **PORTFOLIO_REBALANCING_PLAN.md** - This comprehensive plan
3. **rebalance_phase1.py** - Ready-to-execute emergency rebalancing script

---

*Plan prepared by: AI Trading Bot System*
*Date: October 1, 2025*
*Review frequency: Daily during rebalancing, weekly thereafter*
