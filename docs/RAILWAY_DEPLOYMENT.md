# Railway Cloud Deployment Guide
## AI Trading Bot - 24/7 Automation

---

## Overview

Deploy the AI Trading Bot to Railway for automated 24/7 operation without needing your PC on.

**Services to Deploy:**
| Service | Schedule | Time (ET) | Time (UTC) |
|---------|----------|-----------|------------|
| Research | Saturday | 12:00 PM | 17:00 |
| Trades | Mon-Fri | 8:30 AM | 13:30 |
| Execute | Mon-Fri | 9:30 AM | 14:30 |
| Performance | Mon-Fri | 4:30 PM | 21:30 |

---

## Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (recommended)
3. Complete account setup

---

## Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose `foxsake123/ai-stock-trading-bot`
4. Railway will detect the Python project

---

## Step 3: Configure Environment Variables

In Railway dashboard → Project → Variables, add:

### Required API Keys
```
ANTHROPIC_API_KEY=sk-ant-api...
FINANCIAL_DATASETS_API_KEY=...

# DEE-BOT (Paper)
ALPACA_API_KEY_DEE=...
ALPACA_SECRET_KEY_DEE=...

# SHORGAN (Paper)
ALPACA_API_KEY_SHORGAN=...
ALPACA_SECRET_KEY_SHORGAN=...

# SHORGAN (Live)
ALPACA_LIVE_API_KEY_SHORGAN=...
ALPACA_LIVE_SECRET_KEY_SHORGAN=...

# Telegram Notifications
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=7870288896

# Automation Settings
REQUIRE_LIVE_CONFIRMATION=false
```

---

## Step 4: Create Cron Services

Railway requires separate services for each cron job. Create 4 services:

### Service 1: Research (Saturday 12 PM ET)
1. Click **"New Service"** → **"Empty Service"**
2. Name: `trading-research`
3. Settings → Deploy:
   - Start Command: `python railway_cron.py research`
4. Settings → Cron:
   - Schedule: `0 17 * * 6` (17:00 UTC Saturday = 12 PM ET)

### Service 2: Trades (Weekdays 8:30 AM ET)
1. Click **"New Service"** → **"Empty Service"**
2. Name: `trading-trades`
3. Settings → Deploy:
   - Start Command: `python railway_cron.py trades`
4. Settings → Cron:
   - Schedule: `30 13 * * 1-5` (13:30 UTC Mon-Fri = 8:30 AM ET)

### Service 3: Execute (Weekdays 9:30 AM ET)
1. Click **"New Service"** → **"Empty Service"**
2. Name: `trading-execute`
3. Settings → Deploy:
   - Start Command: `python railway_cron.py execute`
4. Settings → Cron:
   - Schedule: `30 14 * * 1-5` (14:30 UTC Mon-Fri = 9:30 AM ET)

### Service 4: Performance (Weekdays 4:30 PM ET)
1. Click **"New Service"** → **"Empty Service"**
2. Name: `trading-performance`
3. Settings → Deploy:
   - Start Command: `python railway_cron.py performance`
4. Settings → Cron:
   - Schedule: `30 21 * * 1-5` (21:30 UTC Mon-Fri = 4:30 PM ET)

---

## Step 5: Link Services to GitHub

For each service:
1. Settings → Source
2. Connect to `foxsake123/ai-stock-trading-bot`
3. Branch: `master`
4. Root Directory: `/` (project root)

---

## Step 6: Share Environment Variables

1. Go to Project Settings → Shared Variables
2. Add all environment variables here
3. Each service will inherit them automatically

---

## Step 7: Deploy & Monitor

1. Click **"Deploy"** on each service
2. Watch logs for any errors
3. Check Telegram for notifications

---

## Cron Schedule Reference

| Expression | Description |
|------------|-------------|
| `0 17 * * 6` | 17:00 UTC every Saturday |
| `30 13 * * 1-5` | 13:30 UTC Mon-Fri |
| `30 14 * * 1-5` | 14:30 UTC Mon-Fri |
| `30 21 * * 1-5` | 21:30 UTC Mon-Fri |

**Note:** Railway uses UTC time. ET = UTC - 5 (or UTC - 4 during DST)

---

## Testing

### Manual Trigger
In Railway dashboard, click **"Run"** on any service to trigger manually.

### Check Logs
Click on a service → Deployments → View Logs

### Verify Telegram
You should receive notifications when each task runs.

---

## Troubleshooting

### Build Fails
- Check `requirements.txt` has all dependencies
- View build logs for missing packages

### Task Fails
- Check environment variables are set
- View runtime logs for error details
- Telegram will send error notifications

### Wrong Times
- Verify cron expressions use UTC
- ET = UTC - 5 (standard) or UTC - 4 (DST)
- Use [crontab.guru](https://crontab.guru) to verify

---

## Costs

Railway Pricing (as of Jan 2026):
- **Hobby Plan**: $5/month includes:
  - 500 execution hours
  - 8GB RAM
  - Cron jobs included

Estimated usage for trading bot:
- ~4 cron jobs × 5-10 min each × 22 trading days = ~15-20 hours/month
- Well within Hobby plan limits

---

## Alternative: Single Service with Sleep

Instead of 4 separate cron services, you can run one always-on service:

```python
# Runs continuously, checks schedule internally
python railway_always_on.py
```

This approach:
- Uses more execution hours
- Simpler to manage
- Single set of logs

---

*Last Updated: January 6, 2026*
