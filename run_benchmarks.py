"""
Wrapper script to run Phase 2 benchmarks with proper encoding handling.

This script ensures Unicode characters display correctly on Windows.
"""

import sys
import os
import asyncio

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run benchmarks
from benchmarks.phase2_benchmarks import run_all_benchmarks

if __name__ == "__main__":
    print("=" * 80)
    print("PHASE 2 PERFORMANCE BENCHMARKS")
    print("=" * 80)
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Encoding: {sys.stdout.encoding}")
    print()

    try:
        report = asyncio.run(run_all_benchmarks())
        print("\n[SUCCESS] Benchmarks completed successfully!")
        print(f"Report saved to: benchmarks/reports/")
    except KeyboardInterrupt:
        print("\n[CANCELLED] Benchmarks cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Benchmarks failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
