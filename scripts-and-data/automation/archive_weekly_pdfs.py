#!/usr/bin/env python3
"""
Simple Weekly PDF Archiver
Archives ChatGPT deep research PDFs to organized folders
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import sys

class WeeklyPDFArchiver:
    def __init__(self):
        # Define paths
        self.upload_folder = Path("../../weekly-uploads")
        self.archive_folder = Path("../../docs/index/reports-pdf/weekly")
        self.upload_folder.mkdir(parents=True, exist_ok=True)
        self.archive_folder.mkdir(parents=True, exist_ok=True)

    def archive_pdf(self, pdf_path):
        """Archive a single PDF to the appropriate weekly folder"""
        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            print(f"Error: File not found - {pdf_path}")
            return False

        # Determine week folder
        week_str = f"Week_{datetime.now().strftime('%Y_W%U')}"
        week_folder = self.archive_folder / week_str
        week_folder.mkdir(exist_ok=True)

        # Determine bot type from filename
        filename_lower = pdf_file.name.lower()
        if 'dee' in filename_lower or 'defensive' in filename_lower:
            bot_type = 'dee-bot'
        elif 'shorgan' in filename_lower or 'catalyst' in filename_lower:
            bot_type = 'shorgan-bot'
        else:
            bot_type = 'combined'

        # Create destination filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest_name = f"{bot_type}_weekly_research_{timestamp}.pdf"
        dest_path = week_folder / dest_name

        # Copy file
        shutil.copy2(pdf_file, dest_path)
        print(f"Archived: {pdf_file.name} -> {dest_path}")

        # Also create a "latest" copy for easy access
        latest_name = f"{bot_type}_weekly_latest.pdf"
        latest_path = self.archive_folder / latest_name
        shutil.copy2(pdf_file, latest_path)
        print(f"Updated latest: {latest_path}")

        return True

    def process_upload_folder(self):
        """Process all PDFs in the upload folder"""
        print("\nChecking upload folder for PDFs...")

        pdf_files = list(self.upload_folder.glob("*.pdf"))

        if not pdf_files:
            print(f"No PDFs found in {self.upload_folder}")
            print("\nTo upload PDFs, place them in:")
            print(f"  {self.upload_folder.absolute()}")
            return 0

        archived_count = 0
        for pdf_file in pdf_files:
            print(f"\nProcessing: {pdf_file.name}")
            if self.archive_pdf(pdf_file):
                # Move to processed folder after successful archive
                processed_folder = self.upload_folder / "processed"
                processed_folder.mkdir(exist_ok=True)
                shutil.move(str(pdf_file), str(processed_folder / pdf_file.name))
                archived_count += 1

        return archived_count

    def create_index_file(self):
        """Create an index of all archived weekly PDFs"""
        index_file = self.archive_folder / "index.md"

        with open(index_file, 'w') as f:
            f.write("# Weekly Deep Research PDFs Index\n\n")
            f.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # List all week folders
            week_folders = sorted([d for d in self.archive_folder.iterdir() if d.is_dir()])

            for week_folder in reversed(week_folders):  # Most recent first
                f.write(f"\n## {week_folder.name.replace('_', ' ')}\n\n")

                # List PDFs in this week
                pdfs = sorted(week_folder.glob("*.pdf"))
                if pdfs:
                    for pdf in pdfs:
                        f.write(f"- [{pdf.name}]({pdf.name})\n")
                else:
                    f.write("- No PDFs archived yet\n")

            # List latest files
            f.write("\n## Latest Reports\n\n")
            latest_files = self.archive_folder.glob("*_latest.pdf")
            for latest in latest_files:
                f.write(f"- [{latest.name}]({latest.name})\n")

        print(f"\nIndex updated: {index_file}")

def main():
    """Main execution"""
    print("=" * 60)
    print("WEEKLY PDF ARCHIVER")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    archiver = WeeklyPDFArchiver()

    # Check for command line arguments
    if len(sys.argv) > 1:
        # Archive specific file(s)
        for pdf_path in sys.argv[1:]:
            archiver.archive_pdf(pdf_path)
    else:
        # Process upload folder
        archived = archiver.process_upload_folder()
        print(f"\nArchived {archived} PDF(s)")

    # Update index
    archiver.create_index_file()

    print("\n" + "=" * 60)
    print("ARCHIVING COMPLETE")
    print("=" * 60)

    print("\nUsage:")
    print("1. Place PDFs in: weekly-uploads/")
    print("2. Run: python archive_weekly_pdfs.py")
    print("   OR")
    print("   python archive_weekly_pdfs.py path/to/file.pdf")

if __name__ == "__main__":
    main()