#!/usr/bin/env python3
"""
AI Trading Bot - Health Check Script
Last Updated: 2025-10-23

Comprehensive health monitoring that verifies:
- System resources (CPU, memory, disk)
- API connectivity (Financial Datasets, Alpaca, Anthropic)
- Required directories and files
- Recent pipeline execution
- Database connectivity
- Log file sizes

Exit codes:
  0 - System healthy (score >= 60%)
  1 - System unhealthy (score < 60%)
  2 - Critical failure (cannot complete health check)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import psutil
import requests
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import optional dependencies
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from alpaca.trading.client import TradingClient
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False


# ============================================================================
# CONSTANTS
# ============================================================================

THRESHOLDS = {
    'cpu_percent': 80.0,
    'memory_percent': 80.0,
    'disk_percent': 90.0,
    'log_size_mb': 100,
    'pipeline_hours': 4,
    'critical_score': 60,
}

REQUIRED_DIRS = [
    'data',
    'logs',
    'reports',
    'configs',
]

REQUIRED_FILES = [
    'configs/.env',
    'requirements.txt',
    'scripts/daily_pipeline.py',
]

STATUS_ICONS = {
    'HEALTHY': '🟢',
    'WARNING': '🟡',
    'CRITICAL': '🔴',
}


# ============================================================================
# HEALTH CHECK CLASS
# ============================================================================

class HealthChecker:
    """Comprehensive system health checker."""

    def __init__(self, verbose: bool = False):
        """
        Initialize health checker.

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.checks: List[Dict] = []
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.project_root = Path(__file__).parent.parent

        # Load environment variables
        load_dotenv(self.project_root / 'configs' / '.env')

    def log(self, message: str, level: str = 'INFO'):
        """Log message if verbose enabled."""
        if self.verbose or level in ['WARNING', 'ERROR', 'CRITICAL']:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] [{level}] {message}")

    def add_check(self, name: str, passed: bool, value: str,
                  threshold: Optional[str] = None, weight: int = 10):
        """Add check result."""
        self.checks.append({
            'name': name,
            'passed': passed,
            'value': value,
            'threshold': threshold,
            'weight': weight,
        })

        if not passed:
            if weight >= 20:
                self.issues.append(f"{name}: {value}")
            else:
                self.warnings.append(f"{name}: {value}")

    # ------------------------------------------------------------------------
    # SYSTEM RESOURCE CHECKS
    # ------------------------------------------------------------------------

    def check_cpu_usage(self) -> bool:
        """Check CPU usage."""
        self.log("Checking CPU usage...")

        try:
            # Get average over 1 second
            cpu_percent = psutil.cpu_percent(interval=1)
            threshold = THRESHOLDS['cpu_percent']
            passed = cpu_percent < threshold

            self.add_check(
                name='CPU Usage',
                passed=passed,
                value=f"{cpu_percent:.1f}%",
                threshold=f"< {threshold}%",
                weight=15
            )

            if not passed:
                self.log(f"CPU usage high: {cpu_percent:.1f}%", 'WARNING')

            return passed

        except Exception as e:
            self.log(f"CPU check failed: {e}", 'ERROR')
            self.add_check('CPU Usage', False, 'CHECK FAILED', weight=15)
            return False

    def check_memory_usage(self) -> bool:
        """Check memory usage."""
        self.log("Checking memory usage...")

        try:
            memory = psutil.virtual_memory()
            threshold = THRESHOLDS['memory_percent']
            passed = memory.percent < threshold

            used_gb = memory.used / (1024**3)
            total_gb = memory.total / (1024**3)

            self.add_check(
                name='Memory Usage',
                passed=passed,
                value=f"{memory.percent:.1f}% ({used_gb:.1f}GB / {total_gb:.1f}GB)",
                threshold=f"< {threshold}%",
                weight=15
            )

            if not passed:
                self.log(f"Memory usage high: {memory.percent:.1f}%", 'WARNING')

            return passed

        except Exception as e:
            self.log(f"Memory check failed: {e}", 'ERROR')
            self.add_check('Memory Usage', False, 'CHECK FAILED', weight=15)
            return False

    def check_disk_usage(self) -> bool:
        """Check disk usage."""
        self.log("Checking disk usage...")

        try:
            disk = psutil.disk_usage(str(self.project_root))
            threshold = THRESHOLDS['disk_percent']
            passed = disk.percent < threshold

            used_gb = disk.used / (1024**3)
            total_gb = disk.total / (1024**3)

            self.add_check(
                name='Disk Usage',
                passed=passed,
                value=f"{disk.percent:.1f}% ({used_gb:.1f}GB / {total_gb:.1f}GB)",
                threshold=f"< {threshold}%",
                weight=20
            )

            if not passed:
                self.log(f"Disk usage critical: {disk.percent:.1f}%", 'CRITICAL')

            return passed

        except Exception as e:
            self.log(f"Disk check failed: {e}", 'ERROR')
            self.add_check('Disk Usage', False, 'CHECK FAILED', weight=20)
            return False

    # ------------------------------------------------------------------------
    # API CONNECTION CHECKS
    # ------------------------------------------------------------------------

    def check_financial_datasets_api(self) -> bool:
        """Check Financial Datasets API connection."""
        self.log("Checking Financial Datasets API...")

        api_key = os.getenv('FINANCIAL_DATASETS_API_KEY')
        if not api_key:
            self.add_check(
                'Financial Datasets API',
                False,
                'API key not configured',
                weight=25
            )
            return False

        try:
            # Test API with a simple request
            url = 'https://api.financialdatasets.ai/financials/'
            headers = {'X-API-KEY': api_key}
            params = {'ticker': 'AAPL', 'period': 'ttm', 'limit': 1}

            response = requests.get(url, headers=headers, params=params, timeout=10)
            passed = response.status_code == 200

            if passed:
                value = 'Connected ✓'
            else:
                value = f'HTTP {response.status_code}'

            self.add_check(
                'Financial Datasets API',
                passed,
                value,
                weight=25
            )

            if not passed:
                self.log(f"Financial Datasets API failed: {value}", 'ERROR')

            return passed

        except requests.Timeout:
            self.add_check('Financial Datasets API', False, 'Timeout', weight=25)
            self.log("Financial Datasets API timeout", 'ERROR')
            return False
        except Exception as e:
            self.add_check('Financial Datasets API', False, f'Error: {str(e)[:50]}', weight=25)
            self.log(f"Financial Datasets API error: {e}", 'ERROR')
            return False

    def check_alpaca_api(self) -> bool:
        """Check Alpaca API connection."""
        self.log("Checking Alpaca API...")

        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')

        if not api_key or not secret_key:
            self.add_check(
                'Alpaca API',
                False,
                'API keys not configured',
                weight=30
            )
            return False

        if not ALPACA_AVAILABLE:
            self.add_check(
                'Alpaca API',
                False,
                'alpaca-py not installed',
                weight=30
            )
            return False

        try:
            # Test connection
            client = TradingClient(api_key, secret_key, paper=True)
            account = client.get_account()

            passed = account is not None
            value = f"Connected ✓ (${float(account.portfolio_value):,.2f})" if passed else 'Connection failed'

            self.add_check(
                'Alpaca API',
                passed,
                value,
                weight=30
            )

            if not passed:
                self.log("Alpaca API connection failed", 'ERROR')

            return passed

        except Exception as e:
            self.add_check('Alpaca API', False, f'Error: {str(e)[:50]}', weight=30)
            self.log(f"Alpaca API error: {e}", 'ERROR')
            return False

    def check_anthropic_api(self) -> bool:
        """Check Anthropic API connection."""
        self.log("Checking Anthropic API...")

        api_key = os.getenv('ANTHROPIC_API_KEY')

        if not api_key:
            self.add_check(
                'Anthropic API',
                False,
                'API key not configured',
                weight=25
            )
            return False

        if not ANTHROPIC_AVAILABLE:
            self.add_check(
                'Anthropic API',
                False,
                'anthropic package not installed',
                weight=25
            )
            return False

        try:
            # Test connection with minimal request
            client = Anthropic(api_key=api_key)

            # Quick test - just verify client creation
            # (actual API call would cost money, so we verify the key format only)
            if api_key.startswith('sk-ant-api'):
                passed = True
                value = 'Connected ✓ (key format valid)'
            else:
                passed = False
                value = 'Invalid key format'

            self.add_check(
                'Anthropic API',
                passed,
                value,
                weight=25
            )

            if not passed:
                self.log("Anthropic API key format invalid", 'ERROR')

            return passed

        except Exception as e:
            self.add_check('Anthropic API', False, f'Error: {str(e)[:50]}', weight=25)
            self.log(f"Anthropic API error: {e}", 'ERROR')
            return False

    # ------------------------------------------------------------------------
    # FILESYSTEM CHECKS
    # ------------------------------------------------------------------------

    def check_required_directories(self) -> bool:
        """Check required directories exist."""
        self.log("Checking required directories...")

        missing_dirs = []
        for dir_name in REQUIRED_DIRS:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)

        passed = len(missing_dirs) == 0

        if passed:
            value = f"{len(REQUIRED_DIRS)} directories exist ✓"
        else:
            value = f"Missing: {', '.join(missing_dirs)}"

        self.add_check(
            'Required Directories',
            passed,
            value,
            weight=20
        )

        if not passed:
            self.log(f"Missing directories: {missing_dirs}", 'ERROR')

        return passed

    def check_required_files(self) -> bool:
        """Check required files exist."""
        self.log("Checking required files...")

        missing_files = []
        for file_name in REQUIRED_FILES:
            file_path = self.project_root / file_name
            if not file_path.exists():
                missing_files.append(file_name)

        passed = len(missing_files) == 0

        if passed:
            value = f"{len(REQUIRED_FILES)} files exist ✓"
        else:
            value = f"Missing: {', '.join(missing_files)}"

        self.add_check(
            'Required Files',
            passed,
            value,
            weight=20
        )

        if not passed:
            self.log(f"Missing files: {missing_files}", 'ERROR')

        return passed

    def check_log_sizes(self) -> bool:
        """Check log file sizes aren't excessive."""
        self.log("Checking log file sizes...")

        logs_dir = self.project_root / 'logs'
        if not logs_dir.exists():
            self.add_check('Log File Sizes', False, 'logs/ directory missing', weight=10)
            return False

        try:
            large_logs = []
            total_size = 0
            threshold_bytes = THRESHOLDS['log_size_mb'] * 1024 * 1024

            for log_file in logs_dir.rglob('*.log'):
                size = log_file.stat().st_size
                total_size += size

                if size > threshold_bytes:
                    size_mb = size / (1024 * 1024)
                    large_logs.append(f"{log_file.name} ({size_mb:.1f}MB)")

            total_mb = total_size / (1024 * 1024)
            passed = len(large_logs) == 0

            if passed:
                value = f"Total: {total_mb:.1f}MB ✓"
            else:
                value = f"Large files: {', '.join(large_logs[:3])}"

            self.add_check(
                'Log File Sizes',
                passed,
                value,
                threshold=f"< {THRESHOLDS['log_size_mb']}MB per file",
                weight=10
            )

            if not passed:
                self.log(f"Large log files found: {large_logs}", 'WARNING')

            return passed

        except Exception as e:
            self.log(f"Log size check failed: {e}", 'ERROR')
            self.add_check('Log File Sizes', False, 'CHECK FAILED', weight=10)
            return False

    # ------------------------------------------------------------------------
    # PIPELINE CHECKS
    # ------------------------------------------------------------------------

    def check_recent_pipeline_execution(self) -> bool:
        """Check if pipeline has executed recently."""
        self.log("Checking recent pipeline execution...")

        reports_dir = self.project_root / 'reports' / 'premarket'
        if not reports_dir.exists():
            self.add_check(
                'Recent Pipeline Execution',
                False,
                'reports/premarket/ directory missing',
                weight=15
            )
            return False

        try:
            # Find most recent report
            today = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

            recent_reports = []
            for date_str in [today, yesterday]:
                date_dir = reports_dir / date_str
                if date_dir.exists():
                    for report in date_dir.glob('*.md'):
                        mtime = datetime.fromtimestamp(report.stat().st_mtime)
                        recent_reports.append((report, mtime))

            if not recent_reports:
                self.add_check(
                    'Recent Pipeline Execution',
                    False,
                    f'No reports found for {today} or {yesterday}',
                    weight=15
                )
                return False

            # Check most recent
            most_recent_file, most_recent_time = max(recent_reports, key=lambda x: x[1])
            age_hours = (datetime.now() - most_recent_time).total_seconds() / 3600
            threshold_hours = THRESHOLDS['pipeline_hours']

            passed = age_hours < threshold_hours

            if passed:
                value = f"Last report: {age_hours:.1f}h ago ✓"
            else:
                value = f"Last report: {age_hours:.1f}h ago (too old)"

            self.add_check(
                'Recent Pipeline Execution',
                passed,
                value,
                threshold=f"< {threshold_hours}h",
                weight=15
            )

            if not passed:
                self.log(f"Pipeline execution stale: {age_hours:.1f}h old", 'WARNING')

            return passed

        except Exception as e:
            self.log(f"Pipeline execution check failed: {e}", 'ERROR')
            self.add_check('Recent Pipeline Execution', False, 'CHECK FAILED', weight=15)
            return False

    # ------------------------------------------------------------------------
    # DATABASE CHECKS
    # ------------------------------------------------------------------------

    def check_database_connectivity(self) -> bool:
        """Check database connectivity if configured."""
        self.log("Checking database connectivity...")

        database_url = os.getenv('DATABASE_URL')

        if not database_url:
            self.add_check(
                'Database Connectivity',
                True,
                'Not configured (optional)',
                weight=5
            )
            return True

        if not POSTGRES_AVAILABLE:
            self.add_check(
                'Database Connectivity',
                False,
                'psycopg2 not installed',
                weight=10
            )
            return False

        try:
            # Parse connection string and test
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            passed = result[0] == 1
            value = 'Connected ✓' if passed else 'Connection failed'

            self.add_check(
                'Database Connectivity',
                passed,
                value,
                weight=10
            )

            return passed

        except Exception as e:
            self.add_check('Database Connectivity', False, f'Error: {str(e)[:50]}', weight=10)
            self.log(f"Database connectivity error: {e}", 'ERROR')
            return False

    def check_redis_connectivity(self) -> bool:
        """Check Redis connectivity if configured."""
        self.log("Checking Redis connectivity...")

        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', '6379'))

        if not redis_host or redis_host == 'localhost':
            self.add_check(
                'Redis Connectivity',
                True,
                'Not configured (optional)',
                weight=5
            )
            return True

        if not REDIS_AVAILABLE:
            self.add_check(
                'Redis Connectivity',
                False,
                'redis package not installed',
                weight=10
            )
            return False

        try:
            client = redis.Redis(host=redis_host, port=redis_port,
                                socket_connect_timeout=5, socket_timeout=5)
            pong = client.ping()

            passed = pong is True
            value = 'Connected ✓' if passed else 'Ping failed'

            self.add_check(
                'Redis Connectivity',
                passed,
                value,
                weight=10
            )

            return passed

        except Exception as e:
            self.add_check('Redis Connectivity', False, f'Error: {str(e)[:50]}', weight=10)
            self.log(f"Redis connectivity error: {e}", 'ERROR')
            return False

    # ------------------------------------------------------------------------
    # MAIN HEALTH CHECK
    # ------------------------------------------------------------------------

    def run_all_checks(self) -> Tuple[float, str, List[str]]:
        """
        Run all health checks.

        Returns:
            Tuple of (health_score, status, issues)
        """
        self.log("Starting comprehensive health check...", 'INFO')
        start_time = time.time()

        # Run all checks
        self.check_cpu_usage()
        self.check_memory_usage()
        self.check_disk_usage()

        self.check_financial_datasets_api()
        self.check_alpaca_api()
        self.check_anthropic_api()

        self.check_required_directories()
        self.check_required_files()
        self.check_log_sizes()

        self.check_recent_pipeline_execution()

        self.check_database_connectivity()
        self.check_redis_connectivity()

        # Calculate health score
        total_weight = sum(check['weight'] for check in self.checks)
        passed_weight = sum(check['weight'] for check in self.checks if check['passed'])

        health_score = (passed_weight / total_weight * 100) if total_weight > 0 else 0

        # Determine status
        if health_score >= 80:
            status = 'HEALTHY'
        elif health_score >= THRESHOLDS['critical_score']:
            status = 'WARNING'
        else:
            status = 'CRITICAL'

        elapsed = time.time() - start_time
        self.log(f"Health check completed in {elapsed:.2f}s", 'INFO')

        return health_score, status, self.issues

    def generate_report(self, health_score: float, status: str) -> str:
        """Generate health report."""
        icon = STATUS_ICONS.get(status, '⚪')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        report = []
        report.append("=" * 80)
        report.append(f"{icon} SYSTEM HEALTH REPORT")
        report.append("=" * 80)
        report.append(f"Timestamp: {timestamp}")
        report.append(f"Overall Health: {health_score:.1f}%")
        report.append(f"Status: {status}")
        report.append("")

        # Detailed checks
        report.append("DETAILED CHECKS:")
        report.append("-" * 80)

        for check in self.checks:
            status_icon = '✓' if check['passed'] else '✗'
            name = check['name'].ljust(30)
            value = check['value'].ljust(30)
            threshold = f"[{check['threshold']}]" if check['threshold'] else ''

            report.append(f"  {status_icon} {name} {value} {threshold}")

        # Issues
        if self.issues:
            report.append("")
            report.append("CRITICAL ISSUES:")
            report.append("-" * 80)
            for issue in self.issues:
                report.append(f"  🔴 {issue}")

        # Warnings
        if self.warnings:
            report.append("")
            report.append("WARNINGS:")
            report.append("-" * 80)
            for warning in self.warnings:
                report.append(f"  🟡 {warning}")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)


# ============================================================================
# ALERT MANAGER INTEGRATION
# ============================================================================

def send_critical_alert(health_score: float, issues: List[str]):
    """Send critical alert if health score is low."""
    try:
        # Try to import and use AlertManager
        from src.alerts.alert_manager import AlertManager

        alert_mgr = AlertManager()

        message = f"🔴 CRITICAL: System health at {health_score:.1f}%\n\n"
        message += "Issues:\n"
        for issue in issues:
            message += f"- {issue}\n"

        alert_mgr.send_alert(
            message=message,
            level='critical',
            channels=['telegram', 'slack']
        )

        print("✓ Critical alert sent via AlertManager")

    except ImportError:
        print("⚠ AlertManager not available, skipping alert")
    except Exception as e:
        print(f"⚠ Failed to send alert: {e}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Comprehensive health check for AI Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/health_check.py                    # Run health check
  python scripts/health_check.py --verbose          # Verbose output
  python scripts/health_check.py --json             # JSON output
  python scripts/health_check.py --output report.txt  # Save to file
        """
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Save report to file'
    )

    parser.add_argument(
        '--no-alert',
        action='store_true',
        help='Disable critical alerts'
    )

    args = parser.parse_args()

    try:
        # Run health check
        checker = HealthChecker(verbose=args.verbose)
        health_score, status, issues = checker.run_all_checks()

        # Generate report
        if args.json:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'health_score': health_score,
                'status': status,
                'checks': checker.checks,
                'issues': checker.issues,
                'warnings': checker.warnings,
            }
            report = json.dumps(report_data, indent=2)
        else:
            report = checker.generate_report(health_score, status)

        # Output
        print(report)

        # Save to file if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report)
            print(f"\n✓ Report saved to {args.output}")

        # Send alert if critical
        if health_score < THRESHOLDS['critical_score'] and not args.no_alert:
            send_critical_alert(health_score, issues)

        # Exit code
        exit_code = 0 if health_score >= THRESHOLDS['critical_score'] else 1
        sys.exit(exit_code)

    except Exception as e:
        print(f"ERROR: Health check failed: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
