#!/usr/bin/env python3
"""
Send notification after trade execution
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = '8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c'
TELEGRAM_CHAT_ID = '7870288896'

def send_telegram_message(message):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("[SUCCESS] Telegram notification sent")
        else:
            print(f"[ERROR] Telegram failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Telegram notification failed: {e}")

def find_latest_execution_log():
    """Find the most recent execution log"""
    log_dir = Path("scripts-and-data/trade-logs")
    if not log_dir.exists():
        return None

    log_files = list(log_dir.glob("daily_execution_*.json"))
    if not log_files:
        return None

    # Get most recent file
    latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
    return latest_log

def format_notification_message():
    """Create notification message"""
    log_file = find_latest_execution_log()

    if not log_file:
        return "🚨 <b>Trade Execution Alert</b>\n\nNo execution log found - check system status"

    try:
        with open(log_file, 'r') as f:
            log_data = json.load(f)

        executed_trades = log_data.get('executed_trades', [])
        failed_trades = log_data.get('failed_trades', [])
        execution_time = log_data.get('execution_time', 'Unknown')

        # Parse execution time
        try:
            exec_dt = datetime.fromisoformat(execution_time)
            time_str = exec_dt.strftime('%H:%M:%S')
        except:
            time_str = execution_time

        # Create message
        if executed_trades and not failed_trades:
            status_emoji = "✅"
            status_text = "SUCCESS"
        elif executed_trades and failed_trades:
            status_emoji = "⚠️"
            status_text = "PARTIAL"
        elif failed_trades:
            status_emoji = "🚨"
            status_text = "FAILED"
        else:
            status_emoji = "ℹ️"
            status_text = "NO TRADES"

        message = f"{status_emoji} <b>Morning Trade Execution</b>\n\n"
        message += f"<b>Time:</b> {time_str}\n"
        message += f"<b>Status:</b> {status_text}\n"
        message += f"<b>Executed:</b> {len(executed_trades)} trades\n"

        if failed_trades:
            message += f"<b>Failed:</b> {len(failed_trades)} trades\n"

        if executed_trades:
            message += "\n<b>📊 Executed Trades:</b>\n"
            dee_trades = [t for t in executed_trades if 'PK6FZK4DA' in str(t.get('order_id', ''))]
            shorgan_trades = [t for t in executed_trades if 'PKJRLSB2M' in str(t.get('order_id', ''))]

            if dee_trades:
                message += "\n<i>DEE-BOT:</i>\n"
                for trade in dee_trades[:3]:  # Limit to 3 trades
                    price_str = f" @ ${trade.get('limit_price', 'MKT')}" if trade.get('limit_price') else ""
                    message += f"  {trade['side'].upper()} {trade['shares']} {trade['symbol']}{price_str}\n"

            if shorgan_trades:
                message += "\n<i>SHORGAN-BOT:</i>\n"
                for trade in shorgan_trades[:3]:  # Limit to 3 trades
                    price_str = f" @ ${trade.get('limit_price', 'MKT')}" if trade.get('limit_price') else ""
                    message += f"  {trade['side'].upper()} {trade['shares']} {trade['symbol']}{price_str}\n"

        if failed_trades:
            message += "\n<b>❌ Failed Trades:</b>\n"
            for trade in failed_trades[:2]:  # Limit to 2 failed trades
                message += f"  {trade['side'].upper()} {trade['shares']} {trade['symbol']} - {trade.get('error', 'Unknown error')[:50]}\n"

        message += f"\n<i>Log: {log_file.name}</i>"

        return message

    except Exception as e:
        return f"🚨 <b>Trade Execution Alert</b>\n\nError reading execution log: {e}"

def main():
    print("Preparing execution notification...")

    message = format_notification_message()
    # Remove Unicode characters for console output
    preview = message.encode('ascii', 'replace').decode('ascii')
    print(f"Message preview:\n{preview}\n")

    send_telegram_message(message)

if __name__ == "__main__":
    main()