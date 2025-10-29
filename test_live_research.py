"""Test SHORGAN-BOT-LIVE research generation"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "scripts" / "automation"))

from claude_research_generator import ClaudeResearchGenerator

# Test that we can generate research for live account
gen = ClaudeResearchGenerator()

print("Testing SHORGAN-BOT-LIVE research generation...")
print("This will take 3-5 minutes (Claude deep research mode)\n")

try:
    # Generate live account research
    report, portfolio_data = gen.generate_research_report(
        bot_name="SHORGAN-BOT-LIVE",
        week_number=9,
        include_market_data=True
    )

    print(f"\n{'='*70}")
    print("SUCCESS: SHORGAN-BOT-LIVE research generated")
    print(f"{'='*70}")
    print(f"Report length: {len(report)} characters")
    print(f"Report lines: {report.count(chr(10))} lines")
    print(f"\nPortfolio data:")
    print(f"  Cash: ${portfolio_data.get('cash', 0):.2f}")
    print(f"  Portfolio Value: ${portfolio_data.get('portfolio_value', 0):.2f}")
    print(f"  Positions: {portfolio_data.get('position_count', 0)}")

    # Save the report
    md_path, pdf_path = gen.save_report(
        report=report,
        bot_name="SHORGAN-BOT-LIVE",
        portfolio_data=portfolio_data,
        export_pdf=True
    )

    print(f"\nReport saved:")
    print(f"  Markdown: {md_path}")
    print(f"  PDF: {pdf_path}")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
