"""
Update DEE-BOT API Keys in .env file
Run this after regenerating keys in Alpaca dashboard
"""

import os
from dotenv import load_dotenv

def update_dee_keys():
    """Interactive script to update DEE-BOT API keys"""

    print("=" * 80)
    print("DEE-BOT API KEY UPDATE")
    print("=" * 80)
    print()
    print("Have you regenerated API keys in Alpaca dashboard?")
    print("(Go to https://app.alpaca.markets/ → API Keys → Generate New Key)")
    print("Make sure 'Trading' permission is ENABLED!")
    print()

    response = input("Ready to update? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled. Update keys in Alpaca first, then run this script again.")
        return

    print()
    print("Enter your NEW DEE-BOT API credentials:")
    print("(These will update ALPACA_API_KEY and ALPACA_SECRET_KEY in .env)")
    print()

    new_key = input("DEE-BOT API Key ID: ").strip()
    new_secret = input("DEE-BOT Secret Key: ").strip()

    if not new_key or not new_secret:
        print("Error: Keys cannot be empty")
        return

    print()
    print("Updating .env file...")

    # Read current .env
    env_path = '.env'
    if not os.path.exists(env_path):
        print(f"Error: {env_path} not found")
        return

    with open(env_path, 'r') as f:
        lines = f.readlines()

    # Update keys
    updated_lines = []
    key_updated = False
    secret_updated = False

    for line in lines:
        if line.startswith('ALPACA_API_KEY='):
            updated_lines.append(f'ALPACA_API_KEY={new_key}\n')
            key_updated = True
            print(f"Updated: ALPACA_API_KEY={new_key[:10]}...")
        elif line.startswith('ALPACA_SECRET_KEY='):
            updated_lines.append(f'ALPACA_SECRET_KEY={new_secret}\n')
            secret_updated = True
            print(f"Updated: ALPACA_SECRET_KEY={new_secret[:10]}...")
        else:
            updated_lines.append(line)

    # Add if not found
    if not key_updated:
        updated_lines.append(f'ALPACA_API_KEY={new_key}\n')
        print(f"Added: ALPACA_API_KEY={new_key[:10]}...")

    if not secret_updated:
        updated_lines.append(f'ALPACA_SECRET_KEY={new_secret}\n')
        print(f"Added: ALPACA_SECRET_KEY={new_secret[:10]}...")

    # Write updated .env
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)

    print()
    print("✅ .env file updated successfully!")
    print()
    print("Next step: Run verification script to test trading permissions")
    print("Command: python verify_dee_trading.py")
    print()

if __name__ == '__main__':
    update_dee_keys()
