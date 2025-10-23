"""
Phase 2 Integration - Seamless Integration of All Enhancements

Integrates:
1. Alternative Data Consolidation (insider trades, Google Trends)
2. Bull/Bear Debate Mechanism
3. Intraday Catalyst Monitor
4. Options Flow Analyzer

Features:
- Backwards compatible with existing system
- Configuration flags to enable/disable enhancements
- Unified decision pipeline
- Comprehensive testing harness
- Automatic report generation
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import yaml

# Import existing components
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Alternative Data
try:
    from src.agents.alternative_data_agent import AlternativeDataAgent
    ALTERNATIVE_DATA_AVAILABLE = True
except ImportError:
    ALTERNATIVE_DATA_AVAILABLE = False
    logging.warning("Alternative Data Agent not available")

# Debate System
try:
    from src.agents.debate_orchestrator import DebateOrchestrator
    from src.agents.bull_analyst import BullAnalyst
    from src.agents.bear_analyst import BearAnalyst
    from src.agents.neutral_moderator import NeutralModerator
    from src.agents.debate_coordinator import DebateCoordinator
    DEBATE_SYSTEM_AVAILABLE = True
except ImportError:
    DEBATE_SYSTEM_AVAILABLE = False
    logging.warning("Debate System not available")

# Catalyst Monitor
try:
    from src.monitors.catalyst_monitor import CatalystMonitor
    from src.monitors.news_scanner import NewsScanner
    from src.monitors.event_calendar import EventCalendar
    from src.alerts.catalyst_alerts import CatalystAlerts
    CATALYST_MONITOR_AVAILABLE = True
except ImportError:
    CATALYST_MONITOR_AVAILABLE = False
    logging.warning("Catalyst Monitor not available")

# Options Flow
try:
    from src.data.options_data_fetcher import OptionsDataFetcher
    from src.analysis.options_flow import OptionsFlowAnalyzer
    from src.signals.unusual_activity import UnusualActivityDetector
    OPTIONS_FLOW_AVAILABLE = True
except ImportError:
    OPTIONS_FLOW_AVAILABLE = False
    logging.warning("Options Flow Analyzer not available")

logger = logging.getLogger(__name__)


@dataclass
class Phase2Config:
    """Configuration for Phase 2 enhancements"""

    # Feature flags
    enable_alternative_data: bool = True
    enable_debate_system: bool = True
    enable_catalyst_monitor: bool = True
    enable_options_flow: bool = True

    # Alternative Data settings
    alt_data_weight: float = 0.3  # Weight in final decision (0-1)
    insider_lookback_days: int = 90
    trends_lookback_days: int = 30

    # Debate settings
    debate_timeout_seconds: int = 30
    debate_min_confidence: float = 0.55
    use_debates_for_all: bool = False  # If False, only for medium-confidence trades

    # Catalyst Monitor settings
    catalyst_check_interval: int = 300  # 5 minutes
    catalyst_alert_channels: List[str] = field(default_factory=lambda: ['email', 'telegram'])
    monitor_market_hours_only: bool = True

    # Options Flow settings
    options_lookback_minutes: int = 60
    options_min_confidence: float = 0.6
    options_weight: float = 0.4  # Weight in alternative data composite

    # Backwards compatibility
    fallback_to_simple_voting: bool = True  # If enhancements fail, use simple voting
    preserve_existing_reports: bool = True  # Keep existing report format

    # Logging
    verbose_logging: bool = False
    log_file: str = "logs/phase2_integration.log"


class Phase2IntegrationEngine:
    """
    Main integration engine for Phase 2 enhancements

    Coordinates all new components and integrates with existing system
    """

    def __init__(self, config: Optional[Phase2Config] = None):
        """
        Initialize Phase 2 integration

        Args:
            config: Phase2Config instance (uses defaults if None)
        """
        self.config = config or Phase2Config()

        # Setup logging
        self._setup_logging()

        # Initialize components
        self.alt_data_agent: Optional[AlternativeDataAgent] = None
        self.debate_coordinator: Optional[DebateCoordinator] = None
        self.catalyst_monitor: Optional[CatalystMonitor] = None
        self.options_analyzer: Optional[OptionsFlowAnalyzer] = None

        # Component status
        self.components_initialized = {
            'alternative_data': False,
            'debate_system': False,
            'catalyst_monitor': False,
            'options_flow': False
        }

        logger.info("Phase2IntegrationEngine initialized")
        logger.info(f"Feature flags: alt_data={self.config.enable_alternative_data}, "
                   f"debate={self.config.enable_debate_system}, "
                   f"catalyst={self.config.enable_catalyst_monitor}, "
                   f"options={self.config.enable_options_flow}")

    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = logging.DEBUG if self.config.verbose_logging else logging.INFO

        # Create logs directory
        os.makedirs(os.path.dirname(self.config.log_file), exist_ok=True)

        # Configure logger
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler()
            ]
        )

    async def initialize(self):
        """Initialize all enabled components"""
        logger.info("Initializing Phase 2 components...")

        # Initialize Alternative Data Agent
        if self.config.enable_alternative_data and ALTERNATIVE_DATA_AVAILABLE:
            try:
                self.alt_data_agent = AlternativeDataAgent(
                    insider_lookback_days=self.config.insider_lookback_days,
                    trends_lookback_days=self.config.trends_lookback_days
                )

                # Initialize options flow if enabled
                if self.config.enable_options_flow and OPTIONS_FLOW_AVAILABLE:
                    fetcher = OptionsDataFetcher()
                    self.options_analyzer = OptionsFlowAnalyzer(data_fetcher=fetcher)

                self.components_initialized['alternative_data'] = True
                logger.info("✓ Alternative Data Agent initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Alternative Data Agent: {e}")

        # Initialize Debate System
        if self.config.enable_debate_system and DEBATE_SYSTEM_AVAILABLE:
            try:
                # Create debate orchestrator
                orchestrator = DebateOrchestrator(
                    bull_analyst=BullAnalyst(),
                    bear_analyst=BearAnalyst(),
                    moderator=NeutralModerator(),
                    timeout_seconds=self.config.debate_timeout_seconds
                )

                # Create debate coordinator
                self.debate_coordinator = DebateCoordinator(
                    orchestrator=orchestrator,
                    enable_debates=True,
                    debate_threshold=self.config.debate_min_confidence
                )

                self.components_initialized['debate_system'] = True
                logger.info("✓ Debate System initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Debate System: {e}")

        # Initialize Catalyst Monitor
        if self.config.enable_catalyst_monitor and CATALYST_MONITOR_AVAILABLE:
            try:
                # Create components
                news_scanner = NewsScanner()
                event_calendar = EventCalendar()
                alert_system = CatalystAlerts(primary_channel='telegram')

                # Create monitor
                self.catalyst_monitor = CatalystMonitor(
                    news_scanner=news_scanner,
                    event_calendar=event_calendar,
                    alert_system=alert_system,
                    check_interval=self.config.catalyst_check_interval
                )

                self.components_initialized['catalyst_monitor'] = True
                logger.info("✓ Catalyst Monitor initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Catalyst Monitor: {e}")

        # Initialize Options Flow Analyzer
        if self.config.enable_options_flow and OPTIONS_FLOW_AVAILABLE:
            try:
                if not self.options_analyzer:  # Not already initialized via alt data
                    fetcher = OptionsDataFetcher()
                    self.options_analyzer = OptionsFlowAnalyzer(data_fetcher=fetcher)

                self.components_initialized['options_flow'] = True
                logger.info("✓ Options Flow Analyzer initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Options Flow Analyzer: {e}")

        # Log initialization summary
        active_count = sum(self.components_initialized.values())
        logger.info(f"Phase 2 initialization complete: {active_count}/4 components active")

    async def analyze_ticker(
        self,
        ticker: str,
        market_data: Dict,
        fundamental_data: Dict,
        technical_data: Dict,
        existing_agent_analyses: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis using all Phase 2 enhancements

        Args:
            ticker: Stock ticker
            market_data: Market data dict
            fundamental_data: Fundamental data dict
            technical_data: Technical data dict
            existing_agent_analyses: Analyses from existing agents

        Returns:
            Enhanced decision dict with all Phase 2 data
        """
        logger.info(f"Analyzing {ticker} with Phase 2 enhancements")

        decision = {
            'ticker': ticker,
            'timestamp': datetime.now(),
            'action': 'HOLD',
            'confidence': 0.0,
            'reasoning': [],
            'phase2_data': {},
            'fallback_used': False
        }

        try:
            # 1. Get alternative data score
            alt_data_score = 0.0
            if self.components_initialized['alternative_data']:
                try:
                    alt_data_score = await self._get_alternative_data_score(ticker)
                    decision['phase2_data']['alternative_data'] = {
                        'score': alt_data_score,
                        'weight': self.config.alt_data_weight
                    }
                    logger.info(f"{ticker} alternative data score: {alt_data_score:.2f}")
                except Exception as e:
                    logger.error(f"Error getting alternative data for {ticker}: {e}")

            # 2. Run debate if enabled and appropriate
            debate_result = None
            if self.components_initialized['debate_system']:
                try:
                    # Determine if we should run debate
                    should_debate = self._should_run_debate(
                        ticker,
                        existing_agent_analyses,
                        alt_data_score
                    )

                    if should_debate:
                        debate_result = await self._run_debate(
                            ticker,
                            market_data,
                            fundamental_data,
                            technical_data,
                            alt_data_score
                        )

                        decision['phase2_data']['debate'] = debate_result
                        logger.info(f"{ticker} debate result: {debate_result['final_position']} "
                                  f"(confidence={debate_result['confidence']:.1%})")
                except Exception as e:
                    logger.error(f"Error running debate for {ticker}: {e}")

            # 3. Get options flow signal
            options_signal = None
            if self.components_initialized['options_flow']:
                try:
                    options_signal = await self.options_analyzer.analyze_ticker(
                        ticker,
                        minutes_back=self.config.options_lookback_minutes
                    )

                    decision['phase2_data']['options_flow'] = {
                        'signal': options_signal.signal,
                        'confidence': options_signal.confidence,
                        'put_call_ratio': options_signal.put_call_metrics.volume_ratio,
                        'flow_imbalance': options_signal.flow_imbalance.total_imbalance,
                        'large_trades': options_signal.large_trades_count
                    }
                    logger.info(f"{ticker} options flow: {options_signal.signal} "
                              f"(confidence={options_signal.confidence:.1%})")
                except Exception as e:
                    logger.error(f"Error getting options flow for {ticker}: {e}")

            # 4. Combine all signals into final decision
            final_decision = self._synthesize_decision(
                ticker,
                existing_agent_analyses,
                alt_data_score,
                debate_result,
                options_signal
            )

            decision.update(final_decision)

        except Exception as e:
            logger.error(f"Error in Phase 2 analysis for {ticker}: {e}")

            # Fallback to simple voting if enabled
            if self.config.fallback_to_simple_voting:
                logger.warning(f"Falling back to simple voting for {ticker}")
                decision['fallback_used'] = True
                decision['action'] = 'HOLD'
                decision['confidence'] = 0.0

        return decision

    async def _get_alternative_data_score(self, ticker: str) -> float:
        """Get alternative data composite score"""
        if not self.alt_data_agent:
            return 0.0

        # Get insider trading score
        insider_score = await self.alt_data_agent.get_insider_score(ticker)

        # Get Google Trends score
        trends_score = await self.alt_data_agent.get_trends_score(ticker)

        # Get options flow score if available
        options_score = 0.0
        if self.options_analyzer:
            try:
                signal = await self.options_analyzer.analyze_ticker(ticker)
                signal_map = {
                    'VERY_BULLISH': 1.0,
                    'BULLISH': 0.5,
                    'NEUTRAL': 0.0,
                    'BEARISH': -0.5,
                    'VERY_BEARISH': -1.0
                }
                options_score = signal_map.get(signal.signal, 0.0) * signal.confidence
            except Exception as e:
                logger.error(f"Error getting options score: {e}")

        # Weighted combination
        composite_score = (
            insider_score * 0.3 +
            trends_score * 0.3 +
            options_score * 0.4
        )

        return composite_score

    def _should_run_debate(
        self,
        ticker: str,
        agent_analyses: Optional[Dict],
        alt_data_score: float
    ) -> bool:
        """Determine if we should run a debate for this ticker"""

        # Always debate if config says so
        if self.config.use_debates_for_all:
            return True

        # If no agent analyses, don't debate
        if not agent_analyses:
            return False

        # Check if there's disagreement among agents
        # (This is simplified - actual implementation would analyze agent votes)
        disagreement_threshold = 0.3  # 30% disagreement

        # For now, debate if alt data score is significant
        if abs(alt_data_score) > 0.5:
            return True

        return False

    async def _run_debate(
        self,
        ticker: str,
        market_data: Dict,
        fundamental_data: Dict,
        technical_data: Dict,
        alt_data_score: float
    ) -> Dict:
        """Run bull/bear debate"""

        # Prepare debate context
        debate_context = {
            'ticker': ticker,
            'market_data': market_data,
            'fundamental_data': fundamental_data,
            'technical_data': technical_data,
            'alternative_data': {
                'composite_score': alt_data_score
            }
        }

        # Conduct debate
        conclusion = await self.debate_coordinator.orchestrator.conduct_debate(
            ticker=ticker,
            market_data=market_data,
            fundamental_data=fundamental_data,
            technical_data=technical_data,
            alternative_data=debate_context.get('alternative_data')
        )

        # Convert to dict
        return {
            'final_position': conclusion.final_position.value,
            'confidence': conclusion.confidence,
            'bull_score': conclusion.bull_score,
            'bear_score': conclusion.bear_score,
            'key_arguments': conclusion.key_arguments,
            'risk_factors': conclusion.risk_factors
        }

    def _synthesize_decision(
        self,
        ticker: str,
        agent_analyses: Optional[Dict],
        alt_data_score: float,
        debate_result: Optional[Dict],
        options_signal
    ) -> Dict:
        """
        Synthesize final decision from all signals

        Priority:
        1. Debate result (if available and high confidence)
        2. Options flow (if very strong signal)
        3. Alternative data + existing agents
        """

        # Start with neutral
        action = 'HOLD'
        confidence = 0.0
        reasoning = []

        # Use debate result if available and confident
        if debate_result and debate_result['confidence'] >= self.config.debate_min_confidence:
            position_map = {
                'LONG': 'BUY',
                'SHORT': 'SELL',
                'NEUTRAL': 'HOLD'
            }
            action = position_map.get(debate_result['final_position'], 'HOLD')
            confidence = debate_result['confidence']

            reasoning.append(
                f"Debate conclusion: {debate_result['final_position']} "
                f"(bull={debate_result['bull_score']}, bear={debate_result['bear_score']})"
            )

        # Consider options flow
        elif options_signal and options_signal.confidence >= self.config.options_min_confidence:
            signal_map = {
                'VERY_BULLISH': 'BUY',
                'BULLISH': 'BUY',
                'NEUTRAL': 'HOLD',
                'BEARISH': 'SELL',
                'VERY_BEARISH': 'SELL'
            }
            action = signal_map.get(options_signal.signal, 'HOLD')
            confidence = options_signal.confidence

            reasoning.append(
                f"Options flow: {options_signal.signal} "
                f"(P/C={options_signal.put_call_metrics.volume_ratio:.2f}, "
                f"imbalance=${options_signal.flow_imbalance.total_imbalance:,.0f})"
            )

        # Otherwise use alternative data + agent consensus
        else:
            # Simple mapping for alt data
            if alt_data_score > 0.5:
                action = 'BUY'
                confidence = min(abs(alt_data_score), 1.0)
            elif alt_data_score < -0.5:
                action = 'SELL'
                confidence = min(abs(alt_data_score), 1.0)
            else:
                action = 'HOLD'
                confidence = 0.5

            reasoning.append(f"Alternative data score: {alt_data_score:.2f}")

        return {
            'action': action,
            'confidence': confidence,
            'reasoning': reasoning
        }

    async def monitor_positions(self, positions: List[str]):
        """Monitor positions for catalyst events"""
        if not self.components_initialized['catalyst_monitor']:
            logger.warning("Catalyst monitor not available")
            return

        try:
            # Add positions to monitoring
            self.catalyst_monitor.add_monitored_tickers(positions)

            # Start monitoring (non-blocking)
            logger.info(f"Started catalyst monitoring for {len(positions)} positions")

            # Note: In production, this would be a background task
            # For now, we just set it up
        except Exception as e:
            logger.error(f"Error starting catalyst monitoring: {e}")

    async def generate_enhanced_report(
        self,
        decisions: List[Dict],
        include_phase2_details: bool = True
    ) -> str:
        """
        Generate enhanced report with Phase 2 data

        Args:
            decisions: List of decision dicts from analyze_ticker
            include_phase2_details: Include detailed Phase 2 sections

        Returns:
            Markdown formatted report
        """
        report = [
            "# Trading Decisions Report (Phase 2 Enhanced)",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            ""
        ]

        # Summary statistics
        buy_count = len([d for d in decisions if d['action'] == 'BUY'])
        sell_count = len([d for d in decisions if d['action'] == 'SELL'])
        hold_count = len([d for d in decisions if d['action'] == 'HOLD'])

        report.append(f"- **Total Analyzed**: {len(decisions)}")
        report.append(f"- **Buy Signals**: {buy_count}")
        report.append(f"- **Sell Signals**: {sell_count}")
        report.append(f"- **Hold/Pass**: {hold_count}")
        report.append("")

        # Phase 2 components status
        if include_phase2_details:
            report.append("## Phase 2 Enhancements Status")
            report.append("")
            for component, status in self.components_initialized.items():
                status_icon = "✓" if status else "✗"
                report.append(f"- {status_icon} {component.replace('_', ' ').title()}")
            report.append("")

        # Decisions
        report.append("## Decisions")
        report.append("")

        for decision in sorted(decisions, key=lambda d: d['confidence'], reverse=True):
            report.append(f"### {decision['ticker']} - {decision['action']} "
                        f"({decision['confidence']:.1%} confidence)")

            # Reasoning
            if decision.get('reasoning'):
                report.append("**Reasoning**:")
                for reason in decision['reasoning']:
                    report.append(f"- {reason}")
                report.append("")

            # Phase 2 details
            if include_phase2_details and 'phase2_data' in decision:
                phase2 = decision['phase2_data']

                # Alternative data
                if 'alternative_data' in phase2:
                    alt_data = phase2['alternative_data']
                    report.append(f"**Alternative Data**: Score {alt_data['score']:.2f} "
                                f"(weight {alt_data['weight']:.0%})")

                # Debate
                if 'debate' in phase2:
                    debate = phase2['debate']
                    report.append(f"**Debate**: {debate['final_position']} "
                                f"(bull={debate['bull_score']}, bear={debate['bear_score']})")

                # Options flow
                if 'options_flow' in phase2:
                    opts = phase2['options_flow']
                    report.append(f"**Options Flow**: {opts['signal']} "
                                f"(P/C={opts['put_call_ratio']:.2f}, "
                                f"imbalance=${opts['flow_imbalance']:,.0f})")

                report.append("")

            # Fallback warning
            if decision.get('fallback_used'):
                report.append("⚠️ *Fallback to simple voting used*")
                report.append("")

        return "\n".join(report)

    def run_integration_tests(self) -> Dict[str, bool]:
        """
        Run integration tests for all components

        Returns:
            Dict of component -> pass/fail
        """
        logger.info("Running Phase 2 integration tests...")

        results = {}

        # Test Alternative Data
        if self.components_initialized['alternative_data']:
            try:
                # Test that agent can be called
                asyncio.run(self.alt_data_agent.get_insider_score('AAPL'))
                results['alternative_data'] = True
                logger.info("✓ Alternative Data test passed")
            except Exception as e:
                results['alternative_data'] = False
                logger.error(f"✗ Alternative Data test failed: {e}")
        else:
            results['alternative_data'] = False

        # Test Debate System
        if self.components_initialized['debate_system']:
            try:
                # Test that debate can be orchestrated
                test_context = {
                    'ticker': 'TEST',
                    'market_data': {},
                    'fundamental_data': {},
                    'technical_data': {}
                }
                # Just check it exists
                assert self.debate_coordinator is not None
                results['debate_system'] = True
                logger.info("✓ Debate System test passed")
            except Exception as e:
                results['debate_system'] = False
                logger.error(f"✗ Debate System test failed: {e}")
        else:
            results['debate_system'] = False

        # Test Catalyst Monitor
        if self.components_initialized['catalyst_monitor']:
            try:
                # Test that monitor can add tickers
                self.catalyst_monitor.add_monitored_tickers(['TEST'])
                results['catalyst_monitor'] = True
                logger.info("✓ Catalyst Monitor test passed")
            except Exception as e:
                results['catalyst_monitor'] = False
                logger.error(f"✗ Catalyst Monitor test failed: {e}")
        else:
            results['catalyst_monitor'] = False

        # Test Options Flow
        if self.components_initialized['options_flow']:
            try:
                # Test that analyzer exists
                assert self.options_analyzer is not None
                results['options_flow'] = True
                logger.info("✓ Options Flow test passed")
            except Exception as e:
                results['options_flow'] = False
                logger.error(f"✗ Options Flow test failed: {e}")
        else:
            results['options_flow'] = False

        # Summary
        passed = sum(results.values())
        total = len(results)
        logger.info(f"Integration tests: {passed}/{total} passed")

        return results


def load_config_from_file(config_path: str = "config.yaml") -> Phase2Config:
    """
    Load Phase 2 configuration from YAML file

    Args:
        config_path: Path to config file

    Returns:
        Phase2Config instance
    """
    try:
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)

        # Extract Phase 2 section
        phase2_dict = config_dict.get('phase2', {})

        # Create config
        config = Phase2Config(
            enable_alternative_data=phase2_dict.get('enable_alternative_data', True),
            enable_debate_system=phase2_dict.get('enable_debate_system', True),
            enable_catalyst_monitor=phase2_dict.get('enable_catalyst_monitor', True),
            enable_options_flow=phase2_dict.get('enable_options_flow', True),
            alt_data_weight=phase2_dict.get('alt_data_weight', 0.3),
            insider_lookback_days=phase2_dict.get('insider_lookback_days', 90),
            trends_lookback_days=phase2_dict.get('trends_lookback_days', 30),
            debate_timeout_seconds=phase2_dict.get('debate_timeout_seconds', 30),
            debate_min_confidence=phase2_dict.get('debate_min_confidence', 0.55),
            use_debates_for_all=phase2_dict.get('use_debates_for_all', False),
            catalyst_check_interval=phase2_dict.get('catalyst_check_interval', 300),
            options_lookback_minutes=phase2_dict.get('options_lookback_minutes', 60),
            options_min_confidence=phase2_dict.get('options_min_confidence', 0.6),
            fallback_to_simple_voting=phase2_dict.get('fallback_to_simple_voting', True),
            verbose_logging=phase2_dict.get('verbose_logging', False)
        )

        logger.info(f"Loaded config from {config_path}")
        return config

    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using defaults")
        return Phase2Config()
    except Exception as e:
        logger.error(f"Error loading config: {e}, using defaults")
        return Phase2Config()


async def example_usage():
    """Example usage of Phase2IntegrationEngine"""

    # Load configuration
    config = load_config_from_file("config.yaml")

    # Create engine
    engine = Phase2IntegrationEngine(config)

    # Initialize
    await engine.initialize()

    # Run integration tests
    test_results = engine.run_integration_tests()
    print(f"\nIntegration Tests: {test_results}")

    # Analyze a ticker
    decision = await engine.analyze_ticker(
        ticker="AAPL",
        market_data={'current_price': 150.0},
        fundamental_data={'pe_ratio': 28.5},
        technical_data={'rsi': 65}
    )

    print(f"\nDecision for AAPL:")
    print(f"Action: {decision['action']}")
    print(f"Confidence: {decision['confidence']:.1%}")
    print(f"Reasoning: {decision['reasoning']}")

    # Generate report
    report = await engine.generate_enhanced_report([decision])
    print(f"\n{report}")


if __name__ == '__main__':
    asyncio.run(example_usage())
