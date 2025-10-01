# Portfolio Rebalancing - Quick Reference
**Date:** October 1, 2025

---

## CRITICAL ISSUE
**DEE-BOT has NEGATIVE CASH: -$5,143.84**
- 3 pending buy orders will make it worse (-$23,935 more)
- **IMMEDIATE ACTION REQUIRED**

---

## IMMEDIATE EXECUTION (Next Hour)

### Run the Script
```bash
python rebalance_phase1.py
```

### What It Does

**DEE-BOT:**
1. Cancels 3 pending orders: JPM, LMT, ABBV ($23,935 total)
2. Sells 160 PG @ market (~$24,355)
3. Sells 136 CL @ market (~$10,763)
4. **Result:** Cash goes from -$5,143 to +$29,974 ✓

**SHORGAN-BOT:**
1. Cancels PEP short order (unnecessary defensive short)
2. Covers 132 PG short @ market (~$20,093)
3. **Result:** Eliminates cross-bot PG exposure ✓

### Expected Outcome
- **DEE-BOT:** $103,850 portfolio, +$29,974 cash, 6 positions
- **SHORGAN-BOT:** $105,872 portfolio, $54,072 cash, 3 shorts
- **Total:** $209,722 (+4.86% maintained)

---

## KEY METRICS AFTER PHASE 1

### DEE-BOT (Target: Conservative/Defensive)
```
Portfolio Value:  ~$103,850
Cash:             ~$29,974 (POSITIVE ✓)
Positions:        6 stocks
  - AAPL: $21,530 (20.7%)
  - JPM:  $19,919 (19.2%)
  - MSFT: $17,652 (17.0%)
  - WMT:  $5,073  (4.9%)
  - XOM:  $4,914  (4.7%)
  - CVX:  $4,785  (4.6%)
Cash:   $29,974 (28.9%)
```

### SHORGAN-BOT (Target: Aggressive/Catalyst)
```
Portfolio Value:  ~$105,872
Cash:             ~$54,072 (51.1%)
Long Positions:   17 stocks ($100,850)
Short Positions:  3 stocks (-$36,050)
  - CVX:  -$14,356 (+1.84% profit)
  - IONQ: -$12,542 (+15.91% profit)
  - NCNO: -$9,152  (+11.51% profit)
```

---

## PHASE 2 ACTIONS (Days 2-3)

### DEE-BOT Portfolio Refinement

**Trims (Reduce Concentration):**
- Sell 24 AAPL → Reduce from 84 to 60 shares
- Sell 4 MSFT → Reduce from 34 to 30 shares
- Sell 31 CVX → Full exit (energy overlap)

**Additions (Diversification):**
- Buy 40 JNJ @ ~$160 = $6,400 (Healthcare)
- Buy 35 ABBV @ ~$171 = $6,000 (Healthcare)
- Buy 16 LMT @ ~$550 = $8,800 (Defense)
- Buy 25 CAT @ ~$360 = $9,000 (Industrials)

**Target Allocation:**
- Tech: 31% (AAPL, MSFT)
- Financials: 20% (JPM)
- Healthcare: 12% (JNJ, ABBV)
- Industrials/Defense: 18% (LMT, CAT)
- Energy: 5% (XOM)
- Consumer: 5% (WMT)
- Cash: 9%

### SHORGAN-BOT Portfolio Cleanup

**Sells (Low Conviction/Losers):**
- FUBO: 1000 shares @ $3.98 = $3,980 (-2.21%)
- EMBC: 68 shares @ $14.36 = $976 (-5.71%)
- GPK: 142 shares @ $19.39 = $2,752 (-8.00%)
- MFIC: 385 shares (50%) @ $11.82 = $4,552 (-2.75%)

**Total cleanup cash:** ~$12,260

**Keeps (High Conviction Winners):**
- RGTI: +98.30% (quantum computing)
- ORCL: +20.62% (cloud infrastructure)
- BTBT: +21.99% (crypto mining)
- SAVA: +44.53% (biotech)
- SRRK: +10.43% (digital media)
- UNH: +0.95% (healthcare stability)
- SPY: +2.87% (market exposure)

**Add Stop Losses:**
- IONQ short: Stop at $75.00 (entry price)
- NCNO short: Stop at $30.00 (entry price)
- CVX short: Stop at $160.00

---

## RISK CONTROLS

### Position Limits
- **DEE-BOT:** Max 15% per position, 30% per sector
- **SHORGAN-BOT:** Max 10% long, 8% short per position

### Cash Requirements
- **DEE-BOT:** Minimum 8-10% cash ($8,000-$10,000)
- **SHORGAN-BOT:** Minimum 20% cash ($21,000)

### Monitoring
**Daily:**
- Cash balances (DEE must stay positive)
- Short position risk (squeeze monitoring)
- P&L review

**Weekly:**
- Sector allocation
- Position concentration
- Stop loss updates

---

## TROUBLESHOOTING

### If Phase 1 Script Fails

**Manual Execution (DEE-BOT):**
```python
# Via Alpaca website or API directly
1. Cancel orders: JPM (55), LMT (18), ABBV (53)
2. Market sell: 160 PG
3. Market sell: 136 CL
```

**Manual Execution (SHORGAN-BOT):**
```python
1. Cancel order: PEP (30 short)
2. Market buy: 132 PG (to cover short)
```

### If Cash Still Negative After Phase 1

**Additional DEE-BOT sells:**
- Option A: Sell 31 CVX → +$4,785
- Option B: Sell 22 XOM (half) → +$2,457
- Option C: Trim WMT or JPM

### If Orders Don't Fill

- **Market closed:** Orders will queue for open
- **Insufficient shares:** Script will adjust automatically
- **Position not found:** Skip that sell, move to next

---

## FILES REFERENCE

1. **get_portfolio_status.py** - Check real-time positions
2. **rebalance_phase1.py** - Execute immediate rebalancing
3. **PORTFOLIO_REBALANCING_PLAN.md** - Full detailed plan
4. **REBALANCING_QUICK_REFERENCE.md** - This file

---

## EXECUTION CHECKLIST

### Before Running Phase 1
- [ ] Read PORTFOLIO_REBALANCING_PLAN.md
- [ ] Understand the changes being made
- [ ] Backup: Run `python get_portfolio_status.py` (save output)
- [ ] Check market status (open/closed)

### During Phase 1
- [ ] Run: `python rebalance_phase1.py`
- [ ] Confirm execution when prompted
- [ ] Monitor console output for errors
- [ ] Note any failed orders

### After Phase 1
- [ ] Wait 5-10 minutes for settlements
- [ ] Run: `python get_portfolio_status.py`
- [ ] Verify DEE-BOT cash is positive
- [ ] Verify SHORGAN-BOT covered PG short
- [ ] Check trade-logs/ for execution log

### Phase 2 (Days 2-3)
- [ ] Review Phase 2 actions in main plan
- [ ] Execute DEE-BOT trims/adds gradually
- [ ] Clean up SHORGAN-BOT losing positions
- [ ] Add stop losses to shorts
- [ ] Final verification with status script

---

## CONTACT/SUPPORT

If issues arise:
1. Check error logs in `scripts-and-data/trade-logs/`
2. Run `python get_portfolio_status.py` for current state
3. Review Alpaca dashboard directly
4. Consult PORTFOLIO_REBALANCING_PLAN.md for details

---

**REMEMBER:** Phase 1 is critical to restore DEE-BOT positive cash.
Phase 2 is optimization and can be done gradually.

**Don't skip Phase 1!**
