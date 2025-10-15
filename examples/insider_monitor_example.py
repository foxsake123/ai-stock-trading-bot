"""
Example usage of Insider Transaction Monitoring
Demonstrates how to use the insider monitor module
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from data_sources.insider_monitor import InsiderMonitor, get_insider_signals
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def example_basic_usage():
    """
    Example 1: Basic usage with get_insider_signals convenience function
    """
    print("=" * 70)
    print("EXAMPLE 1: Basic Insider Signals")
    print("=" * 70)
    print()

    # Mock API client for demonstration
    # In production, use: from financial_datasets import FinancialDatasetsClient
    # fd_client = FinancialDatasetsClient(api_key=os.getenv('FINANCIAL_DATASETS_API_KEY'))

    class MockAPIClient:
        """Mock API client for demonstration purposes"""

        def get_filings(self, ticker, filing_type, limit):
            """Return mock Form 4 filings"""
            mock_filings = {
                'AAPL': [
                    {
                        'filing_date': '2025-10-12T00:00:00',
                        'transaction_date': '2025-10-12T00:00:00',
                        'reporting_owner': 'Tim Cook',
                        'title': 'CEO',
                        'transaction_type': 'PURCHASE',
                        'shares_traded': 10000,
                        'price_per_share': 175.0
                    },
                    {
                        'filing_date': '2025-10-10T00:00:00',
                        'transaction_date': '2025-10-10T00:00:00',
                        'reporting_owner': 'Luca Maestri',
                        'title': 'CFO',
                        'transaction_type': 'PURCHASE',
                        'shares_traded': 5000,
                        'price_per_share': 175.0
                    }
                ],
                'MSFT': [
                    {
                        'filing_date': '2025-10-13T00:00:00',
                        'transaction_date': '2025-10-13T00:00:00',
                        'reporting_owner': 'Satya Nadella',
                        'title': 'CEO',
                        'transaction_type': 'SALE',
                        'shares_traded': 50000,
                        'price_per_share': 300.0
                    }
                ],
                'TSLA': []
            }
            return mock_filings.get(ticker, [])

    # Create mock client
    mock_client = MockAPIClient()

    # Get insider signals for multiple tickers
    tickers = ['AAPL', 'MSFT', 'TSLA']
    signals = get_insider_signals(tickers, mock_client, days=30)

    # Print the formatted report
    print(signals['report'])

    # Print summary statistics
    print("\nSummary Statistics:")
    print(f"  Tickers with signals: {signals['summary']['total_tickers']}")
    print(f"  Total transactions: {signals['summary']['total_transactions']}")
    print(f"  Bullish signals: {signals['summary']['bullish_signals']}")
    print(f"  Bearish signals: {signals['summary']['bearish_signals']}")
    print()


def example_advanced_usage():
    """
    Example 2: Advanced usage with InsiderMonitor class
    """
    print("=" * 70)
    print("EXAMPLE 2: Advanced Usage - Custom Filtering")
    print("=" * 70)
    print()

    class MockAPIClient:
        """Mock API client"""

        def get_filings(self, ticker, filing_type, limit):
            return [
                {
                    'filing_date': '2025-10-15T00:00:00',
                    'transaction_date': '2025-10-15T00:00:00',
                    'reporting_owner': 'Jane Doe',
                    'title': 'President',
                    'transaction_type': 'BUY',
                    'shares_traded': 20000,
                    'price_per_share': 100.0
                },
                {
                    'filing_date': '2025-10-14T00:00:00',
                    'transaction_date': '2025-10-14T00:00:00',
                    'reporting_owner': 'John Smith',
                    'title': 'Director',
                    'transaction_type': 'SELL',
                    'shares_traded': 1000,
                    'price_per_share': 100.0
                }
            ]

    # Create monitor with custom configuration
    monitor = InsiderMonitor(MockAPIClient())

    # Customize thresholds
    print(f"Default significance threshold: ${monitor.significance_threshold:,.0f}")
    monitor.significance_threshold = 1_000_000  # $1M
    print(f"Updated significance threshold: ${monitor.significance_threshold:,.0f}")
    print()

    # Fetch transactions for a single ticker
    transactions = monitor.fetch_recent_transactions('NVDA', days=30)

    print(f"Found {len(transactions)} total transactions for NVDA")
    for t in transactions:
        print(f"  {t.transaction_date.strftime('%Y-%m-%d')}: "
              f"{t.insider_name} ({t.title}) - "
              f"{t.transaction_type} {t.shares:,} shares @ ${t.price:.2f} "
              f"= ${t.value:,.0f} [{t.signal}]")
    print()

    # Get significant transactions only
    significant = monitor.get_significant_transactions(['NVDA'], days=30)

    if 'NVDA' in significant:
        print(f"Significant transactions: {len(significant['NVDA'])}")
    else:
        print("No significant transactions found (all below new $1M threshold)")
    print()


def example_signal_interpretation():
    """
    Example 3: Interpreting insider signals
    """
    print("=" * 70)
    print("EXAMPLE 3: Signal Interpretation Guide")
    print("=" * 70)
    print()

    class MockAPIClient:
        def get_filings(self, ticker, filing_type, limit):
            return []

    monitor = InsiderMonitor(MockAPIClient())

    # Test various scenarios
    scenarios = [
        ('BUY', 600_000, 'CEO', 'C-suite buy >$500K'),
        ('BUY', 400_000, 'Director', 'Non-C-suite buy <$500K'),
        ('SELL', 1_500_000, 'CFO', 'C-suite sell >$1M'),
        ('SELL', 800_000, 'President', 'C-suite sell <$1M'),
        ('SELL', 2_000_000, 'Director', 'Large non-C-suite sell'),
        ('SELL', 300_000, 'VP Engineering', 'Routine sell'),
    ]

    print("Signal determination for various scenarios:\n")
    print(f"{'Transaction':<35} {'Type':<8} {'Value':<12} {'Title':<15} {'Signal':<10}")
    print("-" * 80)

    for trans_type, value, title, description in scenarios:
        signal = monitor._determine_signal(trans_type, value, title)
        signal_icon = "[BUY]" if signal == "BULLISH" else "[SELL]" if signal == "BEARISH" else "[HOLD]"
        print(f"{description:<35} {trans_type:<8} ${value:>10,} {title:<15} {signal_icon} {signal}")

    print("\nInterpretation:")
    print("  [BUY] BULLISH   - Likely positive signal, insiders buying")
    print("  [SELL] BEARISH  - Caution warranted, significant selling")
    print("  [HOLD] NEUTRAL  - Routine activity, likely not predictive")
    print()


def example_integration_with_strategy():
    """
    Example 4: Integration with trading strategy
    """
    print("=" * 70)
    print("EXAMPLE 4: Integration with Trading Strategy")
    print("=" * 70)
    print()

    class MockAPIClient:
        def get_filings(self, ticker, filing_type, limit):
            # Return heavy insider buying for demonstration
            return [
                {
                    'filing_date': f'2025-10-{10+i}T00:00:00',
                    'transaction_date': f'2025-10-{10+i}T00:00:00',
                    'reporting_owner': f'Executive {i+1}',
                    'title': ['CEO', 'CFO', 'President'][i % 3],
                    'transaction_type': 'BUY',
                    'shares_traded': 10000 + i * 1000,
                    'price_per_share': 50.0
                }
                for i in range(3)
            ]

    def analyze_ticker_with_insider_data(ticker):
        """Example function showing how to integrate insider data into analysis"""

        monitor = InsiderMonitor(MockAPIClient())

        # Get recent insider transactions
        signals = get_insider_signals([ticker], monitor.api, days=30)

        # Extract metrics
        bullish = signals['summary']['bullish_signals']
        bearish = signals['summary']['bearish_signals']
        total = signals['summary']['total_transactions']

        print(f"Analyzing {ticker}:")
        print(f"  Insider signals: {total} transactions ({bullish} bullish, {bearish} bearish)")

        # Determine conviction boost
        conviction_boost = 0.0

        if bullish >= 3 and bearish == 0:
            conviction_boost = 0.20  # +20% conviction for consensus buying
            print(f"  [STRONG BUY] Multiple insider buys detected")

        elif bullish >= 2 and bullish > bearish:
            conviction_boost = 0.10  # +10% conviction for net buying
            print(f"  [BUY] Net insider buying detected")

        elif bearish >= 2 and bearish > bullish:
            conviction_boost = -0.10  # -10% conviction for net selling
            print(f"  [CAUTION] Net insider selling detected")

        else:
            print(f"  [NEUTRAL] Mixed or routine insider activity")

        print(f"  Conviction adjustment: {conviction_boost:+.1%}")
        print()

        return conviction_boost

    # Analyze multiple tickers
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    for ticker in tickers:
        analyze_ticker_with_insider_data(ticker)


def main():
    """Run all examples"""
    print("\n")
    print("*" * 70)
    print("INSIDER TRANSACTION MONITORING - EXAMPLE USAGE")
    print("*" * 70)
    print("\n")

    example_basic_usage()
    print("\n")

    example_advanced_usage()
    print("\n")

    example_signal_interpretation()
    print("\n")

    example_integration_with_strategy()
    print("\n")

    print("*" * 70)
    print("Examples complete!")
    print("*" * 70)
    print()
    print("Next steps:")
    print("1. Replace MockAPIClient with real FinancialDatasetsClient")
    print("2. Add to daily_premarket_report.py for automated monitoring")
    print("3. Integrate with multi-agent validation system")
    print("4. Track insider signal accuracy over time")
    print()


if __name__ == "__main__":
    main()
