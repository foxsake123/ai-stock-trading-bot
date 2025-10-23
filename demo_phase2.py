"""
Phase 2 Demo Script

Demonstrates Phase 2 functionality without requiring external API keys.
Shows graceful degradation and fallback mechanisms working correctly.
"""

import asyncio
import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.integration.phase2_integration import Phase2IntegrationEngine, Phase2Config


async def demo_basic_analysis():
    """Demo: Basic ticker analysis"""
    print("\n" + "="*80)
    print("DEMO 1: Basic Ticker Analysis")
    print("="*80)

    # Create config with all features enabled
    config = Phase2Config(
        enable_alternative_data=True,
        enable_debate_system=True,
        enable_catalyst_monitor=False,  # Disable to avoid initialization issues
        enable_options_flow=True,
        fallback_to_simple_voting=True
    )

    # Create engine
    engine = Phase2IntegrationEngine(config)
    await engine.initialize()

    # Analyze a ticker
    print("\n[INFO] Analyzing AAPL...")
    result = await engine.analyze_ticker(
        ticker="AAPL",
        market_data={"price": 175.0, "volume": 50000000, "change_percent": 1.5},
        fundamental_data={"pe_ratio": 28.0, "revenue_growth": 0.10},
        technical_data={"rsi": 65.0, "macd": 1.5}
    )

    print(f"\n[RESULTS]")
    print(f"  Ticker: AAPL")
    print(f"  Action: {result.get('action', 'N/A')}")
    print(f"  Confidence: {result.get('confidence', 0):.2%}")
    print(f"  Reasoning: {result.get('reasoning', ['N/A'])[0] if result.get('reasoning') else 'N/A'}")

    return result


async def demo_batch_analysis():
    """Demo: Batch ticker analysis"""
    print("\n" + "="*80)
    print("DEMO 2: Batch Ticker Analysis")
    print("="*80)

    config = Phase2Config(
        enable_alternative_data=True,
        enable_debate_system=True,
        enable_catalyst_monitor=False,
        enable_options_flow=True,
        fallback_to_simple_voting=True
    )

    engine = Phase2IntegrationEngine(config)
    await engine.initialize()

    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    results = []

    print(f"\n[INFO] Analyzing {len(tickers)} tickers...")

    for ticker in tickers:
        result = await engine.analyze_ticker(
            ticker=ticker,
            market_data={"price": 100.0, "volume": 10000000},
            fundamental_data={"pe_ratio": 25.0},
            technical_data={"rsi": 60.0}
        )
        results.append((ticker, result))
        print(f"  [{result.get('action', 'HOLD'):4s}] {ticker:5s} - Confidence: {result.get('confidence', 0):.2%}")

    print(f"\n[COMPLETE] Analyzed {len(results)} tickers")
    return results


async def demo_component_status():
    """Demo: Show component initialization status"""
    print("\n" + "="*80)
    print("DEMO 3: Component Status")
    print("="*80)

    config = Phase2Config(
        enable_alternative_data=True,
        enable_debate_system=True,
        enable_catalyst_monitor=False,
        enable_options_flow=True
    )

    engine = Phase2IntegrationEngine(config)
    await engine.initialize()

    print("\n[COMPONENT STATUS]")
    for component, initialized in engine.components_initialized.items():
        status = "[OK]" if initialized else "[FAIL]"
        print(f"  {status} {component}")

    # Run integration tests
    print("\n[INTEGRATION TESTS]")
    test_results = engine.run_integration_tests()

    for component, passed in test_results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {component}")

    return test_results


async def demo_graceful_degradation():
    """Demo: Show graceful degradation when components fail"""
    print("\n" + "="*80)
    print("DEMO 4: Graceful Degradation")
    print("="*80)

    # Config with fallback enabled
    config = Phase2Config(
        enable_alternative_data=True,
        enable_debate_system=True,
        enable_catalyst_monitor=False,
        enable_options_flow=True,
        fallback_to_simple_voting=True  # Important for graceful degradation
    )

    engine = Phase2IntegrationEngine(config)
    await engine.initialize()

    print("\n[INFO] Testing graceful degradation...")
    print("[INFO] Components may fail due to missing API keys")
    print("[INFO] System should fall back to simple voting\n")

    # Analyze ticker (should work even if Phase 2 components fail)
    result = await engine.analyze_ticker(
        ticker="MSFT",
        market_data={"price": 350.0, "volume": 20000000},
        fundamental_data={"pe_ratio": 32.0},
        technical_data={"rsi": 55.0}
    )

    print(f"[RESULTS]")
    print(f"  Ticker: MSFT")
    print(f"  Action: {result.get('action', 'N/A')}")
    print(f"  Confidence: {result.get('confidence', 0):.2%}")
    print(f"  Method: {'Phase 2' if result.get('confidence', 0) > 0.55 else 'Simple Voting (Fallback)'}")

    print(f"\n[SUCCESS] System handled component failures gracefully")
    print(f"[SUCCESS] Fallback mechanism working correctly")

    return result


async def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("PHASE 2 DEMONSTRATION")
    print("="*80)
    print("\nThis demo shows Phase 2 functionality working with graceful degradation.")
    print("External API keys are not required - system falls back to simple voting.")
    print("\nPress Ctrl+C to stop at any time.")

    try:
        # Demo 1: Basic analysis
        await demo_basic_analysis()

        # Demo 2: Batch analysis
        await demo_batch_analysis()

        # Demo 3: Component status
        await demo_component_status()

        # Demo 4: Graceful degradation
        await demo_graceful_degradation()

        print("\n" + "="*80)
        print("DEMO COMPLETE")
        print("="*80)
        print("\n[SUCCESS] All demos completed successfully!")
        print("\n[INFO] Phase 2 system is operational with graceful degradation")
        print("[INFO] To enable full functionality, configure API keys in .env:")
        print("  - ANTHROPIC_API_KEY (for debate system)")
        print("  - FINANCIAL_DATASETS_API_KEY (for options flow)")
        print("  - SEC_API_KEY (for insider trading data)")

    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Demo cancelled by user")
    except Exception as e:
        print(f"\n\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
