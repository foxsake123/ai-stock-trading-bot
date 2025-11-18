"""
Diagnostic script to test SHORGAN-BOT file save bug
Generates ONLY SHORGAN-BOT research with verbose logging
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.automation.claude_research_generator import ClaudeResearchGenerator

def main():
    print("="*70)
    print("SHORGAN-BOT FILE SAVE DIAGNOSTIC TEST")
    print("="*70)
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}\n")

    # Initialize generator
    generator = ClaudeResearchGenerator()

    # Calculate week number
    start_date = datetime(2025, 9, 1)
    days_elapsed = (datetime.now() - start_date).days
    week_number = (days_elapsed // 7) + 1

    bot_name = "SHORGAN-BOT"

    try:
        print(f"\n{'='*70}")
        print(f"STEP 1: GENERATE RESEARCH REPORT FOR {bot_name}")
        print(f"{'='*70}\n")

        report, portfolio_data = generator.generate_research_report(
            bot_name=bot_name,
            week_number=week_number,
            include_market_data=True
        )

        print(f"\n[+] Research generated successfully!")
        print(f"    Report length: {len(report):,} characters")
        print(f"    Portfolio data keys: {list(portfolio_data.keys()) if portfolio_data else 'None'}")

        print(f"\n{'='*70}")
        print(f"STEP 2: SAVE REPORT TO FILESYSTEM")
        print(f"{'='*70}\n")

        # Calculate expected paths
        tomorrow = datetime.now() + timedelta(days=1)
        date_str = tomorrow.strftime("%Y-%m-%d")
        bot_slug = bot_name.lower().replace("-", "_")

        print(f"[*] Date string: {date_str}")
        print(f"[*] Bot slug: {bot_slug}")
        print(f"[*] Expected directory: reports/premarket/{date_str}")
        print(f"[*] Expected filename (MD): claude_research_{bot_slug}_{date_str}.md")
        print(f"[*] Expected filename (PDF): claude_research_{bot_slug}_{date_str}.pdf\n")

        # Save with verbose output
        print(f"[*] Calling save_report()...")
        md_path, pdf_path = generator.save_report(
            report=report,
            bot_name=bot_name,
            portfolio_data=portfolio_data,
            export_pdf=True
        )

        print(f"\n[+] save_report() completed successfully!")
        print(f"    Returned MD path: {md_path}")
        print(f"    Returned PDF path: {pdf_path}")

        print(f"\n{'='*70}")
        print(f"STEP 3: VERIFY FILES EXIST ON FILESYSTEM")
        print(f"{'='*70}\n")

        # Check if files actually exist
        md_exists = os.path.exists(md_path)
        pdf_exists = os.path.exists(pdf_path) if pdf_path else False

        print(f"[*] Checking markdown file: {md_path}")
        print(f"    Exists: {md_exists}")
        if md_exists:
            md_size = os.path.getsize(md_path)
            print(f"    Size: {md_size:,} bytes")
            print(f"    ✅ MARKDOWN FILE EXISTS!")
        else:
            print(f"    ❌ MARKDOWN FILE MISSING!")

        print(f"\n[*] Checking PDF file: {pdf_path}")
        print(f"    Exists: {pdf_exists}")
        if pdf_exists:
            pdf_size = os.path.getsize(pdf_path)
            print(f"    Size: {pdf_size:,} bytes")
            print(f"    ✅ PDF FILE EXISTS!")
        else:
            print(f"    ❌ PDF FILE MISSING!")

        print(f"\n{'='*70}")
        print(f"STEP 4: LIST ALL FILES IN TARGET DIRECTORY")
        print(f"{'='*70}\n")

        target_dir = Path(f"reports/premarket/{date_str}")
        if target_dir.exists():
            print(f"[*] Directory contents: {target_dir}")
            for file in sorted(target_dir.iterdir()):
                size = file.stat().st_size if file.is_file() else 0
                print(f"    {file.name} ({size:,} bytes)")
        else:
            print(f"    ❌ Directory does not exist: {target_dir}")

        print(f"\n{'='*70}")
        print(f"DIAGNOSTIC SUMMARY")
        print(f"{'='*70}\n")

        if md_exists and pdf_exists:
            print(f"✅ TEST PASSED: Both files saved successfully!")
            print(f"    The bug did NOT reproduce in this test.")
        elif not md_exists and not pdf_exists:
            print(f"❌ TEST FAILED: Both files missing!")
            print(f"    BUG REPRODUCED: Files claimed saved but don't exist")
        elif md_exists and not pdf_exists:
            print(f"⚠️ PARTIAL FAILURE: Markdown exists but PDF missing")
            print(f"    PDF generation may have failed")
        else:
            print(f"⚠️ WEIRD: PDF exists but markdown missing")
            print(f"    Unexpected state!")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

        print(f"\n[!] Exception occurred during test")
        print(f"[!] This may explain why files are not being saved")

    print(f"\n{'='*70}")
    print(f"TEST COMPLETE")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
