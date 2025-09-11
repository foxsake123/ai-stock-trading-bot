# Performance Tracking System

## Overview
Automated daily performance tracking for DEE-BOT and SHORGAN-BOT trading accounts. Fetches real data from Alpaca Paper Trading API and sends formatted reports via Telegram.

## Components

### 1. Daily Performance Tracker (`daily_performance_tracker.py`)
- Connects to both Alpaca paper trading accounts
- Fetches account data, positions, and orders
- Calculates P&L metrics and win rates
- Saves performance data to JSON

### 2. Telegram Reporter (`send_performance_update.py`)
- Loads latest performance data
- Formats as emoji-rich Telegram message
- Sends to configured Telegram chat

### 3. Automated Scheduler (`automated_performance_tracker.py`)
- Runs complete tracking pipeline
- Can be scheduled or run manually
- Includes logging and error handling

### 4. Market Hours Checker (`market_hours_checker.py`)
- Determines if markets are open
- Checks for holidays and weekends
- Validates report timing

## Setup Instructions

### 1. Install Dependencies
```bash
pip install alpaca-trade-api python-telegram-bot pytz holidays schedule
```

### 2. Configure Environment Variables
Ensure `.env` file contains:
```
# Telegram Configuration
TELEGRAM_BOT_TOKEN=8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c
TELEGRAM_CHAT_ID=7870288896

# DEE-BOT Alpaca Credentials
ALPACA_API_KEY_DEE=PK6FZK4DAQVTD7DYVH78
ALPACA_SECRET_KEY_DEE=JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt

# SHORGAN-BOT Alpaca Credentials  
ALPACA_API_KEY_SHORGAN=PKJRLSB2MFEJUSK6UK2E
ALPACA_SECRET_KEY_SHORGAN=QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic
```

### 3. Manual Execution

Run performance tracking immediately:
```bash
python Performance_Tracking/automated_performance_tracker.py --run-now
```

Run on continuous schedule:
```bash
python Performance_Tracking/automated_performance_tracker.py --schedule
```

### 4. Windows Task Scheduler Setup

Run PowerShell as Administrator:
```powershell
cd C:\Users\shorg\ai-stock-trading-bot\Performance_Tracking
.\setup_windows_scheduler.ps1
```

This creates a scheduled task that runs daily at 4:15 PM ET on weekdays.

To manage the task:
- Open Task Scheduler (`taskschd.msc`)
- Look for "AI Trading Bot Performance Tracker"

To run manually from PowerShell:
```powershell
Start-ScheduledTask -TaskName "AI Trading Bot Performance Tracker"
```

## Report Timing

- **Pre-Market Report**: 8:30 AM ET (before market open)
- **Post-Market Report**: 4:15 PM ET (after market close)
- Reports only run on trading days (Mon-Fri, excluding holidays)

## Output Files

### Performance Data
- `daily_performance/{date}/performance_{time}.json` - Detailed performance data
- `performance_history.json` - Cumulative history

### Logs
- `performance_tracking.log` - Application logs

## Telegram Report Format

Daily reports include:
- Portfolio values for both bots
- Daily and total P&L
- Win rates and position counts
- Best/worst performing positions
- Combined portfolio summary

## Testing

Test individual components:
```bash
# Test market hours
python Performance_Tracking/market_hours_checker.py

# Test performance tracking
python Performance_Tracking/daily_performance_tracker.py

# Test Telegram sending
python Performance_Tracking/send_performance_update.py

# Test full automation
python Performance_Tracking/automated_performance_tracker.py --run-now
```

## Troubleshooting

### No Data Retrieved
- Check Alpaca API credentials in `.env`
- Verify paper trading accounts have positions/trades
- Check network connectivity

### Telegram Not Sending
- Verify bot token and chat ID
- Ensure you've messaged the bot first
- Check `get_telegram_chat_id.py` to verify chat ID

### Task Scheduler Issues
- Run PowerShell as Administrator
- Check Event Viewer for task errors
- Verify Python path in batch file

## Data Flow

1. **Alpaca API** → Fetch account/position data
2. **Performance Tracker** → Calculate metrics
3. **JSON Storage** → Save performance data
4. **Telegram Reporter** → Format and send message
5. **User** → Receives formatted report on Telegram