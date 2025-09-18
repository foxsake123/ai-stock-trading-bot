# 📊 AI Trading Bot Performance Dashboard
## Last Updated: September 17, 2025, 6:15 PM ET

---

## 💰 DUAL-STRATEGY PORTFOLIO PERFORMANCE

### Combined Portfolio
| Metric | Value | Details |
|--------|--------|---------|
| **Total Portfolio Value** | $205,338.41 | Both strategies combined |
| **Total P&L** | +$5,199.73 | SHORGAN: +$5,081, DEE: +$119 |
| **Total Positions** | 20 | SHORGAN: 17, DEE: 3 |
| **Cash Available** | $88,844 | For new opportunities |

---

## 🚀 SHORGAN-BOT (Catalyst Strategy)
| Metric | Value | Details |
|--------|--------|---------|
| **Portfolio Value** | $105,338.41 | 51% of total |
| **P&L** | +$5,080.89 | +4.82% return |
| **Positions** | 17 | Active catalyst plays |
| **Win Rate** | 65% | 11/17 profitable |
| **Strategy** | Aggressive | Earnings, FDA, momentum |
| **Top Winner** | RGTI +22.73% | AI momentum play |

[📊 SHORGAN Details](../portfolio-holdings/shorgan-bot/SHORGAN_SUMMARY.md)

---

## 🛡️ DEE-BOT (Beta-Neutral Strategy)
| Metric | Value | Details |
|--------|--------|---------|
| **Portfolio Value** | $100,118.84 | 49% of total |
| **P&L** | +$118.84 | +0.12% return |
| **Positions** | 3 | Defensive holdings |
| **Portfolio Beta** | ~1.0 | Market neutral |
| **Strategy** | Defensive | S&P 100 large-caps |
| **Holdings** | PG, JNJ, KO | Consumer/Healthcare |

[📊 DEE Details](../portfolio-holdings/dee-bot/DEE_SUMMARY.md)

---

## 📈 TODAY'S ACTIVITY

### Key Events
- ❗ **CBRL Earnings Miss**: -10% after hours, exit planned for tomorrow
- ✅ **Profit-Taking Setup**: RGTI & ORCL 50% sales ready
- ⚠️ **KSS Near Stop**: -7.4%, close to -8% trigger
- 📅 **INCY FDA Thursday**: Binary event preparation

### Tomorrow's Orders (Sept 18, 9:30 AM)
1. **EXIT** CBRL: 81 shares (earnings miss)
2. **SELL** RGTI: 65 shares (profit-taking)
3. **SELL** ORCL: 21 shares (profit-taking)
4. **WATCH** KSS: Stop at $15.18
5. **SET** Trailing stops on winners

Expected Impact: +$908 net profit, $11,048 cash raised

---

## 📁 QUICK LINKS

### Daily Reports (NEW STRUCTURE)
- [Today's Reports](../daily-reports/2025-09-17/)
- [Portfolio Summary PDF](../daily-reports/2025-09-18/portfolio_summary_2025-09-18.pdf)
- [Tomorrow's Order Plan](../ORDERS_FOR_SEPT_18.md)
- [CBRL Earnings Strategy](../CBRL_EARNINGS_STRATEGY.md)
- [INCY FDA Strategy](../INCY_FDA_STRATEGY.md)

### SHORGAN-BOT Portfolio
- [Strategy Overview](../portfolio-holdings/shorgan-bot/SHORGAN_SUMMARY.md)
- [Current Positions](../portfolio-holdings/shorgan-bot/current/positions.csv)
- [Trade History](../trade-logs/shorgan-bot/)
- [Historical Snapshots](../portfolio-holdings/shorgan-bot/historical/)

### DEE-BOT Portfolio
- [Strategy Overview](../portfolio-holdings/dee-bot/DEE_SUMMARY.md)
- [Current Positions](../portfolio-holdings/dee-bot/current/positions.csv)
- [Trade History](../trade-logs/dee-bot/)
- [Historical Snapshots](../portfolio-holdings/dee-bot/historical/)

### Combined Views
- [Combined Portfolio](../portfolio-holdings/current/combined-portfolio.csv)
- [All Trades](../trade-logs/all-trades.csv)
- [Recent Activity](../trade-logs/recent-trades.csv)

### System Documentation
- [Architecture](../docs/SYSTEM_ARCHITECTURE.md)
- [Product Plan](../docs/PRODUCT_PLAN.md)
- [CLAUDE.md Guide](../CLAUDE.md)
- [Portfolio Structure](../PORTFOLIO_LOGGING_STRUCTURE.md)

---

## 📊 CURRENT HOLDINGS

### Top Winners 🚀
| Symbol | Shares | Entry | Current | P&L | Action |
|--------|--------|-------|---------|-----|--------|
| RGTI | 130 | $15.35 | $18.84 | +22.73% | Sell 50% tomorrow |
| ORCL | 42 | $239.04 | $291.43 | +21.92% | Sell 50% tomorrow |
| DAKT | 743 | $20.97 | $23.87 | +13.85% | Trailing stop |
| TSLA | 2 | $349.12 | $395.50 | +13.28% | Hold |
| BTBT | 570 | $2.66 | $2.95 | +10.89% | Hold |

### Positions at Risk ⚠️
| Symbol | Shares | Entry | Current | P&L | Action |
|--------|--------|-------|---------|-----|--------|
| KSS | 90 | $16.50 | $15.28 | -7.37% | Near stop @ $15.18 |
| CBRL | 81 | $51.00 | ~$45.82 | -10.16% | EXIT tomorrow |
| SAVA | 200 | $2.17 | $2.10 | -3.22% | Monitor |

### Upcoming Catalysts 📅
| Date | Symbol | Event | Position | Strategy |
|------|--------|-------|----------|----------|
| Sept 17 | CBRL | Earnings (MISSED) | 81 shares | Exit at open |
| Sept 19 | INCY | FDA Decision | 61 shares | Hold for binary |

---

## 📉 RISK METRICS

### Portfolio Risk
- **Capital Deployed**: 58.2% ($116,494)
- **Cash Available**: 41.8% ($88,844)
- **Max Daily Loss**: -3% trigger deleveraging
- **Force Close**: -7% daily loss
- **Sector Concentration**: Within 30% limits

### Position Limits
- **SHORGAN Max**: 10% per position
- **DEE Max**: 8% per position
- **Current Largest**: DAKT at 8.6%

---

## 🔧 SYSTEM STATUS

### Services
| Service | Status | Details |
|---------|--------|---------|
| ChatGPT Server | 🟢 Running | localhost:8888 |
| Telegram Bot | ✅ Active | 4:30 PM reports |
| Multi-Agent System | ✅ Operational | 9 agents |
| Risk Management | ✅ Active | All stops set |

### Known Issues
- ⚠️ DEE-BOT position updates need automation
- ⚠️ Yahoo Finance rate limiting
- ⚠️ ChatGPT extension float parsing

---

## 📅 UPCOMING WEEK

### Schedule
- **Sept 18**: Execute morning trades, monitor CBRL gap
- **Sept 19**: INCY FDA decision (binary event)
- **Sept 20**: Post-FDA portfolio rebalancing
- **Sept 23**: New week catalyst scan

### Development Tasks
1. Fix DEE-BOT Alpaca API configuration
2. Automate position price updates
3. Consolidate PDF reports
4. Create master trade log
5. Build web dashboard

---

## 📈 PERFORMANCE HISTORY

### Monthly Returns
| Month | SHORGAN | DEE | Combined |
|-------|---------|-----|----------|
| Sept 2025 | +4.82% | +0.12% | +2.54% |
| Aug 2025 | - | - | - |

### Key Statistics
- **Trades Executed**: 47
- **Win Rate**: 65%
- **Average Hold**: 3-7 days
- **Best Trade**: RGTI +22.73%
- **Worst Trade**: KSS -7.37%

---

## 🔗 EXTERNAL LINKS

### Resources
- [GitHub Repository](https://github.com/foxsake123/ai-stock-trading-bot)
- [Alpaca Dashboard](https://paper-api.alpaca.markets)
- [ChatGPT TradingAgents](https://chatgpt.com)

### References
- [LuckyOne7777 Experiment](https://github.com/LuckyOne7777/ChatGPT-Micro-Cap-Experiment)
- [TradingAgents Paper](../07_docs/research_papers/TradingAgents_Multi-Agents LLM Financial Trading.pdf)

---

*Dashboard auto-generated from live portfolio data. Updates daily at 4:30 PM ET.*

**Next Update**: September 18, 2025, after market close