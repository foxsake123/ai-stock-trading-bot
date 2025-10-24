#!/usr/bin/env python3
"""
AI Trading Bot - Daily Pipeline
Main automation entry point for daily trading operations

Schedule: Runs at 6:00 AM ET on market days
Duration: ~90 minutes (6:00 AM - 7:30 AM)

Pipeline Phases:
1. Data Collection (6:00-6:15): Fetch market data, news, sentiment, alternative data
2. Agent Analysis (6:15-6:45): 7-agent council analyzes opportunities
3. Debate Phase (6:45-7:00): Bull/Bear debates for high-confidence trades
4. Strategy Allocation (7:00-7:15): Assign trades to DEE-BOT and SHORGAN-BOT
5. Report Generation (7:15-7:30): Generate pre-market reports
6. Notifications (7:30): Send alerts via Telegram/Email/Slack
7. Intraday Monitoring (7:30-9:30): Monitor catalysts until market open

Author: AI Trading Bot Team
Last Updated: 2025-10-23
"""

import asyncio
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import traceback
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import utilities
from src.utils.market_hours import MarketHours, should_run_pipeline
from src.utils.logger import setup_logging
from src.utils.config_loader import load_config
from src.utils.performance_tracker import PerformanceTracker

# Import components
from src.data.alternative_data_aggregator import AlternativeDataAggregator
from src.agents.agent_council import AgentCouncil
from src.agents.debate_orchestrator import DebateOrchestrator
from src.strategies.strategy_manager import StrategyManager
from src.reports.premarket_report import PreMarketReport
from src.alerts.alert_manager import AlertManager
from src.monitors.catalyst_monitor import CatalystMonitor
from src.monitors.health_check import HealthMonitor


# ============================================================================
# LOGGING SETUP
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# DAILY PIPELINE ORCHESTRATOR
# ============================================================================

class DailyPipeline:
    """
    Main daily trading pipeline orchestrator

    Coordinates all phases of the daily trading workflow from data collection
    through report generation and notification delivery.
    """

    def __init__(self, config_path: str = "configs/config.yaml"):
        """
        Initialize daily pipeline

        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.start_time = datetime.now()

        # Initialize components
        self.market_hours = MarketHours()
        self.health_monitor = HealthMonitor(self.config)
        self.alert_manager = AlertManager(self.config)
        self.perf_tracker = PerformanceTracker()

        # Phase tracking
        self.errors = []
        self.phase_results = {}
        self.pipeline_metrics = {
            'start_time': self.start_time.isoformat(),
            'phases': {}
        }

    async def run(self) -> bool:
        """
        Execute complete daily pipeline

        Returns:
            bool: True if pipeline completed successfully
        """
        try:
            logger.info("=" * 80)
            logger.info("AI TRADING BOT - DAILY PIPELINE")
            logger.info("=" * 80)
            logger.info(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S ET')}")

            # Log market status
            self.market_hours.log_market_status()

            # Check if pipeline should run
            should_run, reason = should_run_pipeline()
            if not should_run:
                logger.warning(f"Pipeline execution skipped: {reason}")
                await self.alert_manager.send_info_alert(
                    "Pipeline Skipped",
                    f"Daily pipeline not executed: {reason}"
                )
                return False

            logger.info(f"Pipeline execution authorized: {reason}")
            logger.info("=" * 80)

            # Pre-flight checks
            logger.info("\nRunning pre-flight checks...")
            if not await self.pre_flight_checks():
                logger.error("Pre-flight checks failed. Aborting pipeline.")
                await self.alert_manager.send_critical_alert(
                    "Pipeline Aborted - Pre-Flight Failure",
                    "Pre-flight health checks failed. Check logs for details."
                )
                return False

            # Execute pipeline phases
            phases = [
                ("Phase 1: Data Collection", "6:00-6:15", self.phase_1_data_collection),
                ("Phase 2: Agent Analysis", "6:15-6:45", self.phase_2_agent_analysis),
                ("Phase 3: Bull/Bear Debates", "6:45-7:00", self.phase_3_debate_phase),
                ("Phase 4: Strategy Allocation", "7:00-7:15", self.phase_4_strategy_allocation),
                ("Phase 5: Report Generation", "7:15-7:30", self.phase_5_report_generation),
                ("Phase 6: Notifications", "7:30", self.phase_6_notifications),
                ("Phase 7: Intraday Monitoring", "7:30+", self.phase_7_start_monitoring),
            ]

            for phase_name, time_window, phase_func in phases:
                success = await self.execute_phase(phase_name, time_window, phase_func)

                # Check if we should halt on error
                if not success:
                    if self.config.get('system', {}).get('emergency', {}).get('auto_close_on_error', False):
                        logger.error(f"Phase '{phase_name}' failed. Emergency stop enabled.")
                        await self.alert_manager.send_critical_alert(
                            "Pipeline Halted",
                            f"Phase '{phase_name}' failed and auto_close_on_error is enabled."
                        )
                        return False
                    else:
                        logger.warning(f"Phase '{phase_name}' failed but continuing pipeline...")

            # Pipeline completed successfully
            await self.pipeline_complete()
            return True

        except KeyboardInterrupt:
            logger.warning("Pipeline interrupted by user")
            await self.alert_manager.send_warning_alert(
                "Pipeline Interrupted",
                "Daily pipeline was manually interrupted"
            )
            return False

        except Exception as e:
            logger.critical(f"CRITICAL ERROR in pipeline: {e}")
            logger.critical(traceback.format_exc())
            await self.alert_manager.send_critical_alert(
                "Pipeline Crash",
                f"Unhandled exception: {str(e)}\n\n{traceback.format_exc()}"
            )
            return False

    async def pre_flight_checks(self) -> bool:
        """
        Run pre-flight health checks before starting pipeline

        Returns:
            bool: True if all critical checks pass
        """
        checks = [
            ("Market Status", self.check_market_status),
            ("API Connectivity", self.health_monitor.check_api_connectivity),
            ("Data Sources", self.health_monitor.check_data_sources),
            ("Disk Space", self.health_monitor.check_disk_space),
            ("Kill Switch", self.check_kill_switch),
        ]

        all_passed = True
        critical_failed = False

        for check_name, check_func in checks:
            try:
                result = await check_func()
                status = "PASS" if result else "FAIL"
                logger.info(f"  [{status}] {check_name}")

                if not result:
                    all_passed = False
                    # Market Status and Kill Switch are critical
                    if check_name in ["Market Status", "Kill Switch"]:
                        critical_failed = True

            except Exception as e:
                logger.error(f"  [ERROR] {check_name}: {e}")
                all_passed = False

        if critical_failed:
            return False

        if not all_passed:
            logger.warning("Some non-critical checks failed, but proceeding...")

        return True

    async def check_market_status(self) -> bool:
        """Check if today is a valid market day"""
        return self.market_hours.is_market_day()

    async def check_kill_switch(self) -> bool:
        """Check if emergency kill switch is activated"""
        kill_switch_file = PROJECT_ROOT / "data" / "state" / "kill_switch.flag"

        if kill_switch_file.exists():
            logger.error("KILL SWITCH ACTIVATED - Pipeline halted")
            return False

        return True

    async def execute_phase(self, phase_name: str, time_window: str, phase_func) -> bool:
        """
        Execute a single pipeline phase with comprehensive error handling

        Args:
            phase_name: Name of the phase
            time_window: Expected time window (e.g., "6:00-6:15")
            phase_func: Async function to execute

        Returns:
            bool: True if phase completed successfully
        """
        logger.info(f"\n{'=' * 80}")
        logger.info(f"{phase_name} ({time_window})")
        logger.info(f"Started: {datetime.now().strftime('%H:%M:%S ET')}")
        logger.info(f"{'=' * 80}")

        phase_start = datetime.now()
        self.perf_tracker.start_timer(phase_name)

        try:
            # Execute phase
            result = await phase_func()

            # Record metrics
            duration = (datetime.now() - phase_start).total_seconds()
            self.perf_tracker.stop_timer(phase_name)

            self.phase_results[phase_name] = {
                'success': True,
                'duration_seconds': duration,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }

            self.pipeline_metrics['phases'][phase_name] = {
                'status': 'success',
                'duration_seconds': duration,
                'timestamp': datetime.now().isoformat()
            }

            logger.info(f"\n[SUCCESS] {phase_name} completed in {duration:.1f}s")
            logger.info(f"{'=' * 80}\n")

            return True

        except Exception as e:
            duration = (datetime.now() - phase_start).total_seconds()
            error_msg = f"{phase_name} failed: {str(e)}"

            self.errors.append({
                'phase': phase_name,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            })

            self.phase_results[phase_name] = {
                'success': False,
                'duration_seconds': duration,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

            self.pipeline_metrics['phases'][phase_name] = {
                'status': 'failed',
                'duration_seconds': duration,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

            logger.error(f"\n[FAILED] {error_msg}")
            logger.error(traceback.format_exc())
            logger.info(f"{'=' * 80}\n")

            # Send alert about phase failure
            await self.alert_manager.send_error_alert(
                f"Phase Failed: {phase_name}",
                f"{error_msg}\n\nDuration: {duration:.1f}s"
            )

            return False

    # ========================================================================
    # PHASE 1: DATA COLLECTION (6:00-6:15)
    # ========================================================================

    async def phase_1_data_collection(self) -> Dict:
        """
        Collect all required data for analysis

        Uses AlternativeDataAggregator to fetch:
        - Market data (prices, volumes)
        - News and catalysts
        - Sentiment data (Reddit, Twitter)
        - Alternative data (options flow, insider trading, dark pool)
        - Watchlist data

        Returns:
            Dict with collected data organized by source
        """
        logger.info("Initializing data collection...")

        aggregator = AlternativeDataAggregator(self.config)

        # Collect data concurrently for performance
        logger.info("Fetching data from all sources...")

        tasks = {
            'market_data': aggregator.fetch_market_data(),
            'news': aggregator.fetch_news(),
            'sentiment': aggregator.fetch_sentiment(),
            'alternative_data': aggregator.fetch_alternative_data(),
            'watchlist': aggregator.fetch_watchlist_data(),
        }

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        # Map results back to sources
        data = {}
        errors_found = []

        for i, (source_name, _) in enumerate(tasks.items()):
            if isinstance(results[i], Exception):
                logger.error(f"  [ERROR] {source_name}: {results[i]}")
                errors_found.append(f"{source_name}: {results[i]}")
                data[source_name] = None
            else:
                data[source_name] = results[i]
                count = len(results[i]) if isinstance(results[i], (list, dict)) else "N/A"
                logger.info(f"  [OK] {source_name}: {count} items")

        if errors_found:
            logger.warning(f"Data collection had {len(errors_found)} errors:")
            for error in errors_found:
                logger.warning(f"  - {error}")

        logger.info(f"Data collection complete: {len([d for d in data.values() if d is not None])}/{len(data)} sources successful")

        return data

    # ========================================================================
    # PHASE 2: AGENT ANALYSIS (6:15-6:45)
    # ========================================================================

    async def phase_2_agent_analysis(self) -> List[Dict]:
        """
        Run 7-agent council to analyze opportunities

        Agents:
        1. FundamentalAnalyst - Financial metrics, valuations
        2. TechnicalAnalyst - Charts, indicators, entry points
        3. NewsAnalyst - Catalyst validation
        4. SentimentAnalyst - Market sentiment
        5. BullResearcher - Upside case
        6. BearResearcher - Downside risks
        7. RiskManager - Position sizing, risk assessment

        Returns:
            List of trade recommendations with consensus scores
        """
        logger.info("Initializing 7-agent council...")

        council = AgentCouncil(self.config)

        # Get data from Phase 1
        data = self.phase_results.get('Phase 1: Data Collection', {}).get('result', {})

        if not data:
            raise ValueError("No data available from Phase 1")

        # Run all agents in parallel
        logger.info("Running multi-agent analysis...")
        recommendations = await council.analyze_opportunities(data)

        # Log summary
        logger.info(f"\nAgent Analysis Summary:")
        logger.info(f"  Total opportunities identified: {len(recommendations)}")

        if recommendations:
            high_conf = len([r for r in recommendations if r.get('consensus_confidence', 0) >= 0.60])
            medium_conf = len([r for r in recommendations if 0.50 <= r.get('consensus_confidence', 0) < 0.60])
            low_conf = len([r for r in recommendations if r.get('consensus_confidence', 0) < 0.50])

            logger.info(f"  High confidence (>=60%): {high_conf}")
            logger.info(f"  Medium confidence (50-60%): {medium_conf}")
            logger.info(f"  Low confidence (<50%): {low_conf}")

            # Log top 5 recommendations
            sorted_recs = sorted(recommendations, key=lambda x: x.get('consensus_confidence', 0), reverse=True)
            logger.info(f"\n  Top 5 Recommendations:")
            for i, rec in enumerate(sorted_recs[:5], 1):
                ticker = rec.get('ticker', 'N/A')
                action = rec.get('action', 'N/A')
                conf = rec.get('consensus_confidence', 0)
                logger.info(f"    {i}. {ticker} - {action} ({conf:.1%} confidence)")

        return recommendations

    # ========================================================================
    # PHASE 3: BULL/BEAR DEBATES (6:45-7:00)
    # ========================================================================

    async def phase_3_debate_phase(self) -> List[Dict]:
        """
        Run bull/bear debates for high-confidence recommendations

        For recommendations with consensus >= debate_threshold:
        - BullResearcher argues upside case
        - BearResearcher argues downside risks
        - Judge evaluates arguments
        - Consensus score adjusted +/- 5-10%

        Returns:
            List of recommendations with debate-adjusted scores
        """
        logger.info("Initializing debate orchestrator...")

        orchestrator = DebateOrchestrator(self.config)

        # Get recommendations from Phase 2
        recommendations = self.phase_results.get('Phase 2: Agent Analysis', {}).get('result', [])

        if not recommendations:
            logger.warning("No recommendations from Phase 2, skipping debates")
            return []

        # Filter high-confidence recommendations for debate
        debate_threshold = self.config.get('agents', {}).get('consensus', {}).get('debate_threshold', 0.60)

        candidates = [
            r for r in recommendations
            if r.get('consensus_confidence', 0) >= debate_threshold
        ]

        logger.info(f"Debate candidates: {len(candidates)} (threshold: {debate_threshold:.0%})")

        if not candidates:
            logger.info("No recommendations meet debate threshold, skipping debates")
            return recommendations  # Return original recommendations

        # Run debates
        logger.info("Running bull/bear debates...")
        debate_results = await orchestrator.run_debates(candidates)

        # Merge debate results back into original recommendations
        debated_tickers = {r['ticker'] for r in debate_results}

        final_recommendations = []
        for rec in recommendations:
            if rec['ticker'] in debated_tickers:
                # Find debated version
                debated = next((d for d in debate_results if d['ticker'] == rec['ticker']), rec)
                final_recommendations.append(debated)
            else:
                final_recommendations.append(rec)

        # Log debate summary
        logger.info(f"\nDebate Summary:")
        logger.info(f"  Debates conducted: {len(debate_results)}")

        for result in debate_results:
            ticker = result.get('ticker', 'N/A')
            old_conf = result.get('pre_debate_confidence', 0)
            new_conf = result.get('consensus_confidence', 0)
            change = new_conf - old_conf
            logger.info(f"  {ticker}: {old_conf:.1%} -> {new_conf:.1%} ({change:+.1%})")

        return final_recommendations

    # ========================================================================
    # PHASE 4: STRATEGY ALLOCATION (7:00-7:15)
    # ========================================================================

    async def phase_4_strategy_allocation(self) -> Dict:
        """
        Allocate recommendations to DEE-BOT and SHORGAN-BOT strategies

        DEE-BOT (Beta-Neutral):
        - Low beta stocks (<0.7)
        - Defensive positioning
        - Long-only

        SHORGAN-BOT (Catalyst-Driven):
        - High-conviction catalysts
        - Both long and short
        - Aggressive positioning

        Returns:
            Dict with allocations: {'dee_bot': [...], 'shorgan_bot': [...]}
        """
        logger.info("Initializing strategy manager...")

        manager = StrategyManager(self.config)

        # Get debate results from Phase 3
        recommendations = self.phase_results.get('Phase 3: Bull/Bear Debates', {}).get('result', [])

        if not recommendations:
            logger.warning("No recommendations from Phase 3, skipping allocation")
            return {'dee_bot': [], 'shorgan_bot': []}

        # Allocate trades
        logger.info("Allocating trades to strategies...")
        allocations = await manager.allocate_trades(recommendations)

        # Log allocation summary
        dee_count = len(allocations.get('dee_bot', []))
        shorgan_count = len(allocations.get('shorgan_bot', []))

        logger.info(f"\nStrategy Allocation Summary:")
        logger.info(f"  DEE-BOT (Beta-Neutral): {dee_count} positions")
        logger.info(f"  SHORGAN-BOT (Catalyst): {shorgan_count} positions")
        logger.info(f"  Total allocated: {dee_count + shorgan_count}")

        # Log position details
        if dee_count > 0:
            logger.info(f"\n  DEE-BOT Positions:")
            for pos in allocations['dee_bot'][:5]:
                logger.info(f"    - {pos.get('ticker')}: {pos.get('action')} ({pos.get('size')} shares)")

        if shorgan_count > 0:
            logger.info(f"\n  SHORGAN-BOT Positions:")
            for pos in allocations['shorgan_bot'][:5]:
                logger.info(f"    - {pos.get('ticker')}: {pos.get('action')} ({pos.get('size')} shares)")

        return allocations

    # ========================================================================
    # PHASE 5: REPORT GENERATION (7:15-7:30)
    # ========================================================================

    async def phase_5_report_generation(self) -> Dict:
        """
        Generate comprehensive pre-market reports

        Reports include:
        - Executive summary
        - Market overview
        - Strategy allocations (DEE-BOT, SHORGAN-BOT)
        - Individual agent analyses
        - Debate results
        - Risk metrics
        - Execution plan

        Returns:
            Dict with report file paths: {'markdown': ..., 'pdf': ..., 'json': ...}
        """
        logger.info("Initializing report generator...")

        generator = PreMarketReport(self.config)

        # Gather all pipeline data
        pipeline_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'data_collection': self.phase_results.get('Phase 1: Data Collection', {}).get('result', {}),
            'agent_analysis': self.phase_results.get('Phase 2: Agent Analysis', {}).get('result', []),
            'debate_results': self.phase_results.get('Phase 3: Bull/Bear Debates', {}).get('result', []),
            'allocations': self.phase_results.get('Phase 4: Strategy Allocation', {}).get('result', {}),
            'pipeline_metrics': self.pipeline_metrics,
        }

        # Generate reports in multiple formats
        logger.info("Generating reports...")
        reports = await generator.generate_reports(pipeline_data)

        logger.info(f"\nReports Generated:")
        for report_type, file_path in reports.items():
            size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
            logger.info(f"  - {report_type}: {file_path} ({size:,} bytes)")

        return reports

    # ========================================================================
    # PHASE 6: NOTIFICATIONS (7:30)
    # ========================================================================

    async def phase_6_notifications(self) -> bool:
        """
        Send notifications via configured channels

        Channels:
        - Telegram: PDF report + summary
        - Email: HTML report + attachments
        - Slack: Summary + link to reports

        Returns:
            bool: True if all notifications sent successfully
        """
        logger.info("Sending notifications...")

        # Get reports from Phase 5
        reports = self.phase_results.get('Phase 5: Report Generation', {}).get('result', {})

        if not reports:
            logger.warning("No reports available from Phase 5")
            return False

        # Get allocations for summary
        allocations = self.phase_results.get('Phase 4: Strategy Allocation', {}).get('result', {})

        # Send to each enabled channel
        tasks = []
        channels_enabled = []

        if self.config.get('alerts', {}).get('channels', {}).get('telegram', {}).get('enabled', False):
            tasks.append(self.alert_manager.send_telegram_report(reports, allocations))
            channels_enabled.append('Telegram')

        if self.config.get('alerts', {}).get('channels', {}).get('email', {}).get('enabled', False):
            tasks.append(self.alert_manager.send_email_report(reports, allocations))
            channels_enabled.append('Email')

        if self.config.get('alerts', {}).get('channels', {}).get('slack', {}).get('enabled', False):
            tasks.append(self.alert_manager.send_slack_report(reports, allocations))
            channels_enabled.append('Slack')

        if not tasks:
            logger.warning("No notification channels enabled")
            return True

        logger.info(f"Sending to {len(tasks)} channels: {', '.join(channels_enabled)}")

        # Send concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check results
        errors = [(channels_enabled[i], r) for i, r in enumerate(results) if isinstance(r, Exception)]

        if errors:
            logger.error(f"Failed to send to {len(errors)} channels:")
            for channel, error in errors:
                logger.error(f"  - {channel}: {error}")
            return False

        logger.info("All notifications sent successfully")
        return True

    # ========================================================================
    # PHASE 7: INTRADAY MONITORING (7:30-9:30)
    # ========================================================================

    async def phase_7_start_monitoring(self) -> bool:
        """
        Start intraday catalyst monitoring

        Monitors:
        - FDA approvals
        - Earnings releases
        - M&A announcements
        - Insider buying/selling
        - Options flow anomalies

        Runs in background until market open

        Returns:
            bool: True if monitoring started successfully
        """
        logger.info("Starting intraday catalyst monitor...")

        monitor = CatalystMonitor(self.config)

        # Get allocated positions to monitor
        allocations = self.phase_results.get('Phase 4: Strategy Allocation', {}).get('result', {})

        all_positions = []
        if allocations:
            all_positions.extend(allocations.get('dee_bot', []))
            all_positions.extend(allocations.get('shorgan_bot', []))

        tickers_to_monitor = [p.get('ticker') for p in all_positions]

        logger.info(f"Monitoring {len(tickers_to_monitor)} positions for catalysts")

        # Start monitoring (runs in background)
        await monitor.start(tickers_to_monitor)

        logger.info("Catalyst monitor started successfully")
        logger.info("Monitor will run until market open (9:30 AM ET)")

        return True

    # ========================================================================
    # PIPELINE COMPLETION
    # ========================================================================

    async def pipeline_complete(self):
        """Handle pipeline completion tasks"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() / 60

        self.pipeline_metrics['end_time'] = end_time.isoformat()
        self.pipeline_metrics['duration_minutes'] = duration
        self.pipeline_metrics['success'] = True
        self.pipeline_metrics['errors'] = self.errors

        # Save metrics
        metrics_file = PROJECT_ROOT / "logs" / "app" / f"pipeline_metrics_{datetime.now().strftime('%Y%m%d')}.json"
        with open(metrics_file, 'w') as f:
            json.dump(self.pipeline_metrics, f, indent=2)

        logger.info("=" * 80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Duration: {duration:.1f} minutes")
        logger.info(f"Phases completed: {len([p for p in self.phase_results.values() if p.get('success')])}/7")

        if self.errors:
            logger.warning(f"Errors encountered: {len(self.errors)}")

        logger.info(f"Metrics saved: {metrics_file}")
        logger.info("=" * 80)

        # Send completion notification
        await self.alert_manager.send_success_alert(
            "Daily Pipeline Complete",
            f"Pipeline completed successfully in {duration:.1f} minutes. Ready for market open at 9:30 AM ET."
        )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point for daily pipeline"""

    # Setup logging
    log_dir = PROJECT_ROOT / "logs" / "app"
    log_dir.mkdir(parents=True, exist_ok=True)

    setup_logging(
        log_dir=log_dir,
        log_file=f"daily_pipeline_{datetime.now().strftime('%Y%m%d')}.log",
        level=logging.INFO,
        log_to_console=True
    )

    logger.info("Daily Pipeline Starting...")

    # Run pipeline
    pipeline = DailyPipeline()
    success = await pipeline.run()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
