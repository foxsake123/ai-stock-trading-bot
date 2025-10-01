"""
Complete Automated Trading Pipeline
====================================
Full end-to-end automation from research to execution.

Pipeline:
1. Generate Claude deep research (6 PM evening before)
2. Validate through multi-agent consensus (9:00 AM)
3. Execute approved trades (9:30 AM market open)
4. Monitor fills and send notifications

Author: AI Trading Bot System
Date: September 30, 2025
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import time

sys.path.append(str(Path(__file__).parent))

from daily_claude_research import should_generate_report, get_next_market_day
from consensus_validator import ConsensusValidator
from auto_executor import AutoExecutor


def run_research_generation():
    """Step 1: Generate Claude research reports"""
    print("\n" + "="*70)
    print("STEP 1: CLAUDE DEEP RESEARCH GENERATION")
    print("="*70 + "\n")

    should_run, next_trading_day, reason = should_generate_report()
    print(f"[*] {reason}")

    if not should_run:
        print("[!] Skipping research generation")
        return False

    # Import and run the daily research script
    from daily_claude_research import main as research_main
    research_main()

    return True


def run_consensus_validation(date_str: str):
    """Step 2: Validate trades through consensus"""
    print("\n" + "="*70)
    print("STEP 2: MULTI-AGENT CONSENSUS VALIDATION")
    print("="*70 + "\n")

    execution_plans = []

    for bot_name in ["DEE-BOT", "SHORGAN-BOT"]:
        bot_slug = bot_name.lower().replace("-", "_")
        report_dir = Path("scripts-and-data/data/reports/weekly/claude-research")
        report_file = report_dir / f"claude_research_{bot_slug}_{date_str}.md"

        if not report_file.exists():
            print(f"[!] Report not found for {bot_name}: {report_file}")
            continue

        # Validate trades
        validator = ConsensusValidator(bot_name)
        results = validator.validate_all(report_file)

        # Save execution plan
        output_dir = Path("scripts-and-data/data/execution-plans")
        plan_path = validator.save_execution_plan(results, output_dir)

        if results['execution_ready']:
            execution_plans.append((bot_name, plan_path))

    return execution_plans


def run_trade_execution(execution_plans: list):
    """Step 3: Execute approved trades"""
    print("\n" + "="*70)
    print("STEP 3: AUTOMATED TRADE EXECUTION")
    print("="*70 + "\n")

    execution_results = []

    for bot_name, plan_path in execution_plans:
        print(f"\n[*] Executing trades for {bot_name}...")

        executor = AutoExecutor(bot_name)
        summary = executor.execute_plan(plan_path)

        execution_results.append((bot_name, summary))

        time.sleep(2)  # Brief pause between bots

    return execution_results


def generate_final_report(execution_results: list):
    """Step 4: Generate final summary report"""
    print("\n" + "="*70)
    print("FINAL EXECUTION SUMMARY")
    print("="*70 + "\n")

    total_trades = 0
    total_filled = 0

    for bot_name, summary in execution_results:
        total_trades += summary['total_trades']
        total_filled += summary['filled']

        print(f"{bot_name}:")
        print(f"  Total: {summary['total_trades']}")
        print(f"  Filled: {summary['filled']}")
        print(f"  Fill Rate: {summary['filled']/summary['total_trades']*100:.1f}%" if summary['total_trades'] > 0 else "  Fill Rate: N/A")
        print()

    print(f"OVERALL:")
    print(f"  Total Trades: {total_trades}")
    print(f"  Total Filled: {total_filled}")
    print(f"  Combined Fill Rate: {total_filled/total_trades*100:.1f}%" if total_trades > 0 else "  Fill Rate: N/A")
    print()

    print("="*70)


def main():
    """Main orchestration function"""
    import argparse

    parser = argparse.ArgumentParser(description="Complete automated trading pipeline")
    parser.add_argument(
        "--mode",
        choices=["research", "validate", "execute", "full"],
        default="full",
        help="Pipeline mode to run"
    )
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Date for operations (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate without actual execution"
    )

    args = parser.parse_args()

    print("\n" + "="*70)
    print("COMPLETE AUTOMATED TRADING PIPELINE")
    print("="*70)
    print(f"Mode: {args.mode.upper()}")
    print(f"Date: {args.date}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    if args.dry_run:
        print("DRY RUN: No actual trades will be placed")
    print("="*70)

    # Execute pipeline based on mode
    if args.mode in ["research", "full"]:
        generated = run_research_generation()
        if not generated and args.mode == "full":
            print("\n[!] No research generated, stopping pipeline")
            return

    if args.mode in ["validate", "full"]:
        execution_plans = run_consensus_validation(args.date)
        if not execution_plans:
            print("\n[!] No execution plans created, stopping pipeline")
            return

    if args.mode in ["execute", "full"]:
        # For execute-only mode, load existing plans
        if args.mode == "execute":
            execution_plans = []
            for bot_name in ["DEE-BOT", "SHORGAN-BOT"]:
                bot_slug = bot_name.lower().replace("-", "_")
                plan_dir = Path("scripts-and-data/data/execution-plans")
                plan_file = plan_dir / f"execution_plan_{bot_slug}_{args.date}.json"

                if plan_file.exists():
                    execution_plans.append((bot_name, plan_file))

        if not execution_plans:
            print("\n[!] No execution plans found")
            return

        if args.dry_run:
            print("\n[DRY RUN] Would execute the following plans:")
            for bot_name, plan_path in execution_plans:
                print(f"  - {bot_name}: {plan_path}")
            return

        execution_results = run_trade_execution(execution_plans)
        generate_final_report(execution_results)

    print("\n" + "="*70)
    print("PIPELINE COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
