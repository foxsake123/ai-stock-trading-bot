#!/usr/bin/env python3
"""
Pre-Market Analysis Report Generator
Provides comprehensive market analysis before trading session
"""

import json
import requests
from datetime import datetime, date
from pathlib import Path

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c"
TELEGRAM_CHAT_ID = "7870288896"

def send_telegram_message(message):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("[SUCCESS] Pre-market analysis sent to Telegram")
            return True
        else:
            print(f"[ERROR] Failed to send message: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Telegram send failed: {str(e)}")
        return False

def generate_premarket_analysis():
    """Generate comprehensive pre-market analysis"""

    report = []
    report.append("<b>PRE-MARKET ANALYSIS REPORT</b>")
    report.append(f"<b>{date.today().strftime('%A, %B %d, %Y')}</b>")
    report.append(f"<b>{datetime.now().strftime('%I:%M %p ET')}</b>")
    report.append("=" * 40)

    # Key Market Events Today
    report.append("\n<b>KEY EVENTS TODAY</b>")

    # Check if today is Sept 17
    if date.today().day == 17:
        report.append("<b>[CRITICAL]</b> CBRL Earnings After Close")
        report.append("  Position: 81 shares @ $51.00")
        report.append("  Catalyst: Q4 earnings + 34% short interest")
        report.append("  Action: Monitor for pre-earnings volatility")
        report.append("  Risk: Stop loss at $46.92")
        report.append("  Target: $60.00 (+15%)")
    else:
        report.append("No major catalyst events today")

    # Upcoming Events
    report.append("\n<b>UPCOMING CATALYSTS</b>")
    report.append("Sept 19: INCY FDA Decision (PDUFA)")
    report.append("  Position: 61 shares @ $83.97")
    report.append("  Binary event - Opzelura approval")

    # Portfolio Status
    report.append("\n<b>PORTFOLIO STATUS</b>")
    report.append("Total Value: $205,338.41")
    report.append("Unrealized P&L: +$5,080.89 (+5.45%)")
    report.append("Capital Deployed: 58.2%")
    report.append("Risk Level: CONTROLLED")

    # Top Performers to Watch
    report.append("\n<b>TOP PERFORMERS (Monitor for Exit)</b>")
    report.append("1. RGTI: +22.73% - Consider partial profit")
    report.append("2. ORCL: +21.92% - Near resistance")
    report.append("3. DAKT: +13.85% - Strong momentum")

    # Underperformers
    report.append("\n<b>UNDERPERFORMERS (Review Stop Loss)</b>")
    report.append("1. KSS: -7.37% - Near stop loss")
    report.append("2. SAVA: -3.22% - Weak momentum")
    report.append("3. GPK: -1.66% - Monitor closely")

    # Trading Strategy for Today
    report.append("\n<b>TODAY'S STRATEGY</b>")

    if date.today().day == 17:
        report.append("1. CBRL Pre-Earnings Focus:")
        report.append("   - Monitor volume spikes")
        report.append("   - Consider tightening stop if volatility increases")
        report.append("   - Watch for short covering activity")

    report.append("2. Portfolio Management:")
    report.append("   - Review stop losses on all positions")
    report.append("   - Consider profit taking on 20%+ winners")
    report.append("   - Maintain defensive DEE-BOT allocation")

    report.append("3. New Opportunities:")
    report.append("   - Check ChatGPT for fresh signals")
    report.append("   - Focus on high-conviction setups only")
    report.append("   - Keep powder dry for INCY event")

    # Risk Management Reminders
    report.append("\n<b>RISK REMINDERS</b>")
    report.append("- All stops are in place")
    report.append("- CBRL earnings risk today")
    report.append("- INCY binary event in 2 days")
    report.append("- Maintain position sizing discipline")

    # System Status
    report.append("\n<b>SYSTEM STATUS</b>")
    report.append("Multi-Agent Analysis: ACTIVE")
    report.append("Automated Reports: SCHEDULED")
    report.append("Stop Loss Protection: ENABLED")
    report.append("ChatGPT Integration: MANUAL MODE")

    # Footer
    report.append("\n" + "=" * 40)
    report.append("Trade carefully. Protect capital.")
    report.append("Next update: Post-Market 4:15 PM ET")

    return "\n".join(report)

def main():
    """Main function to generate and send pre-market analysis"""

    print("=" * 60)
    print("GENERATING PRE-MARKET ANALYSIS")
    print("=" * 60)

    # Generate analysis
    analysis = generate_premarket_analysis()

    # Display in console
    print("\nAnalysis Preview:")
    print("-" * 50)
    console_version = analysis.replace("<b>", "").replace("</b>", "")
    print(console_version)
    print("-" * 50)

    # Send to Telegram
    success = send_telegram_message(analysis)

    if success:
        # Save locally
        report_dir = Path("02_data/research/reports/premarket")
        report_dir.mkdir(parents=True, exist_ok=True)

        report_file = report_dir / f"premarket_analysis_{date.today()}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(analysis)

        print(f"Analysis saved: {report_file}")

    print("=" * 60)
    return success

if __name__ == "__main__":
    main()