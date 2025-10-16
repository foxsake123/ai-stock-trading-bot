"""Tests for Summary Table Generator"""

import pytest
from datetime import datetime, timedelta
from reporting.summary_table_generator import (
    SummaryTableGenerator,
    PerformanceMetrics,
    BotComparison,
    generate_executive_summary
)
from unittest.mock import Mock, patch, mock_open
import json
from pathlib import Path


@pytest.fixture
def sample_performance_data():
    """Sample performance history data"""
    records = []
    base_date = datetime(2025, 10, 1)

    for i in range(30):
        date = base_date + timedelta(days=i)
        # Simulate growing portfolio
        dee_value = 100000 + (i * 200)  # Slow growth
        shorgan_value = 100000 + (i * 400)  # Faster growth

        records.append({
            "date": date.strftime('%Y-%m-%d'),
            "timestamp": date.isoformat(),
            "dee_bot": {
                "value": dee_value,
                "daily_pnl": 200,
                "total_return": (dee_value - 100000) / 100000 * 100
            },
            "shorgan_bot": {
                "value": shorgan_value,
                "daily_pnl": 400,
                "total_return": (shorgan_value - 100000) / 100000 * 100
            },
            "combined": {
                "total_value": dee_value + shorgan_value,
                "total_daily_pnl": 600,
                "total_return": ((dee_value + shorgan_value) - 200000) / 200000 * 100,
                "total_positions": 10,
                "total_orders_today": 2
            }
        })

    return {
        "start_date": base_date.isoformat(),
        "daily_records": records
    }


@pytest.fixture
def generator_with_data(sample_performance_data, tmp_path):
    """Create generator with sample data"""
    perf_file = tmp_path / "performance_history.json"

    with open(perf_file, 'w') as f:
        json.dump(sample_performance_data, f)

    return SummaryTableGenerator(str(perf_file))


class TestSummaryTableGeneratorInitialization:
    """Test initialization"""

    def test_initialization_default(self):
        """Test default initialization"""
        generator = SummaryTableGenerator()
        assert generator.performance_file == Path("data/daily/performance/performance_history.json")

    def test_initialization_custom_file(self, tmp_path):
        """Test initialization with custom file"""
        custom_file = tmp_path / "custom.json"
        generator = SummaryTableGenerator(str(custom_file))
        assert generator.performance_file == custom_file


class TestLoadPerformanceData:
    """Test loading performance data"""

    def test_load_existing_file(self, generator_with_data, sample_performance_data):
        """Test loading existing performance file"""
        data = generator_with_data.load_performance_data()

        assert 'daily_records' in data
        assert len(data['daily_records']) == 30

    def test_load_missing_file(self, tmp_path):
        """Test loading when file doesn't exist"""
        missing_file = tmp_path / "nonexistent.json"
        generator = SummaryTableGenerator(str(missing_file))

        data = generator.load_performance_data()

        assert data['daily_records'] == []

    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON file"""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json }")

        generator = SummaryTableGenerator(str(invalid_file))
        data = generator.load_performance_data()

        assert data['daily_records'] == []


class TestSharpeRatioCalculation:
    """Test Sharpe ratio calculation"""

    def test_sharpe_positive_returns(self):
        """Test Sharpe with positive returns"""
        generator = SummaryTableGenerator()
        returns = [0.01, 0.02, 0.015, 0.01, 0.02]  # All positive

        sharpe = generator.calculate_sharpe_ratio(returns)

        assert sharpe > 0

    def test_sharpe_negative_returns(self):
        """Test Sharpe with negative returns"""
        generator = SummaryTableGenerator()
        returns = [-0.01, -0.02, -0.015]  # All negative

        sharpe = generator.calculate_sharpe_ratio(returns)

        assert sharpe < 0

    def test_sharpe_mixed_returns(self):
        """Test Sharpe with mixed returns"""
        generator = SummaryTableGenerator()
        returns = [0.02, -0.01, 0.015, -0.005, 0.01]

        sharpe = generator.calculate_sharpe_ratio(returns)

        assert isinstance(sharpe, float)

    def test_sharpe_empty_returns(self):
        """Test Sharpe with empty returns list"""
        generator = SummaryTableGenerator()
        sharpe = generator.calculate_sharpe_ratio([])

        assert sharpe == 0.0

    def test_sharpe_single_return(self):
        """Test Sharpe with single return"""
        generator = SummaryTableGenerator()
        sharpe = generator.calculate_sharpe_ratio([0.01])

        assert sharpe == 0.0

    def test_sharpe_zero_volatility(self):
        """Test Sharpe when all returns are identical"""
        generator = SummaryTableGenerator()
        returns = [0.01, 0.01, 0.01, 0.01]

        sharpe = generator.calculate_sharpe_ratio(returns)

        assert sharpe == 0.0


class TestMaxDrawdownCalculation:
    """Test maximum drawdown calculation"""

    def test_drawdown_declining_values(self):
        """Test drawdown with declining portfolio"""
        generator = SummaryTableGenerator()
        values = [100000, 95000, 90000, 85000]  # 15% drawdown

        dd = generator.calculate_max_drawdown(values)

        assert dd == pytest.approx(15.0, rel=0.01)

    def test_drawdown_growing_values(self):
        """Test drawdown with growing portfolio"""
        generator = SummaryTableGenerator()
        values = [100000, 105000, 110000, 115000]  # No drawdown

        dd = generator.calculate_max_drawdown(values)

        assert dd == 0.0

    def test_drawdown_with_recovery(self):
        """Test drawdown with decline and recovery"""
        generator = SummaryTableGenerator()
        values = [100000, 90000, 95000, 105000]  # Max DD 10%

        dd = generator.calculate_max_drawdown(values)

        assert dd == pytest.approx(10.0, rel=0.01)

    def test_drawdown_empty_values(self):
        """Test drawdown with empty values"""
        generator = SummaryTableGenerator()
        dd = generator.calculate_max_drawdown([])

        assert dd == 0.0

    def test_drawdown_single_value(self):
        """Test drawdown with single value"""
        generator = SummaryTableGenerator()
        dd = generator.calculate_max_drawdown([100000])

        assert dd == 0.0

    def test_drawdown_multiple_peaks(self):
        """Test drawdown with multiple peaks"""
        generator = SummaryTableGenerator()
        values = [100000, 95000, 105000, 100000, 110000, 105000]

        dd = generator.calculate_max_drawdown(values)

        # Should be 5% from first peak or 4.76% from 105000 peak
        assert dd > 0


class TestPerformanceSummary:
    """Test performance summary generation"""

    def test_generate_summary_combined(self, generator_with_data):
        """Test summary for combined portfolio"""
        metrics = generator_with_data.generate_performance_summary("combined", days=30)

        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.total_return > 0  # Growing portfolio
        assert metrics.sharpe_ratio != 0
        assert metrics.max_drawdown >= 0
        assert metrics.current_positions == 10

    def test_generate_summary_dee_bot(self, generator_with_data):
        """Test summary for DEE-BOT"""
        metrics = generator_with_data.generate_performance_summary("dee_bot", days=30)

        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.total_return >= 0

    def test_generate_summary_shorgan_bot(self, generator_with_data):
        """Test summary for SHORGAN-BOT"""
        metrics = generator_with_data.generate_performance_summary("shorgan_bot", days=30)

        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.total_return >= 0

    def test_generate_summary_custom_days(self, generator_with_data):
        """Test summary with custom day range"""
        metrics_7d = generator_with_data.generate_performance_summary("combined", days=7)
        metrics_30d = generator_with_data.generate_performance_summary("combined", days=30)

        # Both should be valid but may differ
        assert isinstance(metrics_7d, PerformanceMetrics)
        assert isinstance(metrics_30d, PerformanceMetrics)

    def test_generate_summary_no_data(self, tmp_path):
        """Test summary with no performance data"""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text('{"start_date": "2025-10-01", "daily_records": []}')

        generator = SummaryTableGenerator(str(empty_file))
        metrics = generator.generate_performance_summary("combined")

        assert metrics.total_return == 0.0
        assert metrics.sharpe_ratio == 0.0


class TestBotComparison:
    """Test bot comparison functionality"""

    def test_compare_bots(self, generator_with_data):
        """Test comparing all bots"""
        comparisons = generator_with_data.compare_bots()

        assert len(comparisons) == 3  # DEE, SHORGAN, Combined
        assert all(isinstance(c, BotComparison) for c in comparisons)

        # Check ranks are assigned
        ranks = [c.rank for c in comparisons]
        assert sorted(ranks) == [1, 2, 3]

        # Verify sorted by return
        returns = [c.return_pct for c in comparisons]
        assert returns == sorted(returns, reverse=True)

    def test_compare_bots_no_data(self, tmp_path):
        """Test comparison with no data"""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text('{"start_date": "2025-10-01", "daily_records": []}')

        generator = SummaryTableGenerator(str(empty_file))
        comparisons = generator.compare_bots()

        assert comparisons == []

    def test_bot_comparison_fields(self, generator_with_data):
        """Test bot comparison has all fields"""
        comparisons = generator_with_data.compare_bots()

        for comp in comparisons:
            assert hasattr(comp, 'bot_name')
            assert hasattr(comp, 'value')
            assert hasattr(comp, 'return_pct')
            assert hasattr(comp, 'daily_pnl')
            assert hasattr(comp, 'positions')
            assert hasattr(comp, 'rank')


class TestTableGeneration:
    """Test markdown table generation"""

    def test_generate_performance_table(self, generator_with_data):
        """Test performance table generation"""
        table = generator_with_data.generate_performance_table(days=30)

        assert "## Performance Summary" in table
        assert "Total Return" in table
        assert "Sharpe Ratio" in table
        assert "Max Drawdown" in table
        assert "Current Positions" in table

    def test_generate_bot_comparison_table(self, generator_with_data):
        """Test bot comparison table"""
        table = generator_with_data.generate_bot_comparison_table()

        assert "## Bot Performance Comparison" in table
        assert "DEE-BOT" in table
        assert "SHORGAN-BOT" in table
        assert "Combined" in table
        assert "Rank" in table

    def test_generate_key_metrics_table(self, generator_with_data):
        """Test key metrics table"""
        table = generator_with_data.generate_key_metrics_table()

        assert "## Key Metrics" in table
        assert "DEE-BOT" in table
        assert "SHORGAN-BOT" in table
        assert "Better Performer" in table

    def test_generate_full_executive_summary(self, generator_with_data):
        """Test full executive summary"""
        summary = generator_with_data.generate_full_executive_summary()

        assert "# Executive Summary" in summary
        assert "Performance Summary" in summary
        assert "Bot Performance Comparison" in summary
        assert "Key Metrics" in summary
        assert "Quick Decision Aid" in summary

    def test_table_empty_data(self, tmp_path):
        """Test table generation with empty data"""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text('{"start_date": "2025-10-01", "daily_records": []}')

        generator = SummaryTableGenerator(str(empty_file))

        table = generator.generate_bot_comparison_table()
        assert "No performance data available" in table


class TestDecisionAid:
    """Test decision aid generation"""

    def test_decision_aid_positive_performance(self, generator_with_data):
        """Test decision aid with positive performance"""
        aid = generator_with_data._generate_decision_aid()

        assert "Quick Decision Aid" in aid
        assert "Recommendations" in aid
        # Should show green/positive status for growing portfolio
        assert "[GREEN]" in aid or "[YELLOW]" in aid

    def test_decision_aid_no_data(self, tmp_path):
        """Test decision aid with no data"""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text('{"start_date": "2025-10-01", "daily_records": []}')

        generator = SummaryTableGenerator(str(empty_file))
        aid = generator._generate_decision_aid()

        assert "Insufficient data" in aid


class TestConvenienceFunction:
    """Test convenience function"""

    @patch('reporting.summary_table_generator.SummaryTableGenerator.load_performance_data')
    def test_generate_executive_summary(self, mock_load):
        """Test convenience function"""
        # Mock data
        mock_load.return_value = {
            "start_date": "2025-10-01",
            "daily_records": [
                {
                    "date": "2025-10-15",
                    "combined": {
                        "total_value": 210000,
                        "total_return": 5.0,
                        "total_daily_pnl": 500,
                        "total_positions": 8
                    },
                    "dee_bot": {
                        "value": 105000,
                        "total_return": 5.0,
                        "daily_pnl": 250
                    },
                    "shorgan_bot": {
                        "value": 105000,
                        "total_return": 5.0,
                        "daily_pnl": 250
                    }
                }
            ]
        }

        summary = generate_executive_summary()

        assert "# Executive Summary" in summary
        assert isinstance(summary, str)


class TestQualityIndicators:
    """Test quality indicator generation in tables"""

    def test_sharpe_quality_indicators(self, generator_with_data):
        """Test Sharpe ratio quality indicators"""
        table = generator_with_data.generate_performance_table(days=30)

        # Should have quality indicator text
        assert "Quality Indicators" in table
        assert "Sharpe Ratio:" in table

    def test_drawdown_quality_indicators(self, generator_with_data):
        """Test drawdown quality indicators"""
        table = generator_with_data.generate_performance_table(days=30)

        assert "Drawdown:" in table


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_zero_starting_value(self, tmp_path):
        """Test with zero starting value"""
        data = {
            "start_date": "2025-10-01",
            "daily_records": [
                {
                    "date": "2025-10-15",
                    "combined": {"total_value": 0, "total_return": 0}
                }
            ]
        }

        perf_file = tmp_path / "zero.json"
        with open(perf_file, 'w') as f:
            json.dump(data, f)

        generator = SummaryTableGenerator(str(perf_file))
        metrics = generator.generate_performance_summary("combined")

        assert metrics.total_return == 0.0

    def test_single_day_data(self, tmp_path):
        """Test with only one day of data"""
        data = {
            "start_date": "2025-10-15",
            "daily_records": [
                {
                    "date": "2025-10-15",
                    "combined": {"total_value": 100000, "total_return": 0}
                }
            ]
        }

        perf_file = tmp_path / "single.json"
        with open(perf_file, 'w') as f:
            json.dump(data, f)

        generator = SummaryTableGenerator(str(perf_file))
        metrics = generator.generate_performance_summary("combined")

        # Should handle gracefully
        assert isinstance(metrics, PerformanceMetrics)
