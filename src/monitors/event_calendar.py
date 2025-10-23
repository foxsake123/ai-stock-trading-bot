"""
Event Calendar - Tracks Scheduled Catalysts
Maintains calendar of upcoming FDA decisions, earnings, launches, conferences
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


@dataclass
class ScheduledEvent:
    """Represents a scheduled catalyst event"""
    ticker: str
    event_type: str  # FDA_DECISION, EARNINGS_RELEASE, etc.
    title: str
    description: str
    scheduled_time: datetime
    location: Optional[str] = None
    source: str = "manual"
    metadata: Dict = field(default_factory=dict)
    reminder_sent: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'ticker': self.ticker,
            'event_type': self.event_type,
            'title': self.title,
            'description': self.description,
            'scheduled_time': self.scheduled_time.isoformat(),
            'location': self.location,
            'source': self.source,
            'metadata': self.metadata,
            'reminder_sent': self.reminder_sent,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ScheduledEvent':
        """Create from dictionary"""
        return cls(
            ticker=data['ticker'],
            event_type=data['event_type'],
            title=data['title'],
            description=data['description'],
            scheduled_time=datetime.fromisoformat(data['scheduled_time']),
            location=data.get('location'),
            source=data.get('source', 'manual'),
            metadata=data.get('metadata', {}),
            reminder_sent=data.get('reminder_sent', False),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
        )


class EventCalendar:
    """
    Maintains calendar of scheduled catalyst events

    Features:
    - Track FDA PDUFA dates
    - Track earnings release dates
    - Track product launch dates
    - Track conference presentations
    - Send reminders at configurable intervals
    - Persistent storage
    """

    def __init__(
        self,
        storage_file: Optional[str] = None,
        reminder_hours: List[int] = None
    ):
        """
        Initialize Event Calendar

        Args:
            storage_file: Path to JSON file for persistent storage
            reminder_hours: Hours before event to send reminders (e.g., [24, 4, 1])
        """
        self.storage_file = storage_file or "data/event_calendar.json"
        self.reminder_hours = reminder_hours or [24, 4, 1]  # 24h, 4h, 1h before

        self.events: Dict[str, List[ScheduledEvent]] = {}  # ticker -> events
        self.load_from_storage()

        logger.info(f"EventCalendar initialized (reminders at {self.reminder_hours}h)")

    def add_event(self, event: ScheduledEvent) -> None:
        """Add event to calendar"""
        ticker = event.ticker.upper()

        if ticker not in self.events:
            self.events[ticker] = []

        # Check for duplicate
        for existing in self.events[ticker]:
            if (existing.event_type == event.event_type and
                existing.scheduled_time == event.scheduled_time and
                existing.title == event.title):
                logger.debug(f"Duplicate event for {ticker}, skipping")
                return

        self.events[ticker].append(event)
        self.save_to_storage()

        logger.info(f"Added event for {ticker}: {event.title} at {event.scheduled_time}")

    def add_fda_event(
        self,
        ticker: str,
        pdufa_date: datetime,
        drug_name: str,
        indication: str
    ) -> ScheduledEvent:
        """Add FDA PDUFA date"""
        event = ScheduledEvent(
            ticker=ticker.upper(),
            event_type='FDA_DECISION',
            title=f"FDA PDUFA Date - {drug_name}",
            description=f"FDA decision expected for {drug_name} ({indication})",
            scheduled_time=pdufa_date,
            source='manual',
            metadata={
                'drug_name': drug_name,
                'indication': indication,
                'event_subtype': 'PDUFA'
            }
        )

        self.add_event(event)
        return event

    def add_earnings_event(
        self,
        ticker: str,
        earnings_date: datetime,
        quarter: str,
        fiscal_year: int
    ) -> ScheduledEvent:
        """Add earnings release date"""
        event = ScheduledEvent(
            ticker=ticker.upper(),
            event_type='EARNINGS_RELEASE',
            title=f"{quarter} {fiscal_year} Earnings",
            description=f"Earnings release for {quarter} {fiscal_year}",
            scheduled_time=earnings_date,
            source='manual',
            metadata={
                'quarter': quarter,
                'fiscal_year': fiscal_year
            }
        )

        self.add_event(event)
        return event

    def add_product_launch(
        self,
        ticker: str,
        launch_date: datetime,
        product_name: str,
        description: str
    ) -> ScheduledEvent:
        """Add product launch event"""
        event = ScheduledEvent(
            ticker=ticker.upper(),
            event_type='PRODUCT_LAUNCH',
            title=f"Product Launch - {product_name}",
            description=description,
            scheduled_time=launch_date,
            source='manual',
            metadata={
                'product_name': product_name
            }
        )

        self.add_event(event)
        return event

    def add_conference_presentation(
        self,
        ticker: str,
        presentation_date: datetime,
        conference_name: str,
        location: str,
        presenters: List[str] = None
    ) -> ScheduledEvent:
        """Add conference presentation"""
        event = ScheduledEvent(
            ticker=ticker.upper(),
            event_type='CONFERENCE_PRESENTATION',
            title=f"Presenting at {conference_name}",
            description=f"Company presentation at {conference_name}",
            scheduled_time=presentation_date,
            location=location,
            source='manual',
            metadata={
                'conference_name': conference_name,
                'presenters': presenters or []
            }
        )

        self.add_event(event)
        return event

    async def get_upcoming_events(
        self,
        tickers: Optional[List[str]] = None,
        hours_ahead: int = 24,
        event_types: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get upcoming events within time window

        Args:
            tickers: Filter by tickers (None = all)
            hours_ahead: How far ahead to look
            event_types: Filter by event types (None = all)

        Returns:
            List of events as dictionaries
        """
        now = datetime.now()
        cutoff = now + timedelta(hours=hours_ahead)

        upcoming = []

        # Filter by tickers
        if tickers:
            tickers = [t.upper() for t in tickers]
            events_to_check = {t: self.events.get(t, []) for t in tickers}
        else:
            events_to_check = self.events

        # Find upcoming events
        for ticker, ticker_events in events_to_check.items():
            for event in ticker_events:
                # Check time window
                if now <= event.scheduled_time <= cutoff:
                    # Check event type filter
                    if event_types is None or event.event_type in event_types:
                        upcoming.append({
                            'ticker': event.ticker,
                            'type': event.event_type,
                            'title': event.title,
                            'description': event.description,
                            'scheduled_time': event.scheduled_time,
                            'location': event.location,
                            'source': event.source,
                            'metadata': event.metadata,
                            'hours_until': (event.scheduled_time - now).total_seconds() / 3600
                        })

        # Sort by scheduled time
        upcoming.sort(key=lambda x: x['scheduled_time'])

        return upcoming

    def get_events_needing_reminder(self) -> List[ScheduledEvent]:
        """Get events that need reminder sent"""
        now = datetime.now()
        needs_reminder = []

        for ticker_events in self.events.values():
            for event in ticker_events:
                # Skip if reminder already sent
                if event.reminder_sent:
                    continue

                # Skip if event is in the past
                if event.scheduled_time < now:
                    continue

                # Check if within any reminder window
                hours_until = (event.scheduled_time - now).total_seconds() / 3600

                for reminder_hour in self.reminder_hours:
                    # Send reminder if within 30 minutes of reminder time
                    if abs(hours_until - reminder_hour) <= 0.5:
                        needs_reminder.append(event)
                        break

        return needs_reminder

    def mark_reminder_sent(self, event: ScheduledEvent) -> None:
        """Mark reminder as sent for an event"""
        event.reminder_sent = True
        self.save_to_storage()

    def remove_event(self, ticker: str, event_title: str) -> bool:
        """Remove event from calendar"""
        ticker = ticker.upper()

        if ticker not in self.events:
            return False

        original_count = len(self.events[ticker])
        self.events[ticker] = [e for e in self.events[ticker] if e.title != event_title]

        if len(self.events[ticker]) < original_count:
            self.save_to_storage()
            logger.info(f"Removed event '{event_title}' for {ticker}")
            return True

        return False

    def get_all_events(self, ticker: Optional[str] = None) -> Dict[str, List[ScheduledEvent]]:
        """Get all events (optionally filtered by ticker)"""
        if ticker:
            ticker = ticker.upper()
            return {ticker: self.events.get(ticker, [])}
        return self.events

    def get_events_by_type(self, event_type: str) -> List[ScheduledEvent]:
        """Get all events of a specific type"""
        events = []
        for ticker_events in self.events.values():
            events.extend([e for e in ticker_events if e.event_type == event_type])

        # Sort by scheduled time
        events.sort(key=lambda x: x.scheduled_time)
        return events

    def clear_past_events(self, days_ago: int = 7) -> int:
        """Remove events older than N days"""
        cutoff = datetime.now() - timedelta(days=days_ago)
        removed_count = 0

        for ticker in list(self.events.keys()):
            original_count = len(self.events[ticker])
            self.events[ticker] = [e for e in self.events[ticker] if e.scheduled_time >= cutoff]
            removed_count += original_count - len(self.events[ticker])

            # Remove ticker if no events left
            if not self.events[ticker]:
                del self.events[ticker]

        if removed_count > 0:
            self.save_to_storage()
            logger.info(f"Removed {removed_count} past events")

        return removed_count

    def save_to_storage(self) -> None:
        """Save calendar to persistent storage"""
        try:
            data = {
                'events': {
                    ticker: [event.to_dict() for event in events]
                    for ticker, events in self.events.items()
                },
                'saved_at': datetime.now().isoformat()
            }

            # Ensure directory exists
            import os
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)

            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Saved calendar to {self.storage_file}")

        except Exception as e:
            logger.error(f"Error saving calendar: {e}")

    def load_from_storage(self) -> None:
        """Load calendar from persistent storage"""
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)

            self.events = {}
            for ticker, events_data in data.get('events', {}).items():
                self.events[ticker] = [
                    ScheduledEvent.from_dict(event_dict)
                    for event_dict in events_data
                ]

            total_events = sum(len(events) for events in self.events.values())
            logger.info(f"Loaded {total_events} events from storage")

        except FileNotFoundError:
            logger.info("No existing calendar file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading calendar: {e}")

    def get_calendar_summary(self) -> Dict:
        """Get summary statistics of calendar"""
        now = datetime.now()

        total_events = sum(len(events) for events in self.events.values())
        upcoming_count = 0
        past_count = 0

        event_type_counts = {}

        for ticker_events in self.events.values():
            for event in ticker_events:
                # Count by status
                if event.scheduled_time > now:
                    upcoming_count += 1
                else:
                    past_count += 1

                # Count by type
                event_type = event.event_type
                event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

        return {
            'total_events': total_events,
            'upcoming_events': upcoming_count,
            'past_events': past_count,
            'tracked_tickers': len(self.events),
            'event_type_breakdown': event_type_counts
        }

    def export_calendar(self, filepath: str, format: str = 'json') -> None:
        """Export calendar to file"""
        if format == 'json':
            self.save_to_storage()  # Already handles JSON export
            import shutil
            shutil.copy(self.storage_file, filepath)
            logger.info(f"Exported calendar to {filepath}")

        elif format == 'csv':
            import csv

            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Ticker', 'Type', 'Title', 'Scheduled Time', 'Description', 'Location'])

                for ticker_events in self.events.values():
                    for event in ticker_events:
                        writer.writerow([
                            event.ticker,
                            event.event_type,
                            event.title,
                            event.scheduled_time.isoformat(),
                            event.description,
                            event.location or ''
                        ])

            logger.info(f"Exported calendar to {filepath} (CSV)")

        else:
            raise ValueError(f"Unsupported format: {format}")
