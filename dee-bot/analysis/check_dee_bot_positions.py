"""
Check actual DEE-BOT positions from Alpaca API
"""

import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
import pandas as pd

# DEE-BOT Alpaca credentials (from config)
API_KEY = "PK6FZK4DAQVTD7DYVH78"
SECRET_KEY = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"

print("="*60)
print("CHECKING DEE-BOT ACTUAL POSITIONS FROM ALPACA")
print("="*60)

if not SECRET_KEY:
    print("ERROR: ALPACA_SECRET_KEY environment variable not set")
    print("Attempting to read from config file...")

    # Try to read from config
    import json
    try:
        with open('scripts-and-data/automation/config_dee.json', 'r') as f:
            config = json.load(f)
            SECRET_KEY = config.get('alpaca_secret_key', '')
    except:
        print("Could not read config file")

if SECRET_KEY and SECRET_KEY != "YOUR_SECRET_KEY":
    # Initialize Alpaca client
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

    # Get account info
    account = trading_client.get_account()
    print(f"Account Status: {account.status}")
    print(f"Buying Power: ${float(account.buying_power):,.2f}")
    print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print()

    # Get all positions
    positions = trading_client.get_all_positions()

    print("ACTUAL POSITIONS FROM ALPACA:")
    print("-" * 40)

    if positions:
        position_data = []
        for position in positions:
            print(f"{position.symbol}: {position.qty} shares @ ${float(position.avg_entry_price):.2f}")
            print(f"  Current: ${float(position.current_price):.2f}")
            print(f"  Market Value: ${float(position.market_value):.2f}")
            print(f"  P&L: ${float(position.unrealized_pl):+.2f} ({float(position.unrealized_plpc)*100:+.2f}%)")
            print()

            position_data.append({
                'symbol': position.symbol,
                'quantity': int(position.qty),
                'avg_price': float(position.avg_entry_price),
                'current_price': float(position.current_price),
                'pnl': float(position.unrealized_pl),
                'pnl_pct': f"{float(position.unrealized_plpc)*100:.2f}%",
                'side': 'long' if float(position.qty) > 0 else 'short',
                'date_acquired': '2025-09-16'  # Update this if needed
            })

        # Save to CSV
        df = pd.DataFrame(position_data)
        df.to_csv('portfolio-holdings/dee-bot/current/positions_from_alpaca.csv', index=False)
        print()
        print("Saved actual positions to: positions_from_alpaca.csv")

        # Compare with stored positions
        print()
        print("COMPARING WITH STORED POSITIONS:")
        print("-" * 40)

        stored_df = pd.read_csv('portfolio-holdings/dee-bot/current/positions.csv')

        stored_symbols = set(stored_df['symbol'].tolist())
        actual_symbols = set(df['symbol'].tolist())

        if stored_symbols != actual_symbols:
            print(f"MISMATCH IN HOLDINGS!")
            print(f"Stored: {stored_symbols}")
            print(f"Actual: {actual_symbols}")
            print(f"Missing from stored: {actual_symbols - stored_symbols}")
            print(f"Extra in stored: {stored_symbols - actual_symbols}")
        else:
            print("Symbol lists match")

    else:
        print("NO POSITIONS FOUND IN ALPACA ACCOUNT")

else:
    print("ERROR: Cannot connect to Alpaca - missing or invalid secret key")
    print()
    print("To fix this:")
    print("1. Set environment variable: set ALPACA_SECRET_KEY=your_actual_key")
    print("2. Or update scripts-and-data/automation/config_dee.json")

print()
print("="*60)