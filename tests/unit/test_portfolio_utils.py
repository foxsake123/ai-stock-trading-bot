"""
Unit tests for portfolio utility functions
Tests position sizing, risk calculations, and portfolio management utilities
"""

import pytest


class MockAccount:
    """Mock Alpaca account object for testing"""

    def __init__(self, cash=100000.0, portfolio_value=200000.0, buying_power=100000.0):
        self.cash = str(cash)
        self.portfolio_value = str(portfolio_value)
        self.buying_power = str(buying_power)
        self.long_market_value = str(portfolio_value - cash)
        self.short_market_value = "0.0"


class MockPosition:
    """Mock Alpaca position object for testing"""

    def __init__(self, symbol, qty, avg_entry_price, current_price, market_value):
        self.symbol = symbol
        self.qty = str(qty)
        self.avg_entry_price = str(avg_entry_price)
        self.current_price = str(current_price)
        self.market_value = str(market_value)
        self.unrealized_pl = str(float(market_value) - (float(qty) * float(avg_entry_price)))
        self.unrealized_plpc = str((float(current_price) - float(avg_entry_price)) / float(avg_entry_price))


class TestPositionSizing:
    """Test position sizing calculations"""

    def test_calculate_position_size_fixed_dollar(self):
        """Test position sizing with fixed dollar amount"""
        account_value = 100000.00
        position_pct = 0.05  # 5%
        expected_size = 5000.00

        actual_size = account_value * position_pct
        assert actual_size == expected_size

    def test_calculate_position_size_shares(self):
        """Test converting dollar amount to shares"""
        dollar_amount = 5000.00
        share_price = 100.00
        expected_shares = 50

        actual_shares = int(dollar_amount / share_price)
        assert actual_shares == expected_shares

    def test_position_size_respects_maximum(self):
        """Test position size doesn't exceed maximum percentage"""
        account_value = 100000.00
        max_position_pct = 0.10  # 10% max
        max_position_value = account_value * max_position_pct

        # Try to allocate 15%
        requested = 15000.00

        # Should be capped at 10%
        actual = min(requested, max_position_value)
        assert actual == 10000.00

    def test_position_size_with_fractional_shares(self):
        """Test position sizing that results in fractional shares"""
        dollar_amount = 1000.00
        share_price = 333.33

        shares = dollar_amount / share_price
        # Round down to avoid overspending
        whole_shares = int(shares)

        assert whole_shares == 3
        assert whole_shares * share_price < dollar_amount


class TestRiskCalculations:
    """Test risk calculation functions"""

    def test_calculate_portfolio_risk_single_position(self):
        """Test risk calculation for single position"""
        position_value = 10000.00
        portfolio_value = 100000.00
        stop_loss_pct = 0.10  # 10% stop

        max_loss = position_value * stop_loss_pct
        portfolio_risk_pct = (max_loss / portfolio_value) * 100

        assert max_loss == 1000.00
        assert portfolio_risk_pct == 1.0

    def test_calculate_portfolio_risk_multiple_positions(self):
        """Test risk calculation across multiple positions"""
        positions = [
            {"value": 10000, "stop_pct": 0.10},  # $1000 risk
            {"value": 15000, "stop_pct": 0.15},  # $2250 risk
            {"value": 8000, "stop_pct": 0.08},   # $640 risk
        ]

        total_risk = sum(p["value"] * p["stop_pct"] for p in positions)
        portfolio_value = 100000.00
        total_risk_pct = (total_risk / portfolio_value) * 100

        assert total_risk == 3890.00
        assert pytest.approx(total_risk_pct, 0.01) == 3.89

    def test_risk_reward_ratio(self):
        """Test risk/reward ratio calculation"""
        entry = 100.00
        stop = 90.00  # -10%
        target = 130.00  # +30%

        risk = entry - stop  # 10
        reward = target - entry  # 30
        ratio = reward / risk

        assert ratio == 3.0  # 3:1 risk/reward

    def test_kelly_criterion_approximation(self):
        """Test Kelly Criterion for position sizing"""
        win_rate = 0.60  # 60% win rate
        avg_win = 0.15  # 15% average win
        avg_loss = 0.10  # 10% average loss

        kelly_pct = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win

        # Conservative: use half Kelly
        position_size = kelly_pct * 0.5

        assert kelly_pct > 0  # Positive edge
        assert position_size < 0.5  # Less than 50% allocation


class TestCashManagement:
    """Test cash balance and margin calculations"""

    def test_check_positive_cash_balance(self):
        """Test checking for positive cash balance"""
        account = MockAccount(cash=10000.0)
        cash = float(account.cash)

        assert cash > 0
        assert cash >= 0  # No margin usage

    def test_detect_negative_cash_balance(self):
        """Test detecting negative cash (margin usage)"""
        account = MockAccount(cash=-5000.0)
        cash = float(account.cash)

        assert cash < 0  # Using margin
        needs_rebalance = cash < 0
        assert needs_rebalance is True

    def test_calculate_cash_needed_to_restore_positive(self):
        """Test calculating cash needed to fix negative balance"""
        current_cash = -9521.89
        buffer = 1000.00

        cash_needed = abs(current_cash) + buffer
        assert cash_needed == 10521.89

    def test_verify_long_only_compliance(self):
        """Test verifying LONG-ONLY strategy compliance"""
        account = MockAccount(
            cash=5000.0,
            portfolio_value=105000.0
        )

        cash = float(account.cash)
        short_value = float(account.short_market_value)

        # Both conditions must be true for long-only
        assert cash >= 0  # No margin
        assert short_value == 0.0  # No short positions


class TestPositionManagement:
    """Test position management utilities"""

    def test_sort_positions_by_pnl(self):
        """Test sorting positions by P/L percentage"""
        positions = [
            MockPosition("AAPL", 100, 150.00, 165.00, 16500.00),  # +10%
            MockPosition("MSFT", 50, 300.00, 285.00, 14250.00),   # -5%
            MockPosition("GOOGL", 30, 140.00, 133.00, 3990.00),   # -5%
        ]

        sorted_positions = sorted(positions, key=lambda p: float(p.unrealized_plpc))

        # Losers first
        assert sorted_positions[0].symbol in ["MSFT", "GOOGL"]
        assert sorted_positions[-1].symbol == "AAPL"

    def test_calculate_total_market_value(self):
        """Test calculating total position value"""
        positions = [
            MockPosition("AAPL", 100, 150.00, 165.00, 16500.00),
            MockPosition("MSFT", 50, 300.00, 285.00, 14250.00),
        ]

        total = sum(float(p.market_value) for p in positions)
        assert total == 30750.00

    def test_identify_positions_to_liquidate(self):
        """Test selecting positions to sell for cash"""
        positions = [
            MockPosition("PG", 160, 152.20, 152.01, 24321.60),   # -0.12%
            MockPosition("CL", 136, 79.64, 79.14, 10763.04),     # -0.63%
            MockPosition("CVX", 31, 158.00, 157.27, 4875.37),    # -0.46%
        ]

        # Sort by P/L (sell losers first)
        sorted_pos = sorted(positions, key=lambda p: float(p.unrealized_plpc))

        # Need to raise ~$10,000
        target = 10000.00
        total_raised = 0
        to_sell = []

        for pos in sorted_pos:
            if total_raised >= target:
                break
            to_sell.append(pos.symbol)
            total_raised += float(pos.market_value)

        assert "CL" in to_sell  # Worst performer should be sold
        assert total_raised >= target


class TestPortfolioMetrics:
    """Test portfolio performance metrics"""

    def test_calculate_portfolio_return(self):
        """Test calculating total portfolio return"""
        starting_value = 200000.00
        current_value = 207590.85

        total_return = current_value - starting_value
        return_pct = (total_return / starting_value) * 100

        assert pytest.approx(total_return, 0.01) == 7590.85
        assert pytest.approx(return_pct, 0.01) == 3.80

    def test_calculate_position_allocation(self):
        """Test calculating position allocation percentages"""
        position_value = 21548.52
        portfolio_value = 103896.82

        allocation_pct = (position_value / portfolio_value) * 100

        assert pytest.approx(allocation_pct, 0.01) == 20.74

    def test_verify_diversification(self):
        """Test checking for over-concentration"""
        positions = {
            "AAPL": 21548.52,
            "JPM": 19697.28,
            "MSFT": 17895.22,
            "PG": 9814.02,
            "MRK": 9638.20,
            "Others": 25303.58
        }
        portfolio_value = sum(positions.values())

        # Check if any single position >30%
        max_allocation = max(v / portfolio_value for v in positions.values())

        assert max_allocation < 0.30  # No position >30%

    def test_calculate_cash_allocation(self):
        """Test calculating cash percentage"""
        cash = 5052.41
        portfolio_value = 103896.82

        cash_pct = (cash / portfolio_value) * 100

        assert pytest.approx(cash_pct, 0.01) == 4.86


class TestStopLossCalculations:
    """Test stop-loss price calculations"""

    def test_calculate_stop_price_percentage(self):
        """Test calculating stop price from percentage"""
        entry_price = 20.00
        stop_pct = 0.175  # -17.5%

        stop_price = entry_price * (1 - stop_pct)

        assert stop_price == 16.50

    def test_calculate_stop_prices_multiple_positions(self):
        """Test calculating stops for multiple positions"""
        positions = [
            {"symbol": "ARQT", "entry": 19.98, "stop_pct": 0.175},
            {"symbol": "HIMS", "entry": 55.97, "stop_pct": 0.125},
            {"symbol": "WOLF", "entry": 25.98, "stop_pct": 0.154},
        ]

        stops = {p["symbol"]: p["entry"] * (1 - p["stop_pct"]) for p in positions}

        assert pytest.approx(stops["ARQT"], 0.01) == 16.48
        assert pytest.approx(stops["HIMS"], 0.01) == 48.97
        assert pytest.approx(stops["WOLF"], 0.01) == 21.98

    def test_calculate_max_loss_from_stops(self):
        """Test calculating max loss if all stops hit"""
        positions = [
            {"value": 2937.00, "stop_pct": 0.175},  # ARQT: 513.98
            {"value": 2078.91, "stop_pct": 0.125},  # HIMS: 259.86
            {"value": 2496.00, "stop_pct": 0.154},  # WOLF: 384.38
        ]

        max_loss = sum(p["value"] * p["stop_pct"] for p in positions)
        portfolio_value = 207590.85
        max_loss_pct = (max_loss / portfolio_value) * 100

        # Actual calculation: 513.98 + 259.86 + 384.38 = 1158.22
        assert pytest.approx(max_loss, 1.0) == 1158.22
        assert pytest.approx(max_loss_pct, 0.01) == 0.56


class TestEdgeCases:
    """Test edge cases in portfolio calculations"""

    def test_zero_portfolio_value(self):
        """Test handling zero portfolio value"""
        position_value = 1000.00
        portfolio_value = 0.00

        # Should handle division by zero
        with pytest.raises(ZeroDivisionError):
            allocation = position_value / portfolio_value

    def test_negative_position_value(self):
        """Test handling negative position (short)"""
        position = MockPosition("PLUG", -500, 5.00, 4.50, -2250.00)

        qty = float(position.qty)
        value = float(position.market_value)

        assert qty < 0  # Short position
        assert value < 0  # Negative value

    def test_very_small_position(self):
        """Test handling fractional shares/small positions"""
        position = MockPosition("PENNY", 1, 0.50, 0.52, 0.52)

        value = float(position.market_value)
        assert value > 0
        assert value < 1.00
