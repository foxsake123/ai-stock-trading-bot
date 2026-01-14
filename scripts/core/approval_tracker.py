"""
Approval Rate Tracking for AI Trading Bot
==========================================
Tracks validation approval rates over time for optimization.

Author: AI Trading Bot System
Date: January 13, 2026
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from statistics import mean, stdev

logger = logging.getLogger(__name__)


@dataclass
class ApprovalRecord:
    """Record of a validation session"""
    date: str
    bot: str
    total_recommendations: int
    approved: int
    rejected: int
    approval_rate: float
    avg_external_confidence: float
    avg_final_score: float
    threshold_used: float
    details: Optional[Dict] = None


class ApprovalTracker:
    """
    Tracks and analyzes trade approval rates over time.

    Example:
        tracker = ApprovalTracker()

        # Record validation session
        tracker.record_session(
            bot="SHORGAN-BOT",
            total=10,
            approved=6,
            avg_external=0.72,
            avg_final=0.58,
            threshold=0.55
        )

        # Analyze trends
        stats = tracker.get_statistics("SHORGAN-BOT", days=30)
        print(f"30-day approval rate: {stats['avg_approval_rate']:.1%}")
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Args:
            data_dir: Directory for approval data. Defaults to data/validation/
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "data" / "validation"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.data_file = self.data_dir / "approval_history.json"

    def _load_data(self) -> List[Dict]:
        """Load approval history from file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load approval data: {e}")
        return []

    def _save_data(self, data: List[Dict]):
        """Save approval history to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save approval data: {e}")

    def record_session(
        self,
        bot: str,
        total: int,
        approved: int,
        avg_external: float,
        avg_final: float,
        threshold: float,
        details: Optional[Dict] = None
    ) -> ApprovalRecord:
        """
        Record a validation session.

        Args:
            bot: Bot name (DEE-BOT, SHORGAN-BOT, SHORGAN-BOT-LIVE)
            total: Total recommendations from research
            approved: Number approved after validation
            avg_external: Average external confidence score
            avg_final: Average final combined score
            threshold: Approval threshold used
            details: Optional additional details

        Returns:
            ApprovalRecord of the session
        """
        rejected = total - approved
        approval_rate = approved / total if total > 0 else 0.0

        record = ApprovalRecord(
            date=datetime.now().strftime("%Y-%m-%d"),
            bot=bot,
            total_recommendations=total,
            approved=approved,
            rejected=rejected,
            approval_rate=approval_rate,
            avg_external_confidence=avg_external,
            avg_final_score=avg_final,
            threshold_used=threshold,
            details=details
        )

        # Load, append, save
        data = self._load_data()
        data.append(asdict(record))
        self._save_data(data)

        logger.info(
            f"Recorded approval session for {bot}: "
            f"{approved}/{total} approved ({approval_rate:.1%})"
        )

        return record

    def get_history(
        self,
        bot: Optional[str] = None,
        days: int = 30
    ) -> List[ApprovalRecord]:
        """
        Get approval history.

        Args:
            bot: Filter by bot name (None for all)
            days: Number of days to look back

        Returns:
            List of ApprovalRecords
        """
        data = self._load_data()
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        records = []
        for item in data:
            if item["date"] >= cutoff:
                if bot is None or item["bot"] == bot:
                    records.append(ApprovalRecord(**item))

        return sorted(records, key=lambda r: r.date)

    def get_statistics(
        self,
        bot: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """
        Get statistical summary of approval rates.

        Args:
            bot: Filter by bot name (None for all)
            days: Number of days to analyze

        Returns:
            Dict with statistics
        """
        records = self.get_history(bot, days)

        if not records:
            return {
                "bot": bot or "all",
                "period_days": days,
                "sessions": 0,
                "message": "No data available"
            }

        approval_rates = [r.approval_rate for r in records]
        external_scores = [r.avg_external_confidence for r in records]
        final_scores = [r.avg_final_score for r in records]
        total_recs = sum(r.total_recommendations for r in records)
        total_approved = sum(r.approved for r in records)

        stats = {
            "bot": bot or "all",
            "period_days": days,
            "sessions": len(records),
            "total_recommendations": total_recs,
            "total_approved": total_approved,
            "overall_approval_rate": total_approved / total_recs if total_recs > 0 else 0,
            "avg_approval_rate": mean(approval_rates),
            "min_approval_rate": min(approval_rates),
            "max_approval_rate": max(approval_rates),
            "stddev_approval_rate": stdev(approval_rates) if len(approval_rates) > 1 else 0,
            "avg_external_confidence": mean(external_scores),
            "avg_final_score": mean(final_scores),
            "threshold_range": {
                "min": min(r.threshold_used for r in records),
                "max": max(r.threshold_used for r in records)
            }
        }

        return stats

    def check_anomalies(
        self,
        bot: Optional[str] = None
    ) -> List[str]:
        """
        Check for anomalous approval patterns.

        Returns:
            List of warning messages
        """
        warnings = []
        stats = self.get_statistics(bot, days=7)

        if stats.get("sessions", 0) == 0:
            return ["No recent data to analyze"]

        rate = stats.get("overall_approval_rate", 0)

        # Check for problematic rates
        if rate == 0:
            warnings.append(
                f"CRITICAL: 0% approval rate for {stats['bot']}! "
                "All trades being rejected. Check validation threshold."
            )
        elif rate < 0.2:
            warnings.append(
                f"WARNING: Very low approval rate ({rate:.1%}) for {stats['bot']}. "
                "Consider lowering threshold."
            )
        elif rate == 1.0:
            warnings.append(
                f"WARNING: 100% approval rate for {stats['bot']}! "
                "Validation may not be filtering effectively."
            )
        elif rate > 0.8:
            warnings.append(
                f"INFO: High approval rate ({rate:.1%}) for {stats['bot']}. "
                "Validation may be too lenient."
            )

        # Check for sudden changes
        recent = self.get_history(bot, days=3)
        historical = self.get_history(bot, days=14)

        if len(recent) >= 2 and len(historical) >= 5:
            recent_avg = mean([r.approval_rate for r in recent])
            hist_avg = mean([r.approval_rate for r in historical])

            if abs(recent_avg - hist_avg) > 0.3:
                direction = "increase" if recent_avg > hist_avg else "decrease"
                warnings.append(
                    f"NOTICE: Significant {direction} in approval rate for {stats['bot']}. "
                    f"Recent: {recent_avg:.1%}, Historical: {hist_avg:.1%}"
                )

        return warnings

    def get_optimization_suggestions(
        self,
        bot: Optional[str] = None
    ) -> Dict:
        """
        Get suggestions for optimizing approval threshold.

        Returns:
            Dict with current stats and recommendations
        """
        stats = self.get_statistics(bot, days=30)

        if stats.get("sessions", 0) < 5:
            return {
                "message": "Insufficient data for optimization (need 5+ sessions)",
                "current_data": stats
            }

        rate = stats["overall_approval_rate"]
        current_threshold = stats["threshold_range"]["max"]

        suggestions = {
            "current_stats": stats,
            "target_range": "30-50% approval rate recommended",
            "recommendations": []
        }

        if rate < 0.3:
            suggestions["recommendations"].append({
                "action": "LOWER threshold",
                "reason": f"Current rate {rate:.1%} below target range",
                "suggested_threshold": max(0.45, current_threshold - 0.05)
            })
        elif rate > 0.5:
            suggestions["recommendations"].append({
                "action": "RAISE threshold",
                "reason": f"Current rate {rate:.1%} above target range",
                "suggested_threshold": min(0.70, current_threshold + 0.05)
            })
        else:
            suggestions["recommendations"].append({
                "action": "MAINTAIN threshold",
                "reason": f"Current rate {rate:.1%} within target range",
                "current_threshold": current_threshold
            })

        return suggestions


# Global tracker instance
_tracker: Optional[ApprovalTracker] = None


def get_approval_tracker() -> ApprovalTracker:
    """Get or create global approval tracker"""
    global _tracker
    if _tracker is None:
        _tracker = ApprovalTracker()
    return _tracker


if __name__ == "__main__":
    # Test approval tracker
    tracker = ApprovalTracker()

    # Simulate some sessions
    print("Testing approval tracker...")

    tracker.record_session(
        bot="DEE-BOT",
        total=8,
        approved=4,
        avg_external=0.70,
        avg_final=0.56,
        threshold=0.55
    )

    tracker.record_session(
        bot="SHORGAN-BOT",
        total=12,
        approved=6,
        avg_external=0.68,
        avg_final=0.54,
        threshold=0.55
    )

    # Get statistics
    stats = tracker.get_statistics("DEE-BOT", days=7)
    print(f"\nDEE-BOT Stats (7 days):")
    print(f"  Sessions: {stats.get('sessions', 0)}")
    print(f"  Approval Rate: {stats.get('overall_approval_rate', 0):.1%}")

    # Check anomalies
    warnings = tracker.check_anomalies()
    print(f"\nAnomalies: {warnings}")

    # Get suggestions
    suggestions = tracker.get_optimization_suggestions()
    print(f"\nOptimization Suggestions:")
    for rec in suggestions.get("recommendations", []):
        print(f"  {rec['action']}: {rec['reason']}")
