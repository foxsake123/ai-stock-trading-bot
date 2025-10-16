"""
Portfolio Attribution Analysis
Analyzes which factors contributed to portfolio performance
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class TradeAttribution:
    """Attribution for a single trade"""
    ticker: str
    entry_date: datetime
    exit_date: datetime
    return_pct: float
    pnl: float
    position_size: float

    # Attribution factors
    sector: Optional[str] = None
    strategy: Optional[str] = None  # e.g., "catalyst", "momentum", "value"
    agent_recommendation: Optional[str] = None  # Which agent recommended
    market_condition: Optional[str] = None  # "bull", "bear", "sideways"
    catalyst_type: Optional[str] = None  # "earnings", "FDA", etc.

    # Performance vs benchmarks
    vs_spy: Optional[float] = None  # Alpha vs S&P 500
    vs_sector: Optional[float] = None  # Alpha vs sector

    holding_days: int = 0
    win: bool = False


@dataclass
class AttributionBreakdown:
    """Attribution breakdown by factor"""
    factor_name: str  # "sector", "strategy", "agent", etc.
    factor_values: Dict[str, float]  # e.g., {"Technology": 0.05, "Healthcare": 0.03}
    total_contribution: float
    best_performer: str
    worst_performer: str
    count_by_value: Dict[str, int]  # Number of trades per value


@dataclass
class PortfolioAttribution:
    """Complete portfolio attribution analysis"""
    start_date: datetime
    end_date: datetime
    total_return: float
    total_pnl: float
    num_trades: int

    # Attribution by factor
    by_sector: AttributionBreakdown
    by_strategy: AttributionBreakdown
    by_agent: AttributionBreakdown
    by_market_condition: AttributionBreakdown
    by_catalyst_type: AttributionBreakdown

    # Time-based attribution
    monthly_attribution: Dict[str, float]  # "2025-01": 0.03
    weekly_attribution: Dict[str, float]   # "2025-W01": 0.01

    # Alpha generation
    total_alpha_vs_spy: float
    total_alpha_vs_sectors: float

    # Trade details
    trades: List[TradeAttribution] = field(default_factory=list)


class PortfolioAttributionAnalyzer:
    """Analyzes portfolio performance attribution"""

    def __init__(self):
        """Initialize attribution analyzer"""
        self.trades: List[TradeAttribution] = []

    def add_trade(
        self,
        ticker: str,
        entry_date: datetime,
        exit_date: datetime,
        return_pct: float,
        pnl: float,
        position_size: float,
        sector: Optional[str] = None,
        strategy: Optional[str] = None,
        agent_recommendation: Optional[str] = None,
        market_condition: Optional[str] = None,
        catalyst_type: Optional[str] = None,
        vs_spy: Optional[float] = None,
        vs_sector: Optional[float] = None
    ) -> None:
        """
        Add trade to attribution analysis

        Args:
            ticker: Stock ticker
            entry_date: Entry date
            exit_date: Exit date
            return_pct: Return percentage
            pnl: Profit/loss in dollars
            position_size: Position size as % of portfolio
            sector: Stock sector
            strategy: Trading strategy used
            agent_recommendation: Which agent recommended
            market_condition: Market condition during trade
            catalyst_type: Type of catalyst if applicable
            vs_spy: Alpha vs SPY
            vs_sector: Alpha vs sector
        """
        holding_days = (exit_date - entry_date).days

        trade = TradeAttribution(
            ticker=ticker,
            entry_date=entry_date,
            exit_date=exit_date,
            return_pct=return_pct,
            pnl=pnl,
            position_size=position_size,
            sector=sector,
            strategy=strategy,
            agent_recommendation=agent_recommendation,
            market_condition=market_condition,
            catalyst_type=catalyst_type,
            vs_spy=vs_spy,
            vs_sector=vs_sector,
            holding_days=holding_days,
            win=return_pct > 0
        )

        self.trades.append(trade)

    def calculate_attribution_by_factor(
        self,
        factor_name: str,
        get_factor_value: callable
    ) -> AttributionBreakdown:
        """
        Calculate attribution breakdown by a specific factor

        Args:
            factor_name: Name of the factor (e.g., "sector")
            get_factor_value: Function to extract factor value from trade

        Returns:
            AttributionBreakdown
        """
        # Group trades by factor value
        grouped = defaultdict(list)

        for trade in self.trades:
            factor_value = get_factor_value(trade)
            if factor_value:
                grouped[factor_value].append(trade)

        # Calculate contribution for each value
        factor_values = {}
        count_by_value = {}

        for value, value_trades in grouped.items():
            # Total PnL contribution
            contribution = sum(t.pnl for t in value_trades)
            factor_values[value] = contribution
            count_by_value[value] = len(value_trades)

        # Find best and worst
        if factor_values:
            best_performer = max(factor_values.items(), key=lambda x: x[1])[0]
            worst_performer = min(factor_values.items(), key=lambda x: x[1])[0]
            total_contribution = sum(factor_values.values())
        else:
            best_performer = "N/A"
            worst_performer = "N/A"
            total_contribution = 0.0

        return AttributionBreakdown(
            factor_name=factor_name,
            factor_values=factor_values,
            total_contribution=total_contribution,
            best_performer=best_performer,
            worst_performer=worst_performer,
            count_by_value=count_by_value
        )

    def calculate_time_attribution(
        self,
        period: str = "monthly"
    ) -> Dict[str, float]:
        """
        Calculate attribution by time period

        Args:
            period: "monthly" or "weekly"

        Returns:
            Dictionary of period -> PnL
        """
        time_attribution = defaultdict(float)

        for trade in self.trades:
            if period == "monthly":
                key = trade.exit_date.strftime("%Y-%m")
            elif period == "weekly":
                key = trade.exit_date.strftime("%Y-W%U")
            else:
                raise ValueError(f"Unknown period: {period}")

            time_attribution[key] += trade.pnl

        return dict(time_attribution)

    def analyze(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> PortfolioAttribution:
        """
        Perform complete attribution analysis

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            PortfolioAttribution results
        """
        if not self.trades:
            raise ValueError("No trades to analyze")

        # Filter by date if specified
        trades_to_analyze = self.trades
        if start_date:
            trades_to_analyze = [t for t in trades_to_analyze if t.exit_date >= start_date]
        if end_date:
            trades_to_analyze = [t for t in trades_to_analyze if t.exit_date <= end_date]

        if not trades_to_analyze:
            raise ValueError("No trades in specified date range")

        # Use filtered trades for analysis
        original_trades = self.trades
        self.trades = trades_to_analyze

        # Calculate overall metrics
        total_pnl = sum(t.pnl for t in self.trades)

        # Calculate total return (weighted by position size)
        weighted_returns = sum(t.return_pct * t.position_size for t in self.trades)
        total_positions = sum(t.position_size for t in self.trades)
        total_return = weighted_returns / total_positions if total_positions > 0 else 0.0

        # Attribution by factors
        by_sector = self.calculate_attribution_by_factor(
            "sector",
            lambda t: t.sector
        )

        by_strategy = self.calculate_attribution_by_factor(
            "strategy",
            lambda t: t.strategy
        )

        by_agent = self.calculate_attribution_by_factor(
            "agent",
            lambda t: t.agent_recommendation
        )

        by_market_condition = self.calculate_attribution_by_factor(
            "market_condition",
            lambda t: t.market_condition
        )

        by_catalyst_type = self.calculate_attribution_by_factor(
            "catalyst_type",
            lambda t: t.catalyst_type
        )

        # Time-based attribution
        monthly_attribution = self.calculate_time_attribution("monthly")
        weekly_attribution = self.calculate_time_attribution("weekly")

        # Alpha calculation
        trades_with_spy_alpha = [t for t in self.trades if t.vs_spy is not None]
        if trades_with_spy_alpha:
            total_alpha_vs_spy = sum(t.vs_spy * t.position_size for t in trades_with_spy_alpha)
        else:
            total_alpha_vs_spy = 0.0

        trades_with_sector_alpha = [t for t in self.trades if t.vs_sector is not None]
        if trades_with_sector_alpha:
            total_alpha_vs_sectors = sum(t.vs_sector * t.position_size for t in trades_with_sector_alpha)
        else:
            total_alpha_vs_sectors = 0.0

        # Determine date range
        actual_start = min(t.entry_date for t in self.trades)
        actual_end = max(t.exit_date for t in self.trades)

        result = PortfolioAttribution(
            start_date=start_date or actual_start,
            end_date=end_date or actual_end,
            total_return=total_return,
            total_pnl=total_pnl,
            num_trades=len(self.trades),
            by_sector=by_sector,
            by_strategy=by_strategy,
            by_agent=by_agent,
            by_market_condition=by_market_condition,
            by_catalyst_type=by_catalyst_type,
            monthly_attribution=monthly_attribution,
            weekly_attribution=weekly_attribution,
            total_alpha_vs_spy=total_alpha_vs_spy,
            total_alpha_vs_sectors=total_alpha_vs_sectors,
            trades=self.trades.copy()
        )

        # Restore original trades
        self.trades = original_trades

        return result

    def generate_report(self, attribution: PortfolioAttribution) -> str:
        """
        Generate markdown report of attribution analysis

        Args:
            attribution: PortfolioAttribution results

        Returns:
            Markdown formatted report
        """
        report = "# Portfolio Attribution Analysis\n\n"

        report += f"**Period**: {attribution.start_date.strftime('%Y-%m-%d')} to "
        report += f"{attribution.end_date.strftime('%Y-%m-%d')}\n"
        report += f"**Total Trades**: {attribution.num_trades}\n"
        report += f"**Total Return**: {attribution.total_return:.2%}\n"
        report += f"**Total P&L**: ${attribution.total_pnl:,.2f}\n\n"

        # Alpha
        if attribution.total_alpha_vs_spy != 0:
            report += f"**Alpha vs SPY**: {attribution.total_alpha_vs_spy:.2%}\n"
        if attribution.total_alpha_vs_sectors != 0:
            report += f"**Alpha vs Sectors**: {attribution.total_alpha_vs_sectors:.2%}\n"
        report += "\n"

        # Attribution by factors
        report += self._format_breakdown(attribution.by_sector)
        report += self._format_breakdown(attribution.by_strategy)
        report += self._format_breakdown(attribution.by_agent)
        report += self._format_breakdown(attribution.by_market_condition)
        report += self._format_breakdown(attribution.by_catalyst_type)

        # Time-based attribution
        report += "## Monthly Attribution\n\n"
        if attribution.monthly_attribution:
            sorted_months = sorted(attribution.monthly_attribution.items())
            for month, pnl in sorted_months:
                report += f"- **{month}**: ${pnl:,.2f}\n"
        else:
            report += "No monthly data\n"
        report += "\n"

        # Key insights
        report += "## Key Insights\n\n"

        # Best sector
        if attribution.by_sector.factor_values:
            best_sector = attribution.by_sector.best_performer
            best_sector_pnl = attribution.by_sector.factor_values[best_sector]
            report += f"- **Top Sector**: {best_sector} (${best_sector_pnl:,.2f})\n"

        # Best strategy
        if attribution.by_strategy.factor_values:
            best_strategy = attribution.by_strategy.best_performer
            best_strategy_pnl = attribution.by_strategy.factor_values[best_strategy]
            report += f"- **Top Strategy**: {best_strategy} (${best_strategy_pnl:,.2f})\n"

        # Best agent
        if attribution.by_agent.factor_values:
            best_agent = attribution.by_agent.best_performer
            best_agent_pnl = attribution.by_agent.factor_values[best_agent]
            report += f"- **Top Agent**: {best_agent} (${best_agent_pnl:,.2f})\n"

        # Best market condition
        if attribution.by_market_condition.factor_values:
            best_condition = attribution.by_market_condition.best_performer
            best_condition_pnl = attribution.by_market_condition.factor_values[best_condition]
            report += f"- **Best Market Condition**: {best_condition} (${best_condition_pnl:,.2f})\n"

        report += "\n"

        return report

    def _format_breakdown(self, breakdown: AttributionBreakdown) -> str:
        """Format attribution breakdown as markdown"""
        if not breakdown.factor_values:
            return f"## Attribution by {breakdown.factor_name.title()}\n\nNo data\n\n"

        report = f"## Attribution by {breakdown.factor_name.title()}\n\n"

        # Sort by contribution
        sorted_values = sorted(
            breakdown.factor_values.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for value, contribution in sorted_values:
            count = breakdown.count_by_value.get(value, 0)
            pct_of_total = (contribution / breakdown.total_contribution * 100) if breakdown.total_contribution != 0 else 0
            report += f"- **{value}**: ${contribution:,.2f} ({pct_of_total:.1f}%, {count} trades)\n"

        report += f"\n**Best**: {breakdown.best_performer}\n"
        report += f"**Worst**: {breakdown.worst_performer}\n\n"

        return report

    def get_top_contributors(
        self,
        factor: str,
        top_n: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Get top N contributors for a specific factor

        Args:
            factor: "sector", "strategy", "agent", etc.
            top_n: Number of top contributors to return

        Returns:
            List of (factor_value, contribution) tuples
        """
        attribution = self.analyze()

        if factor == "sector":
            breakdown = attribution.by_sector
        elif factor == "strategy":
            breakdown = attribution.by_strategy
        elif factor == "agent":
            breakdown = attribution.by_agent
        elif factor == "market_condition":
            breakdown = attribution.by_market_condition
        elif factor == "catalyst_type":
            breakdown = attribution.by_catalyst_type
        else:
            raise ValueError(f"Unknown factor: {factor}")

        sorted_contributors = sorted(
            breakdown.factor_values.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_contributors[:top_n]

    def compare_factors(
        self,
        factor1: str,
        factor2: str
    ) -> Dict[str, Any]:
        """
        Compare contribution of two factors

        Args:
            factor1: First factor
            factor2: Second factor

        Returns:
            Comparison dictionary
        """
        top1 = self.get_top_contributors(factor1, top_n=1)
        top2 = self.get_top_contributors(factor2, top_n=1)

        if not top1 or not top2:
            return {
                "factor1": factor1,
                "factor2": factor2,
                "winner": None,
                "difference": 0.0
            }

        value1, contrib1 = top1[0]
        value2, contrib2 = top2[0]

        return {
            "factor1": factor1,
            "factor1_value": value1,
            "factor1_contribution": contrib1,
            "factor2": factor2,
            "factor2_value": value2,
            "factor2_contribution": contrib2,
            "winner": factor1 if contrib1 > contrib2 else factor2,
            "difference": abs(contrib1 - contrib2)
        }


def analyze_portfolio_attribution(
    trades: List[Dict[str, Any]],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> PortfolioAttribution:
    """
    Convenience function to analyze portfolio attribution

    Args:
        trades: List of trade dictionaries with attribution data
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        PortfolioAttribution results
    """
    analyzer = PortfolioAttributionAnalyzer()

    for trade in trades:
        analyzer.add_trade(
            ticker=trade['ticker'],
            entry_date=trade['entry_date'],
            exit_date=trade['exit_date'],
            return_pct=trade['return_pct'],
            pnl=trade['pnl'],
            position_size=trade['position_size'],
            sector=trade.get('sector'),
            strategy=trade.get('strategy'),
            agent_recommendation=trade.get('agent_recommendation'),
            market_condition=trade.get('market_condition'),
            catalyst_type=trade.get('catalyst_type'),
            vs_spy=trade.get('vs_spy'),
            vs_sector=trade.get('vs_sector')
        )

    return analyzer.analyze(start_date, end_date)
