# Intraday Catalyst Monitoring System - Complete Guide

## Overview

The Catalyst Monitoring System provides real-time tracking of market-moving events affecting your trading positions. It monitors FDA decisions, earnings releases, product launches, conference presentations, and breaking news to ensure you never miss a critical catalyst.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  CatalystMonitor (Orchestrator)             │
│  - Coordinates all monitoring components                    │
│  - Manages event lifecycle (scheduled → occurred)           │
│  - Triggers alerts based on priority                        │
└──────────┬──────────────┬──────────────┬────────────────────┘
           │              │              │
           ▼              ▼              ▼
    ┌──────────┐   ┌─────────────┐   ┌──────────────┐
    │ News     │   │ Event       │   │ Catalyst     │
    │ Scanner  │   │ Calendar    │   │ Alerts       │
    └──────────┘   └─────────────┘   └──────────────┘

NewsScanner               EventCalendar          CatalystAlerts
- Financial Datasets API  - JSON storage         - Email (SMTP)
- Real-time news          - FDA PDUFA dates      - Slack (webhook)
- Sentiment analysis      - Earnings dates       - Discord (webhook)
- Deduplication          - Reminders (24h, 4h)  - Telegram (Bot API)
```

## Components

### 1. CatalystMonitor (`src/monitors/catalyst_monitor.py`)

**Main orchestrator** that coordinates all monitoring activities.

#### Key Features:
- **Market Hours Detection**: Only monitors during market hours (9:30 AM - 4:00 PM ET)
- **Pre-market/After-hours Support**: Optional extended hours monitoring
- **Event Lifecycle Management**: Tracks events from scheduled → occurred
- **Priority Classification**: Automatically assigns CRITICAL/HIGH/MEDIUM/LOW
- **Callback System**: Notifies registered callbacks when events occur

#### Usage:
```python
from src.monitors.catalyst_monitor import CatalystMonitor, CatalystType, CatalystPriority
from src.monitors.news_scanner import NewsScanner
from src.monitors.event_calendar import EventCalendar
from src.alerts.catalyst_alerts import CatalystAlerts

# Initialize components
news_scanner = NewsScanner(api_key="your_fd_api_key")
event_calendar = EventCalendar(storage_file="data/event_calendar.json")
alert_system = CatalystAlerts(primary_channel='email')

# Create monitor
monitor = CatalystMonitor(
    news_scanner=news_scanner,
    event_calendar=event_calendar,
    alert_system=alert_system,
    check_interval=300,  # Check every 5 minutes
    enable_premarket=True,
    enable_afterhours=True
)

# Add tickers to monitor
monitor.add_monitored_tickers(['PTGX', 'SMMT', 'VKTX', 'AAPL'])

# Register callback for events
def on_catalyst_event(event):
    print(f"Catalyst detected: {event.ticker} - {event.title}")
    print(f"Priority: {event.priority.value}")
    print(f"Sentiment: {event.sentiment}")

monitor.register_callback(on_catalyst_event)

# Start monitoring (async)
await monitor.start()

# Stop monitoring
await monitor.stop()
```

#### Priority Levels:
- **CRITICAL**: Immediate action required (FDA approvals, M&A announcements)
- **HIGH**: Review needed within 1 hour (earnings beats, analyst upgrades)
- **MEDIUM**: Awareness within day (conference presentations, partnerships)
- **LOW**: Logged only (routine announcements)

---

### 2. NewsScanner (`src/monitors/news_scanner.py`)

**Real-time news monitoring** from Financial Datasets API.

#### Key Features:
- **Breaking News Detection**: Scans news every 5 minutes
- **Sentiment Analysis**: Scores news from -1.0 (bearish) to 1.0 (bullish)
- **Relevance Scoring**: Filters high-relevance news (0.7+)
- **Deduplication**: Prevents duplicate alerts for same headline
- **Caching**: 5-minute TTL cache to reduce API calls

#### Usage:
```python
from src.monitors.news_scanner import NewsScanner

scanner = NewsScanner(
    api_key="your_fd_api_key",
    cache_minutes=5,
    max_retries=3
)

# Scan recent news for multiple tickers
news = await scanner.scan_recent_news(
    tickers=['PTGX', 'SMMT'],
    minutes_back=60
)

for item in news:
    print(f"{item['ticker']}: {item['headline']}")
    print(f"Sentiment: {item['sentiment']} ({item['sentiment_score']})")
    print(f"Relevance: {item['relevance_score']}")

# Get breaking news only (high relevance + strong sentiment)
breaking = await scanner.get_breaking_news(
    tickers=['PTGX'],
    minutes_back=15,
    min_relevance=0.7
)

# Analyze sentiment changes over time
sentiment_analysis = await scanner.get_sentiment_changes(
    ticker='PTGX',
    hours_back=24
)

print(f"Average sentiment: {sentiment_analysis['avg_sentiment']}")
print(f"Trend: {sentiment_analysis['sentiment_trend']}")  # IMPROVING, DECLINING, STABLE
print(f"Article count: {sentiment_analysis['article_count']}")
```

#### API Integration:
- **Endpoint**: `https://api.financialdatasets.ai/news`
- **Rate Limiting**: Automatic backoff on 429 errors
- **Timeout**: 10-second timeout per request
- **Retry Logic**: 3 attempts with exponential backoff

---

### 3. EventCalendar (`src/monitors/event_calendar.py`)

**Persistent calendar** for scheduled catalyst events.

#### Key Features:
- **JSON Storage**: Persistent storage in `data/event_calendar.json`
- **Multiple Event Types**: FDA, earnings, launches, conferences
- **Reminder System**: Configurable reminders (24h, 4h, 1h before)
- **Deduplication**: Prevents duplicate scheduled events
- **Export**: JSON and CSV export support

#### Usage:
```python
from src.monitors.event_calendar import EventCalendar
from datetime import datetime, timedelta

calendar = EventCalendar(
    storage_file="data/event_calendar.json",
    reminder_hours=[24, 4, 1]  # Reminders at 24h, 4h, 1h before
)

# Add FDA PDUFA date
calendar.add_fda_event(
    ticker="PTGX",
    pdufa_date=datetime(2025, 11, 15, 16, 0),  # 4 PM ET
    drug_name="Afamitresgene Autoleucel",
    indication="Relapsed/Refractory DLBCL"
)

# Add earnings release
calendar.add_earnings_event(
    ticker="AAPL",
    earnings_date=datetime(2025, 11, 1, 16, 0),  # After market close
    quarter="Q4",
    fiscal_year=2025
)

# Add product launch
calendar.add_product_launch(
    ticker="TSLA",
    launch_date=datetime(2025, 12, 1, 10, 0),
    product_name="Model 3 Refresh",
    description="Updated Model 3 with new features"
)

# Add conference presentation
calendar.add_conference_presentation(
    ticker="VKTX",
    presentation_date=datetime(2025, 11, 10, 9, 30),
    conference_name="American Heart Association 2025",
    location="Chicago, IL",
    presenters=["CEO", "Chief Medical Officer"]
)

# Get upcoming events
upcoming = await calendar.get_upcoming_events(
    tickers=['PTGX', 'AAPL'],
    hours_ahead=24,
    event_types=['FDA_DECISION', 'EARNINGS_RELEASE']
)

# Get events needing reminders
reminders = calendar.get_events_needing_reminder()
for event in reminders:
    print(f"Reminder: {event.ticker} - {event.title}")
    print(f"Scheduled: {event.scheduled_time}")
    calendar.mark_reminder_sent(event)

# Clear past events
removed = calendar.clear_past_events(days_ago=7)
print(f"Removed {removed} past events")

# Export calendar
calendar.export_calendar("calendar_backup.json", format='json')
calendar.export_calendar("calendar_backup.csv", format='csv')
```

---

### 4. CatalystAlerts (`src/alerts/catalyst_alerts.py`)

**Multi-channel notification system** with priority-based routing.

#### Key Features:
- **4 Channels**: Email, Slack, Discord, Telegram
- **Priority Routing**: CRITICAL → all channels, HIGH → email + primary, etc.
- **Rich Formatting**: HTML emails, Slack blocks, Discord embeds
- **Alert History**: Tracks last 1000 alerts
- **Statistics**: Alert counts by priority, ticker, channel

#### Usage:
```python
from src.alerts.catalyst_alerts import CatalystAlerts

# Configure email
email_config = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'your_email@gmail.com',
    'password': 'your_app_password',
    'from_email': 'your_email@gmail.com',
    'to_emails': ['recipient@gmail.com']
}

# Configure Telegram
telegram_config = {
    'bot_token': 'YOUR_BOT_TOKEN',
    'chat_id': 'YOUR_CHAT_ID'
}

alerts = CatalystAlerts(
    email_config=email_config,
    slack_webhook="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    discord_webhook="https://discord.com/api/webhooks/YOUR/WEBHOOK",
    telegram_config=telegram_config,
    primary_channel='telegram'  # Default channel for MEDIUM priority
)

# Send catalyst alert (automatically routes based on priority)
await alerts.send_catalyst_alert(catalyst_event)

# Get alert statistics
stats = alerts.get_alert_stats()
print(f"Total alerts: {stats['total_alerts']}")
print(f"By priority: {stats['by_priority']}")
print(f"By ticker: {stats['by_ticker']}")
print(f"Recent alerts: {stats['recent_alerts']}")
```

#### Priority Routing Logic:
| Priority  | Channels                    | Use Case                          |
|-----------|----------------------------|-----------------------------------|
| CRITICAL  | Email + Slack + Discord + Telegram | FDA approval, M&A announcement    |
| HIGH      | Email + Primary channel    | Earnings beat, analyst upgrade    |
| MEDIUM    | Primary channel only       | Conference presentation           |
| LOW       | Logged only (no alerts)    | Routine announcement              |

---

## Complete Integration Example

### Real-World Setup for Trading Bot

```python
import asyncio
from datetime import datetime
from src.monitors.catalyst_monitor import CatalystMonitor, CatalystEvent
from src.monitors.news_scanner import NewsScanner
from src.monitors.event_calendar import EventCalendar
from src.alerts.catalyst_alerts import CatalystAlerts

async def setup_catalyst_monitoring():
    """Complete setup for catalyst monitoring"""

    # 1. Initialize NewsScanner
    news_scanner = NewsScanner(
        api_key=os.getenv('FINANCIAL_DATASETS_API_KEY'),
        cache_minutes=5,
        max_retries=3
    )

    # 2. Initialize EventCalendar
    event_calendar = EventCalendar(
        storage_file="data/event_calendar.json",
        reminder_hours=[24, 4, 1]
    )

    # 3. Initialize CatalystAlerts
    alert_system = CatalystAlerts(
        email_config={
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': os.getenv('EMAIL_USERNAME'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'from_email': os.getenv('EMAIL_FROM'),
            'to_emails': os.getenv('EMAIL_TO').split(',')
        },
        telegram_config={
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
            'chat_id': os.getenv('TELEGRAM_CHAT_ID')
        },
        primary_channel='telegram'
    )

    # 4. Initialize CatalystMonitor
    monitor = CatalystMonitor(
        news_scanner=news_scanner,
        event_calendar=event_calendar,
        alert_system=alert_system,
        check_interval=300,  # 5 minutes
        market_open_hour=9,
        market_close_hour=16,
        enable_premarket=True,
        enable_afterhours=True
    )

    # 5. Add your positions to monitoring
    positions = ['PTGX', 'SMMT', 'VKTX', 'GKOS', 'SNDX', 'RKLB', 'ACAD']
    monitor.add_monitored_tickers(positions)

    # 6. Add known upcoming catalysts
    event_calendar.add_fda_event(
        ticker="GKOS",
        pdufa_date=datetime(2025, 10, 20, 16, 0),
        drug_name="Elafibranor",
        indication="Primary Biliary Cholangitis"
    )

    event_calendar.add_fda_event(
        ticker="SNDX",
        pdufa_date=datetime(2025, 10, 25, 16, 0),
        drug_name="Axatilimab",
        indication="Chronic GVHD"
    )

    # 7. Register callback for position adjustments
    def on_catalyst_event(event: CatalystEvent):
        """Handle catalyst events with position adjustments"""
        print(f"\n{'='*60}")
        print(f"CATALYST ALERT: {event.ticker}")
        print(f"Type: {event.catalyst_type.value}")
        print(f"Priority: {event.priority.value}")
        print(f"Title: {event.title}")
        print(f"Description: {event.description}")
        print(f"Sentiment: {event.sentiment}")
        print(f"{'='*60}\n")

        # CRITICAL: Immediate action required
        if event.priority.value == 'CRITICAL':
            if event.sentiment == 'POSITIVE':
                print(f"ACTION: Consider adding to {event.ticker} position")
            elif event.sentiment == 'NEGATIVE':
                print(f"ACTION: Consider exiting {event.ticker} position")

        # HIGH: Review within 1 hour
        elif event.priority.value == 'HIGH':
            print(f"ACTION: Review {event.ticker} position within 1 hour")

        # MEDIUM: Monitor
        elif event.priority.value == 'MEDIUM':
            print(f"ACTION: Monitor {event.ticker} for further developments")

    monitor.register_callback(on_catalyst_event)

    # 8. Start monitoring
    print("Starting catalyst monitoring...")
    await monitor.start()

# Run monitoring
if __name__ == '__main__':
    asyncio.run(setup_catalyst_monitoring())
```

---

## Environment Variables

Add to your `.env` file:

```bash
# Financial Datasets API
FINANCIAL_DATASETS_API_KEY=your_fd_api_key_here

# Email (Gmail SMTP)
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient1@gmail.com,recipient2@gmail.com

# Slack (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Discord (optional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/WEBHOOK

# Telegram
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
TELEGRAM_CHAT_ID=YOUR_CHAT_ID
```

---

## Automated Scheduling

### Windows Task Scheduler

Create `scripts/automation/run_catalyst_monitor.bat`:

```batch
@echo off
cd C:\Users\shorg\ai-stock-trading-bot
call venv\Scripts\activate
python scripts/automation/run_catalyst_monitor.py
```

Schedule for market hours:
```batch
schtasks /create /tn "AI Trading - Catalyst Monitor" ^
  /tr "C:\Users\shorg\ai-stock-trading-bot\scripts\automation\run_catalyst_monitor.bat" ^
  /sc daily /st 09:25 /et 16:05 /ri 5 /du 0007:00
```

### Linux systemd

Create `/etc/systemd/system/catalyst-monitor.service`:

```ini
[Unit]
Description=AI Trading Catalyst Monitor
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/home/your_user/ai-stock-trading-bot
ExecStart=/home/your_user/ai-stock-trading-bot/venv/bin/python scripts/automation/run_catalyst_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable catalyst-monitor
sudo systemctl start catalyst-monitor
sudo systemctl status catalyst-monitor
```

---

## Testing

Run the comprehensive test suite:

```bash
# Run all catalyst monitoring tests
pytest tests/test_catalyst_monitor.py -v

# Run with coverage
pytest tests/test_catalyst_monitor.py --cov=src.monitors --cov=src.alerts --cov-report=html

# Run specific test classes
pytest tests/test_catalyst_monitor.py::TestCatalystDetection -v
pytest tests/test_catalyst_monitor.py::TestNewsScanning -v
pytest tests/test_catalyst_monitor.py::TestEventManagement -v
pytest tests/test_catalyst_monitor.py::TestAlertSendingByPriority -v
```

---

## Best Practices

### 1. Position-Specific Monitoring
Only monitor tickers you actually hold:
```python
# Get current positions
positions = alpaca_client.list_positions()
tickers = [p.symbol for p in positions]

# Add to monitoring
monitor.add_monitored_tickers(tickers)
```

### 2. Catalyst Calendar Maintenance
Update calendar weekly with known upcoming events:
```python
# Remove past events weekly
calendar.clear_past_events(days_ago=7)

# Add new PDUFA dates
calendar.add_fda_event(...)
```

### 3. Alert Fatigue Prevention
- Use CRITICAL sparingly (FDA approvals, M&A only)
- Filter LOW priority events (log but don't alert)
- Adjust reminder hours based on your schedule

### 4. API Cost Management
- News scanner uses 5-minute cache (saves API calls)
- Monitor only active positions (not entire watchlist)
- Use Financial Datasets API efficiently (batch requests)

### 5. Testing Before Live Trading
```python
# Test with mock data
monitor = CatalystMonitor(
    news_scanner=MockNewsScanner(),  # Returns test data
    event_calendar=EventCalendar(),
    alert_system=CatalystAlerts(primary_channel='email'),
    check_interval=60  # 1 minute for testing
)
```

---

## Troubleshooting

### Issue: No alerts received
**Check**:
1. Monitor is running (`monitor.is_running == True`)
2. Tickers are added (`monitor.monitored_tickers`)
3. Market hours configured correctly
4. Alert channels configured (email SMTP, Telegram bot token)

### Issue: Duplicate alerts
**Solution**: News scanner deduplicates by headline. If receiving duplicates, check:
- `seen_headlines` cache is working
- Same news from multiple sources

### Issue: Missing catalysts
**Check**:
1. Financial Datasets API key is valid
2. Event calendar has scheduled events
3. `check_interval` isn't too long (recommended: 300 seconds)

### Issue: Alert fatigue (too many alerts)
**Solution**:
- Increase `min_relevance` threshold (0.7 → 0.8)
- Filter by priority (`min_urgency=CatalystUrgency.HIGH`)
- Adjust sentiment threshold (only alert if |sentiment_score| > 0.6)

---

## Performance Considerations

### Memory Usage
- News cache: ~5MB per 100 tickers
- Event calendar: ~1MB per 1000 events
- Alert history: ~500KB per 1000 alerts

### API Calls
- News scanner: 1 call per ticker per 5 minutes
- Financial Datasets API: 50 news items per call
- Daily cost (100 tickers, $49/month plan): ~3000 calls/day

### Response Time
- News scan: <2 seconds per ticker
- Calendar check: <100ms
- Alert sending: <500ms per channel

---

## Future Enhancements

1. **Machine Learning Catalyst Detection**
   - Train model on historical catalyst → price move correlation
   - Predict impact magnitude from news text

2. **Social Media Integration**
   - Monitor Twitter/Reddit for breaking catalyst rumors
   - Track CEO tweet sentiment

3. **Automated Position Adjustments**
   - Auto-increase position on positive CRITICAL catalyst
   - Auto-exit on negative CRITICAL catalyst

4. **Catalyst Backtesting**
   - Analyze historical catalyst → performance correlation
   - Optimize alert thresholds

5. **Multi-Source News Aggregation**
   - Add Bloomberg Terminal API
   - Add Reuters News API
   - Consensus scoring across sources

---

## Contact & Support

For issues or questions:
- GitHub Issues: https://github.com/anthropics/ai-trading-bot/issues
- Documentation: `docs/CATALYST_MONITORING_GUIDE.md`
- Test Suite: `tests/test_catalyst_monitor.py`

---

**Version**: 1.0.0
**Last Updated**: October 23, 2025
**Author**: AI Trading Bot Development Team
