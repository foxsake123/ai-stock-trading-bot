#!/usr/bin/env python3
"""
StateStore: Resilient State Management for Trading Bots
Implements atomic writes, schema versioning, and coherence validation.

Supports: DEE-BOT, SHORGAN Paper, SHORGAN Live
"""

import os
import sys
import json
import tempfile
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Schema version for migrations
SCHEMA_VERSION = "1.0.0"


class BotType(Enum):
    DEE_BOT = "DEE-BOT"
    SHORGAN_PAPER = "SHORGAN-PAPER"
    SHORGAN_LIVE = "SHORGAN-LIVE"


@dataclass
class Position:
    """Single position state"""
    symbol: str
    qty: float
    avg_entry_price: float
    current_price: float
    market_value: float
    pnl_realized: float
    pnl_unrealized: float
    pnl_pct: float
    side: str  # 'long' or 'short'

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Position':
        return cls(**data)


@dataclass
class RiskState:
    """Risk management state"""
    daily_loss_limit: float
    daily_loss_current: float
    max_position_pct: float
    max_drawdown_pct: float
    current_drawdown_pct: float
    fee_budget_remaining: float
    margin_usage_pct: float  # For SHORGAN Live
    stop_loss_pct: float

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'RiskState':
        return cls(**data)


@dataclass
class BotState:
    """Complete bot state snapshot"""
    schema_version: str
    bot_type: str
    asof: str  # ISO timestamp

    # Account state
    equity: float
    cash: float
    buying_power: float
    portfolio_value: float

    # Positions
    positions: Dict[str, Dict]  # symbol -> Position dict

    # Risk state
    risk: Dict

    # Trading cursors (for event continuity)
    cursors: Dict[str, int]  # e.g., {"last_order_id": 12345, "last_fill_seq": 99}

    # Toggles
    toggles: Dict[str, bool]  # e.g., {"trading_enabled": True, "stop_loss_active": True}

    # Timestamps
    timestamps: Dict[str, str]  # e.g., {"last_trade": "...", "last_reconcile": "..."}

    # Pending orders
    pending_orders: List[Dict]

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'BotState':
        return cls(**data)


class StateValidationError(Exception):
    """Raised when state validation fails"""
    pass


class CoherenceError(Exception):
    """Raised when coherence check fails"""
    pass


class StateStore:
    """
    Resilient state storage with atomic writes and validation.

    Features:
    - Atomic writes (temp file + fsync + rename)
    - Schema versioning and migrations
    - Field validation on load
    - Coherence checking against live exchange data
    """

    def __init__(self, bot_type: BotType, state_dir: Path = None):
        self.bot_type = bot_type
        self.state_dir = state_dir or (project_root / "data" / "bot_state")
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # State file path
        self.state_file = self.state_dir / f"{bot_type.value.lower().replace('-', '_')}_state.json"
        self.backup_file = self.state_dir / f"{bot_type.value.lower().replace('-', '_')}_state.backup.json"

        # In-memory state
        self._state: Optional[BotState] = None

        # Validation bounds
        self._validation_rules = self._get_validation_rules()

        logger.info(f"StateStore initialized for {bot_type.value}")

    def _get_validation_rules(self) -> Dict:
        """Get validation rules based on bot type"""
        if self.bot_type == BotType.DEE_BOT:
            return {
                "max_position_pct": 8.0,
                "stop_loss_pct": 11.0,
                "daily_loss_limit": 2000.0,  # 2% of $100K
                "min_equity": 90000.0,
                "max_margin_usage": 0.0,  # No margin for DEE-BOT
            }
        elif self.bot_type == BotType.SHORGAN_PAPER:
            return {
                "max_position_pct": 10.0,
                "stop_loss_pct": 18.0,
                "daily_loss_limit": 3000.0,  # 3% of $100K
                "min_equity": 80000.0,
                "max_margin_usage": 100.0,  # Can use margin
            }
        else:  # SHORGAN_LIVE
            return {
                "max_position_pct": 10.0,
                "stop_loss_pct": 18.0,
                "daily_loss_limit": 300.0,  # 10% of $3K
                "min_equity": 2000.0,
                "max_margin_usage": 85.0,  # Alert at 85%
            }

    def _atomic_write(self, data: Dict, filepath: Path) -> None:
        """
        Write data atomically using temp file + fsync + rename pattern.
        This ensures no partial writes on crash.
        """
        # Create temp file in same directory (same filesystem for atomic rename)
        fd, tmp_path = tempfile.mkstemp(
            dir=str(filepath.parent),
            prefix=f".{filepath.stem}_",
            suffix=".tmp"
        )

        try:
            # Write to temp file
            with os.fdopen(fd, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk

            # Atomic rename
            os.replace(tmp_path, str(filepath))
            logger.debug(f"Atomic write complete: {filepath}")

        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise e

    def save(self, state: BotState = None) -> None:
        """
        Save state to disk with atomic write.
        Creates backup of previous state first.
        """
        state = state or self._state
        if not state:
            raise ValueError("No state to save")

        # Update timestamp
        state.asof = datetime.utcnow().isoformat() + "Z"

        # Backup current state if exists
        if self.state_file.exists():
            try:
                self._atomic_write(
                    json.loads(self.state_file.read_text()),
                    self.backup_file
                )
            except Exception as e:
                logger.warning(f"Failed to create backup: {e}")

        # Write new state
        self._atomic_write(state.to_dict(), self.state_file)
        self._state = state

        logger.info(f"State saved for {self.bot_type.value} at {state.asof}")

    def load(self, validate: bool = True) -> BotState:
        """
        Load state from disk with optional validation.
        Falls back to backup if primary is corrupted.
        """
        state_data = None

        # Try primary state file
        if self.state_file.exists():
            try:
                state_data = json.loads(self.state_file.read_text())
                logger.info(f"Loaded state from {self.state_file}")
            except json.JSONDecodeError as e:
                logger.error(f"Primary state file corrupted: {e}")

        # Fall back to backup
        if state_data is None and self.backup_file.exists():
            try:
                state_data = json.loads(self.backup_file.read_text())
                logger.warning(f"Loaded state from BACKUP: {self.backup_file}")
            except json.JSONDecodeError as e:
                logger.error(f"Backup state file also corrupted: {e}")

        if state_data is None:
            raise FileNotFoundError(f"No valid state file found for {self.bot_type.value}")

        # Check schema version and migrate if needed
        state_data = self._migrate_schema(state_data)

        # Validate if requested
        if validate:
            self._validate_state(state_data)

        self._state = BotState.from_dict(state_data)
        return self._state

    def _migrate_schema(self, data: Dict) -> Dict:
        """
        Migrate state data to current schema version.
        Add migration logic here as schema evolves.
        """
        file_version = data.get("schema_version", "0.0.0")

        if file_version == SCHEMA_VERSION:
            return data

        logger.info(f"Migrating state from v{file_version} to v{SCHEMA_VERSION}")

        # Example migration: v0.0.0 -> v1.0.0
        if file_version == "0.0.0":
            # Add missing fields with defaults
            data.setdefault("cursors", {})
            data.setdefault("toggles", {"trading_enabled": True})
            data.setdefault("pending_orders", [])
            data["schema_version"] = "1.0.0"

        # Add more migrations as needed

        return data

    def _validate_state(self, data: Dict) -> None:
        """
        Validate state data against rules.
        Raises StateValidationError if validation fails.
        """
        errors = []
        rules = self._validation_rules

        # Check required fields
        required_fields = ["bot_type", "asof", "equity", "positions", "risk"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        if errors:
            raise StateValidationError(f"Validation failed: {errors}")

        # Check equity bounds
        equity = data.get("equity", 0)
        if equity < rules["min_equity"]:
            errors.append(f"Equity ${equity:,.2f} below minimum ${rules['min_equity']:,.2f}")

        # Check risk state
        risk = data.get("risk", {})
        daily_loss = risk.get("daily_loss_current", 0)
        if daily_loss > rules["daily_loss_limit"]:
            errors.append(f"Daily loss ${daily_loss:,.2f} exceeds limit ${rules['daily_loss_limit']:,.2f}")

        # Check margin usage (SHORGAN Live only)
        if self.bot_type == BotType.SHORGAN_LIVE:
            margin_usage = risk.get("margin_usage_pct", 0)
            if margin_usage > rules["max_margin_usage"]:
                errors.append(f"Margin usage {margin_usage:.1f}% exceeds safe limit {rules['max_margin_usage']:.1f}%")

        # Check position concentration
        portfolio_value = data.get("portfolio_value", 1)
        for symbol, pos in data.get("positions", {}).items():
            market_value = abs(pos.get("market_value", 0))
            weight_pct = (market_value / portfolio_value * 100) if portfolio_value > 0 else 0
            if weight_pct > rules["max_position_pct"] * 1.1:  # 10% buffer
                errors.append(f"Position {symbol} at {weight_pct:.1f}% exceeds max {rules['max_position_pct']}%")

        # Check timestamp freshness (warn if stale)
        asof = data.get("asof", "")
        if asof:
            try:
                state_time = datetime.fromisoformat(asof.replace("Z", "+00:00"))
                age = datetime.now(state_time.tzinfo) - state_time
                if age > timedelta(hours=24):
                    logger.warning(f"State is {age.total_seconds()/3600:.1f} hours old")
            except Exception:
                pass

        if errors:
            raise StateValidationError(f"Validation failed: {errors}")

        logger.info(f"State validation passed for {self.bot_type.value}")

    def create_initial_state(self, equity: float, cash: float) -> BotState:
        """Create a fresh initial state for a new bot"""
        state = BotState(
            schema_version=SCHEMA_VERSION,
            bot_type=self.bot_type.value,
            asof=datetime.utcnow().isoformat() + "Z",
            equity=equity,
            cash=cash,
            buying_power=cash,
            portfolio_value=equity,
            positions={},
            risk=RiskState(
                daily_loss_limit=self._validation_rules["daily_loss_limit"],
                daily_loss_current=0.0,
                max_position_pct=self._validation_rules["max_position_pct"],
                max_drawdown_pct=15.0,
                current_drawdown_pct=0.0,
                fee_budget_remaining=100.0,
                margin_usage_pct=0.0,
                stop_loss_pct=self._validation_rules["stop_loss_pct"]
            ).to_dict(),
            cursors={
                "last_order_id": 0,
                "last_fill_seq": 0,
                "last_reconcile_seq": 0
            },
            toggles={
                "trading_enabled": True,
                "stop_loss_active": True,
                "rebalance_enabled": True
            },
            timestamps={
                "created": datetime.utcnow().isoformat() + "Z",
                "last_trade": None,
                "last_reconcile": None,
                "last_heartbeat": datetime.utcnow().isoformat() + "Z"
            },
            pending_orders=[]
        )

        self._state = state
        return state

    @property
    def state(self) -> Optional[BotState]:
        return self._state


class CoherenceChecker:
    """
    Validates that in-memory state matches exchange reality.
    Run before going live after a restart.
    """

    def __init__(self, state_store: StateStore):
        self.state_store = state_store
        self.bot_type = state_store.bot_type
        self._alpaca_client = None

    def _get_alpaca_client(self):
        """Get Alpaca client for the bot type"""
        if self._alpaca_client:
            return self._alpaca_client

        from alpaca.trading.client import TradingClient

        if self.bot_type == BotType.DEE_BOT:
            self._alpaca_client = TradingClient(
                os.getenv('ALPACA_API_KEY_DEE'),
                os.getenv('ALPACA_SECRET_KEY_DEE'),
                paper=True
            )
        elif self.bot_type == BotType.SHORGAN_PAPER:
            self._alpaca_client = TradingClient(
                os.getenv('ALPACA_API_KEY_SHORGAN'),
                os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
                paper=True
            )
        else:  # SHORGAN_LIVE
            self._alpaca_client = TradingClient(
                os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'),
                os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'),
                paper=False
            )

        return self._alpaca_client

    def check_positions(self) -> Tuple[bool, List[str]]:
        """
        Compare in-memory positions to exchange positions.
        Returns (passed, list of discrepancies)
        """
        errors = []
        state = self.state_store.state

        if not state:
            return False, ["No state loaded"]

        try:
            api = self._get_alpaca_client()
            exchange_positions = {p.symbol: p for p in api.get_all_positions()}

            state_positions = set(state.positions.keys())
            exchange_symbols = set(exchange_positions.keys())

            # Check for missing positions
            missing = state_positions - exchange_symbols
            if missing:
                errors.append(f"Positions in state but not on exchange: {missing}")

            # Check for unexpected positions
            extra = exchange_symbols - state_positions
            if extra:
                errors.append(f"Positions on exchange but not in state: {extra}")

            # Check qty and value discrepancies
            for symbol in state_positions & exchange_symbols:
                state_pos = state.positions[symbol]
                exch_pos = exchange_positions[symbol]

                state_qty = state_pos.get("qty", 0)
                exch_qty = float(exch_pos.qty)

                if abs(state_qty - exch_qty) > 0.01:
                    errors.append(f"{symbol}: qty mismatch - state={state_qty}, exchange={exch_qty}")

            passed = len(errors) == 0
            return passed, errors

        except Exception as e:
            return False, [f"Position check failed: {str(e)}"]

    def check_account(self) -> Tuple[bool, List[str]]:
        """
        Verify account values match exchange.
        """
        errors = []
        state = self.state_store.state

        if not state:
            return False, ["No state loaded"]

        try:
            api = self._get_alpaca_client()
            account = api.get_account()

            # Check equity (allow 1% tolerance for market movement)
            exch_equity = float(account.equity)
            state_equity = state.equity
            diff_pct = abs(exch_equity - state_equity) / exch_equity * 100

            if diff_pct > 5:  # 5% tolerance
                errors.append(f"Equity mismatch: state=${state_equity:,.2f}, exchange=${exch_equity:,.2f} ({diff_pct:.1f}% diff)")

            # Check buying power
            exch_bp = float(account.buying_power)
            state_bp = state.buying_power

            if abs(exch_bp - state_bp) > 1000:  # $1000 tolerance
                errors.append(f"Buying power mismatch: state=${state_bp:,.2f}, exchange=${exch_bp:,.2f}")

            passed = len(errors) == 0
            return passed, errors

        except Exception as e:
            return False, [f"Account check failed: {str(e)}"]

    def check_pending_orders(self) -> Tuple[bool, List[str]]:
        """
        Verify pending orders are still valid on exchange.
        """
        errors = []
        state = self.state_store.state

        if not state:
            return False, ["No state loaded"]

        try:
            api = self._get_alpaca_client()
            exchange_orders = {o.id: o for o in api.get_orders(status='open')}

            state_order_ids = {o.get("order_id") for o in state.pending_orders}
            exchange_order_ids = set(exchange_orders.keys())

            # Orders in state but not on exchange (filled or cancelled)
            missing = state_order_ids - exchange_order_ids
            if missing:
                errors.append(f"Pending orders no longer on exchange: {len(missing)} orders")

            passed = len(errors) == 0
            return passed, errors

        except Exception as e:
            return False, [f"Order check failed: {str(e)}"]

    def check_risk_limits(self) -> Tuple[bool, List[str]]:
        """
        Verify risk limits are not breached.
        """
        errors = []
        state = self.state_store.state

        if not state:
            return False, ["No state loaded"]

        rules = self.state_store._validation_rules
        risk = state.risk

        # Daily loss check
        if risk.get("daily_loss_current", 0) > rules["daily_loss_limit"]:
            errors.append(f"Daily loss limit exceeded: ${risk['daily_loss_current']:,.2f} > ${rules['daily_loss_limit']:,.2f}")

        # Margin check (SHORGAN Live)
        if self.bot_type == BotType.SHORGAN_LIVE:
            margin = risk.get("margin_usage_pct", 0)
            if margin > rules["max_margin_usage"]:
                errors.append(f"Margin usage critical: {margin:.1f}% > {rules['max_margin_usage']:.1f}%")

        passed = len(errors) == 0
        return passed, errors

    def full_coherence_check(self) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Run all coherence checks.
        Returns (overall_passed, {check_name: [errors]})
        """
        results = {}

        checks = [
            ("positions", self.check_positions),
            ("account", self.check_account),
            ("pending_orders", self.check_pending_orders),
            ("risk_limits", self.check_risk_limits),
        ]

        all_passed = True
        for name, check_fn in checks:
            passed, errors = check_fn()
            results[name] = errors
            if not passed:
                all_passed = False
                logger.warning(f"Coherence check '{name}' FAILED: {errors}")
            else:
                logger.info(f"Coherence check '{name}' PASSED")

        return all_passed, results


class BotBootstrap:
    """
    Safe startup routine for trading bots.
    Loads state, validates, performs coherence check, then goes live.
    """

    def __init__(self, bot_type: BotType):
        self.bot_type = bot_type
        self.state_store = StateStore(bot_type)
        self.coherence_checker = CoherenceChecker(self.state_store)
        self._is_live = False

    def boot(self, force_live: bool = False) -> Tuple[bool, str]:
        """
        Execute safe boot sequence.

        Returns (success, message)
        """
        logger.info(f"{'='*60}")
        logger.info(f"BOOTING {self.bot_type.value}")
        logger.info(f"{'='*60}")

        # Step 1: Load state
        try:
            state = self.state_store.load(validate=True)
            logger.info(f"[1/4] State loaded: {state.asof}")
        except FileNotFoundError:
            logger.warning("[1/4] No state file found - creating initial state")
            state = self._create_initial_state_from_exchange()
            self.state_store.save(state)
        except StateValidationError as e:
            logger.error(f"[1/4] State validation FAILED: {e}")
            if not force_live:
                return False, f"State validation failed: {e}"

        # Step 2: Coherence check
        logger.info("[2/4] Running coherence checks...")
        passed, results = self.coherence_checker.full_coherence_check()

        if not passed:
            logger.error(f"[2/4] Coherence check FAILED")
            for check, errors in results.items():
                if errors:
                    logger.error(f"  - {check}: {errors}")

            if not force_live:
                return False, f"Coherence check failed: {results}"
            else:
                logger.warning("Force live enabled - proceeding despite coherence failures")
        else:
            logger.info("[2/4] Coherence checks PASSED")

        # Step 3: Dry-run validation
        logger.info("[3/4] Performing dry-run validation...")
        dry_run_ok = self._dry_run_validation()

        if not dry_run_ok:
            logger.error("[3/4] Dry-run validation FAILED")
            if not force_live:
                return False, "Dry-run validation failed"
        else:
            logger.info("[3/4] Dry-run validation PASSED")

        # Step 4: Go live
        logger.info("[4/4] Going LIVE...")
        self._is_live = True

        # Update heartbeat
        state.timestamps["last_heartbeat"] = datetime.utcnow().isoformat() + "Z"
        self.state_store.save(state)

        logger.info(f"{'='*60}")
        logger.info(f"{self.bot_type.value} BOOT COMPLETE - LIVE")
        logger.info(f"{'='*60}")

        return True, "Boot successful"

    def _create_initial_state_from_exchange(self) -> BotState:
        """Create initial state by fetching from exchange"""
        from alpaca.trading.client import TradingClient

        if self.bot_type == BotType.DEE_BOT:
            api = TradingClient(
                os.getenv('ALPACA_API_KEY_DEE'),
                os.getenv('ALPACA_SECRET_KEY_DEE'),
                paper=True
            )
        elif self.bot_type == BotType.SHORGAN_PAPER:
            api = TradingClient(
                os.getenv('ALPACA_API_KEY_SHORGAN'),
                os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
                paper=True
            )
        else:
            api = TradingClient(
                os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'),
                os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'),
                paper=False
            )

        account = api.get_account()
        equity = float(account.equity)
        cash = float(account.cash)

        state = self.state_store.create_initial_state(equity, cash)

        # Populate positions
        for pos in api.get_all_positions():
            state.positions[pos.symbol] = {
                "symbol": pos.symbol,
                "qty": float(pos.qty),
                "avg_entry_price": float(pos.avg_entry_price),
                "current_price": float(pos.current_price),
                "market_value": float(pos.market_value),
                "pnl_realized": 0.0,
                "pnl_unrealized": float(pos.unrealized_pl),
                "pnl_pct": float(pos.unrealized_plpc) * 100,
                "side": "long" if float(pos.qty) > 0 else "short"
            }

        return state

    def _dry_run_validation(self) -> bool:
        """
        Perform dry-run checks before going live.
        Validates that trading logic would produce safe results.
        """
        state = self.state_store.state

        # Check trading is enabled
        if not state.toggles.get("trading_enabled", True):
            logger.warning("Trading is disabled in state toggles")
            return True  # Not an error, just disabled

        # Check we have reasonable equity
        if state.equity < self.state_store._validation_rules["min_equity"]:
            logger.error(f"Equity ${state.equity:,.2f} too low")
            return False

        # Check risk limits are sensible
        risk = state.risk
        if risk.get("daily_loss_limit", 0) <= 0:
            logger.error("Invalid daily loss limit")
            return False

        return True

    @property
    def is_live(self) -> bool:
        return self._is_live

    @property
    def state(self) -> Optional[BotState]:
        return self.state_store.state


# Convenience functions
def boot_dee_bot(force: bool = False) -> Tuple[bool, str]:
    """Boot DEE-BOT with safe startup"""
    bootstrap = BotBootstrap(BotType.DEE_BOT)
    return bootstrap.boot(force_live=force)


def boot_shorgan_paper(force: bool = False) -> Tuple[bool, str]:
    """Boot SHORGAN Paper with safe startup"""
    bootstrap = BotBootstrap(BotType.SHORGAN_PAPER)
    return bootstrap.boot(force_live=force)


def boot_shorgan_live(force: bool = False) -> Tuple[bool, str]:
    """Boot SHORGAN Live with safe startup"""
    bootstrap = BotBootstrap(BotType.SHORGAN_LIVE)
    return bootstrap.boot(force_live=force)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Bot State Management")
    parser.add_argument("bot", choices=["dee", "shorgan-paper", "shorgan-live"], help="Bot to manage")
    parser.add_argument("--boot", action="store_true", help="Run boot sequence")
    parser.add_argument("--force", action="store_true", help="Force live even if checks fail")
    parser.add_argument("--check", action="store_true", help="Run coherence check only")
    parser.add_argument("--save", action="store_true", help="Save current state from exchange")

    args = parser.parse_args()

    # Map bot name to type
    bot_map = {
        "dee": BotType.DEE_BOT,
        "shorgan-paper": BotType.SHORGAN_PAPER,
        "shorgan-live": BotType.SHORGAN_LIVE
    }
    bot_type = bot_map[args.bot]

    if args.boot:
        bootstrap = BotBootstrap(bot_type)
        success, msg = bootstrap.boot(force_live=args.force)
        print(f"\nResult: {'SUCCESS' if success else 'FAILED'} - {msg}")
        sys.exit(0 if success else 1)

    elif args.check:
        store = StateStore(bot_type)
        try:
            store.load()
            checker = CoherenceChecker(store)
            passed, results = checker.full_coherence_check()
            print(f"\nCoherence: {'PASSED' if passed else 'FAILED'}")
            for check, errors in results.items():
                status = "OK" if not errors else f"FAIL: {errors}"
                print(f"  {check}: {status}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.save:
        bootstrap = BotBootstrap(bot_type)
        state = bootstrap._create_initial_state_from_exchange()
        bootstrap.state_store.save(state)
        print(f"State saved to {bootstrap.state_store.state_file}")

    else:
        parser.print_help()
