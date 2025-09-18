"""
DEE-BOT Beta-Neutral Recommendations Extractor
Extracts S&P 100 beta-neutral trading recommendations for DEE-BOT
"""

import json
import re
from datetime import datetime
from pathlib import Path

def extract_dee_bot_recommendations(text=None, file_path=None):
    """
    Extract DEE-BOT beta-neutral recommendations

    DEE-BOT focuses on:
    - S&P 100 large-cap stocks
    - Beta-neutral positioning (target beta = 1.0)
    - Defensive sectors (consumer staples, healthcare, utilities)
    - Rebalancing only when beta drifts > 0.15
    """

    if file_path:
        with open(file_path, 'r') as f:
            text = f.read()

    if not text:
        print("Please paste the DEE-BOT recommendations (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        text = '\n'.join(lines)

    recommendations = []

    # DEE-BOT specific patterns for beta-neutral recommendations
    patterns = [
        # Pattern for rebalancing: "Sell XXXX, Buy YYYY for beta adjustment"
        r'(?:Sell|Reduce)\s+([A-Z]{1,5}).*?(?:Buy|Add)\s+([A-Z]{1,5})',

        # Pattern for beta-weighted positions: "XXXX (Beta: X.XX) - XX% allocation"
        r'([A-Z]{1,5})\s*\(?Beta:\s*([\d.]+)\)?\s*-?\s*([\d.]+)%',

        # Pattern for defensive additions: "Add XXXX for defensive positioning"
        r'(?:Add|Buy|Increase)\s+([A-Z]{1,5})\s+(?:for|to)\s+(?:defensive|beta)',

        # Pattern for rebalancing pairs
        r'([A-Z]{1,5})\s*→\s*([A-Z]{1,5})',
    ]

    # Extract rebalancing actions
    for pattern_str in patterns:
        pattern = re.compile(pattern_str, re.IGNORECASE)
        matches = pattern.finditer(text)

        for match in matches:
            groups = match.groups()

            if len(groups) == 2:  # Sell/Buy pair
                recommendations.append({
                    'action': 'REBALANCE',
                    'sell': groups[0],
                    'buy': groups[1],
                    'reason': 'Beta adjustment'
                })
            elif len(groups) == 3:  # Symbol with beta and allocation
                recommendations.append({
                    'symbol': groups[0],
                    'beta': float(groups[1]),
                    'allocation_pct': float(groups[2]),
                    'action': 'HOLD' if float(groups[1]) < 1.0 else 'MONITOR'
                })

    # Look for specific S&P 100 defensive stocks
    sp100_defensive = ['PG', 'JNJ', 'KO', 'PEP', 'WMT', 'CVS', 'UNH', 'MRK',
                      'PFE', 'ABT', 'MDT', 'CL', 'GIS', 'K', 'CPB', 'HSY']

    for symbol in sp100_defensive:
        if symbol in text.upper():
            # Check context around the symbol
            context_pattern = rf'{symbol}.*?(?:buy|add|increase|accumulate)'
            if re.search(context_pattern, text, re.IGNORECASE):
                recommendations.append({
                    'symbol': symbol,
                    'action': 'BUY',
                    'strategy': 'Defensive positioning',
                    'sector': 'Defensive'
                })

    # Save to JSON
    output = {
        'bot': 'DEE-BOT',
        'strategy': 'Beta-Neutral S&P 100',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S'),
        'target_beta': 1.0,
        'recommendations': recommendations,
        'recommendation_count': len(recommendations)
    }

    # Save to file
    output_dir = Path('../../02_data/research/reports/dee_bot')
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f'dee_bot_recommendations_{datetime.now().strftime("%Y-%m-%d")}.json'

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nDEE-BOT Recommendations Extracted:")
    print(f"{'='*50}")
    print(f"Date: {output['date']}")
    print(f"Strategy: {output['strategy']}")
    print(f"Target Beta: {output['target_beta']}")
    print(f"Recommendations: {len(recommendations)}")

    if recommendations:
        print(f"\nActions:")
        for rec in recommendations:
            if 'action' in rec and rec['action'] == 'REBALANCE':
                print(f"  - REBALANCE: Sell {rec['sell']} → Buy {rec['buy']}")
            elif 'symbol' in rec:
                print(f"  - {rec.get('action', 'MONITOR')} {rec['symbol']}")

    print(f"\nSaved to: {output_file}")

    # Also check current portfolio beta
    check_portfolio_beta()

    return output

def check_portfolio_beta():
    """Check current DEE-BOT portfolio beta"""

    # Beta values for current holdings
    current_betas = {
        'AAPL': 1.25,
        'JPM': 1.15,
        'MSFT': 1.20,
        'GOOGL': 1.10,
        'XOM': 0.85,
        'CVX': 0.90,
        'HD': 1.05,
        'NVDA': 1.65
    }

    # Read current positions
    import pandas as pd
    try:
        positions = pd.read_csv('../../portfolio-holdings/dee-bot/current/positions.csv')

        total_value = 0
        weighted_beta = 0

        for _, pos in positions.iterrows():
            symbol = pos['symbol']
            market_value = pos['quantity'] * pos['current_price']
            total_value += market_value

            if symbol in current_betas:
                weighted_beta += market_value * current_betas[symbol]

        if total_value > 0:
            portfolio_beta = weighted_beta / total_value
            print(f"\nCurrent Portfolio Beta: {portfolio_beta:.2f}")

            if abs(portfolio_beta - 1.0) > 0.15:
                print(f"[WARNING] Beta drift detected! Target: 1.0, Current: {portfolio_beta:.2f}")
                print("Rebalancing recommended to return to beta-neutral")
            else:
                print(f"[OK] Portfolio beta within tolerance (1.0 ± 0.15)")

    except Exception as e:
        print(f"Could not check portfolio beta: {e}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # File path provided
        extract_dee_bot_recommendations(file_path=sys.argv[1])
    else:
        # Interactive mode
        extract_dee_bot_recommendations()