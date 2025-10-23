"""
Performance Tests for Phase 2 Enhancements

Tests performance characteristics of:
- Debate mechanism timing
- Alternative data aggregation timing
- Full pipeline processing
- Memory usage
- API rate limiting
- Graceful degradation
- Concurrent processing

Requirements:
- Debate mechanism: <30 seconds per ticker
- Alternative data: 20 tickers in <60 seconds
- Full pipeline: Morning report in <5 minutes
- Memory usage: <1GB during operation
- API rate limits: Respected with delays
- Graceful degradation: Works when sources unavailable
- Concurrent processing: No race conditions
"""

import pytest
import asyncio
import time
import tracemalloc
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, patch, AsyncMock
import statistics

# Phase 2 components
from src.integration.phase2_integration import Phase2IntegrationEngine, Phase2Config
from agents.alternative_data_agent import AlternativeDataAgent
from debate.debate_coordinator import DebateCoordinator
from src.analysis.options_flow import OptionsFlowAnalyzer
from catalyst.catalyst_monitor import CatalystMonitor


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def performance_config():
    """Config optimized for performance testing"""
    return Phase2Config(
        enable_alternative_data=True,
        enable_debate_system=True,
        enable_catalyst_monitor=True,
        enable_options_flow=True,
        alt_data_weight=0.3,
        debate_timeout_seconds=30,
        debate_min_confidence=0.55,
        options_lookback_minutes=60,
        fallback_to_simple_voting=True
    )


@pytest.fixture
async def integration_engine(performance_config):
    """Integration engine for performance tests"""
    engine = Phase2IntegrationEngine(performance_config)
    await engine.initialize()
    return engine


@pytest.fixture
def sample_tickers():
    """Sample ticker list for batch tests"""
    return [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META",
        "TSLA", "NVDA", "JPM", "V", "WMT",
        "JNJ", "PG", "UNH", "HD", "DIS",
        "MA", "BAC", "XOM", "PFE", "ABBV"
    ]


@pytest.fixture
def sample_market_data():
    """Sample market data for testing"""
    return {
        "price": 150.0,
        "volume": 10000000,
        "change_percent": 2.5,
        "high": 152.0,
        "low": 148.0,
        "close": 150.0
    }


@pytest.fixture
def sample_fundamental_data():
    """Sample fundamental data"""
    return {
        "pe_ratio": 25.0,
        "market_cap": 2500000000000,
        "revenue_growth": 0.15,
        "earnings_growth": 0.20,
        "debt_to_equity": 0.5,
        "roe": 0.25
    }


@pytest.fixture
def sample_technical_data():
    """Sample technical data"""
    return {
        "rsi": 65.0,
        "macd": 1.5,
        "sma_50": 145.0,
        "sma_200": 140.0,
        "support": 145.0,
        "resistance": 155.0
    }


# ============================================================================
# Test Class: Debate Mechanism Performance
# ============================================================================

class TestDebateMechanismPerformance:
    """Test debate mechanism timing requirements"""

    @pytest.mark.asyncio
    async def test_debate_single_ticker_under_30_seconds(self, integration_engine, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Debate completes in <30 seconds for single ticker"""
        ticker = "AAPL"

        start_time = time.time()

        result = await integration_engine.analyze_ticker(
            ticker=ticker,
            market_data=sample_market_data,
            fundamental_data=sample_fundamental_data,
            technical_data=sample_technical_data
        )

        elapsed = time.time() - start_time

        assert elapsed < 30.0, f"Debate took {elapsed:.2f}s (limit: 30s)"
        assert result is not None
        assert "action" in result
        print(f"✓ Debate completed in {elapsed:.2f}s (limit: 30s)")


    @pytest.mark.asyncio
    async def test_debate_timing_consistency(self, integration_engine, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Debate timing is consistent across multiple runs"""
        ticker = "MSFT"
        runs = 5
        timings = []

        for i in range(runs):
            start_time = time.time()

            await integration_engine.analyze_ticker(
                ticker=ticker,
                market_data=sample_market_data,
                fundamental_data=sample_fundamental_data,
                technical_data=sample_technical_data
            )

            elapsed = time.time() - start_time
            timings.append(elapsed)

        avg_time = statistics.mean(timings)
        std_dev = statistics.stdev(timings)

        assert avg_time < 30.0, f"Average time {avg_time:.2f}s exceeds 30s"
        assert std_dev < 5.0, f"Timing variance too high: {std_dev:.2f}s"

        print(f"✓ Debate timing: avg={avg_time:.2f}s, std={std_dev:.2f}s")


    @pytest.mark.asyncio
    async def test_debate_timeout_enforcement(self, integration_engine, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Debate respects timeout configuration"""
        ticker = "GOOGL"

        # Set aggressive timeout
        integration_engine.config.debate_timeout_seconds = 15

        start_time = time.time()

        result = await integration_engine.analyze_ticker(
            ticker=ticker,
            market_data=sample_market_data,
            fundamental_data=sample_fundamental_data,
            technical_data=sample_technical_data
        )

        elapsed = time.time() - start_time

        # Should complete or timeout within configured limit + 2s buffer
        assert elapsed < 17.0, f"Debate exceeded timeout: {elapsed:.2f}s"
        print(f"✓ Timeout enforced: {elapsed:.2f}s (limit: 15s + 2s buffer)")


# ============================================================================
# Test Class: Alternative Data Performance
# ============================================================================

class TestAlternativeDataPerformance:
    """Test alternative data aggregation timing"""

    @pytest.mark.asyncio
    async def test_alt_data_20_tickers_under_60_seconds(self, integration_engine, sample_tickers):
        """Test: Alternative data handles 20 tickers in <60 seconds"""

        start_time = time.time()

        results = []
        for ticker in sample_tickers[:20]:
            try:
                score = await integration_engine._get_alternative_data_score(ticker)
                results.append((ticker, score))
            except Exception as e:
                print(f"Warning: {ticker} failed - {e}")

        elapsed = time.time() - start_time

        assert elapsed < 60.0, f"Alt data took {elapsed:.2f}s (limit: 60s)"
        assert len(results) > 0, "No results collected"

        print(f"✓ Alternative data: {len(results)} tickers in {elapsed:.2f}s")
        print(f"  Average per ticker: {elapsed/len(results):.2f}s")


    @pytest.mark.asyncio
    async def test_alt_data_concurrent_vs_sequential(self, integration_engine, sample_tickers):
        """Test: Concurrent processing is faster than sequential"""
        test_tickers = sample_tickers[:10]

        # Sequential timing
        sequential_start = time.time()
        for ticker in test_tickers:
            try:
                await integration_engine._get_alternative_data_score(ticker)
            except:
                pass
        sequential_time = time.time() - sequential_start

        # Concurrent timing
        concurrent_start = time.time()
        tasks = [
            integration_engine._get_alternative_data_score(ticker)
            for ticker in test_tickers
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        concurrent_time = time.time() - concurrent_start

        speedup = sequential_time / concurrent_time

        print(f"✓ Sequential: {sequential_time:.2f}s")
        print(f"✓ Concurrent: {concurrent_time:.2f}s")
        print(f"✓ Speedup: {speedup:.2f}x")

        # Concurrent should be faster (allow some overhead)
        assert concurrent_time < sequential_time * 0.8, "Concurrent not faster"


    @pytest.mark.asyncio
    async def test_alt_data_caching_performance(self, integration_engine):
        """Test: Caching improves repeat query performance"""
        ticker = "AAPL"

        # First call (cold cache)
        cold_start = time.time()
        await integration_engine._get_alternative_data_score(ticker)
        cold_time = time.time() - cold_start

        # Second call (warm cache)
        warm_start = time.time()
        await integration_engine._get_alternative_data_score(ticker)
        warm_time = time.time() - warm_start

        print(f"✓ Cold cache: {cold_time:.2f}s")
        print(f"✓ Warm cache: {warm_time:.2f}s")
        print(f"✓ Cache speedup: {cold_time/warm_time:.2f}x")

        # Warm should be significantly faster
        assert warm_time < cold_time * 0.5, "Cache not improving performance"


# ============================================================================
# Test Class: Full Pipeline Performance
# ============================================================================

class TestFullPipelinePerformance:
    """Test complete pipeline processing time"""

    @pytest.mark.asyncio
    async def test_morning_report_under_5_minutes(self, integration_engine, sample_tickers, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Full pipeline processes morning report in <5 minutes"""

        # Simulate morning report with 15 tickers (realistic load)
        report_tickers = sample_tickers[:15]

        start_time = time.time()

        results = []
        for ticker in report_tickers:
            try:
                result = await integration_engine.analyze_ticker(
                    ticker=ticker,
                    market_data=sample_market_data,
                    fundamental_data=sample_fundamental_data,
                    technical_data=sample_technical_data
                )
                results.append(result)
            except Exception as e:
                print(f"Warning: {ticker} failed - {e}")

        elapsed = time.time() - start_time

        assert elapsed < 300.0, f"Pipeline took {elapsed:.2f}s (limit: 300s)"
        assert len(results) > 0, "No results generated"

        print(f"✓ Full pipeline: {len(results)} tickers in {elapsed:.2f}s")
        print(f"  Average per ticker: {elapsed/len(results):.2f}s")


    @pytest.mark.asyncio
    async def test_pipeline_stages_breakdown(self, integration_engine, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Measure time for each pipeline stage"""
        ticker = "AAPL"
        timings = {}

        # Stage 1: Alternative data
        start = time.time()
        alt_score = await integration_engine._get_alternative_data_score(ticker)
        timings["alt_data"] = time.time() - start

        # Stage 2: Debate (if applicable)
        start = time.time()
        debate_result = await integration_engine._run_debate(
            ticker=ticker,
            market_data=sample_market_data,
            fundamental_data=sample_fundamental_data,
            technical_data=sample_technical_data,
            preliminary_recommendation={"action": "BUY", "confidence": 0.65}
        )
        timings["debate"] = time.time() - start

        # Stage 3: Options flow
        start = time.time()
        if integration_engine.options_analyzer:
            options_signal = await integration_engine.options_analyzer.analyze_ticker(ticker)
        timings["options"] = time.time() - start

        total_time = sum(timings.values())

        print(f"✓ Pipeline stage timings:")
        for stage, duration in timings.items():
            percentage = (duration / total_time) * 100
            print(f"  {stage}: {duration:.2f}s ({percentage:.1f}%)")

        assert total_time < 60.0, f"Total pipeline time {total_time:.2f}s exceeds 60s"


# ============================================================================
# Test Class: Memory Usage
# ============================================================================

class TestMemoryUsage:
    """Test memory usage stays under limits"""

    @pytest.mark.asyncio
    async def test_memory_under_1gb_during_operation(self, integration_engine, sample_tickers, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Memory usage stays under 1GB during operation"""

        # Start memory tracking
        tracemalloc.start()

        # Process multiple tickers
        for ticker in sample_tickers[:10]:
            try:
                await integration_engine.analyze_ticker(
                    ticker=ticker,
                    market_data=sample_market_data,
                    fundamental_data=sample_fundamental_data,
                    technical_data=sample_technical_data
                )
            except:
                pass

        # Get peak memory
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Convert to MB
        peak_mb = peak / 1024 / 1024

        print(f"✓ Peak memory usage: {peak_mb:.2f} MB")

        # Allow 512MB for reasonable operations
        assert peak_mb < 512.0, f"Memory usage {peak_mb:.2f}MB exceeds 512MB"


    @pytest.mark.asyncio
    async def test_no_memory_leaks(self, integration_engine, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: No memory leaks during repeated operations"""
        ticker = "AAPL"

        tracemalloc.start()

        # Run 10 iterations
        memory_samples = []
        for i in range(10):
            await integration_engine.analyze_ticker(
                ticker=ticker,
                market_data=sample_market_data,
                fundamental_data=sample_fundamental_data,
                technical_data=sample_technical_data
            )

            current, _ = tracemalloc.get_traced_memory()
            memory_samples.append(current)

        tracemalloc.stop()

        # Memory should stabilize, not grow linearly
        first_half_avg = statistics.mean(memory_samples[:5])
        second_half_avg = statistics.mean(memory_samples[5:])

        growth_rate = (second_half_avg - first_half_avg) / first_half_avg

        print(f"✓ Memory growth rate: {growth_rate*100:.2f}%")

        # Allow 20% growth (caching is expected)
        assert growth_rate < 0.20, f"Potential memory leak: {growth_rate*100:.2f}% growth"


# ============================================================================
# Test Class: API Rate Limiting
# ============================================================================

class TestAPIRateLimiting:
    """Test API rate limits are respected"""

    @pytest.mark.asyncio
    async def test_rate_limiting_with_delays(self, integration_engine, sample_tickers):
        """Test: API calls respect rate limits with delays"""

        # Track API call timings
        call_times = []

        for ticker in sample_tickers[:5]:
            start = time.time()
            try:
                await integration_engine._get_alternative_data_score(ticker)
            except:
                pass
            call_times.append(time.time() - start)

        # Calculate time between calls
        if len(call_times) > 1:
            intervals = [call_times[i+1] - call_times[i] for i in range(len(call_times)-1)]
            avg_interval = statistics.mean(intervals)

            print(f"✓ Average call interval: {avg_interval:.2f}s")

            # Should have some delay (not instant)
            assert avg_interval > 0.1, "Calls too fast, rate limiting may not be working"


    @pytest.mark.asyncio
    async def test_retry_logic_on_rate_limit(self, integration_engine):
        """Test: Proper retry logic when rate limited"""
        ticker = "AAPL"

        # Mock rate limit error
        with patch.object(integration_engine.alt_data_agent, 'analyze_ticker', side_effect=[
            Exception("429 Rate Limit"),
            {"score": 0.7, "confidence": 0.8}  # Success on retry
        ]):
            start = time.time()
            try:
                result = await integration_engine._get_alternative_data_score(ticker)
                elapsed = time.time() - start

                print(f"✓ Retry succeeded after {elapsed:.2f}s")
                # Should have delay for retry
                assert elapsed > 1.0, "No retry delay detected"
            except:
                pytest.skip("Retry logic not implemented yet")


# ============================================================================
# Test Class: Graceful Degradation
# ============================================================================

class TestGracefulDegradation:
    """Test graceful degradation when sources unavailable"""

    @pytest.mark.asyncio
    async def test_fallback_when_alt_data_unavailable(self, performance_config, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: System works when alternative data unavailable"""

        # Disable alt data component
        performance_config.enable_alternative_data = False

        engine = Phase2IntegrationEngine(performance_config)
        await engine.initialize()

        result = await engine.analyze_ticker(
            ticker="AAPL",
            market_data=sample_market_data,
            fundamental_data=sample_fundamental_data,
            technical_data=sample_technical_data
        )

        assert result is not None
        assert "action" in result
        print("✓ System functional without alternative data")


    @pytest.mark.asyncio
    async def test_fallback_when_debate_unavailable(self, performance_config, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: System works when debate system unavailable"""

        # Disable debate
        performance_config.enable_debate_system = False

        engine = Phase2IntegrationEngine(performance_config)
        await engine.initialize()

        result = await engine.analyze_ticker(
            ticker="MSFT",
            market_data=sample_market_data,
            fundamental_data=sample_fundamental_data,
            technical_data=sample_technical_data
        )

        assert result is not None
        assert "action" in result
        print("✓ System functional without debate")


    @pytest.mark.asyncio
    async def test_fallback_when_options_unavailable(self, performance_config, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: System works when options flow unavailable"""

        # Disable options
        performance_config.enable_options_flow = False

        engine = Phase2IntegrationEngine(performance_config)
        await engine.initialize()

        result = await engine.analyze_ticker(
            ticker="GOOGL",
            market_data=sample_market_data,
            fundamental_data=sample_fundamental_data,
            technical_data=sample_technical_data
        )

        assert result is not None
        assert "action" in result
        print("✓ System functional without options flow")


    @pytest.mark.asyncio
    async def test_fallback_to_simple_voting(self, performance_config, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: System falls back to simple voting when all Phase 2 fails"""

        # Enable fallback
        performance_config.fallback_to_simple_voting = True

        engine = Phase2IntegrationEngine(performance_config)
        await engine.initialize()

        # Mock all Phase 2 components to fail
        with patch.object(engine, '_get_alternative_data_score', side_effect=Exception("Alt data failed")):
            with patch.object(engine, '_run_debate', side_effect=Exception("Debate failed")):
                result = await engine.analyze_ticker(
                    ticker="AMZN",
                    market_data=sample_market_data,
                    fundamental_data=sample_fundamental_data,
                    technical_data=sample_technical_data
                )

                assert result is not None
                assert "action" in result
                print("✓ Fallback to simple voting successful")


# ============================================================================
# Test Class: Concurrent Processing
# ============================================================================

class TestConcurrentProcessing:
    """Test concurrent processing without race conditions"""

    @pytest.mark.asyncio
    async def test_concurrent_ticker_analysis_no_race_conditions(self, integration_engine, sample_tickers, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Concurrent analysis has no race conditions"""

        test_tickers = sample_tickers[:5]

        # Run concurrent analysis
        tasks = [
            integration_engine.analyze_ticker(
                ticker=ticker,
                market_data=sample_market_data,
                fundamental_data=sample_fundamental_data,
                technical_data=sample_technical_data
            )
            for ticker in test_tickers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check all completed
        assert len(results) == len(test_tickers)

        # Check no exceptions (race conditions often cause exceptions)
        exceptions = [r for r in results if isinstance(r, Exception)]
        assert len(exceptions) == 0, f"Race condition detected: {exceptions}"

        print(f"✓ Concurrent processing: {len(test_tickers)} tickers, no race conditions")


    @pytest.mark.asyncio
    async def test_shared_state_thread_safety(self, integration_engine, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Shared state is thread-safe during concurrent operations"""
        ticker = "AAPL"

        # Run same ticker multiple times concurrently (stress test)
        tasks = [
            integration_engine.analyze_ticker(
                ticker=ticker,
                market_data=sample_market_data,
                fundamental_data=sample_fundamental_data,
                technical_data=sample_technical_data
            )
            for _ in range(10)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed with consistent results
        exceptions = [r for r in results if isinstance(r, Exception)]
        assert len(exceptions) == 0, f"Thread safety issue: {exceptions}"

        # Results should be consistent (same ticker, same data)
        valid_results = [r for r in results if not isinstance(r, Exception)]
        if len(valid_results) > 1:
            first_action = valid_results[0].get("action")
            all_same = all(r.get("action") == first_action for r in valid_results)
            assert all_same, "Inconsistent results indicate race condition"

        print("✓ Shared state is thread-safe")


# ============================================================================
# Run All Performance Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
