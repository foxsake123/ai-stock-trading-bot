"""Tests for Portfolio Attribution Analysis"""

import pytest
from datetime import datetime, timedelta
from performance.portfolio_attribution import (
    PortfolioAttributionAnalyzer,
    TradeAttribution,
    AttributionBreakdown,
    PortfolioAttribution,
    analyze_portfolio_attribution
)


@pytest.fixture
def sample_trades():
    """Sample trades for testing"""
    base_date = datetime(2025, 1, 1)

    return [
        {
            'ticker': 'AAPL',
            'entry_date': base_date,
            'exit_date': base_date + timedelta(days=7),
            'return_pct': 0.05,
            'pnl': 500.0,
            'position_size': 0.10,
            'sector': 'Technology',
            'strategy': 'momentum',
            'agent_recommendation': 'TechnicalAnalyst',
            'market_condition': 'bull',
            'catalyst_type': None,
            'vs_spy': 0.02,
            'vs_sector': 0.01
        },
        {
            'ticker': 'JNJ',
            'entry_date': base_date + timedelta(days=7),
            'exit_date': base_date + timedelta(days=14),
            'return_pct': 0.03,
            'pnl': 300.0,
            'position_size': 0.10,
            'sector': 'Healthcare',
            'strategy': 'value',
            'agent_recommendation': 'FundamentalAnalyst',
            'market_condition': 'bull',
            'catalyst_type': None,
            'vs_spy': 0.01,
            'vs_sector': 0.005
        },
        {
            'ticker': 'PTGX',
            'entry_date': base_date + timedelta(days=14),
            'exit_date': base_date + timedelta(days=21),
            'return_pct': 0.15,
            'pnl': 1500.0,
            'position_size': 0.10,
            'sector': 'Biotech',
            'strategy': 'catalyst',
            'agent_recommendation': 'CatalystAgent',
            'market_condition': 'sideways',
            'catalyst_type': 'M&A',
            'vs_spy': 0.12,
            'vs_sector': 0.10
        },
        {
            'ticker': 'TSLA',
            'entry_date': base_date + timedelta(days=21),
            'exit_date': base_date + timedelta(days=28),
            'return_pct': -0.08,
            'pnl': -800.0,
            'position_size': 0.10,
            'sector': 'Technology',
            'strategy': 'momentum',
            'agent_recommendation': 'TechnicalAnalyst',
            'market_condition': 'bear',
            'catalyst_type': None,
            'vs_spy': -0.05,
            'vs_sector': -0.03
        },
        {
            'ticker': 'GKOS',
            'entry_date': base_date + timedelta(days=28),
            'exit_date': base_date + timedelta(days=35),
            'return_pct': 0.10,
            'pnl': 1000.0,
            'position_size': 0.10,
            'sector': 'Biotech',
            'strategy': 'catalyst',
            'agent_recommendation': 'CatalystAgent',
            'market_condition': 'bull',
            'catalyst_type': 'FDA',
            'vs_spy': 0.08,
            'vs_sector': 0.07
        }
    ]


@pytest.fixture
def analyzer():
    """Create analyzer instance"""
    return PortfolioAttributionAnalyzer()


@pytest.fixture
def populated_analyzer(analyzer, sample_trades):
    """Analyzer populated with sample trades"""
    for trade in sample_trades:
        analyzer.add_trade(**trade)
    return analyzer


class TestPortfolioAttributionAnalyzerInitialization:
    """Test analyzer initialization"""

    def test_initialization(self):
        """Test default initialization"""
        analyzer = PortfolioAttributionAnalyzer()

        assert isinstance(analyzer.trades, list)
        assert len(analyzer.trades) == 0


class TestAddTrade:
    """Test adding trades"""

    def test_add_single_trade(self, analyzer):
        """Test adding single trade"""
        analyzer.add_trade(
            ticker='AAPL',
            entry_date=datetime(2025, 1, 1),
            exit_date=datetime(2025, 1, 8),
            return_pct=0.05,
            pnl=500.0,
            position_size=0.10,
            sector='Technology',
            strategy='momentum'
        )

        assert len(analyzer.trades) == 1
        assert analyzer.trades[0].ticker == 'AAPL'
        assert analyzer.trades[0].sector == 'Technology'

    def test_add_multiple_trades(self, analyzer):
        """Test adding multiple trades"""
        for i in range(5):
            analyzer.add_trade(
                ticker=f'STOCK{i}',
                entry_date=datetime(2025, 1, 1),
                exit_date=datetime(2025, 1, 8),
                return_pct=0.05,
                pnl=100.0,
                position_size=0.05
            )

        assert len(analyzer.trades) == 5

    def test_trade_calculates_holding_days(self, analyzer):
        """Test holding days are calculated"""
        analyzer.add_trade(
            ticker='AAPL',
            entry_date=datetime(2025, 1, 1),
            exit_date=datetime(2025, 1, 8),
            return_pct=0.05,
            pnl=500.0,
            position_size=0.10
        )

        assert analyzer.trades[0].holding_days == 7

    def test_trade_determines_win_loss(self, analyzer):
        """Test win/loss is determined from return"""
        # Winning trade
        analyzer.add_trade(
            ticker='WIN',
            entry_date=datetime(2025, 1, 1),
            exit_date=datetime(2025, 1, 8),
            return_pct=0.05,
            pnl=500.0,
            position_size=0.10
        )

        # Losing trade
        analyzer.add_trade(
            ticker='LOSS',
            entry_date=datetime(2025, 1, 1),
            exit_date=datetime(2025, 1, 8),
            return_pct=-0.03,
            pnl=-300.0,
            position_size=0.10
        )

        assert analyzer.trades[0].win is True
        assert analyzer.trades[1].win is False


class TestCalculateAttributionByFactor:
    """Test attribution calculation by factor"""

    def test_attribution_by_sector(self, populated_analyzer):
        """Test calculating attribution by sector"""
        breakdown = populated_analyzer.calculate_attribution_by_factor(
            "sector",
            lambda t: t.sector
        )

        assert isinstance(breakdown, AttributionBreakdown)
        assert breakdown.factor_name == "sector"
        assert "Technology" in breakdown.factor_values
        assert "Healthcare" in breakdown.factor_values
        assert "Biotech" in breakdown.factor_values

    def test_attribution_by_strategy(self, populated_analyzer):
        """Test calculating attribution by strategy"""
        breakdown = populated_analyzer.calculate_attribution_by_factor(
            "strategy",
            lambda t: t.strategy
        )

        assert "momentum" in breakdown.factor_values
        assert "value" in breakdown.factor_values
        assert "catalyst" in breakdown.factor_values

    def test_attribution_best_worst(self, populated_analyzer):
        """Test best and worst performers identified"""
        breakdown = populated_analyzer.calculate_attribution_by_factor(
            "strategy",
            lambda t: t.strategy
        )

        # Catalyst strategy should be best (PTGX +1500, GKOS +1000 = 2500)
        assert breakdown.best_performer == "catalyst"

        # Momentum should be worst (AAPL +500, TSLA -800 = -300)
        assert breakdown.worst_performer == "momentum"

    def test_attribution_counts(self, populated_analyzer):
        """Test trade counts per factor"""
        breakdown = populated_analyzer.calculate_attribution_by_factor(
            "sector",
            lambda t: t.sector
        )

        # Technology: AAPL, TSLA = 2
        assert breakdown.count_by_value["Technology"] == 2

        # Healthcare: JNJ = 1
        assert breakdown.count_by_value["Healthcare"] == 1

        # Biotech: PTGX, GKOS = 2
        assert breakdown.count_by_value["Biotech"] == 2

    def test_attribution_empty_factor(self, analyzer):
        """Test attribution with no trades"""
        breakdown = analyzer.calculate_attribution_by_factor(
            "sector",
            lambda t: t.sector
        )

        assert breakdown.best_performer == "N/A"
        assert breakdown.worst_performer == "N/A"
        assert breakdown.total_contribution == 0.0


class TestCalculateTimeAttribution:
    """Test time-based attribution"""

    def test_monthly_attribution(self, populated_analyzer):
        """Test monthly attribution calculation"""
        monthly = populated_analyzer.calculate_time_attribution("monthly")

        assert isinstance(monthly, dict)
        assert "2025-01" in monthly or "2025-02" in monthly

        # Some trades may be in January, some in February depending on dates
        total_pnl = sum(monthly.values())
        assert total_pnl == 2500.0

    def test_weekly_attribution(self, populated_analyzer):
        """Test weekly attribution calculation"""
        weekly = populated_analyzer.calculate_time_attribution("weekly")

        assert isinstance(weekly, dict)
        # Should have multiple weeks
        assert len(weekly) >= 1

    def test_invalid_period_raises_error(self, populated_analyzer):
        """Test invalid period raises error"""
        with pytest.raises(ValueError, match="Unknown period"):
            populated_analyzer.calculate_time_attribution("daily")


class TestAnalyze:
    """Test full attribution analysis"""

    def test_analyze_all_trades(self, populated_analyzer):
        """Test analyzing all trades"""
        result = populated_analyzer.analyze()

        assert isinstance(result, PortfolioAttribution)
        assert result.num_trades == 5
        assert result.total_pnl == 2500.0

    def test_analyze_calculates_all_breakdowns(self, populated_analyzer):
        """Test all breakdowns are calculated"""
        result = populated_analyzer.analyze()

        assert isinstance(result.by_sector, AttributionBreakdown)
        assert isinstance(result.by_strategy, AttributionBreakdown)
        assert isinstance(result.by_agent, AttributionBreakdown)
        assert isinstance(result.by_market_condition, AttributionBreakdown)
        assert isinstance(result.by_catalyst_type, AttributionBreakdown)

    def test_analyze_with_date_filter(self, populated_analyzer):
        """Test analyzing with date filters"""
        # Only first trade (through Jan 7)
        result = populated_analyzer.analyze(
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 8)
        )

        assert result.num_trades == 1
        # AAPL (500)
        assert result.total_pnl == 500.0

    def test_analyze_empty_trades_raises_error(self, analyzer):
        """Test analyzing with no trades raises error"""
        with pytest.raises(ValueError, match="No trades to analyze"):
            analyzer.analyze()

    def test_analyze_no_trades_in_range_raises_error(self, populated_analyzer):
        """Test analyzing with no trades in range raises error"""
        with pytest.raises(ValueError, match="No trades in specified date range"):
            populated_analyzer.analyze(
                start_date=datetime(2026, 1, 1),
                end_date=datetime(2026, 12, 31)
            )

    def test_analyze_calculates_alpha(self, populated_analyzer):
        """Test alpha calculation"""
        result = populated_analyzer.analyze()

        # Should calculate alpha vs SPY and sectors
        assert isinstance(result.total_alpha_vs_spy, float)
        assert isinstance(result.total_alpha_vs_sectors, float)

    def test_analyze_calculates_total_return(self, populated_analyzer):
        """Test total return calculation"""
        result = populated_analyzer.analyze()

        # Weighted average return: (0.05 + 0.03 + 0.15 - 0.08 + 0.10) * 0.10 / (0.10 * 5)
        expected_return = 0.05  # (0.25 / 5)
        assert abs(result.total_return - expected_return) < 0.001


class TestGenerateReport:
    """Test report generation"""

    def test_generate_report(self, populated_analyzer):
        """Test generating attribution report"""
        result = populated_analyzer.analyze()
        report = populated_analyzer.generate_report(result)

        assert isinstance(report, str)
        assert "Portfolio Attribution Analysis" in report
        assert "Total Trades" in report
        assert "Total P&L" in report

    def test_report_includes_all_breakdowns(self, populated_analyzer):
        """Test report includes all attribution breakdowns"""
        result = populated_analyzer.analyze()
        report = populated_analyzer.generate_report(result)

        assert "Attribution by Sector" in report
        assert "Attribution by Strategy" in report
        assert "Attribution by Agent" in report
        assert ("Attribution by Market_condition" in report or "Attribution by Market_Condition" in report)
        assert ("Attribution by Catalyst_type" in report or "Attribution by Catalyst_Type" in report)

    def test_report_includes_monthly(self, populated_analyzer):
        """Test report includes monthly attribution"""
        result = populated_analyzer.analyze()
        report = populated_analyzer.generate_report(result)

        assert "Monthly Attribution" in report
        assert "2025-01" in report

    def test_report_includes_key_insights(self, populated_analyzer):
        """Test report includes key insights"""
        result = populated_analyzer.analyze()
        report = populated_analyzer.generate_report(result)

        assert "Key Insights" in report
        assert "Top Sector" in report
        assert "Top Strategy" in report
        assert "Top Agent" in report


class TestGetTopContributors:
    """Test getting top contributors"""

    def test_get_top_sector_contributors(self, populated_analyzer):
        """Test getting top sector contributors"""
        top = populated_analyzer.get_top_contributors("sector", top_n=3)

        assert isinstance(top, list)
        assert len(top) == 3

        # Biotech should be top (PTGX 1500 + GKOS 1000 = 2500)
        assert top[0][0] == "Biotech"
        assert top[0][1] == 2500.0

    def test_get_top_strategy_contributors(self, populated_analyzer):
        """Test getting top strategy contributors"""
        top = populated_analyzer.get_top_contributors("strategy", top_n=2)

        assert len(top) == 2

        # Catalyst should be top (PTGX 1500 + GKOS 1000 = 2500)
        assert top[0][0] == "catalyst"

    def test_get_top_with_limit(self, populated_analyzer):
        """Test top N limit is respected"""
        top = populated_analyzer.get_top_contributors("sector", top_n=1)

        assert len(top) == 1

    def test_get_top_invalid_factor_raises_error(self, populated_analyzer):
        """Test invalid factor raises error"""
        with pytest.raises(ValueError, match="Unknown factor"):
            populated_analyzer.get_top_contributors("invalid", top_n=5)


class TestCompareFactors:
    """Test comparing factors"""

    def test_compare_sector_vs_strategy(self, populated_analyzer):
        """Test comparing two factors"""
        comparison = populated_analyzer.compare_factors("sector", "strategy")

        assert comparison["factor1"] == "sector"
        assert comparison["factor2"] == "strategy"
        assert "winner" in comparison
        assert "difference" in comparison

    def test_comparison_identifies_winner(self, populated_analyzer):
        """Test comparison identifies better performer"""
        comparison = populated_analyzer.compare_factors("sector", "strategy")

        # Both have Biotech/catalyst at 2500, should tie or pick one
        assert comparison["winner"] in ["sector", "strategy"]

    def test_comparison_calculates_difference(self, populated_analyzer):
        """Test comparison calculates difference"""
        comparison = populated_analyzer.compare_factors("sector", "strategy")

        assert isinstance(comparison["difference"], float)
        assert comparison["difference"] >= 0


class TestConvenienceFunction:
    """Test convenience function"""

    def test_analyze_portfolio_attribution(self, sample_trades):
        """Test convenience function"""
        result = analyze_portfolio_attribution(sample_trades)

        assert isinstance(result, PortfolioAttribution)
        assert result.num_trades == 5

    def test_convenience_function_with_date_filter(self, sample_trades):
        """Test convenience function with date filters"""
        result = analyze_portfolio_attribution(
            sample_trades,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 22)
        )

        # AAPL (Jan 8), JNJ (Jan 15), PTGX (Jan 22) = 3 trades
        assert result.num_trades == 3


class TestEdgeCases:
    """Test edge cases"""

    def test_single_trade_analysis(self, analyzer):
        """Test analysis with single trade"""
        analyzer.add_trade(
            ticker='AAPL',
            entry_date=datetime(2025, 1, 1),
            exit_date=datetime(2025, 1, 8),
            return_pct=0.05,
            pnl=500.0,
            position_size=0.10,
            sector='Technology'
        )

        result = analyzer.analyze()

        assert result.num_trades == 1
        assert result.total_pnl == 500.0

    def test_all_winning_trades(self, analyzer):
        """Test with all winning trades"""
        for i in range(5):
            analyzer.add_trade(
                ticker=f'WIN{i}',
                entry_date=datetime(2025, 1, 1),
                exit_date=datetime(2025, 1, 8),
                return_pct=0.05,
                pnl=500.0,
                position_size=0.10,
                sector='Technology'
            )

        result = analyzer.analyze()

        assert result.total_pnl == 2500.0
        assert all(t.win for t in result.trades)

    def test_all_losing_trades(self, analyzer):
        """Test with all losing trades"""
        for i in range(5):
            analyzer.add_trade(
                ticker=f'LOSS{i}',
                entry_date=datetime(2025, 1, 1),
                exit_date=datetime(2025, 1, 8),
                return_pct=-0.05,
                pnl=-500.0,
                position_size=0.10,
                sector='Technology'
            )

        result = analyzer.analyze()

        assert result.total_pnl == -2500.0
        assert all(not t.win for t in result.trades)

    def test_trades_without_optional_fields(self, analyzer):
        """Test trades with minimal fields"""
        analyzer.add_trade(
            ticker='AAPL',
            entry_date=datetime(2025, 1, 1),
            exit_date=datetime(2025, 1, 8),
            return_pct=0.05,
            pnl=500.0,
            position_size=0.10
        )

        result = analyzer.analyze()

        assert result.num_trades == 1
        # Should handle None values gracefully

    def test_zero_pnl_trades(self, analyzer):
        """Test with breakeven trades"""
        analyzer.add_trade(
            ticker='EVEN',
            entry_date=datetime(2025, 1, 1),
            exit_date=datetime(2025, 1, 8),
            return_pct=0.0,
            pnl=0.0,
            position_size=0.10,
            sector='Technology'
        )

        result = analyzer.analyze()

        assert result.total_pnl == 0.0
        assert result.trades[0].win is False  # 0% return is not a win

    def test_mixed_sectors_and_strategies(self, analyzer):
        """Test with varied sectors and strategies"""
        sectors = ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer']
        strategies = ['momentum', 'value', 'catalyst', 'arbitrage', 'pairs']

        for i, (sector, strategy) in enumerate(zip(sectors, strategies)):
            analyzer.add_trade(
                ticker=f'STOCK{i}',
                entry_date=datetime(2025, 1, 1),
                exit_date=datetime(2025, 1, 8),
                return_pct=0.05,
                pnl=500.0,
                position_size=0.10,
                sector=sector,
                strategy=strategy
            )

        result = analyzer.analyze()

        # All 5 sectors and strategies should appear
        assert len(result.by_sector.factor_values) == 5
        assert len(result.by_strategy.factor_values) == 5
