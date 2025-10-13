"""
Update DEE-BOT API Keys - Simple Version
"""

import os

def update_keys():
    print("=" * 80)
    print("DEE-BOT API KEY UPDATE")
    print("=" * 80)
    print()
    print("Paste your NEW API credentials from Alpaca:")
    print()

    new_key = input("API Key ID (starts with PK): ").strip()
    new_secret = input("Secret Key: ").strip()

    if not new_key or not new_secret:
        print("Error: Keys cannot be empty")
        return

    print()
    print("Updating .env file...")

    env_path = '.env'
    with open(env_path, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    key_found = False
    secret_found = False

    for line in lines:
        if line.startswith('ALPACA_API_KEY=') and not line.startswith('ALPACA_API_KEY_SHORGAN'):
            updated_lines.append(f'ALPACA_API_KEY={new_key}\n')
            key_found = True
            print(f"Updated: ALPACA_API_KEY={new_key[:10]}...")
        elif line.startswith('ALPACA_SECRET_KEY=') and not line.startswith('ALPACA_SECRET_KEY_SHORGAN'):
            updated_lines.append(f'ALPACA_SECRET_KEY={new_secret}\n')
            secret_found = True
            print(f"Updated: ALPACA_SECRET_KEY={new_secret[:10]}...")
        else:
            updated_lines.append(line)

    if not key_found:
        updated_lines.append(f'ALPACA_API_KEY={new_key}\n')
    if not secret_found:
        updated_lines.append(f'ALPACA_SECRET_KEY={new_secret}\n')

    with open(env_path, 'w') as f:
        f.writelines(updated_lines)

    print()
    print("[OK] .env file updated!")
    print()
    print("Next: python verify_dee_trading.py")

if __name__ == '__main__':
    update_keys()
