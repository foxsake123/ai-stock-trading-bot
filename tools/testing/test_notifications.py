#!/usr/bin/env python
"""
Test Notification System
Quick test to verify Slack/Telegram integration works
"""

import os
from send_bot_reports import send_deebot_report, send_shorgan_report, send_both_reports

def test_credentials():
    """Test if credentials are configured"""
    print("🔍 Checking notification credentials...")
    
    has_slack = bool(os.getenv('SLACK_WEBHOOK_URL'))
    has_telegram = bool(os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'))
    
    print(f"📱 Slack configured: {'✅' if has_slack else '❌'}")
    print(f"📱 Telegram configured: {'✅' if has_telegram else '❌'}")
    
    if not has_slack and not has_telegram:
        print("\n❌ No notification services configured!")
        print("Please set environment variables:")
        print("  - Slack: SLACK_WEBHOOK_URL")  
        print("  - Telegram: TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID")
        return False
    
    return True

def test_send_reports():
    """Test sending reports"""
    if not test_credentials():
        return
    
    print("\n🚀 Testing notification system...")
    
    # Test DEE-BOT report
    print("\n📊 Testing DEE-BOT report...")
    send_deebot_report()
    
    # Brief delay
    import time
    time.sleep(3)
    
    # Test Shorgan-Bot report  
    print("\n⚡ Testing Shorgan-Bot report...")
    send_shorgan_report()
    
    print("\n✅ Test completed!")
    print("Check your Slack/Telegram for the trading reports.")

if __name__ == "__main__":
    test_send_reports()