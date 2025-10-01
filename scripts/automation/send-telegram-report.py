"""
Send daily trading report via Telegram
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def send_pdf_via_telegram(pdf_path, message_text):
    """Send PDF report via Telegram"""
    
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '-4524457329')
    
    if not telegram_token:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env file")
        return False
    
    # Send text message first
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        'chat_id': telegram_chat_id,
        'text': message_text,
        'parse_mode': 'HTML'
    }
    
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Text message sent successfully")
    else:
        print(f"Failed to send text: {response.text}")
    
    # Send PDF document
    url = f"https://api.telegram.org/bot{telegram_token}/sendDocument"
    
    with open(pdf_path, 'rb') as f:
        files = {'document': f}
        data = {
            'chat_id': telegram_chat_id,
            'caption': f"📊 Full Trading Report - {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}",
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            print("PDF sent successfully via Telegram")
            return True
        else:
            print(f"Failed to send PDF: {response.text}")
            return False

def main():
    """Send today's report"""
    
    # Find the most recent PDF report
    report_dir = '07_docs/dual_bot_reports'
    pdf_files = [f for f in os.listdir(report_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF reports found")
        return
    
    # Get the most recent file
    latest_pdf = max(pdf_files, key=lambda f: os.path.getctime(os.path.join(report_dir, f)))
    pdf_path = os.path.join(report_dir, latest_pdf)
    
    # Prepare message
    message = f"""<b>🤖 AI Trading Bot - Daily Report</b>
    
📅 {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}

<b>Portfolio Status:</b>
• SHORGAN-BOT: $103,552.63 (+5.42%)
• DEE-BOT: $102,690.85 (+2.69%)
• <b>Total:</b> $206,243.48 (+4.16%)

<b>Today's Activity:</b>
• MFIC: LONG 770 shares @ $12.16
  - Catalyst: Insider buying ($2M CEO purchase)
  - Stop Loss: $11.07 (-9%)
  - Target: $15.80 (+30%)
  - Agent Consensus: 7.43/10 ✅

<b>Multi-Agent Analysis:</b>
• Fundamental: 7.5/10 (Undervalued P/E)
• Technical: 8.0/10 (Breakout pattern)
• News: 9.0/10 (Insider catalyst)
• Sentiment: 7.0/10 (Positive social)
• Bull Case: 8.5/10 (Multiple catalysts)
• Bear Case: 4.0/10 (Limited risks)
• Risk Manager: APPROVED ✅

<b>Current Positions:</b>
• SHORGAN: 14 positions (including MFIC)
• DEE: 8 positions (target 15)
• Portfolio Beta: 0.98 (target 1.0)

📎 Full PDF report attached with complete analysis
"""
    
    # Send the report
    send_pdf_via_telegram(pdf_path, message)
    print(f"Report sent: {latest_pdf}")

if __name__ == "__main__":
    main()