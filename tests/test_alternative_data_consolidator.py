"""Tests for Alternative Data Consolidator"""

import pytest
from datetime import datetime
from data_sources.alternative_data_consolidator import (
    AlternativeDataConsolidator,
    ConsolidatedSignal,
    DataSourceStatus,
    consolidate_alternative_data
)
from unittest.mock import Mock, patch


@pytest.fixture
def sample_insider_data():
    """Sample insider trading data"""
    return {
        'transactions': [
            {
                'ticker': 'AAPL',
                'insider_name': 'Tim Cook',
                'title': 'CEO',
                'transaction_type': 'BUY',
                'shares': 10000,
                'price': 175.00,
                'value': 1750000,
                'filing_date': '2025-10-15'
            },
            {
                'ticker': 'AAPL',
                'insider_name': 'Luca Maestri',
                'title': 'CFO',
                'transaction_type': 'BUY',
                'shares': 5000,
                'price': 175.00,
                'value': 875000,
                'filing_date': '2025-10-14'
            }
        ]
    }


@pytest.fixture
def sample_trends_data():
    """Sample Google Trends data"""
    return {
        'signal': 'BULLISH',
        'momentum_score': 0.62,
        'is_breakout': True,
        'current_interest': 85,
        'trend_direction': 'RISING'
    }


@pytest.fixture
def sample_options_data():
    """Sample options flow data"""
    return {
        'signal': 'BULLISH',
        'sentiment': 0.45,
        'put_call_ratio': 0.65
    }


@pytest.fixture
def consolidator():
    """Create consolidator with mock sources"""
    insider_monitor = Mock()
    trends_monitor = Mock()
    options_analyzer = Mock()
    return AlternativeDataConsolidator(
        insider_monitor,
        trends_monitor,
        options_analyzer
    )


class TestConsolidatorInitialization:
    """Test consolidator initialization"""

    def test_initialization_with_all_sources(self):
        """Test initialization with all sources"""
        insider = Mock()
        trends = Mock()
        options = Mock()

        consolidator = AlternativeDataConsolidator(insider, trends, options)

        assert consolidator.insider_monitor == insider
        assert consolidator.trends_monitor == trends
        assert consolidator.options_analyzer == options

    def test_initialization_without_sources(self):
        """Test initialization without sources"""
        consolidator = AlternativeDataConsolidator()

        assert consolidator.insider_monitor is None
        assert consolidator.trends_monitor is None
        assert consolidator.options_analyzer is None

    def test_default_weights(self):
        """Test default weight configuration"""
        consolidator = AlternativeDataConsolidator()

        assert 'insider' in consolidator.weights
        assert 'trends' in consolidator.weights
        assert 'options' in consolidator.weights

        # Weights should sum to 1.0
        assert abs(sum(consolidator.weights.values()) - 1.0) < 0.01

    def test_custom_weights(self):
        """Test custom weight configuration"""
        custom_weights = {
            'insider': 0.50,
            'trends': 0.30,
            'options': 0.20
        }

        consolidator = AlternativeDataConsolidator(weights=custom_weights)

        # Weights should be normalized
        assert abs(sum(consolidator.weights.values()) - 1.0) < 0.01

    def test_thresholds_configured(self):
        """Test signal thresholds are configured"""
        consolidator = AlternativeDataConsolidator()

        assert 0 < consolidator.bullish_threshold < 1
        assert 0 < consolidator.bearish_threshold < 1
        assert consolidator.bearish_threshold < consolidator.bullish_threshold


class TestSourceStatus:
    """Test data source status"""

    def test_all_sources_available(self):
        """Test status when all sources available"""
        consolidator = AlternativeDataConsolidator(
            insider_monitor=Mock(),
            trends_monitor=Mock(),
            options_analyzer=Mock()
        )

        status = consolidator.get_source_status()

        assert status.insider_available is True
        assert status.trends_available is True
        assert status.options_available is True
        assert status.sources_active == 3
        assert status.sources_total == 3

    def test_no_sources_available(self):
        """Test status when no sources available"""
        consolidator = AlternativeDataConsolidator()

        status = consolidator.get_source_status()

        assert status.insider_available is False
        assert status.trends_available is False
        assert status.options_available is False
        assert status.sources_active == 0
        assert status.sources_total == 3

    def test_partial_sources_available(self):
        """Test status with some sources"""
        consolidator = AlternativeDataConsolidator(
            insider_monitor=Mock(),
            trends_monitor=None,
            options_analyzer=Mock()
        )

        status = consolidator.get_source_status()

        assert status.insider_available is True
        assert status.trends_available is False
        assert status.options_available is True
        assert status.sources_active == 2


class TestInsiderScoreCalculation:
    """Test insider score calculation"""

    def test_strong_buying(self, consolidator):
        """Test score for strong insider buying"""
        data = {
            'transactions': [
                {'transaction_type': 'BUY', 'value': 2000000},
                {'transaction_type': 'BUY', 'value': 500000}
            ]
        }

        score = consolidator._calculate_insider_score(data)

        # Strong buying should score > 0.8
        assert score > 0.8

    def test_strong_selling(self, consolidator):
        """Test score for strong insider selling"""
        data = {
            'transactions': [
                {'transaction_type': 'SELL', 'value': 2000000},
                {'transaction_type': 'SELL', 'value': 500000}
            ]
        }

        score = consolidator._calculate_insider_score(data)

        # Strong selling should score < 0.2
        assert score < 0.2

    def test_neutral_insider_activity(self, consolidator):
        """Test score with balanced activity"""
        data = {
            'transactions': [
                {'transaction_type': 'BUY', 'value': 1000000},
                {'transaction_type': 'SELL', 'value': 1000000}
            ]
        }

        score = consolidator._calculate_insider_score(data)

        # Balanced should be neutral (~0.5)
        assert 0.45 <= score <= 0.55

    def test_no_insider_data(self, consolidator):
        """Test score with no data"""
        score = consolidator._calculate_insider_score(None)

        assert score == 0.5  # Neutral

    def test_empty_transactions(self, consolidator):
        """Test score with empty transactions"""
        data = {'transactions': []}

        score = consolidator._calculate_insider_score(data)

        assert score == 0.5


class TestTrendsScoreCalculation:
    """Test trends score calculation"""

    def test_bullish_with_breakout(self, consolidator):
        """Test score for bullish breakout"""
        data = {
            'signal': 'BULLISH',
            'momentum_score': 0.5,
            'is_breakout': True,
            'current_interest': 85
        }

        score = consolidator._calculate_trends_score(data)

        # Bullish + breakout should score high
        assert score > 0.75

    def test_bearish_with_momentum(self, consolidator):
        """Test score for bearish with momentum"""
        data = {
            'signal': 'BEARISH',
            'momentum_score': -0.6,
            'is_breakout': False,
            'current_interest': 50
        }

        score = consolidator._calculate_trends_score(data)

        # Bearish with negative momentum should score low
        assert score < 0.35

    def test_neutral_trends(self, consolidator):
        """Test score for neutral trends"""
        data = {
            'signal': 'NEUTRAL',
            'momentum_score': 0.0,
            'is_breakout': False,
            'current_interest': 50
        }

        score = consolidator._calculate_trends_score(data)

        # Neutral should be around 0.5
        assert 0.45 <= score <= 0.55

    def test_very_low_interest(self, consolidator):
        """Test penalty for very low interest"""
        data = {
            'signal': 'NEUTRAL',
            'momentum_score': 0.0,
            'is_breakout': False,
            'current_interest': 5  # Very low
        }

        score = consolidator._calculate_trends_score(data)

        # Should be penalized
        assert score < 0.5

    def test_no_trends_data(self, consolidator):
        """Test score with no data"""
        score = consolidator._calculate_trends_score(None)

        assert score == 0.5


class TestOptionsScoreCalculation:
    """Test options score calculation"""

    def test_bullish_options_low_pc(self, consolidator):
        """Test score for bullish options with low P/C"""
        data = {
            'signal': 'BULLISH',
            'sentiment': 0.5,
            'put_call_ratio': 0.6  # Low (bullish)
        }

        score = consolidator._calculate_options_score(data)

        # Bullish + low P/C should score high
        assert score > 0.75

    def test_bearish_options_high_pc(self, consolidator):
        """Test score for bearish options with high P/C"""
        data = {
            'signal': 'BEARISH',
            'sentiment': -0.5,
            'put_call_ratio': 1.5  # High (bearish)
        }

        score = consolidator._calculate_options_score(data)

        # Bearish + high P/C should score low
        assert score < 0.25

    def test_neutral_options(self, consolidator):
        """Test score for neutral options"""
        data = {
            'signal': 'NEUTRAL',
            'sentiment': 0.0,
            'put_call_ratio': 1.0  # Neutral
        }

        score = consolidator._calculate_options_score(data)

        # Neutral should be around 0.5
        assert 0.45 <= score <= 0.55

    def test_no_options_data(self, consolidator):
        """Test score with no data"""
        score = consolidator._calculate_options_score(None)

        assert score == 0.5


class TestSignalDetermination:
    """Test signal determination logic"""

    def test_bullish_signal(self, consolidator):
        """Test bullish signal determination"""
        signal = consolidator._determine_signal(0.75)

        assert signal == 'BULLISH'

    def test_bearish_signal(self, consolidator):
        """Test bearish signal determination"""
        signal = consolidator._determine_signal(0.25)

        assert signal == 'BEARISH'

    def test_neutral_signal(self, consolidator):
        """Test neutral signal determination"""
        signal = consolidator._determine_signal(0.50)

        assert signal == 'NEUTRAL'

    def test_boundary_bullish(self, consolidator):
        """Test signal at bullish threshold"""
        signal = consolidator._determine_signal(consolidator.bullish_threshold)

        assert signal == 'BULLISH'

    def test_boundary_bearish(self, consolidator):
        """Test signal at bearish threshold"""
        signal = consolidator._determine_signal(consolidator.bearish_threshold)

        assert signal == 'BEARISH'


class TestConfidenceCalculation:
    """Test confidence calculation"""

    def test_high_agreement(self, consolidator):
        """Test confidence with high source agreement"""
        # All sources agree
        confidence = consolidator._calculate_confidence(0.8, 0.8, 0.8)

        # High agreement = high confidence
        assert confidence > 0.9

    def test_low_agreement(self, consolidator):
        """Test confidence with low source agreement"""
        # Sources disagree
        confidence = consolidator._calculate_confidence(0.2, 0.5, 0.8)

        # Low agreement = lower confidence
        assert confidence < 0.7

    def test_moderate_agreement(self, consolidator):
        """Test confidence with moderate agreement"""
        confidence = consolidator._calculate_confidence(0.5, 0.6, 0.55)

        # Moderate agreement = moderate to high confidence
        assert 0.5 <= confidence <= 1.0

    def test_confidence_range(self, consolidator):
        """Test confidence stays in valid range"""
        # Extreme disagreement
        confidence = consolidator._calculate_confidence(0.0, 0.5, 1.0)

        assert 0.0 <= confidence <= 1.0


class TestStrengthDetermination:
    """Test signal strength determination"""

    def test_strong_signal(self, consolidator):
        """Test strong signal determination"""
        # High score + high confidence
        strength = consolidator._determine_strength(0.95, 0.95)

        assert strength == 'STRONG'

    def test_weak_signal(self, consolidator):
        """Test weak signal determination"""
        # Near neutral + low confidence
        strength = consolidator._determine_strength(0.52, 0.3)

        assert strength == 'WEAK'

    def test_moderate_signal(self, consolidator):
        """Test moderate signal determination"""
        # Moderate score + high confidence
        # Distance = abs(0.85 - 0.5) = 0.35, metric = 0.35 * 2 * 0.9 = 0.63 (MODERATE)
        strength = consolidator._determine_strength(0.85, 0.9)

        assert strength in ['STRONG', 'MODERATE']

    def test_neutral_score_low_confidence(self, consolidator):
        """Test neutral score with low confidence"""
        strength = consolidator._determine_strength(0.5, 0.5)

        assert strength == 'WEAK'


class TestFactorIdentification:
    """Test factor identification"""

    def test_identify_insider_buying(self, consolidator):
        """Test identification of insider buying"""
        insider_data = {
            'transactions': [
                {'transaction_type': 'BUY'},
                {'transaction_type': 'BUY'},
                {'transaction_type': 'SELL'}
            ]
        }

        bullish, bearish = consolidator._identify_factors(
            insider_data, None, None
        )

        assert any('Insider buying' in f for f in bullish)

    def test_identify_insider_selling(self, consolidator):
        """Test identification of insider selling"""
        insider_data = {
            'transactions': [
                {'transaction_type': 'SELL'},
                {'transaction_type': 'SELL'},
                {'transaction_type': 'BUY'}
            ]
        }

        bullish, bearish = consolidator._identify_factors(
            insider_data, None, None
        )

        assert any('Insider selling' in f for f in bearish)

    def test_identify_breakout(self, consolidator):
        """Test identification of search breakout"""
        trends_data = {
            'is_breakout': True,
            'momentum_score': 0.4,
            'current_interest': 85
        }

        bullish, bearish = consolidator._identify_factors(
            None, trends_data, None
        )

        assert any('breakout' in f.lower() for f in bullish)

    def test_identify_low_interest(self, consolidator):
        """Test identification of low interest"""
        trends_data = {
            'is_breakout': False,
            'momentum_score': 0.0,
            'current_interest': 5  # Very low
        }

        bullish, bearish = consolidator._identify_factors(
            None, trends_data, None
        )

        assert any('low' in f.lower() and 'interest' in f.lower() for f in bearish)

    def test_identify_options_flow(self, consolidator):
        """Test identification of options flow"""
        options_data = {
            'signal': 'BULLISH',
            'put_call_ratio': 0.6
        }

        bullish, bearish = consolidator._identify_factors(
            None, None, options_data
        )

        assert any('options' in f.lower() for f in bullish)
        assert any('put/call' in f.lower() for f in bullish)


class TestConsolidateSignal:
    """Test full signal consolidation"""

    def test_consolidate_all_bullish(
        self,
        consolidator,
        sample_insider_data,
        sample_trends_data,
        sample_options_data
    ):
        """Test consolidation when all sources bullish"""
        signal = consolidator.consolidate_signal(
            'AAPL',
            sample_insider_data,
            sample_trends_data,
            sample_options_data
        )

        assert isinstance(signal, ConsolidatedSignal)
        assert signal.ticker == 'AAPL'
        assert signal.composite_signal == 'BULLISH'
        assert signal.composite_score > 0.6
        assert len(signal.bullish_factors) > 0

    def test_consolidate_mixed_signals(self, consolidator):
        """Test consolidation with mixed signals"""
        # Bullish insider, bearish trends, neutral options
        insider_data = {'transactions': [{'transaction_type': 'BUY', 'value': 2000000}]}
        trends_data = {'signal': 'BEARISH', 'momentum_score': -0.5, 'is_breakout': False, 'current_interest': 50}
        options_data = {'signal': 'NEUTRAL', 'sentiment': 0.0, 'put_call_ratio': 1.0}

        signal = consolidator.consolidate_signal(
            'AAPL',
            insider_data,
            trends_data,
            options_data
        )

        # Should be somewhat neutral due to mixed signals
        assert 0.35 <= signal.composite_score <= 0.65
        assert signal.confidence < 0.8  # Lower confidence due to disagreement

    def test_consolidate_no_data(self, consolidator):
        """Test consolidation with no data"""
        signal = consolidator.consolidate_signal('AAPL', None, None, None)

        assert signal.composite_score == 0.5  # Neutral
        assert signal.composite_signal == 'NEUTRAL'

    def test_signal_has_breakdown(
        self,
        consolidator,
        sample_insider_data,
        sample_trends_data,
        sample_options_data
    ):
        """Test signal includes detailed breakdown"""
        signal = consolidator.consolidate_signal(
            'AAPL',
            sample_insider_data,
            sample_trends_data,
            sample_options_data
        )

        assert 'insider' in signal.breakdown
        assert 'trends' in signal.breakdown
        assert 'options' in signal.breakdown

        # Each breakdown should have score, weight, contribution
        for source in ['insider', 'trends', 'options']:
            assert 'score' in signal.breakdown[source]
            assert 'weight' in signal.breakdown[source]
            assert 'contribution' in signal.breakdown[source]

    def test_signal_timestamp(self, consolidator):
        """Test signal has timestamp"""
        signal = consolidator.consolidate_signal('AAPL', None, None, None)

        assert isinstance(signal.timestamp, datetime)


class TestReportGeneration:
    """Test report generation"""

    def test_generate_report_with_signals(self, consolidator):
        """Test report generation with signals"""
        signals = [
            ConsolidatedSignal(
                ticker='AAPL',
                timestamp=datetime.now(),
                insider_score=0.8,
                trends_score=0.7,
                options_score=0.75,
                composite_score=0.75,
                composite_signal='BULLISH',
                confidence=0.85,
                strength='STRONG',
                bullish_factors=['Insider buying', 'Breakout'],
                bearish_factors=[],
                breakdown={}
            )
        ]

        report = consolidator.generate_report(signals)

        assert 'AAPL' in report
        assert 'BULLISH' in report
        assert 'STRONG' in report

    def test_generate_report_no_signals(self, consolidator):
        """Test report with no signals"""
        report = consolidator.generate_report([])

        assert 'No alternative data signals' in report

    def test_generate_report_filters_neutral(self, consolidator):
        """Test report filters neutral signals"""
        signals = [
            ConsolidatedSignal(
                ticker='AAPL',
                timestamp=datetime.now(),
                insider_score=0.5,
                trends_score=0.5,
                options_score=0.5,
                composite_score=0.5,
                composite_signal='NEUTRAL',
                confidence=0.5,
                strength='WEAK',
                bullish_factors=[],
                bearish_factors=[],
                breakdown={}
            )
        ]

        report = consolidator.generate_report(signals, include_neutral=False)

        # Should be filtered out
        assert 'AAPL' not in report or 'No significant' in report

    def test_generate_report_includes_summary(self, consolidator):
        """Test report includes summary"""
        signals = [
            ConsolidatedSignal(
                ticker='AAPL',
                timestamp=datetime.now(),
                insider_score=0.8,
                trends_score=0.7,
                options_score=0.75,
                composite_score=0.75,
                composite_signal='BULLISH',
                confidence=0.85,
                strength='STRONG',
                bullish_factors=[],
                bearish_factors=[],
                breakdown={}
            ),
            ConsolidatedSignal(
                ticker='TSLA',
                timestamp=datetime.now(),
                insider_score=0.3,
                trends_score=0.3,
                options_score=0.35,
                composite_score=0.32,
                composite_signal='BEARISH',
                confidence=0.80,
                strength='MODERATE',
                bullish_factors=[],
                bearish_factors=[],
                breakdown={}
            )
        ]

        report = consolidator.generate_report(signals)

        assert 'Summary' in report
        assert '2 tickers analyzed' in report
        assert 'bullish' in report.lower()
        assert 'bearish' in report.lower()


class TestConvenienceFunction:
    """Test convenience function"""

    @patch('data_sources.alternative_data_consolidator.AlternativeDataConsolidator')
    def test_consolidate_alternative_data(self, mock_consolidator_class):
        """Test convenience function"""
        # Setup mocks
        mock_consolidator = Mock()
        mock_consolidator_class.return_value = mock_consolidator

        mock_signal = Mock()
        mock_signal.composite_signal = 'BULLISH'
        mock_signal.strength = 'STRONG'
        mock_consolidator.consolidate_signal.return_value = mock_signal
        mock_consolidator.generate_report.return_value = "Test report"
        mock_consolidator.get_source_status.return_value = Mock(
            insider_available=True,
            trends_available=True,
            options_available=False,
            sources_active=2,
            sources_total=3
        )

        insider_monitor = Mock()
        trends_monitor = Mock()

        # Call function
        result = consolidate_alternative_data(
            ['AAPL', 'TSLA'],
            insider_monitor,
            trends_monitor
        )

        # Verify structure
        assert 'signals' in result
        assert 'report' in result
        assert 'summary' in result

        # Verify summary contents
        assert 'total_analyzed' in result['summary']
        assert 'bullish_signals' in result['summary']
        assert 'source_status' in result['summary']


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_extreme_scores(self, consolidator):
        """Test with extreme scores"""
        # All scores at maximum
        signal = consolidator.consolidate_signal(
            'AAPL',
            {'transactions': [{'transaction_type': 'BUY', 'value': 10000000}]},
            {'signal': 'BULLISH', 'momentum_score': 1.0, 'is_breakout': True, 'current_interest': 100},
            {'signal': 'BULLISH', 'sentiment': 1.0, 'put_call_ratio': 0.1}
        )

        # Composite should be clamped to valid range
        assert 0.0 <= signal.composite_score <= 1.0
        assert signal.composite_signal == 'BULLISH'

    def test_zero_weight_source(self):
        """Test with zero weight for a source"""
        consolidator = AlternativeDataConsolidator(
            weights={'insider': 1.0, 'trends': 0.0, 'options': 0.0}
        )

        signal = consolidator.consolidate_signal(
            'AAPL',
            {'transactions': [{'transaction_type': 'BUY', 'value': 2000000}]},
            None,
            None
        )

        # Should only use insider score
        assert signal.composite_score > 0.7

    def test_missing_transaction_values(self, consolidator):
        """Test insider data with missing values"""
        data = {
            'transactions': [
                {'transaction_type': 'BUY'},  # Missing value
                {'transaction_type': 'SELL', 'value': 1000000}
            ]
        }

        # Should not crash
        score = consolidator._calculate_insider_score(data)
        assert 0.0 <= score <= 1.0

    def test_invalid_momentum_score(self, consolidator):
        """Test trends with out-of-range momentum"""
        data = {
            'signal': 'BULLISH',
            'momentum_score': 5.0,  # Out of range
            'is_breakout': False,
            'current_interest': 50
        }

        score = consolidator._calculate_trends_score(data)

        # Should clamp to valid range
        assert 0.0 <= score <= 1.0


class TestWeightAdjustment:
    """Test weight adjustment scenarios"""

    def test_insider_heavy_weighting(self):
        """Test with heavy insider weighting"""
        consolidator = AlternativeDataConsolidator(
            weights={'insider': 0.70, 'trends': 0.15, 'options': 0.15}
        )

        # Strong insider buying, weak other signals
        signal = consolidator.consolidate_signal(
            'AAPL',
            {'transactions': [{'transaction_type': 'BUY', 'value': 3000000}]},
            {'signal': 'NEUTRAL', 'momentum_score': 0.0, 'is_breakout': False, 'current_interest': 50},
            {'signal': 'NEUTRAL', 'sentiment': 0.0, 'put_call_ratio': 1.0}
        )

        # Should be bullish due to insider weight
        assert signal.composite_score > 0.6

    def test_equal_weighting(self):
        """Test with equal weighting"""
        consolidator = AlternativeDataConsolidator(
            weights={'insider': 0.33, 'trends': 0.33, 'options': 0.34}
        )

        # Mixed signals
        signal = consolidator.consolidate_signal(
            'AAPL',
            {'transactions': [{'transaction_type': 'BUY', 'value': 2000000}]},  # Bullish
            {'signal': 'BEARISH', 'momentum_score': -0.5, 'is_breakout': False, 'current_interest': 50},  # Bearish
            {'signal': 'NEUTRAL', 'sentiment': 0.0, 'put_call_ratio': 1.0}  # Neutral
        )

        # Should be somewhat balanced
        assert 0.4 <= signal.composite_score <= 0.6
