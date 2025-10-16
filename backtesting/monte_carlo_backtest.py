"""
Monte Carlo Backtesting Engine
Simulates multiple trading scenarios to test strategy robustness
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class DistributionType(Enum):
    """Statistical distribution types"""
    NORMAL = "normal"
    LOGNORMAL = "lognormal"
    T_DISTRIBUTION = "t_distribution"
    HISTORICAL = "historical"


@dataclass
class Trade:
    """Individual trade in simulation"""
    ticker: str
    entry_date: datetime
    entry_price: float
    exit_date: datetime
    exit_price: float
    position_size: float  # Percentage of portfolio
    return_pct: float
    win: bool
    max_drawdown: float  # During holding period
    holding_days: int


@dataclass
class SimulationResult:
    """Results from a single Monte Carlo simulation"""
    simulation_id: int
    total_return: float
    final_portfolio_value: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    profit_factor: float
    max_consecutive_wins: int
    max_consecutive_losses: int
    trades: List[Trade] = field(default_factory=list)


@dataclass
class MonteCarloResults:
    """Aggregated results from all Monte Carlo simulations"""
    num_simulations: int
    initial_capital: float

    # Return statistics
    mean_return: float
    median_return: float
    std_return: float
    best_return: float
    worst_return: float
    percentile_5: float
    percentile_25: float
    percentile_75: float
    percentile_95: float

    # Drawdown statistics
    mean_max_drawdown: float
    median_max_drawdown: float
    worst_max_drawdown: float

    # Risk metrics
    mean_sharpe: float
    median_sharpe: float
    mean_sortino: float

    # Win rate statistics
    mean_win_rate: float
    median_win_rate: float

    # Probability of outcomes
    prob_profit: float  # Probability of positive return
    prob_10pct_gain: float
    prob_20pct_gain: float
    prob_10pct_loss: float
    prob_20pct_loss: float

    # Confidence intervals (95%)
    return_ci_lower: float
    return_ci_upper: float
    drawdown_ci_lower: float
    drawdown_ci_upper: float

    # All simulations
    simulations: List[SimulationResult] = field(default_factory=list)


class MonteCarloBacktest:
    """Monte Carlo backtesting engine"""

    def __init__(
        self,
        initial_capital: float = 100000.0,
        risk_free_rate: float = 0.04,
        distribution_type: DistributionType = DistributionType.NORMAL
    ):
        """
        Initialize Monte Carlo backtest

        Args:
            initial_capital: Starting portfolio value
            risk_free_rate: Annual risk-free rate for Sharpe/Sortino
            distribution_type: Distribution for randomizing returns
        """
        self.initial_capital = initial_capital
        self.risk_free_rate = risk_free_rate
        self.distribution_type = distribution_type

        # Historical statistics (set from historical data)
        self.mean_return: Optional[float] = None
        self.std_return: Optional[float] = None
        self.mean_win_rate: Optional[float] = None
        self.mean_holding_period: Optional[int] = None
        self.historical_returns: List[float] = []

    def fit_historical_data(
        self,
        historical_trades: List[Dict[str, Any]]
    ) -> None:
        """
        Fit parameters from historical trading data

        Args:
            historical_trades: List of historical trade results
        """
        if not historical_trades:
            raise ValueError("No historical trades provided")

        returns = [t.get('return_pct', 0) for t in historical_trades]
        wins = [t.get('win', False) for t in historical_trades]
        holding_periods = [t.get('holding_days', 0) for t in historical_trades]

        self.historical_returns = returns
        self.mean_return = np.mean(returns)
        self.std_return = np.std(returns)
        self.mean_win_rate = np.mean(wins)
        self.mean_holding_period = int(np.mean(holding_periods))

        logger.info(f"Fitted historical data: {len(historical_trades)} trades")
        logger.info(f"Mean return: {self.mean_return:.2%}")
        logger.info(f"Std return: {self.std_return:.2%}")
        logger.info(f"Win rate: {self.mean_win_rate:.2%}")

    def generate_random_return(self) -> float:
        """
        Generate random return based on distribution type

        Returns:
            Random return percentage
        """
        if self.mean_return is None or self.std_return is None:
            raise ValueError("Must call fit_historical_data() first")

        if self.distribution_type == DistributionType.NORMAL:
            return np.random.normal(self.mean_return, self.std_return)

        elif self.distribution_type == DistributionType.LOGNORMAL:
            # Lognormal better models positive-skewed returns
            mu = np.log(1 + self.mean_return) - 0.5 * np.log(1 + (self.std_return / (1 + self.mean_return))**2)
            sigma = np.sqrt(np.log(1 + (self.std_return / (1 + self.mean_return))**2))
            return np.random.lognormal(mu, sigma) - 1

        elif self.distribution_type == DistributionType.T_DISTRIBUTION:
            # T-distribution has fatter tails (more extreme outcomes)
            df = 5  # Degrees of freedom
            return self.mean_return + self.std_return * np.random.standard_t(df)

        elif self.distribution_type == DistributionType.HISTORICAL:
            # Bootstrap from historical returns
            return np.random.choice(self.historical_returns)

        else:
            raise ValueError(f"Unknown distribution type: {self.distribution_type}")

    def simulate_trade_sequence(
        self,
        num_trades: int,
        position_size_range: Tuple[float, float] = (0.02, 0.10)
    ) -> List[Trade]:
        """
        Simulate a sequence of trades

        Args:
            num_trades: Number of trades to simulate
            position_size_range: Min/max position size (as portfolio %)

        Returns:
            List of simulated trades
        """
        trades = []
        current_date = datetime.now()

        for i in range(num_trades):
            # Generate random return
            return_pct = self.generate_random_return()

            # Random position size within range
            position_size = np.random.uniform(*position_size_range)

            # Random holding period around mean
            if self.mean_holding_period:
                holding_days = max(1, int(np.random.normal(
                    self.mean_holding_period,
                    self.mean_holding_period * 0.3
                )))
            else:
                holding_days = np.random.randint(1, 30)

            # Simulate trade
            entry_date = current_date
            exit_date = entry_date + timedelta(days=holding_days)
            entry_price = 100.0  # Normalized
            exit_price = entry_price * (1 + return_pct)

            # Simulate intra-trade drawdown
            # Assume max drawdown is between 0 and abs(return) * 1.5
            if return_pct >= 0:
                max_dd = np.random.uniform(0, abs(return_pct) * 0.5)
            else:
                max_dd = abs(return_pct) + np.random.uniform(0, abs(return_pct) * 0.5)

            trade = Trade(
                ticker=f"SIM{i}",
                entry_date=entry_date,
                entry_price=entry_price,
                exit_date=exit_date,
                exit_price=exit_price,
                position_size=position_size,
                return_pct=return_pct,
                win=return_pct > 0,
                max_drawdown=max_dd,
                holding_days=holding_days
            )

            trades.append(trade)
            current_date = exit_date

        return trades

    def calculate_portfolio_metrics(
        self,
        trades: List[Trade],
        initial_capital: float
    ) -> Tuple[float, float, float, float]:
        """
        Calculate portfolio performance metrics

        Args:
            trades: List of trades
            initial_capital: Starting capital

        Returns:
            (total_return, max_drawdown, sharpe_ratio, sortino_ratio)
        """
        if not trades:
            return 0.0, 0.0, 0.0, 0.0

        # Calculate portfolio value over time
        portfolio_values = [initial_capital]
        capital = initial_capital

        for trade in trades:
            # Capital allocated to this trade
            trade_capital = capital * trade.position_size
            # P&L from trade
            pnl = trade_capital * trade.return_pct
            # Update capital
            capital += pnl
            portfolio_values.append(capital)

        # Total return
        total_return = (capital - initial_capital) / initial_capital

        # Max drawdown
        peak = portfolio_values[0]
        max_drawdown = 0.0

        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # Calculate returns for Sharpe/Sortino
        returns = []
        for i in range(1, len(portfolio_values)):
            ret = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
            returns.append(ret)

        if not returns:
            return total_return, max_drawdown, 0.0, 0.0

        # Sharpe ratio (annualized)
        mean_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return > 0:
            # Assuming daily returns, annualize
            sharpe_ratio = (mean_return * 252 - self.risk_free_rate) / (std_return * np.sqrt(252))
        else:
            sharpe_ratio = 0.0

        # Sortino ratio (only downside deviation)
        negative_returns = [r for r in returns if r < 0]
        if negative_returns:
            downside_std = np.std(negative_returns)
            if downside_std > 0:
                sortino_ratio = (mean_return * 252 - self.risk_free_rate) / (downside_std * np.sqrt(252))
            else:
                sortino_ratio = sharpe_ratio
        else:
            sortino_ratio = sharpe_ratio

        return total_return, max_drawdown, sharpe_ratio, sortino_ratio

    def run_simulation(
        self,
        simulation_id: int,
        num_trades: int,
        position_size_range: Tuple[float, float] = (0.02, 0.10)
    ) -> SimulationResult:
        """
        Run a single Monte Carlo simulation

        Args:
            simulation_id: Simulation number
            num_trades: Number of trades to simulate
            position_size_range: Position size range

        Returns:
            SimulationResult
        """
        # Generate trades
        trades = self.simulate_trade_sequence(num_trades, position_size_range)

        # Calculate metrics
        total_return, max_drawdown, sharpe, sortino = self.calculate_portfolio_metrics(
            trades, self.initial_capital
        )

        # Trade statistics
        winning_trades = [t for t in trades if t.win]
        losing_trades = [t for t in trades if not t.win]

        win_rate = len(winning_trades) / len(trades) if trades else 0.0
        avg_win = np.mean([t.return_pct for t in winning_trades]) if winning_trades else 0.0
        avg_loss = np.mean([t.return_pct for t in losing_trades]) if losing_trades else 0.0

        # Profit factor
        total_wins = sum(t.return_pct * t.position_size for t in winning_trades)
        total_losses = abs(sum(t.return_pct * t.position_size for t in losing_trades))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')

        # Consecutive wins/losses
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        current_wins = 0
        current_losses = 0

        for trade in trades:
            if trade.win:
                current_wins += 1
                current_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, current_losses)

        return SimulationResult(
            simulation_id=simulation_id,
            total_return=total_return,
            final_portfolio_value=self.initial_capital * (1 + total_return),
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            win_rate=win_rate,
            total_trades=len(trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            max_consecutive_wins=max_consecutive_wins,
            max_consecutive_losses=max_consecutive_losses,
            trades=trades
        )

    def run_monte_carlo(
        self,
        num_simulations: int = 1000,
        num_trades_per_simulation: int = 50,
        position_size_range: Tuple[float, float] = (0.02, 0.10),
        random_seed: Optional[int] = None
    ) -> MonteCarloResults:
        """
        Run Monte Carlo simulations

        Args:
            num_simulations: Number of simulations to run
            num_trades_per_simulation: Trades per simulation
            position_size_range: Position size range
            random_seed: Random seed for reproducibility

        Returns:
            MonteCarloResults with aggregated statistics
        """
        if self.mean_return is None:
            raise ValueError("Must call fit_historical_data() first")

        if random_seed is not None:
            np.random.seed(random_seed)

        logger.info(f"Running {num_simulations} Monte Carlo simulations...")

        simulations = []

        for i in range(num_simulations):
            sim = self.run_simulation(i, num_trades_per_simulation, position_size_range)
            simulations.append(sim)

            if (i + 1) % 100 == 0:
                logger.info(f"Completed {i + 1}/{num_simulations} simulations")

        # Aggregate statistics
        returns = [s.total_return for s in simulations]
        drawdowns = [s.max_drawdown for s in simulations]
        sharpes = [s.sharpe_ratio for s in simulations]
        sortinos = [s.sortino_ratio for s in simulations]
        win_rates = [s.win_rate for s in simulations]

        # Return statistics
        mean_return = np.mean(returns)
        median_return = np.median(returns)
        std_return = np.std(returns)
        best_return = max(returns)
        worst_return = min(returns)

        p5 = np.percentile(returns, 5)
        p25 = np.percentile(returns, 25)
        p75 = np.percentile(returns, 75)
        p95 = np.percentile(returns, 95)

        # Drawdown statistics
        mean_dd = np.mean(drawdowns)
        median_dd = np.median(drawdowns)
        worst_dd = max(drawdowns)

        # Risk metrics
        mean_sharpe = np.mean(sharpes)
        median_sharpe = np.median(sharpes)
        mean_sortino = np.mean(sortinos)

        # Win rate
        mean_wr = np.mean(win_rates)
        median_wr = np.median(win_rates)

        # Probabilities
        prob_profit = sum(1 for r in returns if r > 0) / len(returns)
        prob_10_gain = sum(1 for r in returns if r > 0.10) / len(returns)
        prob_20_gain = sum(1 for r in returns if r > 0.20) / len(returns)
        prob_10_loss = sum(1 for r in returns if r < -0.10) / len(returns)
        prob_20_loss = sum(1 for r in returns if r < -0.20) / len(returns)

        # Confidence intervals (95%)
        return_ci_lower = np.percentile(returns, 2.5)
        return_ci_upper = np.percentile(returns, 97.5)
        dd_ci_lower = np.percentile(drawdowns, 2.5)
        dd_ci_upper = np.percentile(drawdowns, 97.5)

        results = MonteCarloResults(
            num_simulations=num_simulations,
            initial_capital=self.initial_capital,
            mean_return=mean_return,
            median_return=median_return,
            std_return=std_return,
            best_return=best_return,
            worst_return=worst_return,
            percentile_5=p5,
            percentile_25=p25,
            percentile_75=p75,
            percentile_95=p95,
            mean_max_drawdown=mean_dd,
            median_max_drawdown=median_dd,
            worst_max_drawdown=worst_dd,
            mean_sharpe=mean_sharpe,
            median_sharpe=median_sharpe,
            mean_sortino=mean_sortino,
            mean_win_rate=mean_wr,
            median_win_rate=median_wr,
            prob_profit=prob_profit,
            prob_10pct_gain=prob_10_gain,
            prob_20pct_gain=prob_20_gain,
            prob_10pct_loss=prob_10_loss,
            prob_20pct_loss=prob_20_loss,
            return_ci_lower=return_ci_lower,
            return_ci_upper=return_ci_upper,
            drawdown_ci_lower=dd_ci_lower,
            drawdown_ci_upper=dd_ci_upper,
            simulations=simulations
        )

        logger.info(f"Monte Carlo complete: Mean return = {mean_return:.2%}")

        return results

    def generate_report(self, results: MonteCarloResults) -> str:
        """
        Generate markdown report of Monte Carlo results

        Args:
            results: MonteCarloResults object

        Returns:
            Markdown formatted report
        """
        report = "# Monte Carlo Backtest Results\n\n"

        report += f"**Simulations**: {results.num_simulations:,}\n"
        report += f"**Initial Capital**: ${results.initial_capital:,.2f}\n"
        report += f"**Distribution**: {self.distribution_type.value}\n\n"

        report += "## Return Statistics\n\n"
        report += f"- **Mean Return**: {results.mean_return:.2%}\n"
        report += f"- **Median Return**: {results.median_return:.2%}\n"
        report += f"- **Std Deviation**: {results.std_return:.2%}\n"
        report += f"- **Best Case**: {results.best_return:.2%}\n"
        report += f"- **Worst Case**: {results.worst_return:.2%}\n"
        report += f"- **95% CI**: [{results.return_ci_lower:.2%}, {results.return_ci_upper:.2%}]\n\n"

        report += "### Percentiles\n\n"
        report += f"- **5th**: {results.percentile_5:.2%}\n"
        report += f"- **25th**: {results.percentile_25:.2%}\n"
        report += f"- **75th**: {results.percentile_75:.2%}\n"
        report += f"- **95th**: {results.percentile_95:.2%}\n\n"

        report += "## Risk Metrics\n\n"
        report += f"- **Mean Max Drawdown**: {results.mean_max_drawdown:.2%}\n"
        report += f"- **Median Max Drawdown**: {results.median_max_drawdown:.2%}\n"
        report += f"- **Worst Drawdown**: {results.worst_max_drawdown:.2%}\n"
        report += f"- **Mean Sharpe Ratio**: {results.mean_sharpe:.2f}\n"
        report += f"- **Median Sharpe Ratio**: {results.median_sharpe:.2f}\n"
        report += f"- **Mean Sortino Ratio**: {results.mean_sortino:.2f}\n\n"

        report += "## Outcome Probabilities\n\n"
        report += f"- **Profit**: {results.prob_profit:.1%}\n"
        report += f"- **>10% Gain**: {results.prob_10pct_gain:.1%}\n"
        report += f"- **>20% Gain**: {results.prob_20pct_gain:.1%}\n"
        report += f"- **>10% Loss**: {results.prob_10pct_loss:.1%}\n"
        report += f"- **>20% Loss**: {results.prob_20pct_loss:.1%}\n\n"

        report += "## Win Rate\n\n"
        report += f"- **Mean Win Rate**: {results.mean_win_rate:.1%}\n"
        report += f"- **Median Win Rate**: {results.median_win_rate:.1%}\n\n"

        report += "## Interpretation\n\n"

        if results.mean_return > 0 and results.prob_profit > 0.60:
            report += "✅ **Positive Expected Value**: Strategy shows positive mean return with >60% probability of profit.\n\n"
        elif results.mean_return > 0:
            report += "⚠️ **Modest Positive Expectancy**: Positive mean but lower probability of profit.\n\n"
        else:
            report += "❌ **Negative Expected Value**: Strategy shows negative mean return.\n\n"

        if results.mean_sharpe > 1.0:
            report += "✅ **Good Risk-Adjusted Returns**: Sharpe ratio >1.0 indicates favorable risk/reward.\n\n"
        elif results.mean_sharpe > 0.5:
            report += "⚠️ **Moderate Risk-Adjusted Returns**: Sharpe ratio >0.5 but room for improvement.\n\n"
        else:
            report += "❌ **Poor Risk-Adjusted Returns**: Low Sharpe ratio indicates poor risk/reward.\n\n"

        if results.mean_max_drawdown < 0.15:
            report += "✅ **Manageable Drawdown**: Mean max drawdown <15%.\n\n"
        elif results.mean_max_drawdown < 0.25:
            report += "⚠️ **Moderate Drawdown Risk**: Mean max drawdown 15-25%.\n\n"
        else:
            report += "❌ **High Drawdown Risk**: Mean max drawdown >25%.\n\n"

        return report


def run_monte_carlo_backtest(
    historical_trades: List[Dict[str, Any]],
    num_simulations: int = 1000,
    num_trades_per_simulation: int = 50,
    initial_capital: float = 100000.0,
    distribution_type: DistributionType = DistributionType.NORMAL
) -> MonteCarloResults:
    """
    Convenience function to run Monte Carlo backtest

    Args:
        historical_trades: Historical trade data
        num_simulations: Number of simulations
        num_trades_per_simulation: Trades per simulation
        initial_capital: Starting capital
        distribution_type: Return distribution type

    Returns:
        MonteCarloResults
    """
    backtest = MonteCarloBacktest(
        initial_capital=initial_capital,
        distribution_type=distribution_type
    )

    backtest.fit_historical_data(historical_trades)

    results = backtest.run_monte_carlo(
        num_simulations=num_simulations,
        num_trades_per_simulation=num_trades_per_simulation
    )

    return results
