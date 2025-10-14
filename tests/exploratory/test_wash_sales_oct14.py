"""
Test wash sales for Oct 14 ChatGPT research
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from scripts.utilities.wash_sale_checker import WashSaleChecker

# All proposed trades from ChatGPT research
shorgan_trades = [
    {'ticker': 'ARQT', 'action': 'buy', 'shares': 150},  # Already hold 150
    {'ticker': 'GKOS', 'action': 'buy', 'shares': 44},   # Already hold 44
    {'ticker': 'SNDX', 'action': 'buy', 'shares': 65},   # Already hold 65
    {'ticker': 'RIG', 'action': 'buy', 'shares': 1250},  # Already hold 1250
    {'ticker': 'TLRY', 'action': 'sell', 'shares': 100}, # Short recommendation
]

dee_trades = [
    {'ticker': 'WMT', 'action': 'buy', 'shares': 93},    # Liquidated Oct 8
    {'ticker': 'COST', 'action': 'buy', 'shares': 11},   # Already hold 11
    {'ticker': 'MRK', 'action': 'buy', 'shares': 110},   # Liquidated Oct 8
    {'ticker': 'UNH', 'action': 'buy', 'shares': 22},    # Liquidated Oct 8
    {'ticker': 'NEE', 'action': 'buy', 'shares': 95},    # Canceled Oct 8
]

print("=" * 80)
print("WASH SALE ANALYSIS - OCT 14, 2025 CHATGPT RESEARCH")
print("=" * 80)
print()

print("SHORGAN-BOT Analysis:")
print("-" * 80)
checker_shorgan = WashSaleChecker('shorgan')
safe_shorgan, blocked_shorgan = checker_shorgan.check_multiple_tickers(shorgan_trades)

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
safe_dee, blocked_dee = checker_dee.check_multiple_tickers(dee_trades)

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
