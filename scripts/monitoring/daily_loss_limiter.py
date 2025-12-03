#!/usr/bin/env python3
"""
Daily Loss Limiter - PROD-023
Tracks daily P&L and blocks trading if loss exceeds threshold.

Features:
- Tracks opening portfolio value at market open
- Calculates real-time daily P&L
- Blocks trading if daily loss exceeds configured threshold
- Sends Telegram alerts when trading is halted
- Resets automatically at next market open

Usage:
- Import check_daily_loss_limit() before executing trades
- Returns (can_trade: bool, reason: str)
"""

import os
import sys
import json
import requests
from datetime import datetime, time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

load_dotenv()

# Configuration - Max daily loss as percentage of portfolio
MAX_DAILY_LOSS_PCT = {
    "DEE-BOT": 3.0,           # 3% max daily loss ($3K on $100K)
    "SHORGAN Paper": 5.0,     # 5% max daily loss ($5K on $100K) - more aggressive
    "SHORGAN Live": 5.0       # 5% max daily loss ($150 on $3K)
}

# Absolute dollar limits (whichever is hit first)
MAX_DAILY_LOSS_DOLLARS = {
    "DEE-BOT": 3000.0,        # $3K max daily loss
    "SHORGAN Paper": 5000.0,  # $5K max daily loss
    "SHORGAN Live": 150.0     # $150 max daily loss (protect small account)
}

DAILY_STATE_FILE = project_root / "data" / "daily_loss_state.json"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Account credentials
ACCOUNTS = {
    "DEE-BOT": {
        "api_key": os.getenv("ALPACA_API_KEY_DEE"),
        "secret_key": os.getenv("ALPACA_SECRET_KEY_DEE"),
        "paper": True
    },
    "SHORGAN Paper": {
        "api_key": os.getenv("ALPACA_API_KEY_SHORGAN"),
        "secret_key": os.getenv("ALPACA_SECRET_KEY_SHORGAN"),
        "paper": True
    },
    "SHORGAN Live": {
        "api_key": os.getenv("ALPACA_API_KEY_SHORGAN_LIVE"),
        "secret_key": os.getenv("ALPACA_SECRET_KEY_SHORGAN_LIVE"),
        "paper": False
    }
}


def send_telegram_alert(message: str):
    """Send Telegram notification"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[WARNING] Telegram not configured: {message}")
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
        print(f"[ERROR] Failed to send Telegram alert: {e}")
        return False


def get_market_date() -> str:
    """Get current market date (for state tracking)"""
    now = datetime.now()
    # If before 4 AM, consider it previous day
    if now.hour < 4:
        from datetime import timedelta
        now = now - timedelta(days=1)
    return now.strftime("%Y-%m-%d")


def load_daily_state() -> dict:
    """Load daily state from file"""
    if DAILY_STATE_FILE.exists():
        try:
            with open(DAILY_STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load daily state: {e}")

    return {
        "date": None,
        "opening_values": {},
        "trading_halted": {},
        "alerts_sent": {}
    }


def save_daily_state(state: dict):
    """Save daily state to file"""
    DAILY_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DAILY_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def get_account_value(account_name: str, config: dict) -> float:
    """Get current portfolio value for an account"""
    try:
        client = TradingClient(
            config["api_key"],
            config["secret_key"],
            paper=config["paper"]
        )
        account = client.get_account()
        return float(account.portfolio_value)
    except Exception as e:
        print(f"[ERROR] Failed to get {account_name} value: {e}")
        return None


def check_daily_loss_limit(account_name: str) -> tuple:
    """
    Check if trading is allowed for an account based on daily loss limit.

    Returns:
        (can_trade: bool, reason: str)
    """
    if account_name not in ACCOUNTS:
        return True, "Unknown account - allowing trade"

    # Load state
    state = load_daily_state()
    today = get_market_date()

    # Reset state if new day
    if state.get("date") != today:
        print(f"[INFO] New trading day - resetting daily loss tracking")
        state = {
            "date": today,
            "opening_values": {},
            "trading_halted": {},
            "alerts_sent": {}
        }

    # Check if trading already halted for this account today
    if state["trading_halted"].get(account_name, False):
        return False, f"Trading halted for {account_name} - daily loss limit hit"

    # Get current value
    config = ACCOUNTS[account_name]
    current_value = get_account_value(account_name, config)
    if current_value is None:
        return True, "Could not get account value - allowing trade (with caution)"

    # Set opening value if not set
    if account_name not in state["opening_values"]:
        state["opening_values"][account_name] = current_value
        save_daily_state(state)
        print(f"[INFO] Set opening value for {account_name}: ${current_value:,.2f}")
        return True, "Opening value recorded"

    opening_value = state["opening_values"][account_name]

    # Calculate daily P&L
    daily_pnl = current_value - opening_value
    daily_pnl_pct = (daily_pnl / opening_value) * 100 if opening_value > 0 else 0

    # Check limits
    max_loss_pct = MAX_DAILY_LOSS_PCT.get(account_name, 5.0)
    max_loss_dollars = MAX_DAILY_LOSS_DOLLARS.get(account_name, 5000.0)

    loss_pct_exceeded = daily_pnl_pct <= -max_loss_pct
    loss_dollars_exceeded = daily_pnl <= -max_loss_dollars

    if loss_pct_exceeded or loss_dollars_exceeded:
        # Halt trading
        state["trading_halted"][account_name] = True
        save_daily_state(state)

        # Build reason
        if loss_pct_exceeded:
            reason = f"Daily loss {daily_pnl_pct:.2f}% exceeds {max_loss_pct}% limit"
        else:
            reason = f"Daily loss ${abs(daily_pnl):,.2f} exceeds ${max_loss_dollars:,.2f} limit"

        # Send alert if not already sent
        if not state["alerts_sent"].get(account_name, False):
            message = (
                f"🛑 <b>TRADING HALTED</b>\n\n"
                f"<b>{account_name}</b>\n"
                f"Opening Value: ${opening_value:,.2f}\n"
                f"Current Value: ${current_value:,.2f}\n"
                f"Daily P&L: ${daily_pnl:,.2f} ({daily_pnl_pct:+.2f}%)\n\n"
                f"<b>Reason:</b> {reason}\n\n"
                f"Trading disabled until tomorrow.\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}"
            )
            send_telegram_alert(message)
            state["alerts_sent"][account_name] = True
            save_daily_state(state)

        return False, reason

    # Trading allowed
    return True, f"Daily P&L: ${daily_pnl:,.2f} ({daily_pnl_pct:+.2f}%) - within limits"


def check_all_accounts():
    """Check daily loss limits for all accounts"""
    print("=" * 60)
    print("DAILY LOSS LIMIT CHECK")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    state = load_daily_state()
    today = get_market_date()

    # Reset if new day
    if state.get("date") != today:
        print(f"\n[NEW DAY] Resetting state for {today}")
        state = {
            "date": today,
            "opening_values": {},
            "trading_halted": {},
            "alerts_sent": {}
        }
        save_daily_state(state)

    results = {}

    for account_name, config in ACCOUNTS.items():
        print(f"\n{account_name}:")

        current_value = get_account_value(account_name, config)
        if current_value is None:
            print("  [ERROR] Could not get account value")
            continue

        # Set opening if needed
        if account_name not in state["opening_values"]:
            state["opening_values"][account_name] = current_value
            print(f"  Opening Value: ${current_value:,.2f} (just set)")

        opening = state["opening_values"][account_name]
        daily_pnl = current_value - opening
        daily_pnl_pct = (daily_pnl / opening) * 100 if opening > 0 else 0

        print(f"  Opening Value:  ${opening:,.2f}")
        print(f"  Current Value:  ${current_value:,.2f}")
        print(f"  Daily P&L:      ${daily_pnl:,.2f} ({daily_pnl_pct:+.2f}%)")
        print(f"  Max Loss:       {MAX_DAILY_LOSS_PCT.get(account_name, 5.0)}% or ${MAX_DAILY_LOSS_DOLLARS.get(account_name, 5000):,.0f}")

        can_trade, reason = check_daily_loss_limit(account_name)
        status = "ALLOWED" if can_trade else "HALTED"
        print(f"  Trading Status: {status}")

        results[account_name] = {
            "can_trade": can_trade,
            "daily_pnl": daily_pnl,
            "daily_pnl_pct": daily_pnl_pct
        }

    save_daily_state(state)

    print("\n" + "=" * 60)
    print("Daily loss limit check complete")
    print("=" * 60)

    return results


def reset_for_testing():
    """Reset state for testing purposes"""
    if DAILY_STATE_FILE.exists():
        DAILY_STATE_FILE.unlink()
    print("[INFO] Daily loss state reset")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_for_testing()
    else:
        check_all_accounts()
