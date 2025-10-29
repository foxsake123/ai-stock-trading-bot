"""
Backtest Analysis Script
========================
Analyzes historical trading performance from paper trading data.

Calculates:
- Win rate and trade statistics
- Profit factor and average P&L
- Maximum drawdown and recovery time
- Sharpe ratio and risk metrics
- Per-strategy performance

Usage:
    python backtest_analysis.py --start 2025-09-22 --end 2025-10-27
    python backtest_analysis.py --strategy SHORGAN-BOT
    python backtest_analysis.py --report pdf

Author: AI Trading Bot System
Date: October 29, 2025
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import statistics

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))


class BacktestAnalyzer:
    """Analyze historical trading performance"""

    def __init__(self, start_date: str = None, end_date: str = None):
        self.project_root = Path(__file__).parent.parent.parent
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

        # Load performance history
        self.performance_data = self.load_performance_history()

        # Initial capital
        self.initial_capital = {
            'dee_bot': 100000.0,
            'shorgan_paper': 100000.0,
            'shorgan_live': 1000.0,
            'combined': 201000.0
        }

    def load_performance_history(self) -> List[Dict]:
        """Load performance history from JSON"""
        history_file = self.project_root / "data" / "daily" / "performance" / "performance_history.json"

        if not history_file.exists():
            print(f"ERROR: Performance history not found at {history_file}")
            return []

        with open(history_file, 'r') as f:
            data = json.load(f)

        # Extract daily_records array
        daily_records = data.get('daily_records', [])

        # Filter by date range if specified
        if self.start_date or self.end_date:
            filtered = []
            for record in daily_records:
                record_date = datetime.strptime(record['date'], "%Y-%m-%d")
                if self.start_date and record_date < self.start_date:
                    continue
                if self.end_date and record_date > self.end_date:
                    continue
                filtered.append(record)
            return filtered

        return daily_records

    def calculate_returns(self, strategy: str = 'combined') -> Dict:
        """Calculate return metrics for a strategy"""
        if not self.performance_data:
            return {}

        # Get initial and final values
        first_record = self.performance_data[0]
        last_record = self.performance_data[-1]

        # Handle old naming (shorgan_bot) and new naming (shorgan_paper)
        strategy_key = strategy
        if strategy == 'shorgan_paper' and 'shorgan_bot' in first_record and 'shorgan_paper' not in first_record:
            strategy_key = 'shorgan_bot'

        # For combined, get total_value instead of value
        if strategy == 'combined':
            initial_value = first_record.get(strategy_key, {}).get('total_value', self.initial_capital.get(strategy, 0))
            final_value = last_record.get(strategy_key, {}).get('total_value', 0)
        else:
            initial_value = first_record.get(strategy_key, {}).get('value', self.initial_capital.get(strategy, 0))
            final_value = last_record.get(strategy_key, {}).get('value', 0)

        total_return = ((final_value - initial_value) / initial_value) * 100
        absolute_profit = final_value - initial_value

        # Calculate daily returns
        daily_returns = []
        for i in range(1, len(self.performance_data)):
            # Handle old naming
            strategy_key_prev = strategy if strategy in self.performance_data[i-1] else 'shorgan_bot' if strategy == 'shorgan_paper' else strategy
            strategy_key_curr = strategy if strategy in self.performance_data[i] else 'shorgan_bot' if strategy == 'shorgan_paper' else strategy

            if strategy == 'combined':
                prev_value = self.performance_data[i-1].get(strategy_key_prev, {}).get('total_value', 0)
                curr_value = self.performance_data[i].get(strategy_key_curr, {}).get('total_value', 0)
            else:
                prev_value = self.performance_data[i-1].get(strategy_key_prev, {}).get('value', 0)
                curr_value = self.performance_data[i].get(strategy_key_curr, {}).get('value', 0)

            if prev_value > 0:
                daily_return = ((curr_value - prev_value) / prev_value) * 100
                daily_returns.append(daily_return)

        return {
            'initial_value': initial_value,
            'final_value': final_value,
            'total_return_pct': total_return,
            'absolute_profit': absolute_profit,
            'daily_returns': daily_returns,
            'trading_days': len(self.performance_data)
        }

    def calculate_sharpe_ratio(self, daily_returns: List[float], risk_free_rate: float = 0.05) -> float:
        """Calculate annualized Sharpe ratio"""
        if len(daily_returns) < 2:
            return 0.0

        # Convert annual risk-free rate to daily
        daily_rf = (1 + risk_free_rate) ** (1/252) - 1

        # Calculate excess returns
        excess_returns = [r/100 - daily_rf for r in daily_returns]

        # Calculate Sharpe ratio
        avg_excess = statistics.mean(excess_returns)
        std_excess = statistics.stdev(excess_returns) if len(excess_returns) > 1 else 0

        if std_excess == 0:
            return 0.0

        # Annualize
        sharpe = (avg_excess / std_excess) * (252 ** 0.5)
        return sharpe

    def calculate_max_drawdown(self, strategy: str = 'combined') -> Dict:
        """Calculate maximum drawdown and recovery time"""
        if not self.performance_data:
            return {}

        # Track running maximum and drawdowns
        peak_value = 0
        max_drawdown_pct = 0
        max_drawdown_dollars = 0
        current_drawdown_start = None
        longest_drawdown_days = 0
        current_drawdown_days = 0

        for i, record in enumerate(self.performance_data):
            # Handle old naming
            strategy_key = strategy if strategy in record else 'shorgan_bot' if strategy == 'shorgan_paper' else strategy

            if strategy == 'combined':
                value = record.get(strategy_key, {}).get('total_value', 0)
            else:
                value = record.get(strategy_key, {}).get('value', 0)

            # Update peak
            if value > peak_value:
                peak_value = value
                if current_drawdown_start is not None:
                    # Recovered from drawdown
                    longest_drawdown_days = max(longest_drawdown_days, current_drawdown_days)
                    current_drawdown_start = None
                    current_drawdown_days = 0

            # Calculate drawdown
            if peak_value > 0:
                drawdown_pct = ((peak_value - value) / peak_value) * 100
                drawdown_dollars = peak_value - value

                if drawdown_pct > max_drawdown_pct:
                    max_drawdown_pct = drawdown_pct
                    max_drawdown_dollars = drawdown_dollars

                # Track drawdown duration
                if drawdown_pct > 0:
                    if current_drawdown_start is None:
                        current_drawdown_start = i
                    current_drawdown_days = i - current_drawdown_start

        return {
            'max_drawdown_pct': max_drawdown_pct,
            'max_drawdown_dollars': max_drawdown_dollars,
            'longest_drawdown_days': longest_drawdown_days
        }

    def calculate_volatility(self, daily_returns: List[float]) -> float:
        """Calculate annualized volatility"""
        if len(daily_returns) < 2:
            return 0.0

        daily_vol = statistics.stdev([r/100 for r in daily_returns])
        annualized_vol = daily_vol * (252 ** 0.5) * 100
        return annualized_vol

    def generate_report(self, strategy: str = 'combined') -> str:
        """Generate comprehensive backtest report"""
        print(f"\n{'='*80}")
        print(f"BACKTEST ANALYSIS: {strategy.upper().replace('_', ' ')}")
        print(f"{'='*80}")

        # Date range
        if self.performance_data:
            start_date = self.performance_data[0].get('date', self.performance_data[0].get('timestamp', '')[:10])
            end_date = self.performance_data[-1].get('date', self.performance_data[-1].get('timestamp', '')[:10])
            print(f"Period: {start_date} to {end_date}")
            print(f"Trading Days: {len(self.performance_data)}")
        print()

        # Returns
        returns = self.calculate_returns(strategy)
        if returns:
            print(f"{'='*80}")
            print("RETURN METRICS")
            print(f"{'='*80}")
            print(f"Initial Capital:     ${returns['initial_value']:,.2f}")
            print(f"Final Value:         ${returns['final_value']:,.2f}")
            print(f"Absolute Profit:     ${returns['absolute_profit']:,.2f}")
            print(f"Total Return:        {returns['total_return_pct']:+.2f}%")
            print()

            # Daily statistics
            daily_returns = returns['daily_returns']
            if daily_returns:
                positive_days = sum(1 for r in daily_returns if r > 0)
                negative_days = sum(1 for r in daily_returns if r < 0)
                flat_days = sum(1 for r in daily_returns if r == 0)

                print(f"Positive Days:       {positive_days} ({positive_days/len(daily_returns)*100:.1f}%)")
                print(f"Negative Days:       {negative_days} ({negative_days/len(daily_returns)*100:.1f}%)")
                print(f"Flat Days:           {flat_days}")
                print()

                print(f"Average Daily Return: {statistics.mean(daily_returns):+.2f}%")
                print(f"Best Day:            {max(daily_returns):+.2f}%")
                print(f"Worst Day:           {min(daily_returns):+.2f}%")
                print()

        # Risk Metrics
        if returns and returns.get('daily_returns'):
            daily_returns = returns['daily_returns']

            print(f"{'='*80}")
            print("RISK METRICS")
            print(f"{'='*80}")

            # Volatility
            volatility = self.calculate_volatility(daily_returns)
            print(f"Annualized Volatility: {volatility:.2f}%")

            # Sharpe Ratio
            sharpe = self.calculate_sharpe_ratio(daily_returns)
            print(f"Sharpe Ratio:         {sharpe:.2f}")

            # Drawdown
            drawdown = self.calculate_max_drawdown(strategy)
            if drawdown:
                print(f"Max Drawdown:         {drawdown['max_drawdown_pct']:.2f}% (${drawdown['max_drawdown_dollars']:,.2f})")
                print(f"Longest Drawdown:     {drawdown['longest_drawdown_days']} days")
            print()

        # Strategy-specific notes
        print(f"{'='*80}")
        print("ASSESSMENT")
        print(f"{'='*80}")

        if returns:
            total_return = returns['total_return_pct']
            sharpe = self.calculate_sharpe_ratio(returns['daily_returns']) if returns.get('daily_returns') else 0

            # Rating
            if total_return > 10 and sharpe > 1.5:
                rating = "EXCELLENT"
            elif total_return > 5 and sharpe > 1.0:
                rating = "GOOD"
            elif total_return > 0 and sharpe > 0.5:
                rating = "ACCEPTABLE"
            elif total_return > 0:
                rating = "MARGINAL"
            else:
                rating = "POOR"

            print(f"Overall Rating: {rating}")
            print()

            # Recommendations
            print("Recommendations:")
            if sharpe < 0.5:
                print("  - Sharpe ratio low: Consider tightening stop losses")
            if returns['total_return_pct'] < 0:
                print("  - Negative returns: Review strategy or market conditions")
            if drawdown and drawdown['max_drawdown_pct'] > 15:
                print("  - High drawdown: Reduce position sizes or add diversification")
            if len(daily_returns) < 20:
                print("  - Limited data: Continue testing for at least 30 days")
            if sharpe > 1.0 and total_return > 5:
                print("  - Good performance: Consider scaling capital gradually")

        print(f"{'='*80}\n")

        return "Report generated successfully"

    def compare_strategies(self) -> str:
        """Compare all strategies side-by-side"""
        print(f"\n{'='*80}")
        print("STRATEGY COMPARISON")
        print(f"{'='*80}\n")

        strategies = ['dee_bot', 'shorgan_paper', 'shorgan_live', 'combined']
        results = {}

        for strategy in strategies:
            returns = self.calculate_returns(strategy)
            if returns and returns.get('daily_returns'):
                sharpe = self.calculate_sharpe_ratio(returns['daily_returns'])
                drawdown = self.calculate_max_drawdown(strategy)

                results[strategy] = {
                    'return': returns['total_return_pct'],
                    'sharpe': sharpe,
                    'drawdown': drawdown['max_drawdown_pct'] if drawdown else 0,
                    'final_value': returns['final_value']
                }

        # Print comparison table
        print(f"{'Strategy':<20} {'Return':<12} {'Sharpe':<10} {'Max DD':<12} {'Final Value'}")
        print(f"{'-'*80}")

        for strategy, metrics in results.items():
            strategy_name = strategy.replace('_', ' ').title()
            print(f"{strategy_name:<20} {metrics['return']:>+10.2f}% "
                  f"{metrics['sharpe']:>8.2f}  {metrics['drawdown']:>10.2f}% "
                  f"${metrics['final_value']:>12,.2f}")

        print(f"\n{'='*80}\n")

        # Winner
        if results:
            best_return = max(results.items(), key=lambda x: x[1]['return'])
            best_sharpe = max(results.items(), key=lambda x: x[1]['sharpe'])

            print(f"Best Return:      {best_return[0].replace('_', ' ').title()} ({best_return[1]['return']:+.2f}%)")
            print(f"Best Risk-Adj:    {best_sharpe[0].replace('_', ' ').title()} (Sharpe {best_sharpe[1]['sharpe']:.2f})")
            print()

        return "Comparison complete"


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description="Backtest analysis for AI trading bot")
    parser.add_argument('--start', help='Start date (YYYY-MM-DD)', default='2025-09-22')
    parser.add_argument('--end', help='End date (YYYY-MM-DD)', default='2025-10-27')
    parser.add_argument('--strategy', help='Strategy to analyze (dee_bot, shorgan_paper, shorgan_live, combined)',
                       default='all')
    parser.add_argument('--compare', action='store_true', help='Compare all strategies')

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = BacktestAnalyzer(start_date=args.start, end_date=args.end)

    # Generate reports
    if args.strategy == 'all' or args.compare:
        # Compare all strategies
        analyzer.compare_strategies()

        # Individual reports
        for strategy in ['combined', 'dee_bot', 'shorgan_paper', 'shorgan_live']:
            analyzer.generate_report(strategy)
    else:
        # Single strategy report
        analyzer.generate_report(args.strategy)


if __name__ == "__main__":
    main()
