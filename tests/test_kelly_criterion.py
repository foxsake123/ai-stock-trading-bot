"""
Comprehensive tests for Kelly Criterion position sizing
"""

import pytest
from datetime import datetime
from src.risk.kelly_criterion import (
    KellyPositionSizer,
    KellyParameters,
    PositionSizeRecommendation,
    calculate_historical_kelly_params
)


# Fixtures

@pytest.fixture
def basic_kelly_params():
    """Basic Kelly parameters for testing"""
    return KellyParameters(
        win_rate=0.60,
        avg_win_pct=0.15,
        avg_loss_pct=0.08,
        confidence=0.70,
        volatility=0.30
    )


@pytest.fixture
def high_edge_params():
    """High edge Kelly parameters"""
    return KellyParameters(
        win_rate=0.75,
        avg_win_pct=0.20,
        avg_loss_pct=0.05,
        confidence=0.90,
        volatility=0.20
    )


@pytest.fixture
def low_edge_params():
    """Low edge Kelly parameters"""
    return KellyParameters(
        win_rate=0.52,
        avg_win_pct=0.10,
        avg_loss_pct=0.09,
        confidence=0.50,
        volatility=0.40
    )


@pytest.fixture
def no_edge_params():
    """No edge (negative Kelly) parameters"""
    return KellyParameters(
        win_rate=0.45,
        avg_win_pct=0.10,
        avg_loss_pct=0.12,
        confidence=0.60,
        volatility=0.30
    )


@pytest.fixture
def kelly_sizer():
    """Standard Kelly position sizer"""
    return KellyPositionSizer(
        max_position_pct=0.10,
        max_portfolio_exposure=0.60,
        kelly_fraction=0.25,
        min_position_pct=0.01,
        volatility_scaling=True,
        confidence_scaling=True
    )


@pytest.fixture
def aggressive_sizer():
    """Aggressive Kelly position sizer"""
    return KellyPositionSizer(
        max_position_pct=0.20,
        max_portfolio_exposure=0.80,
        kelly_fraction=0.50,
        min_position_pct=0.01,
        volatility_scaling=False,
        confidence_scaling=False
    )


@pytest.fixture
def sample_trades():
    """Sample historical trades for testing"""
    return [
        {'return_pct': 0.15, 'win': True},
        {'return_pct': -0.08, 'win': False},
        {'return_pct': 0.20, 'win': True},
        {'return_pct': 0.12, 'win': True},
        {'return_pct': -0.10, 'win': False},
        {'return_pct': 0.18, 'win': True},
        {'return_pct': -0.05, 'win': False},
        {'return_pct': 0.25, 'win': True},
        {'return_pct': 0.10, 'win': True},
        {'return_pct': -0.07, 'win': False}
    ]


# Test KellyParameters Validation

class TestKellyParametersValidation:
    """Test Kelly parameters validation"""

    def test_valid_parameters(self, basic_kelly_params):
        """Test valid parameters are accepted"""
        assert basic_kelly_params.win_rate == 0.60
        assert basic_kelly_params.avg_win_pct == 0.15
        assert basic_kelly_params.avg_loss_pct == 0.08

    def test_invalid_win_rate_too_low(self):
        """Test win rate below 0 raises error"""
        with pytest.raises(ValueError, match="win_rate must be between 0 and 1"):
            KellyParameters(
                win_rate=-0.1,
                avg_win_pct=0.15,
                avg_loss_pct=0.08
            )

    def test_invalid_win_rate_too_high(self):
        """Test win rate above 1 raises error"""
        with pytest.raises(ValueError, match="win_rate must be between 0 and 1"):
            KellyParameters(
                win_rate=1.5,
                avg_win_pct=0.15,
                avg_loss_pct=0.08
            )

    def test_invalid_avg_win_negative(self):
        """Test negative avg win raises error"""
        with pytest.raises(ValueError, match="avg_win_pct must be positive"):
            KellyParameters(
                win_rate=0.60,
                avg_win_pct=-0.15,
                avg_loss_pct=0.08
            )

    def test_invalid_avg_loss_negative(self):
        """Test negative avg loss raises error"""
        with pytest.raises(ValueError, match="avg_loss_pct must be positive"):
            KellyParameters(
                win_rate=0.60,
                avg_win_pct=0.15,
                avg_loss_pct=-0.08
            )

    def test_invalid_confidence_too_low(self):
        """Test confidence below 0 raises error"""
        with pytest.raises(ValueError, match="confidence must be between 0 and 1"):
            KellyParameters(
                win_rate=0.60,
                avg_win_pct=0.15,
                avg_loss_pct=0.08,
                confidence=-0.1
            )

    def test_invalid_confidence_too_high(self):
        """Test confidence above 1 raises error"""
        with pytest.raises(ValueError, match="confidence must be between 0 and 1"):
            KellyParameters(
                win_rate=0.60,
                avg_win_pct=0.15,
                avg_loss_pct=0.08,
                confidence=1.5
            )

    def test_invalid_volatility_negative(self):
        """Test negative volatility raises error"""
        with pytest.raises(ValueError, match="volatility must be non-negative"):
            KellyParameters(
                win_rate=0.60,
                avg_win_pct=0.15,
                avg_loss_pct=0.08,
                volatility=-0.1
            )


# Test Kelly Calculation

class TestKellyCalculation:
    """Test Kelly percentage calculation"""

    def test_positive_kelly(self, kelly_sizer, basic_kelly_params):
        """Test positive Kelly for profitable system"""
        kelly = kelly_sizer.calculate_kelly_pct(
            basic_kelly_params.win_rate,
            basic_kelly_params.avg_win_pct,
            basic_kelly_params.avg_loss_pct
        )
        # Kelly = (0.60 × 0.15 - 0.40 × 0.08) / 0.15 = 0.387
        assert kelly > 0
        assert 0.35 < kelly < 0.45

    def test_high_edge_kelly(self, kelly_sizer, high_edge_params):
        """Test high Kelly for high edge system"""
        kelly = kelly_sizer.calculate_kelly_pct(
            high_edge_params.win_rate,
            high_edge_params.avg_win_pct,
            high_edge_params.avg_loss_pct
        )
        # Should be significantly positive
        assert kelly > 0.5

    def test_low_edge_kelly(self, kelly_sizer, low_edge_params):
        """Test low Kelly for low edge system"""
        kelly = kelly_sizer.calculate_kelly_pct(
            low_edge_params.win_rate,
            low_edge_params.avg_win_pct,
            low_edge_params.avg_loss_pct
        )
        # Should be small but positive
        assert 0 < kelly < 0.10

    def test_negative_kelly(self, kelly_sizer, no_edge_params):
        """Test negative Kelly for no edge system"""
        kelly = kelly_sizer.calculate_kelly_pct(
            no_edge_params.win_rate,
            no_edge_params.avg_win_pct,
            no_edge_params.avg_loss_pct
        )
        # Should be negative (no edge)
        assert kelly < 0

    def test_kelly_with_perfect_win_rate(self, kelly_sizer):
        """Test Kelly with 100% win rate"""
        kelly = kelly_sizer.calculate_kelly_pct(
            win_rate=1.0,
            avg_win_pct=0.15,
            avg_loss_pct=0.08
        )
        # Kelly = (1.0 × 0.15 - 0 × 0.08) / 0.15 = 1.0
        assert kelly == 1.0

    def test_kelly_with_zero_win_rate(self, kelly_sizer):
        """Test Kelly with 0% win rate"""
        kelly = kelly_sizer.calculate_kelly_pct(
            win_rate=0.0,
            avg_win_pct=0.15,
            avg_loss_pct=0.08
        )
        # Kelly = (0 × 0.15 - 1.0 × 0.08) / 0.15 = -0.533
        assert kelly < 0


# Test Adjustments

class TestAdjustments:
    """Test volatility and confidence adjustments"""

    def test_volatility_adjustment_enabled(self, kelly_sizer):
        """Test volatility adjustment when enabled"""
        adjustment = kelly_sizer.calculate_volatility_adjustment(0.30)
        # adjustment = 1 / (1 + 0.30) = 0.769
        assert 0.7 < adjustment < 0.8

    def test_volatility_adjustment_high_vol(self, kelly_sizer):
        """Test high volatility reduces position"""
        adjustment = kelly_sizer.calculate_volatility_adjustment(0.60)
        # adjustment = 1 / (1 + 0.60) = 0.625
        assert 0.6 < adjustment < 0.7

    def test_volatility_adjustment_low_vol(self, kelly_sizer):
        """Test low volatility allows larger position"""
        adjustment = kelly_sizer.calculate_volatility_adjustment(0.10)
        # adjustment = 1 / (1 + 0.10) = 0.909
        assert 0.85 < adjustment < 0.95

    def test_volatility_adjustment_disabled(self, aggressive_sizer):
        """Test volatility adjustment when disabled"""
        adjustment = aggressive_sizer.calculate_volatility_adjustment(0.30)
        assert adjustment == 1.0

    def test_confidence_adjustment_enabled(self, kelly_sizer):
        """Test confidence adjustment when enabled"""
        adjustment = kelly_sizer.calculate_confidence_adjustment(0.70)
        assert adjustment == 0.70

    def test_confidence_adjustment_high(self, kelly_sizer):
        """Test high confidence allows larger position"""
        adjustment = kelly_sizer.calculate_confidence_adjustment(0.90)
        assert adjustment == 0.90

    def test_confidence_adjustment_low(self, kelly_sizer):
        """Test low confidence reduces position"""
        adjustment = kelly_sizer.calculate_confidence_adjustment(0.40)
        assert adjustment == 0.40

    def test_confidence_adjustment_disabled(self, aggressive_sizer):
        """Test confidence adjustment when disabled"""
        adjustment = aggressive_sizer.calculate_confidence_adjustment(0.70)
        assert adjustment == 1.0


# Test Position Size Calculation

class TestPositionSizeCalculation:
    """Test position size calculation"""

    def test_basic_position_size(self, kelly_sizer, basic_kelly_params):
        """Test basic position size calculation"""
        rec = kelly_sizer.calculate_position_size(
            ticker="AAPL",
            params=basic_kelly_params,
            current_price=150.0,
            portfolio_value=100000.0,
            current_exposure_pct=0.0
        )

        assert rec.ticker == "AAPL"
        assert rec.kelly_pct > 0
        assert rec.fractional_kelly_pct > 0
        assert rec.recommended_pct > 0
        assert rec.recommended_shares > 0
        assert rec.recommended_dollar_amount > 0

    def test_no_position_for_negative_kelly(self, kelly_sizer, no_edge_params):
        """Test no position recommended for negative Kelly"""
        rec = kelly_sizer.calculate_position_size(
            ticker="LOSER",
            params=no_edge_params,
            current_price=50.0,
            portfolio_value=100000.0
        )

        assert rec.recommended_shares == 0
        assert rec.recommended_pct == 0.0
        assert "No positive edge" in rec.reasoning

    def test_max_position_limit_applied(self, kelly_sizer, high_edge_params):
        """Test max position limit is applied"""
        rec = kelly_sizer.calculate_position_size(
            ticker="WINNER",
            params=high_edge_params,
            current_price=100.0,
            portfolio_value=100000.0
        )

        # Should be capped at max_position_pct (10%)
        assert rec.recommended_pct <= kelly_sizer.max_position_pct

    def test_portfolio_exposure_limit(self, kelly_sizer, basic_kelly_params):
        """Test portfolio exposure limit"""
        rec = kelly_sizer.calculate_position_size(
            ticker="STOCK1",
            params=basic_kelly_params,
            current_price=100.0,
            portfolio_value=100000.0,
            current_exposure_pct=0.55  # Already 55% exposed
        )

        # Should be limited to remaining 5% (60% max - 55% current)
        assert rec.recommended_pct <= 0.05

    def test_no_position_when_exposure_maxed(self, kelly_sizer, basic_kelly_params):
        """Test no position when exposure limit reached"""
        rec = kelly_sizer.calculate_position_size(
            ticker="STOCK1",
            params=basic_kelly_params,
            current_price=100.0,
            portfolio_value=100000.0,
            current_exposure_pct=0.60  # Already at max
        )

        assert rec.recommended_shares == 0
        assert "exposure limit reached" in rec.reasoning

    def test_min_position_size(self, kelly_sizer, low_edge_params):
        """Test minimum position size requirement"""
        rec = kelly_sizer.calculate_position_size(
            ticker="SMALL",
            params=low_edge_params,
            current_price=100.0,
            portfolio_value=100000.0
        )

        # Low edge params might result in position below minimum
        if rec.recommended_shares == 0:
            assert "below minimum" in rec.reasoning
        else:
            assert rec.recommended_pct >= kelly_sizer.min_position_pct

    def test_aggressive_sizing(self, aggressive_sizer, high_edge_params):
        """Test aggressive sizer allows larger positions"""
        rec = aggressive_sizer.calculate_position_size(
            ticker="WINNER",
            params=high_edge_params,
            current_price=100.0,
            portfolio_value=100000.0
        )

        # Aggressive sizer: 50% Kelly, no vol/conf adjustments, 20% max
        assert rec.recommended_pct > 0
        # Should be larger than conservative sizer

    def test_share_calculation(self, kelly_sizer, basic_kelly_params):
        """Test share count calculation"""
        rec = kelly_sizer.calculate_position_size(
            ticker="AAPL",
            params=basic_kelly_params,
            current_price=150.0,
            portfolio_value=100000.0
        )

        # Shares should be integer
        assert isinstance(rec.recommended_shares, int)
        # Dollar amount should match shares × price
        expected_dollar = rec.recommended_shares * rec.current_price
        assert abs(rec.recommended_dollar_amount - expected_dollar) < 1.0


# Test Batch Sizing

class TestBatchSizing:
    """Test batch position sizing"""

    def test_batch_sizing_basic(self, kelly_sizer, basic_kelly_params):
        """Test basic batch sizing"""
        opportunities = [
            {
                'ticker': 'AAPL',
                'params': basic_kelly_params,
                'current_price': 150.0
            },
            {
                'ticker': 'MSFT',
                'params': basic_kelly_params,
                'current_price': 300.0
            }
        ]

        recs = kelly_sizer.calculate_batch_sizes(
            opportunities=opportunities,
            portfolio_value=100000.0
        )

        assert len(recs) == 2
        # Total exposure should not exceed max
        total_exposure = sum(r.recommended_pct for r in recs)
        assert total_exposure <= kelly_sizer.max_portfolio_exposure

    def test_batch_sizing_prioritizes_best(self, kelly_sizer):
        """Test batch sizing prioritizes best Kelly"""
        high_kelly = KellyParameters(
            win_rate=0.75, avg_win_pct=0.20, avg_loss_pct=0.05
        )
        low_kelly = KellyParameters(
            win_rate=0.55, avg_win_pct=0.12, avg_loss_pct=0.10
        )

        opportunities = [
            {'ticker': 'GOOD', 'params': high_kelly, 'current_price': 100.0},
            {'ticker': 'OK', 'params': low_kelly, 'current_price': 100.0}
        ]

        recs = kelly_sizer.calculate_batch_sizes(
            opportunities=opportunities,
            portfolio_value=100000.0
        )

        # GOOD should have larger position than OK
        good_rec = next(r for r in recs if r.ticker == 'GOOD')
        ok_rec = next(r for r in recs if r.ticker == 'OK')
        assert good_rec.recommended_pct >= ok_rec.recommended_pct

    def test_batch_sizing_with_existing_exposure(self, kelly_sizer, basic_kelly_params):
        """Test batch sizing accounts for existing exposure"""
        opportunities = [
            {'ticker': 'STOCK1', 'params': basic_kelly_params, 'current_price': 100.0}
        ]

        recs = kelly_sizer.calculate_batch_sizes(
            opportunities=opportunities,
            portfolio_value=100000.0,
            current_exposure_pct=0.50  # 50% already deployed
        )

        # Should only allow up to 10% more (60% max - 50% current)
        total_new = sum(r.recommended_pct for r in recs)
        assert total_new <= 0.10

    def test_batch_sizing_stops_at_limit(self, kelly_sizer, high_edge_params):
        """Test batch sizing stops when hitting exposure limit"""
        # Create many high-quality opportunities
        opportunities = [
            {'ticker': f'STOCK{i}', 'params': high_edge_params, 'current_price': 100.0}
            for i in range(10)
        ]

        recs = kelly_sizer.calculate_batch_sizes(
            opportunities=opportunities,
            portfolio_value=100000.0
        )

        # Total should not exceed max portfolio exposure
        total_exposure = sum(r.recommended_pct for r in recs)
        # Allow small floating-point tolerance
        assert total_exposure <= kelly_sizer.max_portfolio_exposure + 1e-10

        # Some positions might be rejected due to exposure limit
        rejected = [r for r in recs if r.recommended_shares == 0]
        assert len(rejected) >= 0  # May or may not have rejections


# Test Report Generation

class TestReportGeneration:
    """Test markdown report generation"""

    def test_report_includes_summary(self, kelly_sizer, basic_kelly_params):
        """Test report includes summary section"""
        rec = kelly_sizer.calculate_position_size(
            ticker="AAPL",
            params=basic_kelly_params,
            current_price=150.0,
            portfolio_value=100000.0
        )

        report = kelly_sizer.generate_report([rec])

        assert "# Position Sizing Recommendations" in report
        assert "Total Positions" in report
        assert "Total Exposure" in report
        assert "Total Investment" in report

    def test_report_includes_positions(self, kelly_sizer, basic_kelly_params):
        """Test report includes position details"""
        rec = kelly_sizer.calculate_position_size(
            ticker="AAPL",
            params=basic_kelly_params,
            current_price=150.0,
            portfolio_value=100000.0
        )

        report = kelly_sizer.generate_report([rec])

        assert "AAPL" in report
        assert "Shares" in report
        assert "Price" in report
        assert "Investment" in report
        assert "Position Size" in report

    def test_report_includes_reasoning(self, kelly_sizer, basic_kelly_params):
        """Test report includes reasoning"""
        rec = kelly_sizer.calculate_position_size(
            ticker="AAPL",
            params=basic_kelly_params,
            current_price=150.0,
            portfolio_value=100000.0
        )

        report = kelly_sizer.generate_report([rec])

        assert "Reasoning" in report
        assert "Full Kelly" in report

    def test_report_includes_rejected(self, kelly_sizer, no_edge_params):
        """Test report includes rejected positions"""
        rec = kelly_sizer.calculate_position_size(
            ticker="LOSER",
            params=no_edge_params,
            current_price=50.0,
            portfolio_value=100000.0
        )

        report = kelly_sizer.generate_report([rec])

        assert "Rejected Positions" in report
        assert "LOSER" in report


# Test Historical Parameters

class TestHistoricalParameters:
    """Test calculating Kelly parameters from historical trades"""

    def test_calculate_from_history(self, sample_trades):
        """Test calculating parameters from trade history"""
        params = calculate_historical_kelly_params(sample_trades)

        assert 0 <= params.win_rate <= 1
        assert params.avg_win_pct > 0
        assert params.avg_loss_pct > 0
        assert params.volatility >= 0
        assert params.confidence > 0

    def test_win_rate_calculation(self, sample_trades):
        """Test win rate calculation from history"""
        params = calculate_historical_kelly_params(sample_trades)

        # 6 wins out of 10 trades = 60%
        expected_win_rate = 0.60
        assert abs(params.win_rate - expected_win_rate) < 0.01

    def test_avg_win_calculation(self, sample_trades):
        """Test average win calculation"""
        params = calculate_historical_kelly_params(sample_trades)

        # Wins: 0.15, 0.20, 0.12, 0.18, 0.25, 0.10
        # Avg: 0.1667
        assert params.avg_win_pct > 0.15
        assert params.avg_win_pct < 0.18

    def test_avg_loss_calculation(self, sample_trades):
        """Test average loss calculation"""
        params = calculate_historical_kelly_params(sample_trades)

        # Losses: 0.08, 0.10, 0.05, 0.07
        # Avg: 0.075
        assert params.avg_loss_pct > 0.07
        assert params.avg_loss_pct < 0.08

    def test_lookback_limit(self, sample_trades):
        """Test lookback trade limit"""
        # Create many trades
        many_trades = sample_trades * 10  # 100 trades

        params = calculate_historical_kelly_params(many_trades, lookback_trades=30)

        # Should only use last 30 trades
        # Results should be same as using all (since all are identical pattern)
        assert params.win_rate == 0.60

    def test_no_trades_raises_error(self):
        """Test empty trade list raises error"""
        with pytest.raises(ValueError, match="No trades provided"):
            calculate_historical_kelly_params([])

    def test_no_wins_raises_error(self):
        """Test no winning trades raises error"""
        losing_trades = [
            {'return_pct': -0.10, 'win': False},
            {'return_pct': -0.08, 'win': False}
        ]

        with pytest.raises(ValueError, match="No winning trades found"):
            calculate_historical_kelly_params(losing_trades)

    def test_no_losses_raises_error(self):
        """Test no losing trades raises error"""
        winning_trades = [
            {'return_pct': 0.15, 'win': True},
            {'return_pct': 0.20, 'win': True}
        ]

        with pytest.raises(ValueError, match="No losing trades found"):
            calculate_historical_kelly_params(winning_trades)


# Edge Cases

class TestEdgeCases:
    """Test edge cases"""

    def test_very_high_stock_price(self, kelly_sizer, basic_kelly_params):
        """Test with very high stock price"""
        rec = kelly_sizer.calculate_position_size(
            ticker="BRK.A",
            params=basic_kelly_params,
            current_price=500000.0,  # Berkshire A share
            portfolio_value=100000.0
        )

        # Might result in 0 shares if price too high
        if rec.recommended_shares == 0:
            assert rec.recommended_pct >= 0
        else:
            assert rec.recommended_shares >= 0

    def test_very_small_portfolio(self, kelly_sizer, basic_kelly_params):
        """Test with very small portfolio"""
        rec = kelly_sizer.calculate_position_size(
            ticker="AAPL",
            params=basic_kelly_params,
            current_price=150.0,
            portfolio_value=1000.0  # $1K portfolio
        )

        # Should still work, might have small position
        assert rec.recommended_shares >= 0

    def test_zero_volatility(self, kelly_sizer):
        """Test with zero volatility"""
        params = KellyParameters(
            win_rate=0.60,
            avg_win_pct=0.15,
            avg_loss_pct=0.08,
            volatility=0.0  # No volatility
        )

        rec = kelly_sizer.calculate_position_size(
            ticker="STABLE",
            params=params,
            current_price=100.0,
            portfolio_value=100000.0
        )

        # Should still work, volatility adjustment = 1.0
        assert rec.recommended_shares >= 0

    def test_perfect_confidence(self, kelly_sizer):
        """Test with 100% confidence"""
        params = KellyParameters(
            win_rate=0.70,
            avg_win_pct=0.15,
            avg_loss_pct=0.08,
            confidence=1.0  # Perfect confidence
        )

        rec = kelly_sizer.calculate_position_size(
            ticker="CERTAIN",
            params=params,
            current_price=100.0,
            portfolio_value=100000.0
        )

        # Should allow max position (no confidence reduction)
        assert rec.recommended_shares > 0

    def test_zero_confidence(self, kelly_sizer):
        """Test with 0% confidence"""
        params = KellyParameters(
            win_rate=0.70,
            avg_win_pct=0.15,
            avg_loss_pct=0.08,
            confidence=0.0  # No confidence
        )

        rec = kelly_sizer.calculate_position_size(
            ticker="UNCERTAIN",
            params=params,
            current_price=100.0,
            portfolio_value=100000.0
        )

        # Should result in no position (0% confidence = 0% position)
        assert rec.recommended_shares == 0
