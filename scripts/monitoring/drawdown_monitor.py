#!/usr/bin/env python3
"""
Drawdown Monitor - PROD-021
Monitors portfolio drawdown from peak and sends Telegram alerts when threshold exceeded.

Features:
- Tracks all-time high (ATH) for each account
- Alerts when drawdown exceeds configurable threshold (default 5%)
- Persists peak values to JSON for continuity
- Sends Telegram notifications with drawdown details
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

load_dotenv()

# Configuration
DRAWDOWN_THRESHOLD_PCT = 5.0  # Alert when drawdown exceeds this percentage
PEAK_TRACKING_FILE = project_root / "data" / "portfolio_peaks.json"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Account credentials
ACCOUNTS = {
    "DEE-BOT": {
        "api_key": os.getenv("ALPACA_API_KEY_DEE"),
        "secret_key": os.getenv("ALPACA_SECRET_KEY_DEE"),
        "paper": True,
        "initial_capital": 100000.0
    },
    "SHORGAN Paper": {
        "api_key": os.getenv("ALPACA_API_KEY_SHORGAN"),
        "secret_key": os.getenv("ALPACA_SECRET_KEY_SHORGAN"),
        "paper": True,
        "initial_capital": 100000.0
    },
    "SHORGAN Live": {
        "api_key": os.getenv("ALPACA_API_KEY_SHORGAN_LIVE"),
        "secret_key": os.getenv("ALPACA_SECRET_KEY_SHORGAN_LIVE"),
        "paper": False,
        "initial_capital": 3000.0
    }
}


def send_telegram_alert(message: str, is_critical: bool = False):
    """Send Telegram notification"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[WARNING] Telegram not configured: {message}")
        return False

    try:
        # Add alert emoji based on severity
        prefix = "🚨 CRITICAL DRAWDOWN ALERT" if is_critical else "⚠️ DRAWDOWN WARNING"
        full_message = f"{prefix}\n\n{message}"

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": full_message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram alert: {e}")
        return False


def load_peak_data() -> dict:
    """Load peak portfolio values from file"""
    if PEAK_TRACKING_FILE.exists():
        try:
            with open(PEAK_TRACKING_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load peak data: {e}")

    # Initialize with initial capital as starting peaks
    return {
        "peaks": {
            "DEE-BOT": 100000.0,
            "SHORGAN Paper": 100000.0,
            "SHORGAN Live": 3000.0,
            "Combined": 203000.0
        },
        "last_updated": None,
        "alert_history": []
    }


def save_peak_data(data: dict):
    """Save peak portfolio values to file"""
    PEAK_TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    with open(PEAK_TRACKING_FILE, 'w') as f:
        json.dump(data, f, indent=2)


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


def calculate_drawdown(current_value: float, peak_value: float) -> float:
    """Calculate drawdown percentage from peak"""
    if peak_value <= 0:
        return 0.0
    return ((peak_value - current_value) / peak_value) * 100


def check_drawdowns():
    """Main function to check all account drawdowns"""
    print("=" * 60)
    print("DRAWDOWN MONITOR")
    print(f"Threshold: {DRAWDOWN_THRESHOLD_PCT}%")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Load peak data
    peak_data = load_peak_data()
    peaks = peak_data["peaks"]

    # Track current values and alerts
    current_values = {}
    alerts = []

    # Check each account
    for account_name, config in ACCOUNTS.items():
        current_value = get_account_value(account_name, config)
        if current_value is None:
            continue

        current_values[account_name] = current_value
        peak = peaks.get(account_name, config["initial_capital"])

        # Update peak if current is higher
        if current_value > peak:
            peaks[account_name] = current_value
            peak = current_value
            print(f"[NEW PEAK] {account_name}: ${current_value:,.2f}")

        # Calculate drawdown
        drawdown = calculate_drawdown(current_value, peak)

        # Display status
        status = "OK" if drawdown < DRAWDOWN_THRESHOLD_PCT else "ALERT"
        print(f"\n{account_name}:")
        print(f"  Current:  ${current_value:,.2f}")
        print(f"  Peak:     ${peak:,.2f}")
        print(f"  Drawdown: {drawdown:.2f}% [{status}]")

        # Check if alert needed
        if drawdown >= DRAWDOWN_THRESHOLD_PCT:
            is_critical = drawdown >= (DRAWDOWN_THRESHOLD_PCT * 2)  # 10% = critical
            alerts.append({
                "account": account_name,
                "current": current_value,
                "peak": peak,
                "drawdown": drawdown,
                "is_critical": is_critical
            })

    # Calculate combined drawdown
    if current_values:
        combined_current = sum(current_values.values())
        combined_peak = peaks.get("Combined", sum(ACCOUNTS[a]["initial_capital"] for a in ACCOUNTS))

        if combined_current > combined_peak:
            peaks["Combined"] = combined_current
            combined_peak = combined_current

        combined_drawdown = calculate_drawdown(combined_current, combined_peak)

        print(f"\nCOMBINED PORTFOLIO:")
        print(f"  Current:  ${combined_current:,.2f}")
        print(f"  Peak:     ${combined_peak:,.2f}")
        print(f"  Drawdown: {combined_drawdown:.2f}%")

        if combined_drawdown >= DRAWDOWN_THRESHOLD_PCT:
            alerts.append({
                "account": "Combined Portfolio",
                "current": combined_current,
                "peak": combined_peak,
                "drawdown": combined_drawdown,
                "is_critical": combined_drawdown >= (DRAWDOWN_THRESHOLD_PCT * 2)
            })

    # Save updated peaks
    peak_data["peaks"] = peaks
    save_peak_data(peak_data)

    # Send alerts if needed
    if alerts:
        print("\n" + "=" * 60)
        print("SENDING ALERTS")
        print("=" * 60)

        for alert in alerts:
            message = (
                f"<b>{alert['account']}</b>\n"
                f"Current Value: ${alert['current']:,.2f}\n"
                f"Peak Value: ${alert['peak']:,.2f}\n"
                f"<b>Drawdown: {alert['drawdown']:.2f}%</b>\n"
                f"Threshold: {DRAWDOWN_THRESHOLD_PCT}%\n\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}"
            )

            if send_telegram_alert(message, alert["is_critical"]):
                print(f"[SENT] Alert for {alert['account']}")

            # Log to alert history
            peak_data["alert_history"].append({
                "timestamp": datetime.now().isoformat(),
                "account": alert["account"],
                "drawdown": alert["drawdown"]
            })

        # Keep only last 100 alerts in history
        peak_data["alert_history"] = peak_data["alert_history"][-100:]
        save_peak_data(peak_data)
    else:
        print("\n[OK] No drawdown alerts - all accounts within threshold")

    print("\n" + "=" * 60)
    print("Drawdown check complete")
    print("=" * 60)

    return len(alerts)


if __name__ == "__main__":
    check_drawdowns()
