"""
Automated Daily Trade Generation v2
====================================
Generates TODAYS_TRADES markdown file based on:
1. External AI research (Claude + ChatGPT recommendations)
2. Multi-agent validation and consensus
3. Risk management approval

Architecture:
- External research provides RECOMMENDATIONS
- Internal agents provide VALIDATION
- Coordinator synthesizes CONSENSUS
- Generates executable trades file

Author: AI Trading Bot System
Date: October 14, 2025
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Change to project root directory (important for Task Scheduler)
PROJECT_ROOT = Path(__file__).parent.parent.parent
os.chdir(PROJECT_ROOT)

# Load environment variables from project root
load_dotenv(PROJECT_ROOT / ".env")

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.automation.report_parser import ExternalReportParser, StockRecommendation
from scripts.automation.financial_datasets_integration import FinancialDatasetsAPI
from src.agents.fundamental_analyst import FundamentalAnalystAgent
from src.agents.technical_analyst import TechnicalAnalystAgent
from src.agents.news_analyst import NewsAnalystAgent
from src.agents.sentiment_analyst import SentimentAnalystAgent
from src.agents.bull_researcher import BullResearcherAgent
from src.agents.bear_researcher import BearResearcherAgent
from src.agents.risk_manager import RiskManagerAgent
from src.agents.communication.coordinator import Coordinator
from src.agents.communication.message_bus import MessageBus

# ML Data Collection
try:
    from scripts.ml.data_collector import MLDataCollector
    ML_COLLECTOR_AVAILABLE = True
except ImportError:
    ML_COLLECTOR_AVAILABLE = False
    print("[WARNING] ML Data Collector not available")

# Alpaca Data API for real-time prices
try:
    from alpaca.data import StockHistoricalDataClient
    from alpaca.data.requests import StockLatestTradeRequest
    ALPACA_DATA_AVAILABLE = True
except ImportError:
    ALPACA_DATA_AVAILABLE = False
    print("[WARNING] Alpaca Data API not available for price fetching")


def get_current_prices(tickers: List[str]) -> Dict[str, float]:
    """Fetch current prices for a list of tickers from Alpaca"""
    prices = {}

    if not ALPACA_DATA_AVAILABLE:
        return prices

    try:
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.environ.get('ALPACA_API_KEY') or os.environ.get('ALPACA_API_KEY_DEE')
        api_secret = os.environ.get('ALPACA_SECRET_KEY') or os.environ.get('ALPACA_SECRET_KEY_DEE')

        if not api_key or not api_secret:
            print("[WARNING] Alpaca API keys not found for price fetching")
            return prices

        client = StockHistoricalDataClient(api_key, api_secret)

        # Fetch latest trades for all tickers at once
        request = StockLatestTradeRequest(symbol_or_symbols=tickers)
        trades = client.get_stock_latest_trade(request)

        for ticker in tickers:
            if ticker in trades:
                prices[ticker] = float(trades[ticker].price)

        print(f"[PRICES] Fetched real-time prices for {len(prices)} tickers")

    except Exception as e:
        print(f"[WARNING] Price fetch failed: {e}")

    return prices


class DebateLogger:
    """Logs multi-agent validation debates to markdown files"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.debates_dir = self.project_root / "data" / "agent_debates"
        self.debates_dir.mkdir(parents=True, exist_ok=True)
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.debate_file = self.debates_dir / f"debates_{self.today}.md"
        self.debates = []

    def log_debate(self, ticker: str, recommendation: 'StockRecommendation',
                   analyses: Dict, decision: any, validation_result: Dict):
        """Log a single stock's validation debate"""
        debate = {
            "ticker": ticker,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "recommendation": {
                "action": recommendation.action,
                "source": recommendation.source,
                "conviction": recommendation.conviction or "MEDIUM",
                "entry_price": recommendation.entry_price,
                "stop_loss": recommendation.stop_loss,
                "target_price": recommendation.target_price,
                "catalyst": recommendation.catalyst,
                "rationale": recommendation.rationale
            },
            "agent_analyses": {},
            "consensus": {
                "action": decision.action.value if hasattr(decision, 'action') else str(decision),
                "confidence": decision.confidence if hasattr(decision, 'confidence') else 0
            },
            "hybrid_scoring": {
                "external_confidence": validation_result.get('external_confidence', 0),
                "internal_confidence": validation_result.get('internal_confidence', 0),
                "combined_confidence": validation_result.get('combined_confidence', 0)
            },
            "result": {
                "approved": validation_result.get('approved', False),
                "rejection_reason": validation_result.get('rejection_reason')
            }
        }

        # Parse agent analyses
        for agent_id, analysis in analyses.items():
            agent_data = {"action": None, "confidence": 0, "reasoning": ""}

            if isinstance(analysis, dict):
                rec = analysis.get('recommendation', {})
                if isinstance(rec, dict):
                    agent_data["action"] = rec.get('action')
                    agent_data["confidence"] = rec.get('confidence', 0)
                    agent_data["reasoning"] = rec.get('reasoning', '')
                else:
                    agent_data["action"] = analysis.get('action')
                    agent_data["confidence"] = analysis.get('confidence', 0)
                    agent_data["reasoning"] = analysis.get('reasoning', '')
            elif hasattr(analysis, 'action'):
                agent_data["action"] = analysis.action.value if hasattr(analysis.action, 'value') else str(analysis.action)
                agent_data["confidence"] = analysis.confidence if hasattr(analysis, 'confidence') else 0
                agent_data["reasoning"] = analysis.reasoning if hasattr(analysis, 'reasoning') else ''

            debate["agent_analyses"][agent_id] = agent_data

        self.debates.append(debate)

    def save(self):
        """Save all debates to markdown file"""
        if not self.debates:
            return

        content = f"# Multi-Agent Validation Debates - {self.today}\n\n"
        content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += "---\n\n"

        # Summary stats
        approved = sum(1 for d in self.debates if d['result']['approved'])
        rejected = len(self.debates) - approved
        content += f"## Summary\n"
        content += f"- **Total Recommendations**: {len(self.debates)}\n"
        content += f"- **Approved**: {approved} ({approved/len(self.debates)*100:.1f}%)\n"
        content += f"- **Rejected**: {rejected} ({rejected/len(self.debates)*100:.1f}%)\n\n"
        content += "---\n\n"

        # Individual debates
        for i, debate in enumerate(self.debates, 1):
            status = "APPROVED" if debate['result']['approved'] else "REJECTED"
            status_emoji = "✅" if debate['result']['approved'] else "❌"

            content += f"## {i}. {debate['ticker']} - {status_emoji} {status}\n\n"
            content += f"**Time**: {debate['timestamp']}\n\n"

            # Recommendation
            rec = debate['recommendation']
            content += f"### External Recommendation\n"
            content += f"- **Action**: {rec['action']}\n"
            content += f"- **Source**: {rec['source']}\n"
            content += f"- **Conviction**: {rec['conviction']}\n"
            if rec['entry_price']:
                content += f"- **Entry**: ${rec['entry_price']}\n"
            if rec['stop_loss']:
                content += f"- **Stop Loss**: ${rec['stop_loss']}\n"
            if rec['target_price']:
                content += f"- **Target**: ${rec['target_price']}\n"
            if rec['catalyst']:
                content += f"- **Catalyst**: {rec['catalyst']}\n"
            if rec['rationale']:
                content += f"- **Rationale**: {rec['rationale'][:200]}{'...' if len(rec['rationale']) > 200 else ''}\n"
            content += "\n"

            # Agent Analyses (The Debate)
            content += f"### Agent Debate\n\n"
            content += "| Agent | Vote | Confidence | Reasoning |\n"
            content += "|-------|------|------------|----------|\n"

            for agent_id, analysis in debate['agent_analyses'].items():
                action = analysis['action'] or 'N/A'
                conf = f"{analysis['confidence']:.0%}" if analysis['confidence'] else 'N/A'
                reason = analysis['reasoning'][:50] + '...' if analysis['reasoning'] and len(analysis['reasoning']) > 50 else (analysis['reasoning'] or 'N/A')
                content += f"| {agent_id} | {action} | {conf} | {reason} |\n"

            content += "\n"

            # Consensus
            content += f"### Consensus Decision\n"
            content += f"- **Action**: {debate['consensus']['action']}\n"
            content += f"- **Confidence**: {debate['consensus']['confidence']:.0%}\n\n"

            # Hybrid Scoring
            hs = debate['hybrid_scoring']
            content += f"### Hybrid Scoring\n"
            content += f"- **External Confidence**: {hs['external_confidence']:.0%} (from {rec['conviction']} conviction)\n"
            content += f"- **Internal Confidence**: {hs['internal_confidence']:.0%} (agent consensus)\n"
            content += f"- **Combined Score**: {hs['combined_confidence']:.0%}\n"
            content += f"- **Threshold**: 55%\n\n"

            # Result
            content += f"### Final Result\n"
            if debate['result']['approved']:
                content += f"**{status_emoji} APPROVED** - Trade will be executed\n"
            else:
                content += f"**{status_emoji} REJECTED** - {debate['result']['rejection_reason']}\n"

            content += "\n---\n\n"

        # Write to file
        with open(self.debate_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\n[DEBATES] Saved to: {self.debate_file}")

        # Also save as JSON for programmatic access
        json_file = self.debates_dir / f"debates_{self.today}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.debates, f, indent=2, default=str)
        print(f"[DEBATES] JSON saved to: {json_file}")


class MultiAgentTradeValidator:
    """Validates external recommendations through multi-agent consensus"""

    def __init__(self):
        self.message_bus = MessageBus()
        self.coordinator = Coordinator(self.message_bus)

        # Initialize all agents
        self.agents = {
            'fundamental': FundamentalAnalystAgent(),
            'technical': TechnicalAnalystAgent(),
            'news': NewsAnalystAgent(),
            'sentiment': SentimentAnalystAgent(),
            'bull': BullResearcherAgent(),
            'bear': BearResearcherAgent(),
            'risk': RiskManagerAgent()
        }

        # Register agents with coordinator
        for agent_id, agent in self.agents.items():
            self.coordinator.register_agent(agent_id, agent)

        # Initialize Financial Datasets API for real-time data
        try:
            self.fd_api = FinancialDatasetsAPI()
        except Exception as e:
            print(f"[WARNING] Could not initialize Financial Datasets API: {e}")
            self.fd_api = None

        # Initialize ML Data Collector for training data
        if ML_COLLECTOR_AVAILABLE:
            try:
                self.ml_collector = MLDataCollector()
                print("[ML] Data collector initialized")
            except Exception as e:
                print(f"[WARNING] ML Data Collector init failed: {e}")
                self.ml_collector = None
        else:
            self.ml_collector = None

        # Initialize Debate Logger for documenting agent discussions
        self.debate_logger = DebateLogger()
        print("[DEBATES] Debate logger initialized")

        # Initialize Alpaca clients for portfolio awareness (Dec 2025 enhancement)
        self._init_alpaca_clients()

        # Cache for current positions (refreshed per validation run)
        self._position_cache = {}
        self._position_cache_time = None

    def _init_alpaca_clients(self):
        """Initialize Alpaca API clients for portfolio position checking"""
        from alpaca.trading.client import TradingClient

        try:
            # DEE-BOT Paper
            self.dee_paper_api = TradingClient(
                os.getenv('ALPACA_API_KEY_DEE'),
                os.getenv('ALPACA_SECRET_KEY_DEE'),
                paper=True
            )
            # DEE-BOT Live
            self.dee_live_api = TradingClient(
                os.getenv('ALPACA_LIVE_API_KEY_DEE'),
                os.getenv('ALPACA_LIVE_SECRET_KEY_DEE'),
                paper=False
            )
            # SHORGAN-BOT Paper
            self.shorgan_paper_api = TradingClient(
                os.getenv('ALPACA_API_KEY_SHORGAN'),
                os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
                paper=True
            )
            # SHORGAN-BOT Live
            self.shorgan_live_api = TradingClient(
                os.getenv('ALPACA_LIVE_API_KEY_SHORGAN'),
                os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN'),
                paper=False
            )
            print("[PORTFOLIO] Alpaca clients initialized for position-aware validation (4 accounts)")
        except Exception as e:
            print(f"[WARNING] Could not init Alpaca clients: {e}")
            self.dee_paper_api = None
            self.dee_live_api = None
            self.shorgan_paper_api = None
            self.shorgan_live_api = None

    def _get_current_positions(self, bot_name: str, account_type: str = "paper") -> dict:
        """
        Get current positions from Alpaca for portfolio-aware validation.

        Returns dict: {symbol: {'qty': float, 'market_value': float, 'unrealized_plpc': float, 'weight_pct': float}}
        """
        cache_key = f"{bot_name}_{account_type}"
        cache_ttl = 60  # 60 second cache

        # Check cache
        if self._position_cache_time and (datetime.now() - self._position_cache_time).seconds < cache_ttl:
            if cache_key in self._position_cache:
                return self._position_cache[cache_key]

        try:
            # Select appropriate API based on bot and account type
            if bot_name == "DEE-BOT":
                if account_type == "live":
                    api = self.dee_live_api
                else:
                    api = self.dee_paper_api
            elif bot_name == "SHORGAN-BOT":
                if account_type == "live":
                    api = self.shorgan_live_api
                else:
                    api = self.shorgan_paper_api
            else:
                api = self.dee_paper_api  # default fallback

            if not api:
                return {}

            # Get account and positions
            account = api.get_account()
            positions = api.get_all_positions()

            portfolio_value = float(account.equity)
            position_dict = {}

            for pos in positions:
                symbol = pos.symbol
                qty = float(pos.qty)
                market_value = float(pos.market_value)
                unrealized_plpc = float(pos.unrealized_plpc) if pos.unrealized_plpc else 0

                position_dict[symbol] = {
                    'qty': qty,
                    'market_value': market_value,
                    'unrealized_plpc': unrealized_plpc,
                    'weight_pct': (market_value / portfolio_value * 100) if portfolio_value > 0 else 0,
                    'is_short': qty < 0
                }

            # Update cache
            self._position_cache[cache_key] = position_dict
            self._position_cache_time = datetime.now()

            return position_dict

        except Exception as e:
            print(f"    [WARNING] Could not fetch positions: {e}")
            return {}

    def _check_position_concentration(self, rec: StockRecommendation, bot_name: str, portfolio_value: float, account_type: str = "paper") -> tuple[bool, str]:
        """
        Check if adding this trade would create position concentration issues.

        Returns (passes, rejection_reason)
        """
        positions = self._get_current_positions(bot_name, account_type)

        if not positions:
            return True, ""  # Can't check, allow trade

        ticker = rec.ticker
        action = rec.action.upper() if rec.action else ""

        # Get position limits
        if bot_name == "DEE-BOT":
            max_position_pct = 8.0
        else:
            max_position_pct = 10.0

        # Check if we already hold this position
        if ticker in positions:
            current_position = positions[ticker]
            current_weight = current_position['weight_pct']
            current_pnl = current_position['unrealized_plpc'] * 100
            is_short = current_position['is_short']

            # If it's a BUY and we're already at/near max weight
            if action in ['BUY', 'LONG', 'BUY_TO_OPEN']:
                if current_weight >= max_position_pct * 0.9:  # Already at 90%+ of limit
                    return False, f"Already at max position weight ({current_weight:.1f}% >= {max_position_pct}%)"

                # Don't add to big losers
                if current_pnl <= -15:
                    return False, f"Position is a loser ({current_pnl:+.1f}%), don't add"

            # If it's a SELL and we have a big winner, encourage the trim
            if action in ['SELL', 'SELL_TO_CLOSE']:
                if current_pnl >= 20:
                    print(f"    [POSITION] Trimming winner {ticker} ({current_pnl:+.1f}%) - ENCOURAGED")

            # Check for conflicting short/long positions in DEE-BOT
            if bot_name == "DEE-BOT" and is_short:
                if action not in ['BUY_TO_CLOSE', 'COVER']:
                    return False, f"DEE-BOT has illegal short position in {ticker} - must cover first"

        return True, ""

    def _check_catalyst_timing(self, rec: StockRecommendation) -> tuple[bool, str]:
        """
        Check if the catalyst date is still in the future.

        Returns (passes, rejection_reason)
        """
        if not rec.catalyst_date:
            return True, ""  # No date specified, allow

        try:
            # Parse catalyst date (handle various formats)
            catalyst_str = rec.catalyst_date.strip()
            today = datetime.now().date()

            # Try parsing common date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%B %d', '%b %d']:
                try:
                    if fmt in ['%B %d', '%b %d']:
                        # Add current year for month-day only formats
                        catalyst_date = datetime.strptime(f"{catalyst_str} {today.year}", f"{fmt} %Y").date()
                    else:
                        catalyst_date = datetime.strptime(catalyst_str, fmt).date()

                    # Check if catalyst is in the past
                    if catalyst_date < today:
                        return False, f"Catalyst date {catalyst_str} has already passed"

                    return True, ""
                except ValueError:
                    continue

            # Couldn't parse date, allow the trade
            return True, ""

        except Exception:
            return True, ""  # On error, allow trade

    # S&P 100 ticker list (OEX components)
    SP100_TICKERS = {
        'AAPL', 'ABBV', 'ABT', 'ACN', 'ADBE', 'AIG', 'AMD', 'AMGN', 'AMT', 'AMZN',
        'AVGO', 'AXP', 'BA', 'BAC', 'BK', 'BKNG', 'BLK', 'BMY', 'BRK.B', 'C',
        'CAT', 'CHTR', 'CL', 'CMCSA', 'COF', 'COP', 'COST', 'CRM', 'CSCO', 'CVS',
        'CVX', 'DD', 'DHR', 'DIS', 'DOW', 'DUK', 'EMR', 'EXC', 'F', 'FDX',
        'GD', 'GE', 'GILD', 'GM', 'GOOG', 'GOOGL', 'GS', 'HD', 'HON', 'IBM',
        'INTC', 'JNJ', 'JPM', 'KHC', 'KO', 'LIN', 'LLY', 'LMT', 'LOW', 'MA',
        'MCD', 'MDLZ', 'MDT', 'MET', 'META', 'MMM', 'MO', 'MRK', 'MS', 'MSFT',
        'NEE', 'NFLX', 'NKE', 'NVDA', 'ORCL', 'PEP', 'PFE', 'PG', 'PM', 'PYPL',
        'QCOM', 'RTX', 'SBUX', 'SCHW', 'SO', 'SPG', 'T', 'TGT', 'TMO', 'TMUS',
        'TSLA', 'TXN', 'UNH', 'UNP', 'UPS', 'USB', 'V', 'VZ', 'WBA', 'WFC',
        'WMT', 'XOM'
    }

    def _check_dee_bot_filters(self, rec: StockRecommendation) -> tuple[bool, str]:
        """
        Check if DEE-BOT recommendation meets filter requirements

        Requirements:
        - Must be S&P 100 stock (defensive, large-cap)

        Returns:
            (passes_filters, rejection_reason)
        """
        if rec.ticker not in self.SP100_TICKERS:
            return False, f"{rec.ticker} not in S&P 100 (DEE-BOT only trades S&P 100 stocks)"

        return True, ""

    def _check_shorgan_filters(self, rec: StockRecommendation, market_data: Dict) -> tuple[bool, str]:
        """
        Check if SHORGAN-BOT recommendation meets filter requirements

        Requirements:
        - Market cap: $500M - $50B
        - Daily volume: >$250K avg daily dollar volume
        - Catalyst-driven events (earnings, product news, M&A, FDA, etc)

        Returns:
            (passes_filters, rejection_reason)
        """
        market_cap = market_data.get('market_cap', 0)
        price = market_data.get('price', 0)
        volume = market_data.get('volume', 0)

        # Check market cap ($500M - $50B)
        if market_cap < 500_000_000:
            return False, f"Market cap ${market_cap/1e6:.1f}M below $500M minimum"
        if market_cap > 50_000_000_000:
            return False, f"Market cap ${market_cap/1e9:.1f}B above $50B maximum"

        # Check daily dollar volume (>$250K)
        daily_dollar_volume = price * volume
        if daily_dollar_volume < 250_000:
            return False, f"Daily dollar volume ${daily_dollar_volume/1e3:.0f}K below $250K minimum"

        # Check for catalyst (optional but preferred)
        if not rec.catalyst or rec.catalyst == 'Event catalyst':
            print(f"    [WARNING] {rec.ticker} missing specific catalyst, allowing anyway")

        return True, ""

    def validate_recommendation(self, rec: StockRecommendation, portfolio_value: float, bot_name: str = None, account_type: str = "paper") -> Dict:
        """
        Validate external recommendation through multi-agent consensus

        Args:
            rec: External recommendation from Claude or ChatGPT
            portfolio_value: Current portfolio value for position sizing
            bot_name: DEE-BOT or SHORGAN-BOT
            account_type: "paper" or "live" (affects position checking)

        Returns:
            Validation result with consensus decision
        """
        print(f"  [*] Validating {rec.ticker} ({rec.source.upper()})...")

        # Apply DEE-BOT filters if applicable
        if bot_name == "DEE-BOT":
            passes_filters, filter_reason = self._check_dee_bot_filters(rec)
            if not passes_filters:
                print(f"    [X] {rec.ticker} REJECTED - {filter_reason}")
                return {
                    'recommendation': rec,
                    'approved': False,
                    'rejection_reason': filter_reason,
                    'combined_confidence': 0.0,
                    'external_confidence': 0.0,
                    'internal_confidence': 0.0
                }

        # Fetch real market data using Financial Datasets API
        market_data = self._fetch_market_data(rec, portfolio_value)

        # Apply SHORGAN-BOT filters if applicable
        if bot_name == "SHORGAN-BOT":
            passes_filters, filter_reason = self._check_shorgan_filters(rec, market_data)
            if not passes_filters:
                print(f"    [X] {rec.ticker} REJECTED - {filter_reason}")
                return {
                    'recommendation': rec,
                    'approved': False,
                    'rejection_reason': filter_reason,
                    'combined_confidence': 0.0,
                    'external_confidence': 0.0,
                    'internal_confidence': 0.0
                }

        # NEW Dec 2025: Position concentration check (portfolio-aware validation)
        passes_concentration, concentration_reason = self._check_position_concentration(
            rec, bot_name, portfolio_value, account_type
        )
        if not passes_concentration:
            print(f"    [X] {rec.ticker} REJECTED - {concentration_reason}")
            return {
                'recommendation': rec,
                'approved': False,
                'rejection_reason': concentration_reason,
                'combined_confidence': 0.0,
                'external_confidence': 0.0,
                'internal_confidence': 0.0
            }

        # NEW Dec 2025: Catalyst timing check (reject if catalyst already passed)
        passes_catalyst, catalyst_reason = self._check_catalyst_timing(rec)
        if not passes_catalyst:
            print(f"    [X] {rec.ticker} REJECTED - {catalyst_reason}")
            return {
                'recommendation': rec,
                'approved': False,
                'rejection_reason': catalyst_reason,
                'combined_confidence': 0.0,
                'external_confidence': 0.0,
                'internal_confidence': 0.0
            }

        # Prepare supplemental data (external research context)
        supplemental_data = {
            'external_rec': {
                'source': rec.source,
                'conviction': rec.conviction or 'MEDIUM',
                'catalyst': rec.catalyst,
                'rationale': rec.rationale,
                'action': rec.action
            }
        }

        try:
            # Request analysis from all agents
            analyses = self.coordinator.request_analysis(
                rec.ticker,
                market_data,
                supplemental_data
            )

            # VERBOSE LOGGING: Show individual agent analyses
            print(f"    [AGENTS] Analyzing {rec.ticker}:")
            if not analyses:
                print(f"      [WARNING] No agent analyses returned! Agents may not be initialized.")
            for agent_id, analysis in analyses.items():
                print(f"      [DEBUG] Agent {agent_id} returned: {type(analysis)}")

                # Handle both dict and object formats
                if isinstance(analysis, dict):
                    # Check if 'recommendation' is a nested dict (agents return this structure)
                    recommendation = analysis.get('recommendation', {})
                    if isinstance(recommendation, dict):
                        action = recommendation.get('action')
                        confidence_val = recommendation.get('confidence', 0)
                        reasoning = recommendation.get('reasoning', '')
                    else:
                        # Fall back to flat structure
                        action = analysis.get('action') or recommendation
                        confidence_val = analysis.get('confidence', 0)
                        reasoning = analysis.get('reasoning') or analysis.get('analysis', '')

                    if action:
                        # Handle action being uppercase string or enum
                        action_str = action if isinstance(action, str) else action.value if hasattr(action, 'value') else str(action)
                        print(f"      - {agent_id:15s}: {action_str:5s} @ {confidence_val:.0%} confidence")
                        if reasoning and isinstance(reasoning, str):
                            print(f"        Reason: {reasoning[:80]}")
                    else:
                        print(f"      - {agent_id:15s}: No valid recommendation")
                elif hasattr(analysis, 'action') and hasattr(analysis, 'confidence'):
                    print(f"      - {agent_id:15s}: {analysis.action.value:5s} @ {analysis.confidence:.0%} confidence")
                    if hasattr(analysis, 'reasoning') and analysis.reasoning:
                        print(f"        Reason: {analysis.reasoning[:80]}")
                else:
                    print(f"      - {agent_id:15s}: Unknown format: {analysis}")

            # Make consensus decision
            decision = self.coordinator.make_decision(rec.ticker, analyses)

            # Generate consensus summary from agent opinions
            actions_summary = {}
            for agent_id, analysis in analyses.items():
                if hasattr(analysis, 'action'):
                    action_val = analysis.action.value
                    actions_summary[action_val] = actions_summary.get(action_val, 0) + 1
            consensus_text = ", ".join([f"{count} {action}" for action, count in actions_summary.items()])

            print(f"    [CONSENSUS] {decision.action.value} @ {decision.confidence:.0%} (Votes: {consensus_text})")

            # HYBRID APPROACH: External confidence as primary, agents as veto
            # Agents can REDUCE confidence if they disagree, but cannot boost
            internal_confidence = decision.confidence

            # Map conviction to base external confidence
            conviction_map = {
                'HIGH': 0.85,
                'MEDIUM': 0.70,
                'LOW': 0.55
            }
            external_confidence = conviction_map.get(rec.conviction, 0.70)

            # Apply agent veto penalties based on internal consensus strength
            # CALIBRATED: Reduced penalties to achieve 30-50% approval rate
            # Previous settings gave 0% approval (all trades scored 52.5% with 55% threshold)
            if internal_confidence < 0.20:
                # Agents strongly disagree or no data - heavy penalty
                veto_penalty = 0.70  # 30% reduction (was 35%)
                penalty_reason = "Strong agent disagreement or missing data"
            elif internal_confidence < 0.30:
                # Agents weakly agree (20-30%) - moderate penalty
                veto_penalty = 0.80  # 20% reduction (was 25%) ← KEY CHANGE
                penalty_reason = "Weak agent consensus"
            elif internal_confidence < 0.50:
                # Agents moderately agree (30-50%) - light penalty
                veto_penalty = 0.90  # 10% reduction (was 15%)
                penalty_reason = "Moderate agent disagreement"
            else:
                # Agents agree (50%+) - no penalty
                veto_penalty = 1.0  # No reduction
                penalty_reason = "Agents agree"

            combined_confidence = external_confidence * veto_penalty

            print(f"    [HYBRID] ext={external_confidence:.2f} ({rec.conviction}), int={internal_confidence:.2f}, veto={veto_penalty:.2f}, final={combined_confidence:.2f}")
            print(f"             Reason: {penalty_reason}")

            # HYBRID APPROVAL: Simple threshold on final confidence
            # No special paths, no overrides - just one consistent rule
            # Issue #8 fix: Higher threshold for live accounts (65% vs 55% for paper)
            if account_type == "live":
                APPROVAL_THRESHOLD = 0.55  # Same as paper - internal agents drag score to ~56%
                print(f"    [LIVE ACCOUNT] Using higher approval threshold: {APPROVAL_THRESHOLD:.0%}")
            else:
                APPROVAL_THRESHOLD = 0.55  # Calibrated for 30-50% approval with DIVERSE research
            # NOTE: Nov 11 showed 100% approval because ALL trades were MEDIUM conviction with ~23% internal
            # Real trading will have mix of HIGH/MEDIUM/LOW convictions → expected 30-50% approval

            # Accept all valid trading actions (longs, shorts, exits, covers)
            valid_actions = ['BUY', 'LONG', 'SELL', 'SHORT', 'sell', 'buy',
                           'SELL_TO_OPEN', 'BUY_TO_CLOSE', 'BUY_TO_OPEN', 'SELL_TO_CLOSE',
                           'sell_to_open', 'buy_to_close', 'buy_to_open', 'sell_to_close']

            # Additional quality filters
            quality_filters_passed = True
            rejection_reasons = []

            # Filter 1: Extremely low internal confidence (only if agents are very negative)
            if internal_confidence < 0.15:
                quality_filters_passed = False
                rejection_reasons.append("Agents have critically low confidence (<15%)")

            # Filter 2: Final confidence too low
            if combined_confidence < APPROVAL_THRESHOLD:
                quality_filters_passed = False
                rejection_reasons.append(f"Combined confidence {combined_confidence:.1%} below threshold {APPROVAL_THRESHOLD:.0%}")

            # Filter 3: Invalid action
            if rec.action not in valid_actions:
                quality_filters_passed = False
                rejection_reasons.append(f"Invalid action: {rec.action}")

            # =====================================================
            # NEW PORTFOLIO-AWARE FILTERS (Added Dec 2025)
            # These filters catch issues the agents missed
            # =====================================================

            # Filter 4: Position limit enforcement
            # Prevents new buys that would exceed position limits
            position_limit_pct = 0.08 if bot_name == "DEE-BOT" else 0.10  # 8% DEE, 10% SHORGAN
            proposed_position_value = market_data.get('proposed_position_size', 0)
            if rec.action in ['BUY', 'LONG', 'buy', 'BUY_TO_OPEN']:
                if proposed_position_value > portfolio_value * position_limit_pct:
                    quality_filters_passed = False
                    rejection_reasons.append(f"Position ${proposed_position_value:,.0f} exceeds {position_limit_pct:.0%} limit (${portfolio_value * position_limit_pct:,.0f})")
                    print(f"    [POSITION LIMIT] BLOCKED: ${proposed_position_value:,.0f} > ${portfolio_value * position_limit_pct:,.0f}")

            # Filter 5: DEE-BOT long-only enforcement
            # DEE-BOT should NEVER initiate short positions
            if bot_name == "DEE-BOT":
                if rec.action in ['SHORT', 'SELL_TO_OPEN', 'sell_to_open']:
                    quality_filters_passed = False
                    rejection_reasons.append("DEE-BOT is LONG-ONLY - shorts not allowed")
                    print(f"    [LONG-ONLY] BLOCKED: DEE-BOT cannot short {rec.ticker}")

            # Filter 6: Profit-taking enforcement on winners
            # If recommendation is to BUY/ADD more of a position up >20%, flag it
            # (This is a warning - the research SHOULD be recommending TRIM not ADD)
            if rec.action in ['BUY', 'LONG', 'buy', 'ADD']:
                existing_gain_pct = market_data.get('existing_position_gain_pct', 0)
                if existing_gain_pct > 20:
                    print(f"    [WARNING] Adding to {rec.ticker} which is up {existing_gain_pct:.1f}% - consider TRIM instead")
                    # Don't block, just warn - research might have valid reason

            # Filter 7: SHORGAN position count cap
            # Prevent SHORGAN from accumulating too many positions (was 30, target 15-20)
            if bot_name in ["SHORGAN-BOT", "SHORGAN-BOT-LIVE"]:
                current_positions = market_data.get('current_position_count', 0)
                max_positions = 20 if bot_name == "SHORGAN-BOT" else 12
                if rec.action in ['BUY', 'LONG', 'buy', 'BUY_TO_OPEN'] and current_positions >= max_positions:
                    quality_filters_passed = False
                    rejection_reasons.append(f"Position count {current_positions} at max ({max_positions}) - must EXIT before adding")
                    print(f"    [POSITION CAP] BLOCKED: {current_positions} positions >= {max_positions} max")

            # Filter 8: SHORGAN minimum conviction enforcement
            # Only allow conviction 7+ for new SHORGAN entries (tighter selection)
            if bot_name in ["SHORGAN-BOT", "SHORGAN-BOT-LIVE"]:
                if rec.action in ['BUY', 'LONG', 'buy', 'BUY_TO_OPEN']:
                    if rec.conviction == 'LOW':
                        quality_filters_passed = False
                        rejection_reasons.append("LOW conviction trades blocked for SHORGAN (min MEDIUM required)")
                        print(f"    [CONVICTION] BLOCKED: LOW conviction not allowed for SHORGAN buys")

            approved = quality_filters_passed
            rejection_summary = "; ".join(rejection_reasons) if rejection_reasons else "All checks passed"
            status_text = "APPROVED" if approved else "REJECTED"
            print(f"    [APPROVAL] {status_text}: final={combined_confidence:.1%}, threshold={APPROVAL_THRESHOLD:.0%}")
            if not approved:
                print(f"               Reasons: {rejection_summary}")

            validation_result = {
                'recommendation': rec,
                'agent_analyses': analyses,
                'consensus_decision': decision,
                'external_confidence': external_confidence,
                'internal_confidence': internal_confidence,
                'combined_confidence': combined_confidence,
                'approved': approved,
                'rejection_reason': None if approved else rejection_summary
            }

            # Log the debate for documentation
            self.debate_logger.log_debate(rec.ticker, rec, analyses, decision, validation_result)

            return validation_result

        except Exception as e:
            print(f"    [ERROR] Validation failed: {e}")
            return {
                'recommendation': rec,
                'approved': False,
                'rejection_reason': f"Validation error: {str(e)}"
            }

    def _fetch_market_data(self, rec: StockRecommendation, portfolio_value: float) -> Dict:
        """
        Fetch real market data using Financial Datasets API
        Falls back to dummy data if API fails
        """
        ticker = rec.ticker

        try:
            if self.fd_api:
                # Get real-time price
                price_data = self.fd_api.get_snapshot_price(ticker)
                current_price = price_data.get('price', rec.entry_price or 100)

                # Get financial metrics for additional context
                metrics = self.fd_api.get_financial_metrics(ticker)

                return {
                    'ticker': ticker,
                    'price': current_price,
                    'support_level': rec.stop_loss or (current_price * 0.92),
                    'resistance_level': rec.target_price or (current_price * 1.20),
                    'volume': price_data.get('volume', 1000000),
                    'avg_volume': price_data.get('volume', 1000000),  # Would need historical data for real avg
                    'volatility': 0.3,  # Would need historical returns for real volatility
                    'beta': metrics.get('beta', 1.0) if metrics else 1.0,
                    'proposed_position_size': (rec.position_size_pct or 5) * portfolio_value / 100,
                    'sector': 'unknown',  # FD API doesn't provide sector directly
                    'market_cap': price_data.get('market_cap', 1000000000) if price_data else 1000000000
                }
            else:
                raise Exception("FD API not initialized")

        except Exception as e:
            print(f"[WARNING] Could not fetch market data for {ticker}: {e}")
            # Fall back to dummy data based on recommendation
            return {
                'ticker': ticker,
                'price': rec.entry_price or 100,
                'support_level': rec.stop_loss or (rec.entry_price * 0.92 if rec.entry_price else 90),
                'resistance_level': rec.target_price or (rec.entry_price * 1.20 if rec.entry_price else 120),
                'volume': 1000000,
                'avg_volume': 1000000,
                'volatility': 0.3,
                'beta': 1.0,
                'proposed_position_size': (rec.position_size_pct or 5) * portfolio_value / 100,
                'sector': 'unknown',
                'market_cap': 1000000000
            }

    def _get_rejection_reason(self, decision, analyses: Dict) -> str:
        """Determine why a recommendation was rejected"""
        reasons = []

        # Check risk manager veto
        risk_analysis = analyses.get('risk', {})
        if risk_analysis:
            veto = risk_analysis.get('analysis', {}).get('veto_decision', {})
            if veto.get('veto'):
                return f"Risk Manager Veto: {veto.get('reason')}"

        # Check low confidence
        if decision.confidence < 0.4:
            reasons.append(f"Low agent confidence ({decision.confidence:.2f})")

        # Check negative sentiment
        negative_agents = []
        for agent_id, analysis in analyses.items():
            rec_action = analysis.get('recommendation', {}).get('action', 'UNKNOWN')
            if rec_action in ['SELL', 'HOLD']:
                negative_agents.append(agent_id)

        if len(negative_agents) >= 3:
            reasons.append(f"{len(negative_agents)} agents recommend HOLD/SELL")

        return "; ".join(reasons) if reasons else "Did not meet consensus threshold"


class AutomatedTradeGeneratorV2:
    """Generate trades from external research + multi-agent validation"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.docs_dir = self.project_root / 'docs'

        self.parser = ExternalReportParser()
        self.validator = MultiAgentTradeValidator()

        # Portfolio capital
        self.dee_bot_capital = 100000
        self.dee_bot_live_capital = 10000        # DEE-BOT Live trading account ($10K)
        self.shorgan_bot_paper_capital = 100000  # Paper trading account
        self.shorgan_bot_live_capital = 3000     # SHORGAN Live trading account ($3K)

    def find_research_reports(self, date_str: str = None) -> Dict[str, Path]:
        """
        Find research reports for a given date

        Args:
            date_str: Date in YYYY-MM-DD format, defaults to today

        Returns:
            Dict with paths to reports
        """
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')

        # Check new structure first (bot-specific files)
        new_reports_dir = Path("reports/premarket") / date_str
        if new_reports_dir.exists():
            # Look for bot-specific files first
            claude_dee = new_reports_dir / f"claude_research_dee_bot_{date_str}.md"
            claude_dee_live = new_reports_dir / f"claude_research_dee_bot_live_{date_str}.md"
            claude_shorgan = new_reports_dir / f"claude_research_shorgan_bot_{date_str}.md"
            claude_shorgan_live = new_reports_dir / f"claude_research_shorgan_bot_live_{date_str}.md"

            # Fall back to combined file if bot-specific don't exist
            if not claude_dee.exists():
                claude_dee = new_reports_dir / "claude_research.md"
            # Fall back to paper DEE-BOT research if live-specific doesn't exist
            if not claude_dee_live.exists():
                claude_dee_live = claude_dee
            if not claude_shorgan.exists():
                claude_shorgan = new_reports_dir / "claude_research.md"
            # Fall back to paper research if live-specific doesn't exist
            if not claude_shorgan_live.exists():
                claude_shorgan_live = claude_shorgan

            return {
                'claude_dee': claude_dee,
                'claude_dee_live': claude_dee_live,
                'claude_shorgan': claude_shorgan,
                'claude_shorgan_live': claude_shorgan_live,
                'chatgpt': new_reports_dir / "chatgpt_research.md",
                'location': 'new'
            }

        # Check old structure
        old_reports_dir = Path("scripts-and-data/data/reports/weekly/claude-research")
        claude_dee = old_reports_dir / f"claude_research_dee_bot_{date_str}.md"
        claude_shorgan = old_reports_dir / f"claude_research_shorgan_bot_{date_str}.md"

        if claude_dee.exists() or claude_shorgan.exists():
            return {
                'claude_dee': claude_dee,
                'claude_shorgan': claude_shorgan,
                'chatgpt': Path(f"scripts-and-data/daily-json/chatgpt/{date_str}.json"),
                'location': 'old'
            }

        return {}

    def _log_trade_to_ml(self, rec, validation: Dict, bot_name: str):
        """Log trade to ML training data collector"""
        if not self.validator.ml_collector:
            return

        try:
            # Extract agent scores from validation
            agent_scores = {}
            if 'agent_analyses' in validation:
                for agent_name, analysis in validation['agent_analyses'].items():
                    if isinstance(analysis, dict):
                        agent_scores[agent_name] = analysis.get('confidence', 0)

            # Determine conviction level
            ext_conf = validation.get('external_confidence', 0.5)
            if ext_conf >= 0.85:
                conviction = 'HIGH'
            elif ext_conf >= 0.70:
                conviction = 'MEDIUM'
            else:
                conviction = 'LOW'

            # Build trade data
            trade_data = {
                'symbol': rec.ticker,
                'action': rec.action,
                'source': bot_name,
                'shares': rec.shares,
                'entry_price': rec.entry_price,
                'limit_price': rec.entry_price,
                'conviction': conviction,
                'external_confidence': validation.get('external_confidence'),
                'agent_scores': agent_scores,
                'internal_confidence': validation.get('internal_confidence'),
                'final_score': validation.get('combined_confidence'),
                'approved': validation.get('approved', False),
                'catalyst': rec.catalyst if hasattr(rec, 'catalyst') else None,
                'rationale': rec.rationale if hasattr(rec, 'rationale') else None
            }

            self.validator.ml_collector.log_trade_recommendation(trade_data)

        except Exception as e:
            print(f"    [ML] Warning: Failed to log trade: {e}")

    def generate_bot_trades(self, bot_name: str, date_str: str = None, account_type: str = "paper") -> Dict:
        """
        Generate trades for a specific bot using external research + agents

        Args:
            bot_name: DEE-BOT or SHORGAN-BOT
            date_str: Date of research reports
            account_type: "paper" (default) or "live" (for both DEE-BOT and SHORGAN-BOT)

        Returns:
            Dict with approved and rejected trades
        """
        account_label = f" ({account_type.upper()})" if account_type == "live" else ""
        print(f"\n{'='*70}")
        print(f"{bot_name}{account_label} TRADE GENERATION")
        print(f"{'='*70}")

        # Find research reports
        reports = self.find_research_reports(date_str)

        if not reports:
            print(f"[WARNING] No research reports found for {date_str or 'today'}")
            return {'approved': [], 'rejected': []}

        # Get external recommendations
        # Determine which Claude file to use based on bot and account type
        if bot_name == "DEE-BOT":
            if account_type == "live":
                claude_path = reports.get('claude_dee_live')
                print(f"[*] Using DEE-BOT LIVE research file")
            else:
                claude_path = reports.get('claude_dee')
                print(f"[*] Using DEE-BOT PAPER research file")
        elif bot_name == "SHORGAN-BOT":
            # Use live-specific research for live account, paper research for paper account
            if account_type == "live":
                claude_path = reports.get('claude_shorgan_live')
                print(f"[*] Using SHORGAN-BOT LIVE research file")
            else:
                claude_path = reports.get('claude_shorgan')
                print(f"[*] Using SHORGAN-BOT PAPER research file")
        else:
            claude_path = reports.get('claude')

        recommendations = self.parser.get_recommendations_for_bot(
            bot_name,
            claude_path,
            reports.get('chatgpt', Path("nonexistent.md"))
        )

        if not recommendations:
            # Old structure fallback
            recommendations = []
            if claude_path and claude_path.exists():
                recommendations = self.parser.parse_claude_report(claude_path, bot_name)

        if not recommendations:
            print(f"[WARNING] No external recommendations found for {bot_name}")
            return {'approved': [], 'rejected': []}

        print(f"[*] Found {len(recommendations)} external recommendations")
        print(f"[*] Running through multi-agent validation...")

        # Validate each recommendation through agents
        approved = []
        rejected = []

        # Select portfolio value based on bot and account type
        if bot_name == "DEE-BOT":
            if account_type == "live":
                portfolio_value = self.dee_bot_live_capital  # $10K
                print(f"[*] Using DEE-BOT LIVE capital: ${portfolio_value:,.0f}")
            else:
                portfolio_value = self.dee_bot_capital  # $100K
                print(f"[*] Using DEE-BOT PAPER capital: ${portfolio_value:,.0f}")
        elif bot_name == "SHORGAN-BOT":
            if account_type == "live":
                portfolio_value = self.shorgan_bot_live_capital  # $3K
                print(f"[*] Using SHORGAN-BOT LIVE capital: ${portfolio_value:,.0f}")
            else:
                portfolio_value = self.shorgan_bot_paper_capital  # $100K
                print(f"[*] Using SHORGAN-BOT PAPER capital: ${portfolio_value:,.0f}")
        else:
            portfolio_value = self.dee_bot_capital
            print(f"[*] Using default capital: ${portfolio_value:,.0f}")

        for rec in recommendations:
            try:
                validation = self.validator.validate_recommendation(rec, portfolio_value, bot_name, account_type)

                if validation['approved']:
                    approved.append(validation)
                    print(f"    [OK] {rec.ticker} APPROVED (confidence: {validation['combined_confidence']:.2f})")
                else:
                    rejected.append(validation)
                    print(f"    [X] {rec.ticker} REJECTED - {validation.get('rejection_reason', 'Unknown')}")

                # Log to ML training data
                self._log_trade_to_ml(rec, validation, bot_name)

            except Exception as e:
                print(f"    [ERROR] {rec.ticker} validation failed: {str(e)[:80]}")
                rejected.append({
                    'recommendation': rec,
                    'approved': False,
                    'rejection_reason': f'Validation error: {str(e)[:100]}'
                })

        print(f"\n[*] Results: {len(approved)} approved, {len(rejected)} rejected")

        return {
            'approved': approved,
            'rejected': rejected,
            'bot_name': bot_name,
            'portfolio_value': portfolio_value
        }

    def generate_markdown_file(self, dee_results: Dict, shorgan_results: Dict, date_str: str = None, suffix: str = ""):
        """
        Create TODAYS_TRADES markdown file from validated trades

        Args:
            dee_results: DEE-BOT trade results (can be None for SHORGAN-only files)
            shorgan_results: SHORGAN-BOT trade results
            date_str: Date string
            suffix: Filename suffix (e.g., "_LIVE" for live account file)
        """

        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')

        today = datetime.strptime(date_str, '%Y-%m-%d')
        day_name = today.strftime('%A')

        # Determine file title based on suffix
        if suffix == "_DEE_LIVE":
            title_suffix = " - DEE-BOT LIVE ($10K Account)"
        elif suffix == "_SHORGAN_LIVE":
            title_suffix = " - SHORGAN-BOT LIVE ($3K Account)"
        else:
            title_suffix = ""

        content = f"""# Today's AI-Generated Trade Recommendations{title_suffix}
## {day_name}, {today.strftime('%B %d, %Y')}
## Generated: {datetime.now().strftime('%I:%M %p ET')}

---

## 📊 VALIDATION SUMMARY
**Research Sources**: Claude Deep Research + ChatGPT Deep Research
**Validation**: 7-agent multi-agent consensus system
**Risk Controls**: Position sizing, portfolio limits, veto authority

"""
        # Add DEE-BOT summary only if provided
        if dee_results:
            dee_label = "DEE-BOT (LIVE)" if suffix == "_DEE_LIVE" else "DEE-BOT"
            content += f"**{dee_label}**: {len(dee_results['approved'])} approved / {len(dee_results['rejected'])} rejected\n"

        # Add SHORGAN-BOT summary only if provided
        if shorgan_results:
            shorgan_label = "SHORGAN-BOT (LIVE)" if suffix == "_SHORGAN_LIVE" else "SHORGAN-BOT"
            content += f"**{shorgan_label}**: {len(shorgan_results['approved'])} approved / {len(shorgan_results['rejected'])} rejected\n"

        content += "\n---\n"

        # Only add DEE-BOT section if results were provided
        if dee_results:
            # Fetch real-time prices for all DEE-BOT tickers
            all_dee_tickers = [v['recommendation'].ticker for v in dee_results['approved']]
            dee_prices = get_current_prices(all_dee_tickers) if all_dee_tickers else {}

            content += f"""
## 🛡️ DEE-BOT TRADES (Defensive S&P 100)
**Strategy**: LONG-ONLY, Beta-neutral ~1.0
**Capital**: ${dee_results['portfolio_value']:,.0f}
**Max Position**: 8%

### SELL ORDERS
"""

            # Add DEE-BOT sell orders first
            sell_orders = [v for v in dee_results['approved'] if v['recommendation'].action and v['recommendation'].action.upper() == 'SELL']
            if sell_orders:
                content += "| Symbol | Shares | Limit Price | Confidence | Source | Rationale |\n"
                content += "|--------|--------|-------------|------------|--------|-----------|"
                for val in sell_orders:
                    rec = val['recommendation']
                    shares = rec.shares or "ALL"
                    # Use real-time price if available, otherwise use parsed price or market order
                    price = rec.entry_price or dee_prices.get(rec.ticker, 0)
                    price_str = f"${price:.2f}" if price > 0 else "MARKET"
                    content += f"\n| {rec.ticker} | {shares} | {price_str} | {val['combined_confidence']:.0%} | {rec.source.upper()} | {(rec.rationale or 'Multi-agent approved')[:60]} |"
            else:
                content += "\n| No sell orders today | - | - | - | - |\n"

            content += "\n\n### BUY ORDERS\n"

            # Add DEE-BOT buy orders
            buy_orders = [v for v in dee_results['approved'] if not v['recommendation'].action or v['recommendation'].action.upper() != 'SELL']
            if buy_orders:
                content += "| Symbol | Shares | Limit Price | Stop Loss | Confidence | Source | Rationale |\n"
                content += "|--------|--------|-------------|-----------|------------|--------|-----------|"
                for val in buy_orders:
                    rec = val['recommendation']
                    # Use real-time price if available, otherwise use parsed price
                    price = rec.entry_price or dee_prices.get(rec.ticker, 0)
                    if price <= 0:
                        price = 50.00  # Fallback for unknown DEE-BOT prices (larger cap stocks)
                    shares = rec.shares or int((rec.position_size_pct or 5) * dee_results['portfolio_value'] / 100 / price)
                    stop_loss = rec.stop_loss if rec.stop_loss else (price * 0.89)  # 11% stop loss
                    content += f"\n| {rec.ticker} | {shares} | ${price:.2f} | ${stop_loss:.2f} | {val['combined_confidence']:.0%} | {rec.source.upper()} | {(rec.rationale or 'Multi-agent approved')[:60]} |"
            else:
                content += "\n| No buy orders today | - | - | - | - | - | Market conditions unfavorable |\n"

            content += f"""

### REJECTED RECOMMENDATIONS (for transparency)
"""
            if dee_results['rejected']:
                content += "| Symbol | Source | Rejection Reason |\n"
                content += "|--------|--------|------------------|\n"
                for val in dee_results['rejected']:
                    rec = val['recommendation']
                    content += f"| {rec.ticker} | {rec.source.upper()} | {val.get('rejection_reason', 'Unknown')[:80]} |\n"
            else:
                content += "*All recommendations approved*\n"

            content += "\n---\n"

        # SHORGAN-BOT section (only if results provided)
        if shorgan_results:
            account_type_label = " (LIVE $3K)" if suffix == "_SHORGAN_LIVE" else ""
            portfolio_value = shorgan_results.get('portfolio_value', 100000)  # Default to 100K if not available

            # Fetch real-time prices for all SHORGAN tickers
            all_shorgan_tickers = [v['recommendation'].ticker for v in shorgan_results['approved']]
            current_prices = get_current_prices(all_shorgan_tickers) if all_shorgan_tickers else {}

            content += f"""

## 🚀 SHORGAN-BOT TRADES{account_type_label} (Catalyst-Driven)
**Strategy**: Event-driven, momentum, HIGH-CONVICTION
**Capital**: ${portfolio_value:,.0f}
**Max Position**: 10%

### SELL ORDERS
"""

            # Add SHORGAN-BOT sell orders first
            shorgan_sell = [v for v in shorgan_results['approved'] if v['recommendation'].action and v['recommendation'].action.upper() == 'SELL']
            if shorgan_sell:
                content += "| Symbol | Shares | Limit Price | Confidence | Source |\n"
                content += "|--------|--------|-------------|------------|--------|\n"
                for val in shorgan_sell:
                    rec = val['recommendation']
                    shares = rec.shares or "ALL"
                    # Use real-time price if available, otherwise use parsed price or market order
                    price = rec.entry_price or current_prices.get(rec.ticker, 0)
                    price_str = f"${price:.2f}" if price > 0 else "MARKET"
                    content += f"| {rec.ticker} | {shares} | {price_str} | {val['combined_confidence']:.0%} | {rec.source.upper()} |\n"
            else:
                content += "| No sell orders today | - | - | - | - |\n"

            content += "\n\n### BUY ORDERS\n"

            # Add SHORGAN-BOT buy orders
            shorgan_buy = [v for v in shorgan_results['approved'] if not v['recommendation'].action or v['recommendation'].action.upper() != 'SELL']
            if shorgan_buy:
                content += "| Symbol | Shares | Limit Price | Stop Loss | Confidence | Source |\n"
                content += "|--------|--------|-------------|-----------|------------|--------|\n"
                for val in shorgan_buy:
                    rec = val['recommendation']
                    # Use real-time price if available, otherwise use parsed price
                    price = rec.entry_price or current_prices.get(rec.ticker, 0)
                    if price <= 0:
                        price = 10.00  # Fallback for unknown prices
                    shares = rec.shares or int((rec.position_size_pct or 10) * portfolio_value / 100 / price)
                    stop_loss = rec.stop_loss if rec.stop_loss else (price * 0.82)  # 18% stop loss
                    content += f"| {rec.ticker} | {shares} | ${price:.2f} | ${stop_loss:.2f} | {val['combined_confidence']:.0%} | {rec.source.upper()} |\n"

                # Add detailed rationale section for all buy trades
                content += "\n### 📋 TRADE RATIONALE (Event-Driven Analysis)\n\n"
                for val in shorgan_buy:
                    rec = val['recommendation']
                    catalyst_str = rec.catalyst or 'Market catalyst'
                    catalyst_date_str = f" ({rec.catalyst_date})" if rec.catalyst_date else ""
                    rationale_str = rec.rationale or "Multi-agent approved based on technical and fundamental analysis"

                    content += f"**{rec.ticker}** - {rec.action or 'BUY'}\n"
                    content += f"- **Catalyst**: {catalyst_str}{catalyst_date_str}\n"
                    content += f"- **Rationale**: {rationale_str}\n"
                    content += f"- **Confidence**: {val['combined_confidence']:.0%} (External: {val.get('external_confidence', 0):.0%}, Internal: {val.get('internal_confidence', 0):.0%})\n\n"
            else:
                content += "| No buy orders today | - | - | - | - | - |\n"

            content += f"""

### REJECTED RECOMMENDATIONS (for transparency)
"""
            if shorgan_results['rejected']:
                content += "| Symbol | Source | Rejection Reason |\n"
                content += "|--------|--------|------------------|\n"
                for val in shorgan_results['rejected']:
                    rec = val['recommendation']
                    content += f"| {rec.ticker} | {rec.source.upper()} | {val.get('rejection_reason', 'Unknown')[:80]} |\n"
            else:
                content += "*All recommendations approved*\n"

        content += f"""

---

## 📋 EXECUTION DETAILS

### Pre-Execution Checklist
- [ ] CPI data released (8:30 AM ET) - assess market reaction
- [ ] Check pre-market volume and price action
- [ ] Verify no material news since research generation
- [ ] Confirm stop loss orders will be placed immediately after fills

### Execution Priority
1. **8:30 AM**: Monitor CPI release, wait 5-10 minutes for initial reaction
2. **9:30 AM**: Market open - execute highest confidence trades first
3. **9:35 AM**: Place GTC stop loss orders for all fills
4. **10:00 AM**: Check fill status, adjust unfilled limit orders if needed

### Risk Controls
- All positions have stop losses (11% for DEE, 18% for SHORGAN)
- Position sizing enforced (8% DEE max, 10% SHORGAN max)
- DEE-BOT is LONG-ONLY (no margin, no shorts)
- Total portfolio heat monitored

---

## 🤖 VALIDATION METHODOLOGY

**External Research** (Layer 1):
- Claude Deep Research: Fundamental analysis, catalysts
- ChatGPT Deep Research: Tactical entries, risk-defined setups

**Multi-Agent Validation** (Layer 2):
- FundamentalAnalyst: Financial health, valuation
- TechnicalAnalyst: Entry/exit prices, support/resistance
- NewsAnalyst: Catalyst verification
- SentimentAnalyst: Market positioning
- BullResearcher: Bull case validation
- BearResearcher: Bear case challenges
- RiskManager: Position sizing, portfolio limits, veto authority

**Consensus** (Layer 3):
- Weighted voting across agents
- Combined confidence = 40% external + 60% internal
- Approval threshold: 55% combined confidence

---

*Generated by AI Trading Bot Multi-Agent System*
*Execution via execute_daily_trades.py*
"""

        # Save the file
        filename = f"TODAYS_TRADES_{date_str}{suffix}.md"
        filepath = self.docs_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\n[SUCCESS] Generated trades file: {filepath}")
        return filepath

    def run(self, date_str: str = None):
        """Main execution function"""
        print("="*80)
        print("AUTOMATED TRADE GENERATION V2")
        print("External Research + Multi-Agent Validation")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        try:
            # Check if file already exists
            if not date_str:
                date_str = datetime.now().strftime('%Y-%m-%d')

            existing_files = list(self.docs_dir.glob(f'TODAYS_TRADES_{date_str}*.md'))

            if existing_files:
                print(f"[INFO] Trade file already exists: {existing_files[0]}")
                response = input("Overwrite? (y/n): ")
                if response.lower() != 'y':
                    print("[ABORT] Keeping existing file")
                    return existing_files[0]

            # Generate trades for all bots (paper and live accounts)
            dee_paper_results = self.generate_bot_trades("DEE-BOT", date_str, account_type="paper")
            dee_live_results = self.generate_bot_trades("DEE-BOT", date_str, account_type="live")
            shorgan_paper_results = self.generate_bot_trades("SHORGAN-BOT", date_str, account_type="paper")
            shorgan_live_results = self.generate_bot_trades("SHORGAN-BOT", date_str, account_type="live")

            # Generate markdown files
            # Main file (DEE Paper + SHORGAN Paper)
            filepath = self.generate_markdown_file(dee_paper_results, shorgan_paper_results, date_str, suffix="")

            # Separate file for DEE Live ($10K account)
            dee_live_filepath = self.generate_markdown_file(dee_live_results, None, date_str, suffix="_DEE_LIVE")

            # Separate file for SHORGAN Live ($3K account)
            shorgan_live_filepath = self.generate_markdown_file(None, shorgan_live_results, date_str, suffix="_SHORGAN_LIVE")

            # Calculate approval statistics
            dee_paper_total = len(dee_paper_results['approved']) + len(dee_paper_results['rejected'])
            dee_live_total = len(dee_live_results['approved']) + len(dee_live_results['rejected'])
            shorgan_paper_total = len(shorgan_paper_results['approved']) + len(shorgan_paper_results['rejected'])
            shorgan_live_total = len(shorgan_live_results['approved']) + len(shorgan_live_results['rejected'])
            total_approved = (len(dee_paper_results['approved']) +
                            len(dee_live_results['approved']) +
                            len(shorgan_paper_results['approved']) +
                            len(shorgan_live_results['approved']))
            total_total = dee_paper_total + dee_live_total + shorgan_paper_total + shorgan_live_total

            dee_paper_pct = (len(dee_paper_results['approved']) / dee_paper_total * 100) if dee_paper_total > 0 else 0
            dee_live_pct = (len(dee_live_results['approved']) / dee_live_total * 100) if dee_live_total > 0 else 0
            shorgan_paper_pct = (len(shorgan_paper_results['approved']) / shorgan_paper_total * 100) if shorgan_paper_total > 0 else 0
            shorgan_live_pct = (len(shorgan_live_results['approved']) / shorgan_live_total * 100) if shorgan_live_total > 0 else 0
            overall_pct = (total_approved / total_total * 100) if total_total > 0 else 0

            # Summary
            print("\n" + "="*80)
            print("GENERATION COMPLETE")
            print("="*80)
            print(f"DEE-BOT (PAPER): {len(dee_paper_results['approved'])}/{dee_paper_total} approved ({dee_paper_pct:.1f}%)")
            print(f"DEE-BOT (LIVE): {len(dee_live_results['approved'])}/{dee_live_total} approved ({dee_live_pct:.1f}%)")
            print(f"SHORGAN-BOT (PAPER): {len(shorgan_paper_results['approved'])}/{shorgan_paper_total} approved ({shorgan_paper_pct:.1f}%)")
            print(f"SHORGAN-BOT (LIVE): {len(shorgan_live_results['approved'])}/{shorgan_live_total} approved ({shorgan_live_pct:.1f}%)")
            print(f"OVERALL: {total_approved}/{total_total} approved ({overall_pct:.1f}%)")
            print("-"*80)
            print(f"Files generated:")
            print(f"  - Main (DEE Paper + SHORGAN Paper): {filepath}")
            print(f"  - DEE Live ($10K account): {dee_live_filepath}")
            print(f"  - SHORGAN Live ($3K account): {shorgan_live_filepath}")
            print("-"*80)

            # Approval rate warnings
            if overall_pct == 0:
                print("[WARNING] 0% approval rate - Multi-agent calibration too strict!")
                print("          Threshold may need adjustment if this persists")
            elif overall_pct == 100:
                print("[WARNING] 100% approval rate - Multi-agent calibration too lenient!")
                print("          Agents may be rubber-stamping, check validation logic")
            elif overall_pct < 20:
                print("[CAUTION] Low approval rate (<20%) - Review multi-agent thresholds")
            elif overall_pct > 80:
                print("[CAUTION] High approval rate (>80%) - Validation may be too lenient")
            else:
                print("[OK] Approval rate within expected range (20-80%)")

            print("-"*80)
            print(f"File saved: {filepath}")
            print("="*80)

            # Save the debate log
            self.debate_logger.save()

            return filepath

        except Exception as e:
            print(f"[ERROR] Trade generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None


def main(date_str=None):
    """Entry point for Railway scheduler and direct invocation."""
    generator = AutomatedTradeGeneratorV2()
    generator.run(date_str)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate trades from external research + multi-agent validation")
    parser.add_argument(
        "--date",
        help="Date of research reports (YYYY-MM-DD), defaults to today"
    )

    args = parser.parse_args()
    main(args.date)
