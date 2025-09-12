"""
ChatGPT Report Webhook Receiver
Receives reports via webhook and processes them
"""

import os
import json
from flask import Flask, request, jsonify
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Telegram settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-4524457329')

@app.route('/webhook/chatgpt-report', methods=['POST'])
def receive_chatgpt_report():
    """Receive report from ChatGPT via webhook"""
    try:
        data = request.json
        
        # Save report
        date_str = datetime.now().strftime('%Y-%m-%d')
        report_path = f'02_data/research/reports/pre_market_daily/{date_str}_chatgpt_report.json'
        
        with open(report_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Send to Telegram
        send_telegram_notification(data)
        
        # Trigger pipeline
        trigger_trading_pipeline(data)
        
        return jsonify({'status': 'success', 'message': 'Report received and processed'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def send_telegram_notification(report):
    """Send report summary to Telegram"""
    message = f"""📊 ChatGPT Pre-Market Report Received
    
Date: {report.get('date', 'N/A')}
Trades: {len(report.get('trades', []))}

Top Picks:"""
    
    for trade in report.get('trades', [])[:3]:
        message += f"\n• {trade['symbol']}: {trade['action'].upper()} @ ${trade.get('entry_min', 0):.2f}"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    requests.post(url, data=payload)

def trigger_trading_pipeline(report):
    """Trigger the automated trading pipeline"""
    # This would trigger your daily pipeline
    os.system('python 01_trading_system/automation/daily_pre_market_pipeline.py')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)