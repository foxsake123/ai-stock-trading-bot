"""
Intraday Catalyst Monitor
Tracks real-time market-moving events and catalysts
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CatalystType(Enum):
    """Types of catalysts"""
    EARNINGS = "earnings"
    FDA_APPROVAL = "fda_approval"
    MERGER_ACQUISITION = "merger_acquisition"
    ANALYST_UPGRADE = "analyst_upgrade"
    ANALYST_DOWNGRADE = "analyst_downgrade"
    GUIDANCE_RAISE = "guidance_raise"
    GUIDANCE_LOWER = "guidance_lower"
    PRODUCT_LAUNCH = "product_launch"
    PARTNERSHIP = "partnership"
    BUYBACK = "buyback"
    DIVIDEND = "dividend"
    EARNINGS_BEAT = "earnings_beat"
    EARNINGS_MISS = "earnings_miss"
    LEGAL_NEWS = "legal_news"
    REGULATORY = "regulatory"
    CONTRACT_WIN = "contract_win"
    OTHER = "other"


class CatalystImpact(Enum):
    """Expected impact of catalyst"""
    VERY_BULLISH = "very_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    VERY_BEARISH = "very_bearish"


class CatalystUrgency(Enum):
    """Urgency level for action"""
    IMMEDIATE = "immediate"  # Act now
    HIGH = "high"            # Within 15 minutes
    MODERATE = "moderate"    # Within 1 hour
    LOW = "low"              # Monitor


@dataclass
class Catalyst:
    """Individual catalyst event"""
    ticker: str
    catalyst_type: CatalystType
    impact: CatalystImpact
    urgency: CatalystUrgency
    timestamp: datetime
    description: str
    source: str

    # Additional context
    details: Dict[str, Any]
    confidence: float  # 0-1, how confident we are in the impact

    # Price impact
    expected_move: Optional[float] = None  # Expected % move
    time_window: Optional[str] = None      # How long until event

    def __post_init__(self):
        """Ensure enums are properly typed"""
        if isinstance(self.catalyst_type, str):
            self.catalyst_type = CatalystType(self.catalyst_type)
        if isinstance(self.impact, str):
            self.impact = CatalystImpact(self.impact)
        if isinstance(self.urgency, str):
            self.urgency = CatalystUrgency(self.urgency)


@dataclass
class CatalystAlert:
    """Alert generated from catalyst"""
    catalyst: Catalyst
    alert_time: datetime
    action_recommended: str  # BUY, SELL, HOLD, MONITOR
    rationale: str
    position_sizing: Optional[float] = None  # Suggested position size
    stop_loss: Optional[float] = None
    target: Optional[float] = None


class CatalystMonitor:
    """Monitors and tracks intraday catalysts"""

    def __init__(self, news_api=None, fd_client=None):
        """
        Initialize catalyst monitor

        Args:
            news_api: News API client for fetching news
            fd_client: Financial Datasets client for earnings/events
        """
        self.news_api = news_api
        self.fd_client = fd_client

        # Tracking
        self.active_catalysts: Dict[str, List[Catalyst]] = {}  # ticker -> catalysts
        self.catalyst_history: List[Catalyst] = []
        self.monitored_tickers: Set[str] = set()

        # Market hours
        self.market_open = time(9, 30)
        self.market_close = time(16, 0)

        # Impact scoring
        self.impact_scores = {
            CatalystImpact.VERY_BULLISH: 1.0,
            CatalystImpact.BULLISH: 0.5,
            CatalystImpact.NEUTRAL: 0.0,
            CatalystImpact.BEARISH: -0.5,
            CatalystImpact.VERY_BEARISH: -1.0
        }

    def add_monitored_ticker(self, ticker: str) -> None:
        """Add ticker to monitoring list"""
        self.monitored_tickers.add(ticker)
        if ticker not in self.active_catalysts:
            self.active_catalysts[ticker] = []

    def remove_monitored_ticker(self, ticker: str) -> None:
        """Remove ticker from monitoring list"""
        self.monitored_tickers.discard(ticker)

    def add_catalyst(self, catalyst: Catalyst) -> None:
        """
        Add a catalyst to tracking

        Args:
            catalyst: Catalyst event to track
        """
        ticker = catalyst.ticker

        if ticker not in self.active_catalysts:
            self.active_catalysts[ticker] = []

        self.active_catalysts[ticker].append(catalyst)
        self.catalyst_history.append(catalyst)

        logger.info(f"Added catalyst for {ticker}: {catalyst.catalyst_type.value}")

    def get_active_catalysts(
        self,
        ticker: Optional[str] = None,
        min_urgency: Optional[CatalystUrgency] = None
    ) -> List[Catalyst]:
        """
        Get active catalysts

        Args:
            ticker: Filter by ticker (None = all)
            min_urgency: Minimum urgency level

        Returns:
            List of active catalysts
        """
        if ticker:
            catalysts = self.active_catalysts.get(ticker, [])
        else:
            catalysts = []
            for ticker_catalysts in self.active_catalysts.values():
                catalysts.extend(ticker_catalysts)

        # Filter by urgency if specified
        if min_urgency:
            urgency_order = [
                CatalystUrgency.IMMEDIATE,
                CatalystUrgency.HIGH,
                CatalystUrgency.MODERATE,
                CatalystUrgency.LOW
            ]
            min_index = urgency_order.index(min_urgency)
            catalysts = [
                c for c in catalysts
                if urgency_order.index(c.urgency) <= min_index
            ]

        return catalysts

    def scan_for_catalysts(self, tickers: List[str]) -> List[Catalyst]:
        """
        Scan for new catalysts

        Args:
            tickers: List of tickers to scan

        Returns:
            List of newly discovered catalysts
        """
        new_catalysts = []

        for ticker in tickers:
            self.add_monitored_ticker(ticker)

            # Check earnings
            if self.fd_client:
                earnings_catalysts = self._check_earnings(ticker)
                new_catalysts.extend(earnings_catalysts)

            # Check news
            if self.news_api:
                news_catalysts = self._check_news(ticker)
                new_catalysts.extend(news_catalysts)

        # Add all new catalysts to tracking
        for catalyst in new_catalysts:
            self.add_catalyst(catalyst)

        return new_catalysts

    def _check_earnings(self, ticker: str) -> List[Catalyst]:
        """Check for earnings-related catalysts"""
        catalysts = []

        try:
            # Check if earnings are today or this week
            # This would use the fd_client to fetch earnings calendar
            # For now, return empty list (placeholder)
            pass
        except Exception as e:
            logger.error(f"Error checking earnings for {ticker}: {e}")

        return catalysts

    def _check_news(self, ticker: str) -> List[Catalyst]:
        """Check for news-related catalysts"""
        catalysts = []

        try:
            # Fetch recent news and parse for catalysts
            # This would use the news_api to fetch news
            # For now, return empty list (placeholder)
            pass
        except Exception as e:
            logger.error(f"Error checking news for {ticker}: {e}")

        return catalysts

    def classify_catalyst(
        self,
        description: str,
        ticker: str
    ) -> tuple[CatalystType, CatalystImpact, CatalystUrgency]:
        """
        Classify catalyst from description

        Args:
            description: Text description of event
            ticker: Stock ticker

        Returns:
            (catalyst_type, impact, urgency)
        """
        desc_lower = description.lower()

        # Determine type
        catalyst_type = CatalystType.OTHER
        if any(word in desc_lower for word in ['earnings', 'eps', 'revenue']):
            catalyst_type = CatalystType.EARNINGS
        elif any(word in desc_lower for word in ['fda', 'approval', 'drug']):
            catalyst_type = CatalystType.FDA_APPROVAL
        elif any(word in desc_lower for word in ['merger', 'acquisition', 'buyout']):
            catalyst_type = CatalystType.MERGER_ACQUISITION
        elif 'upgrade' in desc_lower:
            catalyst_type = CatalystType.ANALYST_UPGRADE
        elif 'downgrade' in desc_lower:
            catalyst_type = CatalystType.ANALYST_DOWNGRADE
        elif any(word in desc_lower for word in ['guidance', 'forecast']):
            if any(word in desc_lower for word in ['raise', 'increase', 'beat']):
                catalyst_type = CatalystType.GUIDANCE_RAISE
            elif any(word in desc_lower for word in ['lower', 'reduce', 'miss']):
                catalyst_type = CatalystType.GUIDANCE_LOWER
        elif any(word in desc_lower for word in ['partnership', 'deal', 'agreement']):
            catalyst_type = CatalystType.PARTNERSHIP

        # Determine impact
        impact = CatalystImpact.NEUTRAL
        if catalyst_type in [
            CatalystType.EARNINGS_BEAT,
            CatalystType.GUIDANCE_RAISE,
            CatalystType.FDA_APPROVAL,
            CatalystType.MERGER_ACQUISITION
        ]:
            impact = CatalystImpact.VERY_BULLISH
        elif catalyst_type in [
            CatalystType.ANALYST_UPGRADE,
            CatalystType.PARTNERSHIP,
            CatalystType.CONTRACT_WIN
        ]:
            impact = CatalystImpact.BULLISH
        elif catalyst_type in [
            CatalystType.EARNINGS_MISS,
            CatalystType.GUIDANCE_LOWER
        ]:
            impact = CatalystImpact.VERY_BEARISH
        elif catalyst_type == CatalystType.ANALYST_DOWNGRADE:
            impact = CatalystImpact.BEARISH

        # Additional keyword-based impact adjustment
        if any(word in desc_lower for word in ['beat', 'exceed', 'strong', 'positive']):
            if impact == CatalystImpact.NEUTRAL:
                impact = CatalystImpact.BULLISH
        elif any(word in desc_lower for word in ['miss', 'weak', 'negative', 'concern']):
            if impact == CatalystImpact.NEUTRAL:
                impact = CatalystImpact.BEARISH

        # Determine urgency
        urgency = CatalystUrgency.MODERATE
        if catalyst_type in [
            CatalystType.EARNINGS_BEAT,
            CatalystType.EARNINGS_MISS,
            CatalystType.FDA_APPROVAL,
            CatalystType.MERGER_ACQUISITION
        ]:
            urgency = CatalystUrgency.IMMEDIATE
        elif catalyst_type in [
            CatalystType.ANALYST_UPGRADE,
            CatalystType.ANALYST_DOWNGRADE,
            CatalystType.GUIDANCE_RAISE,
            CatalystType.GUIDANCE_LOWER
        ]:
            urgency = CatalystUrgency.HIGH

        return catalyst_type, impact, urgency

    def generate_alert(self, catalyst: Catalyst) -> CatalystAlert:
        """
        Generate trading alert from catalyst

        Args:
            catalyst: Catalyst event

        Returns:
            CatalystAlert with recommendation
        """
        # Determine action
        if catalyst.impact in [CatalystImpact.VERY_BULLISH, CatalystImpact.BULLISH]:
            action = "BUY"
        elif catalyst.impact in [CatalystImpact.VERY_BEARISH, CatalystImpact.BEARISH]:
            action = "SELL"
        else:
            action = "MONITOR"

        # Generate rationale
        rationale = f"{catalyst.catalyst_type.value.replace('_', ' ').title()} detected. "
        rationale += f"Impact: {catalyst.impact.value}. "
        rationale += f"Urgency: {catalyst.urgency.value}. "
        rationale += catalyst.description

        # Position sizing based on confidence and urgency
        position_sizing = None
        if catalyst.urgency == CatalystUrgency.IMMEDIATE:
            position_sizing = min(0.10, catalyst.confidence * 0.15)  # Max 10%
        elif catalyst.urgency == CatalystUrgency.HIGH:
            position_sizing = min(0.05, catalyst.confidence * 0.10)  # Max 5%
        else:
            position_sizing = min(0.03, catalyst.confidence * 0.05)  # Max 3%

        return CatalystAlert(
            catalyst=catalyst,
            alert_time=datetime.now(),
            action_recommended=action,
            rationale=rationale,
            position_sizing=position_sizing
        )

    def get_catalyst_score(self, ticker: str) -> float:
        """
        Calculate composite catalyst score for ticker

        Args:
            ticker: Stock ticker

        Returns:
            Score from -1 (very bearish) to 1 (very bullish)
        """
        catalysts = self.get_active_catalysts(ticker)

        if not catalysts:
            return 0.0

        # Weighted average by confidence
        total_weight = 0.0
        weighted_score = 0.0

        for catalyst in catalysts:
            impact_score = self.impact_scores[catalyst.impact]
            weight = catalyst.confidence

            weighted_score += impact_score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return weighted_score / total_weight

    def clear_old_catalysts(self, hours: int = 24) -> int:
        """
        Clear catalysts older than specified hours

        Args:
            hours: Age threshold in hours

        Returns:
            Number of catalysts cleared
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        cleared_count = 0

        for ticker in list(self.active_catalysts.keys()):
            original_count = len(self.active_catalysts[ticker])
            self.active_catalysts[ticker] = [
                c for c in self.active_catalysts[ticker]
                if c.timestamp > cutoff
            ]
            cleared_count += original_count - len(self.active_catalysts[ticker])

            # Remove ticker if no catalysts remain
            if not self.active_catalysts[ticker]:
                del self.active_catalysts[ticker]

        return cleared_count

    def generate_report(
        self,
        min_urgency: Optional[CatalystUrgency] = None
    ) -> str:
        """
        Generate markdown report of active catalysts

        Args:
            min_urgency: Minimum urgency level to include

        Returns:
            Markdown formatted report
        """
        catalysts = self.get_active_catalysts(min_urgency=min_urgency)

        if not catalysts:
            return "**No active catalysts**\n"

        report = "## Active Catalyst Monitor\n\n"

        # Sort by urgency then impact
        urgency_order = {
            CatalystUrgency.IMMEDIATE: 0,
            CatalystUrgency.HIGH: 1,
            CatalystUrgency.MODERATE: 2,
            CatalystUrgency.LOW: 3
        }

        catalysts.sort(key=lambda c: (urgency_order[c.urgency], -self.impact_scores[c.impact]))

        # Table header
        report += "| Ticker | Type | Impact | Urgency | Description |\n"
        report += "|--------|------|--------|---------|-------------|\n"

        for catalyst in catalysts:
            # Format impact
            if catalyst.impact == CatalystImpact.VERY_BULLISH:
                impact_display = "[+++] VERY BULLISH"
            elif catalyst.impact == CatalystImpact.BULLISH:
                impact_display = "[++] BULLISH"
            elif catalyst.impact == CatalystImpact.NEUTRAL:
                impact_display = "[=] NEUTRAL"
            elif catalyst.impact == CatalystImpact.BEARISH:
                impact_display = "[--] BEARISH"
            else:
                impact_display = "[---] VERY BEARISH"

            # Format urgency
            urgency_display = catalyst.urgency.value.upper()

            # Format type
            type_display = catalyst.catalyst_type.value.replace('_', ' ').title()

            # Truncate description if too long
            desc = catalyst.description
            if len(desc) > 60:
                desc = desc[:57] + "..."

            report += f"| {catalyst.ticker} | {type_display} | {impact_display} | "
            report += f"{urgency_display} | {desc} |\n"

        # Summary
        immediate = sum(1 for c in catalysts if c.urgency == CatalystUrgency.IMMEDIATE)
        high = sum(1 for c in catalysts if c.urgency == CatalystUrgency.HIGH)
        very_bullish = sum(1 for c in catalysts if c.impact == CatalystImpact.VERY_BULLISH)
        very_bearish = sum(1 for c in catalysts if c.impact == CatalystImpact.VERY_BEARISH)

        report += f"\n**Summary**: {len(catalysts)} active catalysts"
        if immediate > 0:
            report += f", {immediate} IMMEDIATE"
        if high > 0:
            report += f", {high} HIGH urgency"
        if very_bullish > 0:
            report += f", {very_bullish} very bullish"
        if very_bearish > 0:
            report += f", {very_bearish} very bearish"
        report += "\n"

        return report

    def is_market_hours(self) -> bool:
        """Check if currently in market hours"""
        now = datetime.now().time()
        return self.market_open <= now <= self.market_close


def create_catalyst_from_event(
    ticker: str,
    event_type: str,
    description: str,
    source: str = "manual",
    confidence: float = 0.8,
    **kwargs
) -> Catalyst:
    """
    Convenience function to create catalyst from event data

    Args:
        ticker: Stock ticker
        event_type: Type of event
        description: Event description
        source: Data source
        confidence: Confidence level (0-1)
        **kwargs: Additional catalyst parameters

    Returns:
        Catalyst object
    """
    monitor = CatalystMonitor()
    catalyst_type, impact, urgency = monitor.classify_catalyst(description, ticker)

    return Catalyst(
        ticker=ticker,
        catalyst_type=catalyst_type,
        impact=impact,
        urgency=urgency,
        timestamp=datetime.now(),
        description=description,
        source=source,
        details=kwargs,
        confidence=confidence
    )
