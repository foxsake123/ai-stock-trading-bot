"""
Comprehensive tests for Alternative Data Aggregator
Target: 80%+ coverage
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import pandas as pd

from src.data.alternative_data_aggregator import (
    AlternativeDataSignal,
    SignalType,
    SignalCache,
    AlternativeDataAggregator,
    analyze_tickers_sync
)


@pytest.fixture
def sample_bullish_signal():
    """Sample bullish signal"""
    return AlternativeDataSignal(
        ticker='AAPL',
        source='insider',
        signal_type=SignalType.BULLISH,
        strength=80.0,
        confidence=75.0,
        timestamp=datetime.now(),
        metadata={'transaction_value': 1000000}
    )


@pytest.fixture
def sample_bearish_signal():
    """Sample bearish signal"""
    return AlternativeDataSignal(
        ticker='AAPL',
        source='options',
        signal_type=SignalType.BEARISH,
        strength=70.0,
        confidence=65.0,
        timestamp=datetime.now(),
        metadata={'put_call_ratio': 1.5}
    )


@pytest.fixture
def sample_neutral_signal():
    """Sample neutral signal"""
    return AlternativeDataSignal(
        ticker='AAPL',
        source='social',
        signal_type=SignalType.NEUTRAL,
        strength=50.0,
        confidence=50.0,
        timestamp=datetime.now(),
        metadata={'mentions': 0}
    )


@pytest.fixture
def aggregator():
    """Create aggregator instance"""
    return AlternativeDataAggregator(api_client=None)


class TestAlternativeDataSignal:
    """Test AlternativeDataSignal dataclass"""

    def test_signal_creation(self, sample_bullish_signal):
        """Test creating a signal"""
        assert sample_bullish_signal.ticker == 'AAPL'
        assert sample_bullish_signal.source == 'insider'
        assert sample_bullish_signal.signal_type == SignalType.BULLISH
        assert sample_bullish_signal.strength == 80.0
        assert sample_bullish_signal.confidence == 75.0
        assert isinstance(sample_bullish_signal.timestamp, datetime)

    def test_signal_to_dict(self, sample_bullish_signal):
        """Test converting signal to dictionary"""
        signal_dict = sample_bullish_signal.to_dict()

        assert signal_dict['ticker'] == 'AAPL'
        assert signal_dict['source'] == 'insider'
        assert signal_dict['signal_type'] == 'BULLISH'
        assert signal_dict['strength'] == 80.0
        assert signal_dict['confidence'] == 75.0
        assert 'timestamp' in signal_dict
        assert 'metadata' in signal_dict

    def test_signal_types(self):
        """Test all signal types"""
        assert SignalType.BULLISH.value == 'BULLISH'
        assert SignalType.BEARISH.value == 'BEARISH'
        assert SignalType.NEUTRAL.value == 'NEUTRAL'


class TestSignalCache:
    """Test signal caching functionality"""

    def test_cache_initialization(self):
        """Test cache initialization"""
        cache = SignalCache(ttl_seconds=3600)
        assert cache.ttl_seconds == 3600
        assert len(cache.cache) == 0

    def test_cache_set_and_get(self, sample_bullish_signal):
        """Test setting and getting cached data"""
        cache = SignalCache(ttl_seconds=3600)
        signals = [sample_bullish_signal]

        cache.set('AAPL', signals)
        cached_signals = cache.get('AAPL')

        assert cached_signals is not None
        assert len(cached_signals) == 1
        assert cached_signals[0].ticker == 'AAPL'

    def test_cache_miss(self):
        """Test cache miss"""
        cache = SignalCache(ttl_seconds=3600)
        cached_signals = cache.get('TSLA')

        assert cached_signals is None

    def test_cache_expiration(self, sample_bullish_signal):
        """Test cache expiration"""
        cache = SignalCache(ttl_seconds=1)  # 1 second TTL
        signals = [sample_bullish_signal]

        cache.set('AAPL', signals)

        # Should be cached
        assert cache.get('AAPL') is not None

        # Wait for expiration
        import time
        time.sleep(2)

        # Should be expired
        assert cache.get('AAPL') is None

    def test_cache_clear(self, sample_bullish_signal):
        """Test clearing cache"""
        cache = SignalCache(ttl_seconds=3600)
        signals = [sample_bullish_signal]

        cache.set('AAPL', signals)
        cache.set('TSLA', signals)

        assert len(cache.cache) == 2

        cache.clear()

        assert len(cache.cache) == 0


class TestAlternativeDataAggregator:
    """Test aggregator functionality"""

    def test_aggregator_initialization(self, aggregator):
        """Test aggregator initialization"""
        assert aggregator.api_client is None
        assert isinstance(aggregator.cache, SignalCache)
        assert aggregator.SIGNAL_WEIGHTS['insider'] == 0.25
        assert aggregator.SIGNAL_WEIGHTS['options'] == 0.25
        assert aggregator.SIGNAL_WEIGHTS['social'] == 0.20
        assert aggregator.SIGNAL_WEIGHTS['trends'] == 0.15

    def test_signal_weights_sum_to_one(self, aggregator):
        """Test that signal weights sum to 1.0"""
        total_weight = sum(aggregator.SIGNAL_WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.01

    def test_calculate_composite_score_empty(self, aggregator):
        """Test composite score with no signals"""
        composite = aggregator.calculate_composite_score([])

        assert composite['composite_score'] == 0.0
        assert composite['signal_type'] == 'NEUTRAL'
        assert composite['confidence'] == 0.0
        assert composite['signal_count'] == 0

    def test_calculate_composite_score_bullish(self, aggregator, sample_bullish_signal):
        """Test composite score with bullish signals"""
        signals = [sample_bullish_signal]
        composite = aggregator.calculate_composite_score(signals)

        assert composite['composite_score'] > 0
        assert composite['signal_type'] == 'BULLISH'
        assert composite['confidence'] > 0
        assert composite['signal_count'] == 1

    def test_calculate_composite_score_bearish(self, aggregator, sample_bearish_signal):
        """Test composite score with bearish signals"""
        signals = [sample_bearish_signal]
        composite = aggregator.calculate_composite_score(signals)

        assert composite['composite_score'] < 0
        assert composite['signal_type'] == 'BEARISH'
        assert composite['confidence'] > 0
        assert composite['signal_count'] == 1

    def test_calculate_composite_score_neutral(self, aggregator, sample_neutral_signal):
        """Test composite score with neutral signals"""
        signals = [sample_neutral_signal]
        composite = aggregator.calculate_composite_score(signals)

        assert abs(composite['composite_score']) <= 10
        assert composite['signal_type'] == 'NEUTRAL'

    def test_calculate_composite_score_mixed(self, aggregator, sample_bullish_signal, sample_bearish_signal):
        """Test composite score with mixed signals"""
        signals = [sample_bullish_signal, sample_bearish_signal]
        composite = aggregator.calculate_composite_score(signals)

        assert 'composite_score' in composite
        assert 'signal_type' in composite
        assert composite['signal_count'] == 2

    def test_calculate_composite_score_breakdown(self, aggregator, sample_bullish_signal, sample_bearish_signal):
        """Test composite score breakdown by source"""
        signals = [sample_bullish_signal, sample_bearish_signal]
        composite = aggregator.calculate_composite_score(signals)

        assert 'breakdown' in composite
        assert 'insider' in composite['breakdown']
        assert 'options' in composite['breakdown']

        insider_breakdown = composite['breakdown']['insider']
        assert 'strength' in insider_breakdown
        assert 'confidence' in insider_breakdown
        assert 'signal_count' in insider_breakdown
        assert 'weight' in insider_breakdown

    def test_generate_summary_table_empty(self, aggregator):
        """Test generating summary table with no data"""
        df = aggregator.generate_summary_table({})

        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_generate_summary_table(self, aggregator, sample_bullish_signal):
        """Test generating summary table"""
        ticker_signals = {
            'AAPL': [sample_bullish_signal]
        }

        df = aggregator.generate_summary_table(ticker_signals)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert 'Ticker' in df.columns
        assert 'Composite Score' in df.columns
        assert 'Signal' in df.columns
        assert 'Confidence' in df.columns
        assert df.iloc[0]['Ticker'] == 'AAPL'

    def test_generate_summary_table_sorting(self, aggregator):
        """Test summary table is sorted by composite score"""
        bullish_signal = AlternativeDataSignal(
            ticker='AAPL', source='insider', signal_type=SignalType.BULLISH,
            strength=90.0, confidence=80.0, timestamp=datetime.now(), metadata={}
        )

        neutral_signal = AlternativeDataSignal(
            ticker='TSLA', source='social', signal_type=SignalType.NEUTRAL,
            strength=50.0, confidence=50.0, timestamp=datetime.now(), metadata={}
        )

        ticker_signals = {
            'AAPL': [bullish_signal],
            'TSLA': [neutral_signal]
        }

        df = aggregator.generate_summary_table(ticker_signals)

        # AAPL should be first (higher score)
        assert df.iloc[0]['Ticker'] == 'AAPL'

    def test_generate_markdown_report_empty(self, aggregator):
        """Test generating markdown report with no data"""
        report = aggregator.generate_markdown_report({})

        assert isinstance(report, str)
        assert '## Alternative Data Signals' in report
        assert 'No alternative data signals available' in report

    def test_generate_markdown_report(self, aggregator, sample_bullish_signal):
        """Test generating markdown report"""
        ticker_signals = {
            'AAPL': [sample_bullish_signal]
        }

        report = aggregator.generate_markdown_report(ticker_signals)

        assert isinstance(report, str)
        assert '## Alternative Data Signals' in report
        assert 'AAPL' in report
        assert 'Composite Score' in report

    @pytest.mark.asyncio
    async def test_fetch_insider_signals_no_monitor(self, aggregator):
        """Test fetching insider signals when monitor not available"""
        aggregator.insider_monitor = None
        signals = await aggregator._fetch_insider_signals('AAPL')

        assert signals == []

    @pytest.mark.asyncio
    async def test_fetch_insider_signals_with_error(self, aggregator):
        """Test fetching insider signals with error"""
        mock_monitor = Mock()
        mock_monitor.get_signals.side_effect = Exception("API Error")
        aggregator.insider_monitor = mock_monitor

        signals = await aggregator._fetch_insider_signals('AAPL')

        assert signals == []

    @pytest.mark.asyncio
    async def test_fetch_all_signals_cache_hit(self, aggregator, sample_bullish_signal):
        """Test fetching signals uses cache"""
        # Populate cache
        aggregator.cache.set('AAPL', [sample_bullish_signal])

        # Fetch signals (should use cache)
        result = await aggregator.fetch_all_signals(['AAPL'])

        assert 'AAPL' in result
        assert len(result['AAPL']) == 1
        assert result['AAPL'][0].ticker == 'AAPL'

    @pytest.mark.asyncio
    async def test_fetch_all_signals_no_sources(self, aggregator):
        """Test fetching signals with no sources available"""
        aggregator.insider_monitor = None
        aggregator.options_analyzer = None
        aggregator.social_analyzer = None
        aggregator.trends_analyzer = None

        result = await aggregator.fetch_all_signals(['AAPL'])

        assert 'AAPL' in result
        assert result['AAPL'] == []

    @pytest.mark.asyncio
    async def test_analyze_tickers(self, aggregator, sample_bullish_signal):
        """Test complete analyze_tickers workflow"""
        # Mock the cache to return signals
        aggregator.cache.set('AAPL', [sample_bullish_signal])

        result = await aggregator.analyze_tickers(['AAPL'])

        assert 'signals' in result
        assert 'composite_scores' in result
        assert 'summary_table' in result
        assert 'report' in result
        assert 'timestamp' in result

        assert 'AAPL' in result['signals']
        assert 'AAPL' in result['composite_scores']


class TestSynchronousWrapper:
    """Test synchronous wrapper function"""

    def test_analyze_tickers_sync(self, sample_bullish_signal):
        """Test synchronous wrapper"""
        aggregator = AlternativeDataAggregator(api_client=None)

        # Populate cache
        aggregator.cache.set('AAPL', [sample_bullish_signal])

        result = analyze_tickers_sync(['AAPL'], api_client=None)

        assert 'signals' in result
        assert 'composite_scores' in result
        assert 'AAPL' in result['signals']


class TestEdgeCases:
    """Test edge cases"""

    def test_very_high_strength(self, aggregator):
        """Test signal with very high strength"""
        signal = AlternativeDataSignal(
            ticker='AAPL', source='insider', signal_type=SignalType.BULLISH,
            strength=100.0, confidence=100.0, timestamp=datetime.now(), metadata={}
        )

        composite = aggregator.calculate_composite_score([signal])

        assert composite['composite_score'] > 0
        assert composite['composite_score'] <= 100

    def test_very_low_confidence(self, aggregator):
        """Test signal with very low confidence"""
        signal = AlternativeDataSignal(
            ticker='AAPL', source='social', signal_type=SignalType.BULLISH,
            strength=80.0, confidence=10.0, timestamp=datetime.now(), metadata={}
        )

        composite = aggregator.calculate_composite_score([signal])

        # Low confidence should reduce impact
        assert composite['confidence'] < 50

    def test_multiple_signals_same_source(self, aggregator):
        """Test multiple signals from same source"""
        signals = [
            AlternativeDataSignal(
                ticker='AAPL', source='insider', signal_type=SignalType.BULLISH,
                strength=80.0, confidence=75.0, timestamp=datetime.now(), metadata={}
            ),
            AlternativeDataSignal(
                ticker='AAPL', source='insider', signal_type=SignalType.BULLISH,
                strength=70.0, confidence=65.0, timestamp=datetime.now(), metadata={}
            )
        ]

        composite = aggregator.calculate_composite_score(signals)

        assert composite['signal_count'] == 2
        assert 'insider' in composite['breakdown']
        assert composite['breakdown']['insider']['signal_count'] == 2

    def test_conflicting_signals_same_source(self, aggregator):
        """Test conflicting signals from same source"""
        signals = [
            AlternativeDataSignal(
                ticker='AAPL', source='options', signal_type=SignalType.BULLISH,
                strength=80.0, confidence=75.0, timestamp=datetime.now(), metadata={}
            ),
            AlternativeDataSignal(
                ticker='AAPL', source='options', signal_type=SignalType.BEARISH,
                strength=70.0, confidence=65.0, timestamp=datetime.now(), metadata={}
            )
        ]

        composite = aggregator.calculate_composite_score(signals)

        # Should average out
        assert abs(composite['composite_score']) < 50

    def test_old_timestamp(self, aggregator):
        """Test signal with old timestamp"""
        old_signal = AlternativeDataSignal(
            ticker='AAPL', source='trends', signal_type=SignalType.BULLISH,
            strength=80.0, confidence=75.0,
            timestamp=datetime.now() - timedelta(days=30),
            metadata={}
        )

        composite = aggregator.calculate_composite_score([old_signal])

        # Should still calculate (timestamp doesn't affect scoring)
        assert composite['signal_count'] == 1


class TestIntegration:
    """Integration tests"""

    def test_full_workflow_no_api(self):
        """Test full workflow without API client"""
        aggregator = AlternativeDataAggregator(api_client=None)

        # Create test signals manually
        signals = {
            'AAPL': [
                AlternativeDataSignal(
                    ticker='AAPL', source='insider', signal_type=SignalType.BULLISH,
                    strength=80.0, confidence=75.0, timestamp=datetime.now(), metadata={}
                )
            ]
        }

        # Calculate composite scores
        composite_scores = {}
        for ticker, ticker_signals in signals.items():
            composite_scores[ticker] = aggregator.calculate_composite_score(ticker_signals)

        # Generate summary table
        summary_df = aggregator.generate_summary_table(signals)

        # Generate report
        report = aggregator.generate_markdown_report(signals)

        assert len(composite_scores) == 1
        assert not summary_df.empty
        assert 'AAPL' in report

    def test_cache_integration(self, aggregator, sample_bullish_signal):
        """Test cache integration in workflow"""
        # Set cache
        aggregator.cache.set('AAPL', [sample_bullish_signal])

        # Fetch (should use cache)
        result = asyncio.run(aggregator.fetch_all_signals(['AAPL']))

        assert 'AAPL' in result
        assert len(result['AAPL']) == 1

        # Verify cache was used (not expired)
        cached = aggregator.cache.get('AAPL')
        assert cached is not None
