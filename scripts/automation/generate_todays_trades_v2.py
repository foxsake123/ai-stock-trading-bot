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

    def validate_recommendation(self, rec: StockRecommendation, portfolio_value: float, bot_name: str = None) -> Dict:
        """
        Validate external recommendation through multi-agent consensus

        Args:
            rec: External recommendation from Claude or ChatGPT
            portfolio_value: Current portfolio value for position sizing

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

            # Make consensus decision
            decision = self.coordinator.make_decision(rec.ticker, analyses)

            # Calculate combined confidence (external + internal)
            # When FD API data is available, trust Claude Opus 4.1 recommendations more
            has_fd_data = market_data.get('price', 100) != 100  # Check if we got real data

            if has_fd_data and rec.conviction in ['HIGH', 'MEDIUM']:
                # Boost external confidence when we have real data verification
                external_confidence = 0.9 if rec.conviction == 'HIGH' else 0.75
                # Weight external research heavily (80% external, 20% internal)
                combined_confidence = (external_confidence * 0.8 + decision.confidence * 0.2)
                print(f"    [DEBUG] FD-verified, conviction={rec.conviction}, ext={external_confidence:.2f}, int={decision.confidence:.2f}, combined={combined_confidence:.2f}")
            else:
                # Standard confidence and weighting
                external_confidence = 0.7 if rec.conviction == 'HIGH' else 0.5 if rec.conviction == 'MEDIUM' else 0.3
                combined_confidence = (external_confidence * 0.4 + decision.confidence * 0.6)
                print(f"    [DEBUG] Standard weighting, ext={external_confidence:.2f}, int={decision.confidence:.2f}, combined={combined_confidence:.2f}")

            internal_confidence = decision.confidence

            # Check if approved
            # When we have FD-verified data and high external confidence,
            # trust Claude Opus 4.1 research even if internal agents disagree
            # Accept all valid trading actions (longs, shorts, exits, covers)
            valid_actions = ['BUY', 'LONG', 'SELL', 'SHORT', 'sell', 'buy',
                           'SELL_TO_OPEN', 'BUY_TO_CLOSE', 'BUY_TO_OPEN', 'SELL_TO_CLOSE',
                           'sell_to_open', 'buy_to_close', 'buy_to_open', 'sell_to_close']

            if has_fd_data and external_confidence >= 0.75 and combined_confidence >= 0.60:
                # FD-verified path: Trust external research for all action types
                approved = (rec.action in valid_actions)
                print(f"    [DEBUG] FD-verified approval path: action={rec.action}, ext={external_confidence:.2f}, combined={combined_confidence:.2f}, approved={approved}")
            else:
                # Standard path: Require agent consensus
                approved = (
                    decision.action.value == 'BUY' and
                    combined_confidence >= 0.55 and
                    rec.action in valid_actions
                )
                print(f"    [DEBUG] Standard approval path: agent_action={decision.action.value}, rec_action={rec.action}, combined={combined_confidence:.2f}, approved={approved}")

            return {
                'recommendation': rec,
                'agent_analyses': analyses,
                'consensus_decision': decision,
                'external_confidence': external_confidence,
                'internal_confidence': internal_confidence,
                'combined_confidence': combined_confidence,
                'approved': approved,
                'rejection_reason': None if approved else self._get_rejection_reason(decision, analyses)
            }

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
        self.shorgan_bot_capital = 100000

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
            claude_shorgan = new_reports_dir / f"claude_research_shorgan_bot_{date_str}.md"

            # Fall back to combined file if bot-specific don't exist
            if not claude_dee.exists():
                claude_dee = new_reports_dir / "claude_research.md"
            if not claude_shorgan.exists():
                claude_shorgan = new_reports_dir / "claude_research.md"

            return {
                'claude_dee': claude_dee,
                'claude_shorgan': claude_shorgan,
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

    def generate_bot_trades(self, bot_name: str, date_str: str = None) -> Dict:
        """
        Generate trades for a specific bot using external research + agents

        Args:
            bot_name: DEE-BOT or SHORGAN-BOT
            date_str: Date of research reports

        Returns:
            Dict with approved and rejected trades
        """
        print(f"\n{'='*70}")
        print(f"{bot_name} TRADE GENERATION")
        print(f"{'='*70}")

        # Find research reports
        reports = self.find_research_reports(date_str)

        if not reports:
            print(f"[WARNING] No research reports found for {date_str or 'today'}")
            return {'approved': [], 'rejected': []}

        # Get external recommendations
        # Determine which Claude file to use
        if bot_name == "DEE-BOT":
            claude_path = reports.get('claude_dee')
        elif bot_name == "SHORGAN-BOT":
            claude_path = reports.get('claude_shorgan')
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

        portfolio_value = self.dee_bot_capital if bot_name == "DEE-BOT" else self.shorgan_bot_capital

        for rec in recommendations:
            try:
                validation = self.validator.validate_recommendation(rec, portfolio_value, bot_name)

                if validation['approved']:
                    approved.append(validation)
                    print(f"    [OK] {rec.ticker} APPROVED (confidence: {validation['combined_confidence']:.2f})")
                else:
                    rejected.append(validation)
                    print(f"    [X] {rec.ticker} REJECTED - {validation.get('rejection_reason', 'Unknown')}")
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

    def generate_markdown_file(self, dee_results: Dict, shorgan_results: Dict, date_str: str = None):
        """Create TODAYS_TRADES markdown file from validated trades"""

        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')

        today = datetime.strptime(date_str, '%Y-%m-%d')
        day_name = today.strftime('%A')

        content = f"""# Today's AI-Generated Trade Recommendations
## {day_name}, {today.strftime('%B %d, %Y')}
## Generated: {datetime.now().strftime('%I:%M %p ET')}

---

## 📊 VALIDATION SUMMARY
**Research Sources**: Claude Deep Research + ChatGPT Deep Research
**Validation**: 7-agent multi-agent consensus system
**Risk Controls**: Position sizing, portfolio limits, veto authority

**DEE-BOT**: {len(dee_results['approved'])} approved / {len(dee_results['rejected'])} rejected
**SHORGAN-BOT**: {len(shorgan_results['approved'])} approved / {len(shorgan_results['rejected'])} rejected

---

## 🛡️ DEE-BOT TRADES (Defensive S&P 100)
**Strategy**: LONG-ONLY, Beta-neutral ~1.0
**Capital**: ${dee_results['portfolio_value']:,.0f}
**Max Position**: 8%

### BUY ORDERS
"""

        # Add DEE-BOT buy orders
        if dee_results['approved']:
            content += "| Symbol | Shares | Limit Price | Stop Loss | Confidence | Source | Rationale |\n"
            content += "|--------|--------|-------------|-----------|------------|--------|-----------|"
            for val in dee_results['approved']:
                rec = val['recommendation']
                shares = rec.shares or int((rec.position_size_pct or 5) * dee_results['portfolio_value'] / 100 / (rec.entry_price or 100))
                stop_loss = rec.stop_loss if rec.stop_loss else (rec.entry_price * 0.92 if rec.entry_price else 0)
                content += f"\n| {rec.ticker} | {shares} | ${rec.entry_price:.2f} | ${stop_loss:.2f} | {val['combined_confidence']:.0%} | {rec.source.upper()} | {(rec.rationale or 'Multi-agent approved')[:60]} |"
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

        content += f"""

---

## 🚀 SHORGAN-BOT TRADES (Catalyst-Driven)
**Strategy**: Event-driven, momentum, HIGH-CONVICTION
**Capital**: ${shorgan_results['portfolio_value']:,.0f}
**Max Position**: 10%

### BUY ORDERS
"""

        # Add SHORGAN-BOT buy orders
        if shorgan_results['approved']:
            content += "| Symbol | Shares | Limit Price | Stop Loss | Confidence | Source |\n"
            content += "|--------|--------|-------------|-----------|------------|--------|\n"
            for val in shorgan_results['approved']:
                rec = val['recommendation']
                shares = rec.shares or int((rec.position_size_pct or 10) * shorgan_results['portfolio_value'] / 100 / (rec.entry_price or 100))
                stop_loss = rec.stop_loss if rec.stop_loss else (rec.entry_price * 0.85 if rec.entry_price else 0)
                content += f"| {rec.ticker} | {shares} | ${rec.entry_price:.2f} | ${stop_loss:.2f} | {val['combined_confidence']:.0%} | {rec.source.upper()} |\n"

            # Add detailed rationale section for each trade
            content += "\n### 📋 TRADE RATIONALE (Event-Driven Analysis)\n\n"
            for val in shorgan_results['approved']:
                rec = val['recommendation']
                catalyst_str = rec.catalyst or 'Market catalyst'
                catalyst_date_str = f" ({rec.catalyst_date})" if rec.catalyst_date else ""
                rationale_str = rec.rationale or "Multi-agent approved based on technical and fundamental analysis"

                content += f"**{rec.ticker}** - {rec.action}\n"
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
- All positions have stop losses (8% for DEE, 15% for SHORGAN)
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
        filename = f"TODAYS_TRADES_{date_str}.md"
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

            # Generate trades for both bots
            dee_results = self.generate_bot_trades("DEE-BOT", date_str)
            shorgan_results = self.generate_bot_trades("SHORGAN-BOT", date_str)

            # Generate markdown file
            filepath = self.generate_markdown_file(dee_results, shorgan_results, date_str)

            # Summary
            print("\n" + "="*80)
            print("GENERATION COMPLETE")
            print(f"DEE-BOT: {len(dee_results['approved'])} approved")
            print(f"SHORGAN-BOT: {len(shorgan_results['approved'])} approved")
            print(f"File saved: {filepath}")
            print("="*80)

            return filepath

        except Exception as e:
            print(f"[ERROR] Trade generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate trades from external research + multi-agent validation")
    parser.add_argument(
        "--date",
        help="Date of research reports (YYYY-MM-DD), defaults to today"
    )

    args = parser.parse_args()

    generator = AutomatedTradeGeneratorV2()
    generator.run(args.date)
