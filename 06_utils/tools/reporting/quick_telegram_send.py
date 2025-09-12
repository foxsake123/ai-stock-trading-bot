#!/usr/bin/env python
"""
Quick Telegram Sender - Edit the credentials below and run
"""

import requests
import time

# EDIT THESE LINES WITH YOUR CREDENTIALS
BOT_TOKEN = "8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c"  # Your bot token
CHAT_ID = "7870288896"      # Your chat ID

def send_telegram_message(bot_token, chat_id, message_text):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message_text,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    response = requests.post(url, json=payload)
    return response.status_code == 200

# DEE-BOT Report
deebot_report = """🤖 *DEE-BOT TRADING PLAN*
📅 September 10, 2025

*💼 Multi-Agent Institutional System*
💰 Capital: $100,000
📊 Strategy: Conservative Consensus
⏰ Execution: 9:30-10:30 AM EST

*📈 POSITION 1: AAPL - LONG*
• Size: $10,889 (61 shares @ $178.50)
• Stop: $173.50 (-2.8%) | Target: $188.50 (+5.6%)
• Risk: $305 | Reward: $610
• Catalyst: iPhone 16 launch momentum

*📈 POSITION 2: MSFT - LONG*
• Size: $11,948 (29 shares @ $412.00)  
• Stop: $401.38 (-2.6%) | Target: $438.63 (+6.5%)
• Risk: $308 | Reward: $770
• Catalyst: AI/Copilot enterprise adoption

*📉 POSITION 3: SPY - SHORT*
• Size: $3,270 (6 shares @ $545.00)
• Stop: $553.75 (-1.6%) | Target: $523.13 (+4.0%)
• Risk: $53 | Reward: $131
• Purpose: Portfolio hedge

*📈 POSITION 4: JPM - LONG*
• Size: $14,200 (71 shares @ $200.00)
• Stop: $195.63 (-2.2%) | Target: $210.94 (+5.5%)
• Risk: $310 | Reward: $776
• Catalyst: NII expansion, strong capital

*📊 RISK METRICS:*
• Total Deployed: $40,307 (40.3%)
• Total Risk: $976 (0.98% of capital)
• Expected Return: +$1,500-2,300
• Daily Loss Limit: $750

*Paper trading only - institutional grade testing*"""

# Shorgan-Bot Report  
shorgan_report = """⚡ *SHORGAN-BOT TRADING PLAN*
📅 September 10, 2025

*💼 Small/Mid-Cap Catalyst System*
💰 Capital: $100,000
📊 Focus: <$20B Market Cap Companies
⚡ Style: Aggressive Catalyst-Driven
⏰ Execution: 9:30-11:00 AM EST

*📈 PLTR - LONG ($15B)*
• Size: $7,500 (520 shares @ $14.50)
• Stop: $13.30 (-8.3%) | Target: $16.00 (+10.3%)
• Catalyst: AI contract rumors

*📉 CVNA - SHORT ($4B)*
• Size: $5,000 (100 shares @ $48.00)
• Stop: $51.50 (-7.3%) | Target: $42.00 (+12.5%)
• Catalyst: Parabolic exhaustion

*🎲 DDOG - OPTIONS ($14B)*
• Strategy: ATM Straddle ($110 strike)
• Size: $2,400 (3 contracts)
• Catalyst: Earnings tomorrow

*📈 CRWD - LONG ($18B)*
• Size: $7,500 (36 shares @ $210.00)
• Stop: $199.50 (-5%) | Target: $225.00 (+7.1%)
• Catalyst: Cybersecurity demand

*📉 UPST - SHORT ($3B)*
• Size: $3,000 (100 shares @ $30.00)
• Stop: $31.50 (-5%) | Target: $27.00 (+10%)
• Catalyst: Breaking support

*📺 ROKU - CALLS ($8B)*
• Size: $1,050 (3 contracts, $65 strike)
• Catalyst: Streaming rebound

*📊 RISK METRICS:*
• Total Deployed: $26,450 (26.5%)
• Expected Return: +$2,000-4,000
• Daily Loss Limit: $3,000

*Paper trading - small/mid-cap focus testing*"""

def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or CHAT_ID == "YOUR_CHAT_ID_HERE":
        print("Please edit the credentials at the top of this file first!")
        print("Replace BOT_TOKEN and CHAT_ID with your actual values")
        return
    
    print("Sending DEE-BOT report...")
    if send_telegram_message(BOT_TOKEN, CHAT_ID, deebot_report):
        print("[SUCCESS] DEE-BOT report sent!")
    else:
        print("[FAILED] Failed to send DEE-BOT report")
    
    time.sleep(3)
    
    print("Sending Shorgan-Bot report...")
    if send_telegram_message(BOT_TOKEN, CHAT_ID, shorgan_report):
        print("[SUCCESS] Shorgan-Bot report sent!")
    else:
        print("[FAILED] Failed to send Shorgan-Bot report")
    
    print("Done!")

if __name__ == "__main__":
    main()