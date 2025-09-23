"""
Update Both DEE-BOT and SHORGAN-BOT Positions
Runs daily at 9:30 AM and 4:00 PM to sync with Alpaca
"""

import os
import sys
import csv
from datetime import datetime
from alpaca.trading.client import TradingClient

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Bot configurations
BOTS = {
    'DEE': {
        'api_key': 'PK6FZK4DAQVTD7DYVH78',
        'secret_key': 'OvdGPcvzYHQmJnGhLVxsvrobMcrpYLmqGKYesmcS',
        'csv_file': 'scripts-and-data/daily-csv/dee-bot-positions.csv',
        'name': 'DEE-BOT'
    },
    'SHORGAN': {
        'api_key': 'PKJRLSB2MFEJUSK6UK2E',
        'secret_key': 'eTSRAfs9AobCJyqGkycrHFLdD2sAOp8DpqOGVvvr',
        'csv_file': 'scripts-and-data/daily-csv/shorgan-bot-positions.csv',
        'name': 'SHORGAN-BOT'
    }
}

def update_bot_positions(bot_config):
    """Update positions for a single bot"""
    bot_name = bot_config['name']
    print(f"\nUpdating {bot_name} positions...")

    try:
        # Initialize Alpaca client
        client = TradingClient(
            bot_config['api_key'],
            bot_config['secret_key'],
            paper=True
        )

        # Get current positions
        positions = client.get_all_positions()

        # Get account info
        account = client.get_account()

        # Prepare CSV data
        csv_data = []
        total_market_value = 0

        for position in positions:
            market_value = float(position.market_value)
            total_market_value += market_value

            csv_data.append({
                'symbol': position.symbol,
                'qty': int(position.qty),
                'avg_entry_price': float(position.avg_entry_price),
                'current_price': float(position.current_price),
                'market_value': market_value,
                'unrealized_pl': float(position.unrealized_pl),
                'unrealized_plpc': float(position.unrealized_plpc) * 100,
                'side': position.side,
                'exchange': position.exchange,
                'asset_class': position.asset_class,
                'timestamp': datetime.now().isoformat()
            })

        # Sort by market value (largest positions first)
        csv_data.sort(key=lambda x: abs(x['market_value']), reverse=True)

        # Write to CSV
        csv_path = bot_config['csv_file']
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        with open(csv_path, 'w', newline='') as csvfile:
            if csv_data:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)

        # Print summary
        print(f"[SUCCESS] {bot_name} updated successfully:")
        print(f"  - Positions: {len(positions)}")
        print(f"  - Total Market Value: ${total_market_value:,.2f}")
        print(f"  - Cash: ${float(account.cash):,.2f}")
        print(f"  - Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"  - CSV saved to: {csv_path}")

        return True

    except Exception as e:
        print(f"[ERROR] Error updating {bot_name}: {e}")
        return False

def main():
    """Update all bot positions"""
    print("=" * 60)
    print("AUTOMATED POSITION UPDATE - ALL BOTS")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    print("=" * 60)

    success_count = 0

    # Update each bot
    for bot_key, bot_config in BOTS.items():
        if update_bot_positions(bot_config):
            success_count += 1

    print("\n" + "=" * 60)
    print(f"Update Complete: {success_count}/{len(BOTS)} bots updated successfully")
    print("=" * 60)

    if success_count == len(BOTS):
        print("\n[SUCCESS] All positions synced with Alpaca")
        print("[SUCCESS] CSV files updated")
        print("[SUCCESS] Ready for trading day")
        return 0
    else:
        print("\n[WARNING] Some bots failed to update")
        print("Check error messages above")
        return 1

if __name__ == "__main__":
    sys.exit(main())