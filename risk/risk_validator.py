"""
Risk Validator Module

Enforces risk limits from config/risk_limits.json before executing trades.
This is the SAFETY LAYER that prevents catastrophic losses.

Checks:
1. Daily loss limits (dollars and percentage)
2. Position size limits
3. Total exposure limits
4. Cash reserve requirements
5. Drawdown limits
6. Consecutive loss limits
7. Allowed action types
8. Trading time restrictions

Usage:
    from risk.risk_validator import RiskValidator

    validator = RiskValidator()
    result = validator.validate_trade(trade_dict, account_info, trade_history)

    if result['approved']:
        execute_trade(trade_dict)
    else:
        log_rejection(result['reason'])
"""

import json
import os
from datetime import datetime, time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of trade validation"""
    approved: bool
    reason: str
    limit_type: str  # Which limit was hit (if rejected)
    current_value: float  # Current value of the metric
    limit_value: float  # The limit that was violated


class RiskValidator:
    """
    Validates trades against risk limits

    Loads risk limits from config/risk_limits.json and validates
    each trade before execution.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize risk validator

        Args:
            config_path: Path to risk_limits.json (optional)
        """
        if config_path is None:
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "risk_limits.json"

        self.config_path = Path(config_path)
        self.limits = self._load_limits()

    def _load_limits(self) -> Dict:
        """Load risk limits from config file"""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Risk limits config not found: {self.config_path}\n"
                f"Please create config/risk_limits.json"
            )

        with open(self.config_path, 'r') as f:
            return json.load(f)

    def validate_trade(
        self,
        trade: Dict,
        account_info: Dict,
        trade_history: List[Dict]
    ) -> ValidationResult:
        """
        Validate a single trade against all risk limits

        Args:
            trade: Trade dict with keys:
                - symbol: str
                - action: str (BUY, SELL, etc.)
                - quantity: int
                - price: float
                - value: float (optional, calculated if missing)

            account_info: Account dict with keys:
                - equity: float (current portfolio value)
                - cash: float (available cash)
                - buying_power: float
                - positions: List[Dict] (current positions)

            trade_history: List of recent trades for consecutive loss checking
                Each trade should have:
                - date: str (YYYY-MM-DD)
                - pnl: float (profit/loss)
                - symbol: str
                - action: str

        Returns:
            ValidationResult object with approval status and reason
        """
        # Calculate trade value if not provided
        if 'value' not in trade:
            trade['value'] = trade['quantity'] * trade['price']

        # Run all validation checks
        checks = [
            self._check_allowed_action(trade),
            self._check_trading_hours(trade),
            self._check_single_trade_value(trade),
            self._check_position_size(trade, account_info),
            self._check_total_exposure(trade, account_info),
            self._check_cash_reserve(trade, account_info),
            self._check_daily_loss_limit(trade_history, account_info),
            self._check_drawdown_limit(account_info, trade_history),
            self._check_consecutive_losses(trade_history),
            self._check_daily_trade_count(trade_history)
        ]

        # Return first failure, or success if all pass
        for result in checks:
            if not result.approved:
                return result

        return ValidationResult(
            approved=True,
            reason="All risk checks passed",
            limit_type="NONE",
            current_value=0.0,
            limit_value=0.0
        )

    def _check_allowed_action(self, trade: Dict) -> ValidationResult:
        """Check if action type is allowed"""
        action = trade['action'].upper()
        whitelist = self.limits['allowed_actions']['whitelist']
        blacklist = self.limits['allowed_actions']['blacklist']

        if action in blacklist:
            return ValidationResult(
                approved=False,
                reason=f"Action {action} is blacklisted (Week 1: No shorting)",
                limit_type="BLACKLIST",
                current_value=0.0,
                limit_value=0.0
            )

        if whitelist and action not in whitelist:
            return ValidationResult(
                approved=False,
                reason=f"Action {action} not in whitelist {whitelist}",
                limit_type="WHITELIST",
                current_value=0.0,
                limit_value=0.0
            )

        return ValidationResult(
            approved=True,
            reason="Action type allowed",
            limit_type="NONE",
            current_value=0.0,
            limit_value=0.0
        )

    def _check_trading_hours(self, trade: Dict) -> ValidationResult:
        """Check if current time is within allowed trading hours"""
        now = datetime.now().time()

        # Parse time restrictions
        before_str = self.limits['time_restrictions']['allow_trading_before']
        after_str = self.limits['time_restrictions']['allow_trading_after']

        # Convert to time objects
        hour, minute, second = map(int, before_str.split(':'))
        allow_before = time(hour, minute, second)

        hour, minute, second = map(int, after_str.split(':'))
        allow_after = time(hour, minute, second)

        if now < allow_before:
            return ValidationResult(
                approved=False,
                reason=f"Trading before {before_str} not allowed (avoid first 15 min volatility)",
                limit_type="TIME_RESTRICTION",
                current_value=0.0,
                limit_value=0.0
            )

        if now > allow_after:
            return ValidationResult(
                approved=False,
                reason=f"Trading after {after_str} not allowed (avoid last 30 min close)",
                limit_type="TIME_RESTRICTION",
                current_value=0.0,
                limit_value=0.0
            )

        return ValidationResult(
            approved=True,
            reason="Within allowed trading hours",
            limit_type="NONE",
            current_value=0.0,
            limit_value=0.0
        )

    def _check_single_trade_value(self, trade: Dict) -> ValidationResult:
        """Check if single trade value exceeds limit"""
        max_value = self.limits['trade_limits']['max_single_trade_value']
        trade_value = trade['value']

        if trade_value > max_value:
            return ValidationResult(
                approved=False,
                reason=f"Trade value ${trade_value:,.2f} exceeds max ${max_value:,.2f}",
                limit_type="SINGLE_TRADE_VALUE",
                current_value=trade_value,
                limit_value=max_value
            )

        return ValidationResult(
            approved=True,
            reason="Trade value within limit",
            limit_type="NONE",
            current_value=trade_value,
            limit_value=max_value
        )

    def _check_position_size(self, trade: Dict, account_info: Dict) -> ValidationResult:
        """Check if position size exceeds max percentage of portfolio"""
        max_pct = self.limits['position_limits']['max_position_size_pct']
        equity = account_info['equity']
        trade_value = trade['value']

        position_pct = trade_value / equity

        if position_pct > max_pct:
            return ValidationResult(
                approved=False,
                reason=f"Position size {position_pct:.2%} exceeds max {max_pct:.2%}",
                limit_type="POSITION_SIZE",
                current_value=position_pct,
                limit_value=max_pct
            )

        return ValidationResult(
            approved=True,
            reason="Position size within limit",
            limit_type="NONE",
            current_value=position_pct,
            limit_value=max_pct
        )

    def _check_total_exposure(self, trade: Dict, account_info: Dict) -> ValidationResult:
        """Check if total exposure (including this trade) exceeds limit"""
        max_exposure = self.limits['position_limits']['max_total_exposure_pct']
        equity = account_info['equity']

        # Calculate current exposure
        current_exposure = sum(
            abs(float(pos['market_value']))
            for pos in account_info.get('positions', [])
        )

        # Add new trade
        new_exposure = current_exposure + trade['value']
        exposure_pct = new_exposure / equity

        if exposure_pct > max_exposure:
            return ValidationResult(
                approved=False,
                reason=f"Total exposure {exposure_pct:.2%} would exceed max {max_exposure:.2%}",
                limit_type="TOTAL_EXPOSURE",
                current_value=exposure_pct,
                limit_value=max_exposure
            )

        return ValidationResult(
            approved=True,
            reason="Total exposure within limit",
            limit_type="NONE",
            current_value=exposure_pct,
            limit_value=max_exposure
        )

    def _check_cash_reserve(self, trade: Dict, account_info: Dict) -> ValidationResult:
        """Check if cash reserve would fall below minimum"""
        min_cash_pct = self.limits['position_limits']['min_cash_reserve_pct']
        equity = account_info['equity']
        cash = account_info['cash']

        # Calculate cash after trade
        cash_after = cash - trade['value']
        cash_pct = cash_after / equity

        if cash_pct < min_cash_pct:
            return ValidationResult(
                approved=False,
                reason=f"Cash reserve {cash_pct:.2%} would fall below min {min_cash_pct:.2%}",
                limit_type="CASH_RESERVE",
                current_value=cash_pct,
                limit_value=min_cash_pct
            )

        return ValidationResult(
            approved=True,
            reason="Cash reserve adequate",
            limit_type="NONE",
            current_value=cash_pct,
            limit_value=min_cash_pct
        )

    def _check_daily_loss_limit(self, trade_history: List[Dict], account_info: Dict) -> ValidationResult:
        """Check if daily losses exceed limit"""
        max_loss_dollars = self.limits['daily_limits']['max_loss_dollars']
        max_loss_pct = self.limits['daily_limits']['max_loss_pct']
        equity = account_info['equity']

        # Get today's trades
        today = datetime.now().strftime('%Y-%m-%d')
        today_trades = [t for t in trade_history if t.get('date') == today]

        # Calculate today's P&L
        daily_pnl = sum(t.get('pnl', 0.0) for t in today_trades)

        # Check dollar limit
        if daily_pnl < -max_loss_dollars:
            return ValidationResult(
                approved=False,
                reason=f"Daily loss ${abs(daily_pnl):,.2f} exceeds limit ${max_loss_dollars:,.2f}",
                limit_type="DAILY_LOSS_DOLLARS",
                current_value=abs(daily_pnl),
                limit_value=max_loss_dollars
            )

        # Check percentage limit
        loss_pct = abs(daily_pnl) / equity if equity > 0 else 0

        if loss_pct > max_loss_pct:
            return ValidationResult(
                approved=False,
                reason=f"Daily loss {loss_pct:.2%} exceeds limit {max_loss_pct:.2%}",
                limit_type="DAILY_LOSS_PCT",
                current_value=loss_pct,
                limit_value=max_loss_pct
            )

        return ValidationResult(
            approved=True,
            reason="Daily loss within limits",
            limit_type="NONE",
            current_value=loss_pct,
            limit_value=max_loss_pct
        )

    def _check_drawdown_limit(self, account_info: Dict, trade_history: List[Dict]) -> ValidationResult:
        """Check if portfolio drawdown exceeds limit"""
        max_drawdown_pct = self.limits['drawdown_limits']['max_drawdown_from_peak_pct']
        stop_below_balance = self.limits['drawdown_limits']['stop_trading_if_below_balance']

        equity = account_info['equity']

        # Calculate peak equity from history
        peak_equity = equity
        for trade in trade_history:
            if 'equity_after' in trade:
                peak_equity = max(peak_equity, trade['equity_after'])

        # Calculate drawdown
        drawdown = (peak_equity - equity) / peak_equity if peak_equity > 0 else 0

        if drawdown > max_drawdown_pct:
            return ValidationResult(
                approved=False,
                reason=f"Drawdown {drawdown:.2%} exceeds max {max_drawdown_pct:.2%}",
                limit_type="DRAWDOWN_PCT",
                current_value=drawdown,
                limit_value=max_drawdown_pct
            )

        # Check absolute balance floor
        if equity < stop_below_balance:
            return ValidationResult(
                approved=False,
                reason=f"Equity ${equity:,.2f} below floor ${stop_below_balance:,.2f}",
                limit_type="BALANCE_FLOOR",
                current_value=equity,
                limit_value=stop_below_balance
            )

        return ValidationResult(
            approved=True,
            reason="Drawdown within limits",
            limit_type="NONE",
            current_value=drawdown,
            limit_value=max_drawdown_pct
        )

    def _check_consecutive_losses(self, trade_history: List[Dict]) -> ValidationResult:
        """Check for consecutive losing trades"""
        max_consecutive = self.limits['consecutive_loss_limits']['max_consecutive_losses']

        # Count consecutive losses
        consecutive_losses = 0
        for trade in reversed(trade_history):
            if trade.get('pnl', 0) < 0:
                consecutive_losses += 1
            else:
                break

        if consecutive_losses >= max_consecutive:
            return ValidationResult(
                approved=False,
                reason=f"{consecutive_losses} consecutive losses exceeds max {max_consecutive}",
                limit_type="CONSECUTIVE_LOSSES",
                current_value=consecutive_losses,
                limit_value=max_consecutive
            )

        return ValidationResult(
            approved=True,
            reason="No excessive consecutive losses",
            limit_type="NONE",
            current_value=consecutive_losses,
            limit_value=max_consecutive
        )

    def _check_daily_trade_count(self, trade_history: List[Dict]) -> ValidationResult:
        """Check if daily trade count exceeds limit"""
        max_trades = self.limits['daily_limits']['max_trades']

        # Get today's trades
        today = datetime.now().strftime('%Y-%m-%d')
        today_trades = [t for t in trade_history if t.get('date') == today]

        trade_count = len(today_trades)

        if trade_count >= max_trades:
            return ValidationResult(
                approved=False,
                reason=f"Daily trade count {trade_count} exceeds max {max_trades}",
                limit_type="DAILY_TRADE_COUNT",
                current_value=trade_count,
                limit_value=max_trades
            )

        return ValidationResult(
            approved=True,
            reason="Daily trade count within limit",
            limit_type="NONE",
            current_value=trade_count,
            limit_value=max_trades
        )

    def requires_manual_approval(self, trade: Dict) -> bool:
        """Check if trade requires manual approval"""
        threshold = self.limits['trade_limits']['require_manual_approval_above']
        return trade['value'] > threshold

    def get_approval_message(self, trade: Dict) -> str:
        """Generate manual approval message"""
        return (
            f"\n{'='*70}\n"
            f"MANUAL APPROVAL REQUIRED\n"
            f"{'='*70}\n"
            f"Trade: {trade['action']} {trade['quantity']} {trade['symbol']}\n"
            f"Price: ${trade['price']:,.2f}\n"
            f"Value: ${trade['value']:,.2f}\n"
            f"\nThis trade exceeds the manual approval threshold of "
            f"${self.limits['trade_limits']['require_manual_approval_above']:,.2f}\n"
            f"\nType 'APPROVE' to proceed, or anything else to cancel: "
        )


def validate_trade_safe(
    trade: Dict,
    account_info: Dict,
    trade_history: List[Dict],
    config_path: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Convenience function for simple validation

    Args:
        trade: Trade dict
        account_info: Account info dict
        trade_history: List of recent trades
        config_path: Optional path to config file

    Returns:
        (approved: bool, reason: str)
    """
    validator = RiskValidator(config_path=config_path)
    result = validator.validate_trade(trade, account_info, trade_history)
    return result.approved, result.reason


if __name__ == "__main__":
    # Example usage
    print("\nRisk Validator - Example Usage\n" + "="*70)

    # Example trade
    trade = {
        'symbol': 'AAPL',
        'action': 'BUY',
        'quantity': 10,
        'price': 175.0,
        'value': 1750.0
    }

    # Example account info
    account_info = {
        'equity': 20000.0,
        'cash': 15000.0,
        'buying_power': 15000.0,
        'positions': []
    }

    # Example trade history
    trade_history = []

    # Validate
    validator = RiskValidator()
    result = validator.validate_trade(trade, account_info, trade_history)

    print(f"\nTrade: {trade}")
    print(f"\nValidation Result:")
    print(f"  Approved: {result.approved}")
    print(f"  Reason: {result.reason}")

    if result.approved:
        print("\n[OK] Trade approved for execution")
    else:
        print(f"\n[REJECT] Trade rejected: {result.reason}")
        print(f"  Limit Type: {result.limit_type}")
        print(f"  Current: {result.current_value}")
        print(f"  Limit: {result.limit_value}")
