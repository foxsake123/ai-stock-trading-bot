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
    retry_with_backoff,
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


def run_research():
    """Run research generation with health monitoring."""
    logger.info("Starting research generation...")
    send_telegram("🔬 *Railway* - Starting research generation...")

    try:
        with health_monitor.track_task("research_generation") as tracker:
            # Check circuit breaker before proceeding
            if anthropic_circuit.state == "OPEN":
                raise Exception("Anthropic circuit breaker is OPEN - too many recent failures")

            from scripts.automation.daily_claude_research import main as research_main
            research_main()

            anthropic_circuit.record_success()
            tracker.add_detail("status", "success")
            send_telegram("✅ *Railway* - Research complete!")
            logger.info("Research generation complete!")

    except Exception as e:
        try:
            anthropic_circuit.record_failure(e)
        except Exception:
            pass
        error_msg = str(e)[:100]
        send_telegram(f"❌ *Railway* - Research failed: {error_msg}")
        logger.error(f"Research generation failed: {e}")
        health_monitor.send_alert(AlertLevel.HIGH, f"Research generation failed: {error_msg}")


def run_trades():
    """Run trade generation with health monitoring."""
    logger.info("Starting trade generation...")
    send_telegram("📊 *Railway* - Starting trade generation...")

    try:
        with health_monitor.track_task("trade_generation") as tracker:
            from scripts.automation.generate_todays_trades_v2 import main as trades_main
            trades_main()

            tracker.add_detail("status", "success")
            send_telegram("✅ *Railway* - Trades generated!")
            logger.info("Trade generation complete!")

    except Exception as e:
        error_msg = str(e)[:100]
        send_telegram(f"❌ *Railway* - Trade generation failed: {error_msg}")
        logger.error(f"Trade generation failed: {e}")
        health_monitor.send_alert(AlertLevel.HIGH, f"Trade generation failed: {error_msg}")


def run_execute():
    """Run trade execution with health monitoring and circuit breaker."""
    logger.info("Starting trade execution...")
    send_telegram("💰 *Railway* - Starting trade execution...")

    try:
        with health_monitor.track_task("trade_execution") as tracker:
            # Check circuit breaker before proceeding
            if alpaca_circuit.state == "OPEN":
                raise Exception("Alpaca circuit breaker is OPEN - too many recent failures")

            from scripts.automation.execute_daily_trades import main as execute_main
            execute_main()

            alpaca_circuit.record_success()
            tracker.add_detail("status", "success")
            send_telegram("✅ *Railway* - Trades executed!")
            logger.info("Trade execution complete!")

    except Exception as e:
        try:
            alpaca_circuit.record_failure(e)
        except Exception:
            pass
        error_msg = str(e)[:100]
        send_telegram(f"❌ *Railway* - Execution failed: {error_msg}")
        logger.error(f"Trade execution failed: {e}")
        health_monitor.send_alert(AlertLevel.CRITICAL, f"Trade execution failed: {error_msg}")


def run_performance():
    """Run performance graph update with health monitoring."""
    logger.info("Starting performance update...")
    send_telegram("📈 *Railway* - Updating performance...")

    try:
        with health_monitor.track_task("performance_update") as tracker:
            from scripts.performance.generate_performance_graph import main as perf_main
            perf_main()

            tracker.add_detail("status", "success")
            send_telegram("✅ *Railway* - Performance updated!")
            logger.info("Performance update complete!")

    except Exception as e:
        error_msg = str(e)[:100]
        send_telegram(f"❌ *Railway* - Performance failed: {error_msg}")
        logger.error(f"Performance update failed: {e}")
        health_monitor.send_alert(AlertLevel.WARNING, f"Performance update failed: {error_msg}")


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

    # Schedule tasks (ET times)
    # Research: Mon-Fri 6:00 AM (before market open)
    schedule.every().monday.at("06:00").do(run_research)
    schedule.every().tuesday.at("06:00").do(run_research)
    schedule.every().wednesday.at("06:00").do(run_research)
    schedule.every().thursday.at("06:00").do(run_research)
    schedule.every().friday.at("06:00").do(run_research)

    # Trades: Mon-Fri 8:30 AM
    schedule.every().monday.at("08:30").do(run_trades)
    schedule.every().tuesday.at("08:30").do(run_trades)
    schedule.every().wednesday.at("08:30").do(run_trades)
    schedule.every().thursday.at("08:30").do(run_trades)
    schedule.every().friday.at("08:30").do(run_trades)

    # Execute: Mon-Fri 9:30 AM
    schedule.every().monday.at("09:30").do(run_execute)
    schedule.every().tuesday.at("09:30").do(run_execute)
    schedule.every().wednesday.at("09:30").do(run_execute)
    schedule.every().thursday.at("09:30").do(run_execute)
    schedule.every().friday.at("09:30").do(run_execute)

    # Performance: Mon-Fri 4:30 PM
    schedule.every().monday.at("16:30").do(run_performance)
    schedule.every().tuesday.at("16:30").do(run_performance)
    schedule.every().wednesday.at("16:30").do(run_performance)
    schedule.every().thursday.at("16:30").do(run_performance)
    schedule.every().friday.at("16:30").do(run_performance)

    # Heartbeat every hour
    schedule.every().hour.do(heartbeat)

    # Daily health check at 5 PM ET
    schedule.every().monday.at("17:00").do(run_health_check)
    schedule.every().tuesday.at("17:00").do(run_health_check)
    schedule.every().wednesday.at("17:00").do(run_health_check)
    schedule.every().thursday.at("17:00").do(run_health_check)
    schedule.every().friday.at("17:00").do(run_health_check)

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
