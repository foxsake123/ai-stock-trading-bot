#!/usr/bin/env python
"""
Send Trading Report to Slack
Sends the daily trading report to your Slack channel
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

def send_to_slack(webhook_url=None, channel=None, token=None):
    """
    Send trading report to Slack
    
    You can use either:
    1. Webhook URL (easier) - Get from Slack App settings
    2. Bot token + channel (more features) - Requires Slack App with bot token
    """
    
    # Read the trading report
    report_file = Path("EMAIL_TRADING_SUMMARY.txt")
    if not report_file.exists():
        print("Error: Trading report not found!")
        return False
    
    with open(report_file, 'r') as f:
        report_content = f.read()
    
    # Format for Slack (convert to code block for better formatting)
    slack_message = {
        "text": "📊 Daily Trading Report - September 10, 2025",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🤖 AI Trading Bot Report"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Trading Date:* September 10, 2025\n*Systems:* DEE-BOT & Shorgan-Bot\n*Total Capital:* $200,000"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "```" + report_content[:2900] + "```"  # Slack has 3000 char limit per block
                }
            }
        ]
    }
    
    # Method 1: Using Webhook URL (Recommended for simplicity)
    if webhook_url:
        response = requests.post(
            webhook_url,
            json=slack_message,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Report sent to Slack successfully!")
            return True
        else:
            print(f"❌ Failed to send to Slack: {response.status_code}")
            print(response.text)
            return False
    
    # Method 2: Using Bot Token (Requires more setup but more features)
    elif token and channel:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Split long message into multiple messages if needed
        messages = []
        if len(report_content) > 3000:
            # Split into chunks
            chunks = [report_content[i:i+2900] for i in range(0, len(report_content), 2900)]
            for i, chunk in enumerate(chunks):
                messages.append({
                    "channel": channel,
                    "text": f"Trading Report Part {i+1}/{len(chunks)}",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "```" + chunk + "```"
                            }
                        }
                    ]
                })
        else:
            messages = [{
                "channel": channel,
                **slack_message
            }]
        
        # Send all messages
        for msg in messages:
            response = requests.post(
                'https://slack.com/api/chat.postMessage',
                headers=headers,
                json=msg
            )
            
            if response.status_code != 200 or not response.json().get('ok'):
                print(f"❌ Failed to send to Slack: {response.text}")
                return False
        
        print("✅ Report sent to Slack successfully!")
        return True
    
    else:
        print("❌ Error: Please provide either webhook_url OR (token + channel)")
        return False

def send_summary_to_slack(webhook_url=None):
    """Send a shorter summary version to Slack"""
    
    summary = """
📊 *TRADING SUMMARY - Sept 10, 2025*

*DEE-BOT Positions:*
• AAPL: LONG $10,889 @ $178.50 (iPhone catalyst)
• MSFT: LONG $11,948 @ $412.00 (AI adoption)
• SPY: SHORT $3,270 @ $545.00 (Hedge)
• JPM: LONG $14,200 @ $200.00 (NII expansion)

*Shorgan-Bot Positions:*
• PLTR: LONG $7,500 @ $14.50 (AI contracts)
• CVNA: SHORT $5,000 @ $48.00 (Exhaustion)
• DDOG: OPTIONS $2,400 (Earnings play)
• CRWD: LONG $7,500 @ $210.00 (Cybersecurity)
• UPST: SHORT $3,000 @ $30.00 (Breakdown)
• ROKU: CALLS $1,050 @ $65 strike

*Risk Metrics:*
• Total Deployed: $70,757 (35%)
• Max Risk: -$4,929 (-2.5%)
• Expected: +$1,800 (+0.9%)

*Execution: 9:30-11:00 AM EST*
"""
    
    if webhook_url:
        message = {
            "text": summary,
            "username": "Trading Bot",
            "icon_emoji": ":chart_with_upwards_trend:"
        }
        
        response = requests.post(webhook_url, json=message)
        if response.status_code == 200:
            print("✅ Summary sent to Slack!")
            return True
    
    return False

if __name__ == "__main__":
    # CONFIGURATION - Add your Slack credentials here
    
    # Option 1: Using Webhook (Easier)
    # 1. Go to https://api.slack.com/apps
    # 2. Create app → Incoming Webhooks → Add New Webhook
    # 3. Copy webhook URL here:
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')
    
    # Option 2: Using Bot Token (More features)
    # 1. Create Slack App with bot token
    # 2. Add bot to channel
    # 3. Set token and channel:
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN', '')
    SLACK_CHANNEL = os.getenv('SLACK_CHANNEL', '#trading')  # or '@username' for DM
    
    # Try to send report
    if SLACK_WEBHOOK_URL:
        print("Sending report via webhook...")
        send_to_slack(webhook_url=SLACK_WEBHOOK_URL)
        # Also send summary
        send_summary_to_slack(webhook_url=SLACK_WEBHOOK_URL)
    elif SLACK_BOT_TOKEN and SLACK_CHANNEL:
        print("Sending report via bot token...")
        send_to_slack(token=SLACK_BOT_TOKEN, channel=SLACK_CHANNEL)
    else:
        print("""
❌ Slack credentials not configured!

Please set one of the following:

Option 1 (Webhook - Recommended):
  export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

Option 2 (Bot Token):
  export SLACK_BOT_TOKEN="xoxb-your-token-here"
  export SLACK_CHANNEL="#trading"

Then run: python send_to_slack.py
        """)