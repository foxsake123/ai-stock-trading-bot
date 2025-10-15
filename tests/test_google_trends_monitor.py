"""Tests for Google Trends monitoring"""

import pytest
from datetime import datetime, timedelta
from data_sources.google_trends_monitor import (
    GoogleTrendsMonitor,
    TrendData,
    ComparisonData,
    get_trends_signals
)
from unittest.mock import Mock, MagicMock, patch
import pandas as pd

@pytest.fixture
def mock_pytrends():
    """Mock pytrends client"""
    client = Mock()
    return client

@pytest.fixture
def trends_monitor(mock_pytrends):
    """Create GoogleTrendsMonitor with mock client"""
    return GoogleTrendsMonitor(mock_pytrends)

@pytest.fixture
def sample_interest_data():
    """Sample interest over time data"""
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    interest = [50] * 60 + [60] * 20 + [80] * 10  # Rising trend
    return pd.DataFrame({
        'AAPL': interest
    }, index=dates)

@pytest.fixture
def sample_comparison_data():
    """Sample comparison data for multiple tickers"""
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    return pd.DataFrame({
        'AAPL': [70] * 30,
        'MSFT': [50] * 30,
        'GOOGL': [90] * 30
    }, index=dates)


class TestGoogleTrendsMonitorInitialization:
    """Test GoogleTrendsMonitor initialization"""

    def test_initialization_with_client(self, mock_pytrends):
        """Test initialization with provided client"""
        monitor = GoogleTrendsMonitor(mock_pytrends)
        assert monitor._pytrends == mock_pytrends
        assert monitor.request_delay == 2
        assert monitor.breakout_threshold == 2.0

    def test_initialization_without_client(self):
        """Test initialization without client (lazy load)"""
        monitor = GoogleTrendsMonitor(None)
        assert monitor._pytrends is None

    def test_lazy_load_pytrends(self):
        """Test lazy loading of pytrends client"""
        monitor = GoogleTrendsMonitor(None)

        # Pytrends not initialized yet
        assert monitor._pytrends is None

        # Will attempt to import pytrends when accessed
        # (Skip actual import test since pytrends may not be installed)

    def test_thresholds_customizable(self, trends_monitor):
        """Test that thresholds are customizable"""
        trends_monitor.breakout_threshold = 3.0
        trends_monitor.rising_threshold = 0.30

        assert trends_monitor.breakout_threshold == 3.0
        assert trends_monitor.rising_threshold == 0.30


class TestInterestOverTime:
    """Test fetching interest over time data"""

    def test_get_interest_over_time_success(self, trends_monitor, sample_interest_data):
        """Test successful interest fetch"""
        trends_monitor.pytrends.interest_over_time.return_value = sample_interest_data

        result = trends_monitor.get_interest_over_time('AAPL')

        assert result is not None
        assert result['keyword'] == 'AAPL'
        assert result['current'] == 80
        assert result['max'] == 80
        assert len(result['interest']) == 90

    def test_get_interest_over_time_empty(self, trends_monitor):
        """Test handling empty data"""
        trends_monitor.pytrends.interest_over_time.return_value = pd.DataFrame()

        result = trends_monitor.get_interest_over_time('INVALID')

        assert result is None

    def test_get_interest_over_time_missing_keyword(self, trends_monitor):
        """Test handling missing keyword in response"""
        df = pd.DataFrame({'OTHER': [1, 2, 3]})
        trends_monitor.pytrends.interest_over_time.return_value = df

        result = trends_monitor.get_interest_over_time('AAPL')

        assert result is None

    def test_get_interest_over_time_exception(self, trends_monitor):
        """Test handling exceptions"""
        trends_monitor.pytrends.interest_over_time.side_effect = Exception("API Error")

        result = trends_monitor.get_interest_over_time('AAPL')

        assert result is None

    def test_get_interest_custom_timeframe(self, trends_monitor, sample_interest_data):
        """Test custom timeframe parameter"""
        trends_monitor.pytrends.interest_over_time.return_value = sample_interest_data

        result = trends_monitor.get_interest_over_time('AAPL', timeframe='now 1-d')

        trends_monitor.pytrends.build_payload.assert_called_with(
            kw_list=['AAPL'],
            timeframe='now 1-d',
            geo='US'
        )


class TestRelatedQueries:
    """Test fetching related queries"""

    def test_get_related_queries_success(self, trends_monitor):
        """Test successful related queries fetch"""
        rising_df = pd.DataFrame({
            'query': ['AAPL stock', 'AAPL price', 'buy AAPL', 'AAPL news', 'AAPL earnings']
        })

        trends_monitor.pytrends.related_queries.return_value = {
            'AAPL': {'rising': rising_df}
        }

        result = trends_monitor.get_related_queries('AAPL')

        assert len(result) == 5
        assert 'AAPL stock' in result

    def test_get_related_queries_empty(self, trends_monitor):
        """Test handling empty related queries"""
        trends_monitor.pytrends.related_queries.return_value = {
            'AAPL': {'rising': None}
        }

        result = trends_monitor.get_related_queries('AAPL')

        assert result == []

    def test_get_related_queries_missing_keyword(self, trends_monitor):
        """Test handling missing keyword"""
        trends_monitor.pytrends.related_queries.return_value = {}

        result = trends_monitor.get_related_queries('AAPL')

        assert result == []

    def test_get_related_queries_exception(self, trends_monitor):
        """Test handling exceptions"""
        trends_monitor.pytrends.related_queries.side_effect = Exception("API Error")

        result = trends_monitor.get_related_queries('AAPL')

        assert result == []


class TestTrendAnalysis:
    """Test trend analysis logic"""

    def test_calculate_recent_avg(self, trends_monitor):
        """Test recent average calculation"""
        series = [10, 20, 30, 40, 50, 60, 70]

        avg_7d = trends_monitor._calculate_recent_avg(series, days=7)
        avg_3d = trends_monitor._calculate_recent_avg(series, days=3)

        assert avg_7d == 40.0  # (10+20+30+40+50+60+70)/7
        assert avg_3d == 60.0  # (50+60+70)/3

    def test_calculate_recent_avg_short_series(self, trends_monitor):
        """Test average with series shorter than requested days"""
        series = [10, 20]

        avg = trends_monitor._calculate_recent_avg(series, days=7)

        assert avg == 15.0  # Uses all available data

    def test_calculate_recent_avg_empty(self, trends_monitor):
        """Test average with empty series"""
        avg = trends_monitor._calculate_recent_avg([], days=7)
        assert avg == 0.0

    def test_determine_trend_rising(self, trends_monitor):
        """Test rising trend detection"""
        trend = trends_monitor._determine_trend(
            current=80,
            avg_7d=60,
            avg_30d=50
        )
        assert trend == 'RISING'

    def test_determine_trend_falling(self, trends_monitor):
        """Test falling trend detection"""
        trend = trends_monitor._determine_trend(
            current=40,
            avg_7d=60,
            avg_30d=70
        )
        assert trend == 'FALLING'

    def test_determine_trend_stable(self, trends_monitor):
        """Test stable trend detection"""
        trend = trends_monitor._determine_trend(
            current=60,
            avg_7d=58,
            avg_30d=62
        )
        assert trend == 'STABLE'

    def test_determine_trend_zero_average(self, trends_monitor):
        """Test trend with zero average"""
        trend = trends_monitor._determine_trend(
            current=10,
            avg_7d=0,
            avg_30d=0
        )
        assert trend == 'STABLE'

    def test_calculate_momentum_positive(self, trends_monitor):
        """Test positive momentum calculation"""
        momentum = trends_monitor._calculate_momentum(
            current=80,
            avg_7d=70,
            avg_30d=50
        )
        assert momentum > 0
        assert -1.0 <= momentum <= 1.0

    def test_calculate_momentum_negative(self, trends_monitor):
        """Test negative momentum calculation"""
        momentum = trends_monitor._calculate_momentum(
            current=40,
            avg_7d=50,
            avg_30d=70
        )
        assert momentum < 0
        assert -1.0 <= momentum <= 1.0

    def test_calculate_momentum_neutral(self, trends_monitor):
        """Test neutral momentum"""
        momentum = trends_monitor._calculate_momentum(
            current=50,
            avg_7d=50,
            avg_30d=50
        )
        assert momentum == 0.0

    def test_calculate_momentum_clamping(self, trends_monitor):
        """Test momentum is clamped to [-1, 1]"""
        # Extreme values
        momentum = trends_monitor._calculate_momentum(
            current=100,
            avg_7d=90,
            avg_30d=10
        )
        assert -1.0 <= momentum <= 1.0


class TestSignalDetermination:
    """Test signal determination logic"""

    def test_determine_signal_bullish_breakout(self, trends_monitor):
        """Test bullish signal for breakout with rising trend"""
        signal = trends_monitor._determine_signal(
            trend='RISING',
            momentum=0.5,
            is_breakout=True,
            current=80,
            avg_30d=40
        )
        assert signal == 'BULLISH'

    def test_determine_signal_bullish_momentum(self, trends_monitor):
        """Test bullish signal for strong momentum"""
        signal = trends_monitor._determine_signal(
            trend='RISING',
            momentum=0.4,
            is_breakout=False,
            current=60,
            avg_30d=50
        )
        assert signal == 'BULLISH'

    def test_determine_signal_bearish_falling(self, trends_monitor):
        """Test bearish signal for falling trend"""
        signal = trends_monitor._determine_signal(
            trend='FALLING',
            momentum=-0.5,
            is_breakout=False,
            current=30,
            avg_30d=50
        )
        assert signal == 'BEARISH'

    def test_determine_signal_bearish_low_interest(self, trends_monitor):
        """Test bearish signal for very low interest"""
        signal = trends_monitor._determine_signal(
            trend='STABLE',
            momentum=0.0,
            is_breakout=False,
            current=5,
            avg_30d=5
        )
        assert signal == 'BEARISH'

    def test_determine_signal_neutral(self, trends_monitor):
        """Test neutral signal"""
        signal = trends_monitor._determine_signal(
            trend='STABLE',
            momentum=0.1,
            is_breakout=False,
            current=50,
            avg_30d=50
        )
        assert signal == 'NEUTRAL'


class TestAnalyzeTicker:
    """Test complete ticker analysis"""

    def test_analyze_ticker_success(self, trends_monitor, sample_interest_data):
        """Test successful ticker analysis"""
        trends_monitor.pytrends.interest_over_time.return_value = sample_interest_data
        trends_monitor.pytrends.related_queries.return_value = {
            'AAPL': {'rising': pd.DataFrame({'query': ['AAPL stock']})}
        }

        result = trends_monitor.analyze_ticker('AAPL')

        assert result is not None
        assert result.ticker == 'AAPL'
        assert result.current_interest == 80
        assert result.trend_direction in ['RISING', 'FALLING', 'STABLE']
        assert -1.0 <= result.momentum_score <= 1.0
        assert result.signal in ['BULLISH', 'BEARISH', 'NEUTRAL']

    def test_analyze_ticker_with_company_name(self, trends_monitor, sample_interest_data):
        """Test analysis with company name"""
        trends_monitor.pytrends.interest_over_time.return_value = sample_interest_data
        trends_monitor.pytrends.related_queries.return_value = {'AAPL': {'rising': None}}

        result = trends_monitor.analyze_ticker('AAPL', company_name='Apple Inc')

        assert result is not None
        assert result.ticker == 'AAPL'

    def test_analyze_ticker_no_data(self, trends_monitor):
        """Test analysis when no data available"""
        trends_monitor.pytrends.interest_over_time.return_value = pd.DataFrame()

        result = trends_monitor.analyze_ticker('INVALID')

        assert result.signal == 'NEUTRAL'
        assert result.current_interest == 0

    def test_analyze_ticker_exception(self, trends_monitor):
        """Test handling exceptions during analysis"""
        trends_monitor.pytrends.interest_over_time.side_effect = Exception("API Error")

        result = trends_monitor.analyze_ticker('AAPL')

        assert result.signal == 'NEUTRAL'


class TestCompareTickers:
    """Test ticker comparison"""

    def test_compare_tickers_success(self, trends_monitor, sample_comparison_data):
        """Test successful ticker comparison"""
        trends_monitor.pytrends.interest_over_time.return_value = sample_comparison_data

        result = trends_monitor.compare_tickers(['AAPL', 'MSFT', 'GOOGL'])

        assert result is not None
        assert result.winner == 'GOOGL'
        assert result.interest_scores['GOOGL'] == 90
        assert result.interest_scores['AAPL'] == 70
        assert result.interest_scores['MSFT'] == 50

    def test_compare_tickers_relative_strength(self, trends_monitor, sample_comparison_data):
        """Test relative strength calculation"""
        trends_monitor.pytrends.interest_over_time.return_value = sample_comparison_data

        result = trends_monitor.compare_tickers(['AAPL', 'MSFT', 'GOOGL'])

        assert result.relative_strength['GOOGL'] == 1.0  # Winner
        assert result.relative_strength['AAPL'] < 1.0
        assert result.relative_strength['MSFT'] < result.relative_strength['AAPL']

    def test_compare_tickers_limit_five(self, trends_monitor, sample_comparison_data):
        """Test limiting to 5 tickers"""
        tickers = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']
        trends_monitor.pytrends.interest_over_time.return_value = sample_comparison_data

        result = trends_monitor.compare_tickers(tickers)

        # Should only process first 5
        trends_monitor.pytrends.build_payload.assert_called_once()
        call_args = trends_monitor.pytrends.build_payload.call_args
        assert len(call_args[1]['kw_list']) == 5

    def test_compare_tickers_empty_data(self, trends_monitor):
        """Test comparison with empty data"""
        trends_monitor.pytrends.interest_over_time.return_value = pd.DataFrame()

        result = trends_monitor.compare_tickers(['AAPL', 'MSFT'])

        assert result is None

    def test_compare_tickers_exception(self, trends_monitor):
        """Test handling exceptions"""
        trends_monitor.pytrends.interest_over_time.side_effect = Exception("API Error")

        result = trends_monitor.compare_tickers(['AAPL', 'MSFT'])

        assert result is None


class TestReportGeneration:
    """Test report generation"""

    def test_generate_report_with_data(self, trends_monitor):
        """Test report generation with trend data"""
        ticker_data = {
            'AAPL': TrendData(
                keyword='AAPL',
                ticker='AAPL',
                current_interest=80,
                avg_interest_7d=70.0,
                avg_interest_30d=50.0,
                peak_interest=90,
                peak_date=datetime.now(),
                trend_direction='RISING',
                momentum_score=0.5,
                is_breakout=True,
                related_queries=['AAPL stock', 'buy AAPL'],
                signal='BULLISH'
            )
        }

        report = trends_monitor.generate_report(ticker_data)

        assert '## Google Trends Analysis' in report
        assert 'AAPL' in report
        assert 'BULLISH' in report
        assert 'BREAKOUT' in report

    def test_generate_report_empty(self, trends_monitor):
        """Test report generation with no data"""
        report = trends_monitor.generate_report({})

        assert 'No Google Trends data available' in report

    def test_generate_report_no_significant(self, trends_monitor):
        """Test report with only neutral signals"""
        ticker_data = {
            'AAPL': TrendData(
                keyword='AAPL',
                ticker='AAPL',
                current_interest=50,
                avg_interest_7d=50.0,
                avg_interest_30d=50.0,
                peak_interest=60,
                peak_date=datetime.now(),
                trend_direction='STABLE',
                momentum_score=0.0,
                is_breakout=False,
                related_queries=[],
                signal='NEUTRAL'
            )
        }

        report = trends_monitor.generate_report(ticker_data)

        assert 'No significant trend signals detected' in report

    def test_generate_report_summary(self, trends_monitor):
        """Test report summary statistics"""
        ticker_data = {
            'AAPL': TrendData(
                keyword='AAPL', ticker='AAPL', current_interest=80,
                avg_interest_7d=70.0, avg_interest_30d=50.0,
                peak_interest=90, peak_date=datetime.now(),
                trend_direction='RISING', momentum_score=0.5,
                is_breakout=True, related_queries=[], signal='BULLISH'
            ),
            'MSFT': TrendData(
                keyword='MSFT', ticker='MSFT', current_interest=30,
                avg_interest_7d=40.0, avg_interest_30d=60.0,
                peak_interest=70, peak_date=datetime.now(),
                trend_direction='FALLING', momentum_score=-0.5,
                is_breakout=False, related_queries=[], signal='BEARISH'
            )
        }

        report = trends_monitor.generate_report(ticker_data)

        assert '2 tickers analyzed' in report
        assert '1 bullish' in report
        assert '1 bearish' in report


class TestConvenienceFunction:
    """Test get_trends_signals convenience function"""

    @patch('data_sources.google_trends_monitor.GoogleTrendsMonitor')
    def test_get_trends_signals(self, mock_monitor_class):
        """Test convenience function"""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        # Mock analyze_ticker to return TrendData
        mock_trend = TrendData(
            keyword='AAPL', ticker='AAPL', current_interest=80,
            avg_interest_7d=70.0, avg_interest_30d=50.0,
            peak_interest=90, peak_date=datetime.now(),
            trend_direction='RISING', momentum_score=0.5,
            is_breakout=True, related_queries=[], signal='BULLISH'
        )
        mock_monitor.analyze_ticker.return_value = mock_trend
        mock_monitor.generate_report.return_value = "Test Report"

        result = get_trends_signals(['AAPL'])

        assert 'trends' in result
        assert 'report' in result
        assert 'summary' in result
        assert result['summary']['total_analyzed'] == 1
        assert result['summary']['bullish_signals'] == 1


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limit_delay(self, trends_monitor):
        """Test that rate limiting enforces delay"""
        import time

        trends_monitor.request_delay = 0.1  # Short delay for testing

        start = time.time()
        trends_monitor._rate_limit()
        trends_monitor._rate_limit()
        elapsed = time.time() - start

        assert elapsed >= 0.1  # At least one delay period

    def test_rate_limit_no_delay_first_call(self, trends_monitor):
        """Test no delay on first call"""
        import time

        trends_monitor.last_request_time = 0

        start = time.time()
        trends_monitor._rate_limit()
        elapsed = time.time() - start

        assert elapsed < 0.1  # Should be nearly instant
