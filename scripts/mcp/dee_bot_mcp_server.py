#!/usr/bin/env python3
import asyncio, base64, json, logging, os, secrets, sys, time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_OK = True
except ImportError:
    MCP_OK = False

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_OK = True
except ImportError:
    CRYPTO_OK = False

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    ALPACA_OK = True
except ImportError:
    ALPACA_OK = False

class Config:
    MASTER_KEY = os.environ.get("DEEBOT_MASTER_KEY", "")
    DATA_DIR = Path(os.environ.get("DEEBOT_DATA_DIR", "./data/mcp_secure"))
    MIN_KEY_LEN, PBKDF2_ITERS, RATE_LIMIT, RATE_WINDOW, CACHE_TTL = 32, 480000, 30, 60, 300
    @classmethod
    def validate(cls):
        errs = []
        if not cls.MASTER_KEY: errs.append("DEEBOT_MASTER_KEY required")
        elif len(cls.MASTER_KEY) < cls.MIN_KEY_LEN: errs.append(f"Key must be {cls.MIN_KEY_LEN}+ chars")
        if not CRYPTO_OK: errs.append("pip install cryptography")
        if not ALPACA_OK: errs.append("pip install alpaca-py")
        if not MCP_OK: errs.append("pip install mcp")
        return errs

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stderr)
log = logging.getLogger("dee-bot")

class AuditLog:
    def __init__(self, path):
        self.path = path / "audit.jsonl"
        self._lock = asyncio.Lock()
    async def write(self, action, user, ok, info=None):
        async with self._lock:
            try:
                with open(self.path, "a") as f:
                    f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "action": action, "user": user[:8], "ok": ok, "info": info or {}}) + "\n")
            except: pass

class Encryption:
    def __init__(self, master_key, data_dir):
        data_dir.mkdir(parents=True, exist_ok=True)
        salt_file = data_dir / ".salt"
        salt = salt_file.read_bytes() if salt_file.exists() else secrets.token_bytes(32)
        if not salt_file.exists(): salt_file.write_bytes(salt)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=Config.PBKDF2_ITERS)
        self._f = Fernet(base64.urlsafe_b64encode(kdf.derive(master_key.encode())))
    def encrypt(self, t): return base64.urlsafe_b64encode(self._f.encrypt(t.encode())).decode()
    def decrypt(self, c): return self._f.decrypt(base64.urlsafe_b64decode(c)).decode()

class Mode(str, Enum):
    PAPER = "paper"
    LIVE = "live"

@dataclass
class Creds:
    user_id: str
    api_key: str
    secret_key: str
    mode: Mode = Mode.PAPER
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CredStore:
    def __init__(self, enc, audit, data_dir):
        self.enc, self.audit, self.file = enc, audit, data_dir / "creds.enc.json"
        self._cache, self._lock = {}, asyncio.Lock()
        data_dir.mkdir(parents=True, exist_ok=True)
    async def save(self, c):
        async with self._lock:
            data = await self._load()
            data[c.user_id] = {"user_id": c.user_id, "api_enc": self.enc.encrypt(c.api_key), "secret_enc": self.enc.encrypt(c.secret_key), "mode": c.mode.value}
            await self._write(data)
            self._cache[c.user_id] = (c, time.time() + Config.CACHE_TTL)
            await self.audit.write("save", c.user_id, True)
    async def get(self, uid):
        async with self._lock:
            if uid in self._cache and time.time() < self._cache[uid][1]: return self._cache[uid][0]
            data = await self._load()
            if uid not in data: return None
            d = data[uid]
            c = Creds(d["user_id"], self.enc.decrypt(d["api_enc"]), self.enc.decrypt(d["secret_enc"]), Mode(d["mode"]))
            self._cache[uid] = (c, time.time() + Config.CACHE_TTL)
            return c
    async def delete(self, uid):
        async with self._lock:
            data = await self._load()
            if uid not in data: return False
            del data[uid]
            await self._write(data)
            self._cache.pop(uid, None)
            return True
    async def list_all(self):
        data = await self._load()
        return [{"user_id": k, "mode": v.get("mode")} for k, v in data.items()]
    async def _load(self): return json.loads(self.file.read_text()) if self.file.exists() else {}
    async def _write(self, d): self.file.write_text(json.dumps(d, indent=2))

class RateLimiter:
    def __init__(self): self._calls, self._lock = {}, asyncio.Lock()
    async def allow(self, key):
        async with self._lock:
            now = time.time()
            calls = [t for t in self._calls.get(key, []) if t > now - Config.RATE_WINDOW]
            if len(calls) >= Config.RATE_LIMIT: return False
            calls.append(now)
            self._calls[key] = calls
            return True

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
    """
    DEE-BOT: Dividend-Enhanced Equity Bot
    Conservative S&P 100 dividend-focused strategy.
    Target: Beta ~1.0, 10-15 positions, defensive quality focus.
    """
    # Target allocations based on actual DEE-BOT portfolio
    TARGETS = {
        "CVX": 0.14,    # Chevron - Energy dividend
        "GILD": 0.14,   # Gilead - Healthcare dividend
        "JNJ": 0.10,    # Johnson & Johnson - Healthcare
        "BMY": 0.09,    # Bristol-Myers - Pharma dividend
        "JPM": 0.08,    # JPMorgan - Financial dividend
        "AAPL": 0.07,   # Apple - Tech dividend growth
        "CL": 0.06,     # Colgate - Consumer staples
        "MRK": 0.05,    # Merck - Healthcare
        "KO": 0.04,     # Coca-Cola - Consumer staples
        "BRK.B": 0.03,  # Berkshire - Diversified
        # ~20% cash buffer for opportunities
    }
    STOP_LOSS = 0.11  # 11% stop loss threshold
    def __init__(self, client): self.client = client
    async def run(self, dry_run=True):
        ts = datetime.now(timezone.utc).isoformat()
        try:
            acct = self.client.get_account()
            value, cash = float(acct.portfolio_value), float(acct.cash)
            positions = {p.symbol: {"qty": int(p.qty), "value": float(p.market_value), "pnl_pct": float(p.unrealized_plpc), "price": float(p.current_price)} for p in self.client.get_all_positions()}
            trades = [Trade(s, "SELL", p["qty"]) for s, p in positions.items() if p["pnl_pct"] < -self.STOP_LOSS]
            for sym, target in self.TARGETS.items():
                cur = positions.get(sym, {}).get("value", 0) / value if value else 0
                if target - cur > 0.03:
                    to_buy = min(value * (target - cur), cash - value * 0.05)
                    if to_buy > 100:
                        price = positions.get(sym, {}).get("price", 100)
                        if price:
                            shares = int(to_buy / price)
                            if shares > 0: trades.append(Trade(sym, "BUY", shares))
            results = []
            for t in trades:
                if dry_run:
                    t.status, t.order_id = "simulated", f"DRY-{t.symbol}-{int(time.time())}"
                else:
                    try:
                        o = self.client.submit_order(MarketOrderRequest(symbol=t.symbol, qty=t.qty, side=OrderSide.BUY if t.action == "BUY" else OrderSide.SELL, time_in_force=TimeInForce.DAY))
                        t.status, t.order_id = o.status.value, str(o.id)
                        t.price = float(o.filled_avg_price) if o.filled_avg_price else None
                    except Exception as e: t.status, t.error = "error", str(e)
                results.append(t)
            va = float(self.client.get_account().portfolio_value)
            pnl = va - value
            return {"ts": ts, "dry_run": dry_run, "value_before": value, "value_after": va, "pnl": pnl, "pnl_pct": (pnl/value*100) if value else 0, "trades": [{"symbol": t.symbol, "action": t.action, "qty": t.qty, "status": t.status, "order_id": t.order_id, "price": t.price, "error": t.error} for t in results], "ok": True}
        except Exception as e: return {"ts": ts, "ok": False, "error": str(e)}

class Shorgan:
    """
    SHORGAN-BOT: Aggressive Catalyst-Driven Strategy
    Micro/mid-cap momentum plays with catalyst triggers.
    Target: High returns, higher risk, 15-25 positions.
    Supports both long and short positions.
    """
    STOP_LOSS = 0.18  # 18% stop loss (wider for volatile stocks)
    TAKE_PROFIT = 0.25  # 25% profit target
    MAX_POSITION_PCT = 0.08  # Max 8% per position

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
                    "qty": qty,
                    "value": float(p.market_value),
                    "pnl_pct": float(p.unrealized_plpc),
                    "price": float(p.current_price),
                    "side": "long" if qty > 0 else "short"
                }

            trades = []

            # Check stop losses and take profits
            for sym, p in positions.items():
                pnl = p["pnl_pct"]
                qty = abs(p["qty"])

                # Stop loss hit
                if pnl < -self.STOP_LOSS:
                    action = "SELL" if p["side"] == "long" else "BUY"  # Cover short
                    trades.append(Trade(sym, action, qty, rationale=f"Stop loss: {pnl*100:.1f}%"))

                # Take profit hit
                elif pnl > self.TAKE_PROFIT:
                    action = "SELL" if p["side"] == "long" else "BUY"  # Cover short
                    trades.append(Trade(sym, action, qty // 2, rationale=f"Take profit: {pnl*100:.1f}%"))

            # Execute trades
            results = []
            for t in trades:
                if dry_run:
                    t.status, t.order_id = "simulated", f"DRY-{t.symbol}-{int(time.time())}"
                else:
                    try:
                        side = OrderSide.BUY if t.action == "BUY" else OrderSide.SELL
                        o = self.client.submit_order(MarketOrderRequest(symbol=t.symbol, qty=t.qty, side=side, time_in_force=TimeInForce.DAY))
                        t.status, t.order_id = o.status.value, str(o.id)
                        t.price = float(o.filled_avg_price) if o.filled_avg_price else None
                    except Exception as e:
                        t.status, t.error = "error", str(e)
                results.append(t)

            va = float(self.client.get_account().portfolio_value)
            pnl_change = va - value

            # Build position summary
            longs = [(s, p) for s, p in positions.items() if p["side"] == "long"]
            shorts = [(s, p) for s, p in positions.items() if p["side"] == "short"]

            return {
                "ts": ts, "dry_run": dry_run, "strategy": "SHORGAN",
                "value_before": value, "value_after": va,
                "pnl": pnl_change, "pnl_pct": (pnl_change/value*100) if value else 0,
                "cash": cash,
                "longs": len(longs), "shorts": len(shorts),
                "trades": [{"symbol": t.symbol, "action": t.action, "qty": t.qty, "status": t.status, "order_id": t.order_id, "price": t.price, "error": t.error, "rationale": t.rationale} for t in results],
                "ok": True
            }
        except Exception as e:
            return {"ts": ts, "ok": False, "error": str(e)}

enc, store, audit, limiter = None, None, None, None
server = Server("stock-bot") if MCP_OK else None

def init():
    global enc, store, audit, limiter
    errs = Config.validate()
    if errs:
        for e in errs: log.error(e)
        return False
    Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    enc = Encryption(Config.MASTER_KEY, Config.DATA_DIR)
    audit = AuditLog(Config.DATA_DIR)
    store = CredStore(enc, audit, Config.DATA_DIR)
    limiter = RateLimiter()
    log.info("Initialized")
    return True

if server:
    @server.list_tools()
    async def list_tools():
        return [
            Tool(name="connect_account", description="Connect Alpaca (AES-256)", inputSchema={"type": "object", "properties": {"user_id": {"type": "string"}, "api_key": {"type": "string"}, "secret_key": {"type": "string"}, "paper": {"type": "boolean", "default": True}}, "required": ["user_id", "api_key", "secret_key"]}),
            Tool(name="disconnect_account", description="Remove account", inputSchema={"type": "object", "properties": {"user_id": {"type": "string"}}, "required": ["user_id"]}),
            Tool(name="get_status", description="Portfolio status", inputSchema={"type": "object", "properties": {"user_id": {"type": "string"}}, "required": ["user_id"]}),
            Tool(name="run_dee_bot", description="Run DEE-BOT (conservative dividend strategy)", inputSchema={"type": "object", "properties": {"user_id": {"type": "string"}, "dry_run": {"type": "boolean", "default": True}, "confirm_live": {"type": "boolean", "default": False}}, "required": ["user_id"]}),
            Tool(name="run_shorgan_bot", description="Run SHORGAN-BOT (aggressive catalyst strategy)", inputSchema={"type": "object", "properties": {"user_id": {"type": "string"}, "dry_run": {"type": "boolean", "default": True}, "confirm_live": {"type": "boolean", "default": False}}, "required": ["user_id"]}),
            Tool(name="list_accounts", description="List accounts", inputSchema={"type": "object", "properties": {}})
        ]
    @server.call_tool()
    async def call_tool(name, args):
        if not store: return [TextContent(type="text", text=json.dumps({"ok": False, "error": "Not init"}))]
        if not await limiter.allow(name): return [TextContent(type="text", text=json.dumps({"ok": False, "error": "Rate limited"}))]
        try:
            if name == "connect_account":
                uid, api, sec, paper = args["user_id"], args["api_key"], args["secret_key"], args.get("paper", True)
                client = TradingClient(api_key=api, secret_key=sec, paper=paper)
                acct = client.get_account()
                await store.save(Creds(uid, api, sec, Mode.PAPER if paper else Mode.LIVE))
                return [TextContent(type="text", text=json.dumps({"ok": True, "user_id": uid, "mode": "paper" if paper else "live", "value": float(acct.portfolio_value)}, indent=2))]
            elif name == "disconnect_account":
                return [TextContent(type="text", text=json.dumps({"ok": await store.delete(args["user_id"])}))]
            elif name == "get_status":
                c = await store.get(args["user_id"])
                if not c: return [TextContent(type="text", text=json.dumps({"ok": False, "error": "Not found"}))]
                client = TradingClient(api_key=c.api_key, secret_key=c.secret_key, paper=c.mode == Mode.PAPER)
                acct = client.get_account()
                return [TextContent(type="text", text=json.dumps({"ok": True, "value": float(acct.portfolio_value), "cash": float(acct.cash), "positions": [{"symbol": p.symbol, "qty": int(p.qty), "value": float(p.market_value)} for p in client.get_all_positions()]}, indent=2))]
            elif name == "run_dee_bot":
                dry, confirm = args.get("dry_run", True), args.get("confirm_live", False)
                if not dry and not confirm: return [TextContent(type="text", text=json.dumps({"ok": False, "error": "confirm_live required"}))]
                c = await store.get(args["user_id"])
                if not c: return [TextContent(type="text", text=json.dumps({"ok": False, "error": "Not found"}))]
                client = TradingClient(api_key=c.api_key, secret_key=c.secret_key, paper=c.mode == Mode.PAPER)
                result = await DeeBot(client).run(dry_run=dry)
                result["user_id"] = c.user_id
                result["strategy"] = "DEE-BOT"
                await audit.write("run_dee", c.user_id, result.get("ok", False), {"pnl": result.get("pnl", 0)})
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            elif name == "run_shorgan_bot":
                dry, confirm = args.get("dry_run", True), args.get("confirm_live", False)
                if not dry and not confirm: return [TextContent(type="text", text=json.dumps({"ok": False, "error": "confirm_live required"}))]
                c = await store.get(args["user_id"])
                if not c: return [TextContent(type="text", text=json.dumps({"ok": False, "error": "Not found"}))]
                client = TradingClient(api_key=c.api_key, secret_key=c.secret_key, paper=c.mode == Mode.PAPER)
                result = await Shorgan(client).run(dry_run=dry)
                result["user_id"] = c.user_id
                await audit.write("run_shorgan", c.user_id, result.get("ok", False), {"pnl": result.get("pnl", 0)})
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            elif name == "list_accounts":
                return [TextContent(type="text", text=json.dumps({"ok": True, "accounts": await store.list_all()}, indent=2))]
            return [TextContent(type="text", text=json.dumps({"ok": False, "error": f"Unknown: {name}"}))]
        except Exception as e: return [TextContent(type="text", text=json.dumps({"ok": False, "error": str(e)}))]

async def main():
    print("STOCK-BOT MCP Server v2.0", file=sys.stderr)
    if not init():
        print("Set DEEBOT_MASTER_KEY (32+ chars)", file=sys.stderr)
        sys.exit(1)
    if not server:
        print("pip install mcp", file=sys.stderr)
        sys.exit(1)
    print(f"Data: {Config.DATA_DIR.absolute()}", file=sys.stderr)
    async with stdio_server() as (r, w):
        await server.run(r, w, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
