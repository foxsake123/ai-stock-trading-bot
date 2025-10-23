"""
Catalyst Monitor - Real-Time Event Tracking System
Monitors catalysts (FDA, earnings, launches) affecting positions in real-time
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Callable
from enum import Enum
import json

logger = logging.getLogger(__name__)


class CatalystType(Enum):
    """Types of catalysts to monitor"""
    FDA_DECISION = "fda_decision"
    EARNINGS_RELEASE = "earnings_release"
    PRODUCT_LAUNCH = "product_launch"
    CONFERENCE_PRESENTATION = "conference_presentation"
    MERGER_ACQUISITION = "merger_acquisition"
    REGULATORY_FILING = "regulatory_filing"
    CLINICAL_TRIAL = "clinical_trial"
    PARTNERSHIP_DEAL = "partnership_deal"
    INSIDER_TRANSACTION = "insider_transaction"
    NEWS_SENTIMENT_SHIFT = "news_sentiment_shift"


class CatalystPriority(Enum):
    """Priority levels for catalyst alerts"""
    CRITICAL = "CRITICAL"  # Immediate action required
    HIGH = "HIGH"          # Review needed soon
    MEDIUM = "MEDIUM"      # Awareness needed
    LOW = "LOW"            # Logged only


class CatalystStatus(Enum):
    """Status of catalyst events"""
    SCHEDULED = "scheduled"
    MONITORING = "monitoring"
    TRIGGERED = "triggered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class CatalystEvent:
    """Represents a single catalyst event"""
    ticker: str
    catalyst_type: CatalystType
    priority: CatalystPriority
    title: str
    description: str
    scheduled_time: Optional[datetime] = None
    actual_time: Optional[datetime] = None
    status: CatalystStatus = CatalystStatus.SCHEDULED
    sentiment: Optional[str] = None  # POSITIVE, NEGATIVE, NEUTRAL
    source: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "ticker": self.ticker,
            "catalyst_type": self.catalyst_type.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "actual_time": self.actual_time.isoformat() if self.actual_time else None,
            "status": self.status.value,
            "sentiment": self.sentiment,
            "source": self.source,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class CatalystMonitor:
    """
    Real-time catalyst monitoring system

    Features:
    - Tracks FDA decisions, earnings, launches, etc.
    - Monitors news sentiment in real-time
    - Sends priority-based alerts
    - Maintains calendar of upcoming catalysts
    - Runs continuously during market hours
    """

    def __init__(
        self,
        news_scanner,
        event_calendar,
        alert_system,
        market_hours: tuple = (9, 30, 16, 0),  # (start_hour, start_min, end_hour, end_min)
        check_interval_seconds: int = 60,
        enable_premarket: bool = True,
        enable_afterhours: bool = True
    ):
        """
        Initialize Catalyst Monitor

        Args:
            news_scanner: NewsScanner instance for real-time news
            event_calendar: EventCalendar instance for scheduled events
            alert_system: CatalystAlerts instance for notifications
            market_hours: Tuple of (start_hour, start_min, end_hour, end_min) in ET
            check_interval_seconds: How often to check for new catalysts
            enable_premarket: Monitor during pre-market hours (7-9:30 AM)
            enable_afterhours: Monitor during after-hours (4-8 PM)
        """
        self.news_scanner = news_scanner
        self.event_calendar = event_calendar
        self.alert_system = alert_system

        self.market_hours = market_hours
        self.check_interval = check_interval_seconds
        self.enable_premarket = enable_premarket
        self.enable_afterhours = enable_afterhours

        # Tracking
        self.monitored_tickers: Set[str] = set()
        self.active_catalysts: Dict[str, List[CatalystEvent]] = {}  # ticker -> events
        self.triggered_events: List[CatalystEvent] = []
        self.event_callbacks: List[Callable] = []

        # State
        self.is_running = False
        self.monitor_task = None

        logger.info(f"CatalystMonitor initialized (interval: {check_interval_seconds}s)")

    def add_ticker(self, ticker: str) -> None:
        """Add ticker to monitoring list"""
        self.monitored_tickers.add(ticker.upper())
        logger.info(f"Added {ticker} to catalyst monitoring")

    def remove_ticker(self, ticker: str) -> None:
        """Remove ticker from monitoring list"""
        ticker = ticker.upper()
        self.monitored_tickers.discard(ticker)
        if ticker in self.active_catalysts:
            del self.active_catalysts[ticker]
        logger.info(f"Removed {ticker} from catalyst monitoring")

    def add_event_callback(self, callback: Callable) -> None:
        """Add callback function to be called when events trigger"""
        self.event_callbacks.append(callback)
        logger.info(f"Added event callback: {callback.__name__}")

    async def start_monitoring(self) -> None:
        """Start continuous catalyst monitoring"""
        if self.is_running:
            logger.warning("Catalyst monitoring already running")
            return

        self.is_running = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Catalyst monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop catalyst monitoring"""
        if not self.is_running:
            return

        self.is_running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("Catalyst monitoring stopped")

    async def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Check if we should be monitoring now
                if not self._should_monitor_now():
                    logger.debug("Outside monitoring hours, waiting...")
                    await asyncio.sleep(300)  # Check every 5 minutes
                    continue

                # Check for new catalysts
                await self._check_catalysts()

                # Wait for next check
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Error in catalyst monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    def _should_monitor_now(self) -> bool:
        """Determine if we should be monitoring at current time"""
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute

        start_hour, start_min, end_hour, end_min = self.market_hours

        # Regular market hours
        if (current_hour > start_hour or (current_hour == start_hour and current_minute >= start_min)) and \
           (current_hour < end_hour or (current_hour == end_hour and current_minute < end_min)):
            return True

        # Pre-market (7:00 AM - 9:30 AM ET)
        if self.enable_premarket and 7 <= current_hour < start_hour:
            return True

        # After-hours (4:00 PM - 8:00 PM ET)
        if self.enable_afterhours and end_hour <= current_hour < 20:
            return True

        return False

    async def _check_catalysts(self) -> None:
        """Check for new catalyst events"""
        if not self.monitored_tickers:
            return

        logger.debug(f"Checking catalysts for {len(self.monitored_tickers)} tickers")

        # Check scheduled events from calendar
        scheduled_events = await self._check_scheduled_events()

        # Check real-time news
        news_events = await self._check_news_events()

        # Process all new events
        all_events = scheduled_events + news_events

        for event in all_events:
            await self._process_event(event)

    async def _check_scheduled_events(self) -> List[CatalystEvent]:
        """Check event calendar for upcoming scheduled events"""
        events = []

        try:
            # Get events from calendar (next 24 hours)
            calendar_events = await self.event_calendar.get_upcoming_events(
                tickers=list(self.monitored_tickers),
                hours_ahead=24
            )

            for cal_event in calendar_events:
                # Convert calendar event to CatalystEvent
                event = CatalystEvent(
                    ticker=cal_event.get('ticker'),
                    catalyst_type=CatalystType[cal_event.get('type', 'EARNINGS_RELEASE')],
                    priority=self._determine_priority(cal_event),
                    title=cal_event.get('title'),
                    description=cal_event.get('description', ''),
                    scheduled_time=cal_event.get('scheduled_time'),
                    status=CatalystStatus.SCHEDULED,
                    source='calendar',
                    metadata=cal_event.get('metadata', {})
                )

                # Check if event is imminent (within check interval)
                if event.scheduled_time:
                    time_until = (event.scheduled_time - datetime.now()).total_seconds()
                    if 0 <= time_until <= self.check_interval * 2:
                        event.status = CatalystStatus.MONITORING
                        events.append(event)

        except Exception as e:
            logger.error(f"Error checking scheduled events: {e}")

        return events

    async def _check_news_events(self) -> List[CatalystEvent]:
        """Check news scanner for real-time breaking news"""
        events = []

        try:
            # Scan news for monitored tickers
            news_items = await self.news_scanner.scan_recent_news(
                tickers=list(self.monitored_tickers),
                minutes_back=self.check_interval // 60 + 5  # Slight overlap
            )

            for news_item in news_items:
                # Check if this is a significant catalyst
                if self._is_significant_news(news_item):
                    event = CatalystEvent(
                        ticker=news_item.get('ticker'),
                        catalyst_type=self._classify_news_type(news_item),
                        priority=self._determine_priority_from_news(news_item),
                        title=news_item.get('headline', ''),
                        description=news_item.get('summary', ''),
                        actual_time=news_item.get('published_time'),
                        status=CatalystStatus.TRIGGERED,
                        sentiment=news_item.get('sentiment'),
                        source=news_item.get('source'),
                        metadata=news_item
                    )

                    events.append(event)

        except Exception as e:
            logger.error(f"Error checking news events: {e}")

        return events

    def _is_significant_news(self, news_item: Dict) -> bool:
        """Determine if news item is a significant catalyst"""
        # Check for catalyst keywords
        catalyst_keywords = [
            'fda', 'approval', 'clinical trial', 'phase', 'pdufa',
            'earnings', 'revenue', 'guidance', 'beat', 'miss',
            'merger', 'acquisition', 'takeover', 'offer',
            'partnership', 'deal', 'agreement',
            'launch', 'release', 'unveil',
            'insider', 'ceo', 'cfo', 'buy', 'sell'
        ]

        headline = news_item.get('headline', '').lower()
        summary = news_item.get('summary', '').lower()

        for keyword in catalyst_keywords:
            if keyword in headline or keyword in summary:
                return True

        # Check sentiment magnitude
        sentiment_score = news_item.get('sentiment_score', 0)
        if abs(sentiment_score) > 0.5:  # Strong positive or negative
            return True

        return False

    def _classify_news_type(self, news_item: Dict) -> CatalystType:
        """Classify news item into catalyst type"""
        headline = news_item.get('headline', '').lower()
        summary = news_item.get('summary', '').lower()
        text = headline + ' ' + summary

        # FDA/Regulatory
        if any(kw in text for kw in ['fda', 'approval', 'pdufa', 'clinical trial']):
            return CatalystType.FDA_DECISION

        # Earnings
        if any(kw in text for kw in ['earnings', 'revenue', 'guidance', 'eps']):
            return CatalystType.EARNINGS_RELEASE

        # M&A
        if any(kw in text for kw in ['merger', 'acquisition', 'takeover', 'offer']):
            return CatalystType.MERGER_ACQUISITION

        # Product Launch
        if any(kw in text for kw in ['launch', 'release', 'unveil', 'debut']):
            return CatalystType.PRODUCT_LAUNCH

        # Partnership
        if any(kw in text for kw in ['partnership', 'deal', 'agreement', 'collaboration']):
            return CatalystType.PARTNERSHIP_DEAL

        # Insider Transaction
        if any(kw in text for kw in ['insider', 'ceo', 'cfo', 'director', 'buy', 'sell']):
            return CatalystType.INSIDER_TRANSACTION

        # Default to sentiment shift
        return CatalystType.NEWS_SENTIMENT_SHIFT

    def _determine_priority(self, event: Dict) -> CatalystPriority:
        """Determine priority level for calendar event"""
        event_type = event.get('type', '').upper()
        time_until = None

        if event.get('scheduled_time'):
            time_until = (event['scheduled_time'] - datetime.now()).total_seconds() / 3600  # hours

        # FDA decisions are always CRITICAL
        if 'FDA' in event_type:
            return CatalystPriority.CRITICAL

        # Earnings within 24 hours are HIGH
        if 'EARNINGS' in event_type and time_until and time_until < 24:
            return CatalystPriority.HIGH

        # M&A events are HIGH
        if 'MERGER' in event_type or 'ACQUISITION' in event_type:
            return CatalystPriority.HIGH

        # Product launches are MEDIUM
        if 'LAUNCH' in event_type:
            return CatalystPriority.MEDIUM

        # Default to LOW
        return CatalystPriority.LOW

    def _determine_priority_from_news(self, news_item: Dict) -> CatalystPriority:
        """Determine priority level for news event"""
        headline = news_item.get('headline', '').lower()
        sentiment_score = news_item.get('sentiment_score', 0)

        # Breaking FDA news is CRITICAL
        if 'fda' in headline and any(kw in headline for kw in ['approval', 'rejection', 'halt']):
            return CatalystPriority.CRITICAL

        # Earnings surprises are HIGH
        if any(kw in headline for kw in ['beat', 'miss', 'surprise']):
            return CatalystPriority.HIGH

        # M&A offers are CRITICAL
        if any(kw in headline for kw in ['offer', 'takeover', 'bid']):
            return CatalystPriority.CRITICAL

        # Strong sentiment shifts (>0.7 or <-0.7) are HIGH
        if abs(sentiment_score) > 0.7:
            return CatalystPriority.HIGH

        # Moderate sentiment shifts are MEDIUM
        if abs(sentiment_score) > 0.4:
            return CatalystPriority.MEDIUM

        return CatalystPriority.LOW

    async def _process_event(self, event: CatalystEvent) -> None:
        """Process a catalyst event"""
        ticker = event.ticker

        # Add to active catalysts
        if ticker not in self.active_catalysts:
            self.active_catalysts[ticker] = []

        # Check for duplicates (same event within 1 hour)
        is_duplicate = False
        for existing_event in self.active_catalysts[ticker]:
            if (existing_event.catalyst_type == event.catalyst_type and
                existing_event.title == event.title and
                abs((existing_event.timestamp - event.timestamp).total_seconds()) < 3600):
                is_duplicate = True
                break

        if is_duplicate:
            logger.debug(f"Duplicate event for {ticker}, skipping")
            return

        # Add to tracking
        self.active_catalysts[ticker].append(event)
        self.triggered_events.append(event)

        logger.info(f"New catalyst for {ticker}: {event.catalyst_type.value} ({event.priority.value})")

        # Send alert
        await self._send_alert(event)

        # Call registered callbacks
        for callback in self.event_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")

    async def _send_alert(self, event: CatalystEvent) -> None:
        """Send alert for catalyst event"""
        try:
            await self.alert_system.send_catalyst_alert(event)
        except Exception as e:
            logger.error(f"Error sending alert for {event.ticker}: {e}")

    def get_active_catalysts(self, ticker: Optional[str] = None) -> Dict[str, List[CatalystEvent]]:
        """Get active catalysts for ticker(s)"""
        if ticker:
            ticker = ticker.upper()
            return {ticker: self.active_catalysts.get(ticker, [])}
        return self.active_catalysts

    def get_critical_catalysts(self) -> List[CatalystEvent]:
        """Get all critical priority catalysts"""
        critical = []
        for events in self.active_catalysts.values():
            critical.extend([e for e in events if e.priority == CatalystPriority.CRITICAL])
        return critical

    def get_triggered_events_since(self, hours: int = 24) -> List[CatalystEvent]:
        """Get events triggered in last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [e for e in self.triggered_events if e.timestamp >= cutoff]

    def clear_old_events(self, hours: int = 48) -> int:
        """Clear events older than N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        removed_count = 0

        for ticker in list(self.active_catalysts.keys()):
            original_count = len(self.active_catalysts[ticker])
            self.active_catalysts[ticker] = [
                e for e in self.active_catalysts[ticker]
                if e.timestamp >= cutoff
            ]
            removed_count += original_count - len(self.active_catalysts[ticker])

            # Remove ticker if no events left
            if not self.active_catalysts[ticker]:
                del self.active_catalysts[ticker]

        logger.info(f"Cleared {removed_count} old catalyst events")
        return removed_count

    def get_monitoring_stats(self) -> Dict:
        """Get monitoring statistics"""
        total_events = sum(len(events) for events in self.active_catalysts.values())

        priority_counts = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0
        }

        for events in self.active_catalysts.values():
            for event in events:
                priority_counts[event.priority.value] += 1

        return {
            'monitored_tickers': len(self.monitored_tickers),
            'active_catalysts': total_events,
            'tickers_with_events': len(self.active_catalysts),
            'priority_breakdown': priority_counts,
            'is_running': self.is_running,
            'check_interval_seconds': self.check_interval
        }

    def export_events(self, filepath: str) -> None:
        """Export all events to JSON file"""
        data = {
            'monitored_tickers': list(self.monitored_tickers),
            'active_catalysts': {
                ticker: [e.to_dict() for e in events]
                for ticker, events in self.active_catalysts.items()
            },
            'triggered_events': [e.to_dict() for e in self.triggered_events],
            'stats': self.get_monitoring_stats(),
            'exported_at': datetime.now().isoformat()
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported catalyst events to {filepath}")
