#!/usr/bin/env python
"""
Send Separate Bot Reports to Slack/Telegram
Allows sending DEE-BOT and Shorgan-Bot reports separately
"""

import os
import sys
import requests
import json
from datetime import datetime
import argparse

# Slack Functions
def send_slack_message(webhook_url, message_data):
    """Send message to Slack"""
    response = requests.post(
        webhook_url,
        json=message_data,
        headers={'Content-Type': 'application/json'}
    )
    return response.status_code == 200

# Telegram Functions  
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

def get_deebot_report():
    """Generate DEE-BOT specific report"""
    return {
        'title': '🤖 DEE-BOT Trading Plan',
        'subtitle': 'Multi-Agent Institutional System ($100,000)',
        'slack_message': {
            "text": "🤖 DEE-BOT Trading Plan - September 10, 2025",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🤖 DEE-BOT Trading Plan"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Multi-Agent Institutional System*\n💰 Capital: $100,000\n📊 Strategy: Conservative Consensus\n⏰ Execution: 9:30-10:30 AM EST"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Position 1: AAPL*\n📈 LONG $10,889 (61 shares)\n💵 Entry: $178.50\n🛑 Stop: $173.50\n🎯 Target: $188.50\n📱 Catalyst: iPhone 16 launch"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Position 2: MSFT*\n📈 LONG $11,948 (29 shares)\n💵 Entry: $412.00\n🛑 Stop: $401.38\n🎯 Target: $438.63\n🤖 Catalyst: AI/Copilot adoption"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Position 3: SPY*\n📉 SHORT $3,270 (6 shares)\n💵 Entry: $545.00\n🛑 Stop: $553.75\n🎯 Target: $523.13\n🛡️ Purpose: Portfolio hedge"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Position 4: JPM*\n📈 LONG $14,200 (71 shares)\n💵 Entry: $200.00\n🛑 Stop: $195.63\n🎯 Target: $210.94\n🏦 Catalyst: NII expansion"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*📊 Risk Metrics:*\n• Total Deployed: $40,307 (40.3%)\n• Total Risk: $976 (0.98%)\n• Expected Return: +$1,500-2,300\n• Agent Confidence: 66% avg\n• Daily Loss Limit: $750"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "🎯 *Strategy:* ATR-based risk mgmt | 🤝 *Consensus:* 7-agent debate | ⚖️ *Risk:* 5-layer defense"
                        }
                    ]
                }
            ]
        },
        'telegram_message': """🤖 *DEE-BOT TRADING PLAN*
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
    }

def get_shorgan_report():
    """Generate Shorgan-Bot specific report"""
    return {
        'title': '⚡ Shorgan-Bot Trading Plan', 
        'subtitle': 'Small/Mid-Cap Catalyst System ($100,000)',
        'slack_message': {
            "text": "⚡ Shorgan-Bot Trading Plan - September 10, 2025",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "⚡ Shorgan-Bot Trading Plan"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Small/Mid-Cap Catalyst System*\n💰 Capital: $100,000\n📊 Focus: <$20B Market Cap\n⚡ Style: Aggressive Catalyst-Driven\n⏰ Execution: 9:30-11:00 AM EST"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*PLTR - LONG ($15B)*\n💵 $7,500 (520 @ $14.50)\n🛑 Stop: $13.30 (-8.3%)\n🎯 Target: $16.00 (+10.3%)\n🎯 Catalyst: AI contracts"
                        },
                        {
                            "type": "mrkdwn", 
                            "text": "*CVNA - SHORT ($4B)*\n💵 $5,000 (100 @ $48.00)\n🛑 Stop: $51.50 (-7.3%)\n🎯 Target: $42.00 (+12.5%)\n📉 Catalyst: Exhaustion"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*DDOG - OPTIONS ($14B)*\n💵 $2,400 (Straddle)\n📊 Strike: $110\n📅 Exp: Sept 13\n📈 Catalyst: Earnings tomorrow"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*CRWD - LONG ($18B)*\n💵 $7,500 (36 @ $210)\n🛑 Stop: $199.50 (-5%)\n🎯 Target: $225 (+7.1%)\n🔒 Catalyst: Cybersecurity"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*UPST - SHORT ($3B)*\n💵 $3,000 (100 @ $30)\n🛑 Stop: $31.50 (-5%)\n🎯 Target: $27 (+10%)\n📉 Catalyst: Breakdown"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*ROKU - CALLS ($8B)*\n💵 $1,050 (3 calls)\n📊 Strike: $65\n📅 Exp: Sept 20\n📺 Catalyst: Bounce"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*📊 Risk Metrics:*\n• Total Deployed: $26,450 (26.5%)\n• Long: $18,450 | Short: $8,000\n• Options: $3,450 | Stocks: $23,000\n• Expected Return: +$2,000-4,000\n• Daily Loss Limit: $3,000"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "⚡ *Focus:* Small/Mid-cap catalysts | 📈 *Mix:* 60% Long, 25% Short, 15% Options | ⏱️ *Horizon:* 1-30 days"
                        }
                    ]
                }
            ]
        },
        'telegram_message': """⚡ *SHORGAN-BOT TRADING PLAN*
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
    }

def send_deebot_report():
    """Send DEE-BOT report to configured channels"""
    report = get_deebot_report()
    
    # Try Slack
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    if slack_webhook:
        if send_slack_message(slack_webhook, report['slack_message']):
            print("✅ DEE-BOT report sent to Slack!")
        else:
            print("❌ Failed to send DEE-BOT report to Slack")
    
    # Try Telegram
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
    if telegram_token and telegram_chat:
        if send_telegram_message(telegram_token, telegram_chat, report['telegram_message']):
            print("✅ DEE-BOT report sent to Telegram!")
        else:
            print("❌ Failed to send DEE-BOT report to Telegram")

def send_shorgan_report():
    """Send Shorgan-Bot report to configured channels"""
    report = get_shorgan_report()
    
    # Try Slack
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    if slack_webhook:
        if send_slack_message(slack_webhook, report['slack_message']):
            print("✅ Shorgan-Bot report sent to Slack!")
        else:
            print("❌ Failed to send Shorgan-Bot report to Slack")
    
    # Try Telegram
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
    if telegram_token and telegram_chat:
        if send_telegram_message(telegram_token, telegram_chat, report['telegram_message']):
            print("✅ Shorgan-Bot report sent to Telegram!")
        else:
            print("❌ Failed to send Shorgan-Bot report to Telegram")

def send_both_reports():
    """Send both reports with a brief delay"""
    import time
    
    print("Sending DEE-BOT report...")
    send_deebot_report()
    
    time.sleep(2)  # Brief delay between messages
    
    print("Sending Shorgan-Bot report...")
    send_shorgan_report()
    
    print("\n✅ Both reports sent!")

def main():
    """Main function with command line argument support"""
    parser = argparse.ArgumentParser(description='Send trading bot reports')
    parser.add_argument('bot', nargs='?', choices=['dee', 'shorgan', 'both'], 
                       default='both', help='Which bot report to send')
    
    args = parser.parse_args()
    
    # Check if credentials are configured
    has_slack = bool(os.getenv('SLACK_WEBHOOK_URL'))
    has_telegram = bool(os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'))
    
    if not has_slack and not has_telegram:
        print("❌ No notification services configured!")
        print("Please set up Slack or Telegram credentials:")
        print("  - Slack: SLACK_WEBHOOK_URL")
        print("  - Telegram: TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID")
        return
    
    print(f"📱 Notification channels available:")
    if has_slack:
        print("  ✅ Slack")
    if has_telegram:
        print("  ✅ Telegram")
    
    print(f"\n📊 Sending {args.bot} report(s)...")
    
    if args.bot == 'dee':
        send_deebot_report()
    elif args.bot == 'shorgan':
        send_shorgan_report()
    else:  # both
        send_both_reports()

if __name__ == "__main__":
    main()