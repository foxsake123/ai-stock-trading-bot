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

    def validate_recommendation(self, rec: StockRecommendation, portfolio_value: float) -> Dict:
        """
        Validate external recommendation through multi-agent consensus

        Args:
            rec: External recommendation from Claude or ChatGPT
            portfolio_value: Current portfolio value for position sizing

        Returns:
            Validation result with consensus decision
        """
        print(f"  [*] Validating {rec.ticker} ({rec.source.upper()})...")

        # Prepare market data for agents
        market_data = {
            'ticker': rec.ticker,
            'price': rec.entry_price or 100,
            'support_level': rec.stop_loss or (rec.entry_price * 0.92 if rec.entry_price else 90),
            'resistance_level': rec.target_price or (rec.entry_price * 1.20 if rec.entry_price else 120),
            'volume': 1000000,  # Would fetch real data in production
            'avg_volume': 1000000,
            'volatility': 0.3,
            'beta': 1.0,
            'proposed_position_size': (rec.position_size_pct or 5) * portfolio_value / 100,
            'sector': 'unknown'
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
            external_confidence = 0.7 if rec.conviction == 'HIGH' else 0.5 if rec.conviction == 'MEDIUM' else 0.3
            internal_confidence = decision.confidence
            combined_confidence = (external_confidence * 0.4 + internal_confidence * 0.6)

            # Check if approved
            approved = (
                decision.action.value == 'BUY' and
                combined_confidence >= 0.55 and
                rec.action in ['BUY', 'LONG']
            )

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
                validation = self.validator.validate_recommendation(rec, portfolio_value)

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
                content += f"\n| {rec.ticker} | {shares} | ${rec.entry_price:.2f} | ${rec.stop_loss:.2f if rec.stop_loss else rec.entry_price * 0.92:.2f} | {val['combined_confidence']:.0%} | {rec.source.upper()} | {(rec.rationale or 'Multi-agent approved')[:60]} |"
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
            content += "| Symbol | Shares | Limit Price | Stop Loss | Confidence | Catalyst | Source |\n"
            content += "|--------|--------|-------------|-----------|------------|----------|--------|\n"
            for val in shorgan_results['approved']:
                rec = val['recommendation']
                shares = rec.shares or int((rec.position_size_pct or 10) * shorgan_results['portfolio_value'] / 100 / (rec.entry_price or 100))
                catalyst_short = (rec.catalyst or 'Event catalyst')[:40]
                content += f"| {rec.ticker} | {shares} | ${rec.entry_price:.2f} | ${rec.stop_loss:.2f if rec.stop_loss else rec.entry_price * 0.85:.2f} | {val['combined_confidence']:.0%} | {catalyst_short} | {rec.source.upper()} |\n"
        else:
            content += "| No buy orders today | - | - | - | - | - | - |\n"

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
