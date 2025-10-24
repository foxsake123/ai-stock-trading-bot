# Telegram Reports - Quick Guide

## ✅ What Just Happened

Successfully sent to your Telegram:
1. ✅ **Morning Trade Report** - Current portfolio status, P/L, top performers
2. ✅ **DEE-BOT Research PDF** - Deep research report for Oct 23 trading
3. ✅ **SHORGAN-BOT Research PDF** - Catalyst research for Oct 23 trading

---

## 📱 Available Reports

### 1. Morning Trade Report (After Market Open)

#### Option A: Enhanced Report (RECOMMENDED) ⭐
**What:** Full enhanced report with executive summary, signal indicators, and priority scoring
**When:** 9:45 AM ET (after trades execute)
**Command:**
```bash
python scripts/automation/send_enhanced_morning_report.py
```

**What's Included:**
- Executive summary with portfolio overview
- Number of trades executed today
- Current portfolio value (both bots)
- P/L summary with percentages
- Top 3 performers
- Watch list (positions with losses)
- Signal strength indicators
- Priority scoring

**Features from Oct 22 Enhanced Format:**
- ✅ Executive summary table
- ✅ Portfolio overview (DEE-BOT + SHORGAN-BOT)
- ✅ Trades executed with entry prices
- ✅ Top performers and watch list
- ✅ Clean Telegram formatting

#### Option B: Basic Report (Legacy)
**What:** Simple text report with portfolio status
**When:** 9:45 AM ET (after trades execute)
**Command:**
```bash
python scripts/automation/send_morning_trade_report.py
```

**What's Included:**
- Number of trades executed today
- Current portfolio value (both bots)
- P/L summary with percentages
- Top 3 performers
- Watch list (positions with losses)

**Example Output:**
```
📊 MORNING TRADE REPORT
Wednesday, October 23, 2025 - 12:06 PM ET

NO TRADES EXECUTED TODAY

CURRENT PORTFOLIO STATUS

DEE-BOT (Beta-Neutral)
Portfolio: $102,725.59
Cash: $48,999.58
Positions: 10

SHORGAN-BOT (Catalyst)
Portfolio: $103,504.49
Cash: $89,309.51
Positions: 23

COMBINED TOTAL
Portfolio: $206,230.08
Total P/L: $6,230.08 (+3.12%)

TOP PERFORMERS:
  🟢 RGTI: +162.14%
  🟢 ORCL: +17.60%
  🟢 WOLF: +15.11%

WATCH LIST (Losses):
  🔴 GKOS: -13.40%
  🔴 FUBO: -13.51%
```

---

### 2. Research PDFs
**What:** Claude deep research reports with trade recommendations
**When:** 6:00 PM ET (evening before trading day)
**Command:**
```bash
# Send today's research
python scripts/automation/send_research_pdfs.py

# Send specific date
python scripts/automation/send_research_pdfs.py --date 2025-10-23

# Send only one bot
python scripts/automation/send_research_pdfs.py --bot dee
python scripts/automation/send_research_pdfs.py --bot shorgan
```

**What's Included:**
- DEE-BOT research PDF (beta-neutral stocks)
- SHORGAN-BOT research PDF (catalyst-driven trades)
- Entry prices, stop losses, targets
- Risk/reward analysis
- Catalyst timeline

---

### 3. Post-Market Report (End of Day)
**What:** End-of-day portfolio summary, daily P/L
**When:** 4:15 PM ET (after market close)
**Command:**
```bash
python scripts/automation/generate_post_market_report.py
```

**What's Included:**
- Daily P/L for both bots
- Percentage changes
- Combined portfolio summary
- Warnings for positions down >10%
- Link to tomorrow's research

**Example Output:**
```
📊 POST-MARKET REPORT
Wednesday, October 23, 2025 - 04:15 PM ET

DEE-BOT (Beta-Neutral)
Portfolio: $102,725.59
P/L: +$1,234.56 (+1.22%)
Positions: 10

SHORGAN-BOT (Catalyst)
Portfolio: $103,504.49
P/L: +$2,345.67 (+2.32%)
Positions: 23

COMBINED TOTAL
Portfolio: $206,230.08
Total P/L: +$3,580.23 (+1.77%)

📈 Review Claude research for tomorrow's trade plan
```

---

## ⏰ Automated Schedule

### Current Automation
```
6:00 PM (evening):     Generate Claude research
7:00 PM:               Manual ChatGPT research
                       → PDFs automatically sent via Telegram ✅

8:30 AM:               Generate trades from research
9:30 AM:               Execute approved trades
9:45 AM:               Send morning report via Telegram ⏳ TO SETUP

4:15 PM:               Send post-market report via Telegram ✅
```

### Setup Morning Report Automation

```batch
schtasks /create /tn "AI Trading - Morning Report" ^
  /tr "python C:\Users\shorg\ai-stock-trading-bot\scripts\automation\send_morning_trade_report.py" ^
  /sc daily /st 09:45 ^
  /ru SYSTEM
```

This will automatically send the morning report at 9:45 AM ET every trading day.

---

## 🎯 Quick Commands

### Send Everything Now
```bash
# 1. Morning report
python scripts/automation/send_morning_trade_report.py

# 2. Research PDFs
python scripts/automation/send_research_pdfs.py --date 2025-10-23

# 3. Post-market report
python scripts/automation/generate_post_market_report.py
```

### Send Specific Date
```bash
# Morning report for specific date
python scripts/automation/send_morning_trade_report.py --date 2025-10-16

# Research for specific date
python scripts/automation/send_research_pdfs.py --date 2025-10-16
```

### Send Specific Bot
```bash
# Only DEE-BOT research
python scripts/automation/send_research_pdfs.py --bot dee

# Only SHORGAN-BOT research
python scripts/automation/send_research_pdfs.py --bot shorgan
```

---

## 📊 What Each Report Shows

### Morning Report Shows:
- ✅ Trades executed this morning
- ✅ Current portfolio value
- ✅ Cash available
- ✅ Number of open positions
- ✅ Total P/L since start
- ✅ Top 3 winning positions
- ✅ Positions with losses (watch list)

### Research PDFs Show:
- ✅ Stock recommendations
- ✅ Entry prices and timing
- ✅ Stop loss levels
- ✅ Target prices
- ✅ Risk/reward ratios
- ✅ Catalyst analysis
- ✅ Position sizing
- ✅ Expected holding period

### Post-Market Report Shows:
- ✅ Daily P/L (both bots)
- ✅ Percentage changes
- ✅ Combined portfolio value
- ✅ Warnings for big losers
- ✅ Link to tomorrow's research

---

## 🔧 Configuration

### Required Environment Variables
Make sure these are in your `.env` file:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Alpaca API (for portfolio data)
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

### Get Your Telegram Config
1. Create bot: Message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow instructions
3. Copy the token (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
4. Get your chat ID: Message [@userinfobot](https://t.me/userinfobot)
5. Add both to `.env` file

---

## 📁 File Locations

### Scripts
```
scripts/automation/
├── send_morning_trade_report.py     ⭐ Morning report
├── send_research_pdfs.py            ⭐ Research PDFs
└── generate_post_market_report.py   ⭐ Post-market report
```

### Reports
```
reports/premarket/2025-10-23/
├── claude_research_dee_bot_2025-10-23.pdf
├── claude_research_shorgan_bot_2025-10-23.pdf
└── claude_research.md

docs/
└── TODAYS_TRADES_2025-10-23.md      (if trades generated)

docs/reports/post-market/
└── post_market_report_2025-10-23.txt
```

---

## 🆘 Troubleshooting

### "Failed to send Telegram message"
**Solution:** Check TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in `.env`

### "No research PDFs found"
**Solution:** Research hasn't been generated yet
```bash
python scripts/automation/daily_claude_research.py --force
```

### "No trades found for today"
**Solution:** No trades were generated/executed
```bash
# Check if research exists
ls reports/premarket/2025-10-23/

# Generate trades from research
python scripts/automation/generate_todays_trades_v2.py
```

### "Portfolio data not available"
**Solution:** Alpaca API issue - check API keys in `.env`

---

## ✨ Summary

You now have **3 automated Telegram reports**:

1. **Morning Report** (9:45 AM) - Portfolio status after trades
2. **Research PDFs** (6:00 PM) - Tomorrow's trade recommendations
3. **Post-Market Report** (4:15 PM) - End of day P/L

All reports are **already working** and can be sent manually or scheduled!

---

**Last Updated:** October 23, 2025
**Status:** ✅ All reports operational
**Next:** Schedule morning report automation
