#!/usr/bin/env python3
"""
Generate SHORGAN-BOT-LIVE research report only
"""
import sys
import os

# Add the automation directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from claude_research_generator import ClaudeResearchGenerator

def main():
    print("="*70)
    print("GENERATING SHORGAN-BOT-LIVE RESEARCH REPORT")
    print("="*70)

    generator = ClaudeResearchGenerator()

    try:
        # Generate report
        report, portfolio_data = generator.generate_research_report(
            bot_name='SHORGAN-BOT-LIVE',
            week_number=6,
            include_market_data=True
        )

        print(f"\n[+] Report generated: {len(report)} characters")

        # Save the report
        md_path, pdf_path = generator.save_report(
            report=report,
            bot_name='SHORGAN-BOT-LIVE',
            portfolio_data=portfolio_data,
            export_pdf=True
        )

        print(f"\n[+] Files saved:")
        print(f"    Markdown: {md_path}")
        print(f"    PDF: {pdf_path}")

    except Exception as e:
        import traceback
        print(f"\n[-] Error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
