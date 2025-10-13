"""
Test wash sales for Claude Oct 13 research (for Oct 14 trading)
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from scripts.utilities.wash_sale_checker import WashSaleChecker

# Claude's SHORGAN recommendations
claude_shorgan_trades = [
    {'ticker': 'SNDX', 'action': 'buy', 'shares': 65},    # 2.5% position
    {'ticker': 'GKOS', 'action': 'buy', 'shares': 44},    # 2.5% position
    {'ticker': 'ARWR', 'action': 'buy', 'shares': 100},   # 2.5% position (~$3,700)
    {'ticker': 'ALT', 'action': 'buy', 'shares': 500},    # 1-2% speculative
    {'ticker': 'CAPR', 'action': 'buy', 'shares': 250},   # 1-2% speculative
]

# Claude's DEE-BOT recommendations
claude_dee_trades = [
    {'ticker': 'DUK', 'action': 'buy', 'shares': 79},     # 25% position ($10K)
    {'ticker': 'ED', 'action': 'buy', 'shares': 124},     # 25% position ($12.5K)
    {'ticker': 'PEP', 'action': 'buy', 'shares': 34},     # 10% position ($5K)
]

print("=" * 80)
print("CLAUDE RESEARCH WASH SALE ANALYSIS - OCT 14, 2025")
print("=" * 80)
print()

print("SHORGAN-BOT Analysis:")
print("-" * 80)
checker_shorgan = WashSaleChecker('shorgan')
safe_shorgan, blocked_shorgan = checker_shorgan.check_multiple_tickers(claude_shorgan_trades)

print(f"Safe: {len(safe_shorgan)}, Blocked: {len(blocked_shorgan)}")
print()

if blocked_shorgan:
    print("BLOCKED TRADES:")
    for trade in blocked_shorgan:
        info = trade['wash_sale_info']
        print(f"[BLOCKED] {trade['action'].upper()} {trade.get('shares', 0)} {trade['ticker']}")
        print(f"   Reason: {info['reason']}")
        print(f"   Clear Date: {info.get('clear_date', 'N/A')}")
        if info.get('alternatives'):
            print(f"   Alternatives: {', '.join(info['alternatives'])}")
        print()

if safe_shorgan:
    print("SAFE TRADES:")
    for trade in safe_shorgan:
        print(f"[OK] {trade['action'].upper()} {trade.get('shares', 0)} {trade['ticker']}")
    print()

print("=" * 80)
print("DEE-BOT Analysis:")
print("-" * 80)
checker_dee = WashSaleChecker('dee')
safe_dee, blocked_dee = checker_dee.check_multiple_tickers(claude_dee_trades)

print(f"Safe: {len(safe_dee)}, Blocked: {len(blocked_dee)}")
print()

if blocked_dee:
    print("BLOCKED TRADES:")
    for trade in blocked_dee:
        info = trade['wash_sale_info']
        print(f"[BLOCKED] {trade['action'].upper()} {trade.get('shares', 0)} {trade['ticker']}")
        print(f"   Reason: {info['reason']}")
        print(f"   Clear Date: {info.get('clear_date', 'N/A')}")
        if info.get('alternatives'):
            print(f"   Alternatives: {', '.join(info['alternatives'])}")
        print()

if safe_dee:
    print("SAFE TRADES:")
    for trade in safe_dee:
        print(f"[OK] {trade['action'].upper()} {trade.get('shares', 0)} {trade['ticker']}")
    print()

print("=" * 80)
print()
print("COMPARISON WITH CURRENT HOLDINGS:")
print("-" * 80)
print("Current SHORGAN positions relevant to Claude recommendations:")
print("  SNDX: 65 shares @ $15.21 (Oct 3) - BLOCKED if buying more")
print("  GKOS: 44 shares @ $84.77 (Oct 1) - BLOCKED if buying more")
print("  ARWR: NOT HELD - Safe to buy")
print("  ALT: NOT HELD - Safe to buy")
print("  CAPR: NOT HELD - Safe to buy")
print()
print("Current DEE positions relevant to Claude recommendations:")
print("  DUK: NOT HELD - Safe to buy")
print("  ED: NOT HELD - Safe to buy")
print("  PEP: NOT HELD - Safe to buy")
print("=" * 80)
