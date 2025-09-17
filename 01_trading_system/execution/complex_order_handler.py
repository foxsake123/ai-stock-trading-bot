#!/usr/bin/env python3
"""
Complex Order Handler for Alpaca API
Handles wash trade warnings and implements advanced order types
"""

import requests
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List

class ComplexOrderHandler:
    """Handle complex orders to avoid wash trade warnings"""

    def __init__(self, api_key: str, secret_key: str = None, paper: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"
        self.headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key or "",
            "Content-Type": "application/json"
        }
        logging.basicConfig(level=logging.INFO)

    def get_recent_orders(self, symbol: str, days: int = 30) -> List[Dict]:
        """Get recent orders for a symbol to check for wash trades"""

        after = (datetime.now() - timedelta(days=days)).isoformat() + 'Z'
        url = f"{self.base_url}/v2/orders"
        params = {
            "symbols": symbol,
            "status": "all",
            "after": after,
            "limit": 500
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Failed to get orders: {response.text}")
                return []
        except Exception as e:
            logging.error(f"Error fetching orders: {e}")
            return []

    def check_wash_trade_risk(self, symbol: str, side: str) -> bool:
        """Check if there's a wash trade risk"""

        recent_orders = self.get_recent_orders(symbol, days=30)

        # Check for opposite side trades in last 30 days
        opposite_side = "sell" if side == "buy" else "buy"

        for order in recent_orders:
            if order.get("side") == opposite_side and order.get("status") == "filled":
                # Check if it was within 30 days
                filled_at = order.get("filled_at")
                if filled_at:
                    filled_date = datetime.fromisoformat(filled_at.replace('Z', '+00:00'))
                    days_ago = (datetime.now(filled_date.tzinfo) - filled_date).days

                    if days_ago <= 30:
                        logging.warning(f"Wash trade risk detected for {symbol}: "
                                      f"Opposite trade {days_ago} days ago")
                        return True

        return False

    def place_complex_order(self, symbol: str, qty: int, side: str,
                           order_type: str = "market",
                           stop_price: Optional[float] = None,
                           limit_price: Optional[float] = None) -> Optional[Dict]:
        """Place a complex order to avoid wash trade warnings"""

        # Check wash trade risk
        if self.check_wash_trade_risk(symbol, side):
            logging.info(f"Wash trade risk for {symbol}. Using complex order...")
            return self.place_one_cancels_other(symbol, qty, side, stop_price, limit_price)

        # Regular order
        return self.place_regular_order(symbol, qty, side, order_type, stop_price, limit_price)

    def place_regular_order(self, symbol: str, qty: int, side: str,
                           order_type: str = "market",
                           stop_price: Optional[float] = None,
                           limit_price: Optional[float] = None) -> Optional[Dict]:
        """Place a regular order"""

        url = f"{self.base_url}/v2/orders"

        order_data = {
            "symbol": symbol,
            "qty": str(qty),
            "side": side,
            "type": order_type,
            "time_in_force": "day"
        }

        if order_type == "limit" and limit_price:
            order_data["limit_price"] = str(round(limit_price, 2))

        if order_type == "stop" and stop_price:
            order_data["stop_price"] = str(round(stop_price, 2))

        if order_type == "stop_limit" and stop_price and limit_price:
            order_data["stop_price"] = str(round(stop_price, 2))
            order_data["limit_price"] = str(round(limit_price, 2))

        try:
            response = requests.post(url, headers=self.headers, json=order_data)

            if response.status_code in [200, 201]:
                logging.info(f"Order placed successfully for {symbol}")
                return response.json()
            else:
                error_msg = response.json().get("message", response.text)
                logging.error(f"Order failed for {symbol}: {error_msg}")
                return None

        except Exception as e:
            logging.error(f"Exception placing order for {symbol}: {e}")
            return None

    def place_one_cancels_other(self, symbol: str, qty: int, side: str,
                               stop_price: Optional[float] = None,
                               take_profit: Optional[float] = None) -> Optional[Dict]:
        """Place a One-Cancels-Other (OCO) order to avoid wash trade issues"""

        url = f"{self.base_url}/v2/orders"

        # Create an OCO bracket order
        order_data = {
            "symbol": symbol,
            "qty": str(qty),
            "side": side,
            "type": "market",
            "time_in_force": "day",
            "order_class": "oco"  # One-Cancels-Other
        }

        # Add take profit order
        if take_profit:
            order_data["take_profit"] = {
                "limit_price": str(round(take_profit, 2))
            }

        # Add stop loss order
        if stop_price:
            order_data["stop_loss"] = {
                "stop_price": str(round(stop_price, 2))
            }

        try:
            response = requests.post(url, headers=self.headers, json=order_data)

            if response.status_code in [200, 201]:
                logging.info(f"OCO order placed successfully for {symbol}")
                return response.json()
            else:
                error_msg = response.json().get("message", response.text)

                # If OCO fails, try bracket order
                if "oco" in error_msg.lower():
                    logging.info("OCO not supported, trying bracket order...")
                    return self.place_bracket_order(symbol, qty, side, stop_price, take_profit)

                logging.error(f"OCO order failed for {symbol}: {error_msg}")
                return None

        except Exception as e:
            logging.error(f"Exception placing OCO order for {symbol}: {e}")
            return None

    def place_bracket_order(self, symbol: str, qty: int, side: str,
                           stop_price: Optional[float] = None,
                           take_profit: Optional[float] = None) -> Optional[Dict]:
        """Place a bracket order (entry with attached stop and target)"""

        url = f"{self.base_url}/v2/orders"

        order_data = {
            "symbol": symbol,
            "qty": str(qty),
            "side": side,
            "type": "market",
            "time_in_force": "day",
            "order_class": "bracket"
        }

        if take_profit:
            order_data["take_profit"] = {
                "limit_price": str(round(take_profit, 2))
            }

        if stop_price:
            order_data["stop_loss"] = {
                "stop_price": str(round(stop_price, 2))
            }

        try:
            response = requests.post(url, headers=self.headers, json=order_data)

            if response.status_code in [200, 201]:
                logging.info(f"Bracket order placed successfully for {symbol}")
                return response.json()
            else:
                error_msg = response.json().get("message", response.text)
                logging.error(f"Bracket order failed for {symbol}: {error_msg}")

                # If bracket fails, try delayed execution
                if "wash" in error_msg.lower():
                    logging.info("Wash trade detected. Waiting 1 minute...")
                    time.sleep(61)  # Wait 61 seconds
                    return self.place_regular_order(symbol, qty, side, "market")

                return None

        except Exception as e:
            logging.error(f"Exception placing bracket order for {symbol}: {e}")
            return None

    def place_adaptive_order(self, symbol: str, qty: int, side: str,
                            stop_loss_pct: float = 0.05,
                            take_profit_pct: float = 0.10) -> Optional[Dict]:
        """Place an adaptive order that handles wash trades automatically"""

        # Get current price
        current_price = self.get_current_price(symbol)
        if not current_price:
            logging.error(f"Could not get current price for {symbol}")
            return None

        # Calculate stop and target
        if side == "buy":
            stop_price = current_price * (1 - stop_loss_pct)
            take_profit = current_price * (1 + take_profit_pct)
        else:  # sell/short
            stop_price = current_price * (1 + stop_loss_pct)
            take_profit = current_price * (1 - take_profit_pct)

        # Try different order types in sequence
        strategies = [
            ("OCO", lambda: self.place_one_cancels_other(symbol, qty, side, stop_price, take_profit)),
            ("Bracket", lambda: self.place_bracket_order(symbol, qty, side, stop_price, take_profit)),
            ("Regular + Stop", lambda: self._place_with_separate_stop(symbol, qty, side, stop_price)),
            ("Delayed", lambda: self._place_with_delay(symbol, qty, side))
        ]

        for strategy_name, strategy_func in strategies:
            logging.info(f"Trying {strategy_name} order for {symbol}...")
            result = strategy_func()

            if result:
                logging.info(f"Successfully placed {strategy_name} order for {symbol}")
                return result

            time.sleep(1)  # Brief pause between attempts

        logging.error(f"All order strategies failed for {symbol}")
        return None

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""

        url = f"https://data.alpaca.markets/v2/stocks/{symbol}/trades/latest"
        headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key or ""
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return float(data["trade"]["price"])
        except Exception as e:
            logging.error(f"Error getting price for {symbol}: {e}")

        return None

    def _place_with_separate_stop(self, symbol: str, qty: int, side: str,
                                 stop_price: float) -> Optional[Dict]:
        """Place market order followed by separate stop loss"""

        # Place market order first
        market_order = self.place_regular_order(symbol, qty, side, "market")

        if market_order:
            time.sleep(2)  # Wait for fill

            # Place stop loss as separate order
            stop_side = "sell" if side == "buy" else "buy"
            stop_order = self.place_regular_order(
                symbol, qty, stop_side, "stop", stop_price=stop_price
            )

            if stop_order:
                return market_order  # Return the entry order

        return None

    def _place_with_delay(self, symbol: str, qty: int, side: str) -> Optional[Dict]:
        """Place order with delay to avoid wash trade"""

        logging.info(f"Waiting 61 seconds to avoid wash trade for {symbol}...")
        time.sleep(61)

        return self.place_regular_order(symbol, qty, side, "market")


def test_complex_orders():
    """Test complex order handling"""

    # Initialize handler
    handler = ComplexOrderHandler(
        api_key="PK6FZK4DAQVTD7DYVH78",
        paper=True
    )

    print("Complex Order Handler Test")
    print("=" * 50)

    # Test getting recent orders
    print("\nChecking recent INCY orders...")
    orders = handler.get_recent_orders("INCY", days=30)
    print(f"Found {len(orders)} recent orders")

    # Test wash trade check
    print("\nChecking wash trade risk for INCY...")
    has_risk = handler.check_wash_trade_risk("INCY", "buy")
    print(f"Wash trade risk: {has_risk}")

    # Test adaptive order (simulation mode)
    print("\nSimulating adaptive order for CBRL...")
    print("Would place: 10 shares with 5% stop loss and 10% take profit")

    print("\nComplex order handler ready for use!")


if __name__ == "__main__":
    test_complex_orders()