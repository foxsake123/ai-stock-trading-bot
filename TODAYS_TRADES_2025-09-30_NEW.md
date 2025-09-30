# DAILY TRADES EXECUTION - September 30, 2025
## Based on ChatGPT TradingAgents Plan

---

## 🛡️ DEE-BOT TRADES (Defensive Beta-Neutral)

### BUY ORDERS - Consumer Staples & Healthcare Quality

#### 1. BUY PG (Procter & Gamble)
- **Symbol**: PG
- **Action**: BUY
- **Shares**: 90
- **Price**: $166.00 LIMIT
- **Stop Loss**: $155.00
- **Target**: $178.00
- **Allocation**: ~15% ($15,000)
- **Reason**: Consumer staples ballast, defensive core

#### 2. BUY PEP (PepsiCo)
- **Symbol**: PEP
- **Action**: BUY
- **Shares**: 88
- **Price**: $169.00 LIMIT
- **Stop Loss**: $160.00
- **Target**: $180.00
- **Allocation**: ~15% ($15,000)
- **Reason**: Staple/cyclical balance, dividend quality

#### 3. BUY ABBV (AbbVie)
- **Symbol**: ABBV
- **Action**: BUY
- **Shares**: 96
- **Price**: $156.00 LIMIT
- **Stop Loss**: $147.00
- **Target**: $170.00
- **Allocation**: ~15% ($15,000)
- **Reason**: Healthcare yield + growth, pharma quality

#### 4. HOLD JNJ (Johnson & Johnson)
- **Symbol**: JNJ
- **Action**: HOLD
- **Entry**: $154.00 (existing position)
- **Stop Loss**: $146.00
- **Target**: $170.00
- **Allocation**: ~15%
- **Reason**: Defensive pharma core

#### 5. TRIM SPY (S&P 500 ETF)
- **Symbol**: SPY
- **Action**: TRIM
- **Entry**: $668.00
- **Stop Loss**: $630.00
- **Target**: $690.00
- **Reason**: Beta hedge post-rally, maintain beta ≈ 1.0
- **Note**: Adjust sizing to keep portfolio beta at 1.0

### DEE-BOT Summary:
- **Total New Capital**: $45,000 (3 new positions)
- **Cash Reserve**: ~$3,000 (3%)
- **Target Beta**: 0.85-1.15
- **Strategy**: Defensive quality, dividend stability

---

## 🚀 SHORGAN-BOT TRADES (Catalyst-Driven)

### BUY ORDERS - FDA Catalysts & Momentum

#### 1. BUY ARQT (Arcutis Biotherapeutics)
- **Symbol**: ARQT
- **Action**: BUY
- **Shares**: 857
- **Price**: $17.50 LIMIT
- **Stop Loss**: $15.00
- **Target**: $22.00
- **Allocation**: ~15% ($15,000)
- **Catalyst**: FDA sNDA Oct 13 (eczema)
- **Risk**: ~1% per stop

#### 2. BUY GKOS (Glaukos Corporation)
- **Symbol**: GKOS
- **Action**: BUY
- **Shares**: 187
- **Price**: $80.00 LIMIT
- **Stop Loss**: $72.00
- **Target**: $100.00
- **Allocation**: ~15% ($15,000)
- **Catalyst**: FDA Approval Oct 20 (Epioxa)
- **Risk**: Binary event

#### 3. BUY SNDX (Syndax Pharmaceuticals)
- **Symbol**: SNDX
- **Action**: BUY
- **Shares**: 967
- **Price**: $15.50 LIMIT
- **Stop Loss**: $13.50
- **Target**: $20.00
- **Allocation**: ~15% ($15,000)
- **Catalyst**: FDA sNDA Oct 25 (Revuforj AML)
- **Risk**: FDA event

#### 4. BUY CRS (Carpenter Technology)
- **Symbol**: CRS
- **Action**: BUY
- **Shares**: 79
- **Price**: $251.00 LIMIT
- **Stop Loss**: $230.00 (trailing)
- **Target**: $280.00
- **Allocation**: ~20% ($20,000)
- **Catalyst**: Aerospace momentum + A&D reclass
- **Note**: Use trailing stops to protect gains

#### 5. SHORT TLRY (Tilray Brands) - OPTIONAL IF ALLOWED
- **Symbol**: TLRY
- **Action**: SELL SHORT
- **Shares**: 5,555
- **Price**: $1.80 LIMIT
- **Stop Loss**: $2.20
- **Target**: $1.20
- **Allocation**: ~10% ($10,000)
- **Catalyst**: Cannabis rally unwind
- **Risk**: Speculative - keep small
- **NOTE**: SKIP IF LONG-ONLY MANDATE

### SHORGAN-BOT Summary:
- **Total New Capital**: $65,000-$75,000 (4-5 positions)
- **Cash Reserve**: ~$25,000-$35,000
- **Risk per position**: ~1% on stop loss
- **Strategy**: FDA binary events + momentum

---

## 📋 EXECUTION SEQUENCE

### Pre-Market (8:00-9:30 AM)
1. Check account cash balances
2. Review pre-market prices
3. Verify all tickers tradeable
4. Confirm no FDA news overnight

### Market Open (9:30 AM)

**DEE-BOT Orders (Place First):**
```bash
# Execute all DEE-BOT trades
BUY PG 90 @ $166.00 LIMIT DAY
BUY PEP 88 @ $169.00 LIMIT DAY
BUY ABBV 96 @ $156.00 LIMIT DAY
TRIM SPY (adjust for beta)
```

**SHORGAN-BOT Orders (Place After DEE):**
```bash
# Execute all SHORGAN-BOT trades
BUY ARQT 857 @ $17.50 LIMIT DAY
BUY GKOS 187 @ $80.00 LIMIT DAY
BUY SNDX 967 @ $15.50 LIMIT DAY
BUY CRS 79 @ $251.00 LIMIT DAY
# SHORT TLRY 5555 @ $1.80 (if allowed)
```

### After Fills (10:00-10:30 AM)
1. **Immediately set stop-loss orders:**
   - PG: STOP $155.00
   - PEP: STOP $160.00
   - ABBV: STOP $147.00
   - ARQT: STOP $15.00
   - GKOS: STOP $72.00
   - SNDX: STOP $13.50
   - CRS: TRAILING STOP $230.00
   - TLRY: STOP $2.20 (if shorted)

2. Verify all stops active
3. Update position tracking
4. Calculate DEE-BOT portfolio beta

### Midday Check (12:00 PM)
- Adjust unfilled limit orders if needed
- Monitor FDA news flow
- Check CRS momentum
- Verify beta in range

### End of Day (4:00 PM)
- Verify all positions and stops
- Update daily CSV files
- Review performance
- Prepare for next day

---

## ⚠️ RISK WARNINGS

### CRITICAL RISKS:
1. **FDA Binary Events**: ARQT, GKOS, SNDX all have approval risk
2. **TLRY Short**: Could squeeze - keep small or skip
3. **CRS Momentum**: Use trailing stops to protect
4. **DEE Beta**: Must monitor and rebalance

### POSITION LIMITS:
- No single position >20%
- DEE-BOT: Max 8% per position stop loss
- SHORGAN-BOT: Max 10% per position stop loss
- Total portfolio risk: <2% per trade

### LIQUIDITY CHECKS:
- All tickers >500K ADV (verified)
- Bid-ask spreads reasonable
- Use LIMIT orders only (no MARKET)

---

## 📊 EXPECTED RESULTS

### If All Trades Fill:

**DEE-BOT:**
- 3 new defensive positions
- Maintained beta near 1.0
- ~45% deployed in quality dividends
- Cash reserve 3%

**SHORGAN-BOT:**
- 4 catalyst positions entered
- 1 short position (optional)
- ~70% deployed in high-conviction plays
- Cash reserve 25-35%

### Success Criteria:
- [ ] All orders filled at or near limit prices
- [ ] Stop losses active for all positions
- [ ] DEE-BOT beta 0.85-1.15
- [ ] No position >20% of portfolio
- [ ] Cash reserves maintained

---

## 📅 CATALYST CALENDAR

### Key Dates to Monitor:
- **October 13**: ARQT FDA sNDA decision (eczema)
- **October 20**: GKOS FDA approval (Epioxa)
- **October 25**: SNDX FDA sNDA decision (Revuforj AML)

### Daily Monitoring:
- CRS aerospace sector momentum
- TLRY cannabis sector weakness
- DEE-BOT beta calculation
- FDA news flow

---

## 🎯 POST-EXECUTION CHECKLIST

- [ ] All DEE-BOT orders submitted
- [ ] All SHORGAN-BOT orders submitted
- [ ] Stop-loss orders for all positions
- [ ] Position tracking updated
- [ ] Portfolio beta calculated (DEE)
- [ ] Cash reserves verified
- [ ] Telegram notifications sent
- [ ] Execution log saved

---

**Execute with:**
```bash
python scripts-and-data/automation/execute_daily_trades.py
```

**Or manually at 9:30 AM via Alpaca interface**

---

**Generated from ChatGPT TradingAgents Plan**
**All trades LIMIT DAY orders**
**Risk management and stops are mandatory**