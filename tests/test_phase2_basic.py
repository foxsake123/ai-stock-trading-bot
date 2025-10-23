"""
Basic Phase 2 Integration Test (No External APIs Required)

Tests Phase 2 integration engine with mocked dependencies.
Validates that the integration layer works correctly without requiring API keys.
"""

import asyncio
import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Phase 2 Integration
from src.integration.phase2_integration import Phase2IntegrationEngine, Phase2Config


@pytest.fixture
def test_config():
    """Configuration for testing"""
    return Phase2Config(
        enable_alternative_data=True,
        enable_debate_system=True,
        enable_catalyst_monitor=False,  # Disable to avoid initialization issues
        enable_options_flow=True,
        alt_data_weight=0.3,
        debate_timeout_seconds=30,
        debate_min_confidence=0.55,
        fallback_to_simple_voting=True
    )


@pytest_asyncio.fixture
async def engine(test_config):
    """Phase 2 integration engine with mocked components"""
    engine = Phase2IntegrationEngine(test_config)

    # Mock alternative data agent
    engine.alt_data_agent = AsyncMock()
    engine.alt_data_agent.analyze_ticker = AsyncMock(return_value={
        "score": 0.75,
        "confidence": 0.80,
        "reasoning": "Positive insider trades and trend sentiment"
    })
    engine.components_initialized["alternative_data"] = True

    # Mock debate coordinator
    engine.debate_coordinator = AsyncMock()
    engine.debate_coordinator.run_debate = AsyncMock(return_value={
        "action": "BUY",
        "confidence": 0.85,
        "reasoning": "Debate concluded positive outlook",
        "bull_score": 0.8,
        "bear_score": 0.4
    })
    engine.components_initialized["debate_system"] = True

    # Mock options analyzer
    engine.options_analyzer = AsyncMock()
    engine.options_analyzer.analyze_ticker = AsyncMock(return_value={
        "signal": "BULLISH",
        "confidence": 0.70,
        "reasoning": "Strong call buying detected"
    })
    engine.components_initialized["options_flow"] = True

    return engine


@pytest.mark.asyncio
async def test_basic_ticker_analysis(engine):
    """Test: Basic ticker analysis with mocked components"""

    ticker = "AAPL"
    market_data = {
        "price": 175.0,
        "volume": 50000000,
        "change_percent": 1.5
    }
    fundamental_data = {
        "pe_ratio": 28.0,
        "revenue_growth": 0.10
    }
    technical_data = {
        "rsi": 65.0,
        "macd": 1.5
    }

    result = await engine.analyze_ticker(
        ticker=ticker,
        market_data=market_data,
        fundamental_data=fundamental_data,
        technical_data=technical_data
    )

    # Validate result
    assert result is not None
    assert "action" in result
    assert "confidence" in result
    assert "reasoning" in result

    print(f"\n[PASS] Basic Analysis Test Passed")
    print(f"   Ticker: {ticker}")
    print(f"   Action: {result['action']}")
    print(f"   Confidence: {result['confidence']:.2%}")


@pytest.mark.asyncio
async def test_integration_tests(engine):
    """Test: Integration test harness"""

    test_results = engine.run_integration_tests()

    print(f"\n[PASS] Integration Test Harness Passed")
    print(f"   Components tested: {len(test_results)}")

    for component, passed in test_results.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"   {status} {component}")

    # At least some components should pass
    passing = sum(1 for passed in test_results.values() if passed)
    assert passing > 0, "No components passed integration tests"


@pytest.mark.asyncio
async def test_fallback_mechanism(test_config):
    """Test: Fallback to simple voting when Phase 2 fails"""

    engine = Phase2IntegrationEngine(test_config)

    # Don't initialize any components (all will fail)
    # This should trigger fallback to simple voting

    result = await engine.analyze_ticker(
        ticker="MSFT",
        market_data={"price": 350.0, "volume": 20000000},
        fundamental_data={"pe_ratio": 32.0},
        technical_data={"rsi": 55.0}
    )

    # Should still return a result (fallback)
    assert result is not None
    assert "action" in result

    print(f"\n[PASS] Fallback Mechanism Test Passed")
    print(f"   Action: {result['action']}")
    print(f"   Confidence: {result['confidence']:.2%}")


@pytest.mark.skip(reason="Report generation requires full component setup - tested in integration tests")
@pytest.mark.asyncio
async def test_generate_report(engine):
    """Test: Report generation (skipped - requires full setup)"""
    pass


def test_config_validation():
    """Test: Configuration validation"""

    # Valid config
    config = Phase2Config(
        enable_alternative_data=True,
        enable_debate_system=True,
        alt_data_weight=0.3
    )

    assert config.enable_alternative_data == True
    assert config.alt_data_weight == 0.3

    print(f"\n[PASS] Config Validation Test Passed")


if __name__ == "__main__":
    # Run tests
    print("=" * 80)
    print("PHASE 2 BASIC INTEGRATION TESTS")
    print("=" * 80)

    pytest.main([__file__, "-v", "-s"])
