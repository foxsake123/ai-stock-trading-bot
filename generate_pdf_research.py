"""
Generate PDF version of ChatGPT Weekly Research Report
Creates professional PDF with all trade recommendations
"""

import os
from pathlib import Path
from datetime import datetime
import markdown2
from weasyprint import HTML, CSS
import pdfkit

def create_pdf_from_markdown():
    """Convert the ChatGPT research markdown to PDF"""

    # Read the ChatGPT research
    research_path = Path("scripts-and-data/data/reports/weekly/chatgpt-research/CHATGPT_ACTUAL_2025-09-30.md")

    with open(research_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Convert markdown to HTML with tables support
    html_content = markdown2.markdown(
        markdown_content,
        extras=['tables', 'fenced-code-blocks', 'header-ids']
    )

    # Create professional HTML template
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Weekly Trading Research - ChatGPT Analysis</title>
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}

            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                page-break-after: avoid;
            }}

            h2 {{
                color: #34495e;
                margin-top: 30px;
                border-bottom: 1px solid #ecf0f1;
                padding-bottom: 5px;
                page-break-after: avoid;
            }}

            h3 {{
                color: #7f8c8d;
                margin-top: 20px;
            }}

            ul, ol {{
                margin-left: 20px;
            }}

            li {{
                margin-bottom: 5px;
            }}

            strong {{
                color: #2c3e50;
                font-weight: 600;
            }}

            code {{
                background-color: #f4f4f4;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }}

            blockquote {{
                border-left: 4px solid #3498db;
                margin-left: 0;
                padding-left: 20px;
                color: #7f8c8d;
            }}

            .trade-section {{
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
                page-break-inside: avoid;
            }}

            .alert-box {{
                background-color: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
            }}

            .risk-box {{
                background-color: #f8d7da;
                border: 1px solid #dc3545;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
            }}

            hr {{
                border: none;
                border-top: 2px solid #ecf0f1;
                margin: 30px 0;
            }}

            a {{
                color: #3498db;
                text-decoration: none;
            }}

            a:hover {{
                text-decoration: underline;
            }}

            .footer {{
                margin-top: 50px;
                padding-top: 20px;
                border-top: 2px solid #ecf0f1;
                color: #7f8c8d;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>ChatGPT Weekly Trading Research</h1>
            <p><strong>Week of September 30 - October 4, 2025</strong></p>
            <p>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}</p>
        </div>

        <div class="alert-box">
            <strong>⚠️ TUESDAY EXECUTION NOTES:</strong>
            <ul>
                <li>FBIO FDA decision was Monday (check outcome)</li>
                <li>Government shutdown vote happened Monday</li>
                <li>BBAI earnings Wednesday after close</li>
                <li>All trades below are for Tuesday execution</li>
            </ul>
        </div>

        {html_content}

        <div class="footer">
            <p>This report is generated from ChatGPT TradingAgents deep research analysis.</p>
            <p>All trades should be executed with proper risk management and position sizing.</p>
            <p>Document generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """

    # Save HTML version
    html_path = Path("scripts-and-data/data/reports/weekly/chatgpt-research/weekly_research_tuesday.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"HTML saved: {html_path}")

    # Try to create PDF using different methods
    pdf_path = Path("scripts-and-data/data/reports/weekly/chatgpt-research/weekly_research_tuesday.pdf")

    # Method 1: Try weasyprint
    try:
        from weasyprint import HTML
        HTML(string=html_template).write_pdf(str(pdf_path))
        print(f"PDF created with weasyprint: {pdf_path}")
        return pdf_path
    except ImportError:
        print("Weasyprint not available")
    except Exception as e:
        print(f"Weasyprint error: {e}")

    # Method 2: Try pdfkit (requires wkhtmltopdf)
    try:
        import pdfkit
        pdfkit.from_string(html_template, str(pdf_path))
        print(f"PDF created with pdfkit: {pdf_path}")
        return pdf_path
    except ImportError:
        print("pdfkit not available")
    except Exception as e:
        print(f"pdfkit error: {e}")

    # Method 3: Save as HTML for manual printing
    print(f"\nHTML version ready at: {html_path}")
    print("To create PDF: Open in browser and print to PDF")

    return html_path

def send_pdf_telegram(file_path):
    """Send PDF via Telegram"""
    import requests

    telegram_token = "8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c"
    chat_id = "7870288896"

    url = f"https://api.telegram.org/bot{telegram_token}/sendDocument"

    # Send summary message first
    message_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    summary = """📊 TUESDAY TRADING PLAN (Oct 1, 2025)

⚠️ CRITICAL UPDATES:
• FBIO FDA decision was MONDAY (check outcome)
• Government shutdown vote COMPLETED
• BBAI earnings WEDNESDAY after close

📈 DEE-BOT TRADES:
• EXIT: NVDA, AMZN, CVX
• ENTER: IBM (quantum + dividend)
• Target Beta: 1.0

🚀 SHORGAN-BOT TRADES:
• COVER: All short positions
• EXIT: ORCL, GPK, TSLA
• HOLD: RGTI (+117%), SAVA (+50%)

Full research report attached."""

    requests.post(message_url, data={
        'chat_id': chat_id,
        'text': summary,
        'parse_mode': 'HTML'
    })

    # Send the document
    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {
            'chat_id': chat_id,
            'caption': 'ChatGPT Weekly Research - Tuesday Execution Plan'
        }

        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            print("Research report sent to Telegram")
            return True
        else:
            print(f"Failed to send: {response.text}")
            return False

if __name__ == "__main__":
    print("="*60)
    print("GENERATING PDF RESEARCH REPORT FOR TUESDAY")
    print("="*60)

    # Create PDF
    file_path = create_pdf_from_markdown()

    # Send via Telegram
    if file_path.exists():
        send_pdf_telegram(file_path)

    print("\n" + "="*60)
    print("TUESDAY EXECUTION SUMMARY")
    print("="*60)
    print("\n9:30 AM Actions:")
    print("1. Check FBIO FDA outcome from Monday")
    print("2. Cover all SHORGAN short positions")
    print("3. Execute DEE-BOT exits (NVDA, AMZN, CVX)")
    print("4. Execute SHORGAN exits (ORCL, GPK, TSLA)")
    print("\n10:00 AM Actions:")
    print("5. Enter IBM position for DEE-BOT")
    print("6. Update all stop losses")
    print("7. Monitor BBAI for Wednesday earnings")
    print("\nResearch report sent to Telegram!")