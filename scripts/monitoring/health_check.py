#!/usr/bin/env python3
"""
Health Check Script for AI Trading Bot
Monitors system health, API connectivity, and file operations.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import argparse
from typing import Tuple, List

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Try to import optional dependencies
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    from alpaca.trading.client import TradingClient
    HAS_ALPACA = True
except ImportError:
    HAS_ALPACA = False


class HealthCheck:
    """System health monitoring and validation."""

    def __init__(self, verbose: bool = False):
        """
        Initialize health check.

        Args:
            verbose: Enable detailed output
        """
        self.verbose = verbose
        self.checks_passed = 0
        self.checks_failed = 0

    def log_verbose(self, message: str) -> None:
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(f"  [DEBUG] {message}")

    def check_research_generation(self) -> Tuple[bool, str]:
        """
        Check if pre-market report was generated today.

        Returns:
            (success, message) tuple
        """
        self.log_verbose("Checking research generation...")

        reports_dir = Path('reports/premarket')

        # Check if directory exists
        if not reports_dir.exists():
            return False, "reports/premarket directory does not exist"

        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        report_file = reports_dir / f'premarket_report_{today}.md'

        self.log_verbose(f"Looking for report: {report_file}")

        # Check if today's report exists
        if not report_file.exists():
            # Check latest.md as fallback
            latest_file = reports_dir / 'latest.md'
            if latest_file.exists():
                # Check file age
                file_mtime = datetime.fromtimestamp(latest_file.stat().st_mtime)
                age_hours = (datetime.now() - file_mtime).total_seconds() / 3600

                self.log_verbose(f"Latest report age: {age_hours:.1f} hours")

                if age_hours > 24:
                    return False, f"Latest report is {age_hours:.1f} hours old (>24h)"

                # Check file size
                file_size = latest_file.stat().st_size
                self.log_verbose(f"Latest report size: {file_size} bytes")

                if file_size < 1000:
                    return False, f"Latest report is too small ({file_size} bytes < 1000)"

                return True, f"Latest report exists ({file_size} bytes, {age_hours:.1f}h old)"
            else:
                return False, "No report found for today and no latest.md"

        # Check today's report age (should be <4 hours old)
        file_mtime = datetime.fromtimestamp(report_file.stat().st_mtime)
        age_hours = (datetime.now() - file_mtime).total_seconds() / 3600

        self.log_verbose(f"Today's report age: {age_hours:.1f} hours")

        if age_hours > 4:
            return False, f"Today's report is {age_hours:.1f} hours old (>4h)"

        # Check file size
        file_size = report_file.stat().st_size
        self.log_verbose(f"Today's report size: {file_size} bytes")

        if file_size < 1000:
            return False, f"Today's report is too small ({file_size} bytes < 1000)"

        return True, f"Today's report exists ({file_size} bytes, {age_hours:.1f}h old)"

    def check_api_connectivity(self) -> List[Tuple[str, bool, str]]:
        """
        Test connectivity to external APIs.

        Returns:
            List of (service, success, message) tuples
        """
        results = []

        # Check Anthropic API
        self.log_verbose("Checking Anthropic API connectivity...")

        if not HAS_ANTHROPIC:
            results.append(("Anthropic API", False, "anthropic package not installed"))
        else:
            api_key = os.getenv('ANTHROPIC_API_KEY')

            if not api_key:
                results.append(("Anthropic API", False, "ANTHROPIC_API_KEY not set"))
            else:
                try:
                    client = anthropic.Anthropic(api_key=api_key)

                    # Make a minimal API call to test connectivity
                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=10,
                        messages=[{"role": "user", "content": "ping"}]
                    )

                    self.log_verbose(f"Anthropic API response: {response.content[0].text}")
                    results.append(("Anthropic API", True, "Connected successfully"))

                except Exception as e:
                    error_msg = str(e)[:100]
                    self.log_verbose(f"Anthropic API error: {error_msg}")
                    results.append(("Anthropic API", False, f"Error: {error_msg}"))

        # Check Alpaca API
        self.log_verbose("Checking Alpaca API connectivity...")

        if not HAS_ALPACA:
            results.append(("Alpaca API", False, "alpaca-py package not installed"))
        else:
            api_key = os.getenv('ALPACA_API_KEY')
            secret_key = os.getenv('ALPACA_SECRET_KEY')
            base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')

            if not api_key or not secret_key:
                results.append(("Alpaca API", False, "API keys not set"))
            else:
                try:
                    client = TradingClient(api_key=api_key, secret_key=secret_key)

                    # Get account info to test connectivity
                    account = client.get_account()

                    self.log_verbose(f"Alpaca account: ${float(account.portfolio_value):,.2f}")
                    results.append(("Alpaca API", True, f"Connected (Portfolio: ${float(account.portfolio_value):,.2f})"))

                except Exception as e:
                    error_msg = str(e)[:100]
                    self.log_verbose(f"Alpaca API error: {error_msg}")
                    results.append(("Alpaca API", False, f"Error: {error_msg}"))

        return results

    def check_file_permissions(self) -> Tuple[bool, str]:
        """
        Check write permissions for required directories.

        Returns:
            (success, message) tuple
        """
        self.log_verbose("Checking file permissions...")

        directories = ['reports/premarket', 'logs']
        issues = []

        for dir_path in directories:
            dir_obj = Path(dir_path)

            # Check if directory exists
            if not dir_obj.exists():
                self.log_verbose(f"Directory does not exist: {dir_path}")
                try:
                    dir_obj.mkdir(parents=True, exist_ok=True)
                    self.log_verbose(f"Created directory: {dir_path}")
                except Exception as e:
                    issues.append(f"Cannot create {dir_path}: {e}")
                    continue

            # Test write permission
            test_file = dir_obj / f'.health_check_test_{datetime.now().timestamp()}'

            try:
                # Try to write
                test_file.write_text("test")
                self.log_verbose(f"Write test passed: {dir_path}")

                # Try to delete
                test_file.unlink()
                self.log_verbose(f"Delete test passed: {dir_path}")

            except Exception as e:
                issues.append(f"Cannot write to {dir_path}: {e}")

        if issues:
            return False, "; ".join(issues)

        return True, f"Write permissions OK for {len(directories)} directories"

    def run_all_checks(self) -> int:
        """
        Run all health checks and print results.

        Returns:
            Exit code (0 if all pass, 1 if any fail)
        """
        print("=" * 80)
        print("AI Trading Bot - System Health Check")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()

        # Check 1: Research Generation
        print("1. Research Generation:")
        success, message = self.check_research_generation()

        if success:
            print(f"   [PASS] {message}")
            self.checks_passed += 1
        else:
            print(f"   [FAIL] {message}")
            self.checks_failed += 1
        print()

        # Check 2: API Connectivity
        print("2. API Connectivity:")
        api_results = self.check_api_connectivity()

        for service, success, message in api_results:
            if success:
                print(f"   [PASS] {service}: {message}")
                self.checks_passed += 1
            else:
                print(f"   [FAIL] {service}: {message}")
                self.checks_failed += 1
        print()

        # Check 3: File Permissions
        print("3. File Permissions:")
        success, message = self.check_file_permissions()

        if success:
            print(f"   [PASS] {message}")
            self.checks_passed += 1
        else:
            print(f"   [FAIL] {message}")
            self.checks_failed += 1
        print()

        # Summary
        total_checks = self.checks_passed + self.checks_failed
        print("=" * 80)
        print(f"Summary: {self.checks_passed}/{total_checks} checks passed")

        if self.checks_failed > 0:
            print(f"Status: [FAIL] FAILED ({self.checks_failed} issues found)")
            print("=" * 80)
            return 1
        else:
            print("Status: [PASS] ALL SYSTEMS OPERATIONAL")
            print("=" * 80)
            return 0


def main():
    """Main entry point for health check script."""
    parser = argparse.ArgumentParser(
        description='AI Trading Bot System Health Check',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python health_check.py              # Run health check
  python health_check.py --verbose    # Run with detailed output
  python health_check.py -v           # Short form

Exit Codes:
  0 - All checks passed
  1 - One or more checks failed
        """
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable detailed debug output'
    )

    args = parser.parse_args()

    # Run health check
    checker = HealthCheck(verbose=args.verbose)
    exit_code = checker.run_all_checks()

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
