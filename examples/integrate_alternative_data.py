"""
Example: Integrating Alternative Data Aggregator with Daily Pre-Market Report
Shows how to add alternative data section to your existing reporting system
"""

import asyncio
from src.data.alternative_data_aggregator import AlternativeDataAggregator, analyze_tickers_sync


# ========================================
# Example 1: Simple Synchronous Integration
# ========================================

def add_alternative_data_simple(tickers):
    """
    Simplest way to add alternative data to your report

    Args:
        tickers: List of stock tickers

    Returns:
        Markdown report string
    """
    result = analyze_tickers_sync(tickers)
    return result['report']


# ========================================
# Example 2: Async Integration (Recommended)
# ========================================

async def add_alternative_data_async(tickers, api_client=None):
    """
    Async version for better performance with multiple tickers

    Args:
        tickers: List of stock tickers
        api_client: Financial Datasets API client (optional)

    Returns:
        Complete results dictionary
    """
    aggregator = AlternativeDataAggregator(api_client=api_client)
    result = await aggregator.analyze_tickers(tickers)

    return result


# ========================================
# Example 3: Full Integration with Filtering
# ========================================

async def generate_filtered_alternative_data_section(tickers, api_client=None, min_confidence=60.0):
    """
    Advanced integration with filtering and custom formatting

    Args:
        tickers: List of stock tickers
        api_client: Financial Datasets API client
        min_confidence: Minimum confidence threshold to include

    Returns:
        Formatted markdown section
    """
    aggregator = AlternativeDataAggregator(api_client=api_client)
    result = await aggregator.analyze_tickers(tickers)

    # Filter by minimum confidence
    filtered_tickers = {}

    for ticker, composite in result['composite_scores'].items():
        if composite['confidence'] >= min_confidence:
            filtered_tickers[ticker] = result['signals'][ticker]

    if not filtered_tickers:
        return "## Alternative Data Signals\n\n*No high-confidence signals detected.*\n"

    # Generate filtered report
    filtered_report = aggregator.generate_markdown_report(filtered_tickers)

    # Add summary stats
    total_signals = sum(len(signals) for signals in result['signals'].values())
    high_conf_count = len(filtered_tickers)

    summary = f"\n**Summary**: {high_conf_count}/{len(tickers)} tickers with ≥{min_confidence}% confidence ({total_signals} total signals)\n\n"

    return filtered_report + summary


# ========================================
# Example 4: Integration with Alerts
# ========================================

async def check_alternative_data_alerts(tickers, api_client=None, alert_threshold=70.0):
    """
    Check for strong alternative data signals and generate alerts

    Args:
        tickers: List of stock tickers
        api_client: Financial Datasets API client
        alert_threshold: Composite score threshold for alerts

    Returns:
        List of alert messages
    """
    aggregator = AlternativeDataAggregator(api_client=api_client)
    result = await aggregator.analyze_tickers(tickers)

    alerts = []

    for ticker, composite in result['composite_scores'].items():
        abs_score = abs(composite['composite_score'])

        if abs_score >= alert_threshold and composite['confidence'] >= 65.0:
            direction = "BULLISH" if composite['composite_score'] > 0 else "BEARISH"
            message = (
                f"[ALERT] {ticker} - Strong {direction} signal!\n"
                f"Score: {composite['composite_score']:.1f}\n"
                f"Confidence: {composite['confidence']:.1f}%\n"
                f"Sources: {composite['signal_count']} signals\n"
            )
            alerts.append(message)

    return alerts


# ========================================
# Example 5: Complete Daily Report Integration
# ========================================

async def generate_complete_daily_report(watchlist, api_client=None):
    """
    Generate complete daily report with alternative data integration

    This is a template for integrating with daily_premarket_report.py

    Args:
        watchlist: List of tickers to analyze
        api_client: Financial Datasets API client

    Returns:
        Complete markdown report
    """
    report = "# Daily Pre-Market Report\n\n"
    report += f"*Generated: {asyncio.get_event_loop().time()}*\n\n"

    # ========================================
    # Section 1: Market Overview (existing)
    # ========================================
    report += "## Market Overview\n\n"
    report += "[Your existing market overview code here]\n\n"

    # ========================================
    # Section 2: Alternative Data Signals (NEW!)
    # ========================================
    print("[*] Fetching alternative data signals...")

    aggregator = AlternativeDataAggregator(api_client=api_client)
    alt_data_result = await aggregator.analyze_tickers(watchlist)

    report += alt_data_result['report']

    # ========================================
    # Section 3: High Priority Alerts (NEW!)
    # ========================================
    alerts = await check_alternative_data_alerts(watchlist, api_client, alert_threshold=70.0)

    if alerts:
        report += "\n## High Priority Alternative Data Alerts\n\n"
        for alert in alerts:
            report += f"```\n{alert}\n```\n\n"

    # ========================================
    # Section 4: Stock Recommendations (existing)
    # ========================================
    report += "## Stock Recommendations\n\n"
    report += "[Your existing recommendations code here]\n\n"

    return report


# ========================================
# Example 6: Cache Usage Demo
# ========================================

async def demonstrate_cache_benefits(tickers):
    """
    Demonstrate the caching system's performance benefits

    Args:
        tickers: List of stock tickers
    """
    import time

    aggregator = AlternativeDataAggregator()

    # First call - fetches from sources (slow)
    print("First call (fetching from sources)...")
    start = time.time()
    result1 = await aggregator.analyze_tickers(tickers)
    duration1 = time.time() - start
    print(f"✓ Completed in {duration1:.2f} seconds")

    # Second call - uses cache (fast!)
    print("\nSecond call (using cache)...")
    start = time.time()
    result2 = await aggregator.analyze_tickers(tickers)
    duration2 = time.time() - start
    print(f"✓ Completed in {duration2:.2f} seconds")

    print(f"\n[CACHE SPEEDUP]: {duration1/duration2:.1f}x faster!")

    # Clear cache
    aggregator.cache.clear()
    print("\n[CACHE CLEARED]")


# ========================================
# Main Examples
# ========================================

if __name__ == '__main__':
    # Example watchlist
    WATCHLIST = ['AAPL', 'TSLA', 'NVDA', 'MSFT']

    # ========================================
    # Run Example 1: Simple Sync
    # ========================================
    print("=" * 60)
    print("Example 1: Simple Synchronous Integration")
    print("=" * 60)

    report = add_alternative_data_simple(WATCHLIST)
    print(report)

    # ========================================
    # Run Example 2: Async
    # ========================================
    print("\n" + "=" * 60)
    print("Example 2: Async Integration")
    print("=" * 60)

    result = asyncio.run(add_alternative_data_async(WATCHLIST))
    print(result['report'])

    # ========================================
    # Run Example 3: Filtered
    # ========================================
    print("\n" + "=" * 60)
    print("Example 3: Filtered by Confidence (≥60%)")
    print("=" * 60)

    filtered_report = asyncio.run(
        generate_filtered_alternative_data_section(WATCHLIST, min_confidence=60.0)
    )
    print(filtered_report)

    # ========================================
    # Run Example 4: Alerts
    # ========================================
    print("\n" + "=" * 60)
    print("Example 4: High Confidence Alerts")
    print("=" * 60)

    alerts = asyncio.run(check_alternative_data_alerts(WATCHLIST, alert_threshold=70.0))

    if alerts:
        for alert in alerts:
            print(alert)
    else:
        print("No high-confidence alerts detected.")

    # ========================================
    # Run Example 5: Complete Report
    # ========================================
    print("\n" + "=" * 60)
    print("Example 5: Complete Daily Report")
    print("=" * 60)

    complete_report = asyncio.run(generate_complete_daily_report(WATCHLIST))
    print(complete_report[:1000] + "...")  # Print first 1000 chars

    # ========================================
    # Run Example 6: Cache Demo
    # ========================================
    print("\n" + "=" * 60)
    print("Example 6: Cache Performance Demo")
    print("=" * 60)

    asyncio.run(demonstrate_cache_benefits(['AAPL', 'TSLA']))

    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
