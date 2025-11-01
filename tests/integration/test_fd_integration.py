#!/usr/bin/env python3
"""
Test Financial Datasets API Integration
Verify that the API is working and data is being retrieved correctly
"""

import os
import sys
import json
from datetime import datetime

# Set a test API key if not in environment
if not os.getenv('FINANCIAL_DATASETS_API_KEY'):
    print("=" * 60)
    print("IMPORTANT: Add your Financial Datasets API key to .env file:")
    print("FINANCIAL_DATASETS_API_KEY=your_api_key_here")
    print("=" * 60)
    print()
    # For testing, you can temporarily set it here:
    # os.environ['FINANCIAL_DATASETS_API_KEY'] = 'your_key_here'

from scripts.automation.financial_datasets_integration import FinancialDatasetsAPI

def test_basic_functionality():
    """Test basic API functionality"""
    print("=" * 60)
    print("TESTING FINANCIAL DATASETS API INTEGRATION")
    print("=" * 60)
    print()

    # Initialize API
    fd_api = FinancialDatasetsAPI()

    # Test ticker
    ticker = "AAPL"
    print(f"Testing with ticker: {ticker}")
    print("-" * 40)

    # 1. Test Snapshot Price
    print("\n1. Testing Snapshot Price...")
    snapshot = fd_api.get_snapshot_price(ticker)
    if snapshot:
        print(f"   [OK] Current Price: ${snapshot.get('price', 'N/A')}")
        print(f"   [OK] Change: {snapshot.get('change_percent', 'N/A')}%")
        if snapshot.get('volume'):
            print(f"   [OK] Volume: {snapshot.get('volume', 0):,}")
    else:
        print("   [FAIL] Failed to get snapshot price")

    # 2. Test Historical Prices
    print("\n2. Testing Historical Prices...")
    hist_data = fd_api.get_historical_prices(ticker, interval='day', limit=5)
    if not hist_data.empty:
        print(f"   [OK] Retrieved {len(hist_data)} days of historical data")
        print(f"   [OK] Latest Close: ${hist_data['close'].iloc[-1]:.2f}")
    else:
        print("   [FAIL] Failed to get historical prices")

    # 3. Test Financial Metrics
    print("\n3. Testing Financial Metrics...")
    metrics = fd_api.get_financial_metrics(ticker)
    if metrics:
        print(f"   [OK] P/E Ratio: {metrics.get('pe_ratio', 'N/A')}")
        print(f"   [OK] Beta: {metrics.get('beta', 'N/A')}")
        print(f"   [OK] ROE: {metrics.get('roe', 'N/A')}")
    else:
        print("   [FAIL] Failed to get financial metrics")

    # 4. Test Earnings Data
    print("\n4. Testing Earnings Data...")
    earnings = fd_api.get_earnings(ticker, limit=4)
    if earnings:
        print(f"   [OK] Retrieved {len(earnings)} earnings reports")
        latest = earnings[0] if earnings else {}
        print(f"   [OK] Latest EPS: ${latest.get('reported_eps', 'N/A')}")
        print(f"   [OK] Surprise: {latest.get('surprise_percent', 'N/A')}%")
    else:
        print("   [FAIL] Failed to get earnings data")

    # 5. Test News
    print("\n5. Testing News Data...")
    news = fd_api.get_news(ticker, limit=3)
    if news:
        print(f"   [OK] Retrieved {len(news)} news articles")
        for i, article in enumerate(news[:2], 1):
            print(f"   [OK] Article {i}: {article.get('title', 'N/A')[:60]}...")
    else:
        print("   [FAIL] Failed to get news data")

    # 6. Test Comprehensive Research
    print("\n6. Testing Comprehensive Research Generation...")
    print("   This may take 10-20 seconds...")
    research = fd_api.generate_comprehensive_research(ticker)

    if research:
        print(f"   [OK] Research generated successfully")
        print(f"   [OK] DEE-BOT Signal: {research['dee_bot_signals']['recommendation']}")
        print(f"   [OK] SHORGAN-BOT Signal: {research['shorgan_bot_signals']['recommendation']}")
        print(f"   [OK] Risks Identified: {len(research['risk_assessment'])}")
        print(f"   [OK] Opportunities: {len(research['opportunities'])}")

        # Save research to file
        output_file = f"fd_test_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(research, f, indent=2, default=str)
        print(f"\n   Full research saved to: {output_file}")
    else:
        print("   [FAIL] Failed to generate comprehensive research")

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    # Count successes
    successes = sum([
        bool(snapshot),
        not hist_data.empty,
        bool(metrics),
        bool(earnings),
        bool(news),
        bool(research)
    ])

    print(f"Successful tests: {successes}/6")

    if successes == 6:
        print("[OK] All tests passed! Financial Datasets API is working correctly.")
        print("\nNext steps:")
        print("1. The integration is ready to use")
        print("2. All yfinance calls can now be replaced")
        print("3. The multi-agent system can use this richer data")
    elif successes > 0:
        print("[WARN] Some tests passed. Check your API key and network connection.")
    else:
        print("[FAIL] All tests failed. Please verify your API key in .env file.")

    return successes == 6


def test_multi_ticker():
    """Test with multiple tickers for portfolio analysis"""
    print("\n" + "=" * 60)
    print("TESTING MULTIPLE TICKERS")
    print("=" * 60)

    fd_api = FinancialDatasetsAPI()

    # Test both DEE and SHORGAN type stocks
    tickers = {
        'DEE-BOT': ['JNJ', 'PG', 'WMT'],  # Defensive stocks
        'SHORGAN-BOT': ['SOUN', 'BBAI', 'IONQ']  # Catalyst stocks
    }

    results = {}

    for bot_type, ticker_list in tickers.items():
        print(f"\n{bot_type} Stocks:")
        print("-" * 40)

        for ticker in ticker_list:
            print(f"\nAnalyzing {ticker}...")

            # Get comprehensive research
            research = fd_api.generate_comprehensive_research(ticker)

            if research:
                if bot_type == 'DEE-BOT':
                    signal = research['dee_bot_signals']['recommendation']
                    quality = research['dee_bot_signals']['quality_score']
                    print(f"  Signal: {signal} (Quality: {quality})")
                else:
                    signal = research['shorgan_bot_signals']['recommendation']
                    catalyst = research['shorgan_bot_signals']['catalyst_score']
                    print(f"  Signal: {signal} (Catalyst: {catalyst})")

                results[ticker] = signal

    print("\n" + "=" * 60)
    print("PORTFOLIO RECOMMENDATIONS")
    print("=" * 60)

    buy_signals = [t for t, s in results.items() if s == 'BUY']
    watch_signals = [t for t, s in results.items() if s in ['HOLD', 'WATCH']]

    if buy_signals:
        print(f"BUY Signals: {', '.join(buy_signals)}")
    if watch_signals:
        print(f"WATCH/HOLD Signals: {', '.join(watch_signals)}")

    return results


if __name__ == "__main__":
    # Run basic tests
    success = test_basic_functionality()

    # If basic tests pass, run portfolio test
    if success:
        test_multi_ticker()
    else:
        print("\nSkipping multi-ticker test until basic functionality works.")
        print("\nTroubleshooting:")
        print("1. Verify your API key is in .env file")
        print("2. Check your internet connection")
        print("3. Ensure Financial Datasets subscription is active")