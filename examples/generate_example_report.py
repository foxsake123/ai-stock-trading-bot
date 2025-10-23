"""
Example: Generate Sample Daily Pre-Market Report
Demonstrates all features of the enhanced reporting system
"""

import asyncio
from datetime import datetime
from src.reports.daily_premarket_report import generate_daily_report


# Sample SHORGAN-BOT recommendations
SHORGAN_RECOMMENDATIONS = [
    {
        'ticker': 'PTGX',
        'strategy': 'M&A Arbitrage',
        'action': 'BUY',
        'entry_price': 76.50,
        'target_price': 95.00,
        'stop_loss': 70.00,
        'position_size': 15.0,
        'composite_score': 72.5,
        'confidence': 85.0,
        'signal_count': 4,
        'priority_score': 88.0,
        'thesis': 'M&A arbitrage play. Acquisition offer at $95/share, currently trading $18.50 below offer price. Deal expected to close Q1 2026.',
        'catalyst': 'FTC approval expected by December 15, 2025. No material anti-trust concerns identified.',
        'risks': [
            'FTC could block deal (low probability ~10%)',
            'Buyer could walk away if market conditions deteriorate',
            'Deal could be renegotiated at lower price'
        ],
        'entry_conditions': [
            'Price must be below $78 for adequate risk/reward',
            'Volume confirmation on entry day',
            'No negative FTC news overnight'
        ]
    },
    {
        'ticker': 'GKOS',
        'strategy': 'FDA Catalyst',
        'action': 'BUY CALLS',
        'entry_price': 83.00,
        'target_price': 110.00,
        'stop_loss': 75.00,
        'position_size': 10.0,
        'composite_score': 65.2,
        'confidence': 75.0,
        'signal_count': 3,
        'priority_score': 78.0,
        'thesis': 'FDA PDUFA date October 28 for Migraine treatment. Strong Phase 3 data, high approval probability.',
        'catalyst': 'PDUFA date October 28, 2025 (6 days). Market peak TAM $8B, current valuation conservative.',
        'risks': [
            'FDA could delay approval (Complete Response Letter)',
            'Label could be restricted, limiting market',
            'Competition from Eli Lilly pending approval'
        ],
        'entry_conditions': [
            'Enter 3-5 days before PDUFA',
            'IV <120% for options',
            'General market not in panic mode (VIX <30)'
        ]
    },
    {
        'ticker': 'SNDX',
        'strategy': 'Product Launch',
        'action': 'BUY',
        'entry_price': 15.50,
        'target_price': 22.00,
        'stop_loss': 13.00,
        'position_size': 12.0,
        'composite_score': 45.8,
        'confidence': 68.0,
        'signal_count': 3,
        'priority_score': 62.0,
        'thesis': 'Axitinib biosimilar launch in Q4. Strong institutional interest, low float (~40M shares).',
        'catalyst': 'Product launch expected November 2025. Partnership with major distributor McKesson.',
        'risks': [
            'Launch could be delayed by manufacturing issues',
            'Pricing pressure from existing biosimilars',
            'Market share capture slower than expected'
        ],
        'entry_conditions': [
            'Confirm no launch delays',
            'McKesson relationship verified',
            'Stock holding support at $15'
        ]
    }
]

# Sample DEE-BOT recommendations
DEE_RECOMMENDATIONS = [
    {
        'ticker': 'JNJ',
        'strategy': 'Defensive Quality',
        'action': 'BUY',
        'entry_price': 158.50,
        'target_price': 172.00,
        'stop_loss': 152.00,
        'position_size': 10.0,
        'composite_score': 35.2,
        'confidence': 72.0,
        'signal_count': 5,
        'priority_score': 68.0,
        'thesis': 'Defensive healthcare with 3.2% dividend yield. Trading at 15.2x P/E vs 5-year avg of 16.8x. Recent insider buying by CFO.',
        'catalyst': 'Q3 earnings November 5. Analyst estimates conservative, beat likely. Talc litigation settlement progress.',
        'risks': [
            'Talc litigation could escalate',
            'Patent cliffs on key drugs 2026-2027',
            'Sector rotation out of healthcare'
        ],
        'entry_conditions': [
            'RSI <50 for better entry',
            'Holding 50-day MA support',
            'Healthcare sector not oversold'
        ]
    },
    {
        'ticker': 'PG',
        'strategy': 'Consumer Staples',
        'action': 'BUY',
        'entry_price': 165.00,
        'target_price': 178.00,
        'stop_loss': 160.00,
        'position_size': 10.0,
        'composite_score': 28.5,
        'confidence': 70.0,
        'signal_count': 4,
        'priority_score': 65.0,
        'thesis': 'Stable consumer staples with pricing power. 2.6% dividend, 68 consecutive years of dividend increases.',
        'catalyst': 'Q1 earnings October 18. Margin expansion from cost cuts, pricing holding despite volume softness.',
        'risks': [
            'Consumer spending slowdown',
            'Private label competition increasing',
            'Currency headwinds from strong dollar'
        ],
        'entry_conditions': [
            'Price pullback to $163-165 range',
            'Consumer sentiment stable',
            'Dollar not surging'
        ]
    },
    {
        'ticker': 'VZ',
        'strategy': 'Dividend Income',
        'action': 'BUY',
        'entry_price': 40.50,
        'target_price': 45.00,
        'stop_loss': 38.00,
        'position_size': 8.0,
        'composite_score': 22.1,
        'confidence': 65.0,
        'signal_count': 3,
        'priority_score': 58.0,
        'thesis': '6.8% dividend yield, trading near 52-week lows. Wireless subscriber growth stable, 5G monetization beginning.',
        'catalyst': 'Spectrum auction results positive. Fiber expansion ahead of schedule. FCF improving.',
        'risks': [
            'Continued subscriber churn',
            'Heavy debt load limits flexibility',
            'Competition from T-Mobile intensifying'
        ],
        'entry_conditions': [
            'Yield >6.5% for entry',
            'Telecom sector not in freefall',
            'Interest rates stabilizing'
        ]
    },
    {
        'ticker': 'COST',
        'strategy': 'Quality Growth',
        'action': 'BUY',
        'entry_price': 560.00,
        'target_price': 620.00,
        'stop_loss': 535.00,
        'position_size': 9.0,
        'composite_score': 38.7,
        'confidence': 78.0,
        'signal_count': 5,
        'priority_score': 72.0,
        'thesis': 'Best-in-class retail with pricing power. Membership renewal rates >90%, comp store sales +5-6%.',
        'catalyst': 'Q1 earnings December 12. Membership fee increase expected 2026 (+10% earnings boost).',
        'risks': [
            'Valuation at 42x P/E (premium)',
            'Consumer spending slowdown risk',
            'Amazon competition in grocery'
        ],
        'entry_conditions': [
            'Wait for pullback below $565',
            'Retail sector showing strength',
            'Consumer spending data positive'
        ]
    }
]


async def main():
    """Generate example report"""
    print("=" * 80)
    print("Generating Example Daily Pre-Market Report")
    print("=" * 80)
    print()

    # Generate report
    report = await generate_daily_report(
        shorgan_recs=SHORGAN_RECOMMENDATIONS,
        dee_recs=DEE_RECOMMENDATIONS,
        api_client=None  # No API client for demo
    )

    # Save to file
    output_file = 'examples/EXAMPLE_DAILY_PREMARKET_REPORT.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ Report generated successfully!")
    print(f"📄 Saved to: {output_file}")
    print()
    print("Report Preview (first 2000 characters):")
    print("-" * 80)
    print(report[:2000])
    print("-" * 80)
    print(f"... ({len(report)} total characters)")
    print()
    print("✅ Example generation complete!")


if __name__ == '__main__':
    asyncio.run(main())
