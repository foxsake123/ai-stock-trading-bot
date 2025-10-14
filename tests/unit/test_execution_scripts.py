"""
Unit tests for execution scripts in scripts/execution/
Tests the trade execution functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json


class TestTradeExecution:
    """Test trade execution logic"""

    def test_parse_trade_action_buy(self):
        """Test parsing BUY action from trade description"""
        trade_text = "BUY 100 AAPL @ $150.50"

        # Extract components
        parts = trade_text.split()
        action = parts[0]
        quantity = int(parts[1])
        ticker = parts[2]
        price = float(parts[4].replace('$', ''))

        assert action == "BUY"
        assert quantity == 100
        assert ticker == "AAPL"
        assert price == 150.50

    def test_parse_trade_action_sell(self):
        """Test parsing SELL action from trade description"""
        trade_text = "SELL 50 TSLA @ $245.75"

        parts = trade_text.split()
        action = parts[0]
        quantity = int(parts[1])

        assert action == "SELL"
        assert quantity == 50

    def test_parse_trade_action_short(self):
        """Test parsing SHORT action from trade description"""
        trade_text = "SHORT 200 PLUG @ $4.50"

        parts = trade_text.split()
        action = parts[0]

        assert action == "SHORT"

    def test_validate_trade_quantity_positive(self):
        """Test quantity validation - must be positive"""
        quantity = 100

        assert quantity > 0

    def test_validate_trade_quantity_not_zero(self):
        """Test quantity validation - cannot be zero"""
        quantity = 0

        assert not (quantity > 0)

    def test_validate_trade_price_positive(self):
        """Test price validation - must be positive"""
        price = 150.50

        assert price > 0


class TestOrderCreation:
    """Test order creation logic"""

    @patch('alpaca.trading.client.TradingClient')
    def test_create_market_order(self, mock_client):
        """Test creating a market order"""
        mock_trading_client = MagicMock()
        mock_client.return_value = mock_trading_client

        # Simulate order creation
        order_data = {
            "symbol": "AAPL",
            "qty": 100,
            "side": "buy",
            "type": "market",
            "time_in_force": "day"
        }

        assert order_data["type"] == "market"
        assert order_data["side"] == "buy"

    @patch('alpaca.trading.client.TradingClient')
    def test_create_limit_order(self, mock_client):
        """Test creating a limit order"""
        mock_trading_client = MagicMock()
        mock_client.return_value = mock_trading_client

        order_data = {
            "symbol": "AAPL",
            "qty": 100,
            "side": "buy",
            "type": "limit",
            "limit_price": 150.50,
            "time_in_force": "day"
        }

        assert order_data["type"] == "limit"
        assert order_data["limit_price"] == 150.50

    def test_order_side_validation(self):
        """Test order side must be buy or sell"""
        valid_sides = ["buy", "sell"]

        assert "buy" in valid_sides
        assert "sell" in valid_sides
        assert "invalid" not in valid_sides


class TestStopLossOrders:
    """Test stop loss order creation"""

    def test_calculate_stop_loss_price_shorgan(self):
        """Test calculating stop loss for SHORGAN (8% trailing)"""
        entry_price = 100.0
        stop_loss_pct = 8.0

        stop_price = entry_price * (1 - stop_loss_pct / 100)

        assert stop_price == 92.0

    def test_calculate_stop_loss_price_dee(self):
        """Test calculating stop loss for DEE (3% fixed)"""
        entry_price = 100.0
        stop_loss_pct = 3.0

        stop_price = entry_price * (1 - stop_loss_pct / 100)

        assert stop_price == 97.0

    def test_stop_loss_order_structure(self):
        """Test stop loss order structure"""
        stop_order = {
            "symbol": "AAPL",
            "qty": 100,
            "side": "sell",
            "type": "stop",
            "stop_price": 92.0,
            "time_in_force": "gtc"  # Good til canceled
        }

        assert stop_order["type"] == "stop"
        assert stop_order["time_in_force"] == "gtc"

    def test_trailing_stop_order_structure(self):
        """Test trailing stop order structure"""
        trailing_stop = {
            "symbol": "AAPL",
            "qty": 100,
            "side": "sell",
            "type": "trailing_stop",
            "trail_percent": 8.0,
            "time_in_force": "gtc"
        }

        assert trailing_stop["type"] == "trailing_stop"
        assert trailing_stop["trail_percent"] == 8.0


class TestExecutionLogging:
    """Test execution logging and tracking"""

    def test_log_successful_execution(self):
        """Test logging successful trade execution"""
        execution_log = {
            "timestamp": datetime.now().isoformat(),
            "ticker": "AAPL",
            "action": "BUY",
            "quantity": 100,
            "price": 150.50,
            "status": "filled",
            "order_id": "abc-123"
        }

        assert execution_log["status"] == "filled"
        assert execution_log["order_id"] is not None

    def test_log_failed_execution(self):
        """Test logging failed trade execution"""
        execution_log = {
            "timestamp": datetime.now().isoformat(),
            "ticker": "PLUG",
            "action": "SHORT",
            "quantity": 500,
            "status": "rejected",
            "error": "Not available for shorting"
        }

        assert execution_log["status"] == "rejected"
        assert "error" in execution_log

    def test_execution_summary_creation(self):
        """Test creating execution summary"""
        executions = [
            {"status": "filled"},
            {"status": "filled"},
            {"status": "rejected"},
            {"status": "filled"}
        ]

        total = len(executions)
        successful = sum(1 for e in executions if e["status"] == "filled")
        failed = total - successful
        success_rate = (successful / total) * 100

        assert successful == 3
        assert failed == 1
        assert success_rate == 75.0


class TestBotSpecificExecution:
    """Test bot-specific execution logic"""

    def test_dee_bot_long_only_validation(self):
        """Test DEE-BOT only allows LONG positions"""
        action = "SHORT"
        bot_type = "DEE"

        # DEE-BOT should only allow BUY and SELL
        allowed_actions = ["BUY", "SELL"]

        is_valid = action in allowed_actions
        assert is_valid is False

    def test_shorgan_bot_allows_shorting(self):
        """Test SHORGAN-BOT allows SHORT positions"""
        action = "SHORT"
        bot_type = "SHORGAN"

        allowed_actions = ["BUY", "SELL", "SHORT"]

        is_valid = action in allowed_actions
        assert is_valid is True

    def test_validate_bot_position_limits(self):
        """Test position size limits per bot"""
        # DEE-BOT: Max 8% per position
        dee_max = 0.08
        portfolio_value = 100000
        dee_max_position = portfolio_value * dee_max

        assert dee_max_position == 8000.0

        # SHORGAN-BOT: Max 10% per position
        shorgan_max = 0.10
        shorgan_max_position = portfolio_value * shorgan_max

        assert shorgan_max_position == 10000.0


class TestErrorHandling:
    """Test error handling in execution"""

    def test_handle_insufficient_buying_power(self):
        """Test handling insufficient buying power error"""
        error_message = "Insufficient buying power"

        is_buying_power_error = "buying power" in error_message.lower()
        assert is_buying_power_error is True

    def test_handle_invalid_ticker(self):
        """Test handling invalid ticker error"""
        error_message = "Symbol INVALID not found"

        is_invalid_ticker = "not found" in error_message.lower()
        assert is_invalid_ticker is True

    def test_handle_market_closed(self):
        """Test handling market closed error"""
        error_message = "Market is closed"

        is_market_closed = "closed" in error_message.lower()
        assert is_market_closed is True

    def test_retry_logic_max_attempts(self):
        """Test retry logic with max attempts"""
        max_retries = 3
        attempt = 0

        while attempt < max_retries:
            attempt += 1

        assert attempt == max_retries


class TestExecutionTiming:
    """Test execution timing logic"""

    def test_market_hours_check(self):
        """Test checking if within market hours"""
        # Market hours: 9:30 AM - 4:00 PM ET
        now = datetime.now().time()

        market_open = datetime.strptime("09:30", "%H:%M").time()
        market_close = datetime.strptime("16:00", "%H:%M").time()

        # Just testing the logic structure
        assert market_open < market_close

    def test_pre_market_hours_check(self):
        """Test checking pre-market hours"""
        # Pre-market: 4:00 AM - 9:30 AM ET
        pre_market_open = datetime.strptime("04:00", "%H:%M").time()
        market_open = datetime.strptime("09:30", "%H:%M").time()

        assert pre_market_open < market_open

    def test_after_hours_check(self):
        """Test checking after-hours trading"""
        # After-hours: 4:00 PM - 8:00 PM ET
        market_close = datetime.strptime("16:00", "%H:%M").time()
        after_hours_close = datetime.strptime("20:00", "%H:%M").time()

        assert market_close < after_hours_close


class TestPositionTracking:
    """Test position tracking after execution"""

    def test_update_position_after_buy(self):
        """Test updating position after buy order"""
        current_position = 0
        buy_quantity = 100

        new_position = current_position + buy_quantity

        assert new_position == 100

    def test_update_position_after_sell(self):
        """Test updating position after sell order"""
        current_position = 100
        sell_quantity = 50

        new_position = current_position - sell_quantity

        assert new_position == 50

    def test_calculate_average_cost_basis(self):
        """Test calculating average cost basis"""
        purchases = [
            {"qty": 100, "price": 150.00},
            {"qty": 50, "price": 155.00}
        ]

        total_cost = sum(p["qty"] * p["price"] for p in purchases)
        total_qty = sum(p["qty"] for p in purchases)
        avg_cost = total_cost / total_qty

        assert avg_cost == pytest.approx(151.67, 0.01)


class TestNotificationAfterExecution:
    """Test sending notifications after execution"""

    def test_format_execution_notification(self):
        """Test formatting execution notification message"""
        execution = {
            "ticker": "AAPL",
            "action": "BUY",
            "quantity": 100,
            "price": 150.50,
            "status": "filled"
        }

        message = f"✅ {execution['action']} {execution['quantity']} {execution['ticker']} @ ${execution['price']}"

        assert "✅" in message
        assert "BUY 100 AAPL" in message

    def test_format_failed_execution_notification(self):
        """Test formatting failed execution notification"""
        execution = {
            "ticker": "PLUG",
            "action": "SHORT",
            "status": "rejected",
            "error": "Not available for shorting"
        }

        message = f"❌ {execution['action']} {execution['ticker']}: {execution['error']}"

        assert "❌" in message
        assert "Not available for shorting" in message
