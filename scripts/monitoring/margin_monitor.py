#!/usr/bin/env python3
"""
Margin Monitor for SHORGAN Live Account
Monitors margin usage and sends Telegram alerts when approaching dangerous levels.

Key metrics tracked:
- Margin usage % = maintenance_margin / equity
- Cash status (positive = cash, negative = using margin)
- Distance to margin call

Alert thresholds:
- WARNING: >50% margin usage
- HIGH: >70% margin usage
- CRITICAL: >85% margin usage (approaching margin call)
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
MARGIN_WARNING_PCT = 50.0   # Yellow alert
MARGIN_HIGH_PCT = 70.0      # Orange alert
MARGIN_CRITICAL_PCT = 85.0  # Red alert - close to margin call

STATUS_FILE = project_root / "data" / "margin_status.json"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# SHORGAN Live credentials
SHORGAN_LIVE_CONFIG = {
    "api_key": os.getenv("ALPACA_LIVE_API_KEY_SHORGAN"),
    "secret_key": os.getenv("ALPACA_LIVE_SECRET_KEY_SHORGAN"),
    "paper": False,
    "initial_capital": 3000.0
}


def send_telegram_alert(message: str, level: str = "WARNING"):
    """Send Telegram notification with appropriate emoji"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[WARNING] Telegram not configured: {message}")
        return False

    try:
        # Add emoji based on severity
        if level == "CRITICAL":
            prefix = "🚨 CRITICAL MARGIN ALERT"
        elif level == "HIGH":
            prefix = "🔴 HIGH MARGIN USAGE"
        elif level == "WARNING":
            prefix = "⚠️ MARGIN WARNING"
        else:
            prefix = "📊 MARGIN STATUS"

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


def load_status():
    """Load previous margin status for change detection"""
    if STATUS_FILE.exists():
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return {"last_alert_level": None, "last_check": None}


def save_status(status: dict):
    """Save current margin status"""
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)


def get_margin_metrics():
    """Get current margin metrics from SHORGAN Live account"""
    try:
        api = TradingClient(
            SHORGAN_LIVE_CONFIG["api_key"],
            SHORGAN_LIVE_CONFIG["secret_key"],
            paper=SHORGAN_LIVE_CONFIG["paper"]
        )
        account = api.get_account()

        # Extract key values (convert from strings to floats)
        equity = float(account.equity)
        maintenance_margin = float(account.maintenance_margin)
        initial_margin = float(account.initial_margin)
        cash = float(account.cash)
        buying_power = float(account.buying_power)
        long_value = float(account.long_market_value)
        short_value = float(account.short_market_value) if account.short_market_value else 0

        # Calculate margin usage percentage
        # Margin usage = maintenance_margin / equity
        margin_usage_pct = (maintenance_margin / equity * 100) if equity > 0 else 0

        # Distance to margin call (when margin_usage approaches 100%)
        margin_cushion = equity - maintenance_margin
        margin_cushion_pct = (margin_cushion / equity * 100) if equity > 0 else 0

        return {
            "equity": equity,
            "maintenance_margin": maintenance_margin,
            "initial_margin": initial_margin,
            "cash": cash,
            "buying_power": buying_power,
            "long_value": long_value,
            "short_value": short_value,
            "margin_usage_pct": margin_usage_pct,
            "margin_cushion": margin_cushion,
            "margin_cushion_pct": margin_cushion_pct,
            "using_margin": cash < 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"[ERROR] Failed to get margin metrics: {e}")
        return None


def determine_alert_level(margin_usage_pct: float) -> str:
    """Determine alert level based on margin usage"""
    if margin_usage_pct >= MARGIN_CRITICAL_PCT:
        return "CRITICAL"
    elif margin_usage_pct >= MARGIN_HIGH_PCT:
        return "HIGH"
    elif margin_usage_pct >= MARGIN_WARNING_PCT:
        return "WARNING"
    return "OK"


def format_margin_report(metrics: dict, alert_level: str) -> str:
    """Format margin metrics for Telegram message"""
    cash_status = "USING MARGIN" if metrics["using_margin"] else "CASH POSITIVE"

    report = f"""<b>SHORGAN Live Margin Status</b>

<b>Margin Usage:</b> {metrics['margin_usage_pct']:.1f}%
<b>Alert Level:</b> {alert_level}

<b>Account Metrics:</b>
• Equity: ${metrics['equity']:,.2f}
• Maintenance Margin: ${metrics['maintenance_margin']:,.2f}
• Cash: ${metrics['cash']:,.2f} ({cash_status})
• Buying Power: ${metrics['buying_power']:,.2f}

<b>Position Values:</b>
• Long Positions: ${metrics['long_value']:,.2f}
• Short Positions: ${metrics['short_value']:,.2f}

<b>Safety Margin:</b>
• Cushion to Margin Call: ${metrics['margin_cushion']:,.2f}
• Cushion %: {metrics['margin_cushion_pct']:.1f}%

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}</i>"""

    return report


def check_margin():
    """Main function to check margin and send alerts if needed"""
    print(f"\n{'='*60}")
    print(f"MARGIN MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    # Get current metrics
    metrics = get_margin_metrics()
    if not metrics:
        print("[ERROR] Could not retrieve margin metrics")
        return False

    # Determine alert level
    alert_level = determine_alert_level(metrics["margin_usage_pct"])

    # Print status
    print(f"\nMargin Usage: {metrics['margin_usage_pct']:.1f}%")
    print(f"Alert Level: {alert_level}")
    print(f"Equity: ${metrics['equity']:,.2f}")
    print(f"Maintenance Margin: ${metrics['maintenance_margin']:,.2f}")
    print(f"Cash: ${metrics['cash']:,.2f}")
    print(f"Margin Cushion: ${metrics['margin_cushion']:,.2f} ({metrics['margin_cushion_pct']:.1f}%)")

    # Load previous status
    prev_status = load_status()
    prev_alert_level = prev_status.get("last_alert_level") or "OK"

    # Decide if we should send alert
    should_alert = False

    # Alert if level increased (got worse)
    level_order = ["OK", "WARNING", "HIGH", "CRITICAL"]
    if level_order.index(alert_level) > level_order.index(prev_alert_level):
        should_alert = True
        print(f"\n[ALERT] Margin level INCREASED: {prev_alert_level} -> {alert_level}")

    # Also alert if CRITICAL (always)
    if alert_level == "CRITICAL":
        should_alert = True
        print(f"\n[ALERT] CRITICAL margin level - immediate attention required!")

    # Send alert if needed
    if should_alert and alert_level != "OK":
        report = format_margin_report(metrics, alert_level)
        success = send_telegram_alert(report, alert_level)
        if success:
            print(f"[TELEGRAM] Alert sent successfully")
        else:
            print(f"[TELEGRAM] Failed to send alert")
    elif alert_level != "OK":
        print(f"\n[INFO] Alert level unchanged at {alert_level} - no new alert sent")
    else:
        print(f"\n[OK] Margin usage within safe limits")

    # Save current status
    save_status({
        "last_alert_level": alert_level,
        "last_check": datetime.now().isoformat(),
        "metrics": metrics
    })

    return True


def get_margin_summary() -> dict:
    """Get margin summary for inclusion in other reports"""
    metrics = get_margin_metrics()
    if not metrics:
        return None

    alert_level = determine_alert_level(metrics["margin_usage_pct"])

    return {
        "margin_usage_pct": metrics["margin_usage_pct"],
        "alert_level": alert_level,
        "equity": metrics["equity"],
        "cash": metrics["cash"],
        "using_margin": metrics["using_margin"],
        "margin_cushion_pct": metrics["margin_cushion_pct"]
    }


if __name__ == "__main__":
    check_margin()
