# Step-by-Step Guide: Setting Up Automated Trading at 9:30 AM ET

## ⚠️ IMPORTANT: Start with Paper Trading Only!

This guide will help you set up automated trade execution at market open (9:30 AM ET).

---

## Step 1: Get Alpaca API Credentials (5 minutes)

### A. Create Alpaca Account
1. Go to https://alpaca.markets
2. Click "Sign Up"
3. Complete registration
4. Verify your email

### B. Get Paper Trading API Keys
1. Log into Alpaca Dashboard
2. Click on "Paper Trading" (top of page)
3. View API Keys (right side)
4. Copy:
   - API Key ID
   - Secret Key

### C. Save to .env file
```bash
# Open .env file and add:
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
```

---

## Step 2: Test Alpaca Connection (2 minutes)

### Create test script:

```python
# save as: test_alpaca_connection.py
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

# Connect to paper trading
api = tradeapi.REST(
    key_id=os.getenv("ALPACA_API_KEY"),
    secret_key=os.getenv("ALPACA_SECRET_KEY"),
    base_url="https://paper-api.alpaca.markets"
)

# Test connection
account = api.get_account()
print(f"Connected to Alpaca Paper Trading!")
print(f"Account Balance: ${account.portfolio_value}")
print(f"Buying Power: ${account.buying_power}")
print(f"Pattern Day Trader: {account.pattern_day_trader}")
```

### Run test:
```bash
python test_alpaca_connection.py
```

You should see your paper account balance ($100,000 default).

---

## Step 3: Configure Trading Settings (5 minutes)

### Edit .env file with your preferences:

```bash
# EXECUTION MODE (ALWAYS start with paper!)
EXECUTION_MODE=paper

# POSITION LIMITS
MAX_POSITION_SIZE=5000      # Max $5,000 per trade (conservative)
MAX_POSITIONS=5              # Max 5 positions at once
MAX_DAILY_TRADES=10          # Max 10 trades per day
MAX_DAILY_LOSS=1000          # Stop if lose $1,000 in a day

# TRADING HOURS
ALLOW_PREMARKET=false        # No pre-market trading
ALLOW_AFTERHOURS=false       # No after-hours trading

# STOCK RESTRICTIONS (optional)
BLACKLIST_STOCKS=            # Comma-separated list to avoid
WHITELIST_STOCKS=            # If set, ONLY trade these
```

---

## Step 4: Create Bot Integration Script (10 minutes)

### Create main execution script:

```python
# save as: run_trading_system.py
#!/usr/bin/env python3
"""
Main trading system runner - executes at 9:30 AM ET
"""
import asyncio
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
sys.path.append('.')

from automated_trade_executor import AutomatedTradeExecutor, ExecutionMode
from trade_signal_generator import SignalRouter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def run_morning_trading():
    """Main trading execution for market open"""
    
    logger.info("="*50)
    logger.info(f"Starting Trading System at {datetime.now()}")
    logger.info("="*50)
    
    # Get execution mode from environment
    mode_str = os.getenv("EXECUTION_MODE", "paper").lower()
    mode_map = {
        'paper': ExecutionMode.PAPER,
        'manual': ExecutionMode.MANUAL_APPROVAL,
        'semi': ExecutionMode.SEMI_AUTO,
        'full': ExecutionMode.FULL_AUTO
    }
    mode = mode_map.get(mode_str, ExecutionMode.PAPER)
    
    logger.info(f"Execution Mode: {mode.value.upper()}")
    
    # Initialize signal router with executor
    router = SignalRouter(mode)
    
    # Check if we have morning recommendations from bots
    dee_bot_file = Path("dee_bot/data/morning_recommendations.json")
    shorgan_bot_file = Path("shorgan-bot/data/morning_recommendations.json")
    
    # Process dee-bot recommendations if available
    if dee_bot_file.exists():
        import json
        with open(dee_bot_file, 'r') as f:
            dee_recommendations = json.load(f)
        logger.info(f"Processing {len(dee_recommendations.get('recommendations', []))} dee-bot signals")
        await router.route_dee_bot_signals(dee_recommendations)
    else:
        logger.info("No dee-bot recommendations found")
    
    # Process shorgan-bot recommendations if available
    if shorgan_bot_file.exists():
        import json
        with open(shorgan_bot_file, 'r') as f:
            shorgan_recommendations = json.load(f)
        logger.info(f"Processing {len(shorgan_recommendations.get('recommendations', []))} shorgan-bot signals")
        await router.route_shorgan_bot_signals(shorgan_recommendations)
    else:
        logger.info("No shorgan-bot recommendations found")
    
    # Get status
    status = router.get_status()
    logger.info(f"Trading System Status:")
    logger.info(f"  Portfolio Value: ${status['executor_status']['portfolio_value']:,.2f}")
    logger.info(f"  Open Positions: {len(status['executor_status']['positions'])}")
    logger.info(f"  Pending Signals: {status['pending_signals']}")
    
    # If manual approval mode, handle approvals
    if mode == ExecutionMode.MANUAL_APPROVAL and status['pending_signals'] > 0:
        logger.info("Manual approval required for pending trades")
        await router.executor.approve_pending_trades()
    
    logger.info("Trading system execution complete")

if __name__ == "__main__":
    asyncio.run(run_morning_trading())
```

---

## Step 5: Create Windows Scheduler (5 minutes)

### A. Create batch file for Windows Task Scheduler:

```batch
@echo off
REM save as: run_morning_trades.bat
cd C:\Users\shorg\ai-stock-trading-bot
call venv\Scripts\activate
python run_trading_system.py
pause
```

### B. Set up Windows Task Scheduler:

1. Open Task Scheduler (search "Task Scheduler" in Windows)
2. Click "Create Basic Task"
3. Name: "Morning Trading Bot 9:30 AM"
4. Trigger: Daily
5. Start time: 9:30 AM
6. Action: Start a program
7. Program: `C:\Users\shorg\ai-stock-trading-bot\run_morning_trades.bat`
8. Check "Open Properties dialog"
9. In Properties:
   - Check "Run only when user is logged on"
   - Check "Run with highest privileges"
   - Conditions tab: Uncheck "Start only if on AC power"

### Alternative: PowerShell Scheduled Task (run as admin):

```powershell
# save as: create_trading_schedule.ps1
$action = New-ScheduledTaskAction -Execute "C:\Users\shorg\ai-stock-trading-bot\run_morning_trades.bat"
$trigger = New-ScheduledTaskTrigger -Daily -At 9:30AM
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "Morning Trading Bot" `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description "Runs trading bot at market open (9:30 AM ET)"
```

---

## Step 6: Test Paper Trading First! (REQUIRED)

### Day 1: Manual Test
```bash
# Test manually first at 9:30 AM
cd C:\Users\shorg\ai-stock-trading-bot
python run_trading_system.py
```

### Check Results:
```bash
# View execution log
type data\execution_log.json

# View signal log  
type data\signal_log.json

# Check trading system log
type logs\trading_system.log
```

---

## Step 7: Monitor Paper Trading (1 Week Minimum)

### Daily Checklist:
- [ ] Check morning execution log
- [ ] Review trades in Alpaca dashboard
- [ ] Monitor win/loss ratio
- [ ] Verify stop losses working
- [ ] Check position sizing correct

### Create monitoring script:

```python
# save as: check_trading_status.py
import json
from pathlib import Path
from datetime import datetime

# Load execution log
log_file = Path("data/execution_log.json")
if log_file.exists():
    with open(log_file, 'r') as f:
        executions = json.load(f)
    
    # Today's trades
    today = datetime.now().date()
    today_trades = [e for e in executions if datetime.fromisoformat(e['timestamp']).date() == today]
    
    print(f"Today's Trading Activity ({today}):")
    print(f"Total Trades: {len(today_trades)}")
    
    successful = sum(1 for t in today_trades if t.get('success', False))
    print(f"Successful: {successful}")
    print(f"Failed: {len(today_trades) - successful}")
    
    for trade in today_trades:
        status = "✓" if trade.get('success') else "✗"
        print(f"{status} {trade['timestamp']}: {trade['action']} {trade['shares']} {trade['ticker']} - {trade['message']}")
else:
    print("No execution log found")
```

---

## Step 8: Progress to Live Trading (After Successful Testing)

### Week 1-2: Paper Trading
```bash
EXECUTION_MODE=paper
```

### Week 3: Manual Approval
```bash
EXECUTION_MODE=manual
# You'll need to approve each trade
```

### Week 4: Semi-Auto (Small Trades)
```bash
EXECUTION_MODE=semi
# Small trades auto-execute
```

### Month 2+: Full Auto (Only if comfortable)
```bash
EXECUTION_MODE=full
# All trades auto-execute
```

---

## Troubleshooting

### Issue: Alpaca connection fails
```bash
# Check credentials
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ALPACA_API_KEY')[:10]+'...')"
```

### Issue: No trades executing
1. Check confidence thresholds in recommendations
2. Verify position limits not exceeded
3. Check blacklist/whitelist settings
4. Ensure market is open

### Issue: Task Scheduler not running
1. Check Windows Event Viewer for errors
2. Ensure Python path is correct
3. Try running batch file manually first

---

## Emergency Stop

### To immediately stop all trading:

1. **Disable Task Scheduler**:
   - Open Task Scheduler
   - Find "Morning Trading Bot"
   - Right-click → Disable

2. **Set paper mode in .env**:
   ```bash
   EXECUTION_MODE=paper
   ```

3. **Or set zero trades**:
   ```bash
   MAX_DAILY_TRADES=0
   ```

---

## Daily Workflow

### 8:30 AM - Pre-Market
- Bots generate research reports
- Review recommendations

### 9:30 AM - Market Open
- Scheduled task runs automatically
- Trades execute based on mode
- Log files updated

### 10:00 AM - Check Status
```bash
python check_trading_status.py
```

### 4:00 PM - End of Day
- Review performance
- Check Alpaca dashboard
- Analyze trades

---

## Important Reminders

⚠️ **ALWAYS**:
1. Start with PAPER trading
2. Test for at least 1 week
3. Use small position sizes initially
4. Monitor daily performance
5. Have emergency stop ready

❌ **NEVER**:
1. Skip paper trading phase
2. Use FULL_AUTO without extensive testing
3. Trade with money you can't afford to lose
4. Ignore safety limits
5. Override risk controls

---

## Support

If you need help:
1. Check logs in `logs/trading_system.log`
2. Review `data/execution_log.json`
3. Verify Alpaca paper account status
4. Ensure all safety controls are active

Remember: The system is designed to be safe by default. Take your time progressing through each stage.