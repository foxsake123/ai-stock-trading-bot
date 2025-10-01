# Daily Portfolio Monitoring Checklist
**Post-Rebalancing Routine**

---

## DAILY TASKS (5 minutes)

### Morning (Before Market Open - 9:00 AM ET)

**Run Status Script:**
```bash
python get_portfolio_status.py
```

**Check Critical Metrics:**
- [ ] DEE-BOT cash is POSITIVE (must be > $0)
- [ ] DEE-BOT not using margin (cash = equity - long market value)
- [ ] SHORGAN-BOT cash > 20% of portfolio (~$21,000+)
- [ ] No margin calls or warnings

**Monitor Short Positions (SHORGAN-BOT):**
- [ ] IONQ current price < $75.00 (stop loss)
- [ ] NCNO current price < $30.00 (stop loss)
- [ ] CVX current price < $160.00 (stop loss)

**Action Required if Stop Loss Triggered:**
```bash
# Cover short immediately
python -c "
from alpaca_trade_api import REST
import os
from dotenv import load_dotenv
load_dotenv()
api = REST(os.getenv('ALPACA_API_KEY_SHORGAN'),
           os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
           'https://paper-api.alpaca.markets', api_version='v2')

# Example: Cover IONQ if > $75
position = api.get_position('IONQ')
qty = abs(int(float(position.qty)))
api.submit_order(symbol='IONQ', qty=qty, side='buy', type='market', time_in_force='day')
print(f'Covered {qty} IONQ short')
"
```

---

### Evening (After Market Close - 4:30 PM ET)

**Run Status Script Again:**
```bash
python get_portfolio_status.py > daily_logs/status_$(date +%Y%m%d).txt
```

**Review Performance:**
- [ ] Calculate daily P&L
- [ ] Note any positions that moved > 5%
- [ ] Check if any positions hit profit targets

**Example Daily Log Format:**
```
Date: October 1, 2025

DEE-BOT:
  Portfolio Value: $103,850.37
  Daily Change: +$425.14 (+0.41%)
  Cash: $29,974.12 ✓
  Positions: 6
  Notes: All positions stable, AAPL up 2.1%

SHORGAN-BOT:
  Portfolio Value: $105,872.00
  Daily Change: -$101.87 (-0.10%)
  Cash: $41,072.20 ✓
  Long Exposure: $100,850.65
  Short Exposure: -$36,050.85
  Notes: RGTI up 5.2%, IONQ short at $63 (well below stop)

Combined:
  Total: $209,722.37
  Return: +4.86%
  Daily: +$323.27 (+0.15%)

Action Items:
  - None
```

---

## WEEKLY TASKS (30 minutes)

### Every Friday Evening

**1. Full Portfolio Review:**
```bash
python get_portfolio_status.py > weekly_logs/status_week_$(date +%Y%W).txt
```

**2. Check Position Sizing:**
- [ ] No DEE-BOT position > 15% of portfolio
- [ ] No SHORGAN-BOT long position > 10%
- [ ] No SHORGAN-BOT short position > 8%

**3. Review Sector Allocation (DEE-BOT):**
```
Target:
  Tech: 31%
  Financials: 20%
  Healthcare: 12%
  Industrials/Defense: 18%
  Energy: 5%
  Consumer: 5%
  Cash: 9%

Actual: [Fill in from status script]
```

**4. Review Winners/Losers (SHORGAN-BOT):**
- [ ] Any position down > 10%? → Consider selling
- [ ] Any position up > 50%? → Consider trimming
- [ ] Any dead money (flat for 2+ weeks)? → Consider rotating

**5. Update Stop Losses:**
- [ ] Adjust stops on profitable shorts (trail by 50% of profit)
- [ ] Example: IONQ now +20% profit → stop at $72 instead of $75

**6. Generate Performance Graph:**
```bash
python generate_performance_graph.py
```

**7. Update Portfolio Tracking:**
```bash
python scripts-and-data/automation/update_portfolio_csv.py
```

---

## MONTHLY TASKS (1 hour)

### First Friday of Each Month

**1. Deep Performance Analysis:**
- [ ] Calculate Sharpe ratio
- [ ] Calculate maximum drawdown
- [ ] Compare vs S&P 500
- [ ] Calculate alpha vs benchmark

**2. Strategy Review:**
- [ ] Is DEE-BOT maintaining beta ~1.0?
- [ ] Is SHORGAN-BOT capturing catalysts effectively?
- [ ] Are both strategies profitable?

**3. Portfolio Rebalancing Check:**
- [ ] Does DEE-BOT need sector rebalancing?
- [ ] Should SHORGAN-BOT rotate to new catalysts?
- [ ] Are cash levels appropriate?

**4. Risk Assessment:**
- [ ] Review correlation between positions
- [ ] Check for hidden sector concentration
- [ ] Verify no cross-bot conflicts
- [ ] Review short squeeze risk

**5. Update Documentation:**
- [ ] Update CLAUDE.md with monthly summary
- [ ] Save performance graphs
- [ ] Archive trade logs

---

## ALERT THRESHOLDS

### RED ALERTS (Immediate Action Required)

**DEE-BOT:**
- ⛔ Cash goes negative
- ⛔ Any position > 20% of portfolio
- ⛔ Portfolio down > 5% in one day
- ⛔ Margin call warning

**SHORGAN-BOT:**
- ⛔ Short position breaks stop loss
- ⛔ Cash < 15% of portfolio
- ⛔ Any short position up > 20% (squeeze risk)
- ⛔ Portfolio down > 8% in one day

### YELLOW ALERTS (Review & Plan)

**DEE-BOT:**
- ⚠️ Cash < 8% of portfolio
- ⚠️ Any position > 15% of portfolio
- ⚠️ Sector > 30% of portfolio
- ⚠️ Portfolio down > 3% in one day

**SHORGAN-BOT:**
- ⚠️ Cash < 20% of portfolio
- ⚠️ Any long position > 10%
- ⚠️ Any short position > 8%
- ⚠️ More than 3 positions down > 5%

---

## QUICK REFERENCE COMMANDS

### Check Portfolio Status
```bash
python get_portfolio_status.py
```

### Check Specific Position
```bash
python -c "
from alpaca_trade_api import REST
import os
from dotenv import load_dotenv
load_dotenv()
api = REST(os.getenv('ALPACA_API_KEY_DEE'),
           os.getenv('ALPACA_SECRET_KEY_DEE'),
           'https://paper-api.alpaca.markets', api_version='v2')
p = api.get_position('AAPL')
print(f'{p.symbol}: {p.qty} shares @ ${float(p.current_price):.2f}')
print(f'Value: ${float(p.market_value):,.2f}')
print(f'P/L: ${float(p.unrealized_pl):,.2f} ({float(p.unrealized_plpc)*100:+.2f}%)')
"
```

### Cover Short Position (Emergency)
```bash
# Replace SYMBOL with actual symbol
python -c "
from alpaca_trade_api import REST
import os
from dotenv import load_dotenv
load_dotenv()
api = REST(os.getenv('ALPACA_API_KEY_SHORGAN'),
           os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
           'https://paper-api.alpaca.markets', api_version='v2')
p = api.get_position('SYMBOL')
qty = abs(int(float(p.qty)))
api.submit_order(symbol='SYMBOL', qty=qty, side='buy', type='market', time_in_force='day')
print(f'Covered {qty} SYMBOL short')
"
```

### Sell Position (Emergency)
```bash
# Replace SYMBOL with actual symbol, BOT with DEE or SHORGAN
python -c "
from alpaca_trade_api import REST
import os
from dotenv import load_dotenv
load_dotenv()
api = REST(os.getenv('ALPACA_API_KEY_BOT'),
           os.getenv('ALPACA_SECRET_KEY_BOT'),
           'https://paper-api.alpaca.markets', api_version='v2')
p = api.get_position('SYMBOL')
qty = int(float(p.qty))
api.submit_order(symbol='SYMBOL', qty=qty, side='sell', type='market', time_in_force='day')
print(f'Sold {qty} SYMBOL')
"
```

---

## PERFORMANCE TRACKING

### Key Metrics to Track Daily

**DEE-BOT:**
- Portfolio Value
- Cash Balance
- Number of Positions
- Beta (vs SPY)
- Daily Return %

**SHORGAN-BOT:**
- Portfolio Value
- Cash Balance
- Long Market Value
- Short Market Value
- Net Exposure
- Daily Return %

**Combined:**
- Total Portfolio Value
- Total Return vs $200K starting capital
- Alpha vs S&P 500
- Daily P&L

### Weekly Metrics

- Weekly return
- Best performing position
- Worst performing position
- Sharpe ratio (rolling 30 days)
- Maximum drawdown

---

## MAINTENANCE SCHEDULE

### Daily (5 min)
- Morning: Check cash, check stops
- Evening: Review P&L, log changes

### Weekly (30 min)
- Friday: Full review, update graphs, rebalance if needed

### Monthly (1 hour)
- First Friday: Deep analysis, strategy review, documentation

### Quarterly (2 hours)
- Full system review
- Backtest strategy performance
- Consider strategy adjustments
- Review API costs and performance

---

## TROUBLESHOOTING

### Issue: Script fails with "position not found"
**Solution:** Position may have been closed. Skip and continue.

### Issue: Can't connect to Alpaca API
**Solution:**
1. Check internet connection
2. Verify API keys in .env
3. Check Alpaca status page

### Issue: Orders rejected
**Solution:**
1. Check account status (not restricted)
2. Verify sufficient buying power
3. Check if market is open
4. Review position limits

### Issue: Performance tracking script fails
**Solution:**
1. Check API rate limits
2. Verify all dependencies installed
3. Check data source availability

---

## CONTACT & RESOURCES

**Alpaca Dashboard:**
- DEE-BOT: https://paper-api.alpaca.markets
- SHORGAN-BOT: https://paper-api.alpaca.markets

**Documentation:**
- Main Plan: PORTFOLIO_REBALANCING_PLAN.md
- Quick Ref: REBALANCING_QUICK_REFERENCE.md
- At-a-Glance: REBALANCING_AT_A_GLANCE.txt

**Support:**
- Alpaca Support: support@alpaca.markets
- API Docs: https://alpaca.markets/docs

---

**Remember:** Consistency is key. A 5-minute daily check prevents major issues.

**Golden Rule:** If DEE-BOT cash goes negative, STOP and rebalance immediately.
