"""
Comprehensive Test Suite for Options Flow Analysis System

Tests:
- OptionsDataFetcher: Data fetching from multiple sources
- OptionsFlowAnalyzer: Flow analysis and signal generation
- UnusualActivityDetector: Unusual pattern detection
- Integration tests
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.options_data_fetcher import (
    OptionsDataFetcher,
    OptionsContract,
    OptionsFlow,
    OptionType,
    TradeType
)
from src.analysis.options_flow import (
    OptionsFlowAnalyzer,
    FlowSignal,
    PutCallMetrics,
    FlowImbalance,
    DeltaGammaExposure,
    OptionsFlowSignal
)
from src.signals.unusual_activity import (
    UnusualActivityDetector,
    ActivityLevel,
    UnusualTrade,
    MultiLegStrategy,
    StrategyType
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_contract():
    """Sample options contract"""
    return OptionsContract(
        ticker="AAPL",
        expiration=datetime.now() + timedelta(days=30),
        strike=150.0,
        option_type=OptionType.CALL,
        last_price=5.0,
        bid=4.90,
        ask=5.10,
        mark=5.0,
        volume=1000,
        open_interest=5000,
        delta=0.5,
        gamma=0.02,
        theta=-0.05,
        vega=0.15,
        implied_volatility=0.25
    )


@pytest.fixture
def sample_flow(sample_contract):
    """Sample options flow"""
    return OptionsFlow(
        ticker="AAPL",
        timestamp=datetime.now(),
        contract=sample_contract,
        premium=50000,  # $50k
        size=100,
        price=5.0,
        trade_type=TradeType.NORMAL,
        side="BUY",
        sentiment="",  # Will be determined
        spot_price=150.0
    )


@pytest.fixture
def mock_data_fetcher():
    """Mock OptionsDataFetcher"""
    fetcher = Mock(spec=OptionsDataFetcher)
    fetcher.fetch_options_chain = AsyncMock(return_value=[])
    fetcher.fetch_options_flow = AsyncMock(return_value=[])
    fetcher.get_spot_price = AsyncMock(return_value=150.0)
    return fetcher


@pytest.fixture
def analyzer(mock_data_fetcher):
    """OptionsFlowAnalyzer instance"""
    return OptionsFlowAnalyzer(data_fetcher=mock_data_fetcher)


@pytest.fixture
def detector():
    """UnusualActivityDetector instance"""
    return UnusualActivityDetector()


# ============================================================================
# OPTIONS DATA FETCHER TESTS
# ============================================================================

class TestOptionsDataFetcher:
    """Test OptionsDataFetcher"""

    def test_initialization(self):
        """Test fetcher initialization"""
        fetcher = OptionsDataFetcher(
            yahoo_enabled=True,
            fd_api_key="test_key",
            cache_ttl=60
        )

        assert fetcher.yahoo_enabled is True
        assert fetcher.fd_api_key == "test_key"
        assert fetcher.cache_ttl == 60
        assert len(fetcher.chain_cache) == 0
        assert len(fetcher.flow_cache) == 0

    @pytest.mark.asyncio
    async def test_fetch_options_chain_cache(self):
        """Test chain caching"""
        fetcher = OptionsDataFetcher(cache_ttl=60)

        # Mock fetch method
        contracts = [
            OptionsContract(
                ticker="AAPL",
                expiration=datetime.now() + timedelta(days=30),
                strike=150.0,
                option_type=OptionType.CALL,
                last_price=5.0,
                bid=4.90,
                ask=5.10,
                mark=5.0,
                volume=1000,
                open_interest=5000
            )
        ]

        with patch.object(fetcher, '_fetch_from_yahoo', new=AsyncMock(return_value=contracts)):
            # First call should hit API
            result1 = await fetcher.fetch_options_chain("AAPL")
            assert len(result1) == 1

            # Second call should use cache
            result2 = await fetcher.fetch_options_chain("AAPL")
            assert len(result2) == 1
            assert result1 == result2


class TestOptionsContract:
    """Test OptionsContract dataclass"""

    def test_contract_creation(self, sample_contract):
        """Test creating options contract"""
        assert sample_contract.ticker == "AAPL"
        assert sample_contract.strike == 150.0
        assert sample_contract.option_type == OptionType.CALL
        assert sample_contract.volume == 1000
        assert sample_contract.open_interest == 5000

    def test_mark_calculation(self):
        """Test mark price calculation"""
        contract = OptionsContract(
            ticker="AAPL",
            expiration=datetime.now() + timedelta(days=30),
            strike=150.0,
            option_type=OptionType.CALL,
            last_price=5.0,
            bid=4.90,
            ask=5.10,
            mark=0,  # Should be calculated
            volume=1000,
            open_interest=5000
        )

        assert contract.mark == 5.0  # (4.90 + 5.10) / 2


class TestOptionsFlow:
    """Test OptionsFlow dataclass"""

    def test_flow_creation(self, sample_flow):
        """Test creating options flow"""
        assert sample_flow.ticker == "AAPL"
        assert sample_flow.premium == 50000
        assert sample_flow.size == 100
        assert sample_flow.side == "BUY"

    def test_sentiment_determination_call_buy(self):
        """Test sentiment for call buy"""
        contract = OptionsContract(
            ticker="AAPL",
            expiration=datetime.now() + timedelta(days=30),
            strike=150.0,
            option_type=OptionType.CALL,
            last_price=5.0,
            bid=4.90,
            ask=5.10,
            mark=5.0,
            volume=1000,
            open_interest=5000
        )

        flow = OptionsFlow(
            ticker="AAPL",
            timestamp=datetime.now(),
            contract=contract,
            premium=50000,
            size=100,
            price=5.0,
            trade_type=TradeType.NORMAL,
            side="BUY",
            sentiment="",
            spot_price=150.0
        )

        assert flow.sentiment == "BULLISH"

    def test_sentiment_determination_put_buy(self):
        """Test sentiment for put buy"""
        contract = OptionsContract(
            ticker="AAPL",
            expiration=datetime.now() + timedelta(days=30),
            strike=150.0,
            option_type=OptionType.PUT,
            last_price=5.0,
            bid=4.90,
            ask=5.10,
            mark=5.0,
            volume=1000,
            open_interest=5000
        )

        flow = OptionsFlow(
            ticker="AAPL",
            timestamp=datetime.now(),
            contract=contract,
            premium=50000,
            size=100,
            price=5.0,
            trade_type=TradeType.NORMAL,
            side="BUY",
            sentiment="",
            spot_price=150.0
        )

        assert flow.sentiment == "BEARISH"

    def test_large_trade_detection(self):
        """Test large trade flag"""
        contract = OptionsContract(
            ticker="AAPL",
            expiration=datetime.now() + timedelta(days=30),
            strike=150.0,
            option_type=OptionType.CALL,
            last_price=5.0,
            bid=4.90,
            ask=5.10,
            mark=5.0,
            volume=1000,
            open_interest=5000
        )

        flow = OptionsFlow(
            ticker="AAPL",
            timestamp=datetime.now(),
            contract=contract,
            premium=150000,  # >$100k
            size=300,
            price=5.0,
            trade_type=TradeType.NORMAL,
            side="BUY",
            sentiment="",
            spot_price=150.0
        )

        assert flow.is_large_trade is True


# ============================================================================
# OPTIONS FLOW ANALYZER TESTS
# ============================================================================

class TestPutCallMetrics:
    """Test PutCallMetrics"""

    def test_ratio_calculation(self):
        """Test put/call ratio calculation"""
        metrics = PutCallMetrics(
            ticker="AAPL",
            timestamp=datetime.now(),
            call_volume=1000,
            put_volume=1500,
            volume_ratio=0,  # Will be calculated
            call_premium=50000,
            put_premium=75000,
            premium_ratio=0,  # Will be calculated
            call_oi=5000,
            put_oi=7500,
            oi_ratio=0  # Will be calculated
        )

        assert metrics.volume_ratio == 1.5
        assert metrics.premium_ratio == 1.5
        assert metrics.oi_ratio == 1.5


class TestFlowImbalance:
    """Test FlowImbalance"""

    def test_imbalance_calculation(self):
        """Test flow imbalance calculation"""
        imbalance = FlowImbalance(
            ticker="AAPL",
            timestamp=datetime.now(),
            call_buys_premium=100000,
            call_sells_premium=50000,
            net_call_premium=0,  # Will be calculated
            put_buys_premium=30000,
            put_sells_premium=40000,
            net_put_premium=0,  # Will be calculated
            total_imbalance=0,  # Will be calculated
            imbalance_ratio=0  # Will be calculated
        )

        assert imbalance.net_call_premium == 50000  # 100k - 50k
        assert imbalance.net_put_premium == -10000  # 30k - 40k
        assert imbalance.total_imbalance == 60000  # 50k - (-10k)
        assert imbalance.imbalance_ratio > 0  # Bullish


class TestOptionsFlowAnalyzer:
    """Test OptionsFlowAnalyzer"""

    def test_initialization(self, analyzer):
        """Test analyzer initialization"""
        assert analyzer.lookback_days == 30
        assert analyzer.large_trade_threshold == 100000
        assert analyzer.unusual_volume_multiplier == 3.0

    @pytest.mark.asyncio
    async def test_analyze_ticker_basic(self, analyzer, mock_data_fetcher):
        """Test basic ticker analysis"""
        # Mock data
        contracts = [
            OptionsContract(
                ticker="AAPL",
                expiration=datetime.now() + timedelta(days=30),
                strike=150.0,
                option_type=OptionType.CALL,
                last_price=5.0,
                bid=4.90,
                ask=5.10,
                mark=5.0,
                volume=1000,
                open_interest=5000,
                delta=0.5
            )
        ]

        flows = [
            OptionsFlow(
                ticker="AAPL",
                timestamp=datetime.now(),
                contract=contracts[0],
                premium=50000,
                size=100,
                price=5.0,
                trade_type=TradeType.NORMAL,
                side="BUY",
                sentiment="BULLISH",
                spot_price=150.0
            )
        ]

        mock_data_fetcher.fetch_options_chain = AsyncMock(return_value=contracts)
        mock_data_fetcher.fetch_options_flow = AsyncMock(return_value=flows)
        mock_data_fetcher.get_spot_price = AsyncMock(return_value=150.0)

        signal = await analyzer.analyze_ticker("AAPL")

        assert isinstance(signal, OptionsFlowSignal)
        assert signal.ticker == "AAPL"
        assert signal.signal in [FlowSignal.BULLISH, FlowSignal.BEARISH, FlowSignal.NEUTRAL, FlowSignal.VERY_BULLISH, FlowSignal.VERY_BEARISH]
        assert 0 <= signal.confidence <= 1

    def test_evaluate_put_call_signal_bullish(self, analyzer):
        """Test put/call signal evaluation - bullish"""
        metrics = PutCallMetrics(
            ticker="AAPL",
            timestamp=datetime.now(),
            call_volume=2000,
            put_volume=500,
            volume_ratio=0.25,
            call_premium=100000,
            put_premium=25000,
            premium_ratio=0.25,
            call_oi=10000,
            put_oi=2500,
            oi_ratio=0.25,
            avg_volume_ratio=1.0,
            volume_ratio_deviation=-2.5  # Low ratio = bullish
        )

        signal = analyzer._evaluate_put_call_signal(metrics)
        assert signal == FlowSignal.BULLISH

    def test_evaluate_put_call_signal_bearish(self, analyzer):
        """Test put/call signal evaluation - bearish"""
        metrics = PutCallMetrics(
            ticker="AAPL",
            timestamp=datetime.now(),
            call_volume=500,
            put_volume=2000,
            volume_ratio=4.0,
            call_premium=25000,
            put_premium=100000,
            premium_ratio=4.0,
            call_oi=2500,
            put_oi=10000,
            oi_ratio=4.0,
            avg_volume_ratio=1.0,
            volume_ratio_deviation=2.5  # High ratio = bearish
        )

        signal = analyzer._evaluate_put_call_signal(metrics)
        assert signal == FlowSignal.BEARISH


# ============================================================================
# UNUSUAL ACTIVITY DETECTOR TESTS
# ============================================================================

class TestUnusualActivityDetector:
    """Test UnusualActivityDetector"""

    def test_initialization(self, detector):
        """Test detector initialization"""
        assert detector.block_threshold == 100000
        assert detector.volume_multiplier == 3.0
        assert detector.strike_threshold == 0.05
        assert detector.oi_threshold == 500

    def test_detect_block_trade(self, detector):
        """Test block trade detection"""
        contract = OptionsContract(
            ticker="AAPL",
            expiration=datetime.now() + timedelta(days=30),
            strike=150.0,
            option_type=OptionType.CALL,
            last_price=5.0,
            bid=4.90,
            ask=5.10,
            mark=5.0,
            volume=2000,
            open_interest=5000
        )

        flow = OptionsFlow(
            ticker="AAPL",
            timestamp=datetime.now(),
            contract=contract,
            premium=150000,  # >$100k = block trade
            size=300,
            price=5.0,
            trade_type=TradeType.BLOCK,
            side="BUY",
            sentiment="BULLISH",
            spot_price=150.0
        )

        unusual_trades = detector.detect_unusual_trades(
            ticker="AAPL",
            flows=[flow],
            chain=[contract],
            spot_price=150.0
        )

        assert len(unusual_trades) > 0
        assert unusual_trades[0].is_block_trade is True

    def test_detect_sweep_order(self, detector):
        """Test sweep order detection"""
        contract = OptionsContract(
            ticker="AAPL",
            expiration=datetime.now() + timedelta(days=30),
            strike=150.0,
            option_type=OptionType.CALL,
            last_price=5.0,
            bid=4.90,
            ask=5.10,
            mark=5.0,
            volume=1000,
            open_interest=5000
        )

        flow = OptionsFlow(
            ticker="AAPL",
            timestamp=datetime.now(),
            contract=contract,
            premium=50000,
            size=100,
            price=5.0,
            trade_type=TradeType.SWEEP,
            side="BUY",
            sentiment="BULLISH",
            spot_price=150.0
        )

        unusual_trades = detector.detect_unusual_trades(
            ticker="AAPL",
            flows=[flow],
            chain=[contract],
            spot_price=150.0
        )

        assert len(unusual_trades) > 0
        assert unusual_trades[0].is_sweep is True

    def test_activity_level_extreme(self, detector):
        """Test extreme activity level detection"""
        # Create high volume flows
        contract = OptionsContract(
            ticker="AAPL",
            expiration=datetime.now() + timedelta(days=30),
            strike=150.0,
            option_type=OptionType.CALL,
            last_price=5.0,
            bid=4.90,
            ask=5.10,
            mark=5.0,
            volume=100,  # Normal volume
            open_interest=5000
        )

        flows = [
            OptionsFlow(
                ticker="AAPL",
                timestamp=datetime.now(),
                contract=contract,
                premium=50000,
                size=1000,  # 10x normal = extreme
                price=5.0,
                trade_type=TradeType.NORMAL,
                side="BUY",
                sentiment="BULLISH",
                spot_price=150.0
            )
        ]

        # Update historical volume
        detector.update_historical_volume("AAPL", contract)

        level = detector.get_activity_level(
            ticker="AAPL",
            flows=flows,
            chain=[contract]
        )

        # Should be elevated or higher
        assert level in [ActivityLevel.ELEVATED, ActivityLevel.HIGH, ActivityLevel.VERY_HIGH, ActivityLevel.EXTREME]

    def test_detect_call_spread(self, detector):
        """Test call spread detection"""
        contract1 = OptionsContract(
            ticker="AAPL",
            expiration=datetime.now() + timedelta(days=30),
            strike=145.0,
            option_type=OptionType.CALL,
            last_price=7.0,
            bid=6.90,
            ask=7.10,
            mark=7.0,
            volume=100,
            open_interest=1000,
            delta=0.6
        )

        contract2 = OptionsContract(
            ticker="AAPL",
            expiration=datetime.now() + timedelta(days=30),
            strike=155.0,
            option_type=OptionType.CALL,
            last_price=3.0,
            bid=2.90,
            ask=3.10,
            mark=3.0,
            volume=100,
            open_interest=1000,
            delta=0.4
        )

        flow1 = OptionsFlow(
            ticker="AAPL",
            timestamp=datetime.now(),
            contract=contract1,
            premium=70000,
            size=100,
            price=7.0,
            trade_type=TradeType.NORMAL,
            side="BUY",  # Buy lower strike
            sentiment="BULLISH",
            spot_price=150.0
        )

        flow2 = OptionsFlow(
            ticker="AAPL",
            timestamp=datetime.now(),
            contract=contract2,
            premium=30000,
            size=100,
            price=3.0,
            trade_type=TradeType.NORMAL,
            side="SELL",  # Sell higher strike
            sentiment="BULLISH",
            spot_price=150.0
        )

        strategies = detector.detect_multi_leg_strategies(
            ticker="AAPL",
            flows=[flow1, flow2],
            time_window_seconds=60
        )

        # Should detect call spread
        assert len(strategies) > 0
        assert strategies[0].strategy_type == StrategyType.CALL_SPREAD


class TestUnusualTrade:
    """Test UnusualTrade dataclass"""

    def test_reasoning_generation(self):
        """Test reasoning generation"""
        contract = OptionsContract(
            ticker="AAPL",
            expiration=datetime.now() + timedelta(days=30),
            strike=150.0,
            option_type=OptionType.CALL,
            last_price=5.0,
            bid=4.90,
            ask=5.10,
            mark=5.0,
            volume=2000,
            open_interest=5000
        )

        flow = OptionsFlow(
            ticker="AAPL",
            timestamp=datetime.now(),
            contract=contract,
            premium=150000,
            size=300,
            price=5.0,
            trade_type=TradeType.SWEEP,
            side="BUY",
            sentiment="BULLISH",
            spot_price=150.0
        )

        unusual = UnusualTrade(
            flow=flow,
            is_block_trade=True,
            is_sweep=True,
            is_unusual_volume=True,
            volume_multiple=5.0
        )

        assert len(unusual.reasoning) > 0
        assert "block trade" in unusual.reasoning[0].lower()
        assert "sweep" in unusual.reasoning[1].lower()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests"""

    @pytest.mark.asyncio
    async def test_end_to_end_analysis(self, mock_data_fetcher):
        """Test complete end-to-end analysis"""
        # Create analyzer
        analyzer = OptionsFlowAnalyzer(data_fetcher=mock_data_fetcher)

        # Mock complete data
        contracts = [
            OptionsContract(
                ticker="AAPL",
                expiration=datetime.now() + timedelta(days=30),
                strike=150.0,
                option_type=OptionType.CALL,
                last_price=5.0,
                bid=4.90,
                ask=5.10,
                mark=5.0,
                volume=1000,
                open_interest=5000,
                delta=0.5,
                gamma=0.02
            ),
            OptionsContract(
                ticker="AAPL",
                expiration=datetime.now() + timedelta(days=30),
                strike=150.0,
                option_type=OptionType.PUT,
                last_price=4.0,
                bid=3.90,
                ask=4.10,
                mark=4.0,
                volume=500,
                open_interest=2500,
                delta=-0.5,
                gamma=0.02
            )
        ]

        flows = [
            OptionsFlow(
                ticker="AAPL",
                timestamp=datetime.now(),
                contract=contracts[0],
                premium=150000,  # Large call buy
                size=300,
                price=5.0,
                trade_type=TradeType.BLOCK,
                side="BUY",
                sentiment="BULLISH",
                spot_price=150.0
            )
        ]

        mock_data_fetcher.fetch_options_chain = AsyncMock(return_value=contracts)
        mock_data_fetcher.fetch_options_flow = AsyncMock(return_value=flows)
        mock_data_fetcher.get_spot_price = AsyncMock(return_value=150.0)

        # Run analysis
        signal = await analyzer.analyze_ticker("AAPL")

        # Verify results
        assert signal.ticker == "AAPL"
        assert signal.signal in [FlowSignal.BULLISH, FlowSignal.VERY_BULLISH]  # Large call buy = bullish
        assert signal.confidence > 0
        assert signal.large_trades_count == 1
        assert signal.put_call_metrics.call_volume > signal.put_call_metrics.put_volume


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
