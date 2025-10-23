"""
Dual-AI Multi-Agent Consensus Validator
========================================
Takes external research (Claude Deep Research + ChatGPT Deep Research)
and validates through the existing multi-agent system for consensus.

Architecture:
1. Parse external research (Claude + ChatGPT recommendations)
2. Run each recommendation through 7-agent debate:
   - FundamentalAnalyst
   - TechnicalAnalyst
   - NewsAnalyst
   - SentimentAnalyst
   - BullResearcher
   - BearResearcher
   - RiskManager (veto power)
3. Coordinator synthesizes weighted consensus
4. Generate validated consensus.md and trades.md

This DOES NOT bypass the multi-agent system - it feeds external
research INTO the agent debate layer as recommendations to validate.

Author: AI Trading Bot System
Date: October 14, 2025
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.fundamental_analyst import FundamentalAnalystAgent
from src.agents.technical_analyst import TechnicalAnalystAgent
from src.agents.news_analyst import NewsAnalystAgent
from src.agents.sentiment_analyst import SentimentAnalystAgent
from src.agents.bull_researcher import BullResearcherAgent
from src.agents.bear_researcher import BearResearcherAgent
from src.agents.risk_manager import RiskManagerAgent
from src.agents.communication.coordinator import Coordinator
from src.agents.communication.message_bus import MessageBus


class ExternalRecommendation:
    """Represents a recommendation from external AI (Claude or ChatGPT)"""

    def __init__(self, data: Dict):
        self.source = data.get('source', 'unknown')  # 'claude' or 'chatgpt'
        self.ticker = data.get('ticker', '').upper()
        self.action = data.get('action', '').upper()  # BUY, SELL, SHORT
        self.entry_price = data.get('entry_price', 0.0)
        self.target_price = data.get('target_price', 0.0)
        self.stop_loss = data.get('stop_loss', 0.0)
        self.position_size_pct = data.get('position_size_pct', 0.0)
        self.catalyst = data.get('catalyst', '')
        self.catalyst_date = data.get('catalyst_date', '')
        self.conviction = data.get('conviction', 'MEDIUM')
        self.rationale = data.get('rationale', '')
        self.bot = data.get('bot', 'UNKNOWN')  # SHORGAN or DEE

    def to_dict(self):
        return {
            'source': self.source,
            'ticker': self.ticker,
            'action': self.action,
            'entry_price': self.entry_price,
            'target_price': self.target_price,
            'stop_loss': self.stop_loss,
            'position_size_pct': self.position_size_pct,
            'catalyst': self.catalyst,
            'catalyst_date': self.catalyst_date,
            'conviction': self.conviction,
            'rationale': self.rationale,
            'bot': self.bot
        }

    def __repr__(self):
        return f"{self.source.upper()} | {self.action} {self.ticker} @ ${self.entry_price} | {self.conviction}"


class DualAIConsensusValidator:
    """Validates external AI research through internal multi-agent system"""

    def __init__(self):
        """Initialize validator with multi-agent system"""
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

    def parse_claude_research(self, report_path: Path) -> List[ExternalRecommendation]:
        """
        Parse Claude Deep Research markdown report

        Returns:
            List of ExternalRecommendation objects
        """
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        recommendations = []

        # SHORGAN section parsing
        shorgan_pattern = r'### Trade \d+: (\w+)(.*?)(?=### Trade \d+:|## DEE-BOT|$)'
        shorgan_matches = re.findall(shorgan_pattern, content, re.DOTALL)

        for ticker, trade_block in shorgan_matches:
            rec = self._parse_trade_block(ticker, trade_block, 'claude', 'SHORGAN')
            if rec:
                recommendations.append(rec)

        # DEE-BOT section parsing
        dee_pattern = r'#### (\w+) -.*?\n(.*?)(?=####|##|$)'
        dee_matches = re.findall(dee_pattern, content, re.DOTALL)

        for ticker, trade_block in dee_matches:
            rec = self._parse_trade_block(ticker, trade_block, 'claude', 'DEE')
            if rec:
                recommendations.append(rec)

        return recommendations

    def parse_chatgpt_research(self, report_path: Path) -> List[ExternalRecommendation]:
        """
        Parse ChatGPT Deep Research markdown report

        Returns:
            List of ExternalRecommendation objects
        """
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        recommendations = []

        # Parse summary table
        table_pattern = r'\| (Shorgan|Dee)‑Bot \| \*\*(\w+)\*\* \| Long \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| \*\*([\d.]+)%?\*\* \|'
        matches = re.findall(table_pattern, content)

        for bot, ticker, entry, stop, target, size in matches:
            rec = ExternalRecommendation({
                'source': 'chatgpt',
                'ticker': ticker,
                'action': 'BUY',
                'entry_price': float(entry),
                'stop_loss': float(stop),
                'target_price': float(target),
                'position_size_pct': float(size),
                'bot': bot.upper(),
                'conviction': 'MEDIUM'
            })
            recommendations.append(rec)

        return recommendations

    def _parse_trade_block(self, ticker: str, block: str, source: str, bot: str) -> Optional[ExternalRecommendation]:
        """Parse individual trade block"""
        data = {
            'source': source,
            'ticker': ticker,
            'bot': bot
        }

        # Extract action
        if 'SHORT' in block.upper() or 'SELL SHORT' in block.upper():
            data['action'] = 'SHORT'
        else:
            data['action'] = 'BUY'

        # Extract prices
        entry_match = re.search(r'Entry Price.*?\$?([\d.,-]+)', block)
        if entry_match:
            data['entry_price'] = float(entry_match.group(1).replace(',', '').replace('$', '').split('-')[0])

        target_match = re.search(r'Target Price.*?\$?([\d.,-]+)', block)
        if target_match:
            data['target_price'] = float(target_match.group(1).replace(',', '').replace('$', ''))

        stop_match = re.search(r'Stop Loss.*?\$?([\d.,-]+)', block)
        if stop_match:
            data['stop_loss'] = float(stop_match.group(1).replace(',', '').replace('$', ''))

        # Extract position size
        size_match = re.search(r'Position Size.*?([\d.]+)[-–]?([\d.]+)?%', block)
        if size_match:
            data['position_size_pct'] = float(size_match.group(1))

        # Extract catalyst
        catalyst_match = re.search(r'Catalyst.*?:(.+?)(?:\n|$)', block)
        if catalyst_match:
            data['catalyst'] = catalyst_match.group(1).strip()

        # Extract conviction
        conviction_match = re.search(r'Conviction.*?:.*?(HIGH|MEDIUM|LOW)', block, re.IGNORECASE)
        if conviction_match:
            data['conviction'] = conviction_match.group(1).upper()

        # Extract rationale
        rationale_match = re.search(r'Rationale.*?:(.+?)(?:\n\*\*|$)', block, re.DOTALL)
        if rationale_match:
            data['rationale'] = rationale_match.group(1).strip()[:200]

        if data.get('ticker') and data.get('entry_price'):
            return ExternalRecommendation(data)

        return None

    def validate_recommendation(self, rec: ExternalRecommendation) -> Dict:
        """
        Validate single recommendation through multi-agent consensus

        Args:
            rec: ExternalRecommendation to validate

        Returns:
            Dict with validation results and agent analyses
        """
        print(f"\n{'='*70}")
        print(f"MULTI-AGENT VALIDATION: {rec.ticker}")
        print(f"{'='*70}")
        print(f"External Recommendation: {rec}")
        print()

        # Prepare market data for agents
        market_data = {
            'ticker': rec.ticker,
            'price': rec.entry_price,
            'support_level': rec.stop_loss if rec.stop_loss else rec.entry_price * 0.90,
            'resistance_level': rec.target_price if rec.target_price else rec.entry_price * 1.20,
            'volume': 1000000,  # Placeholder - would fetch real data
            'avg_volume': 1000000,
            'volatility': 0.3,  # Placeholder
            'beta': 1.0,  # Placeholder
            'proposed_position_size': rec.position_size_pct * 100000,  # Assuming $100K portfolio
            'sector': 'unknown'  # Placeholder
        }

        # Prepare supplemental data
        supplemental_data = {
            'external_rec': {
                'source': rec.source,
                'conviction': rec.conviction,
                'catalyst': rec.catalyst,
                'rationale': rec.rationale
            }
        }

        # Request analysis from all agents
        analyses = self.coordinator.request_analysis(
            rec.ticker,
            market_data,
            supplemental_data
        )

        # Make consensus decision
        decision = self.coordinator.make_decision(rec.ticker, analyses)

        # Print agent votes
        print("\nAgent Analyses:")
        for agent_id, analysis in analyses.items():
            recommendation = analysis.get('recommendation', {})
            action = recommendation.get('action', 'UNKNOWN')
            confidence = analysis.get('confidence', 0.0)
            print(f"  [{agent_id:12s}] {action:6s} (confidence: {confidence:.2f})")

        # Print consensus
        print(f"\nConsensus Decision:")
        print(f"  Action: {decision.action.value}")
        print(f"  Confidence: {decision.confidence:.2f}")

        # Check if approved
        approved = decision.action.value == 'BUY' and decision.confidence >= 0.6

        return {
            'recommendation': rec,
            'agent_analyses': analyses,
            'consensus_decision': decision,
            'approved': approved,
            'confidence': decision.confidence
        }

    def validate_all(self, claude_path: Path, chatgpt_path: Path) -> Dict:
        """
        Validate all recommendations from both AI sources

        Args:
            claude_path: Path to Claude research report
            chatgpt_path: Path to ChatGPT research report

        Returns:
            Complete validation results
        """
        print("\n" + "="*70)
        print("DUAL-AI MULTI-AGENT CONSENSUS VALIDATION")
        print("="*70)
        print(f"Claude Report: {claude_path.name}")
        print(f"ChatGPT Report: {chatgpt_path.name}")
        print()

        # Parse external recommendations
        claude_recs = self.parse_claude_research(claude_path)
        chatgpt_recs = self.parse_chatgpt_research(chatgpt_path)

        all_recs = claude_recs + chatgpt_recs

        print(f"[*] Found {len(claude_recs)} Claude recommendations")
        print(f"[*] Found {len(chatgpt_recs)} ChatGPT recommendations")
        print(f"[*] Total: {len(all_recs)} recommendations to validate")

        # Validate each recommendation
        results = {
            'shorgan': {'approved': [], 'rejected': []},
            'dee': {'approved': [], 'rejected': []}
        }

        for rec in all_recs:
            validation = self.validate_recommendation(rec)

            bot_key = rec.bot.lower()
            if bot_key not in ['shorgan', 'dee']:
                continue

            if validation['approved']:
                results[bot_key]['approved'].append(validation)
                print(f"  [+] APPROVED: {rec.ticker} (Confidence: {validation['confidence']:.2f})")
            else:
                results[bot_key]['rejected'].append(validation)
                print(f"  [-] REJECTED: {rec.ticker} (Confidence: {validation['confidence']:.2f})")

        # Generate summary
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)
        print(f"SHORGAN-BOT:")
        print(f"  Approved: {len(results['shorgan']['approved'])}")
        print(f"  Rejected: {len(results['shorgan']['rejected'])}")
        print(f"DEE-BOT:")
        print(f"  Approved: {len(results['dee']['approved'])}")
        print(f"  Rejected: {len(results['dee']['rejected'])}")
        print("="*70)

        return {
            'timestamp': datetime.now().isoformat(),
            'claude_report': str(claude_path),
            'chatgpt_report': str(chatgpt_path),
            'total_recommendations': len(all_recs),
            'shorgan_approved': len(results['shorgan']['approved']),
            'shorgan_rejected': len(results['shorgan']['rejected']),
            'dee_approved': len(results['dee']['approved']),
            'dee_rejected': len(results['dee']['rejected']),
            'results': results
        }

    def generate_consensus_report(self, validation_results: Dict, output_path: Path):
        """
        Generate consensus.md from validation results

        This is the CORRECT way - consensus generated by agents,
        not manual comparison of external research.
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Multi-Agent Consensus Report\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M ET')}\n")
            f.write(f"**Method**: Dual-AI External Research → Multi-Agent Validation\n\n")
            f.write("---\n\n")

            f.write("## Validation Summary\n\n")
            f.write(f"- **Total External Recommendations**: {validation_results['total_recommendations']}\n")
            f.write(f"- **SHORGAN Approved**: {validation_results['shorgan_approved']}\n")
            f.write(f"- **SHORGAN Rejected**: {validation_results['shorgan_rejected']}\n")
            f.write(f"- **DEE-BOT Approved**: {validation_results['dee_approved']}\n")
            f.write(f"- **DEE-BOT Rejected**: {validation_results['dee_rejected']}\n\n")

            # SHORGAN approved trades
            f.write("## SHORGAN-BOT Validated Trades\n\n")
            for validation in validation_results['results']['shorgan']['approved']:
                rec = validation['recommendation']
                f.write(f"### {rec.ticker} - {rec.action}\n")
                f.write(f"**External Source**: {rec.source.upper()}\n")
                f.write(f"**Entry**: ${rec.entry_price:.2f}\n")
                f.write(f"**Target**: ${rec.target_price:.2f}\n")
                f.write(f"**Stop**: ${rec.stop_loss:.2f}\n")
                f.write(f"**Size**: {rec.position_size_pct:.1f}%\n")
                f.write(f"**Consensus Confidence**: {validation['confidence']:.2f}\n")
                f.write(f"**Catalyst**: {rec.catalyst}\n\n")

            # DEE-BOT approved trades
            f.write("## DEE-BOT Validated Trades\n\n")
            for validation in validation_results['results']['dee']['approved']:
                rec = validation['recommendation']
                f.write(f"### {rec.ticker}\n")
                f.write(f"**Entry**: ${rec.entry_price:.2f}\n")
                f.write(f"**Size**: {rec.position_size_pct:.1f}%\n")
                f.write(f"**Consensus Confidence**: {validation['confidence']:.2f}\n\n")

        print(f"\n[+] Consensus report saved: {output_path}")

    def generate_trades_file(self, validation_results: Dict, output_path: Path):
        """
        Generate trades.md from validated recommendations

        Ready-to-execute format.
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Validated Trades for Execution\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M ET')}\n")
            f.write(f"**Status**: Agent-Validated, Ready for Execution\n\n")
            f.write("---\n\n")

            f.write("## SHORGAN-BOT Trades\n\n")
            for i, validation in enumerate(validation_results['results']['shorgan']['approved'], 1):
                rec = validation['recommendation']
                f.write(f"### Trade {i}: {rec.ticker}\n")
                f.write(f"- **Action**: {rec.action}\n")
                f.write(f"- **Entry Price**: ${rec.entry_price:.2f}\n")
                f.write(f"- **Target Price**: ${rec.target_price:.2f}\n")
                f.write(f"- **Stop Loss**: ${rec.stop_loss:.2f}\n")
                f.write(f"- **Position Size**: {rec.position_size_pct:.1f}%\n")
                f.write(f"- **Catalyst**: {rec.catalyst}\n")
                f.write(f"- **Consensus Confidence**: {validation['confidence']:.2f}\n\n")

            f.write("## DEE-BOT Trades\n\n")
            for i, validation in enumerate(validation_results['results']['dee']['approved'], 1):
                rec = validation['recommendation']
                f.write(f"### Trade {i}: {rec.ticker}\n")
                f.write(f"- **Entry Price**: ${rec.entry_price:.2f}\n")
                f.write(f"- **Position Size**: {rec.position_size_pct:.1f}%\n")
                f.write(f"- **Consensus Confidence**: {validation['confidence']:.2f}\n\n")

        print(f"[+] Trades file saved: {output_path}")


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate dual-AI research through multi-agent consensus")
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Date of reports to validate (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--claude-report",
        help="Path to Claude research report"
    )
    parser.add_argument(
        "--chatgpt-report",
        help="Path to ChatGPT research report"
    )

    args = parser.parse_args()

    # Determine report paths
    if args.claude_report and args.chatgpt_report:
        claude_path = Path(args.claude_report)
        chatgpt_path = Path(args.chatgpt_report)
    else:
        # Use default locations
        reports_dir = Path("reports/premarket") / args.date
        claude_path = reports_dir / "claude_research.md"
        chatgpt_path = reports_dir / "chatgpt_research.md"

    if not claude_path.exists():
        print(f"[!] Claude report not found: {claude_path}")
        return

    if not chatgpt_path.exists():
        print(f"[!] ChatGPT report not found: {chatgpt_path}")
        return

    # Run validation
    validator = DualAIConsensusValidator()
    results = validator.validate_all(claude_path, chatgpt_path)

    # Generate output files
    output_dir = Path("reports/premarket") / args.date
    output_dir.mkdir(parents=True, exist_ok=True)

    consensus_path = output_dir / "consensus.md"
    trades_path = output_dir / "trades.md"

    validator.generate_consensus_report(results, consensus_path)
    validator.generate_trades_file(results, trades_path)

    # Save JSON results
    json_path = output_dir / "validation_results.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n[+] Validation complete!")
    print(f"[+] Results saved to: {output_dir}")


if __name__ == "__main__":
    main()
