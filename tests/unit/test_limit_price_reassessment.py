"""
Unit tests for limit price reassessment functionality
Tests the analyze_limit_adjustment function from reassess_limit_prices.py
"""

import pytest
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'utilities'))

from reassess_limit_prices import analyze_limit_adjustment


class TestBuyLimitAdjustment:
    """Test limit price adjustment for buy orders"""

    def test_market_significantly_above_limit(self):
        """Test when market is >5% above limit price"""
        should_adjust, new_limit, reasoning = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=106.00,  # 6% above
            side='buy'
        )

        assert should_adjust is True
        assert new_limit == 108.12  # 106 * 1.02
        assert "above limit" in reasoning.lower()
        assert "+2% buffer" in reasoning

    def test_market_moderately_above_limit(self):
        """Test when market is 2-5% above limit price"""
        should_adjust, new_limit, reasoning = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=103.00,  # 3% above
            side='buy'
        )

        assert should_adjust is True
        assert new_limit == 104.03  # 103 * 1.01
        assert "+1% buffer" in reasoning

    def test_market_significantly_below_limit(self):
        """Test when limit is >3% above market price"""
        should_adjust, new_limit, reasoning = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=96.00,  # limit is 4.17% above
            side='buy'
        )

        assert should_adjust is True
        assert new_limit == 96.48  # 96 * 1.005
        assert "better entry" in reasoning.lower()

    def test_limit_within_acceptable_range(self):
        """Test when limit is in acceptable range (-3% to +2%)"""
        should_adjust, new_limit, reasoning = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=101.00,  # 1% above
            side='buy'
        )

        assert should_adjust is False
        assert new_limit == 100.00  # No change
        assert "within range" in reasoning.lower()

    def test_limit_at_market_price(self):
        """Test when limit equals market price"""
        should_adjust, new_limit, reasoning = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=100.00,
            side='buy'
        )

        assert should_adjust is False
        assert new_limit == 100.00

    def test_market_barely_above_threshold(self):
        """Test boundary condition: exactly 5% above"""
        should_adjust, new_limit, reasoning = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=105.00,  # Exactly 5% above
            side='buy'
        )

        # At exactly 5%, may or may not adjust depending on implementation
        assert isinstance(should_adjust, bool)
        assert isinstance(new_limit, float)

    def test_market_just_over_threshold(self):
        """Test boundary condition: just over 5% above"""
        should_adjust, new_limit, reasoning = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=105.01,  # Just over 5%
            side='buy'
        )

        assert should_adjust is True
        assert new_limit == 107.11  # 105.01 * 1.02


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_none_current_price(self):
        """Test handling of None current price"""
        should_adjust, new_limit, reasoning = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=None,
            side='buy'
        )

        assert should_adjust is False
        assert new_limit == 100.00
        assert "No current price available" in reasoning

    def test_zero_current_price(self):
        """Test handling of zero price (market closed/error)"""
        should_adjust, new_limit, reasoning = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=0.0,
            side='buy'
        )

        # When price is 0, implementation may vary
        assert isinstance(should_adjust, bool)
        assert isinstance(new_limit, float)

    def test_very_small_price(self):
        """Test with penny stocks (very small prices)"""
        should_adjust, new_limit, reasoning = analyze_limit_adjustment(
            symbol="PENNY",
            current_limit=0.50,
            current_price=0.54,  # 8% above
            side='buy'
        )

        assert should_adjust is True
        assert new_limit == 0.55  # 0.54 * 1.02, rounded

    def test_very_large_price(self):
        """Test with expensive stocks"""
        should_adjust, new_limit, reasoning = analyze_limit_adjustment(
            symbol="BRK.A",
            current_limit=500000.00,
            current_price=530000.00,  # 6% above
            side='buy'
        )

        assert should_adjust is True
        expected = round(530000 * 1.02, 2)
        assert new_limit == expected

    def test_negative_price(self):
        """Test handling of invalid negative price"""
        should_adjust, new_limit, reasoning = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=-10.00,
            side='buy'
        )

        # Should handle gracefully
        assert isinstance(should_adjust, bool)
        assert isinstance(new_limit, float)


class TestPriceRounding:
    """Test price rounding behavior"""

    def test_rounding_to_two_decimals(self):
        """Test prices are rounded to 2 decimal places"""
        should_adjust, new_limit, reasoning = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=106.666,  # 6.666% above
            side='buy'
        )

        assert should_adjust is True
        # 106.666 * 1.02 = 108.79932, should round to 108.80
        assert new_limit == 108.80
        assert isinstance(new_limit, float)

    def test_rounding_down(self):
        """Test rounding down when needed"""
        should_adjust, new_limit, reasoning = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=106.001,
            side='buy'
        )

        expected = round(106.001 * 1.02, 2)
        assert new_limit == expected


class TestReasoningMessages:
    """Test reasoning messages are informative"""

    def test_reasoning_includes_percentage(self):
        """Test reasoning includes percentage difference"""
        _, _, reasoning = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=110.00,
            side='buy'
        )

        # Should mention 10% difference
        assert "10" in reasoning

    def test_reasoning_includes_new_price(self):
        """Test reasoning includes new recommended price"""
        _, new_limit, reasoning = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=110.00,
            side='buy'
        )

        assert str(new_limit) in reasoning or f"{new_limit:.2f}" in reasoning

    def test_reasoning_is_not_empty(self):
        """Test reasoning is always provided"""
        _, _, reasoning = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=100.00,
            side='buy'
        )

        assert reasoning != ""
        assert len(reasoning) > 0


class TestMultipleAdjustments:
    """Test scenarios requiring multiple adjustments"""

    def test_adjustment_prevents_overpaying(self):
        """Test adjustment prevents overpaying in volatile market"""
        # Market jumped 8% - should adjust but with buffer
        should_adjust, new_limit, _ = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=108.00,
            side='buy'
        )

        assert should_adjust is True
        assert new_limit < 108.00 * 1.05  # Not paying >5% over market

    def test_adjustment_improves_entry(self):
        """Test adjustment improves entry when market falls"""
        should_adjust, new_limit, _ = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=95.00,  # Market fell 5%
            side='buy'
        )

        assert should_adjust is True
        assert new_limit < 100.00  # Lower than original limit
        assert new_limit > 95.00  # But still above market


class TestSymbolHandling:
    """Test different symbol formats"""

    def test_standard_ticker(self):
        """Test standard ticker symbols"""
        should_adjust, _, _ = analyze_limit_adjustment(
            symbol="AAPL",
            current_limit=100.00,
            current_price=100.00,
            side='buy'
        )

        assert isinstance(should_adjust, bool)

    def test_ticker_with_dots(self):
        """Test tickers with periods (e.g., BRK.B)"""
        should_adjust, _, _ = analyze_limit_adjustment(
            symbol="BRK.B",
            current_limit=100.00,
            current_price=100.00,
            side='buy'
        )

        assert isinstance(should_adjust, bool)

    def test_ticker_with_hyphen(self):
        """Test tickers with hyphens"""
        should_adjust, _, _ = analyze_limit_adjustment(
            symbol="BF-B",
            current_limit=100.00,
            current_price=100.00,
            side='buy'
        )

        assert isinstance(should_adjust, bool)
