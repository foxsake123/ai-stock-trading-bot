#!/usr/bin/env python3
"""
Trade Execution Alerts - PROD-003
Sends detailed Telegram alerts for trade executions.

Features:
- Per-trade alerts with fill price, quantity, total cost
- Daily summary with all trades executed
- P&L tracking for existing positions
- Integration with execute_daily_trades.py

Usage:
    from scripts.monitoring.trade_alerts import TradeAlertManager

    alert_mgr = TradeAlertManager()
    alert_mgr.send_trade_alert(account, symbol, action, qty, fill_price)
    alert_mgr.send_daily_summary()
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TRADE_LOG_FILE = project_root / "data" / "trade_execution_log.json"


class TradeAlertManager:
    """Manages trade execution alerts and logging"""

    def __init__(self):
        self.trades_today: List[Dict] = []
        self.load_todays_trades()

    def load_todays_trades(self):
        """Load today's trades from log file"""
        today = datetime.now().strftime("%Y-%m-%d")
        if TRADE_LOG_FILE.exists():
            try:
                with open(TRADE_LOG_FILE, 'r') as f:
                    data = json.load(f)
                    if data.get("date") == today:
                        self.trades_today = data.get("trades", [])
            except Exception:
                pass

    def save_trades(self):
        """Save trades to log file"""
        today = datetime.now().strftime("%Y-%m-%d")
        TRADE_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TRADE_LOG_FILE, 'w') as f:
            json.dump({
                "date": today,
                "trades": self.trades_today,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)

    def send_telegram(self, message: str) -> bool:
        """Send Telegram notification"""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print(f"[WARNING] Telegram not configured")
            return False

        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"[ERROR] Failed to send Telegram: {e}")
            return False

    def send_trade_alert(
        self,
        account: str,
        symbol: str,
        action: str,  # BUY, SELL
        qty: int,
        fill_price: float,
        order_type: str = "MARKET",
        stop_loss: Optional[float] = None,
        target: Optional[float] = None,
        conviction: Optional[str] = None,
        rationale: Optional[str] = None
    ) -> bool:
        """
        Send alert for a single trade execution.

        Args:
            account: Account name (DEE-BOT, SHORGAN Paper, SHORGAN Live)
            symbol: Stock symbol
            action: BUY or SELL
            qty: Number of shares
            fill_price: Actual fill price
            order_type: MARKET, LIMIT, etc.
            stop_loss: Stop loss price if set
            target: Target price if specified
            conviction: HIGH, MEDIUM, LOW
            rationale: Brief reason for trade
        """
        total_value = qty * fill_price

        # Emoji based on action
        emoji = "🟢" if action.upper() == "BUY" else "🔴"

        # Account emoji
        account_emoji = "💰" if "Live" in account else "📊"

        # Build message
        message = (
            f"{emoji} <b>TRADE EXECUTED</b>\n\n"
            f"{account_emoji} <b>{account}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>{action.upper()}</b> {symbol}\n"
            f"Shares: {qty:,}\n"
            f"Fill Price: ${fill_price:,.2f}\n"
            f"Total Value: ${total_value:,.2f}\n"
        )

        if stop_loss:
            stop_pct = abs((stop_loss - fill_price) / fill_price * 100)
            message += f"Stop Loss: ${stop_loss:,.2f} ({stop_pct:.1f}%)\n"

        if target:
            target_pct = abs((target - fill_price) / fill_price * 100)
            message += f"Target: ${target:,.2f} ({target_pct:.1f}%)\n"

        if conviction:
            message += f"Conviction: {conviction}\n"

        if rationale:
            # Truncate long rationale
            short_rationale = rationale[:100] + "..." if len(rationale) > 100 else rationale
            message += f"\n<i>{short_rationale}</i>\n"

        message += f"\n⏰ {datetime.now().strftime('%H:%M:%S ET')}"

        # Log trade
        trade_record = {
            "timestamp": datetime.now().isoformat(),
            "account": account,
            "symbol": symbol,
            "action": action.upper(),
            "qty": qty,
            "fill_price": fill_price,
            "total_value": total_value,
            "order_type": order_type,
            "stop_loss": stop_loss,
            "target": target,
            "conviction": conviction
        }
        self.trades_today.append(trade_record)
        self.save_trades()

        return self.send_telegram(message)

    def send_order_failed_alert(
        self,
        account: str,
        symbol: str,
        action: str,
        qty: int,
        reason: str
    ) -> bool:
        """Send alert when order fails"""
        message = (
            f"⚠️ <b>ORDER FAILED</b>\n\n"
            f"<b>{account}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{action.upper()} {qty} {symbol}\n"
            f"<b>Reason:</b> {reason}\n"
            f"\n⏰ {datetime.now().strftime('%H:%M:%S ET')}"
        )
        return self.send_telegram(message)

    def send_daily_summary(self) -> bool:
        """Send end-of-day summary of all trades"""
        if not self.trades_today:
            return self.send_telegram(
                "📋 <b>DAILY TRADE SUMMARY</b>\n\n"
                "No trades executed today.\n"
                f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M ET')}"
            )

        # Group by account
        by_account: Dict[str, List[Dict]] = {}
        for trade in self.trades_today:
            account = trade["account"]
            if account not in by_account:
                by_account[account] = []
            by_account[account].append(trade)

        # Build summary
        message = f"📋 <b>DAILY TRADE SUMMARY</b>\n"
        message += f"{datetime.now().strftime('%Y-%m-%d')}\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        total_bought = 0
        total_sold = 0

        for account, trades in by_account.items():
            account_emoji = "💰" if "Live" in account else "📊"
            message += f"{account_emoji} <b>{account}</b>\n"

            account_bought = 0
            account_sold = 0

            for trade in trades:
                emoji = "🟢" if trade["action"] == "BUY" else "🔴"
                message += f"  {emoji} {trade['action']} {trade['qty']} {trade['symbol']} @ ${trade['fill_price']:,.2f}\n"

                if trade["action"] == "BUY":
                    account_bought += trade["total_value"]
                else:
                    account_sold += trade["total_value"]

            message += f"  Bought: ${account_bought:,.2f} | Sold: ${account_sold:,.2f}\n\n"
            total_bought += account_bought
            total_sold += account_sold

        message += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"<b>Total Bought:</b> ${total_bought:,.2f}\n"
        message += f"<b>Total Sold:</b> ${total_sold:,.2f}\n"
        message += f"<b>Net Flow:</b> ${total_sold - total_bought:,.2f}\n"
        message += f"<b>Trades:</b> {len(self.trades_today)}\n"
        message += f"\n⏰ {datetime.now().strftime('%H:%M ET')}"

        return self.send_telegram(message)

    def send_execution_start_alert(self, accounts: List[str], trade_count: int) -> bool:
        """Send alert when trade execution begins"""
        message = (
            f"🚀 <b>TRADE EXECUTION STARTING</b>\n\n"
            f"Accounts: {', '.join(accounts)}\n"
            f"Trades to execute: {trade_count}\n"
            f"\n⏰ {datetime.now().strftime('%H:%M:%S ET')}"
        )
        return self.send_telegram(message)

    def send_execution_complete_alert(self, filled: int, failed: int, total: int) -> bool:
        """Send alert when trade execution completes"""
        if failed == 0:
            status = "✅"
            status_text = "All trades successful"
        elif filled == 0:
            status = "❌"
            status_text = "All trades failed"
        else:
            status = "⚠️"
            status_text = "Partial execution"

        message = (
            f"{status} <b>EXECUTION COMPLETE</b>\n\n"
            f"<b>{status_text}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Filled: {filled}/{total}\n"
            f"Failed: {failed}/{total}\n"
            f"\n⏰ {datetime.now().strftime('%H:%M:%S ET')}"
        )
        return self.send_telegram(message)


# Convenience functions for direct use
_alert_manager: Optional[TradeAlertManager] = None


def get_alert_manager() -> TradeAlertManager:
    """Get or create the global alert manager"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = TradeAlertManager()
    return _alert_manager


def send_trade_alert(account: str, symbol: str, action: str, qty: int, fill_price: float, **kwargs) -> bool:
    """Convenience function to send trade alert"""
    return get_alert_manager().send_trade_alert(account, symbol, action, qty, fill_price, **kwargs)


def send_order_failed(account: str, symbol: str, action: str, qty: int, reason: str) -> bool:
    """Convenience function to send order failed alert"""
    return get_alert_manager().send_order_failed_alert(account, symbol, action, qty, reason)


def send_daily_summary() -> bool:
    """Convenience function to send daily summary"""
    return get_alert_manager().send_daily_summary()


if __name__ == "__main__":
    # Test the alert system
    print("Testing Trade Alert System...")

    mgr = TradeAlertManager()

    # Test trade alert
    print("\nSending test trade alert...")
    mgr.send_trade_alert(
        account="DEE-BOT",
        symbol="AAPL",
        action="BUY",
        qty=10,
        fill_price=175.50,
        stop_loss=157.95,
        target=200.00,
        conviction="HIGH",
        rationale="Strong earnings momentum, AI services growth"
    )

    # Test daily summary
    print("\nSending test daily summary...")
    mgr.send_daily_summary()

    print("\nDone!")
