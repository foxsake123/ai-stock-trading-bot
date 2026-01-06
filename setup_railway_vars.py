#!/usr/bin/env python3
"""Set up Railway environment variables from .env file."""
import os
import subprocess
from dotenv import dotenv_values

# Load .env file
env_vars = dotenv_values(".env")

# Key variables needed for Railway deployment
REQUIRED_VARS = [
    # Core APIs
    "ANTHROPIC_API_KEY",
    "FINANCIAL_DATASETS_API_KEY",

    # DEE-BOT Paper
    "ALPACA_API_KEY_DEE",
    "ALPACA_SECRET_KEY_DEE",
    "ALPACA_API_KEY",
    "ALPACA_SECRET_KEY",
    "ALPACA_BASE_URL",

    # SHORGAN Paper
    "ALPACA_API_KEY_SHORGAN",
    "ALPACA_SECRET_KEY_SHORGAN",

    # SHORGAN Live
    "ALPACA_LIVE_API_KEY_SHORGAN",
    "ALPACA_LIVE_SECRET_KEY_SHORGAN",
    "ALPACA_API_KEY_SHORGAN_LIVE",
    "ALPACA_SECRET_KEY_SHORGAN_LIVE",

    # Telegram
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",

    # Settings
    "REQUIRE_LIVE_CONFIRMATION",
]

print("Setting Railway environment variables...")
print("=" * 50)

for var in REQUIRED_VARS:
    value = env_vars.get(var)
    if value:
        # Mask the value for display
        display_value = value[:8] + "..." if len(value) > 12 else value
        print(f"Setting {var}={display_value}")

        # Set in Railway (use shell=True for Windows npm packages)
        result = subprocess.run(
            f'railway variables --service trading-bot --set "{var}={value}" --skip-deploys',
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode != 0:
            print(f"  [ERROR] {result.stderr.strip()}")
        else:
            print(f"  [OK]")
    else:
        print(f"[SKIP] {var} not found in .env")

print("=" * 50)
print("Done! Variables set in Railway project.")
