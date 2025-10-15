"""
Example usage of Google Trends Monitoring
Demonstrates how to use the Google Trends module for trading signals
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from data_sources.google_trends_monitor import GoogleTrendsMonitor, get_trends_signals
from datetime import datetime
import pandas as pd


def create_mock_pytrends():
    """Create mock pytrends client for demonstration"""
    from unittest.mock import Mock

    client = Mock()

    # Mock interest over time
    def mock_interest_over_time():
        """Return mock interest data"""
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')

        # Simulate different trend patterns
        ticker = client.last_keyword

        if ticker == 'AAPL':
            # Rising trend with breakout
            interest = [50] * 60 + [60] * 20 + [85] * 10
        elif ticker == 'TSLA':
            # Volatile with high interest
            interest = [70] * 30 + [85] * 30 + [75] * 30
        elif ticker == 'NVDA':
            # Stable high interest
            interest = [80] * 90
        elif ticker == 'AMC':
            # Falling from peak
            interest = [90] * 30 + [60] * 30 + [30] * 30
        else:
            # Low interest
            interest = [15] * 90

        df = pd.DataFrame({ticker: interest}, index=dates)
        return df

    # Mock related queries
    def mock_related_queries():
        """Return mock related queries"""
        ticker = client.last_keyword
        if ticker == 'AAPL':
            rising_df = pd.DataFrame({
                'query': ['AAPL stock price', 'buy AAPL', 'AAPL earnings', 'Apple stock', 'AAPL forecast']
            })
            return {ticker: {'rising': rising_df}}
        return {ticker: {'rising': None}}

    # Mock build_payload
    def mock_build_payload(kw_list, timeframe, geo):
        """Mock build payload"""
        client.last_keyword = kw_list[0]

    client.interest_over_time = mock_interest_over_time
    client.related_queries = mock_related_queries
    client.build_payload = mock_build_payload

    return client


def example_basic_usage():
    """Example 1: Basic usage with get_trends_signals"""
    print("=" * 70)
    print("EXAMPLE 1: Basic Google Trends Analysis")
    print("=" * 70)
    print()

    # Create mock client
    mock_client = create_mock_pytrends()

    # Get trends for multiple tickers
    tickers = ['AAPL', 'TSLA', 'NVDA', 'AMC', 'XYZ']
    signals = get_trends_signals(tickers, mock_client)

    # Print formatted report
    print(signals['report'])

    # Print summary
    print("\nDetailed Summary:")
    print(f"  Total analyzed: {signals['summary']['total_analyzed']}")
    print(f"  Bullish signals: {signals['summary']['bullish_signals']}")
    print(f"  Bearish signals: {signals['summary']['bearish_signals']}")
    print(f"  Breakouts detected: {signals['summary']['breakouts']}")
    print()


def example_single_ticker_analysis():
    """Example 2: Detailed single ticker analysis"""
    print("=" * 70)
    print("EXAMPLE 2: Detailed Single Ticker Analysis")
    print("=" * 70)
    print()

    monitor = GoogleTrendsMonitor(create_mock_pytrends())

    # Analyze AAPL
    trend_data = monitor.analyze_ticker('AAPL', company_name='Apple Inc')

    print(f"Ticker: {trend_data.ticker}")
    print(f"Current Interest: {trend_data.current_interest}/100")
    print(f"7-Day Average: {trend_data.avg_interest_7d:.1f}")
    print(f"30-Day Average: {trend_data.avg_interest_30d:.1f}")
    print(f"Peak Interest: {trend_data.peak_interest} (on {trend_data.peak_date.strftime('%Y-%m-%d')})")
    print()
    print(f"Trend Direction: {trend_data.trend_direction}")
    print(f"Momentum Score: {trend_data.momentum_score:+.2f}")
    print(f"Is Breakout: {trend_data.is_breakout}")
    print(f"Signal: {trend_data.signal}")
    print()

    if trend_data.related_queries:
        print(f"Related Queries ({len(trend_data.related_queries)}):")
        for query in trend_data.related_queries:
            print(f"  - {query}")
    else:
        print("No related queries found")
    print()


def example_compare_tickers():
    """Example 3: Compare relative interest across tickers"""
    print("=" * 70)
    print("EXAMPLE 3: Ticker Comparison (Relative Interest)")
    print("=" * 70)
    print()

    monitor = GoogleTrendsMonitor(create_mock_pytrends())

    # Compare tech stocks
    tickers = ['AAPL', 'TSLA', 'NVDA', 'AMC']

    # Mock comparison data
    from unittest.mock import Mock
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    comparison_df = pd.DataFrame({
        'AAPL': [85] * 30,
        'TSLA': [75] * 30,
        'NVDA': [80] * 30,
        'AMC': [30] * 30
    }, index=dates)

    monitor.pytrends.interest_over_time = lambda: comparison_df

    comparison = monitor.compare_tickers(tickers)

    print(f"Winner (highest interest): {comparison.winner}")
    print()
    print("Interest Scores:")
    for ticker in tickers:
        score = comparison.interest_scores[ticker]
        strength = comparison.relative_strength[ticker]
        bar = "=" * int(strength * 50)
        print(f"  {ticker}: {score}/100 |{bar}| ({strength:.0%})")
    print()


def example_integration_with_strategy():
    """Example 4: Integration with trading strategy"""
    print("=" * 70)
    print("EXAMPLE 4: Integration with Trading Strategy")
    print("=" * 70)
    print()

    def analyze_with_trends(ticker, base_score=0.5):
        """Example function showing how to integrate trends into scoring"""

        monitor = GoogleTrendsMonitor(create_mock_pytrends())
        trend_data = monitor.analyze_ticker(ticker)

        print(f"\nAnalyzing {ticker}:")
        print(f"  Base fundamental score: {base_score:.2f}")
        print(f"  Google Trends interest: {trend_data.current_interest}/100")
        print(f"  Trend: {trend_data.trend_direction}")
        print(f"  Momentum: {trend_data.momentum_score:+.2f}")

        # Adjust score based on trends
        adjusted_score = base_score
        adjustments = []

        if trend_data.is_breakout:
            adjusted_score += 0.15
            adjustments.append("+0.15 (breakout detected)")

        elif trend_data.momentum_score > 0.5:
            adjusted_score += 0.12
            adjustments.append("+0.12 (strong momentum)")

        elif trend_data.momentum_score > 0.3:
            adjusted_score += 0.08
            adjustments.append("+0.08 (rising momentum)")

        elif trend_data.momentum_score < -0.3:
            adjusted_score -= 0.10
            adjustments.append("-0.10 (falling interest)")

        elif trend_data.current_interest < 10:
            adjusted_score -= 0.05
            adjustments.append("-0.05 (very low interest)")

        if adjustments:
            print(f"  Adjustments:")
            for adj in adjustments:
                print(f"    {adj}")
        else:
            print(f"  No adjustments (neutral trends)")

        print(f"  Final score: {adjusted_score:.2f}")

        # Determine action
        if adjusted_score >= 0.7:
            action = "STRONG BUY"
        elif adjusted_score >= 0.55:
            action = "BUY"
        elif adjusted_score <= 0.3:
            action = "SELL"
        elif adjusted_score <= 0.45:
            action = "HOLD/REDUCE"
        else:
            action = "HOLD"

        print(f"  Recommendation: {action}")

        return adjusted_score, action

    # Analyze multiple tickers
    tickers_with_scores = [
        ('AAPL', 0.65),  # Good fundamentals
        ('TSLA', 0.50),  # Neutral fundamentals
        ('NVDA', 0.70),  # Strong fundamentals
        ('AMC', 0.40),   # Weak fundamentals
    ]

    for ticker, base_score in tickers_with_scores:
        final_score, action = analyze_with_trends(ticker, base_score)

    print()


def example_different_timeframes():
    """Example 5: Different timeframes for different strategies"""
    print("=" * 70)
    print("EXAMPLE 5: Different Timeframes")
    print("=" * 70)
    print()

    monitor = GoogleTrendsMonitor(create_mock_pytrends())

    print("Analyzing AAPL across different timeframes:\n")

    timeframes = [
        ('now 1-d', 'Past 24 hours (intraday)'),
        ('today 1-m', 'Past month (short-term)'),
        ('today 3-m', 'Past 3 months (longer-term)')
    ]

    for timeframe, description in timeframes:
        # Mock data for different timeframes
        interest_data = monitor.get_interest_over_time('AAPL', timeframe=timeframe)

        if interest_data:
            print(f"{description}:")
            print(f"  Timeframe: {timeframe}")
            print(f"  Current interest: {interest_data['current']}/100")
            print(f"  Average: {interest_data['avg']:.1f}")
            print(f"  Peak: {interest_data['max']}")
            print()


def main():
    """Run all examples"""
    print("\n")
    print("*" * 70)
    print("GOOGLE TRENDS MONITORING - EXAMPLE USAGE")
    print("*" * 70)
    print("\n")
    print("NOTE: Using mock data for demonstration purposes")
    print("In production, install 'pytrends' and use real Google Trends API")
    print("\n")

    example_basic_usage()
    print("\n")

    example_single_ticker_analysis()
    print("\n")

    example_compare_tickers()
    print("\n")

    example_integration_with_strategy()
    print("\n")

    example_different_timeframes()
    print("\n")

    print("*" * 70)
    print("Examples complete!")
    print("*" * 70)
    print()
    print("Next steps:")
    print("1. Install pytrends: pip install pytrends")
    print("2. Replace mock client with real TrendReq()")
    print("3. Add to daily_premarket_report.py")
    print("4. Integrate with multi-agent validation system")
    print("5. Track trends vs price action correlation")
    print()


if __name__ == "__main__":
    main()
