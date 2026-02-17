"""
Daily automated update script for DEE-BOT positions from Alpaca
Runs daily at 4:00 PM ET to sync actual positions
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")


import os
import sys
from datetime import datetime
from alpaca.trading.client import TradingClient
import pandas as pd
import json

# DEE-BOT Alpaca credentials
API_KEY = os.getenv('ALPACA_API_KEY_DEE')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY_DEE')

def update_dee_bot_positions():
    """Fetch and update DEE-BOT positions from Alpaca"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"DEE-BOT DAILY POSITION UPDATE - {timestamp}")
    print(f"{'='*60}\n")

    try:
        # Initialize Alpaca client
        trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

        # Get account info
        account = trading_client.get_account()
        print(f"Account Status: {account.status}")
        print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"Buying Power: ${float(account.buying_power):,.2f}")
        print(f"Cash: ${float(account.cash):,.2f}\n")

        # Get all positions
        positions = trading_client.get_all_positions()

        if positions:
            print(f"Found {len(positions)} positions:\n")

            position_data = []
            total_pnl = 0

            for position in positions:
                symbol = position.symbol
                qty = int(position.qty)
                avg_price = float(position.avg_entry_price)
                current_price = float(position.current_price)
                pnl = float(position.unrealized_pl)
                pnl_pct = float(position.unrealized_plpc) * 100

                print(f"  {symbol}: {qty} shares @ ${avg_price:.2f} -> ${current_price:.2f}")
                print(f"    P&L: ${pnl:+,.2f} ({pnl_pct:+.2f}%)")

                position_data.append({
                    'symbol': symbol,
                    'quantity': qty,
                    'avg_price': round(avg_price, 2),
                    'current_price': round(current_price, 2),
                    'pnl': round(pnl, 2),
                    'pnl_pct': f"{pnl_pct:.2f}%",
                    'side': 'long' if qty > 0 else 'short',
                    'date_acquired': '2025-09-16'  # Update if tracking actual dates
                })

                total_pnl += pnl

            # Save to CSV
            df = pd.DataFrame(position_data)
            csv_path = '../../portfolio-holdings/dee-bot/current/positions.csv'
            df.to_csv(csv_path, index=False)

            print(f"\n[SUCCESS] Updated {csv_path}")
            print(f"Total P&L: ${total_pnl:+,.2f}")

            # Also save a timestamped snapshot for historical tracking
            snapshot_date = datetime.now().strftime("%Y-%m-%d")
            snapshot_path = f'../../portfolio-holdings/dee-bot/historical/positions_{snapshot_date}.csv'
            df.to_csv(snapshot_path, index=False)
            print(f"[SUCCESS] Saved snapshot: {snapshot_path}")

            # Update the DEE-BOT config file with current stats
            update_config_file(account, positions, total_pnl)

            # Log the update
            log_update(len(positions), total_pnl, float(account.portfolio_value))

        else:
            print("[WARNING] NO POSITIONS FOUND IN DEE-BOT ACCOUNT")

            # Create empty positions file
            empty_df = pd.DataFrame(columns=['symbol', 'quantity', 'avg_price', 'current_price', 'pnl', 'pnl_pct', 'side', 'date_acquired'])
            empty_df.to_csv('../../portfolio-holdings/dee-bot/current/positions.csv', index=False)

    except Exception as e:
        print(f"[ERROR] updating DEE-BOT positions: {e}")
        log_error(str(e))
        return False

    print(f"\n{'='*60}")
    print("DEE-BOT position update completed successfully!")
    print(f"{'='*60}\n")
    return True

def update_config_file(account, positions, total_pnl):
    """Update the DEE-BOT config file with current portfolio stats"""

    config_path = '../../01_trading_system/config/dee_bot_config.json'

    try:
        # Read existing config
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Update portfolio values
        config['configuration']['trading_parameters']['portfolio_value'] = float(account.portfolio_value)
        config['configuration']['trading_parameters']['current_positions'] = len(positions)

        # Update current portfolio section
        position_list = []
        for pos in positions:
            position_list.append({
                "symbol": pos.symbol,
                "shares": int(pos.qty),
                "avg_price": float(pos.avg_entry_price),
                "market_value": float(pos.market_value),
                "unrealized_pl": float(pos.unrealized_pl)
            })

        config['current_portfolio']['positions'] = position_list
        config['current_portfolio']['total_market_value'] = sum(float(p.market_value) for p in positions)
        config['current_portfolio']['cash_available'] = float(account.cash)

        # Update activity
        config['latest_activity']['date'] = datetime.now().strftime("%Y-%m-%d")
        config['latest_activity']['action'] = "Daily position update"

        # Write back
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"[SUCCESS] Updated config file: {config_path}")

    except Exception as e:
        print(f"[WARNING] Could not update config file: {e}")

def log_update(position_count, total_pnl, portfolio_value):
    """Log the daily update for tracking"""

    log_path = '../../09_logs/dee_bot_daily_updates.log'

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} | Positions: {position_count} | P&L: ${total_pnl:+,.2f} | Value: ${portfolio_value:,.2f}\n"

    try:
        with open(log_path, 'a') as f:
            f.write(log_entry)
        print(f"[SUCCESS] Logged update to: {log_path}")
    except Exception as e:
        print(f"[WARNING] Could not write to log: {e}")

def log_error(error_msg):
    """Log errors for debugging"""

    error_log_path = '../../09_logs/dee_bot_errors.log'

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_entry = f"{timestamp} | ERROR: {error_msg}\n"

    try:
        with open(error_log_path, 'a') as f:
            f.write(error_entry)
    except:
        pass

if __name__ == "__main__":
    # Run the update
    success = update_dee_bot_positions()

    # Exit with appropriate code for Task Scheduler
    sys.exit(0 if success else 1)