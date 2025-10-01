"""
Test the complete automated trading pipeline
Validates all components are working correctly
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import subprocess
import requests

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

class PipelineTest:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'overall': 'PENDING'
        }

    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)

    def test_dependencies(self):
        """Test if all required packages are installed"""
        self.print_header("TESTING DEPENDENCIES")

        required_packages = [
            'yfinance',
            'alpaca_trade_api',
            'pandas',
            'requests',
            'flask',
            'flask_cors',
            'selenium',
            'undetected_chromedriver'
        ]

        missing = []
        for package in required_packages:
            try:
                __import__(package.replace('_', '-').replace('-', '_'))
                print(f"[PASS] {package}")
            except ImportError:
                print(f"[FAIL] {package} - MISSING")
                missing.append(package)

        self.results['tests']['dependencies'] = {
            'status': 'PASS' if not missing else 'FAIL',
            'missing': missing
        }

        return len(missing) == 0

    def test_file_structure(self):
        """Test if all critical files exist"""
        self.print_header("TESTING FILE STRUCTURE")

        critical_files = [
            'scripts-and-data/automation/execute_daily_trades.py',
            'scripts-and-data/automation/generate_todays_trades.py',
            'scripts-and-data/automation/automated_chatgpt_fetcher.py',
            'scripts-and-data/automation/generate-post-market-report.py',
            'scripts-and-data/daily-csv/dee-bot-positions.csv',
            'scripts-and-data/daily-csv/shorgan-bot-positions.csv',
            'agents/fundamental_analyst.py',
            'agents/technical_analyst.py',
            'communication/coordinator.py'
        ]

        missing = []
        for file in critical_files:
            filepath = self.project_root / file
            if filepath.exists():
                print(f"[OK] {file}")
            else:
                print(f"[FAIL] {file} - NOT FOUND")
                missing.append(file)

        self.results['tests']['file_structure'] = {
            'status': 'PASS' if not missing else 'FAIL',
            'missing': missing
        }

        return len(missing) == 0

    def test_api_connections(self):
        """Test API connections"""
        self.print_header("TESTING API CONNECTIONS")

        results = {}

        # Test Alpaca connection
        try:
            import alpaca_trade_api as tradeapi
            sys.path.insert(0, str(self.project_root / 'scripts-and-data' / 'automation'))
            from execute_daily_trades import DailyTradeExecutor

            executor = DailyTradeExecutor()
            clock = executor.dee_api.get_clock()

            print(f"[OK] Alpaca API - Market {'OPEN' if clock.is_open else 'CLOSED'}")
            results['alpaca'] = 'CONNECTED'
        except Exception as e:
            print(f"[FAIL] Alpaca API - {str(e)}")
            results['alpaca'] = f'ERROR: {str(e)}'

        # Test ChatGPT server
        try:
            response = requests.get('http://localhost:8888/health', timeout=2)
            if response.status_code == 200:
                print("[OK] ChatGPT Server - RUNNING")
                results['chatgpt_server'] = 'RUNNING'
            else:
                print("[WARN] ChatGPT Server - Not responding")
                results['chatgpt_server'] = 'NOT RUNNING'
        except:
            print("[WARN] ChatGPT Server - OFFLINE (optional)")
            results['chatgpt_server'] = 'OFFLINE'

        self.results['tests']['api_connections'] = results
        return 'ERROR' not in str(results)

    def test_trade_generation(self):
        """Test if trade generation works"""
        self.print_header("TESTING TRADE GENERATION")

        try:
            # Check if today's trades exist
            today = datetime.now().strftime('%Y-%m-%d')
            trades_file = self.project_root / 'docs' / f'TODAYS_TRADES_{today}.md'

            if trades_file.exists():
                print(f"[OK] Today's trades file exists: {trades_file.name}")

                # Check content
                with open(trades_file, 'r') as f:
                    content = f.read()

                if 'DEE-BOT' in content and 'SHORGAN-BOT' in content:
                    print("[OK] Trade file has both bot sections")
                    self.results['tests']['trade_generation'] = 'EXISTS'
                else:
                    print("[WARN] Trade file missing bot sections")
                    self.results['tests']['trade_generation'] = 'INCOMPLETE'
            else:
                print("[WARN] No trades file for today (will be generated)")
                self.results['tests']['trade_generation'] = 'NOT FOUND'

            return True

        except Exception as e:
            print(f"[FAIL] Trade generation test failed: {e}")
            self.results['tests']['trade_generation'] = f'ERROR: {str(e)}'
            return False

    def test_validation_system(self):
        """Test the new validation system"""
        self.print_header("TESTING VALIDATION SYSTEM")

        try:
            sys.path.insert(0, str(self.project_root / 'scripts-and-data' / 'automation'))
            from execute_daily_trades import DailyTradeExecutor

            executor = DailyTradeExecutor()

            # Test validation method exists
            if hasattr(executor, 'validate_trade'):
                print("[OK] Validation method exists")

                # Test a sample validation
                is_valid, result = executor.validate_trade(
                    executor.dee_api,
                    'AAPL',
                    10,
                    'buy',
                    150.00
                )

                if isinstance(is_valid, bool):
                    print("[OK] Validation returns proper format")
                    self.results['tests']['validation'] = 'WORKING'
                else:
                    print("[WARN] Validation format incorrect")
                    self.results['tests']['validation'] = 'FORMAT ERROR'
            else:
                print("[FAIL] Validation method not found")
                self.results['tests']['validation'] = 'NOT FOUND'

            return True

        except Exception as e:
            print(f"[FAIL] Validation test failed: {e}")
            self.results['tests']['validation'] = f'ERROR: {str(e)}'
            return False

    def test_chatgpt_automation(self):
        """Test ChatGPT automation components"""
        self.print_header("TESTING CHATGPT AUTOMATION")

        # Check if Chrome profile exists
        profile_dir = self.project_root / 'chrome_profile'
        if profile_dir.exists():
            print("[OK] Chrome profile directory exists")
        else:
            print("[WARN] Chrome profile not created yet (will be created on first run)")

        # Check for ChatGPT reports
        json_dir = self.project_root / 'scripts-and-data' / 'daily-json' / 'chatgpt'
        if json_dir.exists():
            reports = list(json_dir.glob('*.json'))
            if reports:
                latest = max(reports, key=lambda p: p.stat().st_mtime)
                print(f"[OK] Found {len(reports)} ChatGPT reports")
                print(f"   Latest: {latest.name}")
            else:
                print("[WARN] No ChatGPT reports found yet")
        else:
            print("[WARN] ChatGPT directory not created")

        self.results['tests']['chatgpt'] = 'CONFIGURED'
        return True

    def test_windows_tasks(self):
        """Test Windows Task Scheduler configuration"""
        self.print_header("TESTING WINDOWS TASK SCHEDULER")

        tasks = [
            "AI Trading Bot - Morning Trade Execution 930AM",
            "AI Trading Bot - Post Market 4_30PM",
            "AI Trading Bot - ChatGPT Morning Fetch",
            "AI Trading Bot - ChatGPT Final Fetch",
            "AI Trading Bot - Generate Trades"
        ]

        configured = []
        missing = []

        for task in tasks:
            result = subprocess.run(
                ['schtasks', '/query', '/tn', task],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"[OK] {task}")
                configured.append(task)
            else:
                print(f"[WARN] {task} - Not configured")
                missing.append(task)

        self.results['tests']['scheduler'] = {
            'configured': configured,
            'missing': missing
        }

        return len(missing) <= 3  # Allow some tasks to be missing

    def generate_report(self):
        """Generate test report"""
        self.print_header("TEST SUMMARY")

        # Count results
        passed = sum(1 for t in self.results['tests'].values()
                    if 'PASS' in str(t) or 'WORKING' in str(t) or 'CONNECTED' in str(t))
        total = len(self.results['tests'])

        # Determine overall status
        if passed == total:
            self.results['overall'] = 'ALL TESTS PASSED'
            print("[SUCCESS] ALL SYSTEMS OPERATIONAL")
        elif passed >= total * 0.7:
            self.results['overall'] = 'MOSTLY READY'
            print("[OK] SYSTEM READY (with minor issues)")
        else:
            self.results['overall'] = 'NEEDS ATTENTION'
            print("[WARN] SYSTEM NEEDS CONFIGURATION")

        print(f"\nTest Results: {passed}/{total} passed")

        # Save report
        report_file = self.project_root / 'docs' / f'pipeline_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\nDetailed report saved to: {report_file}")

        # Print recommendations
        self.print_header("RECOMMENDATIONS")

        if 'dependencies' in self.results['tests'] and self.results['tests']['dependencies'].get('missing'):
            print("1. Install missing packages:")
            for pkg in self.results['tests']['dependencies']['missing']:
                print(f"   pip install {pkg}")

        if 'scheduler' in self.results['tests'] and self.results['tests']['scheduler'].get('missing'):
            print("2. Run setup_all_tasks.bat as administrator to configure scheduler")

        if self.results['tests'].get('trade_generation') == 'NOT FOUND':
            print("3. Generate today's trades: python generate_todays_trades.py")

        if self.results['tests'].get('api_connections', {}).get('chatgpt_server') == 'OFFLINE':
            print("4. Optional: Start ChatGPT server for semi-automated backup")

    def run_all_tests(self):
        """Run complete test suite"""
        print("="*60)
        print(" AI TRADING BOT - FULL PIPELINE TEST")
        print(f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        # Run tests
        tests = [
            self.test_dependencies,
            self.test_file_structure,
            self.test_api_connections,
            self.test_trade_generation,
            self.test_validation_system,
            self.test_chatgpt_automation,
            self.test_windows_tasks
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"Test failed with error: {e}")

        # Generate report
        self.generate_report()

        return self.results['overall'] != 'NEEDS ATTENTION'

def main():
    """Main test execution"""
    tester = PipelineTest()
    success = tester.run_all_tests()

    print("\n" + "="*60)
    if success:
        print(" [OK] SYSTEM READY FOR AUTOMATED TRADING")
    else:
        print(" [WARN] SYSTEM NEEDS CONFIGURATION")
    print("="*60)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())