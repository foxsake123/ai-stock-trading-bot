#!/usr/bin/env python3
"""
Railway Always-On Scheduler
============================
Runs continuously on Railway and executes tasks at scheduled times.
This replaces the need for Railway's cron feature.

Schedule (ET):
- Mon-Fri 6:00 AM: Research generation
- Mon-Fri 8:30 AM: Trade generation
- Mon-Fri 9:30 AM: Trade execution
- Mon-Fri 4:30 PM: Performance graph

Enhanced with:
- Health monitoring and task tracking
- Retry logic with exponential backoff
- Circuit breakers for API resilience
- Telegram alerting for failures
"""

import os
import sys
import time
import schedule
import logging
from datetime import datetime
from pathlib import Path

# Set up paths - ensure src module is importable
PROJECT_ROOT = Path(__file__).parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))
# Also add explicit path for src module
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
os.environ['PYTHONPATH'] = str(PROJECT_ROOT)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import pytz

# Import core utilities for health monitoring and retry logic
from scripts.core import (
    get_health_monitor,
    anthropic_circuit,
    alpaca_circuit,
    AlertLevel
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ET = pytz.timezone('America/New_York')

# Global health monitor
health_monitor = get_health_monitor()


def get_et_time():
    """Get current time in ET."""
    return datetime.now(ET)


def send_telegram(message: str):
    """Send notification to Telegram."""
    import requests
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if bot_token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)
        except:
            pass


def run_scheduled_task(
    task_name,
    display_name,
    import_path,
    start_emoji,
    alert_level=AlertLevel.HIGH,
    circuit_breaker=None
):
    """
    Run a scheduled task with health monitoring, circuit breaker checks,
    and Telegram notifications.

    Args:
        task_name: Internal name for health tracking (e.g. "research_generation")
        display_name: Human-readable name for logs/messages (e.g. "Research")
        import_path: Dotted module path to import main() from
        start_emoji: Emoji for the start notification
        alert_level: Severity level for failure alerts
        circuit_breaker: Optional circuit breaker to check/update
    """
    logger.info(f"Starting {display_name.lower()}...")
    send_telegram(f"{start_emoji} *Railway* - Starting {display_name.lower()}...")

    try:
        with health_monitor.track_task(task_name) as tracker:
            if circuit_breaker and circuit_breaker.state == "OPEN":
                raise Exception(f"{circuit_breaker.name.title()} circuit breaker is OPEN - too many recent failures")

            # Dynamic import to avoid loading all modules at startup
            import importlib
            module = importlib.import_module(import_path)
            module.main()

            if circuit_breaker:
                circuit_breaker.record_success()
            tracker.add_detail("status", "success")
            send_telegram(f"✅ *Railway* - {display_name} complete!")
            logger.info(f"{display_name} complete!")

    except Exception as e:
        if circuit_breaker:
            try:
                circuit_breaker.record_failure(e)
            except Exception:
                pass
        error_msg = str(e)[:100]
        send_telegram(f"❌ *Railway* - {display_name} failed: {error_msg}")
        logger.error(f"{display_name} failed: {e}")
        health_monitor.send_alert(alert_level, f"{display_name} failed: {error_msg}")


def run_research():
    """Run research generation with health monitoring."""
    run_scheduled_task(
        task_name="research_generation",
        display_name="Research",
        import_path="scripts.automation.daily_claude_research",
        start_emoji="🔬",
        alert_level=AlertLevel.HIGH,
        circuit_breaker=anthropic_circuit,
    )


def run_trades():
    """Run trade generation with health monitoring."""
    run_scheduled_task(
        task_name="trade_generation",
        display_name="Trade generation",
        import_path="scripts.automation.generate_todays_trades_v2",
        start_emoji="📊",
        alert_level=AlertLevel.HIGH,
    )


def run_execute():
    """Run trade execution with health monitoring and circuit breaker."""
    run_scheduled_task(
        task_name="trade_execution",
        display_name="Trade execution",
        import_path="scripts.automation.execute_daily_trades",
        start_emoji="💰",
        alert_level=AlertLevel.CRITICAL,
        circuit_breaker=alpaca_circuit,
    )


def run_performance():
    """Run performance graph update with health monitoring."""
    run_scheduled_task(
        task_name="performance_update",
        display_name="Performance update",
        import_path="scripts.performance.generate_performance_graph",
        start_emoji="📈",
        alert_level=AlertLevel.WARNING,
    )


def heartbeat():
    """Send hourly heartbeat with health status."""
    now = get_et_time()
    if now.hour == 9 and now.minute < 5:  # Only at 9 AM ET
        # Include health status in heartbeat
        health = health_monitor.get_system_health()
        status_emoji = {
            "healthy": "💚",
            "degraded": "💛",
            "unhealthy": "🟠",
            "critical": "🔴"
        }.get(health["overall"], "⚪")

        summary = health["summary"]
        msg = (
            f"💓 *Railway Scheduler* - Running\n"
            f"Time: {now.strftime('%Y-%m-%d %H:%M ET')}\n"
            f"Health: {status_emoji} {health['overall'].upper()}\n"
            f"Tasks: ✅{summary['healthy']} ⚠️{summary['stale']} ❌{summary['failed']}"
        )
        send_telegram(msg)


def run_health_check():
    """Run daily health check and send alert if issues found."""
    health = health_monitor.get_system_health()

    if health["overall"] in ["unhealthy", "critical"]:
        issues_text = "\n".join(health["issues"][:5])
        health_monitor.send_alert(
            AlertLevel.HIGH if health["overall"] == "unhealthy" else AlertLevel.CRITICAL,
            f"Daily Health Check - {health['overall'].upper()}\n\n{issues_text}"
        )


def main():
    """Main scheduler loop with health monitoring."""
    print("=" * 60)
    print("Railway Scheduler Starting (with Health Monitoring)")
    print(f"Current time (ET): {get_et_time()}")
    print("=" * 60)

    # Get initial health status
    health = health_monitor.get_system_health()
    send_telegram(
        f"🚀 *Railway Scheduler* - Service started!\n"
        f"Health: {health['overall'].upper()}\n"
        f"Circuit breakers: Alpaca={alpaca_circuit.state}, Anthropic={anthropic_circuit.state}"
    )

    # Schedule tasks (ET times) - Mon-Fri for all trading tasks
    WEEKDAYS = [
        schedule.every().monday,
        schedule.every().tuesday,
        schedule.every().wednesday,
        schedule.every().thursday,
        schedule.every().friday,
    ]

    weekday_tasks = [
        ("06:00", run_research),     # Research before market open
        ("08:30", run_trades),       # Trade generation
        ("09:30", run_execute),      # Trade execution at market open
        ("16:30", run_performance),  # Performance graph after close
        ("17:00", run_health_check), # Daily health check
    ]

    for time_str, task_func in weekday_tasks:
        for day in WEEKDAYS:
            day.at(time_str).do(task_func)

    # Heartbeat every hour
    schedule.every().hour.do(heartbeat)

    print("\nScheduled tasks:")
    print("- Research: Mon-Fri 6:00 AM ET")
    print("- Trades: Mon-Fri 8:30 AM ET")
    print("- Execute: Mon-Fri 9:30 AM ET")
    print("- Performance: Mon-Fri 4:30 PM ET")
    print("- Health Check: Mon-Fri 5:00 PM ET")
    print("\nHealth monitoring enabled:")
    print(f"- Circuit breakers: Alpaca, Anthropic, Financial Datasets")
    print(f"- Task tracking: research, trade_gen, execute, performance")
    print("\nWaiting for scheduled times...")

    # Run forever with crash protection
    consecutive_errors = 0
    while True:
        try:
            schedule.run_pending()
            consecutive_errors = 0  # Reset on success
        except Exception as e:
            consecutive_errors += 1
            logger.error(f"Scheduler loop error #{consecutive_errors}: {e}")
            if consecutive_errors >= 5:
                send_telegram(f"🔴 *Railway* - {consecutive_errors} consecutive scheduler errors! Last: {str(e)[:100]}")
                consecutive_errors = 0  # Reset after alerting
        time.sleep(30)  # Check every 30 seconds


if __name__ == "__main__":
    main()
