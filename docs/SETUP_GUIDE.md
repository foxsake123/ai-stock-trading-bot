# AI Trading Bot - Setup Guide
**Version**: 2.0.0
**Last Updated**: October 23, 2025

## Overview

The interactive setup script (`scripts/setup.py`) provides a guided installation process for the AI Trading Bot. It handles:

✅ System requirements verification
✅ Directory structure creation
✅ Dependency installation
✅ Environment configuration
✅ API key setup
✅ Initial watchlist creation
✅ Logging system initialization
✅ API connection testing
✅ Automation setup (optional)
✅ Comprehensive health check

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Interactive Setup](#interactive-setup)
4. [Setup Steps Explained](#setup-steps-explained)
5. [Configuration Options](#configuration-options)
6. [Troubleshooting](#troubleshooting)
7. [Manual Setup](#manual-setup)
8. [Next Steps](#next-steps)

---

## Quick Start

### Run the Interactive Setup

```bash
# Navigate to project directory
cd ai-stock-trading-bot

# Run setup script
python scripts/setup.py
```

The script will guide you through the complete setup process with interactive prompts.

### What to Prepare

Before running setup, have the following ready:

1. **Anthropic API Key** - Get from https://console.anthropic.com/settings/keys
2. **Alpaca API Keys** - Get from https://app.alpaca.markets/paper/dashboard/overview
3. **Financial Datasets API Key** - Get from https://financialdatasets.ai
4. **Telegram Bot Token** (optional) - Create with @BotFather on Telegram
5. **Email SMTP credentials** (optional) - For email notifications

---

## Prerequisites

### System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| Python | 3.9+ | 3.11+ |
| RAM | 2 GB | 4 GB+ |
| Disk Space | 1 GB free | 5 GB+ free |
| OS | Windows/Linux/macOS | Linux Ubuntu 22.04+ |
| Internet | Required | High-speed |

### Required Software

- **Python 3.9+**: Download from https://www.python.org/downloads/
- **pip**: Usually included with Python
- **git** (optional): For version control

### Verify Python Installation

```bash
python --version
# Should output: Python 3.9.x or higher

pip --version
# Should output: pip 21.x or higher
```

---

## Interactive Setup

The setup script uses an interactive command-line interface with colored output for easy navigation.

### Step-by-Step Process

#### 1. Welcome Screen

```
================================================================================
              AI TRADING BOT - INTERACTIVE SETUP
================================================================================
Welcome! This script will guide you through setting up the AI Trading Bot.
Platform: Windows | Python: 3.11.0

? Ready to begin setup? [Y/n]:
```

Press **Enter** to continue or **n** to cancel.

#### 2. System Requirements Check

```
[1/10] Checking System Requirements
────────────────────────────────────────────────────────────────────────────────
  Running: Checking pip... ✓
  Running: Checking git... ✓
  Testing network connectivity... ✓
✓ Python version: 3.11.0
✓ Git: git version 2.40.0
✓ Disk space: 45.2 GB free
```

The script automatically verifies:
- Python version (3.9+ required)
- pip availability
- git installation (optional)
- Disk space (warns if <1 GB)
- Network connectivity

#### 3. Directory Structure Creation

```
[2/10] Creating Directory Structure
────────────────────────────────────────────────────────────────────────────────
✓ Created 25 directories
ℹ Total directories: 42
```

Creates all required directories for:
- Data storage (`data/cache`, `data/database`)
- Logs (`logs/app`, `logs/trades`, `logs/errors`)
- Reports (`reports/premarket`, `reports/execution`)
- Configuration (`configs/`)
- Scripts and source code

#### 4. Dependency Installation

```
[3/10] Installing Dependencies
────────────────────────────────────────────────────────────────────────────────
? Install Python dependencies from requirements.txt? [Y/n]:

ℹ This may take a few minutes...
  Running: Upgrading pip... ✓
  Running: Installing requirements... ✓
✓ Dependencies installed successfully
```

Installs all required Python packages from `requirements.txt`.

**Tip**: Answer **Yes** unless you've already installed dependencies manually.

#### 5. Environment Configuration

```
[4/10] Configuring Environment
────────────────────────────────────────────────────────────────────────────────
✓ Created .env from .env.example

▶ API Key Configuration
────────────────────────────────────────────────────────────────────────────────

ℹ 🤖 Anthropic API Key (Required for Claude Deep Research)
  Get your key at: https://console.anthropic.com/settings/keys
? Enter Anthropic API key: sk-ant-api03-xxxxx

ℹ 📈 Alpaca API Keys (Required for trading execution)
  Get your keys at: https://app.alpaca.markets/paper/dashboard/overview
? Enter Alpaca API key: PKxxxxx
? Enter Alpaca secret key: xxxxx

ℹ 💹 Financial Datasets API Key (Required for market data)
  Get your key at: https://financialdatasets.ai
? Enter Financial Datasets API key: xxxxx

? 📱 Configure Telegram notifications? [Y/n]: y
? Enter Telegram bot token: 123456:ABCxxxxx
? Enter Telegram chat ID: -1001234567890

? 📧 Configure email notifications? [y/N]: n

✓ Configured 5 API keys in .env
```

**Interactive API Key Setup**:
1. **Anthropic** - Required for Claude Deep Research
2. **Alpaca** - Required for paper/live trading
3. **Financial Datasets** - Required for market data
4. **Telegram** - Optional for mobile notifications
5. **Email** - Optional for email alerts

**Security Note**: All API keys are stored in `.env` file which is git-ignored.

#### 6. Portfolio & Strategy Configuration

```
[5/10] Initializing Configuration Files
────────────────────────────────────────────────────────────────────────────────

▶ Portfolio Configuration
────────────────────────────────────────────────────────────────────────────────
? Enter total portfolio size (USD) [200000]: 100000

▶ Strategy Selection
────────────────────────────────────────────────────────────────────────────────
? Enable DEE-BOT (Beta-Neutral, Defensive)? [Y/n]: y
? Enable SHORGAN-BOT (Catalyst-Driven, Aggressive)? [Y/n]: y
? DEE-BOT allocation (% of portfolio) [50]: 60

✓ Updated config.yaml
```

**Portfolio Settings**:
- **Portfolio Size**: Total capital to deploy ($100K-$1M recommended)
- **DEE-BOT**: Beta-neutral, defensive strategy (dividend aristocrats)
- **SHORGAN-BOT**: Catalyst-driven, aggressive strategy (biotech, M&A)
- **Allocation**: % split between strategies (default 50/50)

#### 7. Watchlist Creation

```
[6/10] Creating Initial Watchlists
────────────────────────────────────────────────────────────────────────────────
✓ Created 3 watchlist files
```

Creates default watchlists:
- `dee_bot_defensive.txt` - Defensive stocks (JNJ, PG, KO, etc.)
- `shorgan_bot_catalysts.txt` - Catalyst plays (PTGX, SMMT, VKTX, etc.)
- `sp500_top50.txt` - S&P 500 top 50 by market cap

#### 8. Logging Initialization

```
[7/10] Setting Up Logging
────────────────────────────────────────────────────────────────────────────────
✓ Logging system initialized
✓ Logging test passed
```

Initializes structured logging system with:
- Daily log rotation
- Separate logs for trades, errors, performance
- 30-day retention policy

#### 9. API Connection Tests

```
[8/10] Testing API Connections
────────────────────────────────────────────────────────────────────────────────
  Testing Anthropic API... ✓
  Testing Alpaca API... ✓
  Testing Financial Datasets API... ✓
✓ All 3 API connections successful
```

Validates that all configured API keys work correctly:
- **Anthropic**: Verifies Claude access
- **Alpaca**: Connects to paper trading account
- **Financial Datasets**: Fetches test data (AAPL snapshot)

**If any tests fail**: The script will show the error and ask if you want to continue anyway.

#### 10. Automation Setup (Optional)

```
[9/10] Setting Up Automation (Optional)
────────────────────────────────────────────────────────────────────────────────
? Set up automated daily execution? [y/N]: y

ℹ Setting up Windows Task Scheduler...
⚠ You may be prompted for administrator privileges
  Running: Creating scheduled task... ✓
✓ Task Scheduler configured
ℹ Daily execution scheduled for 6:00 AM ET
```

**Automation Options**:
- **Linux**: Creates systemd service and timer
- **Windows**: Creates Task Scheduler task
- **Scheduling**: Runs daily at 6:00 AM ET (pre-market)

**Tip**: Skip this if you prefer manual execution.

#### 11. Health Check

```
[10/10] Running Health Check
────────────────────────────────────────────────────────────────────────────────
ℹ Running comprehensive health check...

================================================================================
                            SYSTEM HEALTH CHECK
================================================================================
Overall Health: 92.5% 🟢 HEALTHY

System Resources:
  ✓ CPU Usage: 45.2% (threshold: <80%)
  ✓ Memory Usage: 62.1% (threshold: <80%)
  ✓ Disk Usage: 54.8% (threshold: <90%)

API Connections:
  ✓ Financial Datasets API: Connected
  ✓ Alpaca API: Connected
  ✓ Anthropic API: Connected

Directory Structure:
  ✓ All required directories exist

Logs:
  ✓ Log sizes within limits

✓ Health check passed
```

Comprehensive system validation:
- Resource usage (CPU, memory, disk)
- API connectivity
- Directory structure
- Log file sizes
- Recent pipeline execution

#### 12. Setup Complete!

```
================================================================================
                            SETUP COMPLETE! 🎉
================================================================================
✓ Your AI Trading Bot is ready to use!

ℹ Next steps:
  1. Review your configuration in: .env
  2. Check the setup report: setup_report.txt
  3. Start the bot: python scripts/daily_pipeline.py
  4. View the dashboard: python web_dashboard.py

✓ Setup report saved to: setup_report.txt
```

---

## Setup Steps Explained

### Step 1: Check Requirements

**What it does**:
- Verifies Python 3.9+ installed
- Checks pip availability
- Tests git installation (optional)
- Validates disk space (>1 GB free)
- Tests network connectivity

**Why it's important**:
- Prevents installation failures due to missing dependencies
- Ensures system can handle the bot's requirements

### Step 2: Create Directories

**What it does**:
Creates the complete directory structure:

```
ai-stock-trading-bot/
├── data/
│   ├── cache/           # API response caching
│   ├── database/        # SQLite databases
│   └── backups/         # Backup files
├── logs/
│   ├── app/            # Application logs
│   ├── trades/         # Trade execution logs (JSONL)
│   ├── errors/         # Error logs
│   ├── performance/    # Performance metrics (JSONL)
│   └── alerts/         # Alert history
├── reports/
│   ├── premarket/      # Daily research reports
│   ├── execution/      # Trade execution reports
│   ├── performance/    # Performance tracking
│   └── archive/        # Historical reports
├── configs/            # YAML configurations
├── scripts/
│   ├── automation/     # Scheduled scripts
│   ├── monitoring/     # Health monitoring
│   └── emergency/      # Emergency procedures
└── tests/              # Test suite
```

**Why it's important**:
- Organized structure improves maintainability
- Proper separation of data, logs, and code
- Ready for automated execution

### Step 3: Install Dependencies

**What it does**:
- Upgrades pip to latest version
- Installs all packages from `requirements.txt`
- Tracks installed packages for rollback

**Key Dependencies**:
- `anthropic` - Claude AI API
- `alpaca-py` - Alpaca trading API
- `requests` - HTTP requests
- `pandas` - Data manipulation
- `PyYAML` - Configuration parsing
- `python-dotenv` - Environment variables
- `pytz` - Timezone handling

**Why it's important**:
- Ensures all required libraries are available
- Prevents runtime errors due to missing imports

### Step 4: Setup Environment

**What it does**:
- Copies `.env.example` to `.env` if needed
- Interactively prompts for API keys
- Writes secrets to `.env` file
- Never commits `.env` to git (already in `.gitignore`)

**API Keys Required**:
1. **ANTHROPIC_API_KEY** - Claude Deep Research
2. **ALPACA_API_KEY** - Trading execution
3. **ALPACA_SECRET_KEY** - Trading authentication
4. **FINANCIAL_DATASETS_API_KEY** - Market data

**API Keys Optional**:
5. **TELEGRAM_BOT_TOKEN** - Mobile notifications
6. **TELEGRAM_CHAT_ID** - Notification destination
7. **SMTP credentials** - Email notifications

**Why it's important**:
- Secure storage of sensitive credentials
- Easy to update keys without code changes
- Environment-based configuration (dev/staging/prod)

### Step 5: Initialize Configs

**What it does**:
- Updates `configs/config.yaml` with user preferences
- Sets portfolio size and allocation
- Enables/disables trading strategies
- Configures bot-specific settings

**Configuration Examples**:

```yaml
trading:
  portfolio_size: 100000
  bots:
    dee_bot:
      enabled: true
      allocation_pct: 60
    shorgan_bot:
      enabled: true
      allocation_pct: 40
```

**Why it's important**:
- Customizes bot to your trading preferences
- Ensures strategies align with risk tolerance
- Enables/disables features as needed

### Step 6: Create Watchlists

**What it does**:
Creates text files with stock tickers for each strategy:

**DEE-BOT Defensive** (`dee_bot_defensive.txt`):
- Ultra-defensive, high-dividend stocks
- Beta < 0.6 (low correlation to market)
- Examples: JNJ, PG, KO, VZ, DUK

**SHORGAN-BOT Catalysts** (`shorgan_bot_catalysts.txt`):
- High-catalyst biotech and small-caps
- FDA approvals, M&A targets
- Examples: PTGX, SMMT, VKTX, ARQT

**Why it's important**:
- Provides starting point for screening
- Can be customized with your favorite stocks
- Used by automated research generation

### Step 7: Setup Logging

**What it does**:
- Initializes structured logging system
- Creates log directories if needed
- Tests logging functionality
- Configures daily rotation with 30-day retention

**Log Files Created**:
- `logs/app/app_YYYYMMDD.log` - Application logs
- `logs/trades/trades_YYYYMMDD.jsonl` - Trade logs (structured)
- `logs/errors/errors_YYYYMMDD.log` - Error logs
- `logs/performance/performance_YYYYMMDD.jsonl` - Performance metrics

**Why it's important**:
- Audit trail for all trading decisions
- Debugging assistance for errors
- Performance tracking over time
- Regulatory compliance (trade logs)

### Step 8: Test API Connections

**What it does**:
Validates each configured API:

1. **Anthropic API**: Creates test client, verifies key format
2. **Alpaca API**: Connects to account, retrieves account info
3. **Financial Datasets**: Fetches test data (AAPL price snapshot)

**Success Criteria**:
- All API keys valid
- Network connectivity working
- APIs responding successfully

**Why it's important**:
- Prevents runtime failures during trading hours
- Validates API keys before first execution
- Identifies connectivity issues early

### Step 9: Setup Automation

**What it does**:

**Linux (systemd)**:
```bash
sudo cp deployment/systemd/ai-trading-bot.service /etc/systemd/system/
sudo cp deployment/systemd/ai-trading-bot.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ai-trading-bot.timer
sudo systemctl start ai-trading-bot.timer
```

**Windows (Task Scheduler)**:
```batch
schtasks /create /tn "AI Trading - Daily Pipeline" ^
  /tr "python C:\path\to\scripts\daily_pipeline.py" ^
  /sc daily /st 06:00
```

**Schedule**: Daily execution at 6:00 AM ET (pre-market)

**Why it's important**:
- Fully automated operation (hands-free trading)
- Consistent execution timing
- No need to remember to run manually

### Step 10: Run Health Check

**What it does**:
Comprehensive validation of:
- **System Resources**: CPU < 80%, Memory < 80%, Disk < 90%
- **API Connections**: All APIs reachable
- **Directory Structure**: All required directories exist
- **Log Files**: Sizes within limits (<100 MB each)
- **Pipeline Status**: Recent execution detected

**Health Score Calculation**:
```
Score = (Passed Checks Weight / Total Weight) × 100

🟢 HEALTHY: 80-100%
🟡 WARNING: 60-79%
🔴 CRITICAL: 0-59%
```

**Why it's important**:
- Validates entire system is operational
- Identifies issues before first trade
- Baseline for ongoing monitoring

---

## Configuration Options

### Portfolio Size

| Size | Recommended For | Risk Level |
|------|----------------|------------|
| $10K-$50K | Beginners, testing | Low |
| $50K-$200K | Intermediate traders | Medium |
| $200K-$1M | Advanced traders | Medium-High |
| $1M+ | Professional trading | High |

**Default**: $200,000 (split 50/50 between strategies)

### Strategy Selection

#### DEE-BOT (Beta-Neutral Defensive)
- **Goal**: Outperform SPY with lower volatility
- **Target Beta**: 0.4-0.6 (60% less volatile than market)
- **Holdings**: 5-10 ultra-defensive stocks
- **Allocation**: 50-80% recommended
- **Best For**: Risk-averse, steady returns

#### SHORGAN-BOT (Catalyst-Driven Aggressive)
- **Goal**: High returns from binary catalysts
- **Target Beta**: 1.2-2.0 (20-100% more volatile)
- **Holdings**: 10-20 catalyst plays (FDA, M&A, earnings)
- **Allocation**: 20-50% recommended
- **Best For**: Risk-tolerant, high returns

### Notification Preferences

| Channel | Setup Required | Use Case |
|---------|----------------|----------|
| Telegram | Bot token + chat ID | Mobile alerts, instant notifications |
| Email | SMTP credentials | Daily summaries, detailed reports |
| Slack | Webhook URL | Team notifications, workspace integration |
| Discord | Webhook URL | Community sharing, public updates |

**Recommended**: Telegram for instant alerts + Email for daily summaries

---

## Troubleshooting

### Common Issues

#### Issue 1: Python Version Error

**Error**:
```
RuntimeError: Python 3.9+ is required (found 3.8)
```

**Solution**:
```bash
# Check current version
python --version

# Install Python 3.11
# Windows: Download from https://www.python.org/downloads/
# Linux: sudo apt install python3.11
# macOS: brew install python@3.11

# Verify installation
python3.11 --version
```

#### Issue 2: Pip Not Found

**Error**:
```
pip: command not found
```

**Solution**:
```bash
# Linux/macOS
python3 -m ensurepip --upgrade

# Windows
python -m ensurepip --upgrade

# Verify
pip --version
```

#### Issue 3: Permission Denied (Linux)

**Error**:
```
PermissionError: [Errno 13] Permission denied: '/etc/systemd/system/...'
```

**Solution**:
```bash
# Run with sudo for systemd installation
sudo python scripts/setup.py

# Or skip automation setup and configure manually later
```

#### Issue 4: API Connection Test Failed

**Error**:
```
✗ Testing Anthropic API... (401 Unauthorized)
```

**Solutions**:
1. **Verify API Key**: Check for typos, extra spaces
2. **Check API Key Format**:
   - Anthropic: `sk-ant-api03-xxxxx`
   - Alpaca: `PKxxxxx` (key) + secret
   - Financial Datasets: `xxxxx`
3. **Test API Key Manually**:
   ```bash
   curl -H "X-API-KEY: your-key" \
     https://api.financialdatasets.ai/prices/snapshot?ticker=AAPL
   ```
4. **Regenerate API Key**: If key is invalid, create a new one from provider

#### Issue 5: Dependency Installation Timeout

**Error**:
```
TimeoutError: Command timed out
```

**Solution**:
```bash
# Increase timeout and retry
pip install --timeout=300 -r requirements.txt

# Or install dependencies manually
pip install anthropic alpaca-py requests pandas pyyaml python-dotenv pytz
```

#### Issue 6: .env File Not Created

**Error**:
```
FileNotFoundError: .env file not found
```

**Solution**:
```bash
# Create .env manually
cp .env.example .env

# Or create empty .env
touch .env

# Then run setup again
python scripts/setup.py
```

### Rollback on Failure

If setup fails, the script automatically rolls back changes:
- Removes created files
- Removes empty directories
- Shows rollback summary

**Manual Cleanup** (if needed):
```bash
# Remove .env
rm .env

# Remove created directories (if empty)
rm -r logs/ data/ reports/

# Uninstall dependencies
pip uninstall -r requirements.txt -y
```

---

## Manual Setup

If you prefer manual setup over the interactive script:

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create .env File

```bash
cp .env.example .env

# Edit .env with your API keys
nano .env
```

**Required keys**:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
ALPACA_API_KEY=PKxxxxx
ALPACA_SECRET_KEY=xxxxx
FINANCIAL_DATASETS_API_KEY=xxxxx
```

### 3. Create Directories

```bash
mkdir -p data/{cache,database,backups}
mkdir -p logs/{app,trades,errors,performance,alerts}
mkdir -p reports/{premarket,execution,performance,archive}
mkdir -p configs
mkdir -p scripts/emergency
mkdir -p tests/{integration,unit,agents}
```

### 4. Initialize Configuration

```bash
# Copy example configs
cp configs/config.yaml.example configs/config.yaml
cp configs/data_sources.yaml.example configs/data_sources.yaml
cp configs/alerts.yaml.example configs/alerts.yaml

# Edit configs
nano configs/config.yaml
```

### 5. Test Installation

```bash
# Run health check
python scripts/health_check.py

# Generate test report
python scripts/daily_pipeline.py --test
```

---

## Next Steps

### After Setup Completion

1. **Review Configuration**
   ```bash
   # Edit .env if needed
   nano .env

   # Review main config
   cat configs/config.yaml
   ```

2. **Run Test Report**
   ```bash
   # Generate test report (doesn't execute trades)
   python scripts/daily_pipeline.py --test

   # Check output
   cat reports/premarket/latest/claude_research.md
   ```

3. **Start Dashboard**
   ```bash
   # Launch web dashboard
   python web_dashboard.py

   # Open browser to http://localhost:5000
   ```

4. **Check Portfolio Status**
   ```bash
   # View current positions
   python scripts/performance/get_portfolio_status.py
   ```

5. **Run Full Pipeline** (Paper Trading)
   ```bash
   # Generate research and execute trades (paper account)
   python scripts/daily_pipeline.py

   # Monitor execution
   tail -f logs/app/app_$(date +%Y%m%d).log
   ```

### First Week Checklist

- [ ] Day 1: Run test report, verify setup
- [ ] Day 2-7: Run daily pipeline in paper trading
- [ ] Monitor: Check logs daily for errors
- [ ] Review: Portfolio status each evening
- [ ] Adjust: Tune configuration based on results
- [ ] Validate: Ensure 30-day paper trading before live

### Going Live (After 30-Day Validation)

See [LIVE_TRADING_DEPLOYMENT_GUIDE.md](LIVE_TRADING_DEPLOYMENT_GUIDE.md) for:
- 30-day paper trading requirements
- Risk management validation
- Live trading deployment checklist
- Safety mechanisms and kill switches

---

## Additional Resources

- **README.md** - Project overview and quick start
- **UTILS_DOCUMENTATION.md** - Utility functions reference
- **HEALTH_MONITORING.md** - Health check system
- **DEPLOYMENT_SUMMARY.md** - Deployment options comparison
- **BOT_STRATEGIES.md** - Trading strategy documentation

---

**Last Updated**: October 23, 2025
**Version**: 2.0.0
