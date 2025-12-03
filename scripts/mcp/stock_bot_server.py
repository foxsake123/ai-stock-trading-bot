#!/usr/bin/env python3
"""
STOCK-BOT MCP Server - Hosted Web Service Version
==================================================

A hosted MCP server that allows multiple users to connect their
Alpaca trading accounts and run trading strategies via HTTP/SSE.

DEPLOYMENT:
    # Local
    python stock_bot_server.py

    # Docker
    docker build -t stock-bot .
    docker run -p 8000:8000 -e MASTER_KEY=your-key stock-bot

    # Cloud (Railway, Render, Fly.io, etc.)
    Set MASTER_KEY environment variable and deploy

USAGE:
    Users add to Claude Desktop config:
    {
      "mcpServers": {
        "stock-bot": {
          "url": "https://your-server.com/mcp",
          "headers": {
            "Authorization": "Bearer user-api-key"
          }
        }
      }
    }
"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Dict

# Web framework
from aiohttp import web
import aiohttp_cors

# Cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Alpaca
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# HTTP client for webhooks
import aiohttp

# =============================================================================
# CONFIG
# =============================================================================

class Config:
    MASTER_KEY = os.environ.get("MASTER_KEY", os.environ.get("DEEBOT_MASTER_KEY", ""))
    DATA_DIR = Path(os.environ.get("DATA_DIR", "./data/stock_bot_hosted"))
    PORT = int(os.environ.get("PORT", 8000))
    HOST = os.environ.get("HOST", "0.0.0.0")

    # Security
    MIN_KEY_LEN = 32
    PBKDF2_ITERS = 480000
    API_KEY_PREFIX = "sb_"  # stock-bot API key prefix

    # Rate limiting
    RATE_LIMIT = 60  # requests per minute
    RATE_WINDOW = 60

    # Telegram webhook (optional)
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

    @classmethod
    def validate(cls):
        errors = []
        if not cls.MASTER_KEY:
            errors.append("MASTER_KEY environment variable required")
        elif len(cls.MASTER_KEY) < cls.MIN_KEY_LEN:
            errors.append(f"MASTER_KEY must be {cls.MIN_KEY_LEN}+ chars")
        return errors

# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("stock-bot")

# =============================================================================
# ENCRYPTION
# =============================================================================

class Encryption:
    def __init__(self, master_key: str, data_dir: Path):
        data_dir.mkdir(parents=True, exist_ok=True)
        salt_file = data_dir / ".salt"
        if salt_file.exists():
            salt = salt_file.read_bytes()
        else:
            salt = secrets.token_bytes(32)
            salt_file.write_bytes(salt)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=Config.PBKDF2_ITERS)
        self._f = Fernet(base64.urlsafe_b64encode(kdf.derive(master_key.encode())))

    def encrypt(self, text: str) -> str:
        return base64.urlsafe_b64encode(self._f.encrypt(text.encode())).decode()

    def decrypt(self, cipher: str) -> str:
        return self._f.decrypt(base64.urlsafe_b64decode(cipher)).decode()

# =============================================================================
# USER & API KEY MANAGEMENT
# =============================================================================

@dataclass
class User:
    user_id: str
    email: str
    api_key_hash: str  # Hashed API key
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class AlpacaAccount:
    account_id: str
    user_id: str  # Owner
    api_key_enc: str  # Encrypted
    secret_key_enc: str  # Encrypted
    paper: bool = True
    nickname: str = ""

class UserStore:
    def __init__(self, enc: Encryption, data_dir: Path):
        self.enc = enc
        self.users_file = data_dir / "users.json"
        self.accounts_file = data_dir / "accounts.json"
        self._lock = asyncio.Lock()
        data_dir.mkdir(parents=True, exist_ok=True)

    def _hash_api_key(self, api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()

    async def create_user(self, email: str) -> tuple[User, str]:
        """Create user and return (user, api_key)"""
        async with self._lock:
            users = await self._load_users()

            # Check if email exists
            for u in users.values():
                if u.get("email") == email:
                    raise ValueError("Email already registered")

            # Generate API key
            api_key = Config.API_KEY_PREFIX + secrets.token_urlsafe(32)
            api_key_hash = self._hash_api_key(api_key)

            user_id = str(uuid.uuid4())[:8]
            user = User(user_id=user_id, email=email, api_key_hash=api_key_hash)

            users[user_id] = {
                "user_id": user_id,
                "email": email,
                "api_key_hash": api_key_hash,
                "created": user.created
            }
            await self._save_users(users)

            return user, api_key

    async def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """Authenticate user by API key"""
        async with self._lock:
            users = await self._load_users()
            api_key_hash = self._hash_api_key(api_key)

            for u in users.values():
                if u.get("api_key_hash") == api_key_hash:
                    return User(**{k: v for k, v in u.items() if k in ["user_id", "email", "api_key_hash", "created"]})
            return None

    async def add_alpaca_account(self, user_id: str, api_key: str, secret_key: str, paper: bool, nickname: str = "") -> str:
        """Add Alpaca account for user"""
        async with self._lock:
            accounts = await self._load_accounts()

            account_id = str(uuid.uuid4())[:8]
            accounts[account_id] = {
                "account_id": account_id,
                "user_id": user_id,
                "api_key_enc": self.enc.encrypt(api_key),
                "secret_key_enc": self.enc.encrypt(secret_key),
                "paper": paper,
                "nickname": nickname or f"account-{account_id}"
            }
            await self._save_accounts(accounts)
            return account_id

    async def get_user_accounts(self, user_id: str) -> list[dict]:
        """Get all accounts for a user"""
        async with self._lock:
            accounts = await self._load_accounts()
            return [
                {"account_id": a["account_id"], "nickname": a.get("nickname", ""), "paper": a["paper"]}
                for a in accounts.values() if a["user_id"] == user_id
            ]

    async def get_account(self, user_id: str, account_id: str) -> Optional[dict]:
        """Get decrypted account credentials"""
        async with self._lock:
            accounts = await self._load_accounts()
            acc = accounts.get(account_id)
            if acc and acc["user_id"] == user_id:
                return {
                    "account_id": acc["account_id"],
                    "api_key": self.enc.decrypt(acc["api_key_enc"]),
                    "secret_key": self.enc.decrypt(acc["secret_key_enc"]),
                    "paper": acc["paper"],
                    "nickname": acc.get("nickname", "")
                }
            return None

    async def delete_account(self, user_id: str, account_id: str) -> bool:
        async with self._lock:
            accounts = await self._load_accounts()
            if account_id in accounts and accounts[account_id]["user_id"] == user_id:
                del accounts[account_id]
                await self._save_accounts(accounts)
                return True
            return False

    async def rotate_api_key(self, user_id: str) -> Optional[str]:
        """Generate new API key for user, invalidate old one"""
        async with self._lock:
            users = await self._load_users()
            if user_id not in users:
                return None

            # Generate new API key
            new_api_key = Config.API_KEY_PREFIX + secrets.token_urlsafe(32)
            new_api_key_hash = self._hash_api_key(new_api_key)

            # Update user
            users[user_id]["api_key_hash"] = new_api_key_hash
            users[user_id]["key_rotated"] = datetime.now(timezone.utc).isoformat()
            await self._save_users(users)

            return new_api_key

    async def _load_users(self) -> dict:
        if not self.users_file.exists():
            return {}
        return json.loads(self.users_file.read_text())

    async def _save_users(self, data: dict):
        self.users_file.write_text(json.dumps(data, indent=2))

    async def _load_accounts(self) -> dict:
        if not self.accounts_file.exists():
            return {}
        return json.loads(self.accounts_file.read_text())

    async def _save_accounts(self, data: dict):
        self.accounts_file.write_text(json.dumps(data, indent=2))

# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    def __init__(self):
        self._calls: Dict[str, list] = {}

    def check(self, key: str) -> bool:
        now = time.time()
        calls = [t for t in self._calls.get(key, []) if t > now - Config.RATE_WINDOW]
        if len(calls) >= Config.RATE_LIMIT:
            return False
        calls.append(now)
        self._calls[key] = calls
        return True

# =============================================================================
# TELEGRAM WEBHOOK NOTIFICATIONS
# =============================================================================

async def send_telegram_alert(message: str, parse_mode: str = "HTML"):
    """Send alert to Telegram (non-blocking)"""
    if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID:
        log.debug("Telegram not configured, skipping alert")
        return False

    try:
        url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={
                "chat_id": Config.TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": parse_mode
            }, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    log.info("Telegram alert sent successfully")
                    return True
                else:
                    log.warning(f"Telegram alert failed: {resp.status}")
                    return False
    except Exception as e:
        log.warning(f"Telegram alert error: {e}")
        return False

# =============================================================================
# ACTIVITY & ANALYTICS TRACKING
# =============================================================================

class ActivityTracker:
    """Track user activity and trade history"""

    def __init__(self, data_dir: Path):
        self.activity_file = data_dir / "activity.json"
        self.trades_file = data_dir / "trade_history.json"
        self.analytics_file = data_dir / "analytics.json"
        self._lock = asyncio.Lock()
        data_dir.mkdir(parents=True, exist_ok=True)

    async def log_activity(self, user_id: str, action: str, details: dict = None):
        """Log user activity"""
        async with self._lock:
            activities = await self._load_activities()
            activities.append({
                "ts": datetime.now(timezone.utc).isoformat(),
                "user_id": user_id,
                "action": action,
                "details": details or {}
            })
            # Keep last 1000 activities
            activities = activities[-1000:]
            await self._save_activities(activities)

    async def log_trade(self, user_id: str, account_id: str, strategy: str, trade: dict):
        """Log trade for history"""
        async with self._lock:
            trades = await self._load_trades()
            trade_record = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "user_id": user_id,
                "account_id": account_id,
                "strategy": strategy,
                **trade
            }
            trades.append(trade_record)
            # Keep last 10000 trades
            trades = trades[-10000:]
            await self._save_trades(trades)

    async def update_analytics(self, user_id: str, event_type: str):
        """Update usage analytics"""
        async with self._lock:
            analytics = await self._load_analytics()
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

            if user_id not in analytics:
                analytics[user_id] = {"daily": {}, "totals": {}}

            if today not in analytics[user_id]["daily"]:
                analytics[user_id]["daily"][today] = {}

            # Increment counters
            if event_type not in analytics[user_id]["daily"][today]:
                analytics[user_id]["daily"][today][event_type] = 0
            analytics[user_id]["daily"][today][event_type] += 1

            if event_type not in analytics[user_id]["totals"]:
                analytics[user_id]["totals"][event_type] = 0
            analytics[user_id]["totals"][event_type] += 1

            # Keep only last 30 days of daily data
            daily_keys = sorted(analytics[user_id]["daily"].keys())
            if len(daily_keys) > 30:
                for old_key in daily_keys[:-30]:
                    del analytics[user_id]["daily"][old_key]

            await self._save_analytics(analytics)

    async def get_user_trades(self, user_id: str, limit: int = 100) -> list:
        """Get trade history for a user"""
        async with self._lock:
            trades = await self._load_trades()
            user_trades = [t for t in trades if t.get("user_id") == user_id]
            return user_trades[-limit:]

    async def get_user_analytics(self, user_id: str) -> dict:
        """Get analytics for a user"""
        async with self._lock:
            analytics = await self._load_analytics()
            return analytics.get(user_id, {"daily": {}, "totals": {}})

    async def _load_activities(self) -> list:
        if not self.activity_file.exists():
            return []
        return json.loads(self.activity_file.read_text())

    async def _save_activities(self, data: list):
        self.activity_file.write_text(json.dumps(data, indent=2))

    async def _load_trades(self) -> list:
        if not self.trades_file.exists():
            return []
        return json.loads(self.trades_file.read_text())

    async def _save_trades(self, data: list):
        self.trades_file.write_text(json.dumps(data, indent=2))

    async def _load_analytics(self) -> dict:
        if not self.analytics_file.exists():
            return {}
        return json.loads(self.analytics_file.read_text())

    async def _save_analytics(self, data: dict):
        self.analytics_file.write_text(json.dumps(data, indent=2))

# =============================================================================
# TRADING STRATEGIES
# =============================================================================

@dataclass
class Trade:
    symbol: str
    action: str
    qty: int
    status: str = ""
    order_id: str = ""
    price: float = None
    error: str = ""
    rationale: str = ""

class DeeBot:
    """Conservative dividend strategy"""
    TARGETS = {
        "CVX": 0.14, "GILD": 0.14, "JNJ": 0.10, "BMY": 0.09,
        "JPM": 0.08, "AAPL": 0.07, "CL": 0.06, "MRK": 0.05,
        "KO": 0.04, "BRK.B": 0.03
    }
    STOP_LOSS = 0.11

    def __init__(self, client): self.client = client

    async def run(self, dry_run=True):
        ts = datetime.now(timezone.utc).isoformat()
        try:
            acct = self.client.get_account()
            value, cash = float(acct.portfolio_value), float(acct.cash)
            positions = {p.symbol: {"qty": int(p.qty), "value": float(p.market_value),
                        "pnl_pct": float(p.unrealized_plpc), "price": float(p.current_price)}
                        for p in self.client.get_all_positions()}

            trades = [Trade(s, "SELL", p["qty"], rationale=f"Stop loss: {p['pnl_pct']*100:.1f}%")
                     for s, p in positions.items() if p["pnl_pct"] < -self.STOP_LOSS]

            for sym, target in self.TARGETS.items():
                cur = positions.get(sym, {}).get("value", 0) / value if value else 0
                if target - cur > 0.03:
                    to_buy = min(value * (target - cur), cash - value * 0.05)
                    if to_buy > 100:
                        price = positions.get(sym, {}).get("price", 100)
                        if price:
                            shares = int(to_buy / price)
                            if shares > 0:
                                trades.append(Trade(sym, "BUY", shares, rationale=f"Rebalance to {target*100:.0f}%"))

            results = []
            for t in trades:
                if dry_run:
                    t.status, t.order_id = "simulated", f"DRY-{t.symbol}-{int(time.time())}"
                else:
                    try:
                        o = self.client.submit_order(MarketOrderRequest(
                            symbol=t.symbol, qty=t.qty,
                            side=OrderSide.BUY if t.action == "BUY" else OrderSide.SELL,
                            time_in_force=TimeInForce.DAY))
                        t.status, t.order_id = o.status.value, str(o.id)
                        t.price = float(o.filled_avg_price) if o.filled_avg_price else None
                    except Exception as e:
                        t.status, t.error = "error", str(e)
                results.append(t)

            return {"ts": ts, "strategy": "DEE-BOT", "dry_run": dry_run,
                    "value": value, "cash": cash,
                    "trades": [{"symbol": t.symbol, "action": t.action, "qty": t.qty,
                               "status": t.status, "rationale": t.rationale} for t in results],
                    "ok": True}
        except Exception as e:
            return {"ts": ts, "ok": False, "error": str(e)}

class Shorgan:
    """Aggressive catalyst strategy"""
    STOP_LOSS = 0.18
    TAKE_PROFIT = 0.25

    def __init__(self, client): self.client = client

    async def run(self, dry_run=True):
        ts = datetime.now(timezone.utc).isoformat()
        try:
            acct = self.client.get_account()
            value, cash = float(acct.portfolio_value), float(acct.cash)
            positions = {}
            for p in self.client.get_all_positions():
                qty = int(p.qty)
                positions[p.symbol] = {
                    "qty": qty, "value": float(p.market_value),
                    "pnl_pct": float(p.unrealized_plpc), "price": float(p.current_price),
                    "side": "long" if qty > 0 else "short"
                }

            trades = []
            for sym, p in positions.items():
                pnl = p["pnl_pct"]
                qty = abs(p["qty"])
                if pnl < -self.STOP_LOSS:
                    action = "SELL" if p["side"] == "long" else "BUY"
                    trades.append(Trade(sym, action, qty, rationale=f"Stop loss: {pnl*100:.1f}%"))
                elif pnl > self.TAKE_PROFIT:
                    action = "SELL" if p["side"] == "long" else "BUY"
                    trades.append(Trade(sym, action, qty // 2, rationale=f"Take profit: {pnl*100:.1f}%"))

            results = []
            for t in trades:
                if dry_run:
                    t.status, t.order_id = "simulated", f"DRY-{t.symbol}-{int(time.time())}"
                else:
                    try:
                        o = self.client.submit_order(MarketOrderRequest(
                            symbol=t.symbol, qty=t.qty,
                            side=OrderSide.BUY if t.action == "BUY" else OrderSide.SELL,
                            time_in_force=TimeInForce.DAY))
                        t.status, t.order_id = o.status.value, str(o.id)
                    except Exception as e:
                        t.status, t.error = "error", str(e)
                results.append(t)

            longs = len([p for p in positions.values() if p["side"] == "long"])
            shorts = len([p for p in positions.values() if p["side"] == "short"])

            return {"ts": ts, "strategy": "SHORGAN", "dry_run": dry_run,
                    "value": value, "cash": cash, "longs": longs, "shorts": shorts,
                    "trades": [{"symbol": t.symbol, "action": t.action, "qty": t.qty,
                               "status": t.status, "rationale": t.rationale} for t in results],
                    "ok": True}
        except Exception as e:
            return {"ts": ts, "ok": False, "error": str(e)}

# =============================================================================
# HTTP API HANDLERS
# =============================================================================

enc: Encryption = None
user_store: UserStore = None
rate_limiter: RateLimiter = None
activity_tracker: ActivityTracker = None

def init():
    global enc, user_store, rate_limiter, activity_tracker
    errors = Config.validate()
    if errors:
        for e in errors:
            log.error(e)
        return False

    Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    enc = Encryption(Config.MASTER_KEY, Config.DATA_DIR)
    user_store = UserStore(enc, Config.DATA_DIR)
    rate_limiter = RateLimiter()
    activity_tracker = ActivityTracker(Config.DATA_DIR)
    log.info("Server initialized")
    if Config.TELEGRAM_BOT_TOKEN:
        log.info("Telegram notifications enabled")
    return True

@web.middleware
async def auth_middleware(request, handler):
    """Authenticate requests via API key"""
    # Skip auth for public endpoints
    if request.path in ["/register", "/health", "/"] or request.path.startswith("/static") or request.path.startswith("/admin"):
        return await handler(request)

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return web.json_response({"ok": False, "error": "Missing Authorization header"}, status=401)

    api_key = auth[7:]  # Remove "Bearer "
    user = await user_store.get_user_by_api_key(api_key)
    if not user:
        return web.json_response({"ok": False, "error": "Invalid API key"}, status=401)

    # Rate limiting
    if not rate_limiter.check(user.user_id):
        return web.json_response({"ok": False, "error": "Rate limit exceeded"}, status=429)

    request["user"] = user
    return await handler(request)

# --- Routes ---

async def handle_health(request):
    return web.json_response({"ok": True, "service": "stock-bot", "version": "2.1"})

async def handle_register(request):
    """Register new user, get API key"""
    try:
        data = await request.json()
        email = data.get("email")
        if not email:
            return web.json_response({"ok": False, "error": "Email required"}, status=400)

        user, api_key = await user_store.create_user(email)

        # Log activity
        await activity_tracker.log_activity(user.user_id, "register", {"email": email})
        await activity_tracker.update_analytics(user.user_id, "registration")

        # Send Telegram alert (async, non-blocking)
        asyncio.create_task(send_telegram_alert(
            f"<b>New Stock-Bot User!</b>\n\n"
            f"Email: <code>{email}</code>\n"
            f"User ID: <code>{user.user_id}</code>\n"
            f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        ))

        return web.json_response({
            "ok": True,
            "user_id": user.user_id,
            "api_key": api_key,
            "message": "Save your API key - it won't be shown again!"
        })
    except ValueError as e:
        return web.json_response({"ok": False, "error": str(e)}, status=400)
    except Exception as e:
        return web.json_response({"ok": False, "error": str(e)}, status=500)

async def handle_add_account(request):
    """Add Alpaca account"""
    user = request["user"]
    try:
        data = await request.json()
        api_key = data.get("alpaca_api_key")
        secret_key = data.get("alpaca_secret_key")
        paper = data.get("paper", True)
        nickname = data.get("nickname", "")

        if not api_key or not secret_key:
            return web.json_response({"ok": False, "error": "API key and secret required"}, status=400)

        # Verify credentials
        client = TradingClient(api_key=api_key, secret_key=secret_key, paper=paper)
        acct = client.get_account()

        account_id = await user_store.add_alpaca_account(user.user_id, api_key, secret_key, paper, nickname)

        # Log activity
        await activity_tracker.log_activity(user.user_id, "add_account", {
            "account_id": account_id,
            "paper": paper,
            "value": float(acct.portfolio_value)
        })
        await activity_tracker.update_analytics(user.user_id, "account_added")

        # Send Telegram alert
        account_type = "Paper" if paper else "LIVE"
        asyncio.create_task(send_telegram_alert(
            f"<b>New Alpaca Account Connected!</b>\n\n"
            f"User: <code>{user.user_id}</code>\n"
            f"Type: {account_type}\n"
            f"Value: ${float(acct.portfolio_value):,.2f}\n"
            f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        ))

        return web.json_response({
            "ok": True,
            "account_id": account_id,
            "nickname": nickname,
            "paper": paper,
            "portfolio_value": float(acct.portfolio_value)
        })
    except Exception as e:
        return web.json_response({"ok": False, "error": str(e)}, status=400)

async def handle_list_accounts(request):
    """List user's accounts"""
    user = request["user"]
    accounts = await user_store.get_user_accounts(user.user_id)
    return web.json_response({"ok": True, "accounts": accounts})

async def handle_delete_account(request):
    """Delete an account"""
    user = request["user"]
    account_id = request.match_info["account_id"]
    deleted = await user_store.delete_account(user.user_id, account_id)
    if deleted:
        await activity_tracker.log_activity(user.user_id, "delete_account", {"account_id": account_id})
    return web.json_response({"ok": deleted})

async def handle_rotate_key(request):
    """Rotate API key - generates new key, invalidates old one"""
    user = request["user"]
    new_api_key = await user_store.rotate_api_key(user.user_id)
    if new_api_key:
        await activity_tracker.log_activity(user.user_id, "rotate_key", {})
        await activity_tracker.update_analytics(user.user_id, "key_rotation")
        return web.json_response({
            "ok": True,
            "api_key": new_api_key,
            "message": "Save your new API key - the old one is now invalid!"
        })
    return web.json_response({"ok": False, "error": "User not found"}, status=404)

async def handle_trade_history(request):
    """Get user's trade history"""
    user = request["user"]
    limit = int(request.query.get("limit", 100))
    trades = await activity_tracker.get_user_trades(user.user_id, limit=min(limit, 500))
    return web.json_response({"ok": True, "trades": trades, "count": len(trades)})

async def handle_user_analytics(request):
    """Get user's usage analytics"""
    user = request["user"]
    analytics = await activity_tracker.get_user_analytics(user.user_id)
    return web.json_response({"ok": True, "analytics": analytics})

async def handle_portfolio(request):
    """Get portfolio status"""
    user = request["user"]
    account_id = request.match_info["account_id"]

    acc = await user_store.get_account(user.user_id, account_id)
    if not acc:
        return web.json_response({"ok": False, "error": "Account not found"}, status=404)

    try:
        client = TradingClient(api_key=acc["api_key"], secret_key=acc["secret_key"], paper=acc["paper"])
        acct = client.get_account()
        positions = client.get_all_positions()

        return web.json_response({
            "ok": True,
            "account_id": account_id,
            "nickname": acc["nickname"],
            "value": float(acct.portfolio_value),
            "cash": float(acct.cash),
            "buying_power": float(acct.buying_power),
            "positions": [
                {"symbol": p.symbol, "qty": int(p.qty), "value": float(p.market_value),
                 "pnl": float(p.unrealized_pl), "pnl_pct": float(p.unrealized_plpc) * 100}
                for p in positions
            ]
        })
    except Exception as e:
        return web.json_response({"ok": False, "error": str(e)}, status=500)

async def handle_run_strategy(request):
    """Run trading strategy"""
    user = request["user"]
    account_id = request.match_info["account_id"]
    strategy = request.match_info["strategy"]

    acc = await user_store.get_account(user.user_id, account_id)
    if not acc:
        return web.json_response({"ok": False, "error": "Account not found"}, status=404)

    try:
        data = await request.json() if request.body_exists else {}
    except:
        data = {}

    dry_run = data.get("dry_run", True)
    confirm_live = data.get("confirm_live", False)

    if not dry_run and not confirm_live:
        return web.json_response({"ok": False, "error": "confirm_live required for live trading"}, status=400)

    try:
        client = TradingClient(api_key=acc["api_key"], secret_key=acc["secret_key"], paper=acc["paper"])

        if strategy == "dee-bot":
            result = await DeeBot(client).run(dry_run=dry_run)
        elif strategy == "shorgan":
            result = await Shorgan(client).run(dry_run=dry_run)
        else:
            return web.json_response({"ok": False, "error": f"Unknown strategy: {strategy}"}, status=400)

        result["account_id"] = account_id

        # Log activity and trades
        await activity_tracker.log_activity(user.user_id, "run_strategy", {
            "account_id": account_id,
            "strategy": strategy,
            "dry_run": dry_run,
            "trades_count": len(result.get("trades", []))
        })
        await activity_tracker.update_analytics(user.user_id, f"strategy_run_{strategy}")

        # Log individual trades
        for trade in result.get("trades", []):
            await activity_tracker.log_trade(user.user_id, account_id, strategy, trade)

        # Send Telegram alert for live trades
        if not dry_run and result.get("trades"):
            trade_count = len(result.get("trades", []))
            asyncio.create_task(send_telegram_alert(
                f"<b>Strategy Executed!</b>\n\n"
                f"User: <code>{user.user_id}</code>\n"
                f"Strategy: {strategy.upper()}\n"
                f"Account: {'Paper' if acc['paper'] else 'LIVE'}\n"
                f"Trades: {trade_count}\n"
                f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
            ))

        return web.json_response(result)
    except Exception as e:
        return web.json_response({"ok": False, "error": str(e)}, status=500)

# =============================================================================
# MCP SSE TRANSPORT (for Claude Desktop)
# =============================================================================

async def handle_mcp_sse(request):
    """MCP over Server-Sent Events for Claude Desktop"""
    user = request.get("user")

    response = web.StreamResponse(
        status=200,
        reason="OK",
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
    await response.prepare(request)

    # Send tool list
    tools = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "tools": [
                {"name": "add_account", "description": "Add Alpaca trading account",
                 "inputSchema": {"type": "object", "properties": {
                     "alpaca_api_key": {"type": "string"},
                     "alpaca_secret_key": {"type": "string"},
                     "paper": {"type": "boolean", "default": True},
                     "nickname": {"type": "string"}
                 }, "required": ["alpaca_api_key", "alpaca_secret_key"]}},
                {"name": "list_accounts", "description": "List connected accounts",
                 "inputSchema": {"type": "object", "properties": {}}},
                {"name": "get_portfolio", "description": "Get portfolio status",
                 "inputSchema": {"type": "object", "properties": {
                     "account_id": {"type": "string"}
                 }, "required": ["account_id"]}},
                {"name": "run_dee_bot", "description": "Run DEE-BOT conservative strategy",
                 "inputSchema": {"type": "object", "properties": {
                     "account_id": {"type": "string"},
                     "dry_run": {"type": "boolean", "default": True}
                 }, "required": ["account_id"]}},
                {"name": "run_shorgan", "description": "Run SHORGAN aggressive strategy",
                 "inputSchema": {"type": "object", "properties": {
                     "account_id": {"type": "string"},
                     "dry_run": {"type": "boolean", "default": True}
                 }, "required": ["account_id"]}}
            ]
        }
    }

    await response.write(f"data: {json.dumps(tools)}\n\n".encode())

    # Keep connection alive
    while True:
        await asyncio.sleep(30)
        await response.write(b": keepalive\n\n")

# =============================================================================
# STATIC FILES & LANDING PAGE
# =============================================================================

STATIC_DIR = Path(__file__).parent / "static"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "stockbot-admin-2024")  # Change this!

async def handle_landing(request):
    """Serve landing page"""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return web.FileResponse(index_file)
    # Fallback if no static file
    return web.json_response({"ok": True, "service": "stock-bot", "version": "2.0", "docs": "/docs"})

# =============================================================================
# ADMIN DASHBOARD
# =============================================================================

async def handle_admin(request):
    """Serve admin dashboard"""
    admin_file = STATIC_DIR / "admin.html"
    if admin_file.exists():
        return web.FileResponse(admin_file)
    return web.Response(text="Admin dashboard not found", status=404)

async def handle_admin_data(request):
    """Get admin data (password protected)"""
    password = request.query.get("password", "")
    if password != ADMIN_PASSWORD:
        return web.json_response({"ok": False, "error": "Invalid password"}, status=401)

    try:
        # Load users
        users_file = Config.DATA_DIR / "users.json"
        users = json.loads(users_file.read_text()) if users_file.exists() else {}

        # Load accounts
        accounts_file = Config.DATA_DIR / "accounts.json"
        accounts = json.loads(accounts_file.read_text()) if accounts_file.exists() else {}

        # Load activity log
        activity_file = Config.DATA_DIR / "activity.json"
        activity = json.loads(activity_file.read_text()) if activity_file.exists() else []

        # Get portfolio data for each account
        portfolio_data = []
        for acc_id, acc in accounts.items():
            try:
                api_key = enc.decrypt(acc["api_key_enc"])
                secret_key = enc.decrypt(acc["secret_key_enc"])
                client = TradingClient(api_key=api_key, secret_key=secret_key, paper=acc["paper"])
                acct = client.get_account()
                positions = client.get_all_positions()

                portfolio_data.append({
                    "account_id": acc_id,
                    "user_id": acc["user_id"],
                    "nickname": acc.get("nickname", ""),
                    "paper": acc["paper"],
                    "value": float(acct.portfolio_value),
                    "cash": float(acct.cash),
                    "positions": len(positions),
                    "pnl": float(acct.portfolio_value) - 100000 if acc["paper"] else None  # Assuming $100k paper start
                })
            except Exception as e:
                portfolio_data.append({
                    "account_id": acc_id,
                    "user_id": acc["user_id"],
                    "error": str(e)
                })

        return web.json_response({
            "ok": True,
            "stats": {
                "total_users": len(users),
                "total_accounts": len(accounts),
                "paper_accounts": len([a for a in accounts.values() if a.get("paper", True)]),
                "live_accounts": len([a for a in accounts.values() if not a.get("paper", True)])
            },
            "users": [
                {"user_id": u["user_id"], "email": u["email"], "created": u["created"]}
                for u in users.values()
            ],
            "portfolios": portfolio_data,
            "recent_activity": activity[-50:]  # Last 50 activities
        })
    except Exception as e:
        return web.json_response({"ok": False, "error": str(e)}, status=500)

# =============================================================================
# APP SETUP
# =============================================================================

def create_app():
    app = web.Application(middlewares=[auth_middleware])

    # CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })

    # Routes
    app.router.add_get("/", handle_landing)
    app.router.add_get("/health", handle_health)
    app.router.add_post("/register", handle_register)
    app.router.add_post("/accounts", handle_add_account)
    app.router.add_get("/accounts", handle_list_accounts)
    app.router.add_delete("/accounts/{account_id}", handle_delete_account)
    app.router.add_get("/accounts/{account_id}/portfolio", handle_portfolio)
    app.router.add_post("/accounts/{account_id}/run/{strategy}", handle_run_strategy)
    app.router.add_get("/mcp", handle_mcp_sse)
    app.router.add_get("/admin", handle_admin)
    app.router.add_get("/admin/data", handle_admin_data)

    # New v2.1 endpoints
    app.router.add_post("/rotate-key", handle_rotate_key)
    app.router.add_get("/trades", handle_trade_history)
    app.router.add_get("/analytics", handle_user_analytics)

    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)

    return app

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 50)
    print("STOCK-BOT Hosted Server v2.1")
    print("=" * 50)

    if not init():
        print("Set MASTER_KEY environment variable (32+ chars)")
        sys.exit(1)

    app = create_app()
    print(f"Starting server on http://{Config.HOST}:{Config.PORT}")
    print(f"Data directory: {Config.DATA_DIR.absolute()}")
    web.run_app(app, host=Config.HOST, port=Config.PORT)

if __name__ == "__main__":
    main()
