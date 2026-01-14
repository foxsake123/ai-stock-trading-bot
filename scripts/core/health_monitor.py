"""
Health Monitoring for AI Trading Bot
=====================================
Tracks execution status, detects failures, and sends alerts.

Author: AI Trading Bot System
Date: January 13, 2026
"""

import os
import json
import logging
import requests
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"
    STALE = "stale"
    UNKNOWN = "unknown"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TaskExecution:
    """Record of a task execution"""
    task_name: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    details: Optional[Dict] = None


class HealthMonitor:
    """
    Monitors system health and tracks task executions.

    Example:
        monitor = HealthMonitor()

        # Record task execution
        with monitor.track_task("research_generation"):
            generate_research()

        # Check health
        status = monitor.get_system_health()
        if status["overall"] == "unhealthy":
            monitor.send_alert(AlertLevel.CRITICAL, "System unhealthy!")
    """

    TASKS = [
        "research_generation",
        "trade_generation",
        "trade_execution",
        "performance_update",
        "ml_outcome_update"
    ]

    STALE_THRESHOLDS = {
        "research_generation": 168,  # 7 days (weekly)
        "trade_generation": 24,      # 24 hours
        "trade_execution": 24,       # 24 hours
        "performance_update": 24,    # 24 hours
        "ml_outcome_update": 48      # 48 hours
    }

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Args:
            data_dir: Directory for health data. Defaults to data/health/
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "data" / "health"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.status_file = self.data_dir / "task_status.json"
        self.history_file = self.data_dir / "execution_history.json"

        # Telegram config
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # Load existing status
        self._status = self._load_status()

    def _load_status(self) -> Dict:
        """Load status from file"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load status: {e}")
        return {"tasks": {}, "last_updated": None}

    def _save_status(self):
        """Save status to file"""
        self._status["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.status_file, 'w') as f:
                json.dump(self._status, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save status: {e}")

    def _append_history(self, execution: TaskExecution):
        """Append execution to history file"""
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            except:
                pass

        history.append(asdict(execution))

        # Keep last 1000 entries
        history = history[-1000:]

        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def record_start(self, task_name: str):
        """Record task start"""
        self._status["tasks"][task_name] = {
            "status": TaskStatus.RUNNING.value,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "error": None
        }
        self._save_status()
        logger.info(f"Task started: {task_name}")

    def record_success(self, task_name: str, details: Optional[Dict] = None):
        """Record successful task completion"""
        started_at = self._status["tasks"].get(task_name, {}).get("started_at")
        completed_at = datetime.now()

        duration = None
        if started_at:
            start = datetime.fromisoformat(started_at)
            duration = (completed_at - start).total_seconds()

        self._status["tasks"][task_name] = {
            "status": TaskStatus.SUCCESS.value,
            "started_at": started_at,
            "completed_at": completed_at.isoformat(),
            "duration_seconds": duration,
            "error": None,
            "details": details
        }
        self._save_status()

        # Record in history
        execution = TaskExecution(
            task_name=task_name,
            status=TaskStatus.SUCCESS.value,
            started_at=started_at or completed_at.isoformat(),
            completed_at=completed_at.isoformat(),
            duration_seconds=duration,
            details=details
        )
        self._append_history(execution)

        logger.info(f"Task completed: {task_name} (duration: {duration:.1f}s)")

    def record_failure(self, task_name: str, error: str, details: Optional[Dict] = None):
        """Record task failure"""
        started_at = self._status["tasks"].get(task_name, {}).get("started_at")
        completed_at = datetime.now()

        duration = None
        if started_at:
            start = datetime.fromisoformat(started_at)
            duration = (completed_at - start).total_seconds()

        self._status["tasks"][task_name] = {
            "status": TaskStatus.FAILED.value,
            "started_at": started_at,
            "completed_at": completed_at.isoformat(),
            "duration_seconds": duration,
            "error": error,
            "details": details
        }
        self._save_status()

        # Record in history
        execution = TaskExecution(
            task_name=task_name,
            status=TaskStatus.FAILED.value,
            started_at=started_at or completed_at.isoformat(),
            completed_at=completed_at.isoformat(),
            duration_seconds=duration,
            error_message=error,
            details=details
        )
        self._append_history(execution)

        logger.error(f"Task failed: {task_name} - {error}")

    def track_task(self, task_name: str):
        """Context manager for tracking task execution"""
        return TaskTracker(self, task_name)

    def get_task_status(self, task_name: str) -> Dict:
        """Get status for a specific task"""
        task_data = self._status["tasks"].get(task_name, {})

        if not task_data:
            return {
                "status": TaskStatus.UNKNOWN.value,
                "message": "No execution recorded"
            }

        status = task_data.get("status", TaskStatus.UNKNOWN.value)
        completed_at = task_data.get("completed_at")

        # Check if stale
        if status == TaskStatus.SUCCESS.value and completed_at:
            threshold = self.STALE_THRESHOLDS.get(task_name, 24)
            last_run = datetime.fromisoformat(completed_at)
            hours_since = (datetime.now() - last_run).total_seconds() / 3600

            if hours_since > threshold:
                status = TaskStatus.STALE.value
                task_data["message"] = f"Last run {hours_since:.1f}h ago (threshold: {threshold}h)"

        return {
            "status": status,
            **task_data
        }

    def get_system_health(self) -> Dict:
        """
        Get overall system health status.

        Returns:
            Dict with overall status and per-task breakdown
        """
        task_statuses = {}
        issues = []

        for task in self.TASKS:
            status = self.get_task_status(task)
            task_statuses[task] = status

            if status["status"] == TaskStatus.FAILED.value:
                issues.append(f"{task}: FAILED - {status.get('error', 'Unknown error')}")
            elif status["status"] == TaskStatus.STALE.value:
                issues.append(f"{task}: STALE - {status.get('message', 'No recent execution')}")
            elif status["status"] == TaskStatus.UNKNOWN.value:
                issues.append(f"{task}: UNKNOWN - Never executed")

        # Determine overall health
        failed_count = sum(1 for t in task_statuses.values() if t["status"] == TaskStatus.FAILED.value)
        stale_count = sum(1 for t in task_statuses.values() if t["status"] == TaskStatus.STALE.value)
        unknown_count = sum(1 for t in task_statuses.values() if t["status"] == TaskStatus.UNKNOWN.value)

        if failed_count > 0:
            overall = "critical"
        elif stale_count > 1:
            overall = "unhealthy"
        elif stale_count == 1 or unknown_count > 2:
            overall = "degraded"
        else:
            overall = "healthy"

        return {
            "overall": overall,
            "timestamp": datetime.now().isoformat(),
            "tasks": task_statuses,
            "issues": issues,
            "summary": {
                "healthy": len(self.TASKS) - failed_count - stale_count - unknown_count,
                "failed": failed_count,
                "stale": stale_count,
                "unknown": unknown_count
            }
        }

    def send_alert(self, level: AlertLevel, message: str):
        """
        Send alert via Telegram.

        Args:
            level: Alert severity
            message: Alert message
        """
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram not configured, skipping alert")
            return

        emoji = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.HIGH: "🔴",
            AlertLevel.CRITICAL: "🚨"
        }.get(level, "📢")

        full_message = f"{emoji} *{level.value.upper()}*\n\n{message}"

        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            response = requests.post(
                url,
                data={
                    "chat_id": self.telegram_chat_id,
                    "text": full_message,
                    "parse_mode": "Markdown"
                },
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Alert sent: {level.value} - {message[:50]}...")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

    def send_daily_summary(self):
        """Send daily health summary"""
        health = self.get_system_health()

        message = f"*Daily Health Summary*\n"
        message += f"Status: {health['overall'].upper()}\n\n"

        for task, status in health["tasks"].items():
            emoji = "✅" if status["status"] == "success" else "❌"
            message += f"{emoji} {task}: {status['status']}\n"

        if health["issues"]:
            message += f"\n*Issues:*\n"
            for issue in health["issues"][:5]:
                message += f"• {issue}\n"

        self.send_alert(AlertLevel.INFO, message)

    def check_and_alert(self):
        """Check health and send alerts if needed"""
        health = self.get_system_health()

        if health["overall"] == "critical":
            self.send_alert(
                AlertLevel.CRITICAL,
                f"System CRITICAL!\n\n" +
                "\n".join(health["issues"][:3])
            )
        elif health["overall"] == "unhealthy":
            self.send_alert(
                AlertLevel.HIGH,
                f"System unhealthy\n\n" +
                "\n".join(health["issues"][:3])
            )


class TaskTracker:
    """Context manager for tracking task execution"""

    def __init__(self, monitor: HealthMonitor, task_name: str):
        self.monitor = monitor
        self.task_name = task_name
        self.details = {}

    def __enter__(self):
        self.monitor.record_start(self.task_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.monitor.record_success(self.task_name, self.details)
        else:
            self.monitor.record_failure(
                self.task_name,
                str(exc_val),
                self.details
            )
        return False  # Don't suppress exceptions

    def add_detail(self, key: str, value):
        """Add detail to execution record"""
        self.details[key] = value


# Global health monitor instance
_monitor: Optional[HealthMonitor] = None


def get_health_monitor() -> HealthMonitor:
    """Get or create global health monitor"""
    global _monitor
    if _monitor is None:
        _monitor = HealthMonitor()
    return _monitor


if __name__ == "__main__":
    # Test health monitor
    from dotenv import load_dotenv
    load_dotenv()

    monitor = HealthMonitor()

    # Simulate task executions
    print("Testing health monitor...")

    # Test success
    with monitor.track_task("trade_generation") as tracker:
        tracker.add_detail("trades_generated", 5)
        print("  Simulating trade generation...")

    # Test failure
    try:
        with monitor.track_task("performance_update") as tracker:
            raise ValueError("Test error")
    except ValueError:
        pass

    # Check health
    health = monitor.get_system_health()
    print(f"\nSystem Health: {health['overall']}")
    print(f"Issues: {health['issues']}")

    # Show status
    print("\nTask Statuses:")
    for task, status in health["tasks"].items():
        print(f"  {task}: {status['status']}")
