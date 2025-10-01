"""
ChatGPT Pre-Market Recommendations Extractor for SHORGAN-BOT
Specifically designed to extract trading recommendations from TradingAgents format
"""

import json
import re
from datetime import datetime
from pathlib import Path
import requests

def extract_premarket_trades(text):
    """Extract pre-market trading recommendations from ChatGPT format"""

    trades = []

    # Common patterns in TradingAgents recommendations
    patterns = [
        # Pattern 1: "1. SYMBOL (Company) - Action"
        r'(?:\d+\.?\s+)?([A-Z]{1,5})\s+\([^)]+\)[^$]*?(?:Entry|Buy|@).*?\$?([\d.]+)',

        # Pattern 2: "Symbol: XXXX, Entry: $XX.XX, Stop: $XX.XX, Target: $XX.XX"
        r'Symbol:\s*([A-Z]{1,5}).*?Entry:\s*\$?([\d.]+).*?Stop:\s*\$?([\d.]+).*?Target:\s*\$?([\d.]+)',

        # Pattern 3: "XXXX: Buy at $XX, Stop at $XX, Target $XX"
        r'([A-Z]{1,5}):\s*(?:Buy|Long).*?\$?([\d.]+).*?[Ss]top.*?\$?([\d.]+).*?[Tt]arget.*?\$?([\d.]+)',

        # Pattern 4: Structured format with bullets
        r'(?:•|\*|-)\s*([A-Z]{1,5})\s*.*?Entry:\s*\$?([\d.]+)',
    ]

    # Try each pattern
    for pattern_str in patterns:
        pattern = re.compile(pattern_str, re.IGNORECASE | re.DOTALL)
        matches = pattern.finditer(text)

        for match in matches:
            groups = match.groups()

            if len(groups) >= 2:
                trade = {'symbol': groups[0]}

                if len(groups) >= 4:  # Full trade with entry, stop, target
                    trade['entry'] = float(groups[1])
                    trade['stop'] = float(groups[2])
                    trade['target'] = float(groups[3])
                else:  # Just symbol and entry
                    trade['entry'] = float(groups[1])

                    # Try to find stop and target nearby
                    context = text[max(0, match.start()-100):min(len(text), match.end()+200)]

                    stop_match = re.search(r'[Ss]top.*?\$?([\d.]+)', context)
                    if stop_match:
                        trade['stop'] = float(stop_match.group(1))

                    target_match = re.search(r'[Tt]arget.*?\$?([\d.]+)', context)
                    if target_match:
                        trade['target'] = float(target_match.group(1))

                # Determine action
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                if re.search(r'\b(short|sell|bearish)\b', context, re.IGNORECASE):
                    trade['action'] = 'SHORT'
                else:
                    trade['action'] = 'LONG'

                # Default size
                trade['size_pct'] = 5

                # Avoid duplicates
                if not any(t['symbol'] == trade['symbol'] for t in trades):
                    trades.append(trade)

    # Also look for specific SHORGAN-BOT catalyst patterns
    catalyst_pattern = r'([A-Z]{1,5}).*?(?:earnings|FDA|merger|catalyst|squeeze).*?\$?([\d.]+)'
    catalyst_matches = re.finditer(catalyst_pattern, text, re.IGNORECASE)

    for match in catalyst_matches:
        symbol = match.group(1)
        price = float(match.group(2))

        if not any(t['symbol'] == symbol for t in trades):
            trade = {
                'symbol': symbol,
                'entry': price,
                'stop': price * 0.92,  # Default 8% stop for SHORGAN
                'target': price * 1.15,  # Default 15% target
                'action': 'LONG',
                'size_pct': 5,
                'catalyst': True
            }
            trades.append(trade)

    return trades

def validate_trades(trades):
    """Validate and clean extracted trades"""

    valid_trades = []

    for trade in trades:
        # Must have symbol and entry
        if 'symbol' not in trade or 'entry' not in trade:
            continue

        # Symbol validation
        if not re.match(r'^[A-Z]{1,5}$', trade['symbol']):
            continue

        # Price validation
        if trade['entry'] <= 0 or trade['entry'] > 10000:
            continue

        # Set defaults if missing
        if 'stop' not in trade:
            trade['stop'] = trade['entry'] * 0.92  # 8% stop

        if 'target' not in trade:
            trade['target'] = trade['entry'] * 1.15  # 15% target

        if 'action' not in trade:
            trade['action'] = 'LONG'

        if 'size_pct' not in trade:
            trade['size_pct'] = 5

        # Calculate R:R
        risk = abs(trade['entry'] - trade['stop'])
        reward = abs(trade['target'] - trade['entry'])
        if risk > 0:
            trade['risk_reward'] = round(reward / risk, 2)

        valid_trades.append(trade)

    return valid_trades

def save_to_json(trades, raw_text):
    """Save extracted trades to JSON format"""

    timestamp = datetime.now()

    report = {
        'date': timestamp.strftime('%Y-%m-%d'),
        'time': timestamp.strftime('%H:%M:%S'),
        'source': 'ChatGPT SHORGAN-BOT Pre-Market',
        'trades': trades,
        'trade_count': len(trades),
        'raw_text': raw_text[:5000],  # Limit size
        'extracted_at': timestamp.isoformat()
    }

    # Save paths
    output_dir = Path('scripts-and-data/daily-json/chatgpt')
    output_dir.mkdir(parents=True, exist_ok=True)

    daily_file = output_dir / f"premarket_{timestamp.strftime('%Y%m%d')}.json"

    with open(daily_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Saved to: {daily_file}")

    return daily_file

def display_recommendations(trades):
    """Display extracted trading recommendations"""

    print("\n" + "="*70)
    print(f"SHORGAN-BOT PRE-MARKET RECOMMENDATIONS")
    print(f"Extracted: {len(trades)} trades")
    print("="*70)

    total_allocation = 0

    for i, trade in enumerate(trades, 1):
        print(f"\n{i}. {trade['symbol']} - {trade['action']}")
        print(f"   Entry: ${trade['entry']:.2f}")
        print(f"   Stop: ${trade['stop']:.2f} ({((trade['stop']/trade['entry'])-1)*100:.1f}%)")
        print(f"   Target: ${trade['target']:.2f} ({((trade['target']/trade['entry'])-1)*100:.1f}%)")

        if 'risk_reward' in trade:
            print(f"   R:R Ratio: 1:{trade['risk_reward']}")

        print(f"   Position Size: {trade['size_pct']}%")

        if 'catalyst' in trade:
            print(f"   [Catalyst Trade]")

        total_allocation += trade['size_pct']

    print("\n" + "-"*70)
    print(f"Total Allocation: {total_allocation}%")

    if total_allocation > 100:
        print("WARNING: Total allocation exceeds 100%")

def main():
    print("="*70)
    print("CHATGPT PRE-MARKET EXTRACTOR FOR SHORGAN-BOT")
    print("="*70)

    print("\nINSTRUCTIONS:")
    print("1. Go to your ChatGPT conversation")
    print("2. Copy the entire pre-market recommendations")
    print("3. Paste below and press Enter twice")
    print("-"*70)

    # Collect input
    lines = []
    while True:
        try:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        except (EOFError, KeyboardInterrupt):
            break

    text = "\n".join(lines[:-1] if lines and lines[-1] == "" else lines)

    if not text.strip():
        print("\nNo text provided")
        return

    # Extract trades
    print("\nExtracting trades...")
    raw_trades = extract_premarket_trades(text)

    # Validate
    trades = validate_trades(raw_trades)

    if not trades:
        print("\nNo valid trades found")
        print("\nText preview:")
        print(text[:500])
        return

    # Display
    display_recommendations(trades)

    # Save
    output_file = save_to_json(trades, text)

    # Ask to process
    print("\n" + "="*70)
    process = input("\nProcess these trades through multi-agent system? (y/n): ")

    if process.lower() == 'y':
        print("\nLaunching trade processor...")
        import subprocess
        try:
            subprocess.run(['python', 'scripts-and-data/automation/process-trades.py'])
        except Exception as e:
            print(f"Error launching processor: {e}")
            print("Run manually: python scripts-and-data/automation/process-trades.py")

if __name__ == "__main__":
    main()