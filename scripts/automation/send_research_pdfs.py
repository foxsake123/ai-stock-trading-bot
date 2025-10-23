"""
Send Research PDFs via Telegram

Sends Claude research PDF reports via Telegram.

Usage:
    python scripts/automation/send_research_pdfs.py
    python scripts/automation/send_research_pdfs.py --date 2025-10-23
    python scripts/automation/send_research_pdfs.py --bot dee
    python scripts/automation/send_research_pdfs.py --bot shorgan
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()


def get_telegram_config():
    """Get Telegram configuration from environment"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")

    return bot_token, chat_id


def send_telegram_document(bot_token, chat_id, file_path, caption=None):
    """Send document via Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': chat_id}

            if caption:
                data['caption'] = caption
                data['parse_mode'] = 'Markdown'

            response = requests.post(url, data=data, files=files, timeout=30)
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"[ERROR] Failed to send document: {e}")
        return False


def find_research_pdfs(date, bot=None):
    """Find research PDFs for given date"""
    base_path = Path(f"reports/premarket/{date}")

    if not base_path.exists():
        print(f"[ERROR] No research directory found for {date}")
        return []

    pdfs = []

    if bot is None or bot == 'dee':
        dee_pdf = base_path / f"claude_research_dee_bot_{date}.pdf"
        if dee_pdf.exists():
            pdfs.append(('DEE-BOT', dee_pdf))

    if bot is None or bot == 'shorgan':
        shorgan_pdf = base_path / f"claude_research_shorgan_bot_{date}.pdf"
        if shorgan_pdf.exists():
            pdfs.append(('SHORGAN-BOT', shorgan_pdf))

    return pdfs


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Send research PDFs via Telegram')
    parser.add_argument('--date', type=str, help='Date for research (YYYY-MM-DD)', default=None)
    parser.add_argument('--bot', type=str, choices=['dee', 'shorgan'], help='Specific bot (dee or shorgan)', default=None)
    args = parser.parse_args()

    # Get date (tomorrow's trading date by default)
    if args.date:
        research_date = args.date
    else:
        # Default to tomorrow's date (research is for next day's trading)
        from datetime import timedelta
        tomorrow = datetime.now() + timedelta(days=1)
        research_date = tomorrow.strftime('%Y-%m-%d')

    print(f"[INFO] Sending research PDFs for {research_date}...")

    # Get Telegram config
    try:
        bot_token, chat_id = get_telegram_config()
    except ValueError as e:
        print(f"[ERROR] {e}")
        print("[INFO] Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env file")
        return 1

    # Find PDFs
    pdfs = find_research_pdfs(research_date, args.bot)

    if not pdfs:
        print(f"[ERROR] No research PDFs found for {research_date}")
        print(f"[INFO] Looking in: reports/premarket/{research_date}/")
        return 1

    print(f"[INFO] Found {len(pdfs)} PDF(s) to send")

    # Send each PDF
    success_count = 0
    for bot_name, pdf_path in pdfs:
        print(f"[INFO] Sending {bot_name} research PDF...")

        # Create caption
        caption = f"*{bot_name} Research Report*\n"
        caption += f"Trade Date: {research_date}\n"
        caption += f"Generated: {datetime.fromtimestamp(pdf_path.stat().st_mtime).strftime('%I:%M %p ET')}"

        # Send
        if send_telegram_document(bot_token, chat_id, pdf_path, caption):
            print(f"[SUCCESS] {bot_name} PDF sent!")
            success_count += 1
        else:
            print(f"[ERROR] Failed to send {bot_name} PDF")

    print(f"\n[COMPLETE] Sent {success_count}/{len(pdfs)} PDF(s)")
    return 0 if success_count == len(pdfs) else 1


if __name__ == "__main__":
    sys.exit(main())
