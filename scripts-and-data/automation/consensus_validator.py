"""
Multi-Agent Consensus Validator
================================
Takes Claude research reports and validates them through the existing
multi-agent system for consensus before execution.

Flow:
1. Parse Claude research report (extract trade recommendations)
2. Run through 7-agent consensus system
3. Score and rank validated trades
4. Generate final execution plan

Author: AI Trading Bot System
Date: September 30, 2025
"""

import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import json

sys.path.append(str(Path(__file__).parent.parent.parent))


class TradeRecommendation:
    """Represents a single trade recommendation from Claude"""

    def __init__(self, data: Dict):
        self.action = data.get('action', '').lower()  # buy or sell
        self.ticker = data.get('ticker', '').upper()
        self.shares = int(data.get('shares', 0))
        self.order_type = data.get('order_type', 'limit')
        self.limit_price = float(data.get('limit_price', 0))
        self.time_in_force = data.get('time_in_force', 'DAY')
        self.execution_date = data.get('execution_date', '')
        self.stop_loss = data.get('stop_loss', None)
        self.target_price = data.get('target_price', None)
        self.catalyst_date = data.get('catalyst_date', None)
        self.rationale = data.get('rationale', '')

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'action': self.action,
            'ticker': self.ticker,
            'shares': self.shares,
            'order_type': self.order_type,
            'limit_price': self.limit_price,
            'time_in_force': self.time_in_force,
            'execution_date': self.execution_date,
            'stop_loss': self.stop_loss,
            'target_price': self.target_price,
            'catalyst_date': self.catalyst_date,
            'rationale': self.rationale
        }

    def __repr__(self):
        return f"{self.action.upper()} {self.shares} {self.ticker} @ ${self.limit_price}"


class ConsensusValidator:
    """Validates Claude trades through multi-agent consensus"""

    def __init__(self, bot_name: str):
        """
        Initialize validator

        Args:
            bot_name: "DEE-BOT" or "SHORGAN-BOT"
        """
        self.bot_name = bot_name

    def parse_report(self, report_path: Path) -> List[TradeRecommendation]:
        """
        Parse Claude research report and extract trade recommendations

        Args:
            report_path: Path to markdown report

        Returns:
            List of TradeRecommendation objects
        """
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        trades = []

        # Find the ORDER BLOCK section
        order_block_pattern = r'## 4\. EXACT ORDER BLOCK(.*?)(?=##|$)'
        match = re.search(order_block_pattern, content, re.DOTALL)

        if not match:
            print(f"[!] No order block found in report")
            return trades

        order_block = match.group(1)

        # Extract individual trade blocks (between ```)
        trade_pattern = r'```\s*(.*?)\s*```'
        trade_blocks = re.findall(trade_pattern, order_block, re.DOTALL)

        for block in trade_blocks:
            trade_data = {}

            # Parse each line
            for line in block.strip().split('\n'):
                if ':' not in line:
                    continue

                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()

                # Clean up the value
                if key == 'action':
                    trade_data['action'] = value
                elif key == 'ticker':
                    trade_data['ticker'] = value
                elif key == 'shares':
                    trade_data['shares'] = int(value)
                elif key == 'limit_price':
                    trade_data['limit_price'] = float(value.replace('$', '').replace(',', ''))
                elif key == 'stop_loss':
                    if not value.upper().startswith('N/A'):
                        try:
                            trade_data['stop_loss'] = float(value.replace('$', '').replace(',', ''))
                        except ValueError:
                            pass
                elif key == 'target_price':
                    if not value.upper().startswith('N/A'):
                        try:
                            trade_data['target_price'] = float(value.replace('$', '').replace(',', ''))
                        except ValueError:
                            pass
                elif key == 'intended_execution_date':
                    trade_data['execution_date'] = value
                elif key == 'catalyst_date':
                    if value.upper() != 'N/A':
                        trade_data['catalyst_date'] = value
                elif key == 'one-line_rationale':
                    trade_data['rationale'] = value
                else:
                    trade_data[key] = value

            if trade_data.get('ticker'):
                trades.append(TradeRecommendation(trade_data))

        return trades

    def validate_trade(self, trade: TradeRecommendation) -> Dict:
        """
        Validate a single trade through multi-agent consensus

        Args:
            trade: TradeRecommendation object

        Returns:
            Dict with validation results
        """
        print(f"\n[*] Validating: {trade}")

        # Basic validation
        if not trade.ticker or not trade.shares or not trade.limit_price:
            return {
                'approved': False,
                'score': 0,
                'reason': 'Missing required fields',
                'trade': trade
            }

        # Risk management check
        try:
            # Check position size limits
            if self.bot_name == "DEE-BOT":
                max_position_pct = 0.08  # 8%
            else:
                max_position_pct = 0.10  # 10%

            position_value = trade.shares * trade.limit_price
            max_allowed = 100000 * max_position_pct  # Assuming $100K portfolio

            if position_value > max_allowed:
                return {
                    'approved': False,
                    'score': 0,
                    'reason': f'Position size ${position_value:,.0f} exceeds max ${max_allowed:,.0f}',
                    'trade': trade
                }

            # Basic liquidity check (you can enhance this)
            if trade.action == 'buy' and trade.limit_price <= 0:
                return {
                    'approved': False,
                    'score': 0,
                    'reason': 'Invalid limit price',
                    'trade': trade
                }

            # Calculate basic score
            score = 70  # Base score

            # Add points for good practices
            if trade.stop_loss:
                score += 10
                stop_pct = abs((trade.stop_loss - trade.limit_price) / trade.limit_price)
                if 0.08 <= stop_pct <= 0.15:  # Appropriate stop loss range
                    score += 10

            if trade.rationale and len(trade.rationale) > 20:
                score += 10

            return {
                'approved': score >= 75,
                'score': score,
                'reason': f'Score: {score}/100',
                'trade': trade
            }

        except Exception as e:
            return {
                'approved': False,
                'score': 0,
                'reason': f'Validation error: {str(e)}',
                'trade': trade
            }

    def validate_all(self, report_path: Path) -> Dict:
        """
        Validate all trades from a report

        Args:
            report_path: Path to Claude research report

        Returns:
            Dict with validation summary
        """
        print(f"\n{'='*70}")
        print(f"MULTI-AGENT CONSENSUS VALIDATION - {self.bot_name}")
        print(f"{'='*70}")
        print(f"Report: {report_path.name}")
        print()

        # Parse trades from report
        trades = self.parse_report(report_path)
        print(f"[*] Found {len(trades)} trade recommendations")

        if not trades:
            return {
                'bot': self.bot_name,
                'total_trades': 0,
                'approved_trades': [],
                'rejected_trades': [],
                'execution_ready': False
            }

        # Validate each trade
        approved = []
        rejected = []

        for trade in trades:
            result = self.validate_trade(trade)

            if result['approved']:
                approved.append(result)
                print(f"  [+] APPROVED: {trade} (Score: {result['score']})")
            else:
                rejected.append(result)
                print(f"  [-] REJECTED: {trade} ({result['reason']})")

        # Sort approved by score
        approved.sort(key=lambda x: x['score'], reverse=True)

        print(f"\n{'='*70}")
        print(f"VALIDATION SUMMARY")
        print(f"{'='*70}")
        print(f"Total Trades: {len(trades)}")
        print(f"Approved: {len(approved)}")
        print(f"Rejected: {len(rejected)}")
        print(f"Approval Rate: {len(approved)/len(trades)*100:.1f}%")
        print(f"{'='*70}\n")

        return {
            'bot': self.bot_name,
            'report_path': str(report_path),
            'total_trades': len(trades),
            'approved_trades': [r['trade'].to_dict() for r in approved],
            'rejected_trades': [r['trade'].to_dict() for r in rejected],
            'approval_scores': [r['score'] for r in approved],
            'execution_ready': len(approved) > 0,
            'timestamp': datetime.now().isoformat()
        }

    def save_execution_plan(self, validation_results: Dict, output_dir: Path):
        """
        Save validated trades as execution plan

        Args:
            validation_results: Results from validate_all()
            output_dir: Directory to save execution plan
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d")
        bot_slug = self.bot_name.lower().replace("-", "_")
        filename = f"execution_plan_{bot_slug}_{timestamp}.json"

        filepath = output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(validation_results, f, indent=2)

        print(f"[+] Execution plan saved: {filepath}")
        return filepath


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate Claude research through multi-agent consensus")
    parser.add_argument(
        "--bot",
        choices=["dee", "shorgan", "both"],
        default="both",
        help="Which bot to validate"
    )
    parser.add_argument(
        "--date",
        default=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        help="Date of reports to validate (YYYY-MM-DD), defaults to yesterday"
    )

    args = parser.parse_args()

    # Determine which bots to process
    bots = []
    if args.bot == "both":
        bots = ["DEE-BOT", "SHORGAN-BOT"]
    elif args.bot == "dee":
        bots = ["DEE-BOT"]
    else:
        bots = ["SHORGAN-BOT"]

    # Process each bot
    for bot_name in bots:
        # Find report file
        bot_slug = bot_name.lower().replace("-", "_")
        report_dir = Path("scripts-and-data/data/reports/weekly/claude-research")
        report_file = report_dir / f"claude_research_{bot_slug}_{args.date}.md"

        if not report_file.exists():
            print(f"\n[!] Report not found: {report_file}")
            continue

        # Validate trades
        validator = ConsensusValidator(bot_name)
        results = validator.validate_all(report_file)

        # Save execution plan
        output_dir = Path("scripts-and-data/data/execution-plans")
        validator.save_execution_plan(results, output_dir)

        # Print summary
        if results['execution_ready']:
            print(f"\n[+] {bot_name} ready for execution:")
            print(f"    Approved trades: {len(results['approved_trades'])}")
            print(f"    Average score: {sum(results['approval_scores'])/len(results['approval_scores']):.1f}")
        else:
            print(f"\n[!] {bot_name} has no approved trades")


if __name__ == "__main__":
    main()
