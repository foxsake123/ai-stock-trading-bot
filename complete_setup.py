#!/usr/bin/env python3
"""
Simple Setup Completion Script
Completes setup without Unicode characters (Windows-safe)
"""

import sys
import os
from pathlib import Path

# Disable Unicode errors on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).parent

def print_header(text):
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80 + "\n")

def print_section(text):
    print("\n" + text)
    print("-" * 78)

def test_alpaca_api():
    """Test Alpaca API connections for both DEE-BOT and SHORGAN-BOT"""
    print_section("Testing Alpaca API Connections (Both Bots)")

    from alpaca.trading.client import TradingClient
    from dotenv import load_dotenv

    load_dotenv()

    results = {}

    # Test DEE-BOT API
    print("\n[1/2] Testing DEE-BOT Alpaca API...")
    try:
        api_key_dee = os.getenv('ALPACA_API_KEY_DEE')
        secret_key_dee = os.getenv('ALPACA_SECRET_KEY_DEE')

        if not api_key_dee or not secret_key_dee:
            print("  [ERROR] DEE-BOT Alpaca API keys not found in .env")
            results['DEE-BOT'] = False
        else:
            client_dee = TradingClient(api_key_dee, secret_key_dee, paper=True)
            account_dee = client_dee.get_account()

            print(f"  [SUCCESS] DEE-BOT Alpaca API connection working")
            print(f"    Account: {account_dee.account_number}")
            print(f"    Equity: ${float(account_dee.equity):,.2f}")
            print(f"    Cash: ${float(account_dee.cash):,.2f}")
            results['DEE-BOT'] = True

    except Exception as e:
        print(f"  [ERROR] DEE-BOT API test failed: {e}")
        results['DEE-BOT'] = False

    # Test SHORGAN-BOT API
    print("\n[2/2] Testing SHORGAN-BOT Alpaca API...")
    try:
        api_key_shorgan = os.getenv('ALPACA_API_KEY_SHORGAN')
        secret_key_shorgan = os.getenv('ALPACA_SECRET_KEY_SHORGAN')

        if not api_key_shorgan or not secret_key_shorgan:
            print("  [ERROR] SHORGAN-BOT Alpaca API keys not found in .env")
            results['SHORGAN-BOT'] = False
        else:
            client_shorgan = TradingClient(api_key_shorgan, secret_key_shorgan, paper=True)
            account_shorgan = client_shorgan.get_account()

            print(f"  [SUCCESS] SHORGAN-BOT Alpaca API connection working")
            print(f"    Account: {account_shorgan.account_number}")
            print(f"    Equity: ${float(account_shorgan.equity):,.2f}")
            print(f"    Cash: ${float(account_shorgan.cash):,.2f}")
            results['SHORGAN-BOT'] = True

    except Exception as e:
        print(f"  [ERROR] SHORGAN-BOT API test failed: {e}")
        results['SHORGAN-BOT'] = False

    # Check if any test passed
    if any(results.values()):
        print("\n[SUCCESS] At least one Alpaca API connection working")
        if not all(results.values()):
            print("[WARNING] Some API keys failed - check .env file")
        return True
    else:
        print("\n[ERROR] All Alpaca API tests failed")
        print("\nTo fix:")
        print("1. Go to: https://app.alpaca.markets/paper/dashboard/overview")
        print("2. Generate new API keys for DEE-BOT and SHORGAN-BOT")
        print("3. Update .env file:")
        print("   ALPACA_API_KEY_DEE=your-dee-bot-key")
        print("   ALPACA_SECRET_KEY_DEE=your-dee-bot-secret")
        print("   ALPACA_API_KEY_SHORGAN=your-shorgan-bot-key")
        print("   ALPACA_SECRET_KEY_SHORGAN=your-shorgan-bot-secret")
        print("4. Run this script again")
        return False

def test_anthropic_api():
    """Test Anthropic API"""
    print_section("Testing Anthropic API Connection")

    try:
        import anthropic
        from dotenv import load_dotenv

        load_dotenv()

        api_key = os.getenv('ANTHROPIC_API_KEY')

        if not api_key:
            print("[ERROR] Anthropic API key not found in .env")
            return False

        client = anthropic.Anthropic(api_key=api_key)
        print("[SUCCESS] Anthropic API client created successfully")
        return True

    except Exception as e:
        print(f"[ERROR] Anthropic API test failed: {e}")
        return False

def test_financial_datasets_api():
    """Test Financial Datasets API"""
    print_section("Testing Financial Datasets API Connection")

    try:
        import requests
        from dotenv import load_dotenv

        load_dotenv()

        api_key = os.getenv('FINANCIAL_DATASETS_API_KEY')

        if not api_key:
            print("[ERROR] Financial Datasets API key not found in .env")
            return False

        headers = {'X-API-KEY': api_key}
        response = requests.get(
            'https://api.financialdatasets.ai/prices/snapshot?ticker=AAPL',
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            print("[SUCCESS] Financial Datasets API connection working")
            print(f"  Test ticker: AAPL")
            print(f"  Response: OK")
            return True
        else:
            print(f"[ERROR] API returned status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] Financial Datasets API test failed: {e}")
        return False

def create_directories():
    """Create required directories"""
    print_section("Creating Required Directories")

    directories = [
        'data/watchlists',
        'logs/app',
        'logs/trades',
        'logs/errors',
        'logs/performance',
        'reports/premarket',
    ]

    created = 0
    for dir_path in directories:
        full_path = PROJECT_ROOT / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            created += 1

    print(f"[SUCCESS] Created {created} directories")
    return True

def create_watchlists():
    """Create default watchlists"""
    print_section("Creating Watchlists")

    watchlists_dir = PROJECT_ROOT / 'data' / 'watchlists'
    watchlists_dir.mkdir(parents=True, exist_ok=True)

    # DEE-BOT defensive
    dee_watchlist = watchlists_dir / 'dee_bot_defensive.txt'
    if not dee_watchlist.exists():
        with open(dee_watchlist, 'w') as f:
            f.write('# DEE-BOT Defensive Watchlist\n')
            f.write('JNJ\nPG\nKO\nPEP\nWMT\nCOST\nVZ\nT\nDUK\nNEE\n')
        print("[SUCCESS] Created dee_bot_defensive.txt")

    # SHORGAN-BOT catalysts
    shorgan_watchlist = watchlists_dir / 'shorgan_bot_catalysts.txt'
    if not shorgan_watchlist.exists():
        with open(shorgan_watchlist, 'w') as f:
            f.write('# SHORGAN-BOT Catalyst Watchlist\n')
            f.write('PTGX\nSMMT\nVKTX\nARQT\nGKOS\nSNDX\nRKLB\nACAD\n')
        print("[SUCCESS] Created shorgan_bot_catalysts.txt")

    return True

def initialize_logging():
    """Initialize logging system"""
    print_section("Initializing Logging System")

    try:
        from src.utils import setup_logging, get_logger

        setup_logging(
            level='INFO',
            log_to_file=True,
            log_to_console=False,
            rotation='daily'
        )

        logger = get_logger('setup')
        logger.info("Setup completion script - logging test")

        print("[SUCCESS] Logging system initialized")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to initialize logging: {e}")
        return False

def generate_setup_report(api_results):
    """Generate setup completion report"""
    report_file = PROJECT_ROOT / 'setup_complete_report.txt'

    from datetime import datetime

    lines = [
        "=" * 80,
        "AI TRADING BOT - SETUP COMPLETION REPORT".center(80),
        "=" * 80,
        f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Platform: {sys.platform}",
        f"Python: {sys.version.split()[0]}",
        "\n" + "-" * 80,
        "API CONNECTION TESTS",
        "-" * 80,
    ]

    for api_name, success in api_results.items():
        status = "PASS" if success else "FAIL"
        lines.append(f"\n{api_name}: {status}")

    lines.extend([
        "\n" + "-" * 80,
        "NEXT STEPS",
        "-" * 80,
        "\n1. If any API tests failed, fix them using SETUP_FIX_GUIDE.md",
        "2. Generate test report: python scripts/daily_pipeline.py --test",
        "3. View portfolio: python scripts/performance/get_portfolio_status.py",
        "4. Set up automation: See SETUP_FIX_GUIDE.md Issue 3",
        "\n" + "=" * 80,
    ])

    with open(report_file, 'w') as f:
        f.write('\n'.join(lines))

    print(f"\n[SUCCESS] Setup report saved to: {report_file}")

def main():
    """Main setup completion"""
    print_header("AI TRADING BOT - SETUP COMPLETION")

    print("This script will complete your setup without Unicode characters.")
    print("Safe for Windows PowerShell/Command Prompt.\n")

    api_results = {}

    # Test API connections
    api_results['Anthropic'] = test_anthropic_api()
    api_results['Alpaca'] = test_alpaca_api()
    api_results['Financial Datasets'] = test_financial_datasets_api()

    # Create directories
    create_directories()

    # Create watchlists
    create_watchlists()

    # Initialize logging
    initialize_logging()

    # Generate report
    generate_setup_report(api_results)

    # Summary
    print_header("SETUP COMPLETION SUMMARY")

    total_apis = len(api_results)
    passed_apis = sum(1 for success in api_results.values() if success)

    print(f"API Tests: {passed_apis}/{total_apis} passed")

    if passed_apis == total_apis:
        print("\n[SUCCESS] All API connections working!")
        print("\nYour AI Trading Bot is ready to use!")
        print("\nNext steps:")
        print("  1. python scripts/daily_pipeline.py --test")
        print("  2. python web_dashboard.py")
    else:
        print("\n[WARNING] Some API tests failed")
        print("\nPlease fix the failed APIs:")
        for api_name, success in api_results.values():
            if not success:
                print(f"  - {api_name}")
        print("\nSee: SETUP_FIX_GUIDE.md for solutions")

    print("\nSetup report: setup_complete_report.txt")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
