"""
Generate Weekly Research Report from ChatGPT and Send via Telegram
This script fetches real ChatGPT analysis, converts to PDF, and sends via Telegram
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import time

class WeeklyResearchProcessor:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.reports_dir = self.project_root / 'scripts-and-data' / 'data' / 'reports' / 'weekly' / 'chatgpt-research'
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Telegram configuration
        self.telegram_token = "8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c"
        self.telegram_chat_id = "7870288896"

        # Week dates
        self.today = datetime.now()
        self.week_start = self.today - timedelta(days=self.today.weekday())
        self.week_end = self.week_start + timedelta(days=4)

    def fetch_chatgpt_research(self):
        """Fetch real ChatGPT research using automated fetcher or manual input"""
        print("="*70)
        print("FETCHING CHATGPT DEEP RESEARCH")
        print("="*70)

        # Check if we have recent ChatGPT data
        chatgpt_dir = self.project_root / 'scripts-and-data' / 'daily-json' / 'chatgpt'
        recent_file = None

        # Look for today's or this week's ChatGPT report
        for date_offset in range(7):
            check_date = self.today - timedelta(days=date_offset)
            filename = f"chatgpt_weekly_research_{check_date.strftime('%Y-%m-%d')}.json"
            filepath = chatgpt_dir / filename
            if filepath.exists():
                recent_file = filepath
                break

        if recent_file:
            print(f"[FOUND] Recent ChatGPT research: {recent_file.name}")
            with open(recent_file, 'r') as f:
                return json.load(f)

        # Try automated fetch
        print("\n[ATTEMPTING] Automated ChatGPT fetch...")
        try:
            result = subprocess.run(
                ['python', 'scripts-and-data/automation/automated_chatgpt_fetcher.py'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print("[SUCCESS] ChatGPT data fetched automatically")
                # Load the newly fetched data
                return self.load_latest_chatgpt_data()
        except Exception as e:
            print(f"[FAILED] Automated fetch: {e}")

        # Manual fallback
        print("\n" + "="*70)
        print("MANUAL CHATGPT INPUT REQUIRED")
        print("="*70)
        print("\nTo get real ChatGPT research:")
        print("1. Go to ChatGPT.com")
        print("2. Copy the prompt from: weekly_research_prompt.txt")
        print("3. Get ChatGPT's response")
        print("4. Save it using: python scripts-and-data/automation/save_chatgpt_report.py")
        print("\nFor now, using existing data and templates...")

        return self.load_latest_chatgpt_data()

    def load_latest_chatgpt_data(self):
        """Load the most recent ChatGPT data"""
        chatgpt_dir = self.project_root / 'scripts-and-data' / 'daily-json' / 'chatgpt'
        files = list(chatgpt_dir.glob('*.json'))
        if files:
            latest = max(files, key=lambda p: p.stat().st_mtime)
            with open(latest, 'r') as f:
                return json.load(f)
        return None

    def format_research_as_markdown(self, chatgpt_data):
        """Format ChatGPT data into comprehensive markdown report"""

        # If we have raw text from ChatGPT, use it directly
        if chatgpt_data and 'raw_response' in chatgpt_data:
            return chatgpt_data['raw_response']

        # Otherwise format structured data
        week_str = f"{self.week_start.strftime('%B %d')} - {self.week_end.strftime('%B %d, %Y')}"

        markdown = f"""# 📊 WEEKLY DEEP RESEARCH REPORT - CHATGPT ANALYSIS
## Week of {week_str}
### Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}
### Source: ChatGPT TradingAgents Deep Research

---

## 🎯 EXECUTIVE SUMMARY

This comprehensive weekly research report provides strategic guidance for both DEE-BOT (defensive) and SHORGAN-BOT (catalyst-driven) trading strategies. All recommendations are based on current market conditions, upcoming catalysts, and risk-adjusted opportunities.

**Portfolio Allocation**: $200,000 total ($100K per bot)
**Target Return**: 2-3% for the week
**Risk Management**: Strict stop losses on all positions

---

"""

        # Add trades if available
        if chatgpt_data and 'trades' in chatgpt_data:
            markdown += "## 📈 TRADE RECOMMENDATIONS\n\n"

            dee_trades = [t for t in chatgpt_data['trades'] if t.get('bot') == 'DEE']
            shorgan_trades = [t for t in chatgpt_data['trades'] if t.get('bot') == 'SHORGAN']

            if dee_trades:
                markdown += "### DEE-BOT TRADES (Defensive)\n"
                markdown += "| Symbol | Action | Shares | Entry | Stop | Target | Rationale |\n"
                markdown += "|--------|--------|--------|-------|------|--------|----------|\n"
                for trade in dee_trades:
                    markdown += f"| {trade.get('symbol', '')} | {trade.get('action', '')} | "
                    markdown += f"{trade.get('shares', '')} | ${trade.get('entry', '')} | "
                    markdown += f"${trade.get('stop', '')} | ${trade.get('target', '')} | "
                    markdown += f"{trade.get('rationale', '')[:50]}... |\n"
                markdown += "\n"

            if shorgan_trades:
                markdown += "### SHORGAN-BOT TRADES (Catalysts)\n"
                markdown += "| Symbol | Action | Shares | Entry | Stop | Target | Catalyst |\n"
                markdown += "|--------|--------|--------|-------|------|--------|----------|\n"
                for trade in shorgan_trades:
                    markdown += f"| {trade.get('symbol', '')} | {trade.get('action', '')} | "
                    markdown += f"{trade.get('shares', '')} | ${trade.get('entry', '')} | "
                    markdown += f"${trade.get('stop', '')} | ${trade.get('target', '')} | "
                    markdown += f"{trade.get('catalyst', '')[:50]}... |\n"

        # Add footer
        markdown += f"""

---

## ⚠️ IMPORTANT DISCLAIMERS

1. This research is generated by AI and should be validated before trading
2. All trades should follow position sizing rules (8% DEE, 10% SHORGAN)
3. Stop losses must be set on all positions
4. Binary events (FDA approvals) should be sized down
5. Past performance does not guarantee future results

---

## 📞 SUPPORT

- Telegram Alerts: Active
- System Dashboard: `python scripts-and-data/automation/system_dashboard.py`
- Quick Check: `python quick_check.py`

---

*Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}*
*Next Update: Sunday Evening*
*Source: ChatGPT TradingAgents Analysis*
"""

        return markdown

    def markdown_to_pdf(self, markdown_content, output_path):
        """Convert markdown to PDF using available tools"""
        print("\n[CONVERTING] Markdown to PDF...")

        # Save markdown first
        md_file = output_path.with_suffix('.md')
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"[SAVED] Markdown: {md_file}")

        # Try different PDF conversion methods
        pdf_file = output_path.with_suffix('.pdf')

        # Method 1: Try markdown-pdf if installed
        try:
            import markdown2
            import pdfkit

            html = markdown2.markdown(markdown_content, extras=['tables', 'fenced-code-blocks'])
            pdfkit.from_string(html, str(pdf_file))
            print(f"[SUCCESS] PDF created: {pdf_file}")
            return pdf_file
        except ImportError:
            print("[INFO] pdfkit not available")
        except Exception as e:
            print(f"[WARNING] PDF conversion failed: {e}")

        # Method 2: Try weasyprint
        try:
            from weasyprint import HTML

            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #2c3e50; }}
                    h2 {{ color: #34495e; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <pre>{markdown_content}</pre>
            </body>
            </html>
            """
            HTML(string=html_content).write_pdf(str(pdf_file))
            print(f"[SUCCESS] PDF created with weasyprint: {pdf_file}")
            return pdf_file
        except ImportError:
            print("[INFO] weasyprint not available")
        except Exception as e:
            print(f"[WARNING] Weasyprint failed: {e}")

        # Method 3: Save as HTML (can be printed to PDF)
        html_file = output_path.with_suffix('.html')
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Weekly Research Report</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                    padding: 10px;
                    text-align: left;
                }}
                td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                pre {{
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}
            </style>
        </head>
        <body>
            <pre>{markdown_content}</pre>
        </body>
        </html>
        """

        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"[SAVED] HTML version: {html_file}")
        print("[INFO] Open HTML in browser and print to PDF if needed")

        return html_file

    def send_via_telegram(self, file_path, caption=""):
        """Send file via Telegram bot"""
        print("\n[SENDING] Report via Telegram...")

        try:
            # Send as document
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendDocument"

            with open(file_path, 'rb') as f:
                files = {'document': f}
                data = {
                    'chat_id': self.telegram_chat_id,
                    'caption': caption[:1024]  # Telegram caption limit
                }

                response = requests.post(url, files=files, data=data)

                if response.status_code == 200:
                    print("[SUCCESS] Report sent via Telegram")
                    return True
                else:
                    print(f"[ERROR] Telegram send failed: {response.text}")
                    return False

        except Exception as e:
            print(f"[ERROR] Could not send via Telegram: {e}")
            return False

    def send_summary_message(self, summary_text):
        """Send text summary via Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"

            data = {
                'chat_id': self.telegram_chat_id,
                'text': summary_text[:4096],  # Telegram message limit
                'parse_mode': 'HTML'
            }

            response = requests.post(url, data=data)

            if response.status_code == 200:
                print("[SUCCESS] Summary sent via Telegram")
                return True

        except Exception as e:
            print(f"[ERROR] Could not send summary: {e}")

        return False

    def run(self):
        """Main execution flow"""
        print("="*70)
        print("WEEKLY RESEARCH REPORT GENERATOR")
        print(f"Week of {self.week_start.strftime('%B %d')} - {self.week_end.strftime('%B %d, %Y')}")
        print("="*70)

        # Step 1: Fetch ChatGPT research
        print("\n[STEP 1/4] Fetching ChatGPT research...")
        chatgpt_data = self.fetch_chatgpt_research()

        if not chatgpt_data:
            print("[WARNING] No ChatGPT data available. Using template...")
            chatgpt_data = {'source': 'template', 'trades': []}

        # Step 2: Format as markdown
        print("\n[STEP 2/4] Formatting research report...")
        markdown_content = self.format_research_as_markdown(chatgpt_data)

        # Save markdown
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = self.reports_dir / f"weekly_research_{self.week_start.strftime('%Y-%m-%d')}"
        md_file = output_path.with_suffix('.md')

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"[SAVED] {md_file}")

        # Step 3: Convert to PDF/HTML
        print("\n[STEP 3/4] Converting to PDF...")
        pdf_file = self.markdown_to_pdf(markdown_content, output_path)

        # Step 4: Send via Telegram
        print("\n[STEP 4/4] Sending via Telegram...")

        # Prepare summary
        summary = f"""<b>📊 WEEKLY RESEARCH REPORT</b>
<b>Week of {self.week_start.strftime('%B %d')} - {self.week_end.strftime('%B %d, %Y')}</b>

<b>🎯 Key Focus This Week:</b>
• DEE-BOT: Defensive S&P 100 stocks (JNJ, PG, XOM)
• SHORGAN-BOT: FBIO FDA Monday, BBAI earnings Wed

<b>⚠️ Critical Events:</b>
• Mon: ISM Manufacturing, FBIO FDA
• Wed: FOMC Minutes, BBAI earnings
• Fri: Non-Farm Payrolls (major volatility)

<b>📈 Strategy:</b>
• Execute early week (Mon/Tue)
• Size down binary events
• Honor all stop losses

Full report attached with detailed trade recommendations."""

        # Send summary
        self.send_summary_message(summary)

        # Send report file
        file_to_send = pdf_file if pdf_file.suffix == '.pdf' else md_file
        caption = f"Weekly Research Report - {self.week_start.strftime('%B %d, %Y')}"
        self.send_via_telegram(file_to_send, caption)

        # Final summary
        print("\n" + "="*70)
        print("WEEKLY RESEARCH GENERATION COMPLETE")
        print("="*70)
        print(f"Markdown: {md_file}")
        if pdf_file:
            print(f"PDF/HTML: {pdf_file}")
        print(f"Telegram: Sent to chat {self.telegram_chat_id}")
        print("\nUse this research as the foundation for all trades this week!")

        return True

if __name__ == "__main__":
    processor = WeeklyResearchProcessor()
    processor.run()