"""
Manual ChatGPT Report Extractor
Use this when the browser extension isn't working
"""

import json
import os
from datetime import datetime
import re

def extract_trades_from_text(text):
    """Extract trade recommendations from ChatGPT text"""

    trades = {
        'dee_bot': [],
        'shorgan_bot': []
    }

    # Clean the text
    text = text.replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')
    lines = text.split('\n')

    current_bot = None

    for i, line in enumerate(lines):
        line = line.strip()

        # Identify which bot section
        if 'DEE-BOT' in line.upper() or 'DEFENSIVE' in line.upper():
            current_bot = 'dee_bot'
        elif 'SHORGAN' in line.upper() or 'CATALYST' in line.upper():
            current_bot = 'shorgan_bot'

        # Look for trade patterns
        # Pattern 1: "BUY: AAPL (10 shares)"
        # Pattern 2: "SELL AAPL - 10 shares"
        # Pattern 3: "AAPL: BUY 10"

        # Check for BUY/SELL keywords
        if any(action in line.upper() for action in ['BUY', 'SELL', 'SHORT', 'COVER']):
            # Try to extract ticker symbol (uppercase letters 2-5 chars)
            ticker_pattern = r'\b([A-Z]{2,5})\b'
            tickers = re.findall(ticker_pattern, line)

            # Try to extract quantity
            qty_pattern = r'(\d+)\s*(?:shares|shs|share)'
            qty_match = re.search(qty_pattern, line, re.IGNORECASE)

            if tickers and qty_match:
                symbol = tickers[0]
                quantity = int(qty_match.group(1))

                # Determine action
                action = 'BUY' if 'BUY' in line.upper() else 'SELL'

                trade = {
                    'symbol': symbol,
                    'action': action,
                    'quantity': quantity,
                    'reason': line
                }

                # Add to appropriate bot
                if current_bot == 'dee_bot':
                    # Only S&P 100 stocks for DEE-BOT
                    sp100_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
                                   'BRK', 'JPM', 'JNJ', 'V', 'PG', 'XOM', 'UNH', 'HD',
                                   'MA', 'DIS', 'CVX', 'PFE', 'WMT', 'ABBV', 'KO', 'PEP']
                    if symbol in sp100_stocks:
                        trades['dee_bot'].append(trade)
                elif current_bot == 'shorgan_bot':
                    trades['shorgan_bot'].append(trade)
                else:
                    # If no bot identified, guess based on stock
                    if symbol in ['INCY', 'KSS', 'RGTI', 'ORCL', 'IONQ', 'BBAI', 'SOUN']:
                        trades['shorgan_bot'].append(trade)

    return trades

def save_extracted_trades(trades):
    """Save extracted trades to JSON and display summary"""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    date_str = datetime.now().strftime('%Y-%m-%d')

    # Create directory
    save_dir = f'../../daily-reports/{date_str}'
    os.makedirs(save_dir, exist_ok=True)

    # Save to JSON
    filename = f'{save_dir}/manual_extracted_{timestamp}.json'
    with open(filename, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'trades': trades,
            'extraction_method': 'manual'
        }, f, indent=2)

    print(f"\n[SUCCESS] Trades saved to: {filename}")

    # Display summary
    print("\n" + "="*70)
    print("EXTRACTED TRADES SUMMARY")
    print("="*70)

    print(f"\nDEE-BOT ({len(trades['dee_bot'])} trades):")
    for trade in trades['dee_bot']:
        print(f"  - {trade['action']} {trade['quantity']} {trade['symbol']}")

    print(f"\nSHORGAN-BOT ({len(trades['shorgan_bot'])} trades):")
    for trade in trades['shorgan_bot']:
        print(f"  - {trade['action']} {trade['quantity']} {trade['symbol']}")

    return filename

def main():
    print("="*70)
    print("     MANUAL CHATGPT REPORT EXTRACTOR")
    print("="*70)
    print("\nThis tool extracts trades when the browser extension fails")
    print("\nINSTRUCTIONS:")
    print("1. Copy your entire ChatGPT report")
    print("2. Paste it here")
    print("3. Press Enter twice to finish")
    print("-"*70)

    # Collect input
    lines = []
    empty_count = 0

    while True:
        try:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break

    text = '\n'.join(lines)

    if not text.strip():
        print("\n[ERROR] No text provided")
        return

    # Extract trades
    print("\n[PROCESSING] Extracting trades...")
    trades = extract_trades_from_text(text)

    # Save and display
    if trades['dee_bot'] or trades['shorgan_bot']:
        save_extracted_trades(trades)

        print("\n[NEXT STEPS]")
        print("1. Review extracted trades above")
        print("2. Run execution script if correct")
        print("3. Or manually edit the JSON file")
    else:
        print("\n[WARNING] No trades extracted")
        print("Make sure the report contains patterns like:")
        print("  - BUY AAPL 10 shares")
        print("  - SELL: MSFT (5 shares)")
        print("  - NVDA - BUY 15 shares")

if __name__ == "__main__":
    main()