# 📊 AI Trading Bot Performance Dashboard
## Last Updated: September 17, 2025, 6:15 PM ET

---

## 💰 PORTFOLIO PERFORMANCE

### Overall Statistics
| Metric | Value | Change |
|--------|--------|--------|
| **Total Portfolio Value** | $205,338.41 | +2.54% |
| **Total P&L** | +$5,080.89 | - |
| **Win Rate** | 65% (13/20 positions) | - |
| **Best Position** | RGTI | +22.73% |
| **Worst Position** | KSS | -7.37% |
| **Sharpe Ratio** | ~1.45 | - |

### Bot Performance
| Bot | Value | P&L | Positions | Strategy |
|-----|-------|-----|-----------|----------|
| **SHORGAN-BOT** | $105,338.41 | +$5,080.89 | 17 | Catalyst Trading |
| **DEE-BOT** | $100,118.84 | +$118.84 | 3 | Beta-Neutral |
| **Combined** | $205,457.25 | +$5,199.73 | 20 | Dual Strategy |

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

### Portfolio Holdings (ORGANIZED)
- [Combined Portfolio](../portfolio-holdings/current/combined-portfolio.csv)
- [SHORGAN Positions](../portfolio-holdings/current/shorgan-bot-positions.csv)
- [DEE Positions](../portfolio-holdings/current/dee-bot-positions.csv)
- [Historical Snapshots](../portfolio-holdings/historical/)

### Trade Logs (CONSOLIDATED)
- [Master Trade Log](../trade-logs/all-trades.csv)
- [Recent Trades](../trade-logs/recent-trades.csv)
- [SHORGAN Trade JSON](../09_logs/trading/SHORGAN_BOT_TRADE_LOG_COMPLETE.json)
- [DEE Trade JSON](../09_logs/trading/DEE_BOT_TRADE_LOG_COMPLETE.json)

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