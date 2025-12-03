#!/usr/bin/env python3
"""
AI Stock Trading Bot - Comprehensive Web Dashboard
Provides real-time portfolio monitoring, performance tracking, and research viewing.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from flask import Flask, render_template, jsonify, send_file
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__,
            template_folder=str(PROJECT_ROOT / "scripts" / "dashboard" / "templates"),
            static_folder=str(PROJECT_ROOT / "scripts" / "dashboard" / "static"))

# Alpaca imports
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import GetOrdersRequest
    from alpaca.trading.enums import OrderSide, OrderStatus
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    logger.warning("Alpaca not available")


class TradingDashboard:
    """Dashboard data provider"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.data_dir = PROJECT_ROOT / "data"
        self.reports_dir = PROJECT_ROOT / "reports" / "premarket"

        # Initialize Alpaca clients
        self.clients = {}
        if ALPACA_AVAILABLE:
            self._init_alpaca_clients()

    def _init_alpaca_clients(self):
        """Initialize Alpaca trading clients"""
        # DEE-BOT Paper
        dee_key = os.getenv("ALPACA_PAPER_API_KEY")
        dee_secret = os.getenv("ALPACA_PAPER_SECRET_KEY")
        if dee_key and dee_secret:
            self.clients["DEE-BOT"] = TradingClient(dee_key, dee_secret, paper=True)

        # SHORGAN Paper
        shorgan_key = os.getenv("ALPACA_API_KEY_SHORGAN")
        shorgan_secret = os.getenv("ALPACA_SECRET_KEY_SHORGAN")
        if shorgan_key and shorgan_secret:
            self.clients["SHORGAN-Paper"] = TradingClient(shorgan_key, shorgan_secret, paper=True)

        # SHORGAN Live
        live_key = os.getenv("ALPACA_LIVE_API_KEY_SHORGAN") or os.getenv("ALPACA_API_KEY_SHORGAN_LIVE")
        live_secret = os.getenv("ALPACA_LIVE_SECRET_KEY_SHORGAN") or os.getenv("ALPACA_SECRET_KEY_SHORGAN_LIVE")
        if live_key and live_secret:
            self.clients["SHORGAN-Live"] = TradingClient(live_key, live_secret, paper=False)

    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary for all accounts"""
        summary = {
            "accounts": [],
            "total_value": 0,
            "total_pnl": 0,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Capital deployed for each account
        capital_deployed = {
            "DEE-BOT": 100000,
            "SHORGAN-Paper": 100000,
            "SHORGAN-Live": 3000  # User's deposits
        }

        for name, client in self.clients.items():
            try:
                account = client.get_account()
                value = float(account.portfolio_value)
                capital = capital_deployed.get(name, 100000)
                pnl = value - capital
                pnl_pct = (pnl / capital) * 100

                account_data = {
                    "name": name,
                    "value": value,
                    "cash": float(account.cash),
                    "buying_power": float(account.buying_power),
                    "capital_deployed": capital,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "is_live": "Live" in name
                }

                summary["accounts"].append(account_data)
                summary["total_value"] += value
                summary["total_pnl"] += pnl

            except Exception as e:
                logger.error(f"Error getting {name} account: {e}")
                summary["accounts"].append({
                    "name": name,
                    "error": str(e)
                })

        # Calculate total return
        total_capital = sum(capital_deployed.values())
        summary["total_return_pct"] = (summary["total_pnl"] / total_capital) * 100 if total_capital > 0 else 0

        return summary

    def get_positions(self, account_name: str = None) -> List[Dict]:
        """Get positions for specified account or all accounts"""
        all_positions = []

        clients_to_check = {account_name: self.clients[account_name]} if account_name else self.clients

        for name, client in clients_to_check.items():
            try:
                positions = client.get_all_positions()
                for pos in positions:
                    all_positions.append({
                        "account": name,
                        "symbol": pos.symbol,
                        "qty": float(pos.qty),
                        "avg_entry": float(pos.avg_entry_price),
                        "current_price": float(pos.current_price),
                        "market_value": float(pos.market_value),
                        "unrealized_pl": float(pos.unrealized_pl),
                        "unrealized_plpc": float(pos.unrealized_plpc) * 100,
                        "side": "long" if float(pos.qty) > 0 else "short"
                    })
            except Exception as e:
                logger.error(f"Error getting positions for {name}: {e}")

        # Sort by unrealized P&L
        all_positions.sort(key=lambda x: x.get("unrealized_pl", 0), reverse=True)
        return all_positions

    def get_recent_orders(self, limit: int = 20) -> List[Dict]:
        """Get recent orders across all accounts"""
        all_orders = []

        for name, client in self.clients.items():
            try:
                request = GetOrdersRequest(
                    status="all",
                    limit=limit // len(self.clients)
                )
                orders = client.get_orders(filter=request)

                for order in orders:
                    all_orders.append({
                        "account": name,
                        "symbol": order.symbol,
                        "side": order.side.value,
                        "qty": float(order.qty) if order.qty else 0,
                        "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                        "type": order.type.value,
                        "status": order.status.value,
                        "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None,
                        "created_at": order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else None,
                        "is_live": "Live" in name
                    })
            except Exception as e:
                logger.error(f"Error getting orders for {name}: {e}")

        # Sort by created_at
        all_orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return all_orders[:limit]

    def get_research_reports(self) -> List[Dict]:
        """Get list of available research reports"""
        reports = []

        if not self.reports_dir.exists():
            return reports

        # Get all date directories
        for date_dir in sorted(self.reports_dir.iterdir(), reverse=True):
            if date_dir.is_dir() and date_dir.name.startswith("202"):
                date_reports = {
                    "date": date_dir.name,
                    "files": []
                }

                for file in date_dir.glob("*.pdf"):
                    bot_name = "Unknown"
                    if "dee_bot" in file.name.lower():
                        bot_name = "DEE-BOT"
                    elif "shorgan_bot_live" in file.name.lower():
                        bot_name = "SHORGAN-LIVE"
                    elif "shorgan_bot" in file.name.lower():
                        bot_name = "SHORGAN-Paper"

                    date_reports["files"].append({
                        "name": file.name,
                        "bot": bot_name,
                        "path": str(file.relative_to(self.project_root)),
                        "size": file.stat().st_size
                    })

                if date_reports["files"]:
                    reports.append(date_reports)

        return reports[:10]  # Last 10 days

    def get_performance_history(self) -> Dict:
        """Get historical performance data"""
        history_file = self.data_dir / "portfolio_history.json"

        if history_file.exists():
            try:
                with open(history_file, "r") as f:
                    return json.load(f)
            except:
                pass

        return {"dates": [], "values": [], "message": "No historical data available"}

    def get_todays_trades(self) -> Optional[Dict]:
        """Get today's trade recommendations"""
        today = datetime.now().strftime("%Y-%m-%d")
        trades_file = self.project_root / "docs" / f"TODAYS_TRADES_{today}.md"

        if trades_file.exists():
            with open(trades_file, "r") as f:
                content = f.read()
            return {
                "date": today,
                "content": content,
                "file": str(trades_file)
            }

        # Try tomorrow's date (research generated night before)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        trades_file = self.project_root / "docs" / f"TODAYS_TRADES_{tomorrow}.md"

        if trades_file.exists():
            with open(trades_file, "r") as f:
                content = f.read()
            return {
                "date": tomorrow,
                "content": content,
                "file": str(trades_file)
            }

        return None


# Initialize dashboard
dashboard = TradingDashboard()


# Routes
@app.route("/")
def index():
    """Main dashboard page"""
    return render_template("dashboard.html")


@app.route("/api/portfolio")
def api_portfolio():
    """API: Get portfolio summary"""
    try:
        summary = dashboard.get_portfolio_summary()
        return jsonify({"ok": True, "data": summary})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/positions")
def api_positions():
    """API: Get all positions"""
    try:
        positions = dashboard.get_positions()
        return jsonify({"ok": True, "data": positions})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/orders")
def api_orders():
    """API: Get recent orders"""
    try:
        orders = dashboard.get_recent_orders()
        return jsonify({"ok": True, "data": orders})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/research")
def api_research():
    """API: Get research reports list"""
    try:
        reports = dashboard.get_research_reports()
        return jsonify({"ok": True, "data": reports})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/trades")
def api_trades():
    """API: Get today's trade recommendations"""
    try:
        trades = dashboard.get_todays_trades()
        return jsonify({"ok": True, "data": trades})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/history")
def api_history():
    """API: Get performance history"""
    try:
        history = dashboard.get_performance_history()
        return jsonify({"ok": True, "data": history})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/download/<path:filepath>")
def download_file(filepath):
    """Download a file"""
    try:
        full_path = PROJECT_ROOT / filepath
        if full_path.exists():
            return send_file(full_path, as_attachment=True)
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "accounts_connected": len(dashboard.clients)
    })


if __name__ == "__main__":
    # Create template and static directories if needed
    templates_dir = PROJECT_ROOT / "scripts" / "dashboard" / "templates"
    static_dir = PROJECT_ROOT / "scripts" / "dashboard" / "static"
    templates_dir.mkdir(parents=True, exist_ok=True)
    static_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("AI Stock Trading Bot - Dashboard")
    print("=" * 70)
    print(f"Accounts connected: {len(dashboard.clients)}")
    for name in dashboard.clients.keys():
        print(f"  - {name}")
    print("")
    print("Dashboard: http://localhost:5000")
    print("=" * 70)

    app.run(host="0.0.0.0", port=5000, debug=True)
