"""
Executive Summary Table Generator
Creates concise summary tables for quick decision-making
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class PerformanceMetrics:
    """Performance metrics for summary tables"""
    total_return: float
    daily_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    profit_factor: float
    current_positions: int


@dataclass
class BotComparison:
    """Comparison between trading bots"""
    bot_name: str
    value: float
    return_pct: float
    daily_pnl: float
    positions: int
    rank: int


class SummaryTableGenerator:
    """Generate executive summary tables for reports"""

    def __init__(self, performance_file: Optional[str] = None):
        """
        Initialize summary table generator

        Args:
            performance_file: Path to performance_history.json
        """
        if performance_file is None:
            performance_file = "data/daily/performance/performance_history.json"

        self.performance_file = Path(performance_file)

    def load_performance_data(self) -> Dict:
        """Load performance history from JSON file"""
        try:
            with open(self.performance_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"start_date": datetime.now().isoformat(), "daily_records": []}
        except Exception as e:
            print(f"Error loading performance data: {e}")
            return {"start_date": datetime.now().isoformat(), "daily_records": []}

    def calculate_sharpe_ratio(
        self,
        returns: List[float],
        risk_free_rate: float = 0.05
    ) -> float:
        """
        Calculate Sharpe ratio

        Args:
            returns: List of daily returns
            risk_free_rate: Annual risk-free rate (default: 5%)

        Returns:
            Sharpe ratio (annualized)
        """
        if not returns or len(returns) < 2:
            return 0.0

        # Daily risk-free rate
        daily_rf = (1 + risk_free_rate) ** (1/252) - 1

        # Excess returns
        excess_returns = [r - daily_rf for r in returns]

        # Mean and std of excess returns
        mean_excess = sum(excess_returns) / len(excess_returns)

        if len(excess_returns) == 1:
            return 0.0

        variance = sum((r - mean_excess) ** 2 for r in excess_returns) / (len(excess_returns) - 1)
        std_dev = variance ** 0.5

        if std_dev == 0:
            return 0.0

        # Annualize (252 trading days)
        sharpe = (mean_excess / std_dev) * (252 ** 0.5)
        return sharpe

    def calculate_max_drawdown(self, values: List[float]) -> float:
        """
        Calculate maximum drawdown

        Args:
            values: List of portfolio values

        Returns:
            Maximum drawdown as percentage
        """
        if not values or len(values) < 2:
            return 0.0

        peak = values[0]
        max_dd = 0.0

        for value in values:
            if value > peak:
                peak = value

            drawdown = (peak - value) / peak if peak > 0 else 0.0
            max_dd = max(max_dd, drawdown)

        return max_dd * 100  # Return as percentage

    def generate_performance_summary(
        self,
        bot_name: str = "combined",
        days: int = 30
    ) -> PerformanceMetrics:
        """
        Generate performance summary for a bot

        Args:
            bot_name: Bot to analyze ("dee_bot", "shorgan_bot", or "combined")
            days: Number of days to analyze

        Returns:
            PerformanceMetrics object
        """
        data = self.load_performance_data()
        records = data.get('daily_records', [])

        if not records:
            return self._default_metrics()

        # Get recent records
        recent_records = records[-days:] if len(records) > days else records

        # Extract values and returns
        values = []
        daily_returns = []

        for i, record in enumerate(recent_records):
            if bot_name == "combined":
                value = record.get('combined', {}).get('total_value', 0)
            else:
                value = record.get(bot_name, {}).get('value', 0)

            values.append(value)

            # Calculate daily return
            if i > 0 and values[i-1] > 0:
                daily_ret = (value - values[i-1]) / values[i-1]
                daily_returns.append(daily_ret)

        # Calculate metrics
        if not values:
            return self._default_metrics()

        start_value = values[0]
        end_value = values[-1]
        total_return = ((end_value - start_value) / start_value * 100) if start_value > 0 else 0.0

        latest_record = recent_records[-1]
        if bot_name == "combined":
            daily_pnl = latest_record.get('combined', {}).get('total_daily_pnl', 0)
            current_positions = latest_record.get('combined', {}).get('total_positions', 0)
        else:
            daily_pnl = latest_record.get(bot_name, {}).get('daily_pnl', 0)
            current_positions = 0  # Would need to extract from positions data

        daily_return = daily_returns[-1] * 100 if daily_returns else 0.0
        sharpe_ratio = self.calculate_sharpe_ratio(daily_returns)
        max_drawdown = self.calculate_max_drawdown(values)

        # Trade statistics (would need execution logs for accurate data)
        # Using placeholder values for now
        total_trades = 0
        winning_trades = 0
        losing_trades = 0
        avg_win = 0.0
        avg_loss = 0.0

        # Calculate win rate
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0

        # Calculate profit factor
        total_wins = winning_trades * avg_win if avg_win > 0 else 0
        total_losses = abs(losing_trades * avg_loss) if avg_loss < 0 else 0
        profit_factor = (total_wins / total_losses) if total_losses > 0 else 0.0

        return PerformanceMetrics(
            total_return=total_return,
            daily_return=daily_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            current_positions=current_positions
        )

    def compare_bots(self) -> List[BotComparison]:
        """
        Compare performance of all bots

        Returns:
            List of BotComparison objects sorted by return
        """
        data = self.load_performance_data()
        records = data.get('daily_records', [])

        if not records:
            return []

        latest = records[-1]

        bots = [
            ('DEE-BOT', 'dee_bot'),
            ('SHORGAN-BOT', 'shorgan_bot'),
            ('Combined', 'combined')
        ]

        comparisons = []

        for display_name, key in bots:
            if key == 'combined':
                bot_data = latest.get('combined', {})
                value = bot_data.get('total_value', 0)
                return_pct = bot_data.get('total_return', 0)
                daily_pnl = bot_data.get('total_daily_pnl', 0)
                positions = bot_data.get('total_positions', 0)
            else:
                bot_data = latest.get(key, {})
                value = bot_data.get('value', 0)
                return_pct = bot_data.get('total_return', 0)
                daily_pnl = bot_data.get('daily_pnl', 0)
                positions = 0  # Would need positions data

            comparisons.append(BotComparison(
                bot_name=display_name,
                value=value,
                return_pct=return_pct,
                daily_pnl=daily_pnl,
                positions=positions,
                rank=0  # Will be set below
            ))

        # Sort by return and assign ranks
        comparisons.sort(key=lambda x: x.return_pct, reverse=True)
        for i, comp in enumerate(comparisons):
            comp.rank = i + 1

        return comparisons

    def generate_performance_table(self, days: int = 30) -> str:
        """
        Generate markdown performance summary table

        Args:
            days: Number of days to analyze

        Returns:
            Markdown formatted table
        """
        metrics = self.generate_performance_summary("combined", days=days)

        table = "## Performance Summary\n\n"
        table += f"**Period**: Last {days} days\n\n"
        table += "| Metric | Value |\n"
        table += "|--------|-------|\n"
        table += f"| Total Return | {metrics.total_return:+.2f}% |\n"
        table += f"| Daily Return | {metrics.daily_return:+.2f}% |\n"
        table += f"| Sharpe Ratio | {metrics.sharpe_ratio:.2f} |\n"
        table += f"| Max Drawdown | {metrics.max_drawdown:.2f}% |\n"
        table += f"| Current Positions | {metrics.current_positions} |\n"

        # Add quality indicators
        table += "\n**Quality Indicators**:\n"

        if metrics.sharpe_ratio >= 2.0:
            table += "- Sharpe Ratio: EXCELLENT (>2.0)\n"
        elif metrics.sharpe_ratio >= 1.0:
            table += "- Sharpe Ratio: GOOD (>1.0)\n"
        elif metrics.sharpe_ratio >= 0.5:
            table += "- Sharpe Ratio: FAIR (>0.5)\n"
        else:
            table += "- Sharpe Ratio: NEEDS IMPROVEMENT (<0.5)\n"

        if metrics.max_drawdown < 10:
            table += "- Drawdown: EXCELLENT (<10%)\n"
        elif metrics.max_drawdown < 20:
            table += "- Drawdown: GOOD (<20%)\n"
        else:
            table += "- Drawdown: HIGH (>20%)\n"

        return table

    def generate_bot_comparison_table(self) -> str:
        """
        Generate markdown bot comparison table

        Returns:
            Markdown formatted table
        """
        comparisons = self.compare_bots()

        if not comparisons:
            return "**No performance data available**\n"

        table = "## Bot Performance Comparison\n\n"
        table += "| Rank | Bot | Value | Return | Daily P&L | Positions |\n"
        table += "|------|-----|-------|--------|-----------|----------|\n"

        for comp in comparisons:
            # Add medal emojis for ranks
            if comp.rank == 1:
                rank_display = "1st"
            elif comp.rank == 2:
                rank_display = "2nd"
            elif comp.rank == 3:
                rank_display = "3rd"
            else:
                rank_display = f"{comp.rank}th"

            table += f"| {rank_display} | {comp.bot_name} | "
            table += f"${comp.value:,.2f} | {comp.return_pct:+.2f}% | "
            table += f"${comp.daily_pnl:+,.2f} | {comp.positions} |\n"

        return table

    def generate_key_metrics_table(self) -> str:
        """
        Generate at-a-glance key metrics table

        Returns:
            Markdown formatted table
        """
        dee_metrics = self.generate_performance_summary("dee_bot", days=30)
        shorgan_metrics = self.generate_performance_summary("shorgan_bot", days=30)

        table = "## Key Metrics (30-Day)\n\n"
        table += "| Metric | DEE-BOT | SHORGAN-BOT |\n"
        table += "|--------|---------|-------------|\n"
        table += f"| Return | {dee_metrics.total_return:+.2f}% | {shorgan_metrics.total_return:+.2f}% |\n"
        table += f"| Sharpe | {dee_metrics.sharpe_ratio:.2f} | {shorgan_metrics.sharpe_ratio:.2f} |\n"
        table += f"| Max DD | {dee_metrics.max_drawdown:.2f}% | {shorgan_metrics.max_drawdown:.2f}% |\n"
        table += f"| Positions | {dee_metrics.current_positions} | {shorgan_metrics.current_positions} |\n"

        # Determine better performer
        table += "\n**Better Performer**: "
        if dee_metrics.total_return > shorgan_metrics.total_return:
            table += "DEE-BOT (defensive strategy outperforming)\n"
        elif shorgan_metrics.total_return > dee_metrics.total_return:
            table += "SHORGAN-BOT (aggressive strategy outperforming)\n"
        else:
            table += "TIE (equal performance)\n"

        return table

    def generate_full_executive_summary(self) -> str:
        """
        Generate complete executive summary with all tables

        Returns:
            Markdown formatted executive summary
        """
        summary = "# Executive Summary\n"
        summary += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}\n\n"
        summary += "---\n\n"

        # Performance summary
        summary += self.generate_performance_table(days=30)
        summary += "\n---\n\n"

        # Bot comparison
        summary += self.generate_bot_comparison_table()
        summary += "\n---\n\n"

        # Key metrics
        summary += self.generate_key_metrics_table()
        summary += "\n---\n\n"

        # Quick decision aid
        summary += self._generate_decision_aid()

        return summary

    def _generate_decision_aid(self) -> str:
        """Generate quick decision aid section"""
        comparisons = self.compare_bots()

        if not comparisons:
            return "**Insufficient data for decision aid**\n"

        combined = next((c for c in comparisons if c.bot_name == "Combined"), None)

        if not combined:
            return "**Insufficient data for decision aid**\n"

        aid = "## Quick Decision Aid\n\n"

        # Overall status
        if combined.return_pct > 5:
            aid += "[GREEN] Portfolio performing well (>5% return)\n\n"
        elif combined.return_pct > 0:
            aid += "[YELLOW] Portfolio slightly positive (0-5% return)\n\n"
        elif combined.return_pct > -5:
            aid += "[YELLOW] Minor losses (<5% drawdown)\n\n"
        else:
            aid += "[RED] Significant losses (>5% drawdown) - review strategy\n\n"

        # Recommendations
        aid += "**Recommendations**:\n"

        if combined.return_pct < -10:
            aid += "- CRITICAL: Review risk management parameters\n"
            aid += "- Consider reducing position sizes\n"
            aid += "- Evaluate recent trades for pattern analysis\n"
        elif combined.return_pct < 0:
            aid += "- Monitor closely for reversal signals\n"
            aid += "- Review open positions for stop-loss triggers\n"
        elif combined.return_pct < 5:
            aid += "- Continue current strategy\n"
            aid += "- Look for optimization opportunities\n"
        else:
            aid += "- Strategy performing well\n"
            aid += "- Consider scaling position sizes gradually\n"
            aid += "- Monitor for overconfidence risks\n"

        return aid

    def _default_metrics(self) -> PerformanceMetrics:
        """Return default metrics when no data available"""
        return PerformanceMetrics(
            total_return=0.0,
            daily_return=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            avg_win=0.0,
            avg_loss=0.0,
            profit_factor=0.0,
            current_positions=0
        )


def generate_executive_summary(performance_file: Optional[str] = None) -> str:
    """
    Convenience function to generate executive summary

    Args:
        performance_file: Optional path to performance_history.json

    Returns:
        Markdown formatted executive summary
    """
    generator = SummaryTableGenerator(performance_file)
    return generator.generate_full_executive_summary()
