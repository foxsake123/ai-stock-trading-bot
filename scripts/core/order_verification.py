"""
Order Fill Verification for AI Trading Bot
==========================================
Verifies that submitted orders are filled and reconciles with expected trades.

Author: AI Trading Bot System
Date: January 13, 2026
"""

import time
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderStatus, QueryOrderStatus

logger = logging.getLogger(__name__)


class FillStatus(Enum):
    """Order fill status"""
    FILLED = "filled"
    PARTIAL = "partial"
    PENDING = "pending"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


@dataclass
class OrderVerificationResult:
    """Result of order verification"""
    order_id: str
    symbol: str
    side: str
    requested_qty: float
    filled_qty: float
    filled_price: Optional[float]
    status: FillStatus
    wait_time_seconds: float
    error_message: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.status in [FillStatus.FILLED, FillStatus.PARTIAL]

    @property
    def fill_percentage(self) -> float:
        if self.requested_qty <= 0:
            return 0.0
        return (self.filled_qty / self.requested_qty) * 100


class OrderVerifier:
    """
    Verifies order fills with configurable wait time and polling.

    Example:
        verifier = OrderVerifier(client, max_wait_seconds=30)
        result = verifier.verify_order(order_id)

        if result.is_success:
            print(f"Filled {result.filled_qty} @ ${result.filled_price}")
        else:
            print(f"Order failed: {result.status}")
    """

    def __init__(
        self,
        trading_client: TradingClient,
        max_wait_seconds: float = 30.0,
        poll_interval_seconds: float = 1.0
    ):
        """
        Args:
            trading_client: Alpaca TradingClient instance
            max_wait_seconds: Maximum time to wait for fill
            poll_interval_seconds: Time between status checks
        """
        self.client = trading_client
        self.max_wait_seconds = max_wait_seconds
        self.poll_interval_seconds = poll_interval_seconds

    def verify_order(self, order_id: str) -> OrderVerificationResult:
        """
        Wait for order to fill and return verification result.

        Args:
            order_id: Alpaca order ID

        Returns:
            OrderVerificationResult with fill details
        """
        start_time = time.time()
        last_status = None

        while True:
            elapsed = time.time() - start_time

            try:
                order = self.client.get_order_by_id(order_id)
                last_status = order.status

                # Check for terminal states
                if order.status == OrderStatus.FILLED:
                    return OrderVerificationResult(
                        order_id=str(order.id),
                        symbol=order.symbol,
                        side=order.side.value,
                        requested_qty=float(order.qty),
                        filled_qty=float(order.filled_qty or 0),
                        filled_price=float(order.filled_avg_price) if order.filled_avg_price else None,
                        status=FillStatus.FILLED,
                        wait_time_seconds=elapsed
                    )

                elif order.status == OrderStatus.PARTIALLY_FILLED:
                    if elapsed >= self.max_wait_seconds:
                        return OrderVerificationResult(
                            order_id=str(order.id),
                            symbol=order.symbol,
                            side=order.side.value,
                            requested_qty=float(order.qty),
                            filled_qty=float(order.filled_qty or 0),
                            filled_price=float(order.filled_avg_price) if order.filled_avg_price else None,
                            status=FillStatus.PARTIAL,
                            wait_time_seconds=elapsed
                        )

                elif order.status == OrderStatus.CANCELLED:
                    return OrderVerificationResult(
                        order_id=str(order.id),
                        symbol=order.symbol,
                        side=order.side.value,
                        requested_qty=float(order.qty),
                        filled_qty=float(order.filled_qty or 0),
                        filled_price=float(order.filled_avg_price) if order.filled_avg_price else None,
                        status=FillStatus.CANCELLED,
                        wait_time_seconds=elapsed
                    )

                elif order.status == OrderStatus.EXPIRED:
                    return OrderVerificationResult(
                        order_id=str(order.id),
                        symbol=order.symbol,
                        side=order.side.value,
                        requested_qty=float(order.qty),
                        filled_qty=0,
                        filled_price=None,
                        status=FillStatus.EXPIRED,
                        wait_time_seconds=elapsed
                    )

                elif order.status == OrderStatus.REJECTED:
                    return OrderVerificationResult(
                        order_id=str(order.id),
                        symbol=order.symbol,
                        side=order.side.value,
                        requested_qty=float(order.qty),
                        filled_qty=0,
                        filled_price=None,
                        status=FillStatus.REJECTED,
                        wait_time_seconds=elapsed,
                        error_message=f"Order rejected by exchange"
                    )

            except Exception as e:
                logger.error(f"Error checking order {order_id}: {e}")

            # Check timeout
            if elapsed >= self.max_wait_seconds:
                return OrderVerificationResult(
                    order_id=order_id,
                    symbol="UNKNOWN",
                    side="UNKNOWN",
                    requested_qty=0,
                    filled_qty=0,
                    filled_price=None,
                    status=FillStatus.TIMEOUT,
                    wait_time_seconds=elapsed,
                    error_message=f"Timeout after {self.max_wait_seconds}s. Last status: {last_status}"
                )

            time.sleep(self.poll_interval_seconds)

    def verify_multiple_orders(
        self,
        order_ids: List[str]
    ) -> Tuple[List[OrderVerificationResult], Dict[str, any]]:
        """
        Verify multiple orders and return summary.

        Args:
            order_ids: List of Alpaca order IDs

        Returns:
            Tuple of (results list, summary dict)
        """
        results = []

        for order_id in order_ids:
            result = self.verify_order(order_id)
            results.append(result)
            logger.info(
                f"Order {result.symbol} {result.side}: "
                f"{result.status.value} ({result.fill_percentage:.0f}% filled)"
            )

        # Calculate summary
        filled = [r for r in results if r.status == FillStatus.FILLED]
        partial = [r for r in results if r.status == FillStatus.PARTIAL]
        failed = [r for r in results if r.status not in [FillStatus.FILLED, FillStatus.PARTIAL]]

        total_value = sum(
            r.filled_qty * (r.filled_price or 0)
            for r in results
            if r.filled_price
        )

        summary = {
            "total_orders": len(order_ids),
            "filled": len(filled),
            "partial": len(partial),
            "failed": len(failed),
            "success_rate": len(filled) / len(order_ids) * 100 if order_ids else 0,
            "total_value": total_value,
            "failed_symbols": [r.symbol for r in failed]
        }

        return results, summary


def reconcile_trades(
    trading_client: TradingClient,
    expected_trades: List[Dict],
    lookback_hours: int = 4
) -> Dict:
    """
    Reconcile expected trades against actual Alpaca order history.

    Args:
        trading_client: Alpaca TradingClient
        expected_trades: List of expected trades [{"symbol": "AAPL", "side": "buy", "qty": 10}, ...]
        lookback_hours: Hours to look back for orders

    Returns:
        Reconciliation report dict
    """
    # Get recent orders
    request = GetOrdersRequest(
        status=QueryOrderStatus.ALL,
        limit=100
    )
    orders = trading_client.get_orders(filter=request)

    # Filter to recent orders
    cutoff = datetime.now() - timedelta(hours=lookback_hours)
    recent_orders = [
        o for o in orders
        if o.created_at and o.created_at.replace(tzinfo=None) >= cutoff
    ]

    # Build order map
    order_map = {}
    for order in recent_orders:
        key = f"{order.symbol}_{order.side.value}"
        if key not in order_map:
            order_map[key] = []
        order_map[key].append(order)

    # Reconcile
    report = {
        "expected": len(expected_trades),
        "matched": 0,
        "missing": [],
        "extra": [],
        "discrepancies": []
    }

    for trade in expected_trades:
        key = f"{trade['symbol']}_{trade['side']}"

        if key in order_map and order_map[key]:
            # Found matching order
            order = order_map[key].pop(0)
            report["matched"] += 1

            # Check quantity matches
            expected_qty = float(trade.get('qty', 0))
            actual_qty = float(order.filled_qty or 0)

            if expected_qty > 0 and abs(actual_qty - expected_qty) > 0.01:
                report["discrepancies"].append({
                    "symbol": trade['symbol'],
                    "expected_qty": expected_qty,
                    "actual_qty": actual_qty,
                    "difference": actual_qty - expected_qty
                })
        else:
            report["missing"].append(trade['symbol'])

    # Check for extra orders not in expected
    for key, remaining_orders in order_map.items():
        for order in remaining_orders:
            report["extra"].append({
                "symbol": order.symbol,
                "side": order.side.value,
                "qty": float(order.filled_qty or order.qty)
            })

    return report


if __name__ == "__main__":
    # Test verification (requires actual Alpaca connection)
    import os
    from dotenv import load_dotenv

    load_dotenv()

    client = TradingClient(
        os.getenv('ALPACA_API_KEY_SHORGAN_LIVE'),
        os.getenv('ALPACA_SECRET_KEY_SHORGAN_LIVE'),
        paper=False
    )

    verifier = OrderVerifier(client, max_wait_seconds=5)

    # Get recent orders for testing
    request = GetOrdersRequest(status=QueryOrderStatus.ALL, limit=5)
    orders = client.get_orders(filter=request)

    print("Recent Orders:")
    for order in orders:
        print(f"  {order.symbol} {order.side.value}: {order.status.value}")

    if orders:
        print(f"\nVerifying most recent order: {orders[0].id}")
        result = verifier.verify_order(str(orders[0].id))
        print(f"  Status: {result.status.value}")
        print(f"  Filled: {result.filled_qty} @ ${result.filled_price}")
