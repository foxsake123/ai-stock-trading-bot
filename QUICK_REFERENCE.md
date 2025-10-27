# AI Trading Bot - Quick Reference Card
**Updated**: October 26, 2025

---

## 🚀 SYSTEM STATUS: FULLY AUTOMATED

**Portfolio Value**: $206,494.82 (+3.25%)
**Next Action**: Monday Oct 28, 8:30 AM (automatic)

---

## 📅 AUTOMATED SCHEDULE

| Time | Task | What Happens |
|------|------|--------------|
| **Saturday 12:00 PM** | Research Generation | Claude generates trading research, sends PDFs to Telegram |
| **Monday 8:30 AM** | Trade Generation | Multi-agent validates research, creates TODAYS_TRADES file |
| **Monday 9:30 AM** | Trade Execution | Executes approved trades, places stops, sends summary |
| **Monday 4:30 PM** | Performance Update | Updates P&L graph, tracks daily performance |

---

## 📱 TELEGRAM NOTIFICATIONS

You'll receive:
- ✅ Research PDFs (Saturday 12 PM)
- ✅ Execution summary (Monday 9:30 AM)
- ✅ Daily performance (Monday 4:30 PM)

**Chat ID**: 7870288896

---

## 💻 QUICK COMMANDS

**Check Portfolio**:
```bash
python scripts/performance/get_portfolio_status.py
```

**Manual Research** (if automation fails):
```bash
python scripts/automation/daily_claude_research.py --force
```

**Manual Trade Generation**:
```bash
python scripts/automation/generate_todays_trades_v2.py
```

**View Today's Approved Trades**:
```bash
notepad docs\TODAYS_TRADES_2025-10-28.md
```

**Check Task Scheduler**:
```bash
taskschd.msc
```

---

## 📊 MONDAY MONITORING

**8:35 AM** - Review Approved Trades
- File: `docs\TODAYS_TRADES_2025-10-28.md`
- Check: Approval rate, confidence scores, rejection reasons

**9:35 AM** - Verify Execution
- Check: Telegram execution summary
- Verify: Fills and stop-loss orders

**4:35 PM** - Review Performance
- Check: Telegram daily P&L
- Review: Winners/losers for the day

---

## ⚠️ TROUBLESHOOTING

**No research generated?**
- Check: Task Scheduler > "AI Trading - Weekend Research"
- Run manually: `python scripts/automation/daily_claude_research.py --force`

**No trades approved?**
- Check: `docs\TODAYS_TRADES_2025-10-28.md` for rejection reasons
- Common: Low confidence, failed filters, data unavailable

**No Telegram messages?**
- Verify: Chat ID is 7870288896
- Test: Send message to @shorganbot first

**API errors?**
- Anthropic: Check credits at console.anthropic.com
- Alpaca: Check API status at alpaca.markets/status

---

## 📁 KEY FILES

**Research**:
- `reports/premarket/2025-10-27/claude_research_dee_bot_2025-10-27.pdf`
- `reports/premarket/2025-10-27/claude_research_shorgan_bot_2025-10-27.pdf`

**Approved Trades**:
- `docs/TODAYS_TRADES_2025-10-28.md` (Monday 8:30 AM)

**Configuration**:
- `.env` - API keys and secrets
- `config/portfolio_config.yaml` - Portfolio settings

**Documentation**:
- `docs/SATURDAY_RESEARCH_SETUP.md` - Setup guide
- `docs/INCIDENT_REPORT_OCT26.md` - Today's incident
- `docs/SETUP_AUTOMATION_GUIDE.md` - Automation details

---

## 🔧 TASK SCHEDULER TASKS

1. **AI Trading - Weekend Research** (Saturday 12:00 PM)
2. **AI Trading - Morning Trade Generation** (Weekdays 8:30 AM)
3. **AI Trading - Trade Execution** (Weekdays 9:30 AM)
4. **AI Trading - Daily Performance Graph** (Weekdays 4:30 PM)

---

## 📞 EMERGENCY

**Stop All Trading**:
```python
# Cancel all open orders
from alpaca.trading.client import TradingClient
# [Use cancel_stale_orders.py script]
```

**Disable Automation**:
```bash
# Disable all tasks
schtasks /change /tn "AI Trading - Weekend Research" /disable
schtasks /change /tn "AI Trading - Morning Trade Generation" /disable
schtasks /change /tn "AI Trading - Trade Execution" /disable
schtasks /change /tn "AI Trading - Daily Performance Graph" /disable
```

---

## ✅ TODAY'S ACCOMPLISHMENTS

- [x] Research schedule changed to Saturday 12 PM
- [x] Stale order incident resolved
- [x] Telegram integration fixed
- [x] Anthropic API key updated
- [x] Saturday research generated
- [x] Task Scheduler automation complete

---

**Status**: READY FOR MONDAY TRADING
**Last Updated**: October 26, 2025, 5:30 PM ET
