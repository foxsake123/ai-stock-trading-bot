"""
Test Complete Trading System
Verifies all components are working
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
import subprocess

def test_component(name, test_func):
    """Test a system component"""
    print(f"\nTesting: {name}")
    print("-" * 40)
    try:
        result = test_func()
        if result:
            print(f"✅ {name} - PASSED")
            return True
        else:
            print(f"❌ {name} - FAILED")
            return False
    except Exception as e:
        print(f"❌ {name} - ERROR: {str(e)[:100]}")
        return False

def test_chatgpt_research():
    """Test ChatGPT research file exists"""
    research_dir = Path("scripts-and-data/data/reports/weekly/chatgpt-research")
    files = list(research_dir.glob("CHATGPT_ACTUAL_*.md"))
    if files:
        print(f"  Found {len(files)} research files")
        print(f"  Latest: {max(files, key=lambda x: x.stat().st_mtime).name}")
        return True
    return False

def test_multi_agent_system():
    """Test multi-agent imports"""
    try:
        from src.agents.alternative_data_agent import AlternativeDataAgent
        from src.agents.fundamental_analyst import FundamentalAnalystAgent
        from src.agents.technical_analyst import TechnicalAnalystAgent
        print("  All agents importable")
        return True
    except ImportError as e:
        print(f"  Import error: {e}")
        return False

def test_workflow_automation():
    """Test workflow automation script"""
    workflow_script = Path("scripts-and-data/automation/complete_weekly_workflow.py")
    if workflow_script.exists():
        print(f"  Workflow script exists: {workflow_script.name}")
        return True
    return False

def test_daily_automation():
    """Test daily automation script"""
    daily_script = Path("scripts-and-data/automation/daily_automation.py")
    if daily_script.exists():
        print(f"  Daily automation exists: {daily_script.name}")
        return True
    return False

def test_telegram_config():
    """Test Telegram configuration"""
    try:
        import requests
        token = "8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c"
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url)
        if response.status_code == 200:
            print("  Telegram bot connected")
            return True
        else:
            print("  Telegram bot not responding")
            return False
    except:
        return False

def test_alpaca_connection():
    """Test Alpaca API connection"""
    try:
        import alpaca_trade_api as tradeapi

        # DEE-BOT credentials
        dee_api = tradeapi.REST(
            'PK6FZK4DAQVTD7DYVH78',
            'JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt',
            'https://paper-api.alpaca.markets'
        )

        account = dee_api.get_account()
        print(f"  DEE-BOT connected: ${float(account.portfolio_value):,.2f}")

        # SHORGAN-BOT credentials
        shorgan_api = tradeapi.REST(
            'PKJRLSB2MFEJUSK6UK2E',
            'QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic',
            'https://paper-api.alpaca.markets'
        )

        account = shorgan_api.get_account()
        print(f"  SHORGAN-BOT connected: ${float(account.portfolio_value):,.2f}")

        return True
    except Exception as e:
        print(f"  Alpaca error: {e}")
        return False

def test_execution_files():
    """Test execution file generation"""
    trades_files = list(Path(".").glob("TODAYS_TRADES_*.md"))
    consensus_files = list(Path(".").glob("CONSENSUS_TRADES_*.md"))

    if trades_files or consensus_files:
        print(f"  Found {len(trades_files)} trade files")
        print(f"  Found {len(consensus_files)} consensus files")
        if trades_files:
            print(f"  Latest: {max(trades_files, key=lambda x: x.stat().st_mtime).name}")
        return True
    return False

def test_alternative_data():
    """Test alternative data sources"""
    try:
        from data_sources.options_flow_tracker import OptionsFlowTracker
        from data_sources.reddit_wsb_scanner import RedditWSBScanner
        from data_sources.alternative_data_aggregator import AlternativeDataAggregator
        print("  Alternative data sources available")
        return True
    except ImportError as e:
        print(f"  Missing: {e}")
        return False

def main():
    """Run all system tests"""
    print("="*60)
    print("COMPLETE SYSTEM TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    tests = [
        ("ChatGPT Research Files", test_chatgpt_research),
        ("Multi-Agent System", test_multi_agent_system),
        ("Weekly Workflow", test_workflow_automation),
        ("Daily Automation", test_daily_automation),
        ("Telegram Bot", test_telegram_config),
        ("Alpaca Connection", test_alpaca_connection),
        ("Execution Files", test_execution_files),
        ("Alternative Data", test_alternative_data)
    ]

    results = []
    for name, test_func in tests:
        passed = test_component(name, test_func)
        results.append((name, passed))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\nResult: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 SYSTEM FULLY OPERATIONAL!")
        print("\nNext Steps:")
        print("1. Provide ChatGPT research on Sunday")
        print("2. Run: python scripts-and-data/automation/complete_weekly_workflow.py")
        print("3. System will handle everything else automatically")
    else:
        print("\n⚠️ SYSTEM NEEDS ATTENTION")
        print("Fix failing components before trading")

    # Quick instructions
    print("\n" + "="*60)
    print("QUICK START GUIDE")
    print("="*60)
    print("""
WEEKLY (Sunday):
1. Get research from ChatGPT.com
2. Save with: python scripts-and-data/automation/save_chatgpt_report.py
3. Process: python scripts-and-data/automation/complete_weekly_workflow.py

DAILY (Automated):
- 9:00 AM: Pre-market check
- 9:30 AM: Execute trades
- 4:30 PM: Post-market report

That's all you need to do!
""")

if __name__ == "__main__":
    main()