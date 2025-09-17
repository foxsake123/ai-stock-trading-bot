#!/usr/bin/env python3
"""
Position Performance Review
Reviews current positions for both SHORGAN-BOT and DEE-BOT
"""

import csv
from datetime import datetime
from pathlib import Path

def review_positions():
    print("=" * 60)
    print("POSITION PERFORMANCE REVIEW")
    print(f"Time: {datetime.now().strftime('%I:%M %p ET')}")
    print("=" * 60)

    # Check SHORGAN-BOT positions
    print("\nSHORGAN-BOT Positions:")
    print("-" * 40)

    shorgan_file = Path("02_data/portfolio/positions/shorgan_bot_positions.csv")
    total_value = 0
    total_pnl = 0

    if shorgan_file.exists():
        with open(shorgan_file, 'r') as f:
            reader = csv.DictReader(f)
            positions = list(reader)

            # Sort by P&L percentage
            sorted_positions = sorted(positions,
                                     key=lambda x: float(x.get('unrealized_pnl_pct', 0)),
                                     reverse=True)

            for pos in sorted_positions:
                if pos.get('symbol'):
                    try:
                        value = abs(float(pos.get('market_value', 0)))
                        pnl = float(pos.get('unrealized_pnl', 0))
                        pnl_pct = float(pos.get('unrealized_pnl_pct', 0))
                        total_value += value
                        total_pnl += pnl

                        # Status indicator
                        if pnl > 100:
                            status = "[++]"  # Big winner
                        elif pnl > 0:
                            status = "[+]"   # Winner
                        elif pnl < -100:
                            status = "[--]"  # Big loser
                        elif pnl < 0:
                            status = "[-]"   # Loser
                        else:
                            status = "[=]"   # Flat

                        print(f"{status} {pos['symbol']:6} | ${value:10,.2f} | {pnl:+8.2f} ({pnl_pct:+6.2f}%)")
                    except (ValueError, KeyError) as e:
                        print(f"Error processing {pos.get('symbol', 'unknown')}: {e}")

    print(f"\nTotal: ${total_value:,.2f} | P&L: ${total_pnl:+,.2f}")

    # Highlight upcoming catalysts
    print("\n[!] UPCOMING CATALYSTS:")
    print("    CBRL: Earnings tomorrow after close (81 shares)")
    print("    INCY: FDA decision Sept 19 (61 shares)")

    # Check DEE-BOT positions
    print("\n\nDEE-BOT Positions:")
    print("-" * 40)

    dee_file = Path("02_data/portfolio/positions/dee_bot_positions.csv")
    dee_value = 0

    if dee_file.exists():
        with open(dee_file, 'r') as f:
            reader = csv.DictReader(f)
            for pos in reader:
                if pos.get('symbol'):
                    try:
                        qty = int(pos.get('quantity', 0))
                        price = float(pos.get('current_price', pos.get('avg_price', 0)))
                        value = qty * price
                        dee_value += value
                        print(f"    {pos['symbol']:6} | {qty:4} shares | ${value:10,.2f}")
                    except (ValueError, KeyError) as e:
                        print(f"Error processing {pos.get('symbol', 'unknown')}: {e}")

    print(f"\nTotal: ${dee_value:,.2f}")

    # Portfolio Summary
    print("\n" + "=" * 60)
    print("PORTFOLIO SUMMARY")
    print(f"Total Position Value: ${total_value + dee_value:,.2f}")
    print(f"Total Unrealized P&L: ${total_pnl:+,.2f}")

    # Calculate return percentage
    if total_value > 0:
        return_pct = (total_pnl / (total_value - total_pnl)) * 100
        print(f"Return on Deployed Capital: {return_pct:+.2f}%")

    # Deployment percentages
    shorgan_deploy = (total_value / 100000) * 100
    dee_deploy = (dee_value / 100000) * 100

    print(f"\nSHORGAN-BOT Deployment: {shorgan_deploy:.1f}% (${100000 - total_value:,.2f} cash available)")
    print(f"DEE-BOT Deployment: {dee_deploy:.1f}% (${100000 - dee_value:,.2f} cash available)")

    # Risk assessment
    print("\nRISK ASSESSMENT:")
    total_deploy = ((total_value + dee_value) / 200000) * 100
    if total_deploy > 90:
        print(f"[WARNING] High exposure: {total_deploy:.1f}% deployed")
    elif total_deploy > 75:
        print(f"[CAUTION] Moderate exposure: {total_deploy:.1f}% deployed")
    else:
        print(f"[OK] Controlled exposure: {total_deploy:.1f}% deployed")

    print("=" * 60)

if __name__ == "__main__":
    review_positions()