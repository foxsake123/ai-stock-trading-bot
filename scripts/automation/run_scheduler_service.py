#!/usr/bin/env python3
"""
Background Scheduler Service for AI Trading Research
Runs continuously and executes research generation at 6:00 PM ET daily

Usage:
    python scripts/automation/run_scheduler_service.py

This is an alternative to Task Scheduler that doesn't require admin privileges.
"""

import schedule
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def run_research_generation():
    """Execute the daily research generation script"""
    script_path = project_root / "scripts" / "automation" / "daily_claude_research.py"

    print(f"\n{'='*70}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}] Starting research generation...")
    print(f"{'='*70}\n")

    try:
        # Run the research generation script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(project_root),
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ Research generation completed successfully!")
            print(result.stdout)
        else:
            print(f"❌ Research generation failed with exit code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")

    except Exception as e:
        print(f"❌ Error running research generation: {e}")

def main():
    """Main scheduler service"""
    print(f"\n{'='*70}")
    print("AI Trading Research Scheduler Service")
    print(f"{'='*70}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    print(f"Schedule: Daily at 6:00 PM ET")
    print(f"Press Ctrl+C to stop")
    print(f"{'='*70}\n")

    # Schedule the job for 6:00 PM ET daily
    schedule.every().day.at("18:00").do(run_research_generation)

    # Also show next scheduled time
    next_run = schedule.next_run()
    print(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %I:%M %p ET')}\n")

    # Run continuously
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    except KeyboardInterrupt:
        print("\n\n⚠️  Scheduler service stopped by user")
        print("Research generation will not run automatically until service is restarted")
        sys.exit(0)

if __name__ == "__main__":
    # Check if schedule module is installed
    try:
        import schedule
    except ImportError:
        print("❌ Error: 'schedule' module not found")
        print("Install it with: pip install schedule")
        sys.exit(1)

    main()
