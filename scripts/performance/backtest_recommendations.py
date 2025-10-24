"""
Backtest Recommendations Performance Tracker

Analyzes historical pre-market report recommendations and tracks their actual performance.

Features:
- Load historical recommendations from markdown reports
- Fetch actual prices using yfinance
- Calculate win rates, returns, and performance metrics
- Generate comprehensive performance reports
- Compare SHORGAN-BOT vs DEE-BOT strategies

Usage:
    python backtest_recommendations.py                           # All historical data
    python backtest_recommendations.py --start 2025-01-01        # Since date
    python backtest_recommendations.py --ticker SNDX             # Specific stock
    python backtest_recommendations.py --strategy SHORGAN        # Strategy filter
"""

import os
import re
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import yfinance as yf
import pandas as pd


@dataclass
class Recommendation:
    """Data class for a stock recommendation"""
    ticker: str
    strategy: str  # SHORGAN or DEE
    action: str  # BUY, SELL, SHORT
    entry_price: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    position_size: Optional[int]
    catalyst: str
    catalyst_date: Optional[str]
    recommendation_date: str
    time_horizon: Optional[str]
    risk_reward_ratio: Optional[float]

    # Actual performance (filled by backtest)
    actual_entry_price: Optional[float] = None
    actual_catalyst_price: Optional[float] = None
    actual_return: Optional[float] = None
    hit_target: Optional[bool] = None
    hit_stop: Optional[bool] = None
    outcome: Optional[str] = None  # WIN, LOSS, PENDING


class RecommendationBacktester:
    """Backtest historical trading recommendations"""

    def __init__(self, reports_dir: str = "reports/premarket"):
        self.reports_dir = Path(reports_dir)
        self.recommendations: List[Recommendation] = []
        self.performance_dir = Path("reports/performance")
        self.performance_dir.mkdir(parents=True, exist_ok=True)

    def load_historical_reports(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> int:
        """
        Load all recommendations from historical reports.

        Args:
            start_date: Filter reports from this date (YYYY-MM-DD)
            end_date: Filter reports until this date (YYYY-MM-DD)

        Returns:
            Number of recommendations loaded
        """
        if not self.reports_dir.exists():
            print(f"Reports directory not found: {self.reports_dir}")
            return 0

        # Convert dates to datetime for filtering
        start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

        report_files = sorted(self.reports_dir.glob("premarket_report_*.md"))
        loaded_count = 0

        for report_file in report_files:
            # Extract date from filename: premarket_report_2025-10-14.md
            match = re.search(r'premarket_report_(\d{4}-\d{2}-\d{2})\.md', report_file.name)
            if not match:
                continue

            report_date = match.group(1)
            report_dt = datetime.strptime(report_date, "%Y-%m-%d")

            # Filter by date range
            if start_dt and report_dt < start_dt:
                continue
            if end_dt and report_dt > end_dt:
                continue

            # Parse recommendations from report
            recs = self._parse_report(report_file, report_date)
            self.recommendations.extend(recs)
            loaded_count += len(recs)

        print(f"Loaded {loaded_count} recommendations from {len(report_files)} reports")
        return loaded_count

    def _parse_report(self, report_path: Path, report_date: str) -> List[Recommendation]:
        """
        Parse recommendations from a single report file.

        Args:
            report_path: Path to markdown report
            report_date: Date of the report (YYYY-MM-DD)

        Returns:
            List of Recommendation objects
        """
        recommendations = []

        try:
            content = report_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading {report_path}: {e}")
            return recommendations

        # Parse SHORGAN-BOT recommendations
        shorgan_recs = self._parse_strategy_section(
            content,
            "SHORGAN-BOT",
            report_date
        )
        recommendations.extend(shorgan_recs)

        # Parse DEE-BOT recommendations
        dee_recs = self._parse_strategy_section(
            content,
            "DEE-BOT",
            report_date
        )
        recommendations.extend(dee_recs)

        return recommendations

    def _parse_strategy_section(
        self,
        content: str,
        strategy: str,
        report_date: str
    ) -> List[Recommendation]:
        """
        Parse recommendations from a strategy section (SHORGAN or DEE).

        Args:
            content: Full report content
            strategy: "SHORGAN-BOT" or "DEE-BOT"
            report_date: Date of the report

        Returns:
            List of recommendations for this strategy
        """
        recommendations = []

        # Find strategy section
        section_pattern = f"## {strategy} Recommendations"
        if section_pattern not in content:
            return recommendations

        # Extract section content
        section_start = content.find(section_pattern)
        next_section = content.find("##", section_start + len(section_pattern))
        section_content = content[section_start:next_section] if next_section != -1 else content[section_start:]

        # Parse individual stock recommendations
        # Pattern: ### 1. TICKER - Company Name (ACTION)
        stock_pattern = r'###\s+\d+\.\s+([A-Z]+)\s+-\s+([^(]+)\(([^)]+)\)'

        for match in re.finditer(stock_pattern, section_content):
            ticker = match.group(1)
            action = match.group(3).strip().upper()

            # Extract recommendation details
            rec_start = match.start()
            next_rec = section_content.find("###", rec_start + 1)
            rec_content = section_content[rec_start:next_rec] if next_rec != -1 else section_content[rec_start:]

            # Parse fields
            entry_price = self._extract_float(rec_content, r'Entry Price[:\s]+\$?([\d.]+)')
            target_price = self._extract_float(rec_content, r'(?:Price )?Target[:\s]+\$?([\d.]+)')
            stop_loss = self._extract_float(rec_content, r'Stop[- ]Loss[:\s]+\$?([\d.]+)')
            position_size = self._extract_int(rec_content, r'Position Size[:\s]+([\d,]+)\s+shares')

            # Extract catalyst and date
            catalyst = self._extract_text(rec_content, r'Catalyst[:\s]*\n[*-]\s*\*\*Event\*\*[:\s]+([^\n]+)')
            if not catalyst:
                catalyst = self._extract_text(rec_content, r'\*\*Catalyst\*\*[:\s]+([^\n]+)')

            catalyst_date = self._extract_date(rec_content)
            time_horizon = self._extract_text(rec_content, r'Time Horizon[:\s]+([^\n]+)')
            risk_reward = self._extract_float(rec_content, r'Risk/Reward[:\s]+([\d.]+):1')

            # Create recommendation object
            rec = Recommendation(
                ticker=ticker,
                strategy=strategy.replace("-BOT", ""),
                action=action,
                entry_price=entry_price or 0.0,
                target_price=target_price,
                stop_loss=stop_loss,
                position_size=position_size,
                catalyst=catalyst or "Unknown catalyst",
                catalyst_date=catalyst_date,
                recommendation_date=report_date,
                time_horizon=time_horizon,
                risk_reward_ratio=risk_reward
            )

            recommendations.append(rec)

        return recommendations

    def _extract_float(self, text: str, pattern: str) -> Optional[float]:
        """Extract float value from text using regex pattern"""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                value_str = match.group(1).replace(',', '')
                return float(value_str)
            except (ValueError, IndexError):
                pass
        return None

    def _extract_int(self, text: str, pattern: str) -> Optional[int]:
        """Extract integer value from text using regex pattern"""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                value_str = match.group(1).replace(',', '')
                return int(value_str)
            except (ValueError, IndexError):
                pass
        return None

    def _extract_text(self, text: str, pattern: str) -> Optional[str]:
        """Extract text value from text using regex pattern"""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text (various formats)"""
        # Try different date patterns
        patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # 2025-10-25
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4})',  # Oct 25, 2025
            r'(\d{1,2}/\d{1,2}/\d{4})',  # 10/25/2025
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # Normalize to YYYY-MM-DD
                try:
                    if '-' in date_str:
                        return date_str
                    elif '/' in date_str:
                        dt = datetime.strptime(date_str, "%m/%d/%Y")
                        return dt.strftime("%Y-%m-%d")
                    else:
                        dt = datetime.strptime(date_str, "%b %d, %Y")
                        return dt.strftime("%Y-%m-%d")
                except ValueError:
                    pass
        return None

    def fetch_actual_prices(self, ticker: str, entry_date: str, exit_date: str) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        """
        Fetch actual prices for a ticker between entry and exit dates.

        Args:
            ticker: Stock ticker symbol
            entry_date: Entry date (YYYY-MM-DD)
            exit_date: Exit/catalyst date (YYYY-MM-DD)

        Returns:
            Tuple of (entry_open, entry_close, exit_high, exit_close)
        """
        try:
            # Add buffer days to ensure data coverage
            start_date = (datetime.strptime(entry_date, "%Y-%m-%d") - timedelta(days=5)).strftime("%Y-%m-%d")
            end_date = (datetime.strptime(exit_date, "%Y-%m-%d") + timedelta(days=5)).strftime("%Y-%m-%d")

            # Fetch data from yfinance
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)

            if hist.empty:
                return None, None, None, None

            # Get entry price (open on entry date, or closest available)
            entry_dt = datetime.strptime(entry_date, "%Y-%m-%d")
            entry_data = hist[hist.index >= entry_dt].head(1)
            entry_open = entry_data['Open'].iloc[0] if not entry_data.empty else None
            entry_close = entry_data['Close'].iloc[0] if not entry_data.empty else None

            # Get exit price (high and close on exit date, or closest available)
            exit_dt = datetime.strptime(exit_date, "%Y-%m-%d")
            exit_data = hist[hist.index >= exit_dt].head(1)
            exit_high = exit_data['High'].iloc[0] if not exit_data.empty else None
            exit_close = exit_data['Close'].iloc[0] if not exit_data.empty else None

            return entry_open, entry_close, exit_high, exit_close

        except Exception as e:
            print(f"Error fetching prices for {ticker}: {e}")
            return None, None, None, None

    def calculate_performance(self) -> Dict:
        """
        Calculate performance metrics for all recommendations.

        Returns:
            Dictionary with performance statistics
        """
        print(f"\nCalculating performance for {len(self.recommendations)} recommendations...")

        wins = 0
        losses = 0
        pending = 0
        total_return = 0.0

        for i, rec in enumerate(self.recommendations, 1):
            print(f"Processing {i}/{len(self.recommendations)}: {rec.ticker} ({rec.strategy})...", end='\r')

            # Determine exit date (catalyst date or 30 days later)
            if rec.catalyst_date:
                exit_date = rec.catalyst_date
            else:
                # Default to 30 days after recommendation
                exit_dt = datetime.strptime(rec.recommendation_date, "%Y-%m-%d") + timedelta(days=30)
                exit_date = exit_dt.strftime("%Y-%m-%d")

            # Fetch actual prices
            entry_open, entry_close, exit_high, exit_close = self.fetch_actual_prices(
                rec.ticker,
                rec.recommendation_date,
                exit_date
            )

            # Store actual prices
            rec.actual_entry_price = entry_open
            rec.actual_catalyst_price = exit_close

            # Calculate return
            if entry_open and exit_close:
                if rec.action in ['BUY', 'LONG']:
                    rec.actual_return = ((exit_close - entry_open) / entry_open) * 100
                elif rec.action == 'SHORT':
                    rec.actual_return = ((entry_open - exit_close) / entry_open) * 100
                else:
                    rec.actual_return = 0.0

                total_return += rec.actual_return

                # Check if target hit
                if rec.target_price and exit_high:
                    if rec.action in ['BUY', 'LONG']:
                        rec.hit_target = exit_high >= rec.target_price
                    else:
                        rec.hit_target = exit_high <= rec.target_price

                # Check if stop hit
                if rec.stop_loss and entry_close and exit_close:
                    price_range = [entry_close, exit_close]
                    if rec.action in ['BUY', 'LONG']:
                        rec.hit_stop = min(price_range) <= rec.stop_loss
                    else:
                        rec.hit_stop = max(price_range) >= rec.stop_loss

                # Determine outcome
                if rec.hit_target:
                    rec.outcome = "WIN"
                    wins += 1
                elif rec.hit_stop:
                    rec.outcome = "LOSS"
                    losses += 1
                elif rec.actual_return > 0:
                    rec.outcome = "WIN"
                    wins += 1
                else:
                    rec.outcome = "LOSS"
                    losses += 1
            else:
                rec.outcome = "PENDING"
                pending += 1

        print("\nPerformance calculation complete!")

        # Calculate statistics
        total_closed = wins + losses
        win_rate = (wins / total_closed * 100) if total_closed > 0 else 0
        avg_return = (total_return / total_closed) if total_closed > 0 else 0

        # Strategy breakdown
        shorgan_recs = [r for r in self.recommendations if r.strategy == "SHORGAN"]
        dee_recs = [r for r in self.recommendations if r.strategy == "DEE"]

        shorgan_wins = len([r for r in shorgan_recs if r.outcome == "WIN"])
        shorgan_total = len([r for r in shorgan_recs if r.outcome in ["WIN", "LOSS"]])
        shorgan_win_rate = (shorgan_wins / shorgan_total * 100) if shorgan_total > 0 else 0

        dee_wins = len([r for r in dee_recs if r.outcome == "WIN"])
        dee_total = len([r for r in dee_recs if r.outcome in ["WIN", "LOSS"]])
        dee_win_rate = (dee_wins / dee_total * 100) if dee_total > 0 else 0

        return {
            'total_recommendations': len(self.recommendations),
            'total_closed': total_closed,
            'wins': wins,
            'losses': losses,
            'pending': pending,
            'win_rate': win_rate,
            'average_return': avg_return,
            'total_return': total_return,
            'shorgan_count': len(shorgan_recs),
            'shorgan_win_rate': shorgan_win_rate,
            'dee_count': len(dee_recs),
            'dee_win_rate': dee_win_rate,
        }

    def generate_performance_report(self, stats: Dict) -> str:
        """
        Generate markdown performance report.

        Args:
            stats: Performance statistics dictionary

        Returns:
            Path to generated report
        """
        report_date = datetime.now().strftime("%Y-%m-%d")
        report_path = self.performance_dir / f"performance_report_{report_date}.md"

        # Sort recommendations by return
        sorted_recs = sorted(
            [r for r in self.recommendations if r.actual_return is not None],
            key=lambda x: x.actual_return or 0,
            reverse=True
        )

        top_winners = sorted_recs[:10]
        top_losers = sorted_recs[-10:]

        # Generate report content
        content = f"""# Recommendation Performance Report
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Recommendations | {stats['total_recommendations']} |
| Closed Positions | {stats['total_closed']} |
| Pending Positions | {stats['pending']} |
| **Win Rate** | **{stats['win_rate']:.1f}%** ({stats['wins']} wins / {stats['losses']} losses) |
| **Average Return** | **{stats['average_return']:.2f}%** |
| Total Return | {stats['total_return']:.2f}% |

## Strategy Performance

### SHORGAN-BOT (Catalyst-Driven)
- **Recommendations**: {stats['shorgan_count']}
- **Win Rate**: {stats['shorgan_win_rate']:.1f}%

### DEE-BOT (Defensive)
- **Recommendations**: {stats['dee_count']}
- **Win Rate**: {stats['dee_win_rate']:.1f}%

## Top 10 Winners

| Rank | Ticker | Strategy | Entry | Exit | Return | Outcome |
|------|--------|----------|-------|------|--------|---------|
"""

        for i, rec in enumerate(top_winners, 1):
            content += f"| {i} | {rec.ticker} | {rec.strategy} | ${rec.actual_entry_price:.2f} | ${rec.actual_catalyst_price:.2f} | **+{rec.actual_return:.2f}%** | {rec.outcome} |\n"

        content += "\n## Top 10 Losers\n\n"
        content += "| Rank | Ticker | Strategy | Entry | Exit | Return | Outcome |\n"
        content += "|------|--------|----------|-------|------|--------|---------|\\n"

        for i, rec in enumerate(reversed(top_losers), 1):
            content += f"| {i} | {rec.ticker} | {rec.strategy} | ${rec.actual_entry_price:.2f} | ${rec.actual_catalyst_price:.2f} | **{rec.actual_return:.2f}%** | {rec.outcome} |\n"

        # Monthly breakdown
        content += "\n## Monthly Performance Breakdown\n\n"

        monthly_stats = {}
        for rec in self.recommendations:
            if not rec.recommendation_date:
                continue
            month = rec.recommendation_date[:7]  # YYYY-MM
            if month not in monthly_stats:
                monthly_stats[month] = {'wins': 0, 'losses': 0, 'return': 0.0}
            if rec.outcome == "WIN":
                monthly_stats[month]['wins'] += 1
            elif rec.outcome == "LOSS":
                monthly_stats[month]['losses'] += 1
            if rec.actual_return:
                monthly_stats[month]['return'] += rec.actual_return

        content += "| Month | Recommendations | Win Rate | Total Return |\n"
        content += "|-------|-----------------|----------|--------------|\\n"

        for month in sorted(monthly_stats.keys()):
            stats_m = monthly_stats[month]
            total_m = stats_m['wins'] + stats_m['losses']
            win_rate_m = (stats_m['wins'] / total_m * 100) if total_m > 0 else 0
            content += f"| {month} | {total_m} | {win_rate_m:.1f}% | {stats_m['return']:.2f}% |\n"

        content += "\n---\n\n"
        content += "*This report tracks the actual performance of recommendations from pre-market reports.*\n"
        content += "*Performance calculated using actual entry and catalyst/exit dates with yfinance data.*\n"

        # Write report
        report_path.write_text(content, encoding='utf-8')
        print(f"\nPerformance report saved to: {report_path}")

        return str(report_path)

    def save_detailed_results(self) -> str:
        """
        Save detailed results as JSON for further analysis.

        Returns:
            Path to JSON file
        """
        report_date = datetime.now().strftime("%Y-%m-%d")
        json_path = self.performance_dir / f"recommendations_detailed_{report_date}.json"

        # Convert recommendations to dict
        data = [asdict(rec) for rec in self.recommendations]

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"Detailed results saved to: {json_path}")
        return str(json_path)


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Backtest historical trading recommendations",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--start',
        type=str,
        help='Start date (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--end',
        type=str,
        help='End date (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--ticker',
        type=str,
        help='Filter by specific ticker symbol'
    )

    parser.add_argument(
        '--strategy',
        type=str,
        choices=['SHORGAN', 'DEE'],
        help='Filter by strategy (SHORGAN or DEE)'
    )

    parser.add_argument(
        '--reports-dir',
        type=str,
        default='reports/premarket',
        help='Directory containing premarket reports (default: reports/premarket)'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("RECOMMENDATION PERFORMANCE BACKTEST")
    print("=" * 80)

    # Initialize backtester
    backtester = RecommendationBacktester(reports_dir=args.reports_dir)

    # Load historical reports
    print(f"\nLoading reports from: {args.reports_dir}")
    if args.start:
        print(f"Start date: {args.start}")
    if args.end:
        print(f"End date: {args.end}")

    count = backtester.load_historical_reports(
        start_date=args.start,
        end_date=args.end
    )

    if count == 0:
        print("\nNo recommendations found. Exiting.")
        return

    # Apply filters
    if args.ticker:
        backtester.recommendations = [
            r for r in backtester.recommendations
            if r.ticker.upper() == args.ticker.upper()
        ]
        print(f"Filtered to ticker: {args.ticker} ({len(backtester.recommendations)} recommendations)")

    if args.strategy:
        backtester.recommendations = [
            r for r in backtester.recommendations
            if r.strategy == args.strategy
        ]
        print(f"Filtered to strategy: {args.strategy} ({len(backtester.recommendations)} recommendations)")

    if not backtester.recommendations:
        print("\nNo recommendations match your filters. Exiting.")
        return

    # Calculate performance
    stats = backtester.calculate_performance()

    # Generate reports
    report_path = backtester.generate_performance_report(stats)
    json_path = backtester.save_detailed_results()

    # Print summary
    print("\n" + "=" * 80)
    print("PERFORMANCE SUMMARY")
    print("=" * 80)
    print(f"Total Recommendations: {stats['total_recommendations']}")
    print(f"Closed Positions: {stats['total_closed']}")
    print(f"Win Rate: {stats['win_rate']:.1f}% ({stats['wins']} wins / {stats['losses']} losses)")
    print(f"Average Return: {stats['average_return']:.2f}%")
    print(f"\nSHORGAN Win Rate: {stats['shorgan_win_rate']:.1f}%")
    print(f"DEE Win Rate: {stats['dee_win_rate']:.1f}%")
    print("\n" + "=" * 80)
    print(f"\nReports generated:")
    print(f"  - Markdown: {report_path}")
    print(f"  - JSON: {json_path}")
    print("\n")


if __name__ == "__main__":
    main()
