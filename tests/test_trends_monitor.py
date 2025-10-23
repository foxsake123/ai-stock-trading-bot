"""Tests for Google Trends monitoring"""

import pytest
from datetime import datetime
from data_sources.trends_monitor import TrendsMonitor, TrendsData, get_trends_signals
from unittest.mock import Mock, MagicMock, patch
import pandas as pd


@pytest.fixture
def trends_monitor():
    """Create TrendsMonitor instance"""
    with patch('pytrends.request.TrendReq') as mock_trend_req:
        mock_instance = Mock()
        mock_trend_req.return_value = mock_instance
        monitor = TrendsMonitor()
        yield monitor


@pytest.fixture
def sample_trends_df():
    """Sample Google Trends dataframe"""
    dates = pd.date_range(start='2025-01-01', periods=30, freq='D')
    data = {
        'AAPL': [20] * 23 + [25, 25, 30, 30, 35, 35, 100],  # Spike at end (100 vs avg_7d ~40)
        'isPartial': [False] * 30
    }
    return pd.DataFrame(data, index=dates)


@pytest.fixture
def sample_trends_df_low():
    """Sample Google Trends dataframe with low interest"""
    dates = pd.date_range(start='2025-01-01', periods=30, freq='D')
    data = {
        'LOWINT': [50] * 20 + [20, 18, 15, 12, 10, 8, 5, 3, 2, 1],  # Declining
        'isPartial': [False] * 30
    }
    return pd.DataFrame(data, index=dates)


@pytest.fixture
def sample_trends_df_multi():
    """Sample Google Trends dataframe with multiple tickers"""
    dates = pd.date_range(start='2025-01-01', periods=30, freq='D')
    data = {
        'AAPL': [20] * 23 + [25, 25, 30, 30, 35, 35, 100],
        'MSFT': [30] * 23 + [35, 35, 40, 40, 45, 45, 90],
        'isPartial': [False] * 30
    }
    return pd.DataFrame(data, index=dates)


class TestTrendsMonitorInitialization:
    """Test TrendsMonitor initialization"""

    def test_initialization(self, trends_monitor):
        """Test TrendsMonitor initialization"""
        assert trends_monitor.rate_limit_delay == 2

    def test_initialization_without_pytrends(self):
        """Test initialization fails without pytrends"""
        with patch('data_sources.trends_monitor.PYTRENDS_AVAILABLE', False):
            with pytest.raises(ImportError) as exc_info:
                TrendsMonitor()
            assert "pytrends library not installed" in str(exc_info.value)


class TestDetermineSignal:
    """Test signal determination logic"""

    def test_determine_signal_spike(self, trends_monitor):
        """Test spike signal detection"""
        signal = trends_monitor._determine_signal(current=100, avg_7d=50, avg_30d=55)
        assert signal == 'SPIKE'

    def test_determine_signal_elevated(self, trends_monitor):
        """Test elevated signal detection"""
        signal = trends_monitor._determine_signal(current=75, avg_7d=50, avg_30d=55)
        assert signal == 'ELEVATED'

    def test_determine_signal_normal(self, trends_monitor):
        """Test normal signal detection"""
        signal = trends_monitor._determine_signal(current=52, avg_7d=50, avg_30d=55)
        assert signal == 'NORMAL'

    def test_determine_signal_low(self, trends_monitor):
        """Test low signal detection"""
        signal = trends_monitor._determine_signal(current=20, avg_7d=50, avg_30d=55)
        assert signal == 'LOW'

    def test_determine_signal_exact_threshold_spike(self, trends_monitor):
        """Test exact 2x threshold"""
        signal = trends_monitor._determine_signal(current=100, avg_7d=50, avg_30d=50)
        assert signal == 'SPIKE'

    def test_determine_signal_exact_threshold_elevated(self, trends_monitor):
        """Test exact 1.5x threshold"""
        signal = trends_monitor._determine_signal(current=75, avg_7d=50, avg_30d=50)
        assert signal == 'ELEVATED'

    def test_determine_signal_exact_threshold_normal(self, trends_monitor):
        """Test exact 0.5x threshold"""
        signal = trends_monitor._determine_signal(current=25, avg_7d=50, avg_30d=50)
        assert signal == 'NORMAL'

    def test_determine_signal_zero_average(self, trends_monitor):
        """Test with zero average"""
        signal = trends_monitor._determine_signal(current=50, avg_7d=0, avg_30d=0)
        # Should not raise error, should handle gracefully
        assert signal in ['SPIKE', 'ELEVATED', 'NORMAL', 'LOW']


class TestFetchTrendsData:
    """Test fetching trends data"""

    @patch('pytrends.request.TrendReq')
    def test_fetch_trends_data(self, mock_trend_req, sample_trends_df):
        """Test fetching trends data"""
        mock_instance = Mock()
        mock_instance.interest_over_time.return_value = sample_trends_df
        mock_trend_req.return_value = mock_instance

        monitor = TrendsMonitor()
        monitor.pytrends = mock_instance

        data = monitor.fetch_trends_data('AAPL')

        assert data is not None
        assert data.ticker == 'AAPL'
        assert data.current_interest == 100
        assert data.signal == 'SPIKE'
        assert data.change_pct_7d > 0

    @patch('pytrends.request.TrendReq')
    def test_fetch_trends_data_empty_dataframe(self, mock_trend_req):
        """Test handling empty dataframe"""
        mock_instance = Mock()
        mock_instance.interest_over_time.return_value = pd.DataFrame()
        mock_trend_req.return_value = mock_instance

        monitor = TrendsMonitor()
        monitor.pytrends = mock_instance

        data = monitor.fetch_trends_data('INVALID')

        assert data is None

    @patch('pytrends.request.TrendReq')
    def test_fetch_trends_data_missing_ticker(self, mock_trend_req):
        """Test handling missing ticker in dataframe"""
        mock_instance = Mock()
        df = pd.DataFrame({'OTHER': [1, 2, 3]})
        mock_instance.interest_over_time.return_value = df
        mock_trend_req.return_value = mock_instance

        monitor = TrendsMonitor()
        monitor.pytrends = mock_instance

        data = monitor.fetch_trends_data('AAPL')

        assert data is None

    @patch('pytrends.request.TrendReq')
    def test_fetch_trends_data_exception(self, mock_trend_req):
        """Test exception handling"""
        mock_instance = Mock()
        mock_instance.interest_over_time.side_effect = Exception("API Error")
        mock_trend_req.return_value = mock_instance

        monitor = TrendsMonitor()
        monitor.pytrends = mock_instance

        data = monitor.fetch_trends_data('AAPL')

        assert data is None

    @patch('pytrends.request.TrendReq')
    def test_fetch_trends_data_custom_timeframe(self, mock_trend_req, sample_trends_df):
        """Test custom timeframe parameter"""
        mock_instance = Mock()
        mock_instance.interest_over_time.return_value = sample_trends_df
        mock_trend_req.return_value = mock_instance

        monitor = TrendsMonitor()
        monitor.pytrends = mock_instance

        data = monitor.fetch_trends_data('AAPL', timeframe='today 3-m')

        assert data is not None
        monitor.pytrends.build_payload.assert_called_with(
            kw_list=['AAPL'],
            cat=0,
            timeframe='today 3-m',
            geo='US'
        )

    @patch('pytrends.request.TrendReq')
    def test_fetch_trends_data_low_interest(self, mock_trend_req, sample_trends_df_low):
        """Test low interest detection"""
        mock_instance = Mock()
        mock_instance.interest_over_time.return_value = sample_trends_df_low
        mock_trend_req.return_value = mock_instance

        monitor = TrendsMonitor()
        monitor.pytrends = mock_instance

        data = monitor.fetch_trends_data('LOWINT')

        assert data is not None
        assert data.signal == 'LOW'


class TestBatchFetch:
    """Test batch fetching"""

    @patch('pytrends.request.TrendReq')
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_batch_fetch(self, mock_sleep, mock_trend_req):
        """Test batch fetching multiple tickers"""
        dates = pd.date_range(start='2025-01-01', periods=30, freq='D')

        # Create separate DataFrames for each ticker
        aapl_df = pd.DataFrame({
            'AAPL': [20] * 23 + [25, 25, 30, 30, 35, 35, 100],
            'isPartial': [False] * 30
        }, index=dates)

        msft_df = pd.DataFrame({
            'MSFT': [30] * 23 + [35, 35, 40, 40, 45, 45, 90],
            'isPartial': [False] * 30
        }, index=dates)

        mock_instance = Mock()
        mock_instance.interest_over_time.side_effect = [aapl_df, msft_df]
        mock_trend_req.return_value = mock_instance

        monitor = TrendsMonitor()
        monitor.pytrends = mock_instance

        results = monitor.batch_fetch(['AAPL', 'MSFT'])

        assert len(results) == 2
        assert 'AAPL' in results
        assert 'MSFT' in results
        # Verify rate limiting was called
        assert mock_sleep.call_count >= 1

    @patch('pytrends.request.TrendReq')
    @patch('time.sleep')
    def test_batch_fetch_with_errors(self, mock_sleep, mock_trend_req):
        """Test batch fetch continues on individual errors"""
        mock_instance = Mock()
        # First call succeeds, second fails, third succeeds
        mock_instance.interest_over_time.side_effect = [
            pd.DataFrame({'AAPL': [50] * 30, 'isPartial': [False] * 30},
                        index=pd.date_range(start='2025-01-01', periods=30, freq='D')),
            Exception("API Error"),
            pd.DataFrame({'GOOGL': [60] * 30, 'isPartial': [False] * 30},
                        index=pd.date_range(start='2025-01-01', periods=30, freq='D'))
        ]
        mock_trend_req.return_value = mock_instance

        monitor = TrendsMonitor()
        monitor.pytrends = mock_instance

        results = monitor.batch_fetch(['AAPL', 'MSFT', 'GOOGL'])

        assert len(results) == 2
        assert 'AAPL' in results
        assert 'GOOGL' in results
        assert 'MSFT' not in results

    @patch('pytrends.request.TrendReq')
    def test_batch_fetch_empty_list(self, mock_trend_req):
        """Test batch fetch with empty ticker list"""
        mock_instance = Mock()
        mock_trend_req.return_value = mock_instance

        monitor = TrendsMonitor()
        monitor.pytrends = mock_instance

        results = monitor.batch_fetch([])

        assert results == {}


class TestGetRelatedQueries:
    """Test related queries functionality"""

    @patch('pytrends.request.TrendReq')
    def test_get_related_queries(self, mock_trend_req):
        """Test fetching related queries"""
        mock_instance = Mock()
        mock_instance.related_queries.return_value = {
            'AAPL': {
                'top': ['apple stock', 'aapl price'],
                'rising': ['aapl earnings', 'apple news']
            }
        }
        mock_trend_req.return_value = mock_instance

        monitor = TrendsMonitor()
        monitor.pytrends = mock_instance

        queries = monitor.get_related_queries('AAPL')

        assert 'top' in queries
        assert 'rising' in queries
        assert len(queries['top']) > 0

    @patch('pytrends.request.TrendReq')
    def test_get_related_queries_no_data(self, mock_trend_req):
        """Test handling no related queries"""
        mock_instance = Mock()
        mock_instance.related_queries.return_value = {}
        mock_trend_req.return_value = mock_instance

        monitor = TrendsMonitor()
        monitor.pytrends = mock_instance

        queries = monitor.get_related_queries('INVALID')

        assert queries == {'top': [], 'rising': []}

    @patch('pytrends.request.TrendReq')
    def test_get_related_queries_exception(self, mock_trend_req):
        """Test exception handling for related queries"""
        mock_instance = Mock()
        mock_instance.related_queries.side_effect = Exception("API Error")
        mock_trend_req.return_value = mock_instance

        monitor = TrendsMonitor()
        monitor.pytrends = mock_instance

        queries = monitor.get_related_queries('AAPL')

        assert queries == {'top': [], 'rising': []}


class TestGenerateSummaryReport:
    """Test report generation"""

    def test_generate_summary_report(self, trends_monitor):
        """Test markdown report generation"""
        trends_data = {
            'AAPL': TrendsData(
                ticker='AAPL',
                current_interest=100,
                avg_7d=50.0,
                avg_30d=55.0,
                change_pct_7d=100.0,
                change_pct_30d=81.8,
                signal='SPIKE',
                timestamp=datetime.now()
            ),
            'MSFT': TrendsData(
                ticker='MSFT',
                current_interest=45,
                avg_7d=40.0,
                avg_30d=42.0,
                change_pct_7d=12.5,
                change_pct_30d=7.1,
                signal='NORMAL',
                timestamp=datetime.now()
            )
        }

        report = trends_monitor.generate_summary_report(trends_data)

        assert '## Google Trends Sentiment' in report
        assert 'AAPL' in report
        assert 'MSFT' in report
        assert '[FIRE] SPIKE' in report
        assert '[MINUS] NORMAL' in report
        assert '+100%' in report

    def test_generate_summary_report_empty(self, trends_monitor):
        """Test report with no data"""
        report = trends_monitor.generate_summary_report({})
        assert 'unavailable' in report.lower()

    def test_generate_summary_report_sorting(self, trends_monitor):
        """Test that report sorts by signal priority"""
        trends_data = {
            'LOW': TrendsData('LOW', 10, 50, 50, -80, -80, 'LOW', datetime.now()),
            'SPIKE': TrendsData('SPIKE', 100, 50, 50, 100, 100, 'SPIKE', datetime.now()),
            'NORMAL': TrendsData('NORMAL', 50, 50, 50, 0, 0, 'NORMAL', datetime.now()),
            'ELEVATED': TrendsData('ELEVATED', 75, 50, 50, 50, 50, 'ELEVATED', datetime.now())
        }

        report = trends_monitor.generate_summary_report(trends_data)

        # SPIKE should appear before ELEVATED, NORMAL, and LOW
        spike_pos = report.find('SPIKE')
        elevated_pos = report.find('ELEVATED')
        normal_pos = report.find('NORMAL')
        low_pos = report.find('LOW')

        assert spike_pos < elevated_pos < normal_pos < low_pos

    def test_generate_summary_report_interpretation(self, trends_monitor):
        """Test interpretation section"""
        trends_data = {
            'SPIKE1': TrendsData('SPIKE1', 100, 50, 50, 100, 100, 'SPIKE', datetime.now()),
            'SPIKE2': TrendsData('SPIKE2', 100, 50, 50, 100, 100, 'SPIKE', datetime.now()),
            'ELEVATED1': TrendsData('ELEVATED1', 75, 50, 50, 50, 50, 'ELEVATED', datetime.now())
        }

        report = trends_monitor.generate_summary_report(trends_data)

        assert '2 ticker(s) showing **significant retail interest spike**' in report
        assert '1 ticker(s) with **elevated interest**' in report


class TestGetTrendsSignalsConvenience:
    """Test convenience function"""

    @patch('pytrends.request.TrendReq')
    @patch('time.sleep')
    def test_get_trends_signals(self, mock_sleep, mock_trend_req, sample_trends_df):
        """Test convenience function"""
        mock_instance = Mock()
        mock_instance.interest_over_time.return_value = sample_trends_df
        mock_trend_req.return_value = mock_instance

        with patch('data_sources.trends_monitor.TrendsMonitor') as mock_monitor_class:
            mock_monitor = Mock()
            mock_monitor_class.return_value = mock_monitor

            trends_data = {
                'AAPL': TrendsData('AAPL', 100, 50, 50, 100, 100, 'SPIKE', datetime.now())
            }
            mock_monitor.batch_fetch.return_value = trends_data
            mock_monitor.generate_summary_report.return_value = "Test Report"

            result = get_trends_signals(['AAPL'])

            assert 'trends_data' in result
            assert 'report' in result
            assert 'summary' in result
            assert result['summary']['total_tickers'] == 1
            assert result['summary']['spike_signals'] == 1

    @patch('data_sources.trends_monitor.TrendsMonitor')
    def test_get_trends_signals_exception(self, mock_monitor_class):
        """Test convenience function exception handling"""
        mock_monitor_class.side_effect = Exception("Init Error")

        result = get_trends_signals(['AAPL'])

        assert result['summary']['total_tickers'] == 0
        assert 'temporarily unavailable' in result['report']


class TestEdgeCases:
    """Test edge cases"""

    @patch('pytrends.request.TrendReq')
    def test_change_pct_zero_average(self, mock_trend_req):
        """Test change percentage calculation with zero average"""
        mock_instance = Mock()
        # Create dataframe with all zeros
        dates = pd.date_range(start='2025-01-01', periods=30, freq='D')
        df = pd.DataFrame({
            'ZERO': [0] * 30,
            'isPartial': [False] * 30
        }, index=dates)
        mock_instance.interest_over_time.return_value = df
        mock_trend_req.return_value = mock_instance

        monitor = TrendsMonitor()
        monitor.pytrends = mock_instance

        data = monitor.fetch_trends_data('ZERO')

        assert data is not None
        assert data.change_pct_7d == 0
        assert data.change_pct_30d == 0

    def test_empty_trends_data_dict(self, trends_monitor):
        """Test handling empty trends data dict"""
        result = trends_monitor.generate_summary_report({})
        assert 'unavailable' in result.lower()

    @patch('pytrends.request.TrendReq')
    def test_single_data_point(self, mock_trend_req):
        """Test with minimal data"""
        mock_instance = Mock()
        dates = pd.date_range(start='2025-01-01', periods=1, freq='D')
        df = pd.DataFrame({
            'SINGLE': [50],
            'isPartial': [False]
        }, index=dates)
        mock_instance.interest_over_time.return_value = df
        mock_trend_req.return_value = mock_instance

        monitor = TrendsMonitor()
        monitor.pytrends = mock_instance

        data = monitor.fetch_trends_data('SINGLE')

        assert data is not None
        assert data.current_interest == 50
