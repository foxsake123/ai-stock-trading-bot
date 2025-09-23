#!/usr/bin/env python3
"""
Test trade parsing from TODAYS_TRADES file
"""

import re
from pathlib import Path

def test_parsing():
    file_path = Path('docs/TODAYS_TRADES_2025-09-23.md')

    with open(file_path, 'r') as f:
        content = f.read()

    print("=== FILE CONTENT PREVIEW ===")
    print(content[:500])
    print("...\n")

    # Test DEE-BOT section detection
    dee_section_match = re.search(r'## DEE-BOT.*?(?=^## [A-Z]|^---|\Z)', content, re.DOTALL | re.MULTILINE)
    if dee_section_match:
        print("[OK] DEE-BOT section found")
        dee_content = dee_section_match.group(0)
        print(f"DEE-BOT content length: {len(dee_content)}")
        print("DEE-BOT content preview:")
        print(repr(dee_content[:200]))

        # Test sell orders table
        sell_table_match = re.search(r'### SELL ORDERS.*?\n\|.*?\n\|(.*?)(?=\n### |\n## |\Z)', dee_content, re.DOTALL)
        if sell_table_match:
            print("[OK] SELL ORDERS table found")
            sell_rows = sell_table_match.group(1).strip().split('\n')
            print(f"Sell rows found: {len(sell_rows)}")
            for i, row in enumerate(sell_rows):
                print(f"  Row {i}: {repr(row)}")
                if '|' in row and not row.strip().startswith('|--'):
                    parts = [p.strip() for p in row.split('|') if p.strip()]
                    print(f"    Parsed parts: {parts}")
        else:
            print("[FAIL] SELL ORDERS table not found")

        # Test buy orders table
        buy_table_match = re.search(r'### BUY ORDERS.*?\n\|.*?\n\|(.*?)(?=\n### |\n## |\Z)', dee_content, re.DOTALL)
        if buy_table_match:
            print("[OK] BUY ORDERS table found")
            buy_rows = buy_table_match.group(1).strip().split('\n')
            print(f"Buy rows found: {len(buy_rows)}")
            for i, row in enumerate(buy_rows):
                print(f"  Row {i}: {repr(row)}")
        else:
            print("[FAIL] BUY ORDERS table not found")

    else:
        print("[FAIL] DEE-BOT section not found")

    # Test SHORGAN-BOT section
    shorgan_section_match = re.search(r'## SHORGAN-BOT.*?(?=^## [A-Z]|^---|\Z)', content, re.DOTALL | re.MULTILINE)
    if shorgan_section_match:
        print("[OK] SHORGAN-BOT section found")
        shorgan_content = shorgan_section_match.group(0)
        print(f"SHORGAN-BOT content length: {len(shorgan_content)}")
    else:
        print("[FAIL] SHORGAN-BOT section not found")

if __name__ == "__main__":
    test_parsing()