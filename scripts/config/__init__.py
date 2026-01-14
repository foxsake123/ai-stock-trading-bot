"""
Trading Bot Configuration
=========================
Centralized configuration for all trading accounts and settings.

Author: AI Trading Bot System
Date: January 14, 2026
"""

from .trading_config import (
    # Account configurations
    DEE_BOT_CONFIG,
    DEE_BOT_LIVE_CONFIG,
    SHORGAN_PAPER_CONFIG,
    SHORGAN_LIVE_CONFIG,

    # Trading settings
    DEE_SETTINGS,
    SHORGAN_SETTINGS,

    # Feature flags
    SHORGAN_LIVE_TRADING,
    DEE_LIVE_TRADING,

    # Safety settings
    REQUIRE_LIVE_CONFIRMATION,
    MAX_RETRY_ATTEMPTS,

    # Helper functions
    get_trading_client,
    get_account_settings,
)

__all__ = [
    'DEE_BOT_CONFIG',
    'DEE_BOT_LIVE_CONFIG',
    'SHORGAN_PAPER_CONFIG',
    'SHORGAN_LIVE_CONFIG',
    'DEE_SETTINGS',
    'SHORGAN_SETTINGS',
    'SHORGAN_LIVE_TRADING',
    'DEE_LIVE_TRADING',
    'REQUIRE_LIVE_CONFIRMATION',
    'MAX_RETRY_ATTEMPTS',
    'get_trading_client',
    'get_account_settings',
]
