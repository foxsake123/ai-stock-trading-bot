#!/usr/bin/env python
"""
Send Trading Report to Telegram
Sends the daily trading report to your Telegram chat
"""

import os
import requests
import json
from datetime import datetime
from pathlib import Path

def send_to_telegram(bot_token, chat_id, message_text):
    """
    Send message to Telegram using Bot API
    
    Args:
        bot_token (str): Telegram bot token from @BotFather
        chat_id (str): Chat ID (can be user ID or group ID)
        message_text (str): Message content
    """
    
    # Telegram API endpoint
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # Telegram has a 4096 character limit per message
    max_length = 4000  # Leave some buffer
    
    if len(message_text) <= max_length:
        # Send single message
        payload = {
            'chat_id': chat_id,
            'text': message_text,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("✅ Message sent to Telegram successfully!")
            return True
        else:
            print(f"❌ Failed to send to Telegram: {response.status_code}")
            print(response.text)
            return False
    
    else:
        # Split long message into chunks
        print(f"Message too long ({len(message_text)} chars), splitting...")
        
        chunks = []
        lines = message_text.split('\n')
        current_chunk = ""
        
        for line in lines:
            if len(current_chunk + line + '\n') <= max_length:
                current_chunk += line + '\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Send all chunks
        success = True
        for i, chunk in enumerate(chunks):
            payload = {
                'chat_id': chat_id,
                'text': f"*Part {i+1}/{len(chunks)}*\n\n{chunk}",
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code != 200:
                print(f"❌ Failed to send part {i+1}: {response.text}")
                success = False
            else:
                print(f"✅ Sent part {i+1}/{len(chunks)}")
        
        return success

def send_trading_report():
    """Send the full trading report"""
    
    # Read the trading report
    report_file = Path("EMAIL_TRADING_SUMMARY.txt")
    if not report_file.exists():
        print("Error: Trading report not found!")
        return False
    
    with open(report_file, 'r') as f:
        report_content = f.read()
    
    # Format for Telegram (use markdown formatting)
    telegram_message = f"""🤖 *AI Trading Bot Report*

📅 *Date:* September 10, 2025
💰 *Total Capital:* $200,000
📊 *Systems:* DEE-BOT & Shorgan-Bot

```
{report_content}
```

🚨 *This is paper trading for testing purposes only*
"""
    
    # Get credentials from environment variables
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("""
❌ Telegram credentials not configured!

Please set environment variables:
  export TELEGRAM_BOT_TOKEN="your_bot_token"
  export TELEGRAM_CHAT_ID="your_chat_id"

To get these:
1. Message @BotFather on Telegram
2. Send /newbot and follow instructions
3. Copy the bot token
4. For chat ID, message @userinfobot or use your user ID
        """)
        return False
    
    return send_to_telegram(bot_token, chat_id, telegram_message)

def send_summary_to_telegram():
    """Send a shorter summary version"""
    
    summary = """🤖 *AI TRADING SUMMARY* - Sept 10, 2025

*🔵 DEE-BOT (Institutional):*
• AAPL: LONG $10,889 @ $178.50 📱
• MSFT: LONG $11,948 @ $412.00 🤖 
• SPY: SHORT $3,270 @ $545.00 🛡️
• JPM: LONG $14,200 @ $200.00 🏦

*🟡 Shorgan-Bot (Small/Mid-Cap):*
• PLTR: LONG $7,500 @ $14.50 🎯
• CVNA: SHORT $5,000 @ $48.00 📉
• DDOG: OPTIONS $2,400 (Earnings) 📊
• CRWD: LONG $7,500 @ $210.00 🔒
• UPST: SHORT $3,000 @ $30.00 📉
• ROKU: CALLS $1,050 @ $65 strike 📺

*📈 Risk Metrics:*
• Deployed: $70,757 (35% of capital)
• Max Risk: -$4,929 (-2.5%)
• Expected: +$1,800 (+0.9%)

*⏰ Execution: 9:30-11:00 AM EST*

Paper trading only - no real money at risk!"""
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if bot_token and chat_id:
        return send_to_telegram(bot_token, chat_id, summary)
    
    return False

def get_telegram_chat_id(bot_token):
    """
    Helper function to get your chat ID
    Send a message to your bot first, then run this
    """
    
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['result']:
            latest = data['result'][-1]
            chat_id = latest['message']['chat']['id']
            username = latest['message']['from'].get('username', 'Unknown')
            print(f"Your chat ID: {chat_id}")
            print(f"Username: @{username}")
            return chat_id
        else:
            print("No messages found. Send a message to your bot first!")
    else:
        print(f"Failed to get updates: {response.text}")
    
    return None

if __name__ == "__main__":
    import sys
    
    # Check if user wants to get chat ID
    if len(sys.argv) > 1 and sys.argv[1] == '--get-chat-id':
        bot_token = input("Enter your bot token: ")
        print("Now send any message to your bot, then press Enter...")
        input()
        get_telegram_chat_id(bot_token)
        sys.exit()
    
    # Send the trading report
    print("Sending trading report to Telegram...")
    
    # Try to send both summary and full report
    if send_summary_to_telegram():
        print("✅ Summary sent successfully!")
    
    if send_trading_report():
        print("✅ Full report sent successfully!")
    else:
        print("❌ Failed to send report. Check your credentials.")
        print("\nTo set up Telegram:")
        print("1. Message @BotFather on Telegram")
        print("2. Send /newbot and create a bot")
        print("3. Copy the bot token")
        print("4. Run: python send_to_telegram.py --get-chat-id")
        print("5. Set environment variables and run again")