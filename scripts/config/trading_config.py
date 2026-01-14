"""
Trading Configuration
=====================
Centralized trading account and settings configuration.

Author: AI Trading Bot System
Date: January 14, 2026
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")


# =============================================================================
# ACCOUNT CONFIGURATIONS
# =============================================================================

DEE_BOT_CONFIG = {
    'API_KEY': os.getenv('ALPACA_API_KEY_DEE'),
    'SECRET_KEY': os.getenv('ALPACA_SECRET_KEY_DEE'),
    'BASE_URL': 'https://paper-api.alpaca.markets'
}

SHORGAN_PAPER_CONFIG = {
    'API_KEY': os.getenv('ALPACA_API_KEY_SHORGAN'),
    'SECRET_KEY': os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    'BASE_URL': 'https://paper-api.alpaca.markets'
}

SHORGAN_LIVE_CONFIG = {
    'API_KEY': os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'),
    'SECRET_KEY': os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'),
    'BASE_URL': 'https://api.alpaca.markets'
}

DEE_BOT_LIVE_CONFIG = {
    'API_KEY': os.getenv('ALPACA_LIVE_API_KEY_DEE'),
    'SECRET_KEY': os.getenv('ALPACA_LIVE_SECRET_KEY_DEE'),
    'BASE_URL': 'https://api.alpaca.markets'
}


# =============================================================================
# FEATURE FLAGS
# =============================================================================

SHORGAN_LIVE_TRADING = True  # Enable SHORGAN live trading
DEE_LIVE_TRADING = False     # DEE live trading disabled


# =============================================================================
# SAFETY SETTINGS
# =============================================================================

REQUIRE_LIVE_CONFIRMATION = os.getenv('REQUIRE_LIVE_CONFIRMATION', 'true').lower() == 'true'
MAX_RETRY_ATTEMPTS = 3


# =============================================================================
# TRADING SETTINGS
# =============================================================================

@dataclass
class TradingSettings:
    """Trading settings for an account."""
    capital: float
    max_position_size: float
    min_position_size: float
    cash_buffer: float
    max_positions: int
    max_daily_loss: float
    max_trades_per_day: int
    stop_loss_pct: float = 0.08
    allow_shorts: bool = False
    allow_options: bool = False
    long_only: bool = True


# DEE-BOT Settings ($100K Paper, $10K Live)
DEE_SETTINGS = TradingSettings(
    capital=100000.0,
    max_position_size=10000.0,   # 10% of capital
    min_position_size=4000.0,    # 4% of capital
    cash_buffer=5000.0,          # 5% buffer
    max_positions=12,
    max_daily_loss=5000.0,       # 5% max daily loss
    max_trades_per_day=5,
    stop_loss_pct=0.08,          # 8% stop loss
    allow_shorts=False,
    allow_options=False,
    long_only=True
)

# SHORGAN-BOT Settings ($3K Live)
SHORGAN_SETTINGS = TradingSettings(
    capital=3000.0,
    max_position_size=290.0,     # ~10% of capital
    min_position_size=90.0,      # 3% of capital
    cash_buffer=0.0,             # Aggressive - no buffer
    max_positions=10,
    max_daily_loss=300.0,        # 10% max daily loss
    max_trades_per_day=5,
    stop_loss_pct=0.18,          # 18% stop loss (higher volatility)
    allow_shorts=False,          # Cash account
    allow_options=True,
    long_only=False
)


# =============================================================================
# VALIDATION SETTINGS
# =============================================================================

VALIDATION_CONFIG = {
    'base_threshold': 0.55,           # Base approval threshold
    'external_confidence_weight': 0.7, # Weight for external signals
    'agent_confidence_weight': 0.3,    # Weight for multi-agent consensus
    'veto_penalty_weak': 0.20,         # Penalty for weak internal consensus (<30%)
    'veto_penalty_moderate': 0.10,     # Penalty for moderate consensus (30-50%)
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_trading_client(account: str, live: bool = False):
    """
    Get a configured Alpaca trading client.

    Args:
        account: 'dee' or 'shorgan'
        live: True for live trading, False for paper

    Returns:
        Alpaca TradingClient instance
    """
    try:
        from alpaca.trading.client import TradingClient
    except ImportError:
        import alpaca_trade_api as tradeapi

        config = _get_config(account, live)
        if not config['API_KEY'] or not config['SECRET_KEY']:
            raise ValueError(f"API keys not found for {account} ({'live' if live else 'paper'})")

        return tradeapi.REST(
            config['API_KEY'],
            config['SECRET_KEY'],
            config['BASE_URL']
        )

    config = _get_config(account, live)
    if not config['API_KEY'] or not config['SECRET_KEY']:
        raise ValueError(f"API keys not found for {account} ({'live' if live else 'paper'})")

    return TradingClient(
        config['API_KEY'],
        config['SECRET_KEY'],
        paper=not live
    )


def _get_config(account: str, live: bool) -> dict:
    """Get the appropriate config dict."""
    account = account.lower()
    if account == 'dee':
        return DEE_BOT_LIVE_CONFIG if live else DEE_BOT_CONFIG
    elif account == 'shorgan':
        return SHORGAN_LIVE_CONFIG if live else SHORGAN_PAPER_CONFIG
    else:
        raise ValueError(f"Unknown account: {account}")


def get_account_settings(account: str) -> TradingSettings:
    """Get trading settings for an account."""
    account = account.lower()
    if account == 'dee':
        return DEE_SETTINGS
    elif account == 'shorgan':
        return SHORGAN_SETTINGS
    else:
        raise ValueError(f"Unknown account: {account}")


# =============================================================================
# VALIDATION
# =============================================================================

def validate_config():
    """Validate that required environment variables are set."""
    errors = []

    # Check DEE-BOT paper (required)
    if not DEE_BOT_CONFIG['API_KEY'] or not DEE_BOT_CONFIG['SECRET_KEY']:
        errors.append("DEE-BOT paper API keys missing")

    # Check SHORGAN paper (required)
    if not SHORGAN_PAPER_CONFIG['API_KEY'] or not SHORGAN_PAPER_CONFIG['SECRET_KEY']:
        errors.append("SHORGAN paper API keys missing")

    # Check SHORGAN live (required if enabled)
    if SHORGAN_LIVE_TRADING:
        if not SHORGAN_LIVE_CONFIG['API_KEY'] or not SHORGAN_LIVE_CONFIG['SECRET_KEY']:
            errors.append("SHORGAN live API keys missing but live trading enabled")

    return errors


if __name__ == "__main__":
    # Test configuration
    print("Trading Configuration Test")
    print("=" * 50)

    errors = validate_config()
    if errors:
        print("Configuration Errors:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("All required configurations found!")

    print("\nAccount Settings:")
    print(f"  DEE-BOT: ${DEE_SETTINGS.capital:,.0f} capital, {DEE_SETTINGS.max_positions} max positions")
    print(f"  SHORGAN: ${SHORGAN_SETTINGS.capital:,.0f} capital, {SHORGAN_SETTINGS.max_positions} max positions")

    print("\nFeature Flags:")
    print(f"  SHORGAN Live Trading: {SHORGAN_LIVE_TRADING}")
    print(f"  DEE Live Trading: {DEE_LIVE_TRADING}")
