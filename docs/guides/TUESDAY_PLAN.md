# Tuesday, September 23, 2025 - Trading Day Plan

## Market Status
- **Day**: Tuesday (regular trading day)
- **Date**: September 23, 2025
- **Week**: Week 4 of 6-month experiment

## What Will Happen Automatically

### Morning (9:30 AM ET)
✅ **BOTH BOTS Position Update** - Automated sync with Alpaca
- Script: `scripts-and-data/automation/update_all_bot_positions.py`
- Updates:
  - `daily-csv/dee-bot-positions.csv`
  - `daily-csv/shorgan-bot-positions.csv`

### Afternoon (4:00 PM ET)
✅ **BOTH BOTS Position Update** - End-of-day sync
✅ **Daily Portfolio Snapshot** - Captures positions for both bots
- Script: `scripts-and-data/automation/daily_portfolio_snapshot.py`
- Saves to: `daily-snapshots/` directory

### Evening (4:30 PM ET)
✅ **Dual-Bot Post-Market Report** - Combined performance summary
- Script: `scripts-and-data/automation/generate_post_market_report.py`
- Includes: DEE-BOT and SHORGAN-BOT metrics
- Delivery: Telegram bot notification with both portfolios

## Manual Trading Actions Required

### Complete SHORGAN-BOT Weekly Positioning
Execute all ChatGPT deep research recommendations:

1. **IONQ Entry** (NEW)
   - Buy 200 shares @ $12.50 limit
   - Stop loss: $11.00
   - Catalyst: Quantum computing conference

2. **BBAI Earnings Setup**
   - Buy 500 shares @ $1.95 limit
   - Stop loss: $1.75
   - Catalyst: Wednesday earnings after close

3. **SOUN Position** (if Monday didn't fill)
   - Buy 1000 shares @ $5.45 limit
   - Stop loss: $4.85
   - Catalyst: AI voice technology

4. **GPK Exit** (if not done Monday)
   - Sell 142 shares at market
   - Currently down -7.6%
   - Cut losses per weekly plan

3. **Position Monitoring**
   - **KSS**: Watch stop at $15.18 (currently $16.91)
   - **High Performers**: Consider trimming RGTI (+61%), ORCL (+25%)
   - **NCNO**: Short position showing -$208.80 loss (review)

## Execute Trades Script

Run the Tuesday execution script:
```bash
python execute_tuesday_trades.py
```

This will execute ALL pending trades:
- IONQ: 200 shares @ $12.50 (quantum catalyst)
- BBAI: 500 shares @ $1.95 (earnings Wednesday)
- SOUN: 1000 shares @ $5.45 (AI voice, if needed)
- GPK: Exit 142 shares (cut losses)
- Set stop losses automatically for all buys

Total capital needed: ~$10,400 (well within $30,116 available)

## Key Metrics to Watch

### SHORGAN-BOT
- Available Cash: $30,115.61
- Positions: 18 active
- Focus: Catalyst plays (BBAI earnings)

### DEE-BOT
- Available Cash: -$230.34 (fully invested)
- Positions: 11 (S&P 100 defensives)
- Beta: ~1.0 (on target)

## Wednesday Preparation

### BBAI Earnings (After Close)
- Position size: 500 shares (if filled Tuesday)
- Expected move: ±15-20%
- Risk: $975 (500 shares × $1.95)
- Stop loss: $1.75 (-10%)

## Risk Management

### Active Stop Losses
- KSS: $15.18
- BBAI: $1.75 (if filled)
- SOUN: $4.85 (if filled)

### Position Limits
- No position > 10% of portfolio
- Maintain 20-30% cash reserve
- Daily loss limit: 3% of portfolio

## System Checks

### Before Market Open
1. Check ChatGPT server is running (port 8888)
2. Verify Alpaca API connectivity
3. Review pre-market movers
4. Check for any overnight news

### After Market Close
1. Verify all automated reports ran
2. Update CLAUDE.md with day's activities
3. Review Wednesday earnings calendar
4. Plan BBAI exit strategy

## Notes
- This is a regular trading day (not Monday as initially planned)
- Wednesday has BBAI earnings - key catalyst event
- Thursday has no major catalysts scheduled
- Friday will generate weekly performance report (4:30 PM)

---

*Remember: All trades require manual execution via Alpaca or the execution script*