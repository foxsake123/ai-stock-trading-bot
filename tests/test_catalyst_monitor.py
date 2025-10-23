"""
Comprehensive Test Suite for Catalyst Monitoring System

Tests all components:
- CatalystMonitor: Real-time event tracking and monitoring
- NewsScanner: Breaking news monitoring from Financial Datasets API
- EventCalendar: Scheduled catalyst tracking
- CatalystAlerts: Multi-channel notification system
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List

# Import modules to test
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.monitors.catalyst_monitor import (
    CatalystMonitor,
    CatalystEvent,
    CatalystType,
    CatalystPriority,
    CatalystStatus
)
from src.monitors.news_scanner import NewsScanner, NewsItem
from src.monitors.event_calendar import EventCalendar, ScheduledEvent
from src.alerts.catalyst_alerts import CatalystAlerts


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_news_scanner():
    """Mock NewsScanner for testing"""
    scanner = Mock(spec=NewsScanner)
    scanner.scan_recent_news = AsyncMock(return_value=[])
    scanner.get_breaking_news = AsyncMock(return_value=[])
    scanner.get_sentiment_changes = AsyncMock(return_value={
        'ticker': 'PTGX',
        'avg_sentiment': 0.5,
        'sentiment_trend': 'IMPROVING',
        'article_count': 5
    })
    return scanner


@pytest.fixture
def mock_event_calendar():
    """Mock EventCalendar for testing"""
    calendar = Mock(spec=EventCalendar)
    calendar.get_upcoming_events = AsyncMock(return_value=[])
    calendar.get_events_needing_reminder = Mock(return_value=[])
    calendar.add_event = Mock()
    return calendar


@pytest.fixture
def mock_alert_system():
    """Mock CatalystAlerts for testing"""
    alerts = Mock(spec=CatalystAlerts)
    alerts.send_catalyst_alert = AsyncMock()
    return alerts


@pytest.fixture
def sample_catalyst_event():
    """Sample CatalystEvent for testing"""
    return CatalystEvent(
        ticker="PTGX",
        catalyst_type=CatalystType.FDA_DECISION,
        priority=CatalystPriority.HIGH,
        title="FDA PDUFA Date - Afamitresgene Autoleucel",
        description="FDA decision expected for PTGX's CAR-T therapy",
        scheduled_time=datetime.now() + timedelta(hours=24),
        sentiment="POSITIVE",
        source="Financial Datasets"
    )


@pytest.fixture
def sample_news_item():
    """Sample NewsItem for testing"""
    return NewsItem(
        ticker="PTGX",
        headline="PTGX receives positive FDA panel recommendation",
        summary="FDA advisory committee votes 12-2 in favor",
        published_time=datetime.now(),
        source="Bloomberg",
        sentiment="POSITIVE",
        sentiment_score=0.75,
        relevance_score=0.9
    )


@pytest.fixture
def sample_scheduled_event():
    """Sample ScheduledEvent for testing"""
    return ScheduledEvent(
        ticker="PTGX",
        event_type="FDA_DECISION",
        title="FDA PDUFA Date",
        description="FDA decision expected",
        scheduled_time=datetime.now() + timedelta(hours=24)
    )


# ============================================================================
# CATALYST MONITOR TESTS
# ============================================================================

class TestCatalystMonitorInitialization:
    """Test CatalystMonitor initialization and configuration"""

    def test_initialization_with_defaults(self, mock_news_scanner, mock_event_calendar, mock_alert_system):
        """Test monitor initializes with default settings"""
        monitor = CatalystMonitor(
            news_scanner=mock_news_scanner,
            event_calendar=mock_event_calendar,
            alert_system=mock_alert_system
        )

        assert monitor.news_scanner == mock_news_scanner
        assert monitor.event_calendar == mock_event_calendar
        assert monitor.alert_system == mock_alert_system
        assert monitor.check_interval == 300  # Default 5 minutes
        assert monitor.market_open_hour == 9
        assert monitor.market_close_hour == 16
        assert len(monitor.active_catalysts) == 0
        assert not monitor.is_running

    def test_initialization_with_custom_settings(self, mock_news_scanner, mock_event_calendar, mock_alert_system):
        """Test monitor initializes with custom settings"""
        monitor = CatalystMonitor(
            news_scanner=mock_news_scanner,
            event_calendar=mock_event_calendar,
            alert_system=mock_alert_system,
            check_interval=60,
            market_open_hour=8,
            market_close_hour=17,
            enable_premarket=True,
            enable_afterhours=True
        )

        assert monitor.check_interval == 60
        assert monitor.market_open_hour == 8
        assert monitor.market_close_hour == 17
        assert monitor.enable_premarket is True
        assert monitor.enable_afterhours is True


class TestCatalystDetection:
    """Test catalyst event detection from news and calendar"""

    @pytest.mark.asyncio
    async def test_detect_fda_catalyst_from_news(self, mock_news_scanner, mock_event_calendar, mock_alert_system):
        """Test detection of FDA catalyst from breaking news"""
        monitor = CatalystMonitor(
            news_scanner=mock_news_scanner,
            event_calendar=mock_event_calendar,
            alert_system=mock_alert_system
        )

        # Mock news with FDA keywords
        mock_news_scanner.get_breaking_news = AsyncMock(return_value=[{
            'ticker': 'PTGX',
            'headline': 'PTGX receives FDA approval for CAR-T therapy',
            'summary': 'FDA approves afamitresgene autoleucel',
            'published_time': datetime.now(),
            'sentiment': 'POSITIVE',
            'sentiment_score': 0.85,
            'relevance_score': 0.95
        }])

        await monitor._check_catalysts()

        # Should have detected FDA catalyst
        assert len(monitor.active_catalysts) > 0
        event = list(monitor.active_catalysts.values())[0]
        assert event.catalyst_type == CatalystType.FDA_DECISION
        assert event.ticker == 'PTGX'
        assert event.priority == CatalystPriority.CRITICAL

    @pytest.mark.asyncio
    async def test_detect_earnings_catalyst_from_calendar(self, mock_news_scanner, mock_event_calendar, mock_alert_system):
        """Test detection of earnings catalyst from calendar"""
        monitor = CatalystMonitor(
            news_scanner=mock_news_scanner,
            event_calendar=mock_event_calendar,
            alert_system=mock_alert_system
        )

        # Mock upcoming earnings event
        upcoming_event = ScheduledEvent(
            ticker="AAPL",
            event_type="EARNINGS_RELEASE",
            title="Q4 2025 Earnings",
            description="Apple Q4 earnings release",
            scheduled_time=datetime.now() + timedelta(hours=2)
        )
        mock_event_calendar.get_upcoming_events = AsyncMock(return_value=[{
            'ticker': 'AAPL',
            'type': 'EARNINGS_RELEASE',
            'title': 'Q4 2025 Earnings',
            'scheduled_time': datetime.now() + timedelta(hours=2),
            'hours_until': 2.0
        }])

        await monitor._check_catalysts()

        # Should have detected earnings catalyst
        assert len(monitor.active_catalysts) > 0


class TestPriorityClassification:
    """Test automatic priority classification for catalysts"""

    def test_fda_approval_critical_priority(self, mock_news_scanner, mock_event_calendar, mock_alert_system):
        """Test FDA approvals get CRITICAL priority"""
        monitor = CatalystMonitor(
            news_scanner=mock_news_scanner,
            event_calendar=mock_event_calendar,
            alert_system=mock_alert_system
        )

        event = CatalystEvent(
            ticker="PTGX",
            catalyst_type=CatalystType.FDA_DECISION,
            priority=CatalystPriority.CRITICAL,  # Should be auto-assigned
            title="FDA Approval",
            description="FDA approves new drug",
            sentiment="POSITIVE"
        )

        assert event.priority == CatalystPriority.CRITICAL

    def test_earnings_beat_high_priority(self, mock_news_scanner, mock_event_calendar, mock_alert_system):
        """Test earnings beats get HIGH priority"""
        monitor = CatalystMonitor(
            news_scanner=mock_news_scanner,
            event_calendar=mock_event_calendar,
            alert_system=mock_alert_system
        )

        event = CatalystEvent(
            ticker="AAPL",
            catalyst_type=CatalystType.EARNINGS_RELEASE,
            priority=CatalystPriority.HIGH,
            title="Q4 Earnings Beat",
            description="Apple beats EPS by 15%",
            sentiment="POSITIVE"
        )

        assert event.priority == CatalystPriority.HIGH


class TestEventTracking:
    """Test catalyst event tracking and state management"""

    @pytest.mark.asyncio
    async def test_add_catalyst_event(self, mock_news_scanner, mock_event_calendar, mock_alert_system, sample_catalyst_event):
        """Test adding catalyst event to tracking"""
        monitor = CatalystMonitor(
            news_scanner=mock_news_scanner,
            event_calendar=mock_event_calendar,
            alert_system=mock_alert_system
        )

        await monitor._process_event(sample_catalyst_event)

        assert len(monitor.active_catalysts) == 1
        assert sample_catalyst_event.ticker in monitor.active_catalysts

    @pytest.mark.asyncio
    async def test_duplicate_event_handling(self, mock_news_scanner, mock_event_calendar, mock_alert_system, sample_catalyst_event):
        """Test that duplicate events are not added twice"""
        monitor = CatalystMonitor(
            news_scanner=mock_news_scanner,
            event_calendar=mock_event_calendar,
            alert_system=mock_alert_system
        )

        await monitor._process_event(sample_catalyst_event)
        await monitor._process_event(sample_catalyst_event)  # Duplicate

        # Should only have one event
        assert len(monitor.active_catalysts) == 1

    @pytest.mark.asyncio
    async def test_event_status_update(self, mock_news_scanner, mock_event_calendar, mock_alert_system, sample_catalyst_event):
        """Test updating event status"""
        monitor = CatalystMonitor(
            news_scanner=mock_news_scanner,
            event_calendar=mock_event_calendar,
            alert_system=mock_alert_system
        )

        await monitor._process_event(sample_catalyst_event)

        # Update status
        sample_catalyst_event.status = CatalystStatus.OCCURRED
        sample_catalyst_event.actual_time = datetime.now()

        assert sample_catalyst_event.status == CatalystStatus.OCCURRED
        assert sample_catalyst_event.actual_time is not None


class TestAlertSending:
    """Test alert sending for catalyst events"""

    @pytest.mark.asyncio
    async def test_send_alert_for_critical_event(self, mock_news_scanner, mock_event_calendar, mock_alert_system):
        """Test alerts are sent for CRITICAL events"""
        monitor = CatalystMonitor(
            news_scanner=mock_news_scanner,
            event_calendar=mock_event_calendar,
            alert_system=mock_alert_system
        )

        critical_event = CatalystEvent(
            ticker="PTGX",
            catalyst_type=CatalystType.FDA_DECISION,
            priority=CatalystPriority.CRITICAL,
            title="FDA Approval",
            description="FDA approves new drug",
            sentiment="POSITIVE"
        )

        await monitor._process_event(critical_event)

        # Alert should have been sent
        mock_alert_system.send_catalyst_alert.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_alert_for_low_priority(self, mock_news_scanner, mock_event_calendar, mock_alert_system):
        """Test LOW priority events don't trigger alerts"""
        monitor = CatalystMonitor(
            news_scanner=mock_news_scanner,
            event_calendar=mock_event_calendar,
            alert_system=mock_alert_system
        )

        low_event = CatalystEvent(
            ticker="AAPL",
            catalyst_type=CatalystType.CONFERENCE_PRESENTATION,
            priority=CatalystPriority.LOW,
            title="Conference attendance",
            description="Company attending investor conference",
            sentiment="NEUTRAL"
        )

        await monitor._process_event(low_event)

        # No alert should be sent for LOW priority
        mock_alert_system.send_catalyst_alert.assert_not_called()


class TestMarketHoursDetection:
    """Test market hours detection logic"""

    def test_during_market_hours(self, mock_news_scanner, mock_event_calendar, mock_alert_system):
        """Test detection during regular market hours"""
        monitor = CatalystMonitor(
            news_scanner=mock_news_scanner,
            event_calendar=mock_event_calendar,
            alert_system=mock_alert_system
        )

        # Mock time to 2 PM ET (during market hours)
        with patch('src.monitors.catalyst_monitor.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 10, 23, 14, 0)  # 2 PM
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            # Should be monitoring
            assert monitor._should_monitor_now() is True

    def test_outside_market_hours(self, mock_news_scanner, mock_event_calendar, mock_alert_system):
        """Test detection outside market hours"""
        monitor = CatalystMonitor(
            news_scanner=mock_news_scanner,
            event_calendar=mock_event_calendar,
            alert_system=mock_alert_system,
            enable_premarket=False,
            enable_afterhours=False
        )

        # Mock time to 8 AM ET (before market open)
        with patch('src.monitors.catalyst_monitor.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 10, 23, 8, 0)  # 8 AM
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            # Should not be monitoring (premarket disabled)
            assert monitor._should_monitor_now() is False


# ============================================================================
# NEWS SCANNER TESTS
# ============================================================================

class TestNewsScannerInitialization:
    """Test NewsScanner initialization"""

    def test_initialization_with_api_key(self):
        """Test scanner initializes with API key"""
        scanner = NewsScanner(api_key="test_key_123")
        assert scanner.api_key == "test_key_123"
        assert scanner.cache_minutes == 5
        assert scanner.max_retries == 3

    def test_initialization_from_env(self):
        """Test scanner loads API key from environment"""
        with patch.dict(os.environ, {'FINANCIAL_DATASETS_API_KEY': 'env_key_456'}):
            scanner = NewsScanner()
            assert scanner.api_key == 'env_key_456'


class TestNewsScanning:
    """Test news scanning functionality"""

    @pytest.mark.asyncio
    async def test_scan_recent_news_success(self):
        """Test successful news scanning"""
        scanner = NewsScanner(api_key="test_key")

        # Mock API response
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'news': [{
                    'headline': 'PTGX announces M&A',
                    'summary': 'Company in acquisition talks',
                    'published_at': datetime.now().isoformat(),
                    'source': {'name': 'Bloomberg'},
                    'sentiment': {'score': 0.65, 'label': 'POSITIVE'},
                    'relevance_score': 0.85
                }]
            })

            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

            news = await scanner.scan_recent_news(['PTGX'], minutes_back=60)

            assert len(news) > 0

    @pytest.mark.asyncio
    async def test_cache_usage(self):
        """Test that cache reduces API calls"""
        scanner = NewsScanner(api_key="test_key", cache_minutes=5)

        # First call should hit API
        with patch.object(scanner, '_fetch_from_api', new=AsyncMock(return_value=[])) as mock_fetch:
            await scanner.scan_recent_news(['AAPL'])
            assert mock_fetch.call_count == 1

            # Second call within cache window should use cache
            await scanner.scan_recent_news(['AAPL'])
            assert mock_fetch.call_count == 1  # Still 1, cache was used


class TestSentimentAnalysis:
    """Test sentiment analysis features"""

    @pytest.mark.asyncio
    async def test_sentiment_trend_improving(self):
        """Test detection of improving sentiment"""
        scanner = NewsScanner(api_key="test_key")

        # Mock news items with improving sentiment
        mock_items = [
            NewsItem(
                ticker="PTGX",
                headline=f"News {i}",
                summary="Summary",
                published_time=datetime.now() - timedelta(hours=i),
                source="Test",
                sentiment_score=0.3 + (i * 0.05)  # Improving over time
            )
            for i in range(10)
        ]

        with patch.object(scanner, '_fetch_ticker_news', new=AsyncMock(return_value=mock_items)):
            result = await scanner.get_sentiment_changes('PTGX', hours_back=24)

            assert result['sentiment_trend'] == 'IMPROVING'

    @pytest.mark.asyncio
    async def test_sentiment_trend_declining(self):
        """Test detection of declining sentiment"""
        scanner = NewsScanner(api_key="test_key")

        # Mock news items with declining sentiment
        mock_items = [
            NewsItem(
                ticker="SMMT",
                headline=f"News {i}",
                summary="Summary",
                published_time=datetime.now() - timedelta(hours=i),
                source="Test",
                sentiment_score=0.7 - (i * 0.05)  # Declining over time
            )
            for i in range(10)
        ]

        with patch.object(scanner, '_fetch_ticker_news', new=AsyncMock(return_value=mock_items)):
            result = await scanner.get_sentiment_changes('SMMT', hours_back=24)

            assert result['sentiment_trend'] == 'DECLINING'


# ============================================================================
# EVENT CALENDAR TESTS
# ============================================================================

class TestEventCalendarInitialization:
    """Test EventCalendar initialization"""

    def test_initialization_with_defaults(self):
        """Test calendar initializes with default settings"""
        with patch.object(EventCalendar, 'load_from_storage'):
            calendar = EventCalendar()
            assert calendar.reminder_hours == [24, 4, 1]
            assert len(calendar.events) == 0


class TestEventManagement:
    """Test event addition and management"""

    def test_add_fda_event(self):
        """Test adding FDA event"""
        with patch.object(EventCalendar, 'load_from_storage'):
            with patch.object(EventCalendar, 'save_to_storage'):
                calendar = EventCalendar()

                event = calendar.add_fda_event(
                    ticker="PTGX",
                    pdufa_date=datetime(2025, 11, 15),
                    drug_name="Afamitresgene Autoleucel",
                    indication="DLBCL"
                )

                assert event.ticker == "PTGX"
                assert event.event_type == "FDA_DECISION"
                assert "PTGX" in calendar.events

    def test_add_earnings_event(self):
        """Test adding earnings event"""
        with patch.object(EventCalendar, 'load_from_storage'):
            with patch.object(EventCalendar, 'save_to_storage'):
                calendar = EventCalendar()

                event = calendar.add_earnings_event(
                    ticker="AAPL",
                    earnings_date=datetime(2025, 11, 1),
                    quarter="Q4",
                    fiscal_year=2025
                )

                assert event.ticker == "AAPL"
                assert event.event_type == "EARNINGS_RELEASE"

    def test_duplicate_event_prevention(self):
        """Test that duplicate events are not added"""
        with patch.object(EventCalendar, 'load_from_storage'):
            with patch.object(EventCalendar, 'save_to_storage'):
                calendar = EventCalendar()

                # Add same event twice
                calendar.add_fda_event(
                    ticker="PTGX",
                    pdufa_date=datetime(2025, 11, 15),
                    drug_name="Drug A",
                    indication="Disease A"
                )

                initial_count = len(calendar.events.get("PTGX", []))

                calendar.add_fda_event(
                    ticker="PTGX",
                    pdufa_date=datetime(2025, 11, 15),
                    drug_name="Drug A",
                    indication="Disease A"
                )

                # Should still be same count
                assert len(calendar.events.get("PTGX", [])) == initial_count


class TestReminders:
    """Test reminder functionality"""

    def test_get_events_needing_reminder(self):
        """Test detection of events needing reminders"""
        with patch.object(EventCalendar, 'load_from_storage'):
            with patch.object(EventCalendar, 'save_to_storage'):
                calendar = EventCalendar(reminder_hours=[24])

                # Add event 24 hours from now
                event = ScheduledEvent(
                    ticker="PTGX",
                    event_type="FDA_DECISION",
                    title="FDA PDUFA",
                    description="FDA decision",
                    scheduled_time=datetime.now() + timedelta(hours=24)
                )
                calendar.events["PTGX"] = [event]

                # Should need reminder
                reminders = calendar.get_events_needing_reminder()
                assert len(reminders) > 0


# ============================================================================
# CATALYST ALERTS TESTS
# ============================================================================

class TestCatalystAlertsInitialization:
    """Test CatalystAlerts initialization"""

    def test_initialization_with_email_config(self):
        """Test alerts initialize with email configuration"""
        email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'test@gmail.com',
            'password': 'test_password',
            'from_email': 'test@gmail.com',
            'to_emails': ['recipient@gmail.com']
        }

        alerts = CatalystAlerts(email_config=email_config, primary_channel='email')
        assert alerts.email_config == email_config
        assert alerts.primary_channel == 'email'


class TestAlertSendingByPriority:
    """Test alert sending based on priority levels"""

    @pytest.mark.asyncio
    async def test_critical_alert_all_channels(self, sample_catalyst_event):
        """Test CRITICAL alerts go to all channels"""
        alerts = CatalystAlerts(primary_channel='email')
        sample_catalyst_event.priority = CatalystPriority.CRITICAL

        with patch.object(alerts, '_send_email_alert', new=AsyncMock()) as mock_email:
            with patch.object(alerts, '_send_slack_alert', new=AsyncMock()) as mock_slack:
                with patch.object(alerts, '_send_discord_alert', new=AsyncMock()) as mock_discord:
                    with patch.object(alerts, '_send_telegram_alert', new=AsyncMock()) as mock_telegram:
                        await alerts.send_catalyst_alert(sample_catalyst_event)

                        # All channels should be called
                        mock_email.assert_called_once()
                        mock_slack.assert_called_once()
                        mock_discord.assert_called_once()
                        mock_telegram.assert_called_once()

    @pytest.mark.asyncio
    async def test_high_alert_email_plus_primary(self, sample_catalyst_event):
        """Test HIGH alerts go to email + primary channel"""
        alerts = CatalystAlerts(primary_channel='slack')
        sample_catalyst_event.priority = CatalystPriority.HIGH

        with patch.object(alerts, '_send_email_alert', new=AsyncMock()) as mock_email:
            with patch.object(alerts, '_send_slack_alert', new=AsyncMock()) as mock_slack:
                await alerts.send_catalyst_alert(sample_catalyst_event)

                # Email and Slack should be called
                mock_email.assert_called_once()
                mock_slack.assert_called_once()

    @pytest.mark.asyncio
    async def test_low_alert_no_send(self, sample_catalyst_event):
        """Test LOW priority events are logged only"""
        alerts = CatalystAlerts(primary_channel='email')
        sample_catalyst_event.priority = CatalystPriority.LOW

        with patch.object(alerts, '_send_email_alert', new=AsyncMock()) as mock_email:
            await alerts.send_catalyst_alert(sample_catalyst_event)

            # No alerts should be sent
            mock_email.assert_not_called()


class TestAlertHistory:
    """Test alert history tracking"""

    @pytest.mark.asyncio
    async def test_alert_recorded_in_history(self, sample_catalyst_event):
        """Test alerts are recorded in history"""
        alerts = CatalystAlerts(primary_channel='email')

        initial_count = len(alerts.sent_alerts)

        with patch.object(alerts, '_send_email_alert', new=AsyncMock()):
            await alerts.send_catalyst_alert(sample_catalyst_event)

        # History should have new entry
        assert len(alerts.sent_alerts) == initial_count + 1

    def test_get_alert_stats(self, sample_catalyst_event):
        """Test alert statistics generation"""
        alerts = CatalystAlerts(primary_channel='email')

        # Manually add to history
        alerts.sent_alerts.append({
            'ticker': 'PTGX',
            'catalyst_type': 'FDA_DECISION',
            'priority': 'HIGH',
            'timestamp': datetime.now(),
            'channels': ['email']
        })

        stats = alerts.get_alert_stats()

        assert stats['total_alerts'] == 1
        assert 'HIGH' in stats['by_priority']
        assert 'PTGX' in stats['by_ticker']


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestEndToEndMonitoring:
    """Test end-to-end monitoring flow"""

    @pytest.mark.asyncio
    async def test_complete_monitoring_cycle(self, mock_news_scanner, mock_event_calendar, mock_alert_system):
        """Test complete monitoring cycle from detection to alert"""
        monitor = CatalystMonitor(
            news_scanner=mock_news_scanner,
            event_calendar=mock_event_calendar,
            alert_system=mock_alert_system
        )

        # Mock breaking news
        mock_news_scanner.get_breaking_news = AsyncMock(return_value=[{
            'ticker': 'PTGX',
            'headline': 'PTGX announces M&A agreement',
            'summary': 'Company to be acquired at $100/share',
            'published_time': datetime.now(),
            'sentiment': 'POSITIVE',
            'sentiment_score': 0.95,
            'relevance_score': 1.0
        }])

        # Run monitoring check
        await monitor._check_catalysts()

        # Should have detected event and sent alert
        assert len(monitor.active_catalysts) > 0
        mock_alert_system.send_catalyst_alert.assert_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
