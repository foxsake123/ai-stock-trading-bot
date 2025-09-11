"""
Get your Telegram Chat ID
1. Send a message to your bot first
2. Run this script to get your chat ID
"""

import requests
import json

# Your bot token from .env
BOT_TOKEN = "8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c"

def get_chat_id():
    """Get chat ID from recent messages"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        
        if data['result']:
            # Get the most recent message
            for update in data['result']:
                if 'message' in update:
                    chat_id = update['message']['chat']['id']
                    username = update['message']['chat'].get('username', 'Unknown')
                    first_name = update['message']['chat'].get('first_name', '')
                    
                    print(f"Found Chat ID: {chat_id}")
                    print(f"Username: @{username}")
                    print(f"Name: {first_name}")
                    print("\nAdd this to your .env file:")
                    print(f"TELEGRAM_CHAT_ID={chat_id}")
                    return chat_id
            
            print("No messages found. Please send a message to your bot first!")
        else:
            print("No updates found. Please send a message to your bot first!")
            print("\n1. Open Telegram")
            print("2. Search for your bot")
            print("3. Send any message (like 'Hello')")
            print("4. Run this script again")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("TELEGRAM CHAT ID FINDER")
    print("="*50)
    get_chat_id()