# ChatGPT Trading Recommendations Retrieval Guide
## September 17, 2025 Morning Pipeline

---

## 📋 STEPS TO GET FRESH RECOMMENDATIONS

### 1. Open ChatGPT TradingAgents
Navigate to your ChatGPT conversation with TradingAgents

### 2. Request Morning Analysis
Use this prompt:
```
Generate today's trading recommendations for September 17, 2025 for SHORGAN-BOT.
Focus on:
- Micro-cap catalysts (under $2B market cap)
- Upcoming earnings (CBRL tonight)
- FDA decisions (INCY on Sept 19)
- Short squeeze opportunities
- Binary events with asymmetric risk/reward

Provide 5 actionable trades with:
- Entry price
- Stop loss
- Target price
- Position sizing
- Risk/reward analysis
```

### 3. Save the Report
Once ChatGPT generates the report:
- Copy the full text
- Save to: `scripts-and-data/daily-json/chatgpt/chatgpt_report_20250917.json`

### 4. Process Trades
Run the multi-agent analysis:
```bash
python scripts-and-data/automation/process-trades.py
```

---

## 📊 CURRENT POSITIONS TO MONITOR

### High Priority (Catalysts This Week)
- **CBRL**: 81 shares @ $51.00 - Earnings tonight
- **INCY**: 61 shares @ $83.97 - FDA decision Sept 19

### Active Positions (17 total in SHORGAN-BOT)
Best performer: RGTI (+22.73%)
Worst performer: KSS (-7.37%)

---

## 🎯 FOCUS AREAS FOR TODAY

1. **CBRL Earnings Play** - Monitor pre-market movement
2. **New Catalyst Opportunities** - Look for Sept 18-20 events
3. **Risk Management** - Check all stop losses are in place
4. **DEE-BOT Rebalancing** - Verify beta remains near 1.0

---

*Note: Manual retrieval required as ChatGPT extension has parsing issues*