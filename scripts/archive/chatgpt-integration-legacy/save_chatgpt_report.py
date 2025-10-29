"""
Direct ChatGPT Report Saver
Simplest possible tool - just saves what you paste
"""

import json
from datetime import datetime
import os

def save_report():
    print("="*70)
    print("CHATGPT REPORT SAVER")
    print("="*70)
    print("\nPaste your ChatGPT report below.")
    print("Type 'SAVE' on a new line when done.\n")

    lines = []
    while True:
        line = input()
        if line.strip().upper() == 'SAVE':
            break
        lines.append(line)

    text = '\n'.join(lines)

    # Save the raw text
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    date_str = datetime.now().strftime('%Y-%m-%d')

    # Create directory
    save_dir = f'daily-reports/{date_str}'
    os.makedirs(save_dir, exist_ok=True)

    # Save raw text
    filename = f'{save_dir}/chatgpt_raw_{timestamp}.txt'
    with open(filename, 'w') as f:
        f.write(text)

    print(f"\n[SUCCESS] Report saved to: {filename}")

    # Try to extract trades
    trades = {'dee_bot': [], 'shorgan_bot': []}

    for line in lines:
        if 'BUY' in line.upper() or 'SELL' in line.upper():
            parts = line.split()
            if len(parts) >= 3:
                action = 'BUY' if 'BUY' in line.upper() else 'SELL'
                # Find ticker (all caps, 2-5 chars)
                for part in parts:
                    if part.isupper() and 2 <= len(part) <= 5 and part not in ['BUY', 'SELL']:
                        symbol = part
                        # Find number
                        for p in parts:
                            if p.isdigit():
                                qty = int(p)
                                trade = {'action': action, 'symbol': symbol, 'quantity': qty}

                                # Decide which bot
                                if 'DEE' in text.upper()[:lines.index(line)*50]:
                                    trades['dee_bot'].append(trade)
                                else:
                                    trades['shorgan_bot'].append(trade)
                                break
                        break

    # Save JSON
    json_file = f'{save_dir}/chatgpt_trades_{timestamp}.json'
    with open(json_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'raw_text': text,
            'extracted_trades': trades
        }, f, indent=2)

    print(f"[SUCCESS] Trades saved to: {json_file}")

    # Show what was extracted
    print("\nExtracted Trades:")
    print(f"DEE-BOT: {len(trades['dee_bot'])} trades")
    for t in trades['dee_bot']:
        print(f"  - {t['action']} {t['quantity']} {t['symbol']}")

    print(f"\nSHORGAN-BOT: {len(trades['shorgan_bot'])} trades")
    for t in trades['shorgan_bot']:
        print(f"  - {t['action']} {t['quantity']} {t['symbol']}")

if __name__ == "__main__":
    save_report()