# Systemd Deployment Guide

Complete guide for deploying AI Trading Bot as a systemd service on Linux.

## Quick Start

```bash
# 1. Set timezone to Eastern Time
sudo timedatectl set-timezone America/New_York

# 2. Create log directory
sudo mkdir -p /var/log/trading-bot
sudo chown $USER:$USER /var/log/trading-bot

# 3. Copy systemd files
sudo cp deployment/systemd/trading-bot.service /etc/systemd/system/
sudo cp deployment/systemd/trading-bot.timer /etc/systemd/system/

# 4. Update paths in service file
sudo nano /etc/systemd/system/trading-bot.service
# Edit: WorkingDirectory, ExecStart, User, Group

# 5. Reload systemd
sudo systemctl daemon-reload

# 6. Enable and start timer
sudo systemctl enable trading-bot.timer
sudo systemctl start trading-bot.timer

# 7. Verify
systemctl status trading-bot.timer
systemctl list-timers trading-bot.timer
```

## Files

### trading-bot.service

**Purpose:** Defines how the trading bot runs

**Key Settings:**
- `Type=oneshot` - Runs once and exits
- `WorkingDirectory` - Project directory
- `ExecStart` - Command to execute
- `User/Group` - Run as specific user
- `MemoryLimit=2G` - Maximum 2GB RAM
- `CPUQuota=80%` - Maximum 80% of one CPU
- `Restart=on-failure` - Restart if fails (60s delay)

**Resource Limits:**
```ini
MemoryLimit=2G          # Hard limit: 2GB RAM
MemoryHigh=1800M        # Soft limit: 1.8GB RAM
CPUQuota=80%            # Max 80% of one CPU core
TasksMax=100            # Max 100 processes/threads
LimitNOFILE=4096        # Max 4096 file descriptors
```

**Security Features:**
```ini
PrivateTmp=true         # Isolated /tmp directory
ProtectSystem=strict    # Read-only system files
ProtectHome=read-only   # Read-only home directories
NoNewPrivileges=true    # Cannot elevate privileges
```

### trading-bot.timer

**Purpose:** Schedules when the service runs

**Schedule:**
- Monday through Friday (weekdays)
- 6:00 AM Eastern Time
- Persistent (runs missed timers on boot)

**Key Settings:**
```ini
OnCalendar=Mon..Fri *-*-* 06:00:00    # Weekdays at 6 AM
Persistent=true                        # Run if missed
AccuracySec=5min                       # Allow 5 min delay
```

## Installation Steps

### 1. Prerequisites

```bash
# Check Linux distribution
cat /etc/os-release

# Verify systemd is available
systemctl --version

# Check current timezone
timedatectl
```

### 2. Set Timezone

**Critical:** System must use America/New_York timezone

```bash
# View current timezone
timedatectl

# Set to Eastern Time
sudo timedatectl set-timezone America/New_York

# Verify
timedatectl | grep "Time zone"
# Should show: America/New_York (EST, -0500) or (EDT, -0400)
```

### 3. Create Log Directory

```bash
# Create directory
sudo mkdir -p /var/log/trading-bot

# Set ownership (replace 'trader' with your username)
sudo chown trader:trader /var/log/trading-bot

# Set permissions
sudo chmod 755 /var/log/trading-bot

# Verify
ls -ld /var/log/trading-bot
```

### 4. Update Service File

Edit `/etc/systemd/system/trading-bot.service` after copying:

```bash
sudo nano /etc/systemd/system/trading-bot.service
```

**Update these lines:**

```ini
# Line 55: Your project directory
WorkingDirectory=/home/trader/ai-stock-trading-bot

# Line 56: Path to venv python and script
ExecStart=/home/trader/ai-stock-trading-bot/venv/bin/python /home/trader/ai-stock-trading-bot/scripts/daily_pipeline.py

# Line 59-60: Your username and group
User=trader
Group=trader

# Line 93-96: Writable paths (update if different)
ReadWritePaths=/home/trader/ai-stock-trading-bot/data
ReadWritePaths=/home/trader/ai-stock-trading-bot/logs
ReadWritePaths=/home/trader/ai-stock-trading-bot/reports
ReadWritePaths=/var/log/trading-bot
```

### 5. Install Service Files

```bash
# Copy service file
sudo cp deployment/systemd/trading-bot.service /etc/systemd/system/

# Copy timer file
sudo cp deployment/systemd/trading-bot.timer /etc/systemd/system/

# Set permissions
sudo chmod 644 /etc/systemd/system/trading-bot.service
sudo chmod 644 /etc/systemd/system/trading-bot.timer

# Reload systemd to recognize new files
sudo systemctl daemon-reload
```

### 6. Enable and Start

```bash
# Enable service (start on boot)
sudo systemctl enable trading-bot.service

# Enable timer (start on boot)
sudo systemctl enable trading-bot.timer

# Start timer now
sudo systemctl start trading-bot.timer

# Check status
sudo systemctl status trading-bot.timer
```

### 7. Verify Installation

```bash
# Check timer is active
systemctl status trading-bot.timer

# List all timers (find ours)
systemctl list-timers --all | grep trading

# View next scheduled run
systemctl list-timers trading-bot.timer

# Test schedule syntax
systemd-analyze calendar "Mon..Fri *-*-* 06:00:00"
```

## Management

### Service Commands

```bash
# Manually run service now
sudo systemctl start trading-bot.service

# Stop running service
sudo systemctl stop trading-bot.service

# Restart service
sudo systemctl restart trading-bot.service

# Check service status
sudo systemctl status trading-bot.service

# View service logs
sudo journalctl -u trading-bot.service -f

# View last 100 service log lines
sudo journalctl -u trading-bot.service -n 100
```

### Timer Commands

```bash
# Start timer
sudo systemctl start trading-bot.timer

# Stop timer
sudo systemctl stop trading-bot.timer

# Enable timer (auto-start on boot)
sudo systemctl enable trading-bot.timer

# Disable timer
sudo systemctl disable trading-bot.timer

# Check timer status
sudo systemctl status trading-bot.timer

# List all timers
systemctl list-timers

# View timer logs
sudo journalctl -u trading-bot.timer
```

### Log Files

```bash
# systemd journal (all logs)
sudo journalctl -u trading-bot.service -f

# Pipeline stdout
tail -f /var/log/trading-bot/pipeline.log

# Pipeline stderr (errors)
tail -f /var/log/trading-bot/error.log

# Application logs (from Python)
tail -f /home/trader/ai-stock-trading-bot/logs/app/daily_pipeline_*.log

# All logs combined
tail -f /var/log/trading-bot/*.log
```

## Monitoring

### Check Next Run Time

```bash
# View next scheduled run
systemctl list-timers trading-bot.timer

# Example output:
# NEXT                        LEFT          LAST  PASSED  UNIT
# Fri 2025-10-24 06:00:00 EDT 8h left       n/a   n/a     trading-bot.timer
```

### Check Last Run

```bash
# View last run status
systemctl status trading-bot.service

# View last run logs
sudo journalctl -u trading-bot.service -n 100

# Check if last run succeeded
systemctl show trading-bot.service -p ExecMainStatus
```

### Resource Usage

```bash
# Current memory usage
systemctl status trading-bot.service | grep Memory

# Current CPU usage
systemctl status trading-bot.service | grep CPU

# Detailed resource stats
systemctl show trading-bot.service | grep -E "Memory|CPU|Tasks"
```

## Troubleshooting

### Timer Not Running

**Problem:** Timer doesn't trigger at scheduled time

**Solutions:**

```bash
# 1. Check timer is enabled
systemctl is-enabled trading-bot.timer
# Should show: enabled

# 2. Check timer is active
systemctl is-active trading-bot.timer
# Should show: active

# 3. Check timezone
timedatectl | grep "Time zone"
# Should show: America/New_York

# 4. View timer logs for errors
sudo journalctl -u trading-bot.timer -n 50

# 5. Restart timer
sudo systemctl restart trading-bot.timer
```

### Service Fails to Start

**Problem:** Service exits with error

**Solutions:**

```bash
# 1. Check service logs
sudo journalctl -u trading-bot.service -n 100

# 2. Verify paths in service file
sudo systemctl cat trading-bot.service
# Check WorkingDirectory and ExecStart paths exist

# 3. Test command manually
cd /home/trader/ai-stock-trading-bot
./venv/bin/python scripts/daily_pipeline.py

# 4. Check file permissions
ls -la /home/trader/ai-stock-trading-bot/scripts/daily_pipeline.py
# Should be readable by service user

# 5. Verify user exists
id trader

# 6. Check virtual environment
ls -la /home/trader/ai-stock-trading-bot/venv/bin/python
```

### Permission Denied Errors

**Problem:** Service cannot write to files/directories

**Solutions:**

```bash
# 1. Check log directory ownership
ls -ld /var/log/trading-bot
# Should be owned by service user

# 2. Fix ownership
sudo chown -R trader:trader /var/log/trading-bot

# 3. Check project directory permissions
ls -la /home/trader/ai-stock-trading-bot/
# data/, logs/, reports/ should be writable by user

# 4. Fix project permissions
chown -R trader:trader /home/trader/ai-stock-trading-bot

# 5. Update ReadWritePaths in service file
sudo nano /etc/systemd/system/trading-bot.service
# Add any missing directories to ReadWritePaths
```

### Memory/CPU Limits Hit

**Problem:** Service killed due to resource limits

**Solutions:**

```bash
# 1. Check if OOM (Out of Memory) killed
sudo journalctl -u trading-bot.service | grep -i "oom\|killed\|memory"

# 2. Increase memory limit
sudo nano /etc/systemd/system/trading-bot.service
# Change: MemoryLimit=4G

# 3. Increase CPU quota
# Change: CPUQuota=150%

# 4. Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart trading-bot.service
```

### Timezone Issues

**Problem:** Runs at wrong time

**Solutions:**

```bash
# 1. Check system timezone
timedatectl

# 2. Set to Eastern Time
sudo timedatectl set-timezone America/New_York

# 3. Verify timer schedule
systemd-analyze calendar "Mon..Fri *-*-* 06:00:00"

# 4. Restart timer
sudo systemctl restart trading-bot.timer

# 5. Check next run time
systemctl list-timers trading-bot.timer
```

## Uninstallation

```bash
# 1. Stop and disable timer
sudo systemctl stop trading-bot.timer
sudo systemctl disable trading-bot.timer

# 2. Stop and disable service
sudo systemctl stop trading-bot.service
sudo systemctl disable trading-bot.service

# 3. Remove files
sudo rm /etc/systemd/system/trading-bot.service
sudo rm /etc/systemd/system/trading-bot.timer

# 4. Reload systemd
sudo systemctl daemon-reload

# 5. Reset failed states
sudo systemctl reset-failed

# 6. (Optional) Remove logs
sudo rm -rf /var/log/trading-bot
```

## Advanced Configuration

### Multiple Runs Per Day

Edit timer to run at multiple times:

```ini
# /etc/systemd/system/trading-bot.timer
[Timer]
OnCalendar=Mon..Fri 06:00:00
OnCalendar=Mon..Fri 12:00:00
OnCalendar=Mon..Fri 16:00:00
```

### Email Notifications on Failure

Create `/etc/systemd/system/trading-bot-notify@.service`:

```ini
[Unit]
Description=Trading Bot Failure Notification
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/mail -s "Trading Bot Failed" admin@example.com < /var/log/trading-bot/error.log
```

Add to main service:

```ini
# /etc/systemd/system/trading-bot.service
[Unit]
OnFailure=trading-bot-notify@%n.service
```

### Automatic Log Rotation

Create `/etc/logrotate.d/trading-bot`:

```
/var/log/trading-bot/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 trader trader
}
```

## Best Practices

1. **Always test manually first** before enabling timer
2. **Monitor first week** to ensure schedule works correctly
3. **Set up log rotation** to prevent disk space issues
4. **Use Persistent=true** to catch missed runs
5. **Check logs regularly** for errors
6. **Keep backups** of systemd files before changes
7. **Document customizations** for future reference

## Support

If issues persist:

1. Check application logs: `logs/app/`
2. Check systemd journal: `journalctl -u trading-bot.service`
3. Verify market hours script: `python scripts/monitoring/health_check.py`
4. Test pipeline manually: `python scripts/daily_pipeline.py`
5. Review configuration: `cat configs/config.yaml`
