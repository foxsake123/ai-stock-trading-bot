# Reports Directory Structure
**Last Updated**: October 14, 2025
**Status**: Reorganized and cleaned ✅

---

## 📁 Directory Structure

```
reports/
├── premarket/                      # Nightly research for next trading day
│   ├── YYYY-MM-DD/                # Date-specific reports
│   │   ├── claude_research.md     # Claude Deep Research analysis
│   │   ├── chatgpt_research.md    # ChatGPT Deep Research analysis
│   │   ├── consensus.md           # Dual-AI comparison & synthesis
│   │   └── trades.md              # Executable trade recommendations
│   └── latest/                     # Always points to most recent reports
│       ├── claude_research.md
│       ├── chatgpt_research.md
│       ├── consensus.md
│       └── trades.md
│
├── execution/                      # Trade execution logs
│   └── YYYY-MM-DD/
│       ├── orders_submitted.json
│       ├── fills.json
│       └── execution_summary.md
│
├── performance/                    # Daily P&L tracking
│   └── YYYY-MM-DD/
│       ├── portfolio_snapshot.json
│       ├── daily_pnl.json
│       └── performance_summary.md
│
└── archive/                        # Old reports (>30 days)
    └── YYYY-MM/
        └── (historical reports)
```

---

## 📝 File Descriptions

### Premarket Research Files

**`claude_research.md`**
- Deep fundamental analysis from Claude
- Detailed scenario modeling and expected value calculations
- Typically longer-term perspective (30-90 day catalysts)
- Focus on M&A, partnerships, fundamental overvaluation

**`chatgpt_research.md`**
- Tactical catalyst-driven analysis from ChatGPT
- Near-term events (1-30 days)
- Emphasis on FDA PDUFAs, earnings, product launches
- Built-in risk controls (auto-trim on gaps >10%)

**`consensus.md`** ⭐ **START HERE**
- Side-by-side comparison of both AI perspectives
- Identifies overlaps (high-conviction consensus)
- Highlights divergences (diversification opportunities)
- Provides synthesis recommendations
- Includes scenario planning and execution priority

**`trades.md`** 🎯 **READY TO EXECUTE**
- Actionable trade recommendations
- Specific entry prices, stop losses, targets
- Position sizing with risk calculations
- Execution priority and timing guidance
- Copy/paste ready for order entry

---

## 🔄 Daily Workflow

### Evening (after market close)

1. **Generate Research** (automated at 6:00 PM ET)
   ```bash
   # Automated via Windows Task Scheduler
   python daily_premarket_report.py
   ```
   - Generates reports in `reports/premarket/YYYY-MM-DD/`
   - Copies to `reports/premarket/latest/`

2. **Review Research** (manual - 10-15 minutes)
   - Read `consensus.md` for synthesis
   - Deep dive into `claude_research.md` or `chatgpt_research.md` as needed
   - Note any major divergences or warnings

3. **Prepare for Tomorrow** (manual - 5 minutes)
   - Review `trades.md` for execution plan
   - Set price alerts for entries/stops
   - Note key catalysts (CPI, earnings, FDA decisions)

### Morning (pre-market)

1. **Check for Updates** (5 minutes before open)
   ```bash
   python health_check.py
   python get_portfolio_status.py
   ```

2. **Review Latest** (access from `latest/`)
   - Check `latest/trades.md` for any overnight updates
   - Verify no major after-hours gaps (>10% rule)

3. **Execute Trades** (market open)
   ```bash
   # Option 1: Automated
   python scripts/automation/execute_daily_trades.py

   # Option 2: Manual via Alpaca dashboard
   # Use trades.md as reference
   ```

4. **Log Execution** (after fills)
   - Save to `reports/execution/YYYY-MM-DD/`
   - Update portfolio tracking

---

## 📊 Report Comparison Guide

### When to Favor Claude's Recommendations

✅ **Use Claude when:**
- You want longer-term holds (30-90+ days)
- You value detailed scenario analysis
- You prefer M&A arbitrage or partnership plays
- You want ultra-defensive positioning (beta 0.41)
- You appreciate expected value calculations

**Claude's Strengths:**
- Comprehensive fundamental analysis (18+ metrics)
- Detailed alternative data integration
- Sophisticated risk/reward modeling
- Conservative position sizing (Kelly Criterion)

**Example**: PTGX M&A arbitrage (60-90 day timeline, detailed diligence analysis)

### When to Favor ChatGPT's Recommendations

✅ **Use ChatGPT when:**
- You want near-term catalysts (1-14 days)
- You prefer defined-risk setups
- You like FDA PDUFA clusters
- You want market-matching returns (beta ~1.0)
- You value concise, tactical execution

**ChatGPT's Strengths:**
- Imminent catalyst focus (< 2 weeks)
- Built-in risk controls (auto-trim rules)
- Clean execution table format
- Balanced defensive approach

**Example**: GKOS PDUFA Oct 20 (6 days away, clear risk-defined setup)

### When to Use Consensus

⭐ **Always review `consensus.md` first:**
- Identifies high-conviction overlaps (both AIs agree)
- Provides balanced portfolio construction
- Synthesizes complementary perspectives
- Includes hybrid approaches (best of both)

**Recommended Strategy**: Execute consensus recommendations which combine:
- Claude's high-conviction longs (PTGX)
- ChatGPT's imminent catalysts (GKOS, SNDX)
- Overlapping defensives (JNJ, PG)
- Diversified approach across both AI perspectives

---

## 🗂️ Archive Policy

### Automated Archiving (planned)

Reports older than 30 days are automatically moved to `reports/archive/YYYY-MM/`:

```bash
# Run monthly (automated)
python scripts/utilities/archive_old_reports.py --days=30
```

### Manual Archive Access

To access historical reports:

```bash
# List archived months
ls reports/archive/

# View specific month
ls reports/archive/2025-10/

# Extract from archive (if needed)
cp reports/archive/2025-10/YYYY-MM-DD/ reports/premarket/
```

---

## 📈 Performance Tracking

### Portfolio Snapshots

Daily snapshots saved to `reports/performance/YYYY-MM-DD/`:

**`portfolio_snapshot.json`** - End-of-day positions
```json
{
  "date": "2025-10-15",
  "total_value": 207591.42,
  "cash": 152485.33,
  "positions": [
    {"symbol": "PTGX", "shares": 180, "avg_entry": 76.50, "current_price": 77.28}
  ]
}
```

**`daily_pnl.json`** - Daily profit/loss
```json
{
  "date": "2025-10-15",
  "realized_pnl": 1250.00,
  "unrealized_pnl": 3420.50,
  "total_pnl": 4670.50,
  "pnl_pct": 2.25
}
```

**`performance_summary.md`** - Human-readable summary

---

## 🔧 Maintenance

### Weekly Tasks

- [ ] Review execution accuracy (orders filled vs intended)
- [ ] Compare actual performance vs projected (consensus.md scenarios)
- [ ] Note any systematic biases (Claude vs ChatGPT win rates)

### Monthly Tasks

- [ ] Archive reports >30 days old
- [ ] Analyze which AI performed better this month
- [ ] Adjust weighting if consistent over/underperformance
- [ ] Review and update this README if workflow changes

### Quarterly Tasks

- [ ] Deep performance attribution analysis
- [ ] Evaluate dual-AI approach vs single-source
- [ ] Consider adjustments to research generation prompts
- [ ] Backtest consensus recommendations

---

## 🚀 Quick Commands

### View Latest Reports
```bash
# Consensus (recommended starting point)
cat reports/premarket/latest/consensus.md

# Executable trades
cat reports/premarket/latest/trades.md

# Claude detailed analysis
cat reports/premarket/latest/claude_research.md

# ChatGPT tactical analysis
cat reports/premarket/latest/chatgpt_research.md
```

### Execute Trades
```bash
# Automated execution
python scripts/automation/execute_daily_trades.py --date=2025-10-15

# With confirmation prompts
python scripts/automation/execute_daily_trades.py --date=2025-10-15 --confirm
```

### Check Status
```bash
# System health
python health_check.py

# Portfolio status
python get_portfolio_status.py

# Recent performance
python scripts/utilities/show_recent_performance.py --days=7
```

---

## 📚 Related Documentation

- **[Live Trading Deployment Guide](../docs/LIVE_TRADING_DEPLOYMENT_GUIDE.md)** - Safety mechanisms, risk management
- **[Trading Strategies](../docs/TRADING_STRATEGIES.md)** - SHORGAN-BOT and DEE-BOT methodologies
- **[Current Status](../docs/CURRENT_STATUS.md)** - System status and roadmap
- **[API Usage](../docs/API_USAGE.md)** - Anthropic + Financial Datasets API details

---

## ❓ FAQ

**Q: Which report should I read first?**
A: Always start with `consensus.md` - it synthesizes both AI perspectives and provides actionable recommendations.

**Q: What if Claude and ChatGPT completely disagree?**
A: This is actually valuable! It shows diverse perspectives. The consensus report helps you understand why they diverge and suggests balanced approaches.

**Q: Can I execute only one AI's recommendations?**
A: Yes, but you lose diversification benefits. Consensus recommendations typically outperform either AI alone.

**Q: How often are reports generated?**
A: Daily at 6:00 PM ET (automated). Fresh reports available for next trading day by evening.

**Q: What if I miss the 6 PM generation?**
A: Reports are saved in `latest/` and persist until overwritten. You can review them anytime before market open.

**Q: Are stop losses mandatory?**
A: For SHORGAN positions, YES (15-20% stops). For DEE-BOT, stops are optional but 10% portfolio drawdown is a reassessment trigger.

---

**Last Reorganization**: October 14, 2025
**Total Reports Archived**: 18MB (47 files from Sept-Oct)
**Current Reports**: Oct 15, 2025 (ready for execution)
**Status**: ✅ Clean, organized, production-ready
