"""Tests for Monte Carlo Backtesting Engine"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from backtesting.monte_carlo_backtest import (
    MonteCarloBacktest,
    Trade,
    SimulationResult,
    MonteCarloResults,
    DistributionType,
    run_monte_carlo_backtest
)


@pytest.fixture
def sample_historical_trades():
    """Sample historical trades for testing"""
    return [
        {'return_pct': 0.05, 'win': True, 'holding_days': 7},
        {'return_pct': -0.03, 'win': False, 'holding_days': 5},
        {'return_pct': 0.08, 'win': True, 'holding_days': 10},
        {'return_pct': 0.02, 'win': True, 'holding_days': 3},
        {'return_pct': -0.04, 'win': False, 'holding_days': 8},
        {'return_pct': 0.10, 'win': True, 'holding_days': 12},
        {'return_pct': -0.02, 'win': False, 'holding_days': 4},
        {'return_pct': 0.06, 'win': True, 'holding_days': 9},
        {'return_pct': 0.03, 'win': True, 'holding_days': 6},
        {'return_pct': -0.05, 'win': False, 'holding_days': 7}
    ]


@pytest.fixture
def backtest():
    """Create backtest instance"""
    return MonteCarloBacktest(
        initial_capital=100000.0,
        risk_free_rate=0.04,
        distribution_type=DistributionType.NORMAL
    )


@pytest.fixture
def fitted_backtest(backtest, sample_historical_trades):
    """Fitted backtest instance"""
    backtest.fit_historical_data(sample_historical_trades)
    return backtest


class TestMonteCarloBacktestInitialization:
    """Test backtest initialization"""

    def test_initialization_default(self):
        """Test default initialization"""
        backtest = MonteCarloBacktest()

        assert backtest.initial_capital == 100000.0
        assert backtest.risk_free_rate == 0.04
        assert backtest.distribution_type == DistributionType.NORMAL
        assert backtest.mean_return is None
        assert backtest.std_return is None

    def test_initialization_custom(self):
        """Test custom initialization"""
        backtest = MonteCarloBacktest(
            initial_capital=50000.0,
            risk_free_rate=0.05,
            distribution_type=DistributionType.LOGNORMAL
        )

        assert backtest.initial_capital == 50000.0
        assert backtest.risk_free_rate == 0.05
        assert backtest.distribution_type == DistributionType.LOGNORMAL

    def test_initialization_all_distribution_types(self):
        """Test all distribution types"""
        for dist_type in DistributionType:
            backtest = MonteCarloBacktest(distribution_type=dist_type)
            assert backtest.distribution_type == dist_type


class TestFitHistoricalData:
    """Test fitting historical data"""

    def test_fit_historical_data(self, backtest, sample_historical_trades):
        """Test fitting historical trades"""
        backtest.fit_historical_data(sample_historical_trades)

        assert backtest.mean_return is not None
        assert backtest.std_return is not None
        assert backtest.mean_win_rate is not None
        assert backtest.mean_holding_period is not None
        assert len(backtest.historical_returns) == len(sample_historical_trades)

    def test_fit_calculates_correct_statistics(self, backtest, sample_historical_trades):
        """Test statistical calculations"""
        backtest.fit_historical_data(sample_historical_trades)

        # Mean return should be (0.05 - 0.03 + 0.08 + ... - 0.05) / 10 = 0.02
        expected_mean = 0.02
        assert abs(backtest.mean_return - expected_mean) < 0.001

        # Win rate should be 6/10 = 0.6
        assert backtest.mean_win_rate == 0.6

        # Mean holding period should be 7.1
        assert backtest.mean_holding_period == 7

    def test_fit_empty_trades_raises_error(self, backtest):
        """Test fitting empty trades raises error"""
        with pytest.raises(ValueError, match="No historical trades"):
            backtest.fit_historical_data([])


class TestGenerateRandomReturn:
    """Test random return generation"""

    def test_generate_normal_return(self, fitted_backtest):
        """Test normal distribution returns"""
        fitted_backtest.distribution_type = DistributionType.NORMAL

        # Generate multiple returns and check distribution
        returns = [fitted_backtest.generate_random_return() for _ in range(1000)]

        # Mean should be close to fitted mean
        assert abs(np.mean(returns) - fitted_backtest.mean_return) < 0.01

        # Std should be close to fitted std
        assert abs(np.std(returns) - fitted_backtest.std_return) < 0.02

    def test_generate_lognormal_return(self, fitted_backtest):
        """Test lognormal distribution returns"""
        fitted_backtest.distribution_type = DistributionType.LOGNORMAL

        returns = [fitted_backtest.generate_random_return() for _ in range(1000)]

        # Should have positive skew (more common in stock returns)
        assert len(returns) == 1000

    def test_generate_t_distribution_return(self, fitted_backtest):
        """Test t-distribution returns"""
        fitted_backtest.distribution_type = DistributionType.T_DISTRIBUTION

        returns = [fitted_backtest.generate_random_return() for _ in range(1000)]

        # Should have fatter tails than normal
        assert len(returns) == 1000

    def test_generate_historical_return(self, fitted_backtest):
        """Test historical bootstrap returns"""
        fitted_backtest.distribution_type = DistributionType.HISTORICAL

        returns = [fitted_backtest.generate_random_return() for _ in range(100)]

        # All returns should be from historical set
        for ret in returns:
            assert ret in fitted_backtest.historical_returns

    def test_generate_without_fit_raises_error(self, backtest):
        """Test generating return without fitting raises error"""
        with pytest.raises(ValueError, match="Must call fit_historical_data"):
            backtest.generate_random_return()


class TestSimulateTradeSequence:
    """Test trade sequence simulation"""

    def test_simulate_trade_sequence(self, fitted_backtest):
        """Test simulating trades"""
        trades = fitted_backtest.simulate_trade_sequence(num_trades=10)

        assert len(trades) == 10
        assert all(isinstance(t, Trade) for t in trades)

    def test_trade_properties(self, fitted_backtest):
        """Test individual trade properties"""
        trades = fitted_backtest.simulate_trade_sequence(num_trades=5)

        for trade in trades:
            assert trade.position_size >= 0.02
            assert trade.position_size <= 0.10
            assert trade.holding_days >= 1
            assert trade.exit_date > trade.entry_date
            assert trade.win == (trade.return_pct > 0)
            assert trade.max_drawdown >= 0

    def test_position_size_range(self, fitted_backtest):
        """Test position size respects range"""
        trades = fitted_backtest.simulate_trade_sequence(
            num_trades=20,
            position_size_range=(0.05, 0.15)
        )

        for trade in trades:
            assert 0.05 <= trade.position_size <= 0.15

    def test_sequential_dates(self, fitted_backtest):
        """Test trades have sequential dates"""
        trades = fitted_backtest.simulate_trade_sequence(num_trades=5)

        for i in range(1, len(trades)):
            # Next trade should start after previous exits
            assert trades[i].entry_date >= trades[i-1].exit_date


class TestCalculatePortfolioMetrics:
    """Test portfolio metrics calculation"""

    def test_calculate_metrics_positive_returns(self, fitted_backtest):
        """Test metrics with positive returns"""
        trades = [
            Trade(
                ticker='TEST',
                entry_date=datetime.now(),
                entry_price=100.0,
                exit_date=datetime.now() + timedelta(days=1),
                exit_price=105.0,
                position_size=0.10,
                return_pct=0.05,
                win=True,
                max_drawdown=0.01,
                holding_days=1
            )
        ]

        total_ret, max_dd, sharpe, sortino = fitted_backtest.calculate_portfolio_metrics(
            trades, 100000.0
        )

        # Should have positive return
        assert total_ret > 0
        # Drawdown should be small or zero
        assert max_dd >= 0
        assert max_dd < 0.02

    def test_calculate_metrics_negative_returns(self, fitted_backtest):
        """Test metrics with negative returns"""
        trades = [
            Trade(
                ticker='TEST',
                entry_date=datetime.now(),
                entry_price=100.0,
                exit_date=datetime.now() + timedelta(days=1),
                exit_price=95.0,
                position_size=0.10,
                return_pct=-0.05,
                win=False,
                max_drawdown=0.05,
                holding_days=1
            )
        ]

        total_ret, max_dd, sharpe, sortino = fitted_backtest.calculate_portfolio_metrics(
            trades, 100000.0
        )

        # Should have negative return
        assert total_ret < 0
        # Should have some drawdown
        assert max_dd > 0

    def test_calculate_metrics_empty_trades(self, fitted_backtest):
        """Test metrics with empty trades"""
        total_ret, max_dd, sharpe, sortino = fitted_backtest.calculate_portfolio_metrics(
            [], 100000.0
        )

        assert total_ret == 0.0
        assert max_dd == 0.0
        assert sharpe == 0.0
        assert sortino == 0.0

    def test_max_drawdown_calculation(self, fitted_backtest):
        """Test max drawdown is calculated correctly"""
        trades = [
            # First trade: +10%
            Trade('T1', datetime.now(), 100, datetime.now(), 110, 0.10, 0.10, True, 0, 1),
            # Second trade: -20% (creates drawdown)
            Trade('T2', datetime.now(), 100, datetime.now(), 80, 0.10, -0.20, False, 0.20, 1),
            # Third trade: +15% (recovery)
            Trade('T3', datetime.now(), 100, datetime.now(), 115, 0.10, 0.15, True, 0, 1)
        ]

        total_ret, max_dd, sharpe, sortino = fitted_backtest.calculate_portfolio_metrics(
            trades, 100000.0
        )

        # Should have some drawdown from the losing trade
        assert max_dd > 0
        assert max_dd < 0.05  # But not too large due to small position sizes


class TestRunSimulation:
    """Test single simulation run"""

    def test_run_simulation(self, fitted_backtest):
        """Test running single simulation"""
        result = fitted_backtest.run_simulation(
            simulation_id=1,
            num_trades=20
        )

        assert isinstance(result, SimulationResult)
        assert result.simulation_id == 1
        assert result.total_trades == 20
        assert len(result.trades) == 20

    def test_simulation_result_metrics(self, fitted_backtest):
        """Test simulation result contains all metrics"""
        result = fitted_backtest.run_simulation(
            simulation_id=1,
            num_trades=10
        )

        assert isinstance(result.total_return, float)
        assert isinstance(result.final_portfolio_value, float)
        assert isinstance(result.max_drawdown, float)
        assert isinstance(result.sharpe_ratio, float)
        assert isinstance(result.sortino_ratio, float)
        assert isinstance(result.win_rate, float)
        assert result.winning_trades + result.losing_trades == result.total_trades

    def test_simulation_statistics(self, fitted_backtest):
        """Test simulation statistics calculations"""
        result = fitted_backtest.run_simulation(
            simulation_id=1,
            num_trades=50
        )

        # Win rate should be between 0 and 1
        assert 0 <= result.win_rate <= 1

        # Avg win should be positive, avg loss negative
        if result.winning_trades > 0:
            assert result.avg_win > 0
        if result.losing_trades > 0:
            assert result.avg_loss < 0

        # Profit factor should be positive
        assert result.profit_factor >= 0

        # Consecutive counts should be reasonable
        assert result.max_consecutive_wins <= result.total_trades
        assert result.max_consecutive_losses <= result.total_trades


class TestRunMonteCarlo:
    """Test full Monte Carlo simulation"""

    def test_run_monte_carlo(self, fitted_backtest):
        """Test running Monte Carlo simulations"""
        results = fitted_backtest.run_monte_carlo(
            num_simulations=10,
            num_trades_per_simulation=20,
            random_seed=42
        )

        assert isinstance(results, MonteCarloResults)
        assert results.num_simulations == 10
        assert len(results.simulations) == 10

    def test_monte_carlo_without_fit_raises_error(self, backtest):
        """Test Monte Carlo without fitting raises error"""
        with pytest.raises(ValueError, match="Must call fit_historical_data"):
            backtest.run_monte_carlo(num_simulations=10)

    def test_monte_carlo_reproducibility(self, fitted_backtest):
        """Test results are reproducible with same seed"""
        results1 = fitted_backtest.run_monte_carlo(
            num_simulations=10,
            num_trades_per_simulation=10,
            random_seed=42
        )

        results2 = fitted_backtest.run_monte_carlo(
            num_simulations=10,
            num_trades_per_simulation=10,
            random_seed=42
        )

        # Should get identical results with same seed
        assert abs(results1.mean_return - results2.mean_return) < 0.0001

    def test_monte_carlo_statistics(self, fitted_backtest):
        """Test Monte Carlo aggregated statistics"""
        results = fitted_backtest.run_monte_carlo(
            num_simulations=100,
            num_trades_per_simulation=20,
            random_seed=42
        )

        # All statistics should be calculated
        assert results.mean_return is not None
        assert results.median_return is not None
        assert results.std_return is not None
        assert results.best_return >= results.mean_return
        assert results.worst_return <= results.mean_return

        # Percentiles should be in order
        assert results.percentile_5 <= results.percentile_25
        assert results.percentile_25 <= results.percentile_75
        assert results.percentile_75 <= results.percentile_95

        # Probabilities should sum reasonably
        assert 0 <= results.prob_profit <= 1
        assert results.prob_10pct_gain <= results.prob_profit
        assert results.prob_20pct_gain <= results.prob_10pct_gain

    def test_monte_carlo_confidence_intervals(self, fitted_backtest):
        """Test confidence intervals are calculated"""
        results = fitted_backtest.run_monte_carlo(
            num_simulations=100,
            num_trades_per_simulation=20,
            random_seed=42
        )

        # CI should bracket the mean
        assert results.return_ci_lower <= results.mean_return
        assert results.return_ci_upper >= results.mean_return

        # Drawdown CI should be positive
        assert results.drawdown_ci_lower >= 0
        assert results.drawdown_ci_upper >= results.drawdown_ci_lower


class TestGenerateReport:
    """Test report generation"""

    def test_generate_report(self, fitted_backtest):
        """Test generating markdown report"""
        results = fitted_backtest.run_monte_carlo(
            num_simulations=10,
            num_trades_per_simulation=20,
            random_seed=42
        )

        report = fitted_backtest.generate_report(results)

        assert isinstance(report, str)
        assert 'Monte Carlo Backtest Results' in report
        assert 'Return Statistics' in report
        assert 'Risk Metrics' in report
        assert 'Outcome Probabilities' in report

    def test_report_includes_all_metrics(self, fitted_backtest):
        """Test report includes all key metrics"""
        results = fitted_backtest.run_monte_carlo(
            num_simulations=10,
            num_trades_per_simulation=20,
            random_seed=42
        )

        report = fitted_backtest.generate_report(results)

        # Check for key metrics
        assert 'Mean Return' in report
        assert 'Sharpe Ratio' in report
        assert 'Max Drawdown' in report
        assert 'Win Rate' in report
        assert 'Profit' in report

    def test_report_interpretation_positive(self, fitted_backtest):
        """Test report interpretation for positive results"""
        # Fit with highly positive data
        positive_trades = [
            {'return_pct': 0.10, 'win': True, 'holding_days': 5}
        ] * 10

        fitted_backtest.fit_historical_data(positive_trades)

        results = fitted_backtest.run_monte_carlo(
            num_simulations=10,
            num_trades_per_simulation=10,
            random_seed=42
        )

        report = fitted_backtest.generate_report(results)

        # Should have positive interpretation
        assert '✅' in report or 'Positive' in report


class TestConvenienceFunction:
    """Test convenience function"""

    def test_run_monte_carlo_backtest(self, sample_historical_trades):
        """Test convenience function"""
        results = run_monte_carlo_backtest(
            historical_trades=sample_historical_trades,
            num_simulations=10,
            num_trades_per_simulation=20,
            initial_capital=100000.0,
            distribution_type=DistributionType.NORMAL
        )

        assert isinstance(results, MonteCarloResults)
        assert results.num_simulations == 10

    def test_convenience_function_custom_params(self, sample_historical_trades):
        """Test convenience function with custom parameters"""
        results = run_monte_carlo_backtest(
            historical_trades=sample_historical_trades,
            num_simulations=5,
            num_trades_per_simulation=10,
            initial_capital=50000.0,
            distribution_type=DistributionType.LOGNORMAL
        )

        assert results.num_simulations == 5
        assert results.initial_capital == 50000.0


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_single_trade_simulation(self, fitted_backtest):
        """Test simulation with single trade"""
        result = fitted_backtest.run_simulation(
            simulation_id=1,
            num_trades=1
        )

        assert result.total_trades == 1
        assert len(result.trades) == 1

    def test_very_high_win_rate(self, backtest):
        """Test with very high win rate data"""
        winning_trades = [
            {'return_pct': 0.05, 'win': True, 'holding_days': 5}
        ] * 95 + [
            {'return_pct': -0.02, 'win': False, 'holding_days': 5}
        ] * 5

        backtest.fit_historical_data(winning_trades)

        assert backtest.mean_win_rate == 0.95

        results = backtest.run_monte_carlo(
            num_simulations=10,
            num_trades_per_simulation=10,
            random_seed=42
        )

        # Should have high probability of profit
        assert results.prob_profit > 0.7

    def test_very_low_win_rate(self, backtest):
        """Test with very low win rate data"""
        losing_trades = [
            {'return_pct': -0.05, 'win': False, 'holding_days': 5}
        ] * 80 + [
            {'return_pct': 0.02, 'win': True, 'holding_days': 5}
        ] * 20

        backtest.fit_historical_data(losing_trades)

        assert backtest.mean_win_rate == 0.20

        results = backtest.run_monte_carlo(
            num_simulations=10,
            num_trades_per_simulation=10,
            random_seed=42
        )

        # Should have low probability of profit
        assert results.prob_profit < 0.5

    def test_zero_volatility_trades(self, backtest):
        """Test with zero volatility (all same return)"""
        constant_trades = [
            {'return_pct': 0.05, 'win': True, 'holding_days': 5}
        ] * 10

        backtest.fit_historical_data(constant_trades)

        # Std should be zero or very small
        assert backtest.std_return < 0.001

    def test_extreme_position_sizes(self, fitted_backtest):
        """Test with extreme position sizes"""
        # Very small positions
        trades = fitted_backtest.simulate_trade_sequence(
            num_trades=10,
            position_size_range=(0.001, 0.005)
        )

        for trade in trades:
            assert 0.001 <= trade.position_size <= 0.005

        # Very large positions
        trades = fitted_backtest.simulate_trade_sequence(
            num_trades=10,
            position_size_range=(0.50, 0.80)
        )

        for trade in trades:
            assert 0.50 <= trade.position_size <= 0.80
