# Systemd Installation Guide - Pre-Market Report Generator

This guide explains how to set up automated daily execution of the pre-market report generator using systemd on Linux systems.

## Overview

The systemd configuration will:
- Run the pre-market report generator daily at 6:00 PM ET (18:00)
- Execute Monday through Friday only (skip weekends)
- Log output to systemd journal
- Automatically restart on system boot
- Use timezone America/New_York for ET scheduling

## Prerequisites

1. **Linux system with systemd** (Ubuntu 16.04+, Debian 8+, CentOS 7+, Fedora, etc.)
2. **Python 3.8+** installed at `/usr/bin/python3`
3. **Project directory** set up with all dependencies installed
4. **.env file** configured with API keys (see below)
5. **sudo/root access** for systemd configuration

## Step 1: Prepare Your Environment

### 1.1 Update Service File Paths

Edit `premarket-report.service` and replace the following placeholders:

```bash
# Change this line:
User=trader

# To your actual Linux username:
User=yourusername
```

```bash
# Change these paths:
WorkingDirectory=/home/trader/ai-stock-trading-bot
EnvironmentFile=/home/trader/ai-stock-trading-bot/.env
ExecStart=/usr/bin/python3 /home/trader/ai-stock-trading-bot/daily_premarket_report.py

# To your actual paths:
WorkingDirectory=/home/yourusername/ai-stock-trading-bot
EnvironmentFile=/home/yourusername/ai-stock-trading-bot/.env
ExecStart=/usr/bin/python3 /home/yourusername/ai-stock-trading-bot/daily_premarket_report.py
```

### 1.2 Verify Python Path

Check your Python 3 installation location:

```bash
which python3
```

If the output is not `/usr/bin/python3`, update the `ExecStart` line in the service file to match your actual Python path.

### 1.3 Set Up .env File

Ensure your `.env` file exists in the project root with all required API keys:

```bash
# Required API keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret_key
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Optional: Email notifications
EMAIL_ENABLED=true
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_RECIPIENT=recipient@example.com

# Optional: Webhook notifications
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
DISCORD_WEBHOOK=https://discord.com/api/webhooks/YOUR/WEBHOOK/URL
```

**Important:** Ensure `.env` file permissions are secure:
```bash
chmod 600 ~/.../ai-stock-trading-bot/.env
```

### 1.4 Test Manual Execution

Before setting up systemd, verify the script runs correctly:

```bash
cd /home/yourusername/ai-stock-trading-bot
python3 daily_premarket_report.py --test
```

You should see:
- Report generated successfully
- Files saved to `reports/premarket/`
- No errors in output

## Step 2: Install Systemd Files

### 2.1 Copy Files to Systemd Directory

```bash
# Copy service file
sudo cp systemd/premarket-report.service /etc/systemd/system/

# Copy timer file
sudo cp systemd/premarket-report.timer /etc/systemd/system/
```

### 2.2 Set Correct Permissions

```bash
sudo chmod 644 /etc/systemd/system/premarket-report.service
sudo chmod 644 /etc/systemd/system/premarket-report.timer
```

### 2.3 Reload Systemd Configuration

```bash
sudo systemctl daemon-reload
```

## Step 3: Enable and Start Timer

### 3.1 Enable Timer (Start on Boot)

```bash
sudo systemctl enable premarket-report.timer
```

Expected output:
```
Created symlink /etc/systemd/system/timers.target.wants/premarket-report.timer → /etc/systemd/system/premarket-report.timer.
```

### 3.2 Start Timer Immediately

```bash
sudo systemctl start premarket-report.timer
```

### 3.3 Verify Timer Status

```bash
sudo systemctl status premarket-report.timer
```

Expected output:
```
● premarket-report.timer - Daily Pre-Market Trading Report Generator
     Loaded: loaded (/etc/systemd/system/premarket-report.timer; enabled; vendor preset: enabled)
     Active: active (waiting) since Mon 2025-10-13 17:45:00 EDT; 5s ago
    Trigger: Mon 2025-10-14 18:00:00 EDT; 24h 14min left
   Triggers: ● premarket-report.service
```

### 3.4 List Next Scheduled Runs

```bash
systemctl list-timers premarket-report.timer
```

Expected output:
```
NEXT                        LEFT          LAST PASSED UNIT                      ACTIVATES
Mon 2025-10-14 18:00:00 EDT 24h 14min left n/a  n/a    premarket-report.timer    premarket-report.service
```

## Step 4: Testing and Verification

### 4.1 Manual Test Run

Trigger the service manually to test:

```bash
sudo systemctl start premarket-report.service
```

### 4.2 Check Service Status

```bash
sudo systemctl status premarket-report.service
```

Expected output (after successful run):
```
● premarket-report.service - Pre-Market Trading Report Generation Service
     Loaded: loaded (/etc/systemd/system/premarket-report.service; static)
     Active: inactive (dead) since Mon 2025-10-13 17:45:30 EDT; 5s ago
TriggeredBy: ● premarket-report.timer
    Process: 12345 ExecStart=/usr/bin/python3 /home/trader/ai-stock-trading-bot/daily_premarket_report.py (code=exited, status=0/SUCCESS)
   Main PID: 12345 (code=exited, status=0/SUCCESS)
```

### 4.3 View Service Logs

```bash
# View recent logs
sudo journalctl -u premarket-report.service -n 50

# Follow logs in real-time
sudo journalctl -u premarket-report.service -f

# View logs since today
sudo journalctl -u premarket-report.service --since today

# View logs with timestamps
sudo journalctl -u premarket-report.service -o short-iso
```

### 4.4 Verify Report Files

Check that reports are being generated:

```bash
ls -lh /home/yourusername/ai-stock-trading-bot/reports/premarket/
```

You should see:
```
premarket_report_2025-10-14.md
premarket_metadata_2025-10-14.json
latest.md
```

## Step 5: Managing the Service

### Common Commands

```bash
# Stop the timer
sudo systemctl stop premarket-report.timer

# Disable the timer (won't start on boot)
sudo systemctl disable premarket-report.timer

# Restart the timer (after configuration changes)
sudo systemctl restart premarket-report.timer

# View timer details
sudo systemctl show premarket-report.timer

# View service details
sudo systemctl show premarket-report.service
```

### Updating Configuration

If you modify the service or timer files:

```bash
# 1. Copy updated files
sudo cp systemd/premarket-report.* /etc/systemd/system/

# 2. Reload systemd
sudo systemctl daemon-reload

# 3. Restart timer
sudo systemctl restart premarket-report.timer

# 4. Verify changes
sudo systemctl status premarket-report.timer
```

## Troubleshooting

### Timer Not Triggering

**Check timer status:**
```bash
systemctl list-timers --all | grep premarket
```

**Verify timer is enabled:**
```bash
systemctl is-enabled premarket-report.timer
```

If not enabled, run:
```bash
sudo systemctl enable premarket-report.timer
sudo systemctl start premarket-report.timer
```

### Service Failing

**Check service logs:**
```bash
sudo journalctl -u premarket-report.service -n 100 --no-pager
```

**Common issues:**

1. **Python not found:**
   - Error: `Failed to execute command: No such file or directory`
   - Solution: Update `ExecStart` with correct Python path

2. **Permission denied:**
   - Error: `Permission denied: '.env'`
   - Solution: Fix file permissions or User in service file

3. **API key errors:**
   - Error: `ANTHROPIC_API_KEY not set`
   - Solution: Verify `.env` file exists and `EnvironmentFile` path is correct

4. **Import errors:**
   - Error: `ModuleNotFoundError: No module named 'anthropic'`
   - Solution: Install dependencies in system Python or use virtualenv

### Using Virtual Environment

If you use a Python virtual environment:

**Update service file:**
```ini
[Service]
# ... other settings ...
ExecStart=/home/yourusername/ai-stock-trading-bot/venv/bin/python3 /home/yourusername/ai-stock-trading-bot/daily_premarket_report.py
```

### Timezone Issues

**Verify timezone setting:**
```bash
timedatectl
```

**Check if timer uses correct timezone:**
```bash
systemctl show premarket-report.timer | grep OnCalendar
```

Should show: `OnCalendar=Mon-Fri *-*-* 18:00:00`

**To change timezone in service (if needed):**
```ini
Environment='TZ=America/New_York'
```

### Email/Webhook Not Working

**Check environment variables are loaded:**
```bash
# Run service manually with verbose output
sudo -u yourusername bash -c 'cd /home/yourusername/ai-stock-trading-bot && source .env && python3 daily_premarket_report.py'
```

**Verify .env file format:**
- No spaces around `=`
- No quotes around values (unless value contains spaces)
- One variable per line

## Schedule Details

### Current Schedule

- **Frequency:** Monday through Friday (weekdays only)
- **Time:** 18:00 (6:00 PM) Eastern Time (ET)
- **Timezone:** America/New_York
- **Persistence:** Yes (will run missed executions after system downtime)

### Modifying the Schedule

Edit the timer file and change `OnCalendar` line:

```bash
# Examples:
OnCalendar=Mon-Fri *-*-* 17:30:00    # 5:30 PM ET
OnCalendar=*-*-* 18:00:00            # 6:00 PM daily (including weekends)
OnCalendar=Mon,Wed,Fri *-*-* 18:00:00 # Monday, Wednesday, Friday only
```

After changes:
```bash
sudo systemctl daemon-reload
sudo systemctl restart premarket-report.timer
```

### Testing Schedule

To test if the timer will trigger at expected time:

```bash
# Check next trigger time
systemctl status premarket-report.timer | grep Trigger

# Manually trigger for testing
sudo systemctl start premarket-report.service

# View execution history
sudo journalctl -u premarket-report.service --since "1 week ago"
```

## Monitoring and Logs

### View Recent Executions

```bash
# Last 10 executions
sudo journalctl -u premarket-report.service -n 10

# Today's executions
sudo journalctl -u premarket-report.service --since today

# Specific date range
sudo journalctl -u premarket-report.service --since "2025-10-01" --until "2025-10-15"
```

### Export Logs to File

```bash
# Export last 7 days
sudo journalctl -u premarket-report.service --since "7 days ago" > /tmp/premarket-logs.txt

# Export with JSON format
sudo journalctl -u premarket-report.service -o json > /tmp/premarket-logs.json
```

### Set Up Log Rotation

Systemd automatically handles log rotation, but you can configure limits:

```bash
# Edit journald configuration
sudo nano /etc/systemd/journald.conf

# Add limits (example):
SystemMaxUse=1G
SystemMaxFileSize=100M
```

Then restart journald:
```bash
sudo systemctl restart systemd-journald
```

## Uninstallation

To completely remove the systemd configuration:

```bash
# 1. Stop and disable timer
sudo systemctl stop premarket-report.timer
sudo systemctl disable premarket-report.timer

# 2. Remove systemd files
sudo rm /etc/systemd/system/premarket-report.service
sudo rm /etc/systemd/system/premarket-report.timer

# 3. Reload systemd
sudo systemctl daemon-reload

# 4. Reset failed states (if any)
sudo systemctl reset-failed
```

## Additional Notes

### Security Considerations

1. **File Permissions:**
   - `.env` file should be readable only by service user: `chmod 600 .env`
   - Service files should be owned by root: `sudo chown root:root /etc/systemd/system/premarket-report.*`

2. **API Keys:**
   - Never commit `.env` file to git
   - Use restrictive file permissions on `.env`
   - Regularly rotate API keys

3. **User Isolation:**
   - Run service as non-root user (specified in `User=` directive)
   - Consider creating dedicated service user: `sudo useradd -r -s /bin/false trader`

### Production Recommendations

1. **Set up monitoring alerts** for service failures:
   ```bash
   # Example: Email on failure (requires mail utility)
   [Unit]
   OnFailure=status-email@%n.service
   ```

2. **Enable persistent logging:**
   ```bash
   sudo mkdir -p /var/log/journal
   sudo systemd-tmpfiles --create --prefix /var/log/journal
   ```

3. **Set resource limits** in service file:
   ```ini
   [Service]
   MemoryLimit=1G
   CPUQuota=50%
   ```

4. **Add restart policy** for failures:
   ```ini
   [Service]
   Restart=on-failure
   RestartSec=5min
   ```

## Support

For issues with:
- **Systemd configuration:** Check systemd documentation (`man systemd.service`, `man systemd.timer`)
- **Report generation:** See main README.md troubleshooting section
- **Notifications:** See README.md email/Slack/Discord setup sections

## Summary

After following this guide, you should have:
- ✅ Systemd timer running and enabled
- ✅ Daily execution at 6:00 PM ET (Mon-Fri)
- ✅ Logs viewable with `journalctl`
- ✅ Reports generated in `reports/premarket/`
- ✅ Notifications sent (if configured)

To verify everything is working:
```bash
sudo systemctl status premarket-report.timer
sudo systemctl list-timers premarket-report.timer
sudo journalctl -u premarket-report.service -f
```

---

**Version:** 1.0.0
**Last Updated:** October 13, 2025
**Tested On:** Ubuntu 20.04 LTS, Ubuntu 22.04 LTS, Debian 11, CentOS 8
