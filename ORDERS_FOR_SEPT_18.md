# ORDER EXECUTION PLAN
## Wednesday, September 18, 2025

---

## ⏰ PRE-MARKET CHECKLIST (9:00-9:30 AM ET)

### 1. CBRL Earnings Reaction Check
- [ ] Check after-hours movement from yesterday
- [ ] Check pre-market bid/ask spread
- [ ] Determine action based on price:
  - **If > $52.50**: Hold with trailing stop at $51.00
  - **If $50-52.50**: Hold with stop at $49.00
  - **If < $50**: Exit all 81 shares at market open

### 2. Position Health Check
- [ ] Verify all 20 positions are active
- [ ] Check KSS price vs $15.18 stop
- [ ] Review winners for profit-taking

---

## 📝 MARKET OPEN ORDERS (9:30 AM ET)

### EXECUTE IN THIS ORDER:

#### 1. CBRL Action (9:30:00)
```
IF CBRL < $50.00:
  SELL 81 shares CBRL at MARKET
ELSE:
  SET trailing stop at $49.00 (or 3% below current)
```

#### 2. Profit Taking - RGTI (9:30:30)
```
SELL 65 shares RGTI at MARKET
(50% of 130 share position)
Expected proceeds: ~$1,224
Keep 65 shares with trailing stop at $17.50
```

#### 3. Profit Taking - ORCL (9:31:00)
```
SELL 21 shares ORCL at MARKET
(50% of 42 share position)
Expected proceeds: ~$6,120
Keep 21 shares with trailing stop at $280.00
```

#### 4. KSS Stop Check (9:31:30)
```
IF KSS < $15.18:
  SELL 90 shares KSS at MARKET
ELSE:
  SET stop loss at $15.15 (tighter)
```

---

## 🎯 TRAILING STOPS TO SET (9:35 AM)

Set trailing stops on all winners:

| Symbol | Shares | Current Gain | Trailing Stop Level |
|--------|--------|--------------|-------------------|
| DAKT | 743 | +13.8% | $22.50 |
| TSLA | 2 | +13.3% | $380.00 |
| BTBT | 570 | +10.9% | $2.85 |
| BYND | 398 | +6.8% | $2.60 |
| RGTI | 65 (remaining) | +22.7% | $17.50 |
| ORCL | 21 (remaining) | +21.9% | $280.00 |

---

## 📊 EXPECTED RESULTS

### Cash Generation:
- RGTI sale (65 shares): ~$1,224
- ORCL sale (21 shares): ~$6,120
- **Total cash raised**: ~$7,344

### Profit Locking:
- RGTI profit locked: ~$227
- ORCL profit locked: ~$1,100
- **Total profit secured**: ~$1,327

### Risk Reduction:
- Portfolio exposure reduced by ~3.5%
- Two largest winners partially secured
- Stop losses tightened on all positions

---

## 🔄 AFTERNOON TASKS (2:00-4:00 PM)

### 1. INCY FDA Preparation
- [ ] Review FDA calendar for updates
- [ ] Check INCY options flow
- [ ] Confirm 50% reduction strategy for Thursday
- [ ] Set calendar reminder for 10 AM Thursday

### 2. Portfolio Review
- [ ] Update position tracking CSV
- [ ] Calculate new portfolio value
- [ ] Document all executed trades
- [ ] Check for any new stop triggers

### 3. ChatGPT Integration
- [ ] Request new trading ideas from ChatGPT
- [ ] Save report if received
- [ ] Process through multi-agent system

---

## 🚨 RISK ALERTS

### Critical Levels:
- **KSS**: Must exit if below $15.18
- **Portfolio stop**: -3% daily loss = force reduce
- **CBRL**: Exit if gaps down >5%

### Market Conditions:
- Watch SPY for general market direction
- Monitor VIX for volatility spikes
- Check sector rotation (tech vs defensive)

---

## ✅ END OF DAY CHECKLIST (4:00 PM)

- [ ] All orders executed as planned
- [ ] Trailing stops set on all winners
- [ ] Position CSV updated
- [ ] INCY strategy confirmed for Thursday
- [ ] 4:30 PM automated report sent
- [ ] GitHub repository updated
- [ ] Tomorrow's plan documented

---

## 📱 BROKER PLATFORM SETUP

### Alpaca Paper Trading:
1. Log in to paper trading account
2. Open order entry window
3. Have positions page visible
4. Enable notifications for fills

### Order Types to Use:
- **Profit-taking**: MARKET orders (immediate fill)
- **Stop losses**: STOP orders
- **Trailing stops**: TRAILING STOP %

---

## 💡 REMINDERS

1. **Execute quickly at open** - First 5 minutes critical
2. **Don't chase** - If missed entry, wait for pullback
3. **Honor all stops** - No exceptions
4. **Document everything** - For audit trail
5. **Stay calm** - Stick to the plan

---

## 📞 CONTINGENCY

If technical issues:
1. Use mobile app as backup
2. Call broker if needed: 1-855-880-2559
3. Have stop losses as GTC orders
4. Can execute via API if UI fails

---

*"The plan is the plan. Execute with discipline."*
*Time to lock in profits and reduce risk!*