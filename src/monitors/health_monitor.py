"""
AI Trading Bot - Continuous Health Monitor
Last Updated: 2025-10-23

Continuous health monitoring system that:
- Runs health checks on a schedule
- Exposes metrics via HTTP endpoint
- Sends alerts on degraded health
- Tracks health trends over time
- Provides Prometheus-compatible metrics
"""

import asyncio
import json
import logging
import sys
import time
from collections import deque
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread
from typing import Dict, List, Optional, Deque

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.health_check import HealthChecker, THRESHOLDS


# ============================================================================
# CONFIGURATION
# ============================================================================

MONITOR_CONFIG = {
    'check_interval_seconds': 300,  # 5 minutes
    'metrics_port': 9090,
    'history_size': 288,  # 24 hours at 5-min intervals
    'alert_cooldown_minutes': 60,
    'degraded_threshold': 70,
    'critical_threshold': 60,
}


# ============================================================================
# METRICS HANDLER
# ============================================================================

class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for metrics endpoint."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/metrics':
            self.send_metrics()
        elif self.path == '/health':
            self.send_health_status()
        elif self.path == '/history':
            self.send_history()
        else:
            self.send_404()

    def send_metrics(self):
        """Send Prometheus-compatible metrics."""
        monitor = self.server.monitor  # type: HealthMonitor

        # Generate Prometheus metrics
        metrics = []

        # Current health score
        metrics.append(f"# HELP trading_bot_health_score Overall system health score (0-100)")
        metrics.append(f"# TYPE trading_bot_health_score gauge")
        metrics.append(f"trading_bot_health_score {monitor.latest_score}")

        # Individual checks
        metrics.append(f"\n# HELP trading_bot_check_passed Individual health check status (1=pass, 0=fail)")
        metrics.append(f"# TYPE trading_bot_check_passed gauge")

        if monitor.latest_checks:
            for check in monitor.latest_checks:
                check_name = check['name'].lower().replace(' ', '_')
                value = 1 if check['passed'] else 0
                metrics.append(f"trading_bot_check_passed{{check=\"{check_name}\"}} {value}")

        # System resources
        metrics.append(f"\n# HELP trading_bot_resource_usage Resource usage percentage")
        metrics.append(f"# TYPE trading_bot_resource_usage gauge")

        if monitor.latest_checks:
            for check in monitor.latest_checks:
                if 'CPU' in check['name']:
                    value = float(check['value'].rstrip('%'))
                    metrics.append(f"trading_bot_resource_usage{{resource=\"cpu\"}} {value}")
                elif 'Memory' in check['name']:
                    value = float(check['value'].split('%')[0])
                    metrics.append(f"trading_bot_resource_usage{{resource=\"memory\"}} {value}")
                elif 'Disk' in check['name']:
                    value = float(check['value'].split('%')[0])
                    metrics.append(f"trading_bot_resource_usage{{resource=\"disk\"}} {value}")

        # Alert counts
        metrics.append(f"\n# HELP trading_bot_alerts_sent_total Total alerts sent")
        metrics.append(f"# TYPE trading_bot_alerts_sent_total counter")
        metrics.append(f"trading_bot_alerts_sent_total {monitor.alerts_sent}")

        # Last check timestamp
        metrics.append(f"\n# HELP trading_bot_last_check_timestamp Unix timestamp of last health check")
        metrics.append(f"# TYPE trading_bot_last_check_timestamp gauge")
        metrics.append(f"trading_bot_last_check_timestamp {monitor.last_check_time}")

        # Send response
        metrics_text = "\n".join(metrics)
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; version=0.0.4')
        self.end_headers()
        self.wfile.write(metrics_text.encode())

    def send_health_status(self):
        """Send JSON health status."""
        monitor = self.server.monitor  # type: HealthMonitor

        status_data = {
            'status': monitor.latest_status,
            'health_score': monitor.latest_score,
            'last_check': monitor.last_check_time,
            'uptime_seconds': time.time() - monitor.start_time,
            'checks': monitor.latest_checks,
            'issues': monitor.latest_issues,
        }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status_data, indent=2).encode())

    def send_history(self):
        """Send health history."""
        monitor = self.server.monitor  # type: HealthMonitor

        history_data = {
            'interval_seconds': MONITOR_CONFIG['check_interval_seconds'],
            'max_history_size': MONITOR_CONFIG['history_size'],
            'current_size': len(monitor.health_history),
            'history': list(monitor.health_history),
        }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(history_data, indent=2).encode())

    def send_404(self):
        """Send 404 response."""
        self.send_response(404)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Not Found\n\nAvailable endpoints:\n- /metrics\n- /health\n- /history')

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass  # Silent logging to avoid clutter


# ============================================================================
# HEALTH MONITOR
# ============================================================================

class HealthMonitor:
    """Continuous health monitoring system."""

    def __init__(self, check_interval: Optional[int] = None,
                 metrics_port: Optional[int] = None):
        """
        Initialize health monitor.

        Args:
            check_interval: Seconds between health checks (default: 300)
            metrics_port: Port for metrics HTTP server (default: 9090)
        """
        self.check_interval = check_interval or MONITOR_CONFIG['check_interval_seconds']
        self.metrics_port = metrics_port or MONITOR_CONFIG['metrics_port']

        self.running = False
        self.start_time = time.time()

        # Latest state
        self.latest_score = 0.0
        self.latest_status = 'UNKNOWN'
        self.latest_checks: List[Dict] = []
        self.latest_issues: List[str] = []
        self.last_check_time = 0.0

        # History tracking
        self.health_history: Deque[Dict] = deque(maxlen=MONITOR_CONFIG['history_size'])

        # Alert tracking
        self.alerts_sent = 0
        self.last_alert_time: Optional[float] = None

        # Metrics server
        self.metrics_server: Optional[HTTPServer] = None
        self.metrics_thread: Optional[Thread] = None

        # Logging
        self.logger = logging.getLogger('HealthMonitor')
        self.logger.setLevel(logging.INFO)

    def start(self):
        """Start continuous monitoring."""
        if self.running:
            self.logger.warning("Monitor already running")
            return

        self.logger.info("Starting health monitor...")
        self.running = True

        # Start metrics server
        self._start_metrics_server()

        # Run monitoring loop
        try:
            asyncio.run(self._monitoring_loop())
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        finally:
            self.stop()

    def stop(self):
        """Stop monitoring."""
        self.logger.info("Stopping health monitor...")
        self.running = False

        if self.metrics_server:
            self.metrics_server.shutdown()
            self.metrics_server.server_close()

        if self.metrics_thread:
            self.metrics_thread.join(timeout=5)

        self.logger.info("Health monitor stopped")

    def _start_metrics_server(self):
        """Start HTTP metrics server."""
        try:
            # Create server
            self.metrics_server = HTTPServer(
                ('0.0.0.0', self.metrics_port),
                MetricsHandler
            )
            self.metrics_server.monitor = self  # Attach self for handlers

            # Start in thread
            self.metrics_thread = Thread(
                target=self.metrics_server.serve_forever,
                daemon=True,
                name='MetricsServer'
            )
            self.metrics_thread.start()

            self.logger.info(f"Metrics server started on port {self.metrics_port}")
            self.logger.info(f"  - Metrics: http://localhost:{self.metrics_port}/metrics")
            self.logger.info(f"  - Health: http://localhost:{self.metrics_port}/health")
            self.logger.info(f"  - History: http://localhost:{self.metrics_port}/history")

        except Exception as e:
            self.logger.error(f"Failed to start metrics server: {e}")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        self.logger.info(f"Monitoring loop started (check interval: {self.check_interval}s)")

        while self.running:
            try:
                # Run health check
                await self._run_health_check()

                # Sleep until next check
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def _run_health_check(self):
        """Run single health check."""
        self.logger.info("Running health check...")

        try:
            # Create checker
            checker = HealthChecker(verbose=False)

            # Run checks
            health_score, status, issues = await asyncio.to_thread(
                checker.run_all_checks
            )

            # Update state
            self.latest_score = health_score
            self.latest_status = status
            self.latest_checks = checker.checks
            self.latest_issues = issues
            self.last_check_time = time.time()

            # Add to history
            self.health_history.append({
                'timestamp': self.last_check_time,
                'score': health_score,
                'status': status,
                'issues_count': len(issues),
            })

            # Log results
            self.logger.info(f"Health check completed: {status} ({health_score:.1f}%)")

            if issues:
                self.logger.warning(f"Issues found: {len(issues)}")
                for issue in issues:
                    self.logger.warning(f"  - {issue}")

            # Send alerts if needed
            await self._check_and_send_alerts(health_score, status, issues)

        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)

    async def _check_and_send_alerts(self, health_score: float,
                                    status: str, issues: List[str]):
        """Check if alerts should be sent."""
        # Check if score is below thresholds
        if health_score >= MONITOR_CONFIG['degraded_threshold']:
            return  # System healthy, no alert needed

        # Check cooldown
        cooldown_seconds = MONITOR_CONFIG['alert_cooldown_minutes'] * 60

        if self.last_alert_time:
            time_since_last = time.time() - self.last_alert_time

            if time_since_last < cooldown_seconds:
                self.logger.debug(f"Alert cooldown active ({time_since_last:.0f}s / {cooldown_seconds}s)")
                return

        # Send alert
        await self._send_alert(health_score, status, issues)

    async def _send_alert(self, health_score: float, status: str, issues: List[str]):
        """Send health alert."""
        try:
            from src.alerts.alert_manager import AlertManager

            alert_mgr = AlertManager()

            # Determine severity
            if health_score < MONITOR_CONFIG['critical_threshold']:
                level = 'critical'
                icon = '🔴'
            else:
                level = 'warning'
                icon = '🟡'

            # Build message
            message = f"{icon} HEALTH MONITOR ALERT\n\n"
            message += f"Status: {status}\n"
            message += f"Health Score: {health_score:.1f}%\n"
            message += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

            if issues:
                message += f"\nIssues ({len(issues)}):\n"
                for issue in issues[:5]:  # Limit to 5 issues
                    message += f"  - {issue}\n"

            # Send alert
            await asyncio.to_thread(
                alert_mgr.send_alert,
                message=message,
                level=level,
                channels=['telegram', 'slack']
            )

            self.alerts_sent += 1
            self.last_alert_time = time.time()

            self.logger.info(f"Alert sent ({level}): {health_score:.1f}%")

        except ImportError:
            self.logger.warning("AlertManager not available, skipping alert")
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}", exc_info=True)

    def get_health_trend(self, hours: int = 1) -> Optional[float]:
        """
        Calculate health trend over time.

        Args:
            hours: Number of hours to analyze

        Returns:
            Average score change per hour (positive = improving, negative = degrading)
        """
        if len(self.health_history) < 2:
            return None

        # Get data points within time window
        cutoff_time = time.time() - (hours * 3600)
        recent_data = [
            point for point in self.health_history
            if point['timestamp'] >= cutoff_time
        ]

        if len(recent_data) < 2:
            return None

        # Calculate trend (simple linear)
        first_score = recent_data[0]['score']
        last_score = recent_data[-1]['score']
        time_delta_hours = (recent_data[-1]['timestamp'] - recent_data[0]['timestamp']) / 3600

        if time_delta_hours == 0:
            return None

        trend = (last_score - first_score) / time_delta_hours

        return trend


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point for continuous monitoring."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Continuous health monitoring for AI Trading Bot'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Check interval in seconds (default: 300)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=9090,
        help='Metrics HTTP server port (default: 9090)'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create and start monitor
    monitor = HealthMonitor(
        check_interval=args.interval,
        metrics_port=args.port
    )

    try:
        monitor.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        monitor.stop()


if __name__ == '__main__':
    main()
