"""
Manual ChatGPT Report Extractor
Use this when the Chrome extension fails to detect reports
Copy and paste the ChatGPT report text when prompted
"""

import json
import re
from datetime import datetime
from pathlib import Path

def parse_trade_recommendation(text):
    """Parse a trade recommendation from text"""
    trade = {}

    # Extract symbol
    symbol_match = re.search(r'(?:Symbol|Ticker|Stock):\s*([A-Z]{1,5})', text, re.IGNORECASE)
    if symbol_match:
        trade['symbol'] = symbol_match.group(1)

    # Extract action
    if re.search(r'\b(?:buy|long|bullish)\b', text, re.IGNORECASE):
        trade['action'] = 'BUY'
    elif re.search(r'\b(?:sell|short|bearish)\b', text, re.IGNORECASE):
        trade['action'] = 'SELL'

    # Extract prices
    entry_match = re.search(r'(?:Entry|Buy|Enter).*?\$?([\d.]+)', text, re.IGNORECASE)
    if entry_match:
        trade['entry'] = float(entry_match.group(1))

    stop_match = re.search(r'(?:Stop|Stop Loss|SL).*?\$?([\d.]+)', text, re.IGNORECASE)
    if stop_match:
        trade['stop'] = float(stop_match.group(1))

    target_match = re.search(r'(?:Target|Take Profit|TP|PT).*?\$?([\d.]+)', text, re.IGNORECASE)
    if target_match:
        trade['target'] = float(target_match.group(1))

    # Extract position size
    size_match = re.search(r'(?:Size|Position|Allocation).*?([\d.]+)%', text, re.IGNORECASE)
    if size_match:
        trade['size_pct'] = float(size_match.group(1))
    else:
        trade['size_pct'] = 5.0  # Default 5%

    return trade if 'symbol' in trade else None

def extract_trades_from_report(report_text):
    """Extract all trade recommendations from report"""
    trades = []

    # Split by common delimiters
    sections = re.split(r'\n\n|\d+\.\s+|\*\s+', report_text)

    for section in sections:
        # Look for trade patterns
        if re.search(r'(?:Symbol|Ticker|Stock|Entry|Buy|Long|Short)', section, re.IGNORECASE):
            trade = parse_trade_recommendation(section)
            if trade:
                trades.append(trade)

    # Also try to find structured trades
    # Pattern: SYMBOL: Entry $X, Stop $Y, Target $Z
    structured_pattern = r'([A-Z]{1,5}).*?(?:Entry|@).*?\$?([\d.]+).*?(?:Stop|SL).*?\$?([\d.]+).*?(?:Target|TP|PT).*?\$?([\d.]+)'
    structured_matches = re.finditer(structured_pattern, report_text, re.IGNORECASE | re.DOTALL)

    for match in structured_matches:
        trade = {
            'symbol': match.group(1),
            'entry': float(match.group(2)),
            'stop': float(match.group(3)),
            'target': float(match.group(4)),
            'action': 'BUY',
            'size_pct': 5.0
        }
        # Avoid duplicates
        if not any(t.get('symbol') == trade['symbol'] for t in trades):
            trades.append(trade)

    return trades

def save_report(trades, report_text):
    """Save the extracted report"""
    timestamp = datetime.now()

    report = {
        'date': timestamp.strftime('%Y-%m-%d'),
        'time': timestamp.strftime('%H:%M:%S'),
        'source': 'ChatGPT TradingAgents (Manual Extract)',
        'trades': trades,
        'trade_count': len(trades),
        'raw_text': report_text,
        'url': 'https://chatgpt.com/manual_entry',
        'capture_timestamp': timestamp.isoformat()
    }

    # Save to JSON
    output_dir = Path('scripts-and-data/daily-json/chatgpt')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Daily file
    daily_file = output_dir / f"chatgpt_report_{timestamp.strftime('%Y-%m-%d')}.json"
    with open(daily_file, 'w') as f:
        json.dump(report, f, indent=2)

    # Timestamped backup
    backup_file = output_dir / f"chatgpt_report_{timestamp.strftime('%Y-%m-%d_%H%M%S')}.json"
    with open(backup_file, 'w') as f:
        json.dump(report, f, indent=2)

    return daily_file, backup_file

def display_trades(trades):
    """Display extracted trades"""
    print("\n" + "="*60)
    print(f"EXTRACTED {len(trades)} TRADE RECOMMENDATIONS")
    print("="*60)

    for i, trade in enumerate(trades, 1):
        print(f"\nTrade #{i}:")
        print(f"  Symbol: {trade.get('symbol', 'N/A')}")
        print(f"  Action: {trade.get('action', 'BUY')}")
        print(f"  Entry: ${trade.get('entry', 0):.2f}")
        print(f"  Stop: ${trade.get('stop', 0):.2f}")
        print(f"  Target: ${trade.get('target', 0):.2f}")
        print(f"  Size: {trade.get('size_pct', 5)}%")

        # Calculate risk/reward
        if 'entry' in trade and 'stop' in trade and 'target' in trade:
            risk = abs(trade['entry'] - trade['stop'])
            reward = abs(trade['target'] - trade['entry'])
            if risk > 0:
                rr_ratio = reward / risk
                print(f"  R:R Ratio: 1:{rr_ratio:.1f}")

def main():
    print("="*60)
    print("MANUAL CHATGPT REPORT EXTRACTOR")
    print("="*60)
    print("\nPaste the ChatGPT trading report below.")
    print("When done, press Enter twice (empty line) to process.\n")

    # Collect multi-line input
    lines = []
    print("Paste report (press Enter twice when done):")
    print("-"*40)

    while True:
        try:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        except EOFError:
            break

    report_text = "\n".join(lines[:-1] if lines and lines[-1] == "" else lines)

    if not report_text.strip():
        print("\n❌ No text provided. Exiting.")
        return

    print("\n" + "="*60)
    print("PROCESSING REPORT...")
    print("="*60)

    # Extract trades
    trades = extract_trades_from_report(report_text)

    if not trades:
        print("\n⚠️ No trades found in the report.")
        print("The report may not contain structured trade recommendations.")

        # Try to show what was captured
        print("\nReport preview (first 500 chars):")
        print("-"*40)
        print(report_text[:500])

        # Save anyway for debugging
        save_report([], report_text)
        print("\n✅ Raw report saved for manual review.")
        return

    # Display trades
    display_trades(trades)

    # Save report
    daily_file, backup_file = save_report(trades, report_text)

    print("\n" + "="*60)
    print("✅ REPORT SAVED SUCCESSFULLY")
    print("="*60)
    print(f"Daily file: {daily_file}")
    print(f"Backup: {backup_file}")

    # Ask if user wants to process trades
    print("\n" + "="*60)
    process = input("\nProcess these trades through multi-agent system? (y/n): ")
    if process.lower() == 'y':
        import subprocess
        print("\n🚀 Launching trade processor...")
        subprocess.run(['python', 'scripts-and-data/automation/process-trades.py'])

if __name__ == "__main__":
    main()