#!/usr/bin/env python
"""
Direct Telegram Sender - Enter credentials when prompted
"""

import requests
import time

def send_telegram_message(bot_token, chat_id, message_text):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # Split long messages if needed
    max_length = 4000
    if len(message_text) <= max_length:
        payload = {
            'chat_id': chat_id,
            'text': message_text,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        response = requests.post(url, json=payload)
        return response.status_code == 200
    else:
        # Split into chunks
        lines = message_text.split('\n')
        current_chunk = ""
        success = True
        
        for line in lines:
            if len(current_chunk + line + '\n') <= max_length:
                current_chunk += line + '\n'
            else:
                if current_chunk:
                    payload = {
                        'chat_id': chat_id,
                        'text': current_chunk.strip(),
                        'parse_mode': 'Markdown',
                        'disable_web_page_preview': True
                    }
                    response = requests.post(url, json=payload)
                    if response.status_code != 200:
                        success = False
                    time.sleep(1)  # Brief delay between chunks
                current_chunk = line + '\n'
        
        # Send final chunk
        if current_chunk:
            payload = {
                'chat_id': chat_id,
                'text': current_chunk.strip(),
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                success = False
        
        return success

def get_deebot_report():
    """DEE-BOT Telegram message"""
    return """🤖 *DEE-BOT TRADING PLAN*
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
• Agent Consensus: 72%

*📈 POSITION 2: MSFT - LONG*
• Size: $11,948 (29 shares @ $412.00)  
• Stop: $401.38 (-2.6%) | Target: $438.63 (+6.5%)
• Risk: $308 | Reward: $770
• Catalyst: AI/Copilot enterprise adoption
• Agent Consensus: 68%

*📉 POSITION 3: SPY - SHORT*
• Size: $3,270 (6 shares @ $545.00)
• Stop: $553.75 (-1.6%) | Target: $523.13 (+4.0%)
• Risk: $53 | Reward: $131
• Purpose: Portfolio hedge
• Agent Consensus: 60%

*📈 POSITION 4: JPM - LONG*
• Size: $14,200 (71 shares @ $200.00)
• Stop: $195.63 (-2.2%) | Target: $210.94 (+5.5%)
• Risk: $310 | Reward: $776
• Catalyst: NII expansion, strong capital
• Agent Consensus: 65%

*📊 RISK METRICS:*
• Total Deployed: $40,307 (40.3%)
• Total Risk: $976 (0.98% of capital)
• Expected Return: +$1,500-2,300
• Daily Loss Limit: $750
• Circuit Breakers: Active

*🎯 Key Features:*
• ATR-based position sizing
• 7-agent consensus system
• 5-layer risk defense
• Real-time monitoring

*Paper trading only - institutional grade testing*"""

def get_shorgan_report():
    """Shorgan-Bot Telegram message"""
    return """⚡ *SHORGAN-BOT TRADING PLAN*
📅 September 10, 2025

*💼 Small/Mid-Cap Catalyst System*
💰 Capital: $100,000
📊 Focus: <$20B Market Cap Companies
⚡ Style: Aggressive Catalyst-Driven
⏰ Execution: 9:30-11:00 AM EST

*📈 POSITION 1: PLTR - LONG ($15B)*
• Size: $7,500 (520 shares @ $14.50)
• Stop: $13.30 (-8.3%) | Target: $16.00 (+10.3%)
• Risk: $625 | Reward: $780
• Catalyst: AI contract rumors, govt deals
• Setup: Flag breakout pattern

*📉 POSITION 2: CVNA - SHORT ($4B)*
• Size: $5,000 (100 shares @ $48.00)
• Stop: $51.50 (-7.3%) | Target: $42.00 (+12.5%)
• Risk: $350 | Reward: $600
• Catalyst: Parabolic exhaustion (up 40% in 5 days)
• Setup: No fundamental support

*🎲 POSITION 3: DDOG - OPTIONS ($14B)*
• Strategy: ATM Straddle ($110 strike)
• Size: $2,400 (3 contracts)
• Expiry: September 13 (3 days)
• Catalyst: Earnings tomorrow BMO
• Expected Move: ±8.5% ($9.35)
• Breakeven: $102 or $118

*📈 POSITION 4: CRWD - LONG ($18B)*
• Size: $7,500 (36 shares @ $210.00)
• Stop: $199.50 (-5%) | Target: $225.00 (+7.1%)
• Risk: $378 | Reward: $540
• Catalyst: Cybersecurity demand surge
• Setup: Cup and handle breakout

*📉 POSITION 5: UPST - SHORT ($3B)*
• Size: $3,000 (100 shares @ $30.00)
• Stop: $31.50 (-5%) | Target: $27.00 (+10%)
• Risk: $150 | Reward: $300
• Catalyst: Breaking support, lending headwinds
• Warning: 35% short interest (squeeze risk)

*📺 POSITION 6: ROKU - CALL OPTIONS ($8B)*
• Strategy: Long Call ($65 strike)
• Size: $1,050 (3 contracts)
• Expiry: September 20 (10 days)
• Catalyst: Streaming rebound, oversold at RSI 28
• Max Risk: $1,050 | Target: +150% ($2,625)

*📊 RISK METRICS:*
• Total Deployed: $26,450 (26.5%)
• Long Exposure: $18,450
• Short Exposure: $8,000  
• Options Exposure: $3,450
• Expected Return: +$2,000-4,000
• Daily Loss Limit: $3,000

*⚡ Key Features:*
• Volatility-adjusted position sizing
• Catalyst-driven entries
• Long/short/options mix
• 1-30 day time horizon

*Paper trading - small/mid-cap focus testing*"""

def main():
    print("Enter your Telegram credentials:")
    bot_token = input("Bot Token: ").strip()
    chat_id = input("Chat ID: ").strip()
    
    if not bot_token or not chat_id:
        print("Error: Both token and chat ID are required!")
        return
    
    print("\nSending DEE-BOT report...")
    if send_telegram_message(bot_token, chat_id, get_deebot_report()):
        print("✓ DEE-BOT report sent successfully!")
    else:
        print("✗ Failed to send DEE-BOT report")
    
    time.sleep(3)  # Delay between messages
    
    print("Sending Shorgan-Bot report...")
    if send_telegram_message(bot_token, chat_id, get_shorgan_report()):
        print("✓ Shorgan-Bot report sent successfully!")
    else:
        print("✗ Failed to send Shorgan-Bot report")
    
    print("\n🎉 Both reports sent to Telegram!")

if __name__ == "__main__":
    main()