#!/usr/bin/env python3
"""
Regulatory Compliance Module
============================
Ensures all trades comply with US securities regulations:
1. Pattern Day Trading (PDT) Rule - FINRA Rule 4210
2. Wash Sale Rule - IRS Section 1091
3. Free-Riding - Regulation T
4. Good Faith Violations - Regulation T

Author: AI Trading Bot System
Date: December 4, 2025
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")


class ViolationType(Enum):
    """Types of regulatory violations"""
    PDT = "Pattern Day Trading"
    WASH_SALE = "Wash Sale"
    FREE_RIDING = "Free-Riding"
    GOOD_FAITH = "Good Faith Violation"


@dataclass
class TradeRecord:
    """Record of a single trade for compliance tracking"""
    symbol: str
    action: str  # BUY, SELL, SHORT, COVER
    qty: float
    price: float
    timestamp: datetime
    account: str
    order_id: str = ""


@dataclass
class ComplianceCheck:
    """Result of a compliance check"""
    passed: bool
    violation_type: Optional[ViolationType] = None
    message: str = ""
    details: Dict = field(default_factory=dict)


class RegulatoryComplianceChecker:
    """
    Checks trades for regulatory compliance before execution.

    Regulations enforced:
    1. Pattern Day Trading (PDT) - FINRA Rule 4210
       - Accounts under $25K cannot make more than 3 day trades in 5 business days
       - Day trade = buy and sell same security same day

    2. Wash Sale Rule - IRS Section 1091
       - Cannot claim loss if you buy substantially identical security
         within 30 days before or after the sale
       - We prevent buying back within 30 days of selling at a loss

    3. Free-Riding - Regulation T
       - Cannot sell securities before paying for them (cash accounts)
       - Must wait for settlement (T+2 for stocks)

    4. Good Faith Violations - Regulation T
       - Cannot use unsettled funds to buy and sell before settlement
    """

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.data_dir = PROJECT_ROOT / "data" / "compliance"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Trade history file
        self.history_file = self.data_dir / "trade_history.json"
        self.wash_sale_file = self.data_dir / "wash_sale_tracking.json"

        # Load existing data
        self.trade_history = self._load_trade_history()
        self.wash_sale_tracking = self._load_wash_sale_tracking()

        # PDT thresholds
        self.PDT_THRESHOLD = 25000  # Minimum equity to avoid PDT restrictions
        self.PDT_DAY_TRADE_LIMIT = 3  # Max day trades in rolling 5 days for accounts < $25K
        self.PDT_ROLLING_DAYS = 5

        # Settlement period (T+2 for stocks)
        self.SETTLEMENT_DAYS = 2

        # Wash sale window (30 days before and after)
        self.WASH_SALE_WINDOW = 30

    def _load_trade_history(self) -> List[Dict]:
        """Load trade history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []

    def _save_trade_history(self):
        """Save trade history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.trade_history, f, indent=2, default=str)

    def _load_wash_sale_tracking(self) -> Dict:
        """Load wash sale tracking data"""
        if self.wash_sale_file.exists():
            try:
                with open(self.wash_sale_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_wash_sale_tracking(self):
        """Save wash sale tracking data"""
        with open(self.wash_sale_file, 'w') as f:
            json.dump(self.wash_sale_tracking, f, indent=2, default=str)

    def record_trade(self, trade: TradeRecord):
        """Record a trade for compliance tracking"""
        trade_data = {
            'symbol': trade.symbol,
            'action': trade.action,
            'qty': trade.qty,
            'price': trade.price,
            'timestamp': trade.timestamp.isoformat(),
            'account': trade.account,
            'order_id': trade.order_id
        }
        self.trade_history.append(trade_data)
        self._save_trade_history()

        # Update wash sale tracking if this was a sell at a loss
        if trade.action.upper() in ['SELL', 'SELL_TO_CLOSE']:
            self._update_wash_sale_tracking(trade)

    def _update_wash_sale_tracking(self, trade: TradeRecord):
        """Track sells for wash sale rule enforcement"""
        # We'd need cost basis to determine if it's a loss
        # For now, track all sells and let the check determine if wash sale applies
        key = f"{trade.account}:{trade.symbol}"

        if key not in self.wash_sale_tracking:
            self.wash_sale_tracking[key] = []

        self.wash_sale_tracking[key].append({
            'sell_date': trade.timestamp.isoformat(),
            'qty': trade.qty,
            'price': trade.price,
            'wash_sale_end': (trade.timestamp + timedelta(days=self.WASH_SALE_WINDOW)).isoformat()
        })

        self._save_wash_sale_tracking()

    def check_all_regulations(self, symbol: str, action: str, account: str,
                              account_value: float, is_margin_account: bool = False,
                              cost_basis: float = None, current_price: float = None) -> List[ComplianceCheck]:
        """
        Run all regulatory compliance checks for a proposed trade.

        Args:
            symbol: Stock ticker
            action: Trade action (BUY, SELL, SHORT, COVER)
            account: Account identifier
            account_value: Current account equity
            is_margin_account: Whether this is a margin account
            cost_basis: Average cost basis (for wash sale check)
            current_price: Current stock price

        Returns:
            List of ComplianceCheck results
        """
        checks = []

        # 1. Pattern Day Trading check
        pdt_check = self.check_pattern_day_trading(symbol, action, account, account_value)
        checks.append(pdt_check)

        # 2. Wash Sale check (only for buys)
        if action.upper() in ['BUY', 'BUY_TO_OPEN', 'BUY_TO_COVER']:
            wash_check = self.check_wash_sale(symbol, account, cost_basis, current_price)
            checks.append(wash_check)

        # 3. Free-Riding check (only for cash accounts)
        if not is_margin_account:
            free_riding_check = self.check_free_riding(symbol, action, account)
            checks.append(free_riding_check)

        # 4. Good Faith Violation check (only for cash accounts)
        if not is_margin_account:
            gfv_check = self.check_good_faith_violation(symbol, action, account)
            checks.append(gfv_check)

        return checks

    def check_pattern_day_trading(self, symbol: str, action: str, account: str,
                                   account_value: float) -> ComplianceCheck:
        """
        Check for Pattern Day Trading (PDT) rule violation.

        FINRA Rule 4210:
        - Accounts with less than $25,000 equity are limited to 3 day trades
          in any rolling 5 business day period
        - A day trade is buying and selling the same security on the same day

        Args:
            symbol: Stock ticker
            action: Trade action
            account: Account identifier
            account_value: Current account equity

        Returns:
            ComplianceCheck result
        """
        # If account is above PDT threshold, no restrictions
        if account_value >= self.PDT_THRESHOLD:
            return ComplianceCheck(
                passed=True,
                message=f"Account equity ${account_value:,.2f} >= ${self.PDT_THRESHOLD:,} PDT threshold"
            )

        # Count day trades in the last 5 business days
        today = datetime.now().date()
        five_days_ago = today - timedelta(days=7)  # 7 calendar days to cover 5 business days

        day_trades = self._count_day_trades(account, five_days_ago)

        # Check if this trade would create a day trade
        would_be_day_trade = self._would_be_day_trade(symbol, action, account)

        if would_be_day_trade:
            if day_trades >= self.PDT_DAY_TRADE_LIMIT:
                return ComplianceCheck(
                    passed=False,
                    violation_type=ViolationType.PDT,
                    message=f"PDT VIOLATION: Already have {day_trades} day trades in last 5 days. "
                            f"Account under ${self.PDT_THRESHOLD:,} limited to {self.PDT_DAY_TRADE_LIMIT}.",
                    details={
                        'day_trades_count': day_trades,
                        'limit': self.PDT_DAY_TRADE_LIMIT,
                        'account_value': account_value,
                        'threshold': self.PDT_THRESHOLD
                    }
                )
            else:
                return ComplianceCheck(
                    passed=True,
                    message=f"Day trade allowed: {day_trades}/{self.PDT_DAY_TRADE_LIMIT} day trades used. "
                            f"WARNING: Account under ${self.PDT_THRESHOLD:,}",
                    details={
                        'day_trades_count': day_trades,
                        'remaining': self.PDT_DAY_TRADE_LIMIT - day_trades - 1
                    }
                )

        return ComplianceCheck(
            passed=True,
            message="Not a day trade - no PDT concern"
        )

    def _count_day_trades(self, account: str, since_date: datetime.date) -> int:
        """Count day trades for an account since a given date"""
        day_trades = 0

        # Group trades by date and symbol
        trades_by_day_symbol = {}

        for trade in self.trade_history:
            if trade['account'] != account:
                continue

            trade_date = datetime.fromisoformat(trade['timestamp']).date()
            if trade_date < since_date:
                continue

            key = f"{trade_date}:{trade['symbol']}"
            if key not in trades_by_day_symbol:
                trades_by_day_symbol[key] = {'buys': 0, 'sells': 0}

            if trade['action'].upper() in ['BUY', 'BUY_TO_OPEN', 'BUY_TO_COVER']:
                trades_by_day_symbol[key]['buys'] += 1
            elif trade['action'].upper() in ['SELL', 'SELL_TO_CLOSE', 'SELL_TO_OPEN']:
                trades_by_day_symbol[key]['sells'] += 1

        # Count day trades (both buy and sell on same day for same symbol)
        for key, counts in trades_by_day_symbol.items():
            if counts['buys'] > 0 and counts['sells'] > 0:
                day_trades += min(counts['buys'], counts['sells'])

        return day_trades

    def _would_be_day_trade(self, symbol: str, action: str, account: str) -> bool:
        """Check if this trade would constitute a day trade"""
        today = datetime.now().date()

        # Check if we have an opposite position trade today
        for trade in self.trade_history:
            if trade['account'] != account or trade['symbol'] != symbol:
                continue

            trade_date = datetime.fromisoformat(trade['timestamp']).date()
            if trade_date != today:
                continue

            # If we're selling and bought today, it's a day trade
            if action.upper() in ['SELL', 'SELL_TO_CLOSE'] and trade['action'].upper() in ['BUY', 'BUY_TO_OPEN']:
                return True

            # If we're buying and sold today, it's a day trade
            if action.upper() in ['BUY', 'BUY_TO_OPEN'] and trade['action'].upper() in ['SELL', 'SELL_TO_CLOSE']:
                return True

        return False

    def check_wash_sale(self, symbol: str, account: str,
                        cost_basis: float = None, current_price: float = None) -> ComplianceCheck:
        """
        Check for Wash Sale rule violation.

        IRS Section 1091:
        - Cannot claim a tax loss if you purchase substantially identical securities
          within 30 days before or after selling at a loss
        - We prevent buying back a security within 30 days of selling it at a loss

        Args:
            symbol: Stock ticker
            account: Account identifier
            cost_basis: Original cost basis (to determine if sold at loss)
            current_price: Current price

        Returns:
            ComplianceCheck result
        """
        key = f"{account}:{symbol}"

        if key not in self.wash_sale_tracking:
            return ComplianceCheck(
                passed=True,
                message="No recent sales of this security - no wash sale concern"
            )

        today = datetime.now()

        for sale in self.wash_sale_tracking[key]:
            wash_sale_end = datetime.fromisoformat(sale['wash_sale_end'])

            if today <= wash_sale_end:
                days_remaining = (wash_sale_end - today).days
                sell_date = datetime.fromisoformat(sale['sell_date']).strftime('%Y-%m-%d')

                return ComplianceCheck(
                    passed=False,
                    violation_type=ViolationType.WASH_SALE,
                    message=f"WASH SALE WARNING: {symbol} was sold on {sell_date}. "
                            f"Buying back within 30 days may trigger wash sale rule. "
                            f"Wait {days_remaining} more days to be safe.",
                    details={
                        'sell_date': sell_date,
                        'wash_sale_end': wash_sale_end.strftime('%Y-%m-%d'),
                        'days_remaining': days_remaining,
                        'sale_price': sale['price']
                    }
                )

        return ComplianceCheck(
            passed=True,
            message="Outside wash sale window - safe to trade"
        )

    def check_free_riding(self, symbol: str, action: str, account: str) -> ComplianceCheck:
        """
        Check for Free-Riding violation (cash accounts only).

        Regulation T:
        - Cannot sell securities before they are paid for
        - Must wait for settlement (T+2) before selling newly purchased shares

        Args:
            symbol: Stock ticker
            action: Trade action
            account: Account identifier

        Returns:
            ComplianceCheck result
        """
        if action.upper() not in ['SELL', 'SELL_TO_CLOSE']:
            return ComplianceCheck(
                passed=True,
                message="Not a sell order - no free-riding concern"
            )

        today = datetime.now()
        settlement_cutoff = today - timedelta(days=self.SETTLEMENT_DAYS)

        # Check for recent purchases of this symbol that haven't settled
        for trade in self.trade_history:
            if trade['account'] != account or trade['symbol'] != symbol:
                continue

            if trade['action'].upper() not in ['BUY', 'BUY_TO_OPEN']:
                continue

            trade_date = datetime.fromisoformat(trade['timestamp'])

            if trade_date > settlement_cutoff:
                settlement_date = trade_date + timedelta(days=self.SETTLEMENT_DAYS)
                days_until_settled = (settlement_date - today).days

                return ComplianceCheck(
                    passed=False,
                    violation_type=ViolationType.FREE_RIDING,
                    message=f"FREE-RIDING WARNING: {symbol} purchased on "
                            f"{trade_date.strftime('%Y-%m-%d')} has not settled. "
                            f"Wait {max(0, days_until_settled)} more days (settles {settlement_date.strftime('%Y-%m-%d')}).",
                    details={
                        'purchase_date': trade_date.strftime('%Y-%m-%d'),
                        'settlement_date': settlement_date.strftime('%Y-%m-%d'),
                        'days_until_settled': max(0, days_until_settled)
                    }
                )

        return ComplianceCheck(
            passed=True,
            message="No unsettled purchases - safe to sell"
        )

    def check_good_faith_violation(self, symbol: str, action: str, account: str) -> ComplianceCheck:
        """
        Check for Good Faith Violation (cash accounts only).

        Regulation T:
        - Cannot buy securities with unsettled funds and then sell before
          the original trade settles
        - Essentially using proceeds from unsettled trades to fund new trades

        Args:
            symbol: Stock ticker
            action: Trade action
            account: Account identifier

        Returns:
            ComplianceCheck result
        """
        # This is a simplified check - in reality would need to track cash flows
        # For now, we just warn if there's high trading activity in unsettled period

        today = datetime.now()
        settlement_cutoff = today - timedelta(days=self.SETTLEMENT_DAYS)

        unsettled_trades = 0
        for trade in self.trade_history:
            if trade['account'] != account:
                continue

            trade_date = datetime.fromisoformat(trade['timestamp'])
            if trade_date > settlement_cutoff:
                unsettled_trades += 1

        if unsettled_trades >= 4:  # Threshold for concern
            return ComplianceCheck(
                passed=True,  # Warning only, not blocking
                message=f"GOOD FAITH CAUTION: {unsettled_trades} trades in settlement period. "
                        f"Be careful not to trade with unsettled funds.",
                details={
                    'unsettled_trades': unsettled_trades,
                    'settlement_period_days': self.SETTLEMENT_DAYS
                }
            )

        return ComplianceCheck(
            passed=True,
            message="Low unsettled trade activity - no GFV concern"
        )

    def get_compliance_summary(self, account: str, account_value: float) -> Dict:
        """
        Get a summary of current compliance status for an account.

        Args:
            account: Account identifier
            account_value: Current account equity

        Returns:
            Dict with compliance summary
        """
        today = datetime.now().date()
        five_days_ago = today - timedelta(days=7)

        day_trades = self._count_day_trades(account, five_days_ago)
        is_pdt_restricted = account_value < self.PDT_THRESHOLD

        # Count wash sale restrictions
        wash_sale_restrictions = []
        for key, sales in self.wash_sale_tracking.items():
            if not key.startswith(f"{account}:"):
                continue
            symbol = key.split(":")[1]
            for sale in sales:
                wash_end = datetime.fromisoformat(sale['wash_sale_end'])
                if datetime.now() <= wash_end:
                    wash_sale_restrictions.append({
                        'symbol': symbol,
                        'sell_date': sale['sell_date'],
                        'restriction_ends': sale['wash_sale_end']
                    })

        return {
            'account': account,
            'account_value': account_value,
            'pdt_status': {
                'restricted': is_pdt_restricted,
                'day_trades_used': day_trades,
                'day_trades_remaining': max(0, self.PDT_DAY_TRADE_LIMIT - day_trades) if is_pdt_restricted else 'unlimited',
                'threshold': self.PDT_THRESHOLD
            },
            'wash_sale_restrictions': wash_sale_restrictions,
            'settlement_period': f"T+{self.SETTLEMENT_DAYS}"
        }

    def validate_trade_batch(self, trades: List[Dict], account: str,
                             account_value: float, is_margin: bool = False) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate a batch of trades and return approved/rejected lists.

        Args:
            trades: List of trade dicts with 'symbol', 'action', 'qty', 'price'
            account: Account identifier
            account_value: Current account equity
            is_margin: Whether this is a margin account

        Returns:
            Tuple of (approved_trades, rejected_trades)
        """
        approved = []
        rejected = []

        for trade in trades:
            checks = self.check_all_regulations(
                symbol=trade['symbol'],
                action=trade['action'],
                account=account,
                account_value=account_value,
                is_margin_account=is_margin
            )

            # Check if any critical violations
            violations = [c for c in checks if not c.passed and c.violation_type in
                         [ViolationType.PDT, ViolationType.FREE_RIDING]]

            # Wash sale is a warning (tax implication) not a hard block
            wash_sale_warnings = [c for c in checks if c.violation_type == ViolationType.WASH_SALE]

            if violations:
                trade['rejection_reason'] = violations[0].message
                trade['violation_type'] = violations[0].violation_type.value
                rejected.append(trade)
            else:
                if wash_sale_warnings:
                    trade['warning'] = wash_sale_warnings[0].message
                approved.append(trade)

        return approved, rejected


def integrate_with_execution(execute_func):
    """
    Decorator to add compliance checking to trade execution.

    Usage:
        @integrate_with_execution
        def execute_trade(symbol, action, qty, price, account):
            # execution logic
            pass
    """
    def wrapper(symbol, action, qty, price, account, account_value, is_margin=False, **kwargs):
        checker = RegulatoryComplianceChecker()

        checks = checker.check_all_regulations(
            symbol=symbol,
            action=action,
            account=account,
            account_value=account_value,
            is_margin_account=is_margin
        )

        # Check for blocking violations
        for check in checks:
            if not check.passed and check.violation_type in [ViolationType.PDT, ViolationType.FREE_RIDING]:
                print(f"[COMPLIANCE BLOCK] {check.message}")
                return None

        # Print warnings
        for check in checks:
            if check.violation_type == ViolationType.WASH_SALE:
                print(f"[COMPLIANCE WARNING] {check.message}")

        # Execute the trade
        result = execute_func(symbol, action, qty, price, account, **kwargs)

        # Record the trade if successful
        if result:
            checker.record_trade(TradeRecord(
                symbol=symbol,
                action=action,
                qty=qty,
                price=price,
                timestamp=datetime.now(),
                account=account,
                order_id=str(result) if result else ""
            ))

        return result

    return wrapper


# Standalone compliance check function for use in other modules
def check_trade_compliance(symbol: str, action: str, account: str,
                          account_value: float, is_margin: bool = False) -> Tuple[bool, str]:
    """
    Simple function to check if a trade is compliant.

    Args:
        symbol: Stock ticker
        action: Trade action
        account: Account identifier
        account_value: Account equity
        is_margin: Whether margin account

    Returns:
        Tuple of (is_compliant, message)
    """
    checker = RegulatoryComplianceChecker()
    checks = checker.check_all_regulations(
        symbol=symbol,
        action=action,
        account=account,
        account_value=account_value,
        is_margin_account=is_margin
    )

    for check in checks:
        if not check.passed and check.violation_type in [ViolationType.PDT, ViolationType.FREE_RIDING]:
            return False, check.message

    # Check for warnings
    warnings = [c.message for c in checks if c.violation_type == ViolationType.WASH_SALE]
    if warnings:
        return True, f"APPROVED WITH WARNING: {warnings[0]}"

    return True, "COMPLIANT"


def send_compliance_summary_telegram(accounts_data: List[Dict]) -> bool:
    """
    Send daily compliance summary to Telegram.

    Args:
        accounts_data: List of dicts with 'name', 'value', 'is_margin' for each account

    Returns:
        True if sent successfully
    """
    import requests

    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("[WARNING] Telegram credentials not configured")
        return False

    checker = RegulatoryComplianceChecker()

    # Build message
    today = datetime.now().strftime("%Y-%m-%d")
    message_lines = [
        f"📋 *COMPLIANCE STATUS - {today}*",
        ""
    ]

    all_clear = True

    for account in accounts_data:
        summary = checker.get_compliance_summary(
            account=account['name'],
            account_value=account['value']
        )

        pdt = summary['pdt_status']
        wash_sales = summary['wash_sale_restrictions']

        # Account header
        message_lines.append(f"*{account['name']}* (${account['value']:,.0f})")

        # PDT Status
        if pdt['restricted']:
            remaining = pdt['day_trades_remaining']
            if remaining == 0:
                message_lines.append(f"  ⚠️ PDT: {remaining}/3 day trades remaining")
                all_clear = False
            elif remaining <= 1:
                message_lines.append(f"  ⚡ PDT: {remaining}/3 day trades remaining")
            else:
                message_lines.append(f"  ✅ PDT: {remaining}/3 day trades remaining")
        else:
            message_lines.append(f"  ✅ PDT: Unrestricted (>${pdt['threshold']:,})")

        # Wash Sale Restrictions
        if wash_sales:
            message_lines.append(f"  ⚠️ Wash Sale: {len(wash_sales)} restrictions")
            for ws in wash_sales[:3]:  # Show first 3
                end_date = ws['restriction_ends'][:10]
                message_lines.append(f"      {ws['symbol']} until {end_date}")
            all_clear = False
        else:
            message_lines.append(f"  ✅ Wash Sale: No restrictions")

        message_lines.append("")

    # Summary
    if all_clear:
        message_lines.append("✅ *All accounts compliant*")
    else:
        message_lines.append("⚠️ *Review warnings above*")

    message = "\n".join(message_lines)

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        response = requests.post(url, json={
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        })

        if response.status_code == 200:
            print("[TELEGRAM] Compliance summary sent")
            return True
        else:
            print(f"[TELEGRAM ERROR] {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")
        return False


if __name__ == "__main__":
    # Test the compliance checker
    print("="*70)
    print("REGULATORY COMPLIANCE CHECKER - TEST")
    print("="*70)

    checker = RegulatoryComplianceChecker()

    # Test scenarios
    test_cases = [
        {
            'name': 'Small account day trade check',
            'symbol': 'AAPL',
            'action': 'SELL',
            'account': 'TEST-SMALL',
            'account_value': 15000,
            'is_margin': False
        },
        {
            'name': 'Large account (no PDT restriction)',
            'symbol': 'GOOGL',
            'action': 'BUY',
            'account': 'TEST-LARGE',
            'account_value': 100000,
            'is_margin': True
        },
        {
            'name': 'Wash sale check',
            'symbol': 'TSLA',
            'action': 'BUY',
            'account': 'TEST-WASH',
            'account_value': 50000,
            'is_margin': False
        }
    ]

    for test in test_cases:
        print(f"\n--- {test['name']} ---")
        checks = checker.check_all_regulations(
            symbol=test['symbol'],
            action=test['action'],
            account=test['account'],
            account_value=test['account_value'],
            is_margin_account=test['is_margin']
        )

        for check in checks:
            status = "PASS" if check.passed else "FAIL"
            print(f"  [{status}] {check.message}")

    print("\n" + "="*70)
    print("Compliance data stored in:", checker.data_dir)
    print("="*70)
