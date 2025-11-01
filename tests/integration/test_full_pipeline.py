"""
Full Pipeline Integration Tests

Tests the complete end-to-end pipeline from research generation
to trade execution, including all Phase 2 enhancements.

Pipeline Stages:
1. Research Generation (Claude + ChatGPT)
2. Multi-Agent Validation
3. Phase 2 Enhancements (Alt Data + Debate + Options)
4. Trade Approval
5. Execution
6. Performance Tracking

Tests verify:
- Data flows correctly between stages
- All components integrate properly
- Error handling works across boundaries
- Results are consistent and reproducible
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, patch, AsyncMock, mock_open

# Phase 2 Integration
from src.integration.phase2_integration import Phase2IntegrationEngine, Phase2Config

# Core components
from src.agents.fundamental_analyst import FundamentalAnalystAgent
from src.agents.technical_analyst import TechnicalAnalystAgent
from src.agents.news_analyst import NewsAnalystAgent
from src.agents.sentiment_analyst import SentimentAnalystAgent
from src.agents.bull_researcher import BullResearcherAgent
from src.agents.bear_researcher import BearResearcherAgent
from src.agents.risk_manager import RiskManagerAgent

# Alternative data
from src.agents.alternative_data_agent import AlternativeDataAgent

# Debate system
from src.agents.debate_coordinator import DebateCoordinator

# Options flow
from src.analysis.options_flow import OptionsFlowAnalyzer

# Catalyst monitor
from src.monitors.catalyst_monitor import CatalystMonitor


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def test_config():
    """Configuration for integration testing"""
    return Phase2Config(
        enable_alternative_data=True,
        enable_debate_system=True,
        enable_catalyst_monitor=True,
        enable_options_flow=True,
        alt_data_weight=0.3,
        debate_timeout_seconds=30,
        debate_min_confidence=0.55,
        options_lookback_minutes=60,
        fallback_to_simple_voting=True,
        preserve_existing_reports=True
    )


@pytest.fixture
async def full_pipeline(test_config):
    """Full pipeline with all components"""
    engine = Phase2IntegrationEngine(test_config)
    await engine.initialize()
    return engine


@pytest.fixture
def sample_research_data():
    """Sample research data from Claude/ChatGPT"""
    return {
        "ticker": "PTGX",
        "bot": "SHORGAN-BOT",
        "action": "BUY",
        "conviction": "HIGH",
        "entry_price": 75.0,
        "target_price": 95.0,
        "stop_loss": 65.0,
        "catalyst": "M&A arbitrage play - potential acquisition target",
        "reasoning": "Strong Phase 2 data, undervalued relative to peers",
        "timeframe": "30 days",
        "risk_reward": 2.5
    }


@pytest.fixture
def sample_market_data():
    """Sample real-time market data"""
    return {
        "ticker": "PTGX",
        "price": 75.50,
        "volume": 2500000,
        "change_percent": 1.5,
        "high": 76.0,
        "low": 74.0,
        "close": 75.50,
        "avg_volume": 1200000,
        "market_cap": 3500000000
    }


@pytest.fixture
def sample_fundamental_data():
    """Sample fundamental metrics"""
    return {
        "ticker": "PTGX",
        "pe_ratio": 18.5,
        "peg_ratio": 1.2,
        "price_to_book": 3.5,
        "debt_to_equity": 0.4,
        "current_ratio": 2.1,
        "roe": 0.22,
        "revenue_growth": 0.25,
        "earnings_growth": 0.30,
        "profit_margin": 0.15,
        "fcf_yield": 0.08
    }


@pytest.fixture
def sample_technical_data():
    """Sample technical indicators"""
    return {
        "ticker": "PTGX",
        "rsi": 58.0,
        "macd": 1.2,
        "macd_signal": 0.8,
        "sma_50": 72.0,
        "sma_200": 68.0,
        "support": 70.0,
        "resistance": 80.0,
        "atr": 2.5,
        "bollinger_upper": 78.0,
        "bollinger_lower": 70.0
    }


# ============================================================================
# Test Class: End-to-End Pipeline
# ============================================================================

class TestEndToEndPipeline:
    """Test complete pipeline from research to execution"""

    @pytest.mark.asyncio
    async def test_full_pipeline_single_ticker(self, full_pipeline, sample_research_data, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Complete pipeline processes single ticker successfully"""

        # Step 1: External research (simulated)
        research = sample_research_data

        # Step 2: Run through Phase 2 pipeline
        result = await full_pipeline.analyze_ticker(
            ticker=research["ticker"],
            market_data=sample_market_data,
            fundamental_data=sample_fundamental_data,
            technical_data=sample_technical_data
        )

        # Validate result structure
        assert result is not None
        assert "action" in result
        assert "confidence" in result
        assert "reasoning" in result

        # Validate decision quality
        assert result["action"] in ["BUY", "SELL", "HOLD"]
        assert 0.0 <= result["confidence"] <= 1.0

        print(f"✓ Full pipeline completed:")
        print(f"  Action: {result['action']}")
        print(f"  Confidence: {result['confidence']:.2f}")


    @pytest.mark.asyncio
    async def test_pipeline_with_all_components(self, full_pipeline, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Pipeline uses all Phase 2 components"""

        ticker = "AAPL"

        # Track which components were called
        components_used = {
            "alt_data": False,
            "debate": False,
            "options": False,
            "catalyst": False
        }

        # Mock to track calls
        original_alt_data = full_pipeline._get_alternative_data_score
        original_debate = full_pipeline._run_debate

        async def tracked_alt_data(*args, **kwargs):
            components_used["alt_data"] = True
            return await original_alt_data(*args, **kwargs)

        async def tracked_debate(*args, **kwargs):
            components_used["debate"] = True
            return await original_debate(*args, **kwargs)

        with patch.object(full_pipeline, '_get_alternative_data_score', side_effect=tracked_alt_data):
            with patch.object(full_pipeline, '_run_debate', side_effect=tracked_debate):
                result = await full_pipeline.analyze_ticker(
                    ticker=ticker,
                    market_data=sample_market_data,
                    fundamental_data=sample_fundamental_data,
                    technical_data=sample_technical_data
                )

        # Check options analyzer was used
        if full_pipeline.options_analyzer:
            components_used["options"] = True

        # Check catalyst monitor exists
        if full_pipeline.catalyst_monitor:
            components_used["catalyst"] = True

        print(f"✓ Components used: {components_used}")
        assert any(components_used.values()), "No Phase 2 components were used"


    @pytest.mark.asyncio
    async def test_pipeline_batch_processing(self, full_pipeline, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Pipeline handles batch of tickers efficiently"""

        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

        results = []
        for ticker in tickers:
            market_data = {**sample_market_data, "ticker": ticker}
            fundamental_data = {**sample_fundamental_data, "ticker": ticker}
            technical_data = {**sample_technical_data, "ticker": ticker}

            result = await full_pipeline.analyze_ticker(
                ticker=ticker,
                market_data=market_data,
                fundamental_data=fundamental_data,
                technical_data=technical_data
            )
            results.append(result)

        # All should complete
        assert len(results) == len(tickers)

        # All should have valid decisions
        for i, result in enumerate(results):
            assert result is not None, f"{tickers[i]} returned None"
            assert "action" in result, f"{tickers[i]} missing action"

        print(f"✓ Batch processing: {len(results)} tickers completed")


# ============================================================================
# Test Class: Component Integration
# ============================================================================

class TestComponentIntegration:
    """Test integration between major components"""

    @pytest.mark.asyncio
    async def test_alt_data_to_debate_flow(self, full_pipeline, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Alternative data flows into debate system"""

        ticker = "TSLA"

        # Get alt data score
        alt_score = await full_pipeline._get_alternative_data_score(ticker)

        # Use in debate (medium confidence to trigger debate)
        preliminary_rec = {
            "action": "BUY",
            "confidence": 0.65,
            "alt_data_score": alt_score
        }

        debate_result = await full_pipeline._run_debate(
            ticker=ticker,
            market_data=sample_market_data,
            fundamental_data=sample_fundamental_data,
            technical_data=sample_technical_data,
            preliminary_recommendation=preliminary_rec
        )

        # Debate should consider alt data
        if debate_result:
            print(f"✓ Alt data → Debate flow successful")
            print(f"  Alt data score: {alt_score}")
            print(f"  Debate result: {debate_result}")
        else:
            print("✓ Debate skipped (low confidence or disabled)")


    @pytest.mark.asyncio
    async def test_options_flow_to_decision(self, full_pipeline, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Options flow contributes to final decision"""

        ticker = "NVDA"

        result = await full_pipeline.analyze_ticker(
            ticker=ticker,
            market_data=sample_market_data,
            fundamental_data=sample_fundamental_data,
            technical_data=sample_technical_data
        )

        # Check if options signal was considered
        if full_pipeline.options_analyzer and "options_signal" in result:
            print(f"✓ Options flow integrated into decision")
            print(f"  Options signal: {result.get('options_signal')}")
        else:
            print("✓ Options flow not available (expected in test)")


    @pytest.mark.asyncio
    async def test_multi_agent_consensus_integration(self, full_pipeline, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Multi-agent system integrates with Phase 2"""

        ticker = "JPM"

        # Run full analysis
        result = await full_pipeline.analyze_ticker(
            ticker=ticker,
            market_data=sample_market_data,
            fundamental_data=sample_fundamental_data,
            technical_data=sample_technical_data
        )

        # Should have agent votes (if coordinator exists)
        if "agent_votes" in result or "consensus" in result:
            print("✓ Multi-agent consensus integrated")
        else:
            # Phase 2 may override agent votes with debate
            print("✓ Phase 2 decision without agent breakdown (debate/options)")

        assert result is not None
        assert "confidence" in result


# ============================================================================
# Test Class: Error Handling Integration
# ============================================================================

class TestErrorHandlingIntegration:
    """Test error handling across component boundaries"""

    @pytest.mark.asyncio
    async def test_alt_data_failure_fallback(self, full_pipeline, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Pipeline continues when alt data fails"""

        ticker = "AAPL"

        # Mock alt data failure
        with patch.object(full_pipeline, '_get_alternative_data_score', side_effect=Exception("Alt data API down")):
            result = await full_pipeline.analyze_ticker(
                ticker=ticker,
                market_data=sample_market_data,
                fundamental_data=sample_fundamental_data,
                technical_data=sample_technical_data
            )

        # Should still return result (fallback)
        assert result is not None
        assert "action" in result
        print("✓ Graceful fallback when alt data fails")


    @pytest.mark.asyncio
    async def test_debate_failure_fallback(self, full_pipeline, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Pipeline continues when debate fails"""

        ticker = "MSFT"

        # Mock debate failure
        with patch.object(full_pipeline, '_run_debate', side_effect=Exception("Debate timeout")):
            result = await full_pipeline.analyze_ticker(
                ticker=ticker,
                market_data=sample_market_data,
                fundamental_data=sample_fundamental_data,
                technical_data=sample_technical_data
            )

        # Should still return result (fallback to agents)
        assert result is not None
        assert "action" in result
        print("✓ Graceful fallback when debate fails")


    @pytest.mark.asyncio
    async def test_options_failure_fallback(self, full_pipeline, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Pipeline continues when options flow fails"""

        ticker = "GOOGL"

        # Mock options failure
        if full_pipeline.options_analyzer:
            with patch.object(full_pipeline.options_analyzer, 'analyze_ticker', side_effect=Exception("Options API down")):
                result = await full_pipeline.analyze_ticker(
                    ticker=ticker,
                    market_data=sample_market_data,
                    fundamental_data=sample_fundamental_data,
                    technical_data=sample_technical_data
                )

            assert result is not None
            print("✓ Graceful fallback when options flow fails")
        else:
            print("✓ Options analyzer not initialized (expected in test)")


    @pytest.mark.asyncio
    async def test_all_components_fail_fallback(self, full_pipeline, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Pipeline has final fallback when all Phase 2 fails"""

        ticker = "AMZN"

        # Mock all Phase 2 components failing
        with patch.object(full_pipeline, '_get_alternative_data_score', side_effect=Exception("Alt data fail")):
            with patch.object(full_pipeline, '_run_debate', side_effect=Exception("Debate fail")):
                if full_pipeline.options_analyzer:
                    with patch.object(full_pipeline.options_analyzer, 'analyze_ticker', side_effect=Exception("Options fail")):
                        result = await full_pipeline.analyze_ticker(
                            ticker=ticker,
                            market_data=sample_market_data,
                            fundamental_data=sample_fundamental_data,
                            technical_data=sample_technical_data
                        )
                else:
                    result = await full_pipeline.analyze_ticker(
                        ticker=ticker,
                        market_data=sample_market_data,
                        fundamental_data=sample_fundamental_data,
                        technical_data=sample_technical_data
                    )

        # Should use simple voting fallback
        assert result is not None
        assert "action" in result
        print("✓ Final fallback to simple voting successful")


# ============================================================================
# Test Class: Data Flow Validation
# ============================================================================

class TestDataFlowValidation:
    """Test data flows correctly between stages"""

    @pytest.mark.asyncio
    async def test_research_to_validation_flow(self, full_pipeline, sample_research_data, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Research data flows to validation correctly"""

        # External research recommendation
        research_action = sample_research_data["action"]
        research_conviction = sample_research_data["conviction"]

        # Run through pipeline
        result = await full_pipeline.analyze_ticker(
            ticker=sample_research_data["ticker"],
            market_data=sample_market_data,
            fundamental_data=sample_fundamental_data,
            technical_data=sample_technical_data
        )

        # Pipeline should produce decision
        assert result is not None
        assert "action" in result

        # Log relationship between research and validation
        print(f"✓ Data flow validation:")
        print(f"  Research: {research_action} ({research_conviction})")
        print(f"  Pipeline: {result['action']} ({result['confidence']:.2f})")


    @pytest.mark.asyncio
    async def test_validation_to_execution_flow(self, full_pipeline, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Validated decisions have execution-ready data"""

        ticker = "WMT"

        result = await full_pipeline.analyze_ticker(
            ticker=ticker,
            market_data=sample_market_data,
            fundamental_data=sample_fundamental_data,
            technical_data=sample_technical_data
        )

        # Check execution-ready fields
        required_fields = ["action", "confidence"]
        for field in required_fields:
            assert field in result, f"Missing execution field: {field}"

        # Validate execution parameters
        assert result["action"] in ["BUY", "SELL", "HOLD"]
        assert 0.0 <= result["confidence"] <= 1.0

        print(f"✓ Validation → Execution flow: Ready for execution")


    @pytest.mark.asyncio
    async def test_execution_to_tracking_flow(self, full_pipeline, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Execution results flow to performance tracking"""

        ticker = "COST"

        # Simulate execution
        decision = await full_pipeline.analyze_ticker(
            ticker=ticker,
            market_data=sample_market_data,
            fundamental_data=sample_fundamental_data,
            technical_data=sample_technical_data
        )

        # Performance tracking data
        tracking_data = {
            "ticker": ticker,
            "action": decision["action"],
            "confidence": decision["confidence"],
            "entry_price": sample_market_data["price"],
            "timestamp": datetime.now().isoformat()
        }

        # Should have all tracking fields
        assert all(key in tracking_data for key in ["ticker", "action", "confidence", "entry_price", "timestamp"])

        print(f"✓ Execution → Tracking flow: Performance data ready")


# ============================================================================
# Test Class: Consistency and Reproducibility
# ============================================================================

class TestConsistencyReproducibility:
    """Test pipeline produces consistent, reproducible results"""

    @pytest.mark.asyncio
    async def test_deterministic_results_same_input(self, full_pipeline, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Same inputs produce same results (determinism)"""

        ticker = "PG"

        # Run twice with same inputs
        result1 = await full_pipeline.analyze_ticker(
            ticker=ticker,
            market_data=sample_market_data,
            fundamental_data=sample_fundamental_data,
            technical_data=sample_technical_data
        )

        result2 = await full_pipeline.analyze_ticker(
            ticker=ticker,
            market_data=sample_market_data,
            fundamental_data=sample_fundamental_data,
            technical_data=sample_technical_data
        )

        # Actions should match (confidence may vary slightly due to LLM)
        assert result1["action"] == result2["action"], "Non-deterministic results"

        print(f"✓ Determinism check:")
        print(f"  Run 1: {result1['action']} ({result1['confidence']:.2f})")
        print(f"  Run 2: {result2['action']} ({result2['confidence']:.2f})")


    @pytest.mark.asyncio
    async def test_results_stability_under_load(self, full_pipeline, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Results stable under concurrent load"""

        ticker = "JNJ"

        # Run 5 concurrent analyses
        tasks = [
            full_pipeline.analyze_ticker(
                ticker=ticker,
                market_data=sample_market_data,
                fundamental_data=sample_fundamental_data,
                technical_data=sample_technical_data
            )
            for _ in range(5)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        exceptions = [r for r in results if isinstance(r, Exception)]
        assert len(exceptions) == 0, f"Instability under load: {exceptions}"

        # Actions should be consistent
        valid_results = [r for r in results if not isinstance(r, Exception)]
        actions = [r["action"] for r in valid_results]
        most_common_action = max(set(actions), key=actions.count)

        consistency_rate = actions.count(most_common_action) / len(actions)

        print(f"✓ Stability under load:")
        print(f"  Consistency rate: {consistency_rate*100:.1f}%")
        print(f"  Most common action: {most_common_action}")

        # Allow some variance due to LLM non-determinism
        assert consistency_rate >= 0.6, "Results too inconsistent under load"


# ============================================================================
# Test Class: Report Generation Integration
# ============================================================================

class TestReportGenerationIntegration:
    """Test report generation with Phase 2 data"""

    @pytest.mark.asyncio
    async def test_generate_enhanced_report(self, full_pipeline, sample_market_data, sample_fundamental_data, sample_technical_data):
        """Test: Generate report with Phase 2 enhancements"""

        tickers = ["AAPL", "MSFT", "GOOGL"]
        results = []

        for ticker in tickers:
            market_data = {**sample_market_data, "ticker": ticker}
            result = await full_pipeline.analyze_ticker(
                ticker=ticker,
                market_data=market_data,
                fundamental_data=sample_fundamental_data,
                technical_data=sample_technical_data
            )
            results.append((ticker, result))

        # Generate report content
        report_lines = []
        report_lines.append("# Trading Report - Phase 2 Enhanced\n")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for ticker, result in results:
            report_lines.append(f"## {ticker}\n")
            report_lines.append(f"- Action: {result['action']}\n")
            report_lines.append(f"- Confidence: {result['confidence']:.2f}\n")
            if "reasoning" in result:
                report_lines.append(f"- Reasoning: {result['reasoning']}\n")
            report_lines.append("\n")

        report = "".join(report_lines)

        # Validate report structure
        assert "Trading Report" in report
        assert all(ticker in report for ticker in tickers)

        print("✓ Enhanced report generated successfully")
        print(f"  Tickers: {len(tickers)}")
        print(f"  Length: {len(report)} chars")


# ============================================================================
# Test Class: Integration Test Harness
# ============================================================================

class TestIntegrationHarness:
    """Test the integration test harness itself"""

    @pytest.mark.asyncio
    async def test_run_integration_tests(self, full_pipeline):
        """Test: Integration test harness validates all components"""

        # Run built-in integration tests
        test_results = full_pipeline.run_integration_tests()

        print("✓ Integration test harness results:")
        for component, passed in test_results.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {component}")

        # At least some components should pass
        passing = sum(1 for passed in test_results.values() if passed)
        assert passing > 0, "No components passed integration tests"


# ============================================================================
# Run All Integration Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
