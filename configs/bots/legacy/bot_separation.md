# BOT SEPARATION CONFIGURATION

## SHORGAN-BOT
**Purpose:** Aggressive micro-cap catalyst trading
**API Keys:** ALPACA_API_KEY_SHORGAN / ALPACA_SECRET_KEY_SHORGAN
**Portfolio:** ~$104K
**Strategy:**
- Focus on micro to mid-cap stocks only (<$10B market cap)
- Catalyst-driven trades (earnings, insider activity, FDA approvals)
- 5-8 high conviction trades
- Position sizes: 5-15% per trade
- Uses ChatGPT daily research reports
- Options strategies (when available)

**Data Sources:**
- ChatGPT TradingAgents reports
- OpenAI API for research
- Unusual options flow
- Insider trading data

**Files:**
- Reports: `02_data/research/reports/pre_market_daily/*_chatgpt_*.json`
- Positions: `02_data/portfolio/positions/shorgan_bot_positions.csv`
- Logs: `09_logs/trading/shorgan_*.log`

---

## DEE-BOT
**Purpose:** [Original strategy - unchanged]
**API Keys:** ALPACA_API_KEY_DEE / ALPACA_SECRET_KEY_DEE
**Portfolio:** ~$100K
**Strategy:**
- Independent strategy (not micro-cap focused)
- Separate trading rules
- Different position sizing
- Different risk parameters

**Data Sources:**
- Separate research pipeline
- Different indicators/signals
- Independent decision making

**Files:**
- Reports: `02_data/research/reports/dee_bot/*`
- Positions: `02_data/portfolio/positions/dee_bot_positions.csv`
- Logs: `09_logs/trading/dee_*.log`

---

## CRITICAL RULES

1. **NEVER mix strategies between bots**
2. **NEVER use DEE-BOT API keys for SHORGAN trades**
3. **NEVER apply SHORGAN micro-cap rules to DEE-BOT**
4. **Each bot has independent:**
   - Portfolio management
   - Risk limits
   - Position sizing
   - Trade execution
   - Performance tracking

## DAILY OPERATIONS

### Morning (7:00 AM ET)
1. SHORGAN-BOT: Receives ChatGPT micro-cap research
2. DEE-BOT: Runs its independent analysis
3. Both execute separately via their own APIs

### Evening (4:15 PM ET)
1. SHORGAN-BOT: Performance report via Telegram
2. DEE-BOT: Separate performance report
3. Combined summary shows both but keeps them distinct

## FILE NAMING CONVENTION

Always prefix files with bot name:
- `shorgan_trades_20250912.json`
- `dee_trades_20250912.json`
- `shorgan_performance.csv`
- `dee_performance.csv`

This ensures complete separation of strategies and prevents cross-contamination.