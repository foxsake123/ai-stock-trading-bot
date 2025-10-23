"""Tests for Intraday Catalyst Monitor"""

import pytest
from datetime import datetime, time, timedelta
from monitoring.catalyst_monitor import (
    CatalystMonitor,
    Catalyst,
    CatalystAlert,
    CatalystType,
    CatalystImpact,
    CatalystUrgency,
    create_catalyst_from_event
)
from unittest.mock import Mock, patch


@pytest.fixture
def monitor():
    """Create catalyst monitor instance"""
    return CatalystMonitor()


@pytest.fixture
def sample_catalyst():
    """Sample catalyst event"""
    return Catalyst(
        ticker='AAPL',
        catalyst_type=CatalystType.EARNINGS_BEAT,
        impact=CatalystImpact.VERY_BULLISH,
        urgency=CatalystUrgency.IMMEDIATE,
        timestamp=datetime.now(),
        description="Apple reports Q4 earnings beat, EPS $1.52 vs $1.39 expected",
        source="earnings_api",
        details={'eps_actual': 1.52, 'eps_expected': 1.39},
        confidence=0.95
    )


class TestCatalystMonitorInitialization:
    """Test monitor initialization"""

    def test_initialization_default(self):
        """Test default initialization"""
        monitor = CatalystMonitor()

        assert monitor.news_api is None
        assert monitor.fd_client is None
        assert isinstance(monitor.active_catalysts, dict)
        assert isinstance(monitor.catalyst_history, list)
        assert isinstance(monitor.monitored_tickers, set)

    def test_initialization_with_clients(self):
        """Test initialization with API clients"""
        news_api = Mock()
        fd_client = Mock()

        monitor = CatalystMonitor(news_api, fd_client)

        assert monitor.news_api == news_api
        assert monitor.fd_client == fd_client

    def test_market_hours_configured(self):
        """Test market hours are configured"""
        monitor = CatalystMonitor()

        assert monitor.market_open == time(9, 30)
        assert monitor.market_close == time(16, 0)

    def test_impact_scores_configured(self):
        """Test impact scores are configured"""
        monitor = CatalystMonitor()

        assert CatalystImpact.VERY_BULLISH in monitor.impact_scores
        assert CatalystImpact.VERY_BEARISH in monitor.impact_scores
        assert monitor.impact_scores[CatalystImpact.VERY_BULLISH] > 0
        assert monitor.impact_scores[CatalystImpact.VERY_BEARISH] < 0


class TestTickerMonitoring:
    """Test ticker monitoring"""

    def test_add_monitored_ticker(self, monitor):
        """Test adding ticker to monitoring"""
        monitor.add_monitored_ticker('AAPL')

        assert 'AAPL' in monitor.monitored_tickers
        assert 'AAPL' in monitor.active_catalysts

    def test_add_multiple_tickers(self, monitor):
        """Test adding multiple tickers"""
        monitor.add_monitored_ticker('AAPL')
        monitor.add_monitored_ticker('TSLA')
        monitor.add_monitored_ticker('NVDA')

        assert len(monitor.monitored_tickers) == 3

    def test_remove_monitored_ticker(self, monitor):
        """Test removing ticker"""
        monitor.add_monitored_ticker('AAPL')
        monitor.remove_monitored_ticker('AAPL')

        assert 'AAPL' not in monitor.monitored_tickers

    def test_add_duplicate_ticker(self, monitor):
        """Test adding same ticker twice"""
        monitor.add_monitored_ticker('AAPL')
        monitor.add_monitored_ticker('AAPL')

        # Should only appear once in set
        assert monitor.monitored_tickers == {'AAPL'}


class TestCatalystManagement:
    """Test catalyst management"""

    def test_add_catalyst(self, monitor, sample_catalyst):
        """Test adding catalyst"""
        monitor.add_catalyst(sample_catalyst)

        assert 'AAPL' in monitor.active_catalysts
        assert len(monitor.active_catalysts['AAPL']) == 1
        assert len(monitor.catalyst_history) == 1

    def test_add_multiple_catalysts_same_ticker(self, monitor):
        """Test adding multiple catalysts for same ticker"""
        cat1 = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS,
            impact=CatalystImpact.BULLISH,
            urgency=CatalystUrgency.HIGH,
            timestamp=datetime.now(),
            description="Earnings today",
            source="test",
            details={},
            confidence=0.8
        )
        cat2 = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.ANALYST_UPGRADE,
            impact=CatalystImpact.BULLISH,
            urgency=CatalystUrgency.MODERATE,
            timestamp=datetime.now(),
            description="Analyst upgrade",
            source="test",
            details={},
            confidence=0.7
        )

        monitor.add_catalyst(cat1)
        monitor.add_catalyst(cat2)

        assert len(monitor.active_catalysts['AAPL']) == 2

    def test_add_catalysts_different_tickers(self, monitor):
        """Test adding catalysts for different tickers"""
        cat1 = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS,
            impact=CatalystImpact.BULLISH,
            urgency=CatalystUrgency.HIGH,
            timestamp=datetime.now(),
            description="Earnings",
            source="test",
            details={},
            confidence=0.8
        )
        cat2 = Catalyst(
            ticker='TSLA',
            catalyst_type=CatalystType.FDA_APPROVAL,
            impact=CatalystImpact.VERY_BULLISH,
            urgency=CatalystUrgency.IMMEDIATE,
            timestamp=datetime.now(),
            description="FDA approval",
            source="test",
            details={},
            confidence=0.9
        )

        monitor.add_catalyst(cat1)
        monitor.add_catalyst(cat2)

        assert 'AAPL' in monitor.active_catalysts
        assert 'TSLA' in monitor.active_catalysts


class TestGetActiveCatalysts:
    """Test getting active catalysts"""

    def test_get_all_catalysts(self, monitor, sample_catalyst):
        """Test getting all catalysts"""
        monitor.add_catalyst(sample_catalyst)

        catalysts = monitor.get_active_catalysts()

        assert len(catalysts) == 1
        assert catalysts[0] == sample_catalyst

    def test_get_catalysts_by_ticker(self, monitor):
        """Test filtering by ticker"""
        cat1 = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS,
            impact=CatalystImpact.BULLISH,
            urgency=CatalystUrgency.HIGH,
            timestamp=datetime.now(),
            description="AAPL earnings",
            source="test",
            details={},
            confidence=0.8
        )
        cat2 = Catalyst(
            ticker='TSLA',
            catalyst_type=CatalystType.FDA_APPROVAL,
            impact=CatalystImpact.VERY_BULLISH,
            urgency=CatalystUrgency.IMMEDIATE,
            timestamp=datetime.now(),
            description="TSLA approval",
            source="test",
            details={},
            confidence=0.9
        )

        monitor.add_catalyst(cat1)
        monitor.add_catalyst(cat2)

        aapl_catalysts = monitor.get_active_catalysts(ticker='AAPL')

        assert len(aapl_catalysts) == 1
        assert aapl_catalysts[0].ticker == 'AAPL'

    def test_get_catalysts_by_urgency(self, monitor):
        """Test filtering by minimum urgency"""
        cat1 = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS,
            impact=CatalystImpact.BULLISH,
            urgency=CatalystUrgency.IMMEDIATE,
            timestamp=datetime.now(),
            description="Immediate",
            source="test",
            details={},
            confidence=0.8
        )
        cat2 = Catalyst(
            ticker='TSLA',
            catalyst_type=CatalystType.ANALYST_UPGRADE,
            impact=CatalystImpact.BULLISH,
            urgency=CatalystUrgency.LOW,
            timestamp=datetime.now(),
            description="Low urgency",
            source="test",
            details={},
            confidence=0.7
        )

        monitor.add_catalyst(cat1)
        monitor.add_catalyst(cat2)

        immediate = monitor.get_active_catalysts(min_urgency=CatalystUrgency.IMMEDIATE)

        assert len(immediate) == 1
        assert immediate[0].urgency == CatalystUrgency.IMMEDIATE

    def test_get_catalysts_empty(self, monitor):
        """Test getting catalysts when none exist"""
        catalysts = monitor.get_active_catalysts()

        assert catalysts == []


class TestCatalystClassification:
    """Test catalyst classification"""

    def test_classify_earnings_beat(self, monitor):
        """Test classifying earnings beat"""
        desc = "Apple reports earnings beat with EPS of $1.52"

        cat_type, impact, urgency = monitor.classify_catalyst(desc, 'AAPL')

        assert cat_type == CatalystType.EARNINGS
        assert impact == CatalystImpact.BULLISH
        assert urgency == CatalystUrgency.MODERATE

    def test_classify_fda_approval(self, monitor):
        """Test classifying FDA approval"""
        desc = "FDA approves new drug for cancer treatment"

        cat_type, impact, urgency = monitor.classify_catalyst(desc, 'PTGX')

        assert cat_type == CatalystType.FDA_APPROVAL
        assert impact == CatalystImpact.VERY_BULLISH
        assert urgency == CatalystUrgency.IMMEDIATE

    def test_classify_merger(self, monitor):
        """Test classifying merger/acquisition"""
        desc = "Company announces acquisition by major competitor"

        cat_type, impact, urgency = monitor.classify_catalyst(desc, 'SMMT')

        assert cat_type == CatalystType.MERGER_ACQUISITION
        assert impact == CatalystImpact.VERY_BULLISH
        assert urgency == CatalystUrgency.IMMEDIATE

    def test_classify_analyst_upgrade(self, monitor):
        """Test classifying analyst upgrade"""
        desc = "Goldman Sachs upgrades to Buy from Hold"

        cat_type, impact, urgency = monitor.classify_catalyst(desc, 'AAPL')

        assert cat_type == CatalystType.ANALYST_UPGRADE
        assert impact == CatalystImpact.BULLISH
        assert urgency == CatalystUrgency.HIGH

    def test_classify_analyst_downgrade(self, monitor):
        """Test classifying analyst downgrade"""
        desc = "Morgan Stanley downgrades to Sell from Hold"

        cat_type, impact, urgency = monitor.classify_catalyst(desc, 'AAPL')

        assert cat_type == CatalystType.ANALYST_DOWNGRADE
        assert impact == CatalystImpact.BEARISH
        assert urgency == CatalystUrgency.HIGH

    def test_classify_guidance_raise(self, monitor):
        """Test classifying guidance raise"""
        desc = "Company raises full-year guidance above expectations"

        cat_type, impact, urgency = monitor.classify_catalyst(desc, 'AAPL')

        assert cat_type == CatalystType.GUIDANCE_RAISE
        assert impact == CatalystImpact.VERY_BULLISH
        assert urgency == CatalystUrgency.HIGH

    def test_classify_guidance_lower(self, monitor):
        """Test classifying guidance lower"""
        desc = "Company lowers Q4 forecast due to weak demand"

        cat_type, impact, urgency = monitor.classify_catalyst(desc, 'AAPL')

        assert cat_type == CatalystType.GUIDANCE_LOWER
        assert impact == CatalystImpact.VERY_BEARISH
        assert urgency == CatalystUrgency.HIGH

    def test_classify_partnership(self, monitor):
        """Test classifying partnership"""
        desc = "Strategic partnership announced with major tech company"

        cat_type, impact, urgency = monitor.classify_catalyst(desc, 'AAPL')

        assert cat_type == CatalystType.PARTNERSHIP
        assert impact == CatalystImpact.BULLISH
        assert urgency == CatalystUrgency.MODERATE

    def test_classify_generic_news(self, monitor):
        """Test classifying generic news"""
        desc = "Company announces new initiative"

        cat_type, impact, urgency = monitor.classify_catalyst(desc, 'AAPL')

        assert cat_type == CatalystType.OTHER
        assert urgency == CatalystUrgency.MODERATE


class TestAlertGeneration:
    """Test alert generation"""

    def test_generate_alert_bullish(self, monitor):
        """Test generating alert for bullish catalyst"""
        catalyst = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS_BEAT,
            impact=CatalystImpact.VERY_BULLISH,
            urgency=CatalystUrgency.IMMEDIATE,
            timestamp=datetime.now(),
            description="Earnings beat",
            source="test",
            details={},
            confidence=0.9
        )

        alert = monitor.generate_alert(catalyst)

        assert isinstance(alert, CatalystAlert)
        assert alert.action_recommended == "BUY"
        assert alert.position_sizing is not None
        assert alert.position_sizing > 0

    def test_generate_alert_bearish(self, monitor):
        """Test generating alert for bearish catalyst"""
        catalyst = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS_MISS,
            impact=CatalystImpact.VERY_BEARISH,
            urgency=CatalystUrgency.IMMEDIATE,
            timestamp=datetime.now(),
            description="Earnings miss",
            source="test",
            details={},
            confidence=0.8
        )

        alert = monitor.generate_alert(catalyst)

        assert alert.action_recommended == "SELL"

    def test_generate_alert_neutral(self, monitor):
        """Test generating alert for neutral catalyst"""
        catalyst = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.OTHER,
            impact=CatalystImpact.NEUTRAL,
            urgency=CatalystUrgency.LOW,
            timestamp=datetime.now(),
            description="Neutral news",
            source="test",
            details={},
            confidence=0.5
        )

        alert = monitor.generate_alert(catalyst)

        assert alert.action_recommended == "MONITOR"

    def test_alert_position_sizing_immediate(self, monitor):
        """Test position sizing for immediate urgency"""
        catalyst = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.FDA_APPROVAL,
            impact=CatalystImpact.VERY_BULLISH,
            urgency=CatalystUrgency.IMMEDIATE,
            timestamp=datetime.now(),
            description="FDA approval",
            source="test",
            details={},
            confidence=1.0
        )

        alert = monitor.generate_alert(catalyst)

        # Immediate with 100% confidence should suggest larger position
        assert alert.position_sizing <= 0.10  # Max 10%
        assert alert.position_sizing > 0

    def test_alert_position_sizing_low_urgency(self, monitor):
        """Test position sizing for low urgency"""
        catalyst = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.OTHER,
            impact=CatalystImpact.BULLISH,
            urgency=CatalystUrgency.LOW,
            timestamp=datetime.now(),
            description="Low urgency news",
            source="test",
            details={},
            confidence=0.5
        )

        alert = monitor.generate_alert(catalyst)

        # Low urgency should suggest smaller position
        assert alert.position_sizing <= 0.03  # Max 3%


class TestCatalystScoring:
    """Test catalyst scoring"""

    def test_score_single_bullish(self, monitor):
        """Test score with single bullish catalyst"""
        catalyst = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS_BEAT,
            impact=CatalystImpact.VERY_BULLISH,
            urgency=CatalystUrgency.IMMEDIATE,
            timestamp=datetime.now(),
            description="Earnings beat",
            source="test",
            details={},
            confidence=1.0
        )

        monitor.add_catalyst(catalyst)
        score = monitor.get_catalyst_score('AAPL')

        # Very bullish = 1.0, confidence = 1.0, score should be 1.0
        assert score == 1.0

    def test_score_single_bearish(self, monitor):
        """Test score with single bearish catalyst"""
        catalyst = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS_MISS,
            impact=CatalystImpact.VERY_BEARISH,
            urgency=CatalystUrgency.IMMEDIATE,
            timestamp=datetime.now(),
            description="Earnings miss",
            source="test",
            details={},
            confidence=1.0
        )

        monitor.add_catalyst(catalyst)
        score = monitor.get_catalyst_score('AAPL')

        # Very bearish = -1.0, confidence = 1.0, score should be -1.0
        assert score == -1.0

    def test_score_mixed_catalysts(self, monitor):
        """Test score with mixed catalysts"""
        cat1 = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.ANALYST_UPGRADE,
            impact=CatalystImpact.BULLISH,
            urgency=CatalystUrgency.HIGH,
            timestamp=datetime.now(),
            description="Upgrade",
            source="test",
            details={},
            confidence=0.8
        )
        cat2 = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.ANALYST_DOWNGRADE,
            impact=CatalystImpact.BEARISH,
            urgency=CatalystUrgency.HIGH,
            timestamp=datetime.now(),
            description="Downgrade",
            source="test",
            details={},
            confidence=0.8
        )

        monitor.add_catalyst(cat1)
        monitor.add_catalyst(cat2)
        score = monitor.get_catalyst_score('AAPL')

        # Should be close to neutral (0.0)
        assert abs(score) < 0.1

    def test_score_no_catalysts(self, monitor):
        """Test score with no catalysts"""
        score = monitor.get_catalyst_score('AAPL')

        assert score == 0.0


class TestClearOldCatalysts:
    """Test clearing old catalysts"""

    def test_clear_old_catalysts(self, monitor):
        """Test clearing old catalysts"""
        # Add old catalyst
        old_catalyst = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS,
            impact=CatalystImpact.BULLISH,
            urgency=CatalystUrgency.HIGH,
            timestamp=datetime.now() - timedelta(hours=25),
            description="Old earnings",
            source="test",
            details={},
            confidence=0.8
        )

        # Add recent catalyst
        recent_catalyst = Catalyst(
            ticker='TSLA',
            catalyst_type=CatalystType.FDA_APPROVAL,
            impact=CatalystImpact.VERY_BULLISH,
            urgency=CatalystUrgency.IMMEDIATE,
            timestamp=datetime.now(),
            description="Recent approval",
            source="test",
            details={},
            confidence=0.9
        )

        monitor.add_catalyst(old_catalyst)
        monitor.add_catalyst(recent_catalyst)

        # Clear catalysts older than 24 hours
        cleared = monitor.clear_old_catalysts(hours=24)

        assert cleared == 1
        assert 'AAPL' not in monitor.active_catalysts
        assert 'TSLA' in monitor.active_catalysts

    def test_clear_no_old_catalysts(self, monitor):
        """Test clearing when no old catalysts"""
        catalyst = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS,
            impact=CatalystImpact.BULLISH,
            urgency=CatalystUrgency.HIGH,
            timestamp=datetime.now(),
            description="Recent",
            source="test",
            details={},
            confidence=0.8
        )

        monitor.add_catalyst(catalyst)

        cleared = monitor.clear_old_catalysts(hours=24)

        assert cleared == 0
        assert 'AAPL' in monitor.active_catalysts


class TestReportGeneration:
    """Test report generation"""

    def test_generate_report_with_catalysts(self, monitor):
        """Test generating report with catalysts"""
        catalyst = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS_BEAT,
            impact=CatalystImpact.VERY_BULLISH,
            urgency=CatalystUrgency.IMMEDIATE,
            timestamp=datetime.now(),
            description="Earnings beat expectations",
            source="test",
            details={},
            confidence=0.9
        )

        monitor.add_catalyst(catalyst)
        report = monitor.generate_report()

        assert 'AAPL' in report
        assert 'VERY BULLISH' in report
        assert 'IMMEDIATE' in report
        assert 'earnings beat' in report.lower() or 'Earnings Beat' in report

    def test_generate_report_empty(self, monitor):
        """Test generating report with no catalysts"""
        report = monitor.generate_report()

        assert 'No active catalysts' in report

    def test_generate_report_filters_urgency(self, monitor):
        """Test report filters by urgency"""
        cat1 = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS,
            impact=CatalystImpact.BULLISH,
            urgency=CatalystUrgency.IMMEDIATE,
            timestamp=datetime.now(),
            description="Immediate",
            source="test",
            details={},
            confidence=0.8
        )
        cat2 = Catalyst(
            ticker='TSLA',
            catalyst_type=CatalystType.OTHER,
            impact=CatalystImpact.NEUTRAL,
            urgency=CatalystUrgency.LOW,
            timestamp=datetime.now(),
            description="Low urgency",
            source="test",
            details={},
            confidence=0.5
        )

        monitor.add_catalyst(cat1)
        monitor.add_catalyst(cat2)

        report = monitor.generate_report(min_urgency=CatalystUrgency.IMMEDIATE)

        # Should only include IMMEDIATE catalyst
        assert 'AAPL' in report
        assert 'TSLA' not in report

    def test_generate_report_includes_summary(self, monitor):
        """Test report includes summary"""
        catalyst = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS_BEAT,
            impact=CatalystImpact.VERY_BULLISH,
            urgency=CatalystUrgency.IMMEDIATE,
            timestamp=datetime.now(),
            description="Earnings beat",
            source="test",
            details={},
            confidence=0.9
        )

        monitor.add_catalyst(catalyst)
        report = monitor.generate_report()

        assert 'Summary' in report
        assert '1 active catalyst' in report


class TestMarketHours:
    """Test market hours checking"""

    @patch('monitoring.catalyst_monitor.datetime')
    def test_is_market_hours_open(self, mock_datetime, monitor):
        """Test checking if market is open"""
        # Mock current time to be during market hours
        mock_now = Mock()
        mock_now.time.return_value = time(14, 30)  # 2:30 PM
        mock_datetime.now.return_value = mock_now

        assert monitor.is_market_hours() is True

    @patch('monitoring.catalyst_monitor.datetime')
    def test_is_market_hours_closed(self, mock_datetime, monitor):
        """Test checking if market is closed"""
        # Mock current time to be after market close
        mock_now = Mock()
        mock_now.time.return_value = time(17, 0)  # 5:00 PM
        mock_datetime.now.return_value = mock_now

        assert monitor.is_market_hours() is False

    @patch('monitoring.catalyst_monitor.datetime')
    def test_is_market_hours_premarket(self, mock_datetime, monitor):
        """Test checking during pre-market"""
        # Mock current time to be before market open
        mock_now = Mock()
        mock_now.time.return_value = time(8, 0)  # 8:00 AM
        mock_datetime.now.return_value = mock_now

        assert monitor.is_market_hours() is False


class TestConvenienceFunction:
    """Test convenience function"""

    def test_create_catalyst_from_event(self):
        """Test creating catalyst from event data"""
        catalyst = create_catalyst_from_event(
            ticker='AAPL',
            event_type='earnings',
            description='Apple reports earnings beat',
            source='manual',
            confidence=0.9
        )

        assert isinstance(catalyst, Catalyst)
        assert catalyst.ticker == 'AAPL'
        assert catalyst.description == 'Apple reports earnings beat'
        assert catalyst.source == 'manual'
        assert catalyst.confidence == 0.9

    def test_create_catalyst_auto_classification(self):
        """Test catalyst auto-classification"""
        catalyst = create_catalyst_from_event(
            ticker='PTGX',
            event_type='news',
            description='FDA approves new drug',
            confidence=0.95
        )

        # Should auto-classify as FDA approval
        assert catalyst.catalyst_type == CatalystType.FDA_APPROVAL
        assert catalyst.impact == CatalystImpact.VERY_BULLISH
        assert catalyst.urgency == CatalystUrgency.IMMEDIATE


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_catalyst_with_string_enums(self):
        """Test creating catalyst with string enum values"""
        catalyst = Catalyst(
            ticker='AAPL',
            catalyst_type='earnings',
            impact='bullish',
            urgency='high',
            timestamp=datetime.now(),
            description="Test",
            source="test",
            details={},
            confidence=0.8
        )

        # __post_init__ should convert strings to enums
        assert isinstance(catalyst.catalyst_type, CatalystType)
        assert isinstance(catalyst.impact, CatalystImpact)
        assert isinstance(catalyst.urgency, CatalystUrgency)

    def test_score_with_zero_total_weight(self, monitor):
        """Test scoring with zero total weight"""
        catalyst = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS,
            impact=CatalystImpact.BULLISH,
            urgency=CatalystUrgency.HIGH,
            timestamp=datetime.now(),
            description="Test",
            source="test",
            details={},
            confidence=0.0  # Zero confidence
        )

        monitor.add_catalyst(catalyst)
        score = monitor.get_catalyst_score('AAPL')

        # Should return 0 when total weight is 0
        assert score == 0.0

    def test_clear_catalysts_removes_empty_tickers(self, monitor):
        """Test clearing removes tickers with no catalysts"""
        catalyst = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS,
            impact=CatalystImpact.BULLISH,
            urgency=CatalystUrgency.HIGH,
            timestamp=datetime.now() - timedelta(hours=25),
            description="Old",
            source="test",
            details={},
            confidence=0.8
        )

        monitor.add_catalyst(catalyst)
        monitor.clear_old_catalysts(hours=24)

        # AAPL should be removed from active_catalysts
        assert 'AAPL' not in monitor.active_catalysts

    def test_long_description_truncated_in_report(self, monitor):
        """Test long descriptions are truncated in report"""
        catalyst = Catalyst(
            ticker='AAPL',
            catalyst_type=CatalystType.EARNINGS,
            impact=CatalystImpact.BULLISH,
            urgency=CatalystUrgency.HIGH,
            timestamp=datetime.now(),
            description="This is a very long description that should be truncated in the report to avoid making the table too wide and difficult to read",
            source="test",
            details={},
            confidence=0.8
        )

        monitor.add_catalyst(catalyst)
        report = monitor.generate_report()

        # Check that description is truncated (with ...)
        assert '...' in report or len(catalyst.description) <= 60


class TestScanForCatalysts:
    """Test catalyst scanning"""

    def test_scan_adds_tickers_to_monitoring(self, monitor):
        """Test scan adds tickers to monitoring list"""
        tickers = ['AAPL', 'TSLA', 'NVDA']

        monitor.scan_for_catalysts(tickers)

        for ticker in tickers:
            assert ticker in monitor.monitored_tickers

    def test_scan_with_no_clients(self, monitor):
        """Test scan when no API clients configured"""
        # Should not crash even without clients
        catalysts = monitor.scan_for_catalysts(['AAPL'])

        assert isinstance(catalysts, list)
        # May be empty since no clients to fetch data
        assert len(catalysts) == 0
