# Health Monitoring System

**Last Updated:** October 23, 2025
**Version:** 1.0.0

---

## Overview

The AI Trading Bot includes a comprehensive health monitoring system that provides both one-time health checks and continuous monitoring capabilities.

## Components

### 1. Health Check Script (`scripts/health_check.py`)

**Purpose:** One-time comprehensive health validation

**Usage:**
```bash
# Basic health check
python scripts/health_check.py

# Verbose output
python scripts/health_check.py --verbose

# JSON output
python scripts/health_check.py --json

# Save to file
python scripts/health_check.py --output health_report.txt

# Disable critical alerts
python scripts/health_check.py --no-alert
```

**Checks Performed:**

| Category | Check | Weight | Threshold |
|----------|-------|--------|-----------|
| **System Resources** | | | |
| | CPU Usage | 15 | < 80% |
| | Memory Usage | 15 | < 80% |
| | Disk Usage | 20 | < 90% |
| **API Connectivity** | | | |
| | Financial Datasets API | 25 | Connected |
| | Alpaca API | 30 | Connected |
| | Anthropic API | 25 | Connected |
| **Filesystem** | | | |
| | Required Directories | 20 | All exist |
| | Required Files | 20 | All exist |
| | Log File Sizes | 10 | < 100MB each |
| **Pipeline** | | | |
| | Recent Execution | 15 | < 4 hours ago |
| **Database** | | | |
| | PostgreSQL | 10 | Connected (if configured) |
| | Redis | 10 | Connected (if configured) |

**Health Score Calculation:**
```
health_score = (passed_weight / total_weight) * 100
```

**Status Levels:**
- **🟢 HEALTHY** (80-100%): All systems operational
- **🟡 WARNING** (60-79%): Some issues detected
- **🔴 CRITICAL** (0-59%): Immediate attention required

**Exit Codes:**
- `0`: Healthy (score >= 60%)
- `1`: Unhealthy (score < 60%)
- `2`: Critical failure (cannot complete check)

**Example Output:**
```
================================================================================
🟢 SYSTEM HEALTH REPORT
================================================================================
Timestamp: 2025-10-23 14:32:15
Overall Health: 92.5%
Status: HEALTHY

DETAILED CHECKS:
--------------------------------------------------------------------------------
  ✓ CPU Usage                    45.2%                     [< 80.0%]
  ✓ Memory Usage                 62.3% (15.8GB / 25.4GB)  [< 80.0%]
  ✓ Disk Usage                   58.9% (2.3TB / 3.9TB)    [< 90.0%]
  ✓ Financial Datasets API       Connected ✓
  ✓ Alpaca API                   Connected ✓ ($100,234.56)
  ✓ Anthropic API                Connected ✓ (key format valid)
  ✓ Required Directories         4 directories exist ✓
  ✓ Required Files               3 files exist ✓
  ✓ Log File Sizes               Total: 23.4MB ✓
  ✓ Recent Pipeline Execution    Last report: 2.3h ago ✓  [< 4.0h]
  ✓ Database Connectivity        Connected ✓
  ✓ Redis Connectivity           Connected ✓

================================================================================
```

---

### 2. Continuous Health Monitor (`src/monitors/health_monitor.py`)

**Purpose:** Continuous monitoring with metrics exposure

**Usage:**
```bash
# Start with defaults (5-minute checks, port 9090)
python -m src.monitors.health_monitor

# Custom check interval (10 minutes)
python -m src.monitors.health_monitor --interval 600

# Custom metrics port
python -m src.monitors.health_monitor --port 8080

# Debug logging
python -m src.monitors.health_monitor --log-level DEBUG
```

**Features:**
- ✅ Runs health checks on schedule (default: 5 minutes)
- ✅ Exposes HTTP metrics endpoint (Prometheus-compatible)
- ✅ Tracks health history (24 hours)
- ✅ Sends alerts on degraded health
- ✅ Alert cooldown (default: 60 minutes)
- ✅ Automatic recovery detection

**HTTP Endpoints:**

| Endpoint | Description | Format |
|----------|-------------|--------|
| `/metrics` | Prometheus metrics | text/plain |
| `/health` | Current health status | JSON |
| `/history` | Health history (24h) | JSON |

**Example `/metrics` Output:**
```prometheus
# HELP trading_bot_health_score Overall system health score (0-100)
# TYPE trading_bot_health_score gauge
trading_bot_health_score 92.5

# HELP trading_bot_check_passed Individual health check status (1=pass, 0=fail)
# TYPE trading_bot_check_passed gauge
trading_bot_check_passed{check="cpu_usage"} 1
trading_bot_check_passed{check="memory_usage"} 1
trading_bot_check_passed{check="disk_usage"} 1
trading_bot_check_passed{check="financial_datasets_api"} 1
trading_bot_check_passed{check="alpaca_api"} 1

# HELP trading_bot_resource_usage Resource usage percentage
# TYPE trading_bot_resource_usage gauge
trading_bot_resource_usage{resource="cpu"} 45.2
trading_bot_resource_usage{resource="memory"} 62.3
trading_bot_resource_usage{resource="disk"} 58.9

# HELP trading_bot_alerts_sent_total Total alerts sent
# TYPE trading_bot_alerts_sent_total counter
trading_bot_alerts_sent_total 3

# HELP trading_bot_last_check_timestamp Unix timestamp of last health check
# TYPE trading_bot_last_check_timestamp gauge
trading_bot_last_check_timestamp 1729705935.423
```

**Example `/health` Output:**
```json
{
  "status": "HEALTHY",
  "health_score": 92.5,
  "last_check": 1729705935.423,
  "uptime_seconds": 3600.5,
  "checks": [
    {
      "name": "CPU Usage",
      "passed": true,
      "value": "45.2%",
      "threshold": "< 80.0%",
      "weight": 15
    },
    ...
  ],
  "issues": []
}
```

**Configuration:**

```python
MONITOR_CONFIG = {
    'check_interval_seconds': 300,     # 5 minutes
    'metrics_port': 9090,              # HTTP server port
    'history_size': 288,               # 24 hours at 5-min intervals
    'alert_cooldown_minutes': 60,      # 1 hour between alerts
    'degraded_threshold': 70,          # Send warning alerts
    'critical_threshold': 60,          # Send critical alerts
}
```

---

## Integration

### With Docker Compose

Add health monitor service to `docker-compose.yml`:

```yaml
health-monitor:
  container_name: ai-trading-bot-health-monitor
  build:
    context: ../..
    dockerfile: deployment/docker/Dockerfile
  image: ai-trading-bot:latest

  restart: unless-stopped

  command: python -m src.monitors.health_monitor

  ports:
    - "9090:9090"  # Metrics endpoint

  volumes:
    - ../../data:/app/data:ro
    - ../../logs:/app/logs:ro
    - ../../reports:/app/reports:ro

  networks:
    - trading-network

  depends_on:
    - trading-bot
    - redis
    - postgres
```

### With Systemd

Create `/etc/systemd/system/trading-bot-health-monitor.service`:

```ini
[Unit]
Description=AI Trading Bot Health Monitor
After=network.target

[Service]
Type=simple
User=trader
WorkingDirectory=/home/trader/ai-stock-trading-bot
ExecStart=/home/trader/ai-stock-trading-bot/venv/bin/python -m src.monitors.health_monitor
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot-health-monitor
sudo systemctl start trading-bot-health-monitor
```

### With GitHub Actions

Add health check to workflow:

```yaml
- name: Run health check
  run: |
    python scripts/health_check.py --json > health_report.json

- name: Upload health report
  uses: actions/upload-artifact@v4
  with:
    name: health-report
    path: health_report.json
```

---

## Prometheus Integration

### Prometheus Configuration

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'trading-bot'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 60s
```

### Grafana Dashboard

**Key Metrics to Visualize:**

1. **Health Score Over Time**
   ```promql
   trading_bot_health_score
   ```

2. **Resource Usage**
   ```promql
   trading_bot_resource_usage{resource="cpu"}
   trading_bot_resource_usage{resource="memory"}
   trading_bot_resource_usage{resource="disk"}
   ```

3. **Check Success Rate**
   ```promql
   avg(trading_bot_check_passed) * 100
   ```

4. **Alerts Sent**
   ```promql
   rate(trading_bot_alerts_sent_total[1h])
   ```

---

## Alerting

### Alert Conditions

**WARNING Alerts** (Health < 70%):
- Sent via Telegram and Slack
- Cooldown: 60 minutes
- Includes issue details

**CRITICAL Alerts** (Health < 60%):
- Sent via Telegram and Slack
- Cooldown: 60 minutes
- Includes all issues
- Triggers emergency procedures

### Alert Message Format

```
🟡 HEALTH MONITOR ALERT

Status: WARNING
Health Score: 68.5%
Timestamp: 2025-10-23 14:32:15

Issues (3):
  - CPU Usage: 85.2%
  - Memory Usage: 82.3%
  - Recent Pipeline Execution: Last report: 5.2h ago (too old)
```

### Customizing Alerts

Edit `MONITOR_CONFIG` in `src/monitors/health_monitor.py`:

```python
MONITOR_CONFIG = {
    'alert_cooldown_minutes': 30,     # More frequent alerts
    'degraded_threshold': 80,         # Earlier warnings
    'critical_threshold': 70,         # Earlier critical alerts
}
```

---

## Troubleshooting

### Common Issues

**1. Health check fails with import errors**

**Symptom:**
```
ImportError: No module named 'psutil'
```

**Solution:**
```bash
pip install psutil requests python-dotenv
# Optional: redis psycopg2-binary anthropic alpaca-py
```

---

**2. API checks always fail**

**Symptom:**
```
✗ Financial Datasets API    API key not configured
✗ Alpaca API                API keys not configured
```

**Solution:**
```bash
# Ensure .env file exists
cp .env.example configs/.env

# Add your API keys
nano configs/.env
```

---

**3. Metrics endpoint not accessible**

**Symptom:**
```
curl: (7) Failed to connect to localhost port 9090
```

**Solution:**
```bash
# Check if monitor is running
ps aux | grep health_monitor

# Check port is not in use
netstat -tulpn | grep 9090

# Try different port
python -m src.monitors.health_monitor --port 8080
```

---

**4. High false positive alerts**

**Symptom:**
Alerts sent frequently for transient issues

**Solution:**
```python
# Adjust thresholds in health_check.py
THRESHOLDS = {
    'cpu_percent': 90.0,      # Increase from 80%
    'memory_percent': 90.0,   # Increase from 80%
    'pipeline_hours': 6,      # Increase from 4
}
```

---

**5. Database/Redis checks fail**

**Symptom:**
```
✗ Database Connectivity    Error: connection refused
```

**Solution:**
```bash
# Ensure services are running
docker-compose ps postgres redis

# Check DATABASE_URL in .env
echo $DATABASE_URL

# Test connection manually
psql $DATABASE_URL -c "SELECT 1"
```

---

## Best Practices

### Development

```bash
# Run health check before committing
python scripts/health_check.py

# Check specific components
python scripts/health_check.py --verbose | grep "API"

# Save baseline report
python scripts/health_check.py --output baseline_health.txt
```

### Production

```bash
# Run continuous monitor
python -m src.monitors.health_monitor

# Monitor with systemd
sudo systemctl status trading-bot-health-monitor
sudo journalctl -u trading-bot-health-monitor -f

# Check metrics
curl http://localhost:9090/metrics
curl http://localhost:9090/health | jq
```

### Scheduled Health Checks

**Linux/Mac (cron):**
```bash
# Every hour
0 * * * * /path/to/venv/bin/python /path/to/scripts/health_check.py --output /var/log/trading-bot/health_check.log
```

**Windows (Task Scheduler):**
```batch
schtasks /create /tn "Trading Bot Health Check" ^
  /tr "python C:\path\to\scripts\health_check.py" ^
  /sc hourly
```

---

## Maintenance

### Daily

- [ ] Review health score trends
- [ ] Check for new warnings
- [ ] Verify all APIs connected

### Weekly

- [ ] Analyze health history
- [ ] Review alert frequency
- [ ] Optimize thresholds if needed
- [ ] Check log file growth

### Monthly

- [ ] Validate all health checks
- [ ] Update API connection tests
- [ ] Review and adjust thresholds
- [ ] Clean up old health reports

---

## Metrics Reference

### Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `trading_bot_health_score` | gauge | Overall health score (0-100) |
| `trading_bot_check_passed{check="..."}` | gauge | Individual check status (1=pass, 0=fail) |
| `trading_bot_resource_usage{resource="..."}` | gauge | Resource usage % (cpu, memory, disk) |
| `trading_bot_alerts_sent_total` | counter | Total alerts sent |
| `trading_bot_last_check_timestamp` | gauge | Unix timestamp of last check |

### HTTP Endpoints

| Endpoint | Method | Response | Description |
|----------|--------|----------|-------------|
| `/metrics` | GET | text/plain | Prometheus metrics |
| `/health` | GET | application/json | Current health status |
| `/history` | GET | application/json | 24-hour health history |

---

## Advanced Usage

### Custom Health Checks

Add custom checks to `HealthChecker` class:

```python
def check_custom_service(self) -> bool:
    """Check custom service."""
    try:
        # Your check logic
        response = requests.get('http://my-service/health')
        passed = response.status_code == 200

        self.add_check(
            'Custom Service',
            passed,
            'Connected' if passed else 'Failed',
            weight=15
        )

        return passed
    except Exception as e:
        self.add_check('Custom Service', False, str(e), weight=15)
        return False
```

Then call in `run_all_checks()`:
```python
def run_all_checks(self):
    # ... existing checks ...
    self.check_custom_service()
    # ... rest of method ...
```

### Programmatic Usage

```python
from scripts.health_check import HealthChecker

# Create checker
checker = HealthChecker(verbose=True)

# Run checks
health_score, status, issues = checker.run_all_checks()

# Generate report
report = checker.generate_report(health_score, status)

print(report)

# Check specific score
if health_score < 80:
    print(f"WARNING: Health degraded to {health_score}%")
    print(f"Issues: {issues}")
```

---

## Summary

The health monitoring system provides:

✅ **Comprehensive Validation**
- 12+ health checks across system resources, APIs, filesystem, and pipeline
- Weighted scoring system (0-100%)
- Clear status indicators (HEALTHY/WARNING/CRITICAL)

✅ **Continuous Monitoring**
- Scheduled health checks (5-minute default)
- HTTP metrics endpoint (Prometheus-compatible)
- 24-hour health history tracking
- Automatic alerting with cooldown

✅ **Production Ready**
- Integration with Docker, Systemd, GitHub Actions
- Prometheus/Grafana support
- Multi-channel alerting (Telegram, Slack)
- Comprehensive documentation

✅ **Easy to Use**
- Simple CLI for one-time checks
- Background service for continuous monitoring
- JSON/text output formats
- Detailed troubleshooting guides

**Next Steps:**
1. Run initial health check: `python scripts/health_check.py`
2. Start continuous monitor: `python -m src.monitors.health_monitor`
3. Integrate with Prometheus/Grafana
4. Configure alert thresholds
5. Add to production deployment

---

**Version:** 1.0.0
**Last Updated:** October 23, 2025
**Status:** Production-Ready ✅
